---
task_id: FEA-08
author: ZCode CLI R2 session（脚本/证据改造；2026-11-03 10:08–10:39 额度耗尽中断）+ DSH（Integrator 收口：字段自洽修正、全链重跑/staging、EV re-pin、门禁、Handoff）
kind: handoff
delivery_scope: impl-r1 changes_requested（P1=2/P2=9）处置 + 证据全链重出/re-pin；无生产代码改动
delivery_commit: 7b176be6a
---

# FEA-08 R2 返修 Handoff（R2 → impl-r2 Review / DSH 集成）

## 1. 交付概览

- **目标**：闭合 impl-r1（`doc/reviews/FEA-08-impl-r1.md`，changes_requested P0=0/P1=2/P2=9）的两个 P1、逐项处置 9 个 P2；不改变已成立技术结论、不扩大产品范围、不产生产代码。
- **交付 commit**：`7b176be6a`（证据全链重出）；Canonical Evidence **51 项** re-pin @该 commit（`gates.log` 为首见于登记 commit 的文件，按 SHA-256 pin）。
- **写域**：`verification/FEA-08/**`、`doc/research/FEA-08-source-capability.md`（`doc/tasks/FEA-08.md` 在登记 commit 更新）。产品路径 `src/apps/experiments/tests/packaging/scripts/tools` 零 diff（`src_changes=0`）；未 push。
- **实施分工（如实登记）**：ZCode R2 session 完成 9 个脚本/证据改造与首轮全链（10:08–10:39），随后触及 5 小时额度上限（13:13 重置）中断、未提交；DSH 以 Integrator 身份收口：修复 2 个自洽缺陷、重写 `run_all.py` 为「双生成 fixtures → staging → H4/H5/H6(对入库 fixtures)/矩阵 → verdict 校验 → 结果/日志 staging → tmp 清理」、全链重跑、EV re-pin、门禁、Handoff。impl-r2 Review 必须由未参与实现的独立上下文执行。

## 2. P1 处置

| Finding | 处置 | 证据 |
|---|---|---|
| **F08I1-001**（folder fixtures 未入库，M8/M9 不可复现） | `folder_v1/p1-3.png`、`folder_v2/p1,p2renamed,p4.png` 已入库 `verification/FEA-08/fixtures/`；`make_fixtures.py` 逐成员 `reg()` + 生成后自校验；`stage_evidence.py` 目录递归生成 `results/fixtures_manifest.json`（33 项）与 `fixtures/evidence_manifest.json`；**H6 直接对入库 fixtures 运行**（`h6_results.json` 记录 `fixtures_root=G:\CODEX\New Manga\verification\FEA-08\fixtures`、来源 `env FEA08_FIXTURES`）；M8M9 结果为 `needs_confirmation`（folder_membership+bytes_sha256）。复现：`python ...\h6_run.py --fixtures ...\verification\FEA-08\fixtures`（不依赖 tmp）。 | `results/fixtures_manifest.json`、`fixtures/evidence_manifest.json`、`results/h6_results.json`、EV-F08-35..40（folder 成员） |
| **F08I1-002**（9/36 pin 不能按 git-cat-file 复现） | 口径统一为 **Git blob 字节（LF）SHA-256**（复现 `git cat-file -p <commit>:<path>`，工作树 `Get-FileHash` 一致）；集成处置 `.gitattributes` 增 `verification/FEA-08` 文本证据 `text eol=lf`（DSH 提交 `07724b88d`）；全部脚本文本输出统一 `newline='\n'`；`pin_selfcheck.py` 做 blob/worktree/Task 表/干净 checkout 四方校验（`logs/pin-verify.log`）。51/51 通过。 | `logs/pin-verify.log`、Task 卡 Canonical Evidence（51 项 @`7b176be6a`）、`.gitattributes` 规则 |

## 3. P2 处置（F08I1-003…011 + review §9）

| Finding | 处置 | 证据 |
|---|---|---|
| **F08I1-003**（S5 盲区字段/矩阵单值 PASS） | S5a/S5b `detail`：`classification=undetected_mixed`、`mixed_digest_risk=true`、`outcome_protocol=digest_returned`、评估 `outcome=unavailable`、`outcome_evaluation=LIMITED(mmap-blind)`；行级 `mixed_digest_risk_field_consistent=true`；矩阵 NTFS-H4 状态改双态 `PASS(strict) / UNAVAILABLE(mmap-blind)`；h4 `production_constraint` 与报告写为 **strict-only 硬约束**。 | `results/h4_results.json`、`results/capability_matrix.json`、报告 §3.3-2 |
| **F08I1-004**（S2 win32、S5 mtime 字段） | S2 `writer_attempts.write_open=blocked(win32=32)`（`e.args[0]`）；S5 `mtime_changed` 由读前/读后真实 `FileIdentity` 计算（实测 false = 盲区证据）；`outcome_for` 与 `mixed_digest_risk` 对齐。 | `results/h4_results.json` S2/S4/S5 |
| **F08I1-005**（H5 R2 时序、harness exit） | `recycle_lab.wait_for_entries()` 有界轮询（500ms × 12，`entries_poll` 记录）；`h5_run.py` 期望 PASS 场景 FAIL 时 `sys.exit(1)`；`run_all.py` 二次校验 results JSON verdict。 | `results/h5_results.json`（`entries_poll`）、`logs/h5_run.log`（gate 行）、`logs/run_all.log` |
| **F08I1-006**（H5 分支证据强度） | R6b 记录 `destructive_calls_before/after_execute/after_recovery`（5→5）+ `no_destructive_reissued=true`；R5b 用 `GetFileAttributesW`/类型实测（`current_type=directory`、`current_identity_note`）；R3 记录 `fallback_rmdir_used=false` 与 mock 失败注入（ret=0x79 → `keep_at_origin`，标 LIMITED(mocked)）。 | `results/h5_results.json` R3/R5b/R6b |
| **F08I1-007**（H6 自比较/AES/边界） | M12 两路径独立副本（`book_dup_copy.zip`，独立构造固定时间戳）；M13 独立第二份 ZipCrypto 密文（`book_enc_zipcrypto_copy.zip`，密文逐位不同）；M15 独立第二份 AES-256 PDF 密文（`doc_enc_copy.pdf`，/ID 时间戳不同）；自读对照显式标 `self-consistency`；AES ZIP 矩阵标 `LIMITED(pyzipper)`；新增 dhash 邻界 M17（距离 10→candidate）/M18（距离 11→no_match）fixture 并入库。 | `results/h6_results.json` M12/M13/M15/M17/M18、新 fixture 的 EV 行 |
| **F08I1-008**（矩阵硬编码 PASS/无逐格现状） | `matrix.py` 逐格 `current`/`needed`；NTFS 行由 h4/h5/h6 结果推导/校验（推导不满足即降级）；H4/H5 未逐格式实测格标 `LIMITED(inferred: volume-level, format-agnostic)`。 | `results/capability_matrix.{json,md}`、报告 §6 |
| **F08I1-009**（门禁记录缺失） | Task 卡新增「门禁记录」表（命令/head/EXIT/build/全量/check/pins/四 PNG/禁止 diff/pin 自校验/安全边界）；原始输出 `logs/gates.log`。 | Task 卡门禁记录、`logs/gates.log` |
| **F08I1-010**（tmp 清理不一致） | `run_all.py` 末尾实际清理并记录 `tmp_removed`/`tmp_remaining=[]`；当前 `workspace\FEA-08\tmp` 为空。 | `results/run_all_log.json` |
| **F08I1-011**（manifest 指针/脚本口径） | `h6_run.py` 用 `resolve_fixtures_manifest()` 只指向实际存在文件（现为 `verification/FEA-08/results/fixtures_manifest.json`）；Task/报告写清「15 个登记脚本；run_all 执行 5 个核心场景步骤 + staging；stage_evidence/pin_selfcheck 独立」。 | `results/h6_results.json`、`prototype_hashes.txt`、报告 §2/§10 |
| review §9（probe_env 冒烟误读） | `probe_env.py` 改用 `pdfium.PdfDocument.new()` 并做版本探测。 | `prototype_hashes.txt`（probe_env 新 SHA） |

## 4. 门禁（R2 交付实测；原始输出 `verification/FEA-08/logs/gates.log`）

- `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` → **0 warning / 0 error**，EXIT=0。
- 无过滤全量 `dotnet test ... --no-build --settings ...` → **1292 passed / 0 failed / 57 skipped**（逐程序集 21/38/51/253/117/31/128/653；skip 0/0/28/0/0/0/22/7），EXIT=0。
- `check.ps1` → **PASS(3 warnings)**；`verify_pins.ps1` → **15/15 PASS**。
- 旧 FEA-06 四 PNG 未变；禁止范围 diff 为空（`src_changes=0`）；未 push。

## 5. 复现命令

```powershell
python G:\CODEX\New Manga.workspace\FEA-08\prototype\run_all.py        # 全链（会重写 verification/FEA-08 证据）
python G:\CODEX\New Manga.workspace\FEA-08\prototype\h6_run.py --fixtures G:\CODEX\New Manga\verification\FEA-08\fixtures
git add verification/FEA-08
python G:\CODEX\New Manga.workspace\FEA-08\prototype\pin_selfcheck.py  # 生成 logs/pin-verify.log
```

## 6. 风险、遗留与建议 Review 关注点

1. **Review 独立性**：R2 由 ZCode session + DSH 收口完成；impl-r2 Review 必须由独立上下文执行（Codex，或 D-9 独立子 agent；不得由 DSH 主会话或 ZCode R2 session 自审）。
2. **证据可复现边界**：ZIP/PDF 容器含时间戳，跨运行不逐位复现（`evidence_manifest.json` 的 `deterministic_rebuild` 以「入库原件 vs 另一次生成」对照，22/33 为真；图片类全部可确定性重建）。Canonical pin 只承诺「该 commit 的字节可复现」。
3. **产品牌面未决**：AES ZIP 读取需 pyzipper(MIT)（README 登记 LIMITED(pyzipper)，待产品裁决）；IFileOperation per-item sink/flags 未实跑（SHFileOperationW 承载）；USB/SMB/云无硬件；H5 R8 用户取消无人值守不可触发（LIMITED(mocked)）。
4. **本 Task 边界**：不产生产代码；测试 SQLite/DB 不在范围；原生 200% DPI/a11y 与 FEA-08 无关。
5. 建议 impl-r2 Review 重点：P1-001 从入库证据独立复跑 M8M9；P1-002 全部 51 项按 `git cat-file` + 干净 checkout 复现；9 个 P2 的「字段/证据是否真实落地」而非文字；H5 连续复跑稳定性（R2 时序）；门禁独立复跑。

## 7. 下一步

impl-r2 独立 Review（DSH Appointment）→ approved 后 DSH 集成验证（build/全量/check/pins/四 PNG/禁止 diff + 证据复核）→ 关闭 FEA-08 → 释放 FEA-09（引用源与导入）scope。**不 push。**
