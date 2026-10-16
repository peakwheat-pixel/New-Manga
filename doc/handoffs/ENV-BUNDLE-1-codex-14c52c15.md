---
task_id: ENV-BUNDLE-1
author: Codex
recipient: Coordinator (DSH, epoch 5)
base_commit: c6fda8a09c1a8248ec6617369f9fdf9e1cef79ec
delivery_head: 14c52c152b9ae058aba4ee29d55d6ed6f7ef6e0f
status: in_review
---

# Handoff：ENV-BUNDLE-1

## 交付结果

- AC1：在新建的 `G:/CODEX/New Manga.task-envs/m2ac5-build` 使用 Python 3.12.3 安装 `packaging/m2ac5/requirements-build.txt`，pip 成功，退出码 0，278.794 秒。默认 Windows 编码首次读取 UTF-8 requirements 失败，原始 exit 2 日志保留；指定 `-X utf8` 后成功，解析版本记录在 verification。
- AC2：从 worktree 仓库根执行 `build_sidecar.ps1 -Force`，exit 0，395.8 秒；未使用 `-SkipWeights`。生成 5,563 个文件、1,287,287,472 bytes 的 frozen bundle，manifest 与权重校验通过。
- AC3：frontend `npm run build` exit 0，2.789 秒，50 modules；dist 有 2 个文件，共 201,081 bytes。`package-lock.json` 构建前后 SHA-256 相同。首次 `npm ci` 包装日志因 Push-Location 后的相对路径失效；日志如实记录，后续 `npm ls --depth=0` 与生产构建成功。
- AC4：按要求的命令运行 cargo suite，76 passed / 0 failed / 1 ignored，exit 0。六个目标名字均 PASS，逐项结果见 `verification/ENV-BUNDLE-1/ac4-six-test-results.md`。源码检查确认这六个测试直接启动 Python source module / test helper，并没有由 frozen bundle 驱动。真实冻结的 `core_service.exe` 独立协议 2.3 smoke（`core.ping`、`ListBooks`、`core.shutdown`）exit 0。故 AC4 的“六项用例由打包产物驱动”核心条件仍未满足，记录为 PARTIAL；不得将 cargo suite 结果描述为 packaged E2E 通过。
- AC5：产品代码 diff 为空；Cargo 生成的 27 个 tracked Tauri 文件仅行尾变化，已逐项恢复。产品代码证明、受影响路径与处理记录在 verification。
- AC6：可行性探测通过：G 盘可用 1.504 TB、C 临时盘约 398 GB；`pip download --no-deps packaging==25.0` 成功，66,469 bytes / 1.638 秒。Python 3.12.3、Node 24.15.0、npm 12.0.1、Cargo 1.98.1 可用。代理变量只记录是否设置，未记录值。
- AC7：本 handoff 与 Task/verification commits 已形成；Coordinator integration 尚未执行。Task 保持 `in_review`。

所有原始记录与 SHA-256 索引见 [ENV-BUNDLE-1 Task](../tasks/ENV-BUNDLE-1.md) 和 `verification/ENV-BUNDLE-1/`。主证据固定于提交 `bda0c4a1476d2fc257012aa04d5e3352408228fe`，探测记录行尾规范化提交为 `ac9e303436c572976c35ea66758b04b687015df8`，主仓状态观察提交为 `ae23664a0b6448be084b94d4d08d7ce63a2f438f`，main 前进后的状态复核提交为 `14c52c152b9ae058aba4ee29d55d6ed6f7ef6e0f`。Task/Handoff 文档提交不改变上述证据 hash。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC6 | 磁盘、Python/Node/Rust 工具链检查；`pip download --no-deps packaging==25.0` | worktree；Windows PowerShell | PASS | `verification/ENV-BUNDLE-1/ac6-probe.md`; `ac6-pip-connectivity.log` |
| AC1 | 创建 build venv；`python.exe -X utf8 -m pip install -r packaging/m2ac5/requirements-build.txt` | Python 3.12.3；build venv | PASS；exit 0，278.794 s | `ac1-venv-create.log`; `ac1-pip-install.log`; `ac1-pip-install-utf8.log`; `ac1-resolved-versions.txt` |
| AC2 | `powershell -NoProfile -ExecutionPolicy Bypass -File packaging/m2ac5/build_sidecar.ps1 -Force` | worktree source head c6；`-SkipWeights` 未使用 | PASS；exit 0，395.8 s | `ac2-build-sidecar.log`; `ac2-bundle-manifest.txt` |
| AC3 | `npm ci`; `npm ls --depth=0`; `npm run build` | Node 24.15.0 / npm 12.0.1；worktree source head c6 | PASS；build exit 0，2.789 s；首次 npm ci wrapper 日志路径问题已披露 | `ac3-frontend.log`; `ac3-frontend-dist-manifest.txt` |
| AC4 cargo suite | `cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml` | Windows PowerShell；M2RC1_PYTHON 指向已批准 Python 3.12.3；`M2RC1_SRC_ROOT` 与 `M2RC1_PACKAGED` 未设置；source head c6 | 命令 PASS；76 passed / 0 failed / 1 ignored，exit 0。六项通过的是 Python source-backed 测试 | `ac4-cargo-test.log`; `ac4-six-test-results.md` |
| AC4 frozen sidecar smoke | 直接向重建的 `core_service.exe` 发送协议 2.3 ping、ListBooks、shutdown | frozen bundle；无 Python、精简 PATH、隔离运行目录 | PASS；exit 0，1.027 s。未覆盖六个 cargo 测试路径 | `ac4-packaged-core-smoke.log` |
| AC5 | 对比允许范围外的源、契约、依赖与生成文件；检查 Git diff | worktree；base c6 | PASS；无产品源码改动；27 个行尾副作用已恢复 | `ac5-product-code-diff.txt`; `ac5-generated-side-effects-and-restoration.txt` |
| 主仓保护 | 比较 before/after HEAD 与 porcelain 状态 | `G:/CODEX/New Manga` | 构建/测试时 HEAD=c6，before/after 状态为相同 19 项。最终复核时 HEAD 已由后续 main commit 前进到 `c6f975d...`；当前 porcelain 回到原有 19 项，逐项相同。本 Task 全程未写主仓 | `main-head-before.txt`; `main-status-comparison.md`; `final-main-status-observation.txt` |

AC4 尚未运行的部分：完整 NSIS 安装器和 packaged HostControl GUI E2E；六个现有 Rust 用例通过 frozen EXE 的运行路径也未实现/未验证。测试代码把这些用例固定为 Python source module / helper，当前 Task 又禁止修改产品/测试源码；需要新的明确授权范围才能改变测试驱动方式。

主仓状态说明：构建和 cargo 验收时 main HEAD 为 `c6fda8a09c1a8248ec6617369f9fdf9e1cef79ec`，before/after porcelain 均是相同 19 项。16:48 曾短暂观察到 22 项（多出的 staged `doc/REBASELINE_PLAN.md`、`doc/STATUS.md` 和新增 `doc/tasks/UI-DESIGN-1.md`），16:52 状态再次为相同的 19 项。主仓随后/同期出现新 HEAD `c6f975d38842487c16491eea67a01cf134c337f8`，提交时间 16:49:18、subject `docs(UI-DESIGN-1): release AD-001 four-page UI/UX design baseline`。该更新发生在 cargo 测试后；当前分支没有合并或改写它，Coordinator 需在最新 main 集成后复验。整个 Task 没有写入主仓。

AC4 时点：cargo suite 的测试坐标和当时 main 同为 c6。当前 main 已前进到 c6f975d，因此即便 source-backed cargo suite 结果通过，仍需在 Coordinator 集成后的固定 head 重跑；package-backed 六项路径与 packaged HostControl E2E 仍未验证。

## 接收方式

- 仓库：`G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1`
- 分支：`codex/ENV-BUNDLE-1-sidecar-rebuild`
- 基线/源码 head：`c6fda8a09c1a8248ec6617369f9fdf9e1cef79ec`
- Build source head：`c6fda8a09c1a8248ec6617369f9fdf9e1cef79ec`
- Evidence delivery head：`14c52c152b9ae058aba4ee29d55d6ed6f7ef6e0f`
- 交付构建产物位于本 worktree 的 `apps/desktop/src-tauri/target/**`、`apps/desktop/frontend/{dist,node_modules}/`；build venv 位于用户指定的 `G:/CODEX/New Manga.task-envs/m2ac5-build`。
- 复验 cargo suite：需设置 `M2RC1_PYTHON` 为 Python 3.12.3 后运行 `cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml`。此命令仍使用 source-backed 测试。Frozen EXE 位于 `apps/desktop/src-tauri/target/core-sidecar/core-sidecar/core_service.exe`。
- 本次提交只包含 Task/Handoff/verification；未 push、未 merge。主仓保持只读。

## 下一任务建议（必填）

- Task ID / 标题：建议由 Coordinator 建立 ENV-BUNDLE-1 独立 Review / AC4 闭环后续 Task；当前不创建占位 Task。
- 推荐 Agent / Reviewer：DeepSeek Harness 独立 Review；Coordinator（DSH epoch 5）审核集成与范围。
- 推荐原因与前置依赖：验证证据、提交范围与未满足的 packaged-backend Gate；然后决定是否另行授权 Rust 测试驱动支持 frozen bundle 和/或完整 packaged HostControl E2E。
- Recovery point：worktree `G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1`，branch `codex/ENV-BUNDLE-1-sidecar-rebuild`，源码 base `c6fda8a09c1a8248ec6617369f9fdf9e1cef79ec`，evidence head `14c52c152b9ae058aba4ee29d55d6ed6f7ef6e0f`；main 当前 head `c6f975d38842487c16491eea67a01cf134c337f8`，cargo 证据生成于 main 前进前。Review Task 未创建，其他新 worktree 待 Codex 创建。
- 允许修改路径：Review 只写经 Coordinator 新 Task 指定的 Review/verification 路径；若要改测试驱动，先由 Codex 明确产品源和测试路径授权。
- 禁止范围与新增授权条件：当前不得修改产品源码、契约、依赖或 Rust 测试；不得把 source-backed PASS 记为 package-backed PASS；不得操作主仓 dirty。
- 交付物：独立 Review、AC4 是否可由本 Task 关闭的裁决、若需代码变更则另立 Task 与范围。
- 验证命令、环境与完成 Gate：对固定 evidence head `14c52c152b9ae058aba4ee29d55d6ed6f7ef6e0f` 复核证据哈希/提交包含关系、产品 diff 与主仓状态；AC4 完成 Gate 必须在最新 main 集成后的固定 head 由 frozen sidecar 驱动相应集成路径，并单独记录 packaged HostControl E2E 是否执行。
- 可直接转发给 Agent 的指令：请在固定 evidence head `14c52c152b9ae058aba4ee29d55d6ed6f7ef6e0f` 独立审阅 ENV-BUNDLE-1 的 AC1–AC7、Canonical Evidence hash/commit 包含关系、产品代码 diff、主仓状态变化及 AC4 部分完成判定。cargo 验收时 main 为 c6，当前 main 已前进到 `c6f975d38842487c16491eea67a01cf134c337f8`；请将其作为集成后重跑基线。请逐项反馈缺陷和是否可批准。明确指出 cargo 的六项 Rust 测试由 Python source module/helper 驱动；不要将它们视作 frozen bundle 验收。若认为需代码修改，请先给出独立 Task 范围建议，不要直接改产品或测试源码。

## 风险与遗留

- AC4 核心验收仍部分未完成：cargo 中六个目标用例通过，但由源码 Python 模块驱动；frozen bundle 仅完成独立协议 2.3 smoke。不得把本 Task 标为 `done`，直到 Coordinator 处理此 Gate。
- 完整 NSIS 安装器 / packaged HostControl GUI E2E 未运行，结论为 `NOT_RUN`。
- PyInstaller 6.22.3 构建成功，并提示当前以管理员身份运行并非必要，未来 PyInstaller 7.0 将阻止管理员运行。本次固定工具链可用；重建时应在非管理员终端运行。
- 没有 SkipWeights、mock、跳过测试或伪造产物。大型产物保持 gitignored 并保留，未提交二进制。
