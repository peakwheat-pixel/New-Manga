# GOV-DEBT-CLEANUP-2 Closeout 裁定（r14）

日期：2026-10-20（Asia/Shanghai）  
裁定人：Codex / Lead、Architect、Integrator  
范围：仅形成 `GOV-DEBT-CLEANUP-2` 的 closeout 建议、证据/资源登记清单、Plan/STATUS 建议、AC7 后继范围裁定和 1233 文件的技术建议。本轮只新增本文件；不改 Task、Plan、STATUS 或其他证据，不执行 Git 写操作、merge、测试或 `coordinator-lease.py`。

## 1. 核实基线与终态

主 checkout：`G:\CODEX\New Manga`；branch `antigravity/P09-AC3-DELETE-HARDEN-1`；HEAD `2636301fe5d6c33535f873aeb776c3e4beb5dd2d`。Task 当前为 `in_review`，Review `doc/reviews/GOV-DEBT-CLEANUP-2-94c8dcdab-antigravity-r2.md` 绑定 `reviewed_head=94c8dcdabc20f622579cec742cfcd751082693c8`，结论 `APPROVED_WITH_LIMITATIONS`。Task 当前 frontmatter 的 `delivery_head=e63d9324766db0d381bad24b3fc60a58048430e1`，与 Handoff frontmatter 相符。最终主线 HEAD 包含 Review 落盘及其后的记录修正。

AC 事实按交付记录及 Antigravity Review 裁定：AC1 `102 = 78 + 13 + 11` 达成；AC2 29 项、AC3 7000/64、AC4 25 项（21 存在/4 缺失）、AC5 13 项保留、AC6 七项补录、AC8 69 项达成。AC4 的 23/18/5 → 25/21/4 是正确更正。AC1 的 105/79/14/12 曾是错误更正，原因是把表内三行汇总计入数据；它已撤销并记入证据。二者不可混为一谈。

### 1.1 终态

裁定为 **`closed_with_limitations`**，不是 `done`。AC7 明确要求逐项判断 61 个候选文件是否为某个已释放 AC 的“唯一最终证据”；当前 AC7 证据明确承认没有完成此判断，因此是未达成项，不能勾选或以 AC9 closeout 抵消。保留原 `[ ] AC7`、原 Review verdict 和相关 finding；closeout evidence 记录 limitation，不将其重写为 PASS。此终态使任务成为终态节点，不属于 READY，也不把未完成 AC 隐藏为完成。

### 1.2 Head 三元组与 integration_commit

| 字段 | 应记值 | 依据 |
|---|---|---|
| `reviewed_head` | `94c8dcdabc20f622579cec742cfcd751082693c8` | Review frontmatter 固定的被审查提交。 |
| `delivery_head` | `e63d9324766db0d381bad24b3fc60a58048430e1` | 当前 Task/Handoff 交付字段；不得为贴合最终 HEAD 而改成未被 Review 直接指向的提交。 |
| `integration_source_head` | `2636301fe5d6c33535f873aeb776c3e4beb5dd2d` | 主 checkout 最终 HEAD，含后续 AC1 撤销记录、AC4 正确更正及 Review 落盘。 |
| `integration_commit` | `2636301fe5d6c33535f873aeb776c3e4beb5dd2d` | 本任务已直接提交在目标主线；以当前集成端点记录，不伪造 merge commit。 |

核实的提交关系：`e63d932` 是 `94c8dcd` 的祖先，Review head 是 `2636301` 的祖先；最终 HEAD 为现有主线上的后续提交。DSH 的交付并非一个尚待集成的独立分支，且本 Task linked worktree 不存在。故结论是**无需 merge**，不要运行 `git merge --no-ff`。如生命周期字段要求 `integration_commit`，填现有最终主线提交 `2636301…`，并在 closeout 说明其为直交付集成端点，非 merge commit。无需另造空 merge commit。

这与 `GOV-RESOURCE-MANIFEST-JSON-1`、`P19-UI-MANIFEST-VIEW-1`、`GOV-RESOURCE-MANIFEST-SAME-LOCATION-1` 的 worktree→merge 流程不同，是可解释的执行拓扑差异：本 Task 的提交从开始就在主线 checkout，前三者有独立 worktree/source head。应将差异写入本 closeout（本节）及正式 Task closeout/integration notes，注明 source head、目标 branch/head、无 worktree、无 merge 和直接提交事实；**不**把 `--no-ff` 当作所有 Task 的固定 Gate，也无需为了形式一致补造 merge。未来如有独立分支集成，仍按普通 merge 流程记录实际 merge commit。

## 2. Canonical Evidence 清单

Task 当前已有 10 个文件 pin（AC1–AC9 与 finding），加上独立 Review 和 Handoff，共应完整登记 **12 行**。下表 SHA-256 是本轮对工作树当前字节实测值；包含文件的提交由只读 `git log --all --format='%H' -- <path>` 实测。此处提供应登记清单，不代表本轮改写了 Task 表。

| evidence_id | AC/Gate | path | 含文件 commit | SHA-256 | class |
|---|---|---|---|---|---|
| EVID-DEBT-AC1 | AC1 | `verification/GOV-DEBT-CLEANUP-2/ac1-sha-rows.md` | `009d009e47e12f6efc2f5d425aba0b3dd1c2efd5` | `6bdc98d5be79e5be7cc002981ef57ad8cba4f2a8c1714202b50cdd260386f3f7` | `CANONICAL` |
| EVID-DEBT-AC2 | AC2 | `verification/GOV-DEBT-CLEANUP-2/ac2-deferred-tasks.md` | `9be9bab21b70714f3102220f43170de813788995` | `5f2f410b60a959b9c55f6ea89ea15b033bab1fb4e229739eef8ea9edd1bcfc04` | `CANONICAL` |
| EVID-DEBT-AC3 | AC3 | `verification/GOV-DEBT-CLEANUP-2/ac3-budget-decision.md` | `9be9bab21b70714f3102220f43170de813788995` | `0287ac3c083b1226e2598a589e7507c2ebf22f18c979a54f1e71c77e659bbf17` | `CANONICAL` |
| EVID-DEBT-AC4 | AC4 | `verification/GOV-DEBT-CLEANUP-2/ac4-p02-ac3-pins.md` | `cfd920ba2eb7d6b1e0f9bf9224151f2e0715d80a` | `73892ee7faea0c11288fa96aa1f74b832dbba65f8a12a76ad76c5157c7e77ccb` | `CANONICAL` |
| EVID-DEBT-AC5 | AC5 | `verification/GOV-DEBT-CLEANUP-2/ac5-worktree-preserve-list.md` | `5b5c3e299a4e478aff86e12bd923a23c293f70e2` | `e0c582a6a0f9391febae94511f1d3611d80606a10317a0bf4a729aa8f98d8594` | `CANONICAL` |
| EVID-DEBT-AC6 | AC6 | `verification/GOV-DEBT-CLEANUP-2/ac6-manifest-backfill.md` | `4d55bd633c798e60f8dbf3c2bb11e247df554d91` | `94d7df55b7d4a88502f9fcb21e6a90e1299c1549cce461c876f740634d2b5000` | `CANONICAL` |
| EVID-DEBT-AC7 | AC7 | `verification/GOV-DEBT-CLEANUP-2/ac7-evidence-dir-files.md` | `5b5c3e299a4e478aff86e12bd923a23c293f70e2` | `8ec36c265967a7f45443bfb71c4608cd11bafc8a4d119085bbd15b354a7a5393` | `CANONICAL`（记录分类及未判定边界，不证明 AC7 完成） |
| EVID-DEBT-AC8 | AC8 | `verification/GOV-DEBT-CLEANUP-2/ac8-open-acs.md` | `4e9bbe04bb3b46f6812e7ce40ea89a0a491df28a` | `fb61c70f2638f2b1b4d1bbdd3ae34ec1dc6bb620aabb4dca81eb25a2b20a4377` | `CANONICAL` |
| EVID-DEBT-AC9 | AC9 | `verification/GOV-DEBT-CLEANUP-2/ac9-governance-output.txt` | `e63d9324766db0d381bad24b3fc60a58048430e1` | `f2db42f794f8185cc7a0f68cdf78d3a7ce80b2ddddb51151151dcf97a6ccd4a4` | `CANONICAL` |
| EVID-DEBT-FINDING | 治理检查器 finding | `verification/GOV-DEBT-CLEANUP-2/finding-checker-not-tracked.md` | `e09cad1ed7b748ac8c9f17f8245d0f4e1390fabd` | `a7a60f5c5df55bd5c99af0fab3422090f9136524ffb3bb21c93136e4fd05cd8f` | `CANONICAL` |
| EVID-DEBT-REVIEW | 独立 Review | `doc/reviews/GOV-DEBT-CLEANUP-2-94c8dcdab-antigravity-r2.md` | `2636301fe5d6c33535f873aeb776c3e4beb5dd2d` | `0af11140083d8ab9c38d80d38ef526a05ba3f8659be06f2513a5f5299e27531a` | `CANONICAL` |
| EVID-DEBT-HANDOFF | DSH Handoff | `doc/handoffs/GOV-DEBT-CLEANUP-2-e63d9324766.md` | `fbc4fb452515522b25d25b469a7e6cae9226484f` | `99ae37cb45cfc2522d35f9626f1a88b6f6998f5f4e42d91efc44c994d14e0d53` | `CANONICAL` |

复核/重算方法（PowerShell）：

```powershell
$path = 'verification/GOV-DEBT-CLEANUP-2/ac1-sha-rows.md'
Get-FileHash -Algorithm SHA256 -LiteralPath $path
git log --all --format='%H' -- $path | Select-Object -First 1
git cat-file -e '<commit>:<repo-relative-path>'
```

对 Review、Handoff 同样运行；每行的 commit 必须能 `git cat-file -e` 找到该路径，SHA 必须针对该路径当前版本重算。若 closeout 时文件字节或引用 commit 漂移，更新 pin 为真实值，不沿用本表旧值。Closeout 文件本身只能在其被提交后登记：写入时不存在可填的 commit，不能虚构；提交后如需把它当 closure evidence，再以包含它的实际 commit 与 SHA256 增列。

## 3. Resource Manifest 裁定

本 Task 的 tracked 写入范围只涉及 `doc/tasks/GOV-DEBT-CLEANUP-2.md` 和 `verification/GOV-DEBT-CLEANUP-2/`，没有生产代码、测试或产品数据变更。Task 声明的 worktree 路径不存在；本轮核实 `G:\CODEX\New Manga.workspace\worktrees\GOV-DEBT-CLEANUP-2` 不存在，实际提交直接落在主 checkout 的目标 branch。主 checkout 是共享工作区，不应冒称为本 Task 专属 worktree。

| resource_type | source_path | disposition | destination_path | sha256 / manifest | 引用/进程核验与结论 |
|---|---|---|---|---|---|
| Task worktree | `G:\CODEX\New Manga.workspace\worktrees\GOV-DEBT-CLEANUP-2`（Task 原字段另写该路径） | `NOT_APPLICABLE`（未创建） | — | 不适用；无 worktree HEAD/status | 路径不存在；实际在主 checkout 提交。不得登记为已清理的 worktree，也不得删除主 checkout。 |
| Task、Handoff、Review 文档 | `doc/tasks/GOV-DEBT-CLEANUP-2.md`；`doc/handoffs/GOV-DEBT-CLEANUP-2-e63d9324766.md`；`doc/reviews/GOV-DEBT-CLEANUP-2-94c8dcdab-antigravity-r2.md` | `PRESERVE_REFERENCED` | 原路径 | Task/Review/Handoff pins 见 §2；closeout 的 Task 版本需随后补实际 pin | 当前生命周期、交付和 Review 依据；保留。 |
| AC1–AC9 与 finding evidence | `verification/GOV-DEBT-CLEANUP-2/`（10 份） | `PRESERVE_REFERENCED` | 原路径 | §2 的 10 行 Canonical Evidence | 被 Task/AC/Review 引用；保留。 |
| task-env / dataset / model / test material | Task 对应 workspace 子目录 | `NOT_APPLICABLE`（本轮检视的 task-env、dataset/model/test-material 目录均无已知实例） | — | 目录检查；详见本节范围限制 | 未发现该 Task 专属环境/数据资源。 |
| agent-output / exchange / temp / artifact | Task 对应 `G:\CODEX\New Manga.workspace\` 子目录 | `NOT_APPLICABLE`（本轮核实的 agent-output、exchange、task-env 目标目录不存在） | — | 目录存在性检查；没有待迁移 manifest | 本轮没有此类专属派生产物；如之后发现新路径或外部输出，closeout 不得沿用此结论，应补列并核对引用。 |
| 主 checkout 中其他 dirty/untracked 内容 | `G:\CODEX\New Manga`（共享主 checkout） | `PRESERVE_UNKNOWN`，不纳入本 Task 资源或交付 | 原路径 | 本轮前 `git status --porcelain --untracked-files=all` 为 1592 entries，状态文本 SHA-256 `1e64a0a86b26947ba824ae9f584d04664f647677621a9d1aac29d6f8fa1036af` | 既有内容属原作者；本轮不清理、不归档、不迁移，也不把它们误列为本 Task 的产物。 |

closeout 的 `resource_closeout_status` 可为 `complete`，含义是资源类别已盘点、无本 Task 专属未决资源，非“所有主 checkout dirty 内容都已处置”。物理删除/移动/迁移/归档计数均为 0。若要求 `NOT_APPLICABLE` 作为严格的“资源不存在”结论，后续正式写回前应对 Task 所有专属 workspace 类别做一次按任务名的目录核对；上述记录已明确其核验边界，不对仓库外任意位置作全称推断。

## 4. 集成、Plan 与 STATUS

### 4.1 集成顺序

无需 merge。不得创建空 merge commit。若之后在获准的生命周期写入窗口更新 Task/Plan/STATUS，顺序建议如下；以下是待执行命令，**本轮未运行**：

1. 只读确认 `git branch --show-current`、`git rev-parse HEAD`、Task 当前状态及 dirty 文件归属；不 stash、不覆盖作者内容。
2. 确认当前 HEAD 仍为 `2636301fe5d6c33535f873aeb776c3e4beb5dd2d` 或其明确后继，且 `e63d932`、`94c8dcd`、Review 与 10 份 evidence 的引用路径/哈希仍对应 §2。
3. 在 Task/closeout lifecycle record 写入三个 head 与 `integration_commit=2636301fe5d6c33535f873aeb776c3e4beb5dd2d`；说明直接主线交付、无独立 worktree/source 分支、无 merge commit。
4. 完成 Canonical Evidence 与 Resource Manifest 行更新，保持 AC7 未勾选，Task 状态改为 `closed_with_limitations`；Plan 和 STATUS 对应更新。
5. 按本项目协作协议执行只读治理检查和当前 Task 检查；任何失败如实记录，不为通过而改 checker/预算。本 r14 授权仅允许写本报告，所以这些正式 lifecycle 文档写入不属于本轮实际执行。

### 4.2 Plan 当前行与替换行

当前行：

```markdown
|GOV-DEBT-CLEANUP-2|—|approved（AC6 的 P19-UI-FIX-1 格式债务；AC7 的 61 项归属未结）|
```

建议替换为：

```markdown
|GOV-DEBT-CLEANUP-2|—|closed_with_limitations（AC1–AC6/AC8 达成；AC7 仅完成 61 项候选分类，唯一最终证据判定未做；closeout r14）|
```

当前 `doc/REBASELINE_PLAN.md` 是 2909 UTF-8 bytes / 38 lines；上述仅替换一行后，保留 DONE 数量 34（本 Task 是 `closed_with_limitations`，不计入 done），READY 声明仍是 `ARCH-DOC-REBASELINE、P20`。因而 READY 节点确实只有这两项；除此之外仍存在非 READY 状态：`in_review` 的 HARDEN-2，`blocked` 的 GOV-DEBT-CLEANUP-1，`proposed` 的 RUST-ENV-BASELINE-1 / P07 / P21 等，以及多个终态节点。不得把“READY 只有两项”误述为“计划中只剩两个工作项”。

建议 Plan 完整内容（只替换上表目标行，其余保持当前文本）：

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
|GOV-DEBT-CLEANUP-2|—|closed_with_limitations（AC1–AC6/AC8 达成；AC7 仅完成 61 项候选分类，唯一最终证据判定未做；closeout r14）|
|GOV-RESOURCE-MANIFEST-JSON-1|GOV-PLAN-BUDGET-1|done（外部 JSON Manifest 检查器；19/19 用例；集成 3fe78a67c）|
|P19-UI-MANIFEST-VIEW-1|GOV-RESOURCE-MANIFEST-JSON-1|closed_with_limitations（AC1/AC2/AC4/AC5/AC6 达成；AC3 因 4→10 错误清单失败；按 Codex r11 保留修正）|
|GOV-RESOURCE-MANIFEST-SAME-LOCATION-1|GOV-RESOURCE-MANIFEST-JSON-1|done（同源/空/\- 目的地语义；32/32 用例；集成 4b545eada；P19 错误 9→4）|
|P20-CLOSE-BOUND-1|P20-ISOLATION-1|closed_with_limitations（R6）|
|P20-CLOSE-BOUND-HARDEN-1|P20-CLOSE-BOUND-1|closed_with_limitations|
|P09-AC3-DELETE-HARDEN-1|P09-AC3-DELETE-1|closed_with_limitations（未集成）|
|P09-PREVIEW-LIFECYCLE-RECLAIM-1|P09-AC3-DELETE-HARDEN-1|closed_with_limitations（AC6 未满足；未集成）|
|GOV-PLAN-BUDGET-1|—|done|
|RUST-ENV-BASELINE-1（P20-CLOSE-BOUND-1）/ P07交互补缺（P02）/ P21旧栈归档（P20+另授权）|—|proposed（P07/P21可选）|
|P22 响应归属|P22-REBASE-1|已集成；P04 不放行，H1/P2-1/13 与 BC-AC5 缺项保留。已完成见各节点行。|
READY 节点：ARCH-DOC-REBASELINE、P20。in_review：HARDEN-2。done：**34 项**。
```

### 4.3 STATUS

建议在 `doc/STATUS.md` 的“当前权威指针”终态列表增加 `GOV-DEBT-CLEANUP-2`；READY 仍列 `ARCH-DOC-REBASELINE、P20`，不新增 Active Task，不改 P20 当前 Task 指针。当前 STATUS 实测 3142 bytes / 27 lines，上限 3200/45，余量仅 58 bytes。应做**最小替换**：将当前行中的 `已终态：PREVIEW-LIFECYCLE-RECLAIM-1、P09-AC3-DELETE-HARDEN-1。` 改为 `已终态：GOV-DEBT-CLEANUP-2、PREVIEW-LIFECYCLE-RECLAIM-1、P09-AC3-DELETE-HARDEN-1。` 并立即按 UTF-8 实测字节数；新增 ID 约 21 bytes，仍可能在限制内，但应以实测为准。若超过 3200，精简该行既有说明但不删权威状态，不放宽 checker 限制。正式变更时应运行 Task checker 与全局 checker；本轮未运行。

## 5. AC7 未完成项裁定及后继 Task

**裁定：AC7 的“唯一最终证据”是留债，不放弃。** 这是冻结 AC 的明文要求，且 Canonical Evidence 生命周期要求对已释放 AC 登记当前判别力证据。仅有 61 个文件的路径/候选分类，不能推出哪些文件是 AC 的唯一最终证据，也不能确保每个已释放 AC 有可复核证据。把这要求改判为“过度要求”会追溯改写 Task AC/验收口径；没有来源授权这样做。因此本 Task 保持 limitation，后继 Task 承接未完成判定，不自动恢复本 Task。

以下是范围完整、可用于释放的 Task 内容草案。由于本轮授权只允许写 r14 文件，且未创建该 Task 的 branch/worktree，**不能诚实地声称它已经是协议状态 `ready`**；草案在登记真实 worktree 路径、base/head、STATUS/Plan 指针后由 Codex 置 `ready`。建议 Owner=DeepSeek Harness（只读分类/证据核查），Reviewer=Antigravity（独立审查）；二者不同。

```markdown
---
id: GOV-EVIDENCE-UNIQUE-1
title: GOV-DEBT-CLEANUP-2 AC7 唯一最终证据判定
kind: governance
governance_version: 2
status: proposed
approval: codex_scope_release_required
suggested_owner: dsh
owner: dsh
reviewer: Antigravity
depends_on: [GOV-DEBT-CLEANUP-2]
base_commit: 2636301fe5d6c33535f873aeb776c3e4beb5dd2d
branch: agent/deepseek/GOV-EVIDENCE-UNIQUE-1
worktree: 待 Codex 在 G:\CODEX\New Manga.workspace\worktrees\GOV-EVIDENCE-UNIQUE-1 创建并登记实际路径
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-EVIDENCE-UNIQUE-1
allowed_paths:
  - doc/tasks/GOV-EVIDENCE-UNIQUE-1.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/handoffs/
  - doc/reviews/
  - verification/GOV-EVIDENCE-UNIQUE-1/
---

# GOV-EVIDENCE-UNIQUE-1：GOV-DEBT-CLEANUP-2 AC7 唯一最终证据判定

## 来源与目标

承接 `GOV-DEBT-CLEANUP-2` AC7 未完成部分。只读审查 `verification/GOV-DEBT-CLEANUP-2/ac7-evidence-dir-files.md` 列出的 61 个文件，并按原 AC/来源 Task 判断每项是否为某个已释放 AC 的唯一最终证据。不得因本 Task 而恢复或改写已关闭 Task 的状态、AC、Review、Canonical Evidence 或历史 pin。主证据入口：
- `doc/tasks/GOV-DEBT-CLEANUP-2.md` 与 `doc/reviews/GOV-DEBT-CLEANUP-2-94c8dcdab-antigravity-r2.md`
- `verification/GOV-DEBT-CLEANUP-2/ac7-evidence-dir-files.md`
- `doc/09_COLLABORATION.md` §4.1 / §4.2 / §5

## Acceptance Criteria

- [ ] **AC1 — 61 项逐文件判定**：对源表 61 项逐项记录精确路径、文件 SHA-256、候选类别、对应来源 Task/已释放 AC、当前 Canonical Evidence pin、文件是否能证明 AC、是否存在等效替代证据、是否为唯一最终证据及理由。不得只依据文件名、目录或表面存在性判定。
- [ ] **AC2 — 唯一性与完整性核验**：对每个已释放 AC 建立 `AC → Canonical Evidence` 映射；明确判为唯一、存在其他等效证据、非判别力证据、无法确定或不适用。任何缺失来源、无法访问、hash 不符或 AC 未释放均保留为 `BLOCKED/UNKNOWN`，不可改写成 PASS。
- [ ] **AC3 — 只读保护**：不更改源 Task、Review、既有 Canonical Evidence、pin、61 个文件、`.gitattributes`、`.gitignore` 或生产文件；不移动、删除、归档、重命名、复制或补登记其他 Task 的 evidence。候选补 pin 只写本 Task 的建议表，须由 Codex 在独立获准范围处理。
- [ ] **AC4 — 可复核交付与 Review**：入库逐项结果、来源 commit/hash、方法与未决项；生成 Handoff；由 Antigravity 对固定 delivery head 独立 Review。逐项证据覆盖和 limitation 保持一致。
- [ ] **AC5 — 生命周期和资源 closeout**：完成 Task/Review/Plan/STATUS 生命周期、Canonical Evidence 与 Resource Manifest；更新 integration 字段并按直接/branch 集成事实登记；运行适用治理检查并完整保存命令、环境、stdout、stderr、exit code。任何不通过均如实记录，不放宽 checker。

## 允许修改范围

- `verification/GOV-EVIDENCE-UNIQUE-1/`：只读判定矩阵、复核记录、运行输出。
- 本 Task 自身文件、Handoff、Review 及 Codex 管理的 Plan/STATUS 指针元数据。

## 禁止事项

- 不改 `verification/GOV-DEBT-CLEANUP-2/`、任何来源 Task/Review/evidence、历史 pin、`.gitattributes`、`.gitignore`、`tools/`、`src/`、`tests/` 或其他生产路径。
- 不把建议 pin 写回来源 Task；不执行物理处置；不扫描并裁定与 61 项无关的未入库文件。
- 不把 `closed_with_limitations` 来源 Task 改成 `done`，不重开 AC，也不把 `UNKNOWN/BLOCKED/NOT_RUN` 写成 PASS。

## 测试与验证

本 Task 为只读证据判定，不运行产品测试。planned：对 61 行逐行核对、重算文件 hash、核查来源提交含文件、对照来源 Task 的 AC/pin，并运行 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-EVIDENCE-UNIQUE-1.md` 与全局 checker。按命令、PowerShell 版本、结果、stdout/stderr、exit code 记录；不得把未跑项标为通过。

## Canonical Evidence

登记 AC1–AC5 判别力矩阵、Handoff、Review 和 checker 输出；每项记录仓库相对路径、含文件 commit、SHA-256、class。Review 必须绑定精确 `reviewed_head`。

## Resource Manifest

冻结 ready 前登记实际 Task worktree 路径；task-env、dataset、artifact、temp、agent-output、exchange 逐项核实。不适用需有目录核实依据；未知、dirty、被引用或用户数据一律保留。
```

**推荐的下一步 Task 方向**：正式登记并冻结 `GOV-EVIDENCE-UNIQUE-1`，Owner DeepSeek Harness、Reviewer Antigravity；先由 Codex创建并登记 linked worktree 与 Task 文件，再更新 Plan/STATUS、治理检查通过后置 `ready`。不得在本次 closeout 直接启动。

## 6. 1233 个未入库文件：技术建议（不执行）

本轮现场 `git status --porcelain --untracked-files=all` 实测 **1592 entries**，比问题中所称 1233 多 359；两者计数口径/快照不同，不能直接混用。本轮分组为 `verification/` 1470、`.orchestrator/` 67、`doc/` 32、`archive/` 19、`.qoder-credits/` 2，以及根目录 `CON` 和一条中断会话说明各 1；另外工作区含 `.qoder-credits/report.json` 的 modified 状态。计数不是内容归属结论。可能构成包括历史任务/Review/过程日志、恢复证据与生成输出、旧 archive 镜像、项目治理或编排配置、Qoder 运行数据/用户数据及异常文件名对象。尤其 `.qoder-credits/` 与 `CON`、中断会话文本不得仅凭路径/扩展名认定可提交或可删。

最小安全路径：

1. 先固定待核对的精确集合和时间点，保存 `git status --porcelain --untracked-files=all` 的逐路径清单及其 SHA-256；说明 1233 与本轮 1592 的计数口径差异。不要批量 `git add`、`git clean`、删除、移动或归档。
2. 只读分组：tracked modified/deleted 与 untracked 分开；再按目录、扩展名、大小、文件类型、内容指纹和疑似用户数据分组。逐项查 Git 历史、当前 Task/Review/evidence 引用、来源 owner 和是否可重建；对无法证明归属者标 `PRESERVE_UNKNOWN`。
3. 先输出“来源/归属/引用/建议 disposition”清单，分类为候选纳入版本控制、历史归档候选、仓外用户/运行数据、重复镜像、未知待确认。任何归档/删除/迁移另需满足来源、原路径、hash、完整引用迁移和 workspace 规则；引用中的文件原位保留。
4. 之后按目录/来源拆成独立窄 Task；每个 Task 冻结输入集合、允许路径、禁止范围、验收与资源 manifest。首个 Task 只做只读盘点与建议，不执行 add/删除/移动。用户或 Codex基于证据逐批批准处置后，另开执行 Task。

应立 Task。建议首个 `GOV-UNTRACKED-INVENTORY-1` 定为只读治理 Task：精确冻结清单快照、每文件来源/引用/hash/owner/disposition 建议；禁止 `git add`、清理、迁移、归档和内容修改；将未知项保留。将 `.qoder-credits/`、编排运行态、历史文档/证据和 `archive/` 分开报告，避免一项大 Task 同时授权不同数据类别的处置。只有读完清单后再依据真实构成决定是否需要后续纳入 Git、迁移或归档 Task。

## 7. 本轮 Git 状态对比

操作前 `git status --porcelain --untracked-files=all`：1592 entries；将 LF 连接后的文本 SHA-256 为 `1e64a0a86b26947ba824ae9f584d04664f647677621a9d1aac29d6f8fa1036af`。唯一目标文件在操作前不存在。操作后应为原 1592 entries 全部保留并新增本文件 1 条 `??`，共 1593 entries；没有 Git 写命令，没有改动任何既有状态。
