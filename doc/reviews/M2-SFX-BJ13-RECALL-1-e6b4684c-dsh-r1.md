# M2-SFX-BJ13-RECALL-1 非作者独立复核报告（r1，静态只读）

## 1. 方法段

本次复核全程只读，未修改任何文件，未落盘 Review 文件（按本次指令输出全文至 stdout）。

**已读文件（逐 path）**
- 合同/交接/交付物（全文）：`doc/tasks/M2-SFX-BJ13-RECALL-1.md`、`doc/handoffs/M2-SFX-BJ13-RECALL-1-zcode-20261006.md`、`verification/M2-SFX-BJ13-RECALL-1/recall-report.md`、`verification/M2-SFX-BJ13-RECALL-1/raw/recall-probe.json`、`verification/M2-SFX-BJ13-RECALL-1/raw/recall-probe-run.log`、`experiments/M2-SFX-BJ13-RECALL-1/recall_probe.py`
- 生产语义对位（节段）：`src/infrastructure/providers/detection_sfx.py`（:100-180、:180-310、:530-650、:655-724、:740-860、:930-1050、:1130-1260、:1330-1410）、`src/infrastructure/providers/detection_manga.py`（:106-125、:485-519）、`src/bootstrap/core_assembly.py`（:915-975）
- 上游证据（节段/命中）：`verification/M2-REGION-OVERLAP-ARBITRATION/raw/arbitrate-pages.json`、`.../arbitration-report.md`（grep）、`experiments/M2-REGION-OVERLAP-ARBITRATION/arbitrate_bj13.py`（:58-73、:195-254）、`verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/raw/l1-fullpage-conf-scan.json`（:1-30、:5205-5560）、`experiments/M2-SFX-DETECT-DOMAIN-EXT-DIAG/conf_scan_diag.py`（:86-177）、`.../diagnosis-and-options.md`（grep）
- 交叉验证锚：`verification/M2-SFX-T4-SWITCH/raw/g7-smoke-v2b/{harness-meta.json,summaries/qual-BJ06.json,summaries/qual-report.json}`、`.../g7-smoke-v2b-console.log`、`.../g7-smoke-chiqui7/summaries/qual-BJ06.json`、`.../switch-report.md`、`.../raw/roadmap`（`rollback-drill.json`、`pin-switch-verify.json`）、`verification/M2-SFX-DETECT-EVAL/sfx-detect-eval-report.md`、`verification/M2-SFX-E2E-MATERIAL/bj06-run/summaries/qual-BJ06.json`
- 选项依据：`doc/tasks/M2-SFX-ANNOTATE-R1.md`、`doc/tasks/M2-SFX-ANNOTATE-R2.md`、`doc/tasks/M2-SFX-GATE-T3.md`（grep）
- 入库纪律：`.gitignore`、`test_assets/comic_golden_suite/日漫_JA/.gitignore`

**边界（如实声明）**：本次无 shell/git 执行权限（`pwsh` 以 `SetNamedSecurityInfoW failed (Win32 5)` 失败），因此 **sha256 不能独立重算、`git status`/`git diff --check`/commit 拓扑不能独立执行**。凡涉「零 src」「EXIT=0」「commit 链」的断言，均只做**静态核对**（读文件引用 + 脚本内容推断 + 允许路径枚举），已在 AC4 与发现中标注。所有数字核对为手工重算（IoU/比值），非工具复算。

## 2. 终判

**approved_with_conditions** —— 未发现 P0/P1；核心事实层（三态数字、BJ13 sfx×primary=0.0、BJ06↔G7 逐框对位、生产语义等价）经独立重算与逐字对位**成立**；存在 1 项 P2 事实性口径错误 + 5 项 P3 + 6 项 P4，全部文本级、不改变任何 AC 结论。

## 3. 逐项核对表

| # | 核对项 | 判定 | 证据（path:line）与复算 |
|---|---|---|---|
| V1 | BJ13 conf≥0.5 sfx 唯一候选 conf 0.8914 @[1555.4,2610.8,1778.4,2904.4]（Slipknot 非参照框） | 一致 | `raw/recall-probe.json:419-436`；report:48 |
| V2 | ref1 [2210,240,2560,1000] / ref2 [420,2560,760,3400] 与 DOMAIN-EXT-DIAG verbatim | 一致 | `recall_probe.py:117-131` vs `l1-fullpage-conf-scan.json:5208-5215, 5272-5279` |
| V3 | ref1 IoU 0.5235 / ref2 IoU 0.5584 手算 | 成立（0.5234/0.5585） | `raw/recall-probe.json:451,485`；report:51-52 |
| V4 | 4.4x / 42x 比值 | 成立（4.36/41.8） | 峰值 0.3727/0.1796（`json:451,485`）vs 基线 0.0855/0.0043（`l1-…json:5331,5541`）；report:15 |
| V5 | 基线口径可比性（同一 raw 探针形态 + 同一 letterbox 1024） | 成立 | `conf_scan_diag.py:149-176`（同 `max(scores)<0.01` + letterbox 中心测试）vs `recall_probe.py:275-297`；`l1-…json:3` `"letterbox": 1024` |
| V6 | BJ14 全 rung 零 / BJ15 参照框零 + 页面级孤立 0.5118 | 一致 | `json:784-938`、`:940-1089`；report:56-62 |
| V7 | BJ06 5 候选 conf 0.5446-0.8719、命中 5/8、未命中 ab8974e1/c3781c28/b5b747d0 | 一致 | `json:112-193,196-281`；8 region 清单 `recall_probe.py:135-144` = `conf_scan_diag.py:90-98` |
| V8 | BJ06 五框与 T4 G7 v2b 臂逐框 <0.5px（5=5） | 成立（逐框手算差 ≤0.4px） | `json:112-193` vs `g7-smoke-v2b/summaries/qual-BJ06.json:889-945` |
| V9 | BJ13 sfx×primary max IoU=0.0 | 成立（3 个 manga 框与 Slipknot 框三轴均不相交） | `arbitrate-pages.json:29-33,58-62,87-91,116-121`；`json:768-782` |
| V10 | BJ06 max 0.8732 / 0.85+ 对 1 / 内含形 1(0.7576) / 模拟 0.90 relabels=0 | 一致 | `json:295-346`；与 `detection_sfx.py:1358-1396` 生产语义逐一对照（含 `partial_overlap` 口径） |
| V11 | primary 计数 3/6/7/9 与 `manga-` 过滤 | 一致 | `json:284,770,928,1079` vs `arbitrate-pages.json`（BJ13 3+sfx1、BJ14 6、BJ15 7、BJ06 9+sfx8）；过滤式同 `arbitrate_bj13.py:215` |
| V12 | primary 复用合法性（快照身份 + rerun 自身强制 pin） | 成立 | `detection_manga.py:495-519`（三文件 sha 强制）；rerun 同 dir 常量 `arbitrate_bj13.py:60-63,202` vs `recall_probe.py:103-105,457` |
| V13 | 权重 pin 强制校验 | 成立 | `_build_engine` sha 门 `detection_sfx.py:973-979`；probe 调用 `recall_probe.py:490`；log:2 |
| V14 | 环境 fail-fast（引擎失败非零退出） | 成立 | `recall_probe.py:489-494`（exit 4）、`:450-452,483-486`（exit 2）、`:181,191`（exit 3）；log 无 FATAL |
| V15 | 生产语义等价（letterbox/conf 0.5/NMS 0.7/EP dml/imgsz） | 成立（含 1 项未登记差异） | `_letterbox/_nms/_map_back` 复用 `recall_probe.py:84-87`；EP/imgsz 由 `_build_engine` 解析 `:490`；log:5 `ep_effective=dml`、`imgsz=1024 metadata_parsed`；conf 过滤次序差异见 P3-3 |
| V16 | CHIQUI7 bebaseline imgsz 表述 | **不成立** | report:27「chiqui7 时代为 1280」 vs `l1-…json:3`、`sfx-detect-eval-report.md:67`、`switch-report.md:67` + `rollback-drill.json:16`（均 1024） |
| V17 | 归因与选项依据 | 成立 | R1 delete：`M2-SFX-ANNOTATE-R1.md:63`、`R2.md:69`；BJ36/37 0 框：`M2-SFX-GATE-T3.md:47` |
| V18 | 纪律措辞（无「位级可复现」、无作者自封「独立复核」） | 成立 | grep 命中仅 report:44/109/116、Task:43、Handoff:36/46/54/64；四文件均无「位级可复现」自述 |
| V19 | 零入库（权重/页图） | 成立 | `.gitignore:8-10`（`*.onnx`）、`__pycache__/`；`test_assets/comic_golden_suite/日漫_JA/.gitignore:26`（`/01_black_jack_official/`）；两交付目录仅 .py/.md/json/log |
| V20 | `git diff --check` 口径（静态替代检查） | 未发现反证 | 对 6 个改动文本文件 grep `[ \t]+$` 零命中；**但 git 面 EXIT=0 不可独立执行** |

## 4. 分级发现

**P0（阻塞集成）**：无。

**P1（必须返修）**：无。

**P2（应返修）**
- **P2-1 基线 imgsz 事实性错误**：`verification/M2-SFX-BJ13-RECALL-1/recall-report.md:27` 写「imgsz 由 v2b ONNX metadata 驱动（chiqui7 时代为 1280）」；三项记录一致证明 chiqui7 生产 ONNX 为 **1024**（`verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/raw/l1-fullpage-conf-scan.json:3`、`verification/M2-SFX-DETECT-EVAL/sfx-detect-eval-report.md:67`、`verification/M2-SFX-T4-SWITCH/switch-report.md:67` + `raw/rollback-drill.json:16`）。该括注同时还暗示两代 letterbox 尺寸不同，**削弱**了 4.4x/42x 的可比性（实际同为 1024，比较是更干净的）。处置：改为 1024（并可补「基线为 CPU 形态」）；不涉及任何数字变化。

**P3（建议）**
- **P3-1 AC3 缺 tile 路由适用性说明**：report §4 三选项未提 tile；`_routes_to_tile` 谓词（`detection_sfx.py:556-562`，`SFX_TILE_ROUTE_MAX_PAGE_W=690`/`MIN_ASPECT=8.0`，`:270-271`）对 BJ13（2946×4167，aspect 1.41）不成立，且该谓词属禁改冻结域。建议在 §4 加一行「tile 路由对 BJ13 不可适用且谓词冻结，故不作为选项」。
- **P3-2 域内对照的「自证」性质未承继**：8 个生产 sfx region 来自 chiqui7 自身输出（`verification/M2-SFX-E2E-MATERIAL/bj06-run/summaries/qual-BJ06.json`），其「8/8」是自证而非 GT 召回；上游已登记该限制（`verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/diagnosis-and-options.md:214`），但 report:66-67 与 §6 Known limitations 未携带。建议补一句。
- **P3-3 探针 conf 口径两处差异未登记**：①probe 先按 0.01 过滤再分 rung（`recall_probe.py:224,548-555`），生产先按 conf 阈值过滤（`detection_sfx.py:1184,1193`）——对 ≥0.5 子集数学等价（抑制者分数恒 ≥ 被抑制者，故子集结果相同；同分并列的 argsort 非稳定性为唯一残余），且 V8 已实证；②probe 直接取模块常量 `SFX_CONF_THRESHOLD`（`recall_probe.py:82`），不读 `NEWMANGA_SFX_CONF_THRESHOLD` 覆盖（`detection_sfx.py:136-139`）。report §1 未说明这两点。
- **P3-4 base_commit 三处不一致**：`doc/tasks/M2-SFX-BJ13-RECALL-1.md:11` 为 `3a65150b`，同文件 `:47` 与 `doc/handoffs/…-20261006.md:5,40` 为 `2a1a9f73`（合同外文本均指后者）。静态无法判定谁为真；建议集成方对账并统一 frontmatter。
- **P3-5 raw 日志缺命令/EXIT/环境头**：`verification/M2-SFX-BJ13-RECALL-1/raw/recall-probe-run.log` 仅 22 行 stdout，无调用命令行、无 `EXIT=0` 行、无 shell/venv/python 版本头；EXIT=0 仅见于 report:7 与 Handoff:29 的自述。建议按本项目 raw 证据惯例补头部。

**P4（备注）**
- **P4-1** `relabels` 计数口径：probe 按「相交对数」（`recall_probe.py:409`），生产按「primary 候选数」（`detection_sfx.py:1359-1368`）；当前四页全 0，无影响。
- **P4-2** probe 恒走 letterbox，未自证路由谓词（四页 page_w=2946>690，`detection_sfx.py:756-772` 下必为 letterbox，结论不受影响）。
- **P4-3** 措辞：report:53 / Task:53「两代权重**域内**一致性正面证据」用词不当（BJ13 是 DOMAIN-EXT-DIAG 判定的**域外**页），宜改为「两代权重在该区判定一致」。
- **P4-4** report:66 括注「（未命中：ab8974e1、c3781c28、b5b747d0 小框 87×103）」中「小框 87×103」仅对 b5b747d0 成立（c3781c28 为 217×492）。
- **P4-5** 页图位置措辞：Task:32/41、Handoff:41,69 称「gitignored task-envs 外部树」，实际路径在 peer worktree 的 `.../test_assets/comic_golden_suite/日漫_JA/01_black_jack_official/`（由该目录 `.gitignore:26` 忽略，零入库结论仍成立）。
- **P4-6** 4.4x/42x 属 CPU（chiqui7，ORT 1.30.0，见 `sfx-detect-eval-report.md:67`）↔ DML（v2b）跨形态比值；report §5 只声明「DML 单形态」，未点明基线为 CPU。量级远超已登记 ≤2e-06 漂移窗口，不影响结论。
- **P4-7** 漏记更强证据：同像素 chiqui7 的 text 0.5195/sfx 0.0855（`l1-…json:5327-5332`）→ v2b 的 sfx 0.3727/text 0.0（`json:463-468`）是「类别翻转」，比比值更直接支持域适应起效；建议登记。

## 5. AC1–AC5 判定表

| AC | 判定 | 依据 |
|---|---|---|
| **AC1 召回实测** | **PASS** | 四页 conf≥0.5/NMS 0.7/letterbox/EP dml/imgsz 1024 实测完成（log:1-21）；三态逐页登记（report:46-67，判据 §2:37-42）；参照框 verbatim、低 conf 信号与参照框 IoU 全列（`json:437-506`）；BJ06 域内对照 5/8 且与 G7 v2b 逐框 <0.5px（V8）。未尽项：P3-3 口径差异未登记、P2-1 基线 imgsz 表述错。 |
| **AC2 重审切片（提案）** | **PASS** | 已履行为提案未实施：BJ13 sfx×primary **max IoU=0.0**（V9 手工复核）→ 0.90 域无对象；重审条件「内含形/0.85+ 对」双读法如实登记（report:79-83）；`sfx-arb-` 零触发（`json` 四页 relabels=0）；提案=维持 0.90 三条理由（report:87-91）与生产模拟口径（`detection_sfx.py:1358-1396`）一致；未触碰冻结域（`detection_sfx.py:218` 只读引用）。 |
| **AC3 三选项登记** | **PASS**（完整性 P3-1） | report §4:99-103 三选项+成本/收益+推荐序 ③②①；A①前提（R1 delete 未翻案）与 A②前提（BJ36/37 0 框）经上游文本核实（V17）；未新发明方案；tile 路由适用性未说明（P3-1）。 |
| **AC4 回归与纪律（静态面）** | **PASS（静态）／git 面 NOT_VERIFIED** | 交付目录仅含预期文件（glob）；`*.onnx` 与 JA 页图均被 ignore（V19）；6 个改动文本文件无尾随空白；不跑全量 pytest 的理由与「零 src」自洽（report:107-108）。**沙箱无 git/shell**：`git status`/`git diff --check` EXIT=0 不能独立执行，属 Owner 自述。 |
| **AC5 文档** | **PASS**（P3-5） | report + `raw/recall-probe.{json,-run.log}` + Task 回填（:45-55）+ Handoff 齐备；分支结论 AC2/AC3 双路径显式登记（report:20,§7；Task:49-50）。raw 日志头部缺失见 P3-5。 |

## 6. 残留风险与集成建议

1. **召回未恢复的实质风险照旧**：BJ13 参照框 conf≥0.5 零召回，「ピ一一ーン！」仍由 manga-1/3 以 speech 身份进翻译链乱译；仲裁几何上无对象（BJ13 sfx×primary=0.0），因此**不建议**以阈值手段处理，AC2 提案「维持 0.90」在独立复核下成立。
2. **AC2/AC3 双分支交付是保守的正确选择**：BJ13 在「模型信号面部分恢复」与「产品语义未恢复」两个口径下答案不同，报告对两口径分别定论并同时登记 A/B 两分支，未掩盖任一结论；集成时请按双分支呈报用户裁决，不要只取其一。
3. **可复测性**：探针对固定 v2b pin + 四个固定页面，`_build_engine` 强制 sha、primary 快照当次重验，脚本可直接重跑（约 <1 min）；建议把「下次 sfx 权重迭代后重跑本探针」写入 BJ13 依赖链注记的复测点（Handoff:55 已提）。
4. **集成前建议闭合条件**：
   - **C1（=P2-1）**：修正 `recall-report.md:27` 的 chiqui7 imgsz 表述为 1024（Owner 一行返修，或集成方在集成记录落字）。
   - **C2（=P3-4）**：对账并统一 Task frontmatter `base_commit` 与 Handoff/执行记录的 `2a1a9f73`。
   - **C3（=P3-2 + P3-3）**：在 §6 Known limitations 补两条——①8 个 BJ06 region 为 chiqui7 自证、无独立 GT；②probe 的 conf 过滤次序与不读 env 覆盖的差异。
   其余 P3/P4 可延后或并入下一次迭代，不阻断集成。
5. **不可由本次复核覆盖的面（明示）**：commit 链（`0f175b89→47df4dbc→d95bbdfe→docs`）、`零 src` 的 git 级证明、sha256 重算、`git diff --check` EXIT=0 —— 均因无 shell/git 权限而未独立验证，集成方应以真实 `git status`/`git diff --stat <base>..<tip>`/`Get-FileHash` 复核后再落 `done`。
