---
task_id: FEA-10
reviewer: Codex（全新上下文，主审 /root；第 4 轮最终独立实现 Review）
reviewer_kind: agent
author: Codex / ZCode / DSH（实现及历轮返修）
base_commit: 5be507e2787dff54fd020ae83671f87e39f56597
reviewed_head: e23b01a919b4bc52a7e619ed1892bf2a5c3b50db
decision: changes_requested
---

# FEA-10 最终独立实现 Review r2（第 4 轮）

结论：**changes_requested，P0=0、P1=2、P2=2；当前 head 不可 closeout。** FR-01 的普通嵌套样例已拦截，但伪造或再次嵌套 `glossary` 可重新获得词条名豁免，认证哨兵仍能进入 PreparedRun 和持久化 Run；FR-02 的 Canonical Evidence 行仍绑定旧 commit。FR-03、FR-04…FR-07 的指定行为通过本轮独立验证。

## 身份、范围与依据

- 主审为本次用户指定的 Codex 全新上下文 `/root`，未参与该 Task 的实现、返修或原有证据生成。没有可核实的主会话 UUID，不虚构该值。
- 两个只读辅助审查上下文：`/root/standards_review`（Standards/证据与范围）、`/root/spec_review`（Spec/安全及 fallback）；均未参与实现或返修，未写文件、未运行测试。最终 findings 由主审取舍，并由主审复现两个 P1。
- 审查工作树：`G:/CODEX/New Manga`，`main`；开始时 HEAD 精确等于 reviewed_head，`git status --short` 为空；Git common directory 为 `.git`。结束前再次核对 HEAD 及写集。
- 主增量：`git diff 5be507e2787dff54fd020ae83671f87e39f56597 e23b01a9`；提交为 `2b0cbfb1e21abf5f194f4b3d314f8cbc02cc9339` 与 `e23b01a919b4bc52a7e619ed1892bf2a5c3b50db`。必要调用链及既有 AC 对照回看 `a9293458` 以来变更；冻结边界使用实际实现基线 `aa7bcd6161be5df07e2b8bf546600fec04af038f`。
- 已读 Task AC1–AC10、三份历史实现 Review、rework r3 记录、AC-MATRIX、`ADJ-2026-11-04-FEA-10-R2.md`、AD-002 当前架构及 AD-003 覆盖说明、当前 STATUS/DAG/被指向 checkpoint、协作协议 §4/§5、Review 模板。
- 冻结 C-08/C-13/C-05/C-04b 的实际承载文件为 `doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md`、`FEA-C13_DRAFT_PROTECTION_DRAFT.md`、`FEA-C05_PAGE_VISIBILITY_DRAFT.md`、`FEA-C04b_DELETE_PROTOCOL_DRAFT.md`；wire 对照 `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` rev 2.12。没有因用户简称而假定它们都位于 contracts 目录。
- 仓库唯一写入为本报告；测试仅生成隔离合成 fixture，没有改生产代码、测试、冻结契约或既有证据，没有 commit/push/清理/恢复操作。

## Architecture 与 Findings

**Architecture：不通过。** 两阶段接受、既有 SQLite 单写者、candidate-only seam、冻结请求和 durable receipt 的总体边界保持；但认证材料仍能穿过快照安全边界。没有发现新增依赖、Schema、未冻结 wire 或产品范围扩张。

### Standards（executed）

1. **F2-02 / P1**：Task Canonical Evidence commit 与被 pin 的证据版本不匹配，违反协作协议 §4.1。
2. **F2-03 / P2**：r3 日志缺 EXIT/完整命令及环境头，未达到协作协议 §4.2 和 Review 模板的证据纪律。
3. **F2-04 / P2**：FR-08 只追加了纠正说明，旧证据导航仍指向不存在的测试名/路径。

没有需另列的 Fowler smell；不把工具已检查的格式问题升级为实现 finding。

### Spec（executed）

1. **F2-01 / P1**：AC2 与 ADJ §2.2 要求“敏感认证材料……不入快照”；当前 `glossary` 豁免不受合法路径约束，词条值内可重新申请豁免，故仍未达成。未发现本轮新增范围扩张。

### Findings 明细

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 修复要求 | 状态 |
|---|---|---|---|---|---|---|
| F2-01（FR-01 未闭合） | P1 | `src/application/tasks/store.py:253`；`src/infrastructure/sqlite/pipeline.py:1517` | 两处递归只按键名 `glossary` 授予词条名豁免。`typeset.font_family.glossary.authorization` 和 `translate.glossary.outer.glossary.authorization` 都把认证键视作词条名；override 与 defaults 两条路径均可进入 prepared 和持久化 `settings_snapshot_json`/`run_json`。冻结最终快照虽重新扫描，仍使用同一个有漏洞的扫描器。 | 主审 10 场景探针：两个绕过形状 × override/defaults，共 4 次 ACCEPTED；每次 `prepared_contains_sentinel=true`、`db_contains_sentinel=true`。普通 headers 形状拒绝。见下文复现。 | 词条名豁免必须绑定真实的 `translate.glossary` 词条层，且只授予一次；扫描词条值时不得因再次出现 `glossary` 恢复豁免。同步约束 `_redact` 的路径，按需要严格校验 font_family/glossary 的业务值类型。补 override/defaults/最终接受快照回归，保留合法 token 词条。 | open |
| F2-02（FR-02 未闭合） | P1 | `doc/tasks/FEA-10.md:212`；`doc/reviews/FEA-10-rework-r1.md:46` | Canonical Evidence 行仍为 `a92934585088fe75ce8ec53452a67c0a72496d31` + 新 sha `2d264224…`；a929 包含的是旧 AC-MATRIX。r3 记录称已修复、e23 commit message 称已回填，实际 e23 只改 DELIVERY-MANIFEST。机械 check PASS 不能证明 commit 绑定正确。 | 主审直接读取三份 Git blob 并独立算 hash，见下表。即使用本仓库当前 CRLF 工作树 basis，a929 也是 `7428c009…`，不是 `2d264224…`。 | DSH 把 EV 行绑定到确实含相应证据版本的提交（当前对应 `2b0cbfb1…`）；后续证据再变须更新相应 commit/sha。保留并说明工作树/CRLF hash basis，不为此改写冻结历史或全局检查语义。固定新 head 后再独立审查。 | open |
| F2-03 | P2 | `verification/FEA-10/logs/dsh-rework3-pytest.log:1`；`dsh-rework3-providers.log:1`；`dsh-rework3-dotnet.log:1` | 两份 Python 日志只有 COMMAND 和测试输出，没有 EXIT；dotnet 首行仅 `COMMAND=dotnet build + test + ipc`，缺完整参数、shell/环境与实际 TEMP/TMP/IPC 门径头。测试输出存在，但无法按日志独立复现整个调用。 | pytest 1055、providers 559/4 的输出可见；dotnet 有 build/test/ipc 三个 EXIT=0。不得将 Python 缺失的 EXIT 补写成事后“已证实”。 | 后续验证逐次保存完整调用、shell、隔离环境、实际 EXIT 与 skip 原因；保留现有不完整日志，新增可追溯运行记录。 | open，非阻断债务 |
| F2-04（FR-08 部分完成） | P2 | `doc/reviews/FEA-10-rework-r1.md:14`、`:33`；`verification/FEA-10/AC-MATRIX.md:65` | 旧表仍引用不存在的 `RunControllerTests.PreparedRunPayload_CarriesTheSameHostDefaultBindingsAsStartRun`；旧日志导航仍使用 `logs/dsh/…`。r3 追加段给出正确名称/路径，但没有明确标旧导航为 superseded。 | 实际 C# 用例为 `RunControllerNullFakeTests.PreparedRunPayload_CarriesTheHostDefaultBindings`，位于 `apps/desktop-avalonia/tests/NewManga.App.Tests/RunControllerTests.cs`；本轮入库日志为 `verification/FEA-10/logs/dsh-rework3-*.log`。 | 不改冻结历史报告原字节；在当前活动导航明确给出实际用例与真实路径，标注旧导航失效/被替代，不再声称全部校正。 | open，非阻断文档项 |

### FR-01 探针：可复现输入与实际输出

运行方式：PowerShell here-string 经 stdin 传给 `C:/Python314/python.exe -`，不保存探针脚本、不修改源码。`PYTHONDONTWRITEBYTECODE=1`；TEMP/TMP 均为：

`G:/CODEX/New Manga.workspace/FEA-10/fixtures/final2-review-cfa5470633ba432da23338b7916c90da/`

使用生产 SQLite assembly 的 `_new_workspace`，每例独立子目录；哨兵为合成字符串 `SYNTHETIC-FINAL2-AUTH`，不是真实认证材料。核心调用如下（分别执行 override 和 defaults 模式）：

```python
from tests.core.test_fea00a_pipeline_seam import _new_workspace
from domain.tasks.models import PipelineScope, ScopeType

# case_root 为上述隔离根下新建的逐例目录
core, _, region = _new_workspace(case_root)
scope = PipelineScope(ScopeType.REGION, selected_ids=(region,))
settings = {
    "typeset": {"font_family": {"glossary": {
        "authorization": "SYNTHETIC-FINAL2-AUTH"
    }}}
}
# override 模式：
prepared = core.pipeline.prepare_run("ocr_region", scope,
                                    overrides={"settings": settings})
# defaults 模式在另一独立库先 save_settings_section，再无 overrides Prepare。
run, created = core.pipeline.accept_prepared_run(
    prepared, scope, idempotency_key="probe")
row = core.conn.execute(
    "SELECT settings_snapshot_json, run_json FROM pipeline_runs WHERE run_id=?",
    (run.run_id,)).fetchone()
assert "SYNTHETIC-FINAL2-AUTH" in str(prepared)
assert all("SYNTHETIC-FINAL2-AUTH" in value for value in row)
core.conn.close()
```

| settings 输入形状 | override | defaults | 持久化结果 |
|---|---|---|---|
| `translate.glossary.nested.headers.authorization` | RUN_SNAPSHOT_INCOMPLETE | RUN_SNAPSHOT_INCOMPLETE | 拒绝后 Run=0、DB changes=0 |
| `typeset.font_family.headers.authorization` | RUN_SNAPSHOT_INCOMPLETE | RUN_SNAPSHOT_INCOMPLETE | 拒绝后 Run=0、DB changes=0 |
| `typeset.font_family.glossary.authorization` | **ACCEPTED** | **ACCEPTED** | **prepared 与 DB 均含哨兵** |
| `translate.glossary.outer.glossary.authorization` | **ACCEPTED** | **ACCEPTED** | **prepared 与 DB 均含哨兵** |
| 合法 `translate.glossary={token: word-value, headers: another-word}` | ACCEPTED | ACCEPTED | 两个词条均保留；嵌套赋值抛 TypeError，快照不可变 |

此探针 EXIT=0 表示探针完成，并不表示产品安全断言通过。安全结论为 FAIL。

### FR-02 / manifest 独立字节核对

`git show <commit>:verification/FEA-10/AC-MATRIX.md` 以二进制读取，分别计算 blob SHA 与 LF→CRLF 后 SHA，避免把换行差异误认作证据损坏：

| 来源 | 原始 bytes | 原始 SHA-256 | CRLF 工作树 basis SHA-256 |
|---|---:|---|---|
| a9293458 | 8263 | `f7899617f714ed34586e71f20fcbad71e175a40b0a771225fccd129e185a648a` | `7428c009b94e58ce08a3938e93baf6511fba42f1502591253c753e230ffb41f7` |
| 2b0cbfb1 / e23b01a9 | 13416 | `405acfba6ca7acc929e58720c931d795b0da58aa0d23f7fa3363c003226e6075` | `2d26422419239b59fab092239416494bbe1f5e38e588247e7560cb728dbe91d7` |
| 当前工作树 | 13510 | `2d26422419239b59fab092239416494bbe1f5e38e588247e7560cb728dbe91d7` | 同左 |

DELIVERY-MANIFEST 的 **10/10 项 bytes/SHA 全匹配工作树**；`head` 与 `generated_after_head` 都是 `2b0cbfb1…`，`excluded_docs` 明列 Task/Handoff/两份 Review；`uncommitted=true` 描述生成时点，不是当前工作树状态。该清单是增量交付清单，不是全部历史交付文件全集。它本身自洽，不能替代或修复 Task 的错误 EV commit。

## 逐项 AC 独立判断

下列 MET 限于所列机制与冻结口径，不等同于批准整个 Task。

| AC | 独立状态 | 依据与限制 |
|---|---|---|
| AC1 | MET | 复跑四元组独立 hash、Prepare 零写/零执行、digest/配置/Lock/Revision/过期/缺失拒绝测试；Accept 复用 store.accept 的事务校验后写 Run/receipt。安全输入边界另由 AC2 判失败。 |
| AC2 | **NOT MET** | 普通嵌套认证及 unsupported binding 拒绝成立；typed execution/digest 和 fallback 检查成立；但 F2-01 已证明认证哨兵可入 prepared/DB。不能接受卡中整体 MET。 |
| AC3 | MET（按 ADJ §2.1） | `test_preview_and_real_transport_body_use_same_builder_and_pinned_config` 的 preview/实际 endpoint-model-body/发送 provenance 同摘要并成功 commit；邻页 stale 与 accept 后 pin、defaults/provider 漂移隔离均复跑通过。未来 OCR 输出仅标 requires_upstream_output，不声称能提前预览未来正文。FR-05 的 accepted settings 递归不可变已另测。 |
| AC4 | MET（有覆盖边界） | retry 同键重放/异键失败子集/source_run_id/新上下文与新 provider 快照/旧 Run 不改、凭据阻塞与恢复、版本阻塞与恢复均复跑。版本专项仍以 mock-local 证明，本地 typed 正向冻结/resolve 由本轮补充探针验证；真实模型变更未测。显式 retry 是现有新配置确认边界，没有独立差异披露 UI 的验收证据。 |
| AC5 | MET（seam 层） | 17 项故障/原子提交测试复跑通过；三处 live/revision/行数及成功计数守卫成立；C-13 多 Region 与 pipeline step 分用既有 candidate/事务。crash_restart 是恢复放弃断言；source lease 与 binding 是注入 seam，不能写成系统级验收（R-013/R-015 保留）。 |
| AC6 | MET（Python/DB 与 C# 结构层） | 四项控制/终态/重开库测试通过；请求 pending 不冒充 paused/cancelled，scheduler 边界后才投影状态。读取 RunMonitor/RunStateStore，成功 Core 查询才发布快照，无控制请求推导状态的第二真值。`is_terminal` 未被生产消费、原生 UI 点击及专项 C# 行为验证不足，仍按 R-007 披露，不能宣称 UI E2E 已验收。 |
| AC7 | MET | 丢 ACK 后同键找回、过期与配置读取前 receipt 优先、异 fingerprint 拒绝、同 request_id 异 key 独立操作、stop/start 两进程及 ControlRun restart 重开 DB receipt 均由本轮 52 项覆盖。真实 stdio Core 重启链路本轮仅核对既有日志/测试代码。 |
| AC8 | MET（已覆盖生产链路与日志核对） | 本轮 Python 生产 assembly Prepare→Accept→transport→commit 通过；r3 .NET 日志汇总1345/0/75、build0/0、真实IPC1通过，与已入库测试代码相符。相比 r2 主套件1052→1055（+3），.NET初始基线1344→1345（+1），未见减少。本轮未重跑 .NET/真实 IPC/全量 core/pipeline/providers；F2-03 限制其复现性，未将日志核对冒充本轮执行。 |
| AC9 | **PARTIAL** | 冻结17/17、契约/FEA-08/09/组合根零diff、写域检查成立，manifest自洽；F2-02 的 EV commit 仍错，本 Review 未 approved，DSH 最终集成与资源 closeout 未完成。不可关闭。 |
| AC10 | MET | 本轮5个生产文件+1测试文件均在卡写域，其他为允许的证据/文档；无新增依赖/Schema/未冻结wire，无提前实现FEA-11/12/13/14。source保护消费既有seam，未改共享组合根。 |

## Verification：实际执行、日志核对与 NOT_RUN

**Verification：部分通过，不能授予批准。** 本轮实际复跑均在固定 reviewed_head；fixture 为合成库。最初和报告写入前工作树均干净；本报告是唯一仓库新增文件。

| 场景 | 实际命令/步骤 | 结果 |
|---|---|---|
| 治理 | `pwsh -NoProfile -File tools/governance/check.ps1` | PASS，4 warnings；仅机械检查，不证明 F2-02 的 commit 正确 |
| 冻结 pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | EXIT=0；17/17 PASS |
| FEA-10 | `C:/Python314/python.exe -m pytest tests/fea10 -q -p no:cacheprovider`；TEMP/TMP=上述 final2-review 根；PYTHONDONTWRITEBYTECODE=1 | **52 passed，0 skipped，4.35s，EXIT=0** |
| 认证/词条/不可变探针 | stdin Python，10场景，输入/输出见上 | 完成EXIT=0；四次走私成功为安全FAIL；合法词条与不可变PASS |
| fallback 探针 | mock/local/remote primary × missing/untyped/typed-local/typed-mock/typed-remote；生产registry，local为有type/model的合成OCR适配器，remote为VisionOcrProvider+禁止send的transport | 15格中3格同provider不构成fallback，记N/A；其余12格均符合预期。6个missing/untyped组合全部RUN_SNAPSHOT_INCOMPLETE、DB changes=0、Run=0；6个合法typed组合全部有frozen_fallbacks、Accept成功、resolve_for_run模型等于冻结模型。EXIT=0，无网络 |
| Core null binding | `CoreServiceServer._dispatch_run_command('PrepareRun', ..., protocol_minor=12)`，`overrides.provider_bindings=null` | error.code=INVALID_REQUEST，category=validation，retryable=false |
| 非法执行段 | ocr/translate/typeset 分别传 `['invalid']` | 三者均RUN_SNAPSHOT_INCOMPLETE |
| 证据commit/hash/manifest | Python subprocess二进制读取git show、hashlib.sha256、逐项对比manifest | F2-02 FAIL；manifest10/10 PASS；换行basis见上 |
| 冻结/前置/组合根 | `git diff --name-only aa7bcd6161be5df07e2b8bf546600fec04af038f e23b01a9 -- doc/contracts <四份冻结plan契约> verification/FEA-08 verification/FEA-09 doc/tasks/FEA-08.md doc/tasks/FEA-09.md <App.axaml/App.axaml.cs/NewManga.App.csproj/NewManga.sln>` | 空；其他冻结pin由17/17与辅助审查交叉核对 |
| diff hygiene | `git diff --check 5be507e2 e23b01a9` | 3处new blank line at EOF（handoff、rework-r1、test_prepared_run）；仅格式观察，不升级finding |
| r3原始日志抽查 | 读 `dsh-rework3-pytest.log`、`providers.log`、`dotnet.log`，核对命令/EXIT/各程序集汇总 | pytest输出1055/1warning；providers559/4；build0/0；.NET1345/0/75；IPC1。Python缺EXIT，dotnet调用头不完整（F2-03） |
| .NET build/全量/真实IPC | **NOT_RUN（本轮）** | 用户允许核对既有日志；全量可能改写FEA-09 tracked证据，本轮不执行需要恢复字节的步骤。仅核对日志与代码，不能声称本轮独立跑过 |
| Python全量core/pipeline/providers | **NOT_RUN（本轮）** | 指定52项和定向探针已跑；1055与559/4为既有日志，不是本轮重跑。现有providers日志没有-rs逐skip原因，故不逐项臆测其4个skip |
| 原生UI点击、Windows系统级source lease、真实外网provider/模型质量 | **NOT_RUN** | 未访问真实用户数据、模型或网络；seam注入不替代这些验收 |

证据真实性判断：未发现“未跑冒充跑过”的确证。r3 pytest 有完整进度与1055汇总，providers有559/4汇总，dotnet逐程序集通过数可相加为1345、skipped75，另有单独IPC1及EXIT=0；原有失败历史仍保留。缺日志头/EXIT是可追溯性缺口，不能因此推断伪造，也不能反向宣称它们完整。r3 pytest末尾QML TypeError与Pillow deprecation原文仍在，未将其隐藏或改成失败测试。

## 既有债务的可接受边界

| 债务 | 本轮判断 |
|---|---|
| R-006 | 可作为P2保留：支持类型配置不完整的StartRun提前fail-closed会改变失败时点，未导致越权执行；必须继续披露兼容行为，不能称“所有StartRun行为不变”。 |
| R-007 | 可作为P2保留：Core持久status权威与C#仅发布成功查询的结构成立；`is_terminal`未有生产消费者/UI专项不足仍在，不能冒充UI端到端验收。 |
| R-011 | 可作为P2保留：Host候选/attempt缓存无界增长与清理代价仍需后续处理；不是本轮新引入的数据破坏或快照可变漏洞。 |
| R-013 | 可作为P2保留：crash_restart证明恢复放弃及零提前写，不证明重启后candidate可继续提交；保持seam/恢复边界的准确表述。 |
| R-015 | 可作为P2保留：source lease错误被归并db_failed损害诊断，但该故障路径的零live写守卫有测试；后续修taxonomy，不把它当真实Windows租约验收。 |
| R-016 | 可作为P2保留：preview异常统一unavailable削弱诊断；执行与接受仍有守卫，不单凭preview可用性批准请求。 |

这些债务不改变本轮两个P1的阻断性；其最终接受与跟踪仍由DSH裁决。本审查没有以新增UI、真实模型能力或其他Task范围要求扩大FEA-10。

补充治理事实：STATUS/Task描述当前in_review/rework r3，而REBASELINE_PLAN当前行仍保留in_progress/AC2/3/4/6续作中的旧措辞，rolling checkpoint也为更早恢复点。按用户只写报告限制在此留下差异，交DSH同步，不修改这些权威指针，不据其旧文字恢复实施。

## 新 head 修复、复审与 closeout 条件

1. 先修F2-01，至少补两个绕过形状×override/defaults，并验证prepared与两列持久化Run都无认证材料；合法glossary词条名保留，词条值不重新获得豁免。不得以再加几个键名黑名单替代路径/类型边界。
2. 修F2-02：EV commit须真实包含被pin的证据版本；manifest继续显式记录生成时head、增量范围和excluded_docs。若AC-MATRIX变化，重新计算对应sha与包含它的commit，不盲填旧值。
3. 按现有Task门禁复跑并保留完整命令/环境/EXIT/skip：pytest FEA-10+core+pipeline、providers、Release build/test、真实IPC、check、pins、冻结/FEA-08/09/组合根零diff。F2-03/F2-04按上述方式补齐当前导航与新运行记录，保留历史原字节。
4. 固定新head，派未参与返修的独立上下文Review；本报告不批准任何后续head。当前**不得closeout/done**，不得用本轮52 passed替代两个P1的修复。
5. 新head获approved后，仍须DSH记录集成验证、integration_commit、完整canonical evidence、资源disposition及`canonical_evidence_status/resource_closeout_status=complete`，同步Task/STATUS/Plan并跑`check.ps1 -TaskPath doc/tasks/FEA-10.md`，才可closeout。Review approved本身不等于Task done。

## 推荐下一步（交DSH安排，不构成任务释放）

- **Task**：FEA-10 rework r4，修复F2-01/F2-02并补验证记录；继续满足现有依赖，不启动FEA-11。
- **Agent**：DSH负责findings处置、范围/Owner登记与最终集成；建议由DSH承担窄返修，之后指定全新Codex上下文审查。
- **Recovery point**：`G:/CODEX/New Manga`，`main`，base/head=`e23b01a919b4bc52a7e619ed1892bf2a5c3b50db`；本Review为唯一新增文件，须保留。无新worktree。
- **Scope**：按FEA-10既有allowed_paths窄改store.py、sqlite/pipeline.py及现有fea10测试、Task/Handoff/当前导航与verification/FEA-10；禁止改冻结契约、FEA-08/09证据、组合根、共享Schema/wire/依赖，不清理/删除资源，不push。若需扩大范围，由DSH先记录授权。
- **Deliverables/Gate**：新实现head、真实commit/sha绑定的EV、更新Handoff/验证日志/manifest、P1全部闭合及新head独立approved；之后才进入DSH集成closeout。

可直接转发给DSH：

> 在 `G:/CODEX/New Manga`、`main` 上处理FEA-10 rework r4，恢复base/head为 `e23b01a919b4bc52a7e619ed1892bf2a5c3b50db`。请先登记本报告的changes_requested及返修范围，保留 `doc/reviews/FEA-10-final-review-r2.md` 原字节。按现有allowed_paths修复F2-01的路径无关glossary豁免，覆盖override/defaults/最终持久化，保留合法token词条；修F2-02的Canonical Evidence commit/sha绑定，补F2-03/F2-04的新运行记录和当前导航。不得改冻结契约、FEA-08/09证据、组合根、Schema/wire/依赖或清理资源，不push。TEMP/TMP使用 `G:/CODEX/New Manga.workspace/FEA-10/fixtures/<新uuid>/`，跑pytest fea10/core/pipeline、providers、Release build/test、真实IPC、governance check、pins及零diff检查，逐次保留完整命令/环境/EXIT/skip原因，交付Handoff、EV和manifest。固定新head后派未参与返修的全新Codex上下文独立Review；两个P1闭合且approved、DSH集成验证与资源/evidence核销完成前不得done，不提前启动FEA-11。
