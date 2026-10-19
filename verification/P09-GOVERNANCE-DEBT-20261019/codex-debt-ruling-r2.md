# P09 治理债逐项裁定（第二轮）与清理 Task 草案

日期：2026-10-19  
身份：Codex / Lead / Architect / Integrator  
性质：基于事实文件的逐项处置裁定；不是复审，不是集成批准，不授权物理清理。  
范围：`verification/P09-GOVERNANCE-DEBT-20261019/` 中的七份事实文件，并以 `codex-debt-ruling.md` 为上一轮规则依据。

## 0. 执行边界

1. 下列分类按事实文件中的每一行/每一项适用；遇到未满足判据的单项，标为 `BLOCKED`，保持原 pin、原 AC、原资源及原状态，不推断、不覆盖。
2. 任何 Task 状态、DAG、READY 节点、产品 AC 取舍及个人数据处置，均依协作协议 §4.1、§4.2、§5 和用户裁决执行。检查器 PASS 不能替代语义审查、用户授权或集成批准。
3. 本文件内的 Task 草案不是 Task 释放。DSH 持有的 epoch 8 lease 及本轮对单一裁定文件的授权，不自动授权其执行草案中的后续写入。
4. 只允许在新 Task 经 Codex 释放、Plan/STATUS 指针有效、范围冻结且对应 lease 有效后执行可执行项。任何物理资源动作还须满足 approved integration closeout window。

## 1. SHA 不匹配：102 行逐项处置

依据 `sha-mismatch-evidence-chain.md` 的交叉分类。将以下判据对表中每一行分别执行，不能以类别汇总代替逐行结果。

### 1.1 `pin_matches_at_commit` 且工作区等于 HEAD：78 行

- **裁定：** 原 pin 在其记录 commit 上准确，后续正常提交改变了路径内容；这是“历史 pin 与当前版本不同”，不是原证据损坏。该旧 pin 继续代表当时版本，保留原值，不回写历史 Review，也不因当前 hash 不同而判原验收无效。
- **允许纠正的唯一情形：** 当前 Task 的活动 Canonical Evidence 确实需要指向一份新的、仍支持同一已释放 AC 的证据；DSH 对该行提供旧/新文件、commit、raw SHA-256、变更来源和对应 AC，Codex逐项确认替代关系后，可在 GOV-DEBT-CLEANUP-2 中追加 supersession 记录并更新活动 pin。仅为通过当前工作区检查器、或仅因路径被后续提交修改，不得重钉。
- **授权顺序：** DSH 提交逐行证据链 → 独立 Reviewer（Antigravity）复核固定 head 与证据来源 → Codex 对替代关系和 AC 支持作逐项批准 → Task Owner 只更新获批行，并保存旧 pin / 新 pin / 原因 / 裁定者记录。

### 1.2 `pin_differs_at_commit` 且工作区等于 HEAD：13 行

- **裁定：** 该 pin 在其声称的 commit 上就不匹配；不得标成“过时”，不得仅用当前文件 hash 覆盖。
- **必须追溯原 pin 来源。** DSH 对每行检查 Task/Handoff/Review 历史、pin 生成记录、原始证据快照及该 commit 的文件字节，回答：原 pin 是否来自另一合法路径/commit/快照、是否误抄/计算错误、是否存在格式或编码来源差异。保存可复核来源；不得猜测作者意图。
- **纠正判据：** 只有找回并证明该 AC 原本意图引用的确切不可变证据，且该证据内容与 AC 对应时，Codex 才可批准修正 pin。若原 pin 的生成来源无法找回，或原文件内容的 AC 归属不明，保留旧 pin，追加 `origin_unverified` 事实并阻止该行关闭。修正记录必须同时保留原 pin、声称 commit、原证据来源调查结果、新 pin 和 Codex裁定；不能把不匹配历史改写成“曾经正确”。
- **授权顺序：** DSH 逐行追源 → Antigravity 独立复核证据链 → Codex 对“确切来源及 AC 适配”逐行批准 → Owner 在清理 Task 内追加纠正记录并更新活动字段。产品 AC 变化或替代证据改变验收含义时另需用户裁决。

### 1.3 `pin_differs_at_commit` 且工作区不等于 HEAD：11 行

- **裁定：** pin 来源不匹配与未提交工作区修改是两项叠加问题。立即按 `BLOCKED_PRESERVE_DIRTY` 处理；不得从工作区当前字节生成 pin，不得覆盖、暂存、清理或回滚改动。
- **逐行流程：** DSH 只读比较 Task pin、声称 commit 中的文件、当前 HEAD 文件、工作区文件和 raw/LF/CRLF SHA；记录工作区变更的逐文件 diff/stat、来源及是否属于用户或 Owner 修改。若无法确认修改归属，按用户内容保留。只有在锁定一个有来源证明、内容未被未授权改动的不可变版本后，才可继续 1.2 的来源追溯；若同时证明当前活动证据被合法替代，再走 1.1 的替代流程。
- **解阻条件：** dirty 修改已有独立授权处理、内容归属明确且来源版本可复现；之后由 Reviewer 复核、Codex逐行核准。否则保持旧 pin、工作区和失败状态，报告阻塞，不得将该行计作已纠正。

### 1.4 78 条 EOL-only re-pin 记录

`round5-eol-repin-record.md` 已记录 78 行原/新 pin，并证明 CRLF 折叠为 LF 后与原 pin 相等。逐行保留该审计记录；不得将这些行与上述 102 行 byte-different debt 混为一类，也不得重做或抹除旧 pin。清理 Task 只需验证该记录覆盖的 Task/行号和原值完整，不再执行第二次同义重钉。

## 2. DAG 未登记的 29 个非终态 Task

依据 `dangling-dag-facts.md`。裁定：**本轮不把 29 项批量登记，也不将 10 个未入库文件提交；目前不把这 10 个单凭“存在于工作区”定性为历史快照。**

- 10 个未入库 Task 文件维持 `UNREGISTERED_UNTRUSTED_SNAPSHOT`：保留现状，不改、不删除、不移动、不 `git add`。其原始来源、生成/修改时间、分支或交付关系尚须逐项形成可审计来源记录。来源不能证明时，只作为未登记工作区材料，不进入 Plan/STATUS，也不形成历史权威。
- 对其余 19 个已入库文件，同样不因 tracked 就视为仍获授权。对全部 29 项建立逐 Task adjudication 行：现有状态、Plan/STATUS 指涉、依赖、已释放目标、未勾选 AC、交付/集成证据、建议继续/取消/替代/历史处理及其依据。建议不是状态变更授权。
- 当前 28/29 在 STATUS 与 Plan 都零指涉，这只能证明当前指针没有登记它们；不能证明应当继续或取消。未获用户裁决前，原 Task 状态与原 AC 保持不变，不伪造终态。
- Plan 预算从 **2500 bytes / 35 lines** 提至 **7000 bytes / 64 lines** 是待用户裁决项。未确认前不得编辑预算或把任务藏进历史快照、外部清单或伪节点；用户确认后也只登记逐项 adjudication 后仍获授权且非终态的最小集合。READY 项必须列入 READY 声明。
- 10 个文件未来若被用户裁定为继续，须先验证来源、内容完整性和当前授权，并通过正式 Task/DAG 生命周期；是否提交入库是独立写入，不可由本裁定推定。若用户裁定不再继续，也先按来源/引用事实决定保留位置，不自动删除或归档。

## 3. P02 AC3 未合并分支的 23 个 pin

依据 `p02-ac3-branch-evidence-inventory.md`，分支 head `0af8980884e9d027042ef145cd966577d86b5bc5` 不是当前 HEAD 祖先；分支有 18 个对应 pin 文件，另 5 个在该分支上也不存在。

- **18 个分支上存在的 pin：** 只确认“该固定分支 head 有此路径/文件”的事实。它们仍不是主线 Canonical Evidence。不得重钉到绝对 worktree 路径、不得因路径在分支存在而标成已集成。后续需 DSH/Reviewer 对每个文件的内容、对应 AC 和最小必要性作独立审查；只有 Codex正式批准集成且进入 approved integration window，才可集成获批最小集合并以含文件的集成 commit 更新 pin。
- **5 个分支上不存在的 pin**（下列精确路径）：
  1. `doc/handoffs/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION-R1.md`
  2. `verification/P02-NEW-TIME-BASELINE/codex-parent-integration-r1.md`
  3. `verification/P02-NEW-TIME-BASELINE/codex-parent-integration-r1.json`
  4. `verification/P02-NEW-TIME-BASELINE/codex-post-resolution-selftest-r1.meta.json`
  5. `verification/P02-NEW-TIME-BASELINE/codex-post-resolution-selftest-r1.fixture-inventory.json`
- **五项处置：** 不从 Task 中静默移除，也不以“合并分支即可修复”处理。标记为 `MISSING_FROM_FIXED_BRANCH_SOURCE_UNRESOLVED`，保留原引用和原 pin，阻止把 23 项 Canonical Evidence 认定为完整。DSH 只读检索仓库可达历史、已登记证据源及已有工作区副本，逐项记录来源/head/hash；找回后按来源审查。未找回时，只有用户确认对应 AC/证据要求可取消或转移、且 Codex记录正式范围裁决，才可将 AC/引用移出活动范围，同时保留原始缺失状态和替代 Task/证据路径。不得为解决缺项合并分支或删除引用。
- 在上述 5 项全部找到并验证，或获得所需用户范围裁决前，`integration_status: integrated` 与当前证据事实冲突，应标为“未证实/blocked”，不能据字段值判为 integrated/done。该标注只允许在新 Task 获准范围内追加，不得改写历史 Review。

## 4. Worktree closeout：13 项事实与 RUN-IPC-1

依据 `worktree-closeout-facts.md` 和 `doc/WORKTREE_SAFETY_INVENTORY.md`。

- 13 个 worktree 全部记录为 `PRESERVE_UNTIL_INDIVIDUAL_CLOSEOUT`。当前 facts 未提供逐项 source/destination/hash/引用/进程完整结果，故清理 Task 应补齐 Resource Manifest 证据和 disposition；已知唯一提交、dirty 或 untracked 的资源一律 `PRESERVE_UNKNOWN` 或更具体的保留类型，不执行物理处置。
- `P14`（HEAD `41c320694273`）和 `P15-C1-FU2`（HEAD `0aa01eddcd75`）的 HEAD 不在当前分支历史：保留 worktree 与提交，列出独有 commit、引用和归属，Codex另行判断后续集成/替代。不得删除或把“HEAD 不可达”当无价值证明。
- `P14` 有 3 tracked dirty + 1 untracked；`P15` 有 2 untracked；`READER-IPC-1` 有 1 untracked。逐项列名、hash、引用与归属；均保留，不能因计数小而忽略。
- **RUN-IPC-1：** 现有事实只有 25 tracked dirty + 1 untracked，未给出 25 项内容/来源。故性质裁定为 `UNKNOWN_DIRTY_PRESERVE`；本证据不足以判断内容是否影响此前 `done`。Owner 后续只读取得逐路径 diff/stat 与哈希，识别是否触及已交付代码、AC 证据、Task/Handoff/Manifest 或纯本地配置；由独立 Reviewer 复核。若任一改动影响先前验收证据或交付内容，Codex暂停对相应结论的当前有效性认定并按具体差异裁决；若可证实均与交付/AC 无关，原 done 结论保持。不得以目前 `done` 推定 dirty 内容已包含在原交付中，也不得擅自更改任务状态。
- 只有完成协作协议 §4.2 所列逐项检查、刷新 Safety Inventory、证明无 dirty/独有 commit/untracked/引用/进程并由 Codex在 approved integration closeout window 明确授权，才可考虑普通 `git worktree remove`。本 Task 草案不授权任何 worktree 移除、迁移或 prune；不使用 `--force`。

## 5. 七个 DONE Task 缺 Resource Manifest

依据 `missing-manifest-resource-facts.md`。七项均补齐 Manifest 事实，不因补表自动回退/确认 `done`：`FEAT-CREATE-1`、`FEAT-CREATE-2`、`FEAT-CREATE-3`、`FEAT-CREATE-4`、`FEAT-IMPORT-MULTI-1`、`P19-UI-FIX-1`、`P19-UI-FIX-2`。

- 对每个 Task 记录准确 worktree source path、注册状态、HEAD/branch、dirty/untracked、资源来源、当前目的地、hash/manifest、引用/进程检查及 disposition。事实不能核实时填 `PRESERVE_UNKNOWN` 并说明；存在引用填 `PRESERVE_REFERENCED`；经证据确认含个人/用户数据时填 `PRESERVE_USER_DATA`。不得为了补齐字段假填 `NOT_APPLICABLE` 或 `DELETE_SAFE`。
- `FEAT-CREATE-2` 的 `worktree: null` 与“真实存在且已注册”的事实冲突。裁定需更正该 frontmatter 到经只读核验的精确已注册 worktree 路径，并在新增 Closeout/Manifest 记录中保留原值 `null`、本次核验依据和更正日期；不得仅在 Manifest 补路径而保留相互矛盾的 frontmatter。更正不改变 done 状态。
- `FEAT-CREATE-1` HEAD 不在当前分支历史：保留 worktree/HEAD 和其关联证据，补记不可达事实与来源，集成状态不据此推定。
- `FEAT-CREATE-3` 1 dirty + 1 untracked、`FEAT-IMPORT-MULTI-1` 50 dirty + 50 untracked：全部列清单与 fingerprint；标 `PRESERVE_UNKNOWN`，在来源/归属和 AC 影响审查前不修改、不迁移、不删除。50 个 dirty 项对 done 的影响尚未证实；如改动涉及交付或验收证据，按 §4 的 RUN-IPC-1 判据由 Codex裁定。
- 其余三个 Task 也只补事实和安全 disposition；worktree 存在本身不触发删除。资源保留可与 done 并存，前提是 Manifest 闭环并符合 §4.2。
- **个人数据门槛：** `workspace.json` 中个人数据快照是否允许保存/归档尚待用户裁决。裁决前不得复制、归档、迁移、重写或删除此类快照；能确认含个人数据的现存对象保留在原位并记录最少必要 hash/元数据，不把内容复制到新证据中。

## 6. 61 个 evidence_dir 未登记文件

依据 `evidence-dir-classification.md`。确认 A/B/C 作为**初始分流提案**，不将文件名分类直接视为最终 canonical/搬迁授权。

- **A：10 个判别力候选。** 逐文件检查是否直接证明某个已释放 AC/Gate、是否为对应 Task 的唯一/最终结果、是否已有相同 Canonical Evidence。只有满足协作协议 §4.1 才登记为 `CANONICAL`（验收结果）或 `SOURCE_PIN`（不可变来源）；否则记录不登记的原因。至少核实 `pytest-core.log`、最终测试日志和 Review 文件的实际内容与 AC 绑定，不能只看名字。
- **B：49 个过程产物候选。** 逐文件检查是否唯一支持已释放 AC、是否有可复核命令/环境/退出码、是否只是重复尝试/临时诊断。能证明纯过程、无当前证据价值的，不列入 Canonical Evidence；但本裁定不授权删除、移动或归档，文件留在原路径，直到另有明确资源处置授权。若是唯一或最终验收证据，则升级为 A 并走逐项核准，不按文件名强制降级。
- **C：`.gitattributes`（`verification/P15-HOST-1/`）与 `.gitignore`（`verification/P19-BOOT-1/`）。** 确认二者都不是 Canonical Evidence，也不得为了消除未登记错误而注册为证据。它们可能控制行尾或忽略规则，故保留在原位置、内容不改、不删除、不移动；另查明规则覆盖范围和当前作用。只有独立治理 Task 明确授权修改且先证明影响后，才可移出证据目录或合并到仓库配置位置。

## 7. 仍须用户裁决的事项（不得由 Codex/DSH代决）

1. 是否把 `doc/REBASELINE_PLAN.md` 的体量上限由 **2500 bytes / 35 lines** 调至 **7000 bytes / 64 lines**；未裁决不改预算。
2. 对 29 个非终态 Task 逐项决定继续、取消、被替代或暂缓；未裁决不改终态、不登记成活动 DAG 节点。
3. 对仍未完成 Acceptance Criteria 的 Task，逐项决定由原 Task 完成、取消或转移到明确 successor；取消/转移不得伪装为通过，须保留原始未完成状态与替代关系。
4. 是否允许 `workspace.json` 含个人数据快照以及该快照可否保留/归档；未裁决不复制、移动、改写或删除。

## 8. 本轮动作

仅写入本裁定文件。未修改 Task、Plan、STATUS、证据事实文件或源代码；未改 pin、未登记 DAG、未改 Task 状态、未运行治理检查/AC 探针，未执行任何 git 写命令、删除、移动、合并或 worktree 操作。

---

# 可直接落盘的 `doc/tasks/GOV-DEBT-CLEANUP-2.md`

以下 YAML 与正文是完整 Task 草案。由于协作协议 §4 要求 Plan/STATUS 登记、依赖/授权与范围冻结后才可将 Task 设为 `ready`，且本 Task 的预算与范围前置裁决尚待用户决定，草案状态为 `proposed`；这不妨碍 DSH 在取得用户裁决后按本文件继续释放流程。

````markdown
---
id: GOV-DEBT-CLEANUP-2
title: 治理债逐项清理与证据/资源闭环
kind: governance
governance_version: 2
status: proposed
approval: pending_user_decisions_and_codex_release
suggested_owner: dsh
owner: null
reviewer: Antigravity
depends_on: []
base_commit: 55ee9e3da8fc2538c44a47c056c2828b293e9050
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-DEBT-CLEANUP-2
allowed_paths:
  - doc/tasks/
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/handoffs/
  - doc/reviews/
  - verification/
  - verification/GOV-DEBT-CLEANUP-2/
---

# GOV-DEBT-CLEANUP-2：治理债逐项清理与证据/资源闭环

## 来源与目标

来源：
- `verification/P09-GOVERNANCE-DEBT-20261019/codex-debt-ruling.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/codex-debt-ruling-r2.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/round5-eol-repin-record.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/sha-mismatch-evidence-chain.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/dangling-dag-facts.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/p02-ac3-branch-evidence-inventory.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/worktree-closeout-facts.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/evidence-dir-classification.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/missing-manifest-resource-facts.md`
- `doc/09_COLLABORATION.md` §4.1 / §4.2 / §5；`doc/templates/TASK.md`；`doc/WORKTREE_SAFETY_INVENTORY.md`。

目标：按 Codex 第二轮逐项裁定，对历史 evidence pin、未登记 DAG Task、P02 AC3 缺失证据、worktree/resource Manifest、DONE Task Manifest 和未登记 evidence_dir 文件形成可复核的逐项 adjudication 及获准的文档修正。所有原始状态、旧 pin、未完成 AC 和资源均保持可追溯；未经用户裁决的范围选择保持阻塞。

### 释放门槛

本 Task 当前为 `proposed`。Codex 只有在以下事项具备可验证记录后才能改为 `ready`：

1. 用户已决定 Plan 预算是否调整；未同意扩容时，Codex须给出不突破现有预算的替代释放范围，不得擅自修改检查器或预算。
2. 用户已对本轮要处理的 29 个非终态 Task 和未完成 AC 作逐项继续/取消/替代/暂缓裁决；仅不受这些决定影响的子项可由 Codex明确拆分后另行释放。
3. `workspace.json` 个人数据快照的用户决定已记录；未裁决时仅允许原位保留和不含内容的元数据记录。
4. Plan/STATUS 的登记方式、依赖、Owner、Reviewer、base、branch/worktree 和 allowed_paths 已由 Codex冻结，并符合协作协议 §4。
5. 新 Task Owner 与 Reviewer 不同；Owner 为 DSH，Reviewer 为 Antigravity。不得由 DSH审查自己的变更。

## Acceptance Criteria

- [ ] **AC1 — 102 条 SHA mismatch 逐行闭环。** 为 `sha-mismatch-evidence-chain.md` 中 102 行各建立唯一结果记录，至少包含 Task、原行/路径、pin commit、原 pin、raw/LF/CRLF 对比、工作区相对 HEAD 状态、分类、来源审查、AC 绑定、处置、授权/Reviewer/Codex 证据。78 条 commit 匹配项不得因后续演进覆盖历史 pin；仅按 Codex批准的替代关系更新活动 pin并保留 superseded 记录。13 条 commit 不匹配项必须追溯 pin 原始来源；找不到来源的标 `BLOCKED_ORIGIN_UNVERIFIED`。11 条叠加 dirty 的项目不得从工作区重钉；须记录 diff/stat/归属并保留 dirty，未解阻即 `BLOCKED_PRESERVE_DIRTY`。另验证 78 条 EOL-only 记录保留原/新值，不重复重钉。证据：逐行 adjudication 表、Reviewer 结果及逐项 Codex 决定。
- [ ] **AC2 — 29 个未登记 Task 逐项状态裁决。** 对 `dangling-dag-facts.md` 中 29 项分别记录现状、Plan/STATUS 指涉、tracked 状态、依赖、交付/集成、未完成 AC、用户授权及建议。10 个未入库文件默认保持 `UNREGISTERED_UNTRUSTED_SNAPSHOT`，不得 `git add` 或写入 DAG，除非有明确用户裁决、来源证明、Codex释放和独立审查。其余项不得因 tracked 就自动登记。仅登记用户确认继续且仍非终态的最小集合；用户确认的终态变更保留原始状态和依据。更新 Plan/STATUS 必须逐项符合协作协议，READY 节点声明准确。任何未裁决项保留原状态并标 BLOCKED。
- [ ] **AC3 — Plan 预算与 DAG 改动符合用户裁决。** 留存用户对 `2500 bytes / 35 lines` 是否扩至 `7000 / 64` 的明确决定。未同意扩容时不得变更上限；同意时只按批准值修改对应预算，并只登记 AC2 中核准的非终态最小集合。提交前后记录 Plan 字节/行数与 DAG 差异。不得通过历史快照、外部清单、伪节点或放宽检查器规避预算。
- [ ] **AC4 — P02 AC3 的 23 条 pin 逐项有结论。** 对 18 条分支上存在文件记录内容 hash、对应 AC、固定源 head 和独立审查结论；只有单独获得 Codex 集成批准后才可在 approved integration window 集成最小集合。对分支上不存在的 5 条引用，逐项只读检索并记录精确来源/head/hash；未找回的保持原引用并标 `MISSING_FROM_FIXED_BRANCH_SOURCE_UNRESOLVED`。只有用户明确取消/转移对应 AC 且 Codex记录替代关系时才移出活动范围。不得合并整个分支、改用绝对路径、静默删除引用或将其称为 integrated。最终状态与证据事实一致。
- [ ] **AC5 — 13 个 worktree 的 Resource Manifest 与安全 disposition。** 对 `worktree-closeout-facts.md` 中 13 项逐一记录精确 source/destination、注册状态、HEAD/branch、dirty/untracked 文件清单及 hash、Task/commit/evidence 引用、进程检查、disposition 与依据。P14、P15-C1-FU2 的不可达 HEAD 和所有 dirty/untracked 项均保留；RUN-IPC-1 的 25 tracked + 1 untracked 必须逐路径说明性质、归属及是否影响已 done 的 AC/交付，由 Antigravity复核、Codex裁决。无法证明无关的保持 `PRESERVE_UNKNOWN` 并暂停相关结论认定；证实不影响交付/AC 的保留原 done 结论。刷新 Safety Inventory 后也不构成删除授权。
- [ ] **AC6 — 七个 DONE Task 补齐 Manifest 且 frontmatter 一致。** 为 `FEAT-CREATE-1`、`FEAT-CREATE-2`、`FEAT-CREATE-3`、`FEAT-CREATE-4`、`FEAT-IMPORT-MULTI-1`、`P19-UI-FIX-1`、`P19-UI-FIX-2` 补齐逐资源 Manifest 和可复核来源。`FEAT-CREATE-2` 将 `worktree: null` 更正为只读核验得到的精确已注册路径，并记录旧值及更正依据。保留 FEAT-CREATE-1 不可达 HEAD；逐项保留 FEAT-CREATE-3 dirty/untracked 和 FEAT-IMPORT-MULTI-1 的 50 dirty + 50 untracked，未证实其对 done 无影响前不作完成性声明。补表不自动回退或确认 done。对用户裁定可保存的 `workspace.json` 个人数据仍采用最小记录；未获裁决时原位保留、不复制/归档/迁移。
- [ ] **AC7 — 61 个 evidence_dir 文件逐项裁定。** 对 `evidence-dir-classification.md` 的 61 项每项记录是否直接支持已释放 AC、是否唯一/最终、现有 Canonical Evidence 重复情况、最终类别和处置依据。10 个 A 候选只有满足 §4.1 才登记 `CANONICAL`/`SOURCE_PIN`；49 个 B 候选只在证实为过程产物后排除出 Canonical Evidence，不能因文件名降级唯一结果。`.gitattributes` 与 `.gitignore` 不是证据，留原位、不改、不删、不移，并记录覆盖规则/用途审查结论。任何搬迁/删除/归档均不在本 Task 授权内。
- [ ] **AC8 — 未完成 AC 的用户范围决定和历史保真。** 对事实文件、关联 Task 与治理检查结果中发现的每个仍未勾选 AC，记录原文、原状态、证据、用户决定（继续/取消/转移/替代/暂缓）、successor 和依据。取消/转移必须由用户授权；不得把未完成写成 PASS，不得删除原始 AC 审计状态。未获决定的 AC 保持未完成并阻止相应 Task DONE。
- [ ] **AC9 — 验证、交接与关闭记录完整。** 每个修正有对应 Task/Handoff/Review/commit 及 evidence pin；变更前后保留只读治理检查输出和适用的逐 Task 检查输出。执行 `pwsh -NoProfile -File tools/governance/check.ps1` 与本 Task 的 `-TaskPath` 检查，保存原始 stdout/stderr、退出码和环境；失败如实登记，不放宽检查器、不把 BLOCKED/NOT_RUN 写为 PASS。Antigravity 对固定 delivery head 独立 Review；Codex批准集成并完成集成后验证及 closeout 后方可设 `done`。

## 允许修改范围

`allowed_paths` 中的相对项目根路径前缀即本 Task 全部写入范围：

- `doc/tasks/`：只限 AC 明确涉及的 Task 文件，补 pin/adjudication、Manifest、`FEAT-CREATE-2` 的 worktree 字段和已获授权的 AC/状态记录。
- `doc/REBASELINE_PLAN.md`、`doc/STATUS.md`：只在对应用户决定及 Codex DAG 登记批准后更新预算、节点、依赖和运行指针。
- `verification/`：只限本 Task evidence_dir 与 AC1–AC9 所列关联 Task 的逐项裁定、资源清单和执行验证证据；不得覆盖来源事实文件。
- `verification/GOV-DEBT-CLEANUP-2/`：本 Task 判别力证据、逐项 adjudication、原始治理检查输出及 Resource Manifest；该 evidence_dir 在 `allowed_paths` 中显式列出。
- `doc/handoffs/`：本 Task 的 Owner Handoff。
- `doc/reviews/`：独立 Reviewer 对固定 delivery head 的 Review。

写入前复核精确文件路径属于上述范围。对 `.gitattributes`、`.gitignore` 仅读取/记录；对 worktree 外部资源仅记录路径/hash/manifest，不写入其内容。

## 禁止范围与不做事项

- 不改 `tools/governance/check.ps1`、产品源代码、测试、Schema、共享契约或依赖。
- 不删、移、归档任何仓外文件，不写 `New.Manga.workspace/`；不删除或移动任何 evidence 文件。
- 不删除任何 worktree，不运行 `git worktree prune`，不使用 `--force`；不改写 dirty/untracked 内容。
- 不合并 `agent/zcode/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION` 或其他未合并分支；不因分支存在就重钉/宣称集成。
- 不执行 `git add` 来提交十个未入库 Task，除非后续有明确用户决定、Codex范围批准和单独释放的写入授权。
- 不覆盖历史 SHA、Review、Handoff、原始 AC 或用户未提交内容；不把证据不全伪装为 DONE。
- 不自动改 Plan 预算、不代替用户决定 Task 继续/取消/替代、不取消/转移 AC、不复制或处置 `workspace.json` 个人数据快照。
- 不执行 AC 探针或产品测试。治理检查仅按 AC9 在该 Task 被释放且检查范围明确后运行。

## 测试与验证计划

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1–AC8 逐项核对 | 使用只读脚本/表格对来源行数、Task ID、pin/hash、路径、Manifest 与裁定字段做逐项对照；对 dirty 资源只读取得 diff/stat/hash | Task 已释放；用户门槛已满足；不得修改来源事实 | NOT_RUN | `verification/GOV-DEBT-CLEANUP-2/` |
| AC3 DAG/预算 | 读取修改前后 `doc/REBASELINE_PLAN.md` 与 `doc/STATUS.md`，核对用户决定、字节/行数及节点集合 | 已有用户预算裁决与 Codex登记批准 | NOT_RUN | `verification/GOV-DEBT-CLEANUP-2/` |
| AC9 全局治理校验 | `pwsh -NoProfile -File tools/governance/check.ps1` | Task 已释放、文档改动完成；保留原始输出和退出码 | NOT_RUN | `verification/GOV-DEBT-CLEANUP-2/` |
| AC9 本 Task 校验 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-DEBT-CLEANUP-2.md` | 同上；evidence_dir 必须列在 allowed_paths；不得用结果替代审查 | NOT_RUN | `verification/GOV-DEBT-CLEANUP-2/` |
| 产品/AC 探针 | 不运行 | 明确排除在 Task 范围外 | NOT_RUN | 不适用 |

实际执行时逐命令记录精确命令、PowerShell 版本、仓库 HEAD、输入文件 hash、stdout/stderr、exit code、执行时间和阻塞；不得把 planned、NOT_RUN 或 BLOCKED 写成 PASS。

## 依赖、风险与阻塞

- `depends_on: []`：本 Task 依赖已落盘的 P09 事实材料与 codex-debt-ruling-r2，不依赖自动提交或合并任何业务分支。
- 用户门槛：Plan 预算；29 个非终态 Task 的逐项范围；未完成 AC 取消/转移；`workspace.json` 个人数据快照许可。逐项记入 adjudication ledger，未决定项保持 BLOCKED。
- 资源风险：dirty/untracked、不可达 HEAD、个人数据、唯一证据及 pinned 文件均按保留处理。发现文件可能影响历史 DONE 结论时暂停该项，交 Codex判断。
- 若用户只裁决部分事项，Codex可拆分出范围已冻结的子 Task；不得由 Owner 自行缩小 AC、解除 blocker 或改写状态。

## 交付与运行记录

- Task 文件：`doc/tasks/GOV-DEBT-CLEANUP-2.md`（本草案由 DSH 持 lease 落盘；落盘后由 Codex核对并登记，不得据此自启动）。
- Handoff：待 Owner 固定 delivery head 后生成 `doc/handoffs/GOV-DEBT-CLEANUP-2-<short-head>.md`。
- Review：Antigravity，针对固定 delivery head；不得由 DSH自审。
- 实际测试：待执行；遵守上表。无产品测试/AC 探针。
- 完成条件：全部已释放 AC 有证据；未决用户项已解除或通过 Codex核准拆分移出本 Task；独立 Review 通过；Codex集成、集成后验证及 Resource Manifest closeout 完成。

## Canonical Evidence

在进入 `in_review` 前，对每项已释放 AC 登记唯一当前证据。原始七份事实文件只读引用，不复制或修改。

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| 待交付 | AC1–AC9 | `verification/GOV-DEBT-CLEANUP-2/` 下逐项文件 | 待填 | 待填 | 待定 |

## Resource Manifest

不得以本 Manifest 授权物理清理。Task 自身 worktree/agent-output 在释放后按实际资源补录；不适用项填 `NOT_APPLICABLE`。任何未知、dirty、独有提交、pinned、个人数据或未跟踪资源均保留。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task worktree | 待释放后记录 | `PRESERVE_UNKNOWN` | 原路径 | 待记录 | 待检查 |
| agent-output / exchange | 待释放后记录 | 待核实 | 原路径 | 待记录 | 待检查 |
| 其余资源 | 无或待核实 | `NOT_APPLICABLE` 仅在实证确认后填写 | — | — | 记录核实依据 |

## Closeout Record

- Closeout date / Codex：待填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：预期均为 0；如获独立授权另行记录。
- 未关闭项及保留原因：列明未裁决用户项、缺失 pin、dirty/untracked 和不可达提交；无则填写“无”。
- 当前指针清理：完成时更新 STATUS / Plan / Task 导航；若用户门槛导致尚未释放或本 Task 被拆分，记录不适用及 successor。
````



