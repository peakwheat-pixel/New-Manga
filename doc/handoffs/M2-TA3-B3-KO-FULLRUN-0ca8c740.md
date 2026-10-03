---
task_id: M2-TA3-B3-KO-FULLRUN
author: ZCode
recipient: DeepSeek Harness（非作者 Review）→ 编排会话代行 Codex（集成）
base_commit: 73252798
delivery_head: 0ca8c740
status: delivered
---

# Handoff：M2-TA3-B3-KO-FULLRUN（ko 8 case 全量补跑与缺口关闭）

## 交付结果

- **owner 分支 tip `0ca8c740`**（线性链 `73252798 → 24a89d7d(release) → cd76cac0(driver 硬化+invalid-env 归档) → 7aee808d(双 driver 处置) → 0ca8c740(交付)`）。
- 变更路径（全部在允许修改面内）：`verification/M2-TA3-B/ko-fullrun-report.md`（新增主报告）、`verification/M2-TA3-B/phase2/ko-fullrun/**`（9 pass summaries + budget-ledger + determinism + invalid-env 归档目录）、`verification/M2-TA3-B/quality-thresholds.md`（§5 known-limitation 注）、`verification/M2-TA3-B/ko-rerun-report.md`（§7 裁决记录回填）、`doc/tasks/M2-TA3-B3-KO-FULLRUN.md`（交付记录）、`experiments/M2-TA3-B/ko_fullrun_driver.py`（硬化：`runner_env()` + `ocr_stack_ok()`）、`doc/handoffs/`（本文件）。
- AC 逐项判定见 Task 交付记录与主报告 §10：AC1/AC2/AC4/AC5 PASS，AC3 PASS（CER 部分 NOT_AUTOMATED 按任务书预留口径如实登记）。
- **核心成果**：8/8 case 全链 export OK（首跑 0/8 可用）；F1 关闭（detect 5/5 同值×全链组合）；F2 关闭（三页页级实测）；预算 950,954/2,200,000（43.2%）；K02 相似度 remote 轨 FAIL（min=0.0 合法重译形态，按裁决登记 known-limitation）。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 全量 | driver A 队列自动执行（K07→K09→K10→K01→K02 main→K02 rerun→similarity） | worktree HEAD `0ca8c740` 之前的 `7aee808d` 树；T1.1.1-impl-py312 + OCR venv PYTHONPATH 注入 | PASS（9 pass 落盘） | `phase2/ko-fullrun/summaries/qual-*.json`、`budget-ledger.json`、`driver-result.json`（外部树 logs/） |
| AC2 关闭确认 | 对照 TILING qualification 先例 region 数 + KO-RERUN/首跑状态 | 同上 | PASS | 主报告 §2/§3 对照表 |
| 相似度 | `ko_rerun_similarity.py --case K02 --determinism-track remote` | 同上 | FAIL（按裁决口径登记） | `phase2/ko-fullrun/determinism/K02-similarity.json` |
| AC5 计量 | `--meter-translation` 逐 pass | 同上 | PASS | ledger entries 9 条（坏轮 6+1 条已清除并留 `invalidated_entries_note`） |
| key 零明文 | grep 交付树无 key 内容；`dump_json` scrub | 同上 | PASS | （grep 由 Reviewer 复现） |
| 禁改面 | `git diff --name-only 73252798..0ca8c740` 无 src/tests/contracts/packaging/apps | 同上 | PASS（Reviewer 复核项） | — |

**NOT_RUN / 边界（如实）**：K11/K19 不在名单（任务书 AC1 明文）；K01–K10 的 CER NOT_AUTOMATED（无 SVG GT 物）；K01 run1=FAILED steps 全绿（归因未定，非阻塞缺陷）；K10 单 region translate typed 保空（fail-closed 正确）。

## 接收方式

- 分支 `agent/zcode/M2-TA3-B3-KO-FULLRUN` / worktree `G:/CODEX/New Manga.worktrees/M2-TA3-B3-KO-FULLRUN-zcode` / delivery_head `0ca8c740`。
- Reviewer 输入：主报告 `verification/M2-TA3-B/ko-fullrun-report.md` + Task 交付记录 + 本文件；外部证据树 `G:/CODEX/New Manga.task-envs/M2-TA3-B/ko-fullrun-{pixels,logs}/`（logs 含 driver-restart2.log 双 driver 冲突转录与全部 case log）。
- 复现：主报告 §9（driver 断点续跑幂等——summary+ledger 双在即 skip，重跑只产生 resume-skip 不重烧预算）。
- **Reviewer 特别核查点**：①invalid-env 归档目录中 6 份无效 summary 的 `run1.steps` 错误码与有效轮判别基线（报告 §1.1 三条）；②有效 summary 的 OCR 非空率抽查（建议 K02/K05 全绿样本 + K07 最大页）；③budget-ledger 的条目完整性（9 条 vs 已清除的 7 条污染）。

## 下一任务建议（必填）

- Task ID / 标题：无新 Task（本 Task 进入 review→集成收口；候选池见下）。
- 推荐 Agent / Reviewer：DSH 非作者静态 Review → 编排会话代行 Codex 集成。
- 推荐原因与前置依赖：Owner 交付完毕停写；Review→集成链按协作协议。
- Recovery point：本仓库、`agent/zcode/M2-TA3-B3-KO-FULLRUN`、base `73252798`、head `0ca8c740`。
- 允许修改路径：Review 返修限允许修改面；集成面按协议。
- 禁止范围与新增授权条件：同 Task 禁改面。
- 交付物：DSH review 报告 → 集成 merge → post-merge STATUS/PLAN 收口。
- 验证命令、环境与完成 Gate：主报告 §9 复现 + 集成方标准门禁（三套件 pytest；本 Task 无 src 改动，基线 611+1skipped 0 failed 应不变）。
- 可直接转发给 Agent 的指令：

```
对 M2-TA3-B3-KO-FULLRUN 做非作者静态 Review。
worktree：G:/CODEX/New Manga.worktrees/M2-TA3-B3-KO-FULLRUN-zcode
delivery_head：0ca8c740（base 73252798，线性链 24a89d7d→cd76cac0→7aee808d→0ca8c740）
必读：verification/M2-TA3-B/ko-fullrun-report.md（主报告，§1 执行环境事件必读）
核查重点：
1. AC 判定复核（报告 §10 vs Task AC 原文）；
2. invalid-env 事故处置完整性（summaries/invalid-env-2026-10-02-ocr-dep-missing/ 的 run1.steps 错误码、budget-ledger invalidated_entries_note、driver 硬化两 commit 的 env 注入与 fail-fast 逻辑）；
3. 双 driver 处置叙事与 commit 7aee808d 一致性；
4. F1/F2 关闭证据链（detect 同值表 vs M2-DETECT-WEBTOON-TILING/qualification-results.json；K07/K09/K10 export 状态）；
5. 相似度 FAIL 形态归因与 thresholds §5 新注/ko-rerun-report §7 回填的口径一致性；
6. 禁改面（src/tests/contracts/packaging/apps/首跑与 KO-RERUN 产物零改动）与 key 零明文。
输出：verdict + 逐项 R 编号 findings（P0-P4）+ NOT_VERIFIED 清单。
```

## 风险与遗留

- **K01 run1=FAILED steps 全绿**：归因未定（planner 聚合层嫌疑），非阻塞；若后续 Task 需要 run1 状态语义正确（如 mock 轨哈希确定性跑），需先归因。
- **K09 run1 86s/region 异常窗**：API 往返波动观测，单 case 小时级；后续长跑预算模型建议按 case 独立估而非均值外推。
- **运行时 O(页高) 特性**：region 渲染整页画布操作；webtoon 大页生产化前的优化候选（region 局部贴图化），需独立 Task。
- **坏轮像素残留**：`ko-fullrun-pixels` 下坏轮 export/crops 与有效轮同树（有效轮已覆盖同名文件）；如需严格审计可按 mtime 区分，未清理（外部树，无入库影响）。
- **相似度语义度量**：候选方向待校准集，需新 Task；K02 93 对 + K11 浮动对可作种子。

## 实验附录（实验任务必填）

- **数据来源与许可**：测试资产沿用 M2-TA2C 交付的 cases.json（100 case 库，本 run 8 ko case）；无新素材引入。
- **模型/权重**：检测 ogkalu RT-DETR-v2（weights dir 外部树 M2-DOCTR-QUAL-C4）+ chiqui7 SFX ONNX（M2-SFX-DETECT，conf≥0.50 冻结）；OCR PaddleOCR 3.7.0 + paddlepaddle 3.3.1（`enable_mkldnn=False` 正确性代价先例）；翻译 DeepSeek `deepseek-chat`（remote 采样）。
- **硬件/网络**：CPU 推理（`NEWMANGA_DETECTOR_DEVICE=cpu`）；DeepSeek 经用户代理出网；endpoint probe 每阶段前置。
- **参数**：TILING env 未设=默认（4.0/1024/128/0.5）；sfx.policy 缺省=SKIP；`--determinism-track remote`；region 无截断。
- **运行次数**：每 case 1 次主 pass；K02 额外 1 次干净 rerun + similarity 对照。检测层跨 run 同值（5 case vs TILING 先例）构成确定性旁证。
- **原始结果**：全部 summaries/determinism/ledger 已入库；失败样例：42 个 variant pairs 逐对在 K02-similarity.json `pairs[]`（最差三对引用于报告 §5）。
- **限制**：directional（单一 endpoint、单一机型、无温度消融）；CER 面 NOT_AUTOMATED（无 SVG GT）；相似度 Gate 词面口径的合法重译保守误报为已知局限（thresholds §5 注）。
- **Secret**：无（key 仅 env 注入，全落盘物经 scrub；本文件与报告零明文）。
