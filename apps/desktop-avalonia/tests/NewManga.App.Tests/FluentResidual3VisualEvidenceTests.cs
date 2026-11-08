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

namespace NewManga.App.Tests;

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

    [AvaloniaFact]
    public async Task Captures_Residual3_Visual_Inventory_Only_When_Opted_In()
    {
        var root = RepositoryRoot();
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
            host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 0)];
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
            host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 0)];
            host.RegionsByPage["page-1"] = new RegionPageProjection([], null);
            shell.Navigate(FluentPage.Workbench);
            await shell.WorkbenchView.LoadAsync("chapter-key");
            shell.WorkbenchView.SelectTab(WorkbenchViewTab.Batch);
        });

        yield return ("05-workbench-batch-matrix", "workbench · 批量矩阵七状态（吸顶表头）", async (shell, host) =>
        {
            host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 0)];
            host.RegionsByPage["page-1"] = new RegionPageProjection([], null);
            shell.Navigate(FluentPage.Workbench);
            await shell.WorkbenchView.LoadAsync("chapter-key");
            shell.WorkbenchView.SelectTab(WorkbenchViewTab.Batch);
            await StartRunWithProjectionAsync(shell, host, SevenStateProjection());
            Assert.Equal(WorkbenchViewTab.Batch, shell.WorkbenchView.ActiveTab);
        });

        yield return ("06-console-nine-rows", "console · 9 行 Run 投影", async (shell, host) =>
        {
            host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 0)];
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
            $"page-{index + 1}", index, $"p{index + 1}.png", status, false, false,
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

    private static string RepositoryRoot()
    {
        var cursor = new DirectoryInfo(AppContext.BaseDirectory);
        while (cursor is not null && !File.Exists(Path.Combine(cursor.FullName, "doc", "tasks", "FEA-06-RESIDUAL-3.md")))
        {
            cursor = cursor.Parent;
        }

        return cursor?.FullName ?? throw new DirectoryNotFoundException("could not locate the New Manga repository root");
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
