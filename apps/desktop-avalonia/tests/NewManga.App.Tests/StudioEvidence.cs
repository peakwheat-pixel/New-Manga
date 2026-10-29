using System.Text.Json;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-B-3/B-4 evidence sink. Writes under <c>verification/&lt;task&gt;/</c> of the repository so the
/// evidence ships with the commit; resolves the repo root by walking up from the test binaries. Falls
/// back to <c>%NEWMANGA_STUDIO_EVIDENCE_DIR%</c> or the temp directory when the repo root is absent.
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

        _root ??= ResolveRepoRoot();
        var path = _root is null
            ? Path.Combine(Path.GetTempPath(), "newmanga-studio-evidence", task)
            : Path.Combine(_root, "verification", task);
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
