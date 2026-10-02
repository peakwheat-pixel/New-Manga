# M2-SFX-E2E-MATERIAL：SFX 翻译端到端验证与素材扩展报告

- Task：[M2-SFX-E2E-MATERIAL](../../doc/tasks/M2-SFX-E2E-MATERIAL.md) · 分支 `agent/zcode/M2-SFX-E2E-MATERIAL` · base=`73252798` · 日期 2026-10-02
- Owner=ZCode · Reviewer=DeepSeek Harness（非作者，待 review）· Integrator=代行 Codex（用户全权授权+自治授权）
- 授权：用户裁决 2026-10-02 七项之④（SFX 素材寻找/下载/测试全权授权）
- **证据强度裁定（全程适用）**：BJ06 跑与全部质量表述为 **directional**（单一 remote 采样 provider、无 SFX GT、单页/三页样本）；「文化对等为方向性抽检非 Gate」（Task AC4 纪律）。检测域发现的数字同样 directional（单 AI 标注者目检 + 单模型诊断，沿 [M2-SFX-DETECT-EVAL](../M2-SFX-DETECT-EVAL/sfx-detect-eval-report.md) 的证据强度口径）。
- 生产面零改动：`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**` 未触碰；既有 case 产物、首跑/KO-RERUN 产物、`doc/STATUS.md` 零 diff；manifests 只增不改（cases.json 97→100，+214/-0 行）。

## 0. 结论速览

| 交付 | 结论 |
|---|---|
| AC1 BJ06 端到端（policy=translate） | **闭环达成**：chiqui7 检出 17 region（8 sfx + 9 speech，与首跑逐 region 一致）→ SFX gate 放行 8/8（`sfx_policy=translate`）→ DeepSeek 翻译落库 **8/8 非空**（`final_source=machine`）；speech 9/9 正常翻译不受扰（8/9 与首跑逐位一致、1/9 语义等价合法重译）；34 请求 ≈20.2k est token；export OK。**SFX 家族链 DETECT→PROD→SEM→ENTRY→PRIMARY 全链最终闭环实证完成** |
| AC2 素材搜寻与核定 | densho810 BJ 官方卷路线（优先级 a）胜出：许可一手快照在案（sha256 `2bb1dc9f…`），vol03 全卷 221 页目检，择优 3 页入池（BJ13/BJ14/BJ15），checksum 与 case 登记齐全，署名/报告义务沿 TA2B 框架 |
| AC3 新素材端到端 | **链路 PASS（3/3 pipeline_completed、export OK、speech 16 region 翻译正常）+ 检测域缺口如实登记**：chiqui7 sfx 类对 BJ 大型毛笔竖排 SFX 召回为盲区（7 个目检 SFX 实例：sfx 类 0 命中；6 个被 panel 类 0.92-0.97 高置信覆盖；BJ13 唯一 sfx region 为 T 恤印花误报，其 OCR『．．．』→『……』仍完整走通 gate→翻译落库） |
| 合并 SFX 端到端能力结论 | **翻译语义链（gate 放行→SEM-1 prompt 特化→译文落库）在 ja 域实证工作**（BJ06 8/8 + BJ13 1/1）；**检测段是当前 SFX 端到端覆盖的真实瓶颈**——BJ06 的 8 个 sfx region 是「检出且有文本」的恰好素材，新素材的毛笔 SFX 形态暴露 chiqui7 的域外混淆（panel 类）。检测域扩展（阈值/后分类/再训练）= 未来 Task + 用户裁决范畴（DETECT-EVAL §4.4 清单既存），本 Task 零生产改动 |

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
| 检出 | 17 region = 9 speech + **8 sfx**（chiqui7 conf≥0.5；与首跑同 region 数、同类型分布——检测确定性跨 run 复现） |
| gate | sfx region `sfx_policy` 字段实测 `translate` ×8（首跑全 `skip`）；speech region 9 个不受门影响正常翻译 |
| 落库 | **SFX 译文非空 8/8**（`translated_text` 与 `final_translation` 非空、`final_source=machine`）；speech 9/9 |

任务书背景写「BJ06 含 9 个 SFX region」，实测检出 **8 个 sfx region**（+9 speech=17）；与 KO-RERUN 报告 §3.2「ja BJ06 类素材（8 个有文本 sfx region）」一致——以实测 8 为准，任务书表述登记为笔误级偏差（不影响任何验收逻辑）。

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
- 快照内逐条复证条款：二次利用フリー（商用/非商用、无需事先许可）；**署名义务**「ブラックジャックによろしく 佐藤秀峰」（EN: Give My Regards to Black Jack / SHUHO SATO）；**公开利用后 1 个月内邮件报告** info@densho810.com；禁 Kindle 上架、电子书商店须 1 円以上有偿；JASRAC 管理乐曲页位（2 巻 p35/54/150/151/153、7 巻 p192）——**本次选取仅 vol03（JASRAC-free 卷）**。
- 义务登记：每 case `attribution` 字段官方格式原样；报告邮件=用户待办（TA2B 草稿 `verification/M2-TA2B/densho810-report-draft.txt` 覆盖同源新增，无需新草稿）。
- 像素纪律：新页 PNG 入**本 worktree** gitignored 套件目录（`日漫_JA/.gitignore` 规则 `/01_black_jack_official/` 生效，`git check-ignore` 复核）；源 PDF（TA2B worktree）**只读引用**——本 Task 未写任何本 worktree 以外路径。

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

- 新素材上 speech 链完全正常（16 region 翻译方向正确，含标题/对白/癌症病情陈述等长句）；harness 对新 case dict（page_path 指向本 worktree 素材、sha256 预校验）零适配问题。
- cases.json 的 pipeline_status 按实测推导登记：BJ13 `sfx=PASS`（存在走通 translate gate 的 sfx region）；BJ14/15 `sfx=NOT_RUN`（页面无 sfx region→gate 未触发，如实）。

### 3.2 检测域发现（如实登记，directional）

**chiqui7 sfx 类对 BJ 大型毛笔竖排 SFX 存在域外盲区**。目检 7 个 SFX 实例的检测诊断（`diagnose_sfx_detect.py`：生产推理序列复放、conf≥0.25 全类保留、零 src 改动；报告 `sfx-detect-diagnosis.json` + 预览 3 张）：

| 页 | 目检 SFX | chiqui7 实际判定 | 诊断 |
|---|---|---|---|
| BJ13 | ピ一一ーン！×2 | 均 **panel 类** conf 0.943（cov 0.83/1.00）；页面唯一 sfx 类框落在 T 恤印花（conf 0.82，误报=生产 run 的 sfx region） | 类混淆 + 误报 |
| BJ14 | オギャァ×3 | 均 **panel 类** conf 0.967-0.972（cov 0.89-1.00）；sfx 类零输出（全页 0.25 带亦无） | 类混淆（panel 支配） |
| BJ15 | オギャァ×2 | 均 **panel 类** conf 0.919-0.955（cov 1.00）；sfx 类零输出 | 类混淆（panel 支配） |

- 形态学与 DETECT-EVAL 的 ko 域观察不同：ko webtoon SFX 混淆去向是 **text** 类；本样本是 **panel** 类（竖排白底黑框毛笔字与 panel 边框形态相似）。与该报告 Known limitations 4（chiqui7 训练数据未登记→域适配不可预判）方向一致，本发现是**新域样本上的第一手量化登记**（7 实例，directional）。
- 对产品语义的影响面：SfxPolicy=SKIP 默认下该盲区无用户可见影响（sfx 候选缺失仅意味着不触发 SFX 特化翻译）；policy=translate 下也不产生错误 SFX 翻译（漏检即无 region）。**误报面**（T 恤印花被判 sfx）在 policy=translate 下会把印花当 SFX 翻译——本次 BJ13 实测其 OCR『．．．』→『……』，无实义损害，但登记为 policy=translate 的已知误报形态。
- 处置：检测域扩展（SFX 专用再训练/后分类/阈值重冻结）沿 DETECT-EVAL §4.4 集成前条件清单，属后续 Task + 用户裁决；本 Task 零生产改动，只交付证据。

### 3.3 合并 SFX 端到端能力结论

1. **翻译语义链已闭环实证**：BJ06（8/8 sfx region 检出→gate 放行→SEM-1 prompt 特化→DeepSeek 文化对等转换→落库非空）+ BJ13（1/1，另一素材页上同链走通）。SFX 家族 DETECT→PROD→SEM→ENTRY→PRIMARY 的 ENTRY 之后各段在 ja 域无遗留缺口。
2. **检测段是 SFX 端到端覆盖的真实瓶颈**：BJ06 的 8 个 sfx region 恰好是「检出+OCR 有文本」素材；新素材的毛笔 SFX 暴露 chiqui7 域外混淆。SFX 覆盖率提升的未来杠杆在检测层（与 DETECT-EVAL §4 结论「检出与区分为两层设计」收敛），不在翻译层。
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
3. chiqui7 域外结论（panel 类混淆）基于 3 页 7 实例 + 单模型诊断预览，未做阈值扫描/多 seed；「panel 类支配」是方向性归因。
4. 翻译为 remote 采样轨：跨 run 逐位一致性不适用（speech 8/9 逐位一致是观测非承诺）。
5. BJ06 首跑产物（SKIP 基线）与 KO-RERUN 产物零改动；本报告对照引用不构成对既有产物的重写。
6. densho810 报告邮件义务=用户待办（新增 3 页同源同许可，TA2B 草稿覆盖）。

## 6. 证据物与复现

| 证据物 | 位置 |
|---|---|
| BJ06 跑产物 | `verification/M2-SFX-E2E-MATERIAL/bj06-run/`（summaries + run.log） |
| 新素材跑产物 | `verification/M2-SFX-E2E-MATERIAL/new-assets-run/summaries/`（3 case + new-asset-report.json）+ `new-assets-run.log` |
| 素材登记 | `verification/M2-SFX-E2E-MATERIAL/material-inventory.json` + `test_assets/comic_golden_suite/manifests/cases.json`（BJ13-15） |
| 检测诊断 | `verification/M2-SFX-E2E-MATERIAL/sfx-detect-diagnosis.json`（预览在 Git 外 task-envs） |
| 工具 ×3 | `experiments/M2-SFX-E2E-MATERIAL/render_vol_pages.py` / `run_new_asset_e2e.py` / `register_new_cases.py` / `diagnose_sfx_detect.py`（×4） |
| 许可快照 | Git 外 `task-envs/M2-SFX-E2E-MATERIAL/license-evidence/`（sha256 见 material-inventory） |
| 像素产物 | Git 外 `task-envs/M2-SFX-E2E-MATERIAL/pixels*/`（crops+exports）与 `thumbs-vol03/`、`detect-diag-previews/` |

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
