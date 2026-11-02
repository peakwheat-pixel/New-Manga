using System.Diagnostics;
using System.Security.Cryptography;
using System.Text.Json;
using NewManga.Host.Resources;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// S5-B D4-1/3/5/6 security-equivalence harness. These tests never consult mtime for validity; they
/// write the mtime back to its original value after an equal-length rewrite to prove the rejection is
/// digest/identity driven, and they exercise escape attempts at both issue and read time.
/// </summary>
public sealed class D4SecurityHarnessTests : IDisposable
{
    private const int TileSize = 256 * 1024;
    private const int TileCount = 8;
    private readonly string _root;
    private readonly string _allowedRoot;
    private readonly string _pagePath;

    public D4SecurityHarnessTests()
    {
        _root = Path.Combine(Path.GetTempPath(), "nm-d4-" + Guid.NewGuid().ToString("N")[..10]);
        _allowedRoot = Path.Combine(_root, "allowed");
        Directory.CreateDirectory(_allowedRoot);
        _pagePath = Path.Combine(_allowedRoot, "page.bin");
        var bytes = new byte[TileSize * TileCount];
        Random.Shared.NextBytes(bytes);
        File.WriteAllBytes(_pagePath, bytes);
    }

    public void Dispose()
    {
        try
        {
            Directory.Delete(_root, recursive: true);
        }
        catch (IOException)
        {
            // temp cleanup best effort
        }
    }

    private static string Sha(byte[] bytes) => Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();

    private static IReadOnlyList<TileDescriptor> Manifest(byte[] all)
    {
        var tiles = new List<TileDescriptor>();
        for (var index = 0; index < TileCount; index++)
        {
            tiles.Add(new TileDescriptor(index, (long)index * TileSize, TileSize, Sha(all.AsSpan(index * TileSize, TileSize).ToArray())));
        }

        return tiles;
    }

    private TileGrantRequest Request(string? path = null, string? root = null) =>
        new("page:d4", "rev-d4", path ?? _pagePath, root ?? _allowedRoot, new FileInfo(_pagePath).Length, Manifest(File.ReadAllBytes(_pagePath)));

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
    public void D4_1_EqualLengthRewrite_WithRestoredMtime_RejectedWithoutMtimeDependency()
    {
        var channel = new TileChannel();
        var view = channel.Issue(Request());
        Assert.True(channel.ReadTile(view.Handle, 0).Sha256Verified);
        Assert.Equal(TileSize, channel.ReadTile(view.Handle, 1).Length);

        var lengthBefore = new FileInfo(_pagePath).Length;
        var mtimeBefore = File.GetLastWriteTimeUtc(_pagePath);
        using (var stream = new FileStream(_pagePath, FileMode.Open, FileAccess.ReadWrite, FileShare.ReadWrite))
        {
            stream.Position = 42;
            stream.WriteByte((byte)(stream.ReadByte() ^ 0xA5));
        }

        File.SetLastWriteTimeUtc(_pagePath, mtimeBefore);
        var mtimeAfter = File.GetLastWriteTimeUtc(_pagePath);
        var code = Code(() => channel.ReadTile(view.Handle, 0));
        Assert.Equal("TileDigestMismatch", code);
        Assert.Equal(lengthBefore, new FileInfo(_pagePath).Length);
        Assert.Equal(mtimeBefore, mtimeAfter);

        Evidence("security/d4-1-equal-length-rewrite.json", writer =>
        {
            writer.WriteString("ac", "AC1");
            writer.WriteString("scenario", "same-size rewrite with mtime restored to original");
            writer.WriteNumber("file_size", lengthBefore);
            writer.WriteString("mtime_utc", mtimeAfter.ToString("o"));
            writer.WriteBoolean("mtime_unchanged", mtimeBefore == mtimeAfter);
            writer.WriteBoolean("validation_uses_mtime", false);
            writer.WriteString("read_result", code);
        });
    }

    [Fact]
    public void D4_3_Escape_RejectedAtIssue()
    {
        var outside = Path.Combine(_root, "outside");
        Directory.CreateDirectory(outside);
        File.WriteAllBytes(Path.Combine(outside, "x.bin"), new byte[64]);

        var dotDot = Code(() => _ = new TileChannel().Issue(Request(path: Path.Combine(_allowedRoot, "..", "outside", "x.bin"))));
        var unc = Code(() => _ = new TileChannel().Issue(Request(path: @"\\server\share\x.bin")));
        Assert.Equal("TilePathOutsideRoot", dotDot);
        Assert.Equal("TilePathOutsideRoot", unc);

        var junction = Path.Combine(_allowedRoot, "junc");
        var junctionCreated = TryLink($"mklink /J \"{junction}\" \"{outside}\"");
        string? junctionCode = null;
        if (junctionCreated)
        {
            junctionCode = Code(() => _ = new TileChannel().Issue(Request(path: Path.Combine(junction, "x.bin"))));
            Assert.Equal("TilePathReparse", junctionCode);
        }

        var symlink = Path.Combine(_allowedRoot, "sym.bin");
        var symlinkCreated = TryCreateSymlink(symlink, Path.Combine(outside, "x.bin"));
        string? symlinkCode = null;
        if (symlinkCreated)
        {
            symlinkCode = Code(() => _ = new TileChannel().Issue(Request(path: symlink)));
            Assert.Equal("TilePathReparse", symlinkCode);
        }

        Evidence("security/d4-3-escape-issue.json", writer =>
        {
            writer.WriteString("ac", "AC2");
            writer.WriteString("dotdot_escape", dotDot);
            writer.WriteString("unc_escape", unc);
            writer.WriteBoolean("junction_created", junctionCreated);
            writer.WriteString("junction_issue", junctionCode ?? "SKIPPED_CREATION_FAILED");
            writer.WriteBoolean("symlink_created", symlinkCreated);
            writer.WriteString("symlink_issue", symlinkCode ?? "SKIPPED_PRIVILEGE");
        });

        Assert.True(junctionCreated, "directory junction creation is required for D4-3 issue evidence");
    }

    [Fact]
    public void D4_3_Escape_RejectedAtReadTime_AfterPathReplacement()
    {
        var subdir = Path.Combine(_allowedRoot, "sub");
        Directory.CreateDirectory(subdir);
        var page = Path.Combine(subdir, "page.bin");
        var all = File.ReadAllBytes(_pagePath);
        File.WriteAllBytes(page, all);
        var channel = new TileChannel();
        var view = channel.Issue(new TileGrantRequest("page:read-escape", "rev-read", page, _allowedRoot, all.Length, Manifest(all)));
        Assert.True(channel.ReadTile(view.Handle, 0).Sha256Verified);

        var outsideDir = Path.Combine(_root, "outside-read");
        Directory.CreateDirectory(outsideDir);
        File.WriteAllBytes(Path.Combine(outsideDir, "page.bin"), all);
        Directory.Delete(subdir, recursive: true);
        var replacedWithJunction = TryLink($"mklink /J \"{subdir}\" \"{outsideDir}\"");
        var code = Code(() => channel.ReadTile(view.Handle, 0));
        Assert.NotEqual("NO_ERROR", code);
        Assert.Contains(code, new[] { "TilePathOutsideRoot", "TilePathReparse", "TileIdentityMismatch", "TileIoFailure" });

        Evidence("security/d4-3-escape-read.json", writer =>
        {
            writer.WriteString("ac", "AC2");
            writer.WriteBoolean("path_replaced_with_junction", replacedWithJunction);
            writer.WriteString("read_result", code);
            writer.WriteBoolean("rejected", code != "NO_ERROR");
        });

        Assert.True(replacedWithJunction, "read-time escape test requires the junction replacement");
    }

    [Fact]
    public void D4_5_IdentityChange_VolumeFileIndex_Rejected()
    {
        var channel = new TileChannel();
        var view = channel.Issue(Request());
        var original = File.ReadAllBytes(_pagePath);
        var staging = Path.Combine(_root, "replacement.bin");
        File.WriteAllBytes(staging, original);
        File.Move(staging, _pagePath, overwrite: true);
        Assert.Equal(original.Length, new FileInfo(_pagePath).Length);

        var code = Code(() => channel.ReadTile(view.Handle, 0));
        Assert.Equal("TileIdentityMismatch", code);
        Evidence("security/d4-5-identity-change.json", writer =>
        {
            writer.WriteString("ac", "AC3");
            writer.WriteString("detection", "volume serial + file index");
            writer.WriteNumber("size_after_replace", original.Length);
            writer.WriteString("read_result", code);
        });
    }

    [Fact]
    public void D4_6_PageBudget_DigestShareWithinTenPercentOf60msBudget()
    {
        var pageTiles = TileCount;
        var all = File.ReadAllBytes(_pagePath);
        var channel = new TileChannel();
        var view = channel.Issue(new TileGrantRequest("page:perf", "rev-perf", _pagePath, _allowedRoot, all.Length, Manifest(all)));

        var loadWatch = Stopwatch.StartNew();
        var buffers = new List<byte[]>(pageTiles);
        for (var index = 0; index < pageTiles; index++)
        {
            buffers.Add(channel.ReadTile(view.Handle, index).Bytes);
        }

        loadWatch.Stop();
        var pageLoadMs = loadWatch.Elapsed.TotalMilliseconds;

        var digestWatch = Stopwatch.StartNew();
        foreach (var buffer in buffers)
        {
            _ = SHA256.HashData(buffer);
        }

        digestWatch.Stop();
        var digestMs = digestWatch.Elapsed.TotalMilliseconds;
        var budgetMs = 60.0;
        var digestShareOfBudget = digestMs / budgetMs;
        var digestShareOfLoad = digestMs / Math.Max(0.001, pageLoadMs);

        Assert.True(pageLoadMs <= budgetMs, $"page load {pageLoadMs:F2}ms must be <=60ms");
        Assert.True(digestShareOfBudget <= 0.10, $"digest {digestMs:F2}ms is {digestShareOfBudget:P1} of 60ms page budget (>10%)");

        Evidence("performance/d4-6-page-budget.json", writer =>
        {
            writer.WriteString("ac", "AC4");
            writer.WriteString("method", "page = 8 x 256KiB tiles read through TileChannel (per-tile digest on every read); wall clock");
            writer.WriteNumber("page_bytes", all.Length);
            writer.WriteNumber("page_load_ms", Math.Round(pageLoadMs, 3));
            writer.WriteNumber("digest_ms", Math.Round(digestMs, 3));
            writer.WriteNumber("budget_ms", budgetMs);
            writer.WriteNumber("digest_share_of_budget", Math.Round(digestShareOfBudget, 4));
            writer.WriteNumber("digest_share_of_measured_load", Math.Round(digestShareOfLoad, 4));
            writer.WriteBoolean("page_load_le_60ms", pageLoadMs <= budgetMs);
            writer.WriteBoolean("digest_share_le_10pct", digestShareOfBudget <= 0.10);
            writer.WriteString("cache_state", "freshly written temp file; OS read cache may be warm (wall-clock budget gate, not disk-cold claim)");
        });
    }

    [Fact]
    public void D4_6_ContractFreeze_CoreToHostTileManifest_AndUiViews()
    {
        var contractPath = Path.Combine(
            AppContext.BaseDirectory, "..", "..", "..", "..", "..", "docs", "TILE-CHANNEL-CONTRACT-V1.md");
        contractPath = Path.GetFullPath(contractPath);
        Assert.True(File.Exists(contractPath), $"contract doc missing: {contractPath}");
        var contractDoc = File.ReadAllText(contractPath);
        foreach (var token in new[] { "\"resource_id\"", "\"revision\"", "\"size\"", "\"tiles\"", "\"index\"", "\"offset\"", "\"length\"", "\"sha256\"", "\"handle\"", "\"tile_count\"", "\"expires_at\"", "TilePathReparse", "TileDigestMismatch", "TileIdentityMismatch" })
        {
            Assert.Contains(token, contractDoc, StringComparison.Ordinal);
        }

        // Host-internal grant manifest shape (Core -> Host).
        var manifestKeys = new[] { "ResourceId", "RevisionFingerprint", "AbsolutePath", "AllowedRoot", "Size", "Tiles", "Ttl", "VolumeSerial", "FileIndex" };
        Assert.Equal(manifestKeys.OrderBy(x => x), typeof(TileGrantRequest).GetProperties().Select(property => property.Name).OrderBy(x => x));
        var tileKeys = new[] { "Index", "Offset", "Length", "Sha256" };
        Assert.Equal(tileKeys.OrderBy(x => x), typeof(TileDescriptor).GetProperties().Select(property => property.Name).OrderBy(x => x));

        // UI-facing surface must not expose paths or digests.
        foreach (var type in new[] { typeof(TileGrantView), typeof(TileReadResult) })
        {
            var names = type.GetProperties().Select(property => property.Name).ToArray();
            Assert.DoesNotContain(names, name => name.Contains("Path", StringComparison.OrdinalIgnoreCase));
            Assert.DoesNotContain(names, name => name.Contains("Sha", StringComparison.OrdinalIgnoreCase) && name != "Sha256Verified");
            Assert.DoesNotContain(names, name => name.Contains("Digest", StringComparison.OrdinalIgnoreCase));
        }

        var contractSha = Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(contractPath))).ToLowerInvariant();
        Evidence("contract/tile-contract.json", writer =>
        {
            writer.WriteString("ac", "AC5");
            writer.WriteString("contract_doc", "apps/desktop-avalonia/docs/TILE-CHANNEL-CONTRACT-V1.md");
            writer.WriteString("contract_sha256", contractSha);
            writer.WriteBoolean("core_changed", false);
            writer.WriteString("grant_manifest", "resource_id/revision/size/tiles[index,offset,length,sha256]");
            writer.WriteString("ui_view", "handle/resource_id/revision/size/tile_count/issued_at/expires_at");
            writer.WriteBoolean("ui_exposes_paths_or_digests", false);
            writer.WriteString("error_codes", "TilePathOutsideRoot,TilePathReparse,TileIdentityMismatch,TileSizeMismatch,TileDigestMismatch,TileGrantRevoked,TileGrantExpired");
        });
    }

    private static bool TryLink(string arguments)
    {
        try
        {
            var start = new ProcessStartInfo("cmd.exe", "/c " + arguments)
            {
                CreateNoWindow = true,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
            };
            using var process = Process.Start(start)!;
            process.WaitForExit(5000);
            return process.ExitCode == 0;
        }
        catch (Exception ex) when (ex is IOException or System.ComponentModel.Win32Exception)
        {
            return false;
        }
    }

    private static bool TryCreateSymlink(string link, string target)
    {
        try
        {
            File.CreateSymbolicLink(link, target);
            return File.Exists(link);
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or PlatformNotSupportedException)
        {
            return false;
        }
    }

    private static void Evidence(string relativePath, Action<Utf8JsonWriter> write)
    {
        var rootDir = Environment.GetEnvironmentVariable("NEWMANGA_EVIDENCE_DIR");
        if (string.IsNullOrWhiteSpace(rootDir))
        {
            rootDir = Path.Combine(Path.GetTempPath(), "newmanga-s5b-evidence");
        }

        var path = Path.Combine(rootDir, relativePath.Replace('/', Path.DirectorySeparatorChar));
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        using var stream = File.Create(path);
        using var writer = new Utf8JsonWriter(stream, new JsonWriterOptions { Indented = true });
        writer.WriteStartObject();
        writer.WriteString("task", "HOST-RESOURCE-SECURITY-1");
        writer.WriteString("at_utc", DateTime.UtcNow.ToString("o"));
        write(writer);
        writer.WriteEndObject();
    }
}
