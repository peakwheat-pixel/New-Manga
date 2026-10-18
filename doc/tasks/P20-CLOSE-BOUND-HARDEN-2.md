---
id: P20-CLOSE-BOUND-HARDEN-2
title: sidecar worker holder 生命周期与审计边界收口（R4-01 承接）
kind: fix
governance_version: 2
status: in_review
approval: user_ruling_20261018_close_harden_1_and_split_harden_2
blocked_by: null
suggested_owner: dsh
owner: dsh
reviewer: Codex
depends_on: [P20-CLOSE-BOUND-HARDEN-1]
base_commit: 35770fe91ab722b6d6c5e06e1f855c062d15c0a2
branch: null
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: a2f90b047ae94e93ceb5afe8ede0eafa5bb408c7
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/P20-CLOSE-BOUND-HARDEN-2
---

# P20-CLOSE-BOUND-HARDEN-2：worker holder 生命周期与审计边界收口

## 执行方改派（2026-10-18 用户指令）

用户指令：**本对话不再调用 agy**，停止 Antigravity 手上的本 Task，**改派 dsh 执行**。Owner 由 Antigravity 改为 **dsh**；Reviewer 仍为 **Codex**（满足 owner != reviewer）。

**AC5 的执行约束（改派后仍然成立）**：AC5 要求 `P20-CLOSE-BOUND-1` 的 AC7 **真实交互桌面直跑**，并明确「由 Coordinator 在交互式桌面执行；**本 Task 只负责脚本正确性，不得自行记 PASS**」。改派 dsh 执行**不改变**这一约束 —— dsh 可以交付并自检脚本，但**该 AC 的 PASS 只能由人在交互桌面上产生**，不得由执行方自行判定。

## 背景（用户裁决 2026-10-18）

`P20-CLOSE-BOUND-HARDEN-1` 经三轮返修（R1fix/R2fix/R3fix）后，R4 复审仍为 `changes_requested`。用户已按 DIR-4 用尽豁免（"最后一次"），裁决：**原 Task 以 `closed_with_limitations` 收口，未闭合项由本 Task 承接**（仿 `P09-AC3-DELETE-1` → `P09-AC3-DELETE-HARDEN-1` 先例）。

来源：`verification/P20-CLOSE-BOUND-HARDEN-1/codex-review-r4.md`。

## 未闭合项（原样承接，不得抹除）

**R4-01（P1，延续 R3-01）** —— 依据 `apps/desktop/src-tauri/src/library_bridge.rs:1527-1569`、`:3630-3647`、`:3665-3682`、`:3787-3804`、`:3822-3839`；审计 `verification/P20-CLOSE-BOUND-1/concurrency-lock-audit.md:26`、`:134-150`：

- registry **连续锁超时**时仍可能丢失对 holder 的保留；
- registry **达到容量饱和**时的行为未定义；
- **holder spawn 失败**路径未覆盖；
- 审计表仍宣称句柄"绝不被 drop"，并把有限 registry/reaping 描述为**完整生命周期保证**（`:113` 的 CloseHandle 行号已修正为 `1857, 1965, 3880, 3886`，但 `:26`、`:134-135`、`:147-150` 的表述仍需按真实语义改写）。

## 验收标准

- [x] **AC1**：registry 连续锁超时路径**不得丢失** holder/handle 保留语义；给出可运行的注入用例。
- [x] **AC2**：registry **容量饱和**有明确定义的行为（拒绝、退避或显式扩容），并有注入用例。
- [x] **AC3**：**holder spawn 失败**路径有覆盖，且失败时句柄处置明确（不泄漏、不误 drop）。
- [x] **AC4**：`concurrency-lock-audit.md` 的**生命周期边界**按修复后真实语义重写；不得再出现"绝不 drop"或"完整生命周期保证"这类超出实现强度的表述；行号与源码一致。
- **AC5**：**AC7 真实交互桌面直跑**（由 Coordinator 在交互式桌面执行；本 Task 只负责脚本正确性，不得自行记 PASS）。
- [x] **AC6**：不回归 —— `P20-CLOSE-BOUND-HARDEN-1` 已通过的 AC8 九项回归（R-008 心跳恢复、R-003 拆环 reap、R-006 错误呈现、`MAX_RETRIES=3`、resilient 9 项、stdio drop、shutdown writes、2 MB pipe overflow）保持通过。
- [x] **AC7**：报告中所有 40 位 SHA 必须能通过 `git cat-file -e` 校验；`sha256` 按**磁盘真实字节**实算（本仓库为 **CRLF 检出**）。

## 边界

- 不改 IPC / 共享契约 / Schema / ACL / 依赖版本；不动 `apps/desktop/frontend/**`。
- 禁止改写历史 pin 以"消除失败"；证据一律追加。
- 禁止编造 commit SHA。

## 交付物

- 修复后的 `library_bridge.rs` 与更新后的审计表
- 上述注入用例的原始日志与退出码
- Handoff（引用实际文件与 commit）

## 交付记录与证据（2026-10-19）

### 实现提交（40 位 SHA 经 `git cat-file -e` 验证）

| 短 SHA | AC | 内容 |
|---|---|---|
| `b7e63a49b` | AC3 | 共享槽 holder：4 处 `let _ = spawn(...)` 收敛为 1 个 `spawn_persistent_holder`，spawn 失败时经槽同步 `join` |
| `40d933700` | AC1 | 连续锁超时注入用例（真实持锁跨越完整重试窗口） |
| `580bb0d65` | AC2 | 饱和语义明确化 + 有界退避（50 ms→500 ms 上限）+ 注入用例 |
| `3b4d52766` | AC4 | 审计表按真实语义重写，撤回「绝不 drop」「绝对不 drop」「彻底杜绝」 |
| `a2f90b047` | AC6/AC7 | 九项回归证据 + SHA 校验 |

### 测试结果

| AC | 场景 | 结果 |
|---|---|---|
| AC1 | 连续锁超时 | `cargo test --bin m2rc1-desktop ac1_consecutive_lock_timeouts` → **1 passed**（3.31 s） |
| AC2 | 容量饱和 | `ac2_saturated` → **1 passed**（8.10 s） |
| AC3 | spawn 失败路径 | `cargo check` exit 0；残留 `let _ = std::thread::Builder::new()` = **0**；4 个 helper 调用点句柄对逐一核对 |
| AC4 | 审计表行号 | 过时行号 `3634/3669/3791/3826` 残留 **0 处** |
| AC6 | 九项回归 | **9/9 PASS**（逐条 cargo test，见证据文件） |
| AC7 | SHA 校验 | 4 个提交 `git cat-file -e` 全部 exit 0 |
| **AC5** | **真实交互桌面** | **未执行、未记 PASS** —— 须由人在交互桌面运行 `run-desktop-close-verification.ps1` |

### Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| H2-AC6-AC7 | AC6/AC7 | verification/P20-CLOSE-BOUND-HARDEN-2/ac6-ac7-regression-and-sha.md | a2f90b047 | 1404be97c0af64b678028ab653d98f7d042ae40276b0e8009d2495b18cd5324b | CANONICAL |
| H2-AC4-AUDIT | AC4 | verification/P20-CLOSE-BOUND-1/concurrency-lock-audit.md | 3b4d52766 | 65bdaf65c846506158af0aef261d0108f022f75f38148387d98f2c3213dcfee0 | CANONICAL |
| H2-AC3-IMPL | AC1/AC2/AC3 | apps/desktop/src-tauri/src/library_bridge.rs | 580bb0d65 | d4825b8a7f9187cef893b646a1cf667045e4bb817eea8ac9af40ba720c03d29b | CANONICAL |
| H2-AC5-SCRIPT | AC5（脚本，非 PASS） | verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1 | 35770fe91 | a0043b6deb2a477c73948a418ceb62902ea0b7840e25f63a5af60c17c4f31f24 | SOURCE_PIN |

### 未关闭项（唯一）

**AC5 未完成**，且**本 Task 无权自行判定**：Task 明文规定其由 Coordinator 在**交互式桌面**执行，且「本 Task 只负责脚本正确性，不得自行记 PASS」。本 Task 已交付脚本并自检其存在与结构，但**不为其提供 PASS 依据**。该项因此保持未勾选，Task 不得据此进入 `done`。

### 强度边界（与 AC4 一致）

AC3 之后，句柄保留是**两条路径的联合结果**：holder 成功启动时由其接管；holder 自身 spawn 失败时句柄仍在共享槽中并被同步 `join`。**这不是「永不失败」的保证**，而是**两条真实路径都不静默 drop**。AC1/AC2 的注入用例分别钉住这两条路径的可观测性质。
