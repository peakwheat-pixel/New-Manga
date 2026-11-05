---
task_id: FEA-12-PREREQ-1
reviewer: 独立上下文 fresh subagent（DSH 派发；未参与实现）
reviewer_kind: subagent
base_commit: 035468a81
reviewed_head: 5a7c7e028
decision: changes_requested
---

# Review：FEA-12-PREREQ-1（M2-C1 rev 2.13 删除/回收站 wire 注册 + Host 投影/白名单 + 负向对照）

**审查者身份与来源**：DSH 派发的独立上下文 fresh subagent（会话 id `68898595-4d2b-46a7-8a72-0d4b6ba05db8`；父会话 `session-8db9dae5-49df-4d09-ac62-696f0805a95c`）。未参与本卡任何实现、未参与 Handoff/证据生成。审查为**只读**：未 commit / push / stash / reset / checkout 他人改动；仅向仓外 `G:\CODEX\New Manga.workspace\FEA-12\review-prereq\` 写日志与本报告；未触碰真实用户数据/AppData/外部卷/真实回收站。

**并发写入声明（非本 Reviewer 所为）**：审查开始及我两次测试后即时检查（约 15:28/15:29）时工作树为 clean；此后（文件 mtime 15:28–15:33）出现**其他任务**的未提交写入：`src/application/maintenance/{__init__,recycle_gateway}.py`、`src/infrastructure/filesystem/simulated_recycle_bin.py`、`tests/fea12/**`（FEA-12-DSIM-1），以及 `src/application/{rendering,sources,tasks}/**`、`src/bootstrap/core_assembly.py`、`src/infrastructure/{providers,sqlite}/**`、`tests/fea11/**`（FEA-11-LINEAGE-1 r3），共 15 项（11 modified + 4 untracked）。本 Review 的验证以**已提交 HEAD `2fd395548`** 与 `--no-build` 已构建程序集为准，不受这些并发写入影响；我未创建/修改/暂存/提交其中任何文件。写域提示：这些是 Python/tests，与本卡 .NET 写域不相交；DSH 仍需按单写者规则确认无重叠。

**审查对象**：实现 commit `08b359251` + Handoff/最终 check 日志 commit `5a7c7e028`（交付 head），base `035468a81`。
**仓库实际 HEAD**：`2fd395548`（`docs(fea-12-core): 窄批补 HostRuntime/HostErrorCodes 到 allowed_paths`，1 file +2；在 reviewed_head 之后，属 Lead 对 `doc/tasks/FEA-12-CORE.md` 的窄批编辑，不在本 Review 范围；不影响下述结论）。
**实现实际父提交**：`c2b40c9f3`（base `035468a81` 之后 8 个其他任务 commit；`M2-C1` 在 `035468a81..c2b40c9f3` 零 diff，故 AC1 对 `035468a81` 的 diff 审计成立）。

## 结论

**decision: changes_requested（P1=1；P2=1；P3=4）**。实现整体方向正确：M2-C1 rev 2.13 是严格 additive（165 insertions / 2 授权既有行变更）、wire minor 11/13/既有 delete 10 正确、Host 投影/白名单/负向对照真实可复现、范围未越界、AC2–AC5 证据充分且可复核。**但 AC1 的 9 项登记点未全部完成**：`BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE` 缺 §5.11.3 表行，导致契约内部自相矛盾（`:849` 的"上表"排除该码 vs `:851` 的白名单声明包含该码），且与 C-04b §2.4 `:97`「§5.11.3 表 追加两行」及任务卡 Scope 3 不符。该 P1 为**单行 additive 修复**，修复后应可 approved。

| 级别 | 数量 | 摘要 |
|---|---|---|
| P0 | 0 | — |
| P1 | 1 | §5.11.3 表缺 `BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE` 行（R-001） |
| P2 | 1 | `CORE_CAPABILITY_MISSING` 未进 delete/trash 白名单（R-002，CORE 集成前置风险） |
| P3 | 4 | check 警告数 4 vs Handoff 3；§5.11.1a「拒收」措辞；B1/B2 负向对照注释过度声明；基线日志 `existing=l` 笔误 |

## 范围与依据

- 需求/AC：`doc/tasks/FEA-12-PREREQ-1.md`（status `in_review`，governance_version 3，allowed_paths 含 DSH 窄批 2 测试文件）AC1–AC5；Scope 1–9；DSH 裁决 5 项。
- 范围冻结：`doc/reviews/ADJ-2026-11-05-FEA-12-SCOPE.md`（D1–D8；D4 additive、D2 §11 对账、D6 写域）。
- 冻结来源：`doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md` §2.0–§2.4（`:99` 独立 Task + 负向对照）；`doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md` SC-B06（`:99-:129`）；`doc/plan/FEA-C14_SOURCE_RELOCATION_DRAFT.md` SC-S08（pending operation 披露）。
- 未审到：`2fd395548`（Lead 窄批，见上）；未跑全量 .NET 与全量 pytest（引用交付证据，理由见「验证」）；未做真实 Windows 回收站/真实数据验证（本卡禁止）。

## Standards（可选视角，executed 简版）

- 仓库记录标准：`AGENTS.md`（只读上下文、冻结契约字节、不碰真实数据）、`doc/09_COLLABORATION.md` §4 生命周期、`doc/WORKSPACE_GOVERNANCE.md`（产物入 workspace）。实现者遵守：`src/**` 零改动、18 pins 零改动、无新依赖/schema、证据与日志入 `verification/FEA-12-PREREQ-1/`、仓外 baseline worktree 保留。
- Fowler baseline：未发现值得报告的 smell；新增 Host 校验/投影为同文件内聚扩展，未引入重复实现（`ProjectDeleteTrashError` 与既有 `ProjectRunError` 同模式，属刻意对齐 C-08 先例）。

## Spec（可选视角，executed 简版）

- 来源要求但缺失/部分完成：**§5.11.3 表两行只落了 1 行**（R-001，P1）；其余 8 个登记点完整。
- diff 中来源未要求的行为：未发现 scope creep。`AllowedDeleteTrashErrorCodes` 把既有 delete 命令也纳入投影（`:117-120` 的 catch 以 `IsDeleteTrashCommand` 过滤）——这是契约新 §5.11.3 additive 句（`:851`）要求的投影语义，非越权；既有 delete 命令的 wire minor/映射零改动。
- 看似实现但有误：无。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| R-001 | **P1** | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:829-851`（§5.11.3 表） | 任务卡 Scope 3 与 C-04b §2.4 `:97` 要求 §5.11.3 表为 2 个新码各追加 1 行；实际只追加了 `INVALID_REQUEST`（`:846`）与 `BOOK_DELETE_STALE_PREVIEW`（`:847`），**缺 `BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE` 行**。`:849` 仍写「每个 `item.error_code` 只接受**上表**列出的稳定码」，而 `:851` 新句声明 items 白名单包含该码；该码只出现在 §5.13 预览表 `:965` 与两个 ErrorView `:874/:884`，不在 §5.11.3 表。CORE 按 `:849` 实现会把该码排除出 batch items 白名单，按 `:851` 则包含——冻结契约出现二义。 | `git diff 035468a81..08b359251` hunk `@@ -803,9 +843,13 @@` 仅 2 个 `+` 表行；`Select-String` 在 head 仅命中 `:28/:851/:874/:884/:965`（无 §5.11.3 表行）；base `035468a81` 对该码零命中；C-04b `doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md:97` 原文「§5.11.3 表 \| 追加两行（本草案 §2.3）」；任务卡 `doc/tasks/FEA-12-PREREQ-1.md:59`「§5.11.3 表两行」。 | 在 §5.11.3 表 `:847` 后 additive 追加一行（category/retryable 用 C-04b §2.3 冻结值）：`\| 删除/预检的清单计算失败（DB 错/临时故障；§5.11.1a/§5.13） \| \`BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE\` / \`unavailable\` / \`retryable=true\` \| 零失败副作用；可显式重试；不得降级软删。 \|`。同时给 `rev213-diff-audit.ps1` 增补「§5.11.3 表 code 集合 ⊇ 两个 ErrorView code 集合」的断言（判别性：在 `5a7c7e028` 上必失败，修复后必通过）。 | open |
| R-002 | P2 | `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs:49-66`；契约 `:969`/`:1022` | 契约把 capability 缺失错误声明为 `CORE_CAPABILITY_MISSING`（`protocol`/`false`），但 `AllowedDeleteTrashErrorCodes`（20 码）不含该码；`HostCommandDispatcher:117-120` 的 catch 对 `IsDeleteTrashCommand` 一律走 `ProjectDeleteTrashError`，未注册码会降级 `category=unknown`。本卡 DSH 裁决明确运行时 probe 归 CORE，故当前无运行时缺陷；但 CORE 接线时若 probe 错误经该 dispatcher 投影，会把契约声明的错误降级。 | 白名单逐项计数 20（15 既有 + 5 新），无 `CORE_CAPABILITY_MISSING`；契约 `:969`/`:1022` 原文；`HostCommandRegistry.cs:49-66`。 | 在 FEA-12-CORE 的 release note / 判别性测试中明确二选一：(a) CORE 把 `CORE_CAPABILITY_MISSING` additive 加入白名单并加投影测试；或 (b) probe 错误在 HostRuntime 层抛出、不经过 `ProjectDeleteTrashError`，并加测试证明该错误保留 `protocol`/`false`。本卡只需在 Handoff「风险」中登记。 | open（defer CORE） |
| R-003 | P3 | `doc/handoffs/FEA-12-PREREQ-1-035468a81.md:43`；`logs/check-final.log` | Handoff 记「check PASS（3 warnings）」；当前独立复跑为 **PASS（4 warnings）**，第 4 条是 `logs/check-final.log` 自身（检查时文件尚不存在，提交后自指）。不影响 EXIT 0/门禁结论，但交付数字与现状不一致。 | 独立复跑 `check.ps1 -TaskPath doc/tasks/FEA-12-PREREQ-1.md`：EXIT 0，4 warnings（含 `logs/check-final.log` 未登记）。 | DONE 前把 `logs/check-final.log` 归入 workspace 或列为 SOURCE_PIN（Handoff 风险 2 已列），并在 closeout 记录警告数变化。 | open（closeout 处置） |
| R-004 | P3 | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:809`（§5.11.1a） | 新句「单条命令继续**拒收** `book_ids`/`confirmed_book_ids`/`confirm_count`/`inventory_digests`（closed shape 不变）」在 Core wire 层成立；但 Host 既有 delete 路径不调用 `RejectUnknownKeys`，对未知键是**丢弃**而非拒绝（`HostCommandDispatcher.cs:458-473`）。措辞可能让 CORE/UI 误以为 Host 会拒绝。 | 读 `HostCommandDispatcher.cs:458-473`（既有单删仅取已知键）；B1 测试只覆盖 `inventory_digest` 类型错，不覆盖 `inventory_digests` 被丢弃。 | 措辞改为「Core closed shape 继续拒收…；Host 既有 delete 路径保持 legacy 透传（不新增未知键拒绝）」；或补一条 Host 单删 `inventory_digests` 的判别性测试并明确期望（拒绝或忽略）。 | open |
| R-005 | P3 | `apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CommandWiringB1Tests.cs:370-373`（及 B2 对应段） | 注释称重建的「pre-registration allow-list」是「exactly what the Host projected BEFORE M2-C1 rev 2.13 was registered」；实际 base 对 delete 族**没有白名单投影**（Core 错误原样透传），该集合是用新投影器减 5 码重建的。基线负向对照的真实机制是 A2 用既有 `ProjectRunError`/19 码 run 白名单演示降级（`baseline-negative-control-base-035468a81.log:25-31`），`REGISTRATION-COMPARISON.md:38` 已如实写明「改动前 delete/trash 白名单不存在」。 | 读 B1/B2 注释与 `baseline-negative-control-base-035468a81.log:25-31`；`REGISTRATION-COMPARISON.md:38`。 | 注释改为「reconstructed pre-registration allow-list (the new projector minus the 5 rev 2.13 codes)」；AC3 结论不变（基线脚本 + 旧 Core 实测均真实）。 | open |
| R-006 | P3 | `verification/FEA-12-PREREQ-1/logs/baseline-negative-control-base-035468a81.log:22` | `existing=l library_delete_book_permanently` 笔误（应为 `existing=single`），纯日志可读性。 | 该行原文。 | 重生成日志或 closeout 时注明；不影响判别力。 | open（cosmetic） |

## 验证

所有独立复跑均在主工作树 `G:\CODEX\New Manga`（HEAD `2fd395548`，工作树 clean）执行；日志在仓外 `G:\CODEX\New Manga.workspace\FEA-12\review-prereq\`。

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | HEAD `2fd395548`（仅 FEA-12-CORE.md 文档 diff，不影响 pins） | **PASS 18/18，EXIT 0** | `r1-gates.log` |
| 治理 check | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-PREREQ-1.md` | 同上 | **PASS（4 warnings），EXIT 0**（见 R-003） | `r1-gates.log` |
| 命令治理测试 | `dotnet test apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/NewManga.CoreClient.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~Command"` | HEAD；.NET 9 | **135 passed / 0 failed / 15 skipped，EXIT 0，15s** | `r1-dotnet-command-filter.log` |
| 旧 Core 负向对照（sidecar） | 同 csproj，filter `Fea12NewCommands\|B1Commands_ExecuteAgainstFrozenCore\|B2Commands_ExecuteAgainstFrozenCore`；`NEWMANGA_CORECLIENT_SIDECAR_DIR=...\HOST-CORECLIENT-1\sidecar-copy`，`NEWMANGA_EVIDENCE_DIR` 指向仓外 | 冻结 Core（2026-10-23 副本） | **3/3 passed，EXIT 0，9.4s**；独立生成的 `fea12-old-core-negative-control.json` 与仓内 EV-08 **byte-identical** | `r1-dotnet-sidecar-negative.log`；`evidence/commands/fea12-old-core-negative-control.json` |
| 基线负向对照 | `pwsh -NoProfile -File verification/FEA-12-PREREQ-1/tools/baseline-negative-control.ps1 -RepoRoot <baseline-worktree> -AssemblyPath <worktree dll>` | 仓外 worktree detached `035468a81`；assembly sha256 `056fbb2e…` 与交付日志一致 | **CAPTURED，EXIT 0**：registry 106；5 新命令 absent + `UNKNOWN_COMMAND`；5 新码 `category=unknown` 且 code 原样；旧 Core 对 Preview(2.11)/MoveToTrash(2.13) → typed `UNKNOWN_COMMAND` | `r1-baseline-negative-control.log` |
| M2-C1 additive | `git diff --numstat 035468a81..08b359251 -- <contract>` + `-U0` hunk/removed 行审计 | base `035468a81` | **165 insertions / 2 deletions**；removed 仅状态行（2.12→2.13）与 §11 policy 行；其余全 `+` | `rev213-diff-audit.log` 复核一致 |
| 范围 | `git diff --name-status 08b359251^..5a7c7e028` | 实现实际父 `c2b40c9f3` | **43 files，全部在 allowed_paths 内**（3 src + 6 tests 含 2 窄批 + M2-C1 + Task + Handoff + verification/**） | 见「范围与冻结核对」 |
| 冻结契约 | `git diff --name-status 035468a81..5a7c7e028 -- doc/contracts/{C-01b,C-04b,C-08,C-09,C-13,C-14,C-17,ADJ-001}*` | base..head | **零 diff**（仅 M2-C1 变） | 命令输出 |
| Canonical Evidence | 逐文件 `Get-FileHash -Algorithm SHA256` 对照任务卡 EV-01…EV-14 | HEAD | **14/14 OK**（sha256 全部匹配） | 本报告「AC5」 |
| 全量 .NET / pytest | 引用交付日志，未重跑 | 交付 head | .NET 首跑 1 failed（App.Tests flaky）→ 复跑 **1403/0/79**；pytest **3073/10** | `logs/dotnet-full-1.log`/`dotnet-full-2.log`/`pytest-full.log`（EV-04/EV-12） |

**未跑项与理由**：全量 .NET 与全量 pytest 未独立重跑（全量 .NET 约 3 分钟/程序集且会重写 `verification/FEA-09`，本卡无 Python 改动；已用交付日志 + 独立过滤测试 + sidecar 负向 3/3 交叉验证）；真实 Windows 回收站/真实数据按卡禁止，NOT_RUN 属预期。**未把 flaky 写成稳定 PASS**：`dotnet-full-1.log` 的 1 failed 与 `dotnet-full-2.log` 的 1403/0/79 分列记录，flaky 归因为 `FluentResidual2VisualEvidenceTests`（断言 `git status --porcelain -- verification` 前后不变）与 `WireLogSourceRedactionTests`（重写 tracked `verification/FEA-09/logs/wire-redacted.ndjson`）的跨程序集写竞争，属既有测试债务（两测试均非本卡改动）；我运行过滤测试后 `git status` 仍 clean，未触发 FEA-09 重写。

## AC1–AC5 判定

| AC | 判定 | 依据 |
|---|---|---|
| AC1 M2-C1 rev 2.13 additive 文本 | **PARTIAL（P1-1）** | additive 形态成立（165/2；仅 2 处授权既有行）；9 项登记点 **8/9 完整**：preview/`DeletePreviewItem` PD-01 三项 ✓（§5.13）、digest 单/批量字段 + 两级校验 ✓（§5.11.1a）、2 删除码**四处同步仅 3.5 处**（两 ErrorView ✓、items 白名单句 ✓、§5.11.3 表缺 PROTECTION 行 ✗）、回收站 4 命令 + 3 TRASH 码 ✓（§5.14）、capability 3 名 ✓、§11 对账 ✓（P09 `:84/87/106-109` 已核）、§12 release boundary ✓、revision history ✓；未加 C-14 pending-operation 字段 ✓；`PROTOCOL_MINOR=3` 未改 ✓；既有 delete wire minor 10 未改 ✓。 |
| AC2 Host 投影 additive | **MET** | registry 5 命令（preview 11 / trash 13）+ `DeleteTrashCommandNames` + 3 capability + `RequiredCapabilities` + 20 码白名单 + `Fea12DeleteTrashErrorCodes` + `IsDeleteTrashCommand`；dispatcher 新命令严格 closed-shape（未知键拒绝、`bookIds` 1..20 去重、`TrashEntryRef` 恰 `{book_id}`、`PurgeTrash confirm:true`）+ 既有 delete 仅 additive digest 透传 + `ProjectDeleteTrashError`；CoreServiceClient 仅追加常量类；独立复跑 135/0/15。 |
| AC3 负向对照 | **MET** | 基线脚本独立复现三条结论（5 码→unknown 且 code 保留；旧 Core Preview/MoveToTrash→typed `UNKNOWN_COMMAND`；旧 Core 对 delete+digest→`INVALID_REQUEST`）；sidecar 3/3 独立复跑，证据 JSON 与 EV-08 byte-identical。机制说明见 R-005（P3，不影响结论）。 |
| AC4 治理门禁 | **MET** | pins 18/18、check PASS 独立复跑；全量 .NET 首跑 1 flaky 已如实分列、复跑 1403/0/79；pytest 3073/10；命令治理 135/0/15；live 负向 3/3。警告数 4 vs 3 见 R-003。 |
| AC5 交付件 | **MET** | Task/Handoff/`verification/FEA-12-PREREQ-1/**` 齐备；EV-01…EV-14 sha256 14/14 匹配；无「未跑冒充实测」；`agent-output-manifest.json` 11 files 与 Canonical Evidence 一致。本 Review 报告按审查指令写在仓外，未提交进 `doc/reviews/`（DSH 可决定是否入库）。 |

## 范围与冻结核对

- **实现实际 delta**（`08b359251^..5a7c7e028`，43 files，+2704/−25）：3 个 `NewManga.CoreClient` 源文件、6 个 CoreClient 测试文件（含 DSH 窄批 `DraftCommandRegistryTests`/`CommandContractV11RTests`）、`doc/contracts/M2-C1`、`doc/tasks/FEA-12-PREREQ-1.md`、`doc/handoffs/FEA-12-PREREQ-1-*`、`verification/FEA-12-PREREQ-1/**` —— **全部在 allowed_paths 内**，无 `src/**`、无 schema/migration/依赖、无其他契约。
- **`035468a81..5a7c7e028` 的越界观感**：该范围含 8 个其他任务 commit（FEA-11-LINEAGE-1 r2、FEA-11-HOST-AUTH-1 closeout、`86bc87e1e` scope 冻结/建卡等），因此出现 `doc/STATUS.md`/`REBASELINE_PLAN.md`/`TASK_LEDGER.md`/`ADJ`/`FEA-12-CORE.md`/`FEA-12-DSIM-1.md`/`src/**`/`verification/FEA-11/**` 等文件；**这些不是本卡 delta**，应归各来源 commit（`git log --graph` 已核）。本卡实际父提交为 `c2b40c9f3`，建议后续卡片把 `base_commit` 与「实际 diff 父」分开记录，避免范围审计误读（非 finding）。
- **Lead 窄批**：`2fd395548` 对 `doc/tasks/FEA-12-CORE.md` +2 行（HostRuntime.cs/HostErrorCodes.cs），在 reviewed_head 之后，属 Lead 编辑，不影响本卡。
- **冻结契约零 diff**：C-01b/C-04b/C-08/C-09/C-13/C-14/C-17/ADJ-001 在 `035468a81..5a7c7e028` 零 diff；`verify_pins.ps1` 18/18。
- **窄批 2 测试文件**：`DraftCommandRegistryTests` 硬编码 `40` → `expected.Count` 派生 + 并集追加 `DeleteTrashCommandNames`；`CommandContractV11RTests` declared 集合追加 `DeleteTrashCommandNames`，`undeclared.Length == 0` 严格断言保留。**与 DSH 2026-11-05 窄批条件逐字一致**，无 skip、无删除测试、未放宽 set equality。唯一治理含义：硬编码总数守卫被派生替换（DSH 明确批准；`CommandParityContractTests` 的 frozen-66 快照断言仍在），若 DSH 仍想保留「冻结总数」门，需另加断言（非本卡 finding）。

## 负向对照复核（独立）

1. **基线（改动前 head `035468a81`）**：独立重跑 `baseline-negative-control.ps1`（assembly sha256 `056fbb2e…` 与交付日志一致），EXIT 0 / `CAPTURED`：
   - registry 106，5 个新命令 absent，`Get()` → `HostCommandUnknownException` / `UNKNOWN_COMMAND`；
   - 5 个新码在既有 run 白名单投影下 `registered=False` / `category=unknown` / `retryable=False` / code 原样（`:25-31`）；
   - 旧 Core：Preview(2.11)、MoveToTrash(2.13) → typed `UNKNOWN_COMMAND`（`result=null`，无静默丢弃）。
2. **sidecar live 旧 Core（改动后 Host）**：独立重跑 3/3；4 个新命令 → `UNKNOWN_COMMAND`（`validation`/`false`），既有 `PermanentlyDeleteBook`(10)+`inventory_digest` → `INVALID_REQUEST`；生成 JSON 与仓内 EV-08 **byte-identical**。
3. **机制说明（R-005）**：基线 A2 用的是既有 `ProjectRunError`/19 码 run 白名单（base 没有 delete 白名单，`REGISTRATION-COMPARISON.md:38` 已如实记录「改动前 Core 错误透传、未注册 code 不降级」）；B1/B2 的「pre-registration allow-list」是「新投影器减 5 码」的重建。结论（未注册码降级 unknown 且 code 保留、旧 Core fail-closed）成立，但注释措辞应修正，避免把机制演示误读为 base 的真实 delete 路径行为。

## limitation / 风险

1. **P1-1 未修前不可批准**：契约 §5.11.3 表的二义会被 FEA-12-CORE 直接消费（batch items 白名单/Tauri 投影），修复成本一行，建议立即返修。
2. **R-002（CORE 集成风险）**：`CORE_CAPABILITY_MISSING` 不在 delete/trash 白名单；CORE 接 probe 时必须显式处理（加入白名单或绕开 `ProjectDeleteTrashError`），否则契约声明的错误会被降级 `unknown`。
3. **未独立重跑全量 .NET/pytest**：引用交付日志；已用过滤测试（135/0/15）+ sidecar 负向 3/3 + 基线脚本独立复现交叉验证。全量 .NET 首跑 flaky 属既有债务（`FluentResidual2VisualEvidenceTests` × `WireLogSourceRedactionTests`），交付者已如实分列「首跑 1 failed / 复跑 1403/0/79」，未冒充实测。
4. **`PurgeTrash` 首版不实现**：契约已按 C-09 原字节登记并明确「委托 C-04b、不是新删除路径」；digest 绑定方式待 DSH additive 裁决——CORE 不得擅自实现。
5. **C-14 SC-S08 pending-operation**：本卡未加 `DeletePreviewItem` 字段，符合卡要求；后续 UNFREEZE 时需 DSH 单独裁决。
6. **本 Review 报告在仓外**：按审查指令只读仓库；DSH 若需入库，可把本文件复制到 `doc/reviews/FEA-12-PREREQ-1-r1.md`（allowed_paths 已含该模式）。
7. **基线 worktree 保留**：`G:\CODEX\New Manga.workspace\task-envs\FEA-12-PREREQ-1\baseline-worktree-035468a81` 仍 clean、detached `035468a81`；我只读复用，未删除/改动（PRESERVE_REFERENCED）。
8. **审查期间工作树被其他任务并发写入**：约 15:28–15:33 起出现 FEA-11-LINEAGE-1 r3 / FEA-12-DSIM-1 的未提交 Python/tests 写入（见上「并发写入声明」），非本 Reviewer 所为；本卡 3 个 .NET 文件与 6 个测试文件未被并发修改。若 DSH 在同一工作树继续本卡 P1 返修，应按单写者规则与 LINEAGE-1 r3/DSIM-1 协调；返修只应触及 `doc/contracts/M2-C1` 与 `verification/FEA-12-PREREQ-1/tools/rev213-diff-audit.ps1`（均在 allowed_paths/证据目录内）。

## done vs changes 意见

- **changes_requested**：仅因 R-001（P1）。最小返修：
  1. `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` §5.11.3 表追加 `BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE` / `unavailable` / `retryable=true` 一行（保持 additive，不动既有行）；
  2. `verification/FEA-12-PREREQ-1/tools/rev213-diff-audit.ps1` 增加「§5.11.3 表 code 集合 ⊇ 两个 ErrorView code 集合（至少含 5 个新码）」断言，并在 `gates.log`/AC-MATRIX 重跑记录；判别性：在 `5a7c7e028` 上该断言必失败，修复后必通过；
  3. 顺手修 R-003/R-004/R-005 的措辞/日志（P3，可与 P1 同批），R-002 在 Handoff「风险」登记给 CORE。
- 修复后新 head 重新进入 `in_review`；本 Review 只对 `5a7c7e028` 有效，新 head 不自动延用。R-001 修复后，其余 AC2–AC5 结论可延用（除非新 head 触及实现）。
- 不建议在本卡内做 `PurgeTrash` digest 绑定、capability probe 接线或 C-14 pending 字段——均属后续 additive 裁决/CORE 范围。

## 自审声明

- 我是 DSH 派发的独立上下文 fresh subagent（会话 id `68898595-4d2b-46a7-8a72-0d4b6ba05db8`），**未参与** FEA-12-PREREQ-1 的实现、Handoff 或证据生成。
- 审查全程只读仓库：未 commit、未 push、未 stash/reset/checkout 他人改动；未修改任何仓库文件；运行 `dotnet test` 后 `git status` 仍 clean（未触发 `verification/FEA-09` 重写，故无需恢复）；日志与报告仅写仓外 `G:\CODEX\New Manga.workspace\FEA-12\review-prereq\`。
- 未触碰真实用户数据/AppData/外部卷/真实回收站；sidecar 测试使用系统临时数据根（`SidecarFixture` 自清理），基线脚本使用 workspace temp 隔离根。
- 事实以 Git/文件/测试为准；未采信聊天记录或旧数字。报告中的「交付证据」均标注为引用（EV/日志），独立复跑结果单列。
