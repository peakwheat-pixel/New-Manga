using NewManga.App;
using NewManga.App.Services;
using NewManga.CoreClient;
using NewManga.Host;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-A-7: the export stale policy (<c>abort</c> / <c>continue_existing</c>) is now a real controller
/// parameter. Illegal values are refused locally with a typed code and zero Core frames; null keeps the
/// historical default <c>abort</c>; the headless fakes record what the UI asked for.
/// </summary>
public sealed class ExportStalePolicyTests
{
    private static readonly string[] Pages = { "page-1" };

    [Fact]
    public async Task FakeController_RecordsTheRequestedStalePolicy()
    {
        var fake = new FakeHostController(ReadySnapshot());

        await fake.StartExportAsync("book", "chapter", Pages, "target.zip", stalePolicy: "abort");
        await fake.StartExportAsync("book", "chapter", Pages, "target.zip", stalePolicy: "continue_existing");
        await fake.StartExportAsync("book", "chapter", Pages, "target.zip");

        Assert.Equal(3, fake.StartExportCalls.Count);
        Assert.Equal("abort", fake.StartExportCalls[0].StalePolicy);
        Assert.Equal("continue_existing", fake.StartExportCalls[1].StalePolicy);
        Assert.Null(fake.StartExportCalls[2].StalePolicy);
    }

    [Fact]
    public async Task NullController_AcceptsBothPolicies_WithoutThrowing()
    {
        var controller = NullHostController.Instance;

        Assert.Null(await controller.StartExportAsync("book", "chapter", Pages, "target.zip", stalePolicy: "abort"));
        Assert.Null(await controller.StartExportAsync("book", "chapter", Pages, "target.zip", stalePolicy: "continue_existing"));
        Assert.Null(await controller.StartExportAsync("book", "chapter", Pages, "target.zip"));
    }

    [Fact]
    public async Task IllegalPolicy_IsRefusedLocally_WithTypedCode_AndNoFrames()
    {
        await using var controller = new HostController(UnstartedOptions());
        await controller.StartAsync();

        var result = await controller.StartExportAsync(
            "book", "chapter", Pages, Path.Combine(Path.GetTempPath(), "target.zip"), stalePolicy: "explode");

        Assert.Null(result);
        Assert.Equal("INVALID_REQUEST", controller.Snapshot.LastError);
        Assert.Equal(0, controller.Snapshot.WireFrameCount);
    }

    [Fact]
    public async Task BlankPolicy_FallsBackToTheDefaultAbort()
    {
        await using var controller = new HostController(UnstartedOptions());
        await controller.StartAsync();

        var result = await controller.StartExportAsync(
            "book", "chapter", Pages, Path.Combine(Path.GetTempPath(), "target.zip"), stalePolicy: "   ");

        // Not refused as an illegal policy: the request reaches the (unstarted) runtime and is null there.
        Assert.Null(result);
        Assert.NotEqual("INVALID_REQUEST", controller.Snapshot.LastError);
    }

    private static HostViewSnapshot ReadySnapshot() => new(
        HostViewState.Ready,
        "ready",
        "读写就绪",
        null,
        null,
        Array.Empty<BookSummary>(),
        0,
        true,
        null);

    private static HostOptions UnstartedOptions() => new()
    {
        DataRoot = Path.Combine(Path.GetTempPath(), "newmanga-a7-unit-" + Guid.NewGuid().ToString("N")[..8]),
        LogDirectory = Path.Combine(Path.GetTempPath(), "newmanga-a7-unit-logs-" + Guid.NewGuid().ToString("N")[..8]),
        MutexName = @"Local\NewManga.App.Tests.A7." + Guid.NewGuid().ToString("N")[..10],
        SidecarDirectoryOverride = Path.Combine(Path.GetTempPath(), "newmanga-a7-missing-sidecar"),
        DetectLegacyShell = false,
    };
}
