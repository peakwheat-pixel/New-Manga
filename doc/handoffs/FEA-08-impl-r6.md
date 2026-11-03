---
task_id: FEA-08
author: DSH（Lead/Integrator 直接实施 R6；impl-r5 Review 由 Codex 担任；DSH 不自审，impl-r6 Review 交 Codex 新独立上下文）
kind: handoff
delivery_scope: impl-r5 changes_requested（P0=0/P1=0/P2=4）处置；矩阵 R6b restored 列表、计数拒绝 bool、backup 移出 OUT/失败保留、门禁采集器失败感知；无生产代码改动
delivery_commit: 见 Task 卡 delivery_head（R6 证据 commit）
---

# FEA-08 R6 返修 Handoff（R6 → impl-r6 Review / DSH 集成）

## 1. 交付概览

- **目标**：处置 `doc/reviews/FEA-08-impl-r5.md`（Codex，changes_requested P0=0/P1=0/P2=4）全部 findings；不改变冻结 scope、不产生产代码。
- **写域**：`verification/FEA-08/**`、`doc/research/FEA-08-source-capability.md`、`doc/handoffs/FEA-08-*.md`、`doc/tasks/FEA-08.md`。产品路径零 diff。未 push。
- **实施者**：DSH（Integrator）。Review 独立性：impl-r6 由 Codex 新会话（未参与 R6）。

## 2. P2 处置（F08I5-001…004）

| Finding | 处置 | 证据 |
|---|---|---|
| **F08I5-001**（矩阵漏验 R6b `restored` 列表） | `matrix.derive_ntfs` 的 R6b 断言补齐：`restored_digest_matches is True` + `restored` 非空 + 每项 `restored is True`（与 `run_all.verify_results` 一致）。 | `matrix.py`、`results/h5_results.json` |
| **F08I5-002**（恢复失败 backup 漏报、二次启动删除旧 backup） | `BACKUP` 从 `out/_promote_backup` 移到 `workspace/FEA-08/backup/promote-<时间戳>-<pid>`（`out/` 每次启动会清空，故原位置会删掉未恢复备份）；失败 JSON 增加 `backup_dir_kept`（实际保留目录）+ `backups_left_for_manual_recovery`；恢复失败明确保留 backup 并报告。 | `run_all.py`；成功路径 backup 目录已清理 |
| **F08I5-003**（整数计数校验接受 JSON boolean） | 新增 `_is_int(v) = isinstance(v, int) and not isinstance(v, bool)`；matrix 与 run_all 的 R6b 三计数、entries_poll iterations 均改用该判定（`True`/`False` 不得冒充计数）。 | `matrix.py`、`run_all.py` |
| **F08I5-004**（采集器失败仍总结“全部通过”） | `gates_capture.py`：phase1 汇总 build/test/pins/四 PNG/禁止 diff/安全搜索失败项到 `phase1-values.json["failures"]`，**任一失败 phase1 非零退出**；phase2 计算 `gates_ok`（phase1 无失败 + check PASS），结论按事实写 PASS/FAIL，**失败时非零退出**；`gates.log` 末尾追加“整体门禁：PASS/FAIL；phase1 failures=…”。 | `logs/gates.log`、`logs/gates-raw/phase1-values.json`（failures=[]） |

## 3. 门禁（R6；原始输出 `logs/gates-raw/**`，摘要 `logs/gates.log`）

- build：0 warning / 0 error；无过滤全量：**1292 passed / 0 failed / 57 skipped**（一次通过）。
- check.ps1：**PASS(3 warnings)**（EXIT=0，elapsed 1.3s）；pins：**15/15**。
- 采集器汇总：`phase1 failures=none`；`整体门禁：PASS`；7 份 raw 齐全（command/EXIT/cwd/shell/elapsed）。
- 旧 FEA-06 四 PNG 未变；禁止范围 diff 空（src_changes=0）；代码路径清空类 API 调用=0。
- Canonical Evidence：**72 项**（71 文件四方 + `pin-verify.log` 自身 SHA-256）；未 push。

## 4. 复现

```powershell
python G:\CODEX\New Manga.workspace\FEA-08\prototype\run_all.py
python G:\CODEX\New Manga.workspace\FEA-08\prototype\gates_capture.py --phase1   # 失败即非零退出
python G:\CODEX\New Manga.workspace\FEA-08\prototype\gates_capture.py --phase2   # 按 gates_ok 退出
git add verification/FEA-08
python G:\CODEX\New Manga.workspace\FEA-08\prototype\pin_selfcheck.py
```

## 5. 风险与遗留

1. 测试 flake 属仓库既有债务；R6 采集一次通过。
2. 产品牌面未决：AES ZIP 需 pyzipper(MIT)；IFileOperation sink 未实跑；USB/SMB/云无硬件；R8 真实取消不可无人值守触发（LIMITED(mocked)）。
3. 判定边界：重复名不同内容（M12）与任一侧重复名（M23）保持 candidate（保守）。
4. 本 Task 不产生产代码；SQLite/DB 不在范围；原生 200% DPI/a11y 无关。

## 6. 下一步

impl-r6 独立 Review（Codex 新会话）→ approved 后 DSH 集成验证 → 关闭 FEA-08（Resource Manifest/Closeout）→ 释放 FEA-09（引用源与导入）scope。**不 push。**
