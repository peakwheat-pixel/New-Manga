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
    private readonly object gate = new();

    public SourceOperationCoordinator(
        CoreServiceClient? core, string dataRoot, Func<bool>? enabled = null)
    {
        this.core = core;
        directory = Path.Combine(dataRoot, "host", "source-operations");
        this.enabled = enabled ?? (() => true);
    }

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

    /// <summary>FEA-11: Host durable ACK first, then tell the Core; the ACK
    /// opens the read gate (C-17 §3.3) and is idempotent on replay.</summary>
    public async Task<JournalEntry> AcknowledgeAsync(
        string operationId, CancellationToken cancellationToken = default)
    {
        RequireEnabled();
        JournalEntry committed;
        lock (gate)
        {
            committed = Read(operationId);
            if (committed.State == "acknowledged") return committed;
            RequireState(committed, "core-committed");
        }

        var client = core ?? throw new SourceAccessException("CORE_UNAVAILABLE");
        var authorizationJson = committed.AuthorizationJson
            ?? throw new SourceAccessException("SOURCE_OPERATION_NOT_FOUND");
        using var authorization = JsonDocument.Parse(authorizationJson);
        var grantIds = string.IsNullOrWhiteSpace(committed.GrantIds)
            ? Array.Empty<string>()
            : committed.GrantIds.Split(',', StringSplitOptions.RemoveEmptyEntries);
        await client.SendHostControlAsync(
                "AcknowledgeSourceOperation",
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("operation_id", committed.OperationId);
                    writer.WriteString("request_digest", committed.RequestDigest);
                    writer.WriteString("commit_digest", committed.CommitDigest ?? string.Empty);
                    writer.WriteString("host_receipt_id", committed.HostReceiptId ?? string.Empty);
                    writer.WriteStartArray("grant_ids");
                    foreach (var grantId in grantIds)
                    {
                        writer.WriteStringValue(grantId);
                    }
                    writer.WriteEndArray();
                    writer.WritePropertyName("authorization");
                    authorization.RootElement.WriteTo(writer);
                    writer.WriteEndObject();
                },
                TimeSpan.FromSeconds(60),
                client.HostSession,
                cancellationToken)
            .ConfigureAwait(false);

        // The Core accepted the ACK: record the Host-side durable acknowledgement.
        lock (gate)
        {
            var current = Read(operationId);
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
    /// recovery closes the pending gates, the Host journal records the state.</summary>
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
        var authorizationJson = entry.AuthorizationJson
            ?? throw new SourceAccessException("SOURCE_OPERATION_NOT_FOUND");
        // r3 P1-02: the crash window between the Core COMMIT and the Host
        // MarkCommitted leaves CommitDigest empty. Re-read the Core receipt
        // first (C-17 §3.2) instead of sending an empty digest.
        var commitDigest = entry.CommitDigest;
        if (string.IsNullOrWhiteSpace(commitDigest))
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
            commitDigest = lookup.Result?.ValueKind == JsonValueKind.Object
                && lookup.Result.Value.TryGetProperty("commit_digest", out var digest)
                && digest.ValueKind == JsonValueKind.String
                    ? digest.GetString()
                    : throw new SourceAccessException("SOURCE_OPERATION_NOT_FOUND");
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
        using var authorization = JsonDocument.Parse(authorizationJson);
        var grantIds = string.IsNullOrWhiteSpace(entry.GrantIds)
            ? Array.Empty<string>()
            : entry.GrantIds.Split(',', StringSplitOptions.RemoveEmptyEntries);
        await client.SendHostControlAsync(
                "CompleteSourceOperationRecovery",
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("operation_id", entry.OperationId);
                    writer.WriteString("request_digest", entry.RequestDigest);
                    writer.WriteString("commit_digest", commitDigest ?? string.Empty);
                    writer.WriteString("host_receipt_id", entry.HostReceiptId ?? string.Empty);
                    writer.WriteStartArray("grant_ids");
                    foreach (var grantId in grantIds)
                    {
                        writer.WriteStringValue(grantId);
                    }
                    writer.WriteEndArray();
                    writer.WritePropertyName("authorization");
                    authorization.RootElement.WriteTo(writer);
                    writer.WriteEndObject();
                },
                TimeSpan.FromSeconds(60),
                client.HostSession,
                cancellationToken)
            .ConfigureAwait(false);

        lock (gate)
        {
            var current = Read(operationId);
            var next = current with { State = "recovered", UpdatedAt = UtcNow() };
            Write(next);
            return next;
        }
    }

    /// <summary>FEA-11: terminal failure record (never a silent drop).</summary>
    /// <summary>C-17 §3.2 line 163: a failed (never committed) operation may be
    /// retried with the same operation/request digest; the journal goes back to
    /// host-authorized and the Core dispatch is re-run by the caller.</summary>
    public JournalEntry RetryFailed(string operationId)
    {
        RequireEnabled();
        lock (gate)
        {
            var entry = Read(operationId);
            RequireState(entry, "failed");
            if (entry.Retryable == false)
            {
                throw new SourceAccessException("SOURCE_SYNC_STATE_CONFLICT");
            }
            var next = entry with
            {
                State = "host-authorized",
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
