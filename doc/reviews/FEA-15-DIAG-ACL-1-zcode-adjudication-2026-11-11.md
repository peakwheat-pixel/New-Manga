---
task_id: FEA-15-DIAG-ACL-1
adjudicator: ZCode 独立 CLI 会话（本轮用户单次授权：治理审查/裁决与下一 Task 范围冻结）
adjudicator_kind: agent
reviewed_head: 1e58398aa07467004c1b329bb52095f63bcb78d4
delivery_head_under_review: 610839af8348f8b1f36e18a623e9fc40882051b5
independent_review: doc/reviews/FEA-15-DIAG-ACL-1-r1.md（Codex Reviewer subagent `/root/fea15_diag_acl_review`，reviewed 610839af8）
base_commit: 1e4542a047e991a5f10b0b213ca5a96eafe919a4
date: 2026-11-11
decision_A_diag_terminal: 确认 closed_with_limitations（AC1–AC3 PARTIAL / AC4–AC5 MET 维持原判）
decision_B_pin_eol_gov_1: 释放（proposed → ready，范围冻结为只读治理盘点）
---

# ZCode 独立裁决：FEA-15-DIAG-ACL-1 终态复核 与 FEA-15-PIN-EOL-GOV-1 释放

## 0. 复核时点与环境

- 复核开始 HEAD = `1e58398aa07467004c1b329bb52095f63bcb78d4`（main），`git status --porcelain` 无输出，工作树干净。
- 派发方观察 HEAD 与实测一致。用户提供的旧基线 `164ebabcfa90b92fc46c07238280960fc01f7423` 为 FEA-15-ACCEPT-1 的执行 base_commit，当前 HEAD 是其后续提交：仅报告，未 reset/merge。
- 本裁决只读复核 + 治理指针更新；未改生产代码/测试/依赖/Schema/冻结契约；未重跑产品测试大套件；未 push。
- 独立性声明：本会话未参与 DIAG-ACL-1 的实现、返修或 r1 Review；对 r1 报告、证据与终态 pin 提交链从零评估。

## 1. 对独立 Review r1 与交付链的独立评估

### 1.1 pin 机械复算（本会话独立执行）

对 Task 卡 Canonical Evidence 表全部 18 条（EV-01..05、SRC-01..13）逐条三项核对：

1. 所列 commit 是否包含对应路径（`git cat-file -e <commit>:<path>`）；
2. 当前工作树文件 SHA-256 是否等于登记值；
3. 登记值等于该 commit 的 blob SHA-256（BLOB 基准）还是仅等于工作区字节（WORKTREE 基准），仅作记录。

结果：**18/18 PASS**（包含性 ✓、工作树 SHA ✓）；其中 7 条 BLOB 基准（EV-01、SRC-01/06/09/11/12/13），**11 条 WORKTREE 基准**（EV-02..05、SRC-02..05/07/08/10）——与 r1 §Verification 记录的行尾差异集合逐条吻合。

### 1.2 交付链 diff 范围（`git diff --name-status`）

- `base 1e4542a04 → delivery_head 610839af8`：12 个文件，全部 ⊆ allowed_paths（本卡、reviews/handoffs 通配、verification/FEA-15-DIAG-ACL-1/**、STATUS/PLAN/LEDGER）。
- `delivery_head 610839af8 → HEAD 1e58398aa`（5 个 docs 提交：dea98ce8f、49a40cd46、05b220848、4ddb3cbd7、1e58398aa）：11 个文件，全部 ⊆ allowed_paths。
- 两段均无 src/、apps/、tests/ 变更，与 r1 Architecture 结论一致。

### 1.3 r1 引用源码位置抽查（本会话独立核实）

- `src/infrastructure/plugins/service.py:346–378`：`_invoke_sandboxed` 调用链、`SandboxError` 双映射（output-exceeded→`PLUGIN_HOOK_FAILED` @376、其余→`PLUGIN_HOOK_UNAVAILABLE` @378）——与 README/r1 描述一致。
- `src/infrastructure/plugins/sandbox.py`：`CreateAppContainerProfile` @257、`_grant` 经 `icacls <path> /grant *<sid>:<rights>` @276–288、`close()` @564–565 仅置 `_closed=True`（不撤销 ACL/不删 profile）——与 README「close() 只关闭对象状态」一致。
- `src/infrastructure/sqlite/schema.py:928–932`：`v12__chapters_custom_rank`（`ALTER TABLE chapters ADD COLUMN custom_rank INTEGER;`）——支持 v7 测试构造债结论。
- `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceSecurity.cs:61–83`：`PrivateDirectory` = 拒绝重解析祖先 → 建目录 → SetOwner + `SetAccessRuleProtection(true,false)` 受保护 DACL + 当前 SID FullControl → `SetAccessControl` → 读回验证——与 README 失败链描述一致。

### 1.4 终态门禁日志自洽性

`gates-terminal.log` 两段：候选树（dea98ce8f，5 modified+1 untracked 状态下 default/TaskPath PASS EXIT 0、18 pins PASS）与 pin 回填后干净树（05b220848，`git_status_porcelain_before_run=empty`，default PASS 3 warnings、TaskPath PASS 5 warnings、pins 18/18，均 EXIT 0）。命令、HEAD、时点、EXIT 记录自洽；Closeout 第 88 行与之一致。本会话未采信日志为唯一证明，另在当前 HEAD 独立复跑（§4）。

### 1.5 r1 报告质量评估

r1 的核对方法（三方哈希、`gates-review.log` HEAD 边界澄清、venv 非完整独立对照的限定、`acl-probe.log` 不可提升证明力）边界意识准确；三条非阻断收口提醒（指针统一、`PLUGIN_HOOK_FAILED` 例外补全、探针脚本缺失披露）均已在终态文档落实或如实披露。**接受 r1 的 approved 结论及其边界。**

## 2. AC 逐项独立判断

| AC | 卡面 | 本裁决 | 独立依据 |
|---|---|---|---|
| AC1 sandbox/export | `[ ]` `<<PARTIAL>>` | **维持 PARTIAL** | 跨主树/clean-tree/venv 失败复现（3515/16/12、4/15、6/10，EXIT 1 均留证）；调用链已记录；失败阶段与原始 Win32 错误未定位，README 未过度归因。 |
| AC2 Host ACL | `[ ]` `<<PARTIAL>>` | **维持 PARTIAL** | 堆栈定位 `SetSecurityInfo`/`SourceSecurity.PrivateDirectory`；卷能力观察（NTFS/持久 ACL）排除简单格式归因；精确原方法探针 NOT_RUN 未被冒充。 |
| AC3 资源影响 | `[ ]` `<<PARTIAL>>` | **维持 PARTIAL** | ACE 48/24 行为运行后快照、无前置快照，归属不可判定；`PRESERVE_UNKNOWN` 处置与 resource-manifest（6 项资源、删除/迁移/归档=0）一致。 |
| AC4 fixture | `[x]` `<<MET>>` | **维持 MET** | 62 项时间窗候选逐行可数，建议与实际处置（原位保留、零清理）一致。 |
| AC5 建议与交付 | `[x]` `<<MET>>` | **维持 MET** | 矩阵/v7 债/NOT_RUN/建议留证；r1 独立 Review approved（P0/P1=0）；r1 评 AC5 PARTIAL 的唯一理由（终态门禁未跑）已由 gates-terminal.log final run 闭合。 |

v3 标记组合全部合规（`[ ]`+PARTIAL 带原因、`[x]`+MET 无原因）。

## 3. 裁决 A：确认 closed_with_limitations

**阶段结论：确认（confirmed），不修订、不退回 Review、不重新开放。**

- 终态语义符合 §4：`closed_with_limitations` 为终态但不等于技术完成或可发布；AC1–AC3 的 PARTIAL 与全部 NOT_RUN 保持原始状态，无一处改写为 PASS；节点不进入 READY DAG（PLAN 第 52 行保留为历史行）。
- 授权链自洽：ZCode 2026-11-11 冻结释放（approval 字段）→ Codex 只读执行（base 1e4542a04）→ 独立上下文 subagent Review approved（reviewed 610839af8）→ Codex primary Agent 按 ACCEPT-1 最终裁决（ZCode `sess_2a802094`）预设路径签发阶段结论 → pin 回填与终态门禁（05b220848 干净树三件套 PASS）→ 本轮 ZCode 独立 CLI adjudication 确认。appointment.md 记录了 ZCode CLI 首选因执行审批挂起改派 subagent 的原因；本裁决补上了独立于作者的阶段裁决视角，治理链闭合。
- `canonical_evidence_status: complete` 与 `resource_closeout_status: complete`（0 删除/迁移/归档）成立；`integration_commit: null` 合理（无生产实现集成）。
- 遗留限制（精确 Host ACL 拒绝条件、sandbox 失败阶段、ACE/profile 归属）保持开放，恢复条件已由 README 记载；62 fixture 候选 `PRESERVE_UNKNOWN` 原位保留，不得从本诊断推导任何清理授权。

## 4. 裁决 B：释放 FEA-15-PIN-EOL-GOV-1（proposed → ready）

### 4.1 释放的事实基础（本会话独立核对）

1. 根本限制真实且多源记录：FEA-15-ACCEPT-1 r1 P2-1（blob 口径 26/29 不匹配）、r2 P3-A（含 SRC-25 后 **30 条中 27 条**）、r27 历史（300 pin 中 187 条工作区口径）、本 Task 新增 18 条中 11 条 WORKTREE 基准（§1.1 实测）。当前全集必须重新盘点，不得以历史数推断。
2. 根因已定位：仓库根 `.gitattributes` 对 `verification/FEA-15-*/**` 无 eol 规则；`core.autocrlf=true` 来自**系统级**配置（`C:/Program Files/Git/etc/gitconfig`；仓库级/全局未设置）。仓库已有三组 eol=lf pin 先例（SEC-FIX-PATH-ECHO-1、P19-UI-MANIFEST-VIEW-1、GOV-EOL-PIN-1/FEA-08 blob/LF 口径）。
3. `tools/governance/check.ps1` r194 条款现行接受 worktree/blob 双基准 → 该语义属 §4.4「语义改动核验前置」适用面：任何口径/规则裁定前必须先完成受影响全集盘点与基线矩阵实测。
4. 跨 checkout 复现性缺口（Linux fresh clone / autocrlf=false 下工作区口径 pin 全部无法复现）不影响本机当前门禁（verify_pins 18/18 PASS、check PASS），属真实但不紧急的治理债——适合只读盘点先行。

### 4.2 范围冻结（release 参数）

- **status**: `ready`；**kind**: governance（只读盘点/观察/分析阶段）。
- **Owner**: `codex`（suggested_owner 不变；认领时实测 base 并登记）。
- **Reviewer**: 认领进入 in_review 前按 §6 上下文独立指定（候选：ZCode 独立会话或 DSH 派发独立上下文 subagent；不得为 Owner 同一会话）。
- **base_commit**: `1e58398aa07467004c1b329bb52095f63bcb78d4`；**branch**: `main`；**worktree**: `G:/CODEX/New Manga`（主树串行，治理文档 Task，先例=DIAG-ACL-1）。
- **evidence_dir**: `verification/FEA-15-PIN-EOL-GOV-1`（已列入 allowed_paths）。
- **allowed_paths**: 本卡、`doc/reviews/FEA-15-PIN-EOL-GOV-1-*.md`、`doc/handoffs/FEA-15-PIN-EOL-GOV-1-*.md`、`verification/FEA-15-PIN-EOL-GOV-1/**`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`。
- **本 Task 只允许**：当前全集盘点（AC1）、跨 checkout 观察矩阵（AC2）、基线证据与候选口径/迁移策略分析（AC3）。
- **禁止**：修改 `.gitattributes`、checker/verify_pins/task_ledger 检查语义、任何历史证据或 pin、冻结契约与 FROZEN 记录（含 C-07）、源代码、Schema、依赖；push；清理任何资源。`.gitattributes`/renormalize/历史 pin 处置的实施必须另开 Task 并经独立授权与 Review（§4.4：盘点未完成不得改 `.gitattributes`）。
- **AC 状态规则**：governance_version 3；进入 in_review 前每 AC 带合法标记；PENDING 不得写成 MET；不可判定项如实登记。
- **Gate**：`pwsh -NoProfile -File tools/governance/check.ps1`（default）与 `-TaskPath doc/tasks/FEA-15-PIN-EOL-GOV-1.md` PASS；`verify_pins.ps1` 18/18；`python tools/generate_api_inventory.py --check` OK。观察命令（`git ls-files --eol`、`git cat-file blob | sha256sum`、隔离 checkout 复算等）逐次记录命令/HEAD/时点/EXIT；NOT_RUN 记录于 `verification/FEA-15-PIN-EOL-GOV-1/README.md`。
- **资源**：跨 checkout 观察所需二次 clone/隔离环境放 `G:/CODEX/New Manga.workspace/FEA-15-PIN-EOL-GOV-1/`，创建前确认不存在；不覆盖既有资源；不污染主树。

### 4.3 释放理由

候选卡已登记 proposed 且 DAG/依赖齐备（依赖 FEA-15-ACCEPT-1 已终态；DIAG-ACL-1 同链收口）；§4.4 硬前置（先盘点后裁定）与用户本轮授权（只读/治理阶段先行，实施另授权）完全一致；范围可完全冻结为只读，无证据/边界缺口阻止安全释放。**释放。**

## 5. 本会话实际运行的门禁（当前 HEAD 1e58398aa 干净树，2026-11-11）

| 命令 | 结果 | EXIT |
|---|---|---|
| `pwsh -NoProfile -File tools/governance/check.ps1` | PASS（3 warnings：11 非终态 Task、STATUS 3181B/31 行 80%、PLAN 6922B/63 行 80%） | 0 |
| `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-15-DIAG-ACL-1.md` | PASS（5 warnings，同上+2 条 resource 同源解释） | 0 |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | PIN AUDIT: PASS (all 18) | 0 |
| `python tools/generate_api_inventory.py --check` | OK: rendered counts match FEA-C07 doc | 0 |

未运行：产品测试套件、sandbox/export 重跑、Host 原方法探针（全部维持 NOT_RUN，与本裁决只读性质一致）。指针更新提交前在本会话以相同命令对含本报告与指针变更的工作树复跑一遍，结果记入 §7。

## 6. 变更清单（本裁决）

1. 新增本报告（本提交）。
2. `doc/tasks/FEA-15-DIAG-ACL-1.md`：Closeout 追加 ZCode adjudication 行（引用本报告）。
3. `doc/tasks/FEA-15-PIN-EOL-GOV-1.md`：按 §4.2 冻结范围置 ready。
4. `doc/STATUS.md` / `doc/REBASELINE_PLAN.md`：当前指针与 DAG 状态同步（预算内最小改写）。
5. `doc/TASK_LEDGER.md`：`python tools/governance/task_ledger.py --write` 重生成。

## 7. 提交前复跑记录（同内容工作树）

于指针更新落盘后、`git add/commit` 前运行（工作树=本报告 + 5 个指针文件变更，内容与两次提交后的最终树完全一致）：

| 命令 | 结果 | EXIT |
|---|---|---|
| `pwsh -NoProfile -File tools/governance/check.ps1` | PASS（3 warnings：11 非终态 Task、STATUS 3179B/31 行 80%、PLAN 6972B/63 行 80%） | 0 |
| `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-15-DIAG-ACL-1.md` | PASS（5 warnings，同上+2 条 resource 同源解释） | 0 |
| `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-15-PIN-EOL-GOV-1.md` | PASS（3 warnings，同 default） | 0 |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | PIN AUDIT: PASS (all 18) | 0 |
| `python tools/generate_api_inventory.py --check` | OK: rendered counts match FEA-C07 doc | 0 |

## 8. 下一步建议（§5.1）

- **Task**：FEA-15-PIN-EOL-GOV-1（已 ready，见 §4.2 全参数）。
- **Agent**：Owner=Codex（认领→in_progress）；Review 由上下文独立者承担。
- **Recovery point**：仓库 `G:/CODEX/New Manga`，branch `main`，base `1e58398aa07467004c1b329bb52095f63bcb78d4`；worktree=主树（无需新建）。
- **可转发指令**：

> Codex：请认领 `doc/tasks/FEA-15-PIN-EOL-GOV-1.md`（已 ready）。只读治理盘点 Task：按卡面 AC1–AC3 完成当前全集 pin 盘点、跨 checkout 观察矩阵与候选口径/迁移策略分析；证据入 `verification/FEA-15-PIN-EOL-GOV-1/`，命令逐次记录 HEAD/时点/EXIT，NOT_RUN 如实登记。禁改 `.gitattributes`、检查器语义、任何历史证据/pin、冻结契约、源代码、Schema、依赖；禁 push；隔离观察环境放 `G:/CODEX/New Manga.workspace/FEA-15-PIN-EOL-GOV-1/`。裁决依据：`doc/reviews/FEA-15-DIAG-ACL-1-zcode-adjudication-2026-11-11.md`。
