---
task_id: FEA-10
reviewer: Codex（用户指定的全新上下文，主审 /root；第 6 轮最终独立实现 Review）
reviewer_kind: agent
author: Codex / ZCode / DSH（实现及历轮返修）
base_commit: b218b52e0f9fe4827468826fe7fe6d3af322cc51
reviewed_head: 018646501467d7d40ab7f512beb8a6690cee6f6a
decision: changes_requested
---

# FEA-10 最终独立实现 Review r4（第 6 轮）

**结论：changes_requested；P0=0、P1=2、P2=1；当前 head 不可 closeout。**

F3-01 只部分修复。既有 glossary 内再次嵌套 translate 的输入已拒绝，但未经过 glossary 的其他路径仍能首次获得豁免；而且包含嵌套值的 glossary 只扫描嵌套值，同级标量认证键被漏过。主审在生产 SQLite assembly 独立复现 8 次走私接受，合成哨兵全部进入 PreparedRun、`settings_snapshot_json` 和 `run_json`。54 项专项通过不能覆盖这些负例。

## 身份、范围与工作区

- 审查者为本次用户直接指定的 Codex 全新上下文 `/root`，未参与该 Task 的任何实现、返修或既有证据生成；本轮未派辅助子 agent。不掌握可核实的主会话 UUID，不虚构该值。
- 仓库 `G:/CODEX/New Manga`，分支 `main`，Git common directory `.git`；开始、复跑及写报告前 HEAD 均为上述 reviewed_head，工作树干净。唯一仓库写入为本报告；未修改生产代码、测试、证据或契约，未 commit/push。
- 增量：`git diff b218b52e0f9fe4827468826fe7fe6d3af322cc51 018646501467d7d40ab7f512beb8a6690cee6f6a`，15 文件；提交 `cdaf441aa8a133a31771debc7064426d53913998`（返修）和 `018646501467d7d40ab7f512beb8a6690cee6f6a`（证据指针回填）。生产改动为 `store.py`、SQLite `pipeline.py`，另改一份专项测试，其余为文档/清单/日志。
- 已对照 AD-002/AD-003 边界、STATUS、REBASELINE_PLAN 当前 DAG、其指定 rolling checkpoint、Task AC/写域/EV、所给五份历史实现 Review、rework r5、AC-MATRIX、Handoff、ADJ-2026-11-04-FEA-10-R2、协作协议 §4/§5.1/§6 与 Review 模板。
- 契约承载：`doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md`（SC-R01…R09）、`FEA-C13_DRAFT_PROTECTION_DRAFT.md`（SC-D07/08）、`FEA-C05_PAGE_VISIBILITY_DRAFT.md`、`FEA-C04b_DELETE_PROTOCOL_DRAFT.md`、`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` rev 2.12 §5.5。不以契约中历史“运行未实现”说明否定当前实现事实。
- 增量逐 hunk 阅读；为判断历史修复及 AC，另读 Prepare/Accept、快照/typed provider/fallback/resolve、生产 assembly、专项测试、C# 默认 binding、RunMonitor/RunStateStore 和真实 IPC 测试。未宣称重新逐行审完实现基线以来全部 105 文件。
- 实现保护边界另从实际实现基线 `aa7bcd6161be5df07e2b8bf546600fec04af038f` 比较。Task `base_commit` 是范围释放基线，与本次增量及实际实现基线分别记录，不混用。

## Architecture、Standards 与 Spec

**Architecture：安全边界不通过。** Python Core/SQLite 单写者、Prepare/Accept、既有 scheduler/store、canonical request builder、candidate-only seam 和 durable receipt 均保持；未见本增量新增依赖、Schema、未冻结 wire 或其他 Task 实现。认证扫描和 scrubber 未实现所声明的业务路径与整表类型边界，导致普通快照落盘违规。

**Standards（executed）：** EV commit/字节绑定及增量写域符合当前记录标准；F4-03 说明新 IPC 日志对协作协议 §6.12 完整调用记录的局部回退。未另列需要阻断的 Fowler smell；安全问题按 Spec 裁定。

**Spec（executed）：** Task AC2 要求“敏感认证材料不入普通快照/日志/错误/证据”，ADJ §2.2 要求强类型白名单与敏感材料不入快照。F3-01 又明确豁免仅在真实 `translate.glossary`、值不得重获豁免。本 head 的两个分支分别违反路径限制与“全部值为标量才豁免”的返修要求。AC2 不成立；没有发现增量产品范围扩张。

## Findings

| ID | 级别 | 文件/行 | 触发、影响与证据 | 新 head 修复要求 | disposition |
|---|---|---|---|---|---|
| F4-01（F3-01 路径问题未闭合） | P1 | `src/application/tasks/store.py:257`、`:269`；`src/infrastructure/sqlite/pipeline.py:1517`、`:1534` | `glossary_exemption_used` 仅在经过 glossary 后置真，`parent == "translate"` 仍只看直接父键。`typeset.font_family.translate.glossary.authorization` 是上一轮已给出的输入，在 override/defaults 仍全部接受；列表包裹及 `translate.target_language.translate.glossary.authorization` 也接受。6 次接受均在 PreparedRun 和两列 Run 保留哨兵。直接 `_redact` 对错置 `...translate.glossary.token` 仍保留哨兵。 | 从明确的 settings 根按完整业务路径授予一次豁免，其他字段/列表不得因局部父键取得豁免。同步扫描与 `_redact`；补上一轮原输入、其他字段与列表包装的 override/defaults、Accept 和两列持久化负例，保留合法 token 词条。 | open；需新 head |
| F4-02（r5 混合词条表仍豁免标量键） | P1 | `src/application/tasks/store.py:259`、`:263`、`:266`；`src/infrastructure/sqlite/pipeline.py:1528` | 当 glossary 有嵌套值时，扫描只遍历 `nested` 的值并 `continue`，未校验同级键。`translate.glossary={authorization: SENTINEL, outer: {normal: "value"}}` 并非全部标量，却仍忽略 authorization 键；override/defaults 两次接受均在三处保留哨兵。`_redact` 此时严格遍历整表，但既有 substring 集合不含 authorization；因此它不能补救扫描漏项。mixed token 的直接探针更显示 scanner 允许、scrubber 删除的策略不一致。 | 整表不满足合法标量词条条件时，须拒绝非法形状，或在取消整表豁免后扫描全部键和值，不能只扫描嵌套值。统一 scrubber 的边界策略。补认证标量键与正常嵌套值混合、键顺序互换、列表值混合及 override/defaults/最终持久化回归。 | open；需新 head |
| F4-03（F2-03 新日志局部回退） | P2 | `verification/FEA-10/logs/dsh-rework5-dotnet.log:214` | r5 IPC 头仅为 `COMMAND=NEWMANGA_FEA10_IPC=1 dotnet test --filter Fea10RunIpcTests`，缺 project、Release/--no-build 等实际参数及 `NEWMANGA_BUILD_PYTHON` 门径；在已声明的 pwsh 中该环境赋值写法也不可直接执行。r4 同位置有完整可复制命令。r5 build/test 两条头完整、IPC 输出/EXIT 存在，故不据此判伪造或升级 P1。 | 后续新增实际运行日志，保存完整 PowerShell 调用、环境及 EXIT；保留 r4/r5 历史原字节，不事后伪补旧日志。 | open；非阻断 |

`test_glossary_exemption_cannot_be_regained_by_nesting` 虽新增，但两个负例都没有覆盖上一轮已复现的 `typeset.font_family.translate.glossary.authorization`；也没有 defaults、混合表或 Accept 后双列断言。其通过不能证明 F3-01 已完整闭合。

## F3-01 主审独立探针

环境：PowerShell 7.6.8（`C:/Program Files/PowerShell/7/pwsh.exe`），Python 3.14.6（`C:/Python314/python.exe`），未新建 venv/依赖；`PYTHONPATH=src`、`PYTHONDONTWRITEBYTECODE=1`。TEMP/TMP 均为：

`G:/CODEX/New Manga.workspace/FEA-10/fixtures/final4-review-a66367d2c57d4763b23c44076141a7f5/`

以 PowerShell here-string 经 stdin 传给 Python，未保存或改动测试脚本。每个输入 × 模式均新建独立合成 SQLite workspace。defaults 通过 `save_settings_section` 注入；记录 `before` 在写默认值之后、Prepare 之前。`SYNTHETIC-FINAL4-AUTH` 为合成哨兵。数据库初始化写入不冒充 Prepare 写入。

| settings 路径/形状 | override | defaults | PreparedRun / settings 列 / run 列 |
|---|---|---|---|
| `typeset.font_family.glossary.authorization` | RUN_SNAPSHOT_INCOMPLETE | RUN_SNAPSHOT_INCOMPLETE | 无 PreparedRun；DB changes=0、Run=0 |
| `translate.glossary.outer.glossary.authorization` | RUN_SNAPSHOT_INCOMPLETE | RUN_SNAPSHOT_INCOMPLETE | 同上 |
| `typeset.font_family.translate.glossary.authorization` | **ACCEPTED** | **ACCEPTED** | **三处均含哨兵**；每例 created=true |
| `translate.glossary.outer.translate.glossary.authorization` | RUN_SNAPSHOT_INCOMPLETE | RUN_SNAPSHOT_INCOMPLETE | 无 PreparedRun；DB changes=0、Run=0 |
| `translate.glossary={authorization: SENTINEL, outer: {normal: "value"}}` | **ACCEPTED** | **ACCEPTED** | **三处均含哨兵**；每例 created=true |
| `typeset.font_family=[{translate: {glossary: {authorization: SENTINEL}}}]` | **ACCEPTED** | **ACCEPTED** | **三处均含哨兵**；每例 created=true |
| `translate.target_language.translate.glossary.authorization` | **ACCEPTED** | **ACCEPTED** | **三处均含哨兵**；每例 created=true |
| `translate.glossary.outer=[{translate: {glossary: {authorization: SENTINEL}}}]` | RUN_SNAPSHOT_INCOMPLETE | RUN_SNAPSHOT_INCOMPLETE | 无 PreparedRun；DB changes=0、Run=0 |
| `typeset.font_family.headers.authorization` | RUN_SNAPSHOT_INCOMPLETE | RUN_SNAPSHOT_INCOMPLETE | 同上 |
| 合法 `translate.glossary={token: "word-value", headers: "another-word"}` | ACCEPTED | ACCEPTED | token 在 preview/两列保留；accepted snapshot 修改抛 TypeError |

20 格合计：10 个拒绝、8 个安全失败的接受、2 个合法接受。所有 Prepare 调用本身 DB changes=0，所有拒绝错误不含哨兵；不能把“Prepare 零写”解释为之后的 Accept 不落敏感数据。

### 可复制核心探针与本次输出 artefact

以下核心循环与本次实际调用一致，可在新的唯一 review 根重放。完整 20 格见上表；代码截取其中 4 个安全失败输入，以便不依赖作者测试复现两个 P1。本报告是本轮唯一允许写入的仓库 artefact，直接保留探针输出，不改写 `verification/**`。

```python
import json
from pathlib import Path
from tests.core.test_fea00a_pipeline_seam import _new_workspace
from domain.tasks.models import PipelineScope, ScopeType, PipelineError

S = "SYNTHETIC-FINAL4-AUTH"
cases = {
    "r3_misplaced_translate": {
        "typeset": {"font_family": {"translate": {"glossary": {"authorization": S}}}}},
    "mixed_glossary": {
        "translate": {"glossary": {"authorization": S, "outer": {"normal": "value"}}}},
    "misplaced_translate_list": {
        "typeset": {"font_family": [{"translate": {"glossary": {"authorization": S}}}]}},
    "nested_translate_in_other_field": {
        "translate": {"target_language": {"translate": {"glossary": {"authorization": S}}}}},
}
# root 是 TEMP/TMP 指定的全新唯一目录；避免复用已有子目录。
for name, settings in cases.items():
    for mode in ("override", "defaults"):
        p = Path(root) / (name + "-" + mode)
        p.mkdir()
        core, _, region = _new_workspace(p)
        try:
            scope = PipelineScope(ScopeType.REGION, selected_ids=(region,))
            if mode == "defaults":
                for section, values in settings.items():
                    core.pipeline_defaults.save_settings_section(section, values)
            before = core.conn.total_changes
            prepared = core.pipeline.prepare_run(
                "ocr_region", scope,
                **({"overrides": {"settings": settings}} if mode == "override" else {}))
            prepare_changes = core.conn.total_changes - before
            run, created = core.pipeline.accept_prepared_run(
                prepared, scope, idempotency_key="probe")
            row = core.conn.execute(
                "SELECT settings_snapshot_json, run_json FROM pipeline_runs WHERE run_id=?",
                (run.run_id,)).fetchone()
            print(json.dumps(dict(
                case=name, mode=mode, result="ACCEPTED", created=created,
                prepare_changes=prepare_changes, prepared_sentinel=S in str(prepared),
                settings_column_sentinel=S in row[0], run_column_sentinel=S in row[1]),
                sort_keys=True))
        finally:
            core.conn.close()
```

本次完整 20 格进程 EXIT=0；下列是其中 8 个安全失败场景的原始 JSON 输出。EXIT=0 表示探针完成，**产品安全结论为 FAIL**。

```text
{"case": "r3_misplaced_translate", "created": true, "mode": "override", "prepare_changes": 0, "prepared_sentinel": true, "result": "ACCEPTED", "run_column_sentinel": true, "settings_column_sentinel": true}
{"case": "r3_misplaced_translate", "created": true, "mode": "defaults", "prepare_changes": 0, "prepared_sentinel": true, "result": "ACCEPTED", "run_column_sentinel": true, "settings_column_sentinel": true}
{"case": "mixed_glossary", "created": true, "mode": "override", "prepare_changes": 0, "prepared_sentinel": true, "result": "ACCEPTED", "run_column_sentinel": true, "settings_column_sentinel": true}
{"case": "mixed_glossary", "created": true, "mode": "defaults", "prepare_changes": 0, "prepared_sentinel": true, "result": "ACCEPTED", "run_column_sentinel": true, "settings_column_sentinel": true}
{"case": "misplaced_translate_list", "created": true, "mode": "override", "prepare_changes": 0, "prepared_sentinel": true, "result": "ACCEPTED", "run_column_sentinel": true, "settings_column_sentinel": true}
{"case": "misplaced_translate_list", "created": true, "mode": "defaults", "prepare_changes": 0, "prepared_sentinel": true, "result": "ACCEPTED", "run_column_sentinel": true, "settings_column_sentinel": true}
{"case": "nested_translate_in_other_field", "created": true, "mode": "override", "prepare_changes": 0, "prepared_sentinel": true, "result": "ACCEPTED", "run_column_sentinel": true, "settings_column_sentinel": true}
{"case": "nested_translate_in_other_field", "created": true, "mode": "defaults", "prepare_changes": 0, "prepared_sentinel": true, "result": "ACCEPTED", "run_column_sentinel": true, "settings_column_sentinel": true}
```

另直接调用生产 `_scan_auth_material`、`_redact`，同一环境、无 DB；输入与输出如下（同一探针进程 EXIT=0）：

| case | 输入核心 | scan | redact_contains_sentinel |
|---|---|---|---|
| root_scalar | `{translate: {glossary: {token: S}}}` | PASS | true（合法词条） |
| misplaced_token | `{typeset: {font_family: {translate: {glossary: {token: S}}}}}` | **PASS** | **true** |
| renested_token | `{translate: {glossary: {outer: {translate: {glossary: {token: S}}}}}}` | RUN_SNAPSHOT_INCOMPLETE | false |
| mixed_token | `{translate: {glossary: {token: S, outer: {normal: "value"}}}}` | **PASS** | false（scanner/scrubber 分歧） |
| mixed_auth | `{translate: {glossary: {authorization: S, outer: {normal: "value"}}}}` | **PASS** | **true** |

```text
{"redact_case": "root_scalar", "redact_contains_sentinel": true, "scan": "PASS"}
{"redact_case": "misplaced_token", "redact_contains_sentinel": true, "scan": "PASS"}
{"redact_case": "renested_token", "redact_contains_sentinel": false, "scan": "RUN_SNAPSHOT_INCOMPLETE"}
{"redact_case": "mixed_token", "redact_contains_sentinel": false, "scan": "PASS"}
{"redact_case": "mixed_auth", "redact_contains_sentinel": true, "scan": "PASS"}
```

## 前轮处置、EV 与 manifest

| 项目 | 本轮判断 | 独立依据 |
|---|---|---|
| F3-01 / F2-01 / FR-01 / RR-01 安全总目标 | **未闭合** | 原旧 glossary 嵌套及再次嵌套 translate 已拒；另一路原 r3 输入仍接受，新混合表也接受，见 F4-01/02。非执行段过滤保持，不等于认证面整体通过。 |
| F2-02 / FR-02 / RR-02 | closed 保持 | 二进制 `git show`、hashlib、CRLF 换算直接核对 commit 与 sha，见下表。 |
| F2-03 | r4 处置仍成立；r5 局部回退 | 新 Python、build/test 日志有完整头与 EXIT；r5 IPC 调用头不全，记 F4-03。不能概括为“所有新日志均完整”。 |
| F2-04 / FR-08 / RR-08 当前导航 | closed 保持 | Task:262 明确旧用例失效，指向 `RunControllerNullFakeTests.PreparedRunPayload_CarriesTheHostDefaultBindings`；实际文件/方法存在，r4 导航原字节保留，r5 新日志独立追加。 |

直接以 `subprocess.check_output(["git", "show", ref+":"+path])` 读取字节，未用 PowerShell 文本重定向算 hash。CRLF 换算先将已有 CRLF 归一 LF，再将 LF 转 CRLF。

| AC-MATRIX 来源 | Git blob bytes / SHA-256 | CRLF 工作树 basis bytes / SHA-256 |
|---|---|---|
| `cdaf441aa8a133a31771debc7064426d53913998` | 14682 / `f4ae9c58d5e5ba08e35b59a88a2364b14cd82b93216236b8fa692231a8e28dc7` | 14790 / `d354bfc207815e2d340ad4f4c32e453d5a6adca0a178f5a9a1a3ddac0ebb0502` |
| `018646501467d7d40ab7f512beb8a6690cee6f6a` | 同上 | 同上 |
| 当前工作树 | 14790 / `d354bfc207815e2d340ad4f4c32e453d5a6adca0a178f5a9a1a3ddac0ebb0502` | 同左 |

Task EV 的 commit=`cdaf441a…` 与 sha=`d354bfc2…` 匹配。原始 LF blob hash 不同是 basis 差异，不能判为损坏。

DELIVERY-MANIFEST 的 **7/7 文件**均匹配工作树 bytes/SHA，也匹配 `head=cdaf441a…` 的 CRLF 字节；`generated_after_head` 同为该 commit。`excluded_docs` 恰为本增量四份文档（Task、Handoff、rework record、r3 Review）；再排除 manifest 自身及资源/范围生成文件后，15 个增量文件无遗漏。它是增量字节清单，不是完整历史证据集合。`created_at` 是提交前生成时点、`uncommitted=true` 是当时状态，两个 head 字段为后补锚点，不宣称清单是在该提交之后独立重新生成。本 r4 报告不属于被审交付，不要求改写原清单。

### 历轮修复保持与债务

- **R-001…R-004**：执行段过滤/合法 typeset 键、三种 binding 规范化、未 typed fallback 冻结错误码、本地 typed 默认 binding 的 Python 专项通过；C# 默认注入代码及实际单测存在、r5 .NET 日志数量保持。本轮未重跑 C#，不把日志核对冒充执行。
- **RR-01** 的非执行段移除及普通嵌套认证负例保持，但安全总目标仍未闭合；**RR-02** 的 EV 保持；**RR-03/RR-09** 的新主套件与 build 成功日志存在，旧失败历史保留；**RR-04** 的 fallback 容器校验、**RR-05** 的 local type/model 与已知类型校验、**RR-06** 的 Core null/非对象 binding 错误码由本轮补充探针确认；**RR-07** 的 IPC workspace 输出/历史说明保持；**RR-08** 当前导航保持。
- **RR-10…RR-14**：用户提供的历史审查文件中未找到这些 finding 编号；实际 rework-review-r1 表到 RR-09。无法把不存在的编号标为 closed；不据此虚构缺失问题。后续编号按实际 FR/F2/F3 记录。
- **FR-01** 仍受 F4-01/02 阻断；**FR-02** 闭合；**FR-03** mock/local/remote primary 共用 `_freeze_fallbacks` 保持，专项含未 typed fallback 拒绝，补充探针确认 local primary 的 typed fallback 完整冻结；**FR-04** null binding、**FR-05** accepted settings 递归不可变、**FR-06** 合法 token 词条、**FR-07** 非法执行段、**FR-08** 当前导航均保持。未把 FR-06 的合法词条通过推导成全路径安全。

| 既有债务 | 本轮可接受边界（最终处置仍归 DSH） |
|---|---|
| R-005 | 支持的 local typed type/model 检查保持；mock/local 合成 adapter 验证不等于真实模型替换或所有 provider 验收；其他类型按 Prepare fail-closed。 |
| R-006 | P2 保留：不完整 typed 配置的 StartRun 提前 fail-closed 会改变失败时点，继续披露，不能称全部兼容行为不变。 |
| R-007 | P2 保留：Python/DB 持久状态权威与 C# 成功查询投影成立；`is_terminal` 无生产消费者、原生 UI/C# 控制专项不足，不升级成 UI E2E。 |
| R-011 | P2 保留：Host 候选/attempt 缓存上限及清理代价未修，继续登记。 |
| R-012 | InMemory 与 SQLite 控制 seam 差异继续显式保留，以生产 SQLite 故障注入判断零提前写。 |
| R-013 | P2 保留：crash_restart 是恢复放弃、candidate 可诊断及零提前写，不证明重启后可继续提交该 candidate。 |
| R-014 | 合法 token 词条误拒解除；衍生认证漏洞是当前 P1，不能接受为 P2 债务。 |
| R-015 | P2 保留：source lease 异常仍归并 db_failed，损害诊断；注入 seam 零写不替代 Windows 系统租约验收。 |
| R-016 | P2 保留：preview 异常统一 unavailable 影响诊断；接受与执行守卫另有验证。 |

## AC1–AC10 独立判断

| AC | 状态 | 本轮依据与结论边界 |
|---|---|---|
| AC1 | MET（机制） | 专项复跑 Prepare 零写/零执行、四元组独立 hash、stale/过期/不完整拒绝；读取 Accept 事务重读后写 Run/receipt。敏感输入缺陷另计 AC2。 |
| AC2 | **NOT MET** | typed execution/digest/白名单与普通负例保持；F4-01/02 独立证明认证哨兵进入 PreparedRun 及 Run 双列。卡中整体 MET 声明不成立。 |
| AC3 | MET（ADJ §2.1 限定） | 专项复跑可确定请求 preview/transport endpoint-model-body/发送 provenance 同摘要并 commit，邻页 stale/接受后 pin、provider/defaults 漂移隔离通过；未来 OCR 输出仅标 requires_upstream_output。 |
| AC4 | MET（限定覆盖） | retry 同键/异键失败子集/source_run_id/接受时上下文、新 provider 冻结与旧 Run 不改、凭据/版本阻塞恢复通过；补充 local type drift 验证。真实模型版本/独立差异披露 UI 未验收。 |
| AC5 | MET（seam 层） | 17 项故障/原子提交专项通过；三处 live/revision/行数及成功 receipt/counts 守卫保持；多 Region apply 与 pipeline step 的事务单位分开。crash 为恢复放弃，lease/binding 为注入。 |
| AC6 | MET（Python/DB 与 C# 结构层） | 4 项控制 pending/终态共同及附加不变量/重开库测试通过；读取 RunMonitor/RunStateStore，仅成功 Core 查询发布权威快照。保留 R-007 限制。 |
| AC7 | MET | 丢 ACK、过期/配置读取前 receipt 优先、异 fingerprint、同 request_id 异 key、独立进程重开同库与 ControlRun restart receipt 复跑通过；真实 stdio 重启本轮仅核对已有代码/日志。 |
| AC8 | MET（所覆盖链路） | 本轮 Python 生产 assembly Prepare→Accept→transport→commit 通过；r5 build/.NET/IPC 输出数量及 EXIT 保持；IPC 主要到 Prepare/Accept/重放，commit 由 Python 覆盖。F4-03 限制 r5 IPC 调用的可复现性；本轮未重跑 .NET。 |
| AC9 | **PARTIAL** | pins17/17、冻结/前置证据/closeout/组合根零 diff、增量写域及 EV/manifest 匹配；但本 Review 未 approved，DSH 最终集成、canonical/resource closeout 尚未完成。 |
| AC10 | MET | 15 个增量文件均在允许写域；无新增依赖/Schema/未冻结 wire 或 FEA-11/12/13/14 范围；组合根及 FEA-08/09 保护边界未动。 |

## Verification 与证据真实性

**Verification：指定机械/专项检查通过；安全探针 FAIL，因此不可批准。**

主审实际 shell/Python/TEMP/TMP 见前文；没有新 venv。测试 helper 自身另在 `FEA-10/fixtures/` 父目录生成逐例唯一合成目录，不保证都嵌套在 TEMP 根内；全部原位保留，无清理/移动。运行记录在本报告保留，未写入只读的 tracked 证据。

| 场景 | 实际命令或步骤 | 结果 |
|---|---|---|
| 治理 | `pwsh -NoProfile -File tools/governance/check.ps1` | PASS，4 warnings，EXIT=0；只证明机械条件。 |
| 冻结 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 17/17 PASS，EXIT=0。 |
| 专项 | `C:/Python314/python.exe -m pytest tests/fea10 -q -p no:cacheprovider` | **54 passed，0 skipped，4.26s，EXIT=0**；禁用 cache 避免仓库缓存写入。 |
| F3-01 探针 | stdin Python，10 输入 × override/defaults，加 5 个 scanner/scrubber 输入 | 20 格与输出见前；8 次安全失败的接受，进程 EXIT=0、安全 FAIL。 |
| 历史修复补充探针 | Core wire null/str/list binding、非法 ocr/translate/typeset 段、local typed fallback/type drift/未知类型、损坏 frozen_fallbacks 容器 | 修正探针环境后全部符合预期，EXIT=0；原始输出见下。 |
| EV/manifest | 二进制 git show、SHA-256、CRLF、7 项文件与 head 逐项比较 | PASS；15 个增量无漏项、无域外项。 |
| 冻结/前置/组合根 | `git diff --name-only aa7bcd6161be5df07e2b8bf546600fec04af038f 01864650 -- doc/contracts <C-08/C-13/C-05/C-04b> verification/FEA-08 verification/FEA-09 doc/tasks/FEA-08.md doc/tasks/FEA-09.md doc/handoffs/FEA-08-closeout.md doc/handoffs/FEA-09-closeout.md <App.axaml/App.axaml.cs/NewManga.App.csproj/NewManga.sln>` | 空；其他冻结承载由17/17 pins核对。 |
| diff hygiene | `git diff --check b218b52e 01864650` | EXIT=2：`doc/reviews/FEA-10-final-review-r3.md:192: new blank line at EOF.`；非行为阻断，不修改历史报告。 |
| r5 日志 | `verification/FEA-10/logs/dsh-rework5-{pytest-main,providers,dotnet}.log` | 主套件1057/1warning、providers559/4、build0/0、.NET1345/0/75、IPC1；各阶段 EXIT=0。IPC头缺项见F4-03。 |

主审专项原始输出（shell/解释器/隔离根已在本节指定）：

```text
......................................................                   [100%]
54 passed in 4.26s
EXIT=0
Governance check: PASS (4 warnings)
EXIT=0
PIN AUDIT: PASS (all 17)
EXIT=0
```

补充历史修复探针使用同一 review 根的独立 `history-wire-corrected` 与 `history-local-corrected` 合成库。Core wire 实例与直接 pipeline 实例分开，local 为有 type/model、禁止调用 recognize 的合成 adapter，无网络/真实模型。第一次辅助探针将两者放同一实例，8 个检查完成后，直接 Accept 触发 `INVALID_RUN_TRANSITION: Run scheduler owner is unavailable`，EXIT=1；这是 CoreServiceServer 注册 scheduler owner 后错误混用直接调用的探针设置问题，不是产品 finding。未隐藏该次失败，也未将其未执行的容器检查标 PASS；随后隔离实例重跑得到以下输出：

```text
{"case": "provider_bindings_NoneType", "error": "INVALID_REQUEST"}
{"case": "provider_bindings_str", "error": "INVALID_REQUEST"}
{"case": "provider_bindings_list", "error": "INVALID_REQUEST"}
{"case": "invalid_section_ocr", "error": "RUN_SNAPSHOT_INCOMPLETE"}
{"case": "invalid_section_translate", "error": "RUN_SNAPSHOT_INCOMPLETE"}
{"case": "invalid_section_typeset", "error": "RUN_SNAPSHOT_INCOMPLETE"}
{"case": "local_fallback_and_type_drift", "frozen_fallback": true, "type_drift_blocked": true}
{"case": "unknown_local_type", "error": "RUN_SNAPSHOT_INCOMPLETE"}
{"case": "malformed_frozen_fallbacks", "error": "RUN_SNAPSHOT_INCOMPLETE"}
REGRESSION_PROBE_COMPLETED
EXIT=0
```

r5 .NET 通过数独立相加为 `21+38+253+117+78+31+136+671=1345`，skip=`46+22+7=75`，总计1420；另一次定向 IPC 为1/0/0。Python 主套件比 r4 的1056增加1，与新专项53→54一致；providers总计563，其中559通过、4跳过。未见测试数量减少或伪造结果的确证。已有失败/不完整历史保留；主套件末尾 QML TypeError 与 Pillow deprecation 仍可见，不将其改写成新架构问题或 pytest 失败。providers4项与.NET75项未在这些日志逐项给出原因，继续保留追溯限制，不能算通过或臆测跳过原因。

**NOT_RUN / 未覆盖：** 本轮未重跑 .NET build/全量/真实 IPC，未重跑 Python core/pipeline/providers 全量；用户允许核对 r5 日志。未做原生 UI 点击、Windows 系统级 lease 故障、真实外网 provider/模型质量与真实模型替换。没有访问真实用户库；未逐文件重算 RESOURCE-MANIFEST 的全部历史 fixtures，也未扫描/清理早期系统 TEMP。未运行项不以日志核对冒充主审实跑。

治理差异仅在此留证，交 DSH 处理：STATUS/Task 当前为 in_review，而 PLAN 仍有 AC2/3/4/6 待续作的旧措辞，rolling checkpoint 是较早恢复点；Task `delivery_head` 仍为 a9293458、integration/canonical/resource 状态未完成。本轮不修改权威指针，也不据旧措辞恢复实施或批准关闭。

报告落盘后再次运行 `check.ps1`：PASS（4 warnings）、EXIT=0；`git status --short` 仅本报告为 untracked，tracked/staged diff 均为空，HEAD 仍为 reviewed_head。

## 新 head 修复与 closeout 条件

1. **当前不得 closeout/done。** F4-01 必须使用完整业务路径/不可重新授予的边界；F4-02 必须处理整张非标量 glossary 的键和值，不再漏过同级标量认证键。同步 `_redact`，保留合法 scalar token 词条；不得仅追加个别黑名单形状。
2. 新负例至少含本报告全部绕过形状、上一轮两条原输入、混合表键顺序/列表值，覆盖 override/defaults、PreparedRun、Accept 和两列 Run；失败要断言冻结错误码与零副作用。补齐新日志完整调用与 skip 原因，保留历史原字节。
3. 在新 head 实跑 Task 门禁（fea10/core/pipeline、providers、Release build/test、真实IPC、governance、pins、保护边界零diff及写域），重新绑定真实包含证据的 commit/sha、Handoff 与 manifest。固定新 head，再由未参与返修的全新上下文 Review；本报告不批准后续 head。
4. 新 head 获 approved 后仍须 DSH 记录集成验证、正确 delivery/integration commit、完整 Canonical Evidence 与资源 disposition（含本轮新增 review fixtures），同步 Task/STATUS/Plan，按生命周期把 canonical_evidence_status/resource_closeout_status 置 complete 并跑治理检查；这些条件完成前不能 done。批准 Review 本身也不等于 Task closeout。

## 推荐下一步与可转发指令

- **Task**：FEA-10 rework r6（处理 F4-01/02，补 F4-03 运行记录）；继续现有依赖与冻结范围，不启动 FEA-11。
- **Agent**：DSH 负责 findings 处置、范围/Owner 登记、窄返修安排及最终集成；返修后指定未参与本次实现/返修的全新 Codex 上下文 Review。
- **Recovery point**：`G:/CODEX/New Manga`、`main`，返修起点 base/head=`018646501467d7d40ab7f512beb8a6690cee6f6a`；本报告是主树唯一新增文件，应保留。无需新建 worktree；如决定隔离，由 DSH 按 workspace 规则创建。
- **Scope**：按 FEA-10 既有 allowed_paths 窄改两个认证函数、现有 fea10 测试及 Task/Handoff/当前导航/verification；禁止改冻结契约、FEA-08/09 证据及 closeout、组合根、Schema/wire/依赖；不删除、迁移或清理资源，不 push。范围扩大须 DSH 先落盘。
- **Deliverables/Gate**：新固定实现 head、两个 P1 闭合的负例 artefact、完整门禁日志、正确 EV commit/sha、Handoff/manifest 与独立 approved；之后才进入 DSH 集成及资源/evidence 核销。

可直接转发给 DSH：

> 在 `G:/CODEX/New Manga`、`main`，以 `018646501467d7d40ab7f512beb8a6690cee6f6a` 为 FEA-10 rework r6 起点，先登记本报告的 changes_requested 与返修范围，并保留 `doc/reviews/FEA-10-final-review-r4.md` 原字节。按现有 allowed_paths 修复 F4-01 的错置 translate.glossary 首次豁免，以及 F4-02 的混合词条表同级认证键漏扫；同步 `_redact`，保留合法 token 词条，补本报告全部绕过形状在 override/defaults、PreparedRun、Accept 与两列持久化的回归。补 F4-03 的真实完整 IPC 调用日志，不改历史日志。不得改冻结契约、FEA-08/09 证据/closeout、组合根、Schema/wire/依赖，不清理资源，不 push。TEMP/TMP 使用 `G:/CODEX/New Manga.workspace/FEA-10/fixtures/<新uuid>/`，实跑 pytest fea10/core/pipeline、providers、Release build/test、真实 IPC、governance check、pins 及保护边界零diff/写域检查，逐次保存完整命令、环境、EXIT 和 skip 原因；交付新 head、Handoff、真实 commit/sha 绑定的 EV 与 manifest。新 head 再派未参与返修的全新 Codex 上下文独立 Review；P1 闭合且 approved、DSH 集成验证与资源/evidence 收口完成前不得 done，不提前启动 FEA-11。
