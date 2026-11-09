using System.Security.Cryptography;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.RegularExpressions;

namespace NewManga.Host.Sources;

/// <summary>FEA-13-SRC-6: the outcome of one handoff import attempt.</summary>
public sealed record SourceAccessRestoreOutcome(
    string Status, string? Code, string? Reason, int Imported, int Unchanged, int Conflicts)
{
    public bool Succeeded => Status is "imported" or "unchanged";
}

/// <summary>
/// FEA-13-SRC-6 (C-09 SC-B07 ④): imports the encrypted source-access snapshot that the
/// Core writes into ``&lt;dataRoot&gt;/backups/restore-handoff/&lt;backup_id&gt;/`` after a
/// successful overwrite restore.
///
/// The Host is the ONLY party that can decrypt the snapshot (DPAPI CurrentUser). Import is
/// fail-closed: any read/validation/decrypt failure is a typed ``rejected`` outcome and the
/// LIVE registry is not written (``ImportRestoredSnapshot`` only saves on a real merge).
/// A receipt marks a completed import, so ``TryImportPending`` never re-imports a handoff
/// that was already consumed (a reset registry must not be revived by a restart scan).
/// </summary>
public static partial class SourceAccessRestore
{
    private const string HandoffDirectoryName = "backups";
    private const string HandoffSubdirectoryName = "restore-handoff";
    private const string SegmentDirectoryName = "source-access";
    private const string SegmentFileName = "registry.v1.dat";
    private const string ManifestFileName = "handoff.json";
    private const string ReceiptFileName = "import-receipt.json";

    [GeneratedRegex("^[0-9a-f]{32}$")]
    private static partial Regex BackupIdPattern();

    private sealed record HandoffManifest(
        [property: JsonPropertyName("backup_id")] string? BackupId,
        [property: JsonPropertyName("member")] string? Member,
        [property: JsonPropertyName("sha256")] string? Sha256,
        [property: JsonPropertyName("size_bytes")] long SizeBytes);

    private sealed record ImportReceipt(
        [property: JsonPropertyName("backup_id")] string BackupId,
        [property: JsonPropertyName("imported_at")] string ImportedAt);

    /// <summary>The handoff directory for one backup id (inside the data root).</summary>
    public static string HandoffRoot(string dataRoot, string backupId) => Path.Combine(
        dataRoot, HandoffDirectoryName, HandoffSubdirectoryName, backupId);

    /// <summary>Import one handoff. Never throws for a bad/missing handoff (typed outcome).</summary>
    public static SourceAccessRestoreOutcome TryImportFromHandoff(
        string dataRoot,
        string backupId,
        SourceAccessRegistry registry,
        Action<string>? log = null,
        bool force = false)
    {
        var id = backupId ?? string.Empty;
        if (!BackupIdPattern().IsMatch(id))
        {
            return Rejected("handoff_corrupt");
        }
        var root = HandoffRoot(dataRoot, id);
        if (!Directory.Exists(root))
        {
            return new SourceAccessRestoreOutcome("not_present", null, null, 0, 0, 0);
        }
        // A receipt marks a consumed handoff (startup scans must not revive a reset
        // registry). An EXPLICIT restore of the same package may re-import it.
        if (!force && File.Exists(Path.Combine(root, ReceiptFileName)))
        {
            return new SourceAccessRestoreOutcome("unchanged", null, null, 0, 0, 0);
        }
        try
        {
            var manifestPath = Path.Combine(root, ManifestFileName);
            SourceSecurity.RejectReparseAncestors(manifestPath);
            if (!File.Exists(manifestPath))
            {
                return Rejected("handoff_corrupt");
            }
            HandoffManifest? manifest;
            try
            {
                manifest = JsonSerializer.Deserialize<HandoffManifest>(
                    File.ReadAllText(manifestPath));
            }
            catch (JsonException)
            {
                return Rejected("handoff_corrupt");
            }
            if (manifest is null
                || !string.Equals(manifest.BackupId, id, StringComparison.Ordinal)
                || string.IsNullOrWhiteSpace(manifest.Member)
                || string.IsNullOrWhiteSpace(manifest.Sha256))
            {
                return Rejected("handoff_corrupt");
            }

            var segmentPath = Path.Combine(root, SegmentDirectoryName, SegmentFileName);
            SourceSecurity.RejectReparseAncestors(segmentPath);
            if (!File.Exists(segmentPath))
            {
                return Rejected("handoff_corrupt");
            }
            var bytes = File.ReadAllBytes(segmentPath);
            if (bytes.Length != manifest.SizeBytes
                || !string.Equals(Sha256Hex(bytes), manifest.Sha256, StringComparison.OrdinalIgnoreCase))
            {
                return Rejected("handoff_corrupt");
            }

            var outcome = registry.ImportRestoredSnapshot(bytes);
            if (outcome.Status == "rejected")
            {
                // The snapshot bytes are authentic but the Host cannot decrypt/parse them
                // (another Windows user or a different machine): a typed, live-zero-write
                // refusal. The message must never claim cross-machine support.
                return new SourceAccessRestoreOutcome(
                    "rejected", "SOURCE_ACCESS_DENIED", outcome.Reason, 0, 0, 0);
            }

            WriteReceipt(root, id);
            log?.Invoke(
                $"source-access handoff imported: {id} "
                + $"imported={outcome.Imported} unchanged={outcome.Unchanged} "
                + $"conflicts={outcome.Conflicts}");
            return new SourceAccessRestoreOutcome(
                outcome.Status, null, null,
                outcome.Imported, outcome.Unchanged, outcome.Conflicts);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException
            or SourceAccessException or JsonException or InvalidDataException)
        {
            log?.Invoke("source-access handoff import failed: " + error.Message);
            return Rejected("handoff_corrupt");
        }
    }

    /// <summary>
    /// Startup catch-up: consume every pending handoff exactly once. A handoff that already
    /// carries a receipt is skipped, so a user-visible ``Reset`` is never undone by a restart.
    /// </summary>
    public static IReadOnlyList<SourceAccessRestoreOutcome> TryImportPending(
        string dataRoot,
        SourceAccessRegistry registry,
        Action<string>? log = null)
    {
        var root = Path.Combine(dataRoot, HandoffDirectoryName, HandoffSubdirectoryName);
        if (!Directory.Exists(root))
        {
            return Array.Empty<SourceAccessRestoreOutcome>();
        }
        var outcomes = new List<SourceAccessRestoreOutcome>();
        foreach (var directory in Directory.EnumerateDirectories(root).OrderBy(item => item, StringComparer.Ordinal))
        {
            var backupId = Path.GetFileName(directory);
            outcomes.Add(TryImportFromHandoff(dataRoot, backupId, registry, log));
        }
        return outcomes;
    }

    private static void WriteReceipt(string handoffRoot, string backupId)
    {
        try
        {
            File.WriteAllText(
                Path.Combine(handoffRoot, ReceiptFileName),
                JsonSerializer.Serialize(new ImportReceipt(backupId, DateTimeOffset.UtcNow.ToString("O"))));
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            // A missing receipt only means a later startup scan retries the import; the
            // merge itself is idempotent (existing registry ids are never re-imported).
        }
    }

    private static SourceAccessRestoreOutcome Rejected(string reason) =>
        new("rejected", "SOURCE_ACCESS_DENIED", reason, 0, 0, 0);

    private static string Sha256Hex(byte[] bytes) =>
        Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
}
