---
review_id: REALUSE-DATA-SAFETY-1-antigravity-r2
task: REALUSE-DATA-SAFETY-1
reviewer: Antigravity (agy CLI headless, conversation 9ef73697-d0df-47d4-9407-6c61d9755cce)
reviewer_independent: true
reviewed_by_implementer: false
round: 2
range: 8669388ae
verdict: PASS
captured_at: 2026-10-30T16:24:00+08:00
captured_by: DSH (verbatim, no edits to the review content)
---

# 独立复核（第 2 轮）：REALUSE-DATA-SAFETY-1

> 针对第 1 轮 FAIL_WITH_MUST_FIX 的三项修复（提交 `8669388ae`）的只读复核，由未参与实现的 Antigravity 给出，DSH 原样落盘。
> 第 1 轮报告见 `REALUSE-DATA-SAFETY-1-antigravity-r1.md`。

### 逐条复核结论

#### M1 备份路径穿越 —— `src/infrastructure/sqlite/nmbak.py`
- **结论**：**已修复**
- **依据与代码行号**：
  1. [`src/infrastructure/sqlite/nmbak.py:73-99`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/src/infrastructure/sqlite/nmbak.py#L73-L99) 新增 `_managed_relative_path`，以字面安全规则全面拦截空路径、绝对路径（`is_absolute()` / `/` / `\`）、Windows 盘符驱动器前缀（`^[A-Za-z]:`）以及任何包含 `..` 的路径遍历分量；
  2. [`src/infrastructure/sqlite/nmbak.py:102-117`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/src/infrastructure/sqlite/nmbak.py#L102-L117) 新增 `_resolve_within`，通过解析 `candidate.resolve()` 必须位于 `root.resolve()` 之下，彻底消除软链接（symlink）或 junction 逃出受管根的越界绕过路径；
  3. 已在打包阶段应用：[`src/infrastructure/sqlite/nmbak.py:419-434`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/src/infrastructure/sqlite/nmbak.py#L419-L434)（`_page_original_refs`）、[`src/infrastructure/sqlite/nmbak.py:457-472`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/src/infrastructure/sqlite/nmbak.py#L457-L472)（`_revision_refs`）及 [`src/infrastructure/sqlite/nmbak.py:494-523`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/src/infrastructure/sqlite/nmbak.py#L494-L523)（`_copy_managed_files`），写入 manifest 的路径统一规范化为 `relative.as_posix()`；
  4. 已在校验与恢复阶段应用：[`src/infrastructure/sqlite/nmbak.py:610-662`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/src/infrastructure/sqlite/nmbak.py#L610-L662)（`_verify_package` 对 `revision_refs`、`page_original_refs`、`managed_files` 全部通过 `_managed_relative_path` 拦截）以及 [`src/infrastructure/sqlite/nmbak.py:700-728`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/src/infrastructure/sqlite/nmbak.py#L700-L728)（`_restore_managed` 在写入目标前经过 `_resolve_within` 确认），恶意 manifest 在验证期直接抛出 `BACKUP_CORRUPT`。

---

#### M2 合并拷贝非原子 —— `src/infrastructure/sqlite/upgrade_legacy_layout.py`
- **结论**：**已修复**
- **依据与代码行号**：
  1. [`src/infrastructure/sqlite/upgrade_legacy_layout.py:130-149`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/src/infrastructure/sqlite/upgrade_legacy_layout.py#L130-L149) 新增 `_copy_file_atomically`：先拷贝到同父目录下的专属临时文件 `.{destination.name}.legacy-tmp-{os.getpid()}-{uuid.uuid4().hex}`，完全拷贝完成后通过 `os.replace(temp, destination)` 原子发布，并在 `finally` 块中通过 `temp.unlink(missing_ok=True)` 彻底清理残留；
  2. [`src/infrastructure/sqlite/upgrade_legacy_layout.py:191`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/src/infrastructure/sqlite/upgrade_legacy_layout.py#L191) 在 `_promote_directory_merged` 非空目标合并时，将原有的裸 `shutil.copy2` 替换为 `_copy_file_atomically`；
  3. 拷贝中断时 `destination` 绝对不会残留截断文件，保证下次启动时 `if destination.exists()` 判定准确，可干净重新迁移。

---

#### M3 自动备份判据 —— `src/bootstrap/core_service.py`
- **结论**：**已修复**
- **依据与代码行号**：
  1. [`src/bootstrap/core_service.py:5601-5619`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/src/bootstrap/core_service.py#L5601-L5619) 定义 `_AUTOMATIC_BACKUP_REFRESH_HOURS = 24`，并新增 `_package_age_hours` 函数，对缺失、空或格式损坏的时间戳按 `math.inf`（陈旧）处理；
  2. [`src/bootstrap/core_service.py:5640-5680`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/src/bootstrap/core_service.py#L5640-L5680) 在 `_ensure_automatic_backup` 中优化判据：
     - 空库（`books == 0`）跳过备份并只触发修剪；
     - 没有任何 verified 包时生成首启包；
     - 最新 verified 包存在时，若其年龄 `age_hours >= 24`，自动生成轮转备份（标注 `scheduled rotation: newest verified package is X.Xh old`）；
     - 最后始终调用 `_prune_automatic_backups` 维持最新 5 个自动包上限，manual 包永不受影响。

---

### 总结论

**PASS**

所有上一轮提出的 3 项必须修复项（M1/M2/M3）均已完整且严密地修复，新增针对性测试（10 例，涉及路径穿越拒绝、原子拷贝中断恢复、陈旧包轮转）全部通过，未引入任何新绕过路径或回归风险。

---

### 新增问题

**无新增问题**。代码无阻塞性缺陷。

---

### 已确认无问题的点

1. **无路径逃逸与盘符绕过漏洞**：
   - Windows 盘符驱动器相对路径（如 `C:foo.png`）和绝对路径（`C:/...`、`\\...`）均被 `_managed_relative_path` 的正则与分量检查阻断；
   - 符号链接逃逸被 `_resolve_within` 的 `.parents` 包含关系校验严密拦截；
   - 恢复流程对 manifest 中的所有路径做预校验，被篡改的包在 `_verify_package` 阶段直接拒绝，无法到达解压写入阶段。
2. **原子文件合并不会跨卷崩溃**：
   - 临时文件使用 `destination.with_name(...)` 创建在与目标文件相同的目录下，严格保证与目标位于同一个文件系统卷上，确保 Windows/Linux 环境下的 `os.replace` 具有原子性。
3. **测试覆盖充分**：
   - `python -m pytest tests/storage/test_nmbak_backup.py tests/infrastructure/test_upgrade_legacy_layout.py tests/infrastructure/test_nmbak_startup_backup.py -q` 运行全部 47 个用例（含新增的 10 个用例）均 **PASS**；
   - 包含针对 `page_original_refs` 绝对路径创建、`..` 穿越创建、篡改包恢复拦截、磁盘满（ENOSPC）中断下无半写文件残留、陈旧包轮转及空库不轮转的完整正反向覆盖。
