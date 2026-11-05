using System.Diagnostics;
using System.Text;
using NewManga.App.Services;
using NewManga.Host.Tests.Support;

namespace NewManga.Host.Tests;

/// <summary>
/// FEA-12-UI L2 evidence: a REAL Host → Python Core chain (unmodified HostRuntime + HostController +
/// the App's production trash port) over stdio. The sidecars are compiled launchers that forward
/// stdin/stdout to the repository's own <c>src/bootstrap/core_service.py</c> and
/// <c>host_bridge.py</c>, so the trash commands under test are the real Python handlers.
///
/// Gated by <c>NEWMANGA_FEA12_UI_IPC=1</c> (one real Core child process for the whole class).
/// </summary>
public sealed class Fea12ProductionFixture : IAsyncLifetime
{
    public string Root { get; private set; } = null!;
    public string Repo { get; private set; } = null!;
    public HostController Controller { get; private set; } = null!;

    public string DataRoot { get; private set; } = null!;

    /// <summary>AC8 sentinel tree OUTSIDE the isolated Core DataRoot (must stay byte-identical).</summary>
    public string SentinelRoot { get; private set; } = null!;

    public string LogRoot => Path.Combine(Root, "logs");

    public string WireDirectory => Path.Combine(LogRoot, "wire");

    public async Task InitializeAsync()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !Directory.Exists(Path.Combine(dir.FullName, ".git")))
        {
            dir = dir.Parent;
        }

        Repo = dir!.FullName;
        Root = Directory.CreateDirectory(Path.Combine(
            Repo + ".workspace", "FEA-12-UI", "ipc-" + Guid.NewGuid().ToString("N"))).FullName;
        var sidecars = Directory.CreateDirectory(Path.Combine(Root, "sidecars")).FullName;
        var python = Environment.GetEnvironmentVariable("NEWMANGA_BUILD_PYTHON") ?? "C:/Python314/python.exe";

        var launcher = """
using System;
using System.Diagnostics;
using System.IO;
using System.Threading;
class Launcher {
    static int Main() {
        string script = Path.ChangeExtension(System.Reflection.Assembly.GetExecutingAssembly().Location, ".py");
        var info = new ProcessStartInfo(@"PYTHON", "-X utf8 \"" + script + "\"");
        info.UseShellExecute = false;
        info.CreateNoWindow = true;
        info.RedirectStandardInput = info.RedirectStandardOutput = info.RedirectStandardError = true;
        using (var child = Process.Start(info)) {
            var stdout = new Thread(() => { try { child.StandardOutput.BaseStream.CopyTo(Console.OpenStandardOutput()); Console.Out.Flush(); } catch (IOException) {} catch (ObjectDisposedException) {} });
            var stderr = new Thread(() => { try { child.StandardError.BaseStream.CopyTo(Console.OpenStandardError()); Console.Error.Flush(); } catch (IOException) {} catch (ObjectDisposedException) {} });
            stdout.IsBackground = true; stderr.IsBackground = true;
            stdout.Start(); stderr.Start();
            string line;
            while ((line = Console.ReadLine()) != null) { child.StandardInput.WriteLine(line); child.StandardInput.Flush(); }
            try { child.StandardInput.Close(); } catch (IOException) {}
            child.WaitForExit();
            stdout.Join(2000); stderr.Join(2000);
            return child.ExitCode;
        }
    }
}
""".Replace("PYTHON", python.Replace("\"", "\"\""));
        var source = Path.Combine(sidecars, "Launcher.cs");
        await File.WriteAllTextAsync(source, launcher);
        var csc = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.Windows),
            "Microsoft.NET", "Framework64", "v4.0.30319", "csc.exe");
        var exe = Path.Combine(sidecars, "core_service.exe");
        var compile = HostFixture.Run(csc, "/nologo", "/target:exe", "/out:" + exe, source);
        Assert.True(compile.ExitCode == 0, compile.Stdout + compile.Stderr);
        File.Copy(exe, Path.Combine(sidecars, "host_bridge.exe"));
        var prelude = "import sys; sys.path.insert(0, " + PythonString(Path.Combine(Repo, "src")) + ")\n";
        await File.WriteAllTextAsync(
            Path.Combine(sidecars, "core_service.py"),
            prelude + "import bootstrap.core_service as m\nraise SystemExit(m.main())\n");
        await File.WriteAllTextAsync(
            Path.Combine(sidecars, "host_bridge.py"),
            prelude + "from infrastructure.resource_channel.host_bridge import main\nraise SystemExit(main())\n");

        var template = HostFixture.CreateOptions("fea12-ui-ipc", out _, parity: true, sidecarDirectoryOverride: sidecars);
        DataRoot = Path.Combine(Root, "data");
        SentinelRoot = Directory.CreateDirectory(Path.Combine(Root, "sentinel")).FullName;
        await File.WriteAllTextAsync(Path.Combine(SentinelRoot, "keep-me.txt"), "FEA-12-UI sentinel: 原文件零触碰");
        await File.WriteAllTextAsync(Path.Combine(SentinelRoot, "notes.json"), "{\"keep\":true}");
        Controller = new HostController(new HostOptions
        {
            DataRoot = DataRoot,
            LogDirectory = LogRoot,
            SidecarDirectoryOverride = sidecars,
            MutexName = template.MutexName,
            DetectLegacyShell = false,
            ParityReached = true,
            FirstRunBackupEnabled = false,
            EnableWireEvidence = true,
            StartupTimeout = TimeSpan.FromSeconds(120),
            RequestTimeout = TimeSpan.FromSeconds(120),
        });
        await Controller.StartAsync();
        Assert.Equal(HostViewState.Ready, Controller.Snapshot.State);
        Assert.True(Controller.Snapshot.WritesAllowed, Controller.Snapshot.ErrorMessage);
    }

    private static string PythonString(string value) => "r'" + value.Replace("'", "\\'") + "'";

    public async Task DisposeAsync()
    {
        if (Controller is not null)
        {
            await Controller.DisposeAsync();
        }
    }
}

/// <summary>Skips the real-IPC test unless the curated run asks for it (same gate style as FEA-09).</summary>
internal sealed class Fea12IpcFactAttribute : FactAttribute
{
    public Fea12IpcFactAttribute()
    {
        if (Environment.GetEnvironmentVariable("NEWMANGA_FEA12_UI_IPC") != "1")
        {
            Skip = "reason: set NEWMANGA_FEA12_UI_IPC=1 to run the real Host→Core recycle-bin IPC test";
        }
    }
}

internal static class Fea12WireEvidence
{
    /// <summary>Reads every core-service wire frame as (command, payload) from the NDJSON evidence file.</summary>
    public static IReadOnlyList<(string Command, System.Text.Json.JsonElement Payload)> CoreFrames(string wireDirectory)
    {
        var path = Path.Combine(wireDirectory, "core-service.ndjson");
        if (!File.Exists(path))
        {
            return Array.Empty<(string, System.Text.Json.JsonElement)>();
        }

        var frames = new List<(string, System.Text.Json.JsonElement)>();
        foreach (var line in File.ReadLines(path))
        {
            if (string.IsNullOrWhiteSpace(line))
            {
                continue;
            }

            using var document = System.Text.Json.JsonDocument.Parse(line);
            if (!document.RootElement.TryGetProperty("request", out var request) ||
                request.ValueKind != System.Text.Json.JsonValueKind.String)
            {
                continue;
            }

            using var requestDocument = System.Text.Json.JsonDocument.Parse(request.GetString()!);
            var command = requestDocument.RootElement.TryGetProperty("command", out var commandValue)
                ? commandValue.GetString() ?? string.Empty
                : string.Empty;
            var payload = requestDocument.RootElement.TryGetProperty("payload", out var payloadValue)
                ? payloadValue.Clone()
                : default;
            frames.Add((command, payload));
        }

        return frames;
    }

    public static string Describe(string command) => command.Length == 0 ? "<none>" : command;

    public static string FirstNonEmpty(string value) => value.Length == 0 ? "<none>" : value;

    internal static string Ascii(string value) => Encoding.ASCII.GetString(Encoding.UTF8.GetBytes(value));
}
