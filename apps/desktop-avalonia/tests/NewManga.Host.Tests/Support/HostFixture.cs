using System.Diagnostics;
using System.Text.Json;
using NewManga.Host;

namespace NewManga.Host.Tests.Support;

/// <summary>Host test environment: unlabelled sidecar copy (AC11), isolated data roots, evidence dir.</summary>
public static class HostFixture
{
    public const string SidecarDirectoryVariable = "NEWMANGA_CORECLIENT_SIDECAR_DIR";
    public const string EvidenceDirectoryVariable = "NEWMANGA_EVIDENCE_DIR";

    public static string SidecarDirectory
    {
        get
        {
            var directory = Environment.GetEnvironmentVariable(SidecarDirectoryVariable);
            if (string.IsNullOrWhiteSpace(directory))
            {
                throw new InvalidOperationException(
                    $"{SidecarDirectoryVariable} is not set. Run tests through scripts/test.ps1 (AC11 unlabelled copy).");
            }

            return directory;
        }
    }

    public static string EvidenceDirectory
    {
        get
        {
            var directory = Environment.GetEnvironmentVariable(EvidenceDirectoryVariable);
            if (string.IsNullOrWhiteSpace(directory))
            {
                directory = Path.Combine(Path.GetTempPath(), "newmanga-host-tests-evidence");
            }

            Directory.CreateDirectory(directory);
            return directory;
        }
    }

    public static string NewDataRoot(string label)
    {
        var root = Path.Combine(
            Path.GetTempPath(),
            "newmanga-host-runtime-tests",
            label + "-" + Guid.NewGuid().ToString("N")[..10]);
        Directory.CreateDirectory(Path.Combine(root, "derived"));
        Directory.CreateDirectory(Path.Combine(root, "catalog"));
        Directory.CreateDirectory(Path.Combine(root, "managed"));
        return root;
    }

    public static HostOptions CreateOptions(
        string testName,
        out string dataRoot,
        bool parity = false,
        string? sidecarDirectoryOverride = null,
        string? mutexName = null,
        bool detectLegacyShell = false)
    {
        dataRoot = NewDataRoot(testName);
        return new HostOptions
        {
            DataRoot = dataRoot,
            LogDirectory = Path.Combine(EvidenceDirectory, "host-logs", testName),
            SidecarDirectoryOverride = sidecarDirectoryOverride ?? SidecarDirectory,
            MutexName = mutexName ?? @"Local\NewManga.Host.Test." + Guid.NewGuid().ToString("N")[..12],
            ParityReached = parity,
            DetectLegacyShell = detectLegacyShell,
            EnableWireEvidence = true,
            StartupTimeout = TimeSpan.FromSeconds(60),
            RequestTimeout = TimeSpan.FromSeconds(60),
        };
    }

    public static void TryDeleteDirectory(string path)
    {
        try
        {
            if (Directory.Exists(path))
            {
                Directory.Delete(path, recursive: true);
            }
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
        {
            // best effort; temp roots are disposable
        }
    }

    public static void WriteEvidenceJson(string relativePath, Action<Utf8JsonWriter> write)
    {
        var path = Path.Combine(EvidenceDirectory, relativePath);
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        using var stream = new FileStream(path, FileMode.Create, FileAccess.Write, FileShare.Read);
        using var writer = new Utf8JsonWriter(stream, new JsonWriterOptions { Indented = true });
        write(writer);
    }

    public static ProcessResult Run(string executablePath, params string[] arguments)
    {
        var startInfo = new ProcessStartInfo
        {
            FileName = executablePath,
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
        };
        foreach (var argument in arguments)
        {
            startInfo.ArgumentList.Add(argument);
        }

        using var process = Process.Start(startInfo)
            ?? throw new InvalidOperationException($"failed to start {executablePath}");
        var stdout = process.StandardOutput.ReadToEnd();
        var stderr = process.StandardError.ReadToEnd();
        process.WaitForExit(60_000);
        return new ProcessResult(process.ExitCode, stdout, stderr);
    }

    public sealed record ProcessResult(int ExitCode, string Stdout, string Stderr);
}
