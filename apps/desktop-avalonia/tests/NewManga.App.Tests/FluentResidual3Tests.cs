using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Avalonia;
using Avalonia.Automation;
using Avalonia.Automation.Peers;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.App.Views.Fluent;
using NewManga.Appearance;
using NewManga.CoreClient;
using NewManga.CoreClient.Commands;
using NewManga.DesignSystem.Controls;
using NewManga.DesignSystem.Theming;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-06-RESIDUAL-3（0 pin，UI-only）定向证据：AC-1（Run 投影两控制面）/ AC-2（9 行）/ AC-3（Reader
/// 双页 + webtoon 滚动）/ AC-4（书架聚合统计 + 零新增命令）/ AC-5（Tab 遍历 + a11y 属性/UIA 树 + Studio）。
///
/// 断言只读 Host 投影/真实框架行为；无投影时一律断言「—」/空态（无假数据不变量）。
/// </summary>
public sealed class FluentResidual3Tests : IDisposable
{
    private static readonly byte[] TinyPng = Convert.FromBase64String(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==");

    private readonly string _root = Path.Combine(Path.GetTempPath(), $"nm-fea06-residual-3-{Guid.NewGuid():N}");

    public FluentResidual3Tests() => Directory.CreateDirectory(_root);

    public void Dispose()
    {
        try
        {
            Directory.Delete(_root, recursive: true);
        }
        catch (IOException)
        {
            // best-effort temp cleanup
        }
    }

    // ---------------------------------------------------------------------------------------
    // Shared helpers
    // ---------------------------------------------------------------------------------------

    private static FluentShell CreateShell(FakeHostController? host = null, AppearanceCoordinator? appearance = null)
    {
        var shell = FluentShell.CreateRoot(host: host, appearance: appearance);
        shell.Width = 1280;
        shell.Height = 900;
        shell.Show();
        RunJobs();
        return shell;
    }

    private static void RunJobs()
    {
        Dispatcher.UIThread.RunJobs(DispatcherPriority.Render);
        Dispatcher.UIThread.RunJobs(DispatcherPriority.Loaded);
        Dispatcher.UIThread.RunJobs();
    }

    private static TaskProjectionInfo Projection(
        IReadOnlyList<RunRowInfo>? rows = null,
        RunCountsInfo? counts = null,
        RunControlsInfo? controls = null,
        string runId = "run-42",
        string runStatus = "running",
        double? progress = 0.62,
        string? currentPageId = "page-2",
        string? currentStepType = "translate")
    {
        return new TaskProjectionInfo(
            runId,
            runStatus,
            "批量翻译",
            progress,
            currentPageId,
            currentStepType,
            Array.Empty<RunStepFlowInfo>(),
            rows ?? Array.Empty<RunRowInfo>(),
            Array.Empty<RunTaskInfo>(),
            counts ?? new RunCountsInfo(10, 3, 2, 1, 4, 0, 0),
            Array.Empty<string>(),
            controls ?? new RunControlsInfo(true, true, false, false, false, true));
    }

    /// <summary>七状态行（术语落表顺序）+ 填充行，让矩阵可滚动以验证吸顶。PageOrder 用真实 1-based。</summary>
    private static IReadOnlyList<RunRowInfo> SevenStateRows()
    {
        var rows = new List<RunRowInfo>();
        var statuses = new[] { "queued", "running", "done", "failed", "blocked", "stale", "skipped" };
        for (var index = 0; index < statuses.Length; index++)
        {
            rows.Add(new RunRowInfo($"page-{index + 1}", index + 1, $"p{index + 1}.png", statuses[index],
                false, false, statuses[index] == "failed" ? "PROVIDER_NOT_CONFIGURED" : null));
        }

        for (var index = 0; index < 24; index++)
        {
            rows.Add(new RunRowInfo($"filler-{index}", 8 + index, $"f{index}.png", "queued", false, false, null));
        }

        return rows;
    }

    private static async Task<(FluentShell Shell, FakeHostController Host)> WorkbenchWithRunAsync(
        TaskProjectionInfo projection, params TaskProjectionInfo[] extraProjections)
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("Sample"));
        host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 0)];
        host.RegionsByPage["page-1"] = new RegionPageProjection([], null);
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Workbench);
        await shell.WorkbenchView.LoadAsync("chapter-key");
        RunJobs();
        shell.WorkbenchView.SelectTab(WorkbenchViewTab.Batch);
        RunJobs();

        shell.WorkbenchView.BatchStartButton.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        RunJobs();

        host.ScriptedTaskProjections.Enqueue(projection);
        foreach (var extra in extraProjections)
        {
            host.ScriptedTaskProjections.Enqueue(extra);
        }

        await shell.WorkbenchViewModel.TickRunPollForTestAsync();
        shell.WorkbenchViewModel.StopRunPolling();
        RunJobs();
        return (shell, host);
    }

    private static string RepoRoot()
    {
        var cursor = new DirectoryInfo(AppContext.BaseDirectory);
        while (cursor is not null && !File.Exists(Path.Combine(cursor.FullName, "doc", "tasks", "FEA-06-RESIDUAL-3.md")))
        {
            cursor = cursor.Parent;
        }

        return cursor?.FullName ?? throw new DirectoryNotFoundException("could not locate the New Manga repository root");
    }

    // ---------------------------------------------------------------------------------------
    // AC-1（格 1）：批量空态 → 恰好 1 次 StartRunAsync（translate_all + chapter scope + 意图键）
    // ---------------------------------------------------------------------------------------

    [AvaloniaFact]
    public async Task AC1_BatchEmptyStart_SubmitsExactlyOneRun_WithChapterScope_AndReusableIntentKey()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("Sample"));
        host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 0)];
        host.RegionsByPage["page-1"] = new RegionPageProjection([], null);
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Workbench);
        await shell.WorkbenchView.LoadAsync("chapter-key");
        RunJobs();
        shell.WorkbenchView.SelectTab(WorkbenchViewTab.Batch);
        RunJobs();

        var start = shell.WorkbenchView.BatchStartButton;
        Assert.True(start.IsEnabled);
        start.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        RunJobs();

        var request = Assert.Single(host.StartRunRequests);
        Assert.Equal("translate_all", request.Command);
        Assert.Equal("chapter", request.Scope["kind"]?.ToString());
        Assert.Equal("chapter-key", request.Scope["chapter_id"]?.ToString());
        Assert.False(string.IsNullOrWhiteSpace(request.IdempotencyKey));

        var viewModel = shell.WorkbenchViewModel;
        Assert.Equal(TimeSpan.FromSeconds(1), viewModel.RunPollIntervalValue);
        Assert.True(viewModel.IsRunPolling);
        Assert.False(start.IsEnabled); // 提交后不再允许重复 StartRun

        // 重试复用同一意图键：同一章节意图内第二次提交仍是同一个 key（Core 以同 key 复用 run）。
        host.ScriptedStartRuns.Enqueue(null);
        await viewModel.StartRunAsync();
        Assert.Equal(2, host.StartRunRequests.Count);
        Assert.Equal(host.StartRunRequests[0].IdempotencyKey, host.StartRunRequests[1].IdempotencyKey);
        viewModel.StopRunPolling();
        shell.Close();
    }

    // ---------------------------------------------------------------------------------------
    // AC-1（格 1）：1s 轮询 ≥2 次 + 七状态矩阵文案（非仅颜色）+ 吸顶表头 + RunProjectionBar 绑定
    // ---------------------------------------------------------------------------------------

    [AvaloniaFact]
    public async Task AC1_RunProjection_PollsTwice_ShowsSevenStateLabels_AndStickyHeader()
    {
        var projection = Projection(SevenStateRows());
        var (shell, host) = await WorkbenchWithRunAsync(projection, projection);
        var viewModel = shell.WorkbenchViewModel;

        // 第二次 tick 走同一生产 tick 路径（不是测试专用第二实现）。
        shell.WorkbenchViewModel.StartRunPolling();
        await viewModel.TickRunPollForTestAsync();
        viewModel.StopRunPolling();
        RunJobs();

        Assert.True(host.TaskProjectionRequests.Count >= 2, $"expected >=2 projection polls, got {host.TaskProjectionRequests.Count}");
        Assert.True(viewModel.RunPollAttempts >= 2);

        // 七状态逐格文案（术语落表：Queued/Running/Done/Failed/Blocked/Stale/Skipped → StatusCatalog 文案）。
        var expectedKinds = new[]
        {
            StatusKind.Queued, StatusKind.Running, StatusKind.Done, StatusKind.Failed,
            StatusKind.Blocked, StatusKind.Stale, StatusKind.Skipped,
        };
        var expectedLabels = expectedKinds.Select(StatusCatalog.Label).ToArray();
        var rowsHost = shell.WorkbenchView.BatchMatrixRowsHost;
        Assert.Equal(31, rowsHost.Children.Count);
        for (var index = 0; index < expectedKinds.Length; index++)
        {
            var row = Assert.IsType<Grid>(rowsHost.Children[index]);
            var texts = row.GetVisualDescendants().OfType<TextBlock>().Select(block => block.Text).ToArray();
            Assert.Contains(expectedLabels[index], texts);
            Assert.Contains(row.GetVisualDescendants().OfType<StatusGlyph>(),
                glyph => glyph.Status == expectedKinds[index]);
            // 术语逐字：投影行携带七状态名（不是仅颜色通道）。
            Assert.Equal(Enum.GetName(expectedKinds[index]), viewModel.RunProjection!.Rows[index].StatusKey);
        }

        // RunProjectionBar 绑定真实投影（两控制面共用同一文案）。
        var barText = Assert.IsType<TextBlock>(shell.WorkbenchView.RunBar.Child).Text;
        Assert.Contains("run-42", barText, StringComparison.Ordinal);
        Assert.Contains("进行中", barText, StringComparison.Ordinal);
        Assert.Contains("62%", barText, StringComparison.Ordinal);

        // 吸顶表头：内容滚动后表头的屏幕 Y 不变（表头在 ScrollViewer 之外）。
        var scroll = shell.WorkbenchView.BatchMatrixScroll;
        var header = shell.WorkbenchView.BatchMatrixHeader;
        shell.UpdateLayout();
        RunJobs();
        var topLevel = Assert.IsAssignableFrom<TopLevel>(TopLevel.GetTopLevel(header));
        var before = header.TranslatePoint(new Point(0, 0), topLevel)!.Value.Y;
        scroll.Offset = new Vector(0, 120);
        RunJobs();
        // 可滚动的证明：Offset 真的落到 >0（headless 下 Extent/Viewport 的发布时机不稳定，用真实滚动代替）。
        Assert.True(scroll.Offset.Y > 0,
            $"the matrix content did not scroll (offset={scroll.Offset}, extent={scroll.Extent}, viewport={scroll.Viewport}, " +
            $"matrixBounds={scroll.Bounds}, tableBounds={shell.WorkbenchView.BatchTableHost.Bounds})");
        var after = header.TranslatePoint(new Point(0, 0), topLevel)!.Value.Y;
        Assert.Equal(before, after, 3);

        shell.Close();
    }

    // ---------------------------------------------------------------------------------------
    // AC-1（格 1）：detach / 切前端停表；停止后不再发任何投影请求（泄漏回归）
    // ---------------------------------------------------------------------------------------

    [AvaloniaFact]
    public async Task AC1_DetachedWorkbench_StopsPolling_AndSendsNoFurtherRequests()
    {
        var projection = Projection(SevenStateRows());
        var host = new FakeHostController(FakeHostController.ReadySnapshot("Sample"));
        host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 0)];
        host.RegionsByPage["page-1"] = new RegionPageProjection([], null);
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Workbench);
        await shell.WorkbenchView.LoadAsync("chapter-key");
        RunJobs();
        await shell.WorkbenchViewModel.StartRunAsync();
        Assert.True(shell.WorkbenchViewModel.IsRunPolling);
        host.ScriptedTaskProjections.Enqueue(projection);
        await shell.WorkbenchViewModel.TickRunPollForTestAsync();
        var requestsWhileAttached = host.TaskProjectionRequests.Count;

        // 切到书架：工作台视图 detach → 计时器停止。
        shell.Navigate(FluentPage.Library);
        RunJobs();
        Assert.False(shell.WorkbenchViewModel.IsRunPolling);

        // 停止后即便 tick 处理路径被再次驱动，也不得发出请求。
        await shell.WorkbenchViewModel.TickRunPollForTestAsync();
        Assert.Equal(requestsWhileAttached, host.TaskProjectionRequests.Count);

        // 回到工作台：同一 Run 仍在跟踪，轮询恢复（再次 detach 会再次停止）。
        shell.Navigate(FluentPage.Workbench);
        RunJobs();
        Assert.True(shell.WorkbenchViewModel.IsRunPolling);
        shell.WorkbenchViewModel.StopRunPolling();
        shell.Close();
    }

    // ---------------------------------------------------------------------------------------
    // R3-001（r1 P1）：Core page_order 是 1-based —— 矩阵与页面条都不得再 +1
    // ---------------------------------------------------------------------------------------

    [AvaloniaFact]
    public async Task R3001_OneBasedPageOrder_IsRenderedVerbatim_InMatrixAndPageStrip()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("Sample"));
        // Core list_chapter_pages 的 pages.sort_order 从 1 开始（tests/library/test_import_images.py:42 `(1,1)`）。
        host.ChapterPagesByChapter["chapter-key"] =
        [
            new ChapterPageSummary("page-1", "one.png", 1),
            new ChapterPageSummary("page-2", "two.png", 2),
        ];
        host.RegionsByPage["page-1"] = new RegionPageProjection([], null);
        host.RegionsByPage["page-2"] = new RegionPageProjection([], null);
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Workbench);
        await shell.WorkbenchView.LoadAsync("chapter-key");
        RunJobs();

        // 页面条：1-based sort_order 直接渲染为 第 1 页 / 第 2 页（旧实现 +1 → 第 2 页 / 第 3 页）。
        var stripLabels = shell.WorkbenchView.GetVisualDescendants().OfType<Button>()
            .Select(button => button.Content?.ToString() ?? string.Empty).ToArray();
        Assert.Contains("第 1 页", stripLabels);
        Assert.Contains("第 2 页", stripLabels);
        Assert.DoesNotContain("第 3 页", stripLabels);

        // 矩阵：注入 PageOrder=1 / 5 → 可见文本必须是「第 1 页」「第 5 页」（旧实现 +1 → 第 2 页 / 第 6 页）。
        shell.WorkbenchView.SelectTab(WorkbenchViewTab.Batch);
        RunJobs();
        shell.WorkbenchView.BatchStartButton.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        RunJobs();
        var rows = new[]
        {
            new RunRowInfo("page-1", 1, "one.png", "done", false, false, null),
            new RunRowInfo("page-5", 5, "five.png", "done", false, false, null),
        };
        host.ScriptedTaskProjections.Enqueue(Projection(rows));
        await shell.WorkbenchViewModel.TickRunPollForTestAsync();
        shell.WorkbenchViewModel.StopRunPolling();
        RunJobs();

        var rowsHost = shell.WorkbenchView.BatchMatrixRowsHost;
        Assert.Equal(2, rowsHost.Children.Count);
        var firstTexts = rowsHost.Children[0].GetVisualDescendants().OfType<TextBlock>()
            .Select(block => block.Text ?? string.Empty).ToArray();
        var secondTexts = rowsHost.Children[1].GetVisualDescendants().OfType<TextBlock>()
            .Select(block => block.Text ?? string.Empty).ToArray();
        Assert.Contains("第 1 页", firstTexts);
        Assert.DoesNotContain("第 2 页", firstTexts);
        Assert.Contains("第 5 页", secondTexts);
        Assert.DoesNotContain("第 6 页", secondTexts);
        Assert.Equal(new[] { 1, 5 },
            shell.WorkbenchViewModel.RunProjection!.Rows.Select(row => row.Order).ToArray());

        shell.Close();
    }

    // ---------------------------------------------------------------------------------------
    // R3-007（r1 P2）：Run 结束后必须释放跟踪 —— 切章节 / 终态后「开始处理」可再次使用
    // ---------------------------------------------------------------------------------------

    [AvaloniaFact]
    public async Task R3007_AfterSuccessfulRun_ChapterSwitch_AllowsANewRun()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("Sample"));
        host.ChapterPagesByChapter["chapter-a"] = [new ChapterPageSummary("page-a", "a.png", 1)];
        host.ChapterPagesByChapter["chapter-b"] = [new ChapterPageSummary("page-b", "b.png", 1)];
        host.RegionsByPage["page-a"] = new RegionPageProjection([], null);
        host.RegionsByPage["page-b"] = new RegionPageProjection([], null);
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Workbench);
        await shell.WorkbenchView.LoadAsync("chapter-a");
        RunJobs();
        shell.WorkbenchView.SelectTab(WorkbenchViewTab.Batch);
        RunJobs();

        var viewModel = shell.WorkbenchViewModel;
        var start = shell.WorkbenchView.BatchStartButton;
        Assert.True(start.IsEnabled);
        start.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        RunJobs();
        Assert.Single(host.StartRunRequests);
        Assert.False(string.IsNullOrEmpty(viewModel.RunId));
        Assert.False(start.IsEnabled);

        // 切章节 → 释放旧 Run 跟踪（R3-007）：RunId 清空、轮询停止、「开始处理」重新可用。
        await shell.WorkbenchView.LoadAsync("chapter-b");
        RunJobs();
        Assert.Null(viewModel.RunId);
        Assert.False(viewModel.IsRunPolling);
        Assert.True(start.IsEnabled);

        // 新章节可再次提交；意图键必须是新的（不能沿用旧 Run 的幂等键）。
        start.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        RunJobs();
        Assert.Equal(2, host.StartRunRequests.Count);
        Assert.NotEqual(host.StartRunRequests[0].IdempotencyKey, host.StartRunRequests[1].IdempotencyKey);
        Assert.Equal("chapter-b", host.StartRunRequests[1].Scope["chapter_id"]?.ToString());
        Assert.True(viewModel.IsRunPolling);
        viewModel.StopRunPolling();

        shell.Close();
    }

    [AvaloniaFact]
    public async Task R3007_TerminalProjection_ReleasesRunTracking_AndAllowsANewRun()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("Sample"));
        host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 1)];
        host.RegionsByPage["page-1"] = new RegionPageProjection([], null);
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Workbench);
        await shell.WorkbenchView.LoadAsync("chapter-key");
        RunJobs();
        shell.WorkbenchView.SelectTab(WorkbenchViewTab.Batch);
        RunJobs();

        var viewModel = shell.WorkbenchViewModel;
        var start = shell.WorkbenchView.BatchStartButton;
        start.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        RunJobs();
        Assert.Single(host.StartRunRequests);
        Assert.False(start.IsEnabled);

        // 终态（无任何可用控制动作）→ 释放跟踪 + 停表，同一章节也可再次开始（投影保留为最终诚实快照）。
        host.ScriptedTaskProjections.Enqueue(Projection(
            runStatus: "completed",
            controls: new RunControlsInfo(false, false, false, false, false, false)));
        await viewModel.TickRunPollForTestAsync();
        RunJobs();
        Assert.Null(viewModel.RunId);
        Assert.False(viewModel.IsRunPolling);
        Assert.True(start.IsEnabled);
        Assert.Equal("completed", viewModel.RunProjection!.RunStatus);
        Assert.Equal("completed", viewModel.RunProjection!.Lines.First(line => line.Label == "RunStatus").Value);

        // 再次提交 → 新 RunId + 新意图键（终态后轮换）。
        start.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        RunJobs();
        Assert.Equal(2, host.StartRunRequests.Count);
        Assert.NotEqual(host.StartRunRequests[0].IdempotencyKey, host.StartRunRequests[1].IdempotencyKey);
        viewModel.StopRunPolling();

        shell.Close();
    }

    // ---------------------------------------------------------------------------------------
    // r2-P1：终态集合对齐 Core —— completed_with_failures 可重试、interrupted 可继续，均必须真发帧
    // ---------------------------------------------------------------------------------------

    [AvaloniaFact]
    public async Task R3008_CompletedWithFailures_RetryFailedSendsOneFrame()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("Sample"));
        host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 1)];
        host.RegionsByPage["page-1"] = new RegionPageProjection([], null);
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Workbench);
        await shell.WorkbenchView.LoadAsync("chapter-key");
        RunJobs();
        shell.WorkbenchView.SelectTab(WorkbenchViewTab.Batch);
        RunJobs();

        var viewModel = shell.WorkbenchViewModel;
        var view = shell.WorkbenchView;
        view.BatchStartButton.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        RunJobs();

        // Core 契约：completed_with_failures && has_failures ⇒ can_retry_failed（projection.py:437-438）。
        host.ScriptedTaskProjections.Enqueue(Projection(
            runStatus: "completed_with_failures",
            counts: new RunCountsInfo(3, 1, 2, 0, 0, 0, 0),
            controls: new RunControlsInfo(false, false, false, false, false, true)));
        await viewModel.TickRunPollForTestAsync();
        RunJobs();

        // 终态后停表，但仍有可用动作 → 必须保留 RunId，否则「重试失败」enabled-but-inert。
        Assert.False(viewModel.IsRunPolling);
        Assert.False(string.IsNullOrEmpty(viewModel.RunId));
        Assert.True(view.RetryRunButton.IsEnabled);
        Assert.Contains("仍可重试", viewModel.Status, StringComparison.Ordinal);

        // 点「重试失败」→ 必须真发 1 帧 C061（而不是因 RunId 被清空直接 return）。
        var trackedRunId = viewModel.RunId;
        host.ScriptedControlRuns.Enqueue(new RunControlInfo("run-42", "running"));
        view.RetryRunButton.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        RunJobs();
        var retried = Assert.Single(host.RetriedFailedRuns);
        Assert.Equal(trackedRunId, retried.RunId);
        Assert.False(string.IsNullOrWhiteSpace(retried.IdempotencyKey));
        Assert.Empty(host.ControlRunRequests); // 重试走 C061，不是 C057

        viewModel.StopRunPolling();
        shell.Close();
    }

    [AvaloniaFact]
    public async Task R3008_Interrupted_ContinueSendsOneFrame()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("Sample"));
        host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 1)];
        host.RegionsByPage["page-1"] = new RegionPageProjection([], null);
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Workbench);
        await shell.WorkbenchView.LoadAsync("chapter-key");
        RunJobs();
        shell.WorkbenchView.SelectTab(WorkbenchViewTab.Batch);
        RunJobs();

        var viewModel = shell.WorkbenchViewModel;
        var view = shell.WorkbenchView;
        view.BatchStartButton.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        RunJobs();

        // Core 契约：interrupted 是**可恢复**态（projection.py:432-435），不是终态。
        host.ScriptedTaskProjections.Enqueue(Projection(
            runStatus: "interrupted",
            counts: new RunCountsInfo(2, 1, 0, 0, 1, 0, 0),
            controls: new RunControlsInfo(false, false, true, true, true, false)));
        await viewModel.TickRunPollForTestAsync();
        RunJobs();

        Assert.True(viewModel.IsRunPolling);          // 非终态：轮询继续
        Assert.False(string.IsNullOrEmpty(viewModel.RunId));
        Assert.True(view.ContinueRunButton.IsEnabled);

        // 点「继续」→ 必须真发 1 帧 C057（continue = 冻结枚举 Resume）。
        var trackedRunId = viewModel.RunId;
        host.ScriptedControlRuns.Enqueue(new RunControlInfo("run-42", "running"));
        view.ContinueRunButton.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        RunJobs();
        var control = Assert.Single(host.ControlRunRequests);
        Assert.Equal(trackedRunId, control.RunId);
        Assert.Equal(RunControlAction.Resume, control.Action);

        viewModel.StopRunPolling();
        shell.Close();
    }

    // ---------------------------------------------------------------------------------------
    // P3-1（r2）：书架预览缩略图页码同样 1-based（ShelfPageView 预览页标签此前无判别）
    // ---------------------------------------------------------------------------------------

    [AvaloniaFact]
    public async Task P3001_ShelfPreviewThumbnails_RenderOneBasedPageOrder()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("Sample"));
        host.ChaptersByBook["book-0"] = [new ChapterSummary("chapter-key", "第 1 章", "1", 0)];
        host.ChapterPagesByChapter["chapter-key"] =
        [
            new ChapterPageSummary("page-1", "one.png", 1),
            new ChapterPageSummary("page-2", "two.png", 2),
        ];
        var shell = CreateShell(host);
        await shell.ShelfViewModel.SelectBookAsync(shell.ShelfViewModel.Books[0]);
        RunJobs();

        var thumbLabels = shell.ShelfView.GetVisualDescendants().OfType<StreamingThumb>()
            .Select(thumb => (thumb.Child as TextBlock)?.Text ?? string.Empty).ToArray();
        Assert.Equal(new[] { "第 1 页", "第 2 页" }, thumbLabels);
        Assert.DoesNotContain("第 3 页", thumbLabels);

        shell.Close();
    }

    // ---------------------------------------------------------------------------------------
    // P3-5（r2）：同章节刷新不得清 RunId / 停轮询（只有章节切换才释放跟踪）
    // ---------------------------------------------------------------------------------------

    [AvaloniaFact]
    public async Task P3009_SameChapterRefresh_KeepsRunTrackingAndPolling()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("Sample"));
        host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 1)];
        host.RegionsByPage["page-1"] = new RegionPageProjection([], null);
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Workbench);
        await shell.WorkbenchView.LoadAsync("chapter-key");
        RunJobs();
        shell.WorkbenchView.SelectTab(WorkbenchViewTab.Batch);
        RunJobs();

        var viewModel = shell.WorkbenchViewModel;
        shell.WorkbenchView.BatchStartButton.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        RunJobs();
        var trackedRunId = viewModel.RunId;
        Assert.False(string.IsNullOrEmpty(trackedRunId));
        Assert.True(viewModel.IsRunPolling);
        var pollsBeforeRefresh = host.TaskProjectionRequests.Count;

        // 同章节刷新（刷新按钮/重新加载同一章）→ 不得清 RunId、不得停轮询。
        await shell.WorkbenchView.LoadAsync("chapter-key");
        RunJobs();
        Assert.Equal(trackedRunId, viewModel.RunId);
        Assert.True(viewModel.IsRunPolling);
        Assert.False(shell.WorkbenchView.BatchStartButton.IsEnabled);

        // 轮询仍生效：驱动一次生产 tick 必须真的再发一次投影请求。
        await viewModel.TickRunPollForTestAsync();
        Assert.True(host.TaskProjectionRequests.Count > pollsBeforeRefresh,
            $"polling stopped after same-chapter refresh ({pollsBeforeRefresh} -> {host.TaskProjectionRequests.Count})");

        viewModel.StopRunPolling();
        shell.Close();
    }

    // ---------------------------------------------------------------------------------------
    // AC-2（格 5）：9 行逐字段等于注入投影
    // ---------------------------------------------------------------------------------------

    [AvaloniaFact]
    public async Task AC2_ConsoleNineRows_EqualInjectedProjection()
    {
        var counts = new RunCountsInfo(10, 3, 2, 1, 4, 0, 0);
        var projection = Projection(counts: counts, progress: 0.62);
        var (shell, _) = await WorkbenchWithRunAsync(projection);
        shell.WorkbenchView.SelectTab(WorkbenchViewTab.Console);
        RunJobs();

        var expected = new[]
        {
            new FluentRunLine("RunId", "run-42"),
            new FluentRunLine("RunStatus", "running"),
            new FluentRunLine("OverallProgress", "62%"),
            new FluentRunLine("CurrentPageId", "page-2"),
            new FluentRunLine("CurrentStepType", "translate"),
            new FluentRunLine("Completed", "3"),
            new FluentRunLine("Failed", "2"),
            new FluentRunLine("Skipped", "1"),
            new FluentRunLine("Blocked", "4"),
        };
        Assert.Equal(FluentRunProjection.LineLabels, shell.WorkbenchViewModel.RunProjection!.Lines.Select(line => line.Label));
        for (var index = 0; index < expected.Length; index++)
        {
            Assert.Equal(expected[index].Label, shell.WorkbenchViewModel.RunProjection!.Lines[index].Label);
            Assert.Equal(expected[index].Value, shell.WorkbenchViewModel.RunProjection!.Lines[index].Value);
            var cell = shell.WorkbenchView.ConsoleRunValue(expected[index].Label);
            Assert.NotNull(cell);
            Assert.Equal(expected[index].Value, cell!.Text);
        }

        shell.Close();
    }

    // ---------------------------------------------------------------------------------------
    // AC-2（格 5）：控制按钮 IsEnabled 完全取自 Controls；禁用态点击 = 0 帧
    // ---------------------------------------------------------------------------------------

    [AvaloniaFact]
    public async Task AC2_ControlButtons_FollowProjectionControls_AndDisabledClickSendsNoFrame()
    {
        var projection = Projection(controls: new RunControlsInfo(
            CanPause: true, CanStop: true, CanContinue: false, CanRestart: false, CanAbandon: false, CanRetryFailed: true));
        var (shell, host) = await WorkbenchWithRunAsync(projection);
        shell.WorkbenchView.SelectTab(WorkbenchViewTab.Console);
        RunJobs();

        var view = shell.WorkbenchView;
        Assert.True(view.PauseRunButton.IsEnabled);
        Assert.True(view.StopRunButton.IsEnabled);
        Assert.False(view.ContinueRunButton.IsEnabled);
        Assert.True(view.RetryRunButton.IsEnabled);

        // 禁用态点击必须 0 帧（即便 RaiseEvent 绕过 IsEnabled，VM 侧也 fail-closed）。
        view.ContinueRunButton.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        RunJobs();
        Assert.Empty(host.ControlRunRequests);

        // 启用态点击走真实 ControlRunAsync（暂停）。
        view.PauseRunButton.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        RunJobs();
        var control = Assert.Single(host.ControlRunRequests);
        Assert.Equal(RunControlAction.Pause, control.Action);

        // 全禁用投影：四个按钮都不发帧。
        host.ScriptedTaskProjections.Enqueue(Projection(controls: new RunControlsInfo(false, false, false, false, false, false)));
        shell.WorkbenchViewModel.StartRunPolling();
        await shell.WorkbenchViewModel.TickRunPollForTestAsync();
        shell.WorkbenchViewModel.StopRunPolling();
        RunJobs();
        Assert.False(view.PauseRunButton.IsEnabled);
        Assert.False(view.StopRunButton.IsEnabled);
        Assert.False(view.ContinueRunButton.IsEnabled);
        Assert.False(view.RetryRunButton.IsEnabled);
        var framesBefore = host.ControlRunRequests.Count + host.RetriedFailedRuns.Count;
        foreach (var button in new[] { view.PauseRunButton, view.StopRunButton, view.ContinueRunButton, view.RetryRunButton })
        {
            button.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        }

        RunJobs();
        Assert.Equal(framesBefore, host.ControlRunRequests.Count + host.RetriedFailedRuns.Count);

        shell.Close();
    }

    // ---------------------------------------------------------------------------------------
    // AC-2（格 5）：Counts 缺失显示「—」而非 0
    // ---------------------------------------------------------------------------------------

    [AvaloniaFact]
    public async Task AC2_MissingCounts_RenderDash_NotZero()
    {
        // Counts 全 null（Core 未报告）+ 行里有 done 行（诱饵：不得从 rows 推导计数）。
        var rows = new[]
        {
            new RunRowInfo("page-1", 0, "p1.png", "done", false, false, null),
            new RunRowInfo("page-2", 1, "p2.png", "done", false, false, null),
        };
        var projection = Projection(rows: rows, counts: new RunCountsInfo());
        var (shell, _) = await WorkbenchWithRunAsync(projection);
        shell.WorkbenchView.SelectTab(WorkbenchViewTab.Console);
        RunJobs();

        foreach (var field in new[] { "Completed", "Failed", "Skipped", "Blocked" })
        {
            var cell = shell.WorkbenchView.ConsoleRunValue(field);
            Assert.NotNull(cell);
            Assert.Equal(FluentRunProjection.Missing, cell!.Text);
        }

        Assert.DoesNotContain("0", shell.WorkbenchView.ConsoleRunValue("Completed")!.Text, StringComparison.Ordinal);
        shell.Close();
    }

    // ---------------------------------------------------------------------------------------
    // AC-3（格 2）：双页加载 Pages[i]/Pages[i+1] 各 1 次、pageId 不同；末页只 1 次
    // ---------------------------------------------------------------------------------------

    [AvaloniaFact]
    public async Task AC3_DoublePage_LoadsBothPagesOnce_WithDistinctPageIds_LastPageOnlyOnce()
    {
        var loads = new Dictionary<string, int>(StringComparer.Ordinal);
        ReaderPageData Page(string pageId, int order) => new(pageId, order, 320, 480, _ =>
        {
            loads[pageId] = loads.GetValueOrDefault(pageId) + 1;
            return Task.FromResult<byte[]?>(TinyPng);
        });

        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        host.ReaderBooksByChapterId["chapter-key"] = new ReaderBookData(
            "book-1", "Sample", "chapter-key", "第 1 章", "fit-page",
            [Page("page-1", 0), Page("page-2", 1), Page("page-3", 2)]);
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Reader);
        shell.ReaderViewModel.DoublePage = true;
        await shell.ReaderViewModel.LoadAsync("book-1", "chapter-key");
        RunJobs();

        var viewModel = shell.ReaderViewModel;
        Assert.Equal(1, loads.GetValueOrDefault("page-1"));
        Assert.Equal(1, loads.GetValueOrDefault("page-2"));
        Assert.Equal(0, loads.GetValueOrDefault("page-3"));
        Assert.Equal("page-1", viewModel.PageId);
        Assert.Equal("page-2", viewModel.SecondaryPageId);
        Assert.NotEqual(viewModel.PageId, viewModel.SecondaryPageId);
        Assert.True(shell.ReaderView.PageImageSecondary.IsVisible);

        // 翻到第 2 页：加载 page-2（当前）+ page-3（后一页）。
        Assert.True(await viewModel.NavigateAsync(1));
        RunJobs();
        Assert.Equal(2, loads.GetValueOrDefault("page-2"));
        Assert.Equal(1, loads.GetValueOrDefault("page-3"));
        Assert.Equal("page-3", viewModel.SecondaryPageId);

        // 末页：只加载 1 次，第二页不得复用当前页 bytes 充数。
        Assert.True(await viewModel.NavigateAsync(1));
        RunJobs();
        Assert.Equal(2, loads.GetValueOrDefault("page-3"));
        Assert.Null(viewModel.SecondaryPageId);
        Assert.Null(viewModel.PageBytesSecondary);
        Assert.False(shell.ReaderView.PageImageSecondary.IsVisible);

        shell.Close();
    }

    // ---------------------------------------------------------------------------------------
    // AC-3（格 2）：webtoon 连续页可滚动 + SaveReadingProgressAsync 收到 scrollOffsetY>0
    // ---------------------------------------------------------------------------------------

    [AvaloniaFact]
    public async Task AC3_WebtoonScroll_IsScrollable_AndSavesPositiveScrollOffset()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        host.ReaderBooksByChapterId["chapter-key"] = new ReaderBookData(
            "book-1", "Sample", "chapter-key", "第 1 章", "webtoon_vertical",
            [
                new ReaderPageData("page-1", 0, 320, 900, _ => Task.FromResult<byte[]?>(TinyPng)),
                new ReaderPageData("page-2", 1, 320, 900, _ => Task.FromResult<byte[]?>(TinyPng)),
            ]);
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Reader);
        await shell.ReaderViewModel.LoadAsync("book-1", "chapter-key");
        RunJobs();

        var viewModel = shell.ReaderViewModel;
        var view = shell.ReaderView;
        Assert.True(viewModel.IsWebtoon);
        Assert.True(view.WebtoonScroll.IsVisible);
        Assert.False(viewModel.DoublePage); // 滚动模式不依赖双页开关
        Assert.True(view.WebtoonScroll.Extent.Height > view.WebtoonScroll.Viewport.Height,
            $"webtoon stack must be scrollable (extent={view.WebtoonScroll.Extent.Height}, viewport={view.WebtoonScroll.Viewport.Height})");

        view.WebtoonScroll.Offset = new Vector(0, 420);
        RunJobs();
        Assert.True(viewModel.ScrollOffsetY > 0, $"scrollOffsetY={viewModel.ScrollOffsetY}");

        Assert.True(await view.FlushScrollProgressAsync());
        var attempt = host.Progress.Attempts.Last();
        Assert.Equal("page-1", attempt.PageId);
        Assert.True(attempt.ScrollOffsetY is > 0, $"SaveReadingProgressAsync received scrollOffsetY={attempt.ScrollOffsetY}");

        shell.Close();
    }

    // ---------------------------------------------------------------------------------------
    // AC-3（格 2）：单页模式不回归（只加载当前页；不显示第二页）
    // ---------------------------------------------------------------------------------------

    [AvaloniaFact]
    public async Task AC3_SinglePage_LoadsOnlyCurrentPage_NoRegression()
    {
        var loads = new Dictionary<string, int>(StringComparer.Ordinal);
        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        host.ReaderBooksByChapterId["chapter-key"] = new ReaderBookData(
            "book-1", "Sample", "chapter-key", "第 1 章", "fit-page",
            [
                new ReaderPageData("page-1", 0, 320, 480, _ =>
                {
                    loads["page-1"] = loads.GetValueOrDefault("page-1") + 1;
                    return Task.FromResult<byte[]?>(TinyPng);
                }),
                new ReaderPageData("page-2", 1, 320, 480, _ =>
                {
                    loads["page-2"] = loads.GetValueOrDefault("page-2") + 1;
                    return Task.FromResult<byte[]?>(TinyPng);
                }),
            ]);
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Reader);
        await shell.ReaderViewModel.LoadAsync("book-1", "chapter-key");
        RunJobs();

        Assert.Equal(1, loads.GetValueOrDefault("page-1"));
        Assert.Equal(0, loads.GetValueOrDefault("page-2"));
        Assert.Null(shell.ReaderViewModel.SecondaryPageId);
        Assert.Null(shell.ReaderViewModel.PageBytesSecondary);
        Assert.False(shell.ReaderView.PageImageSecondary.IsVisible);
        Assert.NotNull(shell.ReaderView.PageImage.Source);

        shell.Close();
    }

    // ---------------------------------------------------------------------------------------
    // R3-002（r1 P1）：webtoon 末页必须彻底清空第二页 —— 不得残留上一页 bitmap
    // ---------------------------------------------------------------------------------------

    [AvaloniaFact]
    public async Task R3002_WebtoonLastPage_ClearsStaleSecondaryImage()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        host.ReaderBooksByChapterId["chapter-key"] = new ReaderBookData(
            "book-1", "Sample", "chapter-key", "第 1 章", "webtoon_vertical",
            [
                new ReaderPageData("page-1", 0, 320, 480, _ => Task.FromResult<byte[]?>(TinyPng)),
                new ReaderPageData("page-2", 1, 320, 480, _ => Task.FromResult<byte[]?>(TinyPng)),
                new ReaderPageData("page-3", 2, 320, 480, _ => Task.FromResult<byte[]?>(TinyPng)),
            ]);
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Reader);
        await shell.ReaderViewModel.LoadAsync("book-1", "chapter-key");
        RunJobs();

        var viewModel = shell.ReaderViewModel;
        var view = shell.ReaderView;
        Assert.True(viewModel.IsWebtoon);
        Assert.Equal("page-2", viewModel.SecondaryPageId);
        Assert.NotNull(view.WebtoonSecondaryImage.Source);
        Assert.True(view.WebtoonSecondaryImage.IsVisible);

        // 中间页：page-3 成为后继页（第二页仍在显示）。
        Assert.True(await viewModel.NavigateAsync(1));
        RunJobs();
        Assert.Equal("page-3", viewModel.SecondaryPageId);
        Assert.NotNull(view.WebtoonSecondaryImage.Source);

        // 末页：后继页不存在 → webtoon 第二页必须彻底清空（旧实现只清 Source，残留 bitmap 会继续显示）。
        Assert.True(await viewModel.NavigateAsync(1));
        RunJobs();
        Assert.Null(viewModel.SecondaryPageId);
        Assert.Null(viewModel.PageBytesSecondary);
        Assert.Null(view.WebtoonSecondaryImage.Source);
        Assert.False(view.WebtoonSecondaryImage.IsVisible);
        Assert.True(view.WebtoonPrimaryImage.IsVisible);

        shell.Close();
    }

    // ---------------------------------------------------------------------------------------
    // AC-4（格 4）：状态条 = "Filtered / Books 部作品" + ΣPageCount（null → 「—」且不计入），三态
    // ---------------------------------------------------------------------------------------

    private static HostViewSnapshot BooksSnapshot(params (string Title, int? PageCount)[] books)
    {
        var summaries = books.Select((book, index) => new BookSummary(
            $"book-{index}", book.Title, string.Empty, false, false, book.PageCount,
            "2026-10-27T00:00:00Z", "2026-10-27T00:00:00Z")).ToArray();
        return new HostViewSnapshot(
            HostViewState.Ready,
            "Host 就绪 · core_service protocol 2.3 + host_bridge wire v1",
            "只读（S2 parity 前） · sidecars ready",
            null,
            null,
            summaries,
            4,
            true,
            null);
    }

    [AvaloniaFact]
    public async Task AC4_ShelfStats_FilteredEmptyReadOnly_ThreeStates()
    {
        // 态 1：筛选后（1 / 3 部作品 · Σ=100；null 不计入）。
        var host = new FakeHostController(BooksSnapshot(("Alpha", 100), ("Beta", null), ("Gamma", 50)));
        var shell = CreateShell(host);
        await shell.ShelfViewModel.RefreshAsync();
        RunJobs();
        Assert.Equal("3 / 3 部作品 · 总页数 150", shell.ShelfViewModel.StatsLine);
        Assert.Contains("3 / 3 部作品", shell.ShelfView.StatusTextBlock.Text, StringComparison.Ordinal);
        Assert.Contains("总页数 150", shell.ShelfView.StatusTextBlock.Text, StringComparison.Ordinal);

        shell.ShelfViewModel.Search = "Alpha";
        RunJobs();
        Assert.Equal("1 / 3 部作品 · 总页数 100", shell.ShelfViewModel.StatsLine);

        // 态 2：空书架（0 / 0 部作品 · 总页数「—」）。
        var emptyHost = new FakeHostController(BooksSnapshot());
        var emptyShell = CreateShell(emptyHost);
        await emptyShell.ShelfViewModel.RefreshAsync();
        RunJobs();
        Assert.Equal("0 / 0 部作品 · 总页数 —", emptyShell.ShelfViewModel.StatsLine);
        emptyShell.Close();

        // 态 3：只读 Host（聚合照常；状态条带只读前缀）。
        var readOnlyHost = new FakeHostController(BooksSnapshot(("Alpha", 100), ("Beta", 30)) with
        {
            ModeLine = "只读（S2 parity 前） · sidecars ready",
        });
        readOnlyHost.Snapshot = readOnlyHost.Snapshot with { WritesAllowed = false };
        var readOnlyShell = CreateShell(readOnlyHost);
        await readOnlyShell.ShelfViewModel.RefreshAsync();
        RunJobs();
        Assert.True(readOnlyShell.ShelfViewModel.IsReadOnly);
        Assert.Equal("2 / 2 部作品 · 总页数 130", readOnlyShell.ShelfViewModel.StatsLine);
        Assert.StartsWith("只读 ·", readOnlyShell.ShelfView.StatusTextBlock.Text, StringComparison.Ordinal);
        readOnlyShell.Close();

        shell.Close();
    }

    [Fact]
    public void AC4_ShelfStats_AddsNoHostCommand_RegistrySetIsIdenticalToBase()
    {
        // AC-4 源码断言：HostCommandRegistry 命令集合与卡前（base 9429fc210）逐字相同。
        var baselinePath = Path.Combine(RepoRoot(), "verification", "FEA-06-RESIDUAL-3", "baseline", "host-commands.txt");
        Assert.True(File.Exists(baselinePath), $"missing command baseline: {baselinePath}");
        var expected = File.ReadAllLines(baselinePath).Where(line => line.Length > 0).ToArray();
        var actual = HostCommandRegistry.All.Keys.OrderBy(key => key, StringComparer.Ordinal).ToArray();
        Assert.Equal(expected, actual);
    }

    // ---------------------------------------------------------------------------------------
    // AC-5（方案 a）：三空间 Tab 完整遍历（S ⊇ F(P)、无连续重复）
    // ---------------------------------------------------------------------------------------

    private static List<Control> FocusSet(TopLevel topLevel) =>
        topLevel.GetVisualDescendants()
            .OfType<Control>()
            .Where(control => control.Focusable && control.IsEffectivelyVisible && control.IsEffectivelyEnabled &&
                              control.Bounds.Width > 1 && control.Bounds.Height > 1)
            .ToList();

    private static List<Control> TabSweep(TopLevel topLevel, int steps)
    {
        var visited = new List<Control>();
        for (var step = 0; step < steps; step++)
        {
            topLevel.KeyPressQwerty(PhysicalKey.Tab, RawInputModifiers.None);
            topLevel.KeyReleaseQwerty(PhysicalKey.Tab, RawInputModifiers.None);
            RunJobs();
            if (topLevel.FocusManager?.GetFocusedElement() is Control focused)
            {
                visited.Add(focused);
            }
        }

        return visited;
    }

    [AvaloniaFact]
    public async Task AC5_TabTraversal_LibraryReaderSettings_CoversFocusableSet_NoConsecutiveRepeats()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("Sample"));
        host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 0)];
        host.RegionsByPage["page-1"] = new RegionPageProjection([], null);
        host.ReaderBooksByChapterId["chapter-key"] = new ReaderBookData(
            "book-1", "Sample", "chapter-key", "第 1 章", "fit-page",
            [new ReaderPageData("page-1", 0, 320, 480, _ => Task.FromResult<byte[]?>(TinyPng))]);
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Library);
        RunJobs();

        foreach (var page in new[] { FluentPage.Library, FluentPage.Reader, FluentPage.Settings })
        {
            shell.Navigate(page);
            RunJobs();
            if (page == FluentPage.Reader)
            {
                await shell.ReaderViewModel.LoadAsync("book-1", "chapter-key");
                RunJobs();
            }

            if (page == FluentPage.Settings)
            {
                await shell.SettingsViewModel.LoadAsync();
                RunJobs();
            }

            var focusSet = FocusSet(shell);
            Assert.NotEmpty(focusSet);
            var visited = TabSweep(shell, (focusSet.Count * 2) + 8);
            Assert.NotEmpty(visited);

            // A1（卡面口径 S ⊇ F(P)；r1 R3-005 修正断言方向）：**全部**可见可聚焦控件都必须被
            // Tab 遍历覆盖，且每个落点仍在 S 内（不得落进隐藏/禁用）。
            foreach (var stop in visited)
            {
                Assert.Contains(stop, focusSet);
                Assert.True(stop.IsEffectivelyVisible, $"{page}: focus landed on a hidden control {stop.GetType().Name}");
                Assert.True(stop.IsEffectivelyEnabled, $"{page}: focus landed on a disabled control {stop.GetType().Name}");
            }

            var unreached = focusSet.Except(visited).ToList();
            Assert.True(unreached.Count == 0,
                $"{page}: Tab traversal missed {unreached.Count}/{focusSet.Count} focusable controls: " +
                string.Join(", ", unreached.Take(20).Select(control => control.GetType().FullName)));

            // 无连续重复（Tab 必须真正移动焦点）。
            for (var index = 1; index < visited.Count; index++)
            {
                Assert.False(ReferenceEquals(visited[index], visited[index - 1]),
                    $"{page}: Tab did not move focus at step {index} ({visited[index].GetType().FullName})");
            }
        }

        shell.Close();
    }

    [AvaloniaFact]
    public void AC5_HiddenControl_IsExcludedFromTabOrder()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("Sample"));
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Library);
        RunJobs();

        var hidden = shell.FindControl<Button>("NavRecycle")!;
        Assert.True(hidden.IsEffectivelyVisible);
        Assert.Contains(hidden, FocusSet(shell));

        hidden.IsVisible = false;
        RunJobs();
        Assert.DoesNotContain(hidden, FocusSet(shell));
        var afterHide = TabSweep(shell, FocusSet(shell).Count + 8);
        Assert.DoesNotContain(afterHide, control => ReferenceEquals(control, hidden));
        Assert.DoesNotContain(afterHide, control => !control.IsEffectivelyVisible);
        shell.Close();
    }

    // ---------------------------------------------------------------------------------------
    // AC-5：A3 每个 Tab 落点 peer.GetName() 非空且非类型名；A4 控件类型白名单
    // ---------------------------------------------------------------------------------------

    [AvaloniaFact]
    public async Task AC5_TabStops_ExposeReadableAutomationNames_AndWhitelistedControlTypes()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("Sample"));
        host.ReaderBooksByChapterId["chapter-key"] = new ReaderBookData(
            "book-1", "Sample", "chapter-key", "第 1 章", "fit-page",
            [new ReaderPageData("page-1", 0, 320, 480, _ => Task.FromResult<byte[]?>(TinyPng))]);
        var shell = CreateShell(host);

        var whitelist = new HashSet<AutomationControlType>
        {
            AutomationControlType.Button,
            AutomationControlType.Edit,
            AutomationControlType.ComboBox,
            AutomationControlType.CheckBox,
            AutomationControlType.RadioButton,
            AutomationControlType.Slider,
            AutomationControlType.List,
            AutomationControlType.ListItem,
            AutomationControlType.Pane,
            AutomationControlType.Group,
            AutomationControlType.Document,
            AutomationControlType.Image,
            AutomationControlType.Custom,
        };

        var unnamed = new List<string>();
        var offWhitelist = new List<string>();
        var checkedCount = 0;
        foreach (var page in new[] { FluentPage.Library, FluentPage.Reader, FluentPage.Settings })
        {
            shell.Navigate(page);
            RunJobs();
            if (page == FluentPage.Reader)
            {
                await shell.ReaderViewModel.LoadAsync("book-1", "chapter-key");
                RunJobs();
            }

            if (page == FluentPage.Settings)
            {
                await shell.SettingsViewModel.LoadAsync();
                RunJobs();
            }

            var visited = TabSweep(shell, (FocusSet(shell).Count * 2) + 8);
            foreach (var stop in visited.Distinct())
            {
                var peer = ControlAutomationPeer.CreatePeerForElement(stop);
                if (peer is null)
                {
                    unnamed.Add($"{page}: {stop.GetType().FullName} has no automation peer");
                    continue;
                }

                var name = peer.GetName();
                if (string.IsNullOrWhiteSpace(name) || name.StartsWith("Avalonia.", StringComparison.Ordinal) ||
                    name.StartsWith("NewManga.", StringComparison.Ordinal) ||
                    string.Equals(name, stop.GetType().Name, StringComparison.Ordinal) ||
                    string.Equals(name, stop.GetType().FullName, StringComparison.Ordinal))
                {
                    unnamed.Add($"{page}: {stop.GetType().FullName} name='{name ?? "<null>"}'");
                }

                var controlType = peer.GetAutomationControlType();
                // L-R3-2：设计系统 ReaderPage 是只读文档面（自定义 Border，automation peer 无标准
                // 控件类型 = None）。不扩域改 DesignSystem（不在本卡 allowed_paths），DS 修复 re-home；
                // 例外必须显式登记，不得静默豁免（见 verification/FEA-06-RESIDUAL-3/limitations.md）。
                var customDocumentSurfaceTypes = new HashSet<Type> { typeof(ReaderPage) };
                var customDocumentSurface = controlType == AutomationControlType.None &&
                    customDocumentSurfaceTypes.Contains(stop.GetType());
                if (!whitelist.Contains(controlType) && !customDocumentSurface)
                {
                    offWhitelist.Add($"{page}: {stop.GetType().FullName} type={controlType}");
                }

                checkedCount++;
            }
        }

        Assert.True(checkedCount > 0, "no Tab stops were collected for the a11y sweep");
        Assert.True(unnamed.Count == 0,
            $"focus stops without a readable AutomationProperties.Name ({unnamed.Count}):\n" +
            string.Join("\n", unnamed.Distinct(StringComparer.Ordinal).Take(40)));
        Assert.True(offWhitelist.Count == 0,
            $"focus stops outside the automation-control-type whitelist ({offWhitelist.Count}):\n" +
            string.Join("\n", offWhitelist.Distinct(StringComparer.Ordinal).Take(40)));
        shell.Close();
    }

    // ---------------------------------------------------------------------------------------
    // AC-5：A5 UIA 树每可交互节点有名 + 浮层开/关焦点往返
    // ---------------------------------------------------------------------------------------

    [AvaloniaFact]
    public void AC5_UiaTree_InteractiveNodesAreNamed_AndOverlayFocusRoundTrips()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("Sample"));
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Library);
        RunJobs();

        // 浮层焦点往返：命令面板（Ctrl+K）打开后焦点进入浮层，Esc 关闭后回到触发控件。
        var paletteButton = shell.FindControl<Button>("CommandPaletteButton")!;
        paletteButton.Focus(NavigationMethod.Tab);
        RunJobs();
        Assert.Same(paletteButton, shell.FocusManager?.GetFocusedElement());
        shell.HandleKeyForTest(Key.K, KeyModifiers.Control);
        RunJobs();
        var focusedInOverlay = shell.FocusManager?.GetFocusedElement() as Control;
        Assert.NotNull(focusedInOverlay);
        Assert.NotSame(paletteButton, focusedInOverlay);
        Assert.NotEmpty(focusedInOverlay!.GetVisualAncestors().OfType<FluentDialog>());
        shell.HandleKeyForTest(Key.Escape, KeyModifiers.None);
        RunJobs();
        Assert.Same(paletteButton, shell.FocusManager?.GetFocusedElement());

        // UIA 树：从 Shell 的 automation peer 出发，所有可交互节点必须有可读名字。
        var root = ControlAutomationPeer.CreatePeerForElement(shell);
        Assert.NotNull(root);
        var interactive = new HashSet<AutomationControlType>
        {
            AutomationControlType.Button,
            AutomationControlType.Edit,
            AutomationControlType.ComboBox,
            AutomationControlType.CheckBox,
            AutomationControlType.RadioButton,
            AutomationControlType.Slider,
            AutomationControlType.List,
            AutomationControlType.ListItem,
        };
        var queue = new Queue<AutomationPeer>();
        queue.Enqueue(root!);
        var nodes = 0;
        var unnamed = new List<string>();
        var seen = new HashSet<AutomationPeer>();
        while (queue.Count > 0)
        {
            var peer = queue.Dequeue();
            if (!seen.Add(peer))
            {
                continue;
            }

            var type = peer.GetAutomationControlType();
            if (interactive.Contains(type))
            {
                nodes++;
                var name = peer.GetName();
                if (string.IsNullOrWhiteSpace(name) || name.StartsWith("Avalonia.", StringComparison.Ordinal) ||
                    name.StartsWith("NewManga.", StringComparison.Ordinal) ||
                    string.Equals(name, peer.GetType().Name, StringComparison.Ordinal))
                {
                    unnamed.Add($"{type}: name='{name ?? "<null>"}' ({peer.GetType().FullName})");
                }
            }

            foreach (var child in peer.GetChildren() ?? new List<AutomationPeer>())
            {
                queue.Enqueue(child);
            }
        }

        Assert.True(nodes > 0, "the UIA tree exposed no interactive nodes");
        Assert.True(unnamed.Count == 0,
            $"UIA interactive nodes without a readable name ({unnamed.Count}):\n" +
            string.Join("\n", unnamed.Distinct(StringComparer.Ordinal).Take(40)));
        shell.Close();
    }

    // ---------------------------------------------------------------------------------------
    // AC-5：Studio 空间 Tab = 模式切换（全局绑定不变）+ 页签条 ←/→ 切页签（本卡实现）
    // ---------------------------------------------------------------------------------------

    [AvaloniaFact]
    public async Task AC5_StudioTabTogglesMode_AndTabStripArrowsSwitchTabs()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("Sample"));
        host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 0)];
        host.RegionsByPage["page-1"] = new RegionPageProjection([], null);
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Workbench);
        await shell.WorkbenchView.LoadAsync("chapter-key");
        RunJobs();

        // Tab = 模式切换（设计 03 §1 冻结全局键：studio.mode.toggle；本卡不改绑定）。
        Assert.False(shell.WorkbenchViewModel.IsBatch);
        Assert.True(shell.HandleKeyForTest(Key.Tab, KeyModifiers.None));
        Assert.True(shell.WorkbenchViewModel.IsBatch);
        Assert.Equal(WorkbenchViewTab.Batch, shell.WorkbenchView.ActiveTab);
        Assert.True(shell.HandleKeyForTest(Key.Tab, KeyModifiers.None));
        Assert.False(shell.WorkbenchViewModel.IsBatch);

        // 页签条 ←/→：焦点在页签条时切换页签并移动焦点（设计 03 §2 冻结行）。
        var tabs = shell.WorkbenchView.ViewTabs.Children.OfType<Button>().ToArray();
        Assert.Equal(3, tabs.Length);
        tabs[0].Focus(NavigationMethod.Tab);
        RunJobs();
        Assert.Equal(WorkbenchViewTab.Page, shell.WorkbenchView.ActiveTab);
        shell.KeyPressQwerty(PhysicalKey.ArrowRight, RawInputModifiers.None);
        shell.KeyReleaseQwerty(PhysicalKey.ArrowRight, RawInputModifiers.None);
        RunJobs();
        Assert.Equal(WorkbenchViewTab.Batch, shell.WorkbenchView.ActiveTab);
        Assert.Same(tabs[1], shell.FocusManager?.GetFocusedElement());
        shell.KeyPressQwerty(PhysicalKey.ArrowRight, RawInputModifiers.None);
        shell.KeyReleaseQwerty(PhysicalKey.ArrowRight, RawInputModifiers.None);
        RunJobs();
        Assert.Equal(WorkbenchViewTab.Console, shell.WorkbenchView.ActiveTab);
        shell.KeyPressQwerty(PhysicalKey.ArrowLeft, RawInputModifiers.None);
        shell.KeyReleaseQwerty(PhysicalKey.ArrowLeft, RawInputModifiers.None);
        RunJobs();
        Assert.Equal(WorkbenchViewTab.Batch, shell.WorkbenchView.ActiveTab);
        Assert.Same(tabs[1], shell.FocusManager?.GetFocusedElement());

        shell.Close();
    }
}
