---
id: M2-FIX-F02-RESOURCE-CHANNEL-FLAKY
title: Resource channel 等长重写拒检并发缺口（f02 flaky 诊断+修复）
kind: fix
status: ready
release_state: M2_FIX_F02_RESOURCE_CHANNEL_FLAKY_RELEASED
approval: released_by_orchestrator_2026-09-29_goal_g2 (Codex 代行,用户授权 2026-09-28;代理裁决,用户可撤销)
execution_approval: released_by_orchestrator_2026-09-29_goal_g2
suggested_owner: ZCode
owner: ZCode（待认领）
reviewer: DeepSeek Harness
integrator: Codex（另一子 agent 以 Codex 身份执行，保持 Owner≠Integrator）
depends_on: [M2-S2]
base_commit: 2b81f91c
branch: agent/zcode/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY
worktree: G:/CODEX/New Manga.worktrees/M2-FIX-F02-zcode
delivery_head: null
review: null
integration_merge: null
dispatch_state: RELEASED
---

# M2-FIX-F02-RESOURCE-CHANNEL-FLAKY — Resource channel 等长重写拒检并发缺口（诊断+修复）

## 来源与目标

登记于 M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN 集成收口（2026-09-29，integration `69961029`，[集成记录](../verification/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN/integration-b6cb1af2/integration.md) §2 裁定 1），经编排会话按 [GOAL](../GOAL.md) G2 释放（代理裁决，用户可撤销）。

现象：`cargo test --bin m2rc1-desktop` 的 `f02_equal_size_rewrite_after_first_verify_rejected`（`apps/desktop/src-tauri/src/main.rs:798-826`）在**默认线程**下间歇失败（两侧各三连中首跑红：`left: 200 / right: 400` @`:821`），单线程绿。涉及产品判定（M2-S2 资源通道安全语义）：`resource_protocol.rs:426-436` 的 digest 重验短路——

```rust
let needs_digest = !entry.digest_verified || entry.verified_mtime != Some(mtime);
if needs_digest { /* stream_digest 对比 grant.sha256，失败即 CONTENT_DIGEST_MISMATCH */ }
entry.digest_verified = true; entry.verified_mtime = Some(mtime);
```

**假设（待诊断实证）**：等长原地重写后文件 mtime 读回值与首次 verify 记录值相同（Windows/LazyWriter 元数据延迟或 mtime 粒度碰撞）→ `needs_digest=false` → 重写内容被当作已验证内容 serve（200），安全语义「等长重写必须拒绝」出现**真实产品缺口**，测试 flake 只是缺口的可见症状。

## Acceptance Criteria（2026-09-29 冻结）

- [ ] **AC1 — 诊断实证：** 判别探针循环复现（默认线程下循环跑 f02 场景直至捕获 ≥1 次失败，捕获时 dump `entry.digest_verified`/`entry.verified_mtime`/当前 stat mtime/size 对比），**以证据定位根因**（mtime 碰撞/延迟 vs 其他竞态）；诊断记录（含失败捕获率、dump 证据）落 `verification/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY/`。若循环 ≥100 次无法复现，如实记录并改以「代码推理+单线程/默认线程对照矩阵」定性，不得虚构复现。
- [ ] **AC2 — 修复：** 按诊断根因最小修复产品判定。预期方向（若 mtime 假设成立）：**移除 digest 短路、每次 `handle_m2res_request` 都 `stream_digest` 全量重验**（语义最强；性能注记=每请求一次全文件 hash，受 `MAX_RESOURCE_BYTES` 上限约束，记录实测前后请求耗时对比）；`entry.digest_verified`/`verified_mtime` 状态字段随之清理或保留兼容（最小）。若诊断推翻假设，按实际根因最小修，范围仍限下述允许路径。
- [ ] **AC3 — 稳定性证明：** 修复后默认线程 `cargo test --bin m2rc1-desktop` 连续 **3 轮全绿**（每轮完整套件）+ f02 场景定向循环 ≥50 次全绿；单线程对照仍绿。
- [ ] **AC4 — 零回归：** Python 面零改动（`pytest tests/m2_acceptance -q` 35 passed EXIT=0、`tests/core` 77 passed EXIT=0 留痕）；其余 Rust 测试全绿。
- [ ] **AC5 — 证据纪律：** 命令日志带 shell、工具版本、固定 HEAD、EXIT；`git diff --check <base>..<delivery-head>` 整树 exit 0；范围自检仅落允许路径。

## 允许修改范围（2026-09-29 冻结）

- `apps/desktop/src-tauri/src/resource_protocol.rs`（判定逻辑/状态字段）
- `apps/desktop/src-tauri/src/main.rs`（f02 及相关测试、诊断探针辅助；仅资源通道测试段）
- 诊断/验证的临时探针代码随修复提交或移除（二选一，注明）
- `doc/tasks/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY.md`、`verification/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY/**`、`doc/handoffs/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY-*.md`
- 若契约/resource channel 语义文档需要同步（如 digest 重验频率语义），定位后最小修订并登记

## 禁止范围

- Python Core/`src/**`、前端、命令面、其他 Rust 模块、`M2-S2` 安全语义的反向放宽（不得把「等长重写拒检」弱化为可接受）；依赖、schema；既有测试断言语义（f02 语义保持：重写后必须 400 CONTENT_DIGEST_MISMATCH）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 诊断探针循环 | planned：默认线程循环 f02 捕获失败+dump | apps/desktop/src-tauri，cargo | NOT_RUN | 无 |
| AC3 修复后稳定性 | planned：3 轮全量+50 次定向循环+单线程对照 | 同上 | NOT_RUN | 无 |
| AC4 零回归 | planned：`$py -m pytest tests/m2_acceptance -q` / `tests/core -q` | TASK-012-py312 | NOT_RUN | 无 |
| AC5 diff-check | planned：整树 `git diff --check <base>..<tip>` | Git Bash | NOT_RUN | 无 |

## 依赖、风险与阻塞

- depends_on=`M2-S2`（done，资源通道安全语义归属）。风险：性能代价（每请求全量 digest）需记录并接受；若根因不在 mtime，修复方向按诊断重定（仍在允许路径内）。
- 时间盒：诊断阶段若 60 分钟内无法定位根因，按 AC1 的降级路径（代码推理定性）继续，不得无限发散。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无。
- 后续实际记录包含日期、commit、环境、结果、遗留项；最终由 Integrator 填 integration_merge 并改 done。
