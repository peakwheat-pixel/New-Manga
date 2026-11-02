using System.Diagnostics;
using System.Text;
using Avalonia.Media.Imaging;

namespace NewManga.App.Tests;

/// <summary>
/// R-19 evidence discipline: tests NEVER write into the repository by default. A capture goes to
/// <c>%TEMP%/newmanga-evidence/&lt;TASK&gt;/</c>; it is only mirrored into <c>verification/&lt;TASK&gt;/</c>
/// when an explicit environment switch is present (<c>NEWMANGA_EVIDENCE_DIR</c> or
/// <c>NEWMANGA_EVIDENCE_SYNC=1</c>), which the curated evidence script sets. Writes retry with a uniquified
/// filename and never fail the test on IO contention (mapped/antivirus-locked files were causing the
/// intermittent <c>IOException</c> on CI).
/// </summary>
public static class EvidenceFiles
{
    private static int _sequence;

    /// <summary>True when the caller explicitly asked to publish evidence into the repository.</summary>
    public static bool SyncEnabled =>
        !string.IsNullOrWhiteSpace(Environment.GetEnvironmentVariable("NEWMANGA_EVIDENCE_DIR")) ||
        string.Equals(Environment.GetEnvironmentVariable("NEWMANGA_EVIDENCE_SYNC"), "1", StringComparison.Ordinal);

    /// <summary>Per-task directory under the OS temp root (always writable, never the repo).</summary>
    public static string TempRoot(string task) =>
        Path.Combine(Path.GetTempPath(), "newmanga-evidence", task);

    /// <summary>
    /// R-19: explicit curation runs may target another task evidence directory (B-2 reuses the shared
    /// conformance inventory without duplicating the scan). Ordinary test runs never set this.
    /// </summary>
    public static string Task(string fallback) =>
        Environment.GetEnvironmentVariable("NEWMANGA_EVIDENCE_TASK") is { Length: > 0 } value
            ? value
            : fallback;

    /// <summary>
    /// Saves a rendered frame. Returns the byte count on success and null when every attempt failed —
    /// the test must not fail because of evidence-file IO, but the curated evidence run reports gaps.
    /// </summary>
    public static long? SaveFrame(Bitmap frame, string task, string name, string? testName = null)
    {
        try
        {
            var bytes = RenderToBytes(frame);
            if (bytes is null)
            {
                return null;
            }

            return WriteBytes(task, Path.Combine("screens", FileNameFor(name, testName)), bytes);
        }
        catch (Exception exception) when (IsExpectedIo(exception))
        {
            Debug.WriteLine($"[evidence] save frame failed ({task}/{name}): {exception.GetType().Name}");
            return null;
        }
    }

    /// <summary>Writes a text evidence artifact (JSON/log) with the same temp-first discipline.</summary>
    public static long? WriteText(string task, string relativePath, string content, string? testName = null)
    {
        try
        {
            var bytes = Encoding.UTF8.GetBytes(content);
            var relative = relativePath.Contains('/', StringComparison.Ordinal) || relativePath.Contains('\\', StringComparison.Ordinal)
                ? relativePath
                : Path.Combine(Path.GetFileNameWithoutExtension(relativePath) + ".txt");
            return WriteBytes(task, relative, bytes, testName);
        }
        catch (Exception exception) when (IsExpectedIo(exception))
        {
            Debug.WriteLine($"[evidence] write text failed ({task}/{relativePath}): {exception.GetType().Name}");
            return null;
        }
    }

    /// <summary>Absolute temp path for reading back a written artifact in assertions.</summary>
    public static string TempPath(string task, string relativePath, string? testName = null) =>
        Path.Combine(TempRoot(task), relativePath);

    private static long? WriteBytes(string task, string relativePath, byte[] bytes, string? testName = null)
    {
        var root = TempRoot(task);
        Directory.CreateDirectory(root);
        for (var attempt = 0; attempt < 3; attempt++)
        {
            var candidate = attempt == 0
                ? Path.Combine(root, relativePath)
                : Path.Combine(
                    Path.GetDirectoryName(Path.Combine(root, relativePath)) ?? root,
                    Path.GetFileNameWithoutExtension(relativePath) + $"-r{attempt}" + Path.GetExtension(relativePath));
            try
            {
                Directory.CreateDirectory(Path.GetDirectoryName(candidate)!);
                File.WriteAllBytes(candidate, bytes);
                if (SyncEnabled)
                {
                    MirrorToRepository(task, relativePath, bytes);
                }

                return bytes.LongLength;
            }
            catch (Exception exception) when (IsExpectedIo(exception))
            {
                Debug.WriteLine($"[evidence] attempt {attempt + 1} failed for {candidate}: {exception.GetType().Name}");
            }
        }

        return null;
    }

    private static void MirrorToRepository(string task, string relativePath, byte[] bytes)
    {
        try
        {
            var explicitRoot = Environment.GetEnvironmentVariable("NEWMANGA_EVIDENCE_DIR");

            var targetRoot = !string.IsNullOrWhiteSpace(explicitRoot)
                ? explicitRoot
                : Path.Combine(RepositoryRoot(), "verification", task);
            var destination = Path.Combine(targetRoot, relativePath);
            Directory.CreateDirectory(Path.GetDirectoryName(destination)!);
            for (var attempt = 0; attempt < 3; attempt++)
            {
                try
                {
                    File.WriteAllBytes(destination, bytes);
                    return;
                }
                catch (Exception exception) when (IsExpectedIo(exception))
                {
                    destination = Path.Combine(
                        Path.GetDirectoryName(destination) ?? targetRoot,
                        Path.GetFileNameWithoutExtension(relativePath) + $"-m{attempt}{Path.GetExtension(relativePath)}");
                }
            }
        }
        catch (Exception exception) when (IsExpectedIo(exception))
        {
            // Evidence mirroring must never fail the test run; the curated script verifies completeness.
            Debug.WriteLine($"[evidence] mirror failed ({task}/{relativePath}): {exception.GetType().Name}");
        }
    }

    private static byte[]? RenderToBytes(Bitmap frame)
    {
        var scratch = Path.Combine(Path.GetTempPath(), $"nm-evidence-{Environment.ProcessId}-{Interlocked.Increment(ref _sequence)}.png");
        try
        {
            frame.Save(scratch);
            return File.Exists(scratch) ? File.ReadAllBytes(scratch) : null;
        }
        finally
        {
            try
            {
                if (File.Exists(scratch))
                {
                    File.Delete(scratch);
                }
            }
            catch (Exception exception) when (IsExpectedIo(exception))
            {
                // best effort temp cleanup
            }
        }
    }

    private static string FileNameFor(string name, string? testName)
    {
        var safeName = Sanitize(name);
        var safeTest = Sanitize(testName ?? "capture");
        return $"{safeTest}--{safeName}.png";
    }

    private static string Sanitize(string value)
    {
        var builder = new StringBuilder(value.Length);
        foreach (var character in value)
        {
            builder.Append(char.IsLetterOrDigit(character) || character is '-' or '_' ? character : '_');
        }

        return builder.ToString();
    }

    private static string RepositoryRoot()
    {
        // The solution lives at apps/desktop-avalonia/NewManga.sln. The repository root is the nearest
        // ancestor that has the governance file + apps tree (linked worktrees keep .git outside the tree).
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            if (File.Exists(Path.Combine(directory.FullName, "AGENTS.md")) &&
                Directory.Exists(Path.Combine(directory.FullName, "apps")))
            {
                return directory.FullName;
            }

            directory = directory.Parent;
        }

        return AppContext.BaseDirectory;
    }

    private static bool IsExpectedIo(Exception exception) => exception is
        IOException or UnauthorizedAccessException or ArgumentException or NotSupportedException;
}
