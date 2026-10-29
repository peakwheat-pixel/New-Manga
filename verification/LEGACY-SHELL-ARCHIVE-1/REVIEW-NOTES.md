# A 复核记录（region-workbench-owner 视角建议 / DSH Lead 自查）

- 复核对象：LEGACY-SHELL-ARCHIVE-1（main `4023da989`，集成提交 `7d4c7764c`）
- 复核时间：2026-10-29
- 结论：**构建解耦与归档范围正确且有据**；两项未闭环（C# 回归、公开 CI 结果），不改变 `closed_with_limitations` 状态。

## 1. 构建路径语义一致性（PASS）

| 检查点 | 事实 |
|---|---|
| `build_sidecar.ps1` 输出根 | `$targetRoot = $repoRoot/apps/desktop-avalonia/build/sidecar`；`$distPath = $targetRoot/core-sidecar` → PyInstaller onedir 输出 `build/sidecar/core-sidecar/core-sidecar/` |
| `build_sidecar.ps1` 增量短路 | `$existingBundle = build/sidecar/core-sidecar/core-sidecar`（与 PyInstaller 输出结构一致） |
| `package.ps1` 默认读取 | `apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar`（与上一致） |
| `README.md` 构建命令 | `-SidecarDir apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar`（一致） |
| `.github/workflows/build-release.yml` | 同上路径（main 版；公开版同路径） |
| `.gitignore` | `/apps/desktop-avalonia/build/` 已忽略构建产物 |
| 旧路径残留 | `apps/desktop/src-tauri/target` 在 5 个活跃构建文件中 0 命中 |

## 2. 归档范围（PASS，与 Limitations 一致）

- 归档 18 个文件：`tests-ui-shell/`（12）、`tests-packaging/`（2）、`tests-workbench/`（1）、`packaging/new_manga.spec`（1）、`tools-dev/dev-preview.ps1`（1）、`README.md`（1）。
- 旧路径已从 Git 移除：`tests/ui_shell`=0、`tests/packaging/test_frozen_runtime_contract.py`=0、`packaging/new_manga.spec`=0。
- `apps/desktop` 保留：`doc/tasks/**` 中 `apps/desktop/(src-tauri|frontend)` 引用 428 行、**精确 evidence pin 42 条**（与卡内声明一致）。
- `src/ui` 保留：`src/bootstrap/app.py` 模块级 `from ui.viewmodels...`；移动后 pytest 实测 8 个 collection error（已回退）。

## 3. 回归（部分）

- pytest 全量：2600 passed / 10 skipped / 0 failed（201s）——`verification/LEGACY-SHELL-ARCHIVE-1/pytest-full.log`。
- C# 回归：**未完成**——worktree 中 `test.ps1` 依赖 HOST-CORECLIENT sidecar 副本与 probe（在 worktree 环境阻塞/超时）；产品代码零改动，建议在主仓库环境复跑确认 258/258。
- 公开 CI：run `40830315601`（a12c8fdfd）= **success，17/17 步全绿**（pytest 子集、新路径 sidecar 构建、base package、NSIS installer 全部通过）——构建解耦在公开 CI 上验证通过；证据 `ci-run-success.json`。

## 4. 公开分支对照（PASS）

- `public-release` = `a12c8fdfd`：同样归档 17 文件（`tests/ui_shell`=0），sidecar 路径同 main，**保留 P0-1 公开 pytest 子集配置**（`--ignore=tests/m2_test_assets|packaging|ui_shell|tools|test_plugin_sandbox.py` + deselect）。
- 修复过程记录：`40828265013`（src/ui 移动失败 → 回退）、`40828776753`（main workflow 覆盖丢失公开子集 → 恢复公开版 + 仅打路径补丁）。

## 5. 遗留（不阻塞 closed_with_limitations）

1. C# 回归在主仓库环境复跑（`apps/desktop-avalonia/scripts/test.ps1`，默认 sidecar 副本）。
2. 公开 CI `40830315601` 结果确认 + 证据 pin。
3. 独立审查（本记录为 Lead 自查，非独立 Review）。
