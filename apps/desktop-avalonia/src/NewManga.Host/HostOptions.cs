namespace NewManga.Host;

public enum HostStatus
{
    Ready,
    AlreadyRunning,
    Failed,
}

/// <summary>Outcome of a host start attempt. Failures are values, never thrown crashes.</summary>
public sealed record HostStartResult(
    HostStatus Status,
    HostMode Mode,
    string? ErrorCode,
    string? UserMessage,
    string? StderrLogPath)
{
    public bool IsReady => Status == HostStatus.Ready;

    public static HostStartResult Ready(HostMode mode) => new(HostStatus.Ready, mode, null, null, null);

    public static HostStartResult AlreadyRunning() => new(
        HostStatus.AlreadyRunning,
        HostMode.ReadOnlyUntilParity,
        "HOST_ALREADY_RUNNING",
        "New Manga 已在运行（全局单实例互斥 Global\\NewManga.Host）。",
        null);

    public static HostStartResult Failed(SidecarErrorLike error) => new(
        HostStatus.Failed,
        HostMode.ReadOnlyUntilParity,
        error.Code,
        error.UserMessage,
        error.StderrLogPath);
}

/// <summary>Small abstraction so Host.Runtime can return typed failures without leaking exceptions.</summary>
public readonly record struct SidecarErrorLike(string Code, string UserMessage, string? StderrLogPath);

public sealed class HostOptions
{
    /// <summary>Shared data root (production: %APPDATA%\com.newmanga.desktop; tests: isolated temp).</summary>
    public required string DataRoot { get; init; }

    /// <summary>Host log directory (host.log + per-sidecar stderr + wire NDJSON).</summary>
    public required string LogDirectory { get; init; }

    /// <summary>Explicit sidecar directory (tests/packaging); null uses the AC7 discovery order.</summary>
    public string? SidecarDirectoryOverride { get; init; }

    /// <summary>Managed root; defaults to &lt;data root&gt;/managed.</summary>
    public string? ManagedRoot { get; init; }

    public string MutexName { get; init; } = SingleInstanceGuard.DefaultMutexName;

    public bool DetectLegacyShell { get; init; } = true;

    /// <summary>
    /// V11R-A-5 (P0 write policy): the release product is writable by default — the migration-era
    /// "read-only until S2 parity" default made every import/create/run fail in the shipped GUI.
    /// Safety is now a real precondition gate instead of a permanent default: read-only only when
    /// the legacy Tauri shell is detected or the caller explicitly passes <c>--parity=false</c>.
    /// </summary>
    public bool ParityReached { get; init; } = true;

    public bool FirstRunBackupEnabled { get; init; } = true;

    public TimeSpan StartupTimeout { get; init; } = TimeSpan.FromSeconds(30);

    public TimeSpan RequestTimeout { get; init; } = TimeSpan.FromSeconds(30);

    /// <summary>Test seam for legacy-shell detection.</summary>
    public IProcessNameProbe? ProcessProbe { get; init; }

    public bool EnableWireEvidence { get; init; } = true;
}
