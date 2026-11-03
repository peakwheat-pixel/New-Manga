---
task_id: FEA-08
author: DSH（Lead/Integrator 直接实施 R7；impl-r6 Review 由 DSH 派发的独立上下文子 agent 完成；DSH 不自审）
kind: handoff
delivery_scope: impl-r6 changes_requested（P0=0/P1=0/P2=5）处置；计数严格整数/范围、helper backup 报告、门禁假 PASS 路径、文档计数与字面 \n、M19 收紧；无生产代码改动
delivery_commit: 见 Task 卡 delivery_head（R7 证据 commit）
---

# FEA-08 R7 返修 Handoff（R7 → impl-r7 独立 Review / DSH 集成）

## 1. 交付概览

- **目标**：处置 `doc/reviews/FEA-08-impl-r6.md`（独立子 agent，changes_requested P0=0/P1=0/P2=5）全部 findings；不改变冻结 scope、不产生产代码。
- **Review 故障转移记录（透明）**：Codex 在 impl-r6 Review 中额度耗尽（重置 15:40，未产出报告）；ZCode 探测遇 HTTP 429（retry-after ≈29 分钟）；按 2026-10-31 裁决改由 **DSH 派发的新独立上下文子 agent** 完成 Review（未参与实现/返修，报告署名如实记录），报告 `doc/reviews/FEA-08-impl-r6.md`。
- **写域**：`verification/FEA-08/**`、`doc/research/FEA-08-source-capability.md`、`doc/handoffs/FEA-08-*.md`、`doc/tasks/FEA-08.md`。产品路径零 diff。未 push。
- **实施者**：DSH（Integrator）。impl-r7 由未参与 R7 的新独立上下文执行。

## 2. P2 处置（F08I6-001…005）

| Finding | 处置 | 证据 |
|---|---|---|
| **F08I6-001**（计数仍接受 bool/1.0/负数；matrix 与 run_all 分歧） | 顶层 `_is_int(v)=isinstance(v,int) and not isinstance(v,bool)`；`R2.restored_count` 必须严格整数且 ==1；`R1/R2/R9 entries_poll.iterations` 严格整数且 >=0；R6b 三计数严格整数且 >=0；matrix 与 run_all 使用同一规则。 | `matrix.py`、`run_all.py`；`results/h5_results.json` 现状通过 |
| **F08I6-002**（helper 自恢复失败 backup 漏报） | `promote_file`/`promote_dir` 异常分支记录 `_restore_entry` 返回的问题到 `HELPER_PROBLEMS`、把仍存在的 backup 加入 `KEPT_BACKUPS`；`rollback()` 的 problems 纳入 helper 问题；failure JSON `backups_left_for_manual_recovery` 合并 journal 与 `KEPT_BACKUPS`。 | `run_all.py` |
| **F08I6-003**（test 重试失败留下旧 values → phase2 假 PASS） | phase1 启动即删除旧 `phase1-values.json`（记录 `stale_values_removed`）；test 重试仍失败时先写 `status=aborted` + `failures` 再 `SystemExit`；phase2 校验 `status=='complete'` 与必需字段（`values_fresh`），不新鲜 → 结论 FAIL、非零退出；`gates.log` 追加 `phase1 status=`。 | `gates_capture.py`、`logs/gates.log`、`logs/gates-raw/phase1-values.json` |
| **F08I6-004**（文档 69→71；字面 `\n` 破坏 Markdown） | Task 三处计数改为 71 commit pin + 1 SHA-only；Task 与研究报告中的字面 `\n` 全部替换为真实换行（AC-2/AC-3 子条目、M20–M23 表格行恢复）。 | `doc/tasks/FEA-08.md`、`doc/research/FEA-08-source-capability.md` |
| **F08I6-005**（M19 期望宽：candidate/no_match 均可） | 收紧为 **仅 `candidate`**（保留 `assert_not_exact`）；matrix 与 run_all 同步；若产品接受 no_match 需另行裁决，本轮按 Task/报告“仅 candidate”口径执行。 | `run_all.py`、`matrix.py` |

## 3. 门禁（R7；原始输出 `logs/gates-raw/**`，摘要 `logs/gates.log`）

- build：0 warning / 0 error；无过滤全量：**1292 passed / 0 failed / 57 skipped**（一次通过）。
- check.ps1：**PASS(3 warnings)**（EXIT=0，elapsed 1.3s）；pins：**15/15**。
- 采集器：`phase1 status=complete failures=none`；`整体门禁：PASS`；7 份 raw 齐全。
- 旧 FEA-06 四 PNG 未变；禁止范围 diff 空（src_changes=0）；代码路径清空类 API 调用=0。
- Canonical Evidence：**72 项**（71 文件四方 + `pin-verify.log` 自身 SHA-256）；未 push。

## 4. 复现

```powershell
python G:\CODEX\New Manga.workspace\FEA-08\prototype\run_all.py
python G:\CODEX\New Manga.workspace\FEA-08\prototype\gates_capture.py --phase1   # 失败即非零退出且写 failure values
python G:\CODEX\New Manga.workspace\FEA-08\prototype\gates_capture.py --phase2   # 校验 phase1 新鲜度，失败非零
git add verification/FEA-08
python G:\CODEX\New Manga.workspace\FEA-08\prototype\pin_selfcheck.py
```

## 5. 风险与遗留

1. 测试 flake 属仓库既有债务；R7 采集一次通过。
2. 产品牌面未决：AES ZIP 需 pyzipper(MIT)；IFileOperation sink 未实跑；USB/SMB/云无硬件；R8 真实取消不可无人值守触发（LIMITED(mocked)）。
3. 判定边界：重复名不同内容（M12）与任一侧重复名（M23）保持 candidate；M19 仅 candidate。
4. 外部 Review 通道配额波动（Codex 15:40 恢复、ZCode 429）；已按裁决使用 DSH 独立子 agent，后续 Review 可继续同法或待外部恢复。

## 6. 下一步

impl-r7 独立 Review（未参与 R7 的新上下文）→ approved 后 DSH 集成验证 → 关闭 FEA-08（Resource Manifest/Closeout）→ 释放 FEA-09（引用源与导入）scope。**不 push。**
