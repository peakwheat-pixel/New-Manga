using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using NewManga.App.Shell.V2.Studio;
using NewManga.App.ViewModels.V2.Studio;

namespace NewManga.App.Tests;

/// <summary>V11R-B-3 headless smoke test: the composed Studio really renders through Skia.</summary>
public sealed class V2StudioSmokeTests
{
    [AvaloniaFact]
    public async Task Studio_RendersRealFrame_WithSkia()
    {
        var (view, _, viewModel) = StudioFixtures.Open();
        Assert.True(await view.LoadAndRenderAsync("book-0", "ch-1"));
        StudioFixtures.Pump();

        Assert.Equal(StudioLoadState.Ready, viewModel.Page.LoadState);
        Assert.Equal(3, viewModel.Page.Regions.Count);

        var window = StudioFixtures.WindowOf(view);
        var frame = window.CaptureRenderedFrame();
        Assert.NotNull(frame);
        var path = StudioEvidence.File("V11R-B-3", "artifacts/smoke.png");
        frame!.Save(path);
        Assert.True(new FileInfo(path).Length > 4096, "screenshot is blank");
    }
}
