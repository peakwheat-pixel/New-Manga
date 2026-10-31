# AC3（MA-11 / MA-20）：需要用户或 DSH 裁决的方案与影响

- Task：REALUSE-DATA-SAFETY-6 / AC3
- 状态：**仅方案，不实施**。本 Task 未执行任何迁移、未移动/删除/改名任何真实数据、未修改 `install.ps1` 等部署脚本、未跑安装流程。
- 事实基线：2026-11-01 对真实数据根 `C:\Users\49745\AppData\Roaming\com.newmanga.desktop`（产品默认 `%APPDATA%\com.newmanga.desktop`）的**只读**盘点，与仓库内代码阅读（见各节引用）。

---

## A. MA-11 旧库布局与旧壳共存

### A.1 事实基线（只读）

| 事实 | 值 / 依据 |
|---|---|
| 迁移实现在位 | `src/infrastructure/sqlite/upgrade_legacy_layout.py`（copy-only，从不删除/移动旧 `data/`；当前布局优先；staging + integrity_check + 原子提升；见文件头 docstring 与 `migrate_legacy_layout()`） |
| 何时跑 | **每次 Core 启动**：`src/bootstrap/core_service.py:5722` 调 `migrate_legacy_layout(data_root)`；失败则拒绝启动（`:5724-5737`，避免首次使用新建空库把旧数据永久盖掉） |
| 日志位置 | 只有真的复制了东西才写 `<root>/logs/upgrade-legacy.log`（`upgrade_legacy_layout.py:196`、`:296`） |
| 本机日志 | `logs/` 下**没有** `upgrade-legacy.log`，也没有 `.upgrade-legacy-staging` 残留 |
| 迁移为何没留痕 | 当前根 `library.db` 已存在且更完整，旧根 `data/` 里没有任何可合并内容（`data/backups`、`data/managed/temp` 是空目录），因此 `copied` 为空 → 只返回 skipped，不写日志。**不是"代码没跑"，而是"跑了但无事可做"** |
| 当前根库 | `library.db` 438,272 B（mtime 2026-10-30 11:02）：books 1 / chapters 1 / pages 169 / reading_progress 1 |
| 旧布局库 | `data/library.db` 344,064 B（mtime 2026-10-29 17:17）：books 1 / chapters 0 / pages 0 / reading_progress 0；另有 `data/library.db.run-owner.lock` |
| 旧壳检测 | `apps/desktop-avalonia/src/NewManga.Host/Coexistence.cs`：检测到 legacy Tauri shell（`new-manga.exe`）运行时 → `HostMode.ReadOnlyLegacyShellRunning`（新壳只读 + 提示，从不杀旧壳、从不双写） |
| 未变的安全前提 | 全程未打开、未写入旧根与当前根 DB；只读 SQLite 用 `file:...?mode=ro`，且只在**仓外副本**上执行 |

**结论性判定**：MA-11 描述里"真实数据根没有跑过迁移"应修正为"真实数据根上迁移是**幂等空操作**：当前布局已胜出，旧根无可合并内容，因此不产生日志"。真正仍成立的风险是：**旧 `data/library.db` 与 `data/` 子树仍然存在，旧壳若被启动仍可写另一份库，形成双库分叉。**

### A.2 可选方案

| 方案 | 做法 | 前置 | 影响 / 风险 | 可回滚性 |
|---|---|---|---|---|
| **A0 保持现状（零动作）** | 不碰真实数据；依赖"当前布局优先"的幂等迁移；继续由 Host 的旧壳检测把新壳切只读 | 无 | 双库分叉风险仍在；旧根占 344 KB 无实际价值；无任何写入 | 天然（未改动） |
| **A1 只读封存旧根** | 用户明确同意后，把 `<root>/data/` 改名为 `<root>/data.legacy-retired-<UTC>`（同卷 rename，不动内容），并写一条操作记录 | 需先做一次经过验证的备份（`.nmbak` 或整根 zip），并确认没有进程占用 | 旧壳若再启动可能新建 `data/`（需要 A4 配合）；改名是文件系统写操作，必须授权；恢复=改回名字 | 高（改名可回滚） |
| **A2 显式迁移（现有语义）** | 在**当前根库缺失或损坏**的场景，用 `migrate_legacy_layout` 的既有语义把旧根拷贝进当前布局；本机现实下会是空操作 | 备份 + 独占运行（无旧壳/无 Host）+ 结果核对 | 本机无收益；真正需要它的是"当前根丢失只剩旧根"的恢复场景 | 高（copy-only，旧根保留） |
| **A3 以旧库为准覆盖当前库** | 把 `data/library.db` 提升为当前库 | 需逐项 diff、用户逐项确认 | **高危**：违反当前布局优先与 AD-003 §3.4"不得整库覆盖"；会丢掉当前根 169 页/1 条进度（除非另有备份与合并方案） | 低（只能靠备份） |
| **A4 阻断旧壳写旧根** | 始终保持 Host 的旧壳检测；可选增加"启动时报告旧根存在 + 建议封存"的可见提示（UI 文案，不改数据） | 无 | 不改数据；只是把风险显性化；提示文案属于 UI 范围，需另立 AC | 高 |

**建议（不构成裁决，交用户/DSH）**：先 A0 + A4（零数据风险，把风险显性化）；若确认旧壳不再使用，再做 A1（需授权 + 备份）；A2 仅作为灾难恢复剧本；**A3 不建议**，任何"以旧库为准"的动作都必须是逐项确认的显式流程，且遵循 AD-003 §3.4 的 staging/commit marker/journal 要求。

### A.3 决策所需的最小输入

1. 旧壳（`new-manga.exe` / Tauri 版）是否还会被启动？（决定 A1/A4 的取舍）
2. 是否接受把旧 `data/library.db`（1 本书、0 章、0 页）视为**无价值残留**？（决定是否需要 A2/A3 的恢复剧本）
3. 允许的写操作边界：是否授权"同卷改名封存"（A1）？是否要求先做整根备份？

---

## B. MA-20 安装/验证脚本的默认数据根隔离

### B.1 事实基线

| 事实 | 依据 |
|---|---|
| 安装脚本默认写真实数据根 | `apps/desktop-avalonia/scripts/install.ps1:4` `[string]$DataRoot=$(Join-Path $env:APPDATA 'com.newmanga.desktop')` |
| 不加 `-SkipBackup` 时会**写入真实数据根** | `install.ps1:20`：`$DataRoot` 存在时 `New-Item <root>/backups` + `Compress-Archive` 整根打包成 `first-run-*.zip` 落在真实 `backups/` |
| 验证脚本目前都用 `-SkipBackup` | `install-smoke.ps1:14`、`install-verify.ps1:6,9` |
| 但"未触碰真实数据"是**断言而非测量** | `install-verify.ps1:15` 直接写 `data_root_untouched=$true` |
| 输出仍带真实路径 | `install.ps1:30` `data_root=$DataRoot` 写进 install JSON |
| 另一处默认真实根 | `scripts/migrate-legacy-dryrun.ps1:1` `LegacyRoot`/`TargetRoot` 默认都是真实根（dry-run 不写，但默认 source==target 的报告没有意义） |

### B.2 可选方案

| 方案 | 做法 | 影响 | 风险 |
|---|---|---|---|
| **M-1 最小硬化（默认隔离 + 显式选真）** | `install.ps1`：`$DataRoot` 改为**必填**或默认隔离路径（task-env 下），真实安装必须显式传 `-DataRoot (Join-Path $env:APPDATA 'com.newmanga.desktop')` 或 `-RealDataRoot`；`data_root_untouched` 改为安装前后实测（文件枚举 + 大小/哈希对比） | 真实安装多一步显式参数；验证/冒烟默认零触碰真实数据；报告从"声称"变"测量" | 低（脚本层，可回滚） |
| **M-2 保持默认真实根 + 二次确认** | 默认 `-SkipBackup`；只有显式 `-ConfirmRealData` 才允许向真实 `backups/` 写 zip，并打印目标路径与预计大小 | 改动小；但默认仍指向真实根，误用面仍存在 | 中低 |
| **M-3 仅文档化** | 不改脚本，在 README/验证说明标注"可能触碰真实数据"；不改 `data_root_untouched` 断言 | 零代码改动，风险完全留给人 | 中（断言仍可能误导） |
| **M-4 验证流程强制隔离** | 所有验证/冒烟/安装回归只在 task-env 隔离根运行；真实安装作为独立人工步骤（带备份与确认） | 验证可重复性最好；需要脚本默认值配合（否则靠调用方自觉） | 低 |

**建议（不构成裁决）**：**M-1 + M-4**（默认隔离 + 实测断言），M-2 作为过渡；纯 M-3 不推荐，因为它保留"硬编码的未验证断言"这一治理风险。

### B.3 与现有约束的关系

- 修改 `install.ps1` / `install-verify.ps1` / `install-smoke.ps1` 属于 `apps/desktop-avalonia/scripts/**`，在本 Task 的 `allowed_paths` 内，但**涉及部署流程与真实数据触碰语义**，按 Task 要求先裁决、不擅自实施。
- 任何"针对真实 `%APPDATA%` 的安装/备份/迁移"实验都必须先有用户授权，并在隔离根上先演练。

---

## C. 本 Task 明确未做的事

- 未运行 `migrate_legacy_layout`，未创建/删除/改名 `data/`，未写入 `<root>/logs/upgrade-legacy.log`。
- 未修改 `install.ps1` / `install-verify.ps1` / `install-smoke.ps1` / `migrate-legacy-dryrun.ps1`。
- 未运行任何安装、卸载、打包、备份或恢复流程。
- 真实数据根的全部访问都是读取：目录枚举 + `mode=ro` SQLite（在仓外副本上）+ 读取样本文件算 sha256。
