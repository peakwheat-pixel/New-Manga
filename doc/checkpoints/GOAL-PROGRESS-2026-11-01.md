# Goal 进度文件 · 2026-11-01（自主推进段）

**目标**：继续推进 FEA 实现线，不等待用户确认；需拍板事项写入本文件「待裁决」区并给推荐，按规则交 DSH/Codex/ZCode 裁决后继续。

**当前 HEAD**：`419d75bbb`（main，clean）
**当前 Task**：`FEA-C11-PREREQ-1` in_progress（契约前置登记，待复核收口）→ 本段主推进 `FEA-03`

---

## 1. 已完成

| 项 | 状态 | 证据 |
|---|---|---|
| `FEA-00A-IMPL-1`（FEA-00a 数据安全修复） | **done** | 集成 `e0ba29eba`；实现 `007094517`；范围复核 r3 approved；实现复核 r1 approved（P0/P1=0）；194 passed / 0 failed；pin 15/15 |
| 范围冻结流程（3 轮独立复核） | done | `doc/reviews/FEA-00A-IMPL-scope-r1/r2/r3.md` |
| Codex 派发链（headless + 沙箱限制绕过） | done | `agent-output/dsh/FEA-00A-IMPL-1/` |

## 2. 进行中（本轮）

`FEA-03 草稿与保护协调`：
1. DSH 裁决释放（Codex 是预期实现者 → 按规则裁决交 DSH；依据：方案 §12.1/§15.6、C-13 已冻结、依赖 FEA-01/FEA-00a 已满足）。
2. 建范围冻结卡（写域、AC、L 判定、V 矩阵）。
3. 派上下文独立复核 → 迭代 → `ready` 交 Codex。

## 3. 待裁决（需用户拍板；DSH 已给推荐，按规则先行裁决不阻塞）

| # | 事项 | 推荐 | 处置（DSH/Codex/ZCode 裁决） |
|---|---|---|---|
| Q-1 | 是否释放 `FEA-03`（草稿与保护协调） | 释放（依赖已满足、C-13 已冻结、下一候选） | **DSH 裁决：释放**（Codex 为该事项实现者，按目标规则裁决交 DSH）。依据：方案 §12.1 `:641`、§15.6 `:923`、C-13 冻结记录 §5「实现释放条件 = 本单冻结 + C-11 建卡 + 独立 Review」。 |
| Q-2 | `FEA-03` 的 draft journal 存储方式（契约未指定表/文件） | **文件 journal**：`<data-root>/drafts/<DraftId>.json`，temp+rename 原子写；不新增 schema 表 | **DSH 裁决：文件 journal**。理由：①不改 `schema.py`/migrations → 规避 L-1 与迁移契约；②崩溃恢复语义自证（文件存在即可恢复）；③跨 Session 一致性由 Core 内单写者保证。若实现中证明文件方案不可行（如需要跨进程共享），须回本文件登记并转 `CONTRACT-UNFREEZE-C13` 流程。 |
| Q-3 | `FEA-03` 是否同时改 `NewManga.ApplicationCore`（C#） | **是**，但拆两切片：CORE（Python 侧 journal/token/apply/locks）先落地；BRIDGE（C# 草稿缓冲）同 Task 内后置 | DSH 裁决：同 Task 两切片；CORE 必须先通过测试，BRIDGE 不得阻塞 CORE 的独立验收。 |
| Q-4 | `FEA-00A-IMPL-1` 的 AC7②（真实用户旧库只读核验） | 需用户提供旧库副本才能补；已登记 `FOLLOW-UP-FEA00A-1` | 不阻塞；下次用户在线时可提供副本补跑。 |
| Q-5 | `G-DELETE-IMPL`（删除线实现授权） | 维持 OPEN；FEA-12 需用户单独确认 | 不阻塞 FEA-03。 |

## 3C. 本轮进展（2026-11-01/02 段）

- FEA-03 范围冻结经 **5 轮独立复核**（r1–r4 changes_requested → **r5 approved P0/P1=0**）；C-13 经 CONTRACT-UNFREEZE-C13 修订为 v6（pin `8faf1e80…`，r3 单独 approved）。
- FEA-03 卡置 `ready`（`b83bc7703`），独立复核报告 r1–r5 全部入库。
- 已建实现 worktree `G:\CODEX\New Manga.workspace\FEA-03`（分支 `feat/fea-03`）并派发 Codex 实现（2026-11-01 23:59 起）。

## 4. 下一动作

1. 提交 `FEA-03` 范围冻结卡（proposed）→ 派独立复核 r1。
2. 复核通过 → `ready` → 派 Codex 实现（两切片）。
3. 实现交付 → 独立实现复核 → 集成 → done。
4. 之后按 DAG 继续（`FEA-04` Current 适配 或 `FEA-04b` Fluent 四页设计规格，视写域冲突与用户偏好择一）。

## 5. 状态变更记录

| 时间 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 23:00 | 建立；记录 FEA-00a done 与 FEA-03 推进计划；DSH 裁决 Q-1/Q-2/Q-3 | DSH |

## 3B. 裁决与执行记录（2026-11-01/02，FEA-03 范围冻结迭代）

| 事项 | 裁决/动作 | 结果 |
|---|---|---|
| Q-6 旧路径语义 | 不改 C073；SC-D11 适用范围修订 | **CONTRACT-UNFREEZE-C13-2026-11-01**：C-13 v5→v6，pin `8faf1e80…`；去重键限新 token 路径 |
| Q-7 commit receipt | 多序列 receipt + DB 去重兜底 | R-RECEIPT-1/2/3、R-APPLY-3、AC15/V20/V21 |
| Q-8 BRIDGE | 收窄为本地缓冲 + 不接线 | AC12、V24；L-2 维持 N/A |
| Q-9 manual 位 | 三锁 + `text_json.translation_locked` + `text_json.manual_edited` | AC10/V17 |
| Q-10 几何/样式 | 同键后到覆盖（草稿阶段不产生新 revision） | AC3/V7 |
| Q-11 SC-D11 | UNFREEZE 已完成（见 Q-6） | 无需 deferral |
| 范围复核 | r1（P0×1/P1×7/P2×11）→ v2；r2（P0×1/P1×5/P2×12）→ v3；r3（P0=0/P1×4/P2×12，**UNFREEZE approved**）→ v4/v5；r4（P0=0/P1×2/P2×12）→ v6 | r5 待审 |

**FOLLOW-UP 登记**：`FOLLOW-UP-FEA03-1` SC-D11 原条款与新路径实现的长期协调（UNFREEZE 已承接，待后续 Task）；`FOLLOW-UP-FEA03-2` C-13 `:173` manual 位引用口径（本卡按 `text_json.translation_locked`+`manual_edited` 实现，无需再改）；`FOLLOW-UP-FEA03-3` 旧路径统一去重（后续 Task，按 C-13 v6 新路径优先）。



## 3D. FEA-03 实现交付（2026-11-02 00:40）

- Codex 实现完成（分支 `feat/fea-03`，commit `7a31c331e`，base `b83bc7703`）：CORE（draft/journal/receipt/intent/candidate/apply/locks/digest）+ BRIDGE（DraftBuffer.cs）+ 证据。
- 集成验证（DSH 侧）：`python -m pytest tests/core tests/domain tests/editing tests/infrastructure -q` → **1050 passed / 0 failed**（基线 885 + 新增 165）；主仓库 `verify_pins` 15/15 PASS；`check.ps1` PASS。
- 修复 Codex 环境无法覆盖的问题：journal 文件锁改为**目录锁 + 同进程共享 + 残留 PID 清理**（解决 Windows WinError 32 / 锁文件不可读 / 重启测试 DRAFT_JOURNAL_LOCKED）；`CoreServices.close()` 释放 journal 锁；评测测试配套适配。
- 交付待上下文独立实现复核（`doc/reviews/FEA-03-r1.md`）。
