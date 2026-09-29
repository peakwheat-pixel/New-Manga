---
id: M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF
title: Resource channel digest 重验成本优化（单趟 hash+capture / per-chunk digest）与 GrantCache 死结构收敛
kind: fix
status: done
release_state: M2_FIX_DIGEST_PERF_RELEASED
approval: approved_by_user_2026-09-29_digestperf_release
execution_approval: approved_by_user_2026-09-29_digestperf_release
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
integrator: Codex（另一子 agent 代行，保持 Owner≠Integrator）
depends_on: [M2-FIX-F02-RESOURCE-CHANNEL-FLAKY]
base_commit: 956e6c3ad3b37fdc274cd6353b285da530e7aeaf
branch: agent/zcode/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF
worktree: G:/CODEX/New Manga.worktrees/M2-FIX-DIGEST-PERF-zcode
delivery_head: 5d7cff11315b36a9b43390e28930a91d39282496
review: doc/reviews/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF-5d7cff11-dsh-r1.md (approved_with_conditions, 0xP0/P1/P2; C1-C4 closed at integration)
integration_merge: bc2529f02dfbd3c378d5e9cd4c9f7ac2ecfe4f15
dispatch_state: INTEGRATED
---

# M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF — Resource channel digest 重验成本优化与 GrantCache 死结构收敛

**已释放 `ready`（2026-09-29，用户批准，编排会话代行 Codex 释放；release commit=治理 commit，base=`956e6c3a`）。** 依赖 [M2-FIX-F02-RESOURCE-CHANNEL-FLAKY](M2-FIX-F02-RESOURCE-CHANNEL-FLAKY.md) 已 `done`（integration `aa2f99b8`）。[release evidence](../verification/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF/release-956e6c3a.md)。

## 来源

登记于 M2-FIX-F02-RESOURCE-CHANNEL-FLAKY 集成收口（2026-09-29，integration merge `aa2f99b8`，[集成记录](../verification/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY/integration-3cef4831/integration.md) §4/§5；来源证据=DSH r1 轴 4/轴 5/P2-1/P3-8，报告 `doc/reviews/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY-fd31a7ad-dsh-r1.md`）。

背景：F02 修复移除了 mtime 短路（NTFS 同 tick 碰撞致等长重写放行的真实产品缺口），改为每请求 `stream_digest` 全量重验——语义最强且冻结接受（1 MiB warm 342µs→18424µs/request，~50x debug profile）。本候选目标是在**不弱化"等长重写必拒"**的前提下消除可避免的成本与死结构。

## 触点（范围，已冻结 2026-09-29）

- `apps/desktop/src-tauri/src/resource_protocol.rs`：
  1. **单趟 hash+capture（必做）**：`verify_and_serve` 一次顺序读文件同时累计 digest 并捕获目标 chunk，比对通过后返回捕获字节——消除现状"整文件 hash（`:434`）+ 丢弃读（`:440-441`）+ 再读（`:449`）"的三读路径，并把 digest→serve 的 TOCTOU 残留窗口（对预持写句柄，M2-S2 T-16 威胁模型；修复前更大，属既有面）一并消除；
  2. **per-chunk digest（授权可选，须经 Core 契约流程）**：grant 携带分块摘要，只验被服务 chunk——安全性等价（响应体即该 chunk），成本从 O(文件) 降到 O(chunk)，消除 16 MiB 分片 ×256 MiB 资源（`MAX_RESOURCE_BYTES`）的 N× 全量 hash 放大。**契约流程授权（Codex 划范围 2026-09-29）**：允许 Python `src/application/resource_channel/dto.py` + `service.py` 最小扩展（DTO 增可选 per-chunk 摘要字段，旧字段语义不变）与 Rust `core_bridge.rs` `Grant` struct 对应扩展；字段须向后兼容（无该字段的 grant 回落全量重验，不得因缺字段失败）；**实施本项时必须在 Handoff 显式声明"已启用条件允许路径"**；
  3. **GrantCache 死结构收敛（必做）**：`CachedGrant.grant` 当前写入即弃（`warning: field 'grant' is never read` @`:68:5`，F02 集成显式接受），处置=删除 `CachedGrant`/`GrantCache` 及其无观察效果的 map 操作，或给出真实消费方（须与 F-01 每请求 resolve 语义兼容）；
  4. **`identity_change_invalidates_cache_entry` 测试更名/收敛（必做）**：缓存失去读取方后该测试名已名不副实（实际验证的是 identity 比对路径），随缓存处置一并更正；
  5. （低优先卫生项）`f02_equal_size_rewrite_stability_loop` 每轮 `mem::forget(dir)` 泄漏 ~50 临时目录，可顺手改为带守卫清理；
  6. （可选补强）机理对照实验：区分"同 tick 碰撞" vs "LazyWriter 元数据延迟"（F02 诊断 P3-7 遗留，跨 tick 负向对照）。

## 允许修改范围（两级授权，冻结）

- **无条件允许**：`apps/desktop/src-tauri/src/resource_protocol.rs`；`apps/desktop/src-tauri/src/main.rs`（资源通道测试段）；`doc/tasks/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF.md`；`verification/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF/**`；`doc/handoffs/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF-*.md`。
- **条件允许（仅实施触点 2 per-chunk 契约修订时启用，Handoff 须声明）**：`apps/desktop/src-tauri/src/core_bridge.rs`（`Grant` struct 最小扩展）；`src/application/resource_channel/dto.py`、`src/application/resource_channel/service.py`（DTO/service 最小扩展，既有字段与语义不变）；`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`（§10 grant 结构最小修订 + rev bump，不弱化既有安全语义）；`tests/core/` 下 resource channel 相关测试文件（DTO 变更的对应断言）。
- **禁止**：其余 `src/**`、`apps/**`、全部 QML/React、schema/migration、依赖清单、打包；发现范围外缺陷只登记候选不扩大范围（AC2 release profile 补测例外：仅测量，不改代码）。

## 硬约束

- **不得弱化"等长重写必拒"语义**：`f02_equal_size_rewrite_after_first_verify_rejected` 与 `f02_equal_size_rewrite_stability_loop`（50 轮）断言不得放宽，loop 红证判别力须保持（F02 集成组 5 已证：修复前代码 50 轮内必红）。
- **不得恢复 mtime 门控/任何基于时间戳粒度的短路**（F02 诊断已证不健全）。
- F-01（每请求 Core resolve 无条件先行）语义不变。

## 验收标准（已冻结 2026-09-29）

- [x] AC1：等长重写必拒语义不弱化——全量 `cargo test --bin m2rc1-desktop` 34 passed（数字随套件演进核实）+ stability loop 定向绿；并留一份"对优化前代码 loop 必红"的判别力红证（F02 集成组 5 已证 50 轮内必红，本 Task 可引用该 artefact 并在优化后 head 复验一次先红）。（实测 @`5d7cff11`：34 passed 1 ignored + loop 1 passed；红证引用 `verification/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY/integration-3cef4831/raw/g5-loop-discrimination-red.log`（FAILED EXIT=101）+ 本 head 复验绿，raw/v1、raw/v2）
- [x] AC2：性能回退目标——chunk 请求成本从 O(文件) 降到 O(chunk)（per-chunk 路线）或消除冗余读（单趟路线），实测前后对比日志留痕（1 MiB 与 ≥16 MiB 各一档，debug profile；release profile 补测以闭合 F02 P3-9 的 unverified 断言，纯测量不涉代码）。（**单趟路线达标**：消除 2 次冗余读，debug 四档 + release 三档前后对比见 [verification-results](../verification/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF/verification-results.md) §3，release 1MiB −14.6%/16MiB −24.4%/32MiB −17.9%，P3-9 实测闭合；per-chunk 不实施，Handoff §5）
- [x] AC3：TOCTOU 残留窗口消除（单趟 capture 路线）或书面说明剩余窗口不大于现状。（单趟 capture：served bytes ≡ digest-covered bytes，digest→serve 窗口结构性消除，Handoff §3-AC3）
- [x] AC4：dead-code warning 清零（`cargo build 2>&1 | grep "never read"` 空输出）；`identity_change_invalidates_cache_entry` 更名后语义与名称一致。（raw/v3 空输出；更名 `identity_change_rejected_by_per_request_verification`）
- [x] AC5：证据纪律同既有惯例（头尾齐全、固定 HEAD、diff --check、范围自检）；三层验证义务——Rust cargo 全量+loop、Python m2_acceptance 全绿（35 passed 0 xfailed 基线不回退）、`git diff --check` 整树 EXIT 0。（raw/v1-v5 全绿；条件允许路径未启用）

## 状态

- 2026-09-29：F02 集成收口时由 Codex（Integrator）登记为候选；**未释放，无 owner/base/branch**。
- 2026-09-29：用户批准释放（编排会话代行 Codex），`proposed → ready`。冻结 base=`956e6c3a`、branch/worktree、两级允许路径、AC1-AC5、硬约束与"等长重写必拒"语义；per-chunk 契约流程范围已由 Codex 划定（见触点 2）。Owner=ZCode（子 agent 代行实现），非作者 Reviewer=DeepSeek Harness，Integrator=另一子 agent 代行 Codex。
- 2026-09-29：Owner 子 agent 交付（claim `b43a1e2a` → 探针 `9df29a6f` → 实现 `5d7cff11` → 回填 `64e6c9a7` → 终 tip `510202ac`）：单趟 hash+capture、GrantCache 删净、测试更名、loop 守卫；per-chunk 评估后不实施（wire 序列化在 `host_bridge.py` 禁止路径，书面留痕）；AC1-AC5 全 PASS。
- 2026-09-29：DSH 非作者 r1 [Review](../reviews/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF-5d7cff11-dsh-r1.md) `approved_with_conditions`（0×P0/P1/P2；A-H 七项 verified，C1-C4 文档/证据条件）。**集成完成 `done`**：集成方闭合 C1（§4 warning 对照更正为 raw 可核验口径，6/5 stash 数字作废）、C2（v7 登记 + 终 tip `510202ac` 绑定 diff-check EXIT=0）、C3（main.rs 生产接线行确认属触点 3 必然删除，见 [集成记录](../verification/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF/integration-510202ac/integration.md) §2）、C4（本 frontmatter 回填）。集成 merge=`bc2529f0`；集成 head 复跑全绿（cargo 34 passed+loop 1 passed+never-read 空 / pytest 35 passed / vitest 31 passed / diff-check 双区间 EXIT=0）。登记遗留：P3-5 `SetFilePointer(offset as i32)` 既有隐患（2 GiB 前不可达）为 planning 候选。
- 2026-09-29：Owner 交付（claim=`b43a1e2a`、探针=`9df29a6f`、delivery_head=`5d7cff11`）。单趟 hash+capture + GrantCache 删除 + 测试更名 + TempDir 守卫；**per-chunk 不实施、条件允许路径未启用**（host_bridge.py 序列化层超范围 + AC2 单趟达标，[Handoff §5](../handoffs/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF-5d7cff11.md)）；触点 6 机理对照 NOT_RUN。AC1-AC5 全勾（实测见 [verification-results](../verification/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF/verification-results.md)）。`ready → in_review`，待 DeepSeek Harness 非作者 Review。
