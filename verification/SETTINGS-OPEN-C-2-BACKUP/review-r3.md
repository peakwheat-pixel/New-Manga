# SETTINGS-OPEN-C-2-BACKUP 独立 Review r3（最终复审）

- Reviewer：`reviewer-settings-a`（非实现者）
- 审查头：**`b2e86a79e9378cde1d3d78e4852d70e424475b3f`**（C-2 handoff head）
- 实际链：`893c00fc` → `62421f538`（实现）→ `2f38ca41`（测试/证据）→ `29f65695`（docs pin）→ `c2d720bd`（r1 修复）→ **`657c18d4`（r2 修复 + Task 恢复）** → `eab7623f`（evidence pin）→ `b2e86a79`（Handoff head）
- Handoff `delivery_head`：`657c18d4a046c34de4e38885b9f5703a613c9d3d`；Task 按 lifecycle v1 不设 `delivery_head` 字段。
- 结论：**approved**。r2 的 Task 损坏 blocker 与 P2 已修复；Task 结构/AC/evidence/Closeout 完整，可 closeout。仅剩 3 项非阻塞文档/代码整洁 P2，建议关闭时顺手修。

## 1. Task 结构核验

Task `doc/tasks/SETTINGS-OPEN-C-2-BACKUP.md` 已恢复为 Task 而不是 Handoff：

- `kind: implementation`、`status: in_review`、`owner/reviewer/created/base_commit/depends_on` 齐全；
- `allowed_paths` 包含 Core/Rust/前端/tests、`doc/tasks`、`doc/handoffs`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、verification；
- AC1–AC5、测试要求表（80/2609/153/43/tsc/GUI）齐全；
- Canonical Evidence 13 行重新 pin 至 `657c18d4`（含 review-r1/r2、05 managed 截图）；
- Closeout Record 存在，`canonical_evidence_status: pending`、`resource_closeout_status: pending`，等待 Review 通过后 closeout。
- Handoff 仍是独立文件，`delivery_head: 657c18d4`，测试数字已更新为 **80 passed / 2609 / 43 files / screenshots 01–05**。

## 2. r2 P1/P2 复核

### P1（Task 文件损坏）— fixed

- 当前 Task 与 Handoff 已分离；Task 不再是一份 Handoff 副本。`git diff 29f..657` 可见恢复原始 Task 结构后再按 r2 更新。
- Task `status: in_review`；canonical/resource 均 pending；AC/evidence/Closeout 可供关闭。
- `STATUS` 已改为 **11 开 1 关（Plugin 待 C-3）**，当前 Task `in_review`。
- `TASK_LEDGER` 与 Task/Handoff 状态一致；`check.ps1` PASS（3 warnings）。

### P2 复核

| r2 P2 | 状态 | 核对 |
|---|---|---|
| Handoff 80/2609/43 + 01–05 | fixed | Handoff `:28-35` 已更新；`ui-test-frontend.log` 43/424；`core-pytest-targeted.log` 80 |
| STATUS 11/1 | fixed | `doc/STATUS.md:7-8` 已更新 |
| delivery_head | fixed | Handoff `:6` 为 `657c18d4`；实现范围 `893c00fc..657c18d4` |
| INCOMPLETE schema-mismatch 真实 rollback id | fixed | `restore()` 捕获 `BACKUP_RESTORE_INCOMPLETE` 后把字面 `rollback package: pre_restore` 替换为 `pre_restore['backup_id']`（`nmbak.py:227-241`） |
| `managed_files` 自授权额外成员 | fixed | `_verify_package` 以 `revision_refs` 为唯一 allowed 集合；`managed_files` 条目必须已 ∈ refs，否则 `BACKUP_CORRUPT`；`_restore_managed` 只写 refs（`:450-480`、`:512-530`） |
| 临时目录清理 | fixed（带代码整洁 P2） | `_remove_tree` 改 `shutil.rmtree(ignore_errors=True)`；隔离数据根 `backups/` 已无 `.nmbak-*` 临时目录 |

## 3. 独立验证

| 命令/检查 | 结果 |
|---|---|
| `python -m pytest tests/storage/test_nmbak_backup.py tests/core/test_core_backup_wire.py tests/core/test_core_cleanup_wire.py tests/core/test_core_service_settings.py -q` | **80 passed**（3.99s） |
| cargo（dev overlay + `M2RC1_PYTHON`） | **153 passed / 0 failed / 1 ignored / 12 filtered**（27.56s） |
| `npm --prefix apps/desktop/frontend test` | **43 files / 424 tests passed** |
| `tsc --noEmit` | exit 0 |
| `check.ps1` | PASS（3 warnings） |
| 工作区 | 干净（仅 `verification/P04/diagnostic_p22_22412...jsonl` 未跟踪；无 gen/ACL dirty） |
| GUI/数据 | 05 managed 往返；此前独立读取 managed 文件为 `ORIGINAL-MANAGED-BLOB`（21 bytes）；manifest `managed_file_count=1`、`revision_refs.region_id=null` |

- 全量 pytest 未独立重跑，证据 log 为 **2609 passed / 9 skipped / 3 既有失败**（detector 权重/时序 flaky；与本改动无关）。
- **NOT_RUN**：packaged sidecar E2E（缺 gitignored bundle，沿既有说明）。

## 4. 剩余非阻塞 P2（建议 closeout 时顺手修）

1. **Task 测试表 GUI 行仍写 `screenshots/01..04`**（Task `:65` 附近）；canonical 已含 `05-managed-restore.png`，建议改为 `01..05`。
2. **Task 运行记录仍有旧计数**：`Task` 的首次测试记录仍写“前端 42/424”“Core 9 + wire 7”；应改为 43/424、12 + 12（测试表已是 80）。
3. **`_remove_tree` 结构可读性**：`nmbak.py:533-540` 有两个 `except OSError`，且 `path.rmdir()` 缩进在第一个 except 内；当前行为由 `shutil.rmtree` 完成且测试通过，但建议简化为单一 `shutil.rmtree(path, ignore_errors=True)` 的 `try/except`，避免误导。
4. **Closeout 文案**仍是“待实现 + 独立 Review + GUI 烟测通过后关闭”；实现已完成，可改为“待 Review approved 后 closeout”。

以上均不影响产品验收；approved 后可 closeout。

## 5. 结论

**approved。**

- r2 的 Task 损坏 blocker 已修复；Task AC/evidence/Closeout 完整，状态 `in_review`，canonical/resource 仍 pending（正确）。
- 产品 P1/P2 修复均已独立复核，主路径和 managed 真实往返通过。
- 建议 Lead：先将 `review-r3.md` 加入 Task canonical evidence（或替换 review-r1/r2 行），再 Task → `done`、canonical/resource → complete、STATUS/LEDGER 更新；之后按裁决释放 **C-3 Plugin**。
