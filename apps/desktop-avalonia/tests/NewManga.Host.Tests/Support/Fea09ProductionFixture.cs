using System.Diagnostics;
using System.Text;
using NewManga.App.Services;
using NewManga.Host.Tests.Support;

namespace NewManga.Host.Tests;

/// <summary>Real source-process sidecars behind unmodified HostRuntime + HostController.
/// The launcher only forwards stdio. Test-only markers inject transport refusals or pause
/// AFTER a real source has committed, without replacing planner/receipt/SQLite behavior.</summary>
public sealed class Fea09ProductionFixture : IAsyncLifetime
{
    public string Root { get; private set; } = null!;
    public string Repo { get; private set; } = null!;
    public HostController Controller { get; private set; } = null!;
    public string DataRoot { get; private set; } = null!;
    public string LogRoot => Path.Combine(Root, "logs");
    public async Task InitializeAsync()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !Directory.Exists(Path.Combine(dir.FullName, ".git"))) dir = dir.Parent;
        Repo = dir!.FullName;
        Root = Directory.CreateDirectory(Path.Combine(Repo + ".workspace", "FEA-09-UI-1", "production-" + Guid.NewGuid().ToString("N"))).FullName;
        var sidecars = Directory.CreateDirectory(Path.Combine(Root, "sidecars")).FullName;
        var python = Environment.GetEnvironmentVariable("NEWMANGA_BUILD_PYTHON") ?? "C:/Python314/python.exe";
        var source = Path.Combine(sidecars, "Launcher.cs");
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
            while ((line = Console.ReadLine()) != null) {
                child.StandardInput.WriteLine(line);
                child.StandardInput.Flush();
            }
            try { child.StandardInput.Close(); } catch (IOException) {}
            child.WaitForExit();
            stdout.Join(2000); stderr.Join(2000);
            return child.ExitCode;
        }
    }
}
""".Replace("PYTHON", python.Replace("\"", "\"\""));


        await File.WriteAllTextAsync(source, launcher);
        var csc = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Windows), "Microsoft.NET", "Framework64", "v4.0.30319", "csc.exe");
        var exe = Path.Combine(sidecars, "core_service.exe");
        var compile = HostFixture.Run(csc, "/nologo", "/target:exe", "/out:" + exe, source);
        Assert.True(compile.ExitCode == 0, compile.Stdout + compile.Stderr);
        File.Copy(exe, Path.Combine(sidecars, "host_bridge.exe"));
        var prelude = "import sys; sys.path.insert(0, " + PythonString(Path.Combine(Repo, "src")) + ")\n";
        await File.WriteAllTextAsync(Path.Combine(sidecars, "host_bridge.py"), prelude + "from infrastructure.resource_channel.host_bridge import main\nraise SystemExit(main())\n");
        var hooks = """
import json, pathlib, time
import bootstrap.core_service as m
from application.importing.referenced.runtime import ReferencedImportRuntime
control = pathlib.Path(__file__).parent.parent
original_dispatch = m.CoreServiceServer._dispatch_request
def dispatch(self, line):
    req = json.loads(line)
    fault_file = control / 'fault'
    fault = fault_file.read_text() if fault_file.exists() else ''
    if fault == 'register' and req.get('command') == 'RegisterSourceReadGrant' and req.get('payload', {}).get('secret_ref'):
        return self._reject_host_control(req['request_id'], 'SOURCE_ACCESS_DENIED', 'validation', 'injected registration refusal'), False
    if fault == 'start' and req.get('command') == 'StartImportReferences':
        req['payload']['plan_digest'] = '0' * 64
        line = json.dumps(req)
    response, stop = original_dispatch(self, line)
    if fault == 'capability' and req.get('command') == 'core.ping':
        response['result']['capabilities'].remove('source.resolve-secret/1')
    if fault == 'replan' and req.get('command') == 'PlanImportReferences':
        response['result'] = None
    return response, stop
m.CoreServiceServer._dispatch_request = dispatch
original_process = ReferencedImportRuntime._process_source
def process_source(self, operation, *args, **kwargs):
    result = original_process(self, operation, *args, **kwargs)
    if (control / 'pause').exists() and sum(p.committed_pages for p in operation.progress) == 1:
        (control / 'paused').touch()
        deadline = time.monotonic() + 30
        while not (control / 'release').exists() and time.monotonic() < deadline:
            time.sleep(.01)
    return result
ReferencedImportRuntime._process_source = process_source
raise SystemExit(m.main())
""";
        await File.WriteAllTextAsync(Path.Combine(sidecars, "core_service.py"), prelude + hooks);
        // Use the existing fixture's isolated options shape; use our Task workspace for all data/logs.
        var template = HostFixture.CreateOptions("fea09-production", out _, parity: true, sidecarDirectoryOverride: sidecars);
        DataRoot = Path.Combine(Root, "data");
        Controller = new HostController(new HostOptions
        {
            DataRoot = DataRoot, LogDirectory = LogRoot, SidecarDirectoryOverride = sidecars,
            MutexName = template.MutexName, DetectLegacyShell = false, ParityReached = true,
            FirstRunBackupEnabled = false, EnableWireEvidence = true,
            StartupTimeout = TimeSpan.FromSeconds(90), RequestTimeout = TimeSpan.FromSeconds(90),
        });
        await Controller.StartAsync();
        Assert.Equal(HostViewState.Ready, Controller.Snapshot.State);
        Assert.True(Controller.Snapshot.WritesAllowed, Controller.Snapshot.ErrorMessage);
    }
    private static string PythonString(string value) => "r'" + value.Replace("'", "\\'") + "'";
    public async Task DisposeAsync() { if (Controller is not null) await Controller.DisposeAsync(); }
}

internal sealed class ProductionIpcFactAttribute : FactAttribute
{
    public ProductionIpcFactAttribute()
    {
        if (Environment.GetEnvironmentVariable("NEWMANGA_FEA09_IPC") != "1")
            Skip = "reason: set NEWMANGA_FEA09_IPC=1 for real HostController + ImportDockViewModel stdio tests";
    }
}
