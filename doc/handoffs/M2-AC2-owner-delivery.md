# Handoff — M2-AC2 Data Integrity Acceptance

- Owner: ZCode（本会话亲自实现，用户授权 2026-09-28）
- Task: `doc/tasks/M2-AC2.md`（`ready / M2_AC2_DATA_INTEGRITY_RELEASED`；纯验收，产品代码零改动）
- Base / release: `61f9db9b` / `01af7732`
- Branch / worktree: `agent/zcode/M2-AC2-data-integrity` / `G:/CODEX/New Manga.worktrees/M2-AC2-zcode`
- Status: delivered（等 DSH 非作者 Review；Integrator=Codex 新会话，保持 Owner≠Integrator）

## 交付物

| 文件 | 说明 |
|---|---|
| `tests/m2_acceptance/test_data_integrity.py` | 新增验收模块，10 场景覆盖 AC1–AC5 |
| `verification/M2-AC2/verification-results.md` | 两级验证原始日志（-v 逐场景 + 全套回归） |
| `doc/tasks/M2-AC2.md` | 状态推进 delivered + AC3 语义澄清 |

## AC 判定表（全部实测）

| AC | 场景 | 判定 |
|---|---|---|
| AC1 | source_hash == sha256(源字节)；源目录零写入、字节不变；duplicate SKIP 不产生第二 page/第二 managed copy | **PASS**（2 场景） |
| AC2 | managed 副本字节一致且不在用户源目录内；删源文件后 managed 仍权威可读；managed 缺失经 page_catalog 显式检出（`invalid`≠`ok`，不静默伪造） | **PASS**（2 场景） |
| AC3 | save_manual_translation → 新 revision + `manual_edited` + RegionText 层 `translation_locked`；pipeline OCR 真跑（mock provider 绑定 + 真实 PNG）后 `edited_translation` 人工译文原样保留 | **PASS**（1 场景，含语义澄清见下） |
| AC4 | page_locked → plan 全 `skip_lock` 且零 StepRun；region_locked（M2-P1 N2 时序）→ OCR `LOCK_CHANGED` 零写；pinned revision 在 CleanupService.run() 后保持；restore_revision → current 指回恢复内容、产生带 `restored_from_revision_id` 溯源的新 revision | **PASS**（4 场景） |
| AC5 | 同 data root 重装配后 hash/Lock/pin/current/人工文本全部保持；restored page lock 仍约束 planner | **PASS**（1 场景） |
| AC6 | 两级 pytest EXIT 0（10 passed / 14 passed）；`git diff --check` EXIT 0；FAIL/BLOCKED/NOT_RUN 无 | **PASS** |

## 验证命令（worktree 根目录，$py=TASK-012-py312）

1. `$py -m pytest tests/m2_acceptance/test_data_integrity.py -v` → **10 passed**，EXIT=0
2. `$py -m pytest tests/m2_acceptance -q` → **14 passed**（M2-AC1 4 + 本模块 10，零回归），EXIT=0
3. `git diff --check 61f9db9b..<delivery-head>` → EXIT=0

## 实现过程中的语义发现（供 Reviewer 重点核对）

1. **双层锁语义（Owner 澄清，已写入 Task AC3）**：`RegionText.translation_locked`（内容保护锁，`save_manual_translation` 置它，`apply_machine_translation` 的 PermissionError 由它触发）与 Region 顶层 `region_locked/translation_locked`（pipeline 写守卫读的列）是**两个不同的字段**。OCR 链不受 text 层锁拦截——OCR 结果写入 `ocr_text` 并推进 current 是预期行为；人工译文承诺体现为 `edited_translation` 不被清除。Task AC3 原措辞（"current 指针保持在人工版本"）基于 Owner 语义误解，已按实测语义修正。
2. **`core_service._PassthroughImageDecoder` 签名缺陷（DSH r2 P3-3 的实证）**：sidecar 的 stub decoder 传 `format=` 给 `DecodedImage`（真实字段 `width/height/mime_type`）→ 任何经该 stub 的导入都会 TypeError。M2-IPC1 命令面不含 import 所以未受影响；本验收按 assembly 的 adapter-injection（I1-AC4）自备 `_AcceptanceDecoder` 绕开。**登记为后续修复项**：未来 core_service 扩 ImportPages 命令前必须替换该 stub。
3. **region 锁场景时序**：plan 前置锁会使 planner 直接跳过（无 StepRun 可断言）；按 M2-P1 N2 时序（plan 后、execute 前置锁）才能真实触达写守卫，实测 `LOCK_CHANGED` + 零写。
4. **image-source 前置**：pipeline OCR 需要真实可解码 PNG（production crop/decode 管线），合成场景用 `acceptance_bridge.synthetic_page_png`（M2-AC1 先例）。
5. **`RevisionText` 快照契约**：revision snapshot 含 `edited_translation` 全字段（`snapshot_state`），restore 产生带 `restored_from_revision_id` 溯源的新 revision——人工文本在 restore 语义下不丢失。

## NOT_RUN / BLOCKED

无。
