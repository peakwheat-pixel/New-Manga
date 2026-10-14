---
id: P02-NEW-TIME-X6-BUILD-CARGO
title: P02 新时点 X6 后续 Build / Cargo 构建门
kind: verification
governance_version: 2
status: ready
approval: user_authorized_new_time_baseline_20261014
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
integrator: Codex /root
depends_on: [P02-NEW-TIME-X6, P02-NEW-TIME-X6-POSTRUN-REVIEW]
base_commit: 49d2a2f9c56462f5602b00ad4b824c5381abb1ab
branch: agent/zcode/P02-NEW-TIME-X6-BUILD-CARGO
worktree: G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO
integration_commit: null
delivery_head: null
reviewed_head: null
review_decision: pending
integration_target: main
integration_status: not_started
dispatch_state: READY
blocked_by: []
profile: ZCODE_HEAVY
revisions: {implementation: 0, test: 0, evidence: 0}
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/P02-NEW-TIME-X6-BUILD-CARGO
---

# P02-NEW-TIME-X6-BUILD-CARGO：P02 新时点 X6 后续 Build / Cargo 构建门

## 来源与目标

仅在 `P02-NEW-TIME-X6` 的一次 X6 结果通过 Codex VERIFY，且 `P02-NEW-TIME-X6-POSTRUN-REVIEW` 获 DSH `APPROVED`、Codex adjudication 与 convergence `APPROVED` 后执行。本 Task 只判定新时点版本能否完成 Windows 前端、Core sidecar、Cargo 与 Tauri 包构建；不补齐、替代或改写旧 H1/P2-1 及其 13 项原始来源缺失记录。

源码基线为 `49d2a2f9c56462f5602b00ad4b824c5381abb1ab`。Build Task 分支从包含本 Task 合同与前序审查记录的 docs-only 后继提交创建；Codex 在派发前验证后继差异不含生产源码、依赖或构建脚本变更。该提交仅提供当前 Gate 文档，不改变此源码基线。

本 Task 沿用已记录的 `Build Authorization=AUTHORIZED_WITH_EXCEPTION`。该授权仅用于本地构建/打包，不把 `Technical Gate=NOT_SATISFIED`、`private_registry_absence=UNPROVABLE` 或旧 Hard Build Barrier 改写为技术 PASS；禁止安装、启动应用、探测/修改 OS、profile、registry、ACL 或执行产品 AC1–AC7。无需再次请求人工授权，除非真实满足 `BLOCKED_WAITING_EXTERNAL_DECISION` 四项条件。

## Acceptance Criteria

- [ ] BC-AC1：Codex 冻结本 Task、源码/依赖/构建输入 manifest、外部模型文件 hash、独立 worktree 与输出路径；AGENT_PREFLIGHT 对 ZCode 返回 PASS 后才允许 Owner 开始。所有输入固定到记录的 commit 或 SHA-256。本机当前观测工具链为 Node v24.15.0/npm 12.0.1、Python 3.12.3、Cargo 1.98.1 (797e8a9bc)、rustc 1.98.1 (48a229cea) stable-x86_64-pc-windows-msvc；ZCode preflight 必须验证并记录实际值。Tauri CLI 固定为 2.12.2；npm registry 当前元数据 pin：主包 integrity=sha512-PMSppzAnlT+BvZtRKuidxjRSm2r5t8kDpJ/czmmQUa0AtDNTwrjLE8vApK3phCWGg7isfnYL46Dl1jB4ArI0hA==、Windows x64 MSVC 包 integrity=sha512-cQXI2ZaZmwBDt0XATCqASVanYizxkEE3ceQVlVHXaQ51HzsQUWA04c9Nz7LrrY2lgAu3jFMyat+8Yz3Z2R2qBA==；执行前须在 frozen npm metadata 再核验。
- [ ] BC-AC2：前端从 lockfile 安装并构建成功：`npm ci --no-audit --no-fund`、`npm run build`；两命令 exit=0，`apps/desktop/frontend/dist/index.html` 存在且被 manifest pin，`package.json` 与 `package-lock.json` 构建前后字节不变。
- [ ] BC-AC3：在 `G:/CODEX/New Manga.workspace/task-envs/P02-NEW-TIME-X6-BUILD-CARGO/venv/` 创建隔离 Python 3.12 build venv，在同一 Task env 下分别设置 PIP_CACHE_DIR、npm cache 与 CARGO_HOME，按 `packaging/m2ac5/requirements-build.txt` 安装精确构建依赖；使用 `packaging/m2ac5/build_sidecar.ps1 -Force` 产出完整 onedir。必须从以下只读来源取 pinned 权重并再次验证 SHA-256：
  - Manga `model.safetensors`: `037930A861E67870EB345BE01B28CC70D7E2B7956528E48EE0EBDB0C093DF80D`；`config.json`: `B6D707933E12E9593A7025604BE1C95ADD70A6DB371FDD1532E8854E2256E072`；`preprocessor_config.json`: `7E9E2245806AA3EF068A5321F5EEBEE3116FA4CEC560173231954FFACA930ECA`，来源目录 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector/`。
  - SFX `yolo11s-seg.onnx`: `944E811410933AD6FF8D32446FCC9EEF90FB463794E1874CE83035E83ACD418D`，来源目录 `G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights-v2b/`。
  - Sidecar 目标位于隔离 Task worktree 的 `apps/desktop/src-tauri/target/core-sidecar/core-sidecar/`；五个入口 `host_bridge.exe`、`core_service.exe`、`acceptance_bridge.exe`、`catalog_loader.exe`、`sfx_detect_probe.exe` 均存在，权重逐项 hash 符合。
- [ ] BC-AC4：在 `apps/desktop/src-tauri/` 执行 `cargo build --locked --release` 与 `npx --yes @tauri-apps/cli@2.12.2 build`，均 exit=0，并将 npm_config_cache 与 CARGO_HOME 指向本 Task 独立 env。NSIS installer `target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe` 存在；记录实际 CLI/toolchain 版本、最终产物 size/SHA-256 与所有原始命令/stdout/stderr/exit。
- [ ] BC-AC5：Codex 确认本 Task 未改生产代码、共享契约、依赖清单、lockfile 或构建脚本；所有 cargo/frontend/sidecar/package 产物只在本隔离 worktree 的 ignored build 路径产生。若 Tauri 生成 tracked schema/permission 文件，先保留前后字节/hash；仅当逐文件证明内容除 CRLF/LF 外完全相同，才可恢复这些精确生成路径；任何其他变更原样保留并暂停在 Codex adjudication，不得 reset/clean/stash。
- [ ] BC-AC6：DSH 对冻结 build 输入 manifest、构建命令与结果 manifest 做一次独立、只读 Review，绑定固定 delivery HEAD；列明 P0–P4、限制、finding ID 与影响。DSH 结果由 Codex 重算 pins、scope 与输出闭合性；不得仅凭 exit=0 或自然语言 PASS 接受。
- [ ] BC-AC7：Codex 按 official `evaluate-result` / `classify-revision` / `decide-convergence.py --mode converge` adjudicate；仅在当前 P0/P1/P2 blocker=0 且输出安全可集成时将 Build/Cargo 标为通过，并把独立产品 AC1–AC7 Task 置为下一 READY。任何 Build finding 按 I1/I2 上限、bounded review、follow-up/resolution lineage 与 DAG 重规划处理；禁止 I3、无限返修和提前产品 AC 放行。

## 允许修改范围

- 本 Task 的状态、Handoff 与 `verification/P02-NEW-TIME-X6-BUILD-CARGO/**`；原始命令输出写入 `G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6-BUILD-CARGO/**`。
- 构建生成物仅写入本 Task linked worktree 下 `apps/desktop/frontend/node_modules/**`、`apps/desktop/frontend/dist/**`、`apps/desktop/src-tauri/target/**`，以及 `G:/CODEX/New Manga.workspace/task-envs/P02-NEW-TIME-X6-BUILD-CARGO/**`；pip、npm/npx、Cargo cache 均设在后者，不写入用户 profile。
- ZCode 可更新本 Task 的运行/证据/resource 表与交付记录；不得编辑产品代码、依赖或共享配置。

## 禁止范围

- 不改 `src/**`、`apps/desktop/frontend/src/**`、`apps/desktop/src-tauri/src/**`、`Cargo.toml`、`Cargo.lock`、`package.json`、`package-lock.json`、`packaging/**`、业务资源/模型源文件及共享契约。
- 不改 root main checkout 的既有 dirty/untracked 文件；不访问或改写旧 H1/P2-1 及 13 项缺失来源，不运行 X6 executor 或重用任何 RunId。
- 不运行 `cargo test`、产品 AC1–AC7、Windows Sandbox、NSIS installer、已构建应用或任何 UI/OS/ACL/registry/profile/API 检查；本 Task 只生成安装包，不安装/启动。
- 发现必须改代码/构建脚本/依赖才能通过时，停止越界修改并交 Codex 依 official convergence 重规划；不得在本 Task 扩大源码范围。

## 测试要求

| 场景/AC | 计划命令或步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| BC-AC1 freeze/preflight | official evidence manifest dry-run/live/verify；`preflight-agent.py --agent zcode --repo <worktree> --write-scope ...` | 两个 X6 依赖均 Codex APPROVED；Task/worktree/outputs 固定 | PARTIAL：318 tracked inputs manifest 与 supplemental pins 已 VERIFY PASS；ZCode live preflight 尚 NOT_RUN | source-manifest-r1、supplemental-inputs-r1、generator-verify-r2；preflight bundle 待生成 |
| BC-AC2 frontend | `npm ci --no-audit --no-fund`; `npm run build` | Node v24.15.0/npm 12.0.1；`package-lock.json` pinned；npm cache 位于 task-env | NOT_RUN | 原始命令、日志、exit、dist hash |
| BC-AC3 sidecar | `python -m venv <task-env>/venv`; `pip install -r packaging/m2ac5/requirements-build.txt`; `powershell -NoProfile -ExecutionPolicy Bypass -File packaging/m2ac5/build_sidecar.ps1 -Force -PythonExe <task-env-python> -WeightsSource <pinned-source> -SfxWeightsSource <pinned-source>` | Python 3.12；PIP_CACHE_DIR 在 task-env；所有 pinned weight 输入可读且 hash 相符 | NOT_RUN | venv/package version、命令输出、sidecar file manifest |
| BC-AC4 cargo/package | `cargo build --locked --release`; `npx --yes @tauri-apps/cli@2.12.2 build` | Cargo 1.98.1/rustc 1.98.1 stable MSVC；frontend dist + sidecar 已 PASS；npm/Cargo cache 在 task-env | NOT_RUN | command/stdout/stderr/exit、installer manifest |
| BC-AC5 scope/integrity | `git status --short`; before/after hash; generated-file normalization check | Build worktree 在派发前 clean | NOT_RUN | Codex verify report |
| BC-AC6 DSH Review | 单次 DSH readonly result Review | build input/result manifests 已冻结验证 | NOT_RUN | DSH report/raw dispatch |
| BC-AC7 adjudication | official result/convergence helper + DAG update | DSH report 完整且 pins 未漂移 | NOT_RUN | Codex adjudication/convergence |

本 Task 不运行产品测试；所有未运行内容保留为 `NOT_RUN/BLOCKED`，不得填作 PASS。

## 依赖、风险与阻塞

前置 Gate：`P02-NEW-TIME-X6=approved`（唯一新时点 X6 运行、Codex VERIFY PASS）与 `P02-NEW-TIME-X6-POSTRUN-REVIEW=approved`（DSH Review、Codex adjudication/convergence 已接受）；未通过不得 Build。父 X6 的 I1/I2=`1/2` 不被本 Task 重置。本 Task 自身 I1/I2 从 `0/2` 开始。

Build 时显式复用 `packaging/m2ac5/README.md` 中的 Windows 构建链。模型源位置属于既有外部 task-env 内容，只读并保留；Task venv、PIP/npm/Cargo cache、build 与安装包输出置于 `New Manga.workspace` 或本隔离 worktree。Tauri CLI 主包与 Windows x64 MSVC binary 固定 2.12.2 并在 frozen npm metadata 中复核完整性。正式 Build/Cargo 不代表应用运行或用户数据验收，也不解除旧 H1/P2-1 状态。

## 交付与运行记录

- Handoff：尚无；完成后固定 build delivery HEAD。
- DSH Review：尚未派发；仅在 Codex input/result manifest VERIFY PASS 后单次只读派发。
- Build 命令：依测试表顺序执行，原样保留每步 stdout/stderr/exit 与环境版本；失败输出不覆盖、不重跑已经成功的输出目标。
- 本 Task 完成不等于 AC1–AC7 通过；下游 AC Task 必须另行冻结、preflight、执行、Review 与 Codex adjudication。

## Canonical Evidence

源码清单冻结于 `source_manifest_commit=55ad82050a4b64f22b493998c9fc99523feeb92e`，产品源码相对 `49d2a2f9c56462f5602b00ad4b824c5381abb1ab` 未变。官方 generator 已 pin 318 个 tracked build inputs；其 mutable-name guard 排除 `Cargo.lock` 与两个 `snapshot` 命名源码文件，这 3 项均以独立 commit+SHA-256 记录在 supplement。四个外部模型权重/配置哈希匹配，Tauri CLI 2.12.2 两个 npm registry integrity 已复核。ZCode live preflight 仍是 BC-AC1 剩余 Gate。

| evidence_id | AC/Gate | path | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| BC-BUILD-SOURCE-MANIFEST-R1 | BC-AC1 tracked source/dependency/build inputs (318 files) | verification/P02-NEW-TIME-X6-BUILD-CARGO/source-manifest-r1.json | e21765f4923ce820f3285e663af40aba724b40ec | 4E91A92291629C776F0B54A36E0805F0219F40778DA4EDB70B85E23B298B5E3B | CANONICAL |
| BC-BUILD-SUPPLEMENTAL-INPUTS-R1 | BC-AC1 generator exclusions, external model pins, toolchain and npm metadata | verification/P02-NEW-TIME-X6-BUILD-CARGO/supplemental-inputs-r1.json | e21765f4923ce820f3285e663af40aba724b40ec | 09EFF15C58D9D646ADE97F25E8F6F9250921780E1D84A2CC555E3281C9111848 | CANONICAL |
| BC-BUILD-MANIFEST-VERIFY-R2 | BC-AC1 official manifest verification (318 files) | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-BUILD-CARGO/build-inputs-r1/generator-verify-r2/stdout.json | - | 4091F317BFFE7FBF7C9708BAF0E6EC1C962C981575BF2EA5A9CDB19AEE870B9B | CANONICAL |

## Resource Manifest

本 Task 的 build worktree、Python venv、npm/cargo cache、sidecar、dist、Cargo target、installer 与所有失败/成功日志均保留并逐项盘点；禁止因可重建而自动删除。本 Task 不清理任何已有 worktree、model source 或用户数据。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| Build Task worktree | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO | PRESERVE_REFERENCED | same | pending | branch `agent/zcode/P02-NEW-TIME-X6-BUILD-CARGO` at e21765f; isolated under workspace; live preflight snapshot pending |
| Task Python env | G:/CODEX/New Manga.workspace/task-envs/P02-NEW-TIME-X6-BUILD-CARGO | PRESERVE_REFERENCED | same | pending | isolated npm cache and empty user/global npm config created; Python venv/build caches not yet created |
| Codex preparation attempts | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-BUILD-CARGO/ | PRESERVE_REFERENCED | same | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-BUILD-CARGO/preparation-manifest-r1.json | manifest SHA-256=`4AD699F8986B0F67434A0540C0C5D1D8EFC4DDA6B1AE1410AF27898C20DD3E07`; contains helper selftest, npm metadata, and every recorded prep attempt including failures |
| Manga model.safetensors | G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector/model.safetensors | PRESERVE_REFERENCED | G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector/model.safetensors | 037930A861E67870EB345BE01B28CC70D7E2B7956528E48EE0EBDB0C093DF80D | read-only existing model source; verified against frozen expected hash |
| Manga model config | G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector/config.json | PRESERVE_REFERENCED | G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector/config.json | B6D707933E12E9593A7025604BE1C95ADD70A6DB371FDD1532E8854E2256E072 | read-only existing model source; verified against frozen expected hash |
| Manga preprocessor config | G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector/preprocessor_config.json | PRESERVE_REFERENCED | G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector/preprocessor_config.json | 7E9E2245806AA3EF068A5321F5EEBEE3116FA4CEC560173231954FFACA930ECA | read-only existing model source; verified against frozen expected hash |
| SFX detector model | G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx | PRESERVE_REFERENCED | G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx | 944E811410933AD6FF8D32446FCC9EEF90FB463794E1874CE83035E83ACD418D | read-only existing model source; verified against frozen expected hash |
| ZCode raw output | G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6-BUILD-CARGO | PRESERVE_REFERENCED | same | pending | 原样保留每次尝试 |
| Build artifacts | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO/apps/desktop/**/target/** + frontend/dist + node_modules | PRESERVE_REFERENCED | same | pending | 当前 Gate 引用，逐文件 manifest |

## Closeout Record

- Closeout date / Codex：待完成时填写。
- canonical_evidence_status / resource_closeout_status：pending / pending。
- 删除、迁移、归档数量/字节数：0 / 0 B。
- 未关闭项及保留原因：Task 尚未执行。
- 当前指针清理：Build Task 进入终态后更新 STATUS / Plan / Task README / rolling checkpoint。
