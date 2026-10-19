# 两个后续治理 Task：基线核对与释放草案 r4

日期：2026-10-19；核对 HEAD：`4c1b7bbfd18af22d9459ea29fd5f9109bfce7f97`

## 1. 基线与 Plan 顺序核对

tools/governance/check.ps1 L127 当前字面值：`@{ Path = 'doc/REBASELINE_PLAN.md'; Bytes = 2500; Lines = 35 }`。L126 是另一独立项：`@{ Path = 'doc/STATUS.md'; Bytes = 3200; Lines = 45 }`。L125–134 的循环按每项 Path/Bytes/Lines 检查；只改 L127 两个数不会影响其它预算。Get-Section（L37–42）按精确二级标题截取；Get-TableRows（L44 起）读取 Markdown 表格行，当前 Resource Manifest 不支持正文外 JSON 引用。

REBASELINE_PLAN 实测 35 行 / 2438 bytes；STATUS 实测 27 行 / 3142 bytes。重要阻塞：check.ps1 未被 HEAD 跟踪（git ls-files --error-unmatch 无匹配，tools/governance 是 untracked），所以给定 HEAD 不包含实际维护对象，不能当作正式可复现 base。Codex须先把当前 checker 状态固定进可复现基线并分配隔离 worktree；完成前以下均为释放草案。

Plan 解法：先把现有 RUST-ENV-BASELINE-1 行和 P07/P21 组合行压为一个物理行，用单元格内 <br> 保留各逻辑节点的 ID、依赖、状态，腾一行；压缩 Plan 首行冗余文本，确保仍不超 2500 bytes。先登记预算 Task 独立 DAG 行及 READY ID，STATUS 加短指针但保持 P20 为 Active。预算 Task 改 L127 并集成后，Plan 上限变为 7000/64，再登记 Manifest Task。不得复用/改写 GOV-DEBT-CLEANUP-2 的 approved 行。两 Task 都写 checker，Manifest Task 依赖预算 Task 完成，不可并行。STATUS 当前余 58 bytes，可先容纳一个短 Task 指针，再在后继释放时替换。

## 2. Task A：预算维护

DSH 实施、Antigravity 独立 Review、Codex集成。base_commit 暂留 null，正式释放时填含 checker 的真实集成 HEAD。

````markdown
---
id: GOV-PLAN-BUDGET-1
title: Plan 预算上限扩容
kind: governance
governance_version: 2
status: ready
approval: user_decision_1_2026-10-19; codex_scope_release_integration-closeout-r3
suggested_owner: dsh
owner: dsh
reviewer: Antigravity
depends_on: []
base_commit: null
branch: agent/deepseek/GOV-PLAN-BUDGET-1
worktree: G:/CODEX/New Manga.workspace/worktrees/GOV-PLAN-BUDGET-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-PLAN-BUDGET-1
allowed_paths:
  - tools/governance/check.ps1
  - doc/tasks/GOV-PLAN-BUDGET-1.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/handoffs/
  - doc/reviews/
  - verification/GOV-PLAN-BUDGET-1/
---

# GOV-PLAN-BUDGET-1：Plan 预算上限扩容

## 来源与目标
依用户 2026-10-19 裁决 1 与 r3 `4，将检查器中 Plan 预算调整到 7000 bytes / 64 lines。

## Acceptance Criteria
- [ ] AC1：只改 Path 为 doc/REBASELINE_PLAN.md 的预算项 Bytes=7000、Lines=64。STATUS 3200/45、其它预算、比较条件、warning/error 逻辑和提示不变；diff 可逐行证明。
- [ ] AC2：Owner只改上述两个值、本 Task、Handoff、evidence_dir。Plan/STATUS/导航仅由 Codex维护生命周期指针；不得登记或修改 29 个暂缓 Task、GOV-DEBT-CLEANUP-2 状态/AC/证据。
- [ ] AC3：隔离 fixture 验证 7000 bytes/64 lines 内通过、7001 bytes 与 65 lines 分别超限、80% warning 不变。记录 fixture、命令、PowerShell 版本、stdout/stderr/exit code；不覆盖 Plan。
- [ ] AC4：固定交付 head 执行全局检查和 TaskPath 检查，保存完整输出/exit code，warnings 如实记录。
- [ ] AC5：DSH 固定 base/delivery 并交 Handoff；Antigravity 独立 Review；Codex集成后验证与资源/evidence closeout，全部完成才 done。

## 允许修改范围
tools/governance/check.ps1 两个数值、本 Task、doc/handoffs/GOV-PLAN-BUDGET-1-*.md、verification/GOV-PLAN-BUDGET-1/**。Codex维护 Plan/STATUS/Task 导航元数据；Reviewer写独立 Review。allowed_paths 含 evidence_dir。

## 禁止范围与不做事项
不改两值外逻辑/预算；不改产品、Schema、依赖、接口；不登记暂缓 Task；不跑 AC 探针或产品测试；不移动/删除仓外资源或 worktree。范围需扩大先交 Codex裁定。

## 测试计划
| AC | 步骤 | 环境 | 结果 | 证据 |
|---|---|---|---|---|
| AC1 | 固定 head diff | Git | NOT_RUN | verification/GOV-PLAN-BUDGET-1/ |
| AC3 | 边界 fixture | PowerShell/Windows | NOT_RUN | 同上 |
| AC4 | 全局及 TaskPath checker | 固定 head | NOT_RUN | 同上 |
| AC5 | 固定 head Review/集成验证 | 固定 base | NOT_RUN | Handoff/Review |

## 依赖、风险与阻塞
先决：checker 纳入可复现基线，Codex登记 Plan/STATUS、固定 branch/worktree/base。Owner DSH；Reviewer Antigravity；不可与其它 checker 写入 Task 并行。

## 交付与运行记录
Handoff：doc/handoffs/GOV-PLAN-BUDGET-1-<short-head>.md；Review：doc/reviews/GOV-PLAN-BUDGET-1-<short-head>-antigravity.md。绑定实际 head，NOT_RUN/BLOCKED 不得记 PASS。

## Canonical Evidence
进入 in_review 前列出 AC1–AC5 当前 evidence 路径、commit/hash/class。
| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| 待交付 | AC1–AC5 | verification/GOV-PLAN-BUDGET-1/ | 待填 | 待填 | 待定 |

## Resource Manifest
| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | 据实记录 | PRESERVE_UNKNOWN | 原路径 | 待记录 | 待检查 |
| agent-output/exchange | 据实记录；无则核实 NOT_APPLICABLE | 据实记录 | 原路径 | 待记录 | 待检查 |

## Closeout Record
- Closeout date / Codex：待填。
- canonical_evidence_status / resource_closeout_status：pending。
- 删除、迁移、归档未授权前为 0。
- 未关闭项及保留原因逐项记录。
- 终态时 Codex更新指针并运行 Task 检查。
````

## 3. Task B：正文外部 JSON Manifest（方案 D）

因为硬依赖和写集合重叠，当前准确状态应为 proposed；只有 Task A done、基线/worktree/Plan/STATUS 固定后才转 ready。不能同时真实 ready 或并行实施。

````markdown
---
id: GOV-RESOURCE-MANIFEST-JSON-1
title: 治理检查器支持外部 JSON Resource Manifest
kind: governance
governance_version: 2
status: proposed
approval: codex_scope_release_integration-closeout-r4; user_decision_2026-10-19_scheme_D
suggested_owner: dsh
owner: dsh
reviewer: Codex
depends_on:
  - GOV-PLAN-BUDGET-1
base_commit: null
branch: agent/deepseek/GOV-RESOURCE-MANIFEST-JSON-1
worktree: G:/CODEX/New Manga.workspace/worktrees/GOV-RESOURCE-MANIFEST-JSON-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-RESOURCE-MANIFEST-JSON-1
allowed_paths:
  - tools/governance/check.ps1
  - tools/governance/resource-manifest.schema.json
  - tools/governance/tests/
  - doc/tasks/GOV-RESOURCE-MANIFEST-JSON-1.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/handoffs/
  - doc/reviews/
  - verification/GOV-RESOURCE-MANIFEST-JSON-1/
---

# GOV-RESOURCE-MANIFEST-JSON-1：检查器支持外部 JSON Manifest

## 来源与目标
依 r3 `2 方案 D，支持正文唯一引用“见 resource-manifest.json”，兼容现有 P19-UI-FIX-1 的 7 项和 closeout counts；保留原 JSON、source/destination 原表达式及原值。

## Acceptance Criteria
- [ ] AC1：仅从 Resource Manifest 正文读唯一引用；以仓库根解析且必须是 verification/** 下唯一现存文件。缺失/重复/绝对/越界/仓外/glob/env/macro/不存在路径均 FAIL；不猜测或展开简写。
- [ ] AC2：新增固定版本 tools/governance/resource-manifest.schema.json，定义字段/类型/必填/枚举/未知字段规则；将原 JSON 7 项及 closeout counts 逐项对应，原表达式和值保留，解析值另存。
- [ ] AC3：ALREADY_ABSENT 仅当证据同时证明资源曾列入 Manifest、目标现在不存在、且无引用/进程时接受；缺项则 FAIL/BLOCKED。绝不可写成 NOT_APPLICABLE；后者仅用于证据证明资源从未适用。不可安全解析者保留原文并阻塞，不造替代路径。
- [ ] AC4：花括号表达式仅在拆分可逆、逐字重组原值且与原 JSON 7 项及 closeout counts 逐项对应时转换；歧义/丢项/重项/count 错配须保留原值并 FAIL/BLOCKED。
- [ ] AC5：增加离线 fixtures 用例：有效引用、目标有/无、ALREADY_ABSENT 三条件正反例、错误/重复/缺失/越界/绝对/不存在引用、非法 JSON/schema、7 项/count 错配、花括号往返成功和不可逆失败。逐例存输出/exit code；不访问网络或用户数据。
- [ ] AC6：固定 head 检查未修改的 P19 Task，加载原 verification/P19-UI-FIX-1/resource-manifest.json 并核对 7 项/counts。结果如实记录；原事实不满足 Schema 则阻塞，不改 P19 Task/JSON，不伪造事实或放宽规则。
- [ ] AC7：DSH 固定交付 head/Handoff/离线证据；Codex（非作者）独立 Review；集成后验证和 evidence/resource closeout 全部完成才 done。

## 允许修改范围
tools/governance/check.ps1、tools/governance/resource-manifest.schema.json、tools/governance/tests/**、本 Task、doc/handoffs/GOV-RESOURCE-MANIFEST-JSON-1-*.md、verification/GOV-RESOURCE-MANIFEST-JSON-1/**。Codex仅维护 Plan/STATUS/导航。兼容输入只读。allowed_paths 显式包含实现、schema、测试及 evidence_dir。

## 禁止范围与不做事项
不把已消失资源写为 NOT_APPLICABLE；不缺少三条件接受 ALREADY_ABSENT。不改 P19 Task/原 JSON/历史 evidence/用户资源；不猜 env/glob/macro/不可逆花括号；不改产品、依赖或共享接口；不跑 AC 探针/产品/网络测试；不与 Task A 并行写 checker。

## 测试计划
| AC | 步骤 | 环境 | 结果 | 证据 |
|---|---|---|---|---|
| AC1–4 | schema/路径/证据门槛/表达式正反例 | 隔离 fixture | NOT_RUN | verification/GOV-RESOURCE-MANIFEST-JSON-1/ |
| AC5 | 离线测试并逐例保存 exit code | 无网络 | NOT_RUN | 同上 |
| AC6 | P19 TaskPath 检查 | 固定 head，只读 | NOT_RUN | 同上 |
| AC7 | Review/集成后验证 | 固定 head | NOT_RUN | Handoff/Review |

## 依赖、风险与阻塞
硬依赖 GOV-PLAN-BUDGET-1 done。转 ready 前固定含集成 checker 的 base/worktree 并登记 Plan/STATUS。Owner DSH，Reviewer Codex；reviewer_unavailable 时由 ZCode独立审查，作者不得自审。原 JSON 不满足 Schema 则停下交 Codex裁定。

## 交付与运行记录
Handoff doc/handoffs/GOV-RESOURCE-MANIFEST-JSON-1-<short-head>.md；Review doc/reviews/GOV-RESOURCE-MANIFEST-JSON-1-<short-head>-codex.md。绑定 head；NOT_RUN/BLOCKED 不得写 PASS。

## Canonical Evidence
进入 in_review 前登记 AC1–AC7 当前证据。
| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| 待交付 | AC1–AC7 | verification/GOV-RESOURCE-MANIFEST-JSON-1/ | 待填 | 待填 | 待定 |

## Resource Manifest
| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | 据实记录 | PRESERVE_UNKNOWN | 原路径 | 待记录 | 待检查 |
| fixtures/agent-output | 据实记录；无则核实 NOT_APPLICABLE | 据实记录 | 原路径 | 待记录 | 待检查 |

## Closeout Record
- Closeout date / Codex：待填。
- canonical_evidence_status / resource_closeout_status：pending。
- 删除、迁移、归档未授权前为 0。
- 未关闭项及保留原因逐项记录。
- 终态时 Codex更新 Plan/STATUS/导航并运行 Task 检查。
````

## 4. 登记结论

先腾一物理行并压缩首行，再只登记预算 Task；扩容集成后再登记后继能力 Task。保留 GOV-DEBT-CLEANUP-2 approved 行。当前二者不能同时真实 ready：checker 无已跟踪基线，后继还有硬依赖和重叠写路径。以上是顺序释放内容，不表示已登记/授权开工。

## 5. git status 对比

写入前：1235 条；UTF-8 行文本 SHA-256：`707be7ac7a4a05ffe6581a591ca125de5c4f2286d3bc93e7a2d88f6a9e8fde4`。写入后：1236 条；SHA-256：`c0eac54f4b6cf8965243f6307b688a9761f42b34cbb6881b6b02de0a07de13ed`。唯一新增项为 `?? verification/P09-GOVERNANCE-DEBT-20261019/codex-release-two-r4.md`；排除该项后的 1235 条状态及 SHA-256 与写入前完全一致。

