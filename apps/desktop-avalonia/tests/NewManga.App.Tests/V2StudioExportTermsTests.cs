using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using NewManga.App.Services;
using NewManga.App.Shell.V2.Studio;
using NewManga.App.ViewModels.V2.Studio;
using NewManga.App.Views.V2.Studio.Controls;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-B-5 acceptance tests: export preflight / history / progress / cancel over the real
/// <see cref="IHostController"/> export face, plus the honest NOT_WIRED terms workbench.
/// Verified degradation facts (recorded in <c>verification/V11R-B-5/preflight.json</c>):
/// Core supports abort|continue_existing but the frozen Host signature exposes no stale_policy
/// parameter, and no glossary/do-not-translate/constraint command exists — both are surfaced, not faked.
/// </summary>
public sealed class V2StudioExportTermsTests
{
    private const string EvidenceTask = "V11R-B-5";

    private static string Capture(Window window, string name)
    {
        StudioFixtures.Pump();
        var frame = window.CaptureRenderedFrame() ?? throw new InvalidOperationException($"{name}: no frame");
        var path = StudioEvidence.File(EvidenceTask, $"artifacts/{name}.png");
        frame.Save(path);
        Assert.True(new FileInfo(path).Length > 4096, $"{name}: blank screenshot");
        return path;
    }

    private static async Task<(StudioWorkspaceView View, FakeHostController Host, StudioWorkspaceViewModel Vm, Window Window)>
        OpenAsync(int width = 1600, int height = 1000)
    {
        var (view, host, vm) = StudioFixtures.Open(null, width, height);
        Assert.True(await view.LoadAndRenderAsync("book-0", "ch-1"));
        StudioFixtures.Pump();
        host.TranslatedPagesByChapter["ch-1"] = new[] { "p1", "p2", "p3" };
        return (view, host, vm, StudioFixtures.WindowOf(view));
    }

    // ---------------------------------------------------------------- preflight

    [AvaloniaFact]
    public async Task Preflight_UsesRealReads_AndRendersUnavailableCountsAsDash()
    {
        var (view, host, vm, window) = await OpenAsync();
        var export = vm.Export;
        Assert.True(await export.RefreshPreflightAsync());
        Assert.Equal(3, export.TranslatedPageCount);
        Assert.Equal(3, export.ExportablePageIds.Count);
        Assert.Equal(1, host.TranslatedPageCalls);
        Assert.Equal(StudioExportPhase.Ready, export.Phase);

        // 未确认 / 过期 have no read face: "—" + reason, never fabricated zeros.
        Assert.Null(export.UnconfirmedPageCount);
        Assert.Null(export.StalePageCount);
        Assert.Equal("—", export.UnconfirmedText);
        Assert.Contains("未接入", export.UnconfirmedTooltip);
        Assert.Contains("StartExport", export.StaleTooltip);

        // Failed/blocked come from the real run projection only when one exists.
        Assert.False(export.HasRunProjection);
        Assert.Equal(0, export.FailedPageCount);

        // Scope = chapter exports all translated pages; selection scope intersects the shared selection.
        Assert.Equal(new[] { "p1", "p2", "p3" }, export.ExportablePageIds);
        vm.Selection.SetSelectedPages(new[] { "p2", "p3" });
        export.Scope = StudioExportScope.SelectedPages;
        Assert.Equal(new[] { "p2", "p3" }, export.ExportablePageIds);
        Assert.Equal("选中 2 页", export.ScopeText);

        await view.Tools.OpenAsync(StudioToolsTab.Preflight);
        StudioFixtures.Pump();
        var panel = view.Tools.Preflight;
        Assert.Equal("3", panel.TranslatedText.Text);
        Assert.Equal("2", panel.ExportableText.Text);
        Assert.Equal("—", panel.UnconfirmedText.Text);
        Assert.Equal("—", panel.StaleText.Text);

        var shot = Capture(window, "export-preflight");
        StudioEvidence.Write(EvidenceTask, "preflight.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC1 预检数据");
            writer.WriteString("screenshot", Path.GetFileName(shot));
            writer.WriteNumber("translated_pages", export.TranslatedPageCount);
            writer.WriteNumber("selected_exportable", export.ExportablePageIds.Count);
            writer.WriteString("unconfirmed", export.UnconfirmedText);
            writer.WriteString("stale", export.StaleText);
            writer.WriteBoolean("has_run_projection", export.HasRunProjection);
            writer.WriteNumber("translated_page_calls", host.TranslatedPageCalls);
            writer.WriteEndObject();
        });
    }

    [AvaloniaFact]
    public async Task StalePolicy_OnlyTheHostSupportedOptionIsSelectable()
    {
        var (view, _, vm, _) = await OpenAsync();
        var export = vm.Export;
        await view.Tools.OpenAsync(StudioToolsTab.Preflight);
        StudioFixtures.Pump();

        Assert.True(export.CanSelectStalePolicy(StudioStalePolicy.Abort));
        Assert.False(export.CanSelectStalePolicy(StudioStalePolicy.ContinueExisting));
        Assert.False(view.Tools.Preflight.ContinueExistingButton.IsEnabled);
        Assert.Contains("未支持", view.Tools.Preflight.ContinueExistingButton.Content?.ToString());

        // Attempting the unsupported policy reports why; it never silently becomes selected.
        Assert.False(export.TrySelectStalePolicy(StudioStalePolicy.ContinueExisting));
        Assert.Equal(StudioStalePolicy.Abort, export.StalePolicy);
        Assert.Contains("未暴露 stale_policy", export.StatusText);
        Assert.Contains("continue_existing", StudioExportViewModel.ContinueExistingNotSupported);

        StudioEvidence.Write(EvidenceTask, "stale-policy.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC1 stale 策略诚实降级");
            writer.WriteBoolean("abort_supported", export.CanSelectStalePolicy(StudioStalePolicy.Abort));
            writer.WriteBoolean("continue_existing_supported", export.CanSelectStalePolicy(StudioStalePolicy.ContinueExisting));
            writer.WriteString("verified_fact", StudioExportViewModel.ContinueExistingNotSupported);
            writer.WriteBoolean("ui_option_disabled", !view.Tools.Preflight.ContinueExistingButton.IsEnabled);
            writer.WriteBoolean("selection_attempt_refused", export.StalePolicy == StudioStalePolicy.Abort);
            writer.WriteEndObject();
        });
    }

    // ---------------------------------------------------------------- start / progress / cancel / reveal

    [AvaloniaFact]
    public async Task Start_PollsSnapshot_CancelLeavesNoResidual_AndRevealCallsHost()
    {
        var (view, host, vm, window) = await OpenAsync();
        var export = vm.Export;
        await view.Tools.OpenAsync(StudioToolsTab.Preflight);
        Assert.True(await export.RefreshPreflightAsync());

        export.Format = StudioExportFormat.Pdf;
        export.PdfContent = StudioPdfContentMode.SearchableDualLayer;
        host.ScriptedStartResults.Enqueue(ExportStartInfo.FromState("exp-9", "pending", 3));
        host.ScriptedSnapshots.Enqueue(new ExportSnapshotInfo("exp-9", ExportJobState.Running, 1, 3, "p2"));
        Assert.NotNull(await export.StartExportAsync());

        var start = Assert.Single(host.StartExportCalls);
        Assert.Equal("pdf", start.Format);
        Assert.Equal("searchable_dual_layer", start.PdfContent);
        Assert.Equal(new[] { "p1", "p2", "p3" }, start.PageIds);
        Assert.Contains("newmanga-ch-1", start.TargetPath);
        Assert.True(export.IsRunning);
        Assert.Equal(1, export.SnapshotCompleted);
        Assert.Equal(3, export.SnapshotTotal);
        Assert.Equal(33, Math.Round(export.SnapshotPercent));

        // Poll ticks update progress through the real GetExportSnapshot read.
        host.ScriptedSnapshots.Enqueue(new ExportSnapshotInfo(
            "exp-9", ExportJobState.Completed, 3, 3, null, "/exports/ch1.zip", "abcdef0123456789", null, "zip"));
        var ticked = export.TickAsync();
        await Task.Delay(1);
        await export.RefreshSnapshotAsync();
        await ticked;
        Assert.Equal(StudioExportPhase.Completed, export.Phase);
        Assert.True(export.IsTerminal);
        Assert.False(export.CanCancel);
        Assert.True(export.CanReveal);
        Assert.Contains("ch1.zip", export.OutputText);
        Assert.DoesNotContain("/exports", export.OutputText); // absolute paths are never rendered

        Assert.True(await export.RevealAsync());
        Assert.Equal(new[] { "exp-9" }, host.RevealCalls);

        // Cancel path: running job → CancelExport called, phase Cancelled, no further polling.
        host.ScriptedStartResults.Enqueue(ExportStartInfo.FromState("exp-10", "running", 3));
        host.ScriptedSnapshots.Enqueue(new ExportSnapshotInfo("exp-10", ExportJobState.Running, 0, 3));
        Assert.NotNull(await export.StartExportAsync());
        host.ScriptedSnapshots.Enqueue(new ExportSnapshotInfo("exp-10", ExportJobState.Cancelled, 0, 3));
        Assert.NotNull(await export.CancelAsync());
        Assert.Equal(new[] { "exp-10" }, host.CancelCalls);
        Assert.Equal(StudioExportPhase.Cancelled, export.Phase);
        Assert.False(export.CanCancel);
        var callsAfterCancel = host.SnapshotCalls.Count;
        await export.TickAsync();
        Assert.Equal(callsAfterCancel, host.SnapshotCalls.Count); // terminal → no residual polling

        var shot = Capture(window, "export-cancelled");
        StudioEvidence.Write(EvidenceTask, "export-job.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC2 导出/轮询/取消/揭示");
            writer.WriteString("screenshot", Path.GetFileName(shot));
            writer.WriteString("format", start.Format);
            writer.WriteString("pdf_content", start.PdfContent);
            writer.WriteNumber("page_ids", start.PageIds.Count);
            writer.WriteNumber("snapshot_calls", host.SnapshotCalls.Count);
            writer.WriteNumber("cancel_calls", host.CancelCalls.Count);
            writer.WriteNumber("reveal_calls", host.RevealCalls.Count);
            writer.WriteString("final_phase", export.Phase.ToString());
            writer.WriteBoolean("output_hides_absolute_path", !export.OutputText.Contains("/exports"));
            writer.WriteEndObject();
        });
    }

    [AvaloniaFact]
    public async Task ReadOnlyHost_CannotStartExport_AndSaysWhy()
    {
        var (view, host, vm, _) = await OpenAsync();
        var export = vm.Export;
        await view.Tools.OpenAsync(StudioToolsTab.Preflight);
        host.Snapshot = host.Snapshot with { WritesAllowed = false };
        Assert.True(await export.RefreshPreflightAsync());
        Assert.False(export.WritesAllowed);
        Assert.False(export.CanStart);
        Assert.Null(await export.StartExportAsync());
        Assert.Contains("只读", export.StatusText);
        Assert.Empty(host.StartExportCalls);

        StudioEvidence.Write(EvidenceTask, "readonly.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC2 只读降级");
            writer.WriteBoolean("can_start", export.CanStart);
            writer.WriteNumber("start_calls", host.StartExportCalls.Count);
            writer.WriteString("status", export.StatusText);
            writer.WriteEndObject();
        });
    }

    // ---------------------------------------------------------------- history

    [AvaloniaFact]
    public async Task History_LoadsRealEntries_AndRendersStates()
    {
        var (view, host, vm, window) = await OpenAsync();
        host.ExportHistory = new List<ExportHistoryEntry>
        {
            new("exp-a", "zip", "completed", "/exports/a.zip", "aaaabbbbccccdddd", 12, "2026-10-29T10:00:00Z"),
            new("exp-b", "pdf", "failed", null, null, 5, "2026-10-28T09:00:00Z"),
        };
        await view.Tools.OpenAsync(StudioToolsTab.History);
        StudioFixtures.Pump();
        var export = vm.Export;
        Assert.Equal(2, export.History.Count);
        Assert.Equal("ZIP", export.History[0].Format);
        Assert.Equal(StudioStateKind.Done, export.History[0].State);
        Assert.Equal("●", export.History[0].StateGlyph);
        Assert.Equal("a.zip", export.History[0].FileName);
        Assert.Equal(StudioStateKind.Failed, export.History[1].State);
        Assert.Equal("✗", export.History[1].StateGlyph);
        Assert.Equal(2, view.Tools.ExportHistory.List.ItemsSource?.Cast<object>().Count());

        var shot = Capture(window, "export-history-terms");
        StudioEvidence.Write(EvidenceTask, "history.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC2 导出历史");
            writer.WriteString("screenshot", Path.GetFileName(shot));
            writer.WriteNumber("entries", export.History.Count);
            writer.WriteString("completed_glyph", export.History[0].StateGlyph);
            writer.WriteString("failed_glyph", export.History[1].StateGlyph);
            writer.WriteBoolean("file_name_only", !export.History[0].FileName.Contains("/exports"));
            writer.WriteEndObject();
        });
    }

    // ---------------------------------------------------------------- terms

    [AvaloniaFact]
    public async Task Terms_AreNotWired_NoFabricatedRows_AndExplainWhy()
    {
        var (view, _, vm, window) = await OpenAsync();
        var terms = vm.Terms;
        Assert.False(terms.IsWired);
        Assert.True(terms.IsNotWired);
        Assert.Contains("不伪造", terms.CapabilityNote);

        await view.Tools.OpenAsync(StudioToolsTab.Terms);
        StudioFixtures.Pump();
        Assert.Equal(0, terms.RowCount);
        Assert.False(terms.HasRows);
        Assert.False(view.Tools.Terms.SearchBox.IsEnabled);
        Assert.Contains("未接入", view.Tools.Terms.BannerBody.Text);
        Assert.Contains("NOT_WIRED", terms.BannerTitle);

        // Every section loads through the NOT_WIRED source: still empty, still honest.
        foreach (var section in new[] { StudioTermsSection.Terms, StudioTermsSection.DoNotTranslate, StudioTermsSection.Conflicts })
        {
            terms.Section = section;
            Assert.True(await terms.LoadAsync());
            Assert.Equal(0, terms.RowCount);
        }

        // Editing attempts are refused with the reason (no fake success).
        Assert.False(terms.TryEdit());
        Assert.False(terms.TryCreate());
        Assert.False(terms.TryResolveConflict());
        Assert.Contains("未接入", terms.StatusText);

        var inventory = terms.BuildCapabilityInventory();
        Assert.Contains(inventory, item => item.Contains("glossary"));
        Assert.Contains(inventory, item => item.Contains("不译表"));

        var shot = Capture(window, "terms-not-wired");
        StudioEvidence.Write(EvidenceTask, "terms.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC3 术语 NOT_WIRED");
            writer.WriteString("screenshot", Path.GetFileName(shot));
            writer.WriteBoolean("wired", terms.IsWired);
            writer.WriteNumber("rows", terms.RowCount);
            writer.WriteBoolean("search_disabled", !view.Tools.Terms.SearchBox.IsEnabled);
            writer.WriteBoolean("edit_refused", !terms.TryEdit());
            writer.WriteStartArray("capability_inventory");
            foreach (var item in inventory)
            {
                writer.WriteStringValue(item);
            }

            writer.WriteEndArray();
            writer.WriteEndObject();
        });
    }

    [AvaloniaFact]
    public async Task ToolsOverlay_OpensAndCloses_KeyboardEscape()
    {
        var (view, _, vm, _) = await OpenAsync();
        Assert.False(view.Tools.IsOpen);
        await view.Tools.OpenAsync(StudioToolsTab.Preflight);
        Assert.True(view.Tools.IsOpen);
        view.Tools.SetTab(StudioToolsTab.History);
        Assert.Equal(StudioToolsTab.History, view.Tools.ActiveTab);
        view.Tools.Close();
        Assert.False(view.Tools.IsOpen);
        Assert.Equal(3, view.Tools.Tabs.Count);
        Assert.True(vm.Export.PollInterval >= TimeSpan.FromMilliseconds(500));
        Assert.True(vm.Export.PollInterval <= TimeSpan.FromMilliseconds(1000));
    }
}
