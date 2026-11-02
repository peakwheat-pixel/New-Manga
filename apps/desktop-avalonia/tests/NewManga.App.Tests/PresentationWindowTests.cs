using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Interactivity;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.App.Services;
using NewManga.App.Views.Fluent;
using NewManga.App.Views.Presentation;
using NewManga.Appearance;
using NewManga.DesignSystem.Theming;
using NewManga.Presentation.Avalonia.Switching;
using NewManga.Presentation.Avalonia.Windows;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-07 slice 2b: the stable window keeps its native identity while hosting/switching the frontend
/// content tree; the hidden staging slot gives the switch transaction real layout/Loaded/render gates and
/// switch failures roll back to the previous tree (§7.1/§7.3/H2, R-001/R-002).
/// </summary>
public sealed class PresentationWindowTests : IDisposable
{
    private readonly string _root;
    private readonly AppearanceCoordinator _appearance;
    private readonly SwitchJournal _journal;

    public PresentationWindowTests()
    {
        _root = Path.Combine(Path.GetTempPath(), $"nm-fea07-window-{Guid.NewGuid():N}");
        Directory.CreateDirectory(_root);
        _appearance = new AppearanceCoordinator(new AppearanceStore(Path.Combine(_root, AppearanceStore.FileName)));
        _appearance.Reload();
        _journal = new SwitchJournal(Path.Combine(_root, "switch-journal.json"));
    }

    public void Dispose()
    {
        try
        {
            Directory.Delete(_root, recursive: true);
        }
        catch (IOException)
        {
            // best-effort cleanup
        }
    }

    private static Border Content(string id, string marker) => new()
    {
        Child = new TextBlock { Text = $"{marker}:{id}" },
    };

    private static string TextOf(PresentationWindow window) =>
        (window.ContentHost.Current as Border)?.Child is TextBlock text ? text.Text ?? string.Empty : string.Empty;

    private PresentationWindow CreateWindow(
        Func<string, Control>? factory = null,
        Func<IReadOnlyList<Control>>? allContentProvider = null)
    {
        var options = AppOptions.Parse(Array.Empty<string>());
        var window = new PresentationWindow(
            options,
            FrontendSelector.Select(FrontendSelector.FluentFrontendId, persistedFrontendId: null),
            hostController: null,
            _appearance,
            _journal,
            factory ?? (id => Content(id, "hosted")),
            allContentProvider: allContentProvider);
        window.Show();
        return window;
    }

    [AvaloniaFact]
    public void Window_HostsInitialFrontendContentAndGeometry()
    {
        var window = CreateWindow();

        Assert.Equal("New Manga", window.Title);
        Assert.Equal(1100, window.Width);
        Assert.Equal(760, window.Height);
        Assert.Equal(FrontendSelector.FluentFrontendId, window.CurrentFrontendId);
        Assert.Equal($"hosted:{FrontendSelector.FluentFrontendId}", TextOf(window));
        Assert.True(window.ContentHost.Bounds.Width > 0 && window.ContentHost.Bounds.Height > 0);
        window.Close();
    }

    /// <summary>R-001: the staging slot is part of the live visual tree but never visible or interactive.</summary>
    [AvaloniaFact]
    public void StagingHost_IsAttachedButNotVisibleOrInteractive()
    {
        var window = CreateWindow();

        Assert.Same(window, TopLevel.GetTopLevel(window.StagingHost));
        Assert.NotNull(window.StagingHost.GetVisualRoot());
        Assert.Equal(0, window.StagingHost.Opacity);
        Assert.False(window.StagingHost.IsHitTestVisible);
        Assert.False(window.StagingHost.Focusable);
        Assert.Null(window.StagingHost.Current);
        Assert.True(window.StagingHost.Bounds.Width > 0 && window.StagingHost.Bounds.Height > 0);
        window.Close();
    }

    [AvaloniaFact]
    public async Task Switch_ReplacesContentButKeepsWindowIdentity()
    {
        var window = CreateWindow();
        var nativeIdentity = window;

        var result = await window.SwitchFrontendAsync(FrontendSelector.CurrentV2FrontendId);

        Assert.True(result.Succeeded, result.Failure);
        Assert.Same(nativeIdentity, window);
        Assert.Equal(FrontendSelector.CurrentV2FrontendId, window.CurrentFrontendId);
        Assert.Equal($"hosted:{FrontendSelector.CurrentV2FrontendId}", TextOf(window));
        Assert.Equal(FrontendSelector.CurrentV2FrontendId, _appearance.FrontendId);
        Assert.Null(window.StagingHost.Current); // the committed tree is moved out of staging
        window.Close();
    }

    [AvaloniaFact]
    public async Task FailedSwitch_KeepsPreviousContentAndJournalRecordsRollback()
    {
        var window = CreateWindow(id => id == FrontendSelector.CurrentV2FrontendId
            ? throw new InvalidOperationException("cannot build v2")
            : Content(id, "hosted"));

        var result = await window.SwitchFrontendAsync(FrontendSelector.CurrentV2FrontendId);

        Assert.False(result.Succeeded);
        Assert.Equal(FrontendSelector.FluentFrontendId, window.CurrentFrontendId);
        Assert.Equal($"hosted:{FrontendSelector.FluentFrontendId}", TextOf(window));
        Assert.Null(window.StagingHost.Current);
        Assert.Equal(WindowState.Normal, window.WindowState);
        Assert.True(_journal.TryRead(out var entry, out _));
        Assert.Equal(SwitchStage.RolledBack, entry!.Stage);
        window.Close();
    }

    [AvaloniaFact]
    public async Task UnknownFrontend_IsRejectedWithoutTouchingContent()
    {
        var window = CreateWindow();
        var before = TextOf(window);

        var result = await window.SwitchFrontendAsync("builtin.not-a-frontend");

        Assert.False(result.Succeeded);
        Assert.Equal(before, TextOf(window));
        Assert.Equal(FrontendSelector.FluentFrontendId, window.CurrentFrontendId);
        window.Close();
    }

    [AvaloniaFact]
    public async Task RepeatedSwitches_KeepOneContentTree()
    {
        var window = CreateWindow();

        for (var i = 0; i < 20; i++)
        {
            var target = i % 2 == 0 ? FrontendSelector.CurrentV2FrontendId : FrontendSelector.FluentFrontendId;
            var result = await window.SwitchFrontendAsync(target);
            Assert.True(result.Succeeded, result.Failure);
            Assert.Equal(target, window.CurrentFrontendId);
            Assert.NotNull(window.ContentHost.Current);
            Assert.Null(window.StagingHost.Current);
        }

        Assert.IsType<Border>(window.ContentHost.Current);
        Assert.False(File.Exists(_journal.FilePath));
        window.Close();
    }

    [AvaloniaFact]
    public void WindowStateMemento_IsRestoredOnConstructionAndCaptured()
    {
        var memento = new NewManga.Presentation.Avalonia.Windows.WindowStateMemento(
            X: 10, Y: 20, Width: 1300, Height: 820, DisplayId: null, Scale: 1.0, IsMaximized: false);
        var window = new PresentationWindow(
            AppOptions.Parse(Array.Empty<string>()),
            FrontendSelector.Select(FrontendSelector.FluentFrontendId, persistedFrontendId: null),
            hostController: null,
            _appearance,
            _journal,
            id => Content(id, "hosted"),
            memento);

        Assert.Equal(1300, window.Width);
        Assert.Equal(820, window.Height);
        var captured = window.CaptureWindowState();
        Assert.Equal(1300, captured.Width);
        Assert.Equal(820, captured.Height);
        Assert.True(captured.Scale > 0);
        window.Close();
    }

    [AvaloniaFact]
    public void Broker_TracksOnlyOneStableMainWindow()
    {
        var window = CreateWindow();
        Assert.NotNull(window.Broker.Main);
        Assert.Equal(WindowRole.Main, window.Broker.Main!.Role);
        Assert.Equal(0, window.Broker.SecondaryCount);

        window.Broker.RegisterSecondary(WindowRole.Inspector, "inspector");
        Assert.Equal(1, window.Broker.SecondaryCount);
        Assert.True(window.Broker.Unregister("inspector"));
        window.Close();
    }

    [AvaloniaFact]
    public void ExitCoordinator_BlocksCloseUntilPendingWorkCompletes()
    {
        var window = CreateWindow();
        window.ExitCoordinator.RegisterPendingEdit("shelf");
        var cancelled = false;
        window.Closing += (_, args) => cancelled |= args.Cancel;

        window.Close();
        Assert.True(cancelled, "closing with pending edits must be blocked by the process-level ExitCoordinator");

        window.ExitCoordinator.CompletePendingEdit("shelf");
        window.Close();
    }

    [AvaloniaFact]
    public async Task ConcurrentSwitches_AreSerializedAndEndOnTheLastRequestedFrontend()
    {
        var window = CreateWindow();
        var toFluent = window.SwitchFrontendAsync(FrontendSelector.FluentFrontendId);
        var backToV2 = window.SwitchFrontendAsync(FrontendSelector.CurrentV2FrontendId);

        var results = await Task.WhenAll(toFluent, backToV2);

        Assert.All(results, result => Assert.True(result.Succeeded, result.Failure));
        Assert.Equal(FrontendSelector.CurrentV2FrontendId, window.CurrentFrontendId);
        Assert.Equal($"hosted:{FrontendSelector.CurrentV2FrontendId}", TextOf(window));
        Assert.False(File.Exists(_journal.FilePath));
        window.Close();
    }

    [AvaloniaFact]
    public void LiveContentExitState_BlocksClose()
    {
        ExitBlockingControl? blocking = null;
        var window = new PresentationWindow(
            AppOptions.Parse(Array.Empty<string>()),
            FrontendSelector.Select(FrontendSelector.FluentFrontendId, persistedFrontendId: null),
            hostController: null,
            _appearance,
            _journal,
            id =>
            {
                blocking = new ExitBlockingControl();
                blocking.Child = new TextBlock { Text = id };
                return blocking;
            });

        blocking!.HasUnsavedEdits = true;
        var cancelled = false;
        window.Closing += (_, args) => cancelled |= args.Cancel;
        window.Close();
        Assert.True(cancelled, "unsaved edits in the live content tree must block the close");

        blocking.HasUnsavedEdits = false;
        blocking.HasActiveRuns = true;
        window.Close();
        Assert.True(cancelled);

        blocking.HasActiveRuns = false;
        window.Close();
    }

    /// <summary>
    /// R-002: the composition root caches one tree per frontend; a dirty/run state in a hidden tree (the
    /// frontend the user switched away from) must still block the close, not just the visible tree.
    /// </summary>
    [AvaloniaFact]
    public void HiddenCachedContentTrees_BlockCloseWhenDirtyOrRunning()
    {
        var hidden = new ExitBlockingControl();
        var window = CreateWindow(allContentProvider: () => new Control[] { hidden, new Border() });
        var cancelled = false;
        window.Closing += (_, args) => cancelled |= args.Cancel;

        hidden.HasUnsavedEdits = true;
        window.Close();
        Assert.True(cancelled, "a hidden cached content tree with unsaved edits must block the close");

        cancelled = false;
        hidden.HasUnsavedEdits = false;
        hidden.HasActiveRuns = true;
        window.Close();
        Assert.True(cancelled, "a hidden cached content tree with an active run must block the close");

        cancelled = false;
        hidden.HasActiveRuns = false;
        window.Close();
        Assert.False(cancelled, "a clean hidden cached tree must not block the close");
    }

    /// <summary>
    /// R-022 (r6): the window mode is part of the switch transaction. A failed switch must restore the
    /// previous tree AND the previous full-screen mode (promote/leaving Fluent clears it before commit).
    /// </summary>
    [AvaloniaFact]
    public async Task FailedSwitch_RestoresTheOriginalFullScreenMode()
    {
        var application = Application.Current!;
        using var themeManager = new DesignSystemThemeManager(application);
        themeManager.Initialize();
        FluentShellSurface? fluent = null;
        var window = new PresentationWindow(
            AppOptions.Parse(Array.Empty<string>()),
            FrontendSelector.Select(FrontendSelector.FluentFrontendId, persistedFrontendId: null),
            hostController: null,
            _appearance,
            _journal,
            id =>
            {
                if (id == FrontendSelector.CurrentV2FrontendId)
                {
                    throw new InvalidOperationException("cannot build v2");
                }

                fluent = new FluentShellSurface(
                    AppOptions.Parse(Array.Empty<string>()),
                    FrontendSelector.Select(FrontendSelector.FluentFrontendId, persistedFrontendId: null),
                    NullHostController.Instance,
                    _appearance,
                    themeManager);
                return fluent;
            });
        try
        {
            window.Show();
            Dispatcher.UIThread.RunJobs();
            fluent!.Navigate(FluentPage.Reader);
            Dispatcher.UIThread.RunJobs();
            var fullScreenButton = fluent.GetVisualDescendants().OfType<Button>()
                .FirstOrDefault(button => string.Equals(button.Content as string, "全屏", StringComparison.Ordinal));
            Assert.NotNull(fullScreenButton);
            fullScreenButton!.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
            Dispatcher.UIThread.RunJobs();
            Assert.True(fluent.ReaderViewModel.IsFullScreen);
            Assert.Equal(WindowState.FullScreen, window.WindowState);

            var result = await window.SwitchFrontendAsync(FrontendSelector.CurrentV2FrontendId);

            Assert.False(result.Succeeded);
            Assert.Same(fluent, window.ContentHost.Current);
            Assert.True(fluent.ReaderViewModel.IsFullScreen);
            Assert.Equal(WindowState.FullScreen, window.WindowState);
        }
        finally
        {
            window.Close();
        }
    }

    /// <summary>
    /// R-022 (r7): the failing transaction must reach the promote stage first (so the old full-screen mode
    /// was already cleared) before the journal finalize fault is injected; the mode must still be restored.
    /// </summary>
    [AvaloniaFact]
    public async Task FailedSwitchAfterPromote_RestoresTheOriginalFullScreenMode()
    {
        using var themeManager = new DesignSystemThemeManager(Application.Current!);
        themeManager.Initialize();
        var window = CreateRealFluentWindow(
            themeManager,
            _ => Content("v2", "hosted"),
            beforeJournalCommit: () => throw new InvalidOperationException("finalize failed"),
            out var fluent);
        try
        {
            ShowFullScreenReader(window, fluent);

            var result = await window.SwitchFrontendAsync(FrontendSelector.CurrentV2FrontendId);

            Assert.False(result.Succeeded);
            Assert.Contains("finalize failed", result.Failure);
            Assert.Same(fluent, window.ContentHost.Current);
            Assert.True(fluent.ReaderViewModel.IsFullScreen);
            Assert.Equal(WindowState.FullScreen, window.WindowState);
            Assert.True(_journal.TryRead(out var entry, out _));
            Assert.Equal(SwitchStage.RolledBack, entry!.Stage);
        }
        finally
        {
            window.Close();
        }
    }

    /// <summary>
    /// R-022 (r7): a cancelled token after promote makes the switch coordinator rethrow
    /// <see cref="OperationCanceledException"/>; the window mode must be compensated while the cancellation
    /// keeps propagating to the caller.
    /// </summary>
    [AvaloniaFact]
    public async Task CancelledSwitchAfterPromote_RestoresTheOriginalFullScreenMode()
    {
        using var themeManager = new DesignSystemThemeManager(Application.Current!);
        themeManager.Initialize();
        using var cts = new CancellationTokenSource();
        var window = CreateRealFluentWindow(
            themeManager,
            _ => Content("v2", "hosted"),
            beforeJournalCommit: () =>
            {
                cts.Cancel();
                throw new OperationCanceledException(cts.Token);
            },
            out var fluent);
        try
        {
            ShowFullScreenReader(window, fluent);

            await Assert.ThrowsAsync<OperationCanceledException>(
                () => window.SwitchFrontendAsync(FrontendSelector.CurrentV2FrontendId, cts.Token));

            Assert.Same(fluent, window.ContentHost.Current);
            Assert.True(fluent.ReaderViewModel.IsFullScreen);
            Assert.Equal(WindowState.FullScreen, window.WindowState);
        }
        finally
        {
            window.Close();
        }
    }

    /// <summary>
    /// R-024 (r7): a request queued behind a successful transaction and then rejected must not restore the
    /// mode snapshot of the transaction it waited for (the snapshot now lives inside the switch gate).
    /// </summary>
    [AvaloniaFact]
    public async Task QueuedRejectedSwitch_DoesNotRestoreAStaleWindowMode()
    {
        using var themeManager = new DesignSystemThemeManager(Application.Current!);
        themeManager.Initialize();
        var finalizeEntered = new ManualResetEventSlim();
        var releaseFinalize = new ManualResetEventSlim();
        var window = CreateRealFluentWindow(
            themeManager,
            _ => Content("v2", "hosted"),
            beforeJournalCommit: () =>
            {
                finalizeEntered.Set();
                releaseFinalize.Wait(TimeSpan.FromSeconds(10));
            },
            out var fluent);
        try
        {
            ShowFullScreenReader(window, fluent);

            var successful = window.SwitchFrontendAsync(FrontendSelector.CurrentV2FrontendId);
            await WaitUntilAsync(() => finalizeEntered.IsSet);
            Assert.True(finalizeEntered.IsSet);

            // Queued behind the in-flight (successful) transaction; rejected after acquiring the gate.
            var rejected = window.SwitchFrontendAsync("builtin.not-a-frontend");
            releaseFinalize.Set();

            var results = await Task.WhenAll(successful, rejected);

            Assert.True(results[0].Succeeded, results[0].Failure);
            Assert.False(results[1].Succeeded);
            Assert.Equal(FrontendSelector.CurrentV2FrontendId, window.CurrentFrontendId);
            Assert.Equal(WindowState.Normal, window.WindowState);
        }
        finally
        {
            window.Close();
        }
    }

    [AvaloniaFact]
    public void MaximizedMemento_IsRestored()
    {
        var memento = new NewManga.Presentation.Avalonia.Windows.WindowStateMemento(
            X: 0, Y: 0, Width: 1400, Height: 900, DisplayId: null, Scale: 1.0, IsMaximized: true);
        var window = new PresentationWindow(
            AppOptions.Parse(Array.Empty<string>()),
            FrontendSelector.Select(FrontendSelector.FluentFrontendId, persistedFrontendId: null),
            hostController: null,
            _appearance,
            _journal,
            id => Content(id, "hosted"),
            memento);

        Assert.Equal(WindowState.Maximized, window.WindowState);
        Assert.True(window.CaptureWindowState().IsMaximized);
        window.Close();
    }

    [AvaloniaFact]
    public async Task InvalidGeometry_FailsTheSwitchAndKeepsTheOldContent()
    {
        var window = CreateWindow(id => id == FrontendSelector.CurrentV2FrontendId
            ? new ZeroSizeControl()
            : Content(id, "hosted"));

        var result = await window.SwitchFrontendAsync(FrontendSelector.CurrentV2FrontendId);

        Assert.False(result.Succeeded);
        Assert.Contains("geometry", result.Failure);
        Assert.Equal($"hosted:{FrontendSelector.FluentFrontendId}", TextOf(window));
        Assert.Equal(FrontendSelector.FluentFrontendId, window.CurrentFrontendId);
        Assert.Null(window.StagingHost.Current);
        window.Close();
    }

    /// <summary>
    /// R-001: a tree that does not remain loaded in the staging host must fail the Loaded gate, roll back
    /// to the previous tree and clean up the staging slot (no half-switched UI is committed).
    /// </summary>
    [AvaloniaFact]
    public async Task LoadedGateFailure_RollsBackAndClearsStaging()
    {
        var window = CreateWindow(id => id == FrontendSelector.CurrentV2FrontendId
            ? new DetachesDuringLoadControl()
            : Content(id, "hosted"));

        var result = await window.SwitchFrontendAsync(FrontendSelector.CurrentV2FrontendId);

        Assert.False(result.Succeeded);
        Assert.Contains("loaded", result.Failure, StringComparison.OrdinalIgnoreCase);
        Assert.Equal($"hosted:{FrontendSelector.FluentFrontendId}", TextOf(window));
        Assert.Equal(FrontendSelector.FluentFrontendId, window.CurrentFrontendId);
        Assert.Null(window.StagingHost.Current);
        Assert.True(_journal.TryRead(out var entry, out _));
        Assert.Equal(SwitchStage.RolledBack, entry!.Stage);
        window.Close();
    }

    private PresentationWindow CreateRealFluentWindow(
        DesignSystemThemeManager themeManager,
        Func<string, Control> targetFactory,
        Action? beforeJournalCommit,
        out FluentShellSurface fluent)
    {
        FluentShellSurface? created = null;
        var window = new PresentationWindow(
            AppOptions.Parse(Array.Empty<string>()),
            FrontendSelector.Select(FrontendSelector.FluentFrontendId, persistedFrontendId: null),
            hostController: null,
            _appearance,
            _journal,
            id =>
            {
                if (id != FrontendSelector.FluentFrontendId)
                {
                    return targetFactory(id);
                }

                created = new FluentShellSurface(
                    AppOptions.Parse(Array.Empty<string>()),
                    FrontendSelector.Select(FrontendSelector.FluentFrontendId, persistedFrontendId: null),
                    NullHostController.Instance,
                    _appearance,
                    themeManager);
                return created;
            },
            initialMemento: null,
            allContentProvider: null,
            beforeJournalCommit: beforeJournalCommit);
        fluent = created ?? throw new InvalidOperationException("the Fluent content tree was not created");
        return window;
    }

    private static void ShowFullScreenReader(PresentationWindow window, FluentShellSurface fluent)
    {
        window.Show();
        Dispatcher.UIThread.RunJobs();
        fluent.Navigate(FluentPage.Reader);
        Dispatcher.UIThread.RunJobs();
        var fullScreenButton = fluent.GetVisualDescendants().OfType<Button>()
            .FirstOrDefault(button => string.Equals(button.Content as string, "全屏", StringComparison.Ordinal));
        Assert.NotNull(fullScreenButton);
        fullScreenButton!.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        Dispatcher.UIThread.RunJobs();
        Assert.True(fluent.ReaderViewModel.IsFullScreen);
        Assert.Equal(WindowState.FullScreen, window.WindowState);
    }

    private static async Task WaitUntilAsync(Func<bool> condition, int timeoutMs = 10000)
    {
        var deadline = DateTime.UtcNow.AddMilliseconds(timeoutMs);
        while (!condition() && DateTime.UtcNow < deadline)
        {
            await Task.Delay(10);
        }
    }

    private sealed class ZeroSizeControl : Control
    {
        protected override Size ArrangeOverride(Size finalSize) => default;
    }

    /// <summary>
    /// Fault injection for the real Loaded gate: once loaded, the tree detaches itself from the staging
    /// slot (a tree that cannot stay mounted must never be committed).
    /// </summary>
    private sealed class DetachesDuringLoadControl : Border
    {
        protected override void OnLoaded(RoutedEventArgs e)
        {
            base.OnLoaded(e);
            if (Parent is ContentControl slot)
            {
                Dispatcher.UIThread.Post(() => slot.Content = null, DispatcherPriority.Render);
            }
        }
    }

    private sealed class ExitBlockingControl : Border, IPresentationExitState
    {
        public bool HasUnsavedEdits { get; set; }

        public bool HasActiveRuns { get; set; }
    }
}
