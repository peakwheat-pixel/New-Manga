# BL-11：Tauri/Rust 构建前置 —— 勘察结论与拆分（2026-10-16）

作者：dsh（Active Coordinator, epoch 5）。本文件为**运行时治理证据**，记录 BL-11 的精确根因与处置。

## 1. 初始症状

HOST-ISSUER-1 在其 worktree 中执行 `cargo build` 与 `cargo test`，**均 exit 101**：

```
thread 'main' panicked at build.rs:23:9:
missing sidecar bundle: .../apps/desktop/src-tauri/target/core-sidecar/core-sidecar does not exist
(gitignored build artifact, absent on a fresh checkout).
Fix: run `powershell -NoProfile -ExecutionPolicy Bypass -File packaging/m2ac5/build_sidecar.ps1`
```

## 2. 勘察（只读）

| 前置 | 主仓 | 新 worktree | 说明 |
|---|---|---|---|
| `apps/desktop/src-tauri/target/core-sidecar/core-sidecar` | **存在**（1,236 MB / 5,610 文件） | 缺失 | gitignored，不随 worktree 复制 |
| `apps/desktop/frontend/dist` | **存在**（`index.html` + `assets`） | 缺失 | gitignored；`tauri.conf.json` 的 `frontendDist` |
| `apps/desktop/frontend/node_modules` | 存在（80 MB） | 缺失 | **不需要**：`beforeBuildCommand` 为空，Tauri 不会跑前端构建 |
| `packaging/m2ac5/build_sidecar.ps1` | 存在 | 存在（git 跟踪） | 既有官方构建入口，含 incremental short-circuit |
| `task-envs/m2ac5-build`（构建 venv） | **不存在** | 不存在 | 完整重建 bundle 所需 |

- `build.rs` 对 bundle 的断言仅为 **`is_dir()`**（不校验内容），随后 `tauri_build::try_build` 需要 `bundle.resources` 路径存在。
- `packaging/m2ac5/README.md` **§2.0 明确规定**：fresh checkout / fresh worktree 必须先跑 `build_sidecar.ps1`，
  并明确 **`frontend/dist` 同为 gitignored 构建产物**，需先完成 frontend build。

## 3. 已执行的处置（编译前置）

采用 **junction（零拷贝、零磁盘）** 补齐 worktree 的 gitignored 前置：

- `worktrees/HOST-ISSUER-1/apps/desktop/src-tauri/target/core-sidecar` → 主仓同名目录
- `worktrees/HOST-ISSUER-1/apps/desktop/frontend/dist` → 主仓同名目录

验证：`build.rs` 探针 `is_dir=True`；5 个 bundle exe 均可见；`frontendDist/index.html` 存在；
**worktree `git status` 仍干净**（junction 位于 gitignored 目录）；**主仓仍 19 项 dirty 未变**。

结果：**`cargo build --locked` 通过（exit 0，16.01s，仅未使用函数的 warning）**。

## 4. 勘察中发现的更深一层问题（重要）

`cargo test --locked` 在 worktree 中：**58 passed / 6 failed / 1 ignored，exit 101**。
失败的 6 项**全部是需要真实 sidecar 的集成测试**，报 `PROTOCOL_VERSION_UNSUPPORTED` 或 `CORE_UNAVAILABLE`。

**对照实验**：在**主仓**运行同一个 `cargo test --locked` —— **同样 58 passed / 6 failed，失败列表完全相同**。

**结论**：
1. 该 6 项失败是**既有环境债务**，**不是**本次 junction 或 HOST-ISSUER-1 引入的偏差；
2. 根因是**主仓的 bundle 构建早于 Core 协议升到 2.3**（P13/P16/P12-C1/P09-FU2 的协议演进之后未重建 bundle），
   故 bundle 与当前源码**协议不匹配**；
3. junction 方案**忠实复现**了主仓的既有状态，未新增偏差。

## 5. BL-11 拆分

- **BL-11a（编译前置）—— 已解决**：worktree 可通过 junction（或按 README 重建）获得 bundle 与 `frontend/dist`，
  使 `cargo build` 通过。**已实测 exit 0。**
- **BL-11b（bundle 与源码匹配 / 真实 sidecar 集成）—— 未解决**：
  需按 `packaging/m2ac5/README.md` §1–§2 创建构建 venv（`task-envs/m2ac5-build`，
  `pip install -r packaging/m2ac5/requirements-build.txt`，含 torch/doctr/transformers/PySide6 的运行时闭包）
  并运行 `build_sidecar.ps1 -Force` 重建 bundle，同时完成 frontend build。
  **影响**：所有依赖真实 sidecar 的 Rust 集成测试（当前 6 项）在主仓与任何 worktree 中**均会失败**，直到重建。
  **阻塞面**：不影响 Rust 单元测试与 issuer 逻辑验证；影响"真实 sidecar 端到端"类验证。

## 6. 证据

- `G:/CODEX/New Manga.workspace/tmp/guarded/bl11-cargo-build.log`（worktree：`cargo build` exit 0）
- `G:/CODEX/New Manga.workspace/tmp/guarded/bl11-cargo-test.log`（worktree：58 passed / 6 failed）
- `G:/CODEX/New Manga.workspace/tmp/guarded/bl11-main-cargo-test.log`（**主仓对照：同样 58 passed / 6 failed**）

## 7. 处置建议

1. **HOST-ISSUER-1 可恢复**：其 AC8 应表述为"`cargo build` 通过 + **新增 Rust 单元测试**通过"，
   并明确既有的 6 项真实 sidecar 集成测试失败属 **BL-11b 既有债务**（主仓同现），不归因于本次实现。
2. **BL-11b 作为独立债务**：在需要真实 sidecar 端到端验证（P12/P19 恢复前）时处理，
   成本为构建 venv（含 ML 运行时闭包下载）+ PyInstaller 重建 + frontend build。
3. **方法论**：fresh worktree 的构建前置应**先读 `packaging/m2ac5/README.md` §2.0**，
   而不是自行发明 junction/复制方案；junction 仅可作为"仅需编译"场景的临时手段，且**必须声明其 bundle 与源码的版本关系**。
