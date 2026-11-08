using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Interactivity;
using Avalonia.Media.Imaging;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.App.Views.Fluent;
using NewManga.CoreClient;
using Xunit;
using Xunit.Sdk;

namespace NewManga.App.Tests;

/// <summary>
/// R3-013：AC-6 证据测试的 self-skip 属性。
/// <para>为什么不用 <c>[AvaloniaFact(Skip=...)]</c>：`AvaloniaFactAttribute` 是 sealed，无法在 discovery
/// 期按磁盘状态（.git 是否存在）决定 Skip；动态 `SkipException` 在本仓库的 Avalonia+Xunit 适配链路里
/// 会被记为失败（实测）。因此复刻 Avalonia 的 discoverer 接线
/// （<c>XunitTestCaseDiscoverer = AvaloniaUIFactDiscoverer</c>，它会创建在 Avalonia Dispatcher 上运行的
/// <c>AvaloniaTestCase</c>），并在特性构造时按显式前置条件设置 <see cref="FactAttribute.Skip"/>。</para>
/// </summary>
[AttributeUsage(AttributeTargets.Method, AllowMultiple = false)]
[XunitTestCaseDiscoverer("Avalonia.Headless.XUnit.AvaloniaUIFactDiscoverer", "Avalonia.Headless.XUnit")]
public sealed class GitBackedAvaloniaFactAttribute : FactAttribute
{
    public GitBackedAvaloniaFactAttribute()
    {
        if (!FluentResidual3EvidencePreconditions.IsSatisfied(out var reason))
        {
            Skip = reason;
        }
    }
}

/// <summary>AC-6 证据测试的显式前置条件：Git checkout + 仓库任务卡（repository root 定位）。</summary>
internal static class FluentResidual3EvidencePreconditions
{
    public static bool IsSatisfied(out string reason)
    {
        var root = FindRepositoryRoot();
        if (root is null)
        {
            reason = "reason: needs repository root (doc/tasks/FEA-06-RESIDUAL-3.md not found from the test output directory)";
            return false;
        }

        if (!HasGitMetadata(root))
        {
            reason = $"reason: needs a Git checkout (.git missing at {root}); evidence zero-write gate uses git status";
            return false;
        }

        reason = string.Empty;
        return true;
    }

    public static string? FindRepositoryRoot()
    {
        // 注意：本方法也在 **[GitBackedAvaloniaFact] 特性构造时（discovery 阶段）**执行，此时
        // AppContext.BaseDirectory 指向 vstest/discovery 宿主目录而**不是**测试输出目录；
        // 因此以测试程序集自身的 Location（bin/…/net9.0）为起点向上找仓库标记。
        var assemblyDirectory = Path.GetDirectoryName(typeof(FluentResidual3EvidencePreconditions).Assembly.Location);
        var cursor = new DirectoryInfo(string.IsNullOrEmpty(assemblyDirectory) ? AppContext.BaseDirectory : assemblyDirectory!);
        while (cursor is not null && !File.Exists(Path.Combine(cursor.FullName, "doc", "tasks", "FEA-06-RESIDUAL-3.md")))
        {
            cursor = cursor.Parent;
        }

        return cursor?.FullName;
    }

    /// <summary>仓库根必须有 .git（普通 checkout 是目录，worktree 是 gitdir 指针文件）。</summary>
    public static bool HasGitMetadata(string root)
    {
        var git = Path.Combine(root, ".git");
        return Directory.Exists(git) || File.Exists(git);
    }
}

/// <summary>
/// FEA-06-RESIDUAL-3 AC-6：证据/门禁。默认运行**零仓库写入**（跑前后
/// <c>git status --porcelain -- verification</c> 相等；<c>verification/FEA-06/**</c> 与
/// <c>verification/FEA-06-RESIDUAL-2/**</c> 恒无新写入）。显式 opt-in
/// <c>NEWMANGA_CAPTURE_RESIDUAL3_PNGS=1</c> 才写 9 张图 + inventory 到本卡证据目录；
/// **像素不作 AC 判据**（只作为签署证据存在）。
/// </summary>
public sealed class FluentResidual3VisualEvidenceTests
{
    private const string CaptureEnvVar = "NEWMANGA_CAPTURE_RESIDUAL3_PNGS";
    private const int ExpectedShotCount = 9;

    private sealed record Shot(string Name, string State, Bitmap Image);

    [GitBackedAvaloniaFact]
    public async Task Captures_Residual3_Visual_Inventory_Only_When_Opted_In()
    {
        // R3-013：前置条件（Git checkout + 任务卡定位）由 [GitBackedAvaloniaFact] 在 discovery 期求值，
        // 不满足即 Skip；这里再取一次仓库根用于证据路径。
        var root = FluentResidual3EvidencePreconditions.FindRepositoryRoot()
            ?? throw new DirectoryNotFoundException(
                "unreachable: [GitBackedAvaloniaFact] already skipped a non-repository checkout");

        var visuals = Path.Combine(root, "verification", "FEA-06-RESIDUAL-3", "visuals");
        var statusBefore = Git(root, "status", "--porcelain", "--", "verification");
        var visualsBefore = Directory.Exists(visuals)
            ? Directory.EnumerateFiles(visuals, "*", SearchOption.AllDirectories).OrderBy(path => path, StringComparer.Ordinal).ToArray()
            : Array.Empty<string>();
        var shots = new List<Shot>();
        try
        {
            foreach (var (name, state, build) in ShotPlan())
            {
                var host = new FakeHostController(FakeHostController.ReadySnapshot("Sample Manga"));
                var shell = FluentShell.CreateRoot(host: host);
                shell.Width = 1280;
                shell.Height = 900;
                shell.Show();
                RunJobs();
                try
                {
                    await build(shell, host);
                    RunJobs();
                    shell.UpdateLayout();
                    // headless 合成器需要显式 render tick 才会把最新内容画进帧；否则会捕获上一帧。
                    for (var tick = 0; tick < 3; tick++)
                    {
                        AvaloniaHeadlessPlatform.ForceRenderTimerTick();
                        RunJobs();
                    }

                    var frame = shell.CaptureRenderedFrame()
                        ?? throw new InvalidOperationException($"frame capture failed: {name}");
                    Assert.True(frame.PixelSize.Width > 0 && frame.PixelSize.Height > 0, $"{name}: empty frame");
                    shots.Add(new Shot(name, state, frame));
                }
                finally
                {
                    shell.Close();
                    RunJobs();
                }
            }

            Assert.Equal(ExpectedShotCount, shots.Count);
            Assert.Equal(shots.Count, shots.Select(shot => shot.Name).Distinct(StringComparer.Ordinal).Count());
            Assert.All(shots, shot => Assert.True(shot.Image.PixelSize.Width >= 320 && shot.Image.PixelSize.Height >= 240,
                $"{shot.Name}: frame too small {shot.Image.PixelSize}"));
            // 9 张必须是 9 个不同状态（防止 tab/主题切换没生效导致重复帧冒充证据）。
            var frameHashes = shots
                .Select(shot => Convert.ToHexString(SHA256.HashData(Residual2Evidence.Bytes(shot.Image))))
                .ToArray();
            Assert.Equal(ExpectedShotCount, frameHashes.Distinct(StringComparer.Ordinal).Count());

            if (CaptureEnabled())
            {
                WriteEvidence(visuals, shots);
                Assert.Equal(ExpectedShotCount, Directory.EnumerateFiles(visuals, "*.png").Count());
                Assert.True(File.Exists(Path.Combine(visuals, "inventory.md")));
            }
            else
            {
                // AC-6：默认（未 opt-in）零仓库写入 —— 证据目录与 verification 树在跑前后完全一致。
                Assert.Equal(statusBefore, Git(root, "status", "--porcelain", "--", "verification"));
                Assert.Equal(visualsBefore, Directory.Exists(visuals)
                    ? Directory.EnumerateFiles(visuals, "*", SearchOption.AllDirectories).OrderBy(path => path, StringComparer.Ordinal).ToArray()
                    : Array.Empty<string>());
                // FEA-06/** 与 FEA-06-RESIDUAL-2/** 不得有本卡产生的任何改动。
                Assert.Equal(string.Empty, Git(root, "status", "--porcelain", "--", "verification/FEA-06", "verification/FEA-06-RESIDUAL-2"));
            }
        }
        finally
        {
            foreach (var shot in shots)
            {
                shot.Image.Dispose();
            }
        }
    }

    // ---------------------------------------------------------------------------------------
    // 9 张签署证据的状态（像素不作 AC；只作为可复现证据）
    // ---------------------------------------------------------------------------------------

    private static IEnumerable<(string Name, string State, Func<FluentShell, FakeHostController, Task> Build)> ShotPlan()
    {
        yield return ("01-shelf-default", "shelf · 满态（真实投影）", async (shell, host) =>
        {
            await shell.ShelfViewModel.RefreshAsync();
            shell.Navigate(FluentPage.Library);
        });

        yield return ("02-shelf-readonly", "shelf · 只读（写入被拒）", async (shell, host) =>
        {
            host.Snapshot = host.Snapshot with { WritesAllowed = false };
            await shell.ShelfViewModel.RefreshAsync();
            shell.Navigate(FluentPage.Library);
        });

        yield return ("03-workbench-page", "workbench · 页面（画布 + 检查器）", async (shell, host) =>
        {
            host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 1)];
            host.RegionsByPage["page-1"] = new RegionPageProjection(
                [new RegionSummary("region-1", "speech", "keep", "detect", 1,
                    new RegionGeometrySummary(0.1, 0.1, 0.4, 0.2, []))],
                new RegionPageSize(640, 960));
            host.PageImagesByPage["page-1"] = Residual2Evidence.PagePng();
            shell.Navigate(FluentPage.Workbench);
            await shell.WorkbenchView.LoadAsync("chapter-key");
            shell.WorkbenchView.SelectPageTab();
            Assert.Equal(WorkbenchViewTab.Page, shell.WorkbenchView.ActiveTab);
        });

        yield return ("04-workbench-batch-empty", "workbench · 批量空态（无假数据）", async (shell, host) =>
        {
            host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 1)];
            host.RegionsByPage["page-1"] = new RegionPageProjection([], null);
            shell.Navigate(FluentPage.Workbench);
            await shell.WorkbenchView.LoadAsync("chapter-key");
            shell.WorkbenchView.SelectTab(WorkbenchViewTab.Batch);
        });

        yield return ("05-workbench-batch-matrix", "workbench · 批量矩阵七状态（吸顶表头）", async (shell, host) =>
        {
            host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 1)];
            host.RegionsByPage["page-1"] = new RegionPageProjection([], null);
            shell.Navigate(FluentPage.Workbench);
            await shell.WorkbenchView.LoadAsync("chapter-key");
            shell.WorkbenchView.SelectTab(WorkbenchViewTab.Batch);
            await StartRunWithProjectionAsync(shell, host, SevenStateProjection());
            Assert.Equal(WorkbenchViewTab.Batch, shell.WorkbenchView.ActiveTab);
        });

        yield return ("06-console-nine-rows", "console · 9 行 Run 投影", async (shell, host) =>
        {
            host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 1)];
            host.RegionsByPage["page-1"] = new RegionPageProjection([], null);
            shell.Navigate(FluentPage.Workbench);
            await shell.WorkbenchView.LoadAsync("chapter-key");
            await StartRunWithProjectionAsync(shell, host, SevenStateProjection());
            shell.WorkbenchView.SelectTab(WorkbenchViewTab.Console);
            Assert.Equal(WorkbenchViewTab.Console, shell.WorkbenchView.ActiveTab);
        });

        yield return ("07-reader-single", "reader · 单页", async (shell, host) =>
        {
            host.ReaderBooksByChapterId["chapter-key"] = new ReaderBookData(
                "book-1", "Sample Manga", "chapter-key", "第 1 章", "fit-page",
                [new ReaderPageData("page-1", 0, 320, 480, _ => Task.FromResult<byte[]?>(Residual2Evidence.PagePng()))]);
            shell.Navigate(FluentPage.Reader);
            await shell.ReaderViewModel.LoadAsync("book-1", "chapter-key");
        });

        yield return ("08-reader-double", "reader · 双页", async (shell, host) =>
        {
            host.ReaderBooksByChapterId["chapter-key"] = new ReaderBookData(
                "book-1", "Sample Manga", "chapter-key", "第 1 章", "fit-page",
                [
                    new ReaderPageData("page-1", 0, 320, 480, _ => Task.FromResult<byte[]?>(Residual2Evidence.PagePng())),
                    new ReaderPageData("page-2", 1, 320, 480, _ => Task.FromResult<byte[]?>(Residual2Evidence.PagePng())),
                ]);
            shell.ReaderViewModel.DoublePage = true;
            shell.Navigate(FluentPage.Reader);
            await shell.ReaderViewModel.LoadAsync("book-1", "chapter-key");
        });

        yield return ("09-reader-webtoon", "reader · webtoon 连续页滚动", async (shell, host) =>
        {
            host.ReaderBooksByChapterId["chapter-key"] = new ReaderBookData(
                "book-1", "Sample Manga", "chapter-key", "第 1 章", "webtoon_vertical",
                [
                    new ReaderPageData("page-1", 0, 320, 480, _ => Task.FromResult<byte[]?>(Residual2Evidence.PagePng())),
                    new ReaderPageData("page-2", 1, 320, 480, _ => Task.FromResult<byte[]?>(Residual2Evidence.PagePng())),
                ]);
            shell.Navigate(FluentPage.Reader);
            await shell.ReaderViewModel.LoadAsync("book-1", "chapter-key");
            shell.UpdateLayout();
            shell.ReaderView.WebtoonScroll.Offset = new Vector(0, 200);
            RunJobs();
        });
    }

    private static async Task StartRunWithProjectionAsync(
        FluentShell shell, FakeHostController host, TaskProjectionInfo projection)
    {
        shell.WorkbenchView.SelectTab(WorkbenchViewTab.Batch);
        RunJobs();
        shell.WorkbenchView.BatchStartButton.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        RunJobs();
        host.ScriptedTaskProjections.Enqueue(projection);
        await shell.WorkbenchViewModel.TickRunPollForTestAsync();
        shell.WorkbenchViewModel.StopRunPolling();
        RunJobs();
    }

    private static TaskProjectionInfo SevenStateProjection()
    {
        var statuses = new[] { "queued", "running", "done", "failed", "blocked", "stale", "skipped" };
        var rows = statuses.Select((status, index) => new RunRowInfo(
            $"page-{index + 1}", index + 1, $"p{index + 1}.png", status, false, false,
            status == "failed" ? "PROVIDER_NOT_CONFIGURED" : null)).ToArray();
        return new TaskProjectionInfo(
            "run-evidence",
            "running",
            "批量翻译",
            0.62,
            "page-2",
            "translate",
            Array.Empty<RunStepFlowInfo>(),
            rows,
            Array.Empty<RunTaskInfo>(),
            new RunCountsInfo(7, 1, 1, 1, 1, 2, 1),
            Array.Empty<string>(),
            new RunControlsInfo(true, true, false, false, false, true));
    }

    // ---------------------------------------------------------------------------------------
    // 证据写入（只在 opt-in 时调用）与门禁辅助
    // ---------------------------------------------------------------------------------------

    private static void WriteEvidence(string directory, IReadOnlyList<Shot> shots)
    {
        Directory.CreateDirectory(directory);
        var capturedAt = DateTimeOffset.Now.ToString("O");
        var builder = new StringBuilder();
        builder.AppendLine("# FEA-06-RESIDUAL-3 visual inventory（opt-in 证据；**像素不作 AC 判据**）");
        builder.AppendLine();
        builder.AppendLine("| file | state | raster-size | sha256 | signed_by | signed_at |");
        builder.AppendLine("|---|---|---|---|---|---|");
        foreach (var shot in shots)
        {
            var file = $"{shot.Name}.png";
            var path = Path.Combine(directory, file);
            shot.Image.Save(path);
            using var stream = File.OpenRead(path);
            var sha = Convert.ToHexString(SHA256.HashData(stream));
            builder.AppendLine($"| {file} | {shot.State} | {shot.Image.PixelSize.Width}x{shot.Image.PixelSize.Height} | {sha} | fea06-residual3-impl | {capturedAt} |");
        }

        builder.AppendLine();
        builder.AppendLine($"- task: FEA-06-RESIDUAL-3");
        builder.AppendLine($"- capture_env: {CaptureEnvVar}=1");
        builder.AppendLine($"- note: 运行 `$env:{CaptureEnvVar}='1'; dotnet test ... --filter FullyQualifiedName~FluentResidual3VisualEvidenceTests` 可重放；像素不作 AC。");
        File.WriteAllText(Path.Combine(directory, "inventory.md"), builder.ToString(), new UTF8Encoding(false));
    }

    private static bool CaptureEnabled() =>
        string.Equals(Environment.GetEnvironmentVariable(CaptureEnvVar), "1", StringComparison.OrdinalIgnoreCase);

    private static void RunJobs()
    {
        Dispatcher.UIThread.RunJobs(DispatcherPriority.Render);
        Dispatcher.UIThread.RunJobs(DispatcherPriority.Loaded);
        Dispatcher.UIThread.RunJobs();
    }

    private static string Git(string workingDirectory, params string[] arguments)
    {
        var start = new ProcessStartInfo("git")
        {
            WorkingDirectory = workingDirectory,
            RedirectStandardOutput = true,
            UseShellExecute = false,
            CreateNoWindow = true,
        };
        foreach (var argument in arguments)
        {
            start.ArgumentList.Add(argument);
        }

        using var process = Process.Start(start)!;
        var output = process.StandardOutput.ReadToEnd();
        process.WaitForExit();
        if (process.ExitCode != 0)
        {
            throw new InvalidOperationException($"git {string.Join(' ', arguments)} failed with {process.ExitCode}");
        }

        return output.Trim();
    }
}
