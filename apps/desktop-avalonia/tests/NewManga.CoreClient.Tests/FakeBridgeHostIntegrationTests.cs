using System.Diagnostics;
using NewManga.CoreClient;
using NewManga.CoreClient.Bridge;
using NewManga.CoreClient.Diagnostics;
using Xunit;

namespace NewManga.CoreClient.Tests;

/// <summary>
/// Drives the REAL production bridge call chain (<c>HostBridgeClient.StartAsync</c> handshake →
/// public <c>SendAsync</c>) against the test-only <c>FakeBridgeHost</c> console app.
///
/// <para>Why a separate .exe instead of the inline-python trick used on the core side:
/// <c>HostBridgeOptions</c> exposes no <c>AdditionalArguments</c> and <c>SidecarProcess</c> runs with
/// <c>UseShellExecute=false</c>, so neither "python + script arg" nor a <c>.cmd</c> wrapper can work.
/// See <c>doc/reviews/BRIDGE-FAKE-HARNESS-DESIGN-2026-11-16.md</c>.</para>
///
/// <para>This closes the gap that <c>BRIDGE-ID-FAILCLOSED-1</c> recorded: the parser had tests, but the
/// production call site's <c>_process.Poison()</c> had NONE — deleting it left every test green
/// (mutation-verified by r1).</para>
/// </summary>
public sealed class FakeBridgeHostIntegrationTests
{
    [Fact]
    public async Task HandshakeSucceeds_AndSubsequentPingAlsoRoundTrips()
    {
        using var fake = FakeBridge.Start("plain");
        await using var bridge = await HostBridgeClient.StartAsync(fake.Options());

        // StartAsync already pinged once; a second round trip proves the process stays usable.
        Assert.True(await bridge.PingAsync());
    }

    /// <summary>
    /// BRIDGE-ID-FAILCLOSED-1 F-01: the production call site must POISON the channel when it sees an
    /// unattributable frame. Asserted by CODE, not by the word "poisoned":
    /// first call → MalformedResponse (parser verdict); second call → RequestTimeout (poisoned fast path,
    /// i.e. it never reached the parser again). Deleting <c>_process.Poison()</c> makes the second code
    /// MalformedResponse again, so this test must go red.
    /// </summary>
    [Fact]
    public async Task SendAsync_PoisonsChannel_WhenResponseOmitsId()
    {
        using var fake = FakeBridge.Start("missing-then-match");
        await using var bridge = await HostBridgeClient.StartAsync(fake.Options());

        var first = await Assert.ThrowsAsync<SidecarException>(() =>
            bridge.IssueAsync("res-1", "fp-1"));

        Assert.Equal(SidecarErrorCode.MalformedResponse, first.Code);
        Assert.Contains("missing id", first.Message, StringComparison.Ordinal);

        var second = await Assert.ThrowsAsync<SidecarException>(() =>
            bridge.IssueAsync("res-1", "fp-1"));

        Assert.Equal(SidecarErrorCode.RequestTimeout, second.Code);
        Assert.Contains("restart required", second.Message, StringComparison.OrdinalIgnoreCase);
    }

    /// <summary>Same wiring, different unattributable shape: a well-formed but WRONG id.</summary>
    [Fact]
    public async Task SendAsync_PoisonsChannel_WhenResponseIdIsMismatched()
    {
        using var fake = FakeBridge.Start("mismatch-then-match");
        await using var bridge = await HostBridgeClient.StartAsync(fake.Options());

        var first = await Assert.ThrowsAsync<SidecarException>(() =>
            bridge.IssueAsync("res-1", "fp-1"));

        Assert.Equal(SidecarErrorCode.MalformedResponse, first.Code);
        Assert.Contains("does not match", first.Message, StringComparison.Ordinal);

        var second = await Assert.ThrowsAsync<SidecarException>(() =>
            bridge.IssueAsync("res-1", "fp-1"));

        Assert.Equal(SidecarErrorCode.RequestTimeout, second.Code);
    }

    /// <summary>Locates the FakeBridgeHost.exe that the ProjectReference drops next to the test assembly.</summary>
    private sealed class FakeBridge : IDisposable
    {
        private readonly string _root;

        private FakeBridge(string root, string scenario)
        {
            _root = root;
            Scenario = scenario;
        }

        public string Scenario { get; }

        public static FakeBridge Start(string scenario)
        {
            var root = Path.Combine(Path.GetTempPath(), "newmanga-fake-bridge-" + Guid.NewGuid().ToString("N")[..8]);
            Directory.CreateDirectory(root);
            return new FakeBridge(root, scenario);
        }

        public HostBridgeOptions Options()
        {
            // Scenario is encoded in the DerivedRoot path: HostBridgeClient forwards that env var to the
            // child, and HostBridgeOptions has no argument/environment passthrough of its own.
            var derived = Path.Combine(_root, "derived", "scenario-" + Scenario);
            var managed = Path.Combine(_root, "managed");
            Directory.CreateDirectory(derived);
            Directory.CreateDirectory(managed);
            return new HostBridgeOptions
            {
                ExecutablePath = ExecutablePath(),
                DerivedRoot = derived,
                ManagedRoot = managed,
                CatalogDbPath = Path.Combine(_root, "catalog.sqlite"),
                StderrLogPath = Path.Combine(_root, "fake-bridge.stderr.log"),
                StartupTimeout = TimeSpan.FromSeconds(20),
                RequestTimeout = TimeSpan.FromSeconds(10),
            };
        }

        private static string ExecutablePath()
        {
            var beside = Path.Combine(AppContext.BaseDirectory, "FakeBridgeHost.exe");
            if (File.Exists(beside))
            {
                return beside;
            }

            throw new InvalidOperationException(
                $"FakeBridgeHost.exe not found next to the test assembly ({beside}); "
                + "the FakeBridgeHost ProjectReference did not copy its output.");
        }

        public void Dispose()
        {
            try
            {
                Directory.Delete(_root, recursive: true);
            }
            catch (IOException)
            {
            }
            catch (UnauthorizedAccessException)
            {
            }
        }
    }
}
