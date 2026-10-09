# P02 Codex Scratch Build Gate：BLOCKED

日期：2026-10-09（Asia/Shanghai）

## 决定与范围

- 本 Gate 只评估一次 Codex-only detached scratch build 是否能证明写入隔离；不评价产品 AC，也不改变 Owner allowlist、P02 scope、基线或状态。
- 方案固定审查 commit=`803594e9c16f3c361e99fa5ffa7c35a95baaf43a`；方案 Review=`approved`，范围仅为计划与 scratch 输出边界。Owner Stage A r8=`89413f45a601966eb40d7af7abea65cbdfc754b3` 已通过独立 Review 与 Codex Integration Gate。
- Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`。Hard Build Barrier 保持；P02=`in_progress / ACTIVE`，AC1–AC6=`BLOCKED`。P01 不重做，P02 不重冻结。
- 独立 Gate Reviewer=`/root/review_scratch_build_plan`，结论为 `BLOCKED`。审查确认 requirements pins 与版本快照一致，但当前证据无法证明 PyInstaller hooks、递归 import/subprocess 和第三方缓存写入均限制在 scratch。

## 已完成的只读证据

- inventory=`codex-scratch-build-python-env-inventory.json`，SHA-256=`a7f2b7c28ed1ac5872d04c495d09f47b836ff3443c886bd56e5360a07c0b4d13`，source HEAD=`803594e9c16f3c361e99fa5ffa7c35a95baaf43a`。命令 `python.exe -B -m pip freeze --all` EXIT=0，列出 62 个 distributions、0 个 direct-reference；9 个 `requirements-build.txt` 直接 pin 与当前 venv 版本一致。
- venv 中 `distutils-precedence.pth` 的 SHA-256 与计划既有记录一致；检查到 PyInstaller 自带 hooks 480 个文件，hooks-contrib stdhooks 684 个文件。仅目录计数/版本快照未确定本次 PyInstaller 分析会实际执行的 hooks。
- 可读到的 sidecar 构建输入 pins 和 scratch 固定输出路径与隔离方案一致；root 已存在的 `frontend/dist`、sidecar bundle 仍禁止复用/覆盖。
- 本次文档更新后的项目路线校验器在 integration worktree HEAD `803594e9c16f3c361e99fa5ffa7c35a95baaf43a` 上 EXIT=0：196 个 Task 节点、依赖/状态/链接一致，产品 build/test/GUI 显示 `NOT_RUN`；`git diff --check` EXIT=0。该规划校验不是产品构建或 AC 验证。

## 未满足的隔离证明

1. **实际 hook 闭包与代码 hash 未固定。** `G:/CODEX/New Manga.task-envs/m2ac5-build/Lib/site-packages/_pyinstaller_hooks_contrib/stdhooks/hook-torch.py:43` 的 `hook()` 调用 `collect_submodules("torch")`；PyInstaller 的 `collect_submodules()` 会在隔离子进程中导入模块（`PyInstaller/utils/hooks/__init__.py:567–665`）。当前 inventory 只列包版本，没有列出本次会执行的 hooks、代码 hash、可达导入和副作用边界。
2. **递归导入与子进程写路径未证明。** PyInstaller isolated worker 从父进程复制环境并保留 `PYTHONPATH`（`PyInstaller/isolated/_parent.py:167–177`）。包版本快照不能证明递归 import 不触发外部写入。
3. **第三方 cache 变量尚未形成最终执行清单。** Torch 从 `TORCH_HOME` / `XDG_CACHE_HOME` 推导 hub/cache 路径（`torch/hub.py:89–90,187–188,276`）；Hugging Face 从 `HF_HOME`、`HF_HUB_CACHE`、`HF_XET_CACHE` 等推导 cache 与 token 路径（`huggingface_hub/constants.py:160–180,254,341–342`）。本次只读 inventory 没有记录未来 build 进程对这些变量的最终赋值，也没有证明所有触达路径都只落在 scratch。`PYINSTALLER_CONFIG_DIR` 可重定向 PyInstaller 自身配置缓存（`PyInstaller/configure.py:53–71`），但这不覆盖 Torch/Hugging Face 或 hook 子进程的所有写入。

以上是“隔离尚未被证明”，不是发生了 root 或用户目录写入的证据。方案中拟设的缓存变量只是计划；不得将其当成已执行的准入检查。

## 现场与下一步

- 审计时 root=`G:/CODEX/New Manga`、branch=`main`、HEAD=`7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a`；202 个既存 dirty/untracked 路径、0 staged。r8 integration worktree=`C:/Users/49745/.codex/worktrees/p02-stage-a-r8-integration/New Manga`、branch=`codex/P02-stage-a-r8-integration`、HEAD=`803594e9c16f3c361e99fa5ffa7c35a95baaf43a`；common Git directory 相同。保护清单原始 294 项的 entries SHA-256=`f5175b610e7570859143ad35a6167b2ed0d155d737ac33e3c38953fc1e6aa5c1`。
- 继续项仅为只读核对可达 hook 文件/hash、递归 import/subprocess 与所有 cache/env 写路径。只有能证明写入仅在固定 scratch allowlist 内，Codex 才能另行记录 PASS Gate；若静态闭包不能证明，则须补充可执行的进程级隔离设计并经 Review。此记录本身不授权 build。
- 本轮未运行 Cargo/Tauri/sidecar/frontend build、Vitest、GUI、真实 WebView/CDP 或 P02 runner；未关机、push、发布或部署。

## 2026-10-09 当前续跑：闭包审计完成，进程隔离方案待审

本节更新前文的“继续只读 hook/cache 核验”动作；该动作已完成，但结果仍是 BLOCKED。

- 当前 live root=`main@549a6544f0be1eec66c09ece393fd1a409f10bf3`，parent=`803594e9c16f3c361e99fa5ffa7c35a95baaf43a`；`7ce3c40...`、已审计划 `803594e...` 均为祖先。root 当前 203 条 status entries、0 staged；完整逐路径 SHA 起点见 [`process-isolation root manifest`](codex-process-isolation-root-start-manifest.json)，entries SHA=`3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`。这些 dirty/untracked 内容未修改。
- Codex 子代理在固定 549 HEAD 检查实际安装 hook、isolated subprocess 环境继承与 Torch/Hugging Face cache 路径；结论=`BLOCKED / NOT_VERIFIED`，报告见 [`hook/cache audit r1`](codex-hook-cache-closure-audit-r1.md)。静态清单不能证明递归 import/子进程完整写入闭包。
- Windows Sandbox 方案=`PROPOSED / REVIEW_PENDING`，详见 [`WSB process isolation proposal`](codex-scratch-build-process-isolation-proposal-r1.md)。环境探针为 Windows 11 Pro build 26300、`wsb 0.8.107.0`、无运行 session。查询 Sandbox Windows Feature 需要提升权限，所以 feature enabled 状态为 `UNKNOWN`；未提权、启用功能或启动 Sandbox。
- 下一步：固定该 proposal HEAD 并派 DeepSeek Harness 做非作者 exact-head Review。Review approval 仅允许后续尝试隔离 smoke；真实 smoke 前不得运行产品 build。当前 `Build Gate=BLOCKED`、build=`NOT_AUTHORIZED / NOT_RUN`、P02 AC1–AC6=`BLOCKED`、Hard Build Barrier 有效。
- 本轮没有运行 PyInstaller、Cargo/Tauri/frontend build、P02 runner、Vitest、GUI 或 WebView，也未运行 Sandbox smoke。

## 2026-10-09 Process Isolation r2（Review r1 CHANGES_REQUESTED 后修订）

- DeepSeek Harness 对固定 r1 commit c542a31b102cdc5c129efd9df155a2760ed777b2 的正式结论为 CHANGES_REQUESTED（P1=1、P2=7、P3=3），报告见 dsh-review-process-isolation-r1.response.md。r1 未授权 isolation smoke 或 build；Hard Build Barrier 继续生效。
- Codex 提交了 scope delta；唯一跨出 verification/P02/** 的授权修改是 doc/tasks/P02.md 中 Codex-only scratch-build output boundary 一行。固定输出目录为 G:\CODEX\P02-scratch-build-source，普通 clone 使用 --no-local --no-hardlinks，私有 common directory、无 alternates/origin；路径已存在即阻塞。
- r2 逐项回应 R01–R11：隔离对象、映射表和 guest path、固定 RW clone、离线 npm/Cargo cache seed、ProtectedClient/config hash、session/window screenshot、core.autocrlf=true、真实映射 smoke、stopped session 检查、MemoryInMB=2048、root entries hash recipe。
- 真实输入 host inventory 见 codex-scratch-build-input-host-inventory-r1.md。真实 pre-start tree manifest、cache seed hash、Sandbox feature/UI/runtime probes 尚未生成，不能记为 PASS。
- 受保护 root 起点仍是 main@549a6544f0be1eec66c09ece393fd1a409f10bf3，203 个 dirty/untracked entries、0 staged；起始清单 hash 未变。产品 AC1–AC6=BLOCKED、Build Gate=BLOCKED、build=NOT_AUTHORIZED / NOT_RUN、Sandbox/smoke=NOT_RUN、Sandbox feature=UNKNOWN；未提升权限、未启用 feature、未启动 Sandbox。
- Process isolation proposal 当前为 PROPOSED / REVIEW_PENDING。下一步先固定 r2 candidate commit，再派 DeepSeek Harness 对 exact head 独立 Review；Review 通过最多只允许尝试 isolation smoke，不允许 build。
- r2 Smoke XML artifact 为 codex-p02-wsb-smoke-config-r2.xml，SHA-256=dcb95da5252709f9ada9899cd92dcc90c388fa81f4ba23cdb60f18663ac691b6，2397 bytes。候选 Networking token 跟随官方 wsb start --config 示例的 Disabled；WSB 文件参考列出 Disable，运行时 CLI/parser 接受状态仍 NOT_VERIFIED。SHA-256 对应 UTF-8 无 BOM/LF 的 Git blob canonical bytes；core.autocrlf 可能转换 checkout 行尾，运行时须归一 CRLF→LF 后对同一字符串核 hash 并传入 CLI。Python XML parser 只验证 XML 结构、10 mappings、1 RW/9 RO 和字段，不证明 WSB 接受或执行该配置。


## 2026-10-09 Process isolation r2 Review 后续

- DeepSeek Harness r2 对 `3555213a748a7b407400589e1490a387353dec16` 的方案 Review=`APPROVED`（仅设计），P0/P1/P2=0、P3=10；详情见 [`r2 DSH Review`](dsh-review-process-isolation-r2.response.md) 与 [`r2 review checkpoint`](codex-checkpoint-p02-process-isolation-r2-review.md)。批准最多允许在当前候选通过复审、完成 preflight 后尝试一次 isolation smoke；未授权 Smoke 自动 PASS 或 Build。
- Codex 已登记 DSH r2 的 F-01–F-09 处置：Build-only Git/MSVC inputs、网络静默忽略 fail-closed、未来 Build memory 范围仍 UNKNOWN、Smoke 系统/资源阈值、clone clean stop、scratch-local RO canary、可复算分级 manifest/hash 与 cache secret scan、r2 hash erratum。F-10 的原始 JSONL 因包含 thinking events 留在 checkout 外并登记 SHA；最终 response/prompt/dispatch 已进入版本化证据。
- 最新候选 r3 的 exact-head 独立 Review 尚待进行；Smoke=`NOT_AUTHORIZED / NOT_RUN`。即使 r3 Review 通过，也仅允许执行本机非提权、只读 feature/resource preflight；所有前置条件满足后才尝试隔离 smoke。
- 本 Gate 继续=`BLOCKED`，build=`NOT_AUTHORIZED / NOT_RUN`，Hard Build Barrier 有效，P02 AC1–AC6=`BLOCKED`。本轮不运行产品 build、runner、Vitest、GUI 或 WebView。
