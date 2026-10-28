using System.Buffers;
using System.Diagnostics;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using NewManga.Host.Resources;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// S5-A D4 subset: issue/read/revoke tile channel, ≤1s authorization cache with revoke invalidation,
/// containment (out-of-root + junction), equal-length rewrite / tampered tile / identity change rejection,
/// plus cold-read performance and digest overhead accounting.
/// </summary>
public sealed class TileChannelTests : IDisposable
{
    private const int TileSize = 64 * 1024;
    private const int TileCount = 4;
    private readonly string _root;
    private readonly string _allowedRoot;
    private readonly string _filePath;

    public TileChannelTests()
    {
        _root = Path.Combine(Path.GetTempPath(), "nm-tile-" + Guid.NewGuid().ToString("N")[..10]);
        _allowedRoot = Path.Combine(_root, "allowed");
        Directory.CreateDirectory(_allowedRoot);
        _filePath = Path.Combine(_allowedRoot, "page.bin");
        var bytes = new byte[TileSize * TileCount];
        Random.Shared.NextBytes(bytes);
        File.WriteAllBytes(_filePath, bytes);
    }

    public void Dispose()
    {
        try
        {
            Directory.Delete(_root, recursive: true);
        }
        catch (IOException)
        {
            // best effort temp cleanup
        }
    }

    private static string Sha(byte[] bytes) => Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();

    private static IReadOnlyList<TileDescriptor> Manifest(byte[] all)
    {
        var list = new List<TileDescriptor>();
        for (var index = 0; index < TileCount; index++)
        {
            var slice = all.AsSpan(index * TileSize, TileSize).ToArray();
            list.Add(new TileDescriptor(index, (long)index * TileSize, TileSize, Sha(slice)));
        }

        return list;
    }

    private TileGrantRequest Request(string? path = null, string? root = null, TimeSpan? ttl = null)
    {
        var all = File.ReadAllBytes(_filePath);
        return new TileGrantRequest(
            ResourceId: "page:test",
            RevisionFingerprint: "rev-1",
            AbsolutePath: path ?? _filePath,
            AllowedRoot: root ?? _allowedRoot,
            Size: all.Length,
            Tiles: Manifest(all),
            Ttl: ttl);
    }

    private static string Code(Action action)
    {
        try
        {
            action();
            return "NO_ERROR";
        }
        catch (TileAccessException ex)
        {
            return ex.Code.ToString();
        }
    }

    [Fact]
    public void Issue_Read_Revoke_TypedAndUiSafe()
    {
        var channel = new TileChannel();
        var view = channel.Issue(Request());
        Assert.Equal(32, view.Handle.Length);
        Assert.DoesNotContain(_allowedRoot, view.ToString(), StringComparison.OrdinalIgnoreCase);
        Assert.DoesNotContain("sha256", view.ToString(), StringComparison.OrdinalIgnoreCase);

        var read = channel.ReadTile(view.Handle, 0);
        Assert.True(read.Sha256Verified);
        Assert.Equal(File.ReadAllBytes(_filePath).AsSpan(0, TileSize).ToArray(), read.Bytes);

        channel.Revoke(view.Handle);
        var afterRevoke = Code(() => channel.ReadTile(view.Handle, 0));
        var probe = Code(() => channel.IsAuthorized(view.Handle));
        Assert.Equal("TileGrantRevoked", afterRevoke);
        Assert.Equal("TileGrantRevoked", probe);
        WriteEvidence("security/issue-read-revoke.json", writer =>
        {
            writer.WriteString("ac", "AC1");
            writer.WriteString("handle_opaque", view.Handle);
            writer.WriteNumber("tile_count", view.TileCount);
            writer.WriteNumber("size", view.Size);
            writer.WriteString("after_revoke", afterRevoke);
            writer.WriteBoolean("ui_view_exposes_no_path_or_digest", true);
        });
    }

    [Fact]
    public void AuthorizationCache_HitsWithinOneSecond_AndRevokeInvalidatesImmediately()
    {
        var channel = new TileChannel(TimeSpan.FromMilliseconds(1000));
        var view = channel.Issue(Request());

        Assert.True(channel.IsAuthorized(view.Handle));
        Assert.True(channel.IsAuthorized(view.Handle));
        Assert.True(channel.IsAuthorized(view.Handle));
        Assert.True(channel.CacheHits >= 2, $"expected cache hits, got {channel.CacheHits}");
        var hitRate = (double)channel.CacheHits / (channel.CacheHits + channel.CacheMisses);

        var revokeWatch = Stopwatch.StartNew();
        channel.Revoke(view.Handle);
        var rejectedAt = Code(() => channel.ReadTile(view.Handle, 0));
        revokeWatch.Stop();
        Assert.Equal("TileGrantRevoked", rejectedAt);
        Assert.True(revokeWatch.Elapsed.TotalMilliseconds < 1000, "revoke must take effect in <=1s");
        Assert.True(channel.CacheInvalidations >= 1);

        WriteEvidence("security/cache-revoke.json", writer =>
        {
            writer.WriteString("ac", "AC2");
            writer.WriteNumber("cache_ttl_ms", 1000);
            writer.WriteNumber("cache_hits", channel.CacheHits);
            writer.WriteNumber("cache_misses", channel.CacheMisses);
            writer.WriteNumber("cache_hit_rate", Math.Round(hitRate, 4));
            writer.WriteNumber("revoke_effective_latency_ms", Math.Round(revokeWatch.Elapsed.TotalMilliseconds, 3));
            writer.WriteBoolean("revoke_latency_le_1s", revokeWatch.Elapsed.TotalMilliseconds < 1000);
            writer.WriteNumber("cache_invalidations", channel.CacheInvalidations);
            writer.WriteString("after_revoke", rejectedAt);
        });
    }

    [Fact]
    public void Expiry_RejectsAfterTtl()
    {
        var channel = new TileChannel();
        var view = channel.Issue(Request(ttl: TimeSpan.FromMilliseconds(80)));
        Assert.True(channel.IsAuthorized(view.Handle));
        Thread.Sleep(150);
        var code = Code(() => channel.ReadTile(view.Handle, 0));
        Assert.Equal("TileGrantExpired", code);
        WriteEvidence("security/expiry.json", writer =>
        {
            writer.WriteString("ac", "AC2");
            writer.WriteNumber("grant_ttl_ms", 80);
            writer.WriteNumber("waited_ms", 150);
            writer.WriteString("after_expiry", code);
        });
    }

    [Fact]
    public void Containment_OutsideRoot_And_Junction_Rejected()
    {
        var outside = Path.Combine(_root, "outside");
        Directory.CreateDirectory(outside);
        var outsideFile = Path.Combine(outside, "secret.bin");
        File.WriteAllBytes(outsideFile, new byte[128]);

        var outsideCode = Code(() => _ = new TileChannel().Issue(Request(path: outsideFile)));
        Assert.Equal("TilePathOutsideRoot", outsideCode);

        var junction = Path.Combine(_allowedRoot, "junc");
        var created = false;
        try
        {
            var start = new ProcessStartInfo("cmd.exe", $"/c mklink /J \"{junction}\" \"{outside}\"")
            {
                CreateNoWindow = true,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
            };
            using var process = Process.Start(start)!;
            process.WaitForExit(5000);
            created = process.ExitCode == 0 && Directory.Exists(junction);
        }
        catch (Exception ex) when (ex is IOException or System.ComponentModel.Win32Exception)
        {
            created = false;
        }

        string? junctionCode = null;
        if (created)
        {
            var throughJunction = Path.Combine(junction, "secret.bin");
            junctionCode = Code(() => _ = new TileChannel().Issue(Request(path: throughJunction)));
            Assert.Equal("TilePathReparse", junctionCode);
        }

        WriteEvidence("security/containment.json", writer =>
        {
            writer.WriteString("ac", "AC3");
            writer.WriteString("outside_root", outsideCode);
            writer.WriteBoolean("junction_created", created);
            writer.WriteString("junction_reparse", junctionCode ?? "SKIPPED_CREATION_FAILED");
        });

        Assert.True(created, "junction creation is required to prove reparse rejection; environment disallows mklink /J");
    }

    [Fact]
    public void EqualLengthRewrite_SameSize_RejectedAsDigestMismatch()
    {
        var channel = new TileChannel();
        var view = channel.Issue(Request());
        Assert.True(channel.ReadTile(view.Handle, 0).Sha256Verified);

        var lengthBefore = new FileInfo(_filePath).Length;
        using (var stream = new FileStream(_filePath, FileMode.Open, FileAccess.ReadWrite, FileShare.ReadWrite))
        {
            stream.Position = 10;
            stream.WriteByte((byte)(stream.ReadByte() ^ 0xFF));
        }

        Assert.Equal(lengthBefore, new FileInfo(_filePath).Length);
        var code = Code(() => channel.ReadTile(view.Handle, 0));
        Assert.Equal("TileDigestMismatch", code);
        Assert.True(channel.DigestMismatches >= 1);
        WriteEvidence("security/equal-length-rewrite.json", writer =>
        {
            writer.WriteString("ac", "AC4");
            writer.WriteNumber("file_size_before", lengthBefore);
            writer.WriteNumber("file_size_after", new FileInfo(_filePath).Length);
            writer.WriteBoolean("size_unchanged", lengthBefore == new FileInfo(_filePath).Length);
            writer.WriteString("read_result", code);
            writer.WriteNumber("digest_mismatches", channel.DigestMismatches);
        });
    }

    [Fact]
    public void TamperedTile_PreservingSize_Rejected()
    {
        var channel = new TileChannel();
        var view = channel.Issue(Request());
        channel.ReadTile(view.Handle, 2);

        var lengthBefore = new FileInfo(_filePath).Length;
        using (var stream = new FileStream(_filePath, FileMode.Open, FileAccess.ReadWrite, FileShare.ReadWrite))
        {
            stream.Position = 2L * TileSize + 100;
            stream.WriteByte(0x7F);
        }

        var code = Code(() => channel.ReadTile(view.Handle, 2));
        Assert.Equal("TileDigestMismatch", code);
        Assert.Equal(lengthBefore, new FileInfo(_filePath).Length);
        WriteEvidence("security/tampered-tile.json", writer =>
        {
            writer.WriteString("ac", "AC4");
            writer.WriteNumber("tile_index", 2);
            writer.WriteBoolean("size_preserved", lengthBefore == new FileInfo(_filePath).Length);
            writer.WriteString("read_result", code);
        });
    }

    [Fact]
    public void IdentityChange_SameLengthReplacement_Rejected()
    {
        var channel = new TileChannel();
        var view = channel.Issue(Request());
        var original = File.ReadAllBytes(_filePath);
        var staging = Path.Combine(_root, "replacement.bin");
        File.WriteAllBytes(staging, original);
        File.Move(staging, _filePath, overwrite: true);
        Assert.Equal(original.Length, new FileInfo(_filePath).Length);

        var code = Code(() => channel.ReadTile(view.Handle, 0));
        Assert.Equal("TileIdentityMismatch", code);
        WriteEvidence("security/identity-change.json", writer =>
        {
            writer.WriteString("ac", "AC4");
            writer.WriteNumber("size_after_replace", original.Length);
            writer.WriteString("read_result", code);
        });
    }

    [Fact]
    public void Performance_ColdRead_AndDigestOverheadMeasured()
    {
        var bigPath = Path.Combine(_allowedRoot, "big.bin");
        const int tileBytes = 4 * 1024 * 1024;
        const int tiles = 4;
        var payload = new byte[tileBytes * tiles];
        Random.Shared.NextBytes(payload);
        File.WriteAllBytes(bigPath, payload);

        var manifest = new List<TileDescriptor>();
        for (var index = 0; index < tiles; index++)
        {
            manifest.Add(new TileDescriptor(index, (long)index * tileBytes, tileBytes, Sha(payload.AsSpan(index * tileBytes, tileBytes).ToArray())));
        }

        var channel = new TileChannel();
        var issueWatch = Stopwatch.StartNew();
        var view = channel.Issue(new TileGrantRequest("page:big", "rev-1", bigPath, _allowedRoot, payload.Length, manifest));
        issueWatch.Stop();

        var cold = new List<double>();
        foreach (var index in Enumerable.Range(0, tiles))
        {
            var watch = Stopwatch.StartNew();
            var result = channel.ReadTile(view.Handle, index);
            watch.Stop();
            Assert.Equal(tileBytes, result.Length);
            cold.Add(watch.Elapsed.TotalMilliseconds);
        }

        // Raw read without per-tile digest, same handle discipline, to quantify hash overhead.
        using var handle = File.OpenHandle(bigPath, FileMode.Open, FileAccess.Read, FileShare.Read);
        var raw = new List<double>();
        var scratch = new byte[tileBytes];
        for (var index = 0; index < tiles; index++)
        {
            var watch = Stopwatch.StartNew();
            RandomAccess.Read(handle, scratch, (long)index * tileBytes);
            watch.Stop();
            raw.Add(watch.Elapsed.TotalMilliseconds);
        }

        var coldMax = cold.Max();
        var digestOverheadRatio = cold.Average() / Math.Max(0.001, raw.Average()) - 1.0;
        Assert.True(coldMax <= 60.0, $"cold read+digest {coldMax:F2}ms must be <=60ms");
        WriteEvidence("performance/tile-read.json", writer =>
        {
            writer.WriteString("ac", "AC1/AC5");
            writer.WriteNumber("tile_bytes", tileBytes);
            writer.WriteNumber("tile_count", tiles);
            writer.WriteNumber("issue_ms", Math.Round(issueWatch.Elapsed.TotalMilliseconds, 3));
            writer.WriteNumber("cold_read_max_ms", Math.Round(coldMax, 3));
            writer.WriteNumber("cold_read_avg_ms", Math.Round(cold.Average(), 3));
            writer.WriteNumber("raw_read_avg_ms", Math.Round(raw.Average(), 3));
            writer.WriteNumber("digest_overhead_ratio", Math.Round(digestOverheadRatio, 3));
            writer.WriteBoolean("cold_read_le_60ms", coldMax <= 60.0);
            writer.WriteString("digest_overhead_note", "S5-A records the ratio; G5 <=10% target is accounted in S5-B harness");
        });
    }

    private static void WriteEvidence(string relativePath, Action<Utf8JsonWriter> write)
    {
        var root = Environment.GetEnvironmentVariable("NEWMANGA_EVIDENCE_DIR");
        if (string.IsNullOrWhiteSpace(root))
        {
            root = Path.Combine(Path.GetTempPath(), "newmanga-s5a-evidence");
        }

        var path = Path.Combine(root, relativePath.Replace('/', Path.DirectorySeparatorChar));

        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        using var stream = File.Create(path);
        using var writer = new Utf8JsonWriter(stream, new JsonWriterOptions { Indented = true });
        writer.WriteStartObject();
        writer.WriteString("task", "HOST-TILE-CHANNEL-1");
        writer.WriteString("at_utc", DateTime.UtcNow.ToString("o"));
        write(writer);
        writer.WriteEndObject();
    }
}
