using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using NewManga.App.Services;
using NewManga.Appearance;
using NewManga.Presentation.Avalonia.Switching;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-07 AC-R4b-2（AC3 / A06）真实**跨进程**崩溃注入（外部驱动 park → kill → recover 三阶段）。
///
/// 口径（冻结卡实现口径 2 + scope review §3）：
/// <list type="bullet">
/// <item>park 使用 production 事务 <see cref="FrontendSwitchCoordinator"/> 的既有
/// <c>beforeJournalCommit</c> seam（<c>PresentationWindow</c> 的同名构造参数），在「目标 frontend 已由
/// 唯一写者落盘、journal 尚未 commit」的真实崩溃窗口停住；**不用** <c>Environment.FailFast</c>，**不造**
/// 生产 backdoor，**不**同进程冒充。</item>
/// <item>kill 由外部脚本 <c>verification/FEA-07-RESIDUAL-3/tools/crash-switch.ps1</c> 用
/// <c>Process.Kill(entireProcessTree: true)</c> 执行；真死由心跳文件冻结证明。</item>
/// <item>recover 是**新进程**，调用生产恢复入口 <see cref="App.RecoverInterruptedSwitch"/>。</item>
/// </list>
/// 两个 fact 都默认 skip + reason（<c>NEWMANGA_FEA07_CRASH=1</c> + <c>NEWMANGA_FEA07_CRASH_PHASE</c>）。
/// </summary>
public sealed class Fea07Residual3CrashTests
{
    // ---------------------------------------------------------------- park

    [Fea07CrashParkFact]
    public async Task Park_ProductionSwitchStopsBetweenPersistedTargetAndJournalCommit()
    {
        var root = Fea07CrashFixture.RequireRoot("park");
        var python = Fea07CrashFixture.ResolvePython();
        var repo = Fea07CrashFixture.ResolveRepositoryRoot();
        var dbPath = Path.Combine(root, "library.db");

        // 1) 真实 library.db（production migrations）+ 切换前保护列快照。
        await Fea07CrashFixture.RunPythonAsync(repo, python, Fea07CrashFixture.SeedScript(), root);
        Assert.True(File.Exists(dbPath), "seeded library.db is missing");
        var before = await Fea07CrashFixture.SnapshotProtectedAsync(repo, python, dbPath, root, "before");
        await File.WriteAllTextAsync(
            Path.Combine(root, "protected-before.json"),
            JsonSerializer.Serialize(before, new JsonSerializerOptions { WriteIndented = true }));

        // 2) 启动前状态：上一已提交 = Current V2（另有一个非 frontend 字段用于「最新状态」断言）。
        var themeHomeDirectory = Path.Combine(root, "theme-home");
        Directory.CreateDirectory(themeHomeDirectory);
        var appearancePath = Path.Combine(themeHomeDirectory, AppearanceStore.FileName);
        var appearance = new AppearanceCoordinator(new AppearanceStore(appearancePath));
        await appearance.SaveAsync(AppearanceDefaults.Settings with
        {
            FrontendId = Fea07CrashFixture.PreviousFrontendId,
            Mode = AppearanceMode.Dark,
        });
        appearance.Reload();
        Assert.Equal(Fea07CrashFixture.PreviousFrontendId, appearance.FrontendId);

        var heartbeatPath = Path.Combine(root, "heartbeat.txt");
        using var heartbeat = new Heartbeat(heartbeatPath);
        heartbeat.Start();

        var parkPath = Path.Combine(root, "park.json");
        var journal = new SwitchJournal(Path.Combine(themeHomeDirectory, "switch-journal.json"));
        var switcher = new FrontendSwitchCoordinator(
            journal,
            beforeJournalCommit: () =>
            {
                // 崩溃窗口：目标 frontend 已由唯一写者落盘，journal 仍是未完成阶段。
                File.WriteAllText(parkPath, JsonSerializer.Serialize(new
                {
                    phase = "beforeJournalCommit",
                    pid = Environment.ProcessId,
                    target = Fea07CrashFixture.TargetFrontendId,
                    previous = Fea07CrashFixture.PreviousFrontendId,
                    appearanceFrontend = appearance.FrontendId,
                    journalStage = journal.TryRead(out var entry, out _) ? entry?.Stage.ToString() : "<none>",
                    heartbeat = heartbeat.Count,
                    parkedAt = DateTimeOffset.UtcNow,
                }, new JsonSerializerOptions { WriteIndented = true }));

                // 等外部进程 kill；绝不返回（返回就等于「没人 kill 我」，由下面的超时断言报告）。
                Thread.Sleep(TimeSpan.FromMinutes(5));
                throw new InvalidOperationException("park was not killed by the external crash driver");
            });

        AppearanceSettings? previousSettings = null;
        var callbacks = new SwitchCallbacks
        {
            ValidateAsync = _ => Task.CompletedTask,
            BuildTreeAsync = _ => Task.CompletedTask,
            CommitAsync = async token =>
            {
                previousSettings = appearance.Settings;
                await appearance.SaveAsync(previousSettings with
                {
                    FrontendId = Fea07CrashFixture.TargetFrontendId,
                }, token).ConfigureAwait(false);
            },
            RollbackAsync = async _ =>
            {
                if (previousSettings is not null)
                {
                    await appearance.SaveAsync(previousSettings, CancellationToken.None).ConfigureAwait(false);
                }
            },
        };

        var switchTask = switcher.SwitchAsync(
            new SwitchRequest(Fea07CrashFixture.TargetFrontendId, Fea07CrashFixture.PreviousFrontendId),
            callbacks);

        // 外部脚本必须在这个窗口内 kill 掉本进程；否则报失败（`NOT_RUN` 不写成 PASS）。
        var deadline = DateTime.UtcNow.AddMinutes(4);
        while (DateTime.UtcNow < deadline && !switchTask.IsCompleted)
        {
            await Task.Delay(200);
        }

        heartbeat.Stop();
        Assert.Fail(
            "the external crash driver never killed the parked process: " +
            $"park.json={File.Exists(parkPath)} switchCompleted={switchTask.IsCompleted}");
    }

    // -------------------------------------------------------------- recover

    [Fea07CrashRecoverFact]
    public async Task Recover_NewProcessRollsBackAndAdoptsTheLatestProtectedState()
    {
        var root = Fea07CrashFixture.RequireRoot("recover");
        var python = Fea07CrashFixture.ResolvePython();
        var repo = Fea07CrashFixture.ResolveRepositoryRoot();
        var themeHomeDirectory = Path.Combine(root, "theme-home");
        var appearancePath = Path.Combine(themeHomeDirectory, AppearanceStore.FileName);
        var journalPath = Path.Combine(themeHomeDirectory, "switch-journal.json");
        var dbPath = Path.Combine(root, "library.db");

        // 0) 崩溃现场：journal 未完成、目标 frontend 已被落盘（真正的「半切换」状态）。
        var journal = new SwitchJournal(journalPath);
        Assert.True(journal.TryRead(out var interrupted, out var readError),
            "the killed run left no switch journal: " + readError);
        Assert.True(journal.HasInterruptedSwitch(out interrupted));
        Assert.Equal(Fea07CrashFixture.TargetFrontendId, interrupted!.TargetFrontendId);
        Assert.Equal(Fea07CrashFixture.PreviousFrontendId, interrupted.PreviousFrontendId);
        Assert.NotEqual(SwitchStage.RolledBack, interrupted.Stage);

        var appearance = new AppearanceCoordinator(new AppearanceStore(appearancePath));
        appearance.Reload();
        Assert.Equal(Fea07CrashFixture.TargetFrontendId, appearance.FrontendId);

        // 1) 「暂停期保护状态」第二条的前半：暂停期间**外部**改了非 frontend 设置（最新状态）。
        await appearance.SaveAsync(appearance.Settings with { Mode = AppearanceMode.Light });
        appearance.Reload();
        Assert.Equal(AppearanceMode.Light, appearance.Settings.Mode);

        // 2) 新进程走生产恢复入口（与 App.OnFrameworkInitializationCompleted 同一调用）。
        var themeHome = new ThemeHomePaths(
            SettingsFilePath: Path.Combine(themeHomeDirectory, "theme-settings.json"),
            ThemesDirectory: Path.Combine(themeHomeDirectory, "themes"),
            FavoritesFilePath: Path.Combine(themeHomeDirectory, "theme-studio-favorites.json"),
            IsCustom: true);
        App.RecoverInterruptedSwitch(themeHome, appearance);

        // 3) 终态断言。
        Assert.True(journal.TryRead(out var recovered, out _));
        Assert.Equal(SwitchStage.RolledBack, recovered!.Stage);
        Assert.Contains("startup recovery", recovered.Failure, StringComparison.Ordinal);

        appearance.Reload();
        Assert.Equal(Fea07CrashFixture.PreviousFrontendId, appearance.FrontendId);
        Assert.NotEqual(Fea07CrashFixture.TargetFrontendId, appearance.FrontendId);
        Assert.Equal(AppearanceMode.Light, appearance.Settings.Mode);

        // 4) 二次恢复零变化（journal 与 appearance 字节都不动）。
        var journalBytes = await File.ReadAllBytesAsync(journalPath);
        var appearanceBytes = await File.ReadAllBytesAsync(appearancePath);
        App.RecoverInterruptedSwitch(themeHome, appearance);
        Assert.Equal(journalBytes, await File.ReadAllBytesAsync(journalPath));
        Assert.Equal(appearanceBytes, await File.ReadAllBytesAsync(appearancePath));
        appearance.Reload();
        Assert.Equal(Fea07CrashFixture.PreviousFrontendId, appearance.FrontendId);

        // 5) 「暂停期保护状态」第一条：整个 park/kill/recover 窗口零写保护列（内嵌 Python 逐列比对）。
        var beforeSnapshotPath = Path.Combine(root, "protected-before.json");
        Assert.True(File.Exists(beforeSnapshotPath), "the parked run wrote no protected-column snapshot");
        var before = JsonSerializer.Deserialize<Dictionary<string, string>>(
            await File.ReadAllTextAsync(beforeSnapshotPath))!;
        var after = await Fea07CrashFixture.SnapshotProtectedAsync(repo, python, dbPath, root, "after");
        var diff = Fea07CrashFixture.Diff(before, after);
        Assert.True(diff.Count == 0,
            "the crash/rollback window wrote protected columns:\n" + string.Join("\n", diff));
        Assert.Equal("0", after.GetValueOrDefault("region_candidates.row_count"));
        Assert.Equal("rr-crash-2", after.GetValueOrDefault("regions.r-crash-1.current_revision_id"));
        Assert.Equal("1", after.GetValueOrDefault("regions.r-crash-1.region_locked"));
        Assert.Equal("1", after.GetValueOrDefault("regions.r-crash-1.translation_locked"));

        // 6) 证据（隔离根，不写跟踪文件）。
        var evidencePath = Path.Combine(root, "recover-evidence.json");
        await File.WriteAllTextAsync(evidencePath, JsonSerializer.Serialize(new
        {
            status = "ok",
            target = Fea07CrashFixture.TargetFrontendId,
            previous = Fea07CrashFixture.PreviousFrontendId,
            journalStage = recovered.Stage.ToString(),
            journalFailure = recovered.Failure,
            finalFrontendId = appearance.FrontendId,
            latestModePreserved = appearance.Settings.Mode.ToString(),
            secondRecoveryChangedNothing = true,
            protectedColumnDiffs = diff.Count,
            protectedColumns = after.Count,
            candidateRows = after.GetValueOrDefault("region_candidates.row_count"),
        }, new JsonSerializerOptions { WriteIndented = true }));
        Assert.Contains("\"status\": \"ok\"", await File.ReadAllTextAsync(evidencePath), StringComparison.Ordinal);
    }

    /// <summary>心跳文件：kill 后必须冻结（证明进程真的死了，而不是「脚本以为它死了」）。</summary>
    private sealed class Heartbeat : IDisposable
    {
        private readonly string _path;
        private readonly CancellationTokenSource _lifetime = new();
        private volatile bool _running;
        private Thread? _thread;

        public Heartbeat(string path)
        {
            _path = path;
        }

        public int Count { get; private set; }

        public void Start()
        {
            _running = true;
            _thread = new Thread(() =>
            {
                while (_running && !_lifetime.IsCancellationRequested)
                {
                    Count++;
                    try
                    {
                        File.WriteAllText(_path, Count.ToString(System.Globalization.CultureInfo.InvariantCulture));
                    }
                    catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
                    {
                        // best effort: a heartbeat write may race with the reader
                    }

                    Thread.Sleep(100);
                }
            })
            {
                IsBackground = true,
                Name = "fea07-crash-heartbeat",
            };
            _thread.Start();
        }

        public void Stop() => _running = false;

        public void Dispose()
        {
            _running = false;
            _lifetime.Cancel();
            _thread?.Join(TimeSpan.FromSeconds(2));
            _lifetime.Dispose();
        }
    }
}

/// <summary>park 阶段的 gated fact：<c>NEWMANGA_FEA07_CRASH=1</c> 且 phase=park。</summary>
public sealed class Fea07CrashParkFactAttribute : FactAttribute
{
    public Fea07CrashParkFactAttribute() => Fea07CrashFixture.ApplyGate(this, "park");
}

/// <summary>recover 阶段的 gated fact：<c>NEWMANGA_FEA07_CRASH=1</c> 且 phase=recover。</summary>
public sealed class Fea07CrashRecoverFactAttribute : FactAttribute
{
    public Fea07CrashRecoverFactAttribute() => Fea07CrashFixture.ApplyGate(this, "recover");
}

/// <summary>AC-R4b-2 的隔离夹具：门禁、隔离根（<c>&lt;repo&gt;.workspace/FEA-07-RESIDUAL-3/</c>）、
/// 真实 <c>library.db</c> 种子与读库（内嵌 Python 先例，不引入 SQLite 托管依赖）。</summary>
internal static class Fea07CrashFixture
{
    public const string GateVariable = "NEWMANGA_FEA07_CRASH";
    public const string PhaseVariable = "NEWMANGA_FEA07_CRASH_PHASE";
    public const string RootVariable = "NEWMANGA_FEA07_CRASH_ROOT";
    public const string TargetFrontendId = "builtin.fluent";
    public const string PreviousFrontendId = "builtin.current-v2";
    private const string ResultMarker = "RESULT_JSON:";

    public static void ApplyGate(FactAttribute fact, string phase)
    {
        if (Environment.GetEnvironmentVariable(GateVariable) != "1")
        {
            fact.Skip = $"reason: cross-process crash injection is externally driven; set {GateVariable}=1 " +
                        $"and {PhaseVariable}={phase} via verification/FEA-07-RESIDUAL-3/tools/crash-switch.ps1";
            return;
        }

        var configured = Environment.GetEnvironmentVariable(PhaseVariable);
        if (!string.Equals(configured, phase, StringComparison.OrdinalIgnoreCase))
        {
            fact.Skip = $"reason: crash phase '{phase}' not selected (" +
                        $"{PhaseVariable}='{configured ?? "<unset>"}'); driven by crash-switch.ps1";
        }
    }

    public static string RequireRoot(string phase)
    {
        var root = Environment.GetEnvironmentVariable(RootVariable);
        if (string.IsNullOrWhiteSpace(root) || !Directory.Exists(root))
        {
            throw new InvalidOperationException(
                $"{RootVariable} must point at the prepared isolated crash root (phase={phase})");
        }

        return root;
    }

    public static string ResolvePython() =>
        Environment.GetEnvironmentVariable("NEWMANGA_BUILD_PYTHON") ?? "C:/Python314/python.exe";

    public static string ResolveRepositoryRoot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null && !Directory.Exists(Path.Combine(directory.FullName, ".git")))
        {
            directory = directory.Parent;
        }

        return directory?.FullName ?? throw new InvalidOperationException("repository not found");
    }

    public static async Task<IReadOnlyDictionary<string, string>> SnapshotProtectedAsync(
        string repo, string python, string dbPath, string root, string label)
    {
        var element = await RunPythonForJsonAsync(
            repo,
            python,
            $$"""
import json
import sqlite3
import sys

conn = sqlite3.connect(r"{{dbPath}}", isolation_level=None)
conn.row_factory = sqlite3.Row
out = {}
for row in conn.execute(
        "SELECT region_id,text_json,current_revision_id,region_locked,translation_locked,"
        " inpaint_locked,sfx_policy FROM regions ORDER BY region_id"):
    rid = row["region_id"]
    for key in ("text_json", "current_revision_id", "region_locked", "translation_locked",
                "inpaint_locked", "sfx_policy"):
        value = row[key]
        out["regions." + rid + "." + key] = "<null>" if value is None else str(value)

out["regions.row_count"] = str(conn.execute("SELECT COUNT(*) FROM regions").fetchone()[0])
out["regions.manual_count"] = str(conn.execute(
    "SELECT COUNT(*) FROM regions WHERE sfx_policy='manual'").fetchone()[0])
out["region_revisions.row_count"] = str(
    conn.execute("SELECT COUNT(*) FROM region_revisions").fetchone()[0])

tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
candidate_table = ('step_result_candidates_v5' if 'step_result_candidates_v5' in tables
                   else 'step_result_candidates' if 'step_result_candidates' in tables else None)
out["region_candidates.table"] = candidate_table or "<absent>"
out["region_candidates.row_count"] = "0" if candidate_table is None else str(
    conn.execute("SELECT COUNT(*) FROM " + candidate_table).fetchone()[0])
if candidate_table is not None:
    for row in conn.execute(
            "SELECT candidate_id,status,base_revision_id,payload_json FROM " + candidate_table +
            " ORDER BY candidate_id"):
        cid = row["candidate_id"]
        for key in ("status", "base_revision_id", "payload_json"):
            value = row[key]
            out["region_candidates." + cid + "." + key] = "<null>" if value is None else str(value)

conn.close()
print("RESULT_JSON:" + json.dumps(out, ensure_ascii=False, sort_keys=True))
""",
            root);

        var snapshot = new Dictionary<string, string>(StringComparer.Ordinal);
        foreach (var property in element.EnumerateObject())
        {
            snapshot[property.Name] = property.Value.ToString();
        }

        Assert.NotEmpty(snapshot);
        Console.WriteLine($"FEA-07-RESIDUAL-3 protected snapshot '{label}': {snapshot.Count} columns");
        return snapshot;
    }

    public static async Task RunPythonAsync(string repo, string python, string script, string root)
    {
        var (exitCode, stdout, stderr) = await ExecuteAsync(repo, python, script, root);
        Assert.True(exitCode == 0, $"embedded Python failed ({exitCode}):{stderr}{stdout}");
    }

    private static async Task<JsonElement> RunPythonForJsonAsync(
        string repo, string python, string script, string root)
    {
        var (exitCode, stdout, stderr) = await ExecuteAsync(repo, python, script, root);
        Assert.True(exitCode == 0, $"embedded Python failed ({exitCode}):{stderr}{stdout}");
        var line = stdout
            .Split('\n')
            .Select(text => text.TrimEnd('\r'))
            .LastOrDefault(text => text.StartsWith(ResultMarker, StringComparison.Ordinal));
        Assert.True(line is not null, "embedded Python produced no result line; stdout:" + stdout);
        using var document = JsonDocument.Parse(line![ResultMarker.Length..]);
        return document.RootElement.Clone();
    }

    private static async Task<(int ExitCode, string Stdout, string Stderr)> ExecuteAsync(
        string repo, string python, string script, string root)
    {
        Assert.True(File.Exists(python), $"python interpreter not found: {python}");
        var startInfo = new ProcessStartInfo(python)
        {
            WorkingDirectory = repo,
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            StandardOutputEncoding = new System.Text.UTF8Encoding(encoderShouldEmitUTF8Identifier: false),
            StandardErrorEncoding = new System.Text.UTF8Encoding(encoderShouldEmitUTF8Identifier: false),
        };
        startInfo.ArgumentList.Add("-X");
        startInfo.ArgumentList.Add("utf8");
        startInfo.ArgumentList.Add("-c");
        startInfo.ArgumentList.Add(script);
        startInfo.ArgumentList.Add(root);
        using var process = Process.Start(startInfo)
            ?? throw new InvalidOperationException($"failed to start {python}");
        var stdout = process.StandardOutput.ReadToEndAsync();
        var stderr = process.StandardError.ReadToEndAsync();
        await process.WaitForExitAsync();
        return (process.ExitCode, await stdout, await stderr);
    }

    /// <summary>真实 <c>library.db</c>：production migrations + 三锁/manual/两版 revision/一条陈旧 candidate。</summary>
    public static string SeedScript() => """
import json
import sqlite3
import sys
from pathlib import Path

repo = Path(r"__REPO__")
root = Path(sys.argv[1])
sys.path[:0] = [str(repo), str(repo / "src")]

from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.schema import default_migrations

NOW = "2026-01-01T00:00:00+00:00"
db = root / "library.db"
conn = sqlite3.connect(db, isolation_level=None)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys = ON")
MigrationRunner(conn, default_migrations()).apply_pending()

conn.execute(
    "INSERT INTO books (book_id,title,created_at,updated_at) VALUES ('b-crash','AC3 真库',?,?)",
    (NOW, NOW))
conn.execute(
    "INSERT INTO chapters (chapter_id,book_id,title,sort_order,created_at,updated_at)"
    " VALUES ('c-crash','b-crash','第 1 章',1,?,?)", (NOW, NOW))
conn.execute(
    "INSERT INTO pages (page_id,chapter_id,sort_order,created_at,updated_at)"
    " VALUES ('p-crash-1','c-crash',1,?,?)", (NOW, NOW))
conn.execute(
    "INSERT INTO regions (region_id,page_id,region_type,reading_order,geometry_json,text_json,"
    " style_json,sfx_policy,region_locked,translation_locked,inpaint_locked,current_revision_id,"
    " created_at,updated_at)"
    " VALUES ('r-crash-1','p-crash-1','speech',1,?,?,?,'manual',1,1,0,NULL,?,?)",
    ('{"bbox":[1,2,10,20]}', '{"text":["暂停期保护"],"v":2}', '{}', NOW, NOW))
conn.execute(
    "INSERT INTO region_revisions (region_revision_id,region_id,revision_no,snapshot_json,origin,"
    " review_state,is_pinned,created_at)"
    " VALUES ('rr-crash-1','r-crash-1',1,?, 'machine','unreviewed',0,?)",
    ('{"text":["旧"],"v":1}', NOW))
conn.execute(
    "INSERT INTO region_revisions (region_revision_id,region_id,revision_no,snapshot_json,origin,"
    " review_state,is_pinned,created_at)"
    " VALUES ('rr-crash-2','r-crash-1',2,?, 'user','confirmed',1,?)",
    ('{"text":["暂停期保护"],"v":2}', NOW))
conn.execute("UPDATE regions SET current_revision_id='rr-crash-2' WHERE region_id='r-crash-1'")

conn.commit()
conn.close()
print("RESULT_JSON:" + json.dumps({"status": "ok", "db": str(db)}, ensure_ascii=False))
""".Replace("__REPO__", ResolveRepositoryRoot(), StringComparison.Ordinal);

    public static IReadOnlyList<string> Diff(
        IReadOnlyDictionary<string, string> before,
        IReadOnlyDictionary<string, string> after)
    {
        var differences = new List<string>();
        foreach (var (key, value) in before.OrderBy(pair => pair.Key, StringComparer.Ordinal))
        {
            if (!after.TryGetValue(key, out var current))
            {
                differences.Add($"{key}: removed ({value})");
            }
            else if (!string.Equals(value, current, StringComparison.Ordinal))
            {
                differences.Add($"{key}: {value} -> {current}");
            }
        }

        foreach (var key in after.Keys.Except(before.Keys, StringComparer.Ordinal)
                     .OrderBy(text => text, StringComparer.Ordinal))
        {
            differences.Add($"{key}: added ({after[key]})");
        }

        return differences;
    }
}
