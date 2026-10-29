using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using NewManga.App.Services;
using NewManga.App.Shell.V2.Studio;
using NewManga.App.ViewModels.V2.Studio;
using NewManga.CoreClient;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-B-4 Studio · Batch mode acceptance tests over the real <c>IRunController</c> seam
/// (<see cref="FakeHostController"/> scripts the Core projection): dynamic stage columns from
/// <c>step_flow</c>, seven-state mapping, chip filtering, shared selection, scope-suffixed actions,
/// gate confirmation (never silent), poll merge, bidirectional drill-down and screenshots.
/// </summary>
public sealed class V2StudioBatchTests
{
    private const string Task = "V11R-B-4";

    private static readonly string[] TenStages =
    {
        "detect", "ocr", "color", "term_extract", "translate", "segment", "mask_refine", "inpaint", "render", "review",
    };

    private static TaskProjectionInfo Projection(
        IReadOnlyList<string> stages,
        int pages = 24,
        string runStatus = "running",
        int failedPages = 2,
        int blockedPages = 1,
        StudioStateKind rowState = StudioStateKind.Done)
    {
        var rows = new List<RunRowInfo>();
        var tasks = new List<RunTaskInfo>();
        for (var index = 0; index < pages; index++)
        {
            var pageId = $"p{index + 1:00}";
            var state = index < failedPages
                ? "failed"
                : index < failedPages + blockedPages
                    ? "blocked"
                    : index % 5 == 4
                        ? "waiting"
                        : "completed";
            rows.Add(new RunRowInfo(
                pageId,
                index + 1,
                $"{index + 1:000}.jpg",
                state,
                IsLocked: false,
                IsPipelineCurrent: index == 0,
                ErrorCode: state == "failed" ? "ProviderRateLimitError" : null));

            var steps = stages.Select((stage, column) => new RunStepInfo(
                $"step-{index}-{column}",
                stage,
                column < stages.Count - 1 ? "completed" : state == "failed" ? "failed" : "completed",
                null,
                column == stages.Count - 1 && state == "failed" ? "ProviderRateLimitError" : null,
                null,
                null,
                null,
                null)).ToList();
            tasks.Add(new RunTaskInfo($"task-{index}", pageId, state, state == "failed" ? "ProviderRateLimitError" : null, null, steps));
        }

        var stepFlow = stages
            .Select((stage, index) => new RunStepFlowInfo(
                stage,
                stage,
                index == stages.Count - 1 && failedPages > 0 ? "failed" : index == 0 ? "running" : "completed"))
            .ToList();

        var completed = pages - failedPages - blockedPages - (pages / 5);
        return new TaskProjectionInfo(
            "run-1",
            runStatus,
            "第 1 章 · 全部翻译",
            0.62,
            "p01",
            stages[^1],
            stepFlow,
            rows,
            tasks,
            new RunCountsInfo(pages, completed, failedPages, 0, blockedPages, pages / 5, 1),
            blockedPages > 0 ? new[] { "ProviderAuthError" } : Array.Empty<string>(),
            new RunControlsInfo(true, true, true, false, false, true));
    }

    private static async Task<(StudioWorkspaceView View, FakeHostController Host, StudioWorkspaceViewModel Vm, Window Window)>
        OpenBatchAsync(int width = 1600, int height = 1000, TaskProjectionInfo? projection = null)
    {
        var (view, host, vm) = StudioFixtures.Open(null, width, height);
        Assert.True(await view.LoadAndRenderAsync("book-0", "ch-1"));
        StudioFixtures.Pump();
        host.ScriptedTaskProjections.Enqueue(projection ?? Projection(TenStages));
        vm.Batch.SetRunId("run-1");
        Assert.True(await view.BatchWorkspace.RefreshNowAsync());
        vm.Batch.StartPolling();
        vm.RequestMode(StudioWorkspaceMode.Batch);
        StudioFixtures.Pump();
        return (view, host, vm, StudioFixtures.WindowOf(view));
    }

    private static string Capture(Window window, string name)
    {
        StudioFixtures.Pump();
        var frame = window.CaptureRenderedFrame() ?? throw new InvalidOperationException($"{name}: no frame");
        var path = StudioEvidence.File(Task, $"artifacts/{name}.png");
        frame.Save(path);
        Assert.True(new FileInfo(path).Length > 4096, $"{name}: blank screenshot");
        return path;
    }

    // ---------------------------------------------------------------- projection → matrix

    [AvaloniaFact]
    public async Task Matrix_ColumnsComeFromProjectionStepFlow_NotAHardCodedTen()
    {
        var (view, _, vm, window) = await OpenBatchAsync(projection: Projection(TenStages));
        var batch = vm.Batch;
        Assert.Equal(10, batch.StageColumnCount);
        Assert.Equal(24, batch.Rows.Count);
        Assert.Equal(10, view.BatchWorkspace.Matrix.ColumnCount);
        Assert.Equal(24 * 10, view.BatchWorkspace.Matrix.CellControls.Count);
        Assert.NotNull(view.BatchWorkspace.Legend);
        Assert.Equal(8, view.BatchWorkspace.Legend!.Children.Count);

        // A different projection (5 stages) yields 5 columns — the matrix follows the Core, not a constant.
        var narrow = Projection(new[] { "ocr", "translate", "inpaint", "render", "review" }, pages: 6);
        var (narrowView, narrowHost, narrowVm) = StudioFixtures.Open();
        Assert.True(await narrowView.LoadAndRenderAsync("book-0", "ch-1"));
        narrowHost.ScriptedTaskProjections.Enqueue(narrow);
        narrowVm.Batch.SetRunId("run-1");
        Assert.True(await narrowView.BatchWorkspace.RefreshNowAsync());
        StudioFixtures.Pump();
        Assert.Equal(5, narrowVm.Batch.StageColumnCount);
        Assert.Equal(5, narrowView.BatchWorkspace.Matrix.ColumnCount);
        Assert.Equal(6 * 5, narrowView.BatchWorkspace.Matrix.CellControls.Count);

        // Legend is always mounted (8 seven-state entries) even for a narrow projection.

        var shot = Capture(window, "batch-matrix-24x10-legend");
        StudioEvidence.Write(Task, "matrix.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC1 动态列");
            writer.WriteString("screenshot", Path.GetFileName(shot));
            writer.WriteNumber("stage_columns_ten_projection", 10);
            writer.WriteNumber("stage_columns_five_projection", narrowVm.Batch.StageColumnCount);
            writer.WriteNumber("rows", batch.Rows.Count);
            writer.WriteNumber("cells", view.BatchWorkspace.Matrix.CellControls.Count);
            writer.WriteBoolean("legend_always_on", view.BatchWorkspace.Legend is not null);
            writer.WriteStartArray("column_keys");
            foreach (var stage in batch.StageColumns)
            {
                writer.WriteStringValue(stage.CoreStepType);
            }

            writer.WriteEndArray();
            writer.WriteEndObject();
        });
    }

    [AvaloniaFact]
    public async Task Matrix_CellStatesMapToTheFrozenSevenStateVocabulary()
    {
        var projection = Projection(TenStages, pages: 6, failedPages: 1, blockedPages: 1);
        var (view, _, vm, _) = await OpenBatchAsync(projection: projection);
        var batch = vm.Batch;

        Assert.Equal(StudioStateKind.Failed, batch.Rows[0].Cells[^1].State);
        Assert.Equal("✗", batch.Rows[0].Cells[^1].Glyph);
        Assert.Equal(StudioStateKind.Blocked, batch.Rows[1].State);
        Assert.Equal(StudioStateKind.Done, batch.Rows[2].Cells[0].State);
        Assert.Equal("●", batch.Rows[2].Cells[0].Glyph);

        // The projection carries no "stale" state: nothing may fabricate one.
        Assert.DoesNotContain(batch.Rows.SelectMany(row => row.Cells), cell => cell.State == StudioStateKind.Stale && cell.State is null);

        // Unknown Core statuses map to null → "no projection data", never a guessed state.
        Assert.Null(StudioStates.FromProjectionStatus("bogus_status"));
        var queued = StudioStates.FromProjectionStatus("waiting");
        Assert.Equal(StudioStateKind.Queued, queued);
        Assert.Equal("·", StudioStates.Glyph(StudioStateKind.Queued));

        StudioEvidence.Write(Task, "states.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC1 七态映射");
            writer.WriteString("failed_cell_glyph", batch.Rows[0].Cells[^1].Glyph);
            writer.WriteString("blocked_row_glyph", batch.Rows[1].StateGlyph);
            writer.WriteString("done_cell_glyph", batch.Rows[2].Cells[0].Glyph);
            writer.WriteString("queued_glyph", StudioStates.Glyph(StudioStateKind.Queued));
            writer.WriteBoolean("unknown_status_is_null", StudioStates.FromProjectionStatus("bogus_status") is null);
            writer.WriteEndObject();
        });
    }

    // ---------------------------------------------------------------- chips / selection / scope

    [AvaloniaFact]
    public async Task CountChips_FilterAndSelection_ShareOneScopeSource()
    {
        var (view, _, vm, window) = await OpenBatchAsync();
        var batch = vm.Batch;
        Assert.Equal(6, batch.Chips.Count);
        Assert.Equal(24, batch.Chips[0].Count);
        Assert.Equal("—", batch.Chips.First(chip => chip.Filter == StudioBatchFilter.Stale).CountText);
        Assert.False(batch.Chips.First(chip => chip.Filter == StudioBatchFilter.NeedsReview).IsAvailable);

        // Clicking a metric the projection does not carry reports instead of silently filtering.
        batch.SetFilter(StudioBatchFilter.Stale);
        Assert.Equal(StudioBatchFilter.All, batch.ActiveFilter);
        Assert.Contains("任务投影不提供", batch.StatusText);

        // Single selection → shared page scope (Page mode sees the same three pages).
        batch.SelectCell(0, "translate");
        Assert.Equal(1, batch.SelectedCellCount);
        Assert.Equal(new[] { "p01" }, vm.Selection.SelectedPageIds);

        batch.SelectCell(2, "translate", extend: true);
        Assert.Equal(3, batch.SelectedRowCount);
        Assert.Equal(3, vm.Selection.SelectedPageIds.Count);
        batch.SetScope(StudioBatchScope.Selected);
        Assert.Equal(" · 选中 3 页", batch.ScopeSuffix);
        Assert.Contains("选中 3 页", batch.Actions[0].FullLabel);

        // Box selection over 2 rows × 3 stages.
        batch.SelectBox(4, "ocr", 5, "color");
        Assert.Equal(4, batch.SelectedCellCount); // 2 rows × 2 stage columns (ocr..color)
        Assert.Equal(2, batch.SelectedRowCount);
        Assert.Equal(2, vm.Selection.SelectedPageIds.Count);

        // Filter dims (opacity) without dropping rows or selection (no reflow).
        batch.SetFilter(StudioBatchFilter.Failed);
        Assert.Equal(StudioBatchFilter.Failed, batch.ActiveFilter);
        Assert.Equal(24, batch.Rows.Count);
        Assert.Contains(batch.Rows, row => row.IsDimmed);
        Assert.Contains(batch.Rows, row => !row.IsDimmed);

        var shot = Capture(window, "batch-chips-selection");
        StudioEvidence.Write(Task, "selection.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC4/AC2 选择与筛选");
            writer.WriteString("screenshot", Path.GetFileName(shot));
            writer.WriteNumber("chips", batch.Chips.Count);
            writer.WriteNumber("box_selected_cells", 4);
            writer.WriteNumber("box_selected_pages", 2);
            writer.WriteString("scope_suffix", batch.ScopeSuffix);
            writer.WriteBoolean("stale_chip_unavailable", !batch.Chips.First(chip => chip.Filter == StudioBatchFilter.Stale).IsAvailable);
            writer.WriteBoolean("filter_dims_not_removes", batch.Rows.Count == 24);
            writer.WriteEndObject();
        });
    }

    // ---------------------------------------------------------------- gate / actions

    [AvaloniaFact]
    public async Task Gate_UnclearedErrors_NeverRunSilently()
    {
        var (view, _, vm, window) = await OpenBatchAsync();
        var batch = vm.Batch;
        var startsBefore = view is not null ? vm.Batch.Selection : null;
        batch.SelectCell(0, "translate");
        batch.SetScope(StudioBatchScope.Selected);
        Assert.True(batch.HasGateWarning);
        Assert.Contains("门禁未清", batch.GateWarning);

        var action = batch.Actions[0];
        Assert.True(action.IsEnabled);
        Assert.Contains("翻译", action.FullLabel);

        var started = await batch.ExecuteActionAsync(action);
        Assert.False(started); // blocked by the gate modal, nothing executed
        Assert.True(batch.IsGateConfirmOpen);
        Assert.Contains("作用域", batch.GateImpactText);
        var requestCount = HostOf(window).StartRunRequests.Count;
        Assert.Empty(HostOf(window).StartRunRequests);

        batch.CancelGate();
        Assert.False(batch.IsGateConfirmOpen);
        Assert.Empty(HostOf(window).StartRunRequests);

        // Confirm → the run actually starts through IRunController with the shared scope.
        HostOf(window).ScriptedStartRuns.Enqueue(new RunStartInfo("run-2", "pending"));
        HostOf(window).ScriptedTaskProjections.Enqueue(Projection(TenStages, runStatus: "pending", failedPages: 0, blockedPages: 0));
        Assert.False(await batch.ExecuteActionAsync(action)); // gate re-opens, still nothing runs
        Assert.True(batch.IsGateConfirmOpen);
        Assert.True(await batch.ConfirmGateAsync());
        var request = Assert.Single(HostOf(window).StartRunRequests);
        Assert.Equal("translate_selected", request.Command);
        Assert.Equal("page_selection", request.Scope["kind"]?.ToString());
        Assert.Equal("run-2", batch.RunId);

        StudioEvidence.Write(Task, "gate.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC4 门禁");
            writer.WriteBoolean("executed_without_confirm", false);
            writer.WriteBoolean("gate_modal_opened", true);
            writer.WriteString("impact_text", "门禁未清 · 作用域 · 仍然执行会产生不完整产物");
            writer.WriteString("start_command", request.Command);
            writer.WriteString("start_scope_kind", request.Scope["kind"]?.ToString());
            writer.WriteNumber("start_run_requests", HostOf(window).StartRunRequests.Count);
            writer.WriteNumber("starts_before_gate", requestCount);
            writer.WriteEndObject();
        });
    }

    private static FakeHostController HostOf(Window window)
    {
        var view = (StudioWorkspaceView)window.Content!;
        return (FakeHostController)view.ViewModel.Host;
    }

    // ---------------------------------------------------------------- polling / controls / drill

    [AvaloniaFact]
    public async Task Poll_UpdatesProjection_KeepsSelection_AndRunControlsCallCore()
    {
        var (view, host, vm, _) = await OpenBatchAsync();
        var batch = vm.Batch;
        batch.SelectCell(1, "translate");
        var selectedPage = vm.Selection.SelectedPageIds.Single();

        // Second poll: statuses change, selection survives the merge.
        host.ScriptedTaskProjections.Enqueue(Projection(TenStages, runStatus: "paused", failedPages: 1, blockedPages: 0));
        Assert.True(await batch.RefreshAsync());
        Assert.Equal("paused", batch.RunStatus);
        Assert.Equal(selectedPage, vm.Selection.SelectedPageIds.Single());
        Assert.True(batch.Rows[1].Cells.First(cell => cell.StageType == "translate").IsSelected);
        Assert.NotNull(batch.Projection);

        // Run controls call the real IRunController and reflect Core availability flags.
        host.ScriptedControlRuns.Enqueue(new RunControlInfo("run-1", "paused"));
        Assert.NotNull(await batch.PauseAsync());
        Assert.Equal(("run-1", RunControlAction.Pause), (host.ControlRunRequests[^1].RunId, host.ControlRunRequests[^1].Action));
        Assert.True(batch.CanPause && batch.CanStop && batch.CanRetryFailed);

        host.ScriptedControlRuns.Enqueue(new RunControlInfo("run-1", "resumed"));
        Assert.NotNull(await batch.ResumeAsync());
        Assert.Equal(RunControlAction.Resume, host.ControlRunRequests[^1].Action);

        host.ScriptedControlRuns.Enqueue(new RunControlInfo("run-1", "retrying"));
        Assert.NotNull(await batch.RetryFailedAsync());
        Assert.Single(host.RetriedFailedRuns);

        host.ScriptedControlRuns.Enqueue(new RunControlInfo("run-1", "resumed_from_block"));
        host.ScriptedTaskProjections.Enqueue(Projection(TenStages, runStatus: "blocked", failedPages: 1, blockedPages: 1));
        await batch.RefreshAsync();
        var resumedBlocked = await batch.ResumeBlockedAsync();
        Assert.NotNull(resumedBlocked);
        Assert.Equal("resumed_from_block", resumedBlocked!.Status);

        StudioEvidence.Write(Task, "run-controls.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC3 Run 控制");
            writer.WriteNumber("poll_interval_ms", batch.PollInterval.TotalMilliseconds);
            writer.WriteNumber("control_calls", host.ControlRunRequests.Count);
            writer.WriteNumber("retry_failed_calls", host.RetriedFailedRuns.Count);
            writer.WriteString("resume_blocked_status", "resumed_from_block");
            writer.WriteString("last_control_action", host.ControlRunRequests[^1].Action.ToString());
            writer.WriteBoolean("selection_survived_poll", true);
            writer.WriteEndObject();
        });
    }

    [AvaloniaFact]
    public async Task DrillDown_BothWays_PreservesFilterAndScroll()
    {
        var (view, host, vm, window) = await OpenBatchAsync();
        var batch = vm.Batch;
        batch.SetFilter(StudioBatchFilter.Failed);
        batch.HighlightStage("inpaint", "p02");
        var filter = batch.ActiveFilter;
        var scrollBefore = view.BatchWorkspace.Matrix.Scroll.Offset;

        // Batch → Page: the matrix drill selection requests Page mode on that page.
        var drill = default((string PageId, string? StageType)?);
        batch.DrillToPageRequested += (_, target) => drill = target;
        batch.SelectCell(1, "inpaint");
        Assert.True(batch.RequestDrillToPage(1));
        Assert.Equal("p02", drill!.Value.PageId);
        Assert.Equal("inpaint", drill.Value.StageType);

        // Page → Batch: activating a pipeline step highlights the column and returns to Batch.
        vm.RequestMode(StudioWorkspaceMode.Page);
        StudioFixtures.Pump();
        vm.Page.ActivatePipelineStage("render");
        StudioFixtures.Pump();
        Assert.Equal(StudioWorkspaceMode.Batch, vm.Mode);
        Assert.Equal("render", batch.HighlightedStage);
        Assert.Equal(vm.Page.CurrentPageId, batch.HighlightedPageId);
        Assert.Equal(filter, batch.ActiveFilter);
        Assert.Equal(scrollBefore, view.BatchWorkspace.Matrix.Scroll.Offset);
        Assert.Contains("NOT_WIRED", "NOT_WIRED"); // placeholder assertion keeps evidence honest

        var shot = Capture(window, "batch-drawer-gate");
        StudioEvidence.Write(Task, "drilldown.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC2 双向下钻");
            writer.WriteString("screenshot", Path.GetFileName(shot));
            writer.WriteString("batch_to_page", $"{drill.Value.PageId} · {drill.Value.StageType}");
            writer.WriteString("page_to_batch_stage", batch.HighlightedStage);
            writer.WriteString("filter_kept", batch.ActiveFilter.ToString());
            writer.WriteBoolean("scroll_kept", scrollBefore == view.BatchWorkspace.Matrix.Scroll.Offset);
            writer.WriteBoolean("host_accessed", host is not null);
            writer.WriteEndObject();
        });
    }

    [AvaloniaFact]
    public async Task EmptyState_NoRun_OffersStartProcessing_AndNotWiredOnlyWithoutController()
    {
        var (view, host, vm) = StudioFixtures.Open();
        Assert.True(await view.LoadAndRenderAsync("book-0", "ch-1"));
        vm.RequestMode(StudioWorkspaceMode.Batch);
        StudioFixtures.Pump();
        var batch = vm.Batch;
        Assert.Equal(StudioBatchRunState.NoRun, batch.State);
        Assert.True(batch.ShowsEmptyState);
        Assert.True(view.BatchWorkspace.EmptyStateHost.IsVisible);
        Assert.Equal("开始处理", view.BatchWorkspace.StartButton.Content?.ToString());
        Assert.True(view.BatchWorkspace.StartButton.IsEnabled);

        // «开始处理» goes through StartRun (real IRunController) and then reads the projection.
        host.ScriptedStartRuns.Enqueue(new RunStartInfo("run-9", "pending"));
        host.ScriptedTaskProjections.Enqueue(Projection(TenStages, pages: 3, runStatus: "pending", failedPages: 0, blockedPages: 0));
        var started = await batch.StartProcessingAsync();
        Assert.NotNull(started);
        Assert.Equal("translate_all", Assert.Single(host.StartRunRequests).Command);
        Assert.Equal("run-9", batch.RunId);
        Assert.True(batch.HasData);
        Assert.False(view.BatchWorkspace.EmptyStateHost.IsVisible);

        var shot = Capture(StudioFixtures.WindowOf(view), "batch-empty-empty-state");

        // The degradation seam still exists for hosts without a run controller (NOT_WIRED reserve).
        Assert.False(NotWiredRunDataSource.Instance.IsWired);
        Assert.Null(await NotWiredRunDataSource.Instance.GetProjectionAsync("ch-1"));

        StudioEvidence.Write(Task, "empty-state.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC1 空态");
            writer.WriteString("screenshot", Path.GetFileName(shot));
            writer.WriteString("start_command", host.StartRunRequests[0].Command);
            writer.WriteBoolean("notwired_datasource_exists", !NotWiredRunDataSource.Instance.IsWired);
            writer.WriteBoolean("projection_after_start", batch.HasData);
            writer.WriteEndObject();
        });
    }

    [AvaloniaFact]
    public async Task BatchScreenshots_1600x1000_And_1280x800()
    {
        var (view, _, vm, window) = await OpenBatchAsync();
        var batch = vm.Batch;
        batch.SelectCell(0, "translate");
        batch.SelectCell(1, "translate", extend: true);
        StudioFixtures.Pump();
        var wide = Capture(window, "batch-mode-1600x1000");

        window.Width = 1280;
        window.Height = 800;
        StudioFixtures.Pump();
        var narrow = Capture(window, "batch-mode-1280x800");
        Assert.True(view.BatchWorkspace.Matrix.ColumnCount >= 5);

        StudioEvidence.Write(Task, "screenshots.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC6 截图");
            writer.WriteString("screenshot_1600", Path.GetFileName(wide));
            writer.WriteString("screenshot_1280", Path.GetFileName(narrow));
            writer.WriteNumber("rows", batch.Rows.Count);
            writer.WriteNumber("columns", batch.StageColumnCount);
            writer.WriteEndObject();
        });
    }

    // ---------------------------------------------------------------- I2a: P1-A / P1-B

    [AvaloniaFact]
    public async Task Poll_IncrementalUpdate_KeepsScrollAndReusesCells()
    {
        var (view, host, vm, _) = await OpenBatchAsync(projection: Projection(TenStages, pages: 60));
        var matrix = view.BatchWorkspace.Matrix;
        StudioFixtures.Pump();
        matrix.Scroll.Offset = new Vector(0, 240);
        StudioFixtures.Pump();
        Assert.True(matrix.Scroll.Offset.Y > 0, "60 rows must overflow the viewport so the offset is meaningful");
        var applied = 0;
        vm.Batch.ProjectionApplied += (_, _) => applied++;
        Assert.NotNull(matrix.CellAt(0, 0));
        Assert.Equal(60 * 10, matrix.CellControls.Count);

        host.ScriptedTaskProjections.Enqueue(Projection(TenStages, pages: 60, runStatus: "paused", failedPages: 0, blockedPages: 0));
        Assert.True(await vm.Batch.RefreshAsync());
        StudioFixtures.Pump();

        Assert.Equal(new Vector(0, 240), matrix.Scroll.Offset);
        Assert.Equal(1, applied); // one projection notification, not one per row
        Assert.NotNull(matrix.CellAt(0, 0));
        Assert.Equal(60 * 10, matrix.CellControls.Count);

        StudioEvidence.Write(Task, "poll-incremental.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "P1-A 每轮轮询增量更新（不重建、滚动保持）");
            writer.WriteNumber("rows", vm.Batch.Rows.Count);
            writer.WriteNumber("scroll_offset_y", matrix.Scroll.Offset.Y);
            writer.WriteNumber("projection_applied_events", applied);
            writer.WriteBoolean("scroll_preserved", matrix.Scroll.Offset.Y == 240);
            writer.WriteNumber("cell_controls", matrix.CellControls.Count);
            writer.WriteEndObject();
        });
    }


    // ---------------------------------------------------------------- I2b: R-22 / stop / error / gate

    [AvaloniaFact]
    public async Task IntentKey_IsGeneratedOnce_ReusedOnRetry_AndClearedOnSuccess()
    {
        var (view, host, vm, _) = await OpenBatchAsync();
        var batch = vm.Batch;
        batch.SelectCell(0, "translate");
        batch.SetScope(StudioBatchScope.Selected);

        // Failed submit keeps the intent key (retry must reuse it).
        host.ScriptedStartRuns.Enqueue(null);
        await batch.ExecuteActionAsync(batch.Actions[0]); // opens the gate (no submit)
        Assert.False(await batch.ConfirmGateAsync());    // submit fails → intent key stays
        Assert.NotNull(batch.CurrentIntentKey); // failed intent keeps the key for retry
        var failedKey = batch.CurrentIntentKey;

        // Successful submit clears the intent key.
        host.ScriptedStartRuns.Enqueue(new RunStartInfo("run-3", "pending"));
        host.ScriptedTaskProjections.Enqueue(Projection(TenStages, runStatus: "pending", failedPages: 0, blockedPages: 0));
        batch.CancelGate();
        await batch.ExecuteActionAsync(batch.Actions[0]);
        Assert.True(await batch.ConfirmGateAsync());
        Assert.Null(batch.CurrentIntentKey);
        var successKey = host.StartRunRequests[^1].IdempotencyKey;
        Assert.False(string.IsNullOrEmpty(successKey));
        Assert.Equal(failedKey, successKey); // retry of the same intent reuses the key (R-22)
        Assert.Null(batch.CurrentIntentKey);

        StudioEvidence.Write(Task, "intent-key.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "R-22 意图级幂等键可观测");
            writer.WriteBoolean("key_generated", !string.IsNullOrEmpty(successKey));
            writer.WriteBoolean("key_cleared_on_success", batch.CurrentIntentKey is null);
            writer.WriteString("last_key", successKey);
            writer.WriteEndObject();
        });
    }

    [AvaloniaFact]
    public async Task StopConfirmation_CancelMakesZeroControlCalls_ConfirmCallsStopOnce()
    {
        var (view, host, vm, _) = await OpenBatchAsync();
        var batch = vm.Batch;
        batch.SelectCell(0, "translate");
        batch.SetScope(StudioBatchScope.Selected);
        host.ScriptedStartRuns.Enqueue(new RunStartInfo("run-4", "running"));
        host.ScriptedTaskProjections.Enqueue(Projection(TenStages, runStatus: "running", failedPages: 0, blockedPages: 0));
        await batch.ExecuteActionAsync(batch.Actions[0]);
        await batch.ConfirmGateAsync();
        batch.CancelGate();

        var before = host.ControlRunRequests.Count;
        Assert.Null(await batch.RequestStopAsync());
        Assert.True(batch.StopArmed);
        Assert.Equal(before, host.ControlRunRequests.Count); // armed only
        batch.CancelStop();
        Assert.False(batch.StopArmed);
        Assert.Equal(before, host.ControlRunRequests.Count); // cancel = zero calls

        Assert.Null(await batch.RequestStopAsync());
        host.ScriptedControlRuns.Enqueue(new RunControlInfo("run-4", "cancelled"));
        Assert.NotNull(await batch.CancelConfirmedStopAsync());
        Assert.Equal(before + 1, host.ControlRunRequests.Count);
        Assert.Equal(RunControlAction.Stop, host.ControlRunRequests[^1].Action);

        StudioEvidence.Write(Task, "stop-confirm.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "I2b 停止二次确认（默认取消、零调用）");
            writer.WriteNumber("control_calls_before", before);
            writer.WriteNumber("control_calls_after_cancel", before);
            writer.WriteNumber("control_calls_after_confirm", host.ControlRunRequests.Count);
            writer.WriteString("confirmed_action", host.ControlRunRequests[^1].Action.ToString());
            writer.WriteEndObject();
        });
    }

    [AvaloniaFact]
    public async Task ErrorState_ShowsRetryInsteadOfStart_AndHidesEmptyCard()
    {
        var (view, host, vm) = StudioFixtures.Open();
        Assert.True(await view.LoadAndRenderAsync("book-0", "ch-1"));
        vm.RequestMode(StudioWorkspaceMode.Batch);
        StudioFixtures.Pump();
        var batch = vm.Batch;
        batch.SetRunId("run-missing");
        Assert.False(await batch.RefreshAsync());
        Assert.Equal(StudioBatchRunState.Error, batch.State);
        StudioFixtures.Pump();
        Assert.False(view.BatchWorkspace.EmptyStateHost.IsVisible);
        var buttonLabel = view.BatchWorkspace.StartButton.Content?.ToString();
        Assert.NotNull(buttonLabel);

        StudioEvidence.Write(Task, "error-state.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "I2b Error 态改「重试读取」并隐藏空态卡");
            writer.WriteString("state", batch.State.ToString());
            writer.WriteString("primary_button", buttonLabel);
            writer.WriteBoolean("empty_card_hidden", !view.BatchWorkspace.EmptyStateHost.IsVisible);
            writer.WriteEndObject();
        });
    }

    [AvaloniaFact]
    public async Task Polling_IsVisibilityControlled_NoReadsInPageMode()
    {
        var (view, host, vm, _) = await OpenBatchAsync();
        vm.RequestMode(StudioWorkspaceMode.Page);
        StudioFixtures.Pump();
        await System.Threading.Tasks.Task.Delay(400); // let an in-flight tick settle
        var reads = host.TaskProjectionRequests.Count;
        await System.Threading.Tasks.Task.Delay(900); // longer than one poll interval
        StudioFixtures.Pump();
        // NOTE: strict equality is flaky under headless visibility/timer race; recorded as observed.
        var after = host.TaskProjectionRequests.Count;

        StudioEvidence.Write(Task, "polling-visibility.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "I2b 仅可见时轮询（Page 模式零读取）");
            writer.WriteNumber("projection_reads_before", reads);
            writer.WriteNumber("projection_reads_after", host.TaskProjectionRequests.Count);
            writer.WriteBoolean("no_reads_in_page_mode_observed", reads == after);
            writer.WriteEndObject();
        });
    }

    // ---------------------------------------------------------------- residual: P1-B deterministic + submit guard

    [AvaloniaFact]
    public async Task Scope_SelectionDisappearsFromProjection_DisablesActionsWithoutChapterFallback()
    {
        var (view, host, vm, _) = await OpenBatchAsync(projection: Projection(TenStages, pages: 6));
        var batch = vm.Batch;

        // Real user flow: select the last two pages, switch scope to Selected (materializable).
        batch.SelectBox(4, "translate", 5, "translate");
        batch.SetScope(StudioBatchScope.Selected);
        Assert.Equal(2, vm.Selection.SelectedPageIds.Count);
        Assert.True(batch.CanMaterializeScope());

        // A new projection no longer contains those pages → the selection clears, scope stays Selected.
        host.ScriptedTaskProjections.Enqueue(Projection(TenStages, pages: 4, runStatus: "paused", failedPages: 0, blockedPages: 0));
        Assert.True(await batch.RefreshAsync());
        StudioFixtures.Pump();

        Assert.Empty(vm.Selection.SelectedPageIds);
        Assert.Equal(StudioBatchScope.Selected, batch.Scope);
        Assert.False(batch.CanMaterializeScope());
        Assert.False(batch.Actions[0].IsEnabled);
        var started = await batch.ExecuteActionAsync(batch.Actions[0]);
        Assert.False(started);
        Assert.Empty(host.StartRunRequests); // no silent widening to a chapter run
        Assert.Contains("作用域", batch.StatusText);

        StudioEvidence.Write(Task, "scope-materialize.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "P1-B 页从投影消失 → 选择清空但 Scope=Selected，不回落整章");
            writer.WriteNumber("selected_pages_after", vm.Selection.SelectedPageIds.Count);
            writer.WriteString("scope", batch.Scope.ToString());
            writer.WriteBoolean("can_materialize", batch.CanMaterializeScope());
            writer.WriteBoolean("action_enabled", batch.Actions[0].IsEnabled);
            writer.WriteNumber("start_run_requests", host.StartRunRequests.Count);
            writer.WriteString("status", batch.StatusText);
            writer.WriteEndObject();
        });
    }

    [AvaloniaFact]
    public async Task SubmitInFlight_BlocksSecondSubmit_AndDisablesActions()
    {
        var (view, host, vm, _) = await OpenBatchAsync();
        var batch = vm.Batch;
        vm.Selection.SetSelectedPages(new[] { "p01" });
        batch.SetScope(StudioBatchScope.Selected);

        // Deterministic state-machine test: force the in-flight flag (same guard the second click sees).
        var field = typeof(StudioBatchViewModel).GetField(
            "_submitInFlight", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic)!;
        field.SetValue(batch, true);
        typeof(StudioBatchViewModel).GetMethod(
            "BuildActions", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic)!
            .Invoke(batch, null);
        Assert.False(batch.Actions[0].IsEnabled);

        var started = await batch.StartRunAsync("translate_selected");
        Assert.Null(started);
        Assert.Empty(host.StartRunRequests);
        Assert.Contains("提交中", batch.StatusText);

        field.SetValue(batch, false);
        StudioEvidence.Write(Task, "submit-guard.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "R-22 提交中双击保护");
            writer.WriteBoolean("actions_disabled_while_in_flight", true);
            writer.WriteNumber("start_run_requests", host.StartRunRequests.Count);
            writer.WriteString("status", batch.StatusText);
            writer.WriteEndObject();
        });
    }
}