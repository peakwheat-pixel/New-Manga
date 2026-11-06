using System.Text.Json;
using NewManga.CoreClient;

namespace NewManga.App.Services;

/// <summary>
/// FEA-12-UI IN-1 / ZCode SCOPE-ADJ Q1: the App's trash/delete port. It is deliberately a SEPARATE
/// interface — the frozen C-07 <see cref="IHostController"/> inventory (54 members, pinned by
/// <c>tools/generate_api_inventory.py --check</c> + 18 contract pins) is not extended. The separate
/// interface satisfies ADJ-001 `:41`'s additive intent without an UNFREEZE.
///
/// Every method maps to exactly ONE Host command frame (or the read-only <c>core_ping</c> capability
/// probe) and returns a typed result; a missing capability/old Core is surfaced as a typed state,
/// never as fabricated data. The runtime capability gate lives in the Host (FEA-12-CORE); the App
/// probes <c>core.ping</c> first so the UI can render the "capability missing" state before it sends
/// a command frame.
/// </summary>
public interface ITrashController
{
    /// <summary>Read-only capability probe: reads <c>core.ping</c> capabilities; never sends a trash command.</summary>
    Task<TrashCapabilityState> ProbeTrashCapabilitiesAsync(CancellationToken cancellationToken = default);

    /// <summary>One <c>library_list_trash</c> frame. <paramref name="cursor"/> is opaque and echoed as-is.</summary>
    Task<TrashListResult> ListTrashAsync(string? cursor = null, CancellationToken cancellationToken = default);

    /// <summary>One <c>library_move_to_trash</c> frame (soft delete).</summary>
    Task<TrashWriteResult> MoveToTrashAsync(
        IReadOnlyList<string> bookIds,
        string idempotencyKey,
        CancellationToken cancellationToken = default);

    /// <summary>One <c>library_restore_from_trash</c> frame. Each call uses its own idempotency key.</summary>
    Task<TrashWriteResult> RestoreFromTrashAsync(
        IReadOnlyList<string> bookIds,
        string idempotencyKey,
        CancellationToken cancellationToken = default);

    /// <summary>One read-only <c>library_preview_permanent_delete_books</c> frame.</summary>
    Task<TrashPreviewResult> PreviewPermanentDeleteAsync(
        IReadOnlyList<string> bookIds,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// One <c>library_delete_book_permanently</c> frame. The same call is the PD-07 cleanup retry:
    /// it re-sends the SAME persisted digest and never re-runs the preview.
    /// </summary>
    Task<TrashDeleteResult> DeletePermanentlyAsync(
        string bookId,
        string inventoryDigest,
        CancellationToken cancellationToken = default);
}

/// <summary>The four Host command names + the read-only probe, in one place (tests assert frames from it).</summary>
public static class TrashWireCommands
{
    public const string CapabilityProbe = "core_ping";
    public const string ListTrash = "library_list_trash";
    public const string MoveToTrash = "library_move_to_trash";
    public const string RestoreFromTrash = "library_restore_from_trash";
    public const string PreviewPermanentDelete = "library_preview_permanent_delete_books";
    public const string DeletePermanently = "library_delete_book_permanently";

    /// <summary>OUT-2: never called by the UI (first Core release returns UNKNOWN_COMMAND).</summary>
    public const string PurgeTrash = "library_purge_trash";

    /// <summary>OUT-1 / L1: batch permanent delete has no UI (whole-library dead end).</summary>
    public const string BatchDeletePermanently = "library_delete_books_permanently";

    public static IReadOnlyList<string> AllowedByAnyway => new[]
    {
        CapabilityProbe, ListTrash, MoveToTrash, RestoreFromTrash, PreviewPermanentDelete, DeletePermanently,
    };
}

/// <summary>Typed capability state from the single <c>core.ping</c> probe (IN-2 / AC7).</summary>
public sealed record TrashCapabilityState(
    bool Probed,
    bool ReadAvailable,
    bool WriteAvailable,
    bool PreviewAvailable,
    string? Code,
    string? Message)
{
    public static TrashCapabilityState Unavailable(string? code, string? message) =>
        new(false, false, false, false, code, message);

    public bool AnyMissing => Probed && (!ReadAvailable || !WriteAvailable || !PreviewAvailable);

    public bool ListAllowed => ReadAvailable;

    public bool WriteAllowed => WriteAvailable;

    public bool PreviewAllowed => PreviewAvailable;
}

/// <summary>One <c>ListTrash</c> row (Q3: only bookId/title/deletedAt; no thumbnails, no content preview).</summary>
public sealed record TrashEntry(string BookId, string Title, string DeletedAt);

/// <summary>One page of <c>ListTrash</c>. The cursor is opaque: replayed verbatim, never decoded/persisted/shown.</summary>
public sealed record TrashListResult(
    bool Ok,
    string? Code,
    string? Message,
    IReadOnlyList<TrashEntry> Items,
    string? NextCursor)
{
    public static TrashListResult Failure(string code, string? message) =>
        new(false, code, message, Array.Empty<TrashEntry>(), null);
}

/// <summary>Per-item skipped/conflict outcome with a whitelisted, user-safe reason.</summary>
public sealed record TrashItemIssue(string BookId, string? ReasonCode, string ReasonText);

/// <summary>Result of one <c>MoveToTrash</c> / <c>RestoreFromTrash</c> frame (per-item, never "all good").</summary>
public sealed record TrashWriteResult(
    bool Ok,
    string? Code,
    string? Message,
    IReadOnlyList<string> SucceededIds,
    IReadOnlyList<TrashItemIssue> FailedItems)
{
    public static TrashWriteResult Failure(string code, string? message) =>
        new(false, code, message, Array.Empty<string>(), Array.Empty<TrashItemIssue>());
}

/// <summary>
/// PD-01/PD-04 protection disclosure. rev 2.14 (C-04b v1.1): the complete current sets are the
/// binding disclosure; the single <see cref="CurrentRevisionId"/> is display-only. <c>null</c> means
/// UNKNOWN (old Core omitted the field) — it must NOT be treated as an empty array; only <c>[]</c>
/// means "no current". Completeness of BOTH sides is required before the UI allows confirmation.
/// </summary>
public sealed record TrashProtection(
    int LockCount,
    string? CurrentRevisionId,
    IReadOnlyList<string>? CurrentRegionRevisionIds,
    IReadOnlyList<string>? CurrentArtifactRevisionIds,
    IReadOnlyList<string> PinnedRevisionIds,
    IReadOnlyList<string> ActiveRunIds,
    int DraftPageCount,
    int ManualRegionCount)
{
    /// <summary>False for an old Core that does not return both rev 2.14 current arrays (fail-closed).</summary>
    public bool CurrentSetKnown =>
        CurrentRegionRevisionIds is not null && CurrentArtifactRevisionIds is not null;

    public int CurrentRegionCount => CurrentRegionRevisionIds?.Count ?? 0;

    public int CurrentArtifactCount => CurrentArtifactRevisionIds?.Count ?? 0;
}

/// <summary>Content totals disclosed by the preview (PD-01 third item is the file/byte pair).</summary>
public sealed record TrashContentSummary(
    int Chapters,
    int Pages,
    int Artifacts,
    int DeletedFiles,
    long DeletedBytes);

/// <summary>One shared managed/source reference with its external project count.</summary>
public sealed record TrashSharedFileRef(string FileId, int OtherProjectCount);

/// <summary>One <c>DeletePreviewItem</c> (camelCase wire, PD-01 three mandatory items present).</summary>
public sealed record TrashPreviewItem(
    string BookId,
    string Title,
    TrashProtection Protection,
    TrashContentSummary Content,
    IReadOnlyList<TrashSharedFileRef> SharedFileRefs);

/// <summary>
/// One <c>PreviewPermanentDeleteBooks</c> frame result. Read-only; zero side effects.
/// <para>
/// <see cref="InventoryDigest"/> is the COLLECTION digest of the echoed <c>bookIds</c> order; the
/// single-book delete frame must be bound to that book's PER-BOOK digest from
/// <see cref="Digests"/> (the Core recomputes the per-book digest and compares byte-for-byte).
/// </para>
/// </summary>
public sealed record TrashPreviewResult(
    bool Ok,
    string? Code,
    string? Message,
    string? InventoryDigest,
    IReadOnlyList<TrashPreviewItem> Items,
    IReadOnlyDictionary<string, string> Digests)
{
    public static TrashPreviewResult Failure(string code, string? message) =>
        new(false, code, message, null, Array.Empty<TrashPreviewItem>(),
            new Dictionary<string, string>(StringComparer.Ordinal));
}

/// <summary>Terminal classification of one permanent-delete frame (single C flow).</summary>
public enum TrashDeleteOutcome
{
    Deleted,
    CleanupPending,
    Stale,
    Busy,
    NotFound,
    Conflict,
    Failed,
    InvalidRequest,
    Unavailable,
    CapabilityMissing,
    ReadOnly,
    Unknown,
}

/// <summary>Typed result of one <c>library_delete_book_permanently</c> frame.</summary>
public sealed record TrashDeleteResult(TrashDeleteOutcome Outcome, string? Code, string? Message)
{
    public bool Succeeded => Outcome == TrashDeleteOutcome.Deleted;

    public static TrashDeleteResult Failure(TrashDeleteOutcome outcome, string code, string? message) =>
        new(outcome, code, message);
}

/// <summary>JSON payload builders: the exact frozen closed shapes (no extra keys).</summary>
public static class TrashPayloads
{
    public static JsonElement ListTrash(string? cursor)
    {
        if (string.IsNullOrEmpty(cursor))
        {
            return JsonSerializer.SerializeToElement(new Dictionary<string, object?>());
        }

        return JsonSerializer.SerializeToElement(new Dictionary<string, object?>
        {
            ["cursor"] = cursor,
        });
    }

    /// <summary><c>{"entries":[{"book_id":…}],"idempotency_key":…}</c> (closed shape; refs stay snake_case).</summary>
    public static JsonElement MoveOrRestore(IReadOnlyList<string> bookIds, string idempotencyKey) =>
        JsonSerializer.SerializeToElement(new Dictionary<string, object?>
        {
            ["entries"] = bookIds.Select(bookId => new Dictionary<string, object?>
            {
                ["book_id"] = bookId,
            }).ToArray(),
            ["idempotency_key"] = idempotencyKey,
        });

    /// <summary><c>{"bookIds":[…]}</c> — frozen camelCase of C-04b v1.1 §2.1.</summary>
    public static JsonElement Preview(IReadOnlyList<string> bookIds) =>
        JsonSerializer.SerializeToElement(new Dictionary<string, object?>
        {
            ["bookIds"] = bookIds.ToArray(),
        });

    /// <summary>
    /// <c>{"book_id":…,"confirm_permanent_delete":true,"inventory_digest":…}</c> — the payload the
    /// Host forwards has EXACTLY these three keys (AC5); no paths, no titles, no batch fields.
    /// </summary>
    public static JsonElement DeletePermanently(string bookId, string inventoryDigest) =>
        JsonSerializer.SerializeToElement(new Dictionary<string, object?>
        {
            ["book_id"] = bookId,
            ["confirm_permanent_delete"] = true,
            ["inventory_digest"] = inventoryDigest,
        });
}

/// <summary>User-facing copy for reason codes (whitelist + honest fallback; AC3/L5).</summary>
public static class TrashCopy
{
    /// <summary>L5: the first Core release only produces TRASH_ENTRY_NOT_FOUND; the others are mapped for the frozen set.</summary>
    public static string RestoreReason(string? reasonCode) => reasonCode switch
    {
        "TRASH_ENTRY_NOT_FOUND" => "条目不在回收站（可能已恢复或曾被清理）",
        "TRASH_RESTORE_CONFLICT" => "恢复冲突（目标状态不允许恢复）",
        "TRASH_RESTORE_LAYER_MISMATCH" => "恢复冲突（该条目来自不同数据层）",
        null or "" => "恢复冲突（未分类）",
        _ => $"恢复冲突（未分类：{reasonCode}）",
    };

    public static string MoveSkipReason(string? reasonCode) => reasonCode switch
    {
        "TRASH_ENTRY_NOT_FOUND" => "作品已不在书架或已在回收站（原因：TRASH_ENTRY_NOT_FOUND）",
        "BOOK_BUSY" => "作品有进行中的任务，暂不能移入回收站",
        null or "" => "未分类原因",
        _ => $"未分类原因（{reasonCode}）",
    };

    /// <summary>AC4 disclosure: numbers only — never paths, source filenames or stack traces.</summary>
    public static string BytesText(long bytes) => bytes switch
    {
        < 0 => "—",
        < 1024 => $"{bytes} B",
        < 1024 * 1024 => $"{bytes / 1024d:0.0} KiB",
        _ => $"{bytes / (1024d * 1024d):0.0} MiB",
    };
}

/// <summary>Idempotency keys are caller-generated opaque strings, never persisted.</summary>
public static class TrashIdempotency
{
    public static string NewKey() => Guid.NewGuid().ToString("N");
}

/// <summary>
/// Capability names consumed by the UI probe. They are NOT redefined here as new capability
/// vocabulary: the literals come from the registered M2-C1 rev 2.13/2.14 contract constants.
/// </summary>
public static class TrashCapabilities
{
    public const string Read = DeleteTrashWireTargets.TrashReadCapability;
    public const string Write = DeleteTrashWireTargets.TrashWriteCapability;
    public const string Preview = DeleteTrashWireTargets.DeletePreviewCapability;
}

/// <summary>Typed error-code vocabulary the delete/trash UI is allowed to branch on (closed set).</summary>
public static class TrashErrorCodes
{
    public const string InvalidRequest = "INVALID_REQUEST";
    public const string BookNotFound = "BOOK_NOT_FOUND";
    public const string Busy = "BOOK_BUSY";
    public const string Conflict = "BOOK_DELETE_CONFLICT";
    public const string Failed = "BOOK_DELETE_FAILED";
    public const string InventoryUnavailable = "BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE";
    public const string StalePreview = "BOOK_DELETE_STALE_PREVIEW";
    public const string CleanupPending = "BOOK_DELETE_CLEANUP_PENDING";
    public const string TrashEntryNotFound = "TRASH_ENTRY_NOT_FOUND";
    public const string CapabilityMissing = "CORE_CAPABILITY_MISSING";
    public const string ReadOnly = "HOST_READ_ONLY";
    public const string CoreUnavailable = "CORE_UNAVAILABLE";
    public const string ProtocolUnsupported = "PROTOCOL_VERSION_UNSUPPORTED";
    public const string UnknownCommand = "UNKNOWN_COMMAND";
    public const string Unknown = "UNKNOWN";
}
