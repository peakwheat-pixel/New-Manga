# GOV-RESOURCE-MANIFEST-SAME-LOCATION-1 集成裁定（r13）

日期：2026-10-20  
范围：仅提供 Codex 集成裁定、执行顺序与收口建议；本轮未集成，未改 Task/Plan/STATUS/代码/测试或资源。

## 2.1 Head 三元组

| 字段 | 值 | 含义 |
|---|---|---|
| `reviewed_head` | `60242f28d` | Review 文件 frontmatter 明确绑定的被审实现 head；不是 Review 文档提交。 |
| `delivery_head` | `d15aae88a` | 实现提交；Task 与 Handoff 的交付 head。 |
| `integration_source_head` | `0a2c45d5e` | worktree 分支最终 tip，包含实现、Task/Handoff 生命周期文档与 DSH Review；这是建议 merge 的源 head。 |

Review 文档本身在 `0a2c45d5e`，Handoff 在 `60242f28d`。closeout 应分别填写上述三元组，另将 `integration_commit` 填为实际 `--no-ff` merge commit（本报告无法预知）。不得把 `reviewed_head` 改成 `0a2c45d5e`：Review 明确批准的是 `60242f28d`，而后续提交是生命周期文档/Review 落盘；本次集成前后验证覆盖 `0a2c45d5e` 的最终内容。

## 2.2 生命周期、证据与资源

### 生命周期裁定

- 当前 `ready` 是 Antigravity 有意保留的原状态。Codex 开始集成收口时，应按协议先核实精确 Review 并转为 **`approved`**（集成窗口）；不能直接从 `ready` 越级标 `done`。
- 完成 merge、集成验证、登记 `integration_commit`、两张清单、Plan/STATUS 更新及 Task checker 后，才转 **`done`**。`superseded` 不适用：没有被替代的 Task/架构。`closed_with_limitations` 也不适用：七项 AC 均有通过证据，且没有待用户接受的未完成 AC。若集成验证出现回归或资源盘点无法闭环，则保持 `approved` 并记录 blocker，不得强行终结。
- closeout 字段：`canonical_evidence_status: complete`；`resource_closeout_status: complete`。这里的 complete 表示证据索引和资源去向逐项登记完成；worktree 内未知/镜像内容保留也可以完整 closeout，不代表已清理。

### Canonical Evidence 应登记项

保留 Task 已有 E1–E6，并补入 Handoff、Review 两行。文件 hash 为当前 worktree 实测值；commit 列是包含该文件的提交。

| evidence_id | AC/Gate | path | 含文件 commit | SHA-256 | class |
|---|---|---|---|---|---|
| E1 | AC1/AC2 | `tools/governance/check.ps1` | `d15aae88aa62a2e49efa1d2e10494d28960621da` | `296266d9e5dec5135e55bbf9bcc9b1d3345ffbf42aa9f5d5485693315bb34e49` | CANONICAL |
| E2 | AC5 | `tools/governance/tests/run-resource-manifest-cases.py` | `d15aae88aa62a2e49efa1d2e10494d28960621da` | `75760a2200e36478b74f1a04ccc57a0000838761556fafc128897974ec82000f` | CANONICAL |
| E3 | AC5 | `tools/governance/tests/fixtures/resource-manifest/cases.json` | `d15aae88aa62a2e49efa1d2e10494d28960621da` | `f229327ac97fed4bde3a6e4c70011f9c77d0e3abf4c411e1131ae4d975db5a9e` | CANONICAL |
| E4 | AC1–AC4 | `verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1/resource-manifest-cases.txt` | `d15aae88aa62a2e49efa1d2e10494d28960621da` | `8a464d86a27e56889c5f490070ba97912c87495b6e3a17910aee8e55fdd03aaf` | CANONICAL |
| E5 | AC5 | `verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1/regression.txt` | `d15aae88aa62a2e49efa1d2e10494d28960621da` | `e6bc294f0c21d36cbb010d51b94248c7cf432486aeab93ec6844de9e6734f01d` | CANONICAL |
| E6 | AC6 | `verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1/task-check.txt` | `d15aae88aa62a2e49efa1d2e10494d28960621da` | `f3b944446667267712fac9fe8b94942c17dbdd46a414d3ed0ac869183cb85c19` | CANONICAL |
| E7 | AC7 / Handoff | `doc/handoffs/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1-d15aae88a.md` | `60242f28d726edda04fd2a0b1791c93c8440233d` | `5436fc10f0ddae5f11c966fd9c7dee166ff0137cbb912e06fa073ad9130dc30b` | CANONICAL |
| E8 | 独立 Review | `doc/reviews/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1-60242f28d-dsh-r1.md` | `0a2c45d5ea41df351e0f529a9b2d46c0784a1e7b` | `219e7e86e4a9ca6b18e399f76e3cc41b8ec4cd6860c274783b1869f3eb6d6bf7` | CANONICAL |

E4–E6 的运行证据落在实现 head；E7 记录交付；E8 绑定被审 head。merge 后文件字节应相同，closeout 仍记录来源 commit 及本次 integration commit。此次 r13 裁定文件可作为本次集成过程记录，但不替代 AC1–AC7 的判别力证据。

### Resource Manifest 应登记项

| resource_type | source_path | disposition | destination_path | manifest / head | 核验结论 |
|---|---|---|---|---|---|
| Task linked worktree | `G:/CODEX/New Manga/.agents/worktrees/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1` | `PRESERVE_UNKNOWN` | 原路径 | branch `GOV-RESOURCE-MANIFEST-SAME-LOCATION-1`; HEAD `0a2c45d5e` | 本轮实测 20 个 untracked 文件、0 tracked modifications；不得 `git clean`、删除、迁移或 prune。刷新 Worktree Safety Inventory 后再作任何后续处置判断。 |
| 镜像归档资料 | 上述 worktree 的 `archive/` | `PRESERVE_UNKNOWN` | 同一 worktree 原路径 | 19 个 untracked 文件 | 与 Task diff 无关不等于可丢弃；来源/引用/用户价值未核实，保留。 |
| workspace 治理文件 | 上述 worktree 的 `doc/WORKSPACE_GOVERNANCE.md` | `PRESERVE_UNKNOWN` | 同一 worktree 原路径 | 1 个 untracked 文件 | 不在 Task `allowed_paths`，不得纳入 merge；保持原位，另行核实归属。 |
| Task 代码与测试 | `tools/governance/check.ps1`; `tools/governance/tests/` | `PRESERVE_REFERENCED` | 主线相同仓库路径 | E1–E3 / integration commit | 已审查且由治理检查器/回归使用，保留。 |
| Task 证据 | `verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1/` | `PRESERVE_REFERENCED` | 主线相同仓库路径 | E4–E6 / integration commit | Canonical Evidence 引用，保留。 |
| Task 专属 task-env / agent-output / exchange | `G:/CODEX/New Manga.workspace/` 对应 Task 子目录 | `NOT_APPLICABLE`（以核实目录不存在为前提） | — | closeout 时检查目录 | 不得仅凭路径假设无资源；如发现即按实际列项、哈希和引用状态。 |

物理处置数量建议记录为 `deleted=0, moved=0, migrated=0, archived=0`。worktree untracked 镜像文件不属于本次 merge source 的 tracked diff；merge 只集成 `0a2c45d5e` 的提交内容，不会自动带入这些 untracked 文件。

## 2.3 集成裁定、命令与验证

### Plan 冲突判断

已逐字比较主 checkout 与 worktree 的 `doc/REBASELINE_PLAN.md`，SHA-256 都是 `2FF3556BB8D2D996748A5A56F94C3C7585035F4E8A91D09DC4704231176F1FFC`。两边文件完全相同，且 worktree 从主 checkout `57ac3c6ae` 建立；**预判 Plan 不冲突**。集成后再检查完整 diff 和状态。

### DSH 在主 checkout 执行的确切命令

先核实仍在预期分支/head，并查看 merge base 与将集成的提交；不要从 worktree 带入 untracked 内容：

```powershell
Set-Location 'G:\CODEX\New Manga'
git status --short
git branch --show-current
git rev-parse HEAD
git -C 'G:\CODEX\New Manga\.agents\worktrees\GOV-RESOURCE-MANIFEST-SAME-LOCATION-1' rev-parse HEAD
git merge-base HEAD 0a2c45d5e
git diff --stat HEAD...0a2c45d5e
git diff --name-status HEAD...0a2c45d5e
```

确认 `HEAD=57ac3c6ae`、源 head=`0a2c45d5e`、差异严格落在 Task allowed paths 后，执行：

```powershell
git merge --no-ff --no-edit 0a2c45d5e
```

本报告作者没有执行以上 Git 写命令。若实际主线 HEAD 已变化，先检查共同祖先及新增差异，再决定是否重放；不得照抄旧基线直接合并。

### 集成后验证清单

在主 checkout、merge commit 上顺序运行并保存完整 stdout/stderr/exit code：

```powershell
python tools/governance/tests/run-resource-manifest-cases.py
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1.md
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P19-UI-FIX-1.md
```

验收：离线套件 32/32、exit 0；Task checker 与全局 checker 均 0 errors（已知 1 warning 可按原意保留）；P19 checker 中五个 `Same ...` 错误消失，真实 isolation path 错误仍在。逐一核对 case 29–32 的负向预期仍为 True、没有 fixture 残留；检查 merge diff 仅有授权路径变化。最后登记真实 merge commit、更新证据/资源行及状态，并运行 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1.md` 作为最终 closeout gate。若结果不同于预期，暂停 `done` 状态转换并查明原因。

### P19 检查现场基线

本轮在未集成主 checkout 实测：**9 errors / 2 warnings**，其中 5 个 `Same ...` sentinel 都仍报 `Resource 最终路径未验证`。DSH Review 在 worktree 实测 P19 为 **5 errors / 7 warnings**，属于修复代码后的 worktree 结果。故当前主 checkout 尚未获得修复；本报告不把 worktree 结果冒充集成结果。合并后重跑后，预期为消除 5 个 sentinel 错误；具体剩余计数以主线实测为准。

## 2.4 Plan / STATUS 收口内容

Task 从 `ready` 终态到 `done` 后，Plan 对应节点替换为：

```markdown
|GOV-RESOURCE-MANIFEST-SAME-LOCATION-1|GOV-RESOURCE-MANIFEST-JSON-1|done（同源/空/`-` 目的地语义；实现 `d15aae88a`，Review `60242f28d`；集成源 `0a2c45d5e`）|
```

Plan 末尾 READY 行替换为：

```markdown
READY 节点：ARCH-DOC-REBASELINE、P20。in_review：HARDEN-2。done：**35 项**。
```

完整 Plan（除上述行外其余保持主线原文）：

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
|GOV-RESOURCE-MANIFEST-SAME-LOCATION-1|GOV-RESOURCE-MANIFEST-JSON-1|done（同源/空/`-` 目的地语义；实现 d15aae88a，Review 60242f28d；集成源 0a2c45d5e）|
|P20-CLOSE-BOUND-1|P20-ISOLATION-1|closed_with_limitations（R6）|
|P20-CLOSE-BOUND-HARDEN-1|P20-CLOSE-BOUND-1|closed_with_limitations|
|P09-AC3-DELETE-HARDEN-1|P09-AC3-DELETE-1|closed_with_limitations（未集成）|
|P09-PREVIEW-LIFECYCLE-RECLAIM-1|P09-AC3-DELETE-HARDEN-1|closed_with_limitations（AC6 未满足；未集成）|
|GOV-PLAN-BUDGET-1|—|done|
|RUST-ENV-BASELINE-1（P20-CLOSE-BOUND-1）/ P07交互补缺（P02）/ P21旧栈归档（P20+另授权）|—|proposed（P07/P21可选）|
|P22 响应归属|P22-REBASE-1|已集成；P04 不放行，H1/P2-1/13 与 BC-AC5 缺项保留。已完成见各节点行。|
READY 节点：ARCH-DOC-REBASELINE、P20。in_review：HARDEN-2。done：**35 项**。
```

**READY 声明裁定：是。** 本 Task 完成后，在 Plan 中 READY 只剩 `ARCH-DOC-REBASELINE`、`P20`；`P19-UI-MANIFEST-VIEW-1` 已是终态，SAME-LOCATION-1 转入 done，不再列 READY。没有据此新释放其他 Task。

### STATUS 是否修改及完整替换内容

需要更新 DAG 权威指针中的终态列表，登记本 Task 已完成；当前 Task 仍是 P20，不改变唯一 Active Task。主 checkout 实测 `doc/STATUS.md` 为 **3142 bytes**（不是所报 3169；27 行），候选完整替换内容为 **3182 UTF-8 bytes / 27 行**，低于 3200 bytes / 45 lines 限制。写入时按 UTF-8 无 BOM 实测：

```markdown
# Current Development Status

状态刷新：2026-10-19；主控 dsh（epoch 8，唯一 Active Coordinator）。

## 当前 Task

- 当前 Task：[P20](tasks/P20.md) **ready**。**AC1/AC2/AC7 ✅**；**AC3 ✅**（455.1 MB，见 [P20-MEM-OPT-1](tasks/P20-MEM-OPT-1.md)）；**AC6 ✅**（[P20-ISOLATION-1](tasks/P20-ISOLATION-1.md)：12/12）；**AC4 ◐**（延迟 36.0 ms；帧率见 [P20-AC4-FPS-1](tasks/P20-AC4-FPS-1.md)）；**AC5 ✅**（76.54 ms、零残留）。
- READY：[ARCH-DOC-REBASELINE](tasks/ARCH-DOC-REBASELINE.md)（AC7 已完成；AC1–AC3 PARTIAL、AC4–AC6 属消费者责任，不标 done）。
- P20：[FPS-1](tasks/P20-AC4-FPS-1.md) 集成 `approved`；AC3 `NOT_RUN`（Coordinator），AC5 `NOT_VERIFIED_BY_RULING`；HARDEN-1 R4 `changes_requested` → 已 `closed_with_limitations`，R4-01 由 HARDEN-2 承接；AC7 `NOT_RUN`。
- **新增**：[RUST-ENV-BASELINE-1](tasks/RUST-ENV-BASELINE-1.md) `proposed`（12 项 Rust 环境依赖失败）；**REBALANCE**：ZCode 遇 429 限流。
- **READY 待派**：[GOV-DEBT-CLEANUP-1](tasks/GOV-DEBT-CLEANUP-1.md) `blocked`（待用户裁决）。HARDEN-1/2：`closed_with_limitations`/`in_review`（HARDEN-2 仅 AC5 需人工）。
- **P09 已收口**：[P09-AC3-DELETE-1](tasks/P09-AC3-DELETE-1.md) `closed_with_limitations`（R3 `changes_requested`）。**P09 AC3 保持 `BLOCKED`。** **HARDEN-1 删除路径闭环；AC4 判 FAIL 转出。**
- **T2**：4 failed 中 3 项在 `HEAD~` 已失败；1 项由 `d9f7a628c` 引入（v5 断言）。
- **P02**：16 份入库、3 份恢复 HEAD、`report.json` 待裁决；见 [逐份评估](../verification/P02-DOC-PROVENANCE-1/per-file-verdict.md)。
- **待裁决**：P18/G25/BL-12/13。
- DIR-2：Task Owner=codex；DIR-3：只保留一个 Active Coordinator；**DIR-4：同一失败上限 2 次，超限停手上报**（P20 两子项各经用户豁免 1 次）；DIR-5：goal 轮次上限 1000。
- Coordinator=dsh，epoch=8，lease=39640ba370ec4a7cade35c1abd67f234（LEASE_VALID）；20 份具名文件已按裁决处置，原件 20/20 备份于 `New Manga.workspace/P02-DOC-DISPOSAL-20261018/`。
- 恢复点：`verification/PROJECT-ORCHESTRATION-20261016/`（checkpoint-r12）；日志 `.orchestrator/{INFLIGHT,OPLOG}`。

## Gate 与保留项

Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。H1/P2-1/13缺项、BC-AC5 PARTIAL、backlog 保留。用户未提交内容保留，不push/删除。**P20 发布 Gate 已实测通过**（`bundle==resource`；四页可达）。

## 当前权威指针

- DAG：[REBASELINE_PLAN](REBASELINE_PLAN.md)；READY=ARCH-DOC-REBASELINE、P20；BLOCKED=GOV-DEBT-CLEANUP-1；`proposed`=MANAGED-READ-ROOT-TRUST-1；`in_review`=P20-CLOSE-BOUND-HARDEN-2；已终态：PREVIEW-LIFECYCLE-RECLAIM-1、P09-AC3-DELETE-HARDEN-1、GOV-RESOURCE-MANIFEST-SAME-LOCATION-1。
- 本轮证据：P09 [R3](../verification/P09-AC3-DELETE-1/codex-review-r3.md) + [T2](../verification/P09-AC3-DELETE-1/t2-fullsuite-triage.md)；P20 [CB-R4](../verification/P20-CLOSE-BOUND-HARDEN-1/codex-review-r4.md) + [FPS-R4](../verification/P20-AC4-FPS-1/codex-review-r4.md)。
```

## 2.5 GOV-DEBT-CLEANUP-2 AC6 与剩余五类错误

本轮在主 checkout 读取 `GOV-DEBT-CLEANUP-2` AC6 和其 `ac6-manifest-backfill.md`：AC6 要为七个 DONE Task 补 Resource Manifest 事实；P19-UI-FIX-1 的旧记录明确因 checker 不能解释四种 destination 而保留原状。该范围是**资源事实登记**，不是修所有 P19 校验错误或物理处理资源。

| 主线集成后仍需核对的错误 | AC6 归属 | 判定/后续处理 |
|---|---|---|
| `Evidence SHA-256 不匹配：frontend-npm-test-final.log` | 否 | 属 SHA 来源/字节差异的只读分类，落 `GOV-DEBT-CLEANUP-2` AC1 的 102 行核对；不由 AC6 改 pin。 |
| `Evidence SHA-256 不匹配：frontend-npm-build-final.log` | 否 | 同上，AC1。 |
| `Evidence SHA-256 不匹配：verification/P19/import-no-response-r4.md` | 否 | 追溯 SOURCE_PIN 的提交、原始字节/EOL 与工作区状态，属 AC1；仅凭 hash mismatch 不重钉。 |
| `DONE evidence_dir 含未登记文件：（8 个）` | 否 | 文件逐项归类属 AC7（61 项 evidence_dir 分类）；只读记录其内容、用途、是否唯一最终证据，不因未登记而删除或自动加 pin。 |
| `Resource 最终路径未验证：apps/desktop/src-tauri/target/p19-ui-fix-1-isolation-20261017` | **是，资源事实部分** | AC6 必须记录目标实际不存在/未验证并标 `PRESERVE_UNKNOWN`；这满足事实盘点要求，但不证明历史去向，也不消除此项 checker 错误。需要独立只读 provenance Task 核实“曾创建后清理 / 从未创建 / 去向未知”，不可创建、恢复、移动或删除路径。 |

集成 SAME-LOCATION-1 后，5 个精确 `Same ...` 路径错误应消失；列表中仍列的真实 isolation 路径错误不属于同源解析，必须保持失败，直到有独立证据证明目的地现状并另行获准更新 Manifest/Task。AC6 可以在其余六个 Task 与 P19 的资源事实均按来源核实、未知项均显式保留后判达成；AC6 **不要求**把未知资源路径“修成通过”。AC1、AC7 各自按来源完成后也可关闭，剩余报错是证据债事实，不是改 pin/删文件的授权。

**关于 GOV-DEBT-CLEANUP-2 整体终结：**不能仅因 AC6 解除就自动终结。若 AC1–AC9 全部完成、独立 Review 通过、Codex 集成及集成后验证通过、资源 Manifest 闭环，应按协议置 `done`。若仍有未完成 AC，`closed_with_limitations` 只可在用户明确裁决接受限制后由 Codex使用，并保留原 AC/Finding 状态和 closure evidence；目前用户尚未在本任务中作该取舍，因此这里仅给技术建议：**优先完成已授权的只读 AC1/AC7 与独立路径核实，不建议现在判 `closed_with_limitations`。**

## DSH 按序执行

1. **只读预检**：在 worktree 核对 Task status=`ready`、Task `delivery_head=d15aae88a`、Review `reviewed_head=60242f28d`/`APPROVED`、branch tip=`0a2c45d5e`；重算 Task 表 E1–E6 及 E7/E8 文件 SHA；确认 Plan 两份哈希相同。不得改 Task 或源清单。
2. **来源与范围检查**：核对 `git diff HEAD...0a2c45d5e` 只落 `allowed_paths`；将 worktree 20 个 untracked 文件按本报告资源表记录为保留镜像，确保不 stage、不 merge、不清理。
3. **交接给 Codex**：把本报告、三元组、哈希和核对结论完整交给 Codex；DSH 不执行 merge、不改 Plan/STATUS/Task 生命周期字段。
4. **Codex 主线集成**：在确认当前 HEAD 未漂移后，按 2.3 命令 `git merge --no-ff --no-edit 0a2c45d5e`；记录生成的 integration commit 和完整 diff。
5. **集成后验证**：按 2.3 顺序跑 32-case 离线套件、Task/global checker、P19 checker；保存完整日志/退出码。失败或结果偏离预期则 Task 留在 `approved`，提交诊断，不改 P19 JSON 或资源。
6. **Codex closeout**：补 E7/E8、merge commit 和资源核实结果；更新 Task 的 integration/closeout 字段、Plan/STATUS，测 STATUS 字节/行并运行 Task checker；全部通过后设 `done`。另把 P19 真实 isolation path 的只读核实作为独立 Task 释放，不让 DSH 在本次集成中扩围。
7. **GOV-DEBT-CLEANUP-2**：DSH 继续按其 AC1、AC7 做只读分类，AC6 将 P19 未验证 isolation destination 标 `PRESERVE_UNKNOWN`；各自保存证据。仅当 AC1–AC9、独立 Review、集成及资源 closeout 全满足，或取得明确用户 limitation 裁决后，再由 Codex决定终态。

## 主 checkout Git 状态前后对比

- 动手前 `git status --porcelain --untracked-files=all`：**1592 entries**；将输出以 LF 连接后的 SHA-256 为 `1E64A0A86B26947BA824AE9F584D04664F647677621A9D1AAC29D6F8FA1036AF`；目标文件此前不存在。
- 动手后预期：原有 1592 条全部保持，只新增本报告一条 `?? verification/P09-GOVERNANCE-DEBT-20261019/codex-integrate-sameloc-r13.md`，合计 **1593 entries**。完成写入后再实测 SHA-256 并在最终回复报告；不应有任何其他 porcelain 差异。
- 本轮未执行 Git 写命令、未调用 `coordinator-lease.py`、未 merge、未运行测试；仅运行只读 P19 checker 来核实错误现状。