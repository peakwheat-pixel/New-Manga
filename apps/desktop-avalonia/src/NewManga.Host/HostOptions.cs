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

    /// <summary>False until S2 command parity; keeps production data read-only.</summary>
    public bool ParityReached { get; init; }

    public bool FirstRunBackupEnabled { get; init; } = true;

    public TimeSpan StartupTimeout { get; init; } = TimeSpan.FromSeconds(30);

    public TimeSpan RequestTimeout { get; init; } = TimeSpan.FromSeconds(30);

    /// <summary>Test seam for legacy-shell detection.</summary>
    public IProcessNameProbe? ProcessProbe { get; init; }

    public bool EnableWireEvidence { get; init; } = true;
}
