namespace NewManga.Host.Sources;

/// <summary>
/// FEA-11-SCAN-1 (I-6 / AC-S5): the closed, in-process status snapshot of the Host-side read-only
/// periodic source scan. This is the ONLY observable surface of the scan slice: it is an in-process
/// property (<c>HostRuntime.SourceScanStatus</c>) and never a wire command, DTO, DB row or file.
///
/// Redaction contract: the snapshot carries typed source ids, result enums, counts and stable error
/// codes only. It must never carry absolute paths, grant ids, host-session ids, exception messages,
/// stack traces or credentials.
/// </summary>
public sealed record SourceScanStatus(
    bool Enabled,
    int IntervalSeconds,
    bool Paused,
    DateTimeOffset? LastTickAt,
    DateTimeOffset? NextTickAt,
    IReadOnlyList<SourceScanTargetStatus> Targets,
    IReadOnlyList<SourceScanRecentEntry> Recent)
{
    /// <summary>
    /// The honest "no scheduler" state (Host not ready, referenced import disabled, ...).
    /// <c>enabled=false</c> already says "not running"; <c>paused</c> is deliberately false so a
    /// caller cannot confuse "disabled for this host" with "an active scheduler paused by a verdict"
    /// (r1 P3-4).
    /// </summary>
    public static SourceScanStatus Disabled(int intervalSeconds) =>
        new(false, intervalSeconds, false, null, null, Array.Empty<SourceScanTargetStatus>(),
            Array.Empty<SourceScanRecentEntry>());

    /// <summary>
    /// FEA-11-SCAN-2 (B1 / AC-S2-1..S2-4): the cold-start enumeration verdict; null until the first
    /// refresh was attempted. Counts only — never the skipped target paths/ids from the Host side.
    /// </summary>
    public SourceScanEnumerationStatus? Enumeration { get; init; }

    /// <summary>
    /// FEA-11-WATCH-1 (AC-W1/W3/W5): the directory-watcher hint status. Counts/typed codes only — the
    /// snapshot must never carry absolute paths, root names, file names, grants or session material.
    /// Null when this Host has no watcher attached.
    /// </summary>
    public SourceScanWatcherStatus? Watcher { get; init; }
}

/// <summary>
/// FEA-11-WATCH-1 (AC-W1/W3/W5): closed, path-free watcher status. <see cref="Armed"/> is false after
/// Stop/Dispose; <see cref="Uncovered"/> counts targets that cannot be watched (registry/unreadable/
/// cap/degraded); <see cref="OverflowCount"/> counts OS overflow/invalidation events; a hint only marks
/// a source due for one full rescan — it is never a changed/deleted fact.
/// </summary>
public sealed record SourceScanWatcherStatus(
    bool Enabled,
    bool Armed,
    int Active,
    int Uncovered,
    int OverflowCount,
    bool Degraded,
    DateTimeOffset? LastHintAt,
    int HintCount,
    int DebouncedEvents,
    int PendingHints);

/// <summary>
/// FEA-11-SCAN-2 (B1): typed cold-start enumeration state. <see cref="Available"/> is false when the
/// Core did not advertise <c>source.sync.enumerate/1</c> or the enumeration failed; the Host then
/// fails closed without blocking startup (no retry storm — only an explicit refresh retries).
/// </summary>
public sealed record SourceScanEnumerationStatus(
    bool? Available,
    DateTimeOffset? LastRefreshAt,
    string LastResult,
    string? LastErrorCode,
    int SkippedTargets);

/// <summary>One registered scan target, projected without any path or grant material.</summary>
public sealed record SourceScanTargetStatus(
    string SourceId,
    DateTimeOffset? LastScanAt,
    string? LastResult,
    SourceScanCounts? Counts,
    bool Deferred)
{
    /// <summary>I-6: <c>deferred</c> only marks a target postponed by THIS tick's budget.</summary>
    public static SourceScanTargetStatus Empty(string sourceId) =>
        new(sourceId, null, null, null, false);
}

/// <summary>
/// One recent scan outcome (bounded to <see cref="SourceScanResults.MaxRecentEntries"/> entries).
/// <see cref="ErrorCode"/> is a stable typed code, never an exception message.
/// </summary>
public sealed record SourceScanRecentEntry(
    string SourceId,
    DateTimeOffset At,
    string Result,
    SourceScanCounts? Counts,
    string? ErrorCode);

/// <summary>The frozen scan <c>totals</c> projection (C-17 §5.2 Totals) as an in-process record.</summary>
public sealed record SourceScanCounts(
    int Unchanged,
    int Added,
    int Missing,
    int Changed,
    int Ambiguous)
{
    public static SourceScanCounts Zero { get; } = new(0, 0, 0, 0, 0);

    /// <summary>True when the scan observed any non-unchanged classification.</summary>
    public bool HasChange => Added > 0 || Missing > 0 || Changed > 0 || Ambiguous > 0;
}

/// <summary>
/// FEA-11-SCAN-1 (AC-S5): the frozen <c>last_result</c> enum of the scan status. <c>deferred</c> is
/// deliberately NOT a result (I-6: it only means "postponed by this tick's budget").
/// </summary>
public static class SourceScanResults
{
    public const string Ok = "ok";
    public const string Changed = "changed";
    public const string Missing = "missing";
    public const string Unsupported = "unsupported";
    public const string Denied = "denied";

    /// <summary>FEA-11-SCAN-2 / AC-S2-4: registry authorization could not be proven; no scan frame.</summary>
    public const string Skipped = "skipped";

    public const string Error = "error";

    /// <summary>I-6: <c>recent</c> keeps at most 50 entries.</summary>
    public const int MaxRecentEntries = 50;

    public static readonly IReadOnlySet<string> All = new HashSet<string>(StringComparer.Ordinal)
    {
        Ok, Changed, Missing, Unsupported, Denied, Skipped, Error,
    };
}
