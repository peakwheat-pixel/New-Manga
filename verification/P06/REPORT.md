# P06：GC 分发迁移安全补证验收报告

**Owner**: Antigravity  
**Task ID**: P06  
**Base Commit**: `b8f39d667ba5f23ba03a5bea4e61c5b930dbcd1a`  
**Worktree**: `G:/CODEX/New Manga.workspace/worktrees/P06-GC-DISTRIBUTION-MIGRATION`  
**Branch**: `codex/P06-gc-distribution-migration-evidence`  
**隔离运行根**: `G:/CODEX/New Manga.workspace/P06-GC-DISTRIBUTION-MIGRATION`  
**生成时间**: 2026-10-15  

---

## 1. 任务背景与目标

依据 `verification/M2-DERIVED-GC-2/g7-enablement-boundary.md` §2、`verification/M2-DERIVED-GC-2/g1-g7-matrix.md` 与 `doc/contracts/M2_DERIVED_PREVIEW_GC_DESIGN.md` §2.3，在不修改产品源码的前提下，为 GC G7 分发迁移补齐并归档真实进程执行证据，包含：
(a) 完成受控全退出迁移验收并归档可审计执行证据（旧进程存活时独占跳过 → 全部退出后新版本独占首次扫描成功）；  
(b) 对存量旧 catalog 确认 Fail-Closed 策略（拒绝服务/拒绝启动，严禁静默迁移与复用）；  
(c) 明确「验收未归档前，发布物不得以启用 sweep 的配置出货」的阻断条件，产出供 P20 引用的检查清单。

---

## 2. Acceptance Criteria 判别矩阵

| AC 项 | 目标 | 验证方法 / 环境 | 判别结论 | 证据文件 |
|---|---|---|---|---|
| **AC1** | 受控旧版本 runtime 构建与隔离根 | 从协议引入前 commit `ad75fadc` 构建旧 sidecar；建立隔离运行根 | **完成** (PASS) | `old-sidecar-build.log` / `old-sidecar-build.exit` / `old-runtime-probe-evidence.json` |
| **AC2(i)** | 旧/共享进程存活时独占被拒 | 真实子进程持有共享租约，新版 Core 尝试独占启动 | **完成** (PASS) | `ac2-quiet-window-evidence.json` (Phase 1) |
| **AC2(ii)** | 全部退出后独占首次扫描成功 | kill 全部旧/共享进程，新版 Core 独占启动执行首次 sweep | **完成** (PASS) | `ac2-quiet-window-evidence.json` (Phase 2) |
| **AC3** | 旧 catalog Fail-Closed 策略逐机确认 | 构造未绑定资源行库与缺失 lifecycle 旧 schema 库，实测启动 Core | **完成** (PASS) | `ac3-legacy-catalogs-evidence.json` |
| **AC4** | 出货阻断条件与发布前检查清单 | 逐项对照 GC-2 §2 (a)(b)(c) 形成供 P20 直接引用的准则 | **完成** (PASS) | `RELEASE_BLOCKING_CHECKLIST.md` |
| **AC5** | 不重做 GC2 / 零产品改动 | `git diff --name-only <base>..HEAD` 审查，不修改 `src/**`、`apps/**` 等 | **完成** (PASS) | `git status` 审查 |
| **AC6** | 真实执行非冒充 / 边界明确 | 明确区分「机制验证」与「真实装机迁移验收」，无伪造 | **完成** (PASS) | 本报告 §5 边界纪律声明 |

---

## 3. 旧版本 Runtime 构建与特性查验（AC1）

1. **源码版本选择**：
   - Commit: `ad75fadc2944983b4322f353176ba70cf0b0b7ae`（GC-2 首版实现落地前的设计归档点，全仓零 `preview_namespace` 实现）。
   - 检出路径：`G:/CODEX/New Manga.workspace/P06-GC-DISTRIBUTION-MIGRATION/old-runtime/worktree`（通过 `git -C "G:/CODEX/New Manga" worktree add --detach ...` 检出，主仓只读未写入）。
2. **构建命令**：
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File packaging/m2ac5/build_sidecar.ps1 `
       -PythonExe "G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" `
       -Force
   ```
3. **构建产物及 SHA-256 哈希值**：
   - 产物目录：`G:/CODEX/New Manga.workspace/P06-GC-DISTRIBUTION-MIGRATION/old-runtime/worktree/apps/desktop/src-tauri/target/core-sidecar/core-sidecar/`
   - `core_service.exe`: `ec8a03bd7bbd8b9184c70b685e9616ab755e675c8b4bfc35d5ac11deea80542a` (69,389,906 bytes)
   - `catalog_loader.exe`: `e88ce24b3d5ed710c1d84c5448932e3bb96e91334a2fb861822c702b7930ab16` (1,803,032 bytes)
   - `acceptance_bridge.exe`: `3419b17967cc51944d81714327efa7618dff7887c501c96c01e121abfbf60a9f` (69,381,926 bytes)
   - `host_bridge.exe`: `c8549c36fea1108f84fb9580c1b9b846c6c7edeca856c0f09ea6746c41ac7213` (1,805,637 bytes)
   - `sfx_detect_probe.exe`: `433b17e37a9ab97ddd62cb193fcc7cc452d7314d796ac46f8746a70384958495` (68,537,109 bytes)
4. **旧 runtime 行为特征实测**：
   - 运行旧 `core_service.exe` 启动并退出，观测 `data/derived/.preview-lifecycle.lock` 是否存在：`has_lock_file: false`。
   - 证实旧版本 runtime 完全不具备 preview namespace 租约能力，不创建、不感知锁文件。

---

## 4. 全退出迁移验收实测（AC2）与旧 Catalog 策略确认（AC3）

### 4.1 全退出迁移验收（AC2）
在隔离目录 `ac2-run` 下真实进程执行：
- **Phase 1 (旧/共享进程存活)**：
  - 启动真实共享租约持有者进程（PID `4568`）。
  - 启动新版 Core 进程（PID `42952`）。
  - **实测结果**：Core 执行 `try_acquire_exclusive_lease` 返回 `None`，向 stderr 输出：
    `[core.derived_gc] skipped: namespace busy (a managed peer holds a shared lease)`
  - 孤立预览文件 `orphan_probe.png` 零被删除，dead row 零被移除。
  - 独占扫描被**非阻塞安全拒绝**，服务以共享模式正常降级。
- **Phase 2 (进程全部终止后首次独占扫描成功)**：
  - 调用 `kill` 终止 PID `4568`，内核文件锁由 Windows OS 自动回收。
  - 再次启动新版 Core 进程（PID `45944`）。
  - **实测结果**：Core 成功取得独占租约，未输出 `skipped: namespace busy`，向 stderr 输出：
    `[core.derived_gc] orphan_files_removed=1 dead_rows_removed=1`
  - 孤立预览文件 `orphan_probe.png` 真实删除，dead row 真实清理。
  - 独占扫描首次成功，随后正常降级为共享租约进入服务。

### 4.2 旧 Catalog Fail-Closed 策略（AC3）
在隔离目录下分别构造两类存量旧 catalog 并启动新版 Core：
1. **Case 1A（有资源行但未绑定，且无锁文件）**：
   - Core 启动试图取共享租约时因缺少锁文件抛出 `FileNotFoundError`，Core 进程非零退出（exit code 1）。
   - `catalog.sqlite` 文件哈希前后完全一致（`1e30df7d... == 1e30df7d...`），证明**零静默修改**。
   - 显式调用 `initialize_namespace`：抛出 `TypedResourceChannelError: catalog carries resource rows but predates the lifecycle schema; unknown history is never claimed` 明确拒绝认领。
2. **Case 1B（有资源行但未绑定，存在外来锁文件）**：
   - Core 启动在校验租约绑定时抛出 `TypedResourceChannelError: preview namespace unavailable`，进程非零退出（exit code 1）。
   - `catalog.sqlite` 文件哈希前后完全一致（`32eb3b7e... == 32eb3b7e...`），证明**零静默修改**。
3. **Case 2（旧 schema，缺失 preview_lifecycle 表）**：
   - Core 启动失败非零退出（exit code 1）。
   - `catalog.sqlite` 文件哈希前后完全一致（`8f7b8044... == 8f7b8044...`），证明**零补建表、零静默修改**。
   - 显式调用 `initialize_namespace`：抛出 `TypedResourceChannelError` 明确拒绝认领。

---

## 5. 「机制验证 vs 真实装机迁移验收」边界声明

> **重要声明（Boundary Discipline Statement）**：  
> 本仓库为开发/工程代码仓库，**在物理上不存在历史已装机的生产旧版本用户终端**。  
> 因此，本 Task 交付的是在隔离环境受控构造下的**「内核租约互斥与 Fail-Closed 机制验证」**，**不等于**「真实多终端线上装机灰度迁移验收」。  
> 真实多版本共存的分发升级，必须依赖发布交付系统（P20 范围：安装包 NSIS 脚本）严格执行**安装前强制 kill 全部存量进程**的外部管控。机制已证明：只要外部保证旧进程全退出，新版本的独占首次扫描与数据保护即可数学上成立；旧 catalog 绝不会被新版本静默篡改或误用。两者边界清晰，不得混淆。

---

## 6. 证据文件与 SHA-256 清单

| 文件相对路径 | 说明 | SHA-256 (工作区实测) |
|---|---|---|
| `verification/P06/runner_p06.py` | P06 验证执行运行器 | `42c9546a0dc61f830d88517cd87d55c8a9ecc0f9b13a7fe7f644eb0afcdea4f8` |
| `verification/P06/runner_p06.log` | 运行器完整控制台日志 | `012c93ff73b7c8dd9a958b127c1fc90c5de713901c51e989f679cb6d68396a64` |
| `verification/P06/runner_p06.exit` | 运行器退出码 (0) | `13bf7b3039c63bf5a50491fa3cfd8eb4e699d1ba1436315aef9cbe5711530354` |
| `verification/P06/old-sidecar-build.log` | 旧 sidecar (ad75fadc) 构建原始日志 | `30b25b843c1d0e3f976fe13bc059e05cbdb7d60d0fcfa1945b86524947896b92` |
| `verification/P06/old-sidecar-build.exit` | 旧 sidecar 构建退出码 (0) | `13bf7b3039c63bf5a50491fa3cfd8eb4e699d1ba1436315aef9cbe5711530354` |
| `verification/P06/ac2-quiet-window-evidence.json` | AC2 全退出实测双进程证据 | `81872f2962ddaac0d669560a243976210de83cf4444e91a8e965082fd100e3a0` |
| `verification/P06/ac3-legacy-catalogs-evidence.json` | AC3 旧 catalog fail-closed 证据 | `1f89f9161ebf60676bd80912a522f7073a03ab08abe5d18d8969f5515bd120e4` |
| `verification/P06/old-runtime-probe-evidence.json` | 旧 sidecar 真实探针证据 | `0fbf8a03ec437e190b123ab71dc7652dd5107843aa38e3d24314c0006516032a` |
| `verification/P06/RELEASE_BLOCKING_CHECKLIST.md` | 出货阻断检查清单（P20） | `4a951517b5d64ffccfb5351e19240974c7e81450f2f70bff9b9f47b27b600278` |
| `verification/P06/resource-manifest.json` | 资源清单记录 | `a5f91b69a64c35c9ed54f3479692c964dfcedf48fd04311ed293291f5af57a12` |
