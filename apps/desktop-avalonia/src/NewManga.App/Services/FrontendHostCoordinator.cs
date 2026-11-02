using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Interactivity;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.Appearance;
using NewManga.Presentation.Avalonia.Hosting;
using NewManga.Presentation.Avalonia.Switching;

namespace NewManga.App.Services;

/// <summary>
/// FEA-07 app-side switch orchestration: validates the requested frontend against the frozen selector
/// semantics, builds the replacement content tree inside the hidden staging slot, and commits it only
/// after the real layout pass produced valid geometry, the real Loaded event fired and a frame was
/// actually rendered for the mounted tree. <c>theme.frontendId</c> is persisted through the single
/// appearance writer, and the previous tree is restored on any failure (§7.1 / §15.5). All state checks
/// and snapshots live inside one switch gate so concurrent requests cannot return a stale success or
/// roll back to an outdated UI (R-013).
/// </summary>
public sealed class FrontendHostCoordinator
{
    /// <summary>Fail-closed bound for the real Loaded signal (the staging top-level must load the tree).</summary>
    private static readonly TimeSpan LoadedGateTimeout = TimeSpan.FromSeconds(5);

    /// <summary>Fail-closed bound for the real frame-render signal (a window that cannot render must not commit).</summary>
    private static readonly TimeSpan RenderGateTimeout = TimeSpan.FromSeconds(2);

    private readonly FrontendContentHost _host;
    private readonly FrontendContentHost _stagingHost;
    private readonly Func<string, Control> _contentFactory;
    private readonly AppearanceCoordinator _appearance;
    private readonly FrontendSwitchCoordinator _switcher;
    private readonly SemaphoreSlim _switchGate = new(1, 1);
    private readonly object _sync = new();

    /// <summary>R-018: active one-shot Loaded subscriptions, removed when the switch transaction ends.</summary>
    private readonly Dictionary<Control, EventHandler<RoutedEventArgs>> _loadedSubscriptions = new();
    private string _currentFrontendId;

    public FrontendHostCoordinator(
        FrontendContentHost host,
        FrontendContentHost stagingHost,
        string initialFrontendId,
        Func<string, Control> contentFactory,
        AppearanceCoordinator appearance,
        SwitchJournal journal,
        Action? beforeJournalCommit = null)
    {
        ArgumentNullException.ThrowIfNull(host);
        ArgumentNullException.ThrowIfNull(stagingHost);
        ArgumentException.ThrowIfNullOrWhiteSpace(initialFrontendId);
        ArgumentNullException.ThrowIfNull(contentFactory);
        ArgumentNullException.ThrowIfNull(appearance);
        ArgumentNullException.ThrowIfNull(journal);

        _host = host;
        _stagingHost = stagingHost;
        _contentFactory = contentFactory;
        _appearance = appearance;
        _switcher = new FrontendSwitchCoordinator(journal, beforeJournalCommit: beforeJournalCommit);
        _currentFrontendId = initialFrontendId;
    }

    /// <summary>The frontend id currently displayed in the stable window.</summary>
    public string CurrentFrontendId
    {
        get
        {
            lock (_sync)
            {
                return _currentFrontendId;
            }
        }
    }

    /// <summary>
    /// Switches the stable window to <paramref name="requestedFrontendId"/>. Unknown ids are rejected
    /// without touching the live UI (the startup selector keeps its fail-safe fallback, but an explicit
    /// runtime switch must not silently change the requested frontend).
    /// </summary>
    public async Task<SwitchResult> SwitchAsync(string requestedFrontendId, CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(requestedFrontendId);

        await _switchGate.WaitAsync(cancellationToken).ConfigureAwait(true);
        Control? replacement = null;
        try
        {
            var selection = FrontendSelector.Select(requestedFrontendId, persistedFrontendId: null);
            if (selection.IsFallback)
            {
                return new SwitchResult(
                    Succeeded: false,
                    FinalStage: SwitchStage.Preparing,
                    Failure: selection.Diagnostic ?? $"unknown frontend id '{requestedFrontendId}'",
                    RolledBack: false);
            }

            var target = selection.EffectiveFrontendId;
            var previousFrontend = CurrentFrontendId;
            if (string.Equals(target, previousFrontend, StringComparison.Ordinal))
            {
                return new SwitchResult(Succeeded: true, SwitchStage.Committed, Failure: null, RolledBack: false);
            }

            TaskCompletionSource<bool>? loadedSignal = null;
            var previous = _host.Current;
            AppearanceSettings? previousSettings = null;

            var callbacks = new SwitchCallbacks
            {
                ValidateAsync = _ => Task.CompletedTask,
                BuildTreeAsync = _ => InvokeOnUiAsync(() =>
                {
                    replacement = _contentFactory(target);
                    // R-001: subscribe to the real Loaded event before the tree enters the visual tree;
                    // the Loaded gate never fabricates a signal with a dispatcher-priority no-op.
                    // R-018: the handler is tracked and detached when the transaction ends (success,
                    // failure, timeout or cancellation) so cached trees never accumulate subscriptions.
                    var signal = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
                    EventHandler<RoutedEventArgs> handler = (_, _) => signal.TrySetResult(true);
                    lock (_sync)
                    {
                        _loadedSubscriptions[replacement] = handler;
                    }

                    replacement.Loaded += handler;
                    loadedSignal = signal;
                }),
                LayoutAsync = _ => MountAndValidateLayoutAsync(replacement),
                LoadedAsync = token => ValidateLoadedAsync(replacement, loadedSignal, token),
                RenderedAsync = token => ValidateRenderedAsync(replacement, token),
                CommitAsync = async token =>
                {
                    previousSettings = _appearance.Settings;
                    try
                    {
                        await InvokeOnUiAsync(() =>
                            PromoteStagedContent(replacement ?? throw new InvalidOperationException("replacement content tree was not built")));
                        await _appearance.SaveAsync(previousSettings with { FrontendId = target }, token).ConfigureAwait(true);
                    }
                    catch
                    {
                        await InvokeOnUiAsync(() => RestoreContent(previous));
                        if (previousSettings is not null)
                        {
                            await _appearance.SaveAsync(previousSettings, CancellationToken.None).ConfigureAwait(true);
                        }

                        throw;
                    }

                    lock (_sync)
                    {
                        _currentFrontendId = target;
                    }
                },
                RollbackAsync = async _ =>
                {
                    await InvokeOnUiAsync(() => RestoreContent(previous));
                    if (previousSettings is not null)
                    {
                        await _appearance.SaveAsync(previousSettings, CancellationToken.None).ConfigureAwait(true);
                    }

                    lock (_sync)
                    {
                        _currentFrontendId = previousFrontend;
                    }
                },
            };

            return await _switcher.SwitchAsync(
                new SwitchRequest(target, previousFrontend),
                callbacks,
                cancellationToken).ConfigureAwait(true);
        }
        finally
        {
            // R-018: detach the one-shot Loaded subscription of this transaction before the next switch.
            await ReleaseLoadedSubscriptionAsync(replacement).ConfigureAwait(true);
            _switchGate.Release();
        }
    }

    /// <summary>
    /// R-001 layout gate: mount the replacement into the hidden staging slot (already attached to the live
    /// visual tree) and read the geometry produced by the real layout pass. No manual Measure/Arrange and
    /// no synthetic viewport: zero geometry anywhere fails the switch instead of being papered over.
    /// </summary>
    private async Task MountAndValidateLayoutAsync(Control? replacement)
    {
        var tree = replacement ?? throw new InvalidOperationException("replacement content tree was not built");
        await InvokeOnUiAsync(() =>
        {
            _stagingHost.SetContent(tree);
            // R-019: a staged tree must not consume global shortcuts/focus that belong to the visible UI.
            SetInputActive(tree, active: false);
        });

        // The layout pass runs at the dispatcher's Layout priority, which is processed before the job
        // below; this continuation therefore observes the post-layout geometry of the mounted tree.
        await InvokeAtPriorityAsync(DispatcherPriority.Loaded);

        await InvokeOnUiAsync(() =>
        {
            var hostBounds = _host.Bounds;
            if (hostBounds.Width <= 0 || hostBounds.Height <= 0)
            {
                throw new InvalidOperationException(
                    $"stable content host has no valid geometry ({hostBounds.Width:0}x{hostBounds.Height:0}); the window is not laid out");
            }

            var stagingBounds = _stagingHost.Bounds;
            if (stagingBounds.Width <= 0 || stagingBounds.Height <= 0)
            {
                throw new InvalidOperationException(
                    $"staging content host has no valid geometry ({stagingBounds.Width:0}x{stagingBounds.Height:0})");
            }

            var treeBounds = tree.Bounds;
            if (treeBounds.Width <= 0 || treeBounds.Height <= 0)
            {
                throw new InvalidOperationException(
                    $"replacement content tree has no valid geometry ({treeBounds.Width:0}x{treeBounds.Height:0})");
            }
        });
    }

    /// <summary>R-001 loaded gate: the real Loaded event must fire and the tree must stay attached.</summary>
    private async Task ValidateLoadedAsync(
        Control? replacement,
        TaskCompletionSource<bool>? loadedSignal,
        CancellationToken cancellationToken)
    {
        var tree = replacement ?? throw new InvalidOperationException("replacement content tree was not built");
        if (!tree.IsLoaded)
        {
            var signal = loadedSignal ?? throw new InvalidOperationException("replacement content tree has no load signal");
            await signal.Task.WaitAsync(LoadedGateTimeout, cancellationToken).ConfigureAwait(true);
        }

        await InvokeOnUiAsync(() =>
        {
            if (!tree.IsLoaded || tree.GetVisualRoot() is null)
            {
                throw new InvalidOperationException("replacement content tree did not stay loaded in the staging host");
            }

            if (TopLevel.GetTopLevel(tree) is null)
            {
                throw new InvalidOperationException("replacement content tree is not attached to a top level");
            }
        });
    }

    /// <summary>
    /// R-001 rendered gate: wait for an actually produced frame (TopLevel animation frame) for the mounted
    /// tree and re-validate attachment afterwards. A dispatcher-priority no-op is not a rendered signal;
    /// a tree that stops rendering fails the switch and is rolled back.
    /// </summary>
    private async Task ValidateRenderedAsync(Control? replacement, CancellationToken cancellationToken)
    {
        var tree = replacement ?? throw new InvalidOperationException("replacement content tree was not built");
        var topLevel = await InvokeOnUiAsync(() => TopLevel.GetTopLevel(tree))
            ?? throw new InvalidOperationException("replacement content tree is not attached to a top level");

        var frame = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        await InvokeOnUiAsync(() => topLevel.RequestAnimationFrame(_ => frame.TrySetResult(true)));
        await frame.Task.WaitAsync(RenderGateTimeout, cancellationToken).ConfigureAwait(true);

        await InvokeOnUiAsync(() =>
        {
            if (!tree.IsLoaded || tree.GetVisualRoot() is null)
            {
                throw new InvalidOperationException("replacement content tree is no longer attached after the render gate");
            }

            if (tree.Bounds.Width <= 0 || tree.Bounds.Height <= 0)
            {
                throw new InvalidOperationException("replacement content tree lost its geometry after the render gate");
            }
        });
    }

    /// <summary>Moves the gated tree from staging into the visible slot (the previous tree never shows half a switch).</summary>
    private void PromoteStagedContent(Control replacement)
    {
        _stagingHost.Clear();
        _host.SetContent(replacement);
        // R-019: input routing follows the commit, not the (hidden) staging mount.
        SetInputActive(replacement, active: true);
    }

    /// <summary>Restores the previous visible tree and drops any staged replacement.</summary>
    private void RestoreContent(Control? previous)
    {
        _stagingHost.Clear();
        _host.SetContent(previous ?? Placeholder);
        SetInputActive(previous, active: true);
    }

    private static void SetInputActive(Control? tree, bool active)
    {
        if (tree is IPresentationInputState input)
        {
            input.IsInputActive = active;
        }
    }

    /// <summary>R-018: removes this transaction's one-shot Loaded handler from the (cached) content tree.</summary>
    private async Task ReleaseLoadedSubscriptionAsync(Control? tree)
    {
        if (tree is null)
        {
            return;
        }

        EventHandler<RoutedEventArgs> handler;
        lock (_sync)
        {
            if (!_loadedSubscriptions.Remove(tree, out handler!))
            {
                return;
            }
        }

        try
        {
            await InvokeOnUiAsync(() => tree.Loaded -= handler);
        }
        catch (Exception ex) when (ex is InvalidOperationException or ObjectDisposedException)
        {
            // best-effort: the window may be closing; the handler is garbage-collected with the tree.
        }
    }

    private static Control Placeholder => new Border();

    private static async Task InvokeOnUiAsync(Action action) => await Dispatcher.UIThread.InvokeAsync(action);

    private static async Task<T> InvokeOnUiAsync<T>(Func<T> func) => await Dispatcher.UIThread.InvokeAsync(func);

    private static async Task InvokeAtPriorityAsync(DispatcherPriority priority) =>
        await Dispatcher.UIThread.InvokeAsync(static () => { }, priority);
}
