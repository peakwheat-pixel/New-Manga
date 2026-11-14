using NewManga.App.Services;
using NewManga.CoreClient.Commands;
using NewManga.Host;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-06-RESIDUAL-4B slice 2 (4A spec S3 / AC1): the <c>IHostController.ListPageRegionTextsAsync</c>
/// port contract. These tests pin the four properties the workbench compare panel relies on before
/// any UI exists:
/// <list type="number">
/// <item>the inert host and the headless fake degrade to <c>null</c> and never throw or fabricate;</item>
/// <item>a fake can hand back a real projection and records the call (one call per open);</item>
/// <item>the production controller answers <c>null</c> while the Host is not ready (typed reasons stay
/// inside the controller and never reach the UI thread);</item>
/// <item>the method signature is exactly the pre-authorized C-07 row #80 shape -- no revision guard
/// parameter can creep in.</item>
/// </list>
/// The live Host↔Core echo path is NOT covered here (it needs a real sidecar and belongs to the gated
/// integration suite); that limitation is recorded in the card, not hidden by a skip.
/// </summary>
public sealed class ListPageRegionTextsPortTests
{
    public static IEnumerable<object[]> InertHosts()
    {
        yield return new object[] { NullHostController.Instance };
        yield return new object[] { new FakeHostController(FakeHostController.ReadySnapshot("book")) };
    }

    [Theory]
    [MemberData(nameof(InertHosts))]
    public async Task ProjectionUnavailable_DegradesToNull_WithoutThrowing(IHostController host)
    {
        // No filter and an explicit filter must both degrade to null, never to an empty projection:
        // "no regions" and "projection unavailable" are different states for the compare panel.
        Assert.Null(await host.ListPageRegionTextsAsync("page-1", cancellationToken: CancellationToken.None));
        Assert.Null(await host.ListPageRegionTextsAsync(
            "page-1", new[] { "region-1" }, CancellationToken.None));
    }

    [Fact]
    public async Task FakeHost_ReturnsTheRegisteredProjection_AndNullForUnknownPages()
    {
        var fake = new FakeHostController(FakeHostController.ReadySnapshot("book"));
        var projection = Projection("page-1");
        fake.RegionTextsByPage["page-1"] = projection;

        Assert.Same(projection, await fake.ListPageRegionTextsAsync("page-1", cancellationToken: CancellationToken.None));
        Assert.Null(await fake.ListPageRegionTextsAsync("page-404", cancellationToken: CancellationToken.None));
    }

    [Fact]
    public async Task FakeHost_RecordsEveryProjectionCallIncludingTheFilter()
    {
        var fake = new FakeHostController(FakeHostController.ReadySnapshot("book"));

        await fake.ListPageRegionTextsAsync("page-1", cancellationToken: CancellationToken.None);
        await fake.ListPageRegionTextsAsync("page-1", new[] { "region-2", "region-1" }, CancellationToken.None);

        Assert.Equal(2, fake.RegionTextCalls.Count);
        Assert.Equal("page-1", fake.RegionTextCalls[0].PageId);
        Assert.Null(fake.RegionTextCalls[0].RegionIds);
        Assert.Equal(new[] { "region-2", "region-1" }, fake.RegionTextCalls[1].RegionIds);
    }

    [Fact]
    public async Task UnstartedHostController_DegradesToNull()
    {
        await using var controller = new HostController(Options());

        Assert.Null(await controller.ListPageRegionTextsAsync("page-1", cancellationToken: CancellationToken.None));
        Assert.Null(await controller.ListPageRegionTextsAsync(
            "page-1", new[] { "region-1" }, CancellationToken.None));
    }

    [Fact]
    public async Task HostControllerWithUnavailableSidecar_DegradesToNull_WithoutLeakingTheReason()
    {
        // The sidecar directory does not exist, so the runtime never becomes ready. The read must
        // answer null instead of throwing a typed Core/sidecar failure into the UI thread.
        await using var controller = new HostController(Options());
        await controller.StartAsync();

        Assert.Null(await controller.ListPageRegionTextsAsync("page-1", cancellationToken: CancellationToken.None));
    }

    [Fact]
    public void PortSurface_IsDeclaredOnIHostController_WithTheFrozenRow80Signature()
    {
        var method = typeof(IHostController).GetMethod(nameof(IHostController.ListPageRegionTextsAsync));
        Assert.NotNull(method);
        Assert.Equal(typeof(Task<RegionPageTextProjection>), method.ReturnType);

        var parameters = method.GetParameters();
        Assert.Equal(
            new[] { "pageId", "regionIds", "cancellationToken" },
            parameters.Select(parameter => parameter.Name).ToArray());
        Assert.Equal(typeof(string), parameters[0].ParameterType);
        Assert.False(parameters[0].IsOptional);
        Assert.Equal(typeof(IReadOnlyList<string>), parameters[1].ParameterType);
        Assert.True(parameters[1].IsOptional);
        Assert.True(parameters[1].HasDefaultValue);
        Assert.Null(parameters[1].DefaultValue);
        Assert.Equal(typeof(CancellationToken), parameters[2].ParameterType);
        Assert.True(parameters[2].IsOptional);
        Assert.True(parameters[2].HasDefaultValue);
    }

    [Fact]
    public void PortSurface_ExposesNoRevisionGuard()
    {
        // The Core command has no expected_revision (4A P1-2). A parameter that carried one would
        // widen the pre-authorized C-07 signature and force a second UNFREEZE.
        var method = typeof(IHostController).GetMethod(nameof(IHostController.ListPageRegionTextsAsync));
        Assert.NotNull(method);
        Assert.DoesNotContain(
            method.GetParameters(),
            parameter => parameter.Name!.Contains("revision", StringComparison.OrdinalIgnoreCase));
    }

    private static RegionPageTextProjection Projection(string pageId) => new(
        pageId,
        1000,
        1500,
        new[]
        {
            new RegionTextDetail(
                "region-1",
                pageId,
                "speech",
                "skip",
                1,
                null,
                new RegionFourTrackText("原文テキスト", "机翻", "人工译文", "人工译文", "edited", true, true, false),
                new RegionLockProjection(false, false, false),
                "confirmed",
                "user",
                4,
                "rev-4",
                false,
                Array.Empty<int>(),
                "2026-01-01T00:00:00.000+00:00",
                "2026-01-01T00:00:01.000+00:00"),
        });

    private static HostOptions Options() => new()
    {
        DataRoot = Path.Combine(Path.GetTempPath(), "newmanga-4b-unit-" + Guid.NewGuid().ToString("N")[..8]),
        LogDirectory = Path.Combine(Path.GetTempPath(), "newmanga-4b-unit-logs-" + Guid.NewGuid().ToString("N")[..8]),
        MutexName = @"Local\NewManga.App.Tests.4B." + Guid.NewGuid().ToString("N")[..10],
        SidecarDirectoryOverride = Path.Combine(Path.GetTempPath(), "newmanga-4b-missing-sidecar"),
        DetectLegacyShell = false,
    };
}
