---
task: REALUSE-DATA-SAFETY-5
round: 1
reviewer: antigravity-headless
reviewer_participated_in_implementation: false
verdict: FAIL_WITH_MUST_FIX
reviewed_head: 7bb96e49d
reviewed_base: a5c08bfb0
captured_by: dsh-lead
capture_note: >
  Antigravity 原始回答逐字保存（agy headless --output-format json 的 response 字段）。
  正文未做任何编辑。四轮里前三轮都是 FAIL_WITH_MUST_FIX，且两轮针对的是同一件事：
  我第一次把「没搜到」写成了「不存在」，第二次又只把更正写进了仓外文件。
---

# REALUSE-DATA-SAFETY-5 独立审查（Round 1，Antigravity）

**本轮核心问题**：自查记录失真（我第一次用标题格式搜索，漏掉了列表格式的 MA-21/22 并据此断言它们从未存在）；MA-20 脚本路径误判；README 备份扩展名未同步；Task 卡证据 pin 缺失与治理检查失败

## 审查结论

**FAIL_WITH_MUST_FIX**

代码实现的 5 项修复（MA-14 CLI 校验、MA-15 sidecar 相对指引、MA-16 README 状态与能力修正、MA-17 Batch 状态文案、MA-18 备份独立后缀）本身质量优秀，单元与集成测试全部通过（876 passed / 0 failed），且未引入回归。

然而，**自查复核结论存在重大失实断言**：任务卡与复核记录宣称“DEFECTS.md 实际只到 MA-20，MA-21/22 从未存在”，但经查证，DEFECTS.md 第 116-120 行明确记录了 MA-21 和 MA-22，且代码中 MA-22 确实成立；此外，MA-20 脚本实际一直在仓库中并未缺失。同时，任务卡证据引脚和治理检查器存在阻塞项，故判定为必须修复后再进入下一阶段。

---

## 必须修复清单（Must-Fix Items）

### 1. 【重大/P1】AC2 判定失真：误称 MA-21 / MA-22“从未存在”
- **问题描述**：Task 卡将 AC2 标记为 `<<NOT_APPLICABLE>>` 并勾选完成，在复核记录中声称：“DEFECTS.md 实际只到 MA-20，MA-21/22 从未存在（B4 批次表记账错误）”。
- **事实依据**：
  查阅仓外权威自查记录 `G:\CODEX\New Manga.workspace\tmp\self-audit\DEFECTS.md` 第 116-120 行，赫然存在清晰条目：
  ```markdown
  ## P4（卫生项）

  - **MA-21** wire 日志对 `SaveReadingProgress` 重复记录（725 条中 10 条 request 空、response 为进度结果）。
  - **MA-22** `logs/grants/` 每页一个文件且无清理（169 页 = 169 文件）。
  ```
  进一步核查代码：[`HostGrantCoordinator.cs#L516,L559`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/apps/desktop-avalonia/src/NewManga.Host/HostGrantCoordinator.cs#L516-L559) 每次 import 或 export 都会在 `logs/grants/` 下写入 `{operation}-{timestamp}.json`，且没有任何清理策略或配额控制。**MA-22 描述的缺陷在代码中完全真实存在**。
- **修改建议**：
  1. 纠正 DEFECTS.md 复核记录与 Task 卡中的错误断言；
  2. 对 MA-21 与 MA-22 给出实事求是的复核判定；
  3. 按照 AC2 要求，要么修掉，要么在 Task 卡与 DEFECTS.md 中明确记录为何暂不处理并放入后续计划，不可把已存在的条目记录为“从未存在”。

---

### 2. 【中等/P2】MA-20 核对结论失真：误称 `install.ps1` 不在仓库
- **问题描述**：Task 卡与复核记录称：“MA-20 未核对：`scripts/install.ps1` 不在当前仓库（可能已移出或改名），需先确认脚本归属再判定”。
- **事实依据**：
  该脚本完好存在于本仓库：[`apps/desktop-avalonia/scripts/install.ps1`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/apps/desktop-avalonia/scripts/install.ps1#L1-L25)。
  其第 4 行与第 20 行：
  ```powershell
  [string]$DataRoot=$(Join-Path $env:APPDATA 'com.newmanga.desktop'),
  ...
  if(-not $SkipBackup -and (Test-Path $DataRoot)){ $backupDir=Join-Path $DataRoot 'backups'; New-Item -ItemType Directory -Force $backupDir|Out-Null; $backup=Join-Path $backupDir ("first-run-"+[DateTime]::UtcNow.ToString('yyyyMMddHHmmss')+".zip"); Compress-Archive -Path (Join-Path $DataRoot '*') -DestinationPath $backup -CompressionLevel Optimal -ErrorAction SilentlyContinue }
  ```
  行号与逻辑与 DEFECTS.md 所指出的“默认以真实 `%APPDATA%` 为 DataRoot 触碰真实用户数据”完全吻合。
- **修改建议**：定位到真实路径 `apps/desktop-avalonia/scripts/install.ps1`，补充该条目的真实复核判定（如：“仍成立，涉及安装脚本隔离，留给后续 Task”）。

---

### 3. 【中等/P2】`README.md` 第 35 行关于首次备份扩展名的陈旧描述未更新
- **问题描述**：MA-18 修复将首次备份扩展名从 `*.nmbak` 改为了 `.sqlite-backup`，以彻底隔离 Core 的 `.nmbak` zip 包命名空间。然而 `README.md` 第 35 行仍残留旧描述。
- **事实依据**：
  [`README.md#L35`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/README.md#L35)：
  > 每次启动在 sidecar 之前执行 first-run 备份（`%APPDATA%\com.newmanga.desktop\backups\*.nmbak`，幂等不覆盖）。
- **修改建议**：将 `*.nmbak` 更新为 `*.sqlite-backup`（或注明兼容旧版 `*.sqlite.nmbak`），保持对外文档与代码行为一致。

---

### 4. 【治理/P2】Task 证据引脚缺失与治理检查器失败
- **问题描述**：运行 `pwsh -NoProfile -File tools/governance/check.ps1` 报告 8 errors。
- **事实依据**：
  1. [`doc/tasks/REALUSE-DATA-SAFETY-5.md`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/doc/tasks/REALUSE-DATA-SAFETY-5.md#L77-L82) 中的 Canonical Evidence 表全填为 `PENDING`，缺少交付提交哈希（应 pin 至 `eb5b136e8`）；
  2. Evidence 表第 82 行将路径写为带反引号和中文括号的文本 `DEFECTS.md`（仓外 G:/...），导致检查器报错“路径缺失”；
  3. `REBASELINE_PLAN.md` 中 REALUSE-DATA-SAFETY-5 挂在 READY 节点但状态为 `in_review`，违反状态流转约定；`TASK_LEDGER.md` 计数未同步更新。
- **修改建议**：pin 对应 commit `eb5b136e8`，修正 evidence 路径文本，并按治理协议刷新 `REBASELINE_PLAN.md` 与 `TASK_LEDGER.md`，使 `check.ps1` 完全通过。

---

## 已检查且判定无问题的项（Verified Clean）

1. **MA-14 CLI 校验白名单与真实消费方完全一致**：
   - `--page` 白名单（`bookshelf`, `library`, `reader`, `workbench`, `studio`, `settings`, `console`）完整映射至 V2 壳的三大空间（Library/Studio/Console）以及 Legacy 壳四个页面，既无遗漏也无多余，且已做小写规范化；
   - `--variant` 校验仅允许 `light` 和 `dark`（不区分大小写），与 [`App.axaml.cs#L152`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/apps/desktop-avalonia/src/NewManga.App/App.axaml.cs#L152) 及 `LegacyStartupTheme` 的实际消费逻辑完全一致（系统仅解析 dark，其它均按 light 处理）；
   - 非法输入正常走既有 `InvalidReason` 路径（exit 2 + 写入 `logs/invalid-arguments.log`），行为统一。
2. **MA-18 首次备份兼容性与安全性**：
   - **兼容性**：[`DataSafety.cs#L49`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/apps/desktop-avalonia/src/NewManga.Host/DataSafety.cs#L49) 同时枚举 `catalog.*.sqlite-backup` 和 `*.sqlite.nmbak`，已有安装的旧备份文件（`catalog.*.sqlite.nmbak`）会被正常识别并命中跳过，**绝不会重复创建**；
   - **安全性**：`catalog.*.sqlite-backup` glob 前缀后缀双重约束，不会误匹配其它文件；
   - **隔离性**：Core 的 `backup.list` 和自动 prune 均基于 `*.nmbak` glob，新备份文件采用 `.sqlite-backup` 后，不仅不会抑制首次备份，而且彻底避免了此前旧备份被 Core 误读为 `unknown` 损坏 zip 包的问题。
3. **MA-15 相对路径与错误指引**：
   - UI 提示 [`SidecarException.cs#L40-L43`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/apps/desktop-avalonia/src/NewManga.CoreClient/Diagnostics/SidecarException.cs#L40-L43) 仅呈现相对层级（“程序目录下的 core-sidecar”、“resources/core-sidecar”等），**绝无任何绝对路径**；
   - `SidecarLocator.cs` 中包含绝对路径的候选列表仅注入 `SidecarException.Message`，由 `HostLog.Error` 记入 `host.log` 诊断文件；UI 和 `HostController` 均使用 `error.UserMessage`，绝对路径绝不暴露至 UI。
4. **MA-17 Batch 状态中文指引**：
   - 当 `HOST_READ_ONLY` 或 `HOST_NOT_READY` 时，界面提供清晰可执行的恢复说明；且针对非 Provider 原因导致的拒绝，`NeedsProviderSetup` 准确保持为 `false`，不产生误导性 CTA。
5. **MA-19 / MA-09 / MA-11 核对结论属实**：
   - MA-19：`derived/` 目录下确由 `RenderPreviewPublisher` 生成原图全尺寸预览副本（`page-original-{pid}`），目前确无缩减或清理机制，属于资源通道架构演进范围，暂缓处理判定合理；
   - MA-09（阅读进度刷新未接）与 MA-11（迁移分叉）核对结论与代码现状完全一致。
6. **无功能回归**：
   - 整体测试 876 passed / 0 failed，编译 0 Warning / 0 Error。

---

## 推荐下一步

通知实现 Agent（DSH）针对上述 4 项 Must-Fix 进行修复：
1. 修正 Task 卡及 DEFECTS.md 复核记录中关于 MA-21/MA-22 的事实错误，补充真实判定，并核对修正 MA-20 脚本路径与判定；
2. 同步更新 `README.md` 第 35 行中的备份扩展名为 `*.sqlite-backup`；
3. Pin Task 卡 Canonical Evidence 的 commit（`eb5b136e8`），修正路径格式，并更新 `REBASELINE_PLAN.md` 与 `TASK_LEDGER.md` 确保 `tools/governance/check.ps1` 校验全绿；
4. 修复完成后再次提交独立审查。
