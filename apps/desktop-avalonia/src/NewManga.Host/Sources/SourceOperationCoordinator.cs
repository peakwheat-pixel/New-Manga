using System.Runtime.InteropServices;
using System.Globalization;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using NewManga.CoreClient;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Wire;

namespace NewManga.Host.Sources;

/// <summary>
/// FEA-11 (C-17 §3.2/§5.2): the Host-side durable journal and acknowledgement
/// coordinator for Source sync operations.
///
/// The Core's business commit is not the end of the operation: the Host must
/// record the authorization and the commit, acknowledge the Core, and be able
/// to recover after a crash. Journal entries live under
/// <c>&lt;DataRoot&gt;/host/source-operations/&lt;operation_id&gt;.v1.dat</c> as
/// <c>"NMSOP1\0" + DPAPI-CurrentUser(JSON)</c>; writes are lock-guarded,
/// flushed and atomically replaced (the C-15 §5 discipline). The journal is a
/// closed shape: no password, no grant material, no source bytes, no absolute
/// paths.
///
/// State machine (C-17 §5.2): started -> host-authorized -> core-committed ->
/// acknowledged; failed / recovered are terminal. Illegal transitions are
/// typed refusals — the journal never silently degrades.
/// </summary>
public sealed class SourceOperationCoordinator
{
    public const string Magic = "NMSOP1\0";

    private const int CryptProtectUiForbidden = 0x1;

    private readonly CoreServiceClient? core;
    private readonly string directory;
    private readonly Func<bool> enabled;
    private readonly SourceAccessRegistry? registry;
    private readonly object gate = new();

    public SourceOperationCoordinator(
        CoreServiceClient? core, string dataRoot, Func<bool>? enabled = null,
        SourceAccessRegistry? registry = null)
    {
        this.core = core;
        directory = Path.Combine(dataRoot, "host", "source-operations");
        this.enabled = enabled ?? (() => true);
        this.registry = registry;
    }

    /// <summary>
    /// FEA-11-HOST-AUTH-2 (C-17 §3.2:161/:169): the FRESH completion material
    /// produced by <see cref="PrepareCompletion"/>. ACK/recovery send this record
    /// (never the authorization the apply journaled); the journal already holds
    /// these bytes before the Core call is made.
    /// </summary>
    public sealed record CompletionMaterial(
        string OperationId,
        string RequestDigest,
        string CommitDigest,
        string HostReceiptId,
        string AuthorizationJson,
        string AuthorizationDigest,
        IReadOnlyList<string> GrantIds);

    /// <summary>One durable operation journal entry (closed shape, C-17 §5.2).</summary>
    public sealed record JournalEntry(
        string OperationId,
        string PlanId,
        string PlanDigest,
        string Kind,
        string RequestDigest,
        string State,
        string? AuthorizationDigest,
        string? AuthorizationJson,
        string? GrantIds,
        string? HostReceiptId,
        string? CommitDigest,
        string? CommitReceiptJson,
        string? ErrorCode,
        bool? Retryable,
        string? AcknowledgedAt,
        string CreatedAt,
        string UpdatedAt);

    /// <summary>FEA-11: begin an operation; the Host journals *before* any
    /// authorization or Core call (C-17 §5.2 durable-first rule).</summary>
    public JournalEntry Begin(
        string planId, string planDigest, string kind, string requestDigest,
        string? operationId = null, IEnumerable<string>? grantIds = null)
    {
        RequireEnabled();
        var now = UtcNow();
        var resolvedId = operationId
            ?? ("op-" + Convert.ToHexString(RandomNumberGenerator.GetBytes(16)).ToLowerInvariant());
        lock (gate)
        {
            if (File.Exists(PathOf(resolvedId)))
            {
                // r2 P2: a re-used operation id must never overwrite durable
                // journal state (an acknowledged op would silently regress).
                throw new SourceAccessException("SOURCE_OPERATION_NOT_FOUND");
            }
        }
        var entry = new JournalEntry(
            OperationId: resolvedId,
            PlanId: planId,
            PlanDigest: planDigest,
            Kind: kind,
            RequestDigest: requestDigest,
            State: "started",
            AuthorizationDigest: null,
            AuthorizationJson: null,
            GrantIds: grantIds is null ? null : string.Join(",", grantIds),
            CommitReceiptJson: null,
            ErrorCode: null,
            Retryable: null,
            HostReceiptId: null,
            CommitDigest: null,
            AcknowledgedAt: null,
            CreatedAt: now,
            UpdatedAt: now);
        Write(entry);
        return entry;
    }

    /// <summary>FEA-11: record the Host authorization facts (the Registry
    /// durable write must already have happened — caller ordering).</summary>
    public JournalEntry Authorize(string operationId, string authorizationJson, string hostReceiptId)
    {
        RequireEnabled();
        lock (gate)
        {
            var entry = Read(operationId);
            RequireState(entry, "started");
            if (string.IsNullOrWhiteSpace(authorizationJson) || string.IsNullOrWhiteSpace(hostReceiptId))
            {
                throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE");
            }
            var next = entry with
            {
                State = "host-authorized",
                AuthorizationDigest = Sha256Hex(authorizationJson),
                AuthorizationJson = authorizationJson,
                HostReceiptId = hostReceiptId,
                UpdatedAt = UtcNow(),
            };
            Write(next);
            return next;
        }
    }

    /// <summary>FEA-11: record a Core commit performed by the caller (the
    /// Host dispatcher owns the Core call; the journal owns durability).</summary>
    public JournalEntry MarkCommitted(
        string operationId, string commitDigest, string? commitReceiptJson = null)
    {
        RequireEnabled();
        lock (gate)
        {
            var entry = Read(operationId);
            RequireState(entry, "host-authorized");
            var next = entry with
            {
                State = "core-committed",
                CommitDigest = commitDigest,
                CommitReceiptJson = commitReceiptJson,
                UpdatedAt = UtcNow(),
            };
            Write(next);
            return next;
        }
    }

    /// <summary>
    /// FEA-11-HOST-AUTH-2 (C-17 §3.2:161/:169): ACK/recovery must NOT replay the
    /// authorization the apply journaled — the Host re-reads the live
    /// <see cref="SourceAccessRegistry"/> under the journal lock, re-authorizes
    /// every committed registry (advancing <c>LastUsedAt</c>), re-mints the SAME
    /// operation id / request digest / host receipt id with the LIVE generation
    /// plus the COMMITTED BASELINE identity digest, guards the reproduced request
    /// digest and persists the fresh <c>AuthorizationJson/AuthorizationDigest</c>
    /// (C-17:160 "先落盘") before the Core is called.
    ///
    /// Deliberately Core-free: the default gate has to prove the fresh path
    /// without a Python Core (<c>CoreServiceClient</c> is sealed).
    /// </summary>
    /// <param name="operationId">The journaled operation.</param>
    /// <param name="recovery">ACK semantics (<c>core-committed</c> only) vs
    /// recovery semantics (<c>core-committed</c>/<c>host-authorized</c>/<c>failed</c>).</param>
    public CompletionMaterial PrepareCompletion(string operationId, bool recovery = false)
    {
        RequireEnabled();
        var accessRegistry = registry
            ?? throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE");
        JournalEntry entry;
        lock (gate)
        {
            entry = Read(operationId);
            if (recovery)
            {
                RequireState(entry, "core-committed", "host-authorized", "failed");
            }
            else
            {
                RequireState(entry, "core-committed");
            }
            if (string.IsNullOrWhiteSpace(entry.AuthorizationJson)
                || string.IsNullOrWhiteSpace(entry.HostReceiptId))
            {
                throw new SourceAccessException("SOURCE_OPERATION_NOT_FOUND");
            }
        }

        var baselines = ReadAuthorizationBaselines(entry, out var previousAuthorizedAt);
        // AC-F1c (C-17:160/:164, limitation 5): the durable Core receipt must
        // still describe THIS operation before any completion is re-authorized.
        VerifyOperationReceipt(entry.CommitReceiptJson, entry, entry.CommitDigest);

        var fresh = new List<Dictionary<string, object?>>();
        var known = accessRegistry.List().ToDictionary(item => item.RegistryId, item => item);
        foreach (var baseline in baselines)
        {
            if (!known.TryGetValue(baseline.RegistryId, out var live))
            {
                // C-17:169 "Registry 丢失拒绝" (a dropped registry would relax the ACK).
                throw new SourceAccessException("SOURCE_ACCESS_DENIED");
            }
            if (live.RevokedAt is not null)
            {
                throw new SourceAccessException("SOURCE_GRANT_REVOKED");
            }
            // C-17:169: a fresh generation may be >= the committed baseline, never below.
            if (baseline.Generation > live.Generation)
            {
                throw new SourceAccessException("SOURCE_GRANT_REVOKED");
            }
            var roots = live.Roots
                .Where(root => root.Readable)
                .Select(root => root.Root)
                .ToArray();
            if (roots.Length == 0)
            {
                throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE");
            }
            // C-17:169 "generation 变大时 Host 必须锁后取得当前明确授权": the
            // CURRENT generation is authorized (SOURCE_GRANT_REVOKED /
            // SOURCE_REGISTRY_BUSY / SOURCE_REGISTRY_UNAVAILABLE are its refusals).
            accessRegistry.Authorize(baseline.RegistryId, live.Generation, roots);
            fresh.Add(new Dictionary<string, object?>
            {
                ["registry_id"] = baseline.RegistryId,
                ["generation"] = live.Generation,
                ["identity_digest"] = baseline.IdentityDigest,
            });
        }

        // The reproducible request digest proves plan/kind/operation identity did
        // not drift since the apply (C-17:169).
        var minted = HostAuthorizationMinter.Mint(
            entry.PlanId, entry.PlanDigest, entry.Kind, fresh,
            now: AuthorizationAfter(previousAuthorizedAt),
            operationId: entry.OperationId,
            hostReceiptId: entry.HostReceiptId);
        if (!string.Equals(minted.RequestDigest, entry.RequestDigest, StringComparison.Ordinal))
        {
            throw new SourceAccessException("SOURCE_SYNC_STATE_CONFLICT");
        }

        var authorizationJson = CanonicalJson.Text(minted.Authorization);
        lock (gate)
        {
            var current = Read(operationId);
            // C-17 §3.2: a concurrent MarkFailed must never be overwritten by the
            // fresh authorization of a state the caller no longer owns.
            if (!string.Equals(current.State, entry.State, StringComparison.Ordinal))
            {
                throw new SourceAccessException("SOURCE_SYNC_STATE_CONFLICT");
            }
            Write(current with
            {
                AuthorizationJson = authorizationJson,
                // C-17 §5.2:264 — journal keeps the wire authorization_digest
                // (<c>sha256(canonical(authorizations))</c>), never a digest of
                // the surrounding envelope.
                AuthorizationDigest = minted.AuthorizationDigest,
                UpdatedAt = UtcNow(),
            });
        }

        return new CompletionMaterial(
            entry.OperationId,
            minted.RequestDigest,
            entry.CommitDigest ?? string.Empty,
            minted.HostReceiptId,
            authorizationJson,
            minted.AuthorizationDigest,
            string.IsNullOrWhiteSpace(entry.GrantIds)
                ? Array.Empty<string>()
                : entry.GrantIds.Split(',', StringSplitOptions.RemoveEmptyEntries));
    }

    /// <summary>FEA-11: Host durable ACK first, then tell the Core; the ACK
    /// opens the read gate (C-17 §3.3) and is idempotent on replay. From
    /// FEA-11-HOST-AUTH-2 on, the wire authorization is the FRESH one.</summary>
    public async Task<JournalEntry> AcknowledgeAsync(
        string operationId, CancellationToken cancellationToken = default)
    {
        RequireEnabled();
        lock (gate)
        {
            var early = Read(operationId);
            if (early.State == "acknowledged") return early;
        }

        // C-17:160/:169 — durable FRESH authorization before any Core frame.
        var material = PrepareCompletion(operationId);
        var client = core ?? throw new SourceAccessException("CORE_UNAVAILABLE");
        using var authorization = JsonDocument.Parse(material.AuthorizationJson);
        await client.SendHostControlAsync(
                "AcknowledgeSourceOperation",
                writer =>
                {
                    // The host-control envelope already opened the payload object
                    // (CompletionRequest fields are written flat — C-17 §5.2).
                    writer.WriteString("operation_id", material.OperationId);
                    writer.WriteString("request_digest", material.RequestDigest);
                    writer.WriteString("commit_digest", material.CommitDigest);
                    writer.WriteString("host_receipt_id", material.HostReceiptId);
                    writer.WriteStartArray("grant_ids");
                    foreach (var grantId in material.GrantIds)
                    {
                        writer.WriteStringValue(grantId);
                    }
                    writer.WriteEndArray();
                    writer.WritePropertyName("authorization");
                    authorization.RootElement.WriteTo(writer);
                },
                TimeSpan.FromSeconds(60),
                client.HostSession,
                cancellationToken)
            .ConfigureAwait(false);

        // The Core accepted the ACK: record the Host-side durable acknowledgement.
        // The state is re-read INSIDE the lock so a concurrent MarkFailed
        // (core-committed -> failed) can never be regressed to acknowledged.
        lock (gate)
        {
            var current = Read(operationId);
            if (current.State != "core-committed")
            {
                throw new SourceAccessException("SOURCE_SYNC_STATE_CONFLICT");
            }
            var next = current with
            {
                State = "acknowledged",
                AcknowledgedAt = UtcNow(),
                UpdatedAt = UtcNow(),
            };
            Write(next);
            return next;
        }
    }

    /// <summary>FEA-11: finish a recovery after a crash (C-17 §5.2); the Core
    /// recovery closes the pending gates, the Host journal records the state.
    /// FEA-11-HOST-AUTH-2: the receipt re-read now VERIFIES every field against
    /// the journal (AC-F1c) and the CompletionRequest carries a FRESH
    /// authorization, never the apply-time one.</summary>
    public async Task<JournalEntry> RecoverAsync(
        string operationId, CancellationToken cancellationToken = default)
    {
        RequireEnabled();
        JournalEntry entry;
        lock (gate)
        {
            entry = Read(operationId);
            if (entry.State == "recovered") return entry;
            RequireState(entry, "core-committed", "host-authorized", "failed");
        }

        var client = core ?? throw new SourceAccessException("CORE_UNAVAILABLE");
        // r3 P1-02: the crash window between the Core COMMIT and the Host
        // MarkCommitted leaves CommitDigest empty. Re-read the Core receipt
        // first (C-17 §3.2) instead of sending an empty digest.
        if (string.IsNullOrWhiteSpace(entry.CommitDigest))
        {
            var lookup = await client.SendAsync(
                    "source_get_operation", 3,
                    writer =>
                    {
                        writer.WriteStartObject();
                        writer.WriteString("operation_id", entry.OperationId);
                        writer.WriteEndObject();
                    },
                    TimeSpan.FromSeconds(60), cancellationToken)
                .ConfigureAwait(false);
            var receiptJson = lookup.Result?.ValueKind == JsonValueKind.Object
                ? lookup.Result.Value.GetRawText()
                : null;
            var commitDigest = lookup.Result?.ValueKind == JsonValueKind.Object
                && lookup.Result.Value.TryGetProperty("commit_digest", out var digest)
                && digest.ValueKind == JsonValueKind.String
                    ? digest.GetString()
                    : throw new SourceAccessException("SOURCE_OPERATION_NOT_FOUND");
            // AC-F1c: the re-read receipt must describe THIS operation before it is
            // persisted — a mismatch leaves the journal byte-identical.
            VerifyOperationReceipt(receiptJson, entry, commitDigest);
            lock (gate)
            {
                var current = Read(entry.OperationId);
                Write(current with
                {
                    CommitDigest = commitDigest,
                    CommitReceiptJson = receiptJson,
                    UpdatedAt = UtcNow(),
                });
            }
        }

        // C-17:160/:169 — durable FRESH authorization before any Core frame.
        var material = PrepareCompletion(operationId, recovery: true);
        using var authorization = JsonDocument.Parse(material.AuthorizationJson);
        await client.SendHostControlAsync(
                "CompleteSourceOperationRecovery",
                writer =>
                {
                    // Flat CompletionRequest fields (the envelope opened `payload`).
                    writer.WriteString("operation_id", material.OperationId);
                    writer.WriteString("request_digest", material.RequestDigest);
                    writer.WriteString("commit_digest", material.CommitDigest);
                    writer.WriteString("host_receipt_id", material.HostReceiptId);
                    writer.WriteStartArray("grant_ids");
                    foreach (var grantId in material.GrantIds)
                    {
                        writer.WriteStringValue(grantId);
                    }
                    writer.WriteEndArray();
                    writer.WritePropertyName("authorization");
                    authorization.RootElement.WriteTo(writer);
                },
                TimeSpan.FromSeconds(60),
                client.HostSession,
                cancellationToken)
            .ConfigureAwait(false);

        lock (gate)
        {
            var current = Read(operationId);
            // core-committed/failed are still recoverable; acknowledged/recovered
            // are terminal (a concurrent completion won the race).
            if (current.State is not ("core-committed" or "host-authorized" or "failed"))
            {
                throw new SourceAccessException("SOURCE_SYNC_STATE_CONFLICT");
            }
            var next = current with { State = "recovered", UpdatedAt = UtcNow() };
            Write(next);
            return next;
        }
    }

    /// <summary>FEA-11: terminal failure record (never a silent drop).</summary>
    /// <summary>C-17 §3.2 line 163: a failed (NEVER committed) operation may be
    /// retried with the same operation/request digest. The caller re-reads the
    /// registry, mints a FRESH HostAuthorization and hands it here so the
    /// journal records the new durable authorization atomically; a already
    /// committed failure must go through recovery instead.</summary>
    public JournalEntry RetryFailed(
        string operationId, string authorizationJson, string hostReceiptId)
    {
        RequireEnabled();
        if (string.IsNullOrWhiteSpace(authorizationJson) || string.IsNullOrWhiteSpace(hostReceiptId))
        {
            throw new SourceAccessException("SOURCE_ACCESS_DENIED");
        }
        lock (gate)
        {
            var entry = Read(operationId);
            RequireState(entry, "failed");
            if (entry.CommitDigest is not null)
            {
                throw new SourceAccessException("SOURCE_SYNC_STATE_CONFLICT");
            }
            if (entry.Retryable == false)
            {
                throw new SourceAccessException("SOURCE_SYNC_STATE_CONFLICT");
            }
            var next = entry with
            {
                State = "host-authorized",
                AuthorizationJson = authorizationJson,
                AuthorizationDigest = Sha256Hex(authorizationJson),
                HostReceiptId = hostReceiptId,
                ErrorCode = null,
                Retryable = null,
                UpdatedAt = UtcNow(),
            };
            Write(next);
            return next;
        }
    }

    public JournalEntry MarkFailed(
        string operationId, string errorCode, bool retryable = true)
    {
        RequireEnabled();
        lock (gate)
        {
            var entry = Read(operationId);
            if (entry.State == "failed") return entry;
            // r3 P1-03: acknowledged/recovered are terminal; failed must never
            // regress them (C-17 §3.2).
            RequireState(entry, "started", "host-authorized", "core-committed");
            // C-17 §3.2: a pre-commit failure is durable with its error_code and
            // retryable flag, so a retry/recovery entry can find it later.
            var next = entry with
            {
                State = "failed",
                ErrorCode = errorCode,
                Retryable = retryable,
                UpdatedAt = UtcNow(),
            };
            Write(next);
            return next;
        }
    }

    public JournalEntry? Get(string operationId)
    {
        var path = PathOf(operationId);
        if (!File.Exists(path)) return null;
        lock (gate)
        {
            return Read(operationId);
        }
    }

    /// <summary>
    /// FEA-11-RESIDUAL-4A AC-R3-1 (AC11-7; C-17 §5.3 lines 255-257): one page
    /// of a committed operation receipt whose binding status is a
    /// management-facing diagnostic (<c>missing</c> / <c>needs_confirmation</c>).
    /// </summary>
    public sealed record BindingDiagnostic(
        string OperationId,
        string PageId,
        string BindingId,
        int BindingVersion,
        string SourceId,
        string VersionId,
        string EntryId,
        string Status);

    /// <summary>
    /// FEA-11-RESIDUAL-4A AC-R3-1: the READ-ONLY diagnostic projection of a
    /// durable operation journal entry.
    ///
    /// It reads the durable journal's <c>CommitReceipt</c> bindings and returns
    /// only the pages whose <c>status</c> is <c>missing</c> or
    /// <c>needs_confirmation</c> (the two management diagnosis states C-17 §5.3
    /// names). It deliberately:
    ///
    /// <list type="bullet">
    /// <item>adds no Core command, capability or wire field — the receipt is
    /// already journaled by <see cref="MarkCommitted"/>;</item>
    /// <item>does not touch <c>IHostController</c> (the C-07 pin stays at
    /// 18/18);</item>
    /// <item>does not widen V(p,t): a missing page keeps whatever visibility
    /// the frozen C-05 P8 rules give it (normally invisible in the reader /
    /// chapter-page projections) and this projection never publishes it;</item>
    /// <item>is operation-scoped by design (the journal is keyed by operation
    /// id; there is no global enumeration).</item>
    /// </list>
    ///
    /// A journal entry without a committed receipt yields an empty projection;
    /// a receipt that is not valid JSON is a typed conflict (a corrupt durable
    /// record is never silently reported as "nothing to diagnose").
    /// </summary>
    public IReadOnlyList<BindingDiagnostic> ListBindingDiagnostics(string operationId)
    {
        var entry = Get(operationId);
        if (entry?.CommitReceiptJson is null) return Array.Empty<BindingDiagnostic>();
        JsonDocument document;
        try
        {
            document = JsonDocument.Parse(entry.CommitReceiptJson);
        }
        catch (JsonException)
        {
            throw new SourceAccessException("SOURCE_SYNC_STATE_CONFLICT");
        }
        using (document)
        {
            var root = document.RootElement;
            if (root.ValueKind != JsonValueKind.Object
                || !root.TryGetProperty("bindings", out var bindings)
                || bindings.ValueKind != JsonValueKind.Array)
            {
                return Array.Empty<BindingDiagnostic>();
            }
            var rows = new List<BindingDiagnostic>();
            foreach (var binding in bindings.EnumerateArray())
            {
                var status = StringField(binding, "status");
                if (status is not ("missing" or "needs_confirmation")) continue;
                rows.Add(new BindingDiagnostic(
                    entry.OperationId,
                    StringField(binding, "page_id") ?? string.Empty,
                    StringField(binding, "binding_id") ?? string.Empty,
                    NumberField(binding, "binding_version"),
                    StringField(binding, "source_id") ?? string.Empty,
                    StringField(binding, "version_id") ?? string.Empty,
                    StringField(binding, "entry_id") ?? string.Empty,
                    status));
            }
            // Deterministic order: the receipt order is not part of the frozen
            // shape, the management projection must be stable.
            rows.Sort((left, right) => string.CompareOrdinal(left.PageId, right.PageId));
            return rows;
        }
    }

    // ------------------------------------------------------- completion material

    private sealed record AuthorizationBaseline(string RegistryId, int Generation, string IdentityDigest);

    /// <summary>
    /// C-17 §5.2 / FEA-11-HOST-AUTH-2: the committed baseline of the apply-time
    /// authorization is the ONLY thing a completion may inherit (registry id +
    /// identity digest); the generation is deliberately re-read live.
    /// </summary>
    private static List<AuthorizationBaseline> ReadAuthorizationBaselines(
        JournalEntry entry, out string? previousAuthorizedAt)
    {
        previousAuthorizedAt = null;
        var baselines = new List<AuthorizationBaseline>();
        try
        {
            using var document = JsonDocument.Parse(entry.AuthorizationJson!);
            var root = document.RootElement;
            if (root.ValueKind != JsonValueKind.Object)
            {
                throw new SourceAccessException("SOURCE_SYNC_STATE_CONFLICT");
            }
            previousAuthorizedAt = StringField(root, "authorized_at");
            if (!root.TryGetProperty("authorizations", out var authorizations)
                || authorizations.ValueKind != JsonValueKind.Array)
            {
                throw new SourceAccessException("SOURCE_SYNC_STATE_CONFLICT");
            }
            foreach (var item in authorizations.EnumerateArray())
            {
                var registryId = StringField(item, "registry_id");
                var identityDigest = StringField(item, "identity_digest");
                var generation = item.ValueKind == JsonValueKind.Object
                    && item.TryGetProperty("generation", out var generationValue)
                    && generationValue.ValueKind == JsonValueKind.Number
                    && generationValue.TryGetInt32(out var parsed)
                        ? parsed
                        : 0;
                if (string.IsNullOrWhiteSpace(registryId)
                    || string.IsNullOrWhiteSpace(identityDigest) || generation < 1)
                {
                    throw new SourceAccessException("SOURCE_SYNC_STATE_CONFLICT");
                }
                baselines.Add(new AuthorizationBaseline(registryId, generation, identityDigest));
            }
            if (!string.Equals(StringField(root, "operation_id"), entry.OperationId,
                    StringComparison.Ordinal)
                || !string.Equals(StringField(root, "request_digest"), entry.RequestDigest,
                    StringComparison.Ordinal)
                || !string.Equals(StringField(root, "host_receipt_id"), entry.HostReceiptId,
                    StringComparison.Ordinal))
            {
                throw new SourceAccessException("SOURCE_SYNC_STATE_CONFLICT");
            }
        }
        catch (JsonException)
        {
            throw new SourceAccessException("SOURCE_SYNC_STATE_CONFLICT");
        }
        if (baselines.Count == 0)
        {
            throw new SourceAccessException("SOURCE_SYNC_STATE_CONFLICT");
        }
        return baselines;
    }

    /// <summary>
    /// C-17:169 requires a re-signed <c>authorized_at</c>. The millisecond clock
    /// is coarse enough that a fast ACK could otherwise carry the apply timestamp
    /// verbatim, so the fresh stamp is forced strictly later than the previous one.
    /// </summary>
    private static DateTimeOffset? AuthorizationAfter(string? previousAuthorizedAt)
    {
        if (previousAuthorizedAt is null) return null;
        if (!DateTimeOffset.TryParse(previousAuthorizedAt, CultureInfo.InvariantCulture,
                DateTimeStyles.AdjustToUniversal, out var previous))
        {
            return null;
        }
        return DateTimeOffset.UtcNow <= previous ? previous.AddMilliseconds(1) : null;
    }

    /// <summary>
    /// FEA-11-HOST-AUTH-2 AC-F1c (C-17 §3.2:160/:164, limitation 5): the durable
    /// Core operation receipt is re-checked against the journal before any
    /// completion. Any mismatch is a typed refusal with ZERO journal writes.
    /// </summary>
    private static void VerifyOperationReceipt(
        string? receiptJson, JournalEntry entry, string? commitDigest)
    {
        if (string.IsNullOrWhiteSpace(receiptJson)) return;
        JsonDocument document;
        try
        {
            document = JsonDocument.Parse(receiptJson);
        }
        catch (JsonException)
        {
            throw new SourceAccessException("SOURCE_SYNC_STATE_CONFLICT");
        }
        using (document)
        {
            var row = document.RootElement;
            if (row.ValueKind != JsonValueKind.Object)
            {
                throw new SourceAccessException("SOURCE_SYNC_STATE_CONFLICT");
            }
            RequireReceiptValue(row, "operation_id", entry.OperationId);
            RequireReceiptValue(row, "plan_id", entry.PlanId);
            RequireReceiptValue(row, "plan_digest", entry.PlanDigest);
            RequireReceiptValue(row, "request_digest", entry.RequestDigest);
            RequireReceiptValue(row, "kind", entry.Kind);
            if (!string.IsNullOrWhiteSpace(commitDigest))
            {
                RequireReceiptValue(row, "commit_digest", commitDigest);
            }
            // Only a committed (not yet completed) operation may be completed.
            var state = StringField(row, "state");
            if (state is not ("core-committed" or "failed"))
            {
                throw new SourceAccessException("SOURCE_SYNC_STATE_CONFLICT");
            }
            if (row.TryGetProperty("commit", out var commit)
                && commit.ValueKind == JsonValueKind.Object)
            {
                RequireReceiptValue(commit, "operation_id", entry.OperationId);
                RequireReceiptValue(commit, "plan_id", entry.PlanId);
                RequireReceiptValue(commit, "plan_digest", entry.PlanDigest);
                RequireReceiptValue(commit, "request_digest", entry.RequestDigest);
            }
        }
    }

    private static void RequireReceiptValue(JsonElement element, string field, string expected)
    {
        if (!string.Equals(StringField(element, field), expected, StringComparison.Ordinal))
        {
            throw new SourceAccessException("SOURCE_SYNC_STATE_CONFLICT");
        }
    }

    private static string? StringField(JsonElement element, string key) =>
        element.ValueKind == JsonValueKind.Object
        && element.TryGetProperty(key, out var value)
        && value.ValueKind == JsonValueKind.String
            ? value.GetString()
            : null;

    private static int NumberField(JsonElement element, string key) =>
        element.ValueKind == JsonValueKind.Object
        && element.TryGetProperty(key, out var value)
        && value.ValueKind == JsonValueKind.Number
        && value.TryGetInt32(out var parsed)
            ? parsed
            : 0;

    // ------------------------------------------------------------- journal

    private void RequireEnabled()
    {
        if (!enabled()) throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE");
        if (!OperatingSystem.IsWindows())
        {
            throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE");
        }
    }

    private static void RequireState(JournalEntry entry, params string[] allowed)
    {
        if (Array.IndexOf(allowed, entry.State) < 0)
        {
            throw new SourceAccessException("SOURCE_OPERATION_NOT_FOUND");
        }
    }

    private JournalEntry EnsureAuthorized(string operationId)
    {
        lock (gate)
        {
            var entry = Read(operationId);
            RequireState(entry, "host-authorized");
            return entry;
        }
    }

    private string PathOf(string operationId)
    {
        if (!IsSafeId(operationId)) throw new SourceAccessException("SOURCE_OPERATION_NOT_FOUND");
        return Path.Combine(directory, operationId + ".v1.dat");
    }

    private static bool IsSafeId(string value) =>
        value.Length is > 0 and <= 128 &&
        value.All(c => char.IsAsciiLetterOrDigit(c) || c is '-' or '_');

    private void Write(JournalEntry entry)
    {
        Directory.CreateDirectory(directory);
        var payload = JsonSerializer.SerializeToUtf8Bytes(entry);
        var protectedBytes = Protect(payload);
        var magic = Encoding.ASCII.GetBytes(Magic);
        var body = new byte[magic.Length + protectedBytes.Length];
        magic.CopyTo(body, 0);
        protectedBytes.CopyTo(body, magic.Length);
        var path = PathOf(entry.OperationId);
        var temporary = path + ".tmp-" + Guid.NewGuid().ToString("N");
        try
        {
            using (var stream = new FileStream(temporary, FileMode.CreateNew, FileAccess.Write,
                       FileShare.None, 4096, FileOptions.WriteThrough))
            {
                stream.Write(body);
                stream.Flush(true);
            }
            File.Move(temporary, path, overwrite: true);
        }
        finally
        {
            CryptographicOperations.ZeroMemory(payload);
            CryptographicOperations.ZeroMemory(protectedBytes);
            CryptoSafeDelete(temporary);
        }
    }

    private JournalEntry Read(string operationId)
    {
        var path = PathOf(operationId);
        if (!File.Exists(path)) throw new SourceAccessException("SOURCE_OPERATION_NOT_FOUND");
        var body = File.ReadAllBytes(path);
        var magic = Encoding.ASCII.GetBytes(Magic);
        if (body.Length <= magic.Length || !body.AsSpan(0, magic.Length).SequenceEqual(magic))
        {
            throw new SourceAccessException("SOURCE_OPERATION_NOT_FOUND");
        }
        var payload = Unprotect(body[magic.Length..]);
        try
        {
            var entry = JsonSerializer.Deserialize<JournalEntry>(payload);
            if (entry is null || entry.OperationId != operationId)
            {
                throw new SourceAccessException("SOURCE_OPERATION_NOT_FOUND");
            }
            return entry;
        }
        catch (JsonException)
        {
            throw new SourceAccessException("SOURCE_OPERATION_NOT_FOUND");
        }
        finally
        {
            CryptographicOperations.ZeroMemory(payload);
        }
    }

    // ------------------------------------------------------------- DPAPI

    [StructLayout(LayoutKind.Sequential)]
    private struct DataBlob
    {
        public int cbData;
        public IntPtr pbData;
    }

    [DllImport("crypt32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern bool CryptProtectData(
        ref DataBlob pDataIn, string? szDataDescr, ref DataBlob pOptionalEntropy,
        IntPtr pvReserved, IntPtr pPromptStruct, int dwFlags, out DataBlob pDataOut);

    [DllImport("crypt32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern bool CryptUnprotectData(
        ref DataBlob pDataIn, IntPtr ppszDataDescr, ref DataBlob pOptionalEntropy,
        IntPtr pvReserved, IntPtr pPromptStruct, int dwFlags, out DataBlob pDataOut);

    [DllImport("kernel32.dll")]
    private static extern IntPtr LocalFree(IntPtr hMem);

    private static byte[] Protect(byte[] plain)
    {
        var input = new DataBlob { cbData = plain.Length, pbData = Marshal.AllocHGlobal(plain.Length) };
        try
        {
            Marshal.Copy(plain, 0, input.pbData, plain.Length);
            var entropy = default(DataBlob);
            if (!CryptProtectData(ref input, Magic, ref entropy, IntPtr.Zero, IntPtr.Zero,
                    CryptProtectUiForbidden, out var output))
            {
                throw new CryptographicException("DPAPI protect failed");
            }
            try
            {
                var result = new byte[output.cbData];
                Marshal.Copy(output.pbData, result, 0, output.cbData);
                return result;
            }
            finally
            {
                LocalFree(output.pbData);
            }
        }
        finally
        {
            CryptographicOperations.ZeroMemory(plain);
            Marshal.FreeHGlobal(input.pbData);
        }
    }

    private static byte[] Unprotect(byte[] encrypted)
    {
        var input = new DataBlob { cbData = encrypted.Length, pbData = Marshal.AllocHGlobal(encrypted.Length) };
        try
        {
            Marshal.Copy(encrypted, 0, input.pbData, encrypted.Length);
            var entropy = default(DataBlob);
            if (!CryptUnprotectData(ref input, IntPtr.Zero, ref entropy, IntPtr.Zero, IntPtr.Zero,
                    CryptProtectUiForbidden, out var output))
            {
                throw new CryptographicException("DPAPI unprotect failed");
            }
            try
            {
                var result = new byte[output.cbData];
                Marshal.Copy(output.pbData, result, 0, output.cbData);
                return result;
            }
            finally
            {
                LocalFree(output.pbData);
            }
        }
        finally
        {
            Marshal.FreeHGlobal(input.pbData);
        }
    }

    private static string Sha256Hex(string value) =>
        Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(value))).ToLowerInvariant();

    private static string UtcNow() =>
        DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffZ", CultureInfo.InvariantCulture);

    private static void CryptoSafeDelete(string path)
    {
        try { if (File.Exists(path)) File.Delete(path); } catch { /* best effort */ }
    }
}
