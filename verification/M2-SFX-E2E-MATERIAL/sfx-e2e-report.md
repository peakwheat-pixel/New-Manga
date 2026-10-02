# M2-SFX-E2E-MATERIAL：SFX 翻译端到端验证与素材扩展报告

- Task：[M2-SFX-E2E-MATERIAL](../../doc/tasks/M2-SFX-E2E-MATERIAL.md) · 分支 `agent/zcode/M2-SFX-E2E-MATERIAL` · base=`73252798` · 日期 2026-10-02
- Owner=ZCode · Reviewer=DeepSeek Harness（非作者，待 review）· Integrator=代行 Codex（用户全权授权+自治授权）
- 授权：用户裁决 2026-10-02 七项之④（SFX 素材寻找/下载/测试全权授权）
- **证据强度裁定（全程适用）**：BJ06 跑与全部质量表述为 **directional**（单一 remote 采样 provider、无 SFX GT、单页/三页样本）；「文化对等为方向性抽检非 Gate」（Task AC4 纪律）。检测域发现的数字同样 directional（单 AI 标注者目检 + 单模型诊断，沿 [M2-SFX-DETECT-EVAL](../M2-SFX-DETECT-EVAL/sfx-detect-eval-report.md) 的证据强度口径）。
- 生产面零改动：`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**` 未触碰；既有 case 产物、首跑/KO-RERUN 产物、`doc/STATUS.md` 零 diff；manifests 只增不改（cases.json 97→100，+214/-0 行）。

## 0. 结论速览

| 交付 | 结论 |
|---|---|
| AC1 BJ06 端到端（policy=translate） | **闭环达成**：chiqui7 检出 17 region（8 sfx + 9 speech，与首跑 bbox/类型/序号逐条一致、region_id 每跑重生成）→ SFX gate 放行 8/8（`sfx_policy=translate`）→ DeepSeek 翻译落库 **8/8 非空**（`final_source=machine`）；speech 9/9 正常翻译不受扰（8/9 与首跑逐位一致、1/9 语义等价合法重译）；34 请求 ≈20.2k est token；export OK。**SFX 家族链 DETECT→PROD→SEM→ENTRY→PRIMARY 全链最终闭环实证完成** |
| AC2 素材搜寻与核定 | densho810 BJ 官方卷路线（优先级 a）胜出：许可一手快照在案（sha256 `2bb1dc9f…`），vol03 全卷 221 页目检，择优 3 页入池（BJ13/BJ14/BJ15），checksum 与 case 登记齐全，署名/报告义务沿 TA2B 框架 |
| AC3 新素材端到端 | **链路 PASS（3/3 pipeline_completed、export OK）+ 检测域缺口如实登记（r1 修订）**：chiqui7 sfx 类对 BJ 大型毛笔竖排 SFX 召回为盲区（7 个目检 SFX 实例：sfx 类 0 命中、7/7 均有非 sfx 类框覆盖——整页 panel 大框与同位置 text/bubble 框并存、混淆归属未定；BJ13 唯一 sfx region 为 T 恤印花误报，其 OCR『．．．』→『……』仍完整走通 gate→翻译落库）。**误路由损害（r1 R1 新增）**：BJ13 两处目检 SFX（ピ一一ーン！×2）被判 `region_type=speech`，走对话链产出乱译（「いやー、」→「哎呀——」、「Ｗｉｆｉｘ」原样保留）并 export 渲染——**错误译文已进渲染页**；该损害与 SfxPolicy 无关，SKIP 默认下同样发生 |
| 合并 SFX 端到端能力结论 | **翻译语义链（gate 放行→SEM-1 prompt 特化→译文落库）在 ja 域实证工作**（BJ06 8/8 + BJ13 1/1）；**检测段是当前 SFX 端到端覆盖的真实瓶颈**——BJ06 的 8 个 sfx region 是「检出且有文本」的恰好素材，新素材的毛笔 SFX 形态暴露 chiqui7 的域外混淆（panel/text 框并存、归属未定），且盲区的用户可见损害不止「漏检无 region」：SFX 误路由 speech 后经对话链乱译并进渲染（与 SfxPolicy 无关）。检测域扩展（阈值/后分类/再训练）= 未来 Task + 用户裁决范畴（DETECT-EVAL §4.4 清单既存），本 Task 零生产改动 |

## 1. AC1：BJ06 端到端（policy=translate，先行交付）

### 1.1 运行登记

- 命令：`run_qualification.py --case BJ06 --sfx-policy translate --determinism-track remote --meter-translation`（harness=KO-RERUN 判轨控件就绪版，零改动复用）；独立 `--out-dir verification/M2-SFX-E2E-MATERIAL/bj06-run/summaries` + 独立 pixel-root（`task-envs/M2-SFX-E2E-MATERIAL/pixels`，与并行 KO-FULLRUN 零文件交集）。
- key 经 `TA3B_TRANSLATE_API_KEY` env 注入（`$(cat …/deepseek.key)`），记录经 `scrub_secrets`，**零明文**。
- 产物：`bj06-run/summaries/qual-BJ06.json` + `qual-report.json` + `run.log`；export PNG/sha256 在 pixel root（Git 外）。
- 判轨：declared=remote=inferred（DeepSeek binding），fail-closed 校验通过。

| 项 | 值 |
|---|---|
| pipeline_completed | `True`（run1 completed 357.6s + run2 completed 336.9s，17/17 region 零 defect，export OK sha256 `c1d503f49a341ade…`） |
| wall | 695.8s |
| 检出 | 17 region = 9 speech + **8 sfx**（chiqui7 conf≥0.5；与首跑同 region 数、同类型分布、sfx bbox 逐条相同——region_id 每跑重生成，检测确定性跨 run 复现） |
| gate | sfx region `sfx_policy` 字段实测 `translate` ×8（首跑全 `skip`）；speech region 9 个不受门影响正常翻译 |
| 落库 | **SFX 译文非空 8/8**（`translated_text` 与 `final_translation` 非空、`final_source=machine`）；speech 9/9 |

任务书背景写「BJ06 含 9 个 SFX region」，实测检出 **8 个 sfx region**（+9 speech=17）。偏差来源（r1 R8 精确化）：「9」是 M2-TA3-B 的合计口径残留——`sfx-semantic-worksheet.csv` 共 9 行 = 8 BJ06 + 1 K11，`verification/M2-TA3-B/quality-report.md:120` 写「9 个（8 BJ06 + 1 K11）」，该合并口径此前已在 M2-TA3-B2 review r1 被更正过（`doc/reviews/M2-TA3-B2-81e5ad81-dsh-r1.md:62`），任务书背景沿用了未拆分的合计数；与 KO-RERUN 报告 §3.2「ja BJ06 类素材（8 个有文本 sfx region）」一致——以实测 8（BJ06 域内）为准，登记为口径沿用偏差（不影响任何验收逻辑）。

### 1.2 K11 教训核销（素材缺口不在 BJ06）

首跑 BJ06 的 8 个 sfx region OCR **全部非空**（`いいじゃ`/`いいん`/`！！！`/`．．．`×2/`ハチン`/`わ．．．`/`３．`）——K11「唯一 sfx region OCR 空=素材缺口」在 BJ06 不成立。本跑 8/8 端到端译文落库即 KO-RERUN §7.7 裁决项 7（「K11 sfx.policy=translate 端到端素材路线：ja BJ06 或新素材」）的**正面关闭**。

### 1.3 SFX 译文质量抽检（directional，SEM-1 规范对照）

SFX-SEM-1 规范：≤6 字符级、禁直译音节、文化对等转换、保持强度。

| # | OCR 原文 | 译文 | ≤6 字符 | 评估（方向性） |
|---|---|---|---|---|
| 1 | ハチン | 啪 | 1 ✓ | **文化对等典型**：拍击/断裂拟声词→中文拟声词「啪」，非音节直译（音译会形如「哈钦」）；强度相当 |
| 2 | いいじゃ | 好啊 | 2 ✓ | 语气感叹对等（非音译） |
| 3 | いいん | 嗯嗯 | 2 ✓ | 应答语气词对等 |
| 4 | わ．．． | 哇…… | 3 ✓ | 感叹+省略号组合对等 |
| 5 | ！！！ | ！！！ | 3 ✓ | 标点保留（强度不减） |
| 6 | ．．． | …… | 2 ✓ | 中文省略号规范形（非逐字符直译「．．．」） |
| 7 | ．．． | …… | 2 ✓ | 同上 |
| 8 | ３． | 3. | 2 ✓ | 数字保留 |

- **≤6 字符符合率 8/8**；无音节直译实例；#1（ハチン→啪）为文化对等转换的最强单例证据。
- 口径限定（directional，如实）：样本 n=8；OCR 源多为短语气/标点碎片（manga-ocr 对 SFX 的读取本就是弱项，DETECT-EVAL 已登记）；「ハチン」疑为「バチン/パチン」的 OCR 近似——译文方向仍正确。**文化对等结论不外推为「SFX 翻译质量达标」**，正式质量 Gate 属 TA3-B 全量口径。

### 1.4 speech region 对照（正常翻译不受扰）

9/9 speech 翻译落库；与首跑（SKIP 门下）对照：**8/9 逐位一致**，1/9 为合法重译变体（`ちょっとおじいさん！？`「等一下，老爷爷！？」→「喂，老爷爷！？」，remote 采样语义等价——与 KO-RERUN 相似度 Gate 观察的合法重译形态同型）。policy=translate 设置只改变 sfx region 的 gate 路由，speech 链行为零扰动。

### 1.5 成本登记（AC4）

- BJ06 本跑：34 请求（=17 region×2 的 KO-RERUN 请求数模型），est token input 18,604 + output 1,642 = **20,246**（`--meter-translation` proxy 实测，estimate_tokens 口径，非 endpoint 计量）。

## 2. AC2：SFX-rich 素材搜寻与核定

### 2.1 候选评估与择优

| 优先级 | 候选 | 评估 | 结论 |
|---|---|---|---|
| a | densho810 BJ 官方 1/3/5 卷未入池页 | 许可框架现成（TA2B 已核+本次一手快照复证）；在盘 PDF 零新下载；BJ 是拟声词高发的少年漫向作品 | **选中**：vol03 全卷 221 页 40dpi 缩略图→7 张 contact sheet 逐张目检→9 候选页 100dpi 复查→3 页确认 SFX-rich |
| b | Pepper&Carrot 其他语言/页（CC-BY 4.0） | 许可可用，但该作品视觉风格**无独立拟声词字面**（仅对白/旁白），SFX 密度结构性≈0；K11 首跑已示范其单 SFX region 缺口 | 未选（不适配 SFX 目的） |
| c | 其他 CC-BY/CC-BY-SA 开放漫画 | a 已满足 1-3 页目标且预算内 | 未启用 |

- 无明确许可来源一律排除（纪律）；目检方法与结论：`material-inventory.json`（候选逐页 verdict）。
- 目检证据（Git 外）：`task-envs/M2-SFX-E2E-MATERIAL/thumbs-vol03/`（缩略图+contact sheets+100dpi 复查件+zoom 裁片）。

### 2.2 许可核定（一手证据先行）

- 快照：`densho810.com/free/` 2026-10-02 抓取 → `task-envs/M2-SFX-E2E-MATERIAL/license-evidence/densho810-free-snapshot-2026-10-02.html`（32,843 bytes，sha256 `2bb1dc9f1a06de8ca66705af93b772f00633cd85c644bd7835025008d43b6da1`）。
- 快照内已复证条款（复证范围即下述清单，非全文逐条通读，r1 R4 限定）：二次利用フリー（商用/非商用、无需事先许可）；**署名义务**「ブラックジャックによろしく 佐藤秀峰」（EN: Give My Regards to Black Jack / SHUHO SATO）；**公开利用后 1 个月内邮件报告** info@densho810.com；禁 Kindle 上架、电子书商店须 1 円以上有偿；JASRAC 管理乐曲页位三条（2 巻 p35/54/150/151/153、7 巻 p192、11 巻 p77『ジョーンジェットの犬』作品コード 066-3777-9）——**本次选取仅 vol03，不在上述三条页位清单内**。
- 义务登记：每 case `attribution` 字段官方格式原样；报告邮件=用户待办（TA2B 草稿 `verification/M2-TA2B/densho810-report-draft.txt` 覆盖同源新增，无需新草稿）。
- 像素纪律：新页 PNG 入**本 worktree** gitignored 套件目录（`日漫_JA/.gitignore` 规则 `/01_black_jack_official/` 生效，`git check-ignore` 复核）；源 PDF（TA2B worktree）**只读引用**——零写入其他 Task 的 worktree/既有产物（r1 R6 精确化：Git 外 task-env 树写入的是本 Task 自身的像素/预览/清单产物，含 AC3 的 `task-envs/M2-TA3-B/M2-SFX-E2E-MATERIAL/pixels-new-assets/`，见 §6）。

### 2.3 入池清单（3 页，case_id 沿 BJ 家族顺延）

渲染：`render_vol_pages.py`，DPI 150，2946×4167（与既有 BJ 页同规格）；源 PDF sha256 `31c37c85…`；渲染 manifest 在 task-envs。

| case | 页 | sha256 | 目检 SFX 清单（zoom 确认） | 选取理由 |
|---|---|---|---|---|
| BJ13 | vol03_p0048（第19話首页） | `86eeb6c2…` | ピ一一ーン！×2（巨大手写竖排电话铃，独立于气泡） | 巨大竖排 SFX 形态 |
| BJ14 | vol03_p0060（第24話首页） | `61dfeb2f…` | オギャァ×3（竖排毛笔婴儿啼哭，fragmented 布局） | 多 SFX+破碎布局 |
| BJ15 | vol03_p0159（第24話续页） | `3af00541…` | オギャァ×2（竖排毛笔）+正常多说话人对白 | **SFX 与 speech 同页**（gate 路由对照） |

- manifest 登记：`cases.json` BJ13/BJ14/BJ15（schema 沿 BJ06 全字段、attribution/attribution_note 复用官方格式、`registration_note` 指向本 Task 证据；**只增不改**，程序化 append 校验 case_id 无冲突后写入）。
- checksum 与许可核定：`verification/M2-SFX-E2E-MATERIAL/material-inventory.json`（单一登记点：快照 sha256、源 PDF sha256、逐页 sha256/尺寸/目检清单、义务清单）。

## 3. AC3：新素材端到端

### 3.1 全链结果（3/3 PASS）

`run_new_asset_e2e.py`（复用 `run_qualification.run_case` 原样，sfx-policy=translate 与 metering 强制，判轨 fail-closed 校验；独立 out-dir/pixel-root）：

| case | region（speech/sfx） | 译文落库 | export | metering（req / est in+out token） | wall |
|---|---|---|---|---|---|
| BJ13 | 4（3+1 sfx） | 4/4（含 sfx『．．．』→『……』） | OK `70b95ded…` | 8 / 4,370+386 | 217.9s |
| BJ14 | 6（6+0） | 6/6 | OK `9eebedca…` | 12 / 6,654+655 | 309.4s |
| BJ15 | 7（7+0） | 7/7 | OK `2c598592…` | 14 / 7,724+700 | 358.2s |

- 新素材上 speech 链基本正常：**16 个 speech region 中 14 个翻译方向正确**（含标题/对白/癌症病情陈述等长句）；**其余 2 个为 SFX 误路由**（r1 R1：BJ13 region #1/#3 即目检ピ一一ーン！位置，详见 §3.2 影响面）——「16 region 翻译方向正确」的原表述据此限定。harness 对新 case dict（page_path 指向本 worktree 素材、sha256 预校验）零适配问题。
- cases.json 的 pipeline_status 按实测推导登记（推导规则，r1 R10 对齐：PASS=该段实测达标——sfx 段要求 gate 放行**且**该 region 译文非空；NOT_RUN=页面无 sfx region 或 gate 未放行；FAIL=放行但译文为空）：BJ13 `sfx=PASS`（唯一 sfx region `sfx_policy=translate` 且译文『……』非空，按该规则重算维持 PASS）；BJ14/15 `sfx=NOT_RUN`（页面无 sfx region→gate 未触发，如实）。

### 3.2 检测域发现（如实登记，directional；r1 R1/R2 修订）

**chiqui7 sfx 类对 BJ 大型毛笔竖排 SFX 存在域外盲区**。目检 7 个 SFX 实例的检测诊断（`diagnose_sfx_detect.py`：生产推理序列复放、conf≥0.25 全类保留、零 src 改动；报告 `sfx-detect-diagnosis.json` + 预览 3 张。r1 R2 修订：改为**逐参照枚举全部相交框**（类+conf+ref 覆盖+box 覆盖+IoU），不再以单侧 coverage 的单一最优框下结论——单侧 coverage 是 DETECT-EVAL R12 已明文废止用于结论的度量）：

| 页 | 目检 SFX | sfx 类命中 | 与参照框相交的非 sfx 框（全部枚举，`sfx-detect-diagnosis.json`） |
|---|---|---|---|
| BJ13 | ピ一一ーン！×2 | 0（页面唯一 sfx 类框落在 T 恤印花 conf 0.822，误报=生产 run 的 sfx region，与两处参照框均不相交） | 每个 ref 各 2 框并存：同位置 **text** 框（conf 0.744/0.844，ref 覆盖 0.73/0.67，**IoU 0.452/0.544**）+ 近整页 **panel** 大框 (375,370)-(2612,3802)（conf 0.943，ref 覆盖 0.83/1.00，IoU 仅 0.029/0.037——尺寸失衡下的平凡覆盖） |
| BJ14 | オギャァ×3 | 0（全页 0.25 带亦无） | ref1 仅 **panel**（conf 0.967，ref 覆盖 0.89，IoU 0.094）；ref2/ref3 为 **bubble+panel+text** 三类并存（bubble conf 0.967/0.964 IoU 0.122/0.399；panel 0.969/0.972 ref 覆盖 1.00；text 0.941/0.920） |
| BJ15 | オギャァ×2 | 0（全页 0.25 带亦无） | 每个 ref 仅 **panel**（conf 0.955/0.919，ref 覆盖 1.00，IoU 0.056/0.075） |

- **混淆归属未定（r1 R2 撤回原形态学结论）**：初版报告「本样本是 panel 类支配、与 ko 域 text 混淆形态不同」不成立——该判读来自单侧 coverage + 只取最优框，恰好被页面级 panel 大框平凡覆盖支配，并隐去了 BJ13 两个参照框上同位置的 text 类框（DSH r1 复算与重生成 JSON 一致）。按 IoU（尺寸公平口径），BJ13 的紧贴混淆候选是 **text** 类（与 ko 域同型）；panel 大框与 text/bubble 框**并存**，两者均可解释 sfx 类 0 命中，**归属未定**，留待检测域扩展 Task 以更大样本裁决。与 DETECT-EVAL Known limitations 4（chiqui7 训练数据未登记→域适配不可预判）方向一致，本发现是新域样本上的第一手量化登记（7 实例，directional）。
- **对产品语义的影响面（r1 R1 重写，撤回「SKIP 默认下无用户可见影响」免责句）**：盲区的损害不止「漏检即无 region」。**已实证的更重损害形态：SFX 误路由为 speech → 对话链乱译 → 进渲染**——BJ13 生产 run 的 region #1 bbox (2124,258,370,1013) 与 region #3 bbox (472,2668,308,1002) 正是两处目检ピ一一ーン！位置（裁片 `pixels-new-assets/ocr/crops/BJ13/ffed29e8….png`、`de83b0c4….png` 目视确认），其 `region_type=speech`、走正常对话链产出乱译（「いやー、」→「哎呀——」、「Ｗｉｆｉｘ」原样保留）并 export 渲染（export OK）——**错误译文已进入渲染成品页**。该损害发生在 speech 路径上，**与 SfxPolicy 无关**：SfxPolicy=SKIP 默认下同样发生（DSH r1 反证成立，本报告采纳）。**误报面**（T 恤印花被判 sfx）在 policy=translate 下会把印花当 SFX 翻译——本次 BJ13 实测其 OCR『．．．』→『……』，无实义损害，但登记为 policy=translate 的已知误报形态。
- 处置：检测域扩展（SFX 专用再训练/后分类/阈值重冻结）沿 DETECT-EVAL §4.4 集成前条件清单，属后续 Task + 用户裁决；本 Task 零生产改动，只交付证据。**r1 R1 升级**：「SFX 误路由 speech 的损害形态=检测域扩展的真实动因强化」登记为**独立 Task 候选**（供集成方搬 STATUS）——它是 DETECT-EVAL §4.4 域扩展裁决清单的优先级证据：损害从「漏检即无 region」（无翻译、无渲染）升级为「误路由→乱译→渲染进成品页」（用户可见错误内容），显著提高域扩展的优先级权重。

### 3.3 合并 SFX 端到端能力结论

1. **翻译语义链已闭环实证**：BJ06（8/8 sfx region 检出→gate 放行→SEM-1 prompt 特化→DeepSeek 文化对等转换→落库非空）+ BJ13（1/1，另一素材页上同链走通）。SFX 家族 DETECT→PROD→SEM→ENTRY→PRIMARY 的 ENTRY 之后各段在 ja 域无遗留缺口。
2. **检测段是 SFX 端到端覆盖的真实瓶颈**：BJ06 的 8 个 sfx region 恰好是「检出+OCR 有文本」素材；新素材的毛笔 SFX 暴露 chiqui7 域外混淆（panel 大框与 text/bubble 框并存、归属未定，§3.2）。SFX 覆盖率提升的未来杠杆在检测层（与 DETECT-EVAL §4 结论「检出与区分为两层设计」收敛），不在翻译层；且盲区存在**用户可见损害路径**（误路由 speech→乱译→渲染，与 SfxPolicy 无关），域扩展优先级据此上调（§3.2 处置段）。
3. ko 侧（K11）素材缺口与 ja 侧检测缺口是两类独立缺口，均已量化登记；K11 裁决项 7 由本 Task 关闭（ja BJ06 路线交付+新素材入池双轨）。

## 4. 成本合计（AC4 预算对照）

| 跑 | 请求 | est token（in+out） |
|---|---|---|
| BJ06 policy=translate | 34 | 20,246 |
| BJ13 | 8 | 4,756 |
| BJ14 | 12 | 7,309 |
| BJ15 | 14 | 8,424 |
| **合计** | **68** | **40,735** |

预算 10 万 est token 内（40.7%）；key 零明文（env 注入 + scrub_secrets，产物已抽查无泄漏形态）。

## 5. Known limitations（引用本报告时不得省略）

1. **directional 口径**：单 case（BJ06）+3 新页样本；无 SFX GT；质量抽检单 AI 评估；译文质量结论不构成达标 Gate。
2. BJ06 的 8 个 sfx region OCR 多为短语气/标点碎片，SFX 拟声词典型样本占比有限（ハチン 1 例）；文化对等的最强证据是单例级。
3. chiqui7 域外结论基于 3 页 7 实例 + 单模型诊断预览，未做阈值扫描/多 seed；混淆**归属未定**（页面级 panel 大框与同位置 text/bubble 框并存；初版「panel 类支配」的单一归因已按 r1 R2 撤回——其依据的单侧 coverage 度量被 DETECT-EVAL R12 明文废止用于结论）。
4. 翻译为 remote 采样轨：跨 run 逐位一致性不适用（speech 8/9 逐位一致是观测非承诺）。
5. BJ06 首跑产物（SKIP 基线）与 KO-RERUN 产物零改动；本报告对照引用不构成对既有产物的重写。
6. densho810 报告邮件义务=用户待办（新增 3 页同源同许可，TA2B 草稿覆盖）。
7. 误路由损害仅对 BJ13 两处逐点实证（裁片+region bbox 对位）；BJ14/15 的目检 SFX 是否也部分落入生产 speech region（重生成 JSON 显示其参照框与 text/bubble 框有 0.14-0.68 的部分相交）未逐页定性，留待检测域扩展 Task。
8. 本报告含 r1 返修（DSH review，verdict=有条件通过）：R1 影响面重写与 SKIP 免责句撤回、R2 诊断口径改全相交框枚举+归属未定、R3 计数 7 统一、R4 JASRAC 第三条补齐、R5 时间戳 UTC 真值、R6 零写入表述精确化、R7 Task 引用回退、R8 偏差归因精确化、R9 bbox 级措辞、R10 pipeline_status 推导规则显式化；逐条落点见 Handoff「r1 返修记录」。

## 6. 证据物与复现

| 证据物 | 位置 |
|---|---|
| BJ06 跑产物 | `verification/M2-SFX-E2E-MATERIAL/bj06-run/`（summaries + run.log） |
| 新素材跑产物 | `verification/M2-SFX-E2E-MATERIAL/new-assets-run/summaries/`（3 case + new-asset-report.json）+ `new-assets-run.log` |
| 素材登记 | `verification/M2-SFX-E2E-MATERIAL/material-inventory.json` + `test_assets/comic_golden_suite/manifests/cases.json`（BJ13-15） |
| 检测诊断 | `verification/M2-SFX-E2E-MATERIAL/sfx-detect-diagnosis.json`（预览在 Git 外 task-envs） |
| 工具 ×4 | `experiments/M2-SFX-E2E-MATERIAL/render_vol_pages.py` / `run_new_asset_e2e.py` / `register_new_cases.py` / `diagnose_sfx_detect.py` |
| 许可快照 | Git 外 `task-envs/M2-SFX-E2E-MATERIAL/license-evidence/`（sha256 见 material-inventory） |
| 像素产物 | Git 外 `task-envs/M2-SFX-E2E-MATERIAL/pixels*/`（BJ06 crops+exports）与 `thumbs-vol03/`、`detect-diag-previews/`；**AC3 新素材像素根**（r1 R6 补登）：`task-envs/M2-TA3-B/M2-SFX-E2E-MATERIAL/pixels-new-assets/`（crops+exports×3，由 `run_new_asset_e2e.py` 默认从 harness 的 `PIXEL_ROOT_DEFAULT.parent` 派生所致，落入 M2-TA3-B env 树下的本 Task 子目录） |

复现（worktree 根目录）：

```bash
export TA3B_TRANSLATE_API_KEY=$(cat "G:/CODEX/New Manga.task-envs/M2-TA3-B/deepseek.key")
# AC1 BJ06（首跑 SKIP 基线产物零改动——独立 out-dir/pixel-root）
"G:/CODEX/New Manga.task-envs/M2-TA3-B-ocr/Scripts/python.exe" experiments/M2-TA3-B/run_qualification.py \
  --case BJ06 --sfx-policy translate --determinism-track remote --meter-translation \
  --out-dir "verification/M2-SFX-E2E-MATERIAL/bj06-run/summaries" \
  --pixel-root "G:/CODEX/New Manga.task-envs/M2-SFX-E2E-MATERIAL/pixels"
# AC2 渲染（源 PDF 只读；输出入本 worktree gitignored 套件目录）
"G:/CODEX/New Manga.task-envs/M2-TA3-B-ocr/Scripts/python.exe" experiments/M2-SFX-E2E-MATERIAL/render_vol_pages.py \
  --pdf "G:/CODEX/New Manga.worktrees/M2-TA2B-OPEN-ASSETS-zcode/test_assets/comic_golden_suite/日漫_JA/01_black_jack_official/vol03/volume03.pdf" \
  --out-dir "test_assets/comic_golden_suite/日漫_JA/01_black_jack_official/vol03/pages" \
  --dpi 150 --pages 48 --pages 60 --pages 159 --name-prefix vol03_p
# AC3 新素材端到端
"G:/CODEX/New Manga.task-envs/M2-TA3-B-ocr/Scripts/python.exe" experiments/M2-SFX-E2E-MATERIAL/run_new_asset_e2e.py
# AC3 检测诊断（零 src 改动）
"G:/CODEX/New Manga.task-envs/M2-TA3-B-ocr/Scripts/python.exe" experiments/M2-SFX-E2E-MATERIAL/diagnose_sfx_detect.py
# cases.json 增量登记（append-only，冲突 fail-closed）
"G:/CODEX/New Manga.task-envs/M2-TA3-B-ocr/Scripts/python.exe" experiments/M2-SFX-E2E-MATERIAL/register_new_cases.py
```
