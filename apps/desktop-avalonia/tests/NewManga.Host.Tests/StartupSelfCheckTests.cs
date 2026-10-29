using NewManga.CoreClient;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Wire;
using NewManga.Host.Tests.Support;

namespace NewManga.Host.Tests;

/// <summary>
/// V11R-A-6 startup contract self check: a Core/Host contract mismatch closes the write gate and
/// publishes a typed error instead of failing the first user write. Coverage is honest: core.ping
/// exposes only the protocol version and capabilities, so a passing check is Degraded (diagnostics
/// visible) rather than a fake Passed.
/// </summary>
public sealed class StartupSelfCheckTests
{
    private static CorePing Ping(int major = 2, int minor = -1, params string[] capabilities) =>
        new(
            Ready: true,
            ProtocolMajor: major,
            ProtocolMinor: minor < 0 ? StartupSelfCheck.RequiredProtocolMinor : minor,
            Status: "ready",
            Capabilities: capabilities.Length == 0
                ? new[] { StartupSelfCheck.RequiredCapability }
                : capabilities);

    [Fact]
    public void RequiredMinor_IsTheBaseProtocolMinor()
    {
        Assert.Equal(CoreProtocol.DefaultMinor, StartupSelfCheck.RequiredProtocolMinor);
        Assert.True(StartupSelfCheck.RequiredProtocolMinor >= 3);
        Assert.Equal(2, StartupSelfCheck.ExpectedProtocolMajor);
    }

    [Fact]
    public void MatchingCore_IsDegraded_ButWritesStayOpen()
    {
        var result = StartupSelfCheck.Evaluate(Ping());

        Assert.Equal(SelfCheckStatus.Degraded, result.Status);
        Assert.False(result.WritesBlocked);
        Assert.Null(result.ErrorCode);
        Assert.Contains("follow-up", result.Reason, StringComparison.Ordinal);
    }

    [Fact]
    public void MajorMismatch_BlocksWrites_WithTypedCode()
    {
        var result = StartupSelfCheck.Evaluate(Ping(major: 3));

        Assert.Equal(SelfCheckStatus.Failed, result.Status);
        Assert.True(result.WritesBlocked);
        Assert.Equal("PROTOCOL_VERSION_MISMATCH", result.ErrorCode);
    }

    [Fact]
    public void MinorOlderThanRegistry_BlocksWrites_WithTypedCode()
    {
        var result = StartupSelfCheck.Evaluate(Ping(minor: StartupSelfCheck.RequiredProtocolMinor - 1));

        Assert.Equal(SelfCheckStatus.Failed, result.Status);
        Assert.Equal("CORE_PROTOCOL_MINOR_TOO_OLD", result.ErrorCode);
    }

    [Fact]
    public void MissingCapability_BlocksWrites_WithTypedCode()
    {
        var result = StartupSelfCheck.Evaluate(Ping(capabilities: "settings.get"));

        Assert.Equal(SelfCheckStatus.Failed, result.Status);
        Assert.Equal("CORE_CAPABILITY_MISSING", result.ErrorCode);
    }

    [Fact]
    public void NotReadyCore_BlocksWrites_WithTypedCode()
    {
        var result = StartupSelfCheck.Evaluate(new CorePing(false, 2, StartupSelfCheck.RequiredProtocolMinor, "starting", Array.Empty<string>()));

        Assert.Equal(SelfCheckStatus.Failed, result.Status);
        Assert.Equal("CORE_NOT_READY", result.ErrorCode);
    }

    [Fact]
    public async Task ProbeFailure_IsDegraded_WithTypedDiagnostic_AndKeepsWritesOpen()
    {
        var options = new HostOptions
        {
            DataRoot = Path.Combine(Path.GetTempPath(), "newmanga-a6-unit"),
            LogDirectory = Path.Combine(Path.GetTempPath(), "newmanga-a6-unit-logs"),
            StartupPingProbe = _ => throw new SidecarException(
                SidecarErrorCode.ProcessExited,
                "core_service",
                "probe failed"),
        };

        var result = await StartupSelfCheck.RunAsync(options, core: null!, CancellationToken.None);

        Assert.Equal(SelfCheckStatus.Degraded, result.Status);
        Assert.False(result.WritesBlocked);
        Assert.Equal("SELF_CHECK_PROBE_FAILED", result.ErrorCode);
        Assert.Contains("probe failed", result.Detail, StringComparison.Ordinal);
    }

    [HostSidecarFact]
    public async Task RealHost_PassesCheapChecks_AndStaysWritable()
    {
        var dataRoot = HostFixture.NewDataRoot("self-check-pass");
        var options = new HostOptions
        {
            DataRoot = dataRoot,
            LogDirectory = Path.Combine(HostFixture.EvidenceDirectory, "host-logs", "self-check-pass"),
            SidecarDirectoryOverride = HostFixture.SidecarDirectory,
            MutexName = @"Local\NewManga.Host.Test." + Guid.NewGuid().ToString("N")[..12],
            DetectLegacyShell = false,
            EnableWireEvidence = true,
            StartupTimeout = TimeSpan.FromSeconds(90),
            RequestTimeout = TimeSpan.FromSeconds(90),
        };

        try
        {
            await using var runtime = await HostRuntime.StartAsync(options);
            Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);
            Assert.Equal(SelfCheckStatus.Degraded, runtime.SelfCheck.Status);
            Assert.Equal(HostMode.ReadWrite, runtime.Mode);
            Assert.True(runtime.Policy.WritesAllowed);
            Assert.Null(runtime.Result.ErrorCode);

            var book = await runtime.CreateBookAsync("V11R-A-6 自检通过夹具");
            Assert.False(string.IsNullOrWhiteSpace(book.BookId));

            HostFixture.WriteEvidenceJson("startup-self-check/pass.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("status", runtime.SelfCheck.Status.ToString());
                writer.WriteString("mode", runtime.Mode.ToString());
                writer.WriteBoolean("writes_allowed", runtime.Policy.WritesAllowed);
                writer.WriteString("detail", runtime.SelfCheck.Detail);
                writer.WriteString("created_book_id", book.BookId);
                writer.WriteEndObject();
            });
        }
        finally
        {
            HostFixture.TryDeleteDirectory(dataRoot);
        }
    }

    [HostSidecarFact]
    public async Task MajorMismatch_DowngradesToReadOnly_AndRefusesWrites()
    {
        await AssertMismatchDowngrades(
            "protocol-mismatch",
            new CorePing(true, 3, StartupSelfCheck.RequiredProtocolMinor, "ready", new[] { StartupSelfCheck.RequiredCapability }),
            "PROTOCOL_VERSION_MISMATCH");
    }

    [HostSidecarFact]
    public async Task MissingCapability_DowngradesToReadOnly_AndRefusesWrites()
    {
        await AssertMismatchDowngrades(
            "capability-missing",
            new CorePing(true, 2, StartupSelfCheck.RequiredProtocolMinor, "ready", new[] { "settings.get" }),
            "CORE_CAPABILITY_MISSING");
    }

    private static async Task AssertMismatchDowngrades(string label, CorePing ping, string expectedCode)
    {
        var dataRoot = HostFixture.NewDataRoot("self-check-" + label);
        var options = new HostOptions
        {
            DataRoot = dataRoot,
            LogDirectory = Path.Combine(HostFixture.EvidenceDirectory, "host-logs", "self-check-" + label),
            SidecarDirectoryOverride = HostFixture.SidecarDirectory,
            MutexName = @"Local\NewManga.Host.Test." + Guid.NewGuid().ToString("N")[..12],
            DetectLegacyShell = false,
            EnableWireEvidence = true,
            StartupTimeout = TimeSpan.FromSeconds(90),
            RequestTimeout = TimeSpan.FromSeconds(90),
            StartupPingProbe = _ => Task.FromResult(ping),
        };

        try
        {
            await using var runtime = await HostRuntime.StartAsync(options);

            // The host stays usable read-only (sidecars up) but the write gate is closed with a typed error.
            Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);
            Assert.Equal(SelfCheckStatus.Failed, runtime.SelfCheck.Status);
            Assert.Equal(HostMode.ReadOnlySelfCheckFailed, runtime.Mode);
            Assert.False(runtime.Policy.WritesAllowed);
            Assert.Equal(expectedCode, runtime.Result.ErrorCode);
            Assert.Contains("只读（启动自检失败）", CoexistenceRules.Describe(runtime.Mode), StringComparison.Ordinal);

            var refused = await Assert.ThrowsAsync<ReadOnlyHostException>(
                () => runtime.CreateBookAsync("V11R-A-6 自检失败夹具"));
            Assert.Equal("HOST_READ_ONLY", refused.Code);

            HostFixture.WriteEvidenceJson($"startup-self-check/{label}.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("status", runtime.SelfCheck.Status.ToString());
                writer.WriteString("mode", runtime.Mode.ToString());
                writer.WriteBoolean("writes_allowed", runtime.Policy.WritesAllowed);
                writer.WriteString("typed_error", runtime.Result.ErrorCode);
                writer.WriteString("reason", CoexistenceRules.Describe(runtime.Mode));
                writer.WriteString("refusal_code", refused.Code);
                writer.WriteEndObject();
            });
        }
        finally
        {
            HostFixture.TryDeleteDirectory(dataRoot);
        }
    }
}
