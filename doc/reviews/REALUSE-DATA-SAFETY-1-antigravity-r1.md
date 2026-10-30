---
review_id: REALUSE-DATA-SAFETY-1-antigravity-r1
task: REALUSE-DATA-SAFETY-1
reviewer: Antigravity (agy CLI headless, conversation 9ef73697-d0df-47d4-9407-6c61d9755cce)
reviewer_independent: true
reviewed_by_implementer: false
range: b1c1f5a56..586adcc7c
verdict: FAIL_WITH_MUST_FIX
captured_at: 2026-10-30T16:12:00+08:00
captured_by: DSH (verbatim, no edits to the review content)
---

# 独立审查：REALUSE-DATA-SAFETY-1（第 1 轮）

> 本文由 Antigravity（未参与实现）以只读模式审查 `b1c1f5a56..586adcc7c` 后给出，DSH 仅原样落盘，未改动任何审查结论。

### 审查范围与基线
- **工作区**：`G:\CODEX\New Manga.workspace\worktrees\REALUSE-DATA-SAFETY-1`
- **分支**：`task/REALUSE-DATA-SAFETY-1`
- **Diff 范围**：`git diff b1c1f5a56..586adcc7c`（9 个提交，24 个文件，+2069 / -86 行）
- **审查性质**：只读审查（未修改任何工作区文件，所有结论均基于代码与测试事实）

---

### 总结论

**FAIL-WITH-MUST-FIX**

> [!CAUTION]
> 本次提交在数据安全性上取得了实质性修复（如 AC1 自愈、Console 接线与二次确认），但在 **备份路径安全校验（Path Traversal 漏洞）** 与 **非空目录合并的原子写入保证** 上存在高风险漏洞，必须修复后方可合并。

---

### 逐条审查结论概览

| 序号 | 审查项 | 结论 | 关键判定原因 |
|---|---|---|---|
| 1 | `nmbak.py` 的 `page_original_refs` 路径穿越 / 越界 | **有问题** | 打包与恢复均未对 `managed_path` 做纯相对路径与防穿越校验，存在逃逸与任意写风险 |
| 2 | `core_service.py` 的 `_ensure_automatic_backup` 判据 | **有问题** | 以“存在任意 verified 包”为判据，导致初次之后的新增数据永久处于零自动备份状态 |
| 3 | `core_service.py` 的 `_prune_automatic_backups` 修剪 | **OK** | 严格保留最新 5 个 automatic 包且不碰 manual 包，单包场景 `excess <= 0` 不会误删 |
| 4 | `upgrade_legacy_layout.py` 的 `_promote_directory_merged` | **有问题** | 不会覆盖当前文件（OK），但 `shutil.copy2` 非原子写，中断将留下无法自愈的半写损坏文件 |
| 5 | `catalog_store.py` 的 fail-closed 目录替换绕过 | **OK** | 强制要求 lock 与 catalog 完全一致 + canonical schema + 底层 handle 身份校验，无法绕过 |
| 6 | Console 恢复二次确认链 | **OK** | UI 命令严格绑定确认弹窗，Core 侧服务端与服务层双重校验 `confirm_restore: true` |
| 7 | 测试套件负向覆盖 | **有问题** | 缺少路径穿越、恶意包恢复、拷贝中断半写、数据过期自动备份等关键负向用例 |

---

### 必须修复项（MUST-FIX）

#### 1. `nmbak.py` 存在打包越界读取与恢复任意文件写入（Path Traversal）风险
- **文件与行号**：
  - 打包阶段：[`src/infrastructure/sqlite/nmbak.py:374-388`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/src/infrastructure/sqlite/nmbak.py#L374-L388)、[`src/infrastructure/sqlite/nmbak.py:448-450`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/src/infrastructure/sqlite/nmbak.py#L448-L450)
  - 校验与恢复：[`src/infrastructure/sqlite/nmbak.py:543-555`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/src/infrastructure/sqlite/nmbak.py#L543-L555)、[`src/infrastructure/sqlite/nmbak.py:603-618`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/src/infrastructure/sqlite/nmbak.py#L603-L618)
- **风险**：
  1. **打包时越界读取与自覆写**：`_page_original_refs` 从数据库读取 `pages.managed_original_ref` 后直接执行 `source = self._managed_root / Path(managed_path)`。在 Python `pathlib.Path` 中，若 `managed_path` 是绝对路径（如 Windows 盘符 `C:/...` 或 `/...`），右侧绝对路径会直接**覆盖**左侧根路径；若包含 `../`，则可向上逃逸出 `managed_root`。随后在 `_copy_managed_files` 中：`destination = workdir / MANAGED_PREFIX / Path(managed_path)`，同样会被绝对路径覆盖，甚至导致 `destination.write_bytes(source.read_bytes())` 原地覆写外部文件。
  2. **恢复时任意文件写入（Path Traversal）**：在 `_restore_managed` 中，仅执行了 `entry.get("managed_path", "").lstrip("/")`，随后直接 `destination = self._managed_root / Path(managed_path)`。在 Windows 下，`lstrip("/")` 无法过滤带盘符的绝对路径（如 `C:\Windows\System32\...`），也无法过滤 `..\..\` 相对穿越路径。任何被篡改的 `.nmbak` 包或恶意 manifest 均可通过恢复接口在 `self._managed_root` 之外任意路径创建目录并写入文件。
- **触发条件**：
  - 库中 `pages.managed_original_ref` 存在绝对路径或脏相对路径；
  - 或者用户在 Console 恢复了一个被篡改或构造了穿越路径的 `.nmbak` 包。
- **建议修法**：
  在 `nmbak.py` 中引入严格的路径规范化安全断言（例如 `_validate_managed_relative_path(path_str: str) -> Path`）：
  1. 必须禁止绝对路径（`Path(p).is_absolute()` 或含有驱动器盘符）；
  2. 禁止包含 `..` 分量（`".." in Path(p).parts`）；
  3. 必须通过 `(root / rel).resolve().is_relative_to(root.resolve())` 校验；
  4. 在 `_page_original_refs`、`_verify_package` 及 `_restore_managed` 中强制校验，非法路径直接 fail-closed 抛出 `NmbakBackupError("BACKUP_CORRUPT", ...)`。

---

#### 2. `_promote_directory_merged` 非空目标合并非原子写，断电/崩溃会留下永久损坏文件
- **文件与行号**：
  [`src/infrastructure/sqlite/upgrade_legacy_layout.py:164-172`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/src/infrastructure/sqlite/upgrade_legacy_layout.py#L164-L172)
- **风险**：
  - 代码在向非空目标合并旧原图时使用 `shutil.copy2(source, destination)`：
    ```python
    if destination.exists():
        continue  # current layout wins: never overwrite
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    ```
  - `shutil.copy2` 是非原子的流式拷贝。如果拷贝数十兆的原图或大文件时进程被杀、崩溃、断电或发生磁盘满（ENOSPC），`destination` 会以 0 字节或截断状态残留在目标目录。
  - **严重后果**：因为第 167 行存在 `if destination.exists(): continue`，在下次重启应用重新运行迁移时，该半写文件会被判定为“当前布局已存在”，从而被永久跳过，导致用户受管原图永久损坏且失去迁移修复机会。
- **触发条件**：
  旧版本升级迁移大文件或大量原图过程中，发生系统断电、进程强制中止、磁盘空间耗尽等异常中断。
- **建议修法**：
  改用原子拷贝模式：先拷贝到同目录的隐藏临时文件（如 `destination.with_name(f".{destination.name}.tmp-{uuid4().hex}")`），写完后使用 `os.replace` 原子替换为目标文件；发生异常时在 `finally` 块中清理临时文件。确保目标路径要么不存在（下次可干净重试），要么完整就绪。

---

#### 3. `_ensure_automatic_backup` 判定逻辑导致后续数据永久失去自动备份覆盖
- **文件与行号**：
  [`src/bootstrap/core_service.py:5608-5614`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/src/bootstrap/core_service.py#L5608-L5614)
- **风险**：
  - 代码逻辑：
    ```python
    existing = [entry for entry in service.list_backups() if entry.get("verified")]
    if existing:
        _prune_automatic_backups(service, existing)
        return
    ```
  - 只要 `backups/` 目录下存在**任何一个**历史 verified 包（包括首启生成的初始包、甚至空库时手动导出的旧包），后续应用启动时此函数都会直接退出，不再执行任何备份。
  - 用户在日常使用中导入了数十本新书、执行了大量流水线处理产物后，如果 schema 没有发生 DDL 变更，系统**永远不会再生成任何新的自动备份**。一旦发生数据损坏，用户只能回滚到最初空旷的状态，严重违背数据安全防护预期。
- **触发条件**：
  用户在应用首次启动生成自动包（或手动备份）后，长期正常使用并持续导入新数据。
- **建议修法**：
  1. 如果定位是“首启防护”，应将函数及日志明确命名为 `_ensure_first_run_backup`，并在文档与 UI 中明确提示“仅在无任何备份时做冷启动保护，日常运行不自动轮转备份”；
  2. （推荐）如果需要真正的安全兜底，应引入变更感知或时间窗口（例如：当最新自动备份的时间距离当前超过 24 小时且数据库存在更新，或当前 `books`/`pages` 数量较备份有显著增长时），自动创建新的 `automatic` 轮转备份并触发 prune。

---

### 建议项（非阻塞）

1. **`_prune_automatic_backups` 备份类型隔离建议**：
   - 文件：[`src/bootstrap/core_service.py:5634-5658`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/src/bootstrap/core_service.py#L5634-L5658)
   - 目前将 `automatic`、`pre_migration`、`pre_restore` 混在一起按时间修剪至 5 个。若用户在恢复或迁移时连续出现多次操作，会产生多个 `pre_restore`，从而将原本唯一的 `automatic`（首启全量包）淘汰挤出。建议为 `pre_restore` 回滚点与常规自动备份分别设置保留配额，或保证至少保留一个基础自动备份。
2. **测试用例负向路径补全**：
   - 文件：[`tests/storage/test_nmbak_backup.py`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/tests/storage/test_nmbak_backup.py)、[`tests/infrastructure/test_upgrade_legacy_layout.py`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/tests/infrastructure/test_upgrade_legacy_layout.py)
   - 增加针对 `../` 路径穿越、绝对路径的打包/恢复拦截测试；
   - 增加迁移合并时目标文件半写（0 字节/坏文件）时的恢复测试。

---

### 已检查且判定无问题的点（避免误报）

1. **`_prune_automatic_backups` 不会删掉用户唯一存在的包**：
   - 判定：**OK**。
   - 依据：[`src/bootstrap/core_service.py:5648`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/src/bootstrap/core_service.py#L5648)。`_AUTOMATIC_BACKUP_KEEP = 5`，当包总数 `<= 5` 时，`excess <= 0` 立即返回；且 `manual` 类型的包在第 5642 行被严格过滤，永不被修剪。
2. **`_promote_directory_merged` 不会覆盖当前目标文件**：
   - 判定：**OK**。
   - 依据：[`src/infrastructure/sqlite/upgrade_legacy_layout.py:167-168`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/src/infrastructure/sqlite/upgrade_legacy_layout.py#L167-L168)。代码显式执行 `if destination.exists(): continue`，确保现有文件绝对优先。
3. **`catalog_store.py` 的 fail-closed 语义无法被目录替换绕过**：
   - 判定：**OK**。
   - 依据：[`src/infrastructure/resource_channel/catalog_store.py:314-320`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/src/infrastructure/resource_channel/catalog_store.py#L314-L320)。`rebind_namespace` 强校验 `existing is not None` 且 `existing == catalog_binding`，加上 `_assert_canonical_namespace_table` 校验和底层 handle 身份解析，单边替换或篡改均会直接抛出 `TypedResourceChannelError` 并拒绝服务。
4. **Console 恢复确认链不存在绕过二次确认的路径**：
   - 判定：**OK**。
   - 依据：[`ConsoleViewModel.cs:1890-1925`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L1890-L1925)。UI 界面唯一入口绑定在 `RequestRestoreBackupCommand`，该命令强制弹出 `_requestConfirm` 对话框，`RestoreBackupAsync` 为私有方法；Core 端 [`core_service.py:1988`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/src/bootstrap/core_service.py#L1988) 与 [`nmbak.py:224`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/src/infrastructure/sqlite/nmbak.py#L224) 均硬编码校验 `confirm_restore is True`，双向门禁严密。

---

### 推荐下一步

将上述 2 项必须修复项（`nmbak.py` 路径安全校验、`upgrade_legacy_layout.py` 原子写入）交由 **Antigravity** 或 **DSH** 在本分支（`task/REALUSE-DATA-SAFETY-1`）内进行修复并补全对应的负向单测；修复完成后重新提交独立审查。
