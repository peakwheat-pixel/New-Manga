---
task_id: M2-FIX-F02-RESOURCE-CHANNEL-FLAKY
author: ZCode（子 agent 代行，用户授权 2026-09-28）
recipient: DeepSeek Harness（非作者 Review r1）→ Codex（Integrator，另一子 agent，保持 Owner≠Integrator）
base_commit: 2b81f91c
delivery_head: fd31a7ad7e8bff338d87f3648577b5abeb173aac
status: DELIVERED_FOR_REVIEW
---

# Handoff：M2-FIX-F02-RESOURCE-CHANNEL-FLAKY（Resource channel 等长重写拒检并发缺口，诊断+修复）

## 交付结果

按冻结 AC1-AC5 完成「先诊断后修复」：**诊断实证推翻"测试 flake"定性——这是真实 M2-S2 产品安全缺口**。AC1 探针 3/3 次运行捕获失败（round 5 / 0 / 2），dump 铁证：等长原地重写后经 handle 读回的 LastWriteTime 与首 verify 记录值**逐位相同**（`mtime_delta_100ns=0`，NTFS 时间戳取值粒度受系统定时器 tick 约束），`needs_digest` 短路为 false，**重写内容被当作已验证内容以 200 serve**；vol/file-index/size 全程不变，排除 identity/size 竞态，唯一通路即 mtime 比对。

AC2 按冻结预期方向修复：`verify_and_serve` **移除 mtime 短路，每次请求都 `stream_digest` 全量重验并对比 `grant.sha256`**，不匹配即 `CONTENT_DIGEST_MISMATCH`（f02 语义保持：重写后必须 400）。`CachedGrant` 删除 `digest_verified`/`verified_mtime` 状态字段（**选清理**：字段唯一用途即短路判定，短路移除后为死代码，全仓 grep 确认无外部引用）；grant cache 退化为只 memoise Core resolve 结果（F-01 语义不变），`CONTENT_DIGEST_MISMATCH` 时的 entry 驱逐保留。

变更路径（全部在允许范围）：

- `apps/desktop/src-tauri/src/resource_protocol.rs`（判定逻辑 + 状态字段清理 + 模块 doc 第 4 点同步为 every-request 语义）
- `apps/desktop/src-tauri/src/main.rs`（资源通道测试段：新增 `f02_equal_size_rewrite_stability_loop` 50 轮断言循环，随修复提交并注明；TEMP-DIAG 探针、TEMP-DIAG entry 读取辅助、TEMP-PERF 计时测试**均已移除**，不进交付）
- `verification/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY/**`（results + 14 份 raw 日志）
- 本 Handoff、Task 回填

Commit ledger：claim `6a404c19` → 交付 `fd31a7ad` → Task 回填（delivery_head=`fd31a7ad`）。

## 诊断记录（Review 重点）

探针方法：TEMP-DIAG `f02_diag_probe_loop`（已移除）在默认线程全 bin 下循环独立重放 f02 场景（首 fetch 200 → `OpenOptions(write)` 等长原地重写 → 二 fetch），捕获首个非 400 时 dump：重写前后 `GetFileInformationByHandle` 原始 mtime（FILETIME 100ns）+ cache entry `digest_verified`/`verified_mtime`（经 TEMP-DIAG `diag_entry_state_for_tests`，已移除）。

捕获 dump 原文（run1 @round 5；run2 @round 0、run3 @round 2 同构，raw/f02_diag_run{1,2,3}.log）：

```text
F02-DIAG captured round=5 second_status=200 body=?+/;6w)3 ?w(?-(3.?w*;#65;>
F02-DIAG facts_before vol=1485189147 idx=2251799817143236 size=26 mtime=134350960517034742
F02-DIAG facts_after  vol=1485189147 idx=2251799817143236 size=26 mtime=134350960517034742
F02-DIAG mtime_equal=true mtime_delta_100ns=0
F02-DIAG entry(digest_verified,verified_mtime)=(Some((true, Some(134350960517034742))))
F02-DIAG: flaky failure captured at round 5 (see stderr dump)
```

- 捕获率：3/3 运行，失败概率极高（LISTBOOKS 集成"三连首跑红"与此一致）；未触发 100 轮降级路径。
- 单线程绿的解释：不是并发竞态，而是 tick 边界概率——fixture 写入与重写跨越系统 tick 时 mtime 不同 → 400（绿）；同 tick → 200（红）。多/单线程只通过耗时分布间接影响落点。
- 修复前基线佐证间歇性：默认线程全量一轮 33 passed f02 绿（raw/f02_baseline_run1.log）。

## 验证证据

环境：Windows 10.0.26200 / Git Bash / cargo 1.98.1 (797e8a9bc 2026-08-05) / Python 3.12.3（`G:/CODEX/New Manga.task-envs/TASK-012-py312`）；日志头含 shell、cargo --version、HEAD、ISO，尾含 EXIT（raw/）。

| AC/场景 | 实际命令 | 被测状态 | 结果 | 日志 |
|---|---|---|---|---|
| 修复前基线 | `cargo test --bin m2rc1-desktop`（默认线程） | claim `6a404c19` 树 | 33 passed（f02 本轮绿，佐证间歇性）EXIT=0 | raw/f02_baseline_run1.log |
| AC1 探针 ×3 | `cargo test --bin m2rc1-desktop -- --nocapture` | 修复前 + TEMP-DIAG | **3/3 捕获**（200 serve 重写内容；delta=0）EXIT=101 | raw/f02_diag_run{1,2,3}.log |
| AC2 性能注记 | TEMP-PERF：1 MiB fixture warm 200 次 chunk-0 请求计时（测后移除） | 修复前 / 修复后 | **342.0 µs → 18424.5 µs/request（~50x；另测 381.3/18606.0，波动 ~11%）**；debug 测试 profile，量级参考；上限受 `MAX_RESOURCE_BYTES`（T1 256 MiB）线性约束 | raw/f02_perf_prefix.log、raw/f02_perf_postfix.log |
| AC3 全量 ×3 | `cargo test --bin m2rc1-desktop`（默认线程） | 修复后（pre-delivery 树，内容=交付树） | **34 passed / 0 failed EXIT=0 ×3** | raw/f02_fix_round{1,2,3}.log |
| AC3 定向循环 | `cargo test --bin m2rc1-desktop f02_equal_size_rewrite_stability_loop` | 同上 | 1 passed（50 场景）EXIT=0；另 3 轮全量内含 3×50=150 场景全绿 | raw/f02_fix_directed_loop.log |
| AC3 单线程对照 | `cargo test --bin m2rc1-desktop -- --test-threads=1` | 同上 | 34 passed EXIT=0 | raw/f02_fix_singlethread.log |
| AC4 Python 回归 | `$py -m pytest tests/m2_acceptance -q` | 主 repo（Python 面零改动） | **35 passed** EXIT=0 | raw/f02_py_m2acceptance.log |
| AC4 Python 回归 | `$py -m pytest tests/core -q` | 同上 | **77 passed** EXIT=0 | raw/f02_py_core_full.log |
| 交付候选复核 | `cargo test --bin m2rc1-desktop`（默认线程） | 交付树（=pre-delivery 树内容） | 34 passed / 0 failed EXIT=0 | raw/f02_final_tip_verify.log |
| 交付 tip 绑定复跑（owner 侧） | `cargo test --bin m2rc1-desktop`（默认线程） | 回填 commit（日志 head 戳为 amend 前 `bf4b3dc0`；并入该日志的 amend 不触碰 src，工作树内容=最终回填 tip 树） | **34 passed / 0 failed EXIT=0** | raw/final-tip-bind-rerun.log |
| AC5 范围/纪律 | `git diff --check 2b81f91c..fd31a7ad`（整树）+ `git diff --name-status 2b81f91c..fd31a7ad` | 交付 tip | **diff --check 空 EXIT=0**；delta 全落允许路径（src 两文件 + verification/** + docs） | raw/scope-and-diff-check.log（见下方提交说明） |

\* AC3 三轮与定向循环执行于交付 commit 创建之前的修复后工作树，其内容与交付 commit `fd31a7ad` 树逐字一致（唯一中间 diff 为 commit 动作本身）；交付候选 tip 复核行（f02_final_tip_verify.log）在提交前于同一内容上复跑，日志 head 戳 `6a404c19`（交付前）。owner 侧 tip 绑定复跑行已补（见上表）；**集成 head 上的最终复跑仍归集成方惯例**。

## 偏差与判定（review 重点）

1. **性能代价 ~50x（0.34 ms → 18.4 ms/request @1 MiB debug profile）**：Task AC2 冻结明示接受方向（"性能注记=每请求一次全文件 hash…记录实测前后请求耗时对比"），如实记录；release 构建显著低于该量级，真实负载（16 MiB chunk 封顶、按需拉取）下的产品影响由集成/产品侧知悉即可。
2. **`CachedGrant` 选清理而非保留兼容**：AC2 给出两选项（"清理或保留兼容（最小，选一注明）"）；清理选最小且无兼容负担——字段为私有 struct 私有字段、全仓无外部引用，删除不构成契约变更。
3. **`mtime` 读取保留**（`_mtime` 绑定）：`identity_size_mtime` 一次返回四元组，identity/size 校验仍每请求执行；mtime 值本身不再参与判定。
4. **worktree dist 构建**：`apps/desktop/frontend/dist` worktree 缺失，`npm install && npm run build` 生成（gitignored，不进交付）；与 LISTBOOKS Handoff 记录的环境前置一致。

## NOT_RUN / 未覆盖（如实登记）

- **release-profile 性能测量未做**：性能注记为 debug 测试 profile 下的相对量级（测试框架内可复现的最小口径）；release 数字留给集成/产品侧按需补测，不阻塞安全语义验收。
- **真实 Core sidecar 通道下的 f02 复放未做**：诊断与稳定性证明均在 MockCoreChannel 通道（与 f02 原测试同口径）；`real_core_sidecar_*` 测试全绿覆盖真进程桥，但未在真通道上重放等长重写场景（原 f02 亦不覆盖，非本 Task 收窄）。
- **多 tick/高分辨率时钟行为矩阵未穷举**：诊断证明"同 tick → 碰撞"存在且高概率；不同 Windows 计时器配置（如 timer resolution 被多媒体/后台进程改写）下 tick 粒度变化只影响碰撞概率、不影响修复正确性（修复后 mtime 不参与判定）。

## 回退方法

revert 交付 commit `fd31a7ad` 即恢复 mtime 短路行为（注意：回退即重新引入本诊断实证的等长重写放行缺口；无 schema/数据迁移、无持久层触碰）。

## 下一任务建议（必填）

- Task ID / 标题：M2-FIX-F02-RESOURCE-CHANNEL-FLAKY 的非作者 Review（DSH r1）→ Codex 集成收口
- 推荐 Agent / Reviewer：DeepSeek Harness（Review）→ Codex（Integrator，另一子 agent，保持 Owner≠Integrator）
- 推荐原因与前置依赖：Task 交付完成，按协作协议进入 Review→集成；本 Task 现为 Review 准备态（in_review）
- Recovery point：仓库 `G:/CODEX/New Manga`；branch=`agent/zcode/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY`；worktree=`G:/CODEX/New Manga.worktrees/M2-FIX-F02-zcode`；固定 base=`2b81f91c`、delivery_head=`fd31a7ad`
- 允许修改路径：`doc/reviews/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY-*/**`（DSH 报告）、`doc/tasks/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY.md`（review/integration_merge 回填）、`verification/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY/**`（集成记录）、`doc/STATUS.md`
- 禁止范围与新增授权条件：Review/集成不得改实现与测试语义；**不得以性能为由恢复 mtime 门控**（诊断已证其不健全）——如需性能优化须另立 Task 且不得弱化"等长重写拒检"语义
- 交付物：DSH review 报告、集成记录、Task 终态回填
- 验证命令、环境与完成 Gate：`cargo test --bin m2rc1-desktop`（cwd=`apps/desktop/src-tauri`，预期 34 passed；前置 worktree `apps/desktop/frontend` 下 `npm install && npm run build` 产 dist）+ `$py -m pytest tests/m2_acceptance -q`（预期 35 passed）+ `$py -m pytest tests/core -q`（预期 77 passed）+ `git diff --check 2b81f91c..<tip>` 整树 EXIT=0 + 范围复算 + Owner≠Integrator 保持
- 可直接转发给 Agent 的指令：对交付 tip `fd31a7ad` 做 M2-FIX-F02-RESOURCE-CHANNEL-FLAKY 非作者静态 Review（重点：AC1 dump 证据链与"真实产品缺口"定性、every-request 全量重验语义与 f02 保持、字段清理最小性、性能接受口径、范围/纪律），产出 `doc/reviews/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY-fd31a7ad-dsh-r1.md`；通过后由 Codex 集成收口。
