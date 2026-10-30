using NewManga.App.Services;
using NewManga.Host;

namespace NewManga.App.Tests;

/// <summary>
/// REALUSE-DATA-SAFETY-2 review r1 (MUST FIX 1): a failed start still owns the Win32
/// single-instance mutex. <c>HostRuntime.StartAsync</c> returns the runtime on failure (its catch
/// blocks set <c>Result = Failed</c> and stop sidecars, but never release <c>_guard</c>), so the
/// retry path added for audit MA-04 must dispose the stale instance. Without that, the second
/// attempt cannot acquire the mutex and reports <c>AlreadyRunning</c> forever — "retry" would lie.
/// </summary>
public sealed class HostControllerRetryTests
{
    [Fact]
    public async Task FailedStart_IsRetryable_AndTheSecondAttemptIsNotAlreadyRunning()
    {
        var dataRoot = Path.Combine(Path.GetTempPath(), "nm-retry-" + Guid.NewGuid().ToString("N")[..10]);
        var logDirectory = Path.Combine(Path.GetTempPath(), "nm-retry-logs-" + Guid.NewGuid().ToString("N")[..10]);
        var mutexName = @"Local\NewManga.App.Tests.Retry." + Guid.NewGuid().ToString("N")[..12];

        try
        {
            var options = new HostOptions
            {
                DataRoot = dataRoot,
                LogDirectory = logDirectory,
                // Pointing at a missing directory makes the first attempt fail AFTER the
                // single-instance mutex was acquired — the exact leak the review reported.
                SidecarDirectoryOverride = Path.Combine(dataRoot, "no-such-sidecar"),
                MutexName = mutexName,
                DetectLegacyShell = false,
                StartupTimeout = TimeSpan.FromSeconds(20),
                RequestTimeout = TimeSpan.FromSeconds(20),
            };

            await using var controller = new HostController(options);

            await controller.StartAsync();
            Assert.Equal(HostViewState.Failed, controller.Snapshot.State);
            var firstCode = controller.Snapshot.ErrorCode;
            Assert.False(string.IsNullOrEmpty(firstCode), "the first attempt must publish a typed code");

            // Retry must be a real second attempt that fails the same way, not AlreadyRunning.
            await controller.StartAsync();

            Assert.NotEqual(HostViewState.AlreadyRunning, controller.Snapshot.State);
            Assert.Equal(HostViewState.Failed, controller.Snapshot.State);
            Assert.Equal(firstCode, controller.Snapshot.ErrorCode);
            Assert.Equal(2, controller.StartRequests);
        }
        finally
        {
            RunFixture.TryDeleteDirectory(dataRoot);
            RunFixture.TryDeleteDirectory(logDirectory);
        }
    }
}
