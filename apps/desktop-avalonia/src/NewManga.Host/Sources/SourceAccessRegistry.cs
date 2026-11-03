using System.Buffers.Binary;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace NewManga.Host.Sources;

public sealed record SourceRoot(string Root, ulong VolumeSerial, ulong FileId, string IdentityVerifiedAt, bool Readable);
public sealed record SourceAuthorization(string RegistryId, string Locator, int Generation, string CreatedAt,
    string LastUsedAt, string? RevokedAt, SourceRoot[] Roots, object? IdentityFacts = null);
internal sealed record RegistrySnapshot(int FormatVersion, string WrittenAt, SourceAuthorization[] Entries);

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

    public SourceAuthorization[] List() => Locked(() => Load().Entries);

    public SourceAuthorization Authorize(string registryId, int expectedGeneration, IReadOnlyList<string> paths) => Locked(() =>
    {
        var snapshot = Load();
        var entry = snapshot.Entries.SingleOrDefault(e => e.RegistryId == registryId)
            ?? throw new SourceAccessException("SOURCE_ACCESS_DENIED");
        if (entry.RevokedAt is not null) throw new SourceAccessException("SOURCE_GRANT_REVOKED");
        if (entry.Generation != expectedGeneration) throw new SourceAccessException("SOURCE_REGISTRY_BUSY");
        foreach (var raw in paths)
        {
            var path = SourceSecurity.Normalize(raw);
            SourceSecurity.RejectReparseAncestors(path);
            if (!entry.Roots.Any(r => r.Readable && SourceSecurity.Contains(r.Root, path)))
                throw new SourceAccessException("SOURCE_ACCESS_DENIED");
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

    private RegistrySnapshot Load()
    {
        if (!File.Exists(RegistryPath)) return new RegistrySnapshot(1, DateTimeOffset.UtcNow.ToString("O"), []);
        try
        {
            SourceSecurity.RejectReparseAncestors(RegistryPath);
            var bytes = File.ReadAllBytes(RegistryPath);
            if (bytes.Length < 12 || bytes.Length > 4 * 1024 * 1024 || !bytes.AsSpan(0, Magic.Length).SequenceEqual(Magic))
                throw new InvalidDataException();
            var length = BinaryPrimitives.ReadUInt32LittleEndian(bytes.AsSpan(Magic.Length, 4));
            var plaintext = _protector.Unprotect(bytes[(Magic.Length + 4)..]);
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
                if (entry.Generation < 1 || string.IsNullOrEmpty(entry.RegistryId) || entry.Roots is null || entry.Roots.Length == 0)
                    throw new InvalidDataException();
                foreach (var root in entry.Roots)
                {
                    if (root.Root != SourceSecurity.Normalize(root.Root) || !root.Readable) throw new InvalidDataException();
                    var identity = SourceSecurity.Identity(root.Root);
                    if (identity.Volume != root.VolumeSerial || identity.Id != root.FileId) throw new InvalidDataException();
                }
            }
            return snapshot;
        }
        catch (Exception error) when (error is not OutOfMemoryException)
        {
            try { File.Copy(RegistryPath, RegistryPath + ".corrupt-" + DateTimeOffset.UtcNow.ToString("yyyyMMddHHmmssfffffff"), false); }
            catch (IOException) { }
            catch (UnauthorizedAccessException) { }
            throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE");
        }
    }

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
                try { acquired = mutex.WaitOne(0); }
                catch (AbandonedMutexException) { acquired = true; }
                if (!acquired) throw new SourceAccessException("SOURCE_REGISTRY_BUSY");
                SourceSecurity.RejectReparseAncestors(_directory);
                FileStream fileLock;
                try { fileLock = new FileStream(Path.Combine(_directory, "registry.v1.lock"), FileMode.OpenOrCreate, FileAccess.ReadWrite, FileShare.None); }
                catch (IOException) { throw new SourceAccessException("SOURCE_REGISTRY_BUSY"); }
                using (fileLock) return action();
            }
            catch (SourceAccessException) { throw; }
            catch (Exception error) when (error is IOException or UnauthorizedAccessException or System.Security.SecurityException)
            { throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE"); }
            finally { if (acquired) mutex.ReleaseMutex(); }
        }
    }
}
