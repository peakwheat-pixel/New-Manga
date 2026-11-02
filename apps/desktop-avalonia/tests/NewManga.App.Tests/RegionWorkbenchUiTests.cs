using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Interactivity;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.ViewModels;
using NewManga.App.Views;
using NewManga.CoreClient;

namespace NewManga.App.Tests;

/// <summary>
/// READER-WORKBENCH-1 AC1–AC3 headless tests: the workbench loads the real book → chapter → page
/// chain through <see cref="IHostController"/>, projects Core <c>list_regions</c> geometry through
/// <c>page_size</c>, keeps the list/canvas selection bidirectional, runs retype / undo / rerender
/// through typed write seams and disables every write control under the read-only policy.
/// </summary>
public sealed class RegionWorkbenchUiTests
{
    // 1x1 transparent PNG: a real decodable image so the resource-channel path is exercised.
    private const string OnePixelPngBase64 =
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==";

    private static FakeHostController CreateHost(HostViewSnapshot? snapshot = null)
    {
        var host = new FakeHostController(snapshot ?? FakeHostController.ReadySnapshot("书一"));
        host.ChaptersByBook["book-0"] = new[]
        {
            new ChapterSummary("ch-1", "第 1 章", "1", 0),
        };
        host.ChapterPagesByChapter["ch-1"] = new[]
        {
            new ChapterPageSummary("p1", "01.jpg", 0),
            new ChapterPageSummary("p2", "02.jpg", 1),
        };
        host.RegionsByPage["p1"] = new RegionPageProjection(
            new[]
            {
                new RegionSummary(
                    "region-1",
                    "speech",
                    "skip",
                    "user",
                    3,
                    new RegionGeometrySummary(0.1, 0.1, 0.8, 0.8, Array.Empty<RegionGeometryPoint>())),
                new RegionSummary(
                    "region-2",
                    "sfx",
                    "translate",
                    "machine",
                    1,
                    new RegionGeometrySummary(0.2, 0.3, 0.1, 0.1, Array.Empty<RegionGeometryPoint>())),
            },
            new RegionPageSize(1200, 1660));
        host.PageImagesByPage["p1"] = Convert.FromBase64String(OnePixelPngBase64);
        host.RevisionsByRegion["region-1"] = new RegionRevisionHistory(
            "region-1",
            3,
            new[]
            {
                new RegionRevisionSummary("r1", 1, "user", "unreviewed", false, null, "t1", "speech", "skip", false),
                new RegionRevisionSummary("r2", 2, "user", "needs_review", false, null, "t2", "narration", "skip", false),
                new RegionRevisionSummary("r3", 3, "user", "confirmed", false, null, "t3", "speech", "skip", true),
            });
        return host;
    }

    private static (FakeHostController Host, WorkbenchViewModel ViewModel, WorkbenchPage Page) Open(
        HostViewSnapshot? snapshot = null)
    {
        var host = CreateHost(snapshot);
        var viewModel = new WorkbenchViewModel();
        var page = new WorkbenchPage(viewModel, host);
        return (host, viewModel, page);
    }

    private static void Click(Button button) => button.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));

    private static void Pump() => Dispatcher.UIThread.RunJobs();

    [AvaloniaFact]
    public async Task Workbench_LoadsRealBookChapterPageChain_AndProjectsRegionGeometry()
    {
        var (host, viewModel, page) = Open();

        Assert.True(await page.EnsureLoadedAsync());
        Pump();

        // AC1: the real Host reads happened in the book → chapter → page → region order.
        Assert.Equal(1, host.ChapterListCalls);
        Assert.Contains("ch-1", host.ChapterPageCalls);
        Assert.Contains("p1", host.PageImageCalls);
        Assert.Contains("p1", host.RegionListCalls);
        Assert.Equal("book-0", page.LoadedBookId);
        Assert.Equal("ch-1", page.LoadedChapterId);
        Assert.Equal("p1", page.LoadedPageId);

        // AC1: real region rows, not the old in-memory skeleton.
        Assert.Equal(2, viewModel.Regions.Count);
        var first = viewModel.Regions[0];
        Assert.Equal("region-1", first.Id);
        Assert.Equal("speech", first.Kind);
        Assert.Equal("user", first.Origin);
        Assert.Equal(3, first.RevisionNo);
        Assert.Equal("skip", first.SfxPolicy);

        // AC1: normalized bbox × page_size 1200×1660 = pixel rectangle.
        Assert.Equal(120, first.X, 3);
        Assert.Equal(166, first.Y, 3);
        Assert.Equal(960, first.Width, 3);
        Assert.Equal(1328, first.Height, 3);
        Assert.Equal(1200, page.PageProjection!.PageSize!.Width);
        Assert.Equal(1660, page.PageProjection.PageSize.Height);

        // AC1: selection is synchronized into the list, and the list drives the model.
        Assert.Same(first, viewModel.SelectedRegion);
        Assert.Same(first, page.RegionList.SelectedItem);
        Assert.Contains("region-1"[..8], page.SelectionDetail.Text);

        // AC2/AC3: writable Host + selected region enables every write control.
        Assert.True(page.WriteControlsEnabled);
        Assert.True(page.ApplyRegionTypeButton.IsEnabled);
        Assert.True(page.UndoRegionRevisionButton.IsEnabled);
        Assert.True(page.RerenderPageButton.IsEnabled);
        Assert.False(page.ReadOnlyBanner.IsVisible);

        Evidence.Write("workbench/ui-load.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC1");
            writer.WriteString("book_id", page.LoadedBookId);
            writer.WriteString("chapter_id", page.LoadedChapterId);
            writer.WriteString("page_id", page.LoadedPageId);
            writer.WriteNumber("region_count", viewModel.Regions.Count);
            writer.WriteString("first_region_id", first.Id);
            writer.WriteString("first_region_type", first.Kind);
            writer.WriteNumber("first_region_revision", first.RevisionNo);
            writer.WriteNumber("first_region_pixel_x", Math.Round(first.X, 3));
            writer.WriteNumber("first_region_pixel_y", Math.Round(first.Y, 3));
            writer.WriteNumber("first_region_pixel_width", Math.Round(first.Width, 3));
            writer.WriteNumber("first_region_pixel_height", Math.Round(first.Height, 3));
            writer.WriteNumber("page_width", page.PageProjection.PageSize.Width);
            writer.WriteNumber("page_height", page.PageProjection.PageSize.Height);
            writer.WriteBoolean("page_image_loaded", page.PageImageControl.Source is not null);
            writer.WriteEndObject();
        });
    }

    [AvaloniaFact]
    public async Task Workbench_RegionList_AndCanvasSelection_AreBidirectional()
    {
        var (_, viewModel, page) = Open();
        await page.EnsureLoadedAsync();
        Pump();
        Assert.Equal(2, viewModel.Regions.Count);

        // list → model
        page.RegionList.SelectedIndex = 1;
        Pump();
        Assert.Same(viewModel.Regions[1], viewModel.SelectedRegion);
        Assert.Equal("sfx", viewModel.SelectedRegion!.Kind);

        // canvas → list + model
        page.SelectRegionFromCanvas(viewModel.Regions[0]);
        Pump();
        Assert.Same(viewModel.Regions[0], viewModel.SelectedRegion);
        Assert.Equal(0, page.RegionList.SelectedIndex);
    }

    [AvaloniaFact]
    public async Task Workbench_ApplyType_Undo_Rerender_RefreshRealRegionData()
    {
        var (host, viewModel, page) = Open();
        await page.EnsureLoadedAsync();
        Pump();
        page.SelectRegionFromCanvas(viewModel.Regions[0]);

        // AC2: retype keeps the read revision as the optimistic guard and refreshes afterwards.
        page.RegionTypeSelector.SelectedItem = "narration";
        var applied = await page.ApplySelectedRegionTypeAsync();
        Assert.True(applied.IsSuccess);
        Assert.Equal(4, applied.RevisionNo);
        var setCall = Assert.Single(host.SetRegionTypeCalls);
        Assert.Equal(("region-1", "narration", 3), setCall);
        Assert.Equal("narration", viewModel.Regions[0].Kind);
        Assert.Equal(4, viewModel.Regions[0].RevisionNo);
        Assert.Equal(4, page.PageProjection!.Regions[0].RevisionNo);
        Assert.Contains("narration", page.StatusText.Text);

        // AC2: undo reads the history first, then restores the immediately previous revision.
        var undone = await page.UndoSelectedRegionRevisionAsync();
        Assert.True(undone.IsSuccess);
        Assert.Equal(5, undone.RevisionNo);
        var restoreCall = Assert.Single(host.RestoreRegionCalls);
        Assert.Equal(("region-1", 3, 4), restoreCall);
        Assert.Equal("speech", viewModel.Regions[0].Kind);
        Assert.Equal(5, viewModel.Regions[0].RevisionNo);

        // AC2: rerender goes through the Host and refreshes the loaded page.
        var rerendered = await page.RerenderCurrentPageAsync();
        Assert.True(rerendered.IsSuccess);
        Assert.Equal("p1", Assert.Single(host.RerenderCalls));
        Assert.True(rerendered.PreviewPublished);
        Assert.Contains("重渲染", page.StatusText.Text);

        // The UI buttons drive the same typed paths (click path, not only direct calls).
        page.RegionTypeSelector.SelectedItem = "note";
        Click(page.ApplyRegionTypeButton);
        await page.LastWriteOperation;
        Pump();
        Assert.Equal(2, host.SetRegionTypeCalls.Count);
        Assert.Equal("note", host.SetRegionTypeCalls[1].NewType);

        Evidence.Write("workbench/ui-write.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC2");
            writer.WriteString("region_id", "region-1");
            writer.WriteNumber("retype_expected_revision", setCall.ExpectedRevision);
            writer.WriteNumber("retype_new_revision", applied.RevisionNo);
            writer.WriteNumber("restore_source_revision", restoreCall.RevisionNo);
            writer.WriteNumber("restore_expected_revision", restoreCall.ExpectedRevision);
            writer.WriteNumber("restore_new_revision", undone.RevisionNo);
            writer.WriteString("rerender_page_id", host.RerenderCalls[0]);
            writer.WriteString("rerender_artifact_id", rerendered.ArtifactId);
            writer.WriteBoolean("rerender_preview_published", rerendered.PreviewPublished);
            writer.WriteBoolean("undo_read_history_first", host.RevisionListCalls.Count >= 1);
            writer.WriteEndObject();
        });
    }

    [AvaloniaFact]
    public async Task Workbench_ReadOnlyHost_DisablesWrites_ShowsReason_ReadFaceStillWorks()
    {
        var (host, viewModel, page) = Open(FakeHostController.ReadOnlySnapshot("书一"));
        Assert.True(await page.EnsureLoadedAsync());
        Pump();

        // AC3: reads still work (real region rows are loaded)…
        Assert.Equal(2, viewModel.Regions.Count);
        Assert.Equal("p1", page.LoadedPageId);

        // …while every write control is disabled and the reason is visible.
        Assert.False(page.WriteControlsEnabled);
        Assert.False(page.ApplyRegionTypeButton.IsEnabled);
        Assert.False(page.UndoRegionRevisionButton.IsEnabled);
        Assert.False(page.RerenderPageButton.IsEnabled);
        Assert.False(page.RegionTypeSelector.IsEnabled);
        Assert.True(page.ReadOnlyBanner.IsVisible);
        Assert.Contains("只读", page.ReadOnlyBanner.Text);

        // AC3: a direct write attempt is a typed refusal with ZERO Controller write calls.
        page.RegionTypeSelector.SelectedItem = "narration";
        var refused = await page.ApplySelectedRegionTypeAsync();
        Assert.Equal(RegionOperationStatus.ReadOnly, refused.Status);
        Assert.Equal("HOST_READ_ONLY", refused.ErrorCode);
        Assert.Empty(host.SetRegionTypeCalls);
        var rerender = await page.RerenderCurrentPageAsync();
        Assert.Equal(RegionOperationStatus.ReadOnly, rerender.Status);
        Assert.Empty(host.RerenderCalls);

        Evidence.Write("workbench/ui-readonly.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC3");
            writer.WriteBoolean("writes_allowed", host.Snapshot.WritesAllowed);
            writer.WriteString("write_controls_enabled", page.WriteControlsEnabled ? "true" : "false");
            writer.WriteBoolean("banner_visible", page.ReadOnlyBanner.IsVisible);
            writer.WriteString("banner_text", page.ReadOnlyBanner.Text);
            writer.WriteNumber("regions_read_in_read_only_mode", viewModel.Regions.Count);
            writer.WriteString("retype_status", refused.Status.ToString());
            writer.WriteString("retype_error_code", refused.ErrorCode);
            writer.WriteBoolean("zero_write_calls", host.SetRegionTypeCalls.Count == 0 && host.RerenderCalls.Count == 0);
            writer.WriteEndObject();
        });
    }

    [AvaloniaFact]
    public void MainWindow_WorkbenchNavigation_LoadsTheRealRegionChain()
    {
        var host = CreateHost();
        var window = new MainWindow(host, new AppOptions());
        window.Show();
        Pump();
        window.Navigate("workbench");
        Pump();

        var localDeadline = DateTime.UtcNow + TimeSpan.FromSeconds(5);
        while (window.Workbench.LoadedPageId is null && DateTime.UtcNow < localDeadline)
        {
            Pump();
            Thread.Sleep(10);
        }

        Assert.Equal("p1", window.Workbench.LoadedPageId);
        Assert.Equal(2, window.Workbench.ViewModel.Regions.Count);
        Assert.Same(window.Workbench, window.PageHostControl.Content);
        window.Close();
    }
}
