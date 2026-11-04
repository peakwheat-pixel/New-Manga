---
task_id: FEA-10
reviewer: Codex（全新上下文，主审 /root；第 5 轮最终独立实现 Review）
reviewer_kind: agent
author: Codex / ZCode / DSH（实现及历轮返修）
base_commit: e23b01a919b4bc52a7e619ed1892bf2a5c3b50db
reviewed_head: b218b52e0f9fe4827468826fe7fe6d3af322cc51
decision: changes_requested
---

# FEA-10 最终独立实现 Review r3（第 5 轮）

结论：**changes_requested；P0=0、P1=1；当前 head 不可 closeout。** F2-01 的两个旧输入形状已被拒绝，但修复仍只检查直接父键，不检查完整路径；在嵌套值中再次加入 `translate.glossary` 可重新获得豁免。主审独立复现四次接受，合成认证哨兵进入 PreparedRun 及 `settings_snapshot_json`、`run_json` 两列。F2-02/F2-03/F2-04 已闭合。

## 身份、范围与依据

- 本次用户直接指定的 Codex 全新审查上下文 `/root`，未参与 FEA-10 的实现、返修或既有证据生成。不掌握可核实的主会话 UUID，不虚构该值。
- 只读辅助审查上下文：`/root/standards_review`（Standards、EV/manifest/日志/范围）、`/root/spec_review`（Spec、安全调用链及历史修复保持）；两者未实现、返修、写文件或运行测试。主审独立执行指定门禁、生产 assembly 探针及二进制 hash 核对，并裁定最终 findings。
- 仓库 `G:/CODEX/New Manga`，分支 `main`，Git common directory `.git`；初始 HEAD 精确等于 reviewed_head，初始及测试后工作树均干净。唯一仓库写入为本报告；没有 commit/push，没有修改或恢复生产代码、测试、证据、契约。
- 增量命令：`git diff e23b01a919b4bc52a7e619ed1892bf2a5c3b50db b218b52e`。两个提交为 `1ee761e7e4b25bf1cb15a5ae7b4e1c36693cb77a`、`b218b52e0f9fe4827468826fe7fe6d3af322cc51`。冻结/前置/组合根边界另与实际实现基线 `aa7bcd6161be5df07e2b8bf546600fec04af038f` 比较。
- 已读当前 STATUS、DAG、所指 rolling checkpoint、Task AC/写域/EV、上一轮及三份历史实现 Review、rework r4、AC-MATRIX、ADJ-2026-11-04-FEA-10-R2、协作协议 §4/§5.1/§6、Review 模板和实际调用链。
- 契约对照承载：`doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md`、`FEA-C13_DRAFT_PROTECTION_DRAFT.md`、`FEA-C05_PAGE_VISIBILITY_DRAFT.md`、`FEA-C04b_DELETE_PROTOCOL_DRAFT.md`，以及 `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` rev 2.12；架构按 AD-002 与其 AD-003 覆盖说明。
- 历史编号以文件实际内容为准：所给 rework-review-r1 含 RR-01…RR-09，未找到 RR-10…RR-14；后续为 FR-01…FR-08、F2-01…F2-04。不把不存在的编号宣布为已验证或已关闭。

## Architecture 与双轴审查

**Architecture：不通过安全边界。** 既有 Python Core/SQLite 单写者、Prepare/Accept、canonical request builder、candidate-only seam 与 durable receipt 均保持；认证材料的路径白名单仍可绕过。没有发现本增量新增依赖、Schema、未冻结 wire 或产品范围扩张。

### Standards（executed）

未发现本增量新增的记录标准硬性违规或需要单列的 Fowler smell。F2-02 的 commit/字节绑定现符合协作协议 §4.1；F2-03 的四份 r4 日志已补足完整调用、shell、TEMP/TMP、EXIT；F2-04 当前导航明确废止旧测试名并指向真实用例及日志。既有 skip 逐项原因不足仍保留为追溯限制，不重复计为新 finding。

### Spec（executed）

**1 个 P1：F3-01（F2-01 未闭合）。** Task AC2 要求“敏感认证材料不入普通快照/日志/错误/证据”；ADJ §2.2 要求敏感材料不入快照且强类型白名单落盘；前轮 F2-01 要求豁免仅绑定真实 `translate.glossary` 词条层、不得重新授予。目前实现仅验证最后一个父键，仍违反该要求。未发现增量范围扩张。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 修复要求 | 状态 |
|---|---|---|---|---|---|---|
| F3-01（F2-01 未闭合） | P1 | `src/application/tasks/store.py:254`、`:261`；`src/infrastructure/sqlite/pipeline.py:1517`、`:1526` | `parent == "translate"` 仅检查直接父键；递归遇到任意嵌套 `translate` 即重新授予 glossary 词条名豁免。`typeset.font_family.translate.glossary.authorization` 与 `translate.glossary.outer.translate.glossary.authorization` 在 override/defaults 均被接受，认证值进入 PreparedRun 与两列 Run。`_redact` 同样可被嵌套 translate 重启豁免。 | 主审生产 SQLite assembly 10 场景及 4 个 `_redact` 探针，见下表；4 次绕过均 created=true，prepared 与两列 sentinel=true。 | 在已知 settings 根建立完整路径或不可重新授予的状态；仅豁免真实 `translate.glossary` 一层词条名，词条值及其他路径不得重新获得豁免。同步 `_redact`，必要时按业务类型拒绝非法 font_family/glossary 值。补旧形状、新形状、override/defaults、最终接受与两列持久化负例，保留合法 token 词条。 | open；需新 head |

`filter_prepared_settings`（store.py:101）只过滤 section；`validate_prepared_snapshots`（:127–133）只检查 section 为 Mapping 及第一层字段白名单，没有对 font_family 或 glossary 词条值作可阻断本输入的业务类型校验。Prepare 的 override 扫描、freeze 中的 `_redact`、最终 settings 扫描与 Accept 的再次扫描均不能挡住此形状。

### F3-01 主审独立复现

shell 为 PowerShell；以下代码以 here-string 经 stdin 传给 `C:/Python314/python.exe -`，未保存或修改测试脚本。设置 `PYTHONPATH=src`、`PYTHONDONTWRITEBYTECODE=1`，TEMP/TMP 均为：

`G:/CODEX/New Manga.workspace/FEA-10/fixtures/final3-review-56afb09370d4446cab231a5c445c09df/`

每例 `_new_workspace` 在该根的独立子目录创建合成库；默认值在记录 `before` 前写入，拒绝后的 DB changes 从准备调用前开始计。哨兵 `SYNTHETIC-FINAL3-AUTH` 为合成文本。

```python
from tests.core.test_fea00a_pipeline_seam import _new_workspace
from domain.tasks.models import PipelineScope, ScopeType

core, _, region = _new_workspace(case_root)
scope = PipelineScope(ScopeType.REGION, selected_ids=(region,))
settings = {"typeset": {"font_family": {"translate": {"glossary": {
    "authorization": "SYNTHETIC-FINAL3-AUTH"
}}}}}
# override 路径；defaults 路径在另一独立库先逐 section 调
# core.pipeline_defaults.save_settings_section(section, values)，再无 overrides Prepare。
prepared = core.pipeline.prepare_run("ocr_region", scope,
                                     overrides={"settings": settings})
run, created = core.pipeline.accept_prepared_run(
    prepared, scope, idempotency_key="probe")
row = core.conn.execute(
    "SELECT settings_snapshot_json, run_json FROM pipeline_runs WHERE run_id=?",
    (run.run_id,)).fetchone()
assert created
assert "SYNTHETIC-FINAL3-AUTH" in str(prepared)
assert all("SYNTHETIC-FINAL3-AUTH" in column for column in row)
core.conn.close()
```

| settings 路径/形状 | override | defaults | PreparedRun / settings 列 / run 列 |
|---|---|---|---|---|
| `typeset.font_family.glossary.authorization`（旧形状） | RUN_SNAPSHOT_INCOMPLETE | RUN_SNAPSHOT_INCOMPLETE | 未生成；DB changes=0、Run=0 |
| `translate.glossary.outer.glossary.authorization`（旧形状） | RUN_SNAPSHOT_INCOMPLETE | RUN_SNAPSHOT_INCOMPLETE | 未生成；DB changes=0、Run=0 |
| `typeset.font_family.translate.glossary.authorization`（新形状） | **ACCEPTED** | **ACCEPTED** | **三处均含哨兵**，每例新建 Run |
| `translate.glossary.outer.translate.glossary.authorization`（新形状） | **ACCEPTED** | **ACCEPTED** | **三处均含哨兵**，每例新建 Run |
| 合法 `translate.glossary={token: "word-value", headers: "another-word"}` | ACCEPTED | ACCEPTED | 词条在 preview、持久化 settings 均保留；accepted snapshot 嵌套赋值抛 TypeError |

另直接调用生产 `_redact`：根层 `translate.glossary.token` 保留词条（正确）；`typeset.font_family.glossary.token` 去除（正确）；`typeset.font_family.translate.glossary.token` 与 `translate.glossary.outer.translate.glossary.token` 均保留哨兵（路径豁免仍错误）。这里用 token 检验 scrubber，避免把其既有非 token 键策略误当作此项证据。

探针进程 EXIT=0 表示复现过程完成；四次认证走私结果为安全 FAIL，不能以进程退出成功宣称产品通过。

## 前轮处置与证据核对

| 前轮项 | 本轮判断 | 独立证据 |
|---|---|---|
| F2-01 | **未闭合** | 旧四格拒绝成立，新四格可重启豁免；见 F3-01 |
| F2-02 | closed | 主审以 `subprocess.check_output(["git", "show", ref+":"+path])` 读取二进制，再用 hashlib.sha256，未经过 PowerShell 文本重定向 |
| F2-03 | closed | 四份 `logs/dsh-rework4-*.log` 含完整 COMMAND、shell=pwsh、TEMP/TMP、EXIT=0；dotnet 三条命令完整，IPC 含环境门径 |
| F2-04 | closed | Task:262 明确旧 `RunControllerTests.PreparedRunPayload_*` 失效，当前指向实际 `RunControllerNullFakeTests.PreparedRunPayload_CarriesTheHostDefaultBindings` 及 r4 日志；实际类型/方法存在 |

### F2-02 Git 字节与 manifest

| AC-MATRIX 来源 | Git blob bytes / SHA-256 | CRLF 工作树 basis bytes / SHA-256 |
|---|---|---|
| `1ee761e7e4b25bf1cb15a5ae7b4e1c36693cb77a` | 14127 / `274e50dee40cd0fdcb8981c61b4aa07159297e384935e78e9215ffad6bbd91e9` | 14229 / `0eb384c52893d35f9bdc4637db2a9065262448e4a2bd5af1b81496c324fd59ba` |
| `b218b52e0f9fe4827468826fe7fe6d3af322cc51` | 同上 | 同上 |
| 当前工作树 | 14229 / `0eb384c52893d35f9bdc4637db2a9065262448e4a2bd5af1b81496c324fd59ba` | 同左 |

CRLF 换算先归一已有 CRLF，再把 LF 转为 CRLF。Task EV 的 commit=`1ee761e7…` 与 sha=`0eb384c5…` 确实共同绑定该证据版本，不能因原始 Git blob 的 LF hash 不同而判错。

DELIVERY-MANIFEST **8/8 项 bytes/hash 均匹配当前文件**；`head`、`generated_after_head` 回填为 `1ee761e7…`，`excluded_docs` 列 Task、Handoff、rework record、r2 Review。`created_at` 为提交前生成时点，`uncommitted=true` 描述当时的生成状态；b218 的提交主题说明后补 head。这里将 head 作为承载字节的回填锚点，不把该字段解释为清单在提交之后重新生成的独立证明。此为增量字节清单，非整个 FEA-10 历史文件全集；本报告不在被审清单中，不要求改写它来包含本 Review。

证据真实性：r4 主套件日志为 1056 passed/1 warning；providers 为 559 passed/4 skipped；dotnet build 为 0 warning/0 error，全量逐程序集通过数为 21+38+253+117+78+31+136+671=1345，skip 为 46+22+7=75，另有单独 IPC 1 passed，三阶段 EXIT 均为 0。与专项新增一个测试（52→53、主套件1055→1056）和既有 .NET 数量相符。未发现伪造结果的确证；这些日志没有证明本文新探针的安全断言成立。旧失败/不完整日志保留，不替换为本轮通过记录。providers 4 skip 与 .NET 75 skip 未逐项给原因，保留追溯限制。

## 回归及既有债务

- R-001：执行面过滤、合法 typeset 键及未知执行字段拒绝仍由本轮专项通过；R-002：三种 mapping binding 形状测试通过；R-003：untyped fallback 冻结错误码测试通过。
- R-004：默认本地 OCR typed 快照测试通过，Host 默认 binding 代码未在本增量改动，实际 C# 用例及 r4 .NET/IPC 日志相符；本轮没有冒称独立重跑 .NET。
- RR-01/FR-01 的非执行段过滤、普通嵌套认证拒绝仍保持，但安全总目标因 F3-01 继续不成立。RR-02/FR-02 已由当前 EV 修正闭合；RR-03/09 有本轮新增完整成功日志；RR-04 的 fallback 容器检查、RR-05 的本地 type/model 检查、RR-06/FR-04 的 Core null override 检查保持；RR-07 的历史 IPC 文件及 workspace 输出边界未改；RR-08/FR-08 的当前导航已更正。
- FR-03 的统一 fallback 冻结、FR-05 的 accepted settings 重新 freeze、FR-06 的合法词条保留、FR-07 的非法执行段拒绝，在本轮专项及本增量代码对照中保持。

| R-005…R-016 | 本轮可接受边界 |
|---|---|
| R-005 | 部分修复保持：支持的本地 typed adapter 有 type/model 身份检查；专项版本漂移主要由 mock 证明，真实模型运行/替换未验收。其余类型 fail-closed，不宣称生产模型全覆盖。 |
| R-006 | 仍为 P2：支持类型配置不完整的 StartRun 会提前 fail-closed；未见越权执行，兼容时点差异必须继续披露。 |
| R-007 | 仍为 P2：Core 持久 status 权威与 C# 查询投影结构成立；is_terminal 无生产消费者、原生 UI/C# 专项不足，不宣称 UI E2E 完成。 |
| R-008/R-009/R-010 | 已处理边界保持：IPC 输出 workspace、当前 EV/清单匹配、Owner 范围与 DSH 治理指针口径分开。不是对旧错误历史字节的重写。 |
| R-011 | 仍为 P2：Host 候选/attempt 缓存上限及清理代价未修。 |
| R-012 | 文档化差异保持：InMemory pause/cancel 不等价于生产 seam；本轮以 SQLite 故障注入作为拒写证据。 |
| R-013 | 仍为 P2：crash_restart 是恢复放弃、payload 可诊断及零提前写，不证明重启后 candidate 可继续提交。 |
| R-014 | 合法 token 词条误拒已解除；其衍生认证豁免漏洞仍为 F3-01，不能以 P2 债务接受。 |
| R-015 | 仍为 P2：source lease 异常归并 db_failed 降低诊断精度；seam 零 live 写成立，不等于 Windows 系统租约验收。 |
| R-016 | 仍为 P2：preview 异常统一 unavailable 降低诊断；接受与执行守卫另有验证。 |

上述 P2 限制可继续保留给 DSH 跟踪，不要求本 Review 扩大到其他 Task；最终债务接受及处置归 DSH，不能用它们豁免 F3-01。

## 逐项 AC 独立判断

| AC | 状态 | 依据与限制 |
|---|---|---|
| AC1 | MET（机制） | 本轮复跑 Prepare 零写/零执行、四元组独立 hash、stale/过期/缺失拒绝与 Accept 事务验证；安全输入面另在 AC2 判失败。 |
| AC2 | **NOT MET** | typed execution/digest、白名单与普通认证负例保持；F3-01 证明嵌套 translate 重启豁免后，认证值仍入 PreparedRun 和持久化两列。 |
| AC3 | MET（ADJ §2.1 限定） | 本轮 preview/实际 transport 共 builder、endpoint/model/body 同摘要、邻页 stale/接受后 pin 与 defaults/provider 漂移隔离测试通过；requires_upstream_output 不冒充未来正文预览。 |
| AC4 | MET（限定覆盖） | retry 同键/新键失败子集/source_run_id/接受时上下文与新 binding 冻结/旧 run 不变、凭据与版本阻塞恢复均通过。版本真实模型未测；显式 retry 作为现有确认边界，没有独立差异披露 UI 证据。 |
| AC5 | MET（seam 层） | 本轮 17 项故障/原子提交测试通过；live/revision/成功计数守卫、单事务成功及多 Region apply 保持。crash 为恢复放弃，lease/binding 为注入，不升级成系统级验收。 |
| AC6 | MET（Python/DB 与 C# 结构层） | 本轮4项控制/终态/重开库测试通过；控制请求不冒充持久状态。读 RunMonitor/RunStateStore，仅成功 Core 查询发布快照；原生 UI/专项 C# 行为限制仍在。 |
| AC7 | MET | 本轮 receipt 丢 ACK、过期/配置读取前重放、异 fingerprint、request_id 非键、两进程重开同库及 ControlRun restart 测试通过；真实 stdio 重启本轮核对既有 IPC 代码/日志。 |
| AC8 | MET（所覆盖链路） | 本轮 Python 生产 assembly Prepare→Accept→transport→commit 通过；r4 build/.NET/真实 IPC 日志完整，1345/0/75 与 IPC1保持。真实 IPC 测试主要覆盖 Prepare/Accept/重放，commit由Python生产assembly覆盖。本轮 .NET/真实IPC未重跑。 |
| AC9 | **PARTIAL** | 冻结17/17、契约/FEA-08/09证据/closeout/组合根零diff、增量写域及EV匹配；但本Review未approved，DSH最终集成与canonical/resource closeout未完成。 |
| AC10 | MET | 增量16文件均在允许写域，生产改动仅扫描及scrubber两文件；无新增依赖/Schema/未冻结wire、FEA-11/12/13/14实现或共享组合根改动。 |

## Verification：实际执行与 NOT_RUN

**Verification：指定检查通过，安全探针 FAIL；不足以批准。** 主审实际 shell 为 PowerShell，Python 为 `C:/Python314/python.exe`，无新 venv/依赖。TEMP/TMP 为上文 final3-review 唯一根，PYTHONDONTWRITEBYTECODE=1；测试自身的 workspace helper 另在同一 FEA-10/fixtures 父目录创建逐例唯一目录，全部为合成数据并原位保留。

| 场景 | 命令/步骤 | 结果 |
|---|---|---|
| 治理 | `pwsh -NoProfile -File tools/governance/check.ps1` | PASS，4 warnings，EXIT=0；仅机械验证 |
| 冻结 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 17/17 PASS，EXIT=0 |
| 专项 | `C:/Python314/python.exe -m pytest tests/fea10 -q -p no:cacheprovider` | **53 passed，0 skipped，4.17s，EXIT=0**；禁用cache避免仓库缓存写入 |
| 认证/词条/不可变 | stdin Python，10场景 | 旧4格拒绝、合法2格通过；新4格走私成功；进程EXIT=0、安全FAIL |
| `_redact` | stdin Python，4场景 | 合法根词条保留；旧错置token去除；两条嵌套translate路径仍错误保留 |
| EV/manifest | 二进制 git show + SHA-256 + 8项逐文件bytes/hash | PASS；完整值见上表 |
| 冻结/前置/组合根 | `git diff --name-only aa7bcd6161be5df07e2b8bf546600fec04af038f b218b52e -- doc/contracts <C-08/C-13/C-05/C-04b四文件> verification/FEA-08 verification/FEA-09 doc/tasks/FEA-08.md doc/tasks/FEA-09.md doc/handoffs/FEA-08-closeout.md doc/handoffs/FEA-09-closeout.md <App.axaml/App.axaml.cs/NewManga.App.csproj/NewManga.sln>` | 空；其他冻结承载由17/17 pins交叉核对 |
| 范围 | 增量name-only对Task allowed_paths，辅助审查交叉核对 | 16文件均允许；原始实现全范围与本轮增量不混为同一统计 |
| diff hygiene | `git diff --check e23b01a9 b218b52e` | 无输出，EXIT=0 |
| r4日志核对 | 四份 `verification/FEA-10/logs/dsh-rework4-*.log` | 完整头/EXIT；主套件1056、providers559/4、build0/0、.NET1345/0/75、IPC1；不冒称本轮执行 |

**NOT_RUN：**

- 本轮未重跑 .NET build/全量/真实 IPC；用户允许核对已有 r4 日志。全量可能重写 FEA-09 tracked 证据，本轮没有执行需要恢复证据的动作。
- 本轮未重跑 Python 全量 core/pipeline/providers；1056、559/4 为 r4 日志核对值，主审执行值仅为53专项及所列探针。
- 未做原生 UI 点击、Windows 系统级 source lease 故障、真实外网 provider/模型质量或模型替换验收；没有访问真实用户数据。
- 未对 RESOURCE-MANIFEST 全部历史 fixture 逐文件重算哈希/资源使用审计，也没有扫描/清理早期系统 TEMP。本轮新 fixture 及既有资源均原位保留，待 DSH 更新资源登记。
- r4日志缺少逐项skip原因，不臆测providers4项及.NET75项的具体跳过依据。未运行的场景不以日志汇总或散文改写成主审PASS。

治理事实：STATUS/Task为in_review，REBASELINE_PLAN仍有AC2/3/4/6待续作的旧措辞，rolling checkpoint为较早恢复点。仅在此记录，由DSH同步权威指针；主审不修改写域外文档，也不据旧措辞恢复实施。

## 新 head 与 closeout 条件

当前 **不能 closeout**。先修 F3-01，在新 head 上证明完整路径只能授予一次词条名豁免；至少覆盖两个旧形状和两个新形状×override/defaults，并验证PreparedRun、settings_snapshot_json、run_json均不含合成认证值，合法token词条继续保留且accepted snapshot不可变。同步扫描与scrubber，不只补本次字符串样例。

随后由DSH保存新head成功门禁/失败历史、更新EV commit+字节hash和manifest，派未参与该返修的全新上下文再次Review。仅当P0/P1=0且独立Review approved后，DSH才能执行集成验证、补integration_commit与Handoff/资源处置、使canonical_evidence_status/resource_closeout_status complete、同步Task/STATUS/Plan并复跑治理检查。资源保留可闭环，不因此获得删除授权。本报告不批准当前head，也不释放FEA-11。

### 推荐下一步（可直接转发）

- **Task/Agent：** FEA-10 同Task返修，推荐DSH处置并在现有冻结写域内实施；新Review另约未参与返修的Codex/ZCode上下文。
- **Recovery point：** `G:/CODEX/New Manga`，`main`，返修base/head均为`b218b52e0f9fe4827468826fe7fe6d3af322cc51`；无新worktree。
- **Scope/Deliverables：** 仅既有Task允许的扫描/scrubber、专项测试及FEA-10文档/证据；交付修复、针对性回归、新head、Handoff/EV/manifest。禁止冻结契约、Schema、依赖、组合根、FEA-08/09证据/closeout、真实用户数据改动及push。
- **Verification：** 独立fixture，TEMP/TMP=`G:/CODEX/New Manga.workspace/FEA-10/fixtures/<unique>/`；完整记录Python主套件/providers、.NET build/test、真实IPC、check/pins、范围/冻结零diff及本finding全矩阵；逐项披露skip/NOT_RUN。全绿后冻结新head，再派上下文独立Review，不提前done。

可转发指令：

> DSH：请在`G:/CODEX/New Manga`的main，以`b218b52e0f9fe4827468826fe7fe6d3af322cc51`为base/head，处置FEA-10-final-review-r3的F3-01（P1，F2-01未闭合）。先按生命周期登记返修，限现有Task写域修正_scan_auth_material/_redact的完整路径绑定；覆盖两个旧形状与两个嵌套translate新形状×override/defaults，负例不得进入PreparedRun或Run两列，合法token词条必须保留。不要修改冻结契约、Schema/依赖/组合根、FEA-08/09证据或真实用户数据，不push。用唯一workspace fixture和TEMP/TMP重跑Python主套件/providers、.NET build/test、真实IPC、check/pins及范围/冻结零diff，保存完整COMMAND/shell/环境/EXIT与skip原因，更新Handoff、EV commit/hash和manifest，固定新head后派未参与返修的全新上下文Review。当前不得closeout或释放FEA-11。

