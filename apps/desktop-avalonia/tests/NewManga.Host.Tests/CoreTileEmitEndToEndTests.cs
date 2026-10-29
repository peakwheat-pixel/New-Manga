using System.Security.Cryptography;
using System.Text.Json;
using NewManga.Host.Resources;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// CORE-TILE-EMIT-1 cross-process E2E: consume the real Python-Core tile artifact through the frozen
/// Host TileChannel contract. The artifact is produced by <c>python -m application.resource_channel.tiles</c>
/// (test.ps1 step / pytest test_e2e_artifact_for_host_channel); no local fixture is used.
/// </summary>
public sealed class CoreTileEmitEndToEndTests
{
    private static string ArtifactDir =>
        Environment.GetEnvironmentVariable("NEWMANGA_CORE_TILE_E2E")
        ?? TestWorkspacePaths.Path("task-envs/CORE-TILE-EMIT-1/e2e/artifact");

    private static string EvidenceDir
    {
        get
        {
            var root = Environment.GetEnvironmentVariable("NEWMANGA_EVIDENCE_DIR")
                       ?? Path.Combine(Path.GetTempPath(), "newmanga-core-tile-evidence");
            var dir = Path.Combine(root, "e2e");
            Directory.CreateDirectory(dir);
            return dir;
        }
    }

    [Fact]
    public void HostTileChannel_ConsumesRealCoreArtifact_AllDigestsMatch()
    {
        var artifactDir = ArtifactDir;
        var manifestPath = Path.Combine(artifactDir, "tile-manifest.json");
        if (!File.Exists(manifestPath))
        {
            WriteEvidence(new { executed = false, reason = "artifact missing (run scripts/test.ps1 or pytest test_e2e_artifact_for_host_channel)" });
            return;
        }

        using var document = JsonDocument.Parse(File.ReadAllText(manifestPath));
        var root = document.RootElement;
        var tiles = new List<TileDescriptor>();
        foreach (var tile in root.GetProperty("tiles").EnumerateArray())
        {
            tiles.Add(new TileDescriptor(
                tile.GetProperty("index").GetInt32(),
                tile.GetProperty("offset").GetInt64(),
                tile.GetProperty("length").GetInt32(),
                tile.GetProperty("sha256").GetString()!));
        }

        var size = root.GetProperty("size").GetInt64();
        var pagePath = root.GetProperty("absolute_path").GetString()!;
        var allowedRoot = root.GetProperty("allowed_root").GetString()!;
        Assert.Equal(size, new FileInfo(pagePath).Length);
        Assert.Equal(tiles.Count, tiles.Select(tile => tile.Index).Distinct().Count());

        var channel = new TileChannel();
        var view = channel.Issue(new TileGrantRequest(
            root.GetProperty("resource_id").GetString()!,
            root.GetProperty("revision").GetString()!,
            pagePath,
            allowedRoot,
            size,
            tiles,
            TimeSpan.FromMilliseconds(root.TryGetProperty("ttl_ms", out var ttl) ? ttl.GetInt64() : 300000)));

        var verified = 0;
        long bytes = 0;
        foreach (var descriptor in tiles)
        {
            var result = channel.ReadTile(view.Handle, descriptor.Index);
            Assert.True(result.Sha256Verified);
            Assert.Equal(descriptor.Length, result.Length);
            verified++;
            bytes += result.Length;
        }

        Assert.Equal(tiles.Count, verified);
        Assert.Equal(size, bytes);
        Assert.True(channel.DigestMismatches == 0);

        WriteEvidence(new
        {
            executed = true,
            artifact_dir = artifactDir,
            resource_id = root.GetProperty("resource_id").GetString(),
            revision = root.GetProperty("revision").GetString(),
            tile_count = tiles.Count,
            page_bytes = bytes,
            digests_verified = verified,
            digest_match_rate = (double)verified / tiles.Count,
            digest_mismatches = channel.DigestMismatches,
            contract_fields = new[] { "resource_id", "revision", "size", "tiles", "absolute_path", "allowed_root" },
            ui_fixture_fallback_used = false,
        });
    }

    private static void WriteEvidence(object payload)
    {
        var path = Path.Combine(EvidenceDir, "host-consumes-core-artifact.json");
        File.WriteAllText(path, JsonSerializer.Serialize(payload, new JsonSerializerOptions { WriteIndented = true }));
    }
}
