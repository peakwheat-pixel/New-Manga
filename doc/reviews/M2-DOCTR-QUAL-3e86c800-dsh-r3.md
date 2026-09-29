---
reviewer: DeepSeek Harness (non-author, static)
imported_by: ZCode (M2-DOCTR-QUAL-PREFLIGHT owner, r5)
original_location: task-envs/M2-DOCTR-QUAL-work/dsh-review-r3.md
---

## verdict

**changes_requested**

（复核方式说明：本会话 `pwsh` 沙箱初始化失败 `SetNamedSecurityInfoW failed (Win32 5): grantWrite`，无法直跑 `git`；故改用 `.git/logs/HEAD`、交付内 `git-evidence.txt` 与文件原文取证。全程只读，未修改任何文件。）

## C1–C5 逐项判定

| 条件 | 判定 | 关键证据（本会话实读） |
|---|---|---|
| C1 r2 修订头登记 + git 证据 | **closed** | `.git/logs/HEAD:647` 确认 `3e86c800` 单提交、parent=`4d9d8d0c`；Handoff `line 9` 登记全 hash 并写明"单提交，parent `4d9d8d0c`；20 文件，含 5 个新增"；`git-evidence.txt:3331` 有 `## git diff --stat 4d9d8d0c..3e86c800 (r2 revision scope)`，`:3338–3345` 恰为 5 个新增文件（`141 +`/`75 +`/`34 +`/`3329 +`/`19 +`），`:3354–3355` 为 `-- requirements.txt requirements-dev.txt src/` 空 diff 的 production 零改动证明 |
| C2 计时口径统一 | **open** | 指定 4 点全部通过：Task 测试表 AC2 行 `line 60`（0.54 s / 0.38 s / 33.4–34.6 ms / 522.6 MiB + 显式冷启动标注）、Handoff `line 29`（同值）、baseline-summary §5 耗时列 `line 78`（23.31 s / 17.11 s，与 `results-*-cuda-seg05.json:35` 的 `elapsed_seconds` 逐值一致）、§8 `line 107`。**但仍有 3 处未同步的旧口径值**（详见 P2-N1） |
| C3 §5 归因措辞 | **closed** | `baseline-summary.md:89` 原文："脚本输出 `attribution_available: false`，不再据此计算归因计数（JSON 中残留的 `pure: 0` 为零分母占位，无观测含义）"，语义与要求一致；脚本侧 note（`eval_detection.py:427–433`）同为 "attribution is unavailable (not 'all pure')" |
| C4 UTC 时间戳 | **closed** | `adapter-spot-check-cuda.json:4` = `2026-09-29T16:42:08+00:00`；`consistency-and-sensitivity.json:75` = `2026-09-29T16:42:03+00:00`；`build_eval_manifest.py:31` `from datetime import datetime, timezone` + `:246` `datetime.now(timezone.utc)`；另 `smoke_adapter_check.py:142–144`、`eval_detection.py:403–405` 亦为 `timezone.utc`；既有 v2 manifest 硬编码日期已在 §8 披露 |
| C5 双侧空块判 match | **closed** | `smoke_adapter_check.py:100–106`：注释 "when both sides produce zero blocks, count AND coordinates agree trivially — that is a match, not a mismatch" + `both_empty` 分支置 `coords_match = True`，`:114` `record_match = count_match and coords_match` 归为 match |

## 新问题（按 P 级）

- **P2-N1（C2 未闭合，3 处残留旧计时值）**：①`doc/handoffs/M2-DOCTR-QUAL-PREFLIGHT-baseline.md:60` "GPU 冒烟：engine 4.2s / 稳态 38ms / 523 MiB ✓" 与同文件 `:29` "engine_build 0.54 s … 稳态 33.4–34.6 ms … 522.6 MiB" 同文档直接冲突（同一 `engine_build` 指标 4.2 s vs 0.54 s）；②`doc/tasks/M2-DOCTR-QUAL-PREFLIGHT.md:35`（AC2 验收条目）"~37 ms/region，峰值 523 MiB"；③`doc/STATUS.md:30` "RTX 5070 Ti 实测 ~37 ms/region / 523 MiB"。其中 ②③ 的 `~37 ms` 落在 §8 豁免标注的枚举值（"4.2 s/0.59 s/38 ms"）之外，不能依赖该豁免；①的 4.2 s/38 ms 虽被 §8 标注覆盖，但该处无就地指引（仅 Handoff `:10` 远端指向 §8）。修法：②③ 改为 `33.4–34.6 ms / 522.6 MiB`，①改为 `0.54 s / 0.38 s / 33.4–34.6 ms / 522.6 MiB` 或就地加"另一口径见 §8"。
- **P3-N2**：`baseline-summary.md:1` 标题仍为"（r2）"、`:3` 仍写"本文档为按 r1 修订后的 r2 版"，而 §8 已含 r3 段——版本标签未同步。
- **P3-N3**：`doc/tasks/M2-DOCTR-QUAL-PREFLIGHT.md:79` "Review：尚无。" 为模板占位（对比 `doc/templates/TASK.md:50`），与 `:77` 已记录的完整 review 轨迹自相矛盾。
- **P3-N4**：`git-evidence.txt:1–3304` 的 tree 清单无 commit 标注；实测其为 **r1（`4d9d8d0c`）tree**（`verification/M2-DOCTR-QUAL` 仅 8 条 `:1467–1474`，不含 r2 新增 5 文件），而 Handoff `:9` 让读者"以该清单为准"核对计数——建议加 `## git ls-tree <hash>` 标题避免误读。
- **P3-N5**：`doc/STATUS.md:14` 与 `:30` 自评"C1–C5 已在 r3 闭合"，与 C2 实测状态不符（作者自评超前）。
- **P3-N6**：r3 提交 `fc9bfd61` 未登记于 STATUS/Task/baseline-summary（自引用限制，属正常，待集成回填）。

## 不阻塞项与轨迹核对

- **N6 closed**：`eval_detection.py:355–358` 已加 "primary-layer statistic, repeated across the three layer" 注记并显式 `"layer": "block_coverage"`。
- **N7 部分完成**：`REBASELINE_PLAN.md:75` 已改 `in_review` ✓；Task `:9` reviewer 字段已更新（"r1 `changes_requested`、r2 `approved_with_conditions`"）✓；缺口仅为 P3-N3。
- **review 轨迹一致性**：STATUS `:14`/`:30` 与 Task `:77` 内容层一致（r1 `changes_requested`（24 项）→ r2 修订 `3e86c800`（20 closed / 2 partial / 0 open）→ r2 `approved_with_conditions`（C1–C5 + N6/N7）→ r3 条件闭合），与 `.git/logs/HEAD:646–648` 的提交序列吻合；缺失的仅是 r3 侧 hash 登记（P3-N6）。

## 判定说明与建议下一步

C1/C3/C4/C5 及 N6 已确凿闭合；**唯一阻塞项是 C2**——指定检查点全部达标，但"不得残留两组矛盾数字"的全文级要求被上述 3 处遗漏击穿（其中 1 处为 Handoff 内自我冲突、1 处位于交付入口文档 STATUS）。若裁定 §8 的"另一次含冷启动测量、口径不同"标注构成全局豁免，则 C2 可改判 closed 并整体转为 approved；本 Reviewer 按字面条件判 open。

建议下一步（交回作者 ZCode，纯文档修订，不需重跑）：

> 修订 `doc/handoffs/M2-DOCTR-QUAL-PREFLIGHT-baseline.md:60`、`doc/tasks/M2-DOCTR-QUAL-PREFLIGHT.md:35`、`doc/STATUS.md:30` 三处计时值至机器可读口径（engine_build 0.54 s / first_inference 0.38 s / 稳态 33.4–34.6 ms / 峰值 522.6 MiB），并顺手同步 P3-N2（标题与导语 r2→r3）、P3-N3（`Review：尚无` → 指向 review 轨迹）；提交后由 DeepSeek Harness 做 r4 定点复核（仅复验 C2 与三处 P3，不重开 AC1–AC4 事实层）。
