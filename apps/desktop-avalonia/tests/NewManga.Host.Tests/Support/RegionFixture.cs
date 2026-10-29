using System.Security.Cryptography;
using System.Text.Json;
using Xunit;

namespace NewManga.Host.Tests.Support;

/// <summary>
/// READER-WORKBENCH-1: Host integration fact that needs BOTH the AC11 unlabelled sidecar copy and
/// the seeded S4 region fixture (book + chapter + 8 pages + confirmed translated region). Self-skips
/// with an explicit reason otherwise, exactly like <see cref="BookFixtureFactAttribute"/>.
/// </summary>
public sealed class RegionFixtureFactAttribute : FactAttribute
{
    public RegionFixtureFactAttribute()
    {
        if (!HostFixture.TryGetSidecarDirectory(out _, out var sidecarReason))
        {
            Skip = sidecarReason;
        }
        else if (!RegionFixture.TryGet(out _, out _, out var fixtureReason))
        {
            Skip = fixtureReason;
        }
    }
}

/// <summary>
/// READER-WORKBENCH-1: locates the seeded region fixture created by
/// <c>scripts/seed_s4_region_fixture.py</c> (run by <c>scripts/test.ps1</c>) and copies its durable
/// state into a disposable Host data root. The fixture is re-seeded on every <c>test.ps1</c> run, so
/// the region id is read from <c>fixture.json</c> at runtime and is NEVER hard-coded.
/// </summary>
public static class RegionFixture
{
    public const string DataRootVariable = "NEWMANGA_S4_REGION_FIXTURE";

    private const string DefaultDataRoot =
        @"G:/CODEX/New Manga.workspace/task-envs/S4-CMD-BATCH-1/region-fixture";

    private const string MetaFileName = "fixture.json";

    public sealed record Metadata(
        string BookId,
        string ChapterId,
        string PageId,
        int PageCount,
        int PageWidth,
        int PageHeight,
        string RegionId,
        int RegionRevisionNo,
        string RegionType,
        string RegionText,
        string LibraryDbSha256);

    public static bool TryGet(out string dataRoot, out string metaPath, out string reason)
    {
        dataRoot = Environment.GetEnvironmentVariable(DataRootVariable) ?? string.Empty;
        if (string.IsNullOrWhiteSpace(dataRoot) || !Directory.Exists(dataRoot))
        {
            dataRoot = DefaultDataRoot;
        }

        metaPath = Path.Combine(dataRoot, MetaFileName);
        if (!File.Exists(Path.Combine(dataRoot, "library.db")) || !File.Exists(metaPath))
        {
            reason = $"reason: needs the seeded S4 region fixture - set {DataRootVariable} or run " +
                     "scripts/test.ps1 (scripts/seed_s4_region_fixture.py); expected library.db + " +
                     MetaFileName;
            return false;
        }

        reason = string.Empty;
        return true;
    }

    public static Metadata ReadMetadata()
    {
        if (!TryGet(out _, out var metaPath, out var reason))
        {
            throw new InvalidOperationException(reason);
        }

        using var document = JsonDocument.Parse(File.ReadAllText(metaPath));
        var root = document.RootElement;
        return new Metadata(
            root.GetProperty("book_id").GetString()!,
            root.GetProperty("chapter_id").GetString()!,
            root.GetProperty("page_id").GetString()!,
            root.GetProperty("page_count").GetInt32(),
            root.GetProperty("page_width").GetInt32(),
            root.GetProperty("page_height").GetInt32(),
            root.GetProperty("region_id").GetString()!,
            root.GetProperty("region_revision_no").GetInt32(),
            root.GetProperty("region_type").GetString()!,
            root.GetProperty("region_text").GetString()!,
            root.GetProperty("library_db_sha256").GetString()!);
    }

    /// <summary>Copies the fixture durable state into a disposable Host data root (never writes the fixture).</summary>
    public static string CopyToDisposable(string label)
    {
        if (!TryGet(out var sourceRoot, out _, out var reason))
        {
            throw new InvalidOperationException(reason);
        }

        var dataRoot = HostFixture.NewDataRoot(label);
        BookFixture.CopyTo(sourceRoot, dataRoot);
        return dataRoot;
    }

    /// <summary>SHA-256 of the SQLite database (+WAL when present), for the AC5 before/after comparison.</summary>
    public static (string Db, string? Wal) DatabaseDigests(string dataRoot)
    {
        var dbPath = Path.Combine(dataRoot, "library.db");
        var walPath = Path.Combine(dataRoot, "library.db-wal");
        var db = HashFile(dbPath);
        var wal = File.Exists(walPath) ? HashFile(walPath) : null;
        return (db, wal);
    }

    private static string HashFile(string path)
    {
        using var stream = File.Open(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
        var digest = SHA256.HashData(stream);
        return Convert.ToHexString(digest).ToLowerInvariant();
    }
}
