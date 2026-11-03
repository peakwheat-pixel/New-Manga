---
task_id: FEA-08
author: DSH（Lead/Integrator 直接实施 R5；impl-r4 Review 由 Codex 担任；DSH 不自审，impl-r5 Review 交 Codex 新独立上下文）
kind: handoff
delivery_scope: impl-r4 changes_requested（P0=0/P1=0/P2=5）处置；矩阵 H5 全量语义、事务旧集 hash 恢复核对、重复名双侧核验、门禁日志口径与 gates_capture SHA 登记；无生产代码改动
delivery_commit: 见 Task 卡 delivery_head（R5 证据 commit）
---

# FEA-08 R5 返修 Handoff（R5 → impl-r5 Review / DSH 集成）

## 1. 交付概览

- **目标**：处置 `doc/reviews/FEA-08-impl-r4.md`（Codex，changes_requested P0=0/P1=0/P2=5）全部 findings；不改变冻结 scope、不产生产代码。
- **写域**：`verification/FEA-08/**`、`doc/research/FEA-08-source-capability.md`、`doc/handoffs/FEA-08-*.md`、`doc/tasks/FEA-08.md`。产品路径零 diff（`src_changes=0`）。未 push。
- **实施者**：DSH（Integrator）。Review 独立性：impl-r5 由 Codex 新会话（未参与 R5）。

## 2. P2 处置（F08I4-001…005）

| Finding | 处置 | 证据 |
|---|---|---|
| **F08I4-001**（矩阵 H5 漏验还原等事实，与总驱动不一致） | `matrix.derive_ntfs` 补齐与 `run_all.verify_results` **逐字段一致**的全部 H5 必需事实：R1/R6b 还原 digest+restored 列表、R2 成员 digest/restored_count、R3 禁止永久 fallback、R4 保留+digest、R5/R5b 拒绝零 destructive、R6a 不重发、R6b 整数计数且执行后==恢复后、R9 逐文件 digest、R1/R2/R9 entries_poll。 | `matrix.py`、`run_all.py`；`results/h5_results.json` 现状全通过 |
| **F08I4-002**（晋升失败仍可丢旧证据/误报 rolled_back） | 晋升前对旧 Canonical 集做 **hash 快照**（文件 SHA / 目录树）；`promote_file`/`promote_dir` 在首次可见修改前登记 journal（含 backup 路径与 `old_moved/new_written` 状态）；失败先恢复本项（未恢复 backup 保留并报告）；`rollback()` **完整核对旧集 hash** 后才允许 `rolled_back=true`，未恢复 backup 列入 `backups_left_for_manual_recovery`；临时 `.new-*` 纳入异常清理。stage_evidence 改为写 staging 目录，fixtures_manifest 与 fixtures 同事务晋升。 | `run_all.py`、`stage_evidence.py`、`results/run_all_log.json` |
| **F08I4-003**（重复名歧义只查左侧） | `match_container` 对 dup names **两侧独立核验**：任一侧存在重复成员名即 candidate（含 occurrence 两侧字段）；新增非对称 fixture `book_asym_left/right.zip` 与场景 **M23**，并断言两个方向均为 candidate。 | `results/h6_results.json` M23 |
| **F08I4-004**（check 原始 FAIL 与交付 PASS 矛盾；摘要口径残留） | 在所有证据更新完成后**重新采集** gate 原始日志：`03-check.log` 现为 EXIT=0/PASS(3)/elapsed 1.2s 的真实成功运行（EV 与工作树一致时采集）；`gates.log` 明确“只记录本次采集运行、登记 commit 以 EV 表为准”，删除 SHA-only/旧 R3 口径残留；Task/Handoff/checkpoint 数值同步为新一次采集。 | `logs/gates-raw/03-check.log`、`logs/gates.log` |
| **F08I4-005**（prototype_hashes 中 gates_capture 实际 SHA 不符） | 在脚本全部定稿后**重新生成** `prototype_hashes.txt`（16/16 与工作区实际 SHA 一致），并重新采集关联门禁原始证据。 | `prototype_hashes.txt` |
| 计数口径 | fixtures 目录 **44 文件 = 43 内容 + evidence_manifest.json**（双 manifest 各 43 项）；证据总数 **72**；仅 `pin-verify.log` 为 SHA-only（余 71 文件均有 commit pin）。 | Task 卡、报告 §10 |

## 3. 门禁（R5；原始输出 `logs/gates-raw/**`，摘要 `logs/gates.log`）

- build：0 warning / 0 error；无过滤全量：**1292 passed / 0 failed / 57 skipped**（一次通过）。
- check.ps1：**PASS(3 warnings)**（EXIT=0，elapsed 1.2s，原始日志含 command/EXIT/cwd/shell/elapsed/env）；pins：**15/15**。
- 旧 FEA-06 四 PNG 未变；禁止范围 diff 空（src_changes=0）；代码路径清空类 API 调用=0。
- Canonical Evidence：**72 项**（71 文件 commit-blob/worktree/index-blob/干净 checkout 四方 + `pin-verify.log` 自身 SHA-256）；未 push。

## 4. 复现

```powershell
python G:\CODEX\New Manga.workspace\FEA-08\prototype\run_all.py                # 事务化 staging；失败恢复并核对旧集
python G:\CODEX\New Manga.workspace\FEA-08\prototype\h6_run.py --fixtures G:\CODEX\New Manga\verification\FEA-08\fixtures
python G:\CODEX\New Manga.workspace\FEA-08\prototype\gates_capture.py --phase1
python G:\CODEX\New Manga.workspace\FEA-08\prototype\gates_capture.py --phase2
git add verification/FEA-08
python G:\CODEX\New Manga.workspace\FEA-08\prototype\pin_selfcheck.py
```

## 5. 风险与遗留

1. 测试 flake 属仓库既有债务；R5 采集一次通过。
2. 产品牌面未决：AES ZIP 需 pyzipper(MIT)；IFileOperation sink 未实跑；USB/SMB/云无硬件；R8 真实取消不可无人值守触发（LIMITED(mocked)）。
3. 判定边界：重复名不同内容（M12）与任一侧重复名（M23）保持 candidate（保守）；生产实现需保留成员 identity/ordinal 与 occurrence 映射。
4. 本 Task 不产生产代码；SQLite/DB 不在范围；原生 200% DPI/a11y 无关。

## 6. 下一步

impl-r5 独立 Review（Codex 新会话）→ approved 后 DSH 集成验证（build/全量/check/pins/四 PNG/禁止 diff + 证据复核）→ 关闭 FEA-08（Resource Manifest/Closeout）→ 释放 FEA-09（引用源与导入）scope。**不 push。**
