using NewManga.CoreClient;
using NewManga.Host.Sources;

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

    /// <summary>
    /// V11R-A-6 test seam for the startup contract self check: null uses the live
    /// <c>core.ping</c>; tests inject a mismatching CorePing to prove the write gate closes.
    /// </summary>
    public Func<CancellationToken, Task<CorePing>>? StartupPingProbe { get; init; }

    public bool ReferencedImportEnabled { get; init; } = true;

    public bool EnableWireEvidence { get; init; } = true;

    // ---------------------------------------------------------------------------------------
    // FEA-11-SCAN-1 (I-1/I-4 / AC-S1/S3): the Host-side read-only periodic source scan.
    // Defaults are frozen by the card: enabled=true, interval=900s, 8 targets/tick, 256 MiB per
    // source. NEWMANGA_SOURCE_SCAN_INTERVAL_SECONDS overrides the interval inside [60, 86400] (an
    // illegal value falls back to 900s + a WARN in HostRuntime — never a startup failure) and there
    // is deliberately NO settings section for these values (P15 key space is frozen).
    // ---------------------------------------------------------------------------------------

    /// <summary>Master switch; the scheduler only starts when referenced import is enabled too.</summary>
    public bool SourceScanEnabled { get; init; } = true;

    /// <summary>Configured interval in seconds (environment override applies at Host start).</summary>
    public int SourceScanIntervalSeconds { get; init; } = 900;

    /// <summary>AC-S3: at most this many targets are attempted per tick; the rest are deferred.</summary>
    public int SourceScanMaxTargetsPerTick { get; init; } = 8;

    /// <summary>AC-S3: per-source byte budget (files) — over-budget targets are deferred.</summary>
    public long SourceScanMaxBytesPerSource { get; init; } = 256L * 1024 * 1024;

    /// <summary>AC-S3: per-folder member budget — over-budget targets are deferred.</summary>
    public int SourceScanMaxEntriesPerSource { get; init; } = 10000;

    /// <summary>TimeProvider seam: the scheduler loop and every status timestamp use this clock.</summary>
    public TimeProvider SourceScanTimeProvider { get; init; } = TimeProvider.System;

    /// <summary>
    /// FEA-11-SCAN-2 (B1 / AC-S2-1): run the read-only cold-start target enumeration
    /// (<c>source_list_scan_targets</c>) in the background after the Host becomes ready. It never
    /// blocks startup; a missing capability is a typed fail-closed snapshot state.
    /// </summary>
    public bool SourceScanColdStartEnumeration { get; init; } = true;

    /// <summary>
    /// FEA-11-WATCH-1 (AC-W1/W5): enable the Host-only read-only directory watcher that turns file
    /// events into per-source due hints for the existing full re-enumeration. Disabled/illegal values
    /// degrade to the periodic scan only (never a startup failure).
    /// </summary>
    public bool SourceWatchEnabled { get; init; } = true;

    /// <summary>AC-W5: maximum armed watches (1..4096, default 256); beyond the cap targets are uncovered.</summary>
    public int SourceWatchMaxWatches { get; init; } = SourceWatchOptions.DefaultMaxWatches;

    /// <summary>AC-W5: FileSystemWatcher internal buffer (clamped to [4 KiB, 64 KiB]).</summary>
    public int SourceWatchInternalBufferBytes { get; init; } = SourceWatchOptions.DefaultInternalBufferBytes;

    /// <summary>AC-W2/W5: per-source debounce window in ms (250..60000, default 2000).</summary>
    public int SourceWatchDebounceMilliseconds { get; init; } = SourceWatchOptions.DefaultDebounceMilliseconds;
}
