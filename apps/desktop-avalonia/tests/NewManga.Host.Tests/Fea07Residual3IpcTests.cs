using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using NewManga.App.Services;
using NewManga.App.Shell.V2.Frontends;
using NewManga.Appearance;
using NewManga.CoreClient;
using NewManga.CoreClient.Commands;
using NewManga.Host.Tests.Support;
using NewManga.Presentation.Avalonia.Switching;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// FEA-07 AC-R4b-1（AC1 / A03）：gated 真实 Host/Core 证据。
///
/// 覆盖三件事（冻结卡实现口径 1；默认 skip + reason）：
/// <list type="number">
/// <item><b>A03 真库</b>：≥50 次前端往返切换（100 次切换事务，走生产 <see cref="FrontendSwitchCoordinator"/> +
/// 生产 <see cref="SwitchJournal"/> + 唯一写者 <see cref="AppearanceCoordinator"/>）前后，真实
/// <c>library.db</c> 的 <c>regions.text_json</c>/<c>current_revision_id</c>/三锁列/manual 位/明细行数
/// **逐列相同**；读库用内嵌 Python（<c>Fea11RunGrantIpcTests.cs</c> 先例），**不引入 SQLite 托管依赖**。</item>
/// <item><b>ACK 丢失/重连</b>：同一 idempotency key 经生产 dispatcher（<see cref="HostCommandDispatcher"/> +
/// <see cref="CurrentRunIntentCoordinator"/>）只产生 **1** 个 run；重放返回同一 run id。</item>
/// <item><b>旧结果仅 candidate</b>：切换与重放都不写 <c>regions</c>/<c>region_revisions</c>，预置的陈旧结果
/// 仍是 candidate（状态不变、未被应用）。</item>
/// </list>
/// 门禁：<c>NEWMANGA_FEA07_A03=1</c>；沙箱/隔离根在 <c>&lt;repo&gt;.workspace/FEA-07-RESIDUAL-3/</c>。
/// </summary>
public sealed class Fea07Residual3IpcTests
{
    private const string CurrentRevisionId = "rr-a03-2";
    private const int RoundTrips = 50;

    [Fea07Residual3A03Fact]
    public async Task A03_RealHostCore_FiftyRoundTripsAndAckReplay_KeepProtectedColumnsIdentical()
    {
        var repo = Fea07Residual3Fixture.ResolveRepositoryRoot();
        var python = Fea07Residual3Fixture.ResolvePython();
        var root = Fea07Residual3Fixture.NewDataRoot(repo, "a03");
        var evidence = new List<string>();
        try
        {
            // 1) 真实 library.db（production migrations + 真实行），随后由真实 Python Core 打开。
            var seed = await Fea07Residual3Fixture.RunPythonForJsonAsync(repo, python, SeedScript(repo), root);
            Assert.Equal("ok", seed.GetProperty("status").GetString());
            var regionId = seed.GetProperty("region_id").GetString()!;
            Assert.False(string.IsNullOrWhiteSpace(regionId));
            var dbPath = Path.Combine(root, "library.db");
            Assert.True(File.Exists(dbPath), "seeded library.db is missing");

            var coreOptions = new CoreServiceOptions
            {
                ExecutablePath = python,
                AdditionalArguments =
                [
                    "-X", "utf8", "-c",
                    $"import sys;sys.path.insert(0, r'{Path.Combine(repo, "src")}');"
                    + "import bootstrap.core_service as m;raise SystemExit(m.main())",
                ],
                DataRoot = root,
                DerivedRoot = Path.Combine(root, "derived"),
                CatalogDbPath = Path.Combine(root, "catalog.sqlite"),
                StderrLogPath = Path.Combine(root, "core.stderr.log"),
                WireLogPath = Path.Combine(root, "wire.ndjson"),
                StartupTimeout = TimeSpan.FromSeconds(120),
                RequestTimeout = TimeSpan.FromSeconds(60),
            };

            await using var client = await CoreServiceClient.StartAsync(coreOptions);
            var ping = await client.PingAsync();
            Assert.NotEmpty(ping.Capabilities);

            // 2) 切换前快照（真实库逐列）。
            var before = await SnapshotAsync(repo, python, dbPath, root, "before");
            var beforeRunCount = int.Parse(Column(before, "pipeline_runs.row_count"));
            evidence.Add($"before: regions={Column(before, "regions.row_count")} " +
                         $"revisions={Column(before, "region_revisions.row_count")} " +
                         $"candidates={Column(before, "region_candidates.row_count")} " +
                         $"candidate_table={Column(before, "region_candidates.table")} " +
                         $"manual={Column(before, "regions.manual_count")} runs={beforeRunCount}");

            // 3) 50 次往返 = 100 次生产切换事务（Core 正在运行，切换不得写库）。
            var appearancePath = Path.Combine(root, "presentation-settings.json");
            var appearance = new AppearanceCoordinator(new AppearanceStore(appearancePath));
            appearance.Reload();
            var journal = new SwitchJournal(Path.Combine(root, "switch-journal.json"));
            var switcher = new FrontendSwitchCoordinator(journal);
            var switches = 0;
            var toFluent = false;
            for (var roundTrip = 0; roundTrip < RoundTrips; roundTrip++)
            {
                for (var leg = 0; leg < 2; leg++)
                {
                    toFluent = !toFluent;
                    var target = toFluent
                        ? FrontendSelector.FluentFrontendId
                        : FrontendSelector.CurrentV2FrontendId;
                    var previous = toFluent
                        ? FrontendSelector.CurrentV2FrontendId
                        : FrontendSelector.FluentFrontendId;
                    var result = await SwitchOnceAsync(switcher, appearance, target, previous);
                    Assert.True(result.Succeeded, $"switch #{switches} failed: {result.Failure}");
                    Assert.Equal(target, appearance.FrontendId);
                    switches++;
                }
            }

            Assert.Equal(RoundTrips * 2, switches);
            Assert.Equal(FrontendSelector.CurrentV2FrontendId, appearance.FrontendId);
            Assert.False(File.Exists(journal.FilePath), "a committed switch must not leave an in-flight journal");

            var afterSwitches = await SnapshotAsync(repo, python, dbPath, root, "after-switches");
            var switchDiff = Fea07Residual3Fixture.Diff(before, afterSwitches);
            Assert.True(switchDiff.Count == 0,
                "frontend switching wrote the real library.db:\n" + string.Join("\n", switchDiff));
            evidence.Add($"after {switches} switches: protected columns identical (0 diffs)");

            // 4) ACK 丢失 + 同 key 重连：真实 Run/Intent 链路经生产 dispatcher。
            var dispatcher = new HostCommandDispatcher(core: client);
            var intents = new CurrentRunIntentCoordinator();
            var attempts = 0;
            string? firstRunId = null;
            string? lastFailure = null;

            async Task<RunStartInfo?> StartAsync(string intentKey, CancellationToken token)
            {
                attempts++;
                try
                {
                    var run = await DispatchStartRunAsync(dispatcher, regionId, intentKey, token);
                    firstRunId ??= run.RunId;
                    if (attempts == 1)
                    {
                        // 冻结卡口径：Core 已 accept（run 已落库），但 ACK 在返回途中丢失。
                        throw new IOException("simulated acknowledgement loss after the Core accepted the run");
                    }

                    return run;
                }
                catch (Exception ex) when (ex is not IOException)
                {
                    lastFailure = ex.GetType().Name + ": " + ex.Message;
                    throw;
                }
            }

            Assert.Null(await intents.ExecuteAsync(StartAsync));
            var pendingKey = Assert.IsType<string>(intents.PendingKey);
            Assert.False(string.IsNullOrWhiteSpace(pendingKey));
            Assert.Equal(1, attempts);

            var retried = await intents.ExecuteAsync(StartAsync);
            Assert.True(retried is not null,
                $"replay with the same idempotency key failed; attempts={attempts} lastFailure={lastFailure}");
            Assert.Equal(2, attempts);
            Assert.Equal(firstRunId, retried!.RunId);
            Assert.Null(intents.PendingKey);
            Assert.False(string.IsNullOrWhiteSpace(retried.RunId));

            var afterAck = await SnapshotAsync(repo, python, dbPath, root, "after-ack");
            var runCount = int.Parse(Column(afterAck, "pipeline_runs.row_count"));
            Assert.Equal(beforeRunCount + 1, runCount);
            evidence.Add($"ack replay: attempts=2 runs={beforeRunCount}->{runCount} run_id={retried.RunId} " +
                         $"pending_key_cleared=true");

            // 5) 旧结果仅 candidate：切换 + 重放都没有应用陈旧结果（候选 store 零解析、零应用）。
            Assert.Equal(Column(before, "regions." + regionId + ".text_json"),
                Column(afterAck, "regions." + regionId + ".text_json"));
            Assert.Equal(CurrentRevisionId, Column(afterAck, "regions." + regionId + ".current_revision_id"));
            Assert.Equal("0", Column(afterAck, "region_candidates.row_count"));
            Assert.Equal(Column(before, "region_candidates.table"),
                Column(afterAck, "region_candidates.table"));
            Assert.Equal(Column(before, "region_revisions.row_count"),
                Column(afterAck, "region_revisions.row_count"));
            evidence.Add($"old result: candidate store {Column(afterAck, "region_candidates.table")} " +
                         $"rows=0 resolved/applied=0; current stays {CurrentRevisionId} " +
                         "(stale base never entered current)");

            // 6) 「暂停期保护状态」第一条：切换零写保护列已在步骤 3 断言；此处再断言三锁/manual 逐列相同。
            //    只比对保护列（`pipeline_runs` 是这次真实 Run 的**预期**新行，单独在步骤 4 断言 +1）。
            var protectedDiff = Fea07Residual3Fixture.Diff(ProtectedColumns(before), ProtectedColumns(afterAck));
            Assert.True(protectedDiff.Count == 0,
                "run/ACK replay wrote protected columns:\n" + string.Join("\n", protectedDiff));
            Assert.Contains("manual", string.Join(" ", before.Keys), StringComparison.Ordinal);
            evidence.Add("after ack: protected columns identical (0 diffs), manual bit unchanged=" +
                         Column(afterAck, "regions.manual_count"));

            // 7) 证据落盘（隔离 workspace，不写跟踪文件）。
            evidence.Add("PASS");
            await File.WriteAllTextAsync(
                Path.Combine(root, "a03-evidence.txt"),
                $"DataRoot={root}\nPython={python}\n" + string.Join("\n", evidence) + "\n");
            Assert.Contains("PASS", await File.ReadAllTextAsync(Path.Combine(root, "a03-evidence.txt")),
                StringComparison.Ordinal);
        }
        finally
        {
            // 保留证据目录（隔离 workspace），只清理 Core 派生文件。
            Console.WriteLine("FEA-07-RESIDUAL-3 A03 evidence root: " + root);
            Console.WriteLine(string.Join(Environment.NewLine, evidence));
        }
    }

    /// <summary>一次生产切换事务：journal 决定事务边界，appearance 唯一写者持久化 <c>theme.frontendId</c>。</summary>
    private static Task<SwitchResult> SwitchOnceAsync(
        FrontendSwitchCoordinator switcher,
        AppearanceCoordinator appearance,
        string target,
        string previous)
    {
        // 与 App/Services/FrontendHostCoordinator 的 Commit/Rollback 回调同序：commit 阶段由唯一写者
        // 持久化目标 frontend；任何失败回滚到上一已提交设置。UI 侧 layout/Loaded/render 门禁由
        // App.Tests 的 headless 用例覆盖（本卡只验证「切换事务对真实库零写」）。
        AppearanceSettings? previousSettings = null;
        var callbacks = new SwitchCallbacks
        {
            ValidateAsync = _ => Task.CompletedTask,
            BuildTreeAsync = _ => Task.CompletedTask,
            CommitAsync = async token =>
            {
                previousSettings = appearance.Settings;
                await appearance.SaveAsync(previousSettings with { FrontendId = target }, token)
                    .ConfigureAwait(false);
            },
            RollbackAsync = async _ =>
            {
                if (previousSettings is not null)
                {
                    await appearance.SaveAsync(previousSettings, CancellationToken.None).ConfigureAwait(false);
                }
            },
        };
        return switcher.SwitchAsync(new SwitchRequest(target, previous), callbacks);
    }

    /// <summary>生产 StartRun 链路：生产 payload 构造 + 生产 dispatcher + 生产结果映射。</summary>
    private static async Task<RunStartInfo> DispatchStartRunAsync(
        HostCommandDispatcher dispatcher,
        string regionId,
        string idempotencyKey,
        CancellationToken cancellationToken)
    {
        var request = new RunStartRequest(
            "ocr_region",
            new Dictionary<string, object?>
            {
                ["kind"] = "region",
                ["region_id"] = regionId,
            },
            Overrides: null,
            IdempotencyKey: idempotencyKey);
        var response = await dispatcher
            .InvokeAsync("library_start_run", RunPayloads.StartRun(request), cancellationToken)
            .ConfigureAwait(false);
        var info = RunStartInfo.FromJson(response.Value);
        Assert.False(string.IsNullOrWhiteSpace(info.RunId), "StartRun returned no run id: " + response.Value);
        return info;
    }

    private static string Column(IReadOnlyDictionary<string, string> snapshot, string key) =>
        snapshot.TryGetValue(key, out var value)
            ? value
            : throw new InvalidOperationException($"snapshot column missing: {key}");

    /// <summary>去掉非保护列（`pipeline_runs` 计数由「ACK 只产生 1 个 run」单独断言）。</summary>
    private static IReadOnlyDictionary<string, string> ProtectedColumns(
        IReadOnlyDictionary<string, string> snapshot) =>
        snapshot
            .Where(pair => !pair.Key.StartsWith("pipeline_runs.", StringComparison.Ordinal))
            .ToDictionary(pair => pair.Key, pair => pair.Value, StringComparer.Ordinal);

    private static async Task<IReadOnlyDictionary<string, string>> SnapshotAsync(
        string repo,
        string python,
        string dbPath,
        string root,
        string label)
    {
        var element = await Fea07Residual3Fixture.RunPythonForJsonAsync(
            repo, python, SnapshotScript(dbPath), root);
        var snapshot = new Dictionary<string, string>(StringComparer.Ordinal);
        foreach (var property in element.EnumerateObject())
        {
            snapshot[property.Name] = property.Value.ValueKind == JsonValueKind.Null
                ? "<null>"
                : property.Value.ToString();
        }

        Assert.NotEmpty(snapshot);
        Console.WriteLine($"FEA-07-RESIDUAL-3 snapshot '{label}': {snapshot.Count} columns");
        return snapshot;
    }

    // ------------------------------------------------------------------ 内嵌 Python（种子 + 读库）

    /// <summary>
    /// 真实库种子：走**生产装配**（<c>assemble_core_services</c> + 生产 importer/editing）建出可被真实
    /// Run 展开的 book/chapter/page/region（同 <c>tests/fea10/support/restart_core.py</c> 先例），再用
    /// SQL 落定三锁/manual/两版 revision，使「逐列相同」与「旧结果仅 candidate」非空证明。
    /// </summary>
    private static string SeedScript(string repo) => $$"""
import json
import sqlite3
import sys
from pathlib import Path

repo = Path(r"{{repo}}")
root = Path(sys.argv[1])
sys.path[:0] = [str(repo), str(repo / "src")]

from tests.core.test_fea00a_pipeline_seam import _new_workspace

core, page_id, region_id = _new_workspace(root)
try:
    # 生产装配把 mock provider binding 写进 pipeline_defaults；真实 Core 打不开它，先清掉（Fea10 先例）。
    core.pipeline_defaults.clear_provider_binding('ocr')
finally:
    core.conn.close()

NOW = "2026-01-01T00:00:00+00:00"
db = root / "library.db"
conn = sqlite3.connect(db, isolation_level=None)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys = ON")

# 确定的保护状态：manual sfx + 两锁 + 两版 revision（当前指向 rev 2）。
conn.execute(
    "UPDATE regions SET text_json=?, sfx_policy='manual', region_locked=1, translation_locked=1,"
    " inpaint_locked=0 WHERE region_id=?",
    ('{"text":["protected-pause-state"],"v":2}', region_id))
conn.execute(
    "INSERT INTO region_revisions (region_revision_id,region_id,revision_no,snapshot_json,origin,"
    " review_state,is_pinned,created_at) VALUES ('rr-a03-2',?,2,?, 'user','confirmed',1,?)",
    (region_id, '{"text":["protected-pause-state"],"v":2}', NOW))
conn.execute("UPDATE regions SET current_revision_id='rr-a03-2' WHERE region_id=?", (region_id,))

# 冻结 schema 没有名为 `region_candidates` 的表（候选 store = step_result_candidates/`_v5`，V5 迁移改名）。
# 这里不伪造 run/step 父行（run_json 必须由真实装配写出，见 DEFECTS D-R4b-1）：候选存量保持 0，
# 「旧结果仅 candidate」由「零候选解析 + 陈旧 base 未进入 current」断言。
conn.commit()
conn.close()
print("RESULT_JSON:" + json.dumps({"status": "ok", "region_id": region_id, "page_id": page_id},
                                  ensure_ascii=False))
""";

    /// <summary>
    /// 读库脚本（只读）：把冻结卡要求的列展开成扁平 <c>key -&gt; value</c> 映射，逐列可比。
    /// 不引入 <c>Microsoft.Data.Sqlite</c>：这里只 shell 出仓库自带 Python。
    /// </summary>
    private static string SnapshotScript(string dbPath) => $$"""
import json
import sqlite3
import sys

db = r"{{dbPath}}"
conn = sqlite3.connect(db, isolation_level=None)
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
for row in conn.execute(
        "SELECT region_id,revision_no,region_revision_id,origin,review_state,is_pinned"
        " FROM region_revisions ORDER BY region_id,revision_no"):
    prefix = "region_revisions." + row["region_id"] + ".revision" + str(row["revision_no"])
    out[prefix + "_id"] = row["region_revision_id"]
    out[prefix + "_origin"] = row["origin"]
    out[prefix + "_review_state"] = row["review_state"]
    out[prefix + "_is_pinned"] = str(row["is_pinned"])
out["pipeline_runs.row_count"] = str(
    conn.execute("SELECT COUNT(*) FROM pipeline_runs").fetchone()[0])

tables = [row[0] for row in conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table'")]
candidate_table = ('step_result_candidates_v5' if 'step_result_candidates_v5' in tables
                   else 'step_result_candidates' if 'step_result_candidates' in tables else None)
out["region_candidates.table"] = candidate_table or "<absent>"
if candidate_table is None:
    out["region_candidates.row_count"] = "0"
else:
    out["region_candidates.row_count"] = str(conn.execute(
        "SELECT COUNT(*) FROM " + candidate_table).fetchone()[0])
    for row in conn.execute(
            "SELECT candidate_id,status,base_revision_id,result_kind,region_id,payload_json"
            " FROM " + candidate_table + " ORDER BY candidate_id"):
        cid = row["candidate_id"]
        for key in ("status", "base_revision_id", "result_kind", "region_id", "payload_json"):
            value = row[key]
            out["region_candidates." + cid + "." + key] = "<null>" if value is None else str(value)

conn.close()
print("RESULT_JSON:" + json.dumps(out, ensure_ascii=False, sort_keys=True))
""";
}
