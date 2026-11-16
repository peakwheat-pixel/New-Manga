using System.Buffers.Binary;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace NewManga.Host.Sources;

public sealed record SourceRoot(string Root, ulong VolumeSerial, ulong FileId, string IdentityVerifiedAt, bool Readable);
public sealed record SourceAuthorization(string RegistryId, string Locator, int Generation, string CreatedAt,
    string LastUsedAt, string? RevokedAt, SourceRoot[] Roots, object? IdentityFacts = null);
internal sealed record RegistrySnapshot(int FormatVersion, string WrittenAt, SourceAuthorization[] Entries);

/// <summary>FEA-13-SRC-6: outcome of merging a restored snapshot into the live registry.</summary>
public sealed record ImportOutcome(int Imported, int Unchanged, int Conflicts, string Status, string? Reason);

/// <summary>Host-only encrypted registry. Every operation reloads under mutex + exclusive lock file.</summary>
public sealed class SourceAccessRegistry
{
    private static readonly byte[] Magic = Encoding.ASCII.GetBytes("NMSAR1\0");
    private static readonly JsonSerializerOptions Json = new() { PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower, PropertyNameCaseInsensitive = false };
    private readonly string _directory;
    private readonly string _lockName;
    private readonly ISecretProtector _protector;
    public string RegistryPath => Path.Combine(_directory, "registry.v1.dat");

    public SourceAccessRegistry(string dataRoot, ISecretProtector? protector = null)
    {
        var normalized = SourceSecurity.Normalize(dataRoot);
        _directory = Path.Combine(normalized, "host", "source-access");
        _protector = protector ?? new DpapiSecretProtector();
        var digest = Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(normalized.ToUpperInvariant()))).ToLowerInvariant()[..16];
        _lockName = "NewManga.Host.SourceAccessRegistry." + digest;
        SourceSecurity.PrivateDirectory(Path.Combine(normalized, "host"));
        SourceSecurity.PrivateDirectory(_directory);
    }

    public SourceAuthorization Register(string locator, IReadOnlyList<string> roots) => Locked(() =>
    {
        var snapshot = Load();
        if (string.IsNullOrWhiteSpace(locator) || roots.Count == 0) throw new SourceAccessException("INVALID_REQUEST");
        var normalized = roots.Select(SourceSecurity.Normalize).ToArray();
        for (var i = 0; i < normalized.Length; i++)
        for (var j = i + 1; j < normalized.Length; j++)
            if (SourceSecurity.Contains(normalized[i], normalized[j]) || SourceSecurity.Contains(normalized[j], normalized[i]))
                throw new SourceAccessException("SOURCE_ACCESS_DENIED");
        var now = DateTimeOffset.UtcNow.ToString("O");
        var authorized = normalized.Select(path =>
        {
            var identity = SourceSecurity.Identity(path);
            return new SourceRoot(path, identity.Volume, identity.Id, now, true);
        }).ToArray();
        var entry = new SourceAuthorization(Guid.NewGuid().ToString("N"), locator, 1, now, now, null, authorized);
        Save(snapshot with { Entries = snapshot.Entries.Append(entry).ToArray() });
        return entry;
    });

    /// <summary>
    /// C-15 v1.5 §5: every entry is returned, including entries whose root is currently
    /// unavailable/replaced. Unavailability is DERIVED at use time (per-request verification in
    /// <see cref="Authorize"/>); it is never persisted and never drops/rewrites an entry, so this
    /// projection stays byte-compatible with the frozen format (no new field, same order).
    /// </summary>
    public SourceAuthorization[] List() => Locked(() => Load().Entries);

    public SourceAuthorization Authorize(string registryId, int expectedGeneration, IReadOnlyList<string> paths) => Locked(() =>
    {
        var snapshot = Load();
        var entry = snapshot.Entries.SingleOrDefault(e => e.RegistryId == registryId)
            ?? throw new SourceAccessException("SOURCE_ACCESS_DENIED");
        if (entry.RevokedAt is not null) throw new SourceAccessException("SOURCE_GRANT_REVOKED");
        if (entry.Generation != expectedGeneration) throw new SourceAccessException("SOURCE_REGISTRY_BUSY");
        // C-15 v1.5 §5 (security core): the registered ROOT identity is re-verified PER REQUEST,
        // inside the same lock and after the fresh read of the registry file. It is never cached
        // across calls, never written back and never used to re-authorize/recover a root.
        //
        // * containment is decided on the REGISTERED root only: a root that is currently missing or
        //   replaced never falls back to "no root", to a parent directory or to another root (a
        //   missing root is never "no authorization" that silently admits the request);
        // * a root that no longer exists / is unreadable / carries a different volume+file identity is
        //   THIS request's typed refusal (the frozen SOURCE_REGISTRY_UNAVAILABLE, zero new codes) with
        //   ZERO persistence — the loop runs before any Save, so the registry bytes stay untouched;
        // * requests whose paths belong to a healthy root are unaffected by an unavailable sibling
        //   root (each covered root is probed at most once per call, no cross-call cache);
        // * the reparse/traversal rejection is unchanged and still fail-closed: it runs once the
        //   covering root is verified, so a healthy root keeps returning SOURCE_ACCESS_DENIED for a
        //   reparse ancestor or a vanished requested path (ordering only changes the code reported for
        //   an UNAVAILABLE root, whose paths can no longer be stat'ed at all).
        var verified = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        foreach (var raw in paths)
        {
            var path = SourceSecurity.Normalize(raw);
            var root = entry.Roots.FirstOrDefault(r => r.Readable && SourceSecurity.Contains(r.Root, path))
                ?? throw new SourceAccessException("SOURCE_ACCESS_DENIED");
            if (verified.Add(root.Root)) VerifyRootIdentity(root);
            SourceSecurity.RejectReparseAncestors(path);
        }
        var used = entry with { LastUsedAt = DateTimeOffset.UtcNow.ToString("O") };
        // Persistence is part of authorization: no grant may escape after a failed write.
        Save(snapshot with { Entries = snapshot.Entries.Select(e => e.RegistryId == registryId ? used : e).ToArray() });
        return used;
    });

    public SourceAuthorization Revoke(string registryId) => Locked(() =>
    {
        var snapshot = Load();
        var entry = snapshot.Entries.SingleOrDefault(e => e.RegistryId == registryId)
            ?? throw new SourceAccessException("SOURCE_ACCESS_DENIED");
        var revoked = entry.RevokedAt is null
            ? entry with { Generation = checked(entry.Generation + 1), RevokedAt = DateTimeOffset.UtcNow.ToString("O") }
            : entry;
        Save(snapshot with { Entries = snapshot.Entries.Select(e => e.RegistryId == registryId ? revoked : e).ToArray() });
        return revoked;
    });

    public string Reset(bool confirm) => Locked(() =>
    {
        if (!confirm) throw new SourceAccessException("INVALID_REQUEST");
        var quarantine = Path.Combine(_directory, "quarantine");
        SourceSecurity.PrivateDirectory(quarantine);
        if (File.Exists(RegistryPath)) File.Move(RegistryPath, Path.Combine(quarantine, Guid.NewGuid().ToString("N") + ".dat"));
        Save(new RegistrySnapshot(1, DateTimeOffset.UtcNow.ToString("O"), []));
        return quarantine;
    });

    /// <summary>
    /// C-15 v1.5 §5: re-verifies ONE registered root against the current file system. This is the
    /// per-request replacement for the eager probe <see cref="Load"/> used to run over every root.
    /// The root must still exist, be readable and carry the registered volume/file identity; any
    /// failure is the request's typed <c>SOURCE_REGISTRY_UNAVAILABLE</c> (zero new error codes).
    /// The probe result is NEVER cached, NEVER persisted and NEVER used to rebuild the identity or
    /// re-authorize the root: recovery stays an explicit user action (`source_reset_registry` for
    /// file-level corruption; re-authorization is out of this card).
    /// </summary>
    private static void VerifyRootIdentity(SourceRoot root)
    {
        (ulong Volume, ulong Id, long Size) identity;
        try { identity = SourceSecurity.Identity(root.Root); }
        catch (Exception error) when (error is not OutOfMemoryException)
        { throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE"); }
        if (identity.Volume != root.VolumeSerial || identity.Id != root.FileId)
            throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE");
    }

    /// <summary>
    /// C-15 v1.5 §5: FILE-LEVEL validation only. magic/version/length/DPAPI/JSON and the persisted
    /// entry STRUCTURE (unique id, generation, normalized+readable roots) decide whether the file is
    /// trustworthy; a root whose CURRENT physical identity is unavailable/mismatched is NOT file
    /// corruption (it is derived per request in <see cref="Authorize"/>), so one deleted/moved source
    /// no longer makes every other entry unreadable. The file-level failure path below is unchanged:
    /// fail-closed <c>SOURCE_REGISTRY_UNAVAILABLE</c>, best-effort <c>.corrupt-&lt;utc&gt;</c> copy of
    /// the original bytes, no empty registry created and the original file never overwritten.
    /// </summary>
    private RegistrySnapshot Load()
    {
        if (!File.Exists(RegistryPath)) return new RegistrySnapshot(1, DateTimeOffset.UtcNow.ToString("O"), []);
        try
        {
            SourceSecurity.RejectReparseAncestors(RegistryPath);
            var bytes = File.ReadAllBytes(RegistryPath);
            return ParseSnapshot(bytes, _protector);
        }
        catch (Exception error) when (error is not OutOfMemoryException)
        {
            try { File.Copy(RegistryPath, RegistryPath + ".corrupt-" + DateTimeOffset.UtcNow.ToString("yyyyMMddHHmmssfffffff"), false); }
            catch (IOException) { }
            catch (UnauthorizedAccessException) { }
            throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE");
        }
    }

    /// <summary>
    /// FEA-13-SRC-6 (C-09 SC-B07 ④): byte-level snapshot parser shared by the live file and
    /// the restore HANDOFF. Magic/length/DPAPI/JSON/shape rules are identical, so a snapshot
    /// that cannot be read as the live file cannot be imported either.
    /// </summary>
    internal static RegistrySnapshot ParseSnapshot(byte[] fileBytes, ISecretProtector protector)
    {
        if (fileBytes.Length < 12 || fileBytes.Length > 4 * 1024 * 1024)
            throw new InvalidDataException();
        if (!fileBytes.AsSpan(0, Magic.Length).SequenceEqual(Magic))
        {
            // A different snapshot version (NMSAR2+) is unsupported, not corrupt.
            if (fileBytes.Length >= Magic.Length
                && fileBytes.AsSpan(0, 5).SequenceEqual(Magic.AsSpan(0, 5)))
                throw new NotSupportedException();
            throw new InvalidDataException();
        }
        var length = BinaryPrimitives.ReadUInt32LittleEndian(fileBytes.AsSpan(Magic.Length, 4));
        var plaintext = protector.Unprotect(fileBytes[(Magic.Length + 4)..]);
        RegistrySnapshot? snapshot;
        try
        {
            if (plaintext.Length != length) throw new InvalidDataException();
            snapshot = JsonSerializer.Deserialize<RegistrySnapshot>(plaintext, Json);
        }
        finally { CryptographicOperations.ZeroMemory(plaintext); }
        if (snapshot is null || snapshot.FormatVersion != 1 || snapshot.Entries is null
            || snapshot.Entries.Select(e => e.RegistryId).Distinct().Count() != snapshot.Entries.Length)
            throw new InvalidDataException();
        foreach (var entry in snapshot.Entries)
        {
            if (entry.Generation < 1 || string.IsNullOrEmpty(entry.RegistryId)
                || entry.Roots is null || entry.Roots.Length == 0)
                throw new InvalidDataException();
            foreach (var root in entry.Roots)
            {
                // Persisted ROOT SHAPE only (a file-format invariant); the root's live
                // identity is deliberately NOT probed here (C-15 v1.5 §5).
                if (root.Root != SourceSecurity.Normalize(root.Root) || !root.Readable)
                    throw new InvalidDataException();
            }
        }
        return snapshot;
    }

    /// <summary>
    /// FEA-13-SRC-6 (AC3/AC4): merge a restored snapshot into the LIVE registry.
    ///
    /// Only entries whose ``registry_id`` does not exist live are imported. A live entry
    /// always wins: a newer/equal generation, a revoked live entry, or a revoked candidate
    /// is a CONFLICT and is never overwritten or revived. A failed validation writes nothing.
    /// </summary>
    public ImportOutcome ImportRestoredSnapshot(byte[] handoffBytes)
    {
        RegistrySnapshot candidate;
        try
        {
            candidate = ParseSnapshot(handoffBytes, _protector);
        }
        catch (CryptographicException)
        {
            // Another Windows user / another machine: DPAPI CurrentUser cannot unprotect.
            return new ImportOutcome(0, 0, 0, "rejected", "dpapi_unprotectable");
        }
        catch (NotSupportedException)
        {
            return new ImportOutcome(0, 0, 0, "rejected", "registry_version_unsupported");
        }
        catch (Exception error) when (error is not OutOfMemoryException)
        {
            return new ImportOutcome(0, 0, 0, "rejected", "registry_corrupt");
        }

        try
        {
            return Locked(() =>
            {
                var live = Load();
                var liveById = live.Entries.ToDictionary(item => item.RegistryId, StringComparer.Ordinal);
                var imported = new List<SourceAuthorization>();
                var unchanged = 0;
                var conflicts = 0;
                foreach (var entry in candidate.Entries)
                {
                    if (!liveById.TryGetValue(entry.RegistryId, out var liveEntry))
                    {
                        imported.Add(entry);
                        continue;
                    }
                    if (liveEntry.RevokedAt is not null || entry.RevokedAt is not null)
                    {
                        conflicts++;
                        continue;
                    }
                    if (liveEntry.Generation >= entry.Generation)
                    {
                        // Live wins. Same generation with identical content is a benign
                        // no-op; a same-generation entry whose roots DIFFER is a conflict
                        // (two divergent histories), and an older candidate is a conflict.
                        var sameShape = liveEntry.Generation == entry.Generation
                            && liveEntry.Roots.Select(root => root.Root)
                                .SequenceEqual(entry.Roots.Select(root => root.Root));
                        if (sameShape) unchanged++;
                        else conflicts++;
                        continue;
                    }
                    unchanged++;
                }
                if (imported.Count == 0)
                {
                    return new ImportOutcome(0, unchanged, conflicts, "unchanged", null);
                }
                Save(new RegistrySnapshot(
                    live.FormatVersion,
                    DateTimeOffset.UtcNow.ToString("O"),
                    live.Entries.Concat(imported).ToArray()));
                return new ImportOutcome(imported.Count, unchanged, conflicts, "imported", null);
            });
        }
        catch (SourceAccessException)
        {
            return new ImportOutcome(0, 0, 0, "rejected", "registry_unavailable");
        }
    }

    /// <summary>FEA-13-SRC-6: does the live registry already know ``registryId``?</summary>
    public bool Contains(string registryId) => Locked(() => Load().Entries.Any(
        entry => string.Equals(entry.RegistryId, registryId, StringComparison.Ordinal)));

    private void Save(RegistrySnapshot snapshot)
    {
        var temporary = Path.Combine(_directory, "registry-" + Guid.NewGuid().ToString("N") + ".tmp");
        try
        {
            SourceSecurity.RejectReparseAncestors(_directory);
            var plaintext = JsonSerializer.SerializeToUtf8Bytes(snapshot with { WrittenAt = DateTimeOffset.UtcNow.ToString("O") }, Json);
            try
            {
                var ciphertext = _protector.Protect(plaintext);
                using (var stream = new FileStream(temporary, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                {
                    stream.Write(Magic);
                    Span<byte> size = stackalloc byte[4];
                    BinaryPrimitives.WriteUInt32LittleEndian(size, checked((uint)plaintext.Length));
                    stream.Write(size);
                    stream.Write(ciphertext);
                    stream.Flush(true);
                }
                if (File.Exists(RegistryPath)) File.Replace(temporary, RegistryPath, null);
                else File.Move(temporary, RegistryPath);
            }
            finally { CryptographicOperations.ZeroMemory(plaintext); }
        }
        catch (Exception error) when (error is not OutOfMemoryException)
        { throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE"); }
        finally
        {
            try { if (File.Exists(temporary)) File.Delete(temporary); }
            catch (IOException) { }
            catch (UnauthorizedAccessException) { }
        }
    }

    /// <summary>
    /// HOST-CONCURRENCY-FLAKY-1 (DSH 2026-11-16): how long a registry operation waits for the
    /// cross-process lock before reporting SOURCE_REGISTRY_BUSY.
    /// </summary>
    /// <remarks>
    /// Every operation reloads the registry under this lock, so two callers in the same process
    /// (e.g. a Host caller and the file watcher thread) are guaranteed to contend. The previous
    /// implementation used <c>WaitOne(0)</c> and a single non-retrying <c>FileShare.None</c> open,
    /// which turned that ordinary contention into an immediate SOURCE_REGISTRY_BUSY -- observed as a
    /// deterministic failure of the Host tests whenever the full fixture set runs in parallel.
    /// SOURCE_REGISTRY_BUSY now means "still busy after a bounded wait", which is what callers can
    /// act on; the lock is still released by the same owner, so mutual exclusion is unchanged.
    /// <para>
    /// Worst-case total wait: this mutex wait (5000 ms) plus the exclusive lock-file retry window in
    /// <see cref="AcquireLockFile"/> (another 5000 ms deadline) ≈ <b>10 s</b>. The two deadlines are
    /// deliberately independent so that a caller which owns the mutex is not also rushed through the
    /// physical file lock; do not report 5 s as the operation's upper bound.
    /// </para>
    /// </remarks>
    internal const int LockWaitMillis = 5000;

    /// <summary>Retry interval while waiting for the exclusive lock file.</summary>
    internal const int LockRetryMillis = 25;

    private T Locked<T>(Func<T> action)
    {
        Mutex mutex;
        try { mutex = new Mutex(false, "Global\\" + _lockName); }
        catch (UnauthorizedAccessException) { mutex = new Mutex(false, "Local\\" + _lockName); }
        using (mutex)
        {
            var acquired = false;
            try
            {
                try { acquired = mutex.WaitOne(LockWaitMillis); }
                catch (AbandonedMutexException) { acquired = true; }
                if (!acquired) throw new SourceAccessException("SOURCE_REGISTRY_BUSY");
                SourceSecurity.RejectReparseAncestors(_directory);
                using (AcquireLockFile()) return action();
            }
            catch (SourceAccessException) { throw; }
            catch (Exception error) when (error is IOException or UnauthorizedAccessException or System.Security.SecurityException)
            { throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE"); }
            finally { if (acquired) mutex.ReleaseMutex(); }
        }
    }

    /// <summary>
    /// Opens registry.v1.lock exclusively, retrying briefly. A transient IOException means another
    /// owner is inside the critical section right now, not that the registry is unusable.
    /// </summary>
    private FileStream AcquireLockFile()
    {
        var path = Path.Combine(_directory, "registry.v1.lock");
        var deadline = Environment.TickCount64 + LockWaitMillis;
        while (true)
        {
            try
            {
                return new FileStream(path, FileMode.OpenOrCreate, FileAccess.ReadWrite, FileShare.None);
            }
            catch (IOException) when (Environment.TickCount64 < deadline)
            {
                Thread.Sleep(LockRetryMillis);
            }
            catch (IOException)
            {
                throw new SourceAccessException("SOURCE_REGISTRY_BUSY");
            }
        }
    }
}
