using Xunit;

namespace NewManga.Host.Tests.Support;

/// <summary>
/// READER-PROGRESS-1: Host integration fact that needs BOTH the unlabelled sidecar copy (AC11) and a
/// real BOOK-FIXTURE data root (book + chapter + pages + managed originals). Self-skips otherwise.
/// </summary>
public sealed class BookFixtureFactAttribute : FactAttribute
{
    public BookFixtureFactAttribute()
    {
        if (!HostFixture.TryGetSidecarDirectory(out _, out var sidecarReason))
        {
            Skip = sidecarReason;
        }
        else if (!BookFixture.TryGetDataRoot(out _, out var fixtureReason))
        {
            Skip = fixtureReason;
        }
    }
}

/// <summary>
/// READER-PROGRESS-1: locates the BOOK-FIXTURE-1 isolated data root (book 14340dd…, 1 chapter,
/// 8 pages) and copies it to a disposable data root so writes never touch the shared fixture.
/// </summary>
public static class BookFixture
{
    public const string DataRootVariable = "NEWMANGA_BOOK_FIXTURE_ROOT";

    private const string DefaultDataRoot =
        @"G:/CODEX/New Manga.workspace/task-envs/BOOK-FIXTURE-1/isolated-data";

    public static bool TryGetDataRoot(out string dataRoot, out string reason)
    {
        dataRoot = Environment.GetEnvironmentVariable(DataRootVariable) ?? string.Empty;
        if (string.IsNullOrWhiteSpace(dataRoot) || !Directory.Exists(dataRoot))
        {
            dataRoot = DefaultDataRoot;
        }

        if (!Directory.Exists(dataRoot) || !File.Exists(Path.Combine(dataRoot, "library.db")))
        {
            reason = $"reason: needs BOOK-FIXTURE data root - set {DataRootVariable} " +
                     "(an isolated root with library.db, managed/ and catalog/)";
            return false;
        }

        reason = string.Empty;
        return true;
    }

    public static string DataRoot
    {
        get
        {
            if (!TryGetDataRoot(out var root, out var reason))
            {
                throw new InvalidOperationException(reason);
            }

            return root;
        }
    }

    /// <summary>
    /// Copies the fixture library into <paramref name="destination"/> (already created by HostFixture).
    /// Only durable state is copied: <c>library.db</c> (+WAL sidecars so nothing committed is lost) and
    /// <c>managed/</c>. Derived caches (<c>derived/</c>, <c>catalog/</c>) are NOT copied: they carry a
    /// namespace-binding identity of the source root, and a copy makes the Core refuse to start
    /// ("namespace binding identity mismatch"). The Host/Core rebuild them for the new root.
    /// Runtime state (logs, backups, instance locks) is skipped as well.
    /// </summary>
    public static void CopyTo(string source, string destination)
    {
        Directory.CreateDirectory(destination);
        foreach (var file in Directory.EnumerateFiles(source, "*", SearchOption.AllDirectories))
        {
            var relative = Path.GetRelativePath(source, file);
            var firstSegment = relative.Split(Path.DirectorySeparatorChar, StringSplitOptions.RemoveEmptyEntries)
                .FirstOrDefault() ?? string.Empty;
            if (firstSegment.Equals("logs", StringComparison.OrdinalIgnoreCase) ||
                firstSegment.Equals("backups", StringComparison.OrdinalIgnoreCase) ||
                firstSegment.Equals("derived", StringComparison.OrdinalIgnoreCase) ||
                firstSegment.Equals("catalog", StringComparison.OrdinalIgnoreCase) ||
                relative.EndsWith(".lock", StringComparison.OrdinalIgnoreCase))
            {
                continue;
            }

            var target = Path.Combine(destination, relative);
            Directory.CreateDirectory(Path.GetDirectoryName(target)!);
            File.Copy(file, target, overwrite: true);
        }
    }
}
