---
task_id: P06
author: Antigravity
recipient: Codex
base_commit: b8f39d667ba5f23ba03a5bea4e61c5b930dbcd1a
delivery_head: 2f2da8224fac4509129922069559738b639b47d8
status: delivered
---

# Handoff：P06 GC 分发迁移安全补证

## 交付结果

依据 `verification/M2-DERIVED-GC-2/g7-enablement-boundary.md` §2、`verification/M2-DERIVED-GC-2/g1-g7-matrix.md` 与 `doc/contracts/M2_DERIVED_PREVIEW_GC_DESIGN.md` §2.3，在**不修改任何产品源码与测试**（`src/**`、`apps/**`、`packaging/**`、`tests/**` 零修改）的前提下，完成 GC G7 分发迁移安全补证：

- **AC1**：在隔离运行根 `G:/CODEX/New Manga.workspace/P06-GC-DISTRIBUTION-MIGRATION/old-runtime/worktree` 从引入租约协议前的历史 commit `ad75fadc2944983b4322f353176ba70cf0b0b7ae` 成功复现并构建出真实旧版本 sidecar（含 `core_service.exe`、`catalog_loader.exe` 等全部 5 个产物），记录完整构建命令与 SHA-256 哈希值；实测探针证实旧版本完全无租约协议感知（不生成、不检验 `.preview-lifecycle.lock`）。
- **AC2**：真实进程实测受控全退出迁移机制：
  - **(i)** 存在持有共享租约的旧/同伴进程（PID `4568`）存活时，新版 Core 尝试独占启动被**非阻塞安全拒绝**，输出 `[core.derived_gc] skipped: namespace busy`，孤立文件与 dead row 零被误删，Core 安全降级为共享租约正常服务；
  - **(ii)** 将旧/同伴进程全部 `kill` 后，内核锁由 Windows OS 自动回收，新版 Core 再次启动成功取得独占租约并完成**首次静默扫描**（输出 `orphan_files_removed=1 dead_rows_removed=1`），孤立文件与 dead row 真实清理。
- **AC3**：在隔离根下构造两类存量旧 catalog 并实测启动新版 Core：
  - **Case 1 (有资源行但未绑定)**：Core 启动 fail-closed 退出（exit code 1），数据库文件 SHA-256 零改变（前后一致）；显式调用 `initialize_namespace` 明确拒绝认领历史行；
  - **Case 2 (旧 schema 缺失 lifecycle 表)**：Core 启动 fail-closed 退出（exit code 1），数据库文件 SHA-256 零改变（零静默建表/迁移）；显式调用 `initialize_namespace` 明确拒绝认领。
- **AC4**：产出直接供 P20（Windows 发布 Gate）引用的发布前阻断检查清单 `verification/P06/RELEASE_BLOCKING_CHECKLIST.md`，明确规定分发迁移验收证据未归档前发布物不得以启用 sweep 配置出货的处置规则。
- **AC5**：严格零产品代码修改，不重做 GC2。
- **AC6**：本 Task 明确签署「机制验证 vs 真实装机迁移验收」边界声明，无虚假冒充，真实执行并归档完整证据。

---

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 旧 sidecar 构建 | `powershell packaging/m2ac5/build_sidecar.ps1 -PythonExe ... -Force` | commit `ad75fadc`，隔离工作树 | **PASS** | `verification/P06/old-sidecar-build.log` (SHA256: `30b25b84...`), `old-runtime-probe-evidence.json` |
| AC2(i) 共享租约互斥 | `runner_p06.py`：启动共享 holder 子进程，再启动新版 Core | Windows pwsh, Python 3.12.3 | **PASS** | `verification/P06/ac2-quiet-window-evidence.json` (Phase 1) |
| AC2(ii) kill后首次扫描 | `runner_p06.py`：kill holder 子进程，新版 Core 独占启动 | Windows pwsh, Python 3.12.3 | **PASS** | `verification/P06/ac2-quiet-window-evidence.json` (Phase 2) |
| AC3 旧库 Fail-Closed | `runner_p06.py`：启动新 Core 读取 Case 1A/1B/2 旧库 | Windows pwsh, Python 3.12.3 | **PASS** | `verification/P06/ac3-legacy-catalogs-evidence.json` |
| AC4 发布阻断清单 | 编写并核验 `RELEASE_BLOCKING_CHECKLIST.md` | 文档 | **PASS** | `verification/P06/RELEASE_BLOCKING_CHECKLIST.md` |
| AC5 零产品改动 | `git status --porcelain` | 仓库只读 | **PASS** | 仅 `doc/**` 与 `verification/P06/**` |

---

## 接收方式

- 分支：`codex/P06-gc-distribution-migration-evidence`
- Worktree：`G:/CODEX/New Manga.workspace/worktrees/P06-GC-DISTRIBUTION-MIGRATION`
- 交付提交：`2f2da8224fac4509129922069559738b639b47d8`
- 接收复核命令：
  ```powershell
  # 1. 验证全部原始证据文件存在且 SHA-256 与清单一致
  Get-ChildItem -Path "verification/P06" -File | ForEach-Object {
      [PSCustomObject]@{ Name = $_.Name; SHA256 = (Get-FileHash -Path $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant() }
  }
  # 2. 复跑全部真实进程验证（耗时 ~10s）
  & "G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" -u verification/P06/runner_p06.py
  ```

---

## 下一任务建议（必填）

- Task ID / 标题：`P04`（并发验收）/ `P20`（Windows 发布 Gate）
- 推荐 Agent / Reviewer：
  - P06 Reviewer: DeepSeek Harness (DSH)
  - 架构集成: Codex
  - P20 验收: ZCode / Codex
- 推荐原因与前置依赖：
  - P06 属于 GC 分发迁移补证，已闭环产出 G7 分发证据与出货阻断清单，满足 `verification/PROJECT-ROADMAP-RELEASE/REPORT.md` 中关于「P06 补限定证据」的要求；
  - P06 的结论直接解除 GC G7 对后续发布的未知阻断风险，P20 在进行 Windows 发布审查时可直接引用 `verification/P06/RELEASE_BLOCKING_CHECKLIST.md`。
- 可直接转发给 Reviewer (DSH) 的指令：
  ```
  请 Review P06 交付成果：
  - 坐标：G:/CODEX/New Manga.workspace/worktrees/P06-GC-DISTRIBUTION-MIGRATION
  - 分支：codex/P06-gc-distribution-migration-evidence
  - 交付 commit：2f2da8224fac4509129922069559738b639b47d8
  - 任务契约：doc/tasks/P06.md
  - 交付报告：verification/P06/REPORT.md 与 doc/handoffs/P06-antigravity-2f2da822.md
  - 核查重点：AC1 旧 runtime 构建真伪与产物哈希、AC2 真实双进程实测与 kill 释放证据、AC3 旧 catalog fail-closed 零篡改证据、AC4 发布阻断清单与边界纪律。
  ```

---

## 风险与遗留

- **边界纪律确认**：本仓库中不存在物理已装机的生产环境终端，本次验证通过构造证明了内核文件锁互斥与 fail-closed 机制的安全有效性；在真实多版本分发升级中，必须依赖安装程序（NSIS）严格保证旧版本所有残留进程已在安装前完全退出。
