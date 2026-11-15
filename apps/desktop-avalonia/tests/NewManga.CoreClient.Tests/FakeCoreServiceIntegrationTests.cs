using System.Diagnostics;
using System.Text;
using NewManga.CoreClient;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Wire;
using Xunit;

namespace NewManga.CoreClient.Tests;

/// <summary>
/// Drives the <b>real production call chain</b> (<c>CoreServiceClient.StartAsync</c> → <c>SendAsync</c>)
/// against a fake core_service that speaks enough of the wire protocol to complete the <c>core.ping</c>
/// handshake. This closes two long-standing evidence gaps at once:
///
/// <list type="bullet">
///   <item><b>E-7 #2 / 裁决 §5.3</b>: prove dynamically that the production command paths really use the
///   strict id judgement (<c>ReadResponseForRequestAsync</c>), not just the helper in isolation.</item>
///   <item><b>R002-RESYNC-1 / P2-F1</b>: the resync tests only called the internal helper directly, so a
///   call site could regress back to a direct judgement without any test failing.</item>
/// </list>
///
/// <para>The fake sidecar is an inline Python script written to a temp file at test time (so the test
/// project needs no .csproj changes and no committed fixture binary). The scenario is passed as the
/// script's first <b>command-line argument</b> -- <c>CoreServiceOptions</c> exposes no environment map,
/// so an env-var based scenario is not possible here.</para>
/// </summary>
public sealed class FakeCoreServiceIntegrationTests
{
    private const string FakeCoreScript = """
import json
import os
import sys

scenario = sys.argv[1] if len(sys.argv) > 1 else "plain"

def emit(obj):
    sys.stdout.write(json.dumps(obj, separators=(",", ":")) + "\n")
    sys.stdout.flush()

for raw in sys.stdin:
    raw = raw.strip()
    if not raw:
        continue
    try:
        req = json.loads(raw)
    except Exception:
        continue

    rid = req.get("request_id")
    cmd = req.get("command") or ""

    if cmd == "core.ping":
        emit({
            "request_id": rid,
            "result": {
                "status": "ready",
                "protocol_version": {"major": 2, "minor": 3},
                "capabilities": [],
            },
            "error": None,
        })
        continue

    if scenario == "mismatch-then-match":
        # First a frame that belongs to someone else (proves the production path resynchronises),
        # then the genuinely matching one.
        emit({"request_id": "req-999999", "result": {"stolen": True}, "error": None})
        emit({"request_id": rid, "result": {"ok": True}, "error": None})
        continue

    if scenario == "missing-then-match":
        # A frame with NO request_id (E-7 #2 fail-closed: must be discarded, not accepted).
        emit({"result": {"unattributed": True}, "error": None})
        emit({"request_id": rid, "result": {"ok": True}, "error": None})
        continue

    if scenario == "idless-only":
        # Only unattributable frames: fail-closed must poison instead of handing one over.
        for _ in range(40):
            emit({"result": {"unattributed": True}, "error": None})
        continue

    emit({"request_id": rid, "result": {"ok": True}, "error": None})
""";

    [Fact]
    public async Task ProductionSendAsync_ResynchronisesWhenFirstFrameBelongsToAnotherRequest()
    {
        using var fake = FakeCore.Start("mismatch-then-match");
        await using var client = await CoreServiceClient.StartAsync(fake.Options());

        var response = await client.SendAsync(
            "TestCommand",
            CoreProtocol.DefaultMinor,
            WireJson.EmptyObject,
            TimeSpan.FromSeconds(10));

        // The mismatched frame must be DISCARDED; the caller gets the frame that actually carries its id.
        Assert.Equal("{\"ok\":true}", response.Result?.GetRawText());
    }

    [Fact]
    public async Task ProductionSendAsync_DiscardsIdlessFrame_ThenSucceedsOnTheMatchingOne()
    {
        using var fake = FakeCore.Start("missing-then-match");
        await using var client = await CoreServiceClient.StartAsync(fake.Options());

        var response = await client.SendAsync(
            "TestCommand",
            CoreProtocol.DefaultMinor,
            WireJson.EmptyObject,
            TimeSpan.FromSeconds(10));

        Assert.Equal("{\"ok\":true}", response.Result?.GetRawText());
    }

    [Fact]
    public async Task ProductionSendAsync_PoisonsChannel_WhenOnlyIdlessFramesArrive()
    {
        using var fake = FakeCore.Start("idless-only");
        await using var client = await CoreServiceClient.StartAsync(fake.Options());

        var failure = await Assert.ThrowsAsync<SidecarException>(() =>
            client.SendAsync(
                "TestCommand",
                CoreProtocol.DefaultMinor,
                WireJson.EmptyObject,
                TimeSpan.FromSeconds(10)));

        Assert.Equal(SidecarErrorCode.MalformedResponse, failure.Code);
        Assert.Contains("resynchronised", failure.Message, StringComparison.OrdinalIgnoreCase);

        // Fail-closed: the channel is now poisoned, so the next command must fail immediately rather
        // than quietly reading whatever is left on the wire.
        //
        // r1 P1: asserting only on the substring "poisoned" was a surviving mutant — BOTH the
        // "channel poisoned" path (ThrowIfPoisoned → RequestTimeout) and the "out of step, channel
        // poisoned" resync-exhausted path (MalformedResponse) contain that word, so deleting the whole
        // poison hook kept this test green. Assert the CODE (which distinguishes the two paths) and that
        // the failure is immediate (no resync attempt, hence RequestTimeout rather than MalformedResponse).
        var next = await Assert.ThrowsAsync<SidecarException>(() =>
            client.SendAsync(
                "TestCommand",
                CoreProtocol.DefaultMinor,
                WireJson.EmptyObject,
                TimeSpan.FromSeconds(5)));

        Assert.Equal(SidecarErrorCode.RequestTimeout, next.Code);
        Assert.Contains("restart required", next.Message, StringComparison.OrdinalIgnoreCase);
    }

    /// <summary>
    /// r1 P2: the Codex ruling (§5.3) names BOTH command paths. The three tests above exercise
    /// <see cref="CoreServiceClient.SendAsync"/>; this one proves the second call site
    /// (<c>SendHostControlAsync</c>) resynchronises too.
    /// </summary>
    /// <remarks>
    /// <c>SendHostControlAsync</c> already writes <c>"payload": {</c> and the closing brace itself, so its
    /// <c>payload</c> delegate must write <b>members only</b>. Passing <c>WireJson.EmptyObject</c> (which
    /// opens its own object) raised "Cannot write the start of an object without a property name" -- hence
    /// the no-op delegate below.
    /// </remarks>
    [Fact]
    public async Task ProductionSendHostControlAsync_AlsoResynchronises()
    {
        using var fake = FakeCore.Start("mismatch-then-match");
        await using var client = await CoreServiceClient.StartAsync(fake.Options());

        var response = await client.SendHostControlAsync(
            "TestHostControl",
            static _ => { },
            TimeSpan.FromSeconds(10),
            session: null);

        Assert.Equal("{\"ok\":true}", response.Result?.GetRawText());
    }

    /// <summary>Inline-Python fake core_service: writes the script, starts it, exposes client options.</summary>
    private sealed class FakeCore : IDisposable
    {
        private readonly string _scriptPath;
        private readonly string _stderrPath;

        private FakeCore(string scriptPath, string scenario, string stderrPath)
        {
            _scriptPath = scriptPath;
            Scenario = scenario;
            _stderrPath = stderrPath;
        }

        public string Scenario { get; }

        public static FakeCore Start(string scenario)
        {
            var dir = Path.Combine(Path.GetTempPath(), "newmanga-fake-core-" + Guid.NewGuid().ToString("N")[..8]);
            Directory.CreateDirectory(dir);
            var scriptPath = Path.Combine(dir, "fake_core.py");
            File.WriteAllText(scriptPath, FakeCoreScript, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
            return new FakeCore(scriptPath, scenario, Path.Combine(dir, "fake-core.stderr.log"));
        }

        public CoreServiceOptions Options()
        {
            var root = Path.GetDirectoryName(_scriptPath)!;
            var dataRoot = Path.Combine(root, "data");
            Directory.CreateDirectory(dataRoot);
            return new CoreServiceOptions
            {
                ExecutablePath = PythonPath(),
                AdditionalArguments = new[] { "-u", _scriptPath, Scenario },
                DataRoot = dataRoot,
                DerivedRoot = Path.Combine(dataRoot, "derived"),
                CatalogDbPath = Path.Combine(dataRoot, "catalog.sqlite"),
                StderrLogPath = _stderrPath,
                StartupTimeout = TimeSpan.FromSeconds(20),
                RequestTimeout = TimeSpan.FromSeconds(10),
            };
        }

        private static string PythonPath()
        {
            // SidecarProcess validates with File.Exists, so an absolute path is required -- "python" alone
            // is rejected as SidecarExeMissing. Resolve the interpreter via where on Windows.
            var overridePath = Environment.GetEnvironmentVariable("NEWMANGA_TEST_PYTHON");
            if (!string.IsNullOrWhiteSpace(overridePath))
            {
                return overridePath;
            }

            var startInfo = new ProcessStartInfo("where.exe", "python")
            {
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true,
            };
            using var where = Process.Start(startInfo);
            if (where is not null)
            {
                var first = where.StandardOutput.ReadLine();
                where.WaitForExit(5000);
                if (!string.IsNullOrWhiteSpace(first) && File.Exists(first.Trim()))
                {
                    return first.Trim();
                }
            }

            throw new InvalidOperationException(
                "python interpreter not found on PATH; set NEWMANGA_TEST_PYTHON to an absolute path");
        }

        public void Dispose()
        {
            try
            {
                Directory.Delete(Path.GetDirectoryName(_scriptPath)!, recursive: true);
            }
            catch (IOException)
            {
                // best effort
            }
            catch (UnauthorizedAccessException)
            {
                // best effort
            }
        }
    }
}
