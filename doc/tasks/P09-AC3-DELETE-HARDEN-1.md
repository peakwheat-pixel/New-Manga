---
id: P09-AC3-DELETE-HARDEN-1
title: P09 永久删除加固（R3 未闭合项、四项新 P1 与 Schema v5 测试回归）
kind: fix
governance_version: 2
status: ready
approval: user_ruling_20261018_p09_harden_split
blocked_by: null
suggested_owner: Antigravity
owner: Antigravity
reviewer: Codex
depends_on: [P09-AC3-DELETE-1]
base_commit: a04e4ea78d5b33a0f91efcdc06b396391c4b165e
branch: null
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/P09-AC3-DELETE-HARDEN-1
---

# P09-AC3-DELETE-HARDEN-1：永久删除加固

## 来源与授权

- `P09-AC3-DELETE-1` 经**三轮独立复审**（R1/R2/R3）与 **R1fix、R2fix 两次返修**后，第三轮（`verification/P09-AC3-DELETE-1/codex-review-r3.md`）仍为 **`changes_requested`**，已达 **DIR-4**"同一失败面最多 2 次返修"上限。
- 用户 **2026-10-18 裁决**：**拆加固 Task 接手未闭合项，原 Task 以 `closed_with_limitations` 收口**（仿 `P20-CLOSE-BOUND-1` 先例），**不突破 DIR-4**。
- 并行取证（`verification/P09-AC3-DELETE-1/t2-fullsuite-triage.md`）另证实 P09 引入 **1 项 Python 测试回归**（R3 复审因"pytest NOT_RUN"未覆盖），一并由本 Task 接手。

**本 Task 不恢复原 Task 的实施状态；原 Task 的 12 项 finding 与 4 项新 P1 的原始状态不得在本 Task 前置中抹除或改写为 PASS。**

## Acceptance Criteria

- [ ] AC1：**回收站真实入口打通（R-007 收口）**——把回收站专用删除命令注册到 Tauri **production** command 与 `generate_handler!`，并在 Python Core 侧补齐对应 IPC handler，形成 command → Core → Service 的完整路由；回收站查询数据源必须返回**软删除集合**，整库阻止判定基于**全库现存 Book 集合**而非可见列表长度。补**真实装配 / dispatcher** 层断言；UI 不得在失败时静默显示空回收站。
- [ ] AC2：**多页 Run 删除不再冲突（N-001）**——`pipeline_run_targets` 的 `UNIQUE(pipeline_run_id, target_id)` 在删除事务把同 run 所有 target 置空时触发约束，导致整个永久删除回滚。改用唯一且**无定位语义**的 detached 值或等效安全方案；补**至少两个目标**的真实 Run 测试。
- [ ] AC3：**逐项重试可用（N-002）**——`cleanup_pending` 场景下，前端不得只保留 code/message 而丢失逐项目标；用户须能**仅对 pending 子集**重试，已 `deleted` 项不得再次提交（否则返回 `BOOK_NOT_FOUND`）。补"已删除 + pending"混合批量重试测试。
- [ ] AC4：**译图 preview 不残留（N-003）**——把属于目标 Book 的 preview resource IDs 持久化进 cleanup manifest，并纳入**首次与重试**清理；补真实译图（`publish()` 生成的随机 preview-UUID catalog entry）残留断言。
- [ ] AC5：**symlink 替换不得误删（N-004，数据安全）**——删除前必须对**未解析**的目录项与**逐层路径**做 reparse point / containment 检查，禁止先 `resolve()` 再 `lstat()`（会跟随链接看到目的文件）；在 preflight 阶段拒绝被替换的目标，并使用不跟随链接的安全删除方式。
- [ ] AC6：**历史脱离完整（R-003 收口）**——`pipeline_stage_states` 按契约实际 `detach`（不是仅注释）；`run_json` 的**嵌套** `target/task/step` 定位引用一并清理；测试须断言目标 Page ID 不被保留、嵌套引用确实清空。
- [ ] AC7：**AC4 验收真实断言（R-008 收口）**——`verification/P09-AC3-DELETE-1/verify_all.py` 中多张表 `rows = else 0` 的恒真硬编码改为**按表结构的真实 orphan/count 断言**；补 orphan 扫描与含存量派生数据场景。`foreign_key_check` 不得替代 v5 已移除的 page locator 关系核查。
- [ ] AC8：**清理不再递归遍历（R-011 收口）**——移除 `os.walk(storage.root/books/<book_id>)` 式目录遍历（即使只 `rmdir` 空目录也会递归枚举），只按 manifest/catalog **明确登记**的 Managed/derived 目标清理；证明用户导出目录不会被枚举或删除。
- [ ] AC9：**phase 投影白名单（R-009）**——Rust `details.phase` 只投影固定 `preflight` / `cleanup`，未知值降级或被拒绝；补未知值单测。
- [ ] AC10：**★ Schema v5 测试回归修复（T2 取证）**——`tests/packaging/test_frozen_runtime_contract.py::test_explicit_data_root_isolation` 断言 `ver == 4`，而 P09 已升 Schema v5；改为与真实迁移版本一致的断言，并**全仓搜索**其它硬编码 schema 版本断言（此前只修了 `tests/core/test_bootstrap.py`，本项即遗漏结果）。
- [ ] AC11：**权威指针与证据自洽（R-010 / R-012 收口）**——同步 `P09-AC3-DELETE-1` 与原 `P09` 的 `delivery_head`、Canonical Evidence pin（`sha256` 必须与磁盘字节一致）、closeout 状态；消除 `P09.md` 中"已完成"与 `BLOCKED / 未实现"相互矛盾的记录；由有权 Coordinator 记录实现范围释放与 allowlist。
- [ ] AC12：**不回归**——`P09-AC3-DELETE-1` 已闭合项（R-001/R-002/R-004/R-005/R-006）不得退化；软删除与 Page 级 purge 既有语义不变；`AC-IMPORT-002`（源文件零修改）判定不得放宽；全量 `pytest tests` 的失败数不得高于修复前的 4 项。

## 允许修改范围

- Core：`src/**` 中与永久删除、清理 manifest、preview 资源、pipeline 历史脱离、路径安全检查相关的实现与测试。
- Tauri：`apps/desktop/src-tauri/src/**` 中回收站命令注册与 `details.phase` 投影的最小改动。
- 前端：`apps/desktop/frontend/src/recycleBin/**`、`apps/desktop/frontend/src/library/client.ts` 中逐项状态与重试接线的最小改动。
- `verification/P09-AC3-DELETE-1/**`、`verification/P09-AC3-DELETE-HARDEN-1/**`、本 Task、`doc/handoffs/P09-AC3-DELETE-HARDEN-1-*.md`。
- 覆盖率：`tests/**` 中与上述项对应的测试与断言修正（含 AC10 的版本断言）。

## 禁止范围

- 不扩大产品行为；不新增未冻结的 IPC 命令；不改 Schema 结构本身（v5 已冻结）与 ACL 白名单语义。
- **不得为消除失败而改写历史 pin**；只允许**追加**说明。
- 不得用"删测试 / 跳过断言 / 只改判定口径"让 AC 通过。
- 不触碰用户 20 个具名未提交文件（其来源已在 `verification/P02-DOC-PROVENANCE-1/provenance-investigation.md` 取证；**在用户裁决前保持字节不变**）。
- 不得 `git add -A` / `git add .` / `git commit -a`；禁止 `reset --hard` / `clean` / `push` / `stash` / 删除文件。
- GUI/工作流验证必须使用 `%TEMP%` 下的**新建隔离根**，禁止放 `apps/desktop/src-tauri/target/**`；收尾确保 `m2rc1-desktop` / `core_service` / `host_bridge` 全退。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 真实装配/IPC 路由 | Core + Tauri 命令注册断言；回收站数据源与整库集合测试 | 隔离 DB | NOT_RUN | `verification/P09-AC3-DELETE-HARDEN-1/` |
| AC2 多页 Run 删除 | 至少两个目标的真实 Run 永久删除 | 隔离 DB | NOT_RUN | 删除前后行计数与退出码 |
| AC3 逐项重试 | "已删除 + cleanup_pending"混合批量重试 | 隔离 DB | NOT_RUN | 逐项状态序列 |
| AC4 译图残留 | 真实译图 `publish()` 后永久删除，查 orphan | 隔离根 | NOT_RUN | 残留扫描输出 |
| AC5 symlink 替换 | preflight 注入 symlink 替换目标 | Windows 隔离根 | NOT_RUN | 拒绝证据与目的文件未变 |
| AC6 历史脱离 | stage-state 与 run_json 嵌套引用断言 | 隔离 DB | NOT_RUN | SQL 查询结果 |
| AC7 验收脚本 | 运行修正后的 `verify_all.py` | 隔离根 | NOT_RUN | stdout/exit/orphan 清单 |
| AC8 清理范围 | 证明未递归遍历未登记路径 | 隔离根 | NOT_RUN | 文件系统前后清单 |
| AC9 phase 投影 | 未知 `details.phase` 单测 | Rust toolchain | NOT_RUN | cargo test 输出 |
| AC10 版本断言 | `pytest tests/packaging/test_frozen_runtime_contract.py` + 全量 | 集成 Python | NOT_RUN | stdout/exit |
| AC11 指针自洽 | `check.ps1` 全量 + 相关 `-TaskPath` | — | NOT_RUN | 退出码与输出 |
| AC12 回归 | 全量 `pytest tests`，失败数 ≤ 4 | 集成 Python | NOT_RUN | 失败清单 diff |

## 依赖、风险与阻塞

- 依赖：`P09-AC3-DELETE-1`（`closed_with_limitations`）；其未闭合项清单见 R3 复审与本文 AC1–AC11。
- 风险一：AC5 涉及**数据安全**（symlink 替换可能误删 derived root 内其它登记资源），优先级最高。
- 风险二：AC1 需要跨 Tauri/Core 补路由，属"实现范围释放"范围，须先由 Coordinator 记录 allowlist（AC11 的一部分）。
- 风险三：本 Task 不得复用原 Task 的返修计数；若本 Task 自身达到 DIR-4 上限，同样停手上报。

## 交付与运行记录

- Handoff：待 Owner 认领后创建。
- Review：待固定 delivery head 后由 Codex 独立复核。
- 实际测试：NOT_RUN。
- 2026-10-18 Coordinator（dsh, epoch 8）按用户裁决建立本 Task 并冻结范围。

## Canonical Evidence

尚未进入 `in_review`；该表在交付 head 固定后更新。

| evidence_id | AC/Gate | path | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| 不新建 worktree | 复用 `G:/CODEX/New Manga` | `NOT_APPLICABLE` | 不适用 | 不适用 | 未创建、未删除资源。 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- `canonical_evidence_status`：`pending`。
- `resource_closeout_status`：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：待 Owner 交付和 Review。
- 当前指针清理：待 Task 激活或关闭时由 Codex 同步 STATUS/Plan。
