using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using NewManga.App.Services;
using NewManga.Appearance;
using NewManga.Presentation.Avalonia.Hosting;
using NewManga.Presentation.Avalonia.Switching;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-07 slice 2: the stable-window content switch. The app-side coordinator validates the frozen
/// selector semantics, builds the replacement tree into the hidden staging slot, runs the real
/// layout/Loaded/frame-render gates, persists <c>theme.frontendId</c> through the single appearance
/// writer and swaps into the stable host; any failure keeps the previous UI (§7.1/§15.5, R-001).
/// </summary>
public sealed class FrontendHostCoordinatorTests : IDisposable
{
    private readonly string _root;
    private readonly AppearanceCoordinator _appearance;
    private readonly FrontendContentHost _host;
    private readonly FrontendContentHost _staging;
    private readonly Window _window;
    private readonly SwitchJournal _journal;

    public FrontendHostCoordinatorTests()
    {
        _root = Path.Combine(Path.GetTempPath(), $"nm-fea07-host-{Guid.NewGuid():N}");
        Directory.CreateDirectory(_root);
        _appearance = new AppearanceCoordinator(new AppearanceStore(Path.Combine(_root, AppearanceStore.FileName)));
        _appearance.Reload();
        _host = new FrontendContentHost();
        _host.SetContent(Content(FrontendSelector.CurrentV2FrontendId, "initial"));
        _staging = new FrontendContentHost { Opacity = 0, IsHitTestVisible = false };
        var root = new Grid();
        root.Children.Add(_staging);
        root.Children.Add(_host);
        _window = new Window { Width = 900, Height = 600, Content = root };
        _window.Show();
        _journal = new SwitchJournal(Path.Combine(_root, "switch-journal.json"));
    }

    public void Dispose()
    {
        _window.Close();
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

    private static string TextOf(FrontendContentHost host) =>
        (host.Current as Border)?.Child is TextBlock text ? text.Text ?? string.Empty : string.Empty;

    private FrontendHostCoordinator CreateCoordinator(Func<string, Control>? factory = null) => new(
        _host,
        _staging,
        FrontendSelector.CurrentV2FrontendId,
        factory ?? (id => Content(id, "switched")),
        _appearance,
        _journal);

    [AvaloniaFact]
    public async Task Switch_ToFluent_SwapsContentAndPersistsFrontendId()
    {
        var coordinator = CreateCoordinator();

        var result = await coordinator.SwitchAsync(FrontendSelector.FluentFrontendId);

        Assert.True(result.Succeeded, result.Failure);
        Assert.Equal(FrontendSelector.FluentFrontendId, coordinator.CurrentFrontendId);
        Assert.Equal($"switched:{FrontendSelector.FluentFrontendId}", TextOf(_host));
        Assert.Equal(FrontendSelector.FluentFrontendId, _appearance.FrontendId);
        Assert.False(File.Exists(_journal.FilePath));
    }

    [AvaloniaFact]
    public async Task UnknownFrontend_IsRejectedWithoutTouchingTheUi()
    {
        var coordinator = CreateCoordinator();
        var builds = 0;
        var counting = new FrontendHostCoordinator(
            _host,
            _staging,
            FrontendSelector.CurrentV2FrontendId,
            id =>
            {
                builds++;
                return Content(id, "switched");
            },
            _appearance,
            _journal);

        var result = await counting.SwitchAsync("builtin.not-a-frontend");

        Assert.False(result.Succeeded);
        Assert.Equal(0, builds);
        Assert.Equal(FrontendSelector.CurrentV2FrontendId, coordinator.CurrentFrontendId);
        Assert.Equal($"initial:{FrontendSelector.CurrentV2FrontendId}", TextOf(_host));
        Assert.Equal(AppearanceDefaults.FrontendId, _appearance.FrontendId);
    }

    [AvaloniaFact]
    public async Task FactoryFailure_KeepsPreviousUiAndRollsBackJournal()
    {
        var coordinator = CreateCoordinator(id =>
        {
            if (id == FrontendSelector.FluentFrontendId)
            {
                throw new InvalidOperationException("build failed");
            }

            return Content(id, "switched");
        });

        var result = await coordinator.SwitchAsync(FrontendSelector.FluentFrontendId);

        Assert.False(result.Succeeded);
        Assert.Equal($"initial:{FrontendSelector.CurrentV2FrontendId}", TextOf(_host));
        Assert.Equal(FrontendSelector.CurrentV2FrontendId, coordinator.CurrentFrontendId);
        Assert.Equal(AppearanceDefaults.FrontendId, _appearance.FrontendId);
        Assert.True(_journal.TryRead(out var entry, out _));
        Assert.Equal(SwitchStage.RolledBack, entry!.Stage);
        Assert.Contains("build failed", entry.Failure);
    }

    [AvaloniaFact]
    public async Task SameTarget_IsIdempotentAndDoesNotRebuild()
    {
        var builds = new List<string>();
        var coordinator = CreateCoordinator(id =>
        {
            builds.Add(id);
            return Content(id, "switched");
        });

        var first = await coordinator.SwitchAsync(FrontendSelector.FluentFrontendId);
        var second = await coordinator.SwitchAsync(FrontendSelector.FluentFrontendId);

        Assert.True(first.Succeeded);
        Assert.True(second.Succeeded);
        Assert.Single(builds);
    }

    [AvaloniaFact]
    public async Task HundredRoundTrips_KeepExactlyOneContentTreeAndCleanJournal()
    {
        var coordinator = CreateCoordinator();

        for (var i = 0; i < 100; i++)
        {
            var target = i % 2 == 0 ? FrontendSelector.FluentFrontendId : FrontendSelector.CurrentV2FrontendId;
            var result = await coordinator.SwitchAsync(target);
            Assert.True(result.Succeeded, result.Failure);
            Assert.Equal(target, coordinator.CurrentFrontendId);
            Assert.Equal($"switched:{target}", TextOf(_host));
            Assert.NotNull(_host.Current);
            Assert.False(File.Exists(_journal.FilePath));
        }
    }


    [AvaloniaFact]
    public async Task JournalFinalizeFailure_CompensatesContentSettingsAndCurrentFrontend()
    {
        var coordinator = new FrontendHostCoordinator(
            _host,
            _staging,
            FrontendSelector.CurrentV2FrontendId,
            id => Content(id, "switched"),
            _appearance,
            _journal,
            beforeJournalCommit: () => throw new InvalidOperationException("journal finalize failed"));

        var result = await coordinator.SwitchAsync(FrontendSelector.FluentFrontendId);

        Assert.False(result.Succeeded);
        Assert.Contains("journal finalize failed", result.Failure);
        Assert.Equal($"initial:{FrontendSelector.CurrentV2FrontendId}", TextOf(_host));
        Assert.Equal(FrontendSelector.CurrentV2FrontendId, coordinator.CurrentFrontendId);
        Assert.Equal(AppearanceDefaults.FrontendId, _appearance.FrontendId);
        Assert.True(_journal.TryRead(out var entry, out _));
        Assert.Equal(SwitchStage.RolledBack, entry!.Stage);
    }

    /// <summary>
    /// R-013: deterministic proof that a second request waits for the in-flight transaction instead of
    /// returning an early no-op, and that it executes only after the first transaction's compensation.
    /// The first transaction is paused inside journal finalize (holding the switch gate) and then fails;
    /// the queued second request is a real switch (V2 -> Fluent), not a no-op.
    /// </summary>
    [AvaloniaFact]
    public async Task QueuedSwitch_WaitsForFailingFirstTransaction_ThenExecutesAfterCompensation()
    {
        var firstFinalizeEntered = new ManualResetEventSlim();
        var releaseFirst = new ManualResetEventSlim();
        var finalizeAttempts = 0;
        var coordinator = new FrontendHostCoordinator(
            _host,
            _staging,
            FrontendSelector.CurrentV2FrontendId,
            id => Content(id, "switched"),
            _appearance,
            _journal,
            beforeJournalCommit: () =>
            {
                if (Interlocked.Increment(ref finalizeAttempts) != 1)
                {
                    return;
                }

                firstFinalizeEntered.Set();
                releaseFirst.Wait(TimeSpan.FromSeconds(10));
                throw new InvalidOperationException("first finalize failed");
            });

        var first = coordinator.SwitchAsync(FrontendSelector.FluentFrontendId);
        await WaitUntilAsync(() => firstFinalizeEntered.IsSet);
        Assert.True(firstFinalizeEntered.IsSet, "the first transaction never reached journal finalize");

        // The second request targets Fluent as well: once the first transaction rolls back to V2 this is a
        // real switch (a pre-fix implementation would have returned an immediate no-op success).
        var second = coordinator.SwitchAsync(FrontendSelector.FluentFrontendId);
        await Task.Delay(150);
        Assert.False(second.IsCompleted, "the second switch must wait for the in-flight transaction (switch gate)");

        releaseFirst.Set();
        var results = await Task.WhenAll(first, second);

        Assert.False(results[0].Succeeded);
        Assert.Contains("first finalize failed", results[0].Failure);
        Assert.True(results[1].Succeeded, results[1].Failure);
        Assert.Equal(FrontendSelector.FluentFrontendId, coordinator.CurrentFrontendId);
        Assert.Equal($"switched:{FrontendSelector.FluentFrontendId}", TextOf(_host));
        Assert.Equal(FrontendSelector.FluentFrontendId, _appearance.FrontendId);
        Assert.False(File.Exists(_journal.FilePath));
    }

    /// <summary>R-018: every switch transaction detaches its one-shot Loaded subscription from the tree.</summary>
    [AvaloniaFact]
    public async Task LoadedSubscription_IsReleasedAfterSuccessAndFailure()
    {
        var coordinator = CreateCoordinator();
        for (var i = 0; i < 6; i++)
        {
            var target = i % 2 == 0 ? FrontendSelector.FluentFrontendId : FrontendSelector.CurrentV2FrontendId;
            var result = await coordinator.SwitchAsync(target);
            Assert.True(result.Succeeded, result.Failure);
            Assert.Equal(0, ActiveLoadedSubscriptions(coordinator));
        }

        var failing = new FrontendHostCoordinator(
            _host,
            _staging,
            FrontendSelector.CurrentV2FrontendId,
            id => id == FrontendSelector.FluentFrontendId
                ? new ZeroSizeControl()
                : Content(id, "switched"),
            _appearance,
            _journal);
        var failed = await failing.SwitchAsync(FrontendSelector.FluentFrontendId);

        Assert.False(failed.Succeeded);
        Assert.Equal(0, ActiveLoadedSubscriptions(failing));
    }

    /// <summary>R-019: input activation follows the commit, never the (hidden) staging mount.</summary>
    [AvaloniaFact]
    public async Task InputActivation_IsDisabledWhileStagedAndEnabledOnCommit()
    {
        InputAwareControl? created = null;
        var coordinator = CreateCoordinator(id =>
        {
            created = new InputAwareControl();
            return created;
        });

        var result = await coordinator.SwitchAsync(FrontendSelector.FluentFrontendId);

        Assert.True(result.Succeeded, result.Failure);
        Assert.Equal(new[] { false, true }, created!.ActivationLog);
        Assert.True(created.IsInputActive);
    }

    [AvaloniaFact]
    public async Task InputActivation_StaysInactiveWhenTheStagedTreeFailsTheGates()
    {
        ZeroGeometryInputAwareControl? created = null;
        var coordinator = CreateCoordinator(id =>
        {
            created = new ZeroGeometryInputAwareControl();
            return created;
        });

        var result = await coordinator.SwitchAsync(FrontendSelector.FluentFrontendId);

        Assert.False(result.Succeeded);
        Assert.Contains(false, created!.ActivationLog);
        Assert.DoesNotContain(true, created.ActivationLog);
        Assert.Equal($"initial:{FrontendSelector.CurrentV2FrontendId}", TextOf(_host));
    }

    private static int ActiveLoadedSubscriptions(FrontendHostCoordinator coordinator)
    {
        var field = typeof(FrontendHostCoordinator).GetField(
            "_loadedSubscriptions",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        Assert.NotNull(field);
        var subscriptions = Assert.IsAssignableFrom<System.Collections.ICollection>(field.GetValue(coordinator));
        return subscriptions.Count;
    }

    private static async Task WaitUntilAsync(Func<bool> condition, int timeoutMs = 5000)
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

    private sealed class InputAwareControl : Border, IPresentationInputState
    {
        private bool _isInputActive = true;

        public System.Collections.Generic.List<bool> ActivationLog { get; } = new();

        public bool IsInputActive
        {
            get => _isInputActive;
            set
            {
                _isInputActive = value;
                ActivationLog.Add(value);
            }
        }
    }

    private sealed class ZeroGeometryInputAwareControl : Control, IPresentationInputState
    {
        private bool _isInputActive = true;

        public System.Collections.Generic.List<bool> ActivationLog { get; } = new();

        public bool IsInputActive
        {
            get => _isInputActive;
            set
            {
                _isInputActive = value;
                ActivationLog.Add(value);
            }
        }

        protected override Size ArrangeOverride(Size finalSize) => default;
    }
}