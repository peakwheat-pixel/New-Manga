# M2-SETTINGS-IPC-CHANNEL 验证证据

- 分支：`agent/zcode/M2-SETTINGS-IPC-CHANNEL`（worktree `G:/CODEX/New Manga.worktrees/M2-SETTINGS-IPC-CHANNEL-zcode`）
- 基线：`1c3ac590`（任务书 base `f99a6c55` + 批次 close/release commits）+ merge `4e432fe7`（引入 depends_on 的 SFX-UI 交付 `8c798aed`+`efad4b71`，零冲突）
- 日期：2026-10-02

## 基线（改动前，`1c3ac590` + merge）

| 套件 | 命令（worktree 根，除注明外） | 结果 |
|---|---|---|
| pytest 三套件 | `PYTHONPATH=src "G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" -m pytest tests/providers tests/core tests/m2_acceptance -q` | **575 passed, 1 skipped, 0 failed** |
| cargo | `cd apps/desktop/src-tauri && cargo test` | **44 passed, 1 ignored**（perf） |
| vitest | `cd apps/desktop/frontend && npx vitest run` | **7 files, 48 passed** |
| tsc | `cd apps/desktop/frontend && npx tsc --noEmit` | EXIT=0 |

## 交付后（本 Task 全部改动落地）

| 套件 | 命令 | 结果 | 与基线差 |
|---|---|---|---|
| pytest 三套件 | 同上 | **602 passed, 1 skipped, 0 failed** | +27（`tests/core/test_core_service_settings.py`；既有 2+2 处 minor 断言 1→2 后果同步） |
| cargo | 同上 | **46 passed, 1 ignored** | +2（`settings_mock_channel_round_trip_and_typed_rejection`、`real_core_sidecar_settings_round_trip_and_typed_rejection`） |
| vitest | 同上 | **49 passed**（8 files） | +1（commandSurface settings allow/deny CASE）；既有 48 中 47 条零修改 |
| tsc | 同上 | EXIT=0 | — |

## 关键端到端证据

- `real_core_sidecar_settings_round_trip_and_typed_rejection`（cargo）：真实 `python -m bootstrap.core_service` 子进程上验证——全量投影读取、未设 `sfx` 节读取为 JSON `null`、合法 `sfx.policy=translate` 写入并读回、非法值 `INVALID_REQUEST`(validation) 且旧值保留（写入端前置校验 R4 核心断言）。
- `test_protocol_minor_bumped_to_two_with_settings_surface`（pytest）：envelope minor 1→2 pin。
- 前端 48 既有 vitest 中 47 条零修改通过——SFX-UI pin 的命令名/载荷形状与落地 wire shape 逐字一致（零漂移）。

## 环境说明

- 解释器：`G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312`（含 PySide6；全局 python 3.14 缺 PySide6 会收集失败 4 文件——环境性，非本 Task 引入）。全局 python 3.14 可跑 `tests/core/test_core_service*.py`（用于快速迭代）。
- cargo build.rs 的 fail-closed probe 需要 `apps/desktop/src-tauri/target/core-sidecar/core-sidecar/` 存在（gitignored 构建产物，fresh checkout 需先跑 `packaging/m2ac5/build_sidecar.ps1`——M2-AC5 登记的构建顺序约束）；本 worktree 从主仓库既有产物复制（只读源）。
- cargo 还需要 `apps/desktop/frontend/dist/` 存在（`generate_context!` 的 frontendDist 校验）；由 `npm run build` 生成。
