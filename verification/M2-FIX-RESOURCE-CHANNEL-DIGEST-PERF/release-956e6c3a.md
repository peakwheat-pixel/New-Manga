# M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF Release Evidence — release-956e6c3a

- Release commit: 本次治理 commit（即 `doc/tasks/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF.md` 释放修订 commit，父 commit = `956e6c3a`；实际 hash 见 `git log --grep "release M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF"` 与 STATUS release checkpoint）
- Fixed base: `956e6c3ad3b37fdc274cd6353b285da530e7aeaf`（release 时 main HEAD；GOAL 收口后 REBASELINE audit commit，m2_acceptance 35 passed / core 77 passed / cargo 34 passed 全绿态）
- Approval: 用户 2026-09-29 转发释放指令批准（指令要求见 §4）
- Branch / worktree: `agent/zcode/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF` / `G:/CODEX/New Manga.worktrees/M2-FIX-DIGEST-PERF-zcode`（从 release commit 检出，创建时干净）
- Roles: Owner=ZCode（子 agent 代行实现）/ 非作者 Reviewer=DeepSeek Harness / Integrator=另一子 agent 代行 Codex（Owner≠Integrator 保持）
- Depends_on: [M2-FIX-F02-RESOURCE-CHANNEL-FLAKY](../M2-FIX-F02-RESOURCE-CHANNEL-FLAKY/integration-3cef4831/integration.md)（done @ integration `aa2f99b8`）

## 1. 登记内容（Task 冻结摘要）

- **目标**：在不弱化"等长重写必拒"的前提下，消除 F02 修复（移除 mtime 短路、每请求全量重验）带来的可避免成本与死结构：①单趟 hash+capture（必做，消除三读路径 + TOCTOU 残留窗口）；②per-chunk digest（授权可选，成本 O(文件)→O(chunk)）；③GrantCache dead-code 收敛（必做）；④`identity_change_invalidates_cache_entry` 更名（必做）；⑤loop 临时目录泄漏卫生项；⑥机理对照实验（可选）。
- **硬约束（不得放松）**：等长重写必拒语义与 f02 两个断言不放宽；不得恢复 mtime 门控/时间戳短路；F-01 每请求 Core resolve 无条件先行语义不变；per-chunk digest 已按 Core 契约流程由 Codex 划定范围（Python DTO/service + Rust Grant + 契约文档最小修订，向后兼容）。
- **允许路径（两级授权）**：无条件=`resource_protocol.rs`、`main.rs` 资源通道测试段、Task/verification/handoff；条件（仅 per-chunk 路线，Handoff 声明）=`core_bridge.rs`、`src/application/resource_channel/dto.py`/`service.py`、`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` 最小修订、`tests/core/` 对应测试。
- **AC1-AC5** 已冻结（见 Task 文件）；AC2 明确 release profile 补测闭合 F02 P3-9；AC5 三层验证义务（cargo 全量+loop、m2_acceptance 35 passed 基线不回退、diff --check 整树）。
- Owner 实现要求：**先红后绿**——先复验判别力红证（对优化前/等价现状代码 loop 必红，或引用 F02 集成组 5 artefact 并在优化后 head 复验），再落优化转绿。

## 2. 释放时核验

- main HEAD = `956e6c3a`（2026-09-29 REBASELINE audit；治理文档 clean，仅 5 个 pre-existing `verification/M2-RC2/raw/*` 脏文件属 E2E 运行残留，与本 Task 无关、保留不动）。
- 无 `in_progress`/`ready` Task 争用（GOAL 达成后无 Active）；worktree 名未被占用；分支不存在（新建）。
- Release commit 仅含 Task/evidence/治理文档，**零代码改动**。
- Grant 链路事实核对：Rust `Grant` @ `core_bridge.rs:18`（serde）；Python DTO @ `src/application/resource_channel/dto.py`；三读路径 @ `resource_protocol.rs:434/:440-441/:449`；`CachedGrant.grant` dead-field @ `:68:5`。

## 3. 与 F02 遗留的对应

| F02 遗留 | 本 Task 处置 |
|---|---|
| ~50x digest 重验成本（18424µs/request @1MiB warm debug，冻结接受） | AC2：单趟或 per-chunk 路线消除 |
| release profile 性能 NOT_RUN（P3-9） | AC2：release 补测 |
| `CachedGrant.grant` dead-code（C2 选(b) 显式接受） | AC4：收敛清零 |
| TOCTOU 残留窗口（既有面） | AC3：单趟 capture 消除或书面说明 |
| P3-7 机理归因未区分（tick 碰撞 vs LazyWriter） | 触点 6 可选补强 |

## 4. 释放指令存档（用户转发原文要点）

> 释放 M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF（proposed -> ready）：base=届时 main HEAD，Owner=ZCode 子 agent（新会话/worktree 实现），非作者 Reviewer=DeepSeek Harness，Integrator=另一子 agent 代行 Codex（Owner≠Integrator 保持）；登记 release evidence。硬约束（Task 文件已冻结，不得放松）：不得弱化「等长重写必拒」；不得恢复 mtime 门控；per-chunk digest 须经 Core 契约流程；随 Task 收敛 CachedGrant dead-code 与 identity_change_invalidates_cache_entry 更名；f02 稳定性 loop 与 m2_acceptance 全绿为回归底线。走完整链：claim -> 实现（先红后绿）-> DSH 静态 Review -> 条件闭合 -> 集成 merge -> tip 绑定复跑（pytest/cargo/vitest + f02 loop）-> integration 记录 -> STATUS/PLAN 同步收口。全程 checkpoint 留痕，发现范围外缺陷只登记候选不扩大范围。
