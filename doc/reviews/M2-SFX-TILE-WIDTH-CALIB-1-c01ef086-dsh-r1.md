# M2-SFX-TILE-WIDTH-CALIB-1 独立 Review（Reviewer=DeepSeek Harness，非作者，纯静态）

## 1. 终判

**approved_with_conditions（有条件通过）**

- 三条 AC 的实质判据全部成立（见 §3），交付的核心数字经报告 ↔ raw JSON ↔ log ↔ T5 parity raw 四方互证后**全部自洽，未发现任何编造、错算或方向性误导的数字**；零 src 的 (a) 结论在其已声明的 directional 限制内被数据支撑。
- 附条件：**P2-1（Task frontmatter base_commit 与 owner_claim/Handoff 冲突，影响集成 diff 范围）与 P2-2（参考口径 conf 0.2 下"重采样 ≥ 原生"排序翻转未如实登记）**应在 Codex 集成合并前以 docs-only 方式修正；两项都不需要重跑评测、不需要改 src。
- 无 P0/P1。若集成方接受 P2 为 docs-only 修正，可与集成验证并行。

---

## 2. 分级发现

### P0（阻塞集成）
无。未发现任何"错数、伪造锚点、改 src、证据与结论不符"级别的缺陷。所有结论性数字均可回溯到 raw 证据（复核明细见 §3 前的一致性核验）。

### P1（必须返修）
无。

### P2（应返修）

**P2-1 `base_commit` 字段自相矛盾，直接影响集成 diff 范围**
- `doc/tasks/M2-SFX-TILE-WIDTH-CALIB-1.md:12`：`base_commit: 72807d30`；
- 同一文件 `:6` owner_claim：`base=d298ecd0=释放登记 tip`；`:44` 交付记录：`base `d298ecd0``；
- `doc/handoffs/M2-SFX-TILE-WIDTH-CALIB-1-zcode-20261004.md:5`：`base_commit: d298ecd0`，`:34` 零 src 核验命令用 `d298ecd0`，`:41` 接收方式亦为 `d298ecd0`。
- 后果：集成方若照 Task frontmatter 跑 `git diff 72807d30..HEAD --stat -- src/ tests/ ...`，在 T5 已 merge（`5e70af4e`）且携带 tile src 变更的前提下，很可能得到**非空 src diff**，从而要么误判"零 src 纪律失败"，要么把 T5 的 src 变更错记到本 Task 账上。
- 修法（docs-only）：用 git 确认分支实际交点后，把 frontmatter 统一为实际 base；若分支确实基于 `72807d30` 而 `d298ecd0` 是另一条 tip，则 Handoff:34/:41 的 diff 命令必须同步改成"本 Task 变更面"的正确范围，不能只改一处。

**P2-2 conf 0.2 参考口径下"重采样 ≥ 原生 690"排序翻转，报告以"方向一致"带过**
- `verification/M2-SFX-TILE-WIDTH-CALIB-1/width-calib-report.md:34` 称 conf 0.2 参考口径"与 conf 0.5 主口径方向一致，无新增宽度相关信号"；同句列出的数字本身即显示相反：
  - conf 0.5：W690 **0.6078** < W640 0.6471 / W480 0.6863 / W320 0.6863（`raw/width-eval.json:46`、`:790`、`:1389`、`:2006`）；
  - conf 0.2：W690 **0.7647** > W640 0.7059 / W480 0.7255 / W320 0.7059（`raw/width-eval.json:60`、`:804`、`:1403`、`:2020`）。
- 即 §3.1 的"重采样档 recall 不低于原生 690 档 0.608"**只在主口径成立**；参考口径下三个重采样档全部低于原生档 0.04–0.06。数据未造假（两组数字都在同一句里），但小结措辞会让读者把"无劣化"当成口径无关的结论，而 AC3(a) 恰恰依赖这句。
- 修法（docs-only）：在该脚注与 §5 限制中显式写明"原生 vs 重采样排序随 conf 口径翻转；两口径一致的是'640/480/320 之间无单调劣化趋势'与'tile ≫ letterbox 结构性优势'，而非'重采样 ≥ 原生'"，并把该口径依赖列入 §5 directional 清单。

### P3（建议）

**P3-1 "tile:letterbox ≈8-12×"未覆盖低端（报告自身表格即可算出）**
`width-calib-report.md:42`、`doc/tasks/…:49`、Handoff:37 均写 "≈8-12×"。按报告 §2 表与 JSON：W600 0.366/0.056=**6.5×**（`raw/width-eval.json:698`、`:726`），W640 2.711/0.363=**7.5×**（`:789`、`:796`），W690 8.0×，W480 10.7×，W320 11.6×，SYNTH 8.0–10.9×。真实区间约 **6.5–11.6×**（剔除 W600 后 7.5–11.6×）。建议改为"≈6.5–12×"或逐档给比值。定性结论（GPU 档远低于 T5 的 CPU 档 ≈20×）不受影响。

**P3-2 上限侧（宽>690）tile 面未测，证据是单侧的；且脚本 docstring 与实际行为不符**
- `eval_tile_width.py:12-14` 称域外档"run the default env only"，但代码在 conf 0.2 仍以 `NEWMANGA_SFX_TILE=off` 跑 letterbox（`:348-352`），JSON 里域外档确有两面（`raw/width-eval.json:3546-3574`）——docstring 与行为不一致，应改。
- 更实质：env 面存在 `NEWMANGA_SFX_TILE_ROUTE_MAX_PAGE_W`（`src/infrastructure/providers/detection_sfx.py:274`、`:325`），本 Task**没有**用它在 700–1024 上跑 tile 面，因此本证据集**不能裁决"提高宽上限"类提案**，(a) 只是"保持零变更默认值"的结论。建议在 §5 限制中显式登记"上限侧 tile 性能未测"，避免后续 Task 误引本证据支持放宽 690。
- 备注：域外档"letterbox 0/27"是 aspect 决定的（页面 aspect 60–107 → 整页 letterbox 后宽 9.6–13.6px），报告 §3.4 已如实定性为"既有结构事实复现，非新劣化"，此项表述诚实。

**P3-3 宽度阶梯的非独立性（同一源页复用 5 档）未登记**
`INPUTS.md:38-41` 已声明混合宽度/有效分辨率两因素、合成字形域偏移、页数少，但未声明 640/480/320/800/1024 全部复用同 2 张源页（pre-k08/k09）——观测非独立（pseudo-replication），"逐宽"实为"逐缩放"。建议在 §3 自锚声明补一条。

**P3-4 锚点硬断言强度低于文字描述**
`eval_tile_width.py:356-364` 只断言 `matched` 与 `n_gt`。T5 parity raw 同时提供 `n_pred` 与逐 `pairs`：`parity-v2b.json:15/116/264` = 23/50/5，与本轮 `raw/width-eval.json:87/352/693` 完全一致，`pre-k08` 首条 pair（gt 7/pred 1/iou 0.9657/conf 0.8926，`width-eval.json:96-101`）与 `parity-v2b.json:21-27` 逐字段相同。建议把 `n_pred`（乃至 pairs 摘要）纳入硬断言，才配得上 Handoff:32 "逐页复现 T5 parity raw" 的措辞。

**P3-5 `match_gt`"逐字等价"有一处返回字段偏差**
`eval_tile_width.py:114-149` 与蓝本 `experiments/M2-SFX-GATE-T3/eval_gate_t3.py:160-192` 的匹配判定逐行相同（conf 降序、`v >= IOU_MATCH and v > best[0]`、每 GT/每 pred 至多一次、recall/precision 取整口径一致），但返回值少了 `gt_matched_flags`（`eval_gate_t3.py:191`）。建议注释/报告写明"匹配判定逐字，返回字段省略 `gt_matched_flags`"，或补齐该字段；`iou_xyxy`/`poly_to_xyxy`（`:93-108` vs `:140-157`）确为逐字。

**P3-6 raw JSON 未记录有效执行 EP，GPU/DML 结论靠旁证**
`run_face`（`eval_tile_width.py:231-260`）只落 `sfx_route/tile_count/tile_h/...`，未落 `result.options` 里现成的 `device`/`sfx_ep`/`sfx_ep_fallback`（`src/infrastructure/providers/detection_sfx.py:734-740`）。当前 GPU 判定依赖 ms/tile 16.3–18.4ms（`width-eval.json:94` 等 24 处）vs T5 CPU ~160ms/tile（`verification/M2-SFX-T5-TILE-KO/tile-deploy-report.md:15`：9.26s/58 tiles）这一强旁证。建议后续脚本落该键，使"GPU 档口径"自证。

**P3-7 跨轮一致性主张在仓内无证据，且页数与域内页数不符**
`width-calib-report.md:47` 与 Handoff:62 称"第 2/3 轮域内 11 页逐行 matched/n_pred 完全一致"，但仓内只有最终轮 log（`raw/eval-run.log`，第 21 行已写盘）；且域内页数应为 **12**（14 页减 W800/W1024 两域外页，见 `eval-run.log:3`），"11 页"对不上。建议删除该主张或补登前轮 log。

**P3-8 §5 头句"同量级"的范围应收紧**
`width-calib-report.md:52` 头句把"宽 320-680 的未校准宽度"整体说成与 600/690 "同量级"，而 SYNTH 档 conf 0.5 recall 为 0.245/0.261/0.391（`width-eval.json:2616/2896/3188`），显著低于 0.608。§3.3 已正确归因字形域偏移，建议 §5 头句限定为"真实内容重采样档（640/480/320）"，合成档单列为机械面/耗时面证据。

**P3-9 `~0.8s/页` 是页高相关量，跨域代价宜以 ms/tile 为主表达**
`width-calib-report.md:40`、`doc/tasks/…:49` 用"~0.8s/页"表述 §3④ 跨域激活代价，但页耗时随 tile 数线性（合成页 41–46 tiles vs KO 页 58–112 tiles）；域无关的口径是 ms/tile 16.3–18.4ms。建议主指标用 ms/tile，页级耗时标注页高。

**P3-10 AC4 的"finally 恢复"未按字面落地**
合同 §AC4（`doc/tasks/…:33`）写"权重 sha 先验断言+**finally 恢复**（先例）"。`eval_tile_width.py:307` 用 `env_backup`，恢复在成功路径 `:408-410`，无 `try/finally`；`except AssertionError` 分支（`:431-437`）不恢复。本次零权重重指、env 为进程级，**无实际影响**；建议补 `finally` 以对齐合同字面与 T5 先例。

### P4（备注）

- **P4-1** 控制台汇总对域外档打印 `tile 0/0`（`raw/eval-run.log:32-33`；`eval_tile_width.py:419-428` 直接读 agg 的零初始化 tile 面，`:324-329`），JSON `aggregate` 同样含零值伪面（`width-eval.json:3547-3553`），易被误读为"tile 跑了且 0 命中"；建议打印 `n/a (not routed)` 并让未跑面在 JSON 中缺席或置 null。
- **P4-2** `prepare_pages.py:116` 只断言 `pre-k08=690`、`pre-k02=600`，未断言 `pre-k09=690`（档标签由实际宽推出，`:157-161`），若 k09 换宽会静默生成新档而非失败。
- **P4-3** AC1 盘点表（`INPUTS.md:13`）只枚举 KO 套件 `01_real_webtoon_cleaned_dataset`，未列 `02_public_ground_truth_peppercarrot`。仓内旁证该子目录 K11/K19 为 1200x1660（aspect 1.38，`verification/M2-REGION-OVERLAP-ARBITRATION/raw/ko-scan/K11.json:5-8`、`K19.json:5-8`），不构成反例；"逐树"完整性宜补一行。
- **P4-4** `eval_tile_width.py:49-51` 硬编码 `PROD_PIN_SHA`，未 import `src` 的 `SFX_WEIGHTS_SHA256`（`detection_sfx.py:131-132`，两者当前同值 `944e8114…`）；provider 自身 sha gate 已兜底，但双源存在漂移面。
- **P4-5** `width-eval.json:3` 的 `generated_at_utc=2026-10-06T10:26:52Z` 是 summary 构造时刻（`eval_tile_width.py:291`，warm-up 前），非写盘时刻（log 起于 10:26:48，全程约 2.5 分钟），字段名易误解。
- **P4-6** `eval_tile_width.py:431` 只捕获 `AssertionError`；`KeyError`/`ProviderError` 等不落 failure JSON（本次未发生）。
- **P4-7** 重采样 GT 的 y 坐标按宽度比缩放（`prepare_pages.py:136`），图像高用 `round(h0*scale)`（`:127`），垂直两轴比例差 ~5e-6（页底 ~0.3px）；对本轮 IoU 无影响，可注明。

---

## 3. AC 逐条判定

| AC | 判定 | 一句话理由 |
|---|---|---|
| **AC1** 多宽页评测集与逐来源 GT 声明 | **PASS** | 10 档 14 页逐档登记页数/GT 类型/框数（`INPUTS.md:21-32`），两条授权补样路径与真实来源（原生锚点 W690/W600）齐全，自锚风险四条声明（`:36-41`）；仅盘点表完整性（P4-3）与阶梯非独立性（P3-3）可补强。 |
| **AC2** 生产代码路径 + tile vs letterbox + v2b sha 断言 + 耗时 | **PASS** | 经本 worktree `src` 的 `SfxDetectionProvider.detect`（`eval_tile_width.py:40-41`、`:268`），域内 8 档 tile（默认 env）vs letterbox（`NEWMANGA_SFX_TILE=off`）双面、conf 0.5 主 + 0.2 参考，逐档断言 `sfx_route`（`:237-240`），权重 sha 先验断言且与 src pin 同值（`:272-275` / `detection_sfx.py:131-132`），候选/匹配/耗时三面齐全（含 `elapsed_ms_provider`、`ms_per_tile`）；域外 2 档仅谓词侧 letterbox 面（P3-2）。 |
| **AC3** 三选一结论的证据支撑 | **PASS** | (a) 证据链完整且自洽：原生锚点 14/27、17/24、2/3 与 T5 parity raw 逐页同值（`width-eval.json:181/464/715` vs `parity-v2b.json:8-16/109-117/257-266`，n_pred 23/50/5 亦同），letterbox 10 档×双 conf 全零候选（`eval-run.log:7-20` 每行 `n_pred 0`），域内重采样 conf 0.5 recall 0.647/0.686/0.686 ≥ 0.608；directional 限制逐条声明、零改冻结常量；须按 P2-2 修正参考口径措辞、按 P3-1/P3-8 收紧汇总数字后方可正式作为 §3① 缺口关闭记录。 |

**数字一致性核验（C 项，逐条完成）**
- 恒等式全档成立：`matched ≤ min(n_gt, n_pred)`、`recall=matched/n_gt`、`precision=matched/n_pred`。
- aggregate = 逐页和：W690 `14+17=31`、`23+50=73`、`1.032+1.829=2.861`（`width-eval.json:40-68`、`:87`、`:352`）；W640 `17+16=33`/`30+49=79`/`2.711`；W480 `19+16=35`/`27+48=75`/`2.017`；W320 `19+16=35`/`26+33=59`/`1.31`；conf 0.2 W690 `18+21=39`/`56+95=151`、W640 `36`/`145`、W480 `37`/`118`、W320 `36`/`84`——全部与 `eval-run.log:7-18` 及报告 §2 表一致。
- 报告 §2 表**全部单元格逐格复核通过**（含 0.06/0.36/2.71/0.774/0.85/0.828 等耗时四舍五入值、`ms/tile` 16.3–18.4 的 24 个原始值），lensbox 全零候选、域外 `0/27` 均一致。
- 锚点自检数字：`14/27`、`17/24`、`2/3` ✔；T5 `≈20×` 的 CPU 档归属核对正确（`doc/tasks/M2-KO-TILE-CALIB.md:49`「~8.9s/页 CPU（≈20× letterbox，GPU 未测）」、`tile-deploy-report.md:15` CPU tile 9.26s/页），本 Task 以 GPU 档 6.5–11.6× + ms/tile 并记，属**如实并记**而非口径混用。
- 措辞纪律：全仓 `verification/M2-SFX-TILE-WIDTH-CALIB-1` 内无"显著/significant"（仅纪律声明字符串 `width-eval.json:3706`）。

**复核限制（如实声明，非缺陷）**
1. 本会话沙箱拒绝 shell（`pwsh` 报 `SetNamedSecurityInfoW failed`），**未独立执行** `git diff d298ecd0..HEAD --stat -- src/ tests/ packaging/ contracts/ apps/ doc/STATUS.md doc/REBASELINE_PLAN.md`；仅以 glob 确认交付面文件集合恰为合同允许路径（experiments 3 文件、verification 4 文件、Task+Handoff）。零 src 结论须由 Codex 执行 Handoff:34 命令闭环（并与 P2-1 的 base 冲突一并解决）。
2. 外部树（页图、权重、own-manga/KO/train-v2 素材）不在仓库内，无法直读；INPUTS §1 "真实素材零『宽≠600/690 且 aspect≥8.0』页" 的**仓内旁证**为：`M2-REGION-OVERLAP-ARBITRATION/raw/ko-scan` 的 K01/K02/K04/K05/K07/K08/K09/K10 全 690 或 600 宽（aspect 28–190），K11/K19 为 1200x1660 普通页——无任何反例，但盘点硬结论的最终确认仍在外部树。
3. 报告 §4 前两轮运行 log 未入库，跨轮一致性主张不可独立复核（见 P3-7）。

**值得肯定的点**：nested 变量的评测设计（BIN_ORDER + `width_bin_for`/`domain_for` + 硬断言锚点 + `bin_pages` 非空断言）能防止"少测一档静默通过"；`prepare_pages.py` 原生页 sha256/尺寸双断言 + `eval` 侧再对 prepared manifest 断言，证据链完整；两处运行期 bug 在写盘前修复并完整重跑、如实登记（报告 §4），符合"先写盘后说话"纪律；(a) 结论未夹带任何改常量动作。

## 推荐下一步

1. **ZCode（原 Owner，docs-only 返修）**：修 P2-1（用 git 确认分支实际 base 后统一 Task frontmatter 与 Handoff 的 diff 范围命令）与 P2-2（在报告 §2 脚注与 §5 限制写明 conf 0.5/0.2 下"原生 vs 重采样"排序翻转）；顺带处理 P3-1/P3-8 的汇总数字与措辞。不重跑评测、不改 src。
2. **编排会话代行 Codex（集成）**：返修后执行 `git diff d298ecd0..HEAD --stat -- src/ tests/ packaging/ contracts/ apps/ doc/STATUS.md doc/REBASELINE_PLAN.md`（空 diff）+ 逐页锚点 `14/27、17/24、2/3` 与 `parity-v2b.json` 对照，然后 merge、回填 `review_events` 并将 Task 置 done。
3. 无后续实现 Task 待释放（AC3=(a) 零 src，§3① 缺口以本证据关闭）；`§3④` 的"提高宽上限"类提案若未来出现，须另开 Task 用 `NEWMANGA_SFX_TILE_ROUTE_MAX_PAGE_W` 覆盖补测（见 P3-2）。
