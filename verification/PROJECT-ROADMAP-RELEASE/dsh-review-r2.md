---
task_id: PROJECT-ROADMAP-RELEASE
title: 完整产品路线恢复、Gate裁决与下一实施切片释放
reviewer: DeepSeek Harness（非作者；本轮同时承载 Active Coordinator，Reviewer != Owner 成立）
author: Codex（Owner / Integrator）
base_commit: 0dcc94f3591b2837c91a6b3aa5b6dcce6c23aa64
reviewed_head: a43c6b9fed681e7cb123123eeb6b5ccb7fd4d4b6
r1_reviewed_head: 657096b41042d7cfbbbee76baa856f96c28de24a
review_worktree: G:/CODEX/New Manga（live root，与固定 head 一致：证据目录/任务/STATUS/Plan 均 CLEAN vs HEAD）
date: 2026-10-15
mode: 只读审查 + 确定性 Git/hash 复算；未修改任何被审对象；未执行 Build/Cargo/GUI/模型/真实Core/安装/OS/registry/ACL 操作
object_binding: VERIFIED
architecture_axis: PASS（沿用 R1 文本层结论，本轮无产品源码变化）
verification_axis: PARTIAL（固定head/证据/治理可核验项 PASS；产品测试NOT_RUN，符合本Task性质）
decision: approved_with_conditions
decision_scope: AC1–AC3 维持通过并由本轮独立 Git/hash 证据支撑；AC4 的「固定head独立Review」部分本轮完成，其余 closeout 项（集成后复跑、资源关闭、最终治理检查、证据全量登记、AC勾选）须由 Integrator 关闭后方可 done
---

# PROJECT-ROADMAP-RELEASE 独立 Review（R2 有界复审）

## 0. 本轮相对 R1 的能力变化（关键）

R1 因 DSH 沙箱 ACL 拒绝 pwsh，`git`/`Get-FileHash` 全部 `NOT_RUN`，故 `object_binding=NOT_VERIFIED`。
本轮 DSH 主会话持有 danger-full-access 文件策略，**实际执行**了 Git 与哈希复算，`object_binding=VERIFIED`。这是 R1 明确指出、必须由非作者补齐的缺口。

### 0.1 本轮实际执行（命令与结果）

| 项 | 命令 | 结果 |
|---|---|---|
| 固定head | `git rev-parse HEAD` | `a43c6b9fed681e7cb123123eeb6b5ccb7fd4d4b6` |
| 固定head变更面 | `git show --stat a43c6b9f` | 仅 2 文件：`M doc/tasks/PROJECT-ROADMAP-RELEASE.md`、`A verification/.../adjudication-r1.md` |
| R1head→固定head | `git diff --name-status da8bb7ce a43c6b9f` / `657096b4 a43c6b9f` | 全部落在 `doc/**`、`verification/**`；无产品源码 |
| 对象存在性 | `git cat-file -t` + `git rev-parse` | `92093792…caf86`、`4a707db8…b1a92`、`faea1a2c…529f9`、`0dcc94f3…3aa64`、`571d8970…342f`、`657096b4…e24a`、`da8bb7ce…16f0`、`a43c6b9f…4b6` 均为 commit |
| 祖先关系 | `git merge-base --is-ancestor <sha> HEAD` | `92093792`=False(exit 1)、`faea1a2c`=False(exit 1)、`0dcc94f3`=True(exit 0) |
| 产品源码差量 | `git diff --name-only 0dcc94f3 a43c6b9f` 过滤非 `doc/|verification/` | 26 项全为文档/证据，**产品源码差量 = 0** |
| 工作区一致性 | `git status --porcelain=v1 -- <被审路径>` | 证据目录、本Task、STATUS、Plan 全部 CLEAN vs HEAD |
| 固定pin重验 | 逐行解析Task Canonical Evidence，`Get-FileHash -Algorithm SHA256` | **19/19 一致，0 mismatch** |
| 治理检查器 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/PROJECT-ROADMAP-RELEASE.md` | `Governance check: PASS (2 warnings)`，EXIT=0 |
| 预算实测 | 字节/行数 | `doc/REBASELINE_PLAN.md`=1602 bytes/34 lines（预算2500/35，**80%告警**）；`doc/STATUS.md`=1368 bytes/21 lines（预算3200/45，PASS） |

未执行（NOT_RUN，符合Task禁止范围）：Cargo/产品测试/GUI/模型/sidecar/真实Core/安装/OS/registry/ACL/进程枚举。

### 0.2 与 verification.json 口径的一致性

`verification.json`：`head=571d8970…`（capture head，**非** source base）、`source_pins=10`、`protected_paths=1525`、`protected_bytes=PASS`、`unknown_preserved=[]`、`product_tests=NOT_RUN`、`new_product_code_changes=0`、`helper_selftests=127/127`。与 REPORT/adjudication 的 P2-1 说明一致，未把 capture head 当 source base。**核验通过**。

## 1. R1 findings 在固定 head 的处置核验

| finding | adjudication 处置 | 本轮独立核验 |
|---|---|---|
| P2-1（HEAD口径冲突） | 三个时间点不同对象：log=base `0dcc94f3`、verification.json=capture `571d8970`、R1 review head=`657096b4`；区间产品源码零差量；原始记录不回写 | **PASS**：`0dcc94f3` 为 HEAD 祖先；`571d8970..657096b4` 无产品文件；`0dcc94f3..a43c6b9f` 产品差量 0 |
| P2-1b（保护集合/CON） | 本轮集合 1525 可读文件、`unknown_preserved=[]`；不推断 CON 不存在 | **PASS**：`verification.json` 记 1525/`[]`；REPORT 已写明条件策略 |
| P2-2（core-sidecar 复制/hash 权） | 补 Owner 对 `target/core-sidecar/core-sidecar/**` 的完整复制+逐项 hash 权，禁止假目录/执行真实 Core | **PASS**：`doc/tasks/P22-REBASE-1.md:48`、`:60` 已写明 |
| P2-3（sidecar 输入未 pin） | 固定 `git 92093792…:verification/P04/deterministic_concurrent_sidecar.py` + 准确 SOURCE_PIN | **PASS**：`P22-REBASE-1.md:47` 已给出完整 pin 与 source-manifest 引用 |
| P2-4（测试集与真实Core冲突） | 唯一显式排除 `real_core_sidecar_answers_startup_ping_on_fresh_catalog`，标 NOT_RUN | **PASS**：`P22-REBASE-1.md:41`、`:64` 已写明排除项与 NOT_RUN 语义 |
| P2-5（P16/P17 缺 DOC 边） | 两者增加 DOC 依赖对应 ARCH-DOC-REBASELINE AC6 | **PASS**：`doc/REBASELINE_PLAN.md:23`（P16←P08/P13/**DOC**）、`:24`（P17←P16/**DOC**/UI） |
| P2-6（REPORT 是否第二状态源） | Plan 持续冻结引用 REPORT 作 Gate 输入，REPORT 不独立维护状态 | **PASS**：`REBASELINE_PLAN.md:32` 明写该规则 |
| P2-7（ARCH-DOC-REBASELINE 登记） | 正式登记 proposed，Owner Codex/Reviewer DSH，非第二 READY | **PASS**：Plan `:15` proposed；Task 存在；未进入 READY |
| P2-8（治理检查可复现性） | checker 源码 SOURCE_PIN；live root 执行；不声称固定 worktree 自包含 | **PASS**：`R-17` pin `inputs/tools/governance/check.ps1`；本轮在 live root 实跑 EXIT=0 PASS |
| P2-9（证据分类） | inputs/环境源统一 SOURCE_PIN，结果/裁决 CANONICAL | **PASS**（附 C1）：19 条 pin 中 `inputs/**` 与 `environment-sources.json` 已按 SOURCE_PIN 分类；但本轮新增的 `adjudication-r1.md` 尚未登记（见 R2-01） |
| P3-6/P3-10 | base interpreter 实测/单Cargo 1800s 与同步等待 ≤30s | **PASS**：`P22-REBASE-1.md:58`、`:64` 已写明 |

R1 findings 未发现未处置项；R1 提出的 **P2-3/P2-4/P2-5/P2-8** 四个实质缺口在固定 head 均已闭合。

## 2. AC 逐项结论

- **AC1（P01–P22 恢复到唯一 Plan；P19 接收 P04/P22 并发安全验收）**：**PASS**。Plan 含 P01–P22 全行；P02=`限定关闭`、P22=`in_review来源`、`READY 节点：无。`；P04 依赖 P22，P19←P04 可追踪。沿用 R1 结论，固定 head 未改动该语义。
- **AC2（固定Git命令验证 P22/P04 可达性与审查边界；不以 R10 批准源码；复核架构Gate）**：**PASS**。本轮独立复算：`92093792`/`4a707db8`/`faea1a2c` 存在且**均非 HEAD 祖先**；`0dcc94f3` 为祖先；产品源码差量 0；架构文档 Gate 维持 `PARTIAL/NOT_CLOSED`、P09/P18/P20 `NOT_RUN`。
- **AC3（P22-REBASE-1 独立分支/worktree、Owner/Reviewer、允许/禁止路径、执行环境与判别力测试冻结，非作者Review后ready）**：**PASS（范围冻结）**。`P22-REBASE-1.md` 已含 base/branch/worktree、允许与禁止路径、`ready` 前置、`implementation_repairs_used=1/2`（继承 P22 预算不重置）、判别力要求（必须调用生产 `round_trip`、去锁 mutation 失败、禁 ignore/sleep）。**本 Task 关闭前不得 dispatch**。
- **AC4（保留用户文件；治理检查/固定head独立Review/Codex裁决/证据与资源关闭完成）**：**PARTIAL**。已完成：用户文件保留策略、源零写与范围验证、固定 head 独立 DSH Review（本轮，`object_binding=VERIFIED`）、Codex 裁决 `adjudication-r1.md`。未完成（见 §3 条件）：资源 closeout、证据全量登记、最终治理检查、集成后复跑、Task AC 勾选与 `canonical_evidence_status`/`resource_closeout_status` 转正。

## 3. 条件（进入 closeout / 释放 P22-REBASE-1 前必须满足）

- **C1（证据登记）**：`verification/PROJECT-ROADMAP-RELEASE/adjudication-r1.md` 与本文件 `dsh-review-r2.md` 须登记进 Task `Canonical Evidence`（裁决/Review 为 CANONICAL），并补齐其 commit 与 sha256 pin；当前治理检查器据此报 warning（见 R2-01）。
- **C2（Plan 预算）**：`doc/REBASELINE_PLAN.md` 已 34/35 行、1602/2500 bytes（80% 告警）。释放 `P22-REBASE-1`（`proposed→ready` + READY 节点）时**必须就地改写、不得净增行**；若需新增行须先重排/压缩并复跑治理检查。
- **C3（closeout 边界）**：本 Task 无产品代码集成；`integrator=Codex` 负责集成后复跑、Resource Manifest、Closeout Record、最终 `tools/governance/check.ps1`、AC1–AC4 勾选与状态转正。**在 C1–C3 完成前，不得把本 Task 标 done，也不得 dispatch `P22-REBASE-1`。**

## 4. 新增 findings

| id | 级别 | 内容 | 处置建议 |
|---|---|---|---|
| R2-01 | P2 | `adjudication-r1.md` 位于 `evidence_dir` 但未登记进 Canonical Evidence；治理检查器 warning 已指出 | closeout 时登记并 pin（C1） |
| R2-02 | P2 | Plan 行预算仅余 1 行（34/35）；下一切片释放需要改写 Plan | 就地改写、零净增行（C2） |
| R2-03 | P3 | Task 表 19 条 pin 的 commit 列均为 `da8bb7ce`，而 `base_commit=0dcc94f3`；固定 head 为 `a43c6b9f` | 属正常（证据在 `da8bb7ce` 提交，固定 head 未改证据字节）；closeout 时在 Closeout Record 写明时间口径 |
| R2-04 | P4 | `verification/PROJECT-ROADMAP-RELEASE/` 无 `README`/索引，20 个文件靠 Task 表映射 | 可选；不阻塞关闭 |

## 5. 能力边界（不得外推）

- 本 Review 不代表任何产品实现或运行时结论；本轮**无**产品代码修改、**无** Cargo/产品测试/GUI/模型/真实 Core 运行。
- 本轮 Git/hash 结论均在 **live root**（`G:\CODEX\New Manga`，HEAD 与其工作区一致）执行，不外推为固定 review worktree 可移植自包含。
- `object_binding=VERIFIED` 仅指本 Review 所列对象绑定（head/pin/祖先/差量）由**本 Reviewer 实际执行**得出；不改变 R1 当时的 `NOT_VERIFIED` 事实。
- 用户既有 1243 条 dirty/untracked 内容与 3 个 worktree 均未触碰、未提交、未删除、未 push。
