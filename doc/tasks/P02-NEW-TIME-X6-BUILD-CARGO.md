---
id: P02-NEW-TIME-X6-BUILD-CARGO
title: P02 新时点 X6 后续 Build / Cargo 构建门
kind: verification
governance_version: 2
status: in_review
approval: user_authorized_new_time_baseline_20261014
suggested_owner: ZCode
owner: Antigravity
reviewer: DeepSeek Harness
integrator: Codex /root
depends_on: [P02-NEW-TIME-X6, P02-NEW-TIME-X6-POSTRUN-REVIEW]
base_commit: 49d2a2f9c56462f5602b00ad4b824c5381abb1ab
branch: agent/antigravity/P02-NEW-TIME-X6-BUILD-CARGO
worktree: G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO
integration_commit: null
delivery_head: db4870ab87d36f0663b5e45e4f7b2e3cf9b77917
reviewed_head: null
review_decision: pending
integration_target: main
integration_status: not_started
dispatch_state: IN_REVIEW
blocked_by: []
profile: ANTIGRAVITY_FALLBACK
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

- [x] BC-AC1：Codex 冻结本 Task、源码/依赖/构建输入 manifest、外部模型文件 hash、独立 worktree 与输出路径；所有输入固定到记录的 commit 或 SHA-256。本机冻结工具链为 Node v24.15.0/npm 12.0.1、Python 3.12.3、Cargo 1.98.1 (797e8a9bc)、rustc 1.98.1 (48a229cea) stable-x86_64-pc-windows-msvc。原 ZCode live AGENT_PREFLIGHT r2=`PASS`；故障转移后的 Antigravity `agy 1.3.5` 探测成功，在其固定 branch/head 上完成 live AGENT_PREFLIGHT（`overall=PASS, dispatch_allowed=true`），验证 CLI、Node/git、Task worktree、write scope、fallback 及 quota/permission/session attestation。Tauri CLI 固定为 2.12.2；npm registry 元数据 pin：主包 integrity=sha512-PMSppzAnlT+BvZtRKuidxjRSm2r5t8kDpJ/czmmQUa0AtDNTwrjLE8vApK3phCWGg7isfnYL46Dl1jB4ArI0hA==、Windows x64 MSVC 包 integrity=sha512-cQXI2ZaZmwBDt0XATCqASVanYizxkEE3ceQVlVHXaQ51HzsQUWA04c9Nz7LrrY2lgAu3jFMyat+8Yz3Z2R2qBA==；执行 Build 命令前在 frozen npm metadata 复核通过。
- [x] BC-AC2：前端从 lockfile 安装并构建成功：`npm ci --no-audit --no-fund`、`npm run build` 均 exit=0；`apps/desktop/frontend/dist/index.html` 与 asset 存在，`package.json` 与 `package-lock.json` 构建前后字节不变，Codex 独立核验输出哈希。原始记录见 `agent-output/zcode/P02-NEW-TIME-X6-BUILD-CARGO/run-r1/01-frontend-npm-ci/` 和 `02-frontend-npm-run-build/`，输出纳入 ZCode run evidence manifest。
- [x] BC-AC3：隔离 Python 3.12 build venv 安装 `packaging/m2ac5/requirements-build.txt` 的精确依赖（9/9 与 pip-freeze 匹配）；sidecar 首次失败后在独立 attempt 2 成功生成完整 onedir。Codex 独立校验 5,610 个文件、1,296,373,783 bytes 的大小/hash、无多余文件、五个入口和 pinned 权重。未来 Cargo/Tauri 命令的 TEMP、TMP、PYTHONPYCACHEPREFIX、PYINSTALLER_CONFIG_DIR、npm cache、CARGO_HOME 均须置于 Task env；不得重跑已成功的前端或 Sidecar。
  - Manga `model.safetensors`: `037930A861E67870EB345BE01B28CC70D7E2B7956528E48EE0EBDB0C093DF80D`；`config.json`: `B6D707933E12E9593A7025604BE1C95ADD70A6DB371FDD1532E8854E2256E072`；`preprocessor_config.json`: `7E9E2245806AA3EF068A5321F5EEBEE3116FA4CEC560173231954FFACA930ECA`，来源目录 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector/`。
  - SFX `yolo11s-seg.onnx`: `944E811410933AD6FF8D32446FCC9EEF90FB463794E1874CE83035E83ACD418D`，来源目录 `G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights-v2b/`。
  - Sidecar 目标位于隔离 Task worktree 的 `apps/desktop/src-tauri/target/core-sidecar/core-sidecar/`；五个入口 `host_bridge.exe`、`core_service.exe`、`acceptance_bridge.exe`、`catalog_loader.exe`、`sfx_detect_probe.exe` 均存在，权重逐项 hash 符合。
- [x] BC-AC4：在 `apps/desktop/src-tauri/` 执行 `cargo build --locked --release` 与 `npx --yes @tauri-apps/cli@2.12.2 build`，均 exit=0，并将 npm_config_cache 与 CARGO_HOME 指向本 Task 独立 env。NSIS installer `target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe` 存在（581,475,034 bytes，SHA-256=`A1DD05B64FABBA311A62FDCF9F496C3902B89614577BFDC85B71C70D7DB06C7B`）；实际 CLI/toolchain 版本、最终产物 size/SHA-256 与所有原始命令/stdout/stderr/exit 均已在 `06-cargo-build-attempt2` 和 `07-tauri-build-attempt1` 完整记录。
- [ ] BC-AC5：Codex 确认本 Task 未改生产代码、共享契约、依赖清单、lockfile 或构建脚本；所有 cargo/frontend/sidecar/package 产物只在本隔离 worktree 的 ignored build 路径产生。若 Tauri 生成 tracked schema/permission 文件，先保留前后字节/hash；仅当逐文件证明内容除 CRLF/LF 外完全相同，才可恢复这些精确生成路径；任何其他变更原样保留并暂停在 Codex adjudication，不得 reset/clean/stash。
- [ ] BC-AC6：DSH 对冻结 build 输入 manifest、构建命令与结果 manifest 做一次独立、只读 Review，绑定固定 delivery HEAD；列明 P0–P4、限制、finding ID 与影响。DSH 结果由 Codex 重算 pins、scope 与输出闭合性；不得仅凭 exit=0 或自然语言 PASS 接受。
- [ ] BC-AC7：Codex 按 official `evaluate-result` / `classify-revision` / `decide-convergence.py --mode converge` adjudicate；仅在当前 P0/P1/P2 blocker=0 且输出安全可集成时将 Build/Cargo 标为通过，并把独立产品 AC1–AC7 Task 置为下一 READY。任何 Build finding 按 I1/I2 上限、bounded review、follow-up/resolution lineage 与 DAG 重规划处理；禁止 I3、无限返修和提前产品 AC 放行。

## 允许修改范围

- 本 Task 的状态、Handoff 与 `verification/P02-NEW-TIME-X6-BUILD-CARGO/**`；ZCode 已产生的原始输出保留于 `G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6-BUILD-CARGO/**`；Antigravity 后续命令和 Handoff 输出写入 `G:/CODEX/New Manga.workspace/agent-output/antigravity/P02-NEW-TIME-X6-BUILD-CARGO/**`。
- 构建生成物仅写入本 Task linked worktree 下 `apps/desktop/frontend/node_modules/**`、`apps/desktop/frontend/dist/**`、`apps/desktop/src-tauri/target/**`，以及 `G:/CODEX/New Manga.workspace/task-envs/P02-NEW-TIME-X6-BUILD-CARGO/**`；pip、npm/npx、Cargo cache 均设在后者，不写入用户 profile。
- Antigravity 可更新本 Task 的运行/证据/resource 表与交付记录；不得编辑产品代码、依赖或共享配置。Codex 在 AGY 完成后独立核对所有 Git、原始输出和 artifact。

## 禁止范围

- 不改 `src/**`、`apps/desktop/frontend/src/**`、`apps/desktop/src-tauri/src/**`、`Cargo.toml`、`Cargo.lock`、`package.json`、`package-lock.json`、`packaging/**`、业务资源/模型源文件及共享契约。
- 不改 root main checkout 的既有 dirty/untracked 文件；不访问或改写旧 H1/P2-1 及 13 项缺失来源，不运行 X6 executor 或重用任何 RunId。
- 不运行 `cargo test`、产品 AC1–AC7、Windows Sandbox、NSIS installer、已构建应用或任何 UI/OS/ACL/registry/profile/API 检查；本 Task 只生成安装包，不安装/启动。
- 发现必须改代码/构建脚本/依赖才能通过时，停止越界修改并交 Codex 依 official convergence 重规划；不得在本 Task 扩大源码范围。

## 测试要求

| 场景/AC | 计划命令或步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| BC-AC1 freeze/preflight | official evidence manifest dry-run/live/verify；`preflight-agent.py --agent antigravity --repo <worktree> --write-scope ... --config <agents.json> --attestation <attestation.json>` | 两个 X6 依赖均 Codex APPROVED；Task/worktree/outputs 固定；当前 AGY CLI 为 1.3.5，live preflight PASS | PASS：AGY live AGENT_PREFLIGHT `overall=PASS, dispatch_allowed=true`；npm metadata 校验通过 | source-manifest-r1、supplemental-inputs-r1、generator-verify-r2；原 ZCode preflight r2；agy-probe-manifest-r2；BC-BUILD-PREFLIGHT-AGY-LIVE-R1、BC-BUILD-PREFLIGHT-AGY-BUNDLE-R1 |
| BC-AC2 frontend | `npm ci --no-audit --no-fund`; `npm run build` | Node v24.15.0/npm 12.0.1；`package-lock.json` pinned；npm cache 位于 task-env | PASS：两命令均 exit=0；dist entry/asset 存在；两个 package 文件哈希未变 | `agent-output/zcode/P02-NEW-TIME-X6-BUILD-CARGO/run-r1/{01-frontend-npm-ci,02-frontend-npm-run-build}/`；ZCode run evidence manifest；Codex partial verification manifest |
| BC-AC3 sidecar | `python -m venv <task-env>/venv`; `pip install -r packaging/m2ac5/requirements-build.txt`; `powershell -NoProfile -ExecutionPolicy Bypass -File packaging/m2ac5/build_sidecar.ps1 -Force -PythonExe <task-env-python> -WeightsSource <pinned-source> -SfxWeightsSource <pinned-source>` | Python 3.12；PIP_CACHE_DIR 在 task-env；所有 pinned weight 输入可读且 hash 相符 | PASS：9/9 pinned package versions match；attempt 2 exit=0；5,610 files / 1,296,373,783 bytes 独立 hash 验证通过；attempt 1 失败日志保留 | `agent-output/zcode/P02-NEW-TIME-X6-BUILD-CARGO/run-r1/04-sidecar-pip-install/`、`05-sidecar-build/`、`05-sidecar-build-attempt2/`；sidecar-bundle-manifest；Codex partial verification manifest |
| BC-AC4 cargo/package | `cargo build --locked --release`; `npx --yes @tauri-apps/cli@2.12.2 build` | Cargo 1.98.1/rustc 1.98.1 stable MSVC；frontend dist + sidecar 已 PASS；npm/Cargo cache 在 task-env | PASS：Cargo attempt 2 exit=0；Tauri attempt 1 exit=0；NSIS installer 存在且哈希验证通过 | `agent-output/antigravity/P02-NEW-TIME-X6-BUILD-CARGO/run-r1/{06-cargo-build-attempt2,07-tauri-build-attempt1}/`；`antigravity-run-evidence-manifest-r1.json`；`build-artifacts-manifest-r1.json` |
| BC-AC5 scope/integrity | `git status --short`; before/after hash; generated-file normalization check | Build worktree tracked status clean；sidecar ignored outputs 已完成 hash audit | PARTIAL / Codex adjudication required：发现 44 ignored `__pycache__` dirs、87 `.pyc` files；缺少运行前 ignored inventory，无法证明创建或覆盖；构建过程生成 24 个 schema/permission 仅 CRLF 差异文件未暂存未恢复。均保留不删 | `scope-audit-r1.json`、Codex partial verification manifest；后续 Codex + DSH review 判断 AC disposition |
| BC-AC6 DSH Review | 单次 DSH readonly result Review | build input/result manifests 已冻结验证 | NOT_RUN | DSH report/raw dispatch |
| BC-AC7 adjudication | official result/convergence helper + DAG update | DSH report 完整且 pins 未漂移 | NOT_RUN | Codex adjudication/convergence |

本 Task 不运行产品测试；所有未运行内容保留为 `NOT_RUN/BLOCKED`，不得填作 PASS。

## 依赖、风险与阻塞

前置 Gate：`P02-NEW-TIME-X6=approved`（唯一新时点 X6 运行、Codex VERIFY PASS）与 `P02-NEW-TIME-X6-POSTRUN-REVIEW=approved`（DSH Review、Codex adjudication/convergence 已接受）；未通过不得 Build。父 X6 的 I1/I2=`1/2` 不被本 Task 重置。本 Task 自身 I1/I2 从 `0/2` 开始。

Build 时显式复用 `packaging/m2ac5/README.md` 中的 Windows 构建链。模型源位置属于既有外部 task-env 内容，只读并保留；Task venv、PIP/npm/Cargo cache、build 与安装包输出置于 `New Manga.workspace` 或本隔离 worktree。Tauri CLI 主包与 Windows x64 MSVC binary 固定 2.12.2 并在 frozen npm metadata 中复核完整性。正式 Build/Cargo 不代表应用运行或用户数据验收，也不解除旧 H1/P2-1 状态。

## 交付与运行记录

- Handoff：已完成，见 [P02-NEW-TIME-X6-BUILD-CARGO-antigravity-handoff.md](../handoffs/P02-NEW-TIME-X6-BUILD-CARGO-antigravity-handoff.md)。
- DSH Review：待派发；Cargo 与 Tauri 构建已完成，安装包已生成。
- Build 命令：依测试表顺序执行，原样保留每步 stdout/stderr/exit 与环境版本；失败输出不覆盖、不重跑已经成功的输出目标。
- 本 Task 完成不等于 AC1–AC7 通过；下游 AC Task 必须另行冻结、preflight、执行、Review 与 Codex adjudication。

## Owner Failover / Partial Recovery

- ZCode `run-r1` 因 provider error 1308 / HTTP 429、五小时额度上限以 CLI exit 1 结束；无交付 commit、Handoff 或 tracked worktree 修改，所有原始日志和已完成产物均保留。该 transport/agent 可用性故障不构成 Build 技术 Gate 结论，也不计作一次实现修订。
- 按项目 fallback 顺序由 Antigravity 接管同一隔离 worktree 的 partial artifact；Branch 在派发前改为 `agent/antigravity/P02-NEW-TIME-X6-BUILD-CARGO`，保留现有 clean tracked tree 与 ignored 产物，不允许第二个并发 Writer。Antigravity CLI `agy 1.3.5` fresh probe `exit=0/status=SUCCESS`，manifest SHA-256=`11CDC5065D919CFC42EB6DCB6B94FED582731E3B27772206C753DDF702C0BE2A`；live AGENT_PREFLIGHT 通过后方可派发。
- 接管者须先读本 Task、`codex-failover-adjudication-r1.md`、scope audit 与 ZCode 输出 manifest；不得重跑已 PASS 的前端或 Sidecar。仅在新目录执行 Cargo attempt 2；Cargo 成功后才可执行 Tauri。设置 `TEMP`、`TMP`、`PYTHONPYCACHEPREFIX`、`PYINSTALLER_CONFIG_DIR`、npm cache 与 `CARGO_HOME` 均指向本 Task env；完整记录命令、stdout/stderr/exit、tool versions 和产物 hashes。不删除、不覆盖或清理已观察到的任何 `.pyc`、PyInstaller cache、venv、npm/Cargo cache 或旧 attempts。
- Source-scope audit 记录 44 个 ignored `src/**/__pycache__` 目录、87 个 `.pyc` 文件及 Sidecar log 中的用户 profile PyInstaller cache 路径；因无运行前 ignored inventory，无法区分创建与覆盖。内容已 hash 并保留，BC-AC5 留待 Codex/DSH 按证据 adjudicate；未来构建需重定向缓存，不能以清理解决不确定性。
- 无 `BLOCKED_WAITING_EXTERNAL_DECISION`：存在已验证可用 fallback，且 Cargo 可在受控环境继续；产品 AC1–AC7 仍为 BLOCKED。

## Canonical Evidence

源码清单冻结于 `source_manifest_commit=55ad82050a4b64f22b493998c9fc99523feeb92e`，产品源码相对 `49d2a2f9c56462f5602b00ad4b824c5381abb1ab` 未变。官方 generator 已 pin 318 个 tracked build inputs；其 mutable-name guard 排除 `Cargo.lock` 与两个 `snapshot` 命名源码文件，这 3 项均以独立 commit+SHA-256 记录在 supplement。四个外部模型权重/配置哈希匹配，Tauri CLI 2.12.2 两个 npm registry integrity 已复核。原 ZCode live AGENT_PREFLIGHT r2 对其冻结 Owner worktree 返回 `overall=PASS`、`dispatch_allowed=true`；ZCode 故障后 Antigravity 1.3.5 live AGENT_PREFLIGHT 在固定 Owner branch/head 上完成（`overall=PASS, dispatch_allowed=true`）。Cargo build attempt 2 与 Tauri build attempt 1 均以 exit=0 成功完成，产物哈希已固定。

| evidence_id | AC/Gate | path | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| BC-BUILD-SOURCE-MANIFEST-R1 | BC-AC1 tracked source/dependency/build inputs (318 files) | verification/P02-NEW-TIME-X6-BUILD-CARGO/source-manifest-r1.json | e21765f4923ce820f3285e663af40aba724b40ec | 4E91A92291629C776F0B54A36E0805F0219F40778DA4EDB70B85E23B298B5E3B | CANONICAL |
| BC-BUILD-SUPPLEMENTAL-INPUTS-R1 | BC-AC1 generator exclusions, external model pins, toolchain and npm metadata | verification/P02-NEW-TIME-X6-BUILD-CARGO/supplemental-inputs-r1.json | e21765f4923ce820f3285e663af40aba724b40ec | 09EFF15C58D9D646ADE97F25E8F6F9250921780E1D84A2CC555E3281C9111848 | CANONICAL |
| BC-BUILD-MANIFEST-VERIFY-R2 | BC-AC1 official manifest verification (318 files) | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-BUILD-CARGO/build-inputs-r1/generator-verify-r2/stdout.json | - | 4091F317BFFE7FBF7C9708BAF0E6EC1C962C981575BF2EA5A9CDB19AEE870B9B | CANONICAL |
| BC-BUILD-PREFLIGHT-ZCODE-R1 | BC-AC1 ZCode live AGENT_PREFLIGHT | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-BUILD-CARGO/preflight-live-r1/stdout.json | - | 34E73C4D48CE839241361E886B079EE73E68714906157045D0FA9D1BB07A5A6B | CANONICAL |
| BC-BUILD-PREFLIGHT-BUNDLE-R1 | BC-AC1 preflight attempts evidence manifest | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-BUILD-CARGO/preflight-evidence-manifest-r1.json | - | 40B0072BA46E1496C4890C9D311ACCDFA49752B572263661B77B93EF846E7261 | CANONICAL |
| BC-BUILD-PREFLIGHT-ZCODE-R2 | BC-AC1 ZCode final live AGENT_PREFLIGHT | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-BUILD-CARGO/preflight-live-r2/stdout.json | - | 80E4E413BC2966F2855EB540ACA8A1B846F8553D8788A659AA58F24A9D7C1077 | CANONICAL |
| BC-BUILD-PREFLIGHT-BUNDLE-R2 | BC-AC1 final ZCode preflight attempts manifest | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-BUILD-CARGO/preflight-evidence-manifest-r2.json | - | FB693FC6846DE1BA493A60C5E6F07F284E29363D4592A92D9EC4E4C703B94ED1 | CANONICAL |
| BC-BUILD-ZCODE-RUN-R1 | ZCode transport failure and partial Build outputs | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-BUILD-CARGO/zcode-run-evidence-manifest-r1.json | - | C9C3F4EF8A7E02A76BB83BD64457B845213381FD44E4745D99638625520564A9 | CANONICAL |
| BC-BUILD-PARTIAL-VERIFY-R1 | Codex AC2/AC3 partial output verification | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-BUILD-CARGO/codex-partial-verification-manifest-r1.json | - | 19A28055E8C7FFC9B064345130E1A54F1C341CA2514CF3FA04082D1F0B0DE404 | CANONICAL |
| BC-BUILD-SCOPE-AUDIT-R1 | ignored outputs and scope observation | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-BUILD-CARGO/scope-audit-r1.json | - | B847C162DBBA5A0AA7E028659CA2C1AF823A2E4F37E35CF2145FAB6DC580E923 | CANONICAL |
| BC-BUILD-AGY-PROBE-R2 | Antigravity 1.3.5 live probe | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-BUILD-CARGO/agy-probe-manifest-r2.json | - | 11CDC5065D919CFC42EB6DCB6B94FED582731E3B27772206C753DDF702C0BE2A | CANONICAL |
| BC-BUILD-SIDECAR-R1 | exact sidecar output inventory (5,610 files) | G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6-BUILD-CARGO/run-r1/05-sidecar-build-attempt2/sidecar-bundle-manifest.json | - | CA0F531ADE3B83D5FFD7627643A2393443702F2B48FF60080EF1284B6BAD8175 | CANONICAL |
| BC-BUILD-FAILOVER-ADJUDICATION-R1 | Codex recovery, partial verification and failover decision | verification/P02-NEW-TIME-X6-BUILD-CARGO/codex-failover-adjudication-r1.md | - | 5BD778C252B09E8D6FC2187280B240D5280C55BC906FE46794A5F221F2472EBA | CANONICAL |
| BC-BUILD-PREFLIGHT-AGY-LIVE-R1 | BC-AC1 Antigravity live AGENT_PREFLIGHT stdout | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-BUILD-CARGO/preflight-antigravity-r1/live-r1-stdout.json | - | 86EB6009D9DABE0AF2D9BF6BC33E1D9965C535646A1EB9EFAD37DFA879A23E11 | CANONICAL |
| BC-BUILD-PREFLIGHT-AGY-BUNDLE-R1 | BC-AC1 Antigravity live preflight attempts manifest | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-BUILD-CARGO/preflight-antigravity-r1/preflight-evidence-manifest-r1.json | - | F5B058B907FFAEBFC401A4B21DB51F311B3761244C073DBE8E9793CD6315B859 | CANONICAL |
| BC-BUILD-AGY-RUN-R1 | BC-AC4 Antigravity Cargo attempt 2 & Tauri attempt 1 run evidence manifest | G:/CODEX/New Manga.workspace/agent-output/antigravity/P02-NEW-TIME-X6-BUILD-CARGO/antigravity-run-evidence-manifest-r1.json | - | 9A68B95F8D7B55098A01104F1BC5CBF57438D6326065C6B50CCB035AF355F1B6 | CANONICAL |
| BC-BUILD-ARTIFACTS-MANIFEST-R1 | BC-AC4 Cargo binary and NSIS installer artifacts manifest | verification/P02-NEW-TIME-X6-BUILD-CARGO/build-artifacts-manifest-r1.json | - | CA2BB6CEDD9CE267CAC947681D03CE073C773C08CFE40F5B71623BF16256B57B | CANONICAL |

## Resource Manifest

本 Task 的 build worktree、Python venv、npm/cargo cache、sidecar、dist、Cargo target、installer 与所有失败/成功日志均保留并逐项盘点；禁止因可重建而自动删除。本 Task 不清理任何已有 worktree、model source 或用户数据。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| Build Task worktree | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO | PRESERVE_REFERENCED | same | pending | ZCode branch HEAD `a1fd218a9f8adc587865311b3f3d9aa9076e22fc`; Codex updates will be fast-forwarded, then branch renamed to `agent/antigravity/P02-NEW-TIME-X6-BUILD-CARGO` before AGY preflight; existing artifacts retained |
| Task Python env | G:/CODEX/New Manga.workspace/task-envs/P02-NEW-TIME-X6-BUILD-CARGO | PRESERVE_REFERENCED | same | pending | isolated npm cache and empty user/global npm config created; Python venv/build caches not yet created |
| Codex preparation attempts | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-BUILD-CARGO/ | PRESERVE_REFERENCED | same | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-BUILD-CARGO/preparation-manifest-r1.json | manifest SHA-256=`4AD699F8986B0F67434A0540C0C5D1D8EFC4DDA6B1AE1410AF27898C20DD3E07`; contains helper selftest, npm metadata, and every recorded prep attempt including failures |
| Codex preflight attempts | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-BUILD-CARGO/preflight-evidence-manifest-r1.json | PRESERVE_REFERENCED | same | 40B0072BA46E1496C4890C9D311ACCDFA49752B572263661B77B93EF846E7261 | includes retained dry attempts and live r1 PASS; manifest SHA-256 verified |
| Manga model.safetensors | G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector/model.safetensors | PRESERVE_REFERENCED | G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector/model.safetensors | 037930A861E67870EB345BE01B28CC70D7E2B7956528E48EE0EBDB0C093DF80D | read-only existing model source; verified against frozen expected hash |
| Manga model config | G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector/config.json | PRESERVE_REFERENCED | G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector/config.json | B6D707933E12E9593A7025604BE1C95ADD70A6DB371FDD1532E8854E2256E072 | read-only existing model source; verified against frozen expected hash |
| Manga preprocessor config | G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector/preprocessor_config.json | PRESERVE_REFERENCED | G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector/preprocessor_config.json | 7E9E2245806AA3EF068A5321F5EEBEE3116FA4CEC560173231954FFACA930ECA | read-only existing model source; verified against frozen expected hash |
| SFX detector model | G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx | PRESERVE_REFERENCED | G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx | 944E811410933AD6FF8D32446FCC9EEF90FB463794E1874CE83035E83ACD418D | read-only existing model source; verified against frozen expected hash |
| ZCode raw output | G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6-BUILD-CARGO | PRESERVE_REFERENCED | same | C9C3F4EF8A7E02A76BB83BD64457B845213381FD44E4745D99638625520564A9 | quota failure and completed/partial AC2–AC3 outputs; preserve all attempts |
| Antigravity probe output | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-BUILD-CARGO/agy-probe-r2 | PRESERVE_REFERENCED | same | 11CDC5065D919CFC42EB6DCB6B94FED582731E3B27772206C753DDF702C0BE2A | agy 1.3.5; JSON status SUCCESS; exit 0 |
| Codex partial verification | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-BUILD-CARGO/codex-partial-verification-manifest-r1.json | PRESERVE_REFERENCED | same | 19A28055E8C7FFC9B064345130E1A54F1C341CA2514CF3FA04082D1F0B0DE404 | AC2/AC3 output integrity independently checked; verifier r1 failure retained |
| Scope audit and ignored Python caches | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-BUILD-CARGO/scope-audit-r1.json | PRESERVE_REFERENCED | same | B847C162DBBA5A0AA7E028659CA2C1AF823A2E4F37E35CF2145FAB6DC580E923 | 44 dirs / 87 pyc files retained; no deletion or cleanup |
| Build artifacts | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO/apps/desktop/**/target/** + frontend/dist + node_modules | PRESERVE_REFERENCED | same | CA2BB6CEDD9CE267CAC947681D03CE073C773C08CFE40F5B71623BF16256B57B | 当前 Gate 引用，逐文件 manifest 见 build-artifacts-manifest-r1.json |
| Antigravity run output | G:/CODEX/New Manga.workspace/agent-output/antigravity/P02-NEW-TIME-X6-BUILD-CARGO | PRESERVE_REFERENCED | same | 9A68B95F8D7B55098A01104F1BC5CBF57438D6326065C6B50CCB035AF355F1B6 | 06-cargo-build-attempt2 exit=0, 07-tauri-build-attempt1 exit=0; tool versions and raw logs preserved |
| NSIS Installer & Cargo binary | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO/apps/desktop/src-tauri/target/release/ | PRESERVE_REFERENCED | same | CA2BB6CEDD9CE267CAC947681D03CE073C773C08CFE40F5B71623BF16256B57B | m2rc1-desktop.exe (9,367,040 B, 92AC7B8EFB646FE77DF8245B13C9AF9314BEF415B2F0E007B1CDCEA729BC13FD); m2rc1-desktop_0.1.0_x64-setup.exe (581,475,034 B, A1DD05B64FABBA311A62FDCF9F496C3902B89614577BFDC85B71C70D7DB06C7B) |

## Closeout Record

- Closeout date / Codex：待完成时填写。
- canonical_evidence_status / resource_closeout_status：pending / pending。
- 删除、迁移、归档数量/字节数：0 / 0 B。
- 未关闭项及保留原因：Task execution is active under Antigravity failover; Cargo/Tauri, BC-AC5 adjudication, DSH Review and Codex convergence remain pending.
- 当前指针清理：Build Task 进入终态后更新 STATUS / Plan / Task README / rolling checkpoint。
