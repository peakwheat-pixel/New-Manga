# P19-UI-MANIFEST-VIEW-1 Final Closeout 与同源语义后继 Task 裁定（r12）

日期：2026-10-19（Asia/Shanghai）  
裁定人：Codex  
范围：本报告记录 P19-UI-MANIFEST-VIEW-1 最终 closeout、Plan/STATUS 收口建议、资源/证据盘点、GOV-RESOURCE-MANIFEST-SAME-LOCATION-1 的完整 ready Task 草案，以及真实缺失路径的独立核实归属。按本轮授权，实际只新增本文件；没有改 Task、Plan、STATUS、checker、源 JSON、worktree 文件或 Git 引用。

## 1. 现场事实与主 checkout 状态

主 checkout `G:\CODEX\New Manga`：branch `antigravity/P09-AC3-DELETE-HARDEN-1`，HEAD `0393ce44b08dd1562d7c404ce911d84934a8f54f`。开始前 `git status --porcelain` 为 1,236 行，UTF-8 状态文本 SHA-256 为 `B586C29A17AA755607D288996CA573F38BDB75A129CD4FB34E3F6D8DD9C8BDFB`。工作区已有大量未提交文件，全部归原作者；本轮不覆盖、不清理。

指定 worktree `G:\CODEX\New Manga\.agents\worktrees\P19-UI-MANIFEST-VIEW-1` 当前 branch `P19-UI-MANIFEST-VIEW-1`，HEAD `67a665e4964a8128bddc03cc6c34df1c6f0fe783`。从 `b36817d65` 到该 head 仅有三条 Task/Handoff/Review 文档路径变化：新增 Handoff v2、新增 Review、更新 Task delivery head 与 Closeout Record；没有更改已审查的 P19 正文实现或 evidence 文件。指定的 GOV checker 集成提交 `3fe78a67cdf8e43a539e0de7ddc0ce6b8c0f8311` 是主 checkout HEAD 的祖先。

worktree `git status --porcelain` 当前有 34 行：33 个镜像环境产生的未跟踪文件，以及旧路径 `doc/handoffs/P19-UI-MANIFEST-VIEW-1-4543e23a0.md` 的删除状态。Task Resource Manifest 对 33 个镜像文件的描述不等于允许清理；34 行均保留为 `PRESERVE_UNKNOWN`/未知 dirty 状态，直至其所有者逐项核实。不要移除 worktree、恢复旧 Handoff、移动、删除、归档或清理其中任何对象。

## 2.1 核准与 closeout

**核准终态 head：`67a665e4964a8128bddc03cc6c34df1c6f0fe783`。** 可作为当前 Task 文件、Review、Handoff v2 和最终 closeout 记录的终态快照。保留用户给定与现场一致的 `delivery_head=b36817d65e08a9e1269075bf7c116793e650e928`，不把它改成 `67a665e49`。

原因：`delivery_head` 应指 Review 实际审查并批准的交付 head；Review frontmatter 的 `reviewed_head` 为 `b36817d65`，Review 正文也把审查对象固定在该 head。`67a665e49` 之后的变化是 Review 落盘、delivery 字段/Closeout Record 修正和 Handoff v2，不是新的被 Review 实现交付。若把 delivery_head 改为 `67a665e49`，会制造“Review 已审查该 head”的错误暗示。closeout 应并列记录：

```text
reviewed_head = b36817d65e08a9e1269075bf7c116793e650e928
delivery_head = b36817d65e08a9e1269075bf7c116793e650e928
closeout_head = 67a665e4964a8128bddc03cc6c34df1c6f0fe783
```

如 Task 格式没有 `closeout_head` 字段，将该值记录在 Codex closeout evidence/关闭记录中；不要改写 `delivery_head` 或 Review 的 `reviewed_head`。这与 r9 对 GOV-RESOURCE-MANIFEST-JSON-1 的处理一致：审查 head、交付 head、集成 head 按各自事实记账，不能为了字段一致伪造审查范围。

保留 r11 裁定：不回退引用修正；AC1、AC2、AC4、AC5、AC6 达成，AC3 失败且保持未勾选；Task 为 `closed_with_limitations`，不能记 `done`。错误从 4 到 10 属于解除引用语法阻断后使深层校验首次可达（unmasking），不构成本 Task 引入六个资源债务的证据。

### Plan 完整替换内容

将 `doc/REBASELINE_PLAN.md` 更新为下列完整内容。P19 节点改为 `closed_with_limitations`、从 READY 移除且 `done` 仍为 34 项；新后继 Task 在本轮拟定的完整范围下列为 `ready` 并加入 READY 声明。该内容是供获授权的 Codex/DHS 后续落盘的完整版本，本轮没有写入 Plan。

```markdown
# Project Rebaseline Plan —唯一DAG；运行见[STATUS](STATUS.md)。范围/裁决见[REPORT](../verification/PROJECT-ROADMAP-RELEASE/REPORT.md)。
|节点/目标|依赖|状态|
|---|---|---|
|P01 台账 / P03 SFX入口 / P05 契约注记|—|done|
|P02 WebView|P08|限定关闭|
|P04 并发验收|P22|done|
|P06 GC补证|—|**done**（集成 d3342895）|
|P08 产品范围|—|done|
|ARCH-DOC-REBASELINE|P08|ready / integrated（AC7 消费者裁决待做）|
|P09 导入Core|P08/DOC|closed_with_limitations（集成 c6a7339f；AC3 由下项回补）|
|P09-AC3-DELETE-1|P09|closed_with_limitations（R3 changes_requested；HARDEN-1 接手）|
|P10 凭据通道 / P11 长任务契约|P08|**done**（c46c0df0 / ceca5721）|
|P12 书架导入|P09/UI/C1/FU2|**done**（集成 465e3001e）|
|P13 后台恢复|P09/P11/P13-C1|**done**（集成 8d7cad13）|
|P14 工作台|P13/UI|**done**（集成 2dc14cdd1）|
|P15 设置/Core/host|P15-C1/P10/UI|done（含 FU、HOST-1/2）|
|P16 阅读导出Core|P08/P13/C1|**done**（集成 e1be3082）|
|P17 阅读导出UI|P16/DOC/UI|**done**（集成 f18b7fe8f）|
|P15-C1 设置面契约|P10|**done**（集成 f07221313）|
|P18 JA/KO质量|P10/P13/DOC|closed_with_limitations（AC2门槛、AC5阻塞）|
|P19 四页安全E2E|P12/14/15/17/18/P04|closed_with_limitations（4c860d882）|
|P20 Windows发布|P19/P03/P06/DOC|ready|
|P20-MEM-OPT-1|P20|closed（AC1 完成；AC2 经调阈值消解）|
|P20-ISOLATION-1|P20|in_review|
|P20-AC4-FPS-1|P20|closed_with_limitations（AC3 PASS；AC5 依裁决）|
|GOV-DEBT-CLEANUP-1|P19/P20|blocked（待用户裁决）|
|GOV-DEBT-CLEANUP-2|—|approved（AC6 的 P19-UI-FIX-1 格式债务；AC7 的 61 项归属未结）|
|GOV-RESOURCE-MANIFEST-JSON-1|GOV-PLAN-BUDGET-1|done（外部 JSON Manifest 检查器；19/19 用例；集成 3fe78a67c）|
|P19-UI-MANIFEST-VIEW-1|GOV-RESOURCE-MANIFEST-JSON-1|closed_with_limitations（AC1/AC2/AC4/AC5/AC6 达成；AC3 因 4→10 错误清单失败；按 Codex r11 保留修正）|
|GOV-RESOURCE-MANIFEST-SAME-LOCATION-1|GOV-RESOURCE-MANIFEST-JSON-1|ready（外部 JSON Manifest 同源/空/`-` 目的地语义；不改 P19 源 JSON）|
|P20-CLOSE-BOUND-1|P20-ISOLATION-1|closed_with_limitations（R6）|
|P20-CLOSE-BOUND-HARDEN-1|P20-CLOSE-BOUND-1|closed_with_limitations|
|P09-AC3-DELETE-HARDEN-1|P09-AC3-DELETE-1|closed_with_limitations（未集成）|
|P09-PREVIEW-LIFECYCLE-RECLAIM-1|P09-AC3-DELETE-HARDEN-1|closed_with_limitations（AC6 未满足；未集成）|
|GOV-PLAN-BUDGET-1|—|done|
|RUST-ENV-BASELINE-1（P20-CLOSE-BOUND-1）/ P07交互补缺（P02）/ P21旧栈归档（P20+另授权）|—|proposed（P07/P21可选）|
|P22 响应归属|P22-REBASE-1|已集成；P04 不放行，H1/P2-1/13 与 BC-AC5 缺项保留。已完成见各节点行。|
READY 节点：ARCH-DOC-REBASELINE、P20、GOV-RESOURCE-MANIFEST-SAME-LOCATION-1。in_review：HARDEN-2。done：**34 项**。
```

上文 Plan 最后一行长度/体量应由正式写入者重新测量并运行治理 checker；内容只新增一个 DAG 节点，替换一个终态状态行并更新 READY 声明。

### READY 声明裁定

`P19-UI-MANIFEST-VIEW-1` 必须从 READY 声明移除，因为它已是终态 `closed_with_limitations`。它不增加 `done` 计数。上述建议 Plan 中出现的新 READY 节点仅是后继 Task 在完成正式注册/释放后才成立；P19 本身绝不保留 READY。

### STATUS 裁定

`doc/STATUS.md` 需要改动：Plan 是 DAG/READY 的唯一权威，STATUS 运行指针也应记录新 ready Task 与 P19 终态指针；当前 STATUS 已将 P19 从 READY 列表排除，但其终态列表未列 P19，也未登记新的 Task。保持唯一 Active Task P20 不变。

当前 STATUS 为 3,142 bytes。以下是可替换“当前权威指针”中的 DAG bullet 的完整候选行；按当前文件测算，替换后约 3,198 bytes / 27 行，低于 3,200 / 45 上限，但只剩 2 bytes 余量，写入后必须实测并运行 checker：

```markdown
- DAG：[REBASELINE_PLAN](REBASELINE_PLAN.md)；READY=ARCH-DOC-REBASELINE、P20、GOV-RESOURCE-MANIFEST-SAME-LOCATION-1；BLOCKED=GOV-DEBT-CLEANUP-1；proposed=MANAGED-READ-ROOT-TRUST-1；in_review=P20-CLOSE-BOUND-HARDEN-2；终态=P19-UI-MANIFEST-VIEW-1、PREVIEW-LIFECYCLE-RECLAIM-1、P09-AC3-DELETE-HARDEN-1。
```

## 2.3 证据与资源盘点

### Canonical Evidence

`verification/P19-UI-MANIFEST-VIEW-1/` 中现有 **6 份** evidence 文件，Task 表中相应的 6 个 `CANONICAL` 行完整；第 7 行是 `verification/P19-UI-FIX-1/resource-manifest.json` 的 `SOURCE_PIN`，所以当前 7 行并不缺少 evidence 文件或 pin。

但 Task AC6 明确要求 Handoff 与独立 Review，且它们没有登记在现有 Canonical Evidence 表中。因此，若该表要作为完整的当前 Gate 索引，应补登以下两行（本轮只在本 closeout 文件记录建议，未改 Task 表）：

| evidence_id | AC/Gate | path | commit（含文件） | sha256 | class |
|---|---|---|---|---|---|
| `P19VIEW-HANDOFF-V2` | AC6 / Handoff | `doc/handoffs/P19-UI-MANIFEST-VIEW-1-b36817d65.md` | `67a665e4964a8128bddc03cc6c34df1c6f0fe783` | `9CD486F2BD4B5E3197518B2D9004C1B4F8875DC7148867D2370C7FD014E7238B` | `CANONICAL` |
| `P19VIEW-REVIEW-R1` | AC6 / 独立 Review | `doc/reviews/P19-UI-MANIFEST-VIEW-1-b36817d65-antigravity-r1.md` | `67a665e4964a8128bddc03cc6c34df1c6f0fe783` | `25F6D953D7ECB235EF0382D443982A2C955048F9EB0CD81A65980BA46B0DD43C` | `CANONICAL` |

建议新增 closure evidence 文件：**不另建第二个文件**。本 `codex-closeout-p19-view-r12.md` 是本轮唯一授权写入文件，承载 Codex 裁定、head 差异、Plan/STATUS 内容、证据与资源审计及后继任务规格，可作为本次 closeout/adjudication evidence。它不是 P19 AC 的替代证据，也不能冒充已补入 Task 表的 Review/Handoff pin。

### Resource Manifest

Task 中 5 行 Resource Manifest 已覆盖 P19 Task 文件、源 JSON、evidence 目录、Task worktree、agent output 类别；但 worktree 当前 34 条 porcelain 状态的构成需要在 closeout 说明中以现场值补充：33 个未跟踪镜像文件 + 1 个已删除旧 Handoff 路径。其 disposition 保持 `PRESERVE_UNKNOWN`，destination 保持原 worktree；不得清理、恢复、移动或归档。

`deletion / migration / archive = 0`。agent output 没有本 Task 专属的仓外产物，保留为 `NOT_APPLICABLE`。`resource_closeout_status: complete` 可保留，因为资源状态已盘点且未知项明确保留；“complete”表示 closeout 盘点完成，不表示资源已清除。Task 内已有的镜像数量描述与 worktree porcelain 数不是同一口径，应在 closeout 证据说明各自计数，不能把 34 条状态都说成 34 个未跟踪文件。

## 2.4 后继 ready Task：GOV-RESOURCE-MANIFEST-SAME-LOCATION-1

以下是可完整落盘的 Task 内容。Owner 为 Antigravity，Reviewer 为 DeepSeek Harness，二者不同；`base_commit` 采用主 checkout 当前 HEAD `0393ce44b08dd1562d7c404ce911d84934a8f54f`，该提交包含已集成 checker（集成提交 `3fe78a67cdf8e43a539e0de7ddc0ce6b8c0f8311` 是其祖先）。本内容是待 Codex 正式注册/释放的 Task payload；由于本轮只授权新增本报告，Task、Plan、STATUS 尚未实际写入，故它此刻不是已释放 Task。

````markdown
---
id: GOV-RESOURCE-MANIFEST-SAME-LOCATION-1
title: Resource Manifest 同源与空目的地语义
kind: governance/checker
governance_version: 2
status: ready
approval: codex_release_20261019_after_P19-UI-MANIFEST-VIEW-1_closeout
suggested_owner: Antigravity
owner: antigravity
reviewer: dsh
depends_on: [GOV-RESOURCE-MANIFEST-JSON-1]
base_commit: 0393ce44b08dd1562d7c404ce911d84934a8f54f
branch: GOV-RESOURCE-MANIFEST-SAME-LOCATION-1
worktree: G:/CODEX/New Manga/.agents/worktrees/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1
allowed_paths:
  - tools/governance/check.ps1
  - tools/governance/tests/
  - verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1/
  - doc/tasks/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1.md
  - doc/handoffs/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1-*.md
  - doc/reviews/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1-*.md
---

# GOV-RESOURCE-MANIFEST-SAME-LOCATION-1：Resource Manifest 同源与空目的地语义

## 来源与目标

`P19-UI-MANIFEST-VIEW-1` 在修复外部清单引用格式后，使 checker 首次可达 6 个 destination 校验结果。其中 5 个 `destination_path` 是同源位置说明，不是可以直接交给路径解析器的文件系统路径：

- `Same ignored target/dist locations in this worktree`
- `Same source location`
- `Same shared build environment`
- `Same local cache location`
- `Same main-repository paths`

已集成的 `GOV-RESOURCE-MANIFEST-JSON-1` 提供外部 JSON Manifest 读取、schema 校验及路径检查；它没有定义上述同源标记、空字符串或 `-` 的解释。本 Task 为 checker 增加限缩、可审计的同源语义，且不修改源 JSON、schema 或 P19 历史文件。

## Acceptance Criteria

- [ ] **AC1 同源与空值解析**：外部 JSON Resource Manifest 中，仅将上述五个已核实的 `Same ...` sentinel、空白/空字符串及字面 `-` 作为同源标记。将其解释为该行 `source_path` 并对 source 运行现有路径解析/存在性校验，或明确跳过 destination 存在性校验并输出可审计 note；优先采用 source-path 回退并验证 source。不得把 sentinel 文本本身传给 `Test-Path`。
- [ ] **AC2 note 可追溯**：对每个被解释为同源的资源输出 note，至少指出资源标识、原 `destination_path` 形态及使用的 `source_path`；不得宣称存在一个不同于 source 的 destination。
- [ ] **AC3 限制匹配范围**：非同类普通散文（例如 `some other place`）不能获得同源豁免，仍按普通 destination 路径处理并失败；未知 `Same ...` 文本也不能自动扩展为通用自然语言解析，除非它精确匹配本 Task 列明的 sentinel 之一。
- [ ] **AC4 真实缺失路径继续失败**：`apps/desktop/src-tauri/target/p19-ui-fix-1-isolation-20261017` 继续按真实 destination 路径进行存在性校验；不存在时必须报错。不得把它归类成同源标记、静默豁免或记为通过。
- [ ] **AC5 离线回归用例**：扩展 `tools/governance/tests/run-resource-manifest-cases.py` 及其现有 fixtures，至少覆盖：五个同源 sentinel 通过且给出 note；空字符串/空白与 `-` 回退 `source_path` 并给出 note；存在的普通 destination 通过；非同类散文失败；真实缺失 destination 失败。用例不得访问网络或依赖用户漫画/模型数据。
- [ ] **AC6 集成前验证证据**：运行既有 Resource Manifest 离线套件及指定 Task checker，记录命令、环境、每例 PASS/FAIL、完整 stdout/stderr 与退出码。新行为不改变既有 19 个用例预期；目标 P19 源 Task 中的两项日志 SHA 差异、worktree 行尾差异、8 个未登记文件及真实缺失路径不得被宣称已清理。
- [ ] **AC7 范围与资源保护**：差异只在 `allowed_paths`；不改源 JSON、P19 Task/evidence/pins、其他 Task、schema、依赖或任何资源；Handoff 与独立 Review 固定实际 delivery/reviewed head。

## 允许修改范围

- `tools/governance/check.ps1`：仅外部 JSON Resource Manifest 的 destination 同源语义与 note。
- `tools/governance/tests/`：离线 Resource Manifest 用例与 fixtures。
- `verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1/`：本 Task 判别力证据。
- 本 Task 自己的 Handoff 与独立 Review 文件。

超出以上范围须先由 Codex 另行裁定，不得由 Owner 自行扩围。

## 禁止范围

- 不改 `verification/P19-UI-FIX-1/resource-manifest.json`。
- 不改 `doc/tasks/P19-UI-FIX-1.md` 正文或其 frontmatter。
- 不改 P19 的 evidence、pins、Review、Handoff 或历史日志。
- 不重钉 pin，不删除、移动、归档、重建或清理任何资源。
- 不改 schema、依赖或其它 Task；不扩大为通用自然语言解析器。
- 不把仍缺失的 isolation destination 记为通过。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 同源、空值与 note | `python tools/governance/tests/run-resource-manifest-cases.py`；逐例断言 source 回退与 note | 离线、隔离临时 fixture | NOT_RUN | `verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1/resource-manifest-cases.txt` |
| AC3 普通散文与未知 sentinel | 同一离线套件；断言不被豁免并失败 | 离线 | NOT_RUN | 同上 |
| AC4 真实缺失 destination | 同一离线套件；用隔离根下不存在的真实路径断言失败；另保留该已知 P19 路径的预期失败事实 | 离线，不创建该路径 | NOT_RUN | 同上 |
| AC5 既有回归 | `python tools/governance/tests/run-resource-manifest-cases.py` | Python 环境与既有 19-case fixtures | NOT_RUN | `verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1/regression.txt` |
| AC6 指定治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1.md` | Windows PowerShell 7 | NOT_RUN | `verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1/task-check.txt` |

实现路径/参数若与仓库实际脚本不符，先由 Codex核对并修订 Task；不得记录未运行命令为 PASS。

## 依赖、风险与阻塞

- 硬依赖：`GOV-RESOURCE-MANIFEST-JSON-1`，已集成；本 Task base 固定为主 checkout 的 `0393ce44b08dd1562d7c404ce911d84934a8f54f`。
- 5 个同源标记来自 `verification/P19-UI-FIX-1/resource-manifest.json` 的现有原文，仅作为测试输入；禁止修改该输入。
- 真正缺失的 isolation 路径是独立资源核实事项，不能由本 Task 的 checker 语义实现推断其历史去向。
- 任何 schema 不兼容、需要改 schema/依赖或无法保留非同类散文失败行为时，停止并交 Codex 裁定。

## 交付与运行记录

- Owner：Antigravity；Reviewer：DeepSeek Harness；Codex 负责 Task 注册、集成和 closeout。
- Handoff：`doc/handoffs/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1-<short-head>.md`。
- Review：`doc/reviews/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1-<short-head>-dsh-r1.md`。
- Handoff 记录 base、delivery head、提交、实际用例/检查命令与结果、未跑项及资源保留状态。Review 固定精确 `reviewed_head`，重点复核 sentinel 白名单、普通散文和不存在路径仍失败、note 语义及禁止范围。

## Canonical Evidence

进入 `in_review` 前为 AC1–AC7 各登记当前判别力证据及含文件的 commit/SHA-256。

| evidence_id | AC/Gate | path | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

Task worktree 与派生产物在 closeout 逐项核实；未知或 dirty 项保留，不按目录名推断可删除。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task worktree | `G:/CODEX/New Manga/.agents/worktrees/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1` | `PRESERVE_UNKNOWN` | 原路径 | closeout 时记录 HEAD/status | 未完成盘点前保留 |
| task env / agent output / exchange | `G:/CODEX/New Manga.workspace/` 对应 Task 子目录 | `NOT_APPLICABLE` 或按实核实 | — | closeout 时复核 | 不假定存在；记录检查结果 |
| test fixtures / evidence | 本 Task `tools/governance/tests/` 与 `verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1/` | `PRESERVE_REFERENCED` | 原路径 | closeout 时计算 | 被回归套件/证据索引引用，保留 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- `canonical_evidence_status`: `pending`。
- `resource_closeout_status`: `pending`。
- 删除、迁移、归档数量/字节数：待核实；未获授权不操作。
- 未关闭项及保留原因：待实测后填写。
- 当前指针清理：Codex 更新 STATUS / Plan 并运行 Task checker。
````

## 2.5 真实不存在路径的核实归属

`apps/desktop/src-tauri/target/p19-ui-fix-1-isolation-20261017` 是真实路径形状，不属于 5 个 `Same ...` 同源标记。当前证据只证明在 P19 worktree 检查时路径不存在；不足以证明它曾经创建后被清理，也不足以证明从未创建。

裁定：这是 **P19-UI-FIX-1 的资源账**，但应通过独立、只读的资源去向核实 Task 完成，不能混入同源 checker Task 的实现范围，也不能由本次 view Task 直接推定。由 Codex 为 `P19-UI-FIX-1` 建立范围窄化的 provenance/reconciliation Task 并指定 DeepSeek Harness 执行只读核查；核查至少检查 P19 Resource Manifest 原始声明、Task/closeout 记录、可用 Git 历史与引用、workspace registry/inventory、相关日志及资源 owner 的可验证记录。Reviewer 由非执行者担任。结果只能写成 `证明已清理`、`证明从未创建` 或 `去向未能证明/未知`，并列证据、时间边界与 hash；没有证据时保留 `PRESERVE_UNKNOWN`，不恢复、创建、移动或删除路径。只有核查完成后，Codex 才决定是否更新 P19 资源账；更新原 P19 Task 正文或 pin 需另行明确授权。

## DSH / Codex 执行顺序

1. DSH 先按本报告做只读核验：确认 `b36817d65` 是 Review 的 `reviewed_head`/`delivery_head`，`67a665e49` 是当前 Task closeout head；复核 10 项错误账与源 JSON pin，不改 P19 JSON、证据、Task 或任何资源。
2. Codex 作为唯一权威写入者，先将 P19 行和 READY 声明按本报告更新到 Plan，更新 STATUS 指针；把 Review/Handoff 两项追加到 P19 Canonical Evidence 索引或在正式 closeout 证据中明确登记；实测字节预算并运行适用的 Task/global governance checks。状态仍为 `closed_with_limitations`，AC3 仍 FAIL。当前本轮仅授权本 r12 文件，因此这些写入需要后续明确执行窗口，不能由 DSH 越权改主线文档。
3. Codex 在 P19 closeout 后正式创建 `GOV-RESOURCE-MANIFEST-SAME-LOCATION-1.md`，确认主线 base 仍为 `0393ce44b08dd1562d7c404ce911d84934a8f54f` 或其包含 `3fe78a67c` 的后继；分配 branch/worktree，写入本报告给出的 Task 内容，并把 Plan/STATUS 登记与检查通过后才置 `ready`、释放 Antigravity。不得把“本报告附有 ready YAML”误当实际 release。
4. Antigravity 按冻结范围实现 checker 与离线用例，提交固定 head、Handoff 和 AC 证据；不修改源清单、P19 Task/evidence/pins、schema 或依赖。
5. DSH 在独立工作区针对精确 head Review：确认五个 sentinel 及空/`-` 回退 source 并出 note；非同类散文、未知 sentinel、真实缺失路径继续失败；既有回归通过；对照 allowed_paths 和资源保护。发现越界时不得自行修复生产实现，交 Codex 裁定。
6. 另由 Codex 释放 P19 源资源去向的只读核实 Task，DSH 按其 scope 调查真实 isolation 路径；与第 4 步的 checker 实现分开交付，不能以 checker 测试结果代替资源 provenance 结论。

## 本轮主 checkout porcelain 对比

- 动手前：1,236 行；SHA-256 `B586C29A17AA755607D288996CA573F38BDB75A129CD4FB34E3F6D8DD9C8BDFB`。
- 动手后：1,237 行；SHA-256 `2EC2F200905D4356F38EA1354B9E5C530BD43DCE6DA4CEF3787EE58F7752FDCD`。去掉本文件对应的一行后，仍为 1,236 行且 SHA-256 恢复为动手前的 `B586C29A17AA755607D288996CA573F38BDB75A129CD4FB34E3F6D8DD9C8BDFB`；唯一差异是新增本文件 `?? verification/P09-GOVERNANCE-DEBT-20261019/codex-closeout-p19-view-r12.md`。
- 本轮未执行 Git 写命令、未调用 `coordinator-lease.py`、未运行测试、未执行 merge，也未改 worktree。
