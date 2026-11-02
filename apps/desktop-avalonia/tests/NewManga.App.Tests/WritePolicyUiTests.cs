using NewManga.App;
using NewManga.App.Services;
using NewManga.Host;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-A-5 (P0 write policy): the shipped GUI starts writable by default; the only read-only
/// downgrades are the legacy Tauri shell, the explicit <c>--parity=false</c> switch, or a Host that is
/// not ready/failed. The UI must also receive an explicit reason when writes are refused.
/// </summary>
public sealed class AppOptionsWritePolicyTests
{
    [Fact]
    public void DefaultParse_IsWritable_AndPassesThroughToHostOptions()
    {
        var options = AppOptions.Parse(Array.Empty<string>());

        Assert.True(options.ParityReached);
        Assert.False(options.DemoWrite);
        Assert.Null(options.InvalidReason);
        Assert.True(options.ToHostOptions().ParityReached);
    }

    [Fact]
    public void ParityFalse_ForcesReadOnly()
    {
        var options = AppOptions.Parse(new[] { "--parity=false" });

        Assert.False(options.ParityReached);
        Assert.False(options.ToHostOptions().ParityReached);
    }

    [Fact]
    public void DemoWrite_StillRequiresAnIsolatedDataRoot()
    {
        var withoutRoot = AppOptions.Parse(new[] { "--demo-write" });
        Assert.NotNull(withoutRoot.InvalidReason);

        var isolated = Path.Combine(Path.GetTempPath(), "newmanga-a5-demo-" + Guid.NewGuid().ToString("N")[..8]);
        var withRoot = AppOptions.Parse(new[] { "--demo-write", "--data-root=" + isolated });
        Assert.Null(withRoot.InvalidReason);
        Assert.True(withRoot.ParityReached);
    }
}

/// <summary>
/// V11R-A-5 AC1/AC2 integration: the real controller with the shipped default (no parity flag) is
/// writable and can create a book; <c>--parity=false</c> keeps the write gate closed with a typed
/// refusal and an explicit UI-readable reason. Self-skips without the AC11 sidecar copy.
/// </summary>
public sealed class WritePolicyUiIntegrationTests
{
    [WritePolicySidecarFact]
    public async Task DefaultController_IsWritable_AndParityFalse_IsReadOnlyWithReason()
    {
        var sidecar = RunFixture.TryGetSidecarDirectory(out var directory, out _) ? directory : string.Empty;
        Assert.False(string.IsNullOrEmpty(sidecar));

        var dataRoot = Path.Combine(Path.GetTempPath(), "newmanga-a5-ui-" + Guid.NewGuid().ToString("N")[..10]);
        var logDirectory = Path.Combine(Path.GetTempPath(), "newmanga-a5-ui-logs-" + Guid.NewGuid().ToString("N")[..10]);
        var readOnlyRoot = dataRoot + "-readonly";
        var readOnlyLogs = logDirectory + "-readonly";
        try
        {
            var writableOptions = AppOptions.Parse(new[]
            {
                "--data-root=" + dataRoot,
                "--log-dir=" + logDirectory,
                "--sidecar-dir=" + sidecar,
                "--mutex-name=Local\\NewManga.App.Tests.A5.Write." + Guid.NewGuid().ToString("N")[..10],
                "--legacy-shell-check=off",
            });
            Assert.Null(writableOptions.InvalidReason);
            Assert.True(writableOptions.ParityReached);

            await using (var controller = new HostController(writableOptions.ToHostOptions()))
            {
                await controller.StartAsync();
                Assert.True(
                    controller.Snapshot.State == HostViewState.Ready,
                    $"{controller.Snapshot.ErrorCode}: {controller.Snapshot.ErrorMessage}");

                // AC1: shipped default → writable, and a real create-book write succeeds.
                Assert.True(controller.Snapshot.WritesAllowed);
                Assert.Contains("读写就绪", controller.Snapshot.ModeLine, StringComparison.Ordinal);
                Assert.Null(controller.Snapshot.ReadOnlyReason);
                Assert.True(await controller.TryCreateBookAsync("V11R-A-5 默认 GUI 可写"));
                Assert.Contains(controller.Snapshot.Books, book => book.Title == "V11R-A-5 默认 GUI 可写");
            }

            var readOnlyOptions = AppOptions.Parse(new[]
            {
                "--data-root=" + readOnlyRoot,
                "--log-dir=" + readOnlyLogs,
                "--sidecar-dir=" + sidecar,
                "--mutex-name=Local\\NewManga.App.Tests.A5.ReadOnly." + Guid.NewGuid().ToString("N")[..10],
                "--legacy-shell-check=off",
                "--parity=false",
            });
            Assert.False(readOnlyOptions.ParityReached);

            await using (var controller = new HostController(readOnlyOptions.ToHostOptions()))
            {
                await controller.StartAsync();
                Assert.True(
                    controller.Snapshot.State == HostViewState.Ready,
                    $"{controller.Snapshot.ErrorCode}: {controller.Snapshot.ErrorMessage}");

                // AC2: explicit --parity=false → read-only + typed refusal + explicit reason.
                Assert.False(controller.Snapshot.WritesAllowed);
                Assert.Contains("只读", controller.Snapshot.ModeLine, StringComparison.Ordinal);
                Assert.False(string.IsNullOrWhiteSpace(controller.Snapshot.ReadOnlyReason));
                Assert.False(await controller.TryCreateBookAsync("V11R-A-5 只读 GUI 写入"));

                var chapter = await controller.CreateChapterAsync("book-id", "第 1 章");
                Assert.Null(chapter);
                Assert.Equal("HOST_READ_ONLY", controller.Snapshot.LastError);
            }
        }
        finally
        {
            RunFixture.TryDeleteDirectory(dataRoot);
            RunFixture.TryDeleteDirectory(logDirectory);
            RunFixture.TryDeleteDirectory(readOnlyRoot);
            RunFixture.TryDeleteDirectory(readOnlyLogs);
        }
    }
}

/// <summary>V11R-A-5: integration fact requiring the AC11 sidecar copy only.</summary>
public sealed class WritePolicySidecarFactAttribute : FactAttribute
{
    public WritePolicySidecarFactAttribute()
    {
        if (!RunFixture.TryGetSidecarDirectory(out _, out var reason))
        {
            Skip = reason;
        }
    }
}
