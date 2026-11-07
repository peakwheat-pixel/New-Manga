using System.Text.Json;
using NewManga.CoreClient.Commands;
using NewManga.Host;
using NewManga.Host.Sources;

namespace NewManga.App.Services;

/// <summary>
/// FEA-11-L-S1-B-RECOVERY-REAUTH-1 (B1, C-15 v1.5 §5 / C-16 v1.4 §1): the ONE explicit recovery
/// action the App may offer when a root's authorization no longer matches the file at the
/// registered path. The reference import face is failure-only today: a replaced/missing root makes
/// the same-path re-import fail forever (<see cref="SourceImportCoordinator.FindOrRegisterRootAsync"/>
/// reuses the stale entry, and the Host re-verifies the root identity per request). Recovery stays a
/// USER action — nothing here runs on a failure branch by itself.
/// </summary>
public enum SourceRecoveryAction
{
    /// <summary>No recovery action is offered (the typed code is displayed only).</summary>
    None = 0,

    /// <summary>
    /// Root-level mismatch: the registry file is readable but the registered root's physical
    /// identity no longer matches. Explicit action = revoke EVERY non-revoked entry of that path,
    /// then re-register the entry's OWN registered root string, then re-run the preview.
    /// </summary>
    ReauthorizeSource = 1,

    /// <summary>
    /// File-level corruption: the read-only <c>source_list_roots</c> probe is itself typed
    /// <c>SOURCE_REGISTRY_UNAVAILABLE</c>. Explicit action = reset the source authorization storage
    /// (second confirmation, discards EVERY source authorization).
    /// </summary>
    ResetRegistry = 2,
}

/// <summary>
/// FEA-11-L-S1-B (AC-LSB-1/2): the sanitized outcome of the read-only diagnosis probe. It carries
/// the typed code (for display), the LEAF name only (never a path) and the number of stale
/// non-revoked entries; it never carries a full path, a locator, a grant or
/// <c>quarantine_path</c>.
/// </summary>
public sealed record SourceRecoveryDiagnosis(
    SourceRecoveryAction Action,
    string? ErrorCode,
    string? SourceLeafName,
    int StaleEntryCount)
{
    public bool HasAction => Action != SourceRecoveryAction.None;

    /// <summary>Typed code only — the recovery face refuses to invent a recovery action for it.</summary>
    public static SourceRecoveryDiagnosis NotApplicable(string? errorCode) =>
        new(SourceRecoveryAction.None, errorCode, null, 0);

    public static SourceRecoveryDiagnosis Reauthorize(string? errorCode, string leafName, int staleEntryCount) =>
        new(SourceRecoveryAction.ReauthorizeSource, errorCode, leafName, staleEntryCount);

    public static SourceRecoveryDiagnosis Reset(string? errorCode) =>
        new(SourceRecoveryAction.ResetRegistry, errorCode, null, 0);
}

/// <summary>
/// FEA-11-L-S1-B (AC-LSB-3/4/7): one explicit recovery attempt's typed outcome. Text carries the
/// LEAF name, typed codes and counts only — never an absolute path and never
/// <c>quarantine_path</c> (C-16 §7.3 conflict is NOT fixed here; the field is simply never read).
/// </summary>
public sealed record SourceRecoveryResult(
    bool Ok,
    string? ErrorCode,
    string Message,
    int RevokedCount,
    int RegisteredCount,
    string? LeafName)
{
    /// <summary>
    /// AC-LSB-4 fail-closed shape: the registry now carries REVOKED entries but no live
    /// replacement. Revocation is an irreversible persisted fact — nothing here rolls it back and
    /// nothing may report success for this state.
    /// </summary>
    public bool RevokedButNotRegistered => RevokedCount > 0 && RegisteredCount == 0;

    public static SourceRecoveryResult Failed(string code) =>
        new(false, code, SourceRecoveryText.Code(code), 0, 0, null);

    public static SourceRecoveryResult Failed(string code, string message) =>
        new(false, code, message, 0, 0, null);
}

/// <summary>
/// FEA-11-L-S1-B: UI text for the explicit recovery face. Every string is composed from the leaf
/// name, a typed code and counts only (AC-LSB-7); no path ever reaches this layer.
/// </summary>
public static class SourceRecoveryText
{
    public static string Code(string? code) => SourceImportText.CodeText(code);

    /// <summary>AC-LSB-2 root-level branch: exactly ONE explicit action is disclosed.</summary>
    public static string ReauthorizeOffer(string? leafName, int staleCount) =>
        (string.IsNullOrEmpty(leafName) ? "该来源" : "来源 " + leafName) +
        " 的授权与文件当前状态不一致：可重新授权此来源（撤销 " + staleCount +
        " 条失效授权 → 按已登记来源重新登记 → 重新预览）。仅限 file-source 同路径恢复。";

    /// <summary>AC-LSB-2 file-level branch: reset discards EVERY authorization — disclose it fully.</summary>
    public static string ResetOffer() =>
        "源授权存储文件级不可用（SOURCE_REGISTRY_UNAVAILABLE）：可重置源授权存储。" +
        "重置会丢弃全部来源授权，所有来源都需要重新授权，且不可撤销；隔离路径不显示。";

    public static string ResetConfirmation() =>
        "确认重置源授权存储？将丢弃全部来源授权（所有来源都需要重新授权），不可撤销。";

    public static string ReauthorizeSucceeded(int revokedCount, int registeredCount, string? leafName) =>
        "已重新授权" + (string.IsNullOrEmpty(leafName) ? "该来源" : "来源 " + leafName) +
        "（撤销 " + revokedCount + " 条失效授权 · 新增 " + registeredCount + " 条授权），请重新预览。";

    /// <summary>AC-LSB-4: revoked but NOT re-authorized — never rendered as success.</summary>
    public static string RevokedNotRegistered(int revokedCount, string? code) =>
        "已撤销 " + revokedCount + " 条失效授权，未重新授权（" + code + "）；可重试。";

    public static string ResetSucceeded() =>
        "已重置源授权存储（全部来源授权已丢弃），请重新预览。";

    public static string ResetRefusedNeedsConfirmation() =>
        "重置源授权存储需要二次确认（INVALID_REQUEST），未做任何更改。";

    public static string NothingToReauthorize() =>
        "没有可撤销的失效授权条目：未做任何更改（SOURCE_REGISTRY_UNAVAILABLE）。";

    public static string ReadOnly() => "Host 处于只读模式：无法重新授权来源（HOST_READ_ONLY）。";

    public static string NotReady() => "Host 尚未就绪：恢复不可用（HOST_NOT_READY）。";

    public static string RevokeFailed(int revokedCount, string code) =>
        "已撤销 " + revokedCount + " 条失效授权，未能完成全部撤销（" + code + "）：未重新授权。";

    public static string ResetFailed(string? code) =>
        "重置源授权存储失败（" + code + "）。";
}

/// <summary>
/// FEA-11-L-S1-B (AC-LSB-6): the exact recovery wire payloads. They reuse ONLY the C-16 v1.4 §1
/// existing root commands — no new command/field/capability/error code:
/// <list type="bullet">
/// <item><c>source_revoke_root</c> = <c>{registry_id}</c>; </item>
/// <item><c>source_register_root</c> = <c>{locator, roots[]}</c>; </item>
/// <item><c>source_reset_registry</c> = <c>{confirm}</c>.</item>
/// </list>
/// </summary>
internal static class SourceRecoveryPayloads
{
    /// <summary>Revokes exactly ONE already-registered entry by its opaque id.</summary>
    public static JsonElement RevokeRoot(string registryId) => Build(writer =>
    {
        writer.WriteStartObject();
        writer.WriteString("registry_id", registryId);
        writer.WriteEndObject();
    });

    /// <summary>
    /// Re-registers ONE root. <paramref name="registeredRoot"/> is the entry's OWN persisted
    /// <c>roots[0]</c> string (AC-LSB-6) — the recovery face accepts no caller path.
    /// </summary>
    public static JsonElement RegisterRoot(string registeredRoot) => Build(writer =>
    {
        writer.WriteStartObject();
        writer.WriteString("locator", registeredRoot);
        writer.WritePropertyName("roots");
        writer.WriteStartArray();
        writer.WriteStringValue(registeredRoot);
        writer.WriteEndArray();
        writer.WriteEndObject();
    });

    /// <summary>Resets the whole registry; the Host requires the explicit confirm bit.</summary>
    public static JsonElement ResetRegistry(bool confirm) => Build(writer =>
    {
        writer.WriteStartObject();
        writer.WriteBoolean("confirm", confirm);
        writer.WriteEndObject();
    });

    private static JsonElement Build(Action<Utf8JsonWriter> write)
    {
        using var stream = new MemoryStream();
        using (var writer = new Utf8JsonWriter(stream))
        {
            write(writer);
        }

        using var document = JsonDocument.Parse(stream.ToArray());
        return document.RootElement.Clone();
    }
}

/// <summary>
/// FEA-11-L-S1-B: one parsed <c>source_list_roots</c> entry. INTERNAL by design — it holds the
/// registered root string only so the orchestrator can (a) match the App's failed selection and
/// (b) re-register that EXACT persisted string; it is never projected into a diagnosis/result/UI
/// text (AC-LSB-7).
/// </summary>
internal sealed record SourceRegistryEntry(
    string RegistryId,
    string Root,
    int Generation,
    bool Revoked);

/// <summary>
/// FEA-11-L-S1-B-RECOVERY-REAUTH-1 (B1; App-only, ZERO contract change, 0/18 pins): the explicit
/// recovery orchestrator behind <see cref="ISourceImportController"/>'s recovery face.
///
/// It never runs on a failure branch by itself: <see cref="DiagnoseAsync"/> only PROBES (read-only
/// <c>source_list_roots</c>) to decide which single explicit action may be offered, and
/// <see cref="ReauthorizeAsync"/>/<see cref="ResetRegistryAsync"/> run only when the user clicks.
///
/// Red line R-1 (AC-LSB-5): the plan/mint path is untouched — this class is the ONLY place that
/// calls <c>source_revoke_root</c>/<c>source_register_root</c> after a mint failure, and it never
/// registers on behalf of a failed mint unless the user explicitly asked for it.
///
/// Red line R-2/R-3: revocation and re-registration are two ordered steps of ONE user action
/// (revoke ALL stale entries of the path FIRST, abort on a failed revoke, register the entry's own
/// registered root afterwards). A partial outcome is reported as revoked-but-not-re-authorized —
/// never as success and never rolled back (revocation is an irreversible persisted fact).
/// </summary>
public sealed class SourceRecoveryCoordinator
{
    /// <summary>The frozen C-16 §6 code used for both branches (zero new codes).</summary>
    public const string RegistryUnavailable = "SOURCE_REGISTRY_UNAVAILABLE";

    private readonly HostCommandDispatcher _commands;
    private readonly Func<bool> _writesAllowed;

    public SourceRecoveryCoordinator(HostCommandDispatcher commands, Func<bool>? writesAllowed = null)
    {
        _commands = commands;
        _writesAllowed = writesAllowed ?? (() => true);
    }

    /// <summary>
    /// AC-LSB-2: the read-only branch decision. Order matters:
    /// <list type="number">
    /// <item>the preview must have failed with the frozen <c>SOURCE_REGISTRY_UNAVAILABLE</c> on the
    /// HOST-side mint leg; any other code (a Core-side code, an unexpected code) offers NOTHING and
    /// no probe runs;</item>
    /// <item>probe <c>source_list_roots</c> (read-only, no writes). A typed
    /// <c>SOURCE_REGISTRY_UNAVAILABLE</c> from the probe itself = FILE-LEVEL → only
    /// <see cref="SourceRecoveryAction.ResetRegistry"/>;</item>
    /// <item>a successful probe = ROOT-LEVEL → only <see cref="SourceRecoveryAction.ReauthorizeSource"/>,
    /// and only when a non-revoked entry actually covers one of the failed sources;</item>
    /// <item>any other probe code (e.g. <c>CORE_CAPABILITY_MISSING</c>/<c>SOURCE_REGISTRY_BUSY</c>)
    /// offers NOTHING and only displays that code.</item>
    /// </list>
    /// </summary>
    public async Task<SourceRecoveryDiagnosis> DiagnoseAsync(
        IReadOnlyList<string>? failedPaths,
        string? failureCode,
        bool hostSideMintFailure,
        CancellationToken cancellationToken = default)
    {
        if (!string.Equals(failureCode, RegistryUnavailable, StringComparison.Ordinal) ||
            !hostSideMintFailure ||
            failedPaths is not { Count: > 0 })
        {
            return SourceRecoveryDiagnosis.NotApplicable(failureCode);
        }

        IReadOnlyList<SourceRegistryEntry> entries;
        try
        {
            entries = await ListEntriesAsync(cancellationToken).ConfigureAwait(false);
        }
        catch (Exception error) when (error is not OutOfMemoryException)
        {
            var probeCode = TypedCodeOf(error);
            return string.Equals(probeCode, RegistryUnavailable, StringComparison.Ordinal)
                ? SourceRecoveryDiagnosis.Reset(probeCode)
                : SourceRecoveryDiagnosis.NotApplicable(probeCode);
        }

        var stale = SelectStaleEntries(entries, failedPaths);
        return stale.Count == 0
            ? SourceRecoveryDiagnosis.NotApplicable(failureCode)
            : SourceRecoveryDiagnosis.Reauthorize(failureCode, LeafName(stale[0].Root), stale.Count);
    }

    /// <summary>
    /// AC-LSB-3/4/5: outcome of the single user action "re-authorize this source".
    ///
    /// EVERY non-revoked entry whose persisted single root equals one of the failed sources is
    /// revoked FIRST (generation+1 + revoked_at, persistent) — the reuse selector only skips
    /// REVOKED entries, so revoking just the first duplicate would leave the same permanent
    /// failure. Only after ALL revokes succeeded is exactly ONE new entry registered per distinct
    /// registered root, using that entry's OWN persisted <c>roots[0]</c> string.
    ///
    /// A revoke failure aborts before any registration (fail-closed: the path stays unusable
    /// rather than gaining a healthy entry behind a stale one). A register failure keeps the
    /// revoked facts and reports revoked-but-not-re-authorized (retryable) — never success and
    /// never a rollback. Repeating the action leaves exactly ONE non-revoked entry for the path.
    /// </summary>
    public async Task<SourceRecoveryResult> ReauthorizeAsync(
        IReadOnlyList<string>? failedPaths,
        CancellationToken cancellationToken = default)
    {
        if (!_writesAllowed())
        {
            return SourceRecoveryResult.Failed("HOST_READ_ONLY", SourceRecoveryText.ReadOnly());
        }

        if (failedPaths is not { Count: > 0 })
        {
            return SourceRecoveryResult.Failed("INVALID_REQUEST");
        }

        IReadOnlyList<SourceRegistryEntry> entries;
        try
        {
            entries = await ListEntriesAsync(cancellationToken).ConfigureAwait(false);
        }
        catch (Exception error) when (error is not OutOfMemoryException)
        {
            // Probe failed: nothing was written. A file-level failure keeps the reset branch open
            // (the diagnosis decides); this action never resets by itself.
            return SourceRecoveryResult.Failed(TypedCodeOf(error));
        }

        var stale = SelectStaleEntries(entries, failedPaths);
        // AC-LSB-4 retry leg: a previous explicit attempt may have completed the revokes and then
        // failed to re-register ("已撤销、未重新授权"). The path is then revoked-only — retrying the
        // SAME explicit action finishes the register leg from the entries' own registered root.
        // This is only reachable from an explicit user action (never from a failure branch).
        var retry = stale.Count == 0 ? SelectRevokedEntries(entries, failedPaths) : Array.Empty<SourceRegistryEntry>();
        if (stale.Count == 0 && retry.Count == 0)
        {
            return new SourceRecoveryResult(
                false, RegistryUnavailable, SourceRecoveryText.NothingToReauthorize(), 0, 0, null);
        }

        var revoked = 0;
        foreach (var entry in stale)
        {
            try
            {
                await RevokeAsync(entry.RegistryId, cancellationToken).ConfigureAwait(false);
                revoked++;
            }
            catch (Exception error) when (error is not OutOfMemoryException)
            {
                var code = TypedCodeOf(error);
                return new SourceRecoveryResult(
                    false, code, SourceRecoveryText.RevokeFailed(revoked, code),
                    revoked, 0, LeafName(entry.Root));
            }
        }

        // Re-registration targets: ONE per distinct persisted root string, in listing order. When a
        // previous attempt already revoked everything, the registered roots come from those revoked
        // entries (the same path's own earlier registration).
        var roots = new List<string>();
        var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        foreach (var entry in stale.Count > 0 ? stale : retry)
        {
            if (seen.Add(entry.Root)) roots.Add(entry.Root);
        }

        var registered = 0;
        foreach (var root in roots)
        {
            try
            {
                await RegisterAsync(root, cancellationToken).ConfigureAwait(false);
                registered++;
            }
            catch (Exception error) when (error is not OutOfMemoryException)
            {
                // AC-LSB-4: revoked but not re-authorized — explicit, retryable, no rollback.
                return new SourceRecoveryResult(
                    false, TypedCodeOf(error),
                    SourceRecoveryText.RevokedNotRegistered(revoked, TypedCodeOf(error)),
                    revoked, registered, LeafName(root));
            }
        }

        return new SourceRecoveryResult(
            true, null,
            SourceRecoveryText.ReauthorizeSucceeded(revoked, registered, LeafName(roots[0])),
            revoked, registered, LeafName(roots[0]));
    }

    /// <summary>
    /// AC-LSB-2/7: resets the source authorization storage (second confirmation at the view-model
    /// level; the wire carries the explicit confirm bit). The response's <c>quarantine_path</c>
    /// (an absolute path, C-16 §7.3 conflict) is NEVER read, returned, logged or rendered.
    /// </summary>
    public async Task<SourceRecoveryResult> ResetRegistryAsync(
        bool confirm,
        CancellationToken cancellationToken = default)
    {
        if (!confirm)
        {
            return SourceRecoveryResult.Failed("INVALID_REQUEST", SourceRecoveryText.ResetRefusedNeedsConfirmation());
        }

        if (!_writesAllowed())
        {
            return SourceRecoveryResult.Failed("HOST_READ_ONLY", SourceRecoveryText.ReadOnly());
        }

        try
        {
            var response = await _commands
                .InvokeAsync("source_reset_registry", SourceRecoveryPayloads.ResetRegistry(true), cancellationToken)
                .ConfigureAwait(false);
            if (!SourceImportJson.ReadBool(response.Value, "reset", false))
            {
                return SourceRecoveryResult.Failed(RegistryUnavailable);
            }

            // Deliberately no read of "quarantine_path" here (or anywhere in the App).
            return new SourceRecoveryResult(true, null, SourceRecoveryText.ResetSucceeded(), 0, 0, null);
        }
        catch (Exception error) when (error is not OutOfMemoryException)
        {
            var code = TypedCodeOf(error);
            return SourceRecoveryResult.Failed(code, SourceRecoveryText.ResetFailed(code));
        }
    }

    private async Task<IReadOnlyList<SourceRegistryEntry>> ListEntriesAsync(CancellationToken cancellationToken)
    {
        var response = await _commands
            .InvokeAsync("source_list_roots", default, cancellationToken)
            .ConfigureAwait(false);
        return ParseRoots(response.Value);
    }

    private async Task RevokeAsync(string registryId, CancellationToken cancellationToken)
    {
        var response = await _commands
            .InvokeAsync("source_revoke_root", SourceRecoveryPayloads.RevokeRoot(registryId), cancellationToken)
            .ConfigureAwait(false);
        if (!SourceImportJson.ReadBool(response.Value, "revoked", false))
        {
            throw new SourceAccessException(RegistryUnavailable);
        }
    }

    private async Task RegisterAsync(string registeredRoot, CancellationToken cancellationToken)
    {
        var response = await _commands
            .InvokeAsync("source_register_root", SourceRecoveryPayloads.RegisterRoot(registeredRoot), cancellationToken)
            .ConfigureAwait(false);
        var id = SourceImportJson.ReadString(response.Value, "registry_id");
        var generation = SourceImportJson.ReadInt(response.Value, "generation");
        if (string.IsNullOrEmpty(id) || generation is null)
        {
            throw new SourceAccessException(RegistryUnavailable);
        }
    }

    /// <summary>
    /// The non-revoked entries whose SINGLE persisted root equals one of the App's failed sources.
    /// Only single-root entries are considered: the import face registers exactly one root per
    /// entry, and re-registering a multi-root entry's first root would silently narrow it.
    /// INTERNAL so the App tests can pin the selector directly (they never see a path through it).
    /// </summary>
    internal static IReadOnlyList<SourceRegistryEntry> SelectStaleEntries(
        IReadOnlyList<SourceRegistryEntry> entries,
        IReadOnlyList<string> paths)
    {
        var targets = new HashSet<string>(
            paths.Select(NormalizeForCompare).Where(path => path.Length > 0),
            StringComparer.OrdinalIgnoreCase);
        var selected = new List<SourceRegistryEntry>();
        foreach (var entry in entries)
        {
            if (entry.Revoked || entry.Root.Length == 0) continue;
            if (targets.Contains(NormalizeForCompare(entry.Root))) selected.Add(entry);
        }

        return selected;
    }

    /// <summary>
    /// Parses the frozen <c>source_list_roots</c> projection
    /// (<c>{entries:[{registry_id, roots[], generation, revoked}]}</c>). Type-mismatched rows are
    /// skipped (they can never be a recovery target); an unavailable/absent shape yields an empty
    /// list, which the caller treats as "nothing to re-authorize" rather than as an error.
    /// </summary>
    internal static IReadOnlyList<SourceRegistryEntry> ParseRoots(JsonElement value)
    {
        var entries = new List<SourceRegistryEntry>();
        if (value.ValueKind != JsonValueKind.Object ||
            !value.TryGetProperty("entries", out var array) ||
            array.ValueKind != JsonValueKind.Array)
        {
            return entries;
        }

        foreach (var entry in array.EnumerateArray())
        {
            if (entry.ValueKind != JsonValueKind.Object) continue;
            var id = SourceImportJson.ReadString(entry, "registry_id");
            var generation = SourceImportJson.ReadInt(entry, "generation");
            if (string.IsNullOrEmpty(id) || generation is null) continue;
            if (!entry.TryGetProperty("roots", out var roots) ||
                roots.ValueKind != JsonValueKind.Array ||
                roots.GetArrayLength() != 1)
            {
                continue;
            }

            var root = roots[0].ValueKind == JsonValueKind.String ? roots[0].GetString() : null;
            if (string.IsNullOrEmpty(root)) continue;
            entries.Add(new SourceRegistryEntry(
                id, root!, generation.Value, SourceImportJson.ReadBool(entry, "revoked", false)));
        }

        return entries;
    }

    /// <summary>
    /// The ALREADY-revoked single-root entries of a failed path. Used ONLY as the retry leg of an
    /// explicit re-authorization after a partial outcome (revokes done, register failed) — never to
    /// resurrect a fresh authorization on a failure branch.
    /// </summary>
    internal static IReadOnlyList<SourceRegistryEntry> SelectRevokedEntries(
        IReadOnlyList<SourceRegistryEntry> entries,
        IReadOnlyList<string> paths)
    {
        var targets = new HashSet<string>(
            paths.Select(NormalizeForCompare).Where(path => path.Length > 0),
            StringComparer.OrdinalIgnoreCase);
        return entries
            .Where(entry => entry.Revoked && entry.Root.Length > 0 && targets.Contains(NormalizeForCompare(entry.Root)))
            .ToList();
    }

    /// <summary>
    /// Leaf display name only — the ONE path-derived string the recovery face may show.
    /// </summary>
    internal static string LeafName(string root)
    {
        if (string.IsNullOrWhiteSpace(root)) return string.Empty;
        var trimmed = root.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        var leaf = Path.GetFileName(trimmed);
        return string.IsNullOrEmpty(leaf) ? string.Empty : leaf;
    }

    /// <summary>
    /// Fail-closed mapping for the recovery face: ANY non-fatal transport/refusal failure becomes a
    /// typed result instead of escaping into the UI (a read-only Host race maps to HOST_READ_ONLY).
    /// </summary>
    private static string TypedCodeOf(Exception error) => error switch
    {
        ReadOnlyHostException readOnly => readOnly.Code,
        _ => SourceImportCoordinator.TypedCode(error),
    };
    private static string NormalizeForCompare(string path)
    {
        if (string.IsNullOrWhiteSpace(path)) return string.Empty;
        try
        {
            return Path.TrimEndingDirectorySeparator(Path.GetFullPath(path));
        }
        catch (Exception error) when (error is ArgumentException or NotSupportedException or PathTooLongException or System.Security.SecurityException)
        {
            return path.Trim();
        }
    }
}
