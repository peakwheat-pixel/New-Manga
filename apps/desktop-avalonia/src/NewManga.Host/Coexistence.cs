namespace NewManga.Host;

/// <summary>Host operating modes for the migration window (ADR-0001 D3/D4).</summary>
public enum HostMode
{
    /// <summary>Writes allowed (only after S2 parity and with no legacy shell running).</summary>
    ReadWrite,

    /// <summary>S2 parity not reached: production data is read-only (S1 default).</summary>
    ReadOnlyUntilParity,

    /// <summary>Legacy Tauri shell is running: read-only + notice (chosen AC5 policy).</summary>
    ReadOnlyLegacyShellRunning,

    /// <summary>V11R-A-6: the startup contract self check failed (Core/Host mismatch): read-only.</summary>
    ReadOnlySelfCheckFailed,
}

public sealed record CoexistenceDecision(HostMode Mode, string Reason);

/// <summary>
/// Pure coexistence rules, unit tested without spawning anything. AC5 asks for one of two
/// behaviours while the legacy shell runs; this codebase chooses "start in read-only mode + tell
/// the user", never "kill the legacy shell" or "double write".
/// </summary>
public static class CoexistenceRules
{
    public static CoexistenceDecision Decide(bool legacyShellRunning, bool parityReached)
    {
        if (legacyShellRunning)
        {
            return new CoexistenceDecision(
                HostMode.ReadOnlyLegacyShellRunning,
                "legacy Tauri shell (new-manga.exe) is running; new host starts read-only and shows a notice");
        }

        if (!parityReached)
        {
            return new CoexistenceDecision(
                HostMode.ReadOnlyUntilParity,
                "S2 command parity not reached; production data stays read-only");
        }

        return new CoexistenceDecision(HostMode.ReadWrite, "parity reached and no legacy shell running");
    }

    public static string Describe(HostMode mode) => mode switch
    {
        HostMode.ReadWrite => "读写就绪",
        HostMode.ReadOnlyUntilParity => "只读（S2 parity 前）",
        HostMode.ReadOnlyLegacyShellRunning => "只读（旧壳运行中）",
        HostMode.ReadOnlySelfCheckFailed => "只读（启动自检失败）",
        _ => mode.ToString(),
    };
}
