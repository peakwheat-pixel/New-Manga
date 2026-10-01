静态 Review 已完成（沙箱 `pwsh` 报 `SetNamedSecurityInfoW failed (Win32 5): grantWrite`，全程只读：`read`/`grep`，未执行任何命令，未读取 key 文件内容）。

---

## Verdict（approved / approved_with_conditions / changes_requested）

**changes_requested**

理由：交付的数字登记总体诚实、范围与 key 纪律全部成立（53 文件全落允许面、禁改面零出现、零 key 明文），但存在 **1×P1**：AC3 的核心归因（F5「远端译文浮动 + 渲染器忠实」）被交付物自身的证据反驳——BJ02 两次 run 同一 region 的最终译文不同（`所谓强大` → `所谓强啊`），两个 export PNG 却 sha256+size 逐位相同。这使报告 §5 的结论与「BJ02 PASS / K11 FAIL 根因」双双失去解释力，而 AC3 正是本 Task 三大交付之一。另有 5×P2（AC3 对照仅存 1/3 case、F1 归因表述与证据矛盾、F2 缺原始错误证据、ko G1 CER 排除规则单向偏低且 `cer-summary` 分母声明自相矛盾、相关口径未落文）。

返修面很小（报告 §5/F5 重写 + runner 对照文件合并写入 + 若干数字/文档），其余交付（AC1 全链数字、AC2 方法、AC6 探针、AC5 N1-N4 行号修正、AC4 方法学披露）可维持。若 Owner 能用 render/revision 层证据解释 R1（例如证明两次 export 并非各自 run 的产物、或渲染链不消费 Run2 结果），R1 可降级为 P3，本 Review 随即具备 `approved_with_conditions` 基础。

---

## 逐项核对表

| # | 审查项 | 结论 | 关键证据 |
|---|---|---|---|
| **A** | **F1 归因证据强度** | **部分成立（P2）**：前半（TA3-A 走 docTR、K01/K02 当时有 region）**有硬证据**；后半（「两 backend 页面形态域不同」）**与证据矛盾，应改述** | TA3-A：`experiments/M2-TA3-A/run_smoke.py` pin `fast_base-*.pt`（docTR）；`verification/M2-TA3-A/summaries/smoke-K01.json:14-15,20,29,43`＝690×62133 / `doctr-fast_base-pinned` / `region_count=15`。阶段二同一页：`qual-K01.json:12` 与 `smoke-K01.json:396` 的 `source_sha256` **同为 `600ca755…`**（K02 同型 `b1123355…`）→ 同一页面、不同 backend 检出能力，非「页面形态域不同」。0 候选的机制在交付物中**无适配器级证据**（`qual-K19.json:48-51` 只有 `status=EMPTY/region_count=0`，无 raw 文本框数/bubble 数/送入 tensor 尺寸）；`detection_manga.py:342-348` 把整幅长条漫不加 size 覆盖地交给 `RTDetrImageProcessor`（权重目录内 `preprocessor_config.json` 未入库，重缩放目标无法静态确认）→ 「整页重缩放致失效」是合理假设但**尚未被证据排除**（阈值/pad 无变更：`detection_manga.py:98` conf 固定 0.5，MERGE_* 由 `detection_doctr` import）。Fix 建议 A（tiling / per-family 路由）方向合理，但归因证据需补 |
| **B** | **F2 归因** | **成立但原始证据缺失（P2）**；与 TA3-A **不矛盾**（已核对） | TA3-A 5 case 确为 BJ02/BJ06/K01/K02/K11，K07/K09/K10 未跑过 → 无矛盾。`src/infrastructure/importing.py:45-59` 是唯一 `QImageReader` 使用点且**未设 allocation limit / 无 256 常量** → Qt 内建默认，归因方向正确。尺寸链自洽：K07 690×131289×4B≈345.6 MiB、K09≈264.5 MiB、K10≈265.0 MiB，F1 五例全部 <256 MiB 且 import OK（`qual-K01.json:40-45`）。**但**报告引用的 Qt 原文（`quality-report.md:47,127`）在仓库内**无原始日志**；三份 summary 的 import 错误被截断为空 detail：`qual-K07.json:42`＝`"RuntimeError: import failed: 1 failed"`（`run_qualification.py:356-361` 在 per-file error/detail 皆空时产出空串）→ 该字符串目前只有作者自述 |
| **C** | **AC2 ko G1 CER 有效性（n=6）** | **数字可核、方法有偏（P2）** | n=6 属实（`cer-summary.json:8,17-18`；`cer-regions.csv` 恰 6 行 `G1:svg_native`＝第 58/61/62/63/64/69 行）；69 数据行＝6 G1＋13 排除＋50 G2，与 Owner 称一致。**幸存者偏差成立**：排除规则（`measure_cer.py`：命中 0→UNALIGNED `:224`、>1 元素→`:226-229`、OCR 空白→`:230-233`、`char_overlap<0.3`→`:234-237`）把 K11 13 行剔掉 7 行，其中 `cer-regions.csv:70`（K11:65069961，GT=`당근아!`、OCR 空、`qual-K11.json:556-565` 且 ocr 步 `completed`）是**真 OCR 失败、CER 恒 1.0 却被剔除**；手算其余被剔行 9a30cdf6=0.5、df871de5=1.0、dadc7e00≥0.69 → 若计入其中 3 行，中位数 0.0556→0.2727（FAIL）。精确反事实受「多元素 GT 为拼接非真值」限制（数据不足）。另 **6 行中 3 行是同一条短串 `당근아?`**（`:58,61,62`），有效独立文本仅 4 种，报告未披露。`cer-summary.json:5` 自述 `denominator="all detected regions of the G1 cases"` 与实际 6/13 口径矛盾；`:103,110,117` 的 alignment_notes 只列「多元素/低重叠」两类排除，**漏 UNALIGNED 与 empty-OCR 两类**。ja 侧 NOT_AUTOMATED 判据与代码一致（0.3 常量），但 `quality-report.md:70,79` 的「J46 混入 4 个元素」（实为 4 元素中 3 命中，`cer-regions.csv:52`＝`MANUAL_REVIEW:3-svg-elements`）与「J47 重叠 0」（按 char_overlap 手算≈0.167，唯一共有字符「う」）**表述不准**。thresholds 的 ko G1 行（`quality-thresholds.md:76,195`）**未携带 n=6/0.0556/排除规则** |
| **D** | **AC3 确定性 + F5 三段证据链** | **不成立（P1）** | 三段证据中，「0/13 OCR 差异」可核（两次 K11 summary 的 ocr_text 逐条相同）、「7/13 译文浮动」可核（分母略混用：13 行中 2 行为空译文，非空口径为 7/11）、「渲染器忠实反映输入」**无任何可核对证据**（phase2 内无 renderer 层哈希、无渲染输入 diff），且被 `quality-report.md:142` 自述「渲染器无差异证据」与 `:16,130` 的断言互相矛盾。**决定性反例**：`qual-BJ02.json:177-186`（region `aa2bd2a2…`，bbox 2222,3051,319,500）`translated_text="所谓强大"`（`:331-334`）vs `qual-BJ02.rerun.json:177-186`（region `d90b0fca…`，**同 bbox 同 reading_order=4**）`translated_text="所谓强啊"`（`:331-334`），两次 `run2` 均 5/5 completed 无截断（`:201-207`），而 export **sha256 均 `5c74a4f0…`、size 均 8759037**（`qual-BJ02.json:351-352` vs `.rerun.json:351-352`），`translated_revision_id` 却不同（`7f7626c0…` vs `d7adba58…`）。若渲染对 region 译文敏感，两次 PNG 不可能字节相同；若渲染不敏感（例如导出的是 Run1 页面级 render），则 BJ02 的「PASS」对 translate→render→export 链**是空转**，K11 的哈希不一致也不能由「Run2 译文浮动」解释。附带观察：region_id 每次 run 重新生成（同 bbox 不同 uuid），逐位比较只能按 reading_order 对齐，报告未登记该事实。TA3-A（mock translate）与本 Task（真实 remote）的口径差**未写入权威文档**：`quality-thresholds.md:168,202` 仍无条件要求「export 哈希逐位一致」，全文无 F4/F5，修订只在报告里「建议」（`:130,145,171,181`） |
| **E** | **AC6 探针** | **PASS（附 P4 限定）** | `translate-probe.json` 完整落盘接入序列：profile 写入 `save_settings_section`+`make_credential_ref`（`:14` 记 `NewManga/provider/ta3b-translate-key`，仅约定串）→ 同 db re-assemble 落 `MISSING_CREDENTIAL`（`:22`）→ re-register+invalidate → `ready`（`:38`）→ 真实 region 翻译 `elapsed_s=0.45`（`:43`）；时间戳 `09:43` 早于主 run `09:52`（第 0 步时序成立）。脚本侧：key 只取自 env（`translate_probe.py:61,224`）、resolver 只读 `os.environ`（`:162`）、记录只留 host/model/ref。**限定**：该 READY 的 descriptor 只含 `KIND_ENDPOINT` 要求、无 `KIND_CREDENTIAL`（`translate_probe.py:146-154`），故 READY **不等价于生产描述符的 READY 语义**（探针 docstring 已自述，报告 §0/AC6 行宜加一句）；`translate_probe.py:290-292` 把异常原文写入入库记录（截 400 字），理论上存在端点回显 Authorization 的泄漏路径（实测产物无） |
| **F** | **范围纪律 + key 纪律（含 F6 边界、像素出库）** | **范围 PASS；key PASS；F6 合规 PASS；像素登记 P3** | 53 文件逐条核对：`doc/tasks` 2 + `doc/handoffs` 1 + `experiments/M2-TA3-B` 5 + `verification/M2-TA3-B` 45（plan 1+env 1+export 1+inpaint 2+ocr 9+summaries 25+probe 1+translate 3+报告 2）；`src/**`、`tests/**`、`requirements.txt`、`packaging/**`、`apps/**`、`doc/contracts/**`、`experiments/M2-TA3-A/**`、`doc/STATUS.md` **零出现** ✓。`doc/tasks/M2-TA3-B.md` 改动恰为「阶段二启动条件」一行（允许面「仅阶段二指针/状态行回填」）✓；`quality-thresholds.md`/`phase2-plan.md` 在 `verification/M2-TA3-B/**` 内 ✓。key：`sk-` 命中全为 `task-envs` 路径子串、`sk_[A-Za-z]` 命中全为 `"step_type":"mask_refine"` 误报；无 `Authorization`/`eyJ`/`token=`/`DEEPSEEK_API_KEY` 字面量；`build_worksheets.py:111` 的 `Bearer {key}` 是运行期拼装、无字面值；三个脚本均无读取 key 文件内容的分支 → **硬纪律成立**。F6：写入落在 `tempfile.mkdtemp()/library.sqlite`（`run_qualification.py:272-274`），run 末 `close+rmtree`（`:579-586`），无生产 db 污染；走生产通道 `save_settings_section`（`pipeline_defaults.py:105-120`，整节覆盖语义）+ `handlers.py:329`/`ports/ocr/ports.py:26` 语义源可核 → **合规**。像素：落 `G:\CODEX\New Manga.task-envs\M2-TA3-B\phase2-pixels\`，路径散记于 summary 与三份工作表，**无清单/size/sha256**；且"理由=`.gitignore` 在禁改面"不成立——该目录是仓库树**之外**的兄弟目录（repo/worktree 内均无 `task-envs`，已实测 `rg` IO error），Git 天然不可见，无需 .gitignore 规则 |
| **G** | **AC4 方法学** | **披露充分（通过），覆盖有 P3 缺口** | n=26 属实（ja15+ko11，工作表 38 行 CSV 逐条可数）；`dialogue-readability-worksheet.json:7` 明写 `ai_prefill = DeepSeek self-evaluation (self-anchoring risk declared); user audit = only verdict`，`:18-33` 登记 owner 6-crop 校准（4 ko 对齐 + 2 ja 译文，方向一致、轻度偏高，BJ06:fb648685 忠实 5→owner 判 4），报告 `:113` 明写「参考非判定」。**缺口**：AC4 字面要求「n≥30 + 含 BJ06/BJ10 SFX 示例」→ 实际 n=26 且**零 SFX 条目**（生产 SfxPolicy 默认 SKIP）；n 缺口已登记（报告 `:112`/handoff `:55`），但 SFX 缺口只在 §3.1/§8 登记，**AC4 行（`quality-report.md:17,113`、Task `:58`）未标**。`pool_sizes.ja=48` 与 per-case `n_translated` 合计 48 一致（可核） |
| **H** | **文档精修 AC5（N1/N2/N4/N5/N6）** | **N1/N2/N4/N5 落地且行号经我独立复核为真；N6 越界 + R8 未同步（P3）** | N4 逐条验证：`core_assembly.py:484-498`（`_load_pipeline_settings`）、`:501-514`（`_credential_store` 可 None）、`:779`、`:782`、`pipeline_defaults.py:105`（upsert+commit、整节覆盖）、`ports/providers/credentials.py:25`（`make_credential_ref`）、`registry.py:105/302`、`translate_openai.py:37,136`（`SAKURA_DEFAULT_BASE_URL` 为 `sakura_config()` 默认形参值）、`handlers.py:329` —— **全部命中**。N1 落地于 `quality-thresholds.md:64,66,76,88,105,195` ✓；N2 落地于 `doc/tasks/M2-TA3-B.md:86`，旧 handoff 属禁改面**正确地未触碰**并登记 ✓。N6：`phase2-plan.md:192` 把 token 口径改为「数十万以内」——Task 纪律是「预估 ≤ 数万 token 量级，超预期即停并登记」，而 N6 范围只含「估时回看」，属**未登记的口径放宽**。R8：`quality-thresholds.md:64` 仍写「ep04/ep20 各 472」，与 `svg-gt-manifest.json:8,26,36`（ep20=352、ep04=472、K19 text=0）冲突，未加修正注。另 `phase2-plan.md:24` 仍写阶段二「真实 docTR detect」，与 `run_qualification.py:9,306` 的 ogkalu 不符（AC5 漏同步） |
| **I**（补充，重点 5/8/10） | **F6 边界 / 像素出库 / 成本** | F6 PASS；像素 P3/P4；成本 P3 | 见 F 行与 R7/R8/R11。成本：产物**无** requests/usage/prompt_tokens/completion_tokens 字段（`qual-report.json` 仅 region/timing；`translate-probe.json:43` 仅 elapsed）→ 请求数可间接推导（Σ(1+region)=69 + rerun 20 + 探针 1 + 自评批 ≈3 → 93–104，与「约 100」一致），**token 量完全无证据** |

---

## Findings

> 说明：以下行号均为 worktree 实文件行号；标「子代理核对」者为并行只读核查后我抽样复验一致的项。

**R1｜P1｜AC3/F5 根因链未闭合：BJ02 同 region 译文不同而 export 逐位相同，与「渲染器忠实反映输入」不相容**
文件：`verification/M2-TA3-B/phase2/summaries/qual-BJ02.json:177-186,201-207,331-334,346-353`；`qual-BJ02.rerun.json:177-186,201-207,331-334,346-353`；`verification/M2-TA3-B/quality-report.md:16,130,142,145`
两次 run：同 bbox(2222,3051,319×500)/同 reading_order=4/同 source `強いってのは`，`translated_text` 分别为 `所谓强大`（首跑）与 `所谓强啊`（复跑），run2 均 5/5 completed 无截断；export `sha256=5c74a4f01e05…`、`size=8759037` 两次完全相同而 `translated_revision_id` 不同。渲染链自 `reader_page.translated_path` 取字节（`run_qualification.py:527-557`），故「两次 PNG 字节相同」意味着**这两个 PNG 中至少有一个不反映本轮 Run2 的 region 译文**。
建议：Owner 补 render/revision 层证据（导出 PNG 由哪个 revision 产生、页面 render 在 Run1 还是 Run2 落地、Run2 译文是否触发重渲染），据此二择其一修正报告——
(a) 渲染对 Run2 region 译文不敏感 → BJ02 的确定性 PASS 对 translate→render 链是空转，AC3 需重新设计正例；F5 只能表述为「export 非确定，根因未隔离」；
(b) 记录失真 → 修 runner 的 export 记录口径。
无论哪种，`quality-report.md:145`「TA3-A 确定性框架在输入确定前提下继续成立」与 §8 的 F5 口径修订建议都应暂停，直到本条闭合。同时建议登记「region_id 每 run 重新生成，逐位比较按 reading_order 对齐」的方法学事实。

**R2｜P2｜AC3 交付物只含 1/3 指定 case（BJ02/K01 对照记录被覆盖丢失）**
文件：`verification/M2-TA3-B/phase2/summaries/rerun-compare.json:2-10`（仅 K11）；`experiments/M2-TA3-B/run_qualification.py:791-794`（每次调用整体覆盖该文件）
`phase2-plan.md:17,33` 明确要求 `--rerun-check BJ02,K01,K11` 固定 3 case 的 sha256 逐位比对。BJ02/K01 数据可由 `qual-*.rerun.json` 恢复（我已据此复核 BJ02→R1、K01→region=0 支持 NOT_ACHIEVABLE），故证据面可复核，但**交付 artifact 不满足所声明的对照**。建议改为合并写入（保留历史）并补一份 3-case 对照 JSON。

**R3｜P2｜F1 归因表述与证据矛盾；`phase2-plan.md:24` 未同步**
文件：`quality-report.md:126`；`doc/handoffs/M2-TA3-B2-3c8801b7.md:43`；`phase2-plan.md:24`
「两 backend 的页面形态域不同」被同页同 sha256 的证据反驳（`smoke-K01.json:396`=`qual-K01.json:12`=`600ca755…`；K02 同型）。应改述为「**同一页面上 docTR 有 15/7 个候选、ogkalu 路径 0 候选**：0 候选的适配器级机制（整页重缩放 vs 分块）尚无证据，产出建议 A 前需先补 `n_text_raw/n_bubble/送入 tensor 尺寸` 等适配器可观测值」。同时 `phase2-plan.md:24` 仍写「真实 docTR detect」，与 `run_qualification.py:9,306`（`manga-ogkalu+chiqui7-sfx`）矛盾，应在 AC5 范围内补一行修订。

**R4｜P2｜F2 引用的 Qt 错误原文无原始证据物，summary 错误被截断为空 detail**
文件：`quality-report.md:47,127`；`qual-K07.json:42`、`qual-K09.json:42`、`qual-K10.json:42`；`run_qualification.py:356-361`
归因方向（Qt `QImageReader` 内建 256MB 上限，`importing.py:45-59` 无 allocation limit 设置点）与尺寸边界自洽，但引用的 `QImageIOHandler: Rejecting image…` 在仓库内无日志档、summary 只留 `RuntimeError: import failed: 1 failed`。建议：复跑 K09 一次并把 importer 的 per-file `error/detail`（未截断）落盘入库，或把该行改为「推断（尺寸边界 + Qt 内建默认）」，不引用未归档原文。

**R5｜P2｜ko G1 CER 的排除规则单向偏向低 CER；`cer-summary` 分母声明与实现矛盾；排除规则未进入 thresholds**
文件：`verification/M2-TA3-B/phase2/ocr/cer-summary.json:5,8,17-18,103,110,117`；`cer-regions.csv:58,61,62,70`；`measure_cer.py:224,226-229,230-233,234-237`（子代理核对）；`quality-thresholds.md:76,195`
被剔的 `K11:65069961` 是真空 OCR 的**真失败**（CER 恒 1.0）却被排除；`cer-summary.json:5` 写「denominator=all detected regions of the G1 cases」而实际是 13 中取 6；`:103,110,117` 的 alignment_notes 漏列 UNALIGNED/empty-OCR 两类排除；6 个样本中 3 个是同一条 4 字短串。建议：(1) `cer-summary.json` 增加 `excluded[]`（计数/原因/若计分 CER）并修正 denominator 文案；(2) 报告 §2.3 明写「剔除集内含 1 条 CER=1.0 的真失败，剔除方向系统性偏低，故 0.0556 是下偏统计量；6 行中 3 行为同一短串」；(3) thresholds 的 ko G1 行同步 `n=6` 与排除规则；(4) 顺带修正 `quality-report.md:70,79` 的 J46「4 个元素」/J47「重叠 0」表述。**注**：Owner 已在 `quality-report.md:94,165` 明确「不建议以本 run 数字调阈值」，本条属可引用性/披露问题，不是数字造假。

**R6｜P3｜交付文档中若干数字与产物不符（同一交付内自相矛盾）**
(a) **ja region 数「53」错**：`quality-report.md:14`、`doc/handoffs/…:12`、`doc/tasks/M2-TA3-B2.md:55` 写 53，而 per-case `region_count`（`qual-report.json:13,26,39,52,65,78,91,104,117,130`）合计 **56**（53 无法由任何口径复原；48 翻译与 56−8 SFX 相符）。
(b) **K19 尺寸错**：`quality-report.md:52,126` 写 2481×3508，实测 source/page 均 **1200×1660**（`qual-K19.json:23-24,41-42`）；2481×3503 是 SVG canvas（`svg-gt-manifest.json:37-40`）。
(c) **SFX 分布错**：`quality-report.md:106` 写「9 个（全部在 BJ06）」，而 `sfx-semantic-worksheet.csv:9` 与 `cer-regions.csv:70` 均含 `K11:65069961`（`region_type=sfx`），`cer-summary.json:121` 亦为 9 → 实为 8 BJ06 + 1 K11。
(d) **pipeline_failures=10 的构成未登记**：9 例 case 失败 + rerun 集合 1 次失败（`run_qualification.py:725-726,795-796`，K01 的 NOT_ACHIEVABLE 也被计入该 1），报告中 10 的出现方式（`:14,54`）易被误读为 9+K11 的区域级失败。建议附表逐条列出 10 个单位。

**R7｜P3｜`export-hash-recompute.json` 无生成脚本、无像素路径、不含 rerun 导出**
文件：`verification/M2-TA3-B/phase2/export/export-hash-recompute.json:3,4,98-104`；53 文件清单中无对应脚本
artifact 自述 "this script only reads the pixel files and the summaries"，但脚本未入库 → 「runner 之外独立复算」不可复现；记录只含 `case_id + summary_sha256/recomputed_sha256/size`，无被哈希文件的路径，且不覆盖 `BJ02.rerun`/`K11.rerun` 两个导出。建议入库生成脚本（或加 `run_qualification.py --verify-exports` 子命令）并登记像素相对路径。

**R8｜P3（附 P4 理由错误）｜像素产物无清单/哈希，出库理由与事实不符**
文件：`quality-report.md:27`；`run_qualification.py:37-41`；`ocr-spot-check-worksheet.csv:2-…`、`inpaint-spot-check-worksheet.csv:2-9`
像素根 `G:\CODEX\New Manga.task-envs\M2-TA3-B\phase2-pixels\` 是仓库树之外的兄弟目录（已实测 repo/worktree 内均无 `task-envs`），Git 天然不可见，"`.gitignore` 在禁改面"的理由不成立（无需改；根 `.gitignore` 仅覆盖 `__pycache__/*.pyc/.pytest_cache/.venv/build/dist/*.safetensors/*.pt/*.onnx`）。实质缺口是**无清单**：路径散记于 summary + 三份工作表，无数量/size/sha256 → 外部树一旦变动不可复核（前例 `M2-SFX-DETECT-EVAL` DSH r1 R11 已要求「外部证据复核前提清单」）。建议补 `phase2/pixels-manifest.json`（总数 + 相对路径 + size + sha256）并修正理由表述。

**R9｜P3｜确定性口径（thresholds §5）与报告 §5 结论冲突且未落文**
文件：`quality-thresholds.md:168,182,202`（仍无条件要求 export 哈希逐位一致、无 F4/F5）；`quality-report.md:130,145,171,181`（只「建议」修订）
F4/F5 作为新发现的 Codex/用户裁决点保留是**正确的**，但在权威文档加一行 `superseded-pending（见 quality-report §5/F4/F5）` 成本极低，可避免后续读者据已证伪口径执行。阈值数值本身未被 Owner 单方改动（合纪律）。

**R10｜P3｜AC5 未同步 R8 计数；N6 越界放宽 token 口径**
文件：`quality-thresholds.md:64`（「ep04/ep20 各 472」未加修正注，与 `svg-gt-manifest.json:8,26,36` 冲突）；`phase2-plan.md:192`（「预估总 token 数十万以内」vs Task 纪律「≤ 数万 token 量级」）
N6 定义为「取消截断后估时回看」，token 上限的放宽超出该范围且未登记为待裁决项。

**R11｜P3｜成本声称缺计量证据**
文件：`qual-report.json`（无 usage 字段）；`translate-probe.json:43`（仅 elapsed）
「约 100 次请求」可间接支持（Σ(1+region)=69 + rerun 20 + 探针 1 + 自评批 ≈3）；「<10 万 token」**完全无证据**，且 K07/K09/K10 属 import 失败 0 请求（`wall_s` 0.08–0.11）应在成本基线中扣除。建议 runner/探针落盘每请求 `usage`（prompt/completion/total）与请求计数；本次至少把结论改述为 estimated。

**R12｜P3｜AC4 未达字面要求（n<30 已登记，SFX 示例缺口未挂在 AC4 行）**
文件：`dialogue-readability-worksheet.json:7-8`（n=26）；`quality-report.md:17,106,112,113`；Task `:58`
AC4 要求「n≥30 region（含 BJ06/BJ10 SFX 示例）」。SFX 因生产 SKIP 无法产生译文（原因确凿、已披露），但 AC4 行宜显式写「SFX 示例缺失=生产通路前置条件未满足」，与 n 缺口一并挂账。

**R13｜P4｜AC6 探针的两处硬化项**
文件：`translate_probe.py:146-154`（descriptor 仅 `KIND_ENDPOINT`）；`:290-292`（异常原文入库，截 400 字）；`run_qualification.py:303,329,368,704,768`（同类未 scrub）
(1) READY 是「endpoint-only descriptor」语义，口径应与生产 `MISSING_CREDENTIAL` 语义区分（探针 docstring 已自述，报告宜加一句）；(2) 统一在落盘前 scrub `os.environ[ENV_KEY_NAME]` 的值，关闭「端点错误回显 → key 入库」的低概率路径（硬纪律的最小加固）。

**R14｜P4｜base 元数据不一致（静态不可判定）**
文件：`doc/tasks/M2-TA3-B2.md:13`（`base_commit: 521d0bdd`）；`doc/handoffs/M2-TA3-B2-3c8801b7.md:3,5`（base `521d0bdd`）vs 本次 review 对象给定 base=`69137837`（diff=`69137837..81e5ad81`）。已核实的是**内容面**：该 diff 的 53 文件全在允许面、禁改面零出现；但 Owner 的禁改面自检基于 `521d0bdd..HEAD`，若两者非同一条链，则自检范围与交付范围不重合（`M2-OCR-PADDLE3X-1` DSH r1 R6 同型先例）。集成方以 git 事实定案并回填。

**R15｜P4｜脚本注释/死代码与实际不符**
文件：`build_worksheets.py:20-22`（称自评「30 short requests」，实际 n=26 分 3 批）；`measure_cer.py:25-26,44-47`（声称产出 n=30 工作表与标签常量，实际由 `build_worksheets.py` 产出 28 行骨架）

**已确认成立、无需返修的要点（摘要）**：53 文件范围纪律与禁改面零出现；key 零明文（含 `sk-`/`Bearer`/`Authorization` 程序化扫描与三脚本 env-only 取值路径）；AC5 N4 全部行号引用为真（`core_assembly.py:484-498/501-514/779/782`、`pipeline_defaults.py:105`、`credentials.py:25`、`registry.py:105/302`、`translation_openai.py:136`、`handlers.py:329`、`ports/ocr/ports.py:26`）；F6 因果链（`handlers.py:329` 默认 japanese → `ocr_local.py` korean/latin 拒绝）与临时库无副作用；F2 尺寸边界链自洽；`INVALID_INPUT` typed fail-closed 语义正确、三向归因齐全；AC6 第 0 步时序与真实翻译成功；R8 正式计数（ep20=352/ep04=472/K19=0 文本元素）已落盘为机器可读 manifest。

---

## NOT_VERIFIED（集成方运行时项；本 Review 无 shell，未执行任何命令）

1. `521d0bdd` / `69137837` / `81e5ad81` 的 git 关系；`git diff --name-only 69137837..81e5ad81` 是否恰为 53 文件；禁改面专项 diff 是否为空；`git diff --check` EXIT=0；`git status --porcelain` 干净（R14/F）。
2. **R1 的最终判据**：对 `phase2-pixels/export/BJ02-translated.png` 与 `BJ02.rerun-translated.png` 实算 sha256（或重跑一次 BJ02 rerun），确认「译文不同而字节相同」是渲染机制事实还是记录失真。
3. K07/K09/K10 的 Qt 原始 import 错误复现（importer per-file `error/detail` 未截断）→ R4。
4. K11 两次 run 的 render/revision 链路复现（导出 PNG 来源 revision、Run2 是否触发重渲染）→ R1。
5. 全量重跑（断点续跑语义 + `--force`）；AC1 的 wall_s 与 OCR/渲染耗时未独立复算。
6. 像素外部树存活与 sha256（无清单，R8）；权重目录（ogkalu 三文件 pin）、融合 venv、`pip check` 未独立复核。
7. 产物内无 requests/usage 字段 → 「<10 万 token」不可核对（R11）；`__pycache__/*.pyc` 未反汇编。
8. 三份人工工作表（n=26 / n=28 / n=8）与 G2 50 行的用户审核结果（后续步骤，非本 Task 关闭条件）。

---

## 集成方闭合清单

1. **git 面门禁**：用 `git merge-base`/`git log --oneline --graph` 定案 `521d0bdd` 与 `69137837`/`81e5ad81` 的关系，跑 `git diff --name-only <base>..<head>`（应 53 文件）、禁改面空、`git diff --check` EXIT=0、`porcelain` 干净；按结论回填 `doc/tasks/M2-TA3-B2.md:13` 与 handoff §base（R14）。
2. **闭合 R1（阻塞项）**：实算两个 BJ02 export PNG 的哈希；若确认相同，要求 Owner 提交 render/revision 层解释，并重写 `quality-report.md` §4-F5/§5/§8 与 handoff §3，暂停「TA3-A 确定性框架继续成立」与 F5 口径写入；若不同，则修 summary 的 export 记录口径并同步报告。
3. **回归 Owner 返修（P1/P2）**：R1/R2（runner 合并写入 + 3-case 对照）、R3（F1 改述 + `phase2-plan.md:24` 同步）、R4（Qt 原文归档或改述）、R5（CER 排除清单/分母/方向性披露）。
4. **P3 批量同修**：R6（53→56、K19 尺寸、SFX 分布、J46/J47 描述、pipeline_failures=10 构成）、R7（复算脚本入库或子命令）、R8（pixels-manifest + 理由表述）、R9（thresholds §5/§1 superseded 交叉引用）、R10（R8 计数注 + N6 token 口径回退）、R11（usage 落盘或改述 estimated）、R12（AC4 行显式挂 SFX 缺口）。
5. **P4 顺手清理**：R13（探针 READY 限定 + key scrub）、R15（docstring/死代码）。
6. **裁决移交（不由集成方自裁）**：Task 建议 A（webtoon 长条漫检测）/B（大图导入 allocation limit）的释放与优先级、F4（detect 冒烟口径）与 F5（确定性口径）修订、SFX→translate 产品入口需求、O-1/O-2/O-3 与 T-1/T-2。
7. **`doc/STATUS.md` 收敛由集成方执行**（Owner 全程零触碰，正确）；同时登记 main 与主仓的集成修正 commit（含已知的 `ocr_local.py` ndarray 直通一行适配，本分支不含，属非 Owner 责任）。
8. **用户侧并行不阻塞**：三份工作表 + G2 50 行 GT 审核；像素外部树在审核期间需保持存活（或先补清单/哈希）。
9. **集成门禁复跑**（前例口径）：`PYTHONPATH=src <主venv>/python -m pytest tests/providers tests/m2_acceptance tests/core -q -rs` + 两 worktree 的 diff 范围核对，任一不过回落 Owner 修链而非直接合入。

---

## 推荐下一步（一句）

请编排会话（代行 Codex）先执行闭合清单第 1–2 条（git 事实定案 + 两个 BJ02 export PNG 实算哈希以裁决 R1），据此决定是退回 Owner 修链（重写 §5/F5 + runner 对照合并写入 + R3–R5）还是转入集成。
