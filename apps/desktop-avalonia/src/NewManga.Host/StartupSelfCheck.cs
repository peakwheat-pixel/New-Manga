using NewManga.CoreClient;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Wire;

namespace NewManga.Host;

/// <summary>V11R-A-6: outcome of the Host startup contract self check.</summary>
public enum SelfCheckStatus
{
    /// <summary>No self check has run yet (host not started).</summary>
    NotRun,

    /// <summary>All cheap checks passed and the full command surface was compared.</summary>
    Passed,

    /// <summary>Cheap checks passed but coverage is partial (diagnostics visible; writes stay enabled).</summary>
    Degraded,

    /// <summary>The Core does not match the Host contract: writes are closed and a typed error is published.</summary>
    Failed,
}

/// <summary>
/// V11R-A-6 result. <see cref="ErrorCode"/> is typed (<c>PROTOCOL_VERSION_MISMATCH</c>,
/// <c>CORE_PROTOCOL_MINOR_TOO_OLD</c>, <c>CORE_CAPABILITY_MISSING</c>, <c>CORE_NOT_READY</c>,
/// <c>SELF_CHECK_PROBE_FAILED</c>) and never contains a path or a credential.
/// </summary>
public sealed record StartupSelfCheckResult(
    SelfCheckStatus Status,
    string? ErrorCode,
    string Reason,
    string Detail)
{
    public static StartupSelfCheckResult NotRun { get; } = new(
        SelfCheckStatus.NotRun,
        null,
        "启动自检尚未运行",
        string.Empty);

    /// <summary>True when the mismatch must close the write gate.</summary>
    public bool WritesBlocked => Status == SelfCheckStatus.Failed;
}

/// <summary>
/// V11R-A-6 startup self check (A-5 leftover #1): compare what the running Core actually reports
/// against what the Host contract requires, and close the write gate on a mismatch instead of
/// letting the first user write fail mid-journey.
///
/// Coverage boundary: <c>core.ping</c> exposes the protocol version and the capability list, not an
/// enumeration of all 66 commands (probing every command at startup would execute mutating
/// commands). Those two facts are exactly what this cheap check can prove, so passing them yields
/// <see cref="SelfCheckStatus.Passed"/>; the command-surface comparison is owned by the parity
/// tests and the limitation stays in <see cref="StartupSelfCheckResult.Detail"/>.
/// <see cref="SelfCheckStatus.Degraded"/> is reserved for a probe/transport failure, which is a
/// real degradation rather than an untested area (REALUSE-DATA-SAFETY-2 AC3).
/// </summary>
public static class StartupSelfCheck
{
    public const int ExpectedProtocolMajor = 2;

    /// <summary>The single capability <c>core.ping</c> advertises today; a Core without it is unusable.</summary>
    public const string RequiredCapability = "library.list_books";

    /// <summary>
    /// Base protocol minor the Core must advertise. Per-command minors (7/8/10 in
    /// <see cref="HostCommandRegistry"/>) are request-level widening the dispatcher negotiates per
    /// command — they are NOT what <c>core.ping</c> reports — so the startup check only requires the
    /// base minor; command-level minors stay covered by the parity tests.
    /// </summary>
    public static int RequiredProtocolMinor => CoreProtocol.DefaultMinor;

    public static StartupSelfCheckResult Evaluate(CorePing ping)
    {
        if (!ping.Ready)
        {
            return Failed(
                "CORE_NOT_READY",
                "Core 未报告 ready，写入已关闭。",
                $"status={ping.Status}");
        }

        if (ping.ProtocolMajor != ExpectedProtocolMajor)
        {
            return Failed(
                "PROTOCOL_VERSION_MISMATCH",
                $"Core 协议主版本 {ping.ProtocolMajor} 与 Host 期望 {ExpectedProtocolMajor} 不一致，写入已关闭。",
                $"core_protocol={ping.ProtocolMajor}.{ping.ProtocolMinor}");
        }

        var requiredMinor = RequiredProtocolMinor;
        if (ping.ProtocolMinor < requiredMinor)
        {
            return Failed(
                "CORE_PROTOCOL_MINOR_TOO_OLD",
                $"Core 协议 minor {ping.ProtocolMinor} 低于注册表要求 {requiredMinor}，写入已关闭。",
                $"core_protocol={ping.ProtocolMajor}.{ping.ProtocolMinor} required_minor={requiredMinor}");
        }

        if (!ping.Capabilities.Contains(RequiredCapability, StringComparer.Ordinal))
        {
            return Failed(
                "CORE_CAPABILITY_MISSING",
                $"Core 未声明能力 {RequiredCapability}，写入已关闭。",
                $"capabilities=[{string.Join(",", ping.Capabilities)}]");
        }

        // REALUSE-DATA-SAFETY-2 AC3: every check this probe can perform has passed, so the honest
        // result is Passed. The audit (MA-05) flagged the old unconditional Degraded: twelve of
        // twelve real starts reported "degraded" while nothing was wrong, and the App never consumed
        // the value, so the word carried no information. What core.ping cannot express (an
        // enumeration of all 66 commands) is a coverage boundary owned by the parity tests, not a
        // runtime degradation; it stays in Detail so the limitation is still visible.
        return new StartupSelfCheckResult(
            SelfCheckStatus.Passed,
            null,
            "启动自检通过：协议版本与能力集符合 Host 契约（命令面逐条比对由 parity 测试覆盖）。",
            $"core_protocol={ping.ProtocolMajor}.{ping.ProtocolMinor} required_minor={requiredMinor} " +
            $"capabilities=[{string.Join(",", ping.Capabilities)}]");
    }

    /// <summary>
    /// Runs the check against the live Core (or the injected probe). A probe/transport failure is a
    /// <see cref="SelfCheckStatus.Degraded"/> result with a typed diagnostic — never a silent pass —
    /// and per the V11R-A-6 ruling keeps the host writable because the Core handshake already
    /// succeeded during startup; the failure is logged and visible on <see cref="HostRuntime.SelfCheck"/>.
    /// </summary>
    public static async Task<StartupSelfCheckResult> RunAsync(
        HostOptions options,
        CoreServiceClient core,
        CancellationToken cancellationToken)
    {
        CorePing ping;
        try
        {
            ping = options.StartupPingProbe is { } probe
                ? await probe(cancellationToken).ConfigureAwait(false)
                : await core.PingAsync(cancellationToken).ConfigureAwait(false);
        }
        catch (Exception ex) when (ex is SidecarException or CoreOperationException or OperationCanceledException)
        {
            return new StartupSelfCheckResult(
                SelfCheckStatus.Degraded,
                "SELF_CHECK_PROBE_FAILED",
                "启动自检探测失败（保持可写，已记录降级状态；诊断见 host.log）。",
                $"{ex.GetType().Name}: {ex.Message}");
        }

        return Evaluate(ping);
    }

    private static StartupSelfCheckResult Failed(string code, string reason, string detail) =>
        new(SelfCheckStatus.Failed, code, reason, detail);
}
