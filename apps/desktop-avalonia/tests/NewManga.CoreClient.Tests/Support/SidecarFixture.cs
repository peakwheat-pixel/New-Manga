using System.Diagnostics;
using System.Text;
using System.Text.Json;
using NewManga.CoreClient;
using NewManga.CoreClient.Bridge;
using NewManga.CoreClient.Transport;

namespace NewManga.CoreClient.Tests.Support;

/// <summary>
/// Test environment for the real (unlabelled) sidecar copy. AC11: the repository tree carries a Low
/// mandatory label, so tests must run the sidecars from a copy outside it; this helper refuses to
/// guess and tells you which environment variable to set (scripts/test.ps1 sets it).
/// </summary>
public static class SidecarFixture
{
    public const string SidecarDirectoryVariable = "NEWMANGA_CORECLIENT_SIDECAR_DIR";
    public const string EvidenceDirectoryVariable = "NEWMANGA_EVIDENCE_DIR";
    public const string CatalogLoaderFileName = "catalog_loader.exe";
    public const string CoreServiceFileName = "core_service.exe";
    public const string HostBridgeFileName = "host_bridge.exe";

    public static string SidecarDirectory
    {
        get
        {
            var directory = Environment.GetEnvironmentVariable(SidecarDirectoryVariable);
            if (string.IsNullOrWhiteSpace(directory))
            {
                throw new InvalidOperationException(
                    $"{SidecarDirectoryVariable} is not set. Run tests through scripts/test.ps1, which copies the " +
                    "frozen sidecars to an unlabelled workspace directory (AC11).");
            }

            foreach (var exe in new[] { CoreServiceFileName, HostBridgeFileName, CatalogLoaderFileName })
            {
                if (!File.Exists(Path.Combine(directory, exe)))
                {
                    throw new InvalidOperationException($"{exe} is missing under {SidecarDirectoryVariable}={directory}");
                }
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
                directory = Path.Combine(Path.GetTempPath(), "newmanga-host-client-evidence");
            }

            Directory.CreateDirectory(directory);
            return directory;
        }
    }

    public static string Exe(string fileName) => Path.Combine(SidecarDirectory, fileName);

    public static string NewDataRoot(string label)
    {
        var root = Path.Combine(
            Path.GetTempPath(),
            "newmanga-host-client-tests",
            label + "-" + Guid.NewGuid().ToString("N")[..10]);
        Directory.CreateDirectory(Path.Combine(root, "derived"));
        Directory.CreateDirectory(Path.Combine(root, "catalog"));
        Directory.CreateDirectory(Path.Combine(root, "managed"));
        return root;
    }

    public static CoreServiceOptions CreateCoreOptions(string testName, out string dataRoot, string? executablePath = null)
    {
        dataRoot = NewDataRoot(testName);
        var logDirectory = Path.Combine(EvidenceDirectory, "logs", testName);
        Directory.CreateDirectory(logDirectory);
        return new CoreServiceOptions
        {
            ExecutablePath = executablePath ?? Exe(CoreServiceFileName),
            DataRoot = dataRoot,
            DerivedRoot = Path.Combine(dataRoot, "derived"),
            CatalogDbPath = Path.Combine(dataRoot, "catalog", "catalog.sqlite"),
            ManagedRoot = Path.Combine(dataRoot, "managed"),
            StderrLogPath = Path.Combine(logDirectory, "core_service.stderr.log"),
            WireLogPath = Path.Combine(EvidenceDirectory, "wire", testName + ".ndjson"),
            StartupTimeout = TimeSpan.FromSeconds(60),
            RequestTimeout = TimeSpan.FromSeconds(60),
        };
    }

    public sealed class BridgeContext : IDisposable
    {
        public required string TestName { get; init; }

        public required string DataRoot { get; init; }

        public required HostBridgeOptions Options { get; init; }

        public required string CatalogLoaderStdout { get; init; }

        public required string CatalogLoaderStderr { get; init; }

        public required int CatalogLoaderExitCode { get; init; }

        public void Dispose()
        {
            try
            {
                Directory.Delete(DataRoot, recursive: true);
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
            {
                // best effort
            }
        }
    }

    public static BridgeContext CreateBridgeContext(string testName)
    {
        const string resourceId = "res-1";
        const string relPath = "book/page01.jpg";
        var dataRoot = NewDataRoot(testName);
        var managedRoot = Path.Combine(dataRoot, "managed");
        var derivedRoot = Path.Combine(dataRoot, "derived");
        var catalogDb = Path.Combine(dataRoot, "catalog", "catalog.sqlite");
        var page = Path.Combine(managedRoot, "book", "page01.jpg");
        Directory.CreateDirectory(Path.GetDirectoryName(page)!);
        File.WriteAllBytes(page, Encoding.UTF8.GetBytes("fake-jpeg-bytes-" + new string('x', 1024)));

        var loader = RunProcess(
            Exe(CatalogLoaderFileName),
            new[]
            {
                "--db", catalogDb,
                "--initialize-preview-namespace", derivedRoot,
                "--set", $"{resourceId}={relPath}@managed-read-only",
                "--dump",
            },
            workingDirectory: SidecarDirectory);

        if (loader.ExitCode != 0)
        {
            throw new InvalidOperationException(
                $"catalog_loader failed ({loader.ExitCode}): {loader.Stdout} {loader.Stderr}");
        }

        var logDirectory = Path.Combine(EvidenceDirectory, "logs", testName);
        Directory.CreateDirectory(logDirectory);
        return new BridgeContext
        {
            TestName = testName,
            DataRoot = dataRoot,
            CatalogLoaderStdout = loader.Stdout,
            CatalogLoaderStderr = loader.Stderr,
            CatalogLoaderExitCode = loader.ExitCode,
            Options = new HostBridgeOptions
            {
                ExecutablePath = Exe(HostBridgeFileName),
                DerivedRoot = derivedRoot,
                ManagedRoot = managedRoot,
                CatalogDbPath = catalogDb,
                StderrLogPath = Path.Combine(logDirectory, "host_bridge.stderr.log"),
                WireLogPath = Path.Combine(EvidenceDirectory, "wire", testName + ".ndjson"),
                StartupTimeout = TimeSpan.FromSeconds(60),
                RequestTimeout = TimeSpan.FromSeconds(60),
            },
        };
    }

    public sealed record ProcessResult(int ExitCode, string Stdout, string Stderr);

    public static ProcessResult RunProcess(
        string executablePath,
        IReadOnlyList<string> arguments,
        string? workingDirectory = null,
        IReadOnlyDictionary<string, string>? environment = null,
        int timeoutMs = 60_000)
    {
        var startInfo = new ProcessStartInfo
        {
            FileName = executablePath,
            WorkingDirectory = workingDirectory ?? Path.GetDirectoryName(executablePath) ?? Environment.CurrentDirectory,
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
        };
        foreach (var argument in arguments)
        {
            startInfo.ArgumentList.Add(argument);
        }

        if (environment is not null)
        {
            foreach (var pair in environment)
            {
                startInfo.Environment[pair.Key] = pair.Value;
            }
        }

        using var process = Process.Start(startInfo)
            ?? throw new InvalidOperationException($"failed to start {executablePath}");
        var stdout = process.StandardOutput.ReadToEnd();
        var stderr = process.StandardError.ReadToEnd();
        if (!process.WaitForExit(timeoutMs))
        {
            try
            {
                process.Kill(true);
            }
            catch (InvalidOperationException)
            {
                // already gone
            }

            throw new TimeoutException($"{executablePath} did not exit within {timeoutMs} ms");
        }

        return new ProcessResult(process.ExitCode, stdout, stderr);
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
            // best effort
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

    public static void WriteFrameSummary(Utf8JsonWriter writer, string name, IReadOnlyList<WireFrame> frames)
    {
        writer.WritePropertyName(name);
        writer.WriteStartArray();
        foreach (var frame in frames)
        {
            writer.WriteStartObject();
            writer.WriteString("sidecar", frame.Sidecar);
            writer.WriteString("request", frame.RequestLine);
            writer.WriteString("response", frame.ResponseLine);
            writer.WriteString("request_utf8_hex", frame.RequestUtf8Hex);
            writer.WriteBoolean("request_ascii_only", frame.RequestAsciiOnly);
            writer.WriteBoolean("response_ascii_only", frame.ResponseAsciiOnly);
            writer.WriteNumber("elapsed_ms", Math.Round(frame.ElapsedMs, 3));
            writer.WriteEndObject();
        }

        writer.WriteEndArray();
    }
}
