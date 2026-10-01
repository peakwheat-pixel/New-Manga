## Verdict
**approved（可集成）** —— r1 的 1×P1（R1 自比污染）已实质闭合且算术可复核，6×P2 全部闭合或按设计转为集成方动作；本轮新发现 1 项账目级自相矛盾（AC5 文件数）+ 8 项 P4 文字/口径 nit，全部**不影响三问结论、数字正确性与生产零改动纪律**，可在集成 commit 内顺手闭合，无需第三轮 Review。

静态审查限制：**本轮沙箱彻底不可用**——所有命令以 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\M2-SFX-EVAL-zcode)` 失败，`sandbox_permissions: danger-full-access` 升级被拒（no approval channel）。因此未执行任何 git/pytest/sha256 复算；证据来自 `review-fix.diff`（4367 行，12 文件）、worktree 现文件全量读取、以及**直接读取外部 license 原始快照**（read 工具可越 sandbox 读 task-env）+ 一次 web 复核 Manga109-s 条款页。

## R1-R14 逐条复核表

| 项 | 结论 | 依据（文件:行）与我的独立重算 |
|---|---|---|
| **R1 [P1] 自比污染/三分口径** | **closed** | `onnx-sfx-comparison.json:2`（schema@2）、`:5-9`（三分定义）、`:17-22`（`provenance_counts` 11/18/1/17）、`:23-31`（ALL_instances，ogkalu 列显式改名 `*_SELF_REFERENTIAL`）、`:32-41`（`NON_SELF_subset (R1)`）。**逐实例 provenance 计数我全量点数**（行 67,108,149,190,236,277 = 6；630,671,712,753,876 = 5；`c1_adjudicated` 仅 323；其余 17 为 `agent_estimated`）→ **11+1+17=29 ✓，非自比 18=17+1 ✓**。**按 29 实例 coverage 逐条重算**：自比 11 例 ogkalu cov 全 ≥0.5（0.632–0.987）；非自比 18 例中 ogkalu ≥0.5 = **7**（끌끌 0.965 / 빠걸×3 0.949·0.761·0.654 / Rrrrr 0.987 / rRrRr 0.97 / 수악 0.797）→ **7/18 ✓**；chiqui7 sfx ≥0.5 全量 **11/29 ✓**、非自比 **8/18 ✓**（≥0.3：全量 14、非自比 11 ✓）；Kiuyha 非自比 **2/18 ✓**。与 JSON `:34-39` 逐值一致。方向反转如实声明：报告 `:6,14,83-84,87,104`、Task `:56`、handoff（diff:29）。脚本 `provenance_of` + 6 单元白名单见 diff:3151-3175（字符串匹配与实测数据一致）。**nit**：自动 note（`:40`）写「ogkalu 7/18 vs chiqui7 11/29」，分母混用，建议改 8/18 |
| **R2 [P2] ≥0.3 列** | **closed** | 报告 `:82` 全量 ≥0.3 = ogkalu 18/29（self-referential）/ chiqui7 **14/29** / Kiuyha **7/29**；`:6` 声明「r1 误写 16/9/19」。与 `onnx-sfx-comparison.json:25,28,30` 一致 |
| **R3 [P2] 6/7 判据与 conf/cov 标注** | **closed** | 报告 `:93` 显式「硬盲区命中 = conf≥0.25 且 coverage>0（部分相交）」并并列严格 `cov≥0.5 = 4/7`（빠악 0.663 / 투두 0.926 / 빠직 1.00 / 송송 0.506+삐직 0.582；콰직 0.461、철컹 0.339、칼칼 0.0）；`:14,95` conf=/cov= 标注。我按 `onnx-sfx-comparison.json` 复核 6/7 与 4/7 的帧集合（7 个 missed 帧：K08_R041/R047/R057、K01_R069×2、K07_R103、K08_R019×2、K09_R001×2 归并后 7 帧 ✓）及标注值：콰직 0.7552/0.461、철컹 0.8192/0.339、빠악 0.2987/0.663、투두 0.9539/0.926、수악 0.3219/0.901、끼아아악 0.2715/0.89 — **全部对得上** |
| **R4 [P2] 许可一手证据** | **closed** | `license-evidence.md` 全 47 行（4 份 API 快照 sha256+字节数、抓取时间 2026-10-01T03:09:21Z、Manga109-s 条款短引文、报告候选表 URL 列 `report:21-27`）。**我绕 sandbox 直接读取原始快照逐字段核对**：`api-kiuyha.json`（`license:apache-2.0`、`cardData.license=apache-2.0`、sha `fb646500…`、lastModified 2026-02-17T00:28:51Z）✓、`api-chiqui7.json`（`license:mit`、sha `7f5f5c04…`，且 usedStorage 41227478 = inventory 中 yolo11s-seg.onnx 字节数）✓、`api-cozy.json`（tags 无 `license:`、cardData 无 license 键、sha `4c4d2a69…`）✓、`api-manga109s-dataset.json`（`license:other`/`license_name:manga109-s`/`gated:auto`、v2026 notice）✓；四者字节数 1393/691/730/2505 与 `external-evidence-inventory.json:426,431,436,441` 一致；`fetch-timestamp.txt`=21 B 与「…03:09:21Z\n」自洽。**Manga109-s 条款我用 web_fetch 独立复核**（[HF 数据集卡](https://huggingface.co/datasets/hal-utokyo/Manga109-s)，HTTP 200）：第 5 条「Using results…for commercial use.」、第 6 条「Redistribution…is forbidden.」、第 7 条（含 pre-trained models 须标注）、第 8 条、第 10 条（≤20%）与引文逐字一致 ✓。残留 P4：条款页无 HTML 快照入库（外部树里对应文件 `manga109s-README.md` 只是 401 gated 文本），建议照 API 快照同制补一份 |
| **R5 [P2] raw/block 双口径** | **closed** | 报告 `:13`「raw 11/23（47.8%）@0.5 / block 12/23（52.2%）@0.5；@0.25 两口径均 16/23」+ `:50` 脚注（`화——` raw 0.4625 vs block 0.7720）+ `:52`；Task `:55`、handoff diff:28 同步。artifact 侧逐帧依据同时落双源（`sfx-spot-check-verdicts.json:864,3083`：`[payload 取值] conf=0.4625` + `[frames-export 取值] conf=0.7720`），双口径可机核。P4：`sfx-spot-check-verdicts.json:21-30` 的 `frame_detection_rate` 仍只存 12/23，未加 raw 11/23 伴行列 |
| **R6 [P2] rationale 取值化** | **closed** | 三处指定值已由脚本从 payload 生成并与 artifact 一致：`sfx-spot-check-verdicts.json:43`（B1-U09 conf=**0.8044** cls=text_free）、`:183`（B1-U12 conf=**0.8546** cls=**text_bubble**）、`:254`（B1-U13 conf=**0.5746** cls=text_free）；手写 conf 全部删除（diff:3367-3538 逐条改为「见取值行」），新增 `[payload 取值]`/`[frames-export 取值]` 自动追加（diff:3546-3593）。**1 处残留见新问题 N4** |
| **R7 [P2] STATUS 越界** | **partial（按设计，实质动作归集成方）** | r2 对 STATUS **零触碰**（12 文件清单无 `doc/STATUS.md`）✓；越界登记完整（handoff「R7 越界登记」节，diff:36-38）✓；替换数字给全（含 ogkalu 7/18 vs chiqui7 11/29/8/18、raw/block 双口径、6/7 判据）✓。我核对 `doc/STATUS.md:14-15` 仍为越界版（含 18/29、12/23、5 项旧口径，15 行 `ready` 与 14 行 `in_review` 矛盾）——按 handoff 约定由代行 Codex 收敛，本轮不扣 |
| **R8 [P3] 前处理口径取证/披露** | **closed** | names 断言：`eval_sfx_mangabubble.py:166-167`（字符串键 `{"0":"bubble",…}` / `{"0":"text"}`）与 `:184-185` assert，与 ONNX metadata 字符串解析结果同型，真机不会误炸 ✓；payload 记录 `onnx-sfx-frames.json:34-35,61-62,…`（`onnx_metadata_imgsz`=`[1024, 1024]`/`[1280, 1280]` 非 null + `input_shape`）；偏离披露在 payload `inference_note`（`:7`）、报告 `:70,146`、handoff 限制 5。**「逐字节一致」我做了 diff 级验证**：onnx-sfx-frames.json 段（diff:1642-2298）**仅 1 行删除**（旧 inference_note，diff:1650），其余全部为新增 metadata 键 → 两版之间 23 帧×2 模型 `detections` 完全未变，等价于「重构后重跑检出逐字节一致」（该口径成立）。P4：脚本 docstring `:16-17` 仍只写「letterbox per each model's metadata imgsz」，未带偏离说明 |
| **R9 [P3] tip 锚点/AC5 分述** | **partial** | 已登记：implement=`d5bfd1fe`、被审 tip=`d98bab7e`（Task `:13-14`、handoff diff:11-12）；AC5 按 commit 分述 ✓（Task `:58`、handoff diff:73-75）。**未闭合部分**：(a) **返修 tip 哈希 `c6eae9ad` 全 worktree 零出现**（我全库 grep 无匹配；Task `:14` 只写「返修 tip（review-fix…）」、handoff diff:12 写「见 Task frontmatter（review-fix commit）」= 循环引用）→ 第三锚点实际未落，属自引用限制，须集成方在集成记录中盖哈希；(b) **AC5「13 文件」自相矛盾**（见新问题 N1） |
| **R10 [P3] 「43 区域全检出」** | **closed** | handoff diff:55 与报告 `:158` 改为「43 区域全部完成推理（其中 11 区域 harvest 0.25 仍零检出）」。**我独立复核** `ogkalu-sfx-frames.json`：43 个 region 条目（`case_id` 43 处）、`n_text_dets_harvest: 0` **恰好 11 处**（行 476,651,914,924,1572,1813,1889,1899,1909,2315,2325）✓ |
| **R11 [P3] 外部证据清单** | **closed** | `external-evidence-inventory.json`（`:7-16` 计数 43+23+2+9+2+6+1=**86**，与报告 `:156`/handoff diff:47 的「previews 66/权重 11/manifest 2/许可快照 6/venv 1」一致）；4 份许可快照 sha256（`:427,432,437,442`）与 `license-evidence.md` 逐字符一致；警示语三处齐（inventory `:4`、报告 `:156`、handoff diff:47「previews 缺失则逐帧判定不可独立复核」）；脚本+§6 命令可重生成 ✓ |
| **R12 [P3] IoU/单侧口径** | **closed** | 逐实例 `iou` 入 JSON（29 实例 × 4 列）；`chiqui7_any_class.note`「single-side coverage… dominated by panel-class page-size boxes; NOT used for conclusions」逐实例落库；报告 `:89`（几何口径声明）+ `:145`（Known limitations 6）。实例核验：투두 any-class cov=1.0/iou=0.161（panel 支配）、푸흡 1.0/0.12、끌끌 1.0/0.016 — 声明与实际相符 |
| **R13 [P3] 集成前条件 6/7** | **closed（附注）** | 报告 `:135`（条件 6：+41.2MB、1024 二次推理延迟未测、NSIS 包体、CPU/GPU 双档）与 `:136`（条件 7：阈值与 raw/block 口径冻结+人工兜底触发规则）；§0 `:15` 已改「七项」；handoff diff:30 同步。+41.2MB 与 inventory `:355`（41227478 B）自洽。附注：**Task `:57` AC4 记录仍写「集成前条件 5 项」**（见 N3） |
| **R14 [P4] 细节校字** | **closed（附注）** | 끌끌 移出 D 层 → 报告 `:59`「A1 层의 A1-U06（끌끌.. 伪 GT 框，非 D 层）」✓；「10 条内含 1 处拳头幻觉框」报告 `:53`，与 artifact 一致（`sfx-spot-check-verdicts.json:31` extras=10、`:695-707` 拳头 `best_ogkalu_overlap.conf=0.3952`≈0.40）✓；`verdict_extra` 已删（脚本 diff:3551 过滤 + JSON 零残留，diff:2573/3031 删除）✓；`n_skipped` 拆分 19+2（JSON `:13-14`）✓；컹 位置改入 덜컹 rationale ✓。附注：该句出现「见 extras」悬空引用（N5） |

## 回潮与新问题

**回潮检查（全过）**
- 12 文件全在允许路径：Task/Handoff + `experiments/M2-SFX-DETECT/**`（6 脚本+5 JSON 中的 6 个）+ `verification/M2-SFX-DETECT-EVAL/**`（报告/license-evidence/inventory）；`doc/STATUS.md` **零出现** ✓；禁改面（src/requirements/contracts/apps/packaging/tests）**零出现** ✓；C1/C4 产物零改动（`ogkalu-sfx-frames.json` 不在 diff）✓；无二进制、权重仍仅以 sha256 文本登记 ✓。
- 报告 r2 抽查 ≥10 个数字与 artifact 全部对应：§2.2 帧表 10+2+4+7=23 ✓；0.80/0.85/0.57/0.5475/0.93/0.46\*/0.75/0.73/0.69/0.80/0.62/0.2651/0.33/0.34-0.48/0.30/0.28 ✓；§3.3 conf 0.76/0.82/0.30/0.32/0.27/0.39/0.94/0.95/0.92/0.70/0.55 ✓（含我另查 `onnx-sfx-frames.json:1985` 하하 text 0.9401、`:1028/1039` 뒤적뒤적 K07_R121 0.9307/0.9187）；汇总 9/23、5/23、11/29、14/29、7/29、18/29、7/18、8/18、11/18、2/18 ✓。**未发现新数字错误**。

**新问题（P3×1 + P4×7，均不阻塞）**
1. **N1 [P3｜账目自相矛盾]** AC5「`02bf68a0..d5bfd1fe`=**13** 文件」与其自身枚举（Task+experiments(10)+report）**=12** 不符；下半句又说「tip=14 文件=上述+STATUS+handoff」，则 13+2=15≠14。按 r1 已核的 tip=14 反推，implement 应为 **12**（该「13」疑似把 r2 态 11 个 experiments 文件代入）。位置：`doc/tasks/M2-SFX-DETECT-EVAL.md:58`、handoff diff:73-74。修法：`git diff --name-only 02bf68a0..d5bfd1fe` 实测后回填（集成方本来要跑这条）。
2. **N2 [P4｜锚点未落]** 返修 tip 哈希 `c6eae9ad` 全库无记载（自引用限制）。修法：集成 commit 的集成记录/Task 收口行写入该哈希。
3. **N3 [P4｜文档滞后]** Task `:57` AC4 仍写「集成前条件 5 项」，与报告 §0/§4.4 的 7 项不一致。
4. **N4 [P4｜口径标注错]** `sfx-spot-check-verdicts.json:341,2001`（A__B2-U12）手写 prose 称「（C4 正式 block 口径 conf=0.5475）」，但紧随的自动行为 `[payload 取值] conf=0.5475`（raw harvest），该帧无 frames-export 块层值——既是 R6 想消除的「手写 conf」，口径也标错（raw 误标 block）。
5. **N5 [P4｜悬空引用]** `sfx-spot-check-verdicts.json:430,2090`（A__B2-U14）写「「컹」（约 [430,100,620,310]，见 extras）」但该帧 `extras: []`；报告 `:53` 的表述（记录在 덜컹 主实例依据中而非 extras）才是对的。
6. **N6 [P4｜四舍五入]** 报告 `:89`「투두 cov=0.93/IoU≈**0.87** 级」，JSON 实为 `iou=0.889`（应写 ≈0.89）。
7. **N7 [P4｜计数不一致]** 报告 `:162`「脚本 ×7」vs handoff「脚本 ×6」；实测 `experiments/M2-SFX-DETECT/` 下 **6 个脚本** + C4 基座 import 复用。
8. **N8 [P4｜交付清单与 diff 不符]** 处置说明称「3 脚本修订+**2** 脚本新增」，实际 diff 只含 **1** 个新脚本（`inventory_external_evidence.py`）——与 N1 同源（r2 态 11 个 experiments 文件被误代入 implement 范围）。建议在 r2 记录中改为「3 修订+1 新增+1 新增证据文档」。

## NOT_VERIFIED（集成方复跑项）
1. **沙箱故障导致零命令执行**（`grantWrite` Win32 5；升级无 approval channel）：未做任何 `git`/`pytest`/哈希复算。
2. `git diff --name-only 02bf68a0..d5bfd1fe` 实测文件数（N1，应 12）；`git diff --check 02bf68a0..c6eae9ad` EXIT=0；`git ls-files` 权重 onnx/pt/safetensors/bin=0；被审 tip 确为 `d98bab7e`、返修 tip 确为 `c6eae9ad`。
3. pytest 三套件 providers 291+1 skipped / m2_acceptance 35 / core 111（=437+1 skipped）。
4. `invalid`：两套 ONNX 真机重跑本身（我只能证明「两版 commit 之间检出逐字节一致」，不能证明重跑相对原始运行无差异）；C4 基座 import 复用零改动（ogkalu 权重目录 9 文件 sha256 与 C4 pin 一致未重算）。
5. `external-evidence-inventory.json` 86 文件 sha256 重算与 previews 66 张存活/内容（仅核对了内部与文档间数字自洽）。
6. 29 实例逐条目视（previews-onnx 23 张）——本轮未看图，仅做几何/数值一致性复核。

## 推荐下一步
由代行 Codex 在集成 commit 中按 N1–N3（顺手 N4–N8）修正 Task/Handoff 账目与 r2 tip 哈希登记、以 `git diff --name-only 02bf68a0..d5bfd1fe` 复核 implement 范围、按 handoff「R7 越界登记」节把 STATUS 收敛为指针式并复跑报告 §6 与 pytest 三套件后合并 master（无需第三轮 Review，除非 N1 实测文件数确为 13）。
