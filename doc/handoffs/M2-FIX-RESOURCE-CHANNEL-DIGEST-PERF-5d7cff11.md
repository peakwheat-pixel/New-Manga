# Handoff — M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF（owner delivery）

- **Owner**：ZCode（子 agent 代行实现；用户 2026-09-28/29 全权授权）
- **交付日期**：2026-09-29
- **base**：`956e6c3a`（release commit `6c3d7b34`）
- **claim**：`b43a1e2a`
- **测量探针 commit**：`9df29a6f`（`#[ignore]` 的 perf harness，无行为变更）
- **delivery_head**：`5d7cff11315b36a9b43390e28930a91d39282496`
- **Reviewer（非作者）**：DeepSeek Harness
- **Integrator**：Codex（另一子 agent 代行）
- **条件允许路径**：**未启用**（per-chunk digest 触点 2 评估后不实施，理由见 §5）

## 1. 变更范围（diff --name-status 956e6c3a..5d7cff11，仅 Owner commit 触碰）

| 文件 | 变更 | 允许路径 |
|---|---|---|
| `apps/desktop/src-tauri/src/resource_protocol.rs` | 单趟 hash+capture；删 GrantCache/CachedGrant | 无条件允许 ✓ |
| `apps/desktop/src-tauri/src/main.rs` | 调用点适配；测试更名；TempDir 守卫；perf 探针 | 无条件允许（资源通道测试段）✓ |
| `doc/tasks/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF.md` | claim + 交付回填 | 无条件允许 ✓ |

（956e6c3a..HEAD 的其余 diff 项——doc/00_INDEX.md、REBASE_PLAN、STATUS、tasks/README、release evidence——均来自 base 前的编排者 release commit `6c3d7b34`，非本 Task 产出；v5 日志含全量对照。）

## 2. 做了什么

1. **单趟 hash+capture（触点 1）**：`verify_and_serve` 改为一次顺序读全文件，`stream_digest_and_capture` 同时累计 SHA-256 并捕获 `[chunk_offset, chunk_offset+want)` 字节；比对通过后返回捕获字节。消除原"整文件 hash（:434）+ 丢弃读（:440-441）+ 再读（:449）"三读路径。**digest→serve TOCTOU 窗口结构性消除（AC3）**：返回字节就是 digest 覆盖的字节，不存在"验证后重新读取"的间隙。峰值内存 = 流式块（≤16 MiB）+ 捕获块（≤16 MiB）≤ 32 MiB，在 T4 线内。
2. **GrantCache 死结构收敛（触点 3）**：删除 `CachedGrant`/`GrantCache`/`GRANT_CACHE_MAX_ENTRIES` 及 `handle_m2res_request` 中全部无观察效果 map 操作（insert/clear/两处 remove）。F-01 每请求 Core resolve 无条件先行语义不变（fresh_grant 直接消费）。模块头/F-01 注释同步更正，并留考古注释说明删除原因。
3. **测试更名（触点 4）**：`identity_change_invalidates_cache_entry` → `identity_change_rejected_by_per_request_verification`，doc-comment 记录更名缘由；测试体断言不变（新 inode 替换 → 400 FILE_IDENTITY_CHANGED）。
4. **TempDir 守卫（触点 5）**：`env_with_fixture` 的 `std::mem::forget(dir)` 改为 `TestEnv._dir: tempfile::TempDir` 持有，drop 自动清理。stability loop 50 轮的 ~50 临时目录泄漏修复（覆盖所有 fixture 用户）。
5. **per-chunk digest（触点 2，可选）**：**不实施**，见 §5。
6. **触点 6 机理对照实验（可选补强）**：**未实施**（NOT_RUN），见 §6。

## 3. AC1-AC5 逐项对照（实测）

### AC1 — 等长重写必拒语义不弱化 ✓
- 全量 `cargo test --bin m2rc1-desktop` @`5d7cff11`：**34 passed; 0 failed; 1 ignored**（=基线 34 passed；perf 探针为 ignored 不进默认套件），EXIT=0。raw/v1。
- `f02_equal_size_rewrite_after_first_verify_rejected` + `f02_equal_size_rewrite_stability_loop` 断言一字未动；定向 loop **1 passed**（50 轮全绿，0.16s），EXIT=0。raw/v2。
- 判别力红证（引用 F02 集成组 5 artefact）：`verification/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY/integration-3cef4831/raw/g5-loop-discrimination-red.log` —— 修复前代码 checkout 后 loop **FAILED（0 passed 1 failed，left:200 right:400）**，EXIT=101；本 Task 在最终 head `5d7cff11` 复验 loop 绿（raw/v2）。先红后绿链闭合。

### AC2 — 性能（单趟路线达标）✓
统一 harness：`perf_chunk_request_digest_cost`（warm 1 次 + 计时 N 次，`--ignored --nocapture`）。基线源码态=9df29a6f（三读实现），优化后=5d7cff11（单趟）。

| profile | 档位 | 基线三读 | 单趟优化后 | Δ | 日志 |
|---|---|---|---|---|---|
| debug | 1MiB-chunk0 | 18.84 ms/req | 19.02 ms/req | +1.0%（噪声带内） | b2 / v6b |
| debug | 16MiB-chunk0 | 300.49 ms/req | 302.83 ms/req | +0.8%（噪声带内） | b2 / v6b |
| debug | 32MiB-chunk1 | 610.16 ms/req | 604.43 ms/req | −0.9%（噪声带内） | b2 / v6b |
| release | 1MiB-chunk0 | 898.05 µs/req | 766.62 µs/req | **−14.6%** | v6c / v6a |
| release | 16MiB-chunk0 | 15.14 ms/req | 11.44 ms/req | **−24.4%** | v6c / v6a |
| release | 32MiB-chunk1 | 25.82 ms/req | 21.21 ms/req | **−17.9%** | v6c / v6a |

- 解读：debug profile 下成本被 debug 编译的 SHA256 主导（两条路线都必须每请求算一次全文件 hash，语义要求），冗余读消除被淹没（±11% 噪声带，F02 §7 同口径）；release profile 下真实 IO/系统调用成本占比上升，**chunk=整文件的 16MiB 档收益最大（−24.4%）**，与"三读=3×全文件读→单趟=1×全文件读"的分析一致。
- **F02 P3-9 unverified 断言闭合**：release 实测 1MiB=898µs（基线）/766µs（优化后），比 F02 冻结的 debug 18424.5µs 低 **~20-24 倍**——"release 构建显著低于 debug 量级"由 unverified 转为**实测 verified**。
- per-chunk 路线（O(文件)→O(chunk)）未走（§5）；AC2 冻结文本明示单趟路线（消除冗余读）达标。

### AC3 — TOCTOU 残留窗口消除 ✓
单趟 capture：served bytes ≡ digest-covered bytes，"digest 通过后再重读一次"的窗口不复存在；读后仅保留 post-read identity re-check（RC1-AC4，注释已改写为准确语义）。遗留窗口不大于现状且严格更小（现状含窗口，本实现结构性消除）。

### AC4 — dead-code 清零 + 更名 ✓
- `cargo build 2>&1 | grep "never read"` @5d7cff11：**空输出**（grep EXIT=1=无匹配）。raw/v3。
- 对照（stash 法，同机同 target）：基线 6 warnings 含 `field 'grant' is never read`；优化后 5 warnings，该条消失，其余 5 条（MockCoreChannel/MockEntry never constructed 等，非 test 构建下测试专用结构的既有告警 + `std::sync::Arc` unused）为**基线既有**，逐条 diff 一致（证据：v3 生成过程，见 raw/v3 头注）。
- `identity_change_rejected_by_per_request_verification`：名称与实际语义（每请求文件 identity 比对拒绝）一致，doc-comment 说明更名缘由。

### AC5 — 证据纪律 ✓
- 全部 raw 日志带 shell/解释器头、ISO 时间、固定 HEAD（5d7cff11 或注明 9df29a6f 基线态）、尾部 EXIT。
- `git diff --check 956e6c3a..HEAD`：EXIT=0。raw/v5。
- `git diff --name-status 956e6c3a..HEAD`：范围自检通过（§1），仅无条件允许路径。
- 三层验证：cargo 全量 34 passed ✓ + loop 定向 ✓；`python -m pytest tests/m2_acceptance -q`（TASK-012-py312，worktree 根）：**35 passed** 0 xfailed，EXIT=0，基线不回退。raw/v4。

## 4. 测试命令与 EXIT 一览

| # | 命令 | cwd | 结果 | EXIT | 日志 |
|---|---|---|---|---|---|
| v1 | `cargo test --bin m2rc1-desktop` | src-tauri | 34 passed; 1 ignored | 0 | raw/v1-cargo-full.log |
| v2 | `cargo test f02_equal_size_rewrite_stability_loop -- --nocapture` | src-tauri | 1 passed（50 轮） | 0 | raw/v2-cargo-loop.log |
| v3 | `cargo build 2>&1 \| grep "never read"` | src-tauri | 空输出 | 1（无匹配=PASS） | raw/v3-cargo-build-never-read.log |
| v4 | `TASK-012-py312/Scripts/python.exe -m pytest tests/m2_acceptance -q` | worktree 根 | 35 passed | 0 | raw/v4-pytest-m2acceptance.log |
| v5 | `git diff --check 956e6c3a..HEAD` + `--name-status` | worktree 根 | 空/范围符合 | 0 | raw/v5-diff-check-namestatus.log |
| v6a | `cargo test --release --no-run` + `cargo test --release perf_chunk_request_digest_cost -- --ignored --nocapture` | src-tauri | 1 passed（release 数字） | 0 | raw/v6a-release-perf.log |
| v6b | `cargo test perf_chunk_request_digest_cost -- --ignored --nocapture`（debug，HEAD 复跑） | src-tauri | 1 passed | 0 | raw/v6b-after-perf-debug-head.log |
| v6c | `git checkout 9df29a6f -- src/main.rs src/resource_protocol.rs` + release perf + 恢复 HEAD + porcelain 复核 | src-tauri | 1 passed；src/ 恢复干净 | 0 | raw/v6c-release-perf-baseline.log |
| b1/b2 | 基线 loop + 基线 debug perf（优化前，9df29a6f 源码态） | src-tauri | loop 1 passed / perf 1 passed | 0 | raw/b1-*.log、raw/b2-*.log |

## 5. per-chunk digest 评估结论：不实施（未启用条件允许路径）

1. **授权范围硬约束**：resolve 的 grant→wire 序列化位于 `src/infrastructure/resource_channel/host_bridge.py:103-114`（手写字段枚举，非 dataclass 自动序列化）。per-chunk 摘要要端到端生效必须改该文件，而条件允许路径仅覆盖 `src/application/resource_channel/dto.py`、`service.py`、`core_bridge.rs`、契约文档、`tests/core`——**host_bridge.py 不在其中**。半途实施（DTO/Rust 收了字段但 Core 永远不发）会产生永不生效的死字段，重蹈 GrantCache 写入即弃的覆辙。
2. **AC2 允许单趟路线达标**：冻结 AC2 明示"per-chunk 路线或消除冗余读（单趟路线）"二选一；单趟已消除 2 次冗余读并闭合 TOCTOU，release 实测 −14.6%~−24.4%。
3. **收益场景无产品证据**：per-chunk 的增量收益（O(文件)→O(chunk)）只在"多 chunk 大资源（最大 256 MiB）被反复分片访问"时兑现；当前无该访问模式的实测/需求证据，而 Core issue 侧需一次性 O(文件) 分块 hash 预计算 + 契约修订 + rev bump 全链条成本。
4. 若未来需要：先由 Codex 扩大条件允许路径至 `host_bridge.py`（及 issue 侧 facts 采集链），再按契约流程实施。

## 6. NOT_RUN / 遗留

| 项 | 状态 | 说明 |
|---|---|---|
| 触点 6 机理对照实验（同 tick 碰撞 vs LazyWriter 元数据延迟，F02 P3-7） | NOT_RUN | 可选授权项未实施；两种机理在现行实现下同向失效（mtime 已完全不参与判定），不影响正确性与验收 |
| `python -m pytest tests/core -q` | NOT_RUN（按指令条件） | 仅实施 per-chunk 时要求；本交付 Python 零改动，m2_acceptance 35 passed 已覆盖不回退线 |
| 真 Core sidecar 通道 f02 复放、时钟矩阵穷举（F02 遗留） | NOT_RUN | 维持 F02 集成记录登记，非本 Task 范围 |
| `cargo build --release`（app bin） | 变通 | release 口径用 `cargo test --release`（构建 release 测试二进制）测量；perf 断言都在测试二进制内，app bin 不承载测量逻辑 |
| worktree `apps/desktop/frontend/dist` 缺失 | 已变通 | gitignored 构建副产物；自 F02 worktree 复制（tauri::generate_context! 仅要求路径存在，内容不参与任何测试断言），不进 git |

## 7. 风险与交接提示

- perf 探针为 `#[ignore]`，不会拖慢默认套件；若 Reviewer 复测请用 §4 v6 系命令（同机同 target 口径，绝对数字受机器状态影响，趋势可复现）。
- `TestEnv` 持有 TempDir 后，测试失败时也会清理 fixture 目录；若未来某测试需要跨测试访问 fixture 路径，请显式复制路径而非依赖泄漏行为。
- 下一接收者：**DeepSeek Harness（非作者 Review）**。建议 Review 锚点：`resource_protocol.rs` 的 `stream_digest_and_capture`（捕获区间数学、`served != expected_size` 错误路径）、`handle_m2res_request`（F-01 语义不变、无残留缓存语义）、AC2 四格对比的口径一致性（b2/v6b 为同 profile 基线/after；v6c 为源码态回退测量，恢复后 porcelain 干净）。
