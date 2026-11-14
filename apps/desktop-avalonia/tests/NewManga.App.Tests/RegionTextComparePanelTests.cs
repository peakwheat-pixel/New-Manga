using Avalonia;
using Avalonia.Automation;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.App.Controls;
using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.App.Views.Fluent;
using NewManga.CoreClient;
using NewManga.CoreClient.Commands;
using NewManga.DesignSystem.Controls;
using System.Text.Json;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-06-RESIDUAL-4B slice 3 (4A spec v1.1 S1/S2/S4/S5/S6; AC3/AC4/AC5): the workbench conflict
/// 「查看对照」panel. These are the user-visible acceptance tests; the wire (slice 1) and the port
/// contract (slice 2) are covered by their own suites.
///
/// The invariants pinned here are exactly the ones a reviewer is told to look for:
/// <list type="number">
/// <item>the entry exists ONLY in the conflict state and the banner action is untouched (S4);</item>
/// <item>one open = EXACTLY ONE projection call, two read-only layers, no input/overwrite action (AC3);</item>
/// <item>L2 is the LIVE <c>DraftText</c>, never the persisted draft patch (4A P2-4);</item>
/// <item>the three failure reasons keep a fixed priority and distinct texts, and an empty
/// <c>regions</c> list with a NULL page extent is NEVER rendered as "no conflict"/empty (AC4/P2-3);</item>
/// <item>an unavailable projection renders NO compare text at all -- the negative invariant that must
/// coexist with the new positive entry assertion (AC5).</item>
/// </list>
/// </summary>
public sealed class RegionTextComparePanelTests
{
    // ------------------------------------------------------------------ AC3：入口 / 双栏 / 恰好一次

    [AvaloniaFact]
    public async Task ConflictState_ShowsCompareEntry_AndKeepsTheBannerAction()
    {
        var (shell, _) = await CreateConflictAsync(configure: null);

        Assert.NotNull(FindButton(shell.WorkbenchView, "查看对照"));
        // 4A S4：Banner 的单 action 不得被挪用/改动 —— 既有「重读草稿」必须仍在。
        Assert.NotNull(FindButton(shell.WorkbenchView, "重读草稿"));

        var compareButton = FindButton(shell.WorkbenchView, "查看对照")!;
        Assert.Equal("查看对照", AutomationProperties.GetName(compareButton));
    }

    [AvaloniaFact]
    public async Task OpenCompare_RendersTwoReadOnlyLayers_AndCallsTheProjectionExactlyOnce()
    {
        var (shell, host) = await CreateConflictAsync(configure: fake =>
            fake.RegionTextsByPage["page-1"] = Projection("page-1", "region-1", "基底译文", "edited", revisionNo: 1));

        Click(FindButton(shell.WorkbenchView, "查看对照")!);
        Dispatcher.UIThread.RunJobs();

        // 恰好一次：一次打开只调用一次投影（不缓存、不 per-region N+1）。
        Assert.Single(host.RegionTextCalls);
        Assert.Equal("page-1", host.RegionTextCalls[0].PageId);
        // 4A R-8：端口调用不传 regionIds（整页一次，TARGET_NOT_FOUND 由本地成员判定）。
        Assert.Null(host.RegionTextCalls[0].RegionIds);

        var panel = Assert.Single(shell.WorkbenchView.GetVisualDescendants().OfType<RegionTextComparePanel>());
        Assert.Equal(RegionCompareStatus.Ready, panel.Status);
        Assert.Equal(RegionTextComparePanel.PanelTitle, AutomationProperties.GetName(panel));
        Assert.NotNull(panel.BaseLayer);
        Assert.NotNull(panel.WorkingLayer);
        Assert.Equal(RegionTextComparePanel.BaseTitle, panel.BaseLayer!.Title);
        Assert.Equal(RegionTextComparePanel.WorkingTitle, panel.WorkingLayer!.Title);
        Assert.Equal("基底译文", panel.BaseLayer.Text);
        Assert.Equal("edited", panel.BaseLayer.TextSource);
        Assert.Equal("draft text", panel.WorkingLayer.Text);
        Assert.Equal("本地草稿", panel.WorkingLayer.TextSource);

        // 只读：面板内没有任何输入控件，且可点击动作只有「关闭」（无一键覆盖/应用）。
        Assert.Empty(panel.GetVisualDescendants().OfType<TextBox>());
        Assert.Equal(RegionTextComparePanel.CloseText,
            Assert.Single(panel.GetVisualDescendants().OfType<Button>()).Content?.ToString());
        Assert.DoesNotContain(panel.GetVisualDescendants().OfType<Button>(),
            button => button.Content?.ToString()?.Contains("覆盖", StringComparison.Ordinal) == true
                || button.Content?.ToString()?.Contains("应用", StringComparison.Ordinal) == true);

        // 两栏都有标题（色盲安全：靠文字而不是颜色区分层）。
        var titles = panel.GetVisualDescendants().OfType<TextBlock>()
            .Select(block => block.Text ?? string.Empty).ToArray();
        Assert.Contains(RegionTextComparePanel.BaseTitle, titles);
        Assert.Contains(RegionTextComparePanel.WorkingTitle, titles);
    }

    [AvaloniaFact]
    public async Task WorkingLayer_FollowsTheLiveDraftText_NotThePersistedPatch()
    {
        var (shell, _) = await CreateConflictAsync(configure: fake =>
            fake.RegionTextsByPage["page-1"] = Projection("page-1", "region-1", "基底译文", "edited", revisionNo: 1));

        Click(FindButton(shell.WorkbenchView, "查看对照")!);
        Dispatcher.UIThread.RunJobs();
        var panel = Assert.Single(shell.WorkbenchView.GetVisualDescendants().OfType<RegionTextComparePanel>());
        Assert.Equal("draft text", panel.WorkingLayer!.Text);

        // 4A v1.1 P2-4：L2 = 实时 DraftText，打开后继续编辑必须反映到对照面板。
        shell.WorkbenchViewModel.DraftText = "刚输入的实时文本";
        Dispatcher.UIThread.RunJobs();

        var panelAfter = Assert.Single(shell.WorkbenchView.GetVisualDescendants().OfType<RegionTextComparePanel>());
        Assert.Contains(panelAfter.GetVisualDescendants().OfType<TextBlock>(),
            block => string.Equals(block.Text, "刚输入的实时文本", StringComparison.Ordinal));
        Assert.DoesNotContain(panelAfter.GetVisualDescendants().OfType<TextBlock>(),
            block => string.Equals(block.Text, "draft text", StringComparison.Ordinal));
    }

    [AvaloniaFact]
    public async Task RevisionDrift_RaisesTheTypedNotice_AndShowsBothRevisions()
    {
        var (shell, _) = await CreateConflictAsync(configure: fake =>
            // L1 已推进到 r4，本地 RegionSummary 仍是 r1 ⇒ 差异必须显式化（4A S2-c）。
            fake.RegionTextsByPage["page-1"] = Projection("page-1", "region-1", "基底译文", "edited", revisionNo: 4));

        Click(FindButton(shell.WorkbenchView, "查看对照")!);
        Dispatcher.UIThread.RunJobs();

        var panel = Assert.Single(shell.WorkbenchView.GetVisualDescendants().OfType<RegionTextComparePanel>());
        Assert.True(panel.HasRevisionDrift);
        Assert.Equal(4, panel.BaseLayer!.RevisionNo);
        Assert.Equal(1, panel.WorkingLayer!.RevisionNo);
        Assert.Contains("基底已推进", panel.Compare.DriftNotice);
        Assert.Contains("r4", panel.Compare.DriftNotice);
        Assert.Contains("r1", panel.Compare.DriftNotice);
    }

    [AvaloniaFact]
    public async Task Close_RestoresTheBannerOnly_AndReopenCallsOncePerOpen()
    {
        var (shell, host) = await CreateConflictAsync(configure: fake =>
            fake.RegionTextsByPage["page-1"] = Projection("page-1", "region-1", "基底译文", "edited", revisionNo: 1));

        Click(FindButton(shell.WorkbenchView, "查看对照")!);
        Dispatcher.UIThread.RunJobs();
        Assert.Single(host.RegionTextCalls);

        var panel = Assert.Single(shell.WorkbenchView.GetVisualDescendants().OfType<RegionTextComparePanel>());
        Click(panel.CloseButton);
        Dispatcher.UIThread.RunJobs();

        Assert.Empty(shell.WorkbenchView.GetVisualDescendants().OfType<RegionTextComparePanel>());
        Assert.NotNull(FindButton(shell.WorkbenchView, "查看对照"));
        Assert.NotNull(shell.WorkbenchView.GetVisualDescendants().OfType<AlertBanner>()
            .FirstOrDefault(banner => banner.Title == "并发冲突"));
        Assert.False(shell.WorkbenchViewModel.IsCompareVisible);
        Assert.Null(shell.WorkbenchViewModel.Compare);

        // 每次「打开」各自调用一次；关闭不触发任何投影调用。
        Click(FindButton(shell.WorkbenchView, "查看对照")!);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(2, host.RegionTextCalls.Count);
    }

    [AvaloniaFact]
    public async Task Escape_ClosesTheComparePanel()
    {
        var (shell, _) = await CreateConflictAsync(configure: fake =>
            fake.RegionTextsByPage["page-1"] = Projection("page-1", "region-1", "基底译文", "edited", revisionNo: 1));

        Click(FindButton(shell.WorkbenchView, "查看对照")!);
        Dispatcher.UIThread.RunJobs();
        Assert.Single(shell.WorkbenchView.GetVisualDescendants().OfType<RegionTextComparePanel>());

        Assert.True(shell.WorkbenchView.HandleKeyForTest(Key.Escape, KeyModifiers.None));
        Dispatcher.UIThread.RunJobs();

        Assert.Empty(shell.WorkbenchView.GetVisualDescendants().OfType<RegionTextComparePanel>());
        // 其它键不关闭。
        Assert.False(shell.WorkbenchView.HandleKeyForTest(Key.Enter, KeyModifiers.None));
    }

    [AvaloniaFact]
    public async Task CompareEntry_IsAbsentOutsideTheConflictState()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 0)];
        host.RegionsByPage["page-1"] = new RegionPageProjection(
        [
            new RegionSummary("region-1", "speech", "skip", "detect", 1,
                new RegionGeometrySummary(0.1, 0.1, 0.3, 0.2, [])),
        ], new RegionPageSize(100, 100));
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Workbench);
        await shell.WorkbenchView.LoadAsync("chapter-key");
        await shell.WorkbenchViewModel.SelectRegionAsync(shell.WorkbenchViewModel.Regions[0]);
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(FluentPageState.Ready, shell.WorkbenchViewModel.State);
        Assert.Null(FindButton(shell.WorkbenchView, "查看对照"));
        Assert.Empty(shell.WorkbenchView.GetVisualDescendants().OfType<RegionTextComparePanel>());
    }

    // ------------------------------------------------------------------ AC4：失败/空态固定优先级

    [AvaloniaFact]
    public async Task HostNotReady_IsReportedFirst_WithoutRequestingTheProjection()
    {
        var (shell, host) = await CreateConflictAsync(configure: fake =>
            fake.RegionTextsByPage["page-1"] = Projection("page-1", "region-1", "基底译文", "edited", revisionNo: 1));

        // ① 优先级最高：Host 一旦未就绪，连投影请求都不发。
        host.Snapshot = FakeHostController.FailureSnapshot();
        Assert.True(await shell.WorkbenchViewModel.OpenRegionCompareAsync());
        Dispatcher.UIThread.RunJobs();

        var panel = Assert.Single(shell.WorkbenchView.GetVisualDescendants().OfType<RegionTextComparePanel>());
        Assert.Equal(RegionCompareStatus.HostNotReady, panel.Status);
        Assert.Equal(RegionCompareReasonCodes.HostNotReady, panel.ReasonCode);
        Assert.Empty(host.RegionTextCalls);
    }

    [AvaloniaFact]
    public async Task ProjectionUnavailable_IsReportedSecond_AndRendersNoLayers()
    {
        // fake 没有注册投影 ⇒ 端口返回 null。
        var (shell, host) = await CreateConflictAsync(configure: null);

        Assert.True(await shell.WorkbenchViewModel.OpenRegionCompareAsync());
        Dispatcher.UIThread.RunJobs();

        var panel = Assert.Single(shell.WorkbenchView.GetVisualDescendants().OfType<RegionTextComparePanel>());
        Assert.Equal(RegionCompareStatus.ProjectionUnavailable, panel.Status);
        Assert.Equal(RegionCompareReasonCodes.ProjectionUnavailable, panel.ReasonCode);
        Assert.Single(host.RegionTextCalls);
        Assert.Null(panel.BaseLayer);
        Assert.Null(panel.WorkingLayer);
    }

    [AvaloniaFact]
    public async Task EmptyRegionsWithNullPageExtent_IsTargetNotFound_NeverAnEmptyOrSafeState()
    {
        var (shell, _) = await CreateConflictAsync(configure: fake =>
            // Core 对未知 page 也返回 regions: []，且 page_size 为 null（4A P2-3）。
            fake.RegionTextsByPage["page-1"] = new RegionPageTextProjection("page-1", null, null, []));

        Assert.True(await shell.WorkbenchViewModel.OpenRegionCompareAsync());
        Dispatcher.UIThread.RunJobs();

        var panel = Assert.Single(shell.WorkbenchView.GetVisualDescendants().OfType<RegionTextComparePanel>());
        Assert.Equal(RegionCompareStatus.TargetNotFound, panel.Status);
        Assert.Equal(RegionCompareReasonCodes.TargetNotFound, panel.ReasonCode);
        // 不得渲染成「该页没有区域」的空态，更不得渲染成「无冲突」。
        Assert.DoesNotContain(panel.GetVisualDescendants().OfType<TextBlock>(),
            block => string.Equals(block.Text, RegionTextComparePanel.EmptyText, StringComparison.Ordinal));
    }

    [AvaloniaFact]
    public async Task EmptyRegionsWithPageExtent_IsTheEmptyPageState_WithoutAReasonCode()
    {
        var (shell, _) = await CreateConflictAsync(configure: fake =>
            fake.RegionTextsByPage["page-1"] = new RegionPageTextProjection("page-1", 100, 100, []));

        Assert.True(await shell.WorkbenchViewModel.OpenRegionCompareAsync());
        Dispatcher.UIThread.RunJobs();

        var panel = Assert.Single(shell.WorkbenchView.GetVisualDescendants().OfType<RegionTextComparePanel>());
        Assert.Equal(RegionCompareStatus.EmptyPage, panel.Status);
        Assert.Equal(string.Empty, panel.ReasonCode);
        Assert.Contains(panel.GetVisualDescendants().OfType<TextBlock>(),
            block => string.Equals(block.Text, RegionTextComparePanel.EmptyText, StringComparison.Ordinal));
        Assert.Null(panel.BaseLayer);
        Assert.Null(panel.WorkingLayer);
    }

    [Fact]
    public void FailureReasonCodes_ArePairwiseDistinct_AndDoNotExtendTheFrozenDraftErrorMap()
    {
        var codes = new[]
        {
            RegionCompareReasonCodes.HostNotReady,
            RegionCompareReasonCodes.ProjectionUnavailable,
            RegionCompareReasonCodes.TargetNotFound,
        };
        Assert.Equal(codes.Length, codes.Distinct(StringComparer.Ordinal).Count());

        // 4A P2-5：19 键闭集不得被扩。`REGION_TEXT_PROJECTION_UNAVAILABLE` / `HOST_NOT_READY` 是面板
        // 本地原因码，绝不可加进映射；`TARGET_NOT_FOUND` 只借用同名（它本来就是 Core/FEA-05 的既有
        // 码，属于那 19 个之一，不是本卡新增）。
        Assert.Equal(19, DraftErrorMap.Codes.Count);
        Assert.DoesNotContain(RegionCompareReasonCodes.ProjectionUnavailable, DraftErrorMap.Codes);
        Assert.DoesNotContain(RegionCompareReasonCodes.HostNotReady, DraftErrorMap.Codes);
        Assert.Contains(RegionCompareReasonCodes.TargetNotFound, DraftErrorMap.Codes);
    }

    // ------------------------------------------------------------------ AC5：负向不变量（零伪造对照内容）

    [AvaloniaFact]
    public async Task FailurePanel_NeverRendersAnyCompareText()
    {
        // 投影里有别的 region 的文本，但目标 region 不在结果中 ⇒ 面板不得泄漏/复用别人的文本。
        var (shell, _) = await CreateConflictAsync(configure: fake =>
            fake.RegionTextsByPage["page-1"] =
                Projection("page-1", "region-other", "别人家的译文", "edited", revisionNo: 1));

        Assert.True(await shell.WorkbenchViewModel.OpenRegionCompareAsync());
        Dispatcher.UIThread.RunJobs();

        var panel = Assert.Single(shell.WorkbenchView.GetVisualDescendants().OfType<RegionTextComparePanel>());
        Assert.Equal(RegionCompareStatus.TargetNotFound, panel.Status);
        Assert.Null(panel.BaseLayer);
        Assert.Null(panel.WorkingLayer);
        // 零文本行：既没有 L1（任何 region 的），也没有回落到本地草稿。
        Assert.DoesNotContain(panel.GetVisualDescendants().OfType<TextBlock>(),
            block => string.Equals(block.Text, "别人家的译文", StringComparison.Ordinal)
                || string.Equals(block.Text, "draft text", StringComparison.Ordinal));
        // 只剩原因 + 关闭：面板内唯一可点击动作仍是「关闭」。
        Assert.Equal(RegionTextComparePanel.CloseText,
            Assert.Single(panel.GetVisualDescendants().OfType<Button>()).Content?.ToString());
    }

    // ------------------------------------------------------------------ helpers

    private static FluentShell CreateShell(FakeHostController host)
    {
        var shell = FluentShell.CreateRoot(host: host);
        shell.Show();
        Dispatcher.UIThread.RunJobs();
        return shell;
    }

    private static async Task<(FluentShell Shell, FakeHostController Host)> CreateConflictAsync(
        Action<FakeHostController>? configure)
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 0)];
        host.RegionsByPage["page-1"] = new RegionPageProjection(
        [
            new RegionSummary("region-1", "speech", "skip", "detect", 1,
                new RegionGeometrySummary(0.1, 0.1, 0.3, 0.2, [])),
        ], new RegionPageSize(100, 100));
        // 不可编辑 lease ⇒ 冲突态（与 I13 同一构造路径）。工作副本来自会话草稿（L2 非空）。
        var draft = CreateDraft("draft-1", "page-1", "region-1", "draft text");
        host.ScriptedDrafts = new[] { draft };
        host.DraftLeasesByPageRegion["page-1|region-1"] =
            new DraftLease(draft, CanEdit: false, Token: null);
        configure?.Invoke(host);

        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Workbench);
        await shell.WorkbenchView.LoadAsync("chapter-key");
        await shell.WorkbenchViewModel.SelectRegionAsync(shell.WorkbenchViewModel.Regions[0]);
        Dispatcher.UIThread.RunJobs();
        Assert.False(await shell.WorkbenchViewModel.OpenDraftAsync(1));
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(FluentPageState.Conflict, shell.WorkbenchViewModel.State);
        return (shell, host);
    }

    private static RegionPageTextProjection Projection(
        string pageId,
        string regionId,
        string finalTranslation,
        string finalSource,
        int revisionNo) => new(
        pageId,
        1000,
        1500,
        new[]
        {
            new RegionTextDetail(
                regionId,
                pageId,
                "speech",
                "skip",
                1,
                null,
                new RegionFourTrackText("原文", "机翻", "人工编辑", finalTranslation, finalSource, true, true, false),
                new RegionLockProjection(false, false, false),
                "confirmed",
                "user",
                revisionNo,
                "rev-1",
                false,
                Array.Empty<int>(),
                "2026-01-01T00:00:00.000+00:00",
                "2026-01-01T00:00:01.000+00:00"),
        });

    private static Draft CreateDraft(string draftId, string pageId, string regionId, string text) => new(
        draftId, "session-1", pageId, regionId, "rev-1", PageBindingVersion: 1, DraftSequence: 1,
        Patch: JsonSerializer.SerializeToElement(new { text }), UndoCursor: null,
        SavedAt: "2026-11-02T00:00:00Z", Status: "open");

    private static Button? FindButton(Control root, string content) =>
        root.GetVisualDescendants().OfType<Button>()
            .FirstOrDefault(button => string.Equals(button.Content?.ToString(), content, StringComparison.Ordinal));

    private static void Click(Button button) => button.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));

    // ------------------------------------------------------------------ 视觉证据（opt-in，不作 AC 判据）

    /// <summary>
    /// opt-in 视觉证据：把冲突态横幅与展开后的双栏面板渲染成 PNG，写入
    /// <c>verification/FEA-06-RESIDUAL-4B/visuals/</c>。
    /// <para>口径沿用 <c>FluentResidual3VisualEvidenceTests</c>：**像素不作 AC 判据**，只作为人眼签署证据；
    /// 未设 <c>NEWMANGA_CAPTURE_FEA06_COMPARE_PNGS=1</c> 时不写任何文件（默认零写入）。</para>
    /// </summary>
    [AvaloniaFact]
    public async Task Captures_Compare_Panel_Pngs_Only_When_Opted_In()
    {
        const string captureEnvVar = "NEWMANGA_CAPTURE_FEA06_COMPARE_PNGS";

        var (shell, _) = await CreateConflictAsync(configure: fake =>
            fake.RegionTextsByPage["page-1"] =
                Projection("page-1", "region-1", "基底译文", "edited", revisionNo: 1));

        var conflictFrame = shell.CaptureRenderedFrame();
        Assert.NotNull(conflictFrame);

        Click(FindButton(shell.WorkbenchView, "查看对照")!);
        Dispatcher.UIThread.RunJobs();

        var panelFrame = shell.CaptureRenderedFrame();
        Assert.NotNull(panelFrame);

        if (Environment.GetEnvironmentVariable(captureEnvVar) != "1")
        {
            return;
        }

        var root = FindRepositoryRoot()
            ?? throw new DirectoryNotFoundException("repository root not found from test output dir");
        var visuals = Path.Combine(root, "verification", "FEA-06-RESIDUAL-4B", "visuals");
        Directory.CreateDirectory(visuals);
        conflictFrame!.Save(Path.Combine(visuals, "01-conflict-banner.png"));
        panelFrame!.Save(Path.Combine(visuals, "02-compare-panel.png"));
    }

    private static string? FindRepositoryRoot()
    {
        var assemblyDirectory = Path.GetDirectoryName(typeof(RegionTextComparePanelTests).Assembly.Location);
        var cursor = new DirectoryInfo(string.IsNullOrEmpty(assemblyDirectory) ? AppContext.BaseDirectory : assemblyDirectory!);
        while (cursor is not null)
        {
            if (Directory.Exists(Path.Combine(cursor.FullName, "doc", "tasks")))
            {
                return cursor.FullName;
            }

            cursor = cursor.Parent;
        }

        return null;
    }
}
