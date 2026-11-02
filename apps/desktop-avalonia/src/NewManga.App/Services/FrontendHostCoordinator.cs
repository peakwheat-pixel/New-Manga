using System;
using System.Threading;
using System.Threading.Tasks;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Threading;
using NewManga.Appearance;
using NewManga.Presentation.Avalonia.Hosting;
using NewManga.Presentation.Avalonia.Switching;

namespace NewManga.App.Services;

/// <summary>
/// FEA-07 app-side switch orchestration: validates the requested frontend against the frozen selector
/// semantics, builds the replacement content tree, runs the real layout/loaded/rendered gates, persists
/// <c>theme.frontendId</c> through the single appearance writer and swaps the content into the stable
/// host. The previous tree is restored on any failure (§7.1 / §15.5). All state checks and snapshots are
/// inside one switch gate so concurrent requests cannot return a stale success or roll back to an
/// outdated UI (R-013).
/// </summary>
public sealed class FrontendHostCoordinator
{
    private static readonly Size FallbackViewport = new(1024, 640);

    private readonly FrontendContentHost _host;
    private readonly Func<string, Control> _contentFactory;
    private readonly AppearanceCoordinator _appearance;
    private readonly FrontendSwitchCoordinator _switcher;
    private readonly SemaphoreSlim _switchGate = new(1, 1);
    private readonly object _sync = new();
    private string _currentFrontendId;

    public FrontendHostCoordinator(
        FrontendContentHost host,
        string initialFrontendId,
        Func<string, Control> contentFactory,
        AppearanceCoordinator appearance,
        SwitchJournal journal)
    {
        ArgumentNullException.ThrowIfNull(host);
        ArgumentException.ThrowIfNullOrWhiteSpace(initialFrontendId);
        ArgumentNullException.ThrowIfNull(contentFactory);
        ArgumentNullException.ThrowIfNull(appearance);
        ArgumentNullException.ThrowIfNull(journal);

        _host = host;
        _contentFactory = contentFactory;
        _appearance = appearance;
        _switcher = new FrontendSwitchCoordinator(journal);
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

            Control? replacement = null;
            var previous = _host.Current;
            AppearanceSettings? previousSettings = null;

            var callbacks = new SwitchCallbacks
            {
                ValidateAsync = _ => Task.CompletedTask,
                BuildTreeAsync = _ => InvokeOnUiAsync(() =>
                {
                    replacement = _contentFactory(target);
                }),
                LayoutAsync = _ => InvokeOnUiAsync(() => ValidateLayout(replacement)),
                LoadedAsync = _ => InvokeAtPriorityAsync(DispatcherPriority.Loaded),
                RenderedAsync = _ => InvokeAtPriorityAsync(DispatcherPriority.Render),
                CommitAsync = async token =>
                {
                    previousSettings = _appearance.Settings;
                    try
                    {
                        await InvokeOnUiAsync(() =>
                            _host.SetContent(replacement ?? throw new InvalidOperationException("replacement content tree was not built")));
                        await _appearance.SaveAsync(previousSettings with { FrontendId = target }, token).ConfigureAwait(true);
                    }
                    catch
                    {
                        await InvokeOnUiAsync(() => _host.SetContent(previous ?? Placeholder));
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
                RollbackAsync = _ => InvokeOnUiAsync(() => _host.SetContent(previous ?? Placeholder)),
            };

            return await _switcher.SwitchAsync(
                new SwitchRequest(target, previousFrontend),
                callbacks,
                cancellationToken).ConfigureAwait(true);
        }
        finally
        {
            _switchGate.Release();
        }
    }

    private void ValidateLayout(Control? replacement)
    {
        if (replacement is null)
        {
            throw new InvalidOperationException("replacement content tree was not built");
        }

        var viewport = _host.Bounds.Width > 0 && _host.Bounds.Height > 0
            ? _host.Bounds.Size
            : FallbackViewport;
        replacement.Measure(viewport);
        replacement.Arrange(new Rect(viewport));
        if (replacement.Bounds.Width <= 0 || replacement.Bounds.Height <= 0)
        {
            throw new InvalidOperationException("replacement content tree has no valid geometry");
        }
    }

    private static Control Placeholder => new Border();

    private static async Task InvokeOnUiAsync(Action action) => await Dispatcher.UIThread.InvokeAsync(action);

    private static async Task InvokeAtPriorityAsync(DispatcherPriority priority) =>
        await Dispatcher.UIThread.InvokeAsync(static () => { }, priority);
}
