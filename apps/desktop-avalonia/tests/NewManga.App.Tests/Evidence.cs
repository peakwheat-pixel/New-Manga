using System.Text.Json;

namespace NewManga.App.Tests;

/// <summary>
/// Shared evidence writer used by the retained UI tests after the legacy S3 shell test file was retired
/// in V11R-C-3 R4 (previously declared inside S3ShellTests.cs).
/// </summary>
internal static class Evidence
{
    public static string Directory
    {
        get
        {
            var root = Environment.GetEnvironmentVariable("NEWMANGA_EVIDENCE_DIR");
            if (string.IsNullOrWhiteSpace(root))
            {
                root = Path.Combine(Path.GetTempPath(), "newmanga-s3-evidence");
            }

            System.IO.Directory.CreateDirectory(root);
            return root;
        }
    }

    public static void Write(string relativePath, Action<Utf8JsonWriter> write)
    {
        var path = Path.Combine(Directory, relativePath);
        System.IO.Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        using var stream = File.Create(path);
        using var writer = new Utf8JsonWriter(stream, new JsonWriterOptions { Indented = true });
        write(writer);
    }
}
