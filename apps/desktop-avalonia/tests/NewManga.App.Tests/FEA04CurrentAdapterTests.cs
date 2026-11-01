using NewManga.App.Services;
using NewManga.App.Shell.V2;
using NewManga.App.Shell.V2.Frontends;
using NewManga.App.ViewModels.V2.Library;
using NewManga.App.ViewModels.V2.Shell;
using NewManga.App.Views.V2.Route;
using NewManga.ApplicationCore;

namespace NewManga.App.Tests;

public sealed class FEA04CurrentAdapterTests
{
    [Theory]
    [InlineData("PENDING_REGION_TYPE", "S1")]
    [InlineData("PENDING_CONFIRMATION", "S2")]
    [InlineData("UNFLUSHED_RUN_KEY", "S3")]
    [InlineData("UNMAPPED_READER_ANCHOR", "S4")]
    [InlineData("UNMAPPED_SHELL_STATE", "S6")]
    public void Preflight_reports_each_frozen_blocker_without_host_side_effects(string code, string source)
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("FEA-04"));
        var current = CurrentFrontend.For(host);
        var before = Capture(host);

        var result = current.Preflight(SignalsFor(code));

        Assert.False(result.Allowed);
        var blocker = Assert.Single(result.Blockers);
        Assert.Equal(code, blocker.Code);
        Assert.Equal(source, blocker.Source);
        Assert.Equal(before, Capture(host));
    }

    [Fact]
    public async Task Region_type_draft_has_a_stable_draft_id_and_flushes_without_host_calls()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("FEA-04"));
        var current = CurrentFrontend.For(host);
        var before = Capture(host);

        var draft = current.GetRegionTypeDraft("page-1", "region-1", 3);
        var draftId = draft.Snapshot.DraftId;
        await draft.ApplyPatchAsync(new DraftPatch(Style: new Dictionary<string, object?>
        {
            ["regionType"] = "narration",
        }));

        Assert.Same(draft, current.GetRegionTypeDraft("page-1", "region-1", 3));
        Assert.Equal(draftId, draft.Snapshot.DraftId);
        Assert.Equal("narration", current.ReadPendingRegionType("page-1", "region-1", 3));

        var flush = await draft.FlushAsync(DraftFlushTrigger.PageChange);
        Assert.True(flush.Succeeded);
        Assert.Equal(draftId, flush.Snapshot.DraftId);
        Assert.Equal(before, Capture(host));
        current.ClearRegionTypeDraft("page-1", "region-1");
    }

    [Fact]
    public async Task Preflight_derives_all_five_blockers_from_current_state()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("FEA-04"));
        var current = CurrentFrontend.For(host);
        var draft = current.GetRegionTypeDraft("page-1", "region-1", 3);
        await draft.ApplyPatchAsync(new DraftPatch(Style: new Dictionary<string, object?>
        {
            ["regionType"] = "narration",
        }));
        current.Session.Studio.HasPendingConfirmation = true;
        current.Session.Reader.PageId = "page-1";
        current.Session.Reader.SemanticAnchor = "page-1";
        current.Session.Reader.AnchorMapped = false;
        current.Session.Shell.HasUnmappedState = true;
        current.Session.Appearance.IsDirty = true;
        current.Session.Appearance.IsMapped = false;

        var acknowledgement = new TaskCompletionSource<RunStartInfo?>(TaskCreationOptions.RunContinuationsAsynchronously);
        var execution = current.RunIntents.ExecuteAsync((_, _) => acknowledgement.Task);
        var before = Capture(host);

        var result = current.Preflight();

        Assert.False(result.Allowed);
        Assert.Equal(
            new[] { "PENDING_REGION_TYPE", "PENDING_CONFIRMATION", "UNFLUSHED_RUN_KEY", "UNMAPPED_READER_ANCHOR", "UNMAPPED_SHELL_STATE" },
            result.Blockers.Select(blocker => blocker.Code).ToArray());
        Assert.Equal(before, Capture(host));

        acknowledgement.SetResult(null);
        await execution;
        current.ClearRegionTypeDraft("page-1", "region-1");
    }

    [Fact]
    public async Task Failed_region_draft_flush_keeps_the_page_and_does_not_call_the_host_write()
    {
        var host = StudioFixtures.CreateHost();
        var current = CurrentFrontend.For(host);
        current.GetRegionTypeDraft(
            "p1",
            "region-1",
            3,
            static (_, _) => Task.FromException(new IOException("local journal failed")));
        var workspace = new NewManga.App.ViewModels.V2.Studio.StudioWorkspaceViewModel(host);
        Assert.True(await workspace.LoadAsync("book-0", "ch-1"));
        Assert.Equal("p1", workspace.Page.CurrentPageId);

        await workspace.Page.Inspector.SetPendingRegionTypeAsync("narration");
        Assert.False(await workspace.Page.SelectPageAsync("p2"));
        var result = await workspace.Page.ResolveLeaveAsync(NewManga.App.ViewModels.V2.Studio.StudioLeaveChoice.Save);

        Assert.Equal(NewManga.App.ViewModels.V2.Studio.StudioLeaveOutcome.SaveFailed, result);
        Assert.Equal("p1", workspace.Page.CurrentPageId);
        Assert.Equal("region-1", workspace.Page.SelectedRegion?.RegionId);
        Assert.True(workspace.Page.Inspector.HasPendingTypeEdit);
        Assert.Empty(host.SetRegionTypeCalls);
    }

    [Fact]
    public async Task Failed_host_region_save_keeps_the_edit_available_for_retry()
    {
        var host = StudioFixtures.CreateHost();
        var current = CurrentFrontend.For(host);
        var workspace = new NewManga.App.ViewModels.V2.Studio.StudioWorkspaceViewModel(host);
        Assert.True(await workspace.LoadAsync("book-0", "ch-1"));
        workspace.Page.Inspector.SetPendingRegionType("narration");
        host.ScriptedSetTypeResults.Enqueue(RegionOperationResult.Failed("WRITE_REJECTED"));

        Assert.False(await workspace.Page.SelectPageAsync("p2"));
        var result = await workspace.Page.ResolveLeaveAsync(NewManga.App.ViewModels.V2.Studio.StudioLeaveChoice.Save);

        Assert.Equal(NewManga.App.ViewModels.V2.Studio.StudioLeaveOutcome.SaveFailed, result);
        Assert.Equal("p1", workspace.Page.CurrentPageId);
        Assert.True(workspace.Page.Inspector.HasPendingTypeEdit);
        Assert.Equal("narration", workspace.Page.Inspector.PendingRegionType);
        Assert.Single(host.SetRegionTypeCalls);
        Assert.False(current.Preflight().Allowed);
    }

    [Fact]
    public async Task Discarding_region_type_draft_does_not_flush_or_call_the_host()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("FEA-04"));
        var current = CurrentFrontend.For(host);
        var flushCalls = 0;
        var draft = current.GetRegionTypeDraft("page-1", "region-1", 3, (_, _) =>
        {
            flushCalls++;
            return Task.CompletedTask;
        });
        await draft.ApplyPatchAsync(new DraftPatch(Style: new Dictionary<string, object?>
        {
            ["regionType"] = "narration",
        }));

        current.ClearRegionTypeDraft("page-1", "region-1");

        Assert.Equal(0, flushCalls);
        Assert.False(current.HasPendingRegionTypeDraft);
        Assert.Empty(host.SetRegionTypeCalls);
    }

    [Fact]
    public async Task Run_start_retry_reuses_the_same_key_after_ack_loss()
    {
        var intents = new CurrentRunIntentCoordinator();
        var acceptedByKey = new Dictionary<string, RunStartInfo>(StringComparer.Ordinal);
        var attempts = new List<string>();

        async Task<RunStartInfo?> SimulateStartAsync(string key, CancellationToken _)
        {
            attempts.Add(key);
            if (!acceptedByKey.TryGetValue(key, out var accepted))
            {
                accepted = new RunStartInfo("run-1", "queued");
                acceptedByKey.Add(key, accepted);
            }

            if (attempts.Count == 1)
            {
                await Task.Yield();
                throw new IOException("simulated acknowledgement loss");
            }

            return accepted;
        }

        Assert.Null(await intents.ExecuteAsync(SimulateStartAsync));
        var pendingKey = Assert.IsType<string>(intents.PendingKey);
        Assert.Equal(pendingKey, Assert.Single(attempts));

        var retried = await intents.ExecuteAsync(SimulateStartAsync);

        Assert.NotNull(retried);
        Assert.Equal("run-1", retried.RunId);
        Assert.Equal(pendingKey, attempts[1]);
        Assert.Single(acceptedByKey);
        Assert.Null(intents.PendingKey);
    }

    [Fact]
    public void Rebuilt_shell_content_uses_the_same_host_and_session_without_starting_it()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("FEA-04"));
        var startsBefore = host.StartCalls;
        var startRequestsBefore = host.StartRequests;
        var lifecycleBefore = host.LifecycleLog.ToArray();

        var first = new AppShellViewModel(host);
        var hostBefore = first.Current.HostController;
        first.State.SelectBook("book-1");
        first.State.SwitchSpace(SpaceId.Studio);
        first.State.SetStudioMode(StudioMode.Batch);
        first.RunMonitor.Dispose();

        var second = new AppShellViewModel(host);
        try
        {
            Assert.Same(hostBefore, second.Current.HostController);
            Assert.Equal("book-1", second.State.Selection.BookId);
            Assert.Equal(SpaceId.Studio, second.State.CurrentSpace);
            Assert.Equal(StudioMode.Batch, second.State.StudioMode);
        }
        finally
        {
            second.RunMonitor.Dispose();
        }

        Assert.Same(hostBefore, first.Current.HostController);
        Assert.Equal(startsBefore, host.StartCalls);
        Assert.Equal(startRequestsBefore, host.StartRequests);
        Assert.Equal(lifecycleBefore, host.LifecycleLog);
    }

    [Fact]
    public void Current_route_adapter_preserves_deep_link_page_identity_and_legacy_boundary()
    {
        const string query = "?space=studio&mode=batch&book=book%201&chapter=ch-1&page=3&page_id=page%2F3&region=region-9";

        Assert.True(CurrentRouteAdapter.TryMap(query, out var route));
        Assert.Equal(SpaceId.Studio, route.Space);
        Assert.Equal(StudioMode.Batch, route.Mode);
        Assert.Equal("book 1", route.BookId);
        Assert.Equal(3, route.PageNumber);
        Assert.Equal("page/3", route.PageId);
        Assert.Equal("region-9", route.RegionId);

        var deepLink = CurrentRouteAdapter.ToShellDeepLink(route);
        Assert.Equal("page/3", deepLink.PageId);
        Assert.Equal(route, CurrentRouteAdapter.Map(deepLink));
        Assert.Equal(query.TrimStart('?'), deepLink.ToQuery());
    }

    [Fact]
    public async Task Reader_keeps_old_anchor_when_new_projection_cannot_map_its_page_id()
    {
        var original = ReaderBook("book-1", "chapter-1", new[]
        {
            new ReaderPageData("page-1", 0, 900, 1200),
            new ReaderPageData("page-2", 1, 900, 1200),
        });
        var host = new FakeHostController(FakeHostController.ReadySnapshot("FEA-04"))
        {
            ReaderBook = original,
        };
        var reader = new ReaderOverlayViewModel(host, (_, _) => { });
        Assert.True(await reader.OpenAsync("book-1", "chapter-1"));
        await reader.GoToAsync(1);
        await reader.ToggleDirectionAsync();
        reader.UpdateWebtoonProgress(0.62);
        var oldPage = reader.CurrentPage;

        host.ReaderBook = ReaderBook("book-1", "chapter-1", new[]
        {
            new ReaderPageData("page-1", 0, 900, 1200),
        });
        var reopened = await reader.OpenAsync("book-1", "chapter-1");

        Assert.False(reopened);
        Assert.Same(oldPage, reader.CurrentPage);
        Assert.Equal("page-2", reader.CurrentPage?.PageId);
        Assert.Equal(ReaderDirection.Ltr, reader.Direction);
        Assert.False(CurrentFrontend.For(host).Session.Reader.AnchorMapped);
        Assert.Contains(CurrentFrontend.For(host).Preflight().Blockers, item => item.Code == "UNMAPPED_READER_ANCHOR");
    }

    [Fact]
    public async Task Rebuilt_batch_and_shell_subscribers_share_one_snapshot_and_projection_read_per_run()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("FEA-04"));
        var started = await host.StartRunAsync(new RunStartRequest(
            "translate_all",
            new Dictionary<string, object?>(),
            null,
            "monitor-test-key"));
        Assert.NotNull(started);
        var gate = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        host.RunSnapshotGate = gate.Task;
        var current = CurrentFrontend.For(host);
        current.Session.Studio.RunId = started!.RunId;
        var workspace = new NewManga.App.ViewModels.V2.Studio.StudioWorkspaceViewModel(host);
        try
        {
            await host.RunSnapshotGateStarted.Task.WaitAsync(TimeSpan.FromSeconds(5));
            using var first = current.SubscribeRun(started.RunId, _ => { });
            using var second = current.SubscribeRun(started.RunId, _ => { });
            var refresh = current.RefreshRunAsync(started.RunId);
            gate.SetResult(true);
            await refresh;

            Assert.Single(host.RunSnapshotRequests);
            Assert.Equal(started.RunId, Assert.Single(host.RunSnapshotRequests));
            Assert.Single(host.TaskProjectionRequests);
            Assert.Equal(started.RunId, Assert.Single(host.TaskProjectionRequests));
        }
        finally
        {
            gate.TrySetResult(true);
            workspace.Batch.SetRunId(null);
        }
    }

    [Fact]
    public void Console_selection_and_filters_are_rebuildable_session_state_not_preflight_blockers()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("FEA-04"));
        var current = CurrentFrontend.For(host);
        current.Session.Console.SelectedSectionId = "Backup";
        current.Session.Console.RunIdInput = "run-1";
        current.Session.Console.TrackedRunId = "run-1";
        current.Session.Studio.RunId = "run-1";

        var before = Capture(host);
        var result = current.Preflight(new CurrentPreflightSignals());

        Assert.True(result.Allowed);
        Assert.Empty(result.Blockers);
        Assert.Equal(before, Capture(host));
    }

    private static CurrentPreflightSignals SignalsFor(string code) => code switch
    {
        "PENDING_REGION_TYPE" => new(PendingRegionType: true),
        "PENDING_CONFIRMATION" => new(PendingConfirmation: true),
        "UNFLUSHED_RUN_KEY" => new(UnacknowledgedRunKey: true),
        "UNMAPPED_READER_ANCHOR" => new(UnmappedReaderAnchor: true),
        "UNMAPPED_SHELL_STATE" => new(UnmappedShellState: true),
        _ => throw new ArgumentOutOfRangeException(nameof(code)),
    };

    private static HostEffects Capture(FakeHostController host) => new(
        host.StartCalls,
        host.StartRequests,
        host.RefreshCalls,
        host.ReaderLoadCount,
        host.RunSnapshotRequests.Count,
        host.TaskProjectionRequests.Count,
        host.StartRunRequests.Count,
        host.SetRegionTypeCalls.Count,
        host.LifecycleLog.Count);

    private static ReaderBookData ReaderBook(string bookId, string chapterId, IReadOnlyList<ReaderPageData> pages) =>
        new(bookId, "FEA-04 Book", chapterId, "Chapter 1", "webtoon_vertical", pages);

    private sealed record HostEffects(
        int StartCalls,
        int StartRequests,
        int RefreshCalls,
        int ReaderLoads,
        int SnapshotReads,
        int ProjectionReads,
        int RunStarts,
        int RegionTypeWrites,
        int LifecycleEntries);
}
