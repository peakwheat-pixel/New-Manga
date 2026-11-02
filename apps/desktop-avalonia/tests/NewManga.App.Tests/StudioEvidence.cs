using System.Text.Json;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-B-3/B-4 evidence sink (R-19 证据纪律). Tests write to <c>%TEMP%/newmanga-evidence/&lt;task&gt;/</c>
/// by default — repository files are never locked mid-run. Evidence is copied into
/// <c>verification/&lt;task&gt;/</c> only by an explicit curation step
/// (<c>NEWMANGA_EVIDENCE_SYNC=1</c> with <c>NEWMANGA_EVIDENCE_DIR</c>, or scripts/curate-evidence.ps1).
/// </summary>
internal static class StudioEvidence
{
    private static string? _root;

    public static string Directory(string task)
    {
        if (!string.IsNullOrWhiteSpace(Environment.GetEnvironmentVariable("NEWMANGA_STUDIO_EVIDENCE_DIR")))
        {
            var overridden = Path.Combine(Environment.GetEnvironmentVariable("NEWMANGA_STUDIO_EVIDENCE_DIR")!, task);
            System.IO.Directory.CreateDirectory(overridden);
            return overridden;
        }

        var sync = string.Equals(Environment.GetEnvironmentVariable("NEWMANGA_EVIDENCE_SYNC"), "1", StringComparison.Ordinal);
        _root ??= sync ? ResolveRepoRoot() : Path.Combine(Path.GetTempPath(), "newmanga-evidence");
        var path = _root is null
            ? Path.Combine(Path.GetTempPath(), "newmanga-evidence", task)
            : sync
                ? Path.Combine(_root, "verification", task)
                : Path.Combine(_root, task);
        System.IO.Directory.CreateDirectory(path);
        return path;
    }

    public static string File(string task, string relativePath)
    {
        var path = Path.Combine(Directory(task), relativePath);
        System.IO.Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        return path;
    }

    public static void Write(string task, string relativePath, Action<Utf8JsonWriter> write)
    {
        var path = File(task, relativePath);
        System.IO.Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        using var stream = System.IO.File.Create(path);
        using var writer = new Utf8JsonWriter(stream, new JsonWriterOptions { Indented = true });
        write(writer);
    }

    private static string? ResolveRepoRoot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        for (var depth = 0; depth < 12 && directory is not null; depth++)
        {
            if (System.IO.Directory.Exists(Path.Combine(directory.FullName, "apps", "desktop-avalonia")) &&
                System.IO.Directory.Exists(Path.Combine(directory.FullName, "doc")))
            {
                return directory.FullName;
            }

            directory = directory.Parent;
        }

        return null;
    }
}
