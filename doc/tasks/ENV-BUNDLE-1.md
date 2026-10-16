---
id: ENV-BUNDLE-1
title: 重建与协议 2.3 匹配的 sidecar bundle 与 frontend dist（解 BL-11b）
kind: infra
governance_version: 2
status: ready
approval: coordinator_release_20261016_after_dsh_restart
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [HOST-ISSUER-1, HOST-CORE-1]
base_commit: ea23da4d1f96d3294a6a8b353bfa113f15f80254
branch: codex/ENV-BUNDLE-1-sidecar-rebuild
worktree: G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/ENV-BUNDLE-1
---

# ENV-BUNDLE-1：重建与协议 2.3 匹配的 sidecar bundle 与 frontend dist

## 来源与目标

- 来源：**BL-11b**（`.orchestrator/BACKLOG.md`、`.orchestrator/BL11-ENV-EVIDENCE.md`）。
- **问题事实**：主仓 `apps/desktop/src-tauri/target/core-sidecar/` 的 bundle 构建**早于**协议升到 **2.3**
  （P13-C1 → P16-C1 → P12-C1 → HOST-ISSUER-1-C1 的连续协议演进之后**未重建**），
  因此它与当前源码**协议不匹配**：所有依赖真实 sidecar 的 Rust 集成测试报
  `PROTOCOL_VERSION_UNSUPPORTED` / `CORE_UNAVAILABLE`（**主仓与任何 worktree 均相同：58 passed / 6 failed**）。
- **影响**：**一切打包端到端验证目前都是 `NOT_RUN`** —— 包括 HOST-ISSUER-1 的 packaged HostControl E2E、
  P18 的真实链路、以及 P12/P17/P19 未来需要的端到端结论。
- **目标**：按项目既定方式重建 bundle 与 frontend 产物，使真实 sidecar 集成测试可用于验收。
- **授权依据**：这是"**处理阻塞集成-验证-恢复的技术债**"，且修复入口由项目文档明确规定
  （`packaging/m2ac5/README.md` §1–§2），无产品取舍。

## Acceptance Criteria

- [ ] AC1 **构建 venv**：按 `packaging/m2ac5/README.md` §1 创建/确认专用 build venv
      `G:/CODEX/New Manga.task-envs/m2ac5-build`，并 `pip install -r packaging/m2ac5/requirements-build.txt`；
      归档 **pip 原始日志**（含解析到的版本）与 Python 版本。**必须先做可行性探测**（见 AC6）。
- [ ] AC2 **重建 bundle**：从仓库根运行 `packaging/m2ac5/build_sidecar.ps1 -Force`，
      使 `apps/desktop/src-tauri/target/core-sidecar/core-sidecar` 与**当前源码**一致；
      归档完整原始日志与退出码（bundle 为 gitignored 产物，不产生 Git 变更）。
- [ ] AC3 **frontend build**：完成 `apps/desktop/frontend` 的生产构建，使 `frontend/dist` 与当前源码一致
      （按 `packaging/m2ac5/README.md` §2a；亦为 gitignored 产物）；归档原始日志与退出码。
- [ ] AC4 **验证（本 Task 的核心验收）**：在**已被并入最新 main 的 worktree** 中运行
      `cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml`，
      **此前 6 项因协议不匹配而失败的真实 sidecar 集成测试应转为通过**；
      归档**原始日志与退出码**，并逐项列出这 6 个用例的新结果。若仍有失败，必须逐项给出根因。
- [ ] AC5 **不越界**：**不修改**产品代码（`src/**`、`apps/**` 的源文件）、契约、Schema、依赖清单（`requirements.txt` /
      `Cargo.toml` 的产品依赖）；只创建/重建 **gitignored 构建产物与隔离 venv**。
- [ ] AC6 **先探测后执行（Anti-Thrash）**：在下载大型依赖（torch / transformers / doctr / PySide6 等）前，
      **先做小规模连通性/可用性探测**并记录；若网络/磁盘/工具链不可用 →
      **标 `BLOCKED` 并给出原始失败证据**，**不得**反复重试同一策略，也不得伪造成功。
- [ ] AC7 固定 head、写 Handoff、提交固定 commit（仅 Task/Handoff/verification 入库）；Coordinator 集成。

## 允许修改范围

- **新建/重建（gitignored，不入库）**：`G:/CODEX/New Manga.task-envs/m2ac5-build`、
  `apps/desktop/src-tauri/target/**`、`apps/desktop/frontend/dist/**`、`apps/desktop/frontend/node_modules/**`（如需）。
- **入库**：本 Task（`doc/tasks/ENV-BUNDLE-1.md`）、`doc/handoffs/ENV-BUNDLE-1-*.md`、`verification/ENV-BUNDLE-1/**`。
- 只读引用：`packaging/m2ac5/{README.md,build_sidecar.ps1,requirements-build.txt,core_sidecar.spec}`、
  `requirements.txt`、`apps/desktop/src-tauri/{tauri.conf.json,build.rs}`、`.orchestrator/BL11-ENV-EVIDENCE.md`。

写入仅限本 Task worktree `G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1`；
**构建产物若超 worktree，必须落在 `G:/CODEX/New Manga.workspace/` 或项目既定的 `task-envs/` 下**。

## 禁止范围

- **不得修改**产品源码、契约、Schema、`requirements.txt`、`Cargo.toml` 的产品依赖、`build.rs` 的校验逻辑。
- **不得**删除或覆盖用户既有 dirty/untracked、既有 worktree、既有 `task-envs`（新建 venv 除外）。
- **不得**为"让测试通过"而**放宽断言、跳过用例、或伪造 sidecar**；验收必须是**真实**打包产物驱动。
- 不 `push`、不 `merge`（集成由 Coordinator 执行）、不 `reset`、不 `stash`。
- 不得把大型二进制产物提交入库（保持 gitignored）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC6 探测 | pip 连通性/小包探测 + 磁盘空间检查 | 本机 | NOT_RUN | 无 |
| AC1 venv | `python -m venv` + `pip install -r requirements-build.txt` | 本机 + 网络 | NOT_RUN | 无 |
| AC2 bundle | `build_sidecar.ps1 -Force` | venv 就绪 | NOT_RUN | 无 |
| AC3 frontend | `npm ci` + `npm run build`（或既有脚本） | node/node_modules | NOT_RUN | 无 |
| AC4 验收 | `cargo test --locked`（6 项既有失败应转通过） | 重建后的 bundle/dist | NOT_RUN | 无 |

## 依赖、风险与阻塞

- `depends_on`：HOST-ISSUER-1（`done`）、HOST-CORE-1（`done`）—— 二者把协议推进到 2.3，正是需要重建的原因。
- 风险一（成本）：build venv 需下载 ML 运行时闭包（可能数 GB），耗时且依赖网络 → **AC6 先探测**。
- 风险二（磁盘）：bundle 约 1.2 GB，PyInstaller 中间产物可能更大 → 执行前检查可用空间。
- 风险三（不可伪造）：**不得**用 mock/跳过方式让 6 项测试"变绿"；必须真实重建。
- 阻塞：若网络/磁盘/工具链不可用 → 标 `BLOCKED` + 原始证据；**不得**同策略重复重试。

## 交付与运行记录

- 2026-10-16 Coordinator 释放（dsh, epoch 5）：base=`ea23da4d1f96d3294a6a8b353bfa113f15f80254`；
  依据 R1–R6 恢复后的 R6 判定（BL-11b 是取得真实端到端结论的唯一路径）+ `packaging/m2ac5/README.md` 的既定指引；
  Owner 按 DIR-2 路由为 **codex**。
- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无（全部 `NOT_RUN`）。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| build-venv | G:/CODEX/New Manga.task-envs/m2ac5-build | PRESERVE_REFERENCED | G:/CODEX/New Manga.task-envs/m2ac5-build | verification/ENV-BUNDLE-1/resource-manifest.json | 新建的隔离构建环境；保留以便后续重建；closeout 时补写 manifest |
| bundle | G:/CODEX/New Manga/apps/desktop/src-tauri/target/core-sidecar | PRESERVE_REFERENCED | G:/CODEX/New Manga/apps/desktop/src-tauri/target/core-sidecar | verification/ENV-BUNDLE-1/resource-manifest.json | gitignored 构建产物；重建为与协议 2.3 一致；保留 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：本 Task 全部 AC 尚未执行（`NOT_RUN`）。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` / 本 Task 导航在释放时同步。
