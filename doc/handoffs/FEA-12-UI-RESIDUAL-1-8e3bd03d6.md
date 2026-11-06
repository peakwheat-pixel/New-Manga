---
task_id: FEA-12-UI-RESIDUAL-1
author: ui-residual-impl（DSH Agent Teams 成员；Lead `lead`）
recipient: DeepSeek Harness
base_commit: 9c6ba2da1
delivery_head: 8e3bd03d6
status: in_review
---

# Handoff — FEA-12-UI-RESIDUAL-1（App-only 四项 P3 残余收口）

- Task：`doc/tasks/FEA-12-UI-RESIDUAL-1.md`（Owner=`ui-residual-impl`；卡面 `status` 由 DSH 维护，本 Handoff 不改）
- 交付日期：2026-11-06（Asia/Shanghai）
- 交付基线：`base_commit 9c6ba2da1`（main，clean；较卡面 `base_commit 690c77eb0` 多 1 个 docs-only 提交，代码/测试树等价）；**未 push、未创建 linked worktree**
- 交付实现 + 测试 commit：**`8e3bd03d6`**（2 files changed, 215 insertions, 8 deletions）
- 证据/卡面/本 Handoff：`verification/FEA-12-UI-RESIDUAL-1/**` + `doc/tasks/FEA-12-UI-RESIDUAL-1.md` + 本文件（同批证据提交；`delivery_head` 只指向实现+测试提交）
- 环境：Windows 11 10.0.26300 / PowerShell 7 / CPython 3.14.6 / .NET SDK 10.0.401（net9.0 测试目标）；无新依赖、无 schema/migration/契约/wire 改动
- 范围依据：冻结卡 In（I-1…I-5）与 `doc/reviews/FEA-12-UI-RESIDUAL-1-scope-r1.md`（READY-TO-FREEZE），DSH 2026-11-06 四项冻结口径

## 1. 交付结果（逐项对照 AC）

| 项 | 结果 | 交付内容 |
|---|---|---|
| **I-1** delete-time capability 防御边 | 完成 | `TrashViewModel.ConfirmDeleteAsync` 的 `TrashDeleteOutcome.CapabilityMissing` 分支：删除对页级 `_capabilityMissing`/`_capabilityMessage` 的污染；保留 `_deleteOutcomeCode`（`result.Code ?? CORE_CAPABILITY_MISSING`）、`DeleteResultTitle="删除被拒绝"`、含 typed code 与“未删除任何内容”的结果文案；以 `_previewBlockedReason` 使同一预览 `CanConfirmDelete=false`；不新 probe、不改能力布尔、零成功提示。**defensive invariant only：该分支生产不可达（L-R1），不宣称修复用户可见缺陷。** |
| **I-2** preview `BOOK_NOT_FOUND` 自动刷新 | 完成 | `BeginPermanentDeleteAsync` 的 preview 失败块新增 `BOOK_NOT_FOUND` 前置分支：`_notify` + `ResetPreview()`（关披露面板）+ `await ReloadAsync()`（只一次、重新 probe 并刷新列表）；零 delete 帧、零自动重试；其它失败码（`BOOK_BUSY`/旧 Core/`CORE_UNAVAILABLE`/未知）仍走原“就地错误 + 重新预览”分支，未改动。 |
| **I-3** cleanup retry `BOOK_NOT_FOUND` 提示 | 完成 | `RetryCleanupAsync` 的 NotFound 分支在 `ResetPreview()` 前补 `_notify`（旧实现设置的 `_deleteOutcomeText` 会被 `ResetPreview` 清空而用户不可见）；随后 `ResetPreview()` + `await ReloadAsync()`；`_cleanupPendingVisible=false`/`CanRetryCleanup=false`/面板关闭；digest 仍沿用首次 `_activeDigest`（逐字节相同），不伪报完成、不自动重试、不为 NotFound 重跑 preview。 |
| **I-4** 只读/能力缺口双原因文案 | 完成 | `ShowHostReadOnlyBanner => _hostReadOnly`（去掉 `&& !HasCapabilityGap` 抑制）；`HostReadOnlyBannerText` 删除“回收站可浏览”分句改为“不会执行任何写入；软删/恢复/彻底删除已禁用”；组合态两条 banner 同时展示；单一原因仍单 banner；未改 XAML/控件/令牌。 |
| **I-5** 测试/证据/门禁 | 完成 | `TrashUiTests.cs` 新增 5 个判别测试（对应 AC-R1/R2/R3/R4a/R4b）；`verification/FEA-12-UI-RESIDUAL-1/**`（EV.md、RESOURCE-MANIFEST.json、changed-files.txt、`logs/` 9 份含变异红日志）；变异 9/9 红；全量门禁不降（见 §2）。 |

## 2. 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC-R1 防御边 | `dotnet test ... --filter FullyQualifiedName~Delete_CapabilityMissing_DoesNotTurnThePageIntoReadCapabilityMissing` | Win11 / .NET SDK 10.0.401（net9.0）/ tree `8e3bd03d6` | PASS（绿）；变异 M1 RED | `logs/gates-targeted-after.log`、`logs/scope-mutations.log`（EV-2/EV-8） |
| AC-R2 preview 刷新 | `--filter FullyQualifiedName~Preview_BookNotFound_ClosesPanel_AndReloadsTheList` | 同上 | PASS；变异 M2/M3/M4 RED | EV-2/EV-8 |
| AC-R3 cleanup retry NotFound | `--filter FullyQualifiedName~CleanupRetry_SecondRetryBookNotFound_NotifiesAndRefreshes_WithSameDigest` | 同上 | PASS；变异 M5/M6/M7 RED | EV-2/EV-8 |
| AC-R4 双原因 | `--filter FullyQualifiedName~HostReadOnly_PlusWriteCapabilityGap_ShowsBothIndependentCauses` / `...HostReadOnly_PlusReadCapabilityMissing_ShowsCapabilityStateAndReadOnlyReason` | 同上 | PASS；变异 M8/M9 RED | EV-2/EV-8 |
| AC-R5 定向 | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release --filter FullyQualifiedName~TrashUiTests` | 同上，before/after 两次 | **before 35/0/0 → after 40/0/0（全绿）** | `logs/gates-targeted-before.log` / `logs/gates-targeted-after.log`（EV-1/EV-2） |
| AC-R5 全量 .NET | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` | 同上，before/after 两次 | **before 1527 passed / 0 failed / 86 skipped → after 1532 / 0 / 86**；8 项目 before=21+38+253+117+31+185+167+715、after=21+38+253+117+31+185+167+720；skip=86 为既有环境门控（Host 55 / CoreClient 24 / App 7），未新增/改变 | `logs/gates-dotnet-before.log` / `logs/gates-dotnet-after.log`（EV-3/EV-4） |
| AC-R5 pytest | `C:/Python314/python.exe -m pytest tests -q` | 同上（零 Python diff） | **3249 passed / 10 skipped / 0 failed，EXIT=0（278.59 s）**，与基线相同 | `logs/gates-pytest.log`（EV-5） |
| AC-R5 pins/check/API | `pwsh -NoProfile -File tools/governance/verify_pins.ps1`；`... check.ps1`；`C:/Python314/python.exe tools/generate_api_inventory.py --check` | 同上 | **pins 18/18 PASS；check PASS(3 warnings)；API inventory PASS（EXIT=0）** | `logs/gates-governance.log`（EV-6） |
| AC-R5 scope | `git diff --name-only 9c6ba2da1..8e3bd03d6`、禁止面/依赖/API 文件 diff | 同上 | 仅 2 个允许 App 文件；禁止面、依赖、API 面**零 diff**（证据提交只追加 allowed_paths 内文件） | `logs/scope-validation.log`（EV-7） |
| AC-R5 变异 | 9 个破坏性文本替换 + 目标用例复跑 + pristine 逐字节恢复 | 同上 | **9/9 RED（EXIT=1，断言失败）；恢复 SHA-256 一致** | `logs/scope-mutations.log`（EV-8） |
| AC-R5 汇总 | — | — | — | `logs/gates.log`（EV-9）、`EV.md`（EV-12）、`RESOURCE-MANIFEST.json`（EV-10）、`changed-files.txt`（EV-11） |
| L3/L4 | 真机走查 | — | **NOT_RUN**（本卡不新增真机证据，不得声称通过） | 本文件 |

**未运行/未覆盖**：L3/L4 真机走查未运行；cleanup retry NotFound 无真实 L2 IPC 证据（L-R6）；I-1 生产不可达（L-R1）；pytest 的 QML `TypeError` stdout 噪声为既有 legacy Qt 测试输出，`0 failed`、EXIT=0。

## 3. 接收方式

- 仓库 `G:\CODEX\New Manga`，branch `main`；base `9c6ba2da1`；实现+测试 commit `8e3bd03d6`；证据/卡/Handoff 紧随其后的证据提交（`git log -- verification/FEA-12-UI-RESIDUAL-1`）。
- 复现门禁：见 §2；定向/全量 `.NET` 与 pytest 命令原样可跑。**注意**：全量 .NET 会重写 tracked `verification/FEA-09/logs/wire-redacted.ndjson`（既有副作用），跑完请 `git checkout -- verification/FEA-09`。
- 复核建议：先 `git show --stat 8e3bd03d6`，再读 `verification/FEA-12-UI-RESIDUAL-1/EV.md` §2/§4 与 `logs/scope-mutations.log`，逐项对照 `TrashUiTests.cs` 的 5 个新用例与 `TrashViewModel.cs` 的 4 处改动。

## 4. 下一任务建议（必填）

- **Task ID / 标题**：无需新 Task —— 下一步是本卡的**独立上下文 Review**（`doc/reviews/FEA-12-UI-RESIDUAL-1-r1.md`），随后 DSH 集成验证/closeout。
- **推荐 Agent / Reviewer**：DSH 指派的 fresh subagent（独立上下文、只读被审 head；不得由实现会话/实例自审；报告记录 reviewer 与 session）。
- **推荐原因与前置依赖**：实现+测试+证据已完成、门禁全绿；Review 必须独立于本实现会话。前置：`delivery_head=8e3bd03d6` 与证据目录。
- **Recovery point**：仓库 `G:\CODEX\New Manga`，branch `main`，base `9c6ba2da1`，head=`8e3bd03d6`（+ 证据提交）；未创建 worktree。
- **允许修改路径**：Review 仅写 `doc/reviews/FEA-12-UI-RESIDUAL-1-*.md`（只读其余）。
- **禁止范围与新增授权条件**：不得改生产代码/测试/契约/STATUS/PLAN/LEDGER/FEA-12-UI 历史字节；若发现需扩域（Host/Core/契约/XAML/fake），停下报 DSH。
- **交付物**：Review 报告（verdict + findings + 逐项 AC 核对 + 变异/证据复核）。
- **验证命令、环境与完成 Gate**：§2 全部门禁；Review 需独立复跑定向 `TrashUiTests` 并抽验 1–2 个变异。
- **可直接转发给 Agent 的指令**：`你是独立上下文 Review。只读审 FEA-12-UI-RESIDUAL-1（head 8e3bd03d6，base 9c6ba2da1）的 2 个 App 文件、卡、EV.md、logs；按 AC-R1…R5 逐项核对判别性测试与 9 个变异红日志；复跑定向 TrashUiTests 与全量 .NET；只写 doc/reviews/FEA-12-UI-RESIDUAL-1-r1.md，不得改实现/测试/证据/STATUS；发现需扩域立即停下报 DSH。`

## 5. 风险与遗留

- **L-R1**：I-1 为 defensive invariant only，Host 当前不对 `library_delete_book_permanently` 做能力门、Core 不返回 `CORE_CAPABILITY_MISSING` → **生产不可达**；不得写成已修复用户可见 bug。
- **L-R2**：`CORE_CAPABILITY_MISSING` 不在 `AllowedDeleteTrashErrorCodes`（Host 投影 category→unknown，code 保留）；属 Host/Core，本卡不修。
- **L-R3**：preview NotFound 的 `ReloadAsync` 自身失败只显示列表错误态、不自动重试（有意）。
- **L-R4**：cleanup retry NotFound 后关闭结果面板，typed 提示只经 `_notify`；保留面板需另冻结规则。
- **L-R5**：组合态两条 banner 同时出现（接受视觉冗余以不丢原因）。
- **L-R6**：四项均为 VM 级 fake 证据，无新增真实 IPC；cleanup retry NotFound 无 L2 IPC 证据。
- **L-R7**：只读文案移除“可浏览”，read 可用时信息量略减。
- **L3/L4 真机走查 NOT_RUN**；FEA-12-UI 历史 AC 未回填；**未 push**。
- 过程记录：变异循环恢复 pristine 文件时 `Copy-Item` 保留 mtime，MSBuild 增量曾用 M9 变异产物导致一次伪红；刷新时间戳后定点+全量重跑干净，canonical 日志为重跑版本（详见 EV.md §2）。
