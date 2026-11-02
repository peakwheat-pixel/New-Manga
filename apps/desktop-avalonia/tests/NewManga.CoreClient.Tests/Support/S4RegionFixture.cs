using System.Text.Json;
using NewManga.CoreClient;
using Xunit;

namespace NewManga.CoreClient.Tests.Support;

/// <summary>
/// S4-CMD-BATCH-1: fact that needs BOTH the AC11 unlabelled sidecar copy and the seeded
/// region-write / reader-progress fixture data root (book + chapter + pages + clean artifact +
/// translated region). Self-skips with an explicit reason otherwise, exactly like
/// <see cref="SidecarFactAttribute"/>.
/// </summary>
public sealed class S4RegionFixtureFactAttribute : FactAttribute
{
    public S4RegionFixtureFactAttribute()
    {
        if (!SidecarFixture.TryGetSidecarDirectory(out _, out var sidecarReason))
        {
            Skip = sidecarReason;
        }
        else if (!S4RegionFixture.TryGet(out _, out _, out var fixtureReason))
        {
            Skip = fixtureReason;
        }
    }
}

/// <summary>
/// S4-CMD-BATCH-1: locates the seeded region fixture created by
/// <c>scripts/seed_s4_region_fixture.py</c> (run by <c>scripts/test.ps1</c>) and copies its durable
/// state into a disposable data root so the write commands never mutate the shared fixture.
/// </summary>
public static class S4RegionFixture
{
    public const string DataRootVariable = "NEWMANGA_S4_REGION_FIXTURE";

    private static readonly string DefaultDataRoot =
        TestWorkspacePaths.Path("task-envs/S4-CMD-BATCH-1/region-fixture");

    private const string MetaFileName = "fixture.json";

    public sealed record Metadata(
        string BookId,
        string ChapterId,
        string ChapterType,
        string PageId,
        int PageCount,
        string RegionId,
        int RegionRevisionNo,
        string RegionType,
        string RegionText);

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
            reason = $"reason: needs the S4 region fixture - set {DataRootVariable} or run " +
                     "scripts/test.ps1 (scripts/seed_s4_region_fixture.py); expected library.db + " +
                     MetaFileName;
            return false;
        }

        reason = string.Empty;
        return true;
    }

    public static Metadata ReadMetadata(string metaPath)
    {
        using var document = JsonDocument.Parse(File.ReadAllText(metaPath));
        var root = document.RootElement;
        return new Metadata(
            root.GetProperty("book_id").GetString()!,
            root.GetProperty("chapter_id").GetString()!,
            root.GetProperty("chapter_type").GetString()!,
            root.GetProperty("page_id").GetString()!,
            root.GetProperty("page_count").GetInt32(),
            root.GetProperty("region_id").GetString()!,
            root.GetProperty("region_revision_no").GetInt32(),
            root.GetProperty("region_type").GetString()!,
            root.GetProperty("region_text").GetString()!);
    }

    /// <summary>Copies the durable fixture state (SQLite library + Managed Copy) into a fresh root.</summary>
    public static string CopyDurableToDisposable(string sourceRoot, string testName)
    {
        var destination = Path.Combine(
            Path.GetTempPath(),
            "newmanga-s4-region-tests",
            testName + "-" + Guid.NewGuid().ToString("N")[..10]);
        Directory.CreateDirectory(destination);

        foreach (var name in new[] { "library.db", "library.db-wal", "library.db-shm", MetaFileName })
        {
            var file = Path.Combine(sourceRoot, name);
            if (File.Exists(file))
            {
                File.Copy(file, Path.Combine(destination, name), overwrite: true);
            }
        }

        var managed = Path.Combine(sourceRoot, "managed");
        if (Directory.Exists(managed))
        {
            CopyDirectory(managed, Path.Combine(destination, "managed"));
        }

        return destination;
    }

    /// <summary>Core options bound to an existing data root (instead of SidecarFixture's fresh root).</summary>
    public static CoreServiceOptions CreateCoreOptions(string testName, string dataRoot)
    {
        var logDirectory = Path.Combine(SidecarFixture.EvidenceDirectory, "logs", testName);
        Directory.CreateDirectory(logDirectory);
        return new CoreServiceOptions
        {
            ExecutablePath = SidecarFixture.Exe(SidecarFixture.CoreServiceFileName),
            DataRoot = dataRoot,
            DerivedRoot = Path.Combine(dataRoot, "derived"),
            CatalogDbPath = Path.Combine(dataRoot, "catalog", "catalog.sqlite"),
            ManagedRoot = Path.Combine(dataRoot, "managed"),
            StderrLogPath = Path.Combine(logDirectory, "core_service.stderr.log"),
            WireLogPath = Path.Combine(SidecarFixture.EvidenceDirectory, "wire", testName + ".ndjson"),
            StartupTimeout = TimeSpan.FromSeconds(60),
            RequestTimeout = TimeSpan.FromSeconds(60),
        };
    }

    private static void CopyDirectory(string source, string destination)
    {
        Directory.CreateDirectory(destination);
        foreach (var file in Directory.EnumerateFiles(source, "*", SearchOption.AllDirectories))
        {
            var relative = Path.GetRelativePath(source, file);
            var target = Path.Combine(destination, relative);
            Directory.CreateDirectory(Path.GetDirectoryName(target)!);
            File.Copy(file, target, overwrite: true);
        }
    }
}

