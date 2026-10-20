---
id: ENV-BUNDLE-1
title: 重建与协议 2.3 匹配的 sidecar bundle 与 frontend dist（解 BL-11b）
kind: infra
governance_version: 2
status: closed_with_limitations
approval: coordinator_release_20261016_after_dsh_restart
suggested_owner: Codex
owner: codex
reviewer: dsh
depends_on: [HOST-ISSUER-1, HOST-CORE-1]
base_commit: c6fda8a09c1a8248ec6617369f9fdf9e1cef79ec
branch: codex/ENV-BUNDLE-1-sidecar-rebuild
worktree: G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1
integration_commit: 7b9cbbe6ac657ec0bef4d84fa0bee45844398e2b
delivery_head: 5a23c503789ffecc4215a5ec96fc250faacbad06
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] AC1 **构建 venv**：按 `packaging/m2ac5/README.md` §1 创建/确认专用 build venv
      `G:/CODEX/New Manga.task-envs/m2ac5-build`，并 `pip install -r packaging/m2ac5/requirements-build.txt`；
      归档 **pip 原始日志**（含解析到的版本）与 Python 版本。**必须先做可行性探测**（见 AC6）。
- [x] AC2 **重建 bundle**：从 worktree 仓库根运行 `packaging/m2ac5/build_sidecar.ps1 -Force`，
      使 `apps/desktop/src-tauri/target/core-sidecar/core-sidecar` 与**当前源码**一致；
      归档完整原始日志与退出码（bundle 为 gitignored 产物，不产生 Git 变更）。
- [x] AC3 **frontend build**：完成 `apps/desktop/frontend` 的生产构建，使 `frontend/dist` 与当前源码一致
      （按 `packaging/m2ac5/README.md` §2a；亦为 gitignored 产物）；归档原始日志与退出码。
- [ ] AC4 **验证（本 Task 的核心验收，部分完成）**：在与最新 main 同 head 的 worktree 中运行
      `cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml`，
      此前 6 项用例均通过，但代码检查确认它们直接启动源码 Python 模块，**没有由重建的 frozen bundle 驱动**；
      因而真实打包端到端验收仍未完成。单独的 frozen EXE 协议 2.3 smoke 通过，详见证据。不得把源码测试结果表述成打包 E2E 通过。
- [x] AC5 **不越界**：**未修改**产品代码（`src/**`、`apps/**` 的源文件）、契约、Schema、依赖清单（`requirements.txt` /
      `Cargo.toml` 的产品依赖）；只创建/重建 **gitignored 构建产物与隔离 venv**。
- [x] AC6 **先探测后执行（Anti-Thrash）**：在下载大型依赖（torch / transformers / doctr / PySide6 等）前，
      **先做小规模连通性/可用性探测**并记录；若网络/磁盘/工具链不可用 →
      **标 `BLOCKED` 并给出原始失败证据**，**不得**反复重试同一策略，也不得伪造成功。
- [x] AC7 Owner 交付：固定 build/evidence head、写 Handoff、提交仅含 Task/Handoff/verification 的 commits。Coordinator 集成与集成后复验待后续 Gate，故 Task 保持 `in_review`。

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
| AC6 探测 | G/C 盘空间检查；`pip download --no-deps packaging==25.0` | PowerShell；Python 3.12.3 可用 | PASS；下载 66,469 bytes，1.638 s；G 盘可用 1.504 TB | `verification/ENV-BUNDLE-1/ac6-probe.md`; `ac6-pip-connectivity.log` |
| AC1 venv | `python -m venv`；`python.exe -X utf8 -m pip install -r packaging/m2ac5/requirements-build.txt` | build venv Python 3.12.3 | PASS；pip 退出码 0，278.794 s；记录 61 个解析包。首次默认编码运行因 cp936 解码 UTF-8 requirements 失败（exit 2），保留原始日志后用 UTF-8 模式成功 | `ac1-venv-create.log`; `ac1-pip-install.log`; `ac1-pip-install-utf8.log`; `ac1-resolved-versions.txt`; `ac1-python-environment.txt` |
| AC2 bundle | `powershell -NoProfile -ExecutionPolicy Bypass -File packaging/m2ac5/build_sidecar.ps1 -Force` | worktree 根；Python 3.12.3 build venv；未跳过权重 | PASS；exit 0，395.8 s；5,563 files / 1,287,287,472 bytes；manifest 与权重 hash 校验通过 | `ac2-build-sidecar.log`; `ac2-bundle-manifest.txt`; `resource-manifest.json` |
| AC3 frontend | `npm ci`; `npm ls --depth=0`; `npm run build` | Node 24.15.0 / npm 12.0.1 | PASS；生产构建 exit 0，2.789 s；50 modules，dist 2 files / 201,081 bytes。首次 npm ci 包装器在 Push-Location 后日志相对路径出错，依赖安装实际完成；后续 npm ls 正常且 build 成功。lockfile SHA 前后不变 | `ac3-frontend.log`; `ac3-frontend-dist-manifest.txt` |
| AC4 验收 | `cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml`；另直接调用 frozen core smoke | 运行时 worktree HEAD = main HEAD `c6fda8a...`；无 `M2RC1_SRC_ROOT`/`M2RC1_PACKAGED` override；显式 Python 3.12.3 | PARTIAL：cargo 76 passed / 0 failed / 1 ignored，exit 0，六个名字均 PASS；经源码检查它们启动 Python 源码模块，不是 frozen EXE。frozen `core_service.exe` 的协议 2.3 ping/ListBooks/shutdown 独立 smoke exit 0；六项打包后端验收仍 NOT_RUN。测试后 main 前进到 `c6f975d...`，需在最新 main 集成后复验 | `ac4-cargo-test.log`; `ac4-six-test-results.md`; `ac4-packaged-core-smoke.log`; SOURCE_PIN `src/main.rs` / `library_bridge.rs`; `final-main-status-observation.txt` |

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
- 执行坐标：worktree `G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1`，分支 `codex/ENV-BUNDLE-1-sidecar-rebuild`；授权坐标所列 main base/head 均为 `c6fda8a09c1a8248ec6617369f9fdf9e1cef79ec`。Task release 文档中的旧 base `ea23da4d...` 与实际 branch/main 不一致，按本 Task 明确坐标使用 c6，并保存 main HEAD 前后证据。
- 构建源码 head：`c6fda8a09c1a8248ec6617369f9fdf9e1cef79ec`；交付证据 head：`14c52c152b9ae058aba4ee29d55d6ed6f7ef6e0f`。证据分批提交：`bda0c4a1476d2fc257012aa04d5e3352408228fe`（主证据）、`ac9e303436c572976c35ea66758b04b687015df8`（probe 行尾规范化）、`ae23664a0b6448be084b94d4d08d7ce63a2f438f`（首次最终主仓状态观察）、`14c52c152b9ae058aba4ee29d55d6ed6f7ef6e0f`（main 前进后的状态复核）。
- AC1–AC3 总耗时：pip 安装 278.794 s、sidecar 全量构建 395.8 s、frontend `npm run build` 2.789 s；合计 677.383 s（不含未精确计时的 `npm ci`）。未使用 `-SkipWeights`。
- AC4 核心结果：cargo 命令 76 passed / 0 failed / 1 ignored，exit 0；唯一忽略项为既有 `perf_chunk_request_digest_cost`。六个目标用例在本次 cargo suite 中全部 PASS。基线日志中五项是协议错误；`same_channel_concurrent_round_trips_keep_response_ownership` 原失败实际因未设置 `M2RC1_PYTHON`，非协议错误。本次显式提供 Python 3.12.3，未设置 source-root/package override。代码检查确认六个测试分别直接启动 Python 源码模块或测试 helper，故它们的 PASS 不证明由新 bundle 驱动。
- Frozen bundle 单独直接运行 `core_service.exe`，协议 2.3 `core.ping`、`ListBooks`、`core.shutdown` 成功，exit 0。六项 cargo 用例使用 frozen EXE 的测试路径没有在当前产品代码/允许修改范围中提供；因此 AC4 的打包驱动核心条件未满足，必须在 Task 状态保持未完成。
- 限制：完整 NSIS 安装器 / packaged HostControl GUI E2E 未运行，对应结论为 `NOT_RUN`。
- 工作区副作用：Cargo 生成的 27 个 Tauri generated 文件仅行尾变化，已逐项从 HEAD 恢复；测试诊断 JSONL 已复制入允许的 verification 路径，原生成文件已移除。产品路径 diff 为空，见 `ac5-product-code-diff.txt`。
- 主仓保护：Task 全程只读主仓。构建/测试期间 HEAD 为 c6；before/after porcelain 快照均为相同 19 项，见 `main-status-comparison.md`。后续曾短暂观察到 22 项，随后 2026-10-16 16:52 状态回到与原快照相同的 19 项；main HEAD 已前进到 `c6f975d38842487c16491eea67a01cf134c337f8`（最新提交 `docs(UI-DESIGN-1): release AD-001 four-page UI/UX design baseline`）。这是本 Task 测试之后的外部 main 更新，须由 Coordinator 在集成后复验。时间点与状态原文见 `final-main-status-observation.txt`。
- Handoff：`doc/handoffs/ENV-BUNDLE-1-codex-14c52c15.md`。
- Review：待独立 review；Coordinator integration 与 integration_commit 待后续 Gate。当前 AC4 打包驱动核心条件未满足，当前状态 `in_review`，不能标为 done。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E01 | AC6 | `verification/ENV-BUNDLE-1/ac6-probe.md` | `ac9e303436c572976c35ea66758b04b687015df8` | b01d91cdffeef07c98df3d4bacfa039f614bc25015f6d48c88a830561fc2fabc | CANONICAL |
| E02 | AC6 | `verification/ENV-BUNDLE-1/ac6-pip-connectivity.log` | `bda0c4a1476d2fc257012aa04d5e3352408228fe` | 9bbe1315e40b3a4f0da2eff50e86a150282f70a20decaa6f75ce05f28cc82eaa | CANONICAL |
| E03 | AC1 | `verification/ENV-BUNDLE-1/ac1-venv-create.log` | `bda0c4a1476d2fc257012aa04d5e3352408228fe` | acebdd0c1d538b40915ddfbde7c8d5b3e6a23e233249f11f3ed9e23f209826f7 | CANONICAL |
| E04 | AC1 | `verification/ENV-BUNDLE-1/ac1-pip-install-utf8.log` | `bda0c4a1476d2fc257012aa04d5e3352408228fe` | 7e0b51e2ee231b95098d8b6ea73468749e7817728e7d90b4c8d949e3a2b29232 | CANONICAL |
| E05 | AC1 | `verification/ENV-BUNDLE-1/ac1-resolved-versions.txt` | `bda0c4a1476d2fc257012aa04d5e3352408228fe` | d95da523290a33d93abcb48d8591650cae9c0ff08aa9f9224968ab8a199f63bd | CANONICAL |
| E06 | AC2 | `verification/ENV-BUNDLE-1/ac2-build-sidecar.log` | `bda0c4a1476d2fc257012aa04d5e3352408228fe` | 6a207ee42ffe1e7086595fb10eff7812ecfa20590cbf63f97506e928861295f7 | CANONICAL |
| E07 | AC2 | `verification/ENV-BUNDLE-1/ac2-bundle-manifest.txt` | `bda0c4a1476d2fc257012aa04d5e3352408228fe` | 184839df2d4915398333728e0eba2434931cb14eb40d0c6e5280333cfb3437cd | CANONICAL |
| E08 | AC3 | `verification/ENV-BUNDLE-1/ac3-frontend.log` | `bda0c4a1476d2fc257012aa04d5e3352408228fe` | 280909e1d4c62d45604a583647a1b704ed9bf23d714694f2c4c81d61c7df77b7 | CANONICAL |
| E09 | AC3 | `verification/ENV-BUNDLE-1/ac3-frontend-dist-manifest.txt` | `bda0c4a1476d2fc257012aa04d5e3352408228fe` | 1a4728255254ac12311ab77f814a23abd96ed3ed75ee137308953397550db062 | CANONICAL |
| E10 | AC4 | `verification/ENV-BUNDLE-1/ac4-cargo-test.log` | `bda0c4a1476d2fc257012aa04d5e3352408228fe` | 96842c63b26f20b61732740ad9f7acea011292a9d33dd7049a14459c9a6bcd97 | CANONICAL |
| E11 | AC4 | `verification/ENV-BUNDLE-1/ac4-six-test-results.md` | `bda0c4a1476d2fc257012aa04d5e3352408228fe` | c3c66c0056d1c87b0b276763207c5bb9f1bf94162a1d85c0c41520132509f8c9 | CANONICAL |
| E12 | AC4 | `verification/ENV-BUNDLE-1/ac4-packaged-core-smoke.log` | `bda0c4a1476d2fc257012aa04d5e3352408228fe` | 7d89da0a284760ec1f107a9bd57dd434e8fe73e581483d58ee0c66fd59dd03c4 | CANONICAL |
| E13 | AC5 | `verification/ENV-BUNDLE-1/ac5-product-code-diff.txt` | `bda0c4a1476d2fc257012aa04d5e3352408228fe` | dfd80195f4cb01fe304b86a570d72c160aa6de429478ca90a81c045cf106a0d2 | CANONICAL |
| E14 | AC5 | `verification/ENV-BUNDLE-1/ac5-generated-side-effects-and-restoration.txt` | `bda0c4a1476d2fc257012aa04d5e3352408228fe` | 695cc472a469250d4cff8ab1f5ce9f24c2a111d7e90cc28775e7e58afd9bf98c | CANONICAL |
| E15 | AC7 | `verification/ENV-BUNDLE-1/main-status-comparison.md` | `bda0c4a1476d2fc257012aa04d5e3352408228fe` | f1fe4cb146081fd8fb34586886b5badf90ef4112bbade46c740abdf6bf4ee49a | CANONICAL |
| E16 | AC7 | `verification/ENV-BUNDLE-1/resource-manifest.json` | `bda0c4a1476d2fc257012aa04d5e3352408228fe` | 8724b89255f40ff0a0081853a5a16e7115eb5db060005b69045e409ef1874793 | CANONICAL |
| E17 | AC7 | `verification/ENV-BUNDLE-1/final-main-status-observation.txt` | `14c52c152b9ae058aba4ee29d55d6ed6f7ef6e0f` | 3d7860118a63d6ecc60cf65e06c4682e6cadd08204ce6bff4e0794c525f18856 | CANONICAL |
| S01 | AC1–AC3 | `packaging/m2ac5/README.md` | `c6fda8a09c1a8248ec6617369f9fdf9e1cef79ec` | 4c40c011e26846d6cee73ace46653222304e7549d1737bb54760bd74d6612706 | SOURCE_PIN |
| S02 | AC1 | `packaging/m2ac5/requirements-build.txt` | `c6fda8a09c1a8248ec6617369f9fdf9e1cef79ec` | c50edd6c3058197003d66049bc28662e9dc7e4175b499ffe9989ae8bca0e7a07 | SOURCE_PIN |
| S03 | AC2 | `packaging/m2ac5/build_sidecar.ps1` | `c6fda8a09c1a8248ec6617369f9fdf9e1cef79ec` | 07e12e80ceb2a35bab96150f4530b7a788b914a2467a32056098adbb775dd30e | SOURCE_PIN |
| S04 | AC4 | `apps/desktop/src-tauri/src/main.rs` | `c6fda8a09c1a8248ec6617369f9fdf9e1cef79ec` | 21972b00bdcf643f950b4a0d3c0a669b86623e80896f818ff14903da938ca1b5 | SOURCE_PIN |
| S05 | AC4 | `apps/desktop/src-tauri/src/library_bridge.rs` | `c6fda8a09c1a8248ec6617369f9fdf9e1cef79ec` | 7599fd78c3c5c7e60647d4a351f54defdb7696bcbd950502c7b55f205437967d | SOURCE_PIN |
| S06 | AC3 | `apps/desktop/frontend/package-lock.json` | `c6fda8a09c1a8248ec6617369f9fdf9e1cef79ec` | 520be4900b855e235b8347f8a179b3cffe4a520069a51464151fc880b05f0295 | SOURCE_PIN |
| EVD-ENVBUNDLE1-REVIEW-R1 | AC7 | `verification/ENV-BUNDLE-1/dsh-review-r1.md` | `8250b4205375c2347f607fb8aa47b4dff22b813f` | `24f847a551a3e866cd487a65ffda473cf8263a8caf8fcda13d5fbf3c375fadd5` | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| build-venv | G:/CODEX/New Manga.task-envs/m2ac5-build | PRESERVE_REFERENCED | G:/CODEX/New Manga.task-envs/m2ac5-build | verification/ENV-BUNDLE-1/resource-manifest.json | 隔离构建环境（Python 3.12.3 + build 闭包，实测约 1.42 GB）；未提交入库；保留以便后续重建 |
| bundle | G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1/apps/desktop/src-tauri/target/core-sidecar | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1/apps/desktop/src-tauri/target/core-sidecar | verification/ENV-BUNDLE-1/resource-manifest.json | gitignored 构建产物；全量重建 exit 0（5,563 文件 / 1.199 GiB / 5 exe）；权重 sha256 校验后打包；保留 |
| frontend-dist | G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1/apps/desktop/frontend/dist | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1/apps/desktop/frontend/dist | verification/ENV-BUNDLE-1/resource-manifest.json | gitignored 前端构建产物；`npm ci` + `npm run build` exit 0；`package-lock` 哈希未变；保留 |
## Closeout Record

- Closeout date / Coordinator：2026-10-16，dsh（epoch 5，lease `264c2000541748298000f93fb25a52de`）。
- canonical_evidence_status：`complete`；resource_closeout_status：`complete`（build venv 与 bundle 均 `PRESERVE_REFERENCED`；0 删除 / 0 迁移 / 0 归档）。
- **状态：`closed_with_limitations`（不是 `done`）**。
- **已完成**：AC1（venv + 依赖，pip exit 0）、AC2（**全量重建 bundle，exit 0，395.8s，5563 文件 / 1.199 GiB，权重 sha256 校验后打包，ICU fail-closed guard 满足**）、
  AC3（frontend 生产构建 exit 0，`package-lock` 未变）、AC5（**产品代码 diff 为空**；cargo 产生的 27 个行尾副作用已还原）、AC6（先探测后下载）。
- **AC4 = PARTIAL（Owner 主动判定，Reviewer 维持）**：`cargo test` 虽 **76 passed / 0 failed / 1 ignored（exit 0）**，
  但本次运行**只设 `M2RC1_PYTHON`**、**未设 `M2RC1_SRC_ROOT`/`M2RC1_PACKAGED`**，
  测试经 `spawn_with_resource_roots(python_exe, src_root, …)` 走**源码模块**路径 → **不构成"由 frozen bundle 驱动"的验收**。
- **BL-11b 的实质已解决（有直接证据）**：`ac4-packaged-core-smoke.log` 显示**真实 frozen `core_service.exe`** 在隔离数据目录、
  精简 PATH、**无 Python/source-root override** 条件下完成 `core.ping`（`{"version":{"major":2,"minor":3},"status":"ready"}`）、
  `ListBooks`、`core.shutdown` 往返，**`overall: PASS`**。
- **归因修正（Review F2，采纳 Owner 的诚实纠正）**：baseline 六项失败实为 **5 项协议错误 + 1 项 `M2RC1_PYTHON` 缺失**
  （`same_channel_concurrent_round_trips_keep_response_ownership`），**并非**六项全为协议不匹配；BACKLOG 的 BL-11b 措辞已同步修正。
- **并行工作归因（Review F3）**：审查期间主仓 HEAD 由 `c6fda8a0` 前进到 `c6f975d3`
  （`docs(UI-DESIGN-1): release AD-001 four-page UI/UX design baseline`，作者 `peakwheat-pixel`），
  为**合法治理提交**（checker PASS、dirty 仍 19）且**保留**了本 Task 的 READY 节点；
  Coordinator **不回退**，集成以最新 main 为基并**保留 `UI-DESIGN-1`**。
- **后续项（Review C2，未闭合）**：需另立**经授权**的 Task，使那六项 Rust 集成测试支持 **`M2RC1_PACKAGED`** 驱动
  （真正调用 frozen bundle）；**在该 Task 完成前不得声称 packaged 六项测试已验收**。
- **其他遗留**：完整 NSIS 安装器与 packaged HostControl GUI E2E 仍 `NOT_RUN`（Review F5）；
  PyInstaller 6.22.3 提示未来 7.0 将阻止管理员身份运行，后续重建应用非管理员终端（Review F4）。
- 交付 head 冻结（Review F6）：Owner 申报 `delivery_head=14c52c15`（证据提交），实际 HEAD=`5a23c503`；已冻结为实际值。
- 当前指针清理：`doc/STATUS.md` / `doc/REBASELINE_PLAN.md` 已同步（**保留 `UI-DESIGN-1`**）。