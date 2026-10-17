# P19 发现 R2：修复在源码而打包 sidecar 未重建（产品仍崩溃）

- 时间：2026-10-17
- 发现者：dsh（P19 D+ 验收第 2 步：修复合并后启动打包应用）
- 结论：**P19-BOOT-1 的修复只存在于 `src/**`；Tauri 启动的是 `target/debug/resources/core-sidecar/core_service.exe`（PyInstaller 冻结包，构建于 10-16 17:21，早于修复）→ 应用仍以完全相同的方式崩溃（`FileNotFoundError: …\.preview-lifecycle.lock` → host panic → exit 101）。**
- 证据：`verification/P19/app-stale-bundle-stderr.log`（本次启动原始 stderr）。
- 复核：`core_bridge.rs` 明确 "missing/unreadable sidecar exe … **deliberately NO** [source-run override]" → **不能**用源码 Core 替代，必须**重建 bundle**。
- 处置：以 `packaging/m2ac5/build_sidecar.ps1 -Force`（构建 venv `task-envs/m2ac5-build` 已就绪；ENV-BUNDLE-1 记录约 396s）重建，产物就位后重跑 D+ 验收。
- **教训（打包/发布类）**：修 Python 侧代码后，**必须重建 frozen sidecar 才能进入产品**；"源码修好" ≠ "产品修好"。**P20 发布前的构建清单必须包含该步骤**，且 P19-BOOT-1 的 AC6 真实启动证据应针对**重建后的 bundle** 复核。