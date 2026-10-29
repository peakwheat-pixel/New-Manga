using NewManga.App;
using NewManga.App.Services;
using NewManga.CoreClient;
using NewManga.Host;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-A-6 UI surface: when the startup self check fails, the snapshot must expose the closed write
/// gate, the typed error code and the read-only reason so the shell can tell the user why.
/// </summary>
public sealed class StartupSelfCheckUiTests
{
    [WritePolicySidecarFact]
    public async Task SelfCheckFailure_IsVisibleInTheSnapshot()
    {
        var sidecar = RunFixture.TryGetSidecarDirectory(out var directory, out _) ? directory : string.Empty;
        Assert.False(string.IsNullOrEmpty(sidecar));

        var dataRoot = Path.Combine(Path.GetTempPath(), "newmanga-a6-ui-" + Guid.NewGuid().ToString("N")[..10]);
        var logDirectory = Path.Combine(Path.GetTempPath(), "newmanga-a6-ui-logs-" + Guid.NewGuid().ToString("N")[..10]);
        try
        {
            var options = AppOptions.Parse(new[]
            {
                "--data-root=" + dataRoot,
                "--log-dir=" + logDirectory,
                "--sidecar-dir=" + sidecar,
                "--mutex-name=Local\\NewManga.App.Tests.A6." + Guid.NewGuid().ToString("N")[..10],
                "--legacy-shell-check=off",
            });
            Assert.Null(options.InvalidReason);

            var hostOptions = options.ToHostOptions();
            hostOptions = new HostOptions
            {
                DataRoot = hostOptions.DataRoot,
                LogDirectory = hostOptions.LogDirectory,
                SidecarDirectoryOverride = hostOptions.SidecarDirectoryOverride,
                MutexName = hostOptions.MutexName,
                ParityReached = hostOptions.ParityReached,
                DetectLegacyShell = hostOptions.DetectLegacyShell,
                EnableWireEvidence = hostOptions.EnableWireEvidence,
                // Simulated contract drift: the Core reports a different protocol major.
                StartupPingProbe = _ => Task.FromResult(
                    new CorePing(true, 3, StartupSelfCheck.RequiredProtocolMinor, "ready", new[] { StartupSelfCheck.RequiredCapability })),
            };

            await using var controller = new HostController(hostOptions);
            await controller.StartAsync();

            Assert.Equal(HostViewState.Ready, controller.Snapshot.State);
            Assert.False(controller.Snapshot.WritesAllowed);
            Assert.Equal("PROTOCOL_VERSION_MISMATCH", controller.Snapshot.ErrorCode);
            Assert.Contains("只读（启动自检失败）", controller.Snapshot.ModeLine, StringComparison.Ordinal);
            Assert.False(string.IsNullOrWhiteSpace(controller.Snapshot.ReadOnlyReason));
            Assert.False(await controller.TryCreateBookAsync("V11R-A-6 UI 只读夹具"));
        }
        finally
        {
            RunFixture.TryDeleteDirectory(dataRoot);
            RunFixture.TryDeleteDirectory(logDirectory);
        }
    }
}
