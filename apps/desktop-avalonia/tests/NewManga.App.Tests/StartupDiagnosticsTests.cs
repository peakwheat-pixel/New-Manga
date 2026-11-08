using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using NewManga.App.Services;
using NewManga.Appearance;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-07 AC4（A07）诊断面：<c>StartupDiagnostics</c> 最小 sink 的行为、9 类外观 warning 的逐项
/// fail-safe，以及 4 组参数的真实进程入口（无桌面会话/未开门禁时 skip + reason）。
/// </summary>
public sealed class StartupDiagnosticsTests : IDisposable
{
    private readonly string _root;

    public StartupDiagnosticsTests()
    {
        _root = Path.Combine(Path.GetTempPath(), $"nm-fea07-diagnostics-{Guid.NewGuid():N}");
        Directory.CreateDirectory(_root);
    }

    public void Dispose()
    {
        StartupDiagnostics.ResetForTests();
        try
        {
            Directory.Delete(_root, recursive: true);
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
        {
            // best-effort cleanup
        }
    }

    // ------------------------------------------------------------------ sink

    [Fact]
    public void Install_WritesStartupLogAndStaysTraceCompatible()
    {
        var logDirectory = Path.Combine(_root, "logs");

        Assert.True(StartupDiagnostics.Install(logDirectory));
        Assert.True(StartupDiagnostics.IsInstalled);
        Assert.Equal(Path.Combine(logDirectory, StartupDiagnostics.FileName), StartupDiagnostics.LogPath);

        // The composition root keeps its existing Trace calls; the sink is the only new surface.
        var plan = SafeStartupPlanner.Plan(
            AppOptions.Parse(Array.Empty<string>()),
            AppearanceDefaults.Settings,
            Array.Empty<string>());
        StartupDiagnostics.Report(plan);
        Trace.TraceWarning("startup fell back to the Current V2 shell: builtin.current-v2");

        var log = ReadShared(StartupDiagnostics.LogPath!);
        Assert.Contains("startup-diagnostics: sink v1 installed", log, StringComparison.Ordinal);
        Assert.Contains("startup: shell=Default", log, StringComparison.Ordinal);
        Assert.Contains("effective=builtin.current-v2", log, StringComparison.Ordinal);
        Assert.Contains("fallback=False", log, StringComparison.Ordinal);
        Assert.Contains("WARN", log, StringComparison.Ordinal);
        Assert.Contains("startup fell back to the Current V2 shell", log, StringComparison.Ordinal);

        // Trace compatibility: the message also reaches the non-file listeners of the same process.
        var recorder = new RecordingListener();
        Trace.Listeners.Add(recorder);
        try
        {
            StartupDiagnostics.Report(plan);
            Assert.Contains(recorder.Messages, message => message.Contains("shell=Default", StringComparison.Ordinal));
        }
        finally
        {
            Trace.Listeners.Remove(recorder);
        }
    }

    [Fact]
    public void Install_IsIdempotentPerProcess()
    {
        var first = Path.Combine(_root, "logs-a");

        Assert.True(StartupDiagnostics.Install(first));
        Assert.False(StartupDiagnostics.Install(Path.Combine(_root, "logs-b")));
        Assert.Equal(Path.Combine(first, StartupDiagnostics.FileName), StartupDiagnostics.LogPath);
    }

    [Fact]
    public void Install_DegradesToNoSinkWhenTheDirectoryCannotBeUsed()
    {
        // A regular file where the log directory should be: the sink must not throw (diagnostics are
        // never a new startup failure surface) and must report "not installed".
        var blocker = Path.Combine(_root, "blocked");
        File.WriteAllText(blocker, "not a directory");

        Assert.False(StartupDiagnostics.Install(blocker));
        Assert.False(StartupDiagnostics.IsInstalled);
        Assert.Null(StartupDiagnostics.LogPath);

        // The startup decision can still be reported; it simply has no file sink.
        StartupDiagnostics.Report(null);
    }

    // ------------------------------------------------- 9 类 warning 逐项 fail-safe

    private static readonly (string Label, string Json, string Token)[] WarningClasses =
    [
        ("bad-json", "{ this is not a json appearance document", "not valid JSON"),
        ("schemaVersion", "{\"schemaVersion\": 0}", "unsupported schemaVersion"),
        ("corners.scale", "{\"corners\":{\"scale\":\"xs\"}}", "unsupported corners.scale"),
        ("appearance.mode", "{\"appearance.mode\":\"sepia\"}", "unsupported appearance.mode"),
        ("appearance.contrast", "{\"appearance.contrast\":\"low\"}", "unsupported appearance.contrast"),
        ("motion.mode", "{\"motion.mode\":\"warp\"}", "unsupported motion.mode"),
        ("motion.categories", "{\"motion.categories\":5}", "'motion.categories' must be an object or 'off'"),
        ("theme.frontendId", "{\"theme.frontendId\":\"builtin.not-a-frontend\"}", "unknown theme.frontendId"),
        ("theme.visualThemeId", "{\"theme.visualThemeId\":\"nope\"}", "unknown theme.visualThemeId"),
    ];

    public static TheoryData<string, string, string> WarningClassData()
    {
        var data = new TheoryData<string, string, string>();
        foreach (var (label, json, token) in WarningClasses)
        {
            data.Add(label, json, token);
        }

        return data;
    }

    /// <summary>
    /// AC4：9 类 warning 每一类都必须单独 fail-safe 到 Current V2（planner 是组合根唯一决策源），
    /// 且该 warning 作为诊断行可见（可诊断）。
    /// </summary>
    [Theory]
    [MemberData(nameof(WarningClassData))]
    public void EachAppearanceWarningClass_ForcesCurrentV2AndIsDiagnosable(
        string label, string json, string token)
    {
        Assert.False(string.IsNullOrWhiteSpace(label));
        var read = AppearanceJson.Read(json);

        Assert.NotEmpty(read.Warnings);
        Assert.Contains(read.Warnings, warning => warning.Contains(token, StringComparison.Ordinal));

        var plan = SafeStartupPlanner.Plan(
            AppOptions.Parse(Array.Empty<string>()),
            read.Settings,
            read.Warnings);

        Assert.True(plan.IsFallback, $"{label}: the planner must fail safe to Current V2");
        Assert.Equal(FrontendSelector.CurrentV2FrontendId, plan.EffectiveFrontendId);
        Assert.Contains(plan.Diagnostics, diagnostic =>
            diagnostic.Contains(token, StringComparison.Ordinal));

        // Fail-safe never loses the requested document: the persisted settings still parse field by field.
        Assert.False(string.IsNullOrWhiteSpace(read.Settings.FrontendId));
        Assert.True(read.Settings.SchemaVersion >= AppearanceSettings.CurrentSchemaVersion);
    }

    /// <summary>
    /// AC4 真实进程入口：4 组参数（默认 / <c>--presentation-host=true</c> / <c>--shell=legacy</c> /
    /// 坏外观文档）→ <c>exit_code=0</c>、无 <c>fatal.log</c>、<c>startup.log</c> 含对应诊断行。
    /// 无桌面会话或未开 <c>NEWMANGA_FEA07_STARTUP_PROCESS</c> 时由 attribute skip + reason。
    /// </summary>
    [FEA07StartupProcessFact]
    public void RealProcessLaunchMatrix_ExitZeroAndDiagnosableStartupLog()
    {
        var executable = RealStartupProcessFixture.LocateAppExecutable();
        Assert.True(File.Exists(executable), $"App executable not found: {executable}");

        var cases = new (string Name, string[] ExtraArgs, bool CorruptDocument, string Expected)[]
        {
            ("default", Array.Empty<string>(), false, "startup: shell=Default"),
            ("presentation-host", ["--presentation-host=true"], false, "startup: shell=PresentationHost"),
            ("shell-legacy", ["--shell=legacy"], false, "startup: shell=Legacy"),
            ("corrupt-appearance", Array.Empty<string>(), true, "startup: appearance: appearance document is not valid JSON"),
        };

        var evidence = new List<string>();
        foreach (var (name, extraArgs, corruptDocument, expected) in cases)
        {
            var root = Path.Combine(_root, name);
            var themeHome = Path.Combine(root, "theme");
            var logDirectory = Path.Combine(root, "logs");
            Directory.CreateDirectory(themeHome);
            if (corruptDocument)
            {
                File.WriteAllText(
                    Path.Combine(themeHome, AppearanceStore.FileName),
                    "{ this is not a json appearance document");
            }

            var arguments = new List<string>
            {
                "--data-root=" + Path.Combine(root, "data"),
                "--log-dir=" + logDirectory,
                "--theme-home=" + themeHome,
                "--mutex-name=" + "Local\\NewManga.App.Tests.Fea07Startup." + Guid.NewGuid().ToString("N")[..12],
                "--exit-after=2500",
            };
            arguments.AddRange(extraArgs);

            var (exitCode, timedOut, stdout, stderr) =
                RealStartupProcessFixture.Run(executable, arguments, TimeSpan.FromSeconds(120));
            Assert.False(timedOut, $"{name}: the real process did not exit (stdout:{stdout} stderr:{stderr})");
            Assert.True(exitCode == 0, $"{name}: exit_code={exitCode} stdout:{stdout} stderr:{stderr}");

            var fatal = Path.Combine(logDirectory, "fatal.log");
            Assert.False(File.Exists(fatal), $"{name}: fatal.log must not exist ({ReadIfExists(fatal)})");

            var startupLog = Path.Combine(logDirectory, StartupDiagnostics.FileName);
            Assert.True(File.Exists(startupLog), $"{name}: startup.log was not written");
            var log = File.ReadAllText(startupLog);
            Assert.Contains(expected, log, StringComparison.Ordinal);
            if (corruptDocument)
            {
                Assert.Contains("fallback=True", log, StringComparison.Ordinal);
            }
            else
            {
                Assert.Contains("fallback=False", log, StringComparison.Ordinal);
            }

            evidence.Add(
                $"{name}: exit_code={exitCode} fatal_log=false startup_rows={log.Split('\n').Length} " +
                $"matched='{expected}'");
        }

        // 证据落在隔离临时根下（AC8/W-9：不写真实 %APPDATA%）。
        var evidencePath = Path.Combine(_root, "startup-process-matrix.txt");
        File.WriteAllText(evidencePath, string.Join(Environment.NewLine, evidence) + Environment.NewLine + "PASS");
        Assert.Contains("PASS", File.ReadAllText(evidencePath), StringComparison.Ordinal);
    }

    private static string ReadIfExists(string path) => File.Exists(path) ? File.ReadAllText(path) : "<missing>";

    /// <summary>The sink keeps its writer open (append, AutoFlush), so tests must read with write sharing.</summary>
    private static string ReadShared(string path)
    {
        using var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete);
        using var reader = new StreamReader(stream);
        return reader.ReadToEnd();
    }

    private sealed class RecordingListener : TraceListener
    {
        private readonly List<string> _messages = [];

        public IReadOnlyList<string> Messages
        {
            get
            {
                lock (_messages)
                {
                    return _messages.ToArray();
                }
            }
        }

        public override void Write(string? message) => Add(message);

        public override void WriteLine(string? message) => Add(message);

        public override void TraceEvent(
            TraceEventCache? eventCache, string source, TraceEventType eventType, int id, string? message) =>
            Add(message);

        public override void TraceEvent(
            TraceEventCache? eventCache, string source, TraceEventType eventType, int id, string? format,
            params object?[]? args) =>
            Add(format is null || args is null || args.Length == 0
                ? format
                : string.Format(System.Globalization.CultureInfo.InvariantCulture, format, args));

        private void Add(string? message)
        {
            if (message is null)
            {
                return;
            }

            lock (_messages)
            {
                _messages.Add(message);
            }
        }
    }
}

/// <summary>
/// AC4 真实进程用例的 gated 条件：必须显式开门禁（<c>NEWMANGA_FEA07_STARTUP_PROCESS=1</c>）**且** 存在
/// 交互桌面会话；否则 skip + 明确 reason（`NOT_RUN` 不写成 PASS）。
/// </summary>
public sealed class FEA07StartupProcessFactAttribute : FactAttribute
{
    public const string GateVariable = "NEWMANGA_FEA07_STARTUP_PROCESS";

    public FEA07StartupProcessFactAttribute()
    {
        if (Environment.GetEnvironmentVariable(GateVariable) != "1")
        {
            Skip = $"reason: gated real-process startup matrix; set {GateVariable}=1 " +
                   "and run from an interactive desktop session";
            return;
        }

        if (RealStartupProcessFixture.DesktopSessionReason() is { } reason)
        {
            Skip = reason;
        }
    }
}

/// <summary>4 组参数真实进程矩阵的启动器（隔离临时根；不写真实 %APPDATA%）。</summary>
internal static class RealStartupProcessFixture
{
    /// <summary>App 可执行文件位于测试输出目录（App 项目是 Exe，随引用复制）。</summary>
    public static string LocateAppExecutable() =>
        Path.Combine(AppContext.BaseDirectory, OperatingSystem.IsWindows() ? "NewManga.App.exe" : "NewManga.App");

    /// <summary>
    /// Windows 服务会话（session 0）没有交互桌面：真实窗口用例必须 skip 而不是伪装成 PASS。
    /// </summary>
    public static string? DesktopSessionReason()
    {
        if (!OperatingSystem.IsWindows())
        {
            return "reason: real-process startup matrix requires Windows desktop";
        }

        try
        {
            if (Process.GetCurrentProcess().SessionId == 0)
            {
                return "reason: no interactive desktop session (Windows session 0); " +
                       "the real startup window matrix is NOT_RUN here";
            }
        }
        catch (Exception ex) when (ex is InvalidOperationException or PlatformNotSupportedException)
        {
            return "reason: desktop session could not be determined (" + ex.GetType().Name + ")";
        }

        return null;
    }

    public static (int ExitCode, bool TimedOut, string Stdout, string Stderr) Run(
        string executable,
        IReadOnlyList<string> arguments,
        TimeSpan timeout)
    {
        var startInfo = new ProcessStartInfo(executable)
        {
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            WorkingDirectory = Path.GetDirectoryName(executable) ?? ".",
        };
        foreach (var argument in arguments)
        {
            startInfo.ArgumentList.Add(argument);
        }

        using var process = Process.Start(startInfo)
            ?? throw new InvalidOperationException($"failed to start {executable}");
        var stdout = process.StandardOutput.ReadToEndAsync();
        var stderr = process.StandardError.ReadToEndAsync();
        if (!process.WaitForExit((int)timeout.TotalMilliseconds))
        {
            process.Kill(entireProcessTree: true);
            process.WaitForExit(10_000);
            return (-1, true, stdout.GetAwaiter().GetResult(), stderr.GetAwaiter().GetResult());
        }

        return (process.ExitCode, false, stdout.GetAwaiter().GetResult(), stderr.GetAwaiter().GetResult());
    }
}
