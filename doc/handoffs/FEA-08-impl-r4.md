---
task_id: FEA-08
author: DSH（Lead/Integrator 直接实施 R4；Codex 已担任 impl-r3 Reviewer，DSH 不自审，impl-r4 Review 交 Codex 新独立上下文）
kind: handoff
delivery_scope: impl-r3 changes_requested（P0=0/P1=0/P2=5）处置；H5 语义门禁、事务化晋升、容器唯一映射正例、门禁元数据、计数勘误；无生产代码改动
delivery_commit: 见 Task 卡 delivery_head（R4 证据 commit）
---

# FEA-08 R4 返修 Handoff（R4 → impl-r4 Review / DSH 集成）

## 1. 交付概览

- **目标**：处置 `doc/reviews/FEA-08-impl-r3.md`（Codex，changes_requested P0=0/P1=0/P2=5）全部 findings；不改变冻结 scope、不产生产代码。
- **写域**：`verification/FEA-08/**`、`doc/research/FEA-08-source-capability.md`、`doc/handoffs/FEA-08-*.md`、`doc/tasks/FEA-08.md`（登记）。产品路径 `src/apps/experiments/tests/packaging/scripts/tools` 零 diff（`src_changes=0`）。未 push。
- **实施者**：DSH（Integrator）。Review 独立性：impl-r4 必须由未参与 R4 实现的独立上下文执行（Codex 新会话）。

## 2. P2 处置（F08I3-001…005）

| Finding | 处置 | 证据 |
|---|---|---|
| **F08I3-001**（H5 仍主要相信 verdict；还原 digest=false、启用永久 fallback、计数缺失 `None==None` 仍 PASS） | `matrix.derive_ntfs` 与 `run_all.verify_results` 增加 **H5 语义门禁**：R1/R6b `restored_digest_matches is True` 且 restored 全真；R2 成员 digest/restored_count；R3 不可回收分支 `fallback_rmdir_used is False`（禁止 fallback 永久 rmdir）；R4 保留+digest 不变；R5/R5b 拒绝且零 destructive；R6a 不重发；**R6b 三计数必须为整数且执行后==恢复后**；R9 逐文件还原 digest；R1/R2/R9 `entries_poll` 合法未超时。 | `run_all.py`、`matrix.py`；`results/h5_results.json` 现状通过强化断言 |
| **F08I3-002**（晋升移动/复制失败丢旧文件，journal 未登记即丢失） | `promote_file` 改为**先把新内容写临时文件**→登记 journal（含 backup 路径）→移旧到 backup→`os.replace` 原子换入；任一步失败先在 helper 内恢复本项再抛；`promote_dir` 同样先登记再移动、失败自恢复；`rollback` 逐项恢复并**核对恢复结果**，失败写入 `rollback_problems`。 | `run_all.py`（隔离注入失败探针由 Review 复核） |
| **F08I3-003**（自日志晋升在 journal 提交后，失败留新 Canonical + EXIT0） | 主流程重构：tmp 清理与自日志构建在晋升事务内完成；结果/日志/自日志在**同一事务**晋升；**全部成功后才 `commit_journal()`**；失败统一回滚（含 fixtures）并只写 workspace `run_all_failure.json`，不发布成功日志。 | `run_all.py`、`results/run_all_log.json` |
| **F08I3-004**（唯一内容成员改名被误拒） | `match_container` 改为按 occurrence 构建“内容 → 成员名多重集”映射：**唯一内容可跨名唯一对应**（改名/换位 exact）；**重复内容必须有相同 name/ordinal 锚**（锚一致 exact）；仅锚不一致才 `needs_confirmation`；重复名不同内容仍 candidate。新增正例 fixture `book_renamed_left/right.zip`、`book_dupanchor_left/right.zip` 与场景 **M21/M22**（均 exact + 断言）。 | `results/h6_results.json` M21/M22；fixtures 入库 |
| **F08I3-005**（check 原始日志缺耗时；解释器/环境仅 manifest 级） | `gates_capture.py` phase2 为 check 运行显式计时，并写入 `03-check.log` header：命令/EXIT/cwd/shell/captured_at/**elapsed_s**/**env（OS/shell/python 版本）**；重新采集并 re-pin。 | `logs/gates-raw/03-check.log` |
| 附带勘误 | 修正计数口径：fixtures 目录 **42 文件 = 41 内容 + evidence_manifest.json**（双 manifest 各 41 项）；证据总数 **70**；只有 `pin-verify.log` 为 SHA-only（其余 69 文件均有 commit pin）。 | Task 卡、报告 §10、本 Handoff |

## 3. 门禁（R4；原始输出 `logs/gates-raw/**`，摘要 `logs/gates.log`）

- build：0 warning / 0 error（EXIT=0）。
- 无过滤全量：**1292 passed / 0 failed / 57 skipped**（EXIT=0；本轮一次通过）。
- check.ps1：**PASS(3 warnings)**（EXIT=0，elapsed 3.4s，原始日志含耗时/环境）；pins：**15/15**。
- 旧 FEA-06 四 PNG 未变；禁止范围 diff 空（src_changes=0）；代码路径清空类 API 调用=0。
- Canonical Evidence：**70 项**（69 文件 commit-blob/worktree/index-blob/干净 checkout 四方 + `pin-verify.log` 自身 SHA-256）；未 push。

## 4. 复现

```powershell
python G:\CODEX\New Manga.workspace\FEA-08\prototype\run_all.py                # 全链（事务化 staging；失败回滚旧 Canonical）
python G:\CODEX\New Manga.workspace\FEA-08\prototype\h6_run.py --fixtures G:\CODEX\New Manga\verification\FEA-08\fixtures
python G:\CODEX\New Manga.workspace\FEA-08\prototype\gates_capture.py --phase1
python G:\CODEX\New Manga.workspace\FEA-08\prototype\gates_capture.py --phase2
git add verification/FEA-08
python G:\CODEX\New Manga.workspace\FEA-08\prototype\pin_selfcheck.py
```

## 5. 风险与遗留

1. **测试 flake（历史）**：R3 采集时曾出现项目既有偶发失败并重跑通过；R4 一次通过。属仓库既有测试稳定性债务，非本 Task 引入。
2. **产品牌面未决**：AES ZIP 需 pyzipper(MIT)（LIMITED(pyzipper)）；IFileOperation per-item sink 未实跑；USB/SMB/云无硬件；R8 真实取消不可无人值守触发（LIMITED(mocked)）。
3. **判定边界**：重复名不同内容（M12）仍按 candidate（保守）；生产实现需保留成员 identity/ordinal 与 occurrence 映射（报告 §5.1/§8）。
4. 本 Task 不产生产代码；SQLite/DB 不在范围；原生 200% DPI/a11y 无关。

## 6. 下一步

impl-r4 独立 Review（Codex 新会话）→ approved 后 DSH 集成验证（build/全量/check/pins/四 PNG/禁止 diff + 证据复核）→ 关闭 FEA-08（Resource Manifest/Closeout）→ 释放 FEA-09（引用源与导入）scope。**不 push。**
