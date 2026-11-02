using System.Buffers;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using Microsoft.Win32.SafeHandles;

namespace NewManga.Host.Resources;

public enum TileErrorCode
{
    TileManifestInvalid,
    TileGrantNotFound,
    TileGrantExpired,
    TileGrantRevoked,
    TileIndexOutOfRange,
    TilePathOutsideRoot,
    TilePathReparse,
    TileIdentityMismatch,
    TileSizeMismatch,
    TileDigestMismatch,
    TileIoFailure,
}

public sealed class TileAccessException : Exception
{
    public TileAccessException(TileErrorCode code, string detail)
        : base($"[{code}] {detail}")
    {
        Code = code;
    }

    public TileErrorCode Code { get; }

    public string UserMessage => Code switch
    {
        TileErrorCode.TileGrantNotFound => "资源句柄不存在（可能已被回收）。",
        TileErrorCode.TileGrantExpired => "资源授权已过期。",
        TileErrorCode.TileGrantRevoked => "资源授权已撤销。",
        TileErrorCode.TileIndexOutOfRange => "tile 序号超出范围。",
        TileErrorCode.TilePathOutsideRoot => "资源路径越出允许根。",
        TileErrorCode.TilePathReparse => "资源路径包含 junction/reparse point，已拒绝。",
        TileErrorCode.TileIdentityMismatch => "资源文件身份已变化（可能被替换），已拒绝。",
        TileErrorCode.TileSizeMismatch => "资源文件大小与签发的 size 不一致，已拒绝。",
        TileErrorCode.TileDigestMismatch => "tile 内容摘要不符（可能被等长重写/篡改），已拒绝。",
        TileErrorCode.TileManifestInvalid => "tile 清单非法。",
        _ => "资源读取失败。",
    };
}

public sealed record TileDescriptor(int Index, long Offset, int Length, string Sha256);

public sealed record TileGrantRequest(
    string ResourceId,
    string RevisionFingerprint,
    string AbsolutePath,
    string AllowedRoot,
    long Size,
    IReadOnlyList<TileDescriptor> Tiles,
    TimeSpan? Ttl = null,
    long? VolumeSerial = null,
    long? FileIndex = null);

/// <summary>UI-facing grant view: opaque handle + facts, never the OS path or digests.</summary>
public sealed record TileGrantView(
    string Handle,
    string ResourceId,
    string RevisionFingerprint,
    long Size,
    int TileCount,
    DateTimeOffset IssuedAtUtc,
    DateTimeOffset ExpiresAtUtc);

public sealed record TileReadResult(int Index, int Length, byte[] Bytes, bool Sha256Verified);

/// <summary>
/// S5-A tile resource channel (ADR-0002 D1/D2/D4 subset).
/// Security model: issue captures size + file identity + per-tile SHA-256 list from the Core grant;
/// read re-derives the final path from an OS handle, checks containment, file identity, size, and the
/// tile digest before returning bytes; authorization state is cached for at most 1s and a revoke
/// immediately invalidates that cache entry. Paths and digests never leave the Host.
/// </summary>
public sealed class TileChannel
{
    public const int MaxAuthorizationCacheMs = 1000;

    private sealed class Grant
    {
        public required string Handle { get; init; }
        public required string ResourceId { get; init; }
        public required string RevisionFingerprint { get; init; }
        public required string Path { get; init; }
        public required string AllowedRoot { get; init; }
        public required long Size { get; init; }
        public required long VolumeSerial { get; init; }
        public required long FileIndex { get; init; }
        public required IReadOnlyList<TileDescriptor> Tiles { get; init; }
        public required DateTimeOffset IssuedAtUtc { get; init; }
        public required DateTimeOffset ExpiresAtUtc { get; init; }
        public volatile bool Revoked;
    }

    private sealed record CacheEntry(DateTimeOffset CachedAtUtc);

    private readonly Dictionary<string, Grant> _grants = new(StringComparer.Ordinal);
    private readonly Dictionary<string, CacheEntry> _authorizationCache = new(StringComparer.Ordinal);
    private readonly object _gate = new();
    private readonly TimeSpan _cacheTtl;
    private readonly TimeSpan _defaultTtl;

    public TileChannel(TimeSpan? authorizationCacheTtl = null, TimeSpan? defaultGrantTtl = null)
    {
        _cacheTtl = authorizationCacheTtl is { } ttl && ttl > TimeSpan.Zero && ttl <= TimeSpan.FromMilliseconds(MaxAuthorizationCacheMs)
            ? ttl
            : TimeSpan.FromMilliseconds(MaxAuthorizationCacheMs);
        _defaultTtl = defaultGrantTtl ?? TimeSpan.FromMinutes(5);
    }

    public int CacheHits { get; private set; }

    public int CacheMisses { get; private set; }

    public int CacheInvalidations { get; private set; }

    public int Reads { get; private set; }

    public int DigestMismatches { get; private set; }

    public int GrantsIssued { get; private set; }

    public TileGrantView Issue(TileGrantRequest request)
    {
        ValidateRequest(request);
        var fullPath = Path.GetFullPath(request.AbsolutePath);
        var root = Path.GetFullPath(request.AllowedRoot);
        EnsureAllowedRoot(fullPath, root);
        EnsureNoReparse(fullPath, root);

        using var handle = OpenRead(fullPath);
        var identity = FileIdentity.Read(handle);
        if (request.VolumeSerial is { } expectedVolume && expectedVolume != identity.VolumeSerial)
        {
            throw new TileAccessException(TileErrorCode.TileIdentityMismatch, "volume serial differs from the grant manifest");
        }

        if (request.FileIndex is { } expectedIndex && expectedIndex != identity.FileIndex)
        {
            throw new TileAccessException(TileErrorCode.TileIdentityMismatch, "file index differs from the grant manifest");
        }

        var length = RandomAccess.GetLength(handle);
        if (length != request.Size)
        {
            throw new TileAccessException(TileErrorCode.TileSizeMismatch, $"file size {length} != manifest size {request.Size}");
        }

        var handleId = Convert.ToHexString(RandomNumberGenerator.GetBytes(16)).ToLowerInvariant();
        var now = DateTimeOffset.UtcNow;
        var grant = new Grant
        {
            Handle = handleId,
            ResourceId = request.ResourceId,
            RevisionFingerprint = request.RevisionFingerprint,
            Path = fullPath,
            AllowedRoot = root,
            Size = request.Size,
            VolumeSerial = identity.VolumeSerial,
            FileIndex = identity.FileIndex,
            Tiles = request.Tiles.OrderBy(tile => tile.Index).ToArray(),
            IssuedAtUtc = now,
            ExpiresAtUtc = now + (request.Ttl ?? _defaultTtl),
        };

        lock (_gate)
        {
            _grants[handleId] = grant;
            GrantsIssued++;
        }

        return ToView(grant);
    }

    public TileReadResult ReadTile(string handle, int tileIndex)
    {
        var grant = GetGrant(handle);
        EnsureAuthorized(grant);
        if (tileIndex < 0 || tileIndex >= grant.Tiles.Count)
        {
            throw new TileAccessException(TileErrorCode.TileIndexOutOfRange, $"tile {tileIndex} not in 0..{grant.Tiles.Count - 1}");
        }

        var tile = grant.Tiles[tileIndex];
        using var fileHandle = OpenRead(grant.Path);
        var finalPath = FinalPath.FromHandle(fileHandle);
        EnsureAllowedRoot(finalPath, grant.AllowedRoot);
        EnsureNoReparse(finalPath, grant.AllowedRoot);
        var identity = FileIdentity.Read(fileHandle);
        if (identity.VolumeSerial != grant.VolumeSerial || identity.FileIndex != grant.FileIndex)
        {
            throw new TileAccessException(TileErrorCode.TileIdentityMismatch, "file identity changed since issue");
        }

        var length = RandomAccess.GetLength(fileHandle);
        if (length != grant.Size || tile.Offset + tile.Length > grant.Size)
        {
            throw new TileAccessException(TileErrorCode.TileSizeMismatch, "file size changed since issue");
        }

        var buffer = new byte[tile.Length];
        var read = 0;
        while (read < tile.Length)
        {
            var chunk = RandomAccess.Read(fileHandle, buffer.AsSpan(read), tile.Offset + read);
            if (chunk <= 0)
            {
                throw new TileAccessException(TileErrorCode.TileIoFailure, $"short read at tile {tile.Index}");
            }

            read += chunk;
        }

        var digest = Convert.ToHexString(SHA256.HashData(buffer)).ToLowerInvariant();
        if (!CryptographicOperations.FixedTimeEquals(Encoding.ASCII.GetBytes(digest), Encoding.ASCII.GetBytes(tile.Sha256)))
        {
            lock (_gate)
            {
                DigestMismatches++;
            }

            throw new TileAccessException(TileErrorCode.TileDigestMismatch, $"tile {tile.Index} sha256 mismatch");
        }

        lock (_gate)
        {
            Reads++;
        }

        return new TileReadResult(tile.Index, buffer.Length, buffer, Sha256Verified: true);
    }

    /// <summary>Revoke is event-driven: it flips the grant and evicts the cached authorization immediately.</summary>
    public void Revoke(string handle)
    {
        Grant grant;
        lock (_gate)
        {
            if (!_grants.TryGetValue(handle, out var found))
            {
                throw new TileAccessException(TileErrorCode.TileGrantNotFound, "unknown handle");
            }

            grant = found;
            grant.Revoked = true;

            if (_authorizationCache.Remove(handle))
            {
                CacheInvalidations++;
            }
        }
    }

    /// <summary>Authorization probe (no file IO) used to demonstrate the ≤1s cache and revoke invalidation.</summary>
    public bool IsAuthorized(string handle)
    {
        var grant = GetGrant(handle);
        return CheckAuthorization(grant);
    }

    public TileGrantView? Describe(string handle)
    {
        lock (_gate)
        {
            return _grants.TryGetValue(handle, out var grant) ? ToView(grant) : null;
        }
    }

    private bool CheckAuthorization(Grant grant)
    {
        if (grant.Revoked)
        {
            throw new TileAccessException(TileErrorCode.TileGrantRevoked, "grant revoked");
        }

        var now = DateTimeOffset.UtcNow;
        lock (_gate)
        {
            if (_authorizationCache.TryGetValue(grant.Handle, out var cached) &&
                now - cached.CachedAtUtc <= _cacheTtl &&
                now < grant.ExpiresAtUtc)
            {
                CacheHits++;
                return true;
            }

            CacheMisses++;
            _authorizationCache[grant.Handle] = new CacheEntry(now);
        }

        if (now >= grant.ExpiresAtUtc)
        {
            throw new TileAccessException(TileErrorCode.TileGrantExpired, "grant expired");
        }

        return true;
    }

    private void EnsureAuthorized(Grant grant) => CheckAuthorization(grant);

    private Grant GetGrant(string handle)
    {
        lock (_gate)
        {
            return _grants.TryGetValue(handle, out var grant)
                ? grant
                : throw new TileAccessException(TileErrorCode.TileGrantNotFound, "unknown handle");
        }
    }

    private static TileGrantView ToView(Grant grant) => new(
        grant.Handle,
        grant.ResourceId,
        grant.RevisionFingerprint,
        grant.Size,
        grant.Tiles.Count,
        grant.IssuedAtUtc,
        grant.ExpiresAtUtc);

    private static void ValidateRequest(TileGrantRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.ResourceId) ||
            string.IsNullOrWhiteSpace(request.RevisionFingerprint) ||
            string.IsNullOrWhiteSpace(request.AbsolutePath) ||
            string.IsNullOrWhiteSpace(request.AllowedRoot) ||
            request.Size <= 0)
        {
            throw new TileAccessException(TileErrorCode.TileManifestInvalid, "resource_id/revision/path/root/size are required");
        }

        if (request.Tiles.Count == 0)
        {
            throw new TileAccessException(TileErrorCode.TileManifestInvalid, "tile list is empty");
        }

        var seen = new HashSet<int>();
        foreach (var tile in request.Tiles)
        {
            if (tile.Length <= 0 || tile.Offset < 0 || tile.Offset + tile.Length > request.Size)
            {
                throw new TileAccessException(TileErrorCode.TileManifestInvalid, $"tile {tile.Index} range invalid");
            }

            if (!seen.Add(tile.Index))
            {
                throw new TileAccessException(TileErrorCode.TileManifestInvalid, $"duplicate tile index {tile.Index}");
            }

            if (tile.Sha256.Length != 64 || tile.Sha256.Any(character => !Uri.IsHexDigit(character)))
            {
                throw new TileAccessException(TileErrorCode.TileManifestInvalid, $"tile {tile.Index} digest is not 64-hex");
            }
        }
    }

    private static void EnsureAllowedRoot(string path, string root)
    {
        var normalizedRoot = root.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        if (!string.Equals(path, normalizedRoot, StringComparison.OrdinalIgnoreCase) &&
            !path.StartsWith(normalizedRoot + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
        {
            throw new TileAccessException(TileErrorCode.TilePathOutsideRoot, "path escapes the allowed root");
        }
    }

    private static void EnsureNoReparse(string path, string root)
    {
        var normalizedRoot = root.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        var relative = path.Length > normalizedRoot.Length
            ? path[(normalizedRoot.Length + 1)..]
            : string.Empty;
        var current = normalizedRoot;
        foreach (var part in relative.Split(Path.DirectorySeparatorChar, StringSplitOptions.RemoveEmptyEntries))
        {
            current = Path.Combine(current, part);
            if (Directory.Exists(current) || File.Exists(current))
            {
                var attributes = File.GetAttributes(current);
                if ((attributes & FileAttributes.ReparsePoint) != 0)
                {
                    throw new TileAccessException(TileErrorCode.TilePathReparse, $"reparse point component rejected: {part}");
                }
            }
        }
    }

    private static SafeFileHandle OpenRead(string path)
    {
        try
        {
            return File.OpenHandle(path, FileMode.Open, FileAccess.Read, FileShare.Read);
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or ArgumentException)
        {
            throw new TileAccessException(TileErrorCode.TileIoFailure, $"cannot open resource file: {ex.GetType().Name}");
        }
    }
}

internal static class FinalPath
{
    public static string FromHandle(SafeFileHandle handle)
    {
        var builder = new StringBuilder(1024);
        var length = NativeMethods.GetFinalPathNameByHandle(handle, builder, builder.Capacity, 0);
        if (length == 0)
        {
            throw new TileAccessException(TileErrorCode.TileIoFailure, "GetFinalPathNameByHandle failed");
        }

        var path = builder.ToString();
        if (path.StartsWith(@"\\?\UNC\", StringComparison.Ordinal))
        {
            return @"\\" + path[8..];
        }

        return path.StartsWith(@"\\?\", StringComparison.Ordinal) ? path[4..] : path;
    }
}

internal static class FileIdentity
{
    public static (long VolumeSerial, long FileIndex) Read(SafeFileHandle handle)
    {
        if (!NativeMethods.GetFileInformationByHandle(handle, out var info))
        {
            throw new TileAccessException(TileErrorCode.TileIoFailure, "GetFileInformationByHandle failed");
        }

        var index = ((long)info.FileIndexHigh << 32) | info.FileIndexLow;
        return (info.VolumeSerialNumber, index);
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct ByHandleFileInformation
    {
        public uint FileAttributes;
        public long CreationTime;
        public long LastAccessTime;
        public long LastWriteTime;
        public uint VolumeSerialNumber;
        public uint FileSizeHigh;
        public uint FileSizeLow;
        public uint NumberOfLinks;
        public uint FileIndexHigh;
        public uint FileIndexLow;
    }

    private static class NativeMethods
    {
        [DllImport("kernel32.dll", SetLastError = true)]
        public static extern bool GetFileInformationByHandle(SafeFileHandle handle, out ByHandleFileInformation info);
    }
}

internal static class NativeMethods
{
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    public static extern uint GetFinalPathNameByHandle(SafeFileHandle handle, StringBuilder path, int capacity, uint flags);
}
