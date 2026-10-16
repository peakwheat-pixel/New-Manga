---
task_id: ENV-BUNDLE-1
title: 重建与协议 2.3 匹配的 sidecar bundle 与 frontend dist（解 BL-11b）
reviewer: dsh（项目权威 Reviewer，`.orchestrator/tasks/ENV-BUNDLE-1-role.json`；role_exclusion 已排除 owner=codex）
owner: codex
base_commit: c6fda8a09c1a8248ec6617369f9fdf9e1cef79ec
declared_delivery_head: 14c52c152b9ae058aba4ee29d55d6ed6f7ef6e0f
reviewed_head: 5a23c503789ffecc4215a5ec96fc250faacbad06
review_worktree: G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1
date: 2026-10-16
mode: 只读审查 + 独立 Git/构建日志/测试驱动方式复核；未修改被审分支或主仓任何文件
object_binding: VERIFIED
decision: approved_with_conditions
---

# ENV-BUNDLE-1 独立 Review（R1）

## 0. 复核结果（未采信自述）

| 项 | 方式 | 结果 |
|---|---|---|
| 分支范围 | `git diff --name-only c6fda8a0..HEAD` 过滤非 Task/Handoff/verification | **空** ✅ 只改了 Task、Handoff、`verification/ENV-BUNDLE-1/**` |
| **产品代码零改动** | 读 `ac5-product-code-diff.txt` + 独立过滤 `src apps requirements.txt Cargo.toml doc/contracts` | **空**、exit 0 ✅ |
| worktree | `git status --porcelain` | **clean** |
| 主仓 dirty | `git status --porcelain --untracked-files=no` | **19**（与初始逐项相同）✅ |
| AC2 构建 | 读 `ac2-build-sidecar.log` 尾部 | `Build complete!` / ICU fail-closed guard 满足 / manga 3 文件与 sfx ONNX **均 sha256 校验后打包** / `build_sidecar: OK` / **`exit_code: 0`**（395.8s）✅ |
| AC2 产物 | 读 `ac2-bundle-manifest.txt` | **5563 文件 / 1,287,287,472 B（1.199 GiB）**，5 个 exe 齐全 ✅ |
| AC3 前端 | 读 `ac3-frontend.log` | `npm ci` + `npm run build`，**`npm_build_exit_code: 0`**，`package_lock_unchanged: True` ✅ |
| AC1 依赖 | 读 `ac1-resolved-versions.txt` / `ac1-python-environment.txt` | Python 3.12.3，pip exit 0 ✅ |
| AC6 探测 | 读 `ac6-probe.md` | 磁盘 1.504 TB（G:）、pip 小包下载成功、工具链齐备 ✅ |
| **AC4 驱动方式** | 读 `ac4-six-test-results.md` + 测试代码 | **确认测试走源码路径**（见 §2） |

## 1. AC 逐项结论

| AC | 判定 | 依据 |
|---|---|---|
| AC1 venv 与依赖 | **接受** | venv 实测约 1.42 GB；版本解析与 Python 环境已归档 |
| AC2 重建 bundle | **接受** | 全量 `-Force` 构建 exit 0；**未跳过权重**；closure assertion 通过（core_service 携带 transformers/rt_detr/onnxruntime；sfx_detect_probe 携带 onnxruntime） |
| AC3 frontend dist | **接受** | 生产构建 exit 0；`package-lock` 哈希未变（未改依赖） |
| **AC4 打包产物驱动验收** | **PARTIAL（接受其 PARTIAL 判定）** | 见 §2 |
| AC5 不越界 | **接受** | 产品代码 diff 为空；cargo 产生的 27 个行尾副作用已 `git restore` 还原，`remaining_generated_tracked_count=0` |
| AC6 先探测 | **接受** | 探测先于大型下载，估时与实测均记录 |
| AC7 Review + 集成 | **Review 由本文件闭合；集成由 Coordinator 执行** | 且集成须在**最新 main** 上重跑 |

## 2. AC4 的独立复核（本 Review 核心）

Owner 主动把 AC4 判为 **PARTIAL**，理由（**我独立复核后确认成立**）：

1. `ac4-six-test-results.md` 明确记载：本次运行**只设置** `M2RC1_PYTHON`，
   **`M2RC1_SRC_ROOT` 与 `M2RC1_PACKAGED` 均未设置**；
2. 测试代码路径为 `spawn_with_resource_roots(python_exe, src_root, data_root, …)` —— 即**以 Python 源码模块方式**启动 Core，
   **并非**调用新建的 frozen bundle；
3. 因此 `cargo test` 的 **76 passed / 0 failed / 1 ignored（exit 0）** 证明的是
   "**Rust 侧与当前 Core 源码的集成**"，**不等于**"由打包产物驱动的验收"。

**但同一交付提供了真正的 bundle 证据**：`ac4-packaged-core-smoke.log` 显示**真实 frozen `core_service.exe`** 在
**隔离数据目录、精简 PATH、未使用 Python/source-root override** 的条件下完成
`core.ping`（回报 `{"version":{"major":2,"minor":3},"status":"ready"}`）、`ListBooks`、`core.shutdown` 往返，**`overall: PASS`**。

**结论**：
- **BL-11b 的实质（bundle 与源码协议不匹配）已被直接证据证明解决** ✅；
- 但 AC4 的严格口径（六项测试由 frozen bundle 驱动）**未满足**，且本 Task **明文禁止修改测试/产品源码**，
  因此**不能在 Task 内闭合** → 维持 **PARTIAL** 并转后续项。

## 3. 值得记录的诚实修正（Owner 主动纠正了 Coordinator 的归因）

Owner 对照基线日志指出：此前 6 项失败中**只有 5 项**是 `PROTOCOL_VERSION_UNSUPPORTED` / `CORE_UNAVAILABLE`（协议），
而 **`library_bridge::tests::same_channel_concurrent_round_trips_keep_response_ownership`** 实际是**未设置 `M2RC1_PYTHON`** 所致，
**并非协议错误**。

**该修正成立**，并纠正了 Coordinator 此前在 BL-11b 记录中"六项均为协议不匹配"的表述。本 Review 采纳并据以更新 BL-11b 的精确描述。

## 4. Findings

| id | 级别 | 内容 | 处置 |
|---|---|---|---|
| **F1** | **P2（未闭合项）** | **AC4 未满足"由 frozen bundle 驱动"**：六项 Rust 测试走源码路径；需**独立授权**的后续 Task 让它们支持 `M2RC1_PACKAGED` 驱动 | 转后续项（见 C2）；**不得**用当前 76 passed 声称 packaged E2E 已验证 |
| **F2** | **P2（归因修正）** | BL-11b 原描述"六项均为协议不匹配"**不准确**：实为 **5 项协议 + 1 项 `M2RC1_PYTHON` 缺失** | 由 Coordinator 在 BACKLOG/BL11 证据中修正措辞 |
| **F3** | **P2（并行工作）** | 审查期间**主仓 HEAD 由 `c6fda8a0` 前进到 `c6f975d3`**（提交 `docs(UI-DESIGN-1): release AD-001 four-page UI/UX design baseline`，作者 `peakwheat-pixel`，改动 `doc/{REBASELINE_PLAN,STATUS}.md` 与新增 `doc/tasks/UI-DESIGN-1.md`）。**该提交合法**（治理检查 PASS、dirty 仍 19），且**保留**了 `ENV-BUNDLE-1` 的 READY 节点 | 视为**合法并行进展**，不回退；集成时须以最新 main 为基并**保留 `UI-DESIGN-1`**；AC4 复验须在最新 main 上重跑 |
| **F4** | P3 | PyInstaller 6.22.3 提示未来 7.0 将阻止以管理员身份运行 | 记录：后续重建应使用非管理员终端 |
| **F5** | P3 | 完整 NSIS 安装器与 packaged HostControl GUI E2E 仍 `NOT_RUN` | 属后续端到端范围，不阻断 AC1–AC3/AC6 |
| F6 | P4 | `delivery_head` 申报 `14c52c15`（证据提交），实际 HEAD `5a23c503` | closeout 冻结实际值（BL-7 第 13 次） |

**无 P0/P1 finding。**

## 5. 条件

- **C1**：Coordinator 集成时冻结实际被审 head `5a23c503789ffecc4215a5ec96fc250faacbad06`，并在**最新 main（含 `UI-DESIGN-1`）**上合并与复验。
- **C2**：**AC4 的严格口径转后续项**：需另立经授权的 Task，使六项 Rust 集成测试支持 **`M2RC1_PACKAGED`** 驱动
  （即真正调用 frozen bundle）；在该 Task 完成前，**不得**声称 packaged 六项测试已验收。
- **C3**：**BL-11b 可标"实质解决（bundle 已与协议 2.3 一致，frozen smoke PASS）"**，同时保留 C2 的未闭合项；
  BACKLOG 中 BL-11b 的措辞须按 F2 修正（5 项协议 + 1 项环境变量）。
- **C4**：本 Task 以 **`closed_with_limitations`** 收口（AC1/2/3/5/6 完成；AC4 PARTIAL；AC7 由本 Review + 集成闭合）。
- 构建产物与 venv 的处置：均为 gitignored，按 `PRESERVE_REFERENCED` 保留以便后续重建。

## 6. 能力边界

- 本 Review 覆盖范围合规、构建日志真实性、测试驱动方式的独立判定、以及并行 HEAD 前进的归因；
  **未重跑** `cargo test` 或 PyInstaller 构建（原始日志已核验 exit 0）。
- 所有 Git / 日志 / 代码结论均由 Reviewer 在 live 环境实际执行。
- Reviewer 未修改被审分支、主仓或任何证据文件；未 push。
