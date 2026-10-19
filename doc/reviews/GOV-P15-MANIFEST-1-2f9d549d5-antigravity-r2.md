---
task_id: GOV-P15-MANIFEST-1
reviewer: Antigravity
reviewed_head: 2f9d549d5
verdict: CHANGES_REQUESTED
revision: 2
note: 三项 Junction 已正确登记；但 P15M-RESTORED pin 与 delivery_head 未同步（已修）
---
### 复核结论概述

**总体结论：`CHANGES_REQUESTED`**

交付方对物理存在的 3 项 Junction 的盘点与反思记录均非常扎实、准确，但是在提交 commit `2f9d549d5` 时，**遗漏了同步更新本任务自身文档 [GOV-P15-MANIFEST-1.md](file:///G:/CODEX/New%20Manga/doc/tasks/GOV-P15-MANIFEST-1.md) 中的 Canonical Evidence 表与 `delivery_head`**，导致针对本任务的治理检查器报错失败（`Evidence SHA-256 不匹配`），未能达成 PASS 条件。

---

### 1. 三项 Junction 是否已正确补登记

**结论：已正确登记，实测状态与清单记录完全一致。**

打开 [resource-manifest.json](file:///G:/CODEX/New%20Manga/verification/P15/resource-manifest.json) 核对：
- `resources` 数组当前为 **4 项**（1 项 `worktree` + 3 项 `junction`）。
- 全部 4 项的 `disposition` 均为 `PRESERVE_REFERENCED`，作为历史评审复验与构建复现的现场保留项，处置定义完全恰当。

#### 现场实测路径状态（PowerShell `Test-Path` / `Get-Item -Force`）

| 资源路径 (`source_path`) | 存在性 (`Exists`) | 属性 (`Attributes`) | 类型 (`LinkType`) | 挂载目标 (`Target` / 物理实测) | 文件记载目标 (`destination_path`) |
|---|---|---|---|---|---|
| `G:/CODEX/New Manga.workspace/worktrees/P15` | `True` | `Directory` | — | — (HEAD: `ee19898fc`, 分支: `zcode/P15`) | `G:/CODEX/New Manga.workspace/worktrees/P15` |
| `G:/CODEX/New Manga.workspace/worktrees/P15/apps/desktop/frontend/node_modules` | `True` | `Directory, ReparsePoint` | `Junction` | `G:\CODEX\New Manga\apps\desktop\frontend\node_modules` | `G:/CODEX/New Manga/apps/desktop/frontend/node_modules` |
| `G:/CODEX/New Manga.workspace/worktrees/P15/apps/desktop/frontend/dist` | `True` | `Directory, ReparsePoint` | `Junction` | `G:\CODEX\New Manga\apps\desktop\frontend\dist` | `G:/CODEX/New Manga/apps/desktop/frontend/dist` |
| `G:/CODEX/New Manga.workspace/worktrees/P15/apps/desktop/src-tauri/target/core-sidecar` | `True` | `Directory, ReparsePoint` | `Junction` | `G:\CODEX\New Manga\apps\desktop\src-tauri\target\core-sidecar` | `G:/CODEX/New Manga/apps/desktop/src-tauri/target/core-sidecar` |

实测结果证实：3 项 Junction 均为真实有效的 Windows ReparsePoint，指向主仓库对应目录，与清单中的 `source_path`、`destination_path` 及 `verification.target` 记录完全相符。

---

### 2. 交付方是否如实记录了错误，而不是悄悄替换

**结论：记录如实、清楚且非常恰当。**

阅读 `notes` 数组第 3、4 条：
> *"First version of this file listed only the worktree, on the reasoning that P15's own records never name junctions. Antigravity's review rejected that reasoning and was right to: not recording a resource that physically exists is not the same as not fabricating one. The three junctions were then verified on disk - each is a real Windows ReparsePoint pointing into the main checkout - and registered."*
> *"The distinction that first version got wrong: fabricating provenance means inventing resources that do not exist. It does not mean declining to observe ones that do. Physical truth outranks textual silence."*

- **推理与错误说明**：清楚指出上一版是因“P15 原始文本记录从未提及 Junction”而推导出不应登记，并精准澄清了认知偏差——“伪造来源是指凭空捏造不存在的虚假资源，并不等同于拒绝如实盘点物理存在的真实挂载资源；物理真实性高于文本沉默”。并非模糊的“已修正”。
- **记录方式恰当性**：全文仅 5 条（约 20 行），用词克制精炼。作为一个恢复性治理工件（RESTORED artifact），如实交代为何在原始文本沉默的情况下记录该 3 项物理资源，不仅没有偏离用途，反而强化了该清单的审计证明力（Audit Integrity），恰到好处。

---

### 3. 检查器结果与阻断项

**结论：全局 PASS；`P15` 符合预期（只剩 1 个既有错误）；但本任务自身（`GOV-P15-MANIFEST-1.md`）FAIL。**

#### 实际执行结果

1. **本任务检查**：
   ```powershell
   pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-P15-MANIFEST-1.md
   ```
   **输出**：
   ```text
   Governance scope: 12 current documents; no historical directory scan.
   Task: doc\tasks\GOV-P15-MANIFEST-1.md
   WARN: doc/STATUS.md 已达到预算的 80%：3139 bytes / 30 lines
   FAIL: Evidence SHA-256 不匹配：verification/P15/resource-manifest.json
   Governance check: FAIL (1 errors, 1 warnings)
   ```

2. **全局检查**：
   ```powershell
   pwsh -NoProfile -File tools/governance/check.ps1
   ```
   **输出**：`Governance check: PASS (1 warnings)`。

3. **目标任务检查**：
   ```powershell
   pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P15.md
   ```
   **输出**：
   ```text
   Governance scope: 12 current documents; no historical directory scan.
   Task: doc\tasks\P15.md
   WARN: doc/STATUS.md 已达到预算的 80%：3139 bytes / 30 lines
   FAIL: Evidence SHA-256 不匹配：apps/desktop/frontend/src/settings/SettingsPage.test.tsx
   Governance check: FAIL (1 errors, 1 warnings)
   ```
   *说明：`P15` 缺失 manifest 的错误已成功消除，仅剩既有的 `SettingsPage.test.tsx` pin 错误（归属 `GOV-PIN-LINEAGE-1` 范围）。*

#### 阻断原因

交付方在 commit `2f9d549d5` 中更新了 [resource-manifest.json](file:///G:/CODEX/New%20Manga/verification/P15/resource-manifest.json)，并同步更新了 [P15.md](file:///G:/CODEX/New%20Manga/doc/tasks/P15.md) 中的 pin；**但是遗漏了修改自身任务文件 [GOV-P15-MANIFEST-1.md](file:///G:/CODEX/New%20Manga/doc/tasks/GOV-P15-MANIFEST-1.md)**：
- 第 76 行 `P15M-RESTORED` 的 SHA-256 依然停留在第一版的 `ccdb5fb7d...`（当前文件实测为 `2a8be70bc89152dba1b98d723c43458d2b725754ef6c3a302e4b30cec7c5a02e`）。
- frontmatter 的 `delivery_head` 仍停留在 `237c43862...`。

---

### 推荐下一步

交由交付方完成以下补丁后重新交验：
1. 在 [GOV-P15-MANIFEST-1.md](file:///G:/CODEX/New%20Manga/doc/tasks/GOV-P15-MANIFEST-1.md) 的 Canonical Evidence 表中更新 `P15M-RESTORED` 的 SHA-256 为 `2a8be70bc89152dba1b98d723c43458d2b725754ef6c3a302e4b30cec7c5a02e`，commit 更新为对应版本。
2. 更新 frontmatter 中的 `delivery_head`。
3. 运行 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-P15-MANIFEST-1.md` 确认本任务达到 PASS。
