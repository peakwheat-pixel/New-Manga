using System;
using System.Threading;
using System.Threading.Tasks;
using Avalonia.Controls;
using Avalonia.Threading;
using NewManga.Appearance;
using NewManga.Presentation.Avalonia.Hosting;
using NewManga.Presentation.Avalonia.Switching;

namespace NewManga.App.Services;

/// <summary>
/// FEA-07 app-side switch orchestration: validates the requested frontend against the frozen selector
/// semantics, builds the replacement content tree, persists <c>theme.frontendId</c> through the single
/// appearance writer and swaps the content into the stable host. The previous tree is restored on any
/// failure (§7.1 / §15.5).
/// </summary>
public sealed class FrontendHostCoordinator
{
    private readonly FrontendContentHost _host;
    private readonly Func<string, Control> _contentFactory;
    private readonly AppearanceCoordinator _appearance;
    private readonly FrontendSwitchCoordinator _switcher;
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
    public Task<SwitchResult> SwitchAsync(string requestedFrontendId, CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(requestedFrontendId);

        var selection = FrontendSelector.Select(requestedFrontendId, persistedFrontendId: null);
        if (selection.IsFallback)
        {
            return Task.FromResult(new SwitchResult(
                Succeeded: false,
                FinalStage: SwitchStage.Preparing,
                Failure: selection.Diagnostic ?? $"unknown frontend id '{requestedFrontendId}'",
                RolledBack: false));
        }

        var target = selection.EffectiveFrontendId;
        if (string.Equals(target, CurrentFrontendId, StringComparison.Ordinal))
        {
            return Task.FromResult(new SwitchResult(Succeeded: true, SwitchStage.Committed, Failure: null, RolledBack: false));
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

        return _switcher.SwitchAsync(new SwitchRequest(target, CurrentFrontendId), callbacks, cancellationToken);
    }

    private static Control Placeholder => new Border();

    private static async Task InvokeOnUiAsync(Action action) => await Dispatcher.UIThread.InvokeAsync(action);
}
