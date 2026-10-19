---
task_id: GOV-P15-MANIFEST-1
reviewer: Antigravity
reviewed_head: 6eec515a5
verdict: CHANGES_REQUESTED
revision: 1
note: 实测三个 Junction 全部存在；指出「不抄同类 Task 字段」混淆了伪造与拒绝观察
---
# Review 报告：Task GOV-P15-MANIFEST-1

**审查角色**：Antigravity（独立只读 Reviewer）  
**审查对象**：`Task GOV-P15-MANIFEST-1`  
**Delivery Head**：[`237c43862`](file:///G:/CODEX/New%20Manga/doc/tasks/GOV-P15-MANIFEST-1.md#L16)  
**总体结论**：**`CHANGES_REQUESTED`**（要求返工补齐资源登记）

---

## 逐项核对结论

### 1. 重建的字段是否能在既有记录中找到依据

- **结论**：**符合依据，元数据扩展恰当。**
- **依据核对**：
  - `resources[0]`（`resource_type: "worktree"`、`source_path`、`disposition: "PRESERVE_REFERENCED"`、`destination_path`）四项与 [`doc/tasks/P15.md` L104](file:///G:/CODEX/New%20Manga/doc/tasks/P15.md#L104) 的 Resource Manifest 表完全一致。
  - `closeout_counts` 中的 `deleted: 0`, `moved: 0`, `archived: 0` 与 [`doc/tasks/P15.md` L112](file:///G:/CODEX/New%20Manga/doc/tasks/P15.md#L112) Closeout Record 明确记录的“删除、迁移、归档数量/字节数：0”完全吻合。
  - 针对交付方自行添加的字段（`recorded_at`、`restored_by`、`restoration_basis`、`verification`、`notes`）：
    - **评估**：这些属于**合理且必要的溯源元数据（Provenance）**，没有破坏清单结构，也未使清单偏离其核心功能。由于原件未曾提交入库，明确注明恢复主体与依据是诚实性治理的要求，能够防止后续维护者误将其当做当初现场封存的原件；`verification` 子对象记录了实测校验事实。
    - **注**：`notes` 中耗费篇幅辩解“为何不写其它资源”，反衬出对物理资源实测盘点的不足（见第 2 点）。

---

### 2. 「不抄同类 Task 的字段」是否过于保守？（关键裁定）

- **结论**：**过于保守，本 Task 交付不完整，应补登记 3 项物理存在的 Junction。**
- **实测证据**（通过 PowerShell `Test-Path` 与 `Get-Item` 在 `G:\CODEX\New Manga.workspace\worktrees\P15` 实地检测）：

  ```powershell
  # 实测结果
  apps/desktop/frontend/node_modules         : Directory, ReparsePoint (Junction) -> G:\CODEX\New Manga\apps\desktop\frontend\node_modules
  apps/desktop/frontend/dist                 : Directory, ReparsePoint (Junction) -> G:\CODEX\New Manga\apps\desktop\frontend\dist
  apps/desktop/src-tauri/target/core-sidecar : Directory, ReparsePoint (Junction) -> G:\CODEX\New Manga\apps\desktop\src-tauri\target\core-sidecar
  ```

  三个路径**不仅全部存在**，而且全部是 Windows **ReparsePoint（Junction）**，均挂载并指向主仓库对应路径！
- **裁决理由**：
  1. **物理真实性高于原始文本缺失**：交付方认为“P15 原始文本没写，抄进来就是伪造来源”，混淆了“凭空捏造不存在的虚假资源”与“对现实物理挂载资源的诚实盘点”。
  2. **治理安全防线**：Resource Manifest 的核心职能是防范资源悬空和非预期数据损坏（Accidental Data Loss Prevention）。P15 工作树内实际挂载了指向主仓的 3 个 Junction；如果清单隐瞒/漏记这些外部链接，未来在执行 Worktree 清理、归档或目录修剪时，极易因未知 Junction 关系而导致主仓关键依赖或构建产物受损。
  3. **交付方在 Handoff 中主动声明的局限成立**：交付方已明确提出若 AC2 要求登记实际存在的物理资源，则当前交付尚未完成。经实测确证，**必须对上述 3 个 Junction 予以补充登记**。

---

### 3. 剩下的 1 个检查器错误是否与本 Task 无关

- **结论**：**确认无关，确属时间性失配。**
- **核验核实**：
  - `apps/desktop/frontend/src/settings/SettingsPage.test.tsx` 变更历史显示：
    - `e5f1a719b`：P15 交付实现时锁定的 commit，P15 E6 记录的 SHA-256 即基于此点。
    - `528c6289c`：后续任务（`fix(desktop): disable unopened settings and surface import feedback`）修改了该文件，导致主仓当前文件哈希变更。
  - 本 Task（commits `237c43862`、`6eec515a5`、`85a27a0f7`）仅操作治理与验证文档，未触及该测试文件。
  - 该错误由治理跟踪的后向演进引起，属于立项中的 `GOV-PIN-LINEAGE-1` 范围，非本 Task 引入。

---

## 治理检查执行记录

| 检查命令 | 执行结果 | 说明 |
|---|---|---|
| `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-P15-MANIFEST-1.md` | **PASS** (1 warn) | STATUS.md 预算告警（80%） |
| `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS** (1 warn) | STATUS.md 预算告警（80%） |
| `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P15.md` | **FAIL** (1 err, 1 warn) | 原缺失 manifest 错误已消除；仅剩既有 `SettingsPage.test.tsx` pin 错误 |

---

## 推荐下一步

向 Task Owner（Codex / 承接方）返回 **`CHANGES_REQUESTED`**，返修要求如下：
1. 在 [`verification/P15/resource-manifest.json`](file:///G:/CODEX/New%20Manga/verification/P15/resource-manifest.json) 的 `resources` 数组中补入实测存在的 3 项 Junction 资源，类型标为 `junction`，disposition 标为 `PRESERVE_REFERENCED`，注明其源路径与指向主仓库的目标路径及 LinkType；
2. 同步更新 [`verification/GOV-P15-MANIFEST-1/ac1-ac4-manifest-restoration.md`](file:///G:/CODEX/New%20Manga/verification/GOV-P15-MANIFEST-1/ac1-ac4-manifest-restoration.md) 的实测核验说明，并更新任务与 Handoff 文档后重新提交 Review。
