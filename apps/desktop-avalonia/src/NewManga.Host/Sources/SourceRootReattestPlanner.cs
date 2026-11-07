using System.Globalization;
using System.Text.Json;

namespace NewManga.Host.Sources;

/// <summary>
/// FEA-11-L-S4-B (C-16 v1.5 §2.5 Host obligations): the pre-registry validated
/// fields of ONE Core <c>ScanTarget</c> (<c>source_list_scan_targets</c>). The
/// shape is the frozen C-17 §5.2 DTO — no Core path/version exists on this face.
/// </summary>
public sealed record SourceScanTargetShape(
    string SourceId,
    string RegistryId,
    int Generation,
    string Kind,
    string IdentityDigest,
    IReadOnlyList<string> ProjectIds);

/// <summary>
/// FEA-11-L-S4-B: one EXACT re-attest candidate. The Host mints a witness grant
/// over <see cref="LiveRoot"/> with the live entry's own registry identity; the
/// absolute path never crosses the wire and never reaches logs/status.
/// <see cref="Version"/> is the same frozen placeholder an enumerated
/// <see cref="SourceScanTarget"/> carries (the Core scan-target DTO has no
/// version field); <c>ReattestSourceLocation</c> never reads
/// <c>scope.version</c> — only the grant's signed facts are identity evidence.
/// </summary>
public sealed record SourceRootReattestCandidate(
    string SourceId,
    string Kind,
    string LiveRegistryId,
    int LiveGeneration,
    string LiveRoot,
    string CoreRegistryId,
    int CoreGeneration,
    string Version)
{
    public override string ToString() => "SourceRootReattestCandidate(" + SourceId + ")";
}

/// <summary>One pure planning verdict: either an exact candidate or the frozen skip reason.</summary>
public sealed record SourceRootReattestDecision(
    SourceRootReattestCandidate? Candidate,
    string Reason)
{
    public bool IsCandidate => Candidate is not null;

    public static SourceRootReattestDecision CandidatePlan(
        SourceRootReattestCandidate candidate) => new(candidate, "candidate");

    public static SourceRootReattestDecision Skip(string reason) => new(null, reason);
}

/// <summary>
/// FEA-11-L-S4-B (C-16 v1.5 §2.5 Host-side preconditions): the ONLY place that
/// decides whether a Core scan target whose recorded registry is no longer the
/// live authorization may be re-attested. It is a pure function over the Core
/// target JSON and the Host registry snapshot — no I/O, no storage, no path
/// logging.
///
/// Frozen candidate rules (any miss -> the target keeps its existing typed skip;
/// the Host NEVER sends on an ambiguous/partial match):
/// <list type="number">
/// <item>the Core-recorded <c>registry_id</c> exists in the Host registry and is
/// REVOKED (an existing revoked entry is what B1 leaves behind);</item>
/// <item>that old entry carries EXACTLY one root;</item>
/// <item>exactly ONE live (non-revoked) entry matches it: exactly one root, the
/// normalized path equals the old entry's normalized path, and the
/// (volume_serial, file_id) registered identity equals the old entry's;</item>
/// <item><c>live.CreatedAt &gt; old.RevokedAt</c> — the live entry is provably a
/// re-authorization that happened AFTER the revoke, never a historical
/// duplicate entry;</item>
/// <item>the source kind is not <c>folder</c> (L-S4-2; B1's file-source
/// promise).</item>
/// </list>
/// </summary>
public static class SourceRootReattestPlanner
{
    /// <summary>C-17 §5.2: a shared source maps to 1..20 books (never truncated).</summary>
    public const int MaximumProjectIds = 20;

    /// <summary>
    /// The frozen placeholder an enumerated target carries (see
    /// <see cref="HostSourceScanTargetEnumerator.TryMap"/>); this planner reuses
    /// it so the witness grant has exactly the same shape the scan path mints.
    /// </summary>
    public const string EnumeratedTargetVersion = "1";

    /// <summary>
    /// The pre-registry half of <see cref="HostSourceScanTargetEnumerator.TryMap"/>:
    /// a closed C-17 §5.2 <c>ScanTarget</c> must carry a non-empty source/registry
    /// id, a known kind, a lower-hex-64 identity digest, generation &gt;= 1 and
    /// 1..20 unique project ids. Every violation fails closed; no field is guessed.
    /// </summary>
    public static bool TryReadTarget(JsonElement element, out SourceScanTargetShape shape)
    {
        shape = null!;
        if (element.ValueKind != JsonValueKind.Object)
        {
            return false;
        }

        var sourceId = ReadString(element, "source_id");
        var registryId = ReadString(element, "registry_id");
        var kind = ReadString(element, "source_kind");
        var identityDigest = ReadString(element, "identity_digest");
        if (string.IsNullOrWhiteSpace(sourceId) || string.IsNullOrWhiteSpace(registryId)
            || kind is null || !HostSourceScanTargetEnumerator.KnownSourceKinds.Contains(kind)
            || identityDigest is null || !IsLowerHex64(identityDigest))
        {
            return false;
        }

        if (!element.TryGetProperty("generation", out var generationElement)
            || generationElement.ValueKind != JsonValueKind.Number
            || !generationElement.TryGetInt32(out var generation) || generation < 1)
        {
            return false;
        }

        if (!element.TryGetProperty("project_ids", out var projectElements)
            || projectElements.ValueKind != JsonValueKind.Array)
        {
            return false;
        }

        var projectIds = new List<string>();
        foreach (var project in projectElements.EnumerateArray())
        {
            if (project.ValueKind != JsonValueKind.String
                || project.GetString() is not { Length: > 0 } projectId)
            {
                return false;
            }

            if (!projectIds.Contains(projectId, StringComparer.Ordinal))
            {
                projectIds.Add(projectId);
            }
        }

        // P3-4: 1..20 unique books; more than 20 is a typed skip (never truncate,
        // never fall back to "current" semantics).
        if (projectIds.Count is < 1 or > MaximumProjectIds)
        {
            return false;
        }

        shape = new SourceScanTargetShape(
            sourceId!, registryId!, generation, kind, identityDigest, projectIds);
        return true;
    }

    /// <summary>
    /// Pure candidate planning over ONE Core target element and the Host registry
    /// snapshot. Always returns a typed reason; never throws for malformed input.
    /// </summary>
    public static SourceRootReattestDecision Plan(
        JsonElement element,
        IReadOnlyList<SourceAuthorization> entries)
    {
        if (!TryReadTarget(element, out var shape))
        {
            return SourceRootReattestDecision.Skip("malformed-target");
        }

        return Plan(shape, entries);
    }

    /// <summary>Candidate planning over already validated target fields.</summary>
    public static SourceRootReattestDecision Plan(
        SourceScanTargetShape shape,
        IReadOnlyList<SourceAuthorization> entries)
    {
        if (entries is null)
        {
            return SourceRootReattestDecision.Skip("malformed-registry");
        }

        // L-S4-2: folder identity keys are a separate card; never re-attest one.
        if (shape.Kind == "folder")
        {
            return SourceRootReattestDecision.Skip("folder-source");
        }

        // (1) the Core-recorded authorization must still exist and be REVOKED.
        var oldEntry = entries.FirstOrDefault(
            entry => string.Equals(entry.RegistryId, shape.RegistryId, StringComparison.Ordinal));
        if (oldEntry is null)
        {
            return SourceRootReattestDecision.Skip("old-entry-missing");
        }

        if (oldEntry.RevokedAt is null)
        {
            // A live recorded entry is not the L-S4-B gap; the exact-match path
            // owns it (a generation drift there is NOT re-attested silently).
            return SourceRootReattestDecision.Skip("old-entry-live");
        }

        if (oldEntry.Roots is not { Length: 1 })
        {
            return SourceRootReattestDecision.Skip("old-entry-multiple-roots");
        }

        var oldRoot = oldEntry.Roots[0];
        var oldPath = Normalize(oldRoot.Root);
        var live = entries
            .Where(entry => entry.RevokedAt is null
                && entry.Roots is { Length: 1 }
                && string.Equals(Normalize(entry.Roots[0].Root), oldPath, StringComparison.OrdinalIgnoreCase)
                && entry.Roots[0].VolumeSerial == oldRoot.VolumeSerial
                && entry.Roots[0].FileId == oldRoot.FileId)
            .ToArray();
        if (live.Length == 0)
        {
            return SourceRootReattestDecision.Skip("no-live-entry");
        }

        if (live.Length > 1)
        {
            // Ambiguity is fail-closed: never pick one of several live entries.
            return SourceRootReattestDecision.Skip("ambiguous-live-entries");
        }

        var liveEntry = live[0];
        if (!TryParseTimestamp(liveEntry.CreatedAt, out var created)
            || !TryParseTimestamp(oldEntry.RevokedAt, out var revoked))
        {
            return SourceRootReattestDecision.Skip("invalid-timestamps");
        }

        if (created <= revoked)
        {
            // A historical duplicate entry created before the revoke is never a
            // re-authorization.
            return SourceRootReattestDecision.Skip("time-order-invalid");
        }

        return SourceRootReattestDecision.CandidatePlan(
            new SourceRootReattestCandidate(
                shape.SourceId,
                shape.Kind,
                liveEntry.RegistryId,
                liveEntry.Generation,
                SourceSecurity.Normalize(liveEntry.Roots[0].Root),
                shape.RegistryId,
                shape.Generation,
                EnumeratedTargetVersion));
    }

    private static string Normalize(string path) => SourceSecurity.Normalize(path);

    private static bool TryParseTimestamp(string value, out DateTimeOffset timestamp) =>
        DateTimeOffset.TryParse(
            value,
            CultureInfo.InvariantCulture,
            DateTimeStyles.RoundtripKind,
            out timestamp);

    private static string? ReadString(JsonElement element, string property) =>
        element.TryGetProperty(property, out var value) && value.ValueKind == JsonValueKind.String
            ? value.GetString()
            : null;

    private static bool IsLowerHex64(string? value)
    {
        if (value is not { Length: 64 })
        {
            return false;
        }

        foreach (var character in value)
        {
            if (character is not (>= '0' and <= '9') and not (>= 'a' and <= 'f'))
            {
                return false;
            }
        }

        return true;
    }
}
