---
task_id: M2-SFX-E2E-MATERIAL
author: ZCode
recipient: Codex（集成）/ DeepSeek Harness（Review，非作者）
base_commit: 73252798
delivery_head: 40a8ceec（实现）；本 Handoff 随交付 commit 入库
status: delivered_in_review
---

# Handoff：M2-SFX-E2E-MATERIAL（SFX 翻译端到端验证与素材扩展）

## 交付结果

按 Task（用户裁决 2026-10-02 七项之④全权授权）完成 AC1-AC4 全部范围，分支 `agent/zcode/M2-SFX-E2E-MATERIAL`、worktree `G:/CODEX/New Manga.worktrees/M2-SFX-E2E-MATERIAL-zcode`：

1. **提交列表**
   - `40a8ceec` implement(M2-SFX-E2E-MATERIAL)：全部交付物（17 files，+5569/-2；-2 为 Task 文件回填的 frontmatter/正文替换）
   - 本 Handoff 随后续 handoff commit 入库
2. **AC1 BJ06 端到端（SFX 家族链最终闭环）**：`--sfx-policy translate --determinism-track remote --meter-translation` → pipeline_completed=True（run1 357.6s + run2 336.9s、17/17 region 零 defect、export OK `c1d503f4…`）；chiqui7 检出 17 region（8 sfx + 9 speech，与首跑 bbox/类型/序号一致、region_id 每跑重生成）；SFX gate 放行 8/8（`sfx_policy` 字段实测 skip→translate）；**SFX 译文落库 8/8 非空**（final_source=machine）；质量抽检（directional）：≤6 字符 8/8、无音节直译、`ハチン→啪` 文化对等典型；speech 9/9 不受扰（8/9 与首跑逐位一致、1/9 语义等价合法重译）。任务书背景「9 个 SFX region」实测 8——来源为 sfx-semantic-worksheet 9 行合计口径（8 BJ06 + 1 K11，quality-report.md:120）的沿用偏差（r1 R8 精确化）。K11 裁决项 7 正面关闭。
3. **AC2 素材搜寻/核定/入池**：densho810 路线（优先级 a）；许可一手快照 sha256 `2bb1dc9f…`（已复证条款：二次利用フリー/署名/1 个月报告/Kindle 禁令/JASRAC 三条页位 2巻 p35/54/150/151/153、7巻 p192、11巻 p77——r1 R4 补齐第三条）；vol03 全卷 221 页缩略图目检→9 候选 100dpi 复查→**BJ13（vol03_p0048 ピ一一ーン！×2）/BJ14（vol03_p0060 オギャァ×3）/BJ15（vol03_p0159 オギャァ×2+对白）** 入池；DPI 150 渲染（2946×4167）、逐页 sha256 入 `material-inventory.json`；cases.json 97→100 **只增**（+214/-0，程序化 append、冲突 fail-closed）；像素入本 worktree gitignored 套件目录、源 PDF（TA2B worktree）只读引用——**零写入其他 Task 的 worktree/既有产物**（Git 外像素入 task-env 树，r1 R6 精确化）。
4. **AC3 新素材端到端（r1 R1/R2/R3 修订）**：3/3 pipeline_completed（export OK×3、speech 16 region 中 14 个翻译方向正确、BJ13 sfx region 1/1 落库『．．．』→『……』）+ **检测域缺口如实登记**：chiqui7 sfx 类对 BJ 大型毛笔竖排 SFX 盲区（7 目检实例：sfx 类 0 命中、7/7 均被非 sfx 类框覆盖——页面级 panel 大框与同位置 text/bubble 框并存、混淆归属未定；BJ13 唯一 sfx region=T 恤印花误报 conf 0.82）——directional，`diagnose_sfx_detect.py` 零 src 改动复放生产推理序列取证（r1 R2 起改全相交框枚举）。**r1 R1 新增损害形态**：BJ13 两处目检 SFX 被误路由为 speech、对话链乱译（「いやー、」→「哎呀——」/「Ｗｉｆｉｘ」）并 export 渲染——错误译文进渲染成品页，与 SfxPolicy 无关（SKIP 默认下同样发生）；已升级为独立 Task 候选（见「下一任务建议」）。
5. **AC4 纪律**：合计 68 请求 ≈40,735 est token（预算 10 万的 40.7%）；key env 注入+scrub_secrets、入库文件 leak 扫描 CLEAN；禁改面零 diff；manifests 只增不改。
6. **合并能力结论**：SFX 翻译语义链（gate 放行→SEM-1 特化→DeepSeek 转换→落库）在 ja 域闭环实证（BJ06 8/8 + BJ13 1/1）；**检测段是 SFX 端到端覆盖的真实瓶颈**（新素材域混淆归属未定：panel 大框与 text/bubble 框并存；且盲区存在用户可见损害路径——误路由 speech→乱译→渲染，与 SfxPolicy 无关），域扩展属 DETECT-EVAL §4.4 既有裁决清单，本 Task 零生产改动。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 BJ06 e2e | `run_qualification.py --case BJ06 --sfx-policy translate --determinism-track remote --meter-translation`（独立 out-dir/pixel-root，首跑产物零改动） | 融合 venv `M2-TA3-B-ocr`，worktree @24a89d7d | PASS（pipeline_completed=True） | `verification/M2-SFX-E2E-MATERIAL/bj06-run/summaries/qual-BJ06.json`、`run.log` |
| AC1 质量抽检+speech 对照 | summary JSON 解析（8 条 SFX 逐条表 + 首跑对照） | 同上 | PASS（directional；表见主报告 §1.3/§1.4） | `verification/M2-SFX-E2E-MATERIAL/sfx-e2e-report.md` |
| AC2 许可快照 | curl densho810.com/free/ → sha256 → 关键词逐条复证 | — | PASS（义务沿 TA2B 框架） | Git 外 `task-envs/M2-SFX-E2E-MATERIAL/license-evidence/`；`material-inventory.json` |
| AC2 目检与入池 | `render_vol_pages.py`（40dpi 全卷→contact sheet 目检→100dpi 复查→150dpi 正式渲染）+ `register_new_cases.py`（append-only） | 同上 | PASS（3 页入池；cases.json +214/-0） | `material-inventory.json`、`test_assets/comic_golden_suite/manifests/cases.json`（BJ13-15） |
| AC3 新素材 e2e | `run_new_asset_e2e.py`（复用 run_case 原样，policy/metering 强制） | 同上 | PASS（3/3 pipeline_completed） | `verification/M2-SFX-E2E-MATERIAL/new-assets-run/summaries/` |
| AC3 检测诊断 | `diagnose_sfx_detect.py`（conf≥0.25 全类保留 + 逐参照全相交框枚举 [r1 R2：类/conf/双向覆盖/IoU] + 预览目检） | 同上 | 完成（缺口如实登记，directional） | `verification/M2-SFX-E2E-MATERIAL/sfx-detect-diagnosis.json` |
| AC4 纪律 | `git status --porcelain` / `git diff --check` / 禁改路径 grep / key leak 扫描 | @40a8ceec | PASS（禁改面零触碰；leak CLEAN） | 本 Handoff + 主报告 §4/§5 |

未运行/不适用：BJ01-BJ12 其余页、BJ14/15 的 SFX gate 段（页面无 sfx region，NOT_RUN 如实登记于 cases.json pipeline_status）；正式 SFX 翻译质量 Gate（属 TA3-B 全量口径，本 Task 为 directional 抽检）。

## 接收方式

- 分支 `agent/zcode/M2-SFX-E2E-MATERIAL`（base `73252798`，delivery_head `40a8ceec`），worktree 同 Task frontmatter。
- 复现命令：主报告 §6（BJ06 跑/渲染/新素材跑/诊断/cases 登记五段，key 需先 `export TA3B_TRANSLATE_API_KEY=$(cat …/deepseek.key)`）。
- Review 检查建议：①qual-BJ06.json 的 8 条 sfx translate_details 与抽检表逐条对照；②cases.json diff 仅 BJ13/14/15 追加；③`material-inventory.json` 与 Git 外快照 sha256 一致性；④`diagnose_sfx_detect.py` 判读（sfx-detect-diagnosis.json + Git 外预览 3 张）。

## r1 返修记录（2026-10-02，DSH review verdict=有条件通过，R1-R10 全处置）

DSH r1 报告：Git 外 `G:/CODEX/New Manga.task-envs/M2-SFX-E2E-MATERIAL/dsh-review-r1.md`。返修 commit=分支 tip（`review-fix(M2-SFX-E2E-MATERIAL)`）。逐条落点：

- **R1（P1，选项①）**：目检成立——BJ13 region #1/#3（bbox (2124,258,370,1013)/(472,2668,308,1002)，即两处目检ピ一一ーン！位置）`region_type=speech`、对话链乱译（「いやー、」→「哎呀——」/「Ｗｉｆｉｘ」）并 export 渲染，错误译文已进渲染页。落点：report §3.2 影响面重写（新增「SFX 误路由 speech→对话链乱译→进渲染」损害形态，与 SfxPolicy 无关）+「SKIP 默认下无用户可见影响」免责句撤回（原 :126 及 :15/:112 复述处）；:112「speech 16 region 翻译方向正确」限定为 14/16；Task 交付记录 AC3 段与 Handoff 第 4 条同步；发现升级为独立 Task 候选登记（见下）。
- **R2（P2）**：`diagnose_sfx_detect.py` 改为逐参照**枚举全部相交框**（类+conf+ref 覆盖+box 覆盖+IoU），重生成 `sfx-detect-diagnosis.json`；report §3.2 重写为「存在整页 panel 大框+同位置 text/bubble 框，两者均可解释 sfx 类 0 命中，归属未定」，撤回「panel 类支配/与 ko 域 text 混淆形态不同」形态学结论；Known limitations 3 同步。核对：重生成后 BJ13 仍 5 框（sfx 类仅 T 恤 1 框）、BJ14/15 sfx 类 0 输出——「sfx 类 0 命中」核心事实不变；DSH 复算的 BJ13 同位置 text 框 conf 0.844/0.744（ref 覆盖 0.67/0.73）已如实披露。
- **R3（P3）**：「6 个被 panel 类覆盖」统一为 **7/7**（report §0 与 §3.2 表格及重生成 JSON 一致）；Task AC3 段与 Handoff 第 4 条同步。
- **R4（P3）**：`material-inventory.json` terms 清单与 report §2.2 补 JASRAC 第三条（11巻/77頁『ジョーンジェットの犬』作品コード 066-3777-9）；「逐条复证」限定为「已复证条款清单（复证范围即清单）」；Handoff 第 3 条同步。
- **R5（P3）**：`material-inventory.json` 时间戳改 UTC 真值（`generated_at_utc` 00:20:00Z、`snapshot_captured_at_utc` 00:07:00Z，原值为 UTC+8 本地时间误标 Z），补 `timestamp_basis` 说明；「许可先行」按 task-env 树 mtime 实物顺序成立的事实写入说明保留。
- **R6（P3）**：「本 worktree 以外零写入」改「零写入其他 Task 的 worktree/既有产物（Git 外像素入 task-env 树）」（report §2.2、Task AC2 段、Handoff 第 3 条、material-inventory source_pdf note）；report §6 像素产物行补 AC3 根路径 `task-envs/M2-TA3-B/M2-SFX-E2E-MATERIAL/pixels-new-assets/`。
- **R7（P3）**：Task:21 `dialogue-readiness-worksheet` 回退为 `dialogue-readability-worksheet`（真实产物 `verification/M2-TA3-B/phase2/translate/dialogue-readability-worksheet.csv/.json`）。
- **R8（P4）**：「9→8 笔误级偏差」归因精确化为「sfx-semantic-worksheet 9 行合计口径（8 BJ06 + 1 K11）的沿用偏差」（report §1.1、Task AC1 段、Handoff 第 2 条）。
- **R9（P4）**：「与首跑逐 region 一致」改「bbox/类型/序号逐条一致、region_id 每跑重生成」（report §0/:31、Handoff 第 2 条）。
- **R10（P3）**：`register_new_cases.py` pipeline_status 推导修正——`ocr` 死分支清理（等价 `run2_ok`）、`sfx` 改为结果导向（PASS=gate 放行**且**该 region 译文非空；NOT_RUN=无 sfx region 或未放行；FAIL=放行但译文空）、推导规则写入 docstring 并在 report §3.1 显式声明。**cases.json 改判结果：按新推导重算三 case 全字段与已落盘值一致——BJ13 sfx=PASS 维持**（唯一 sfx region gate 放行且译文『……』非空），BJ14/15 sfx=NOT_RUN 维持，manifests 零 diff。
- 范围纪律：返修改动面=`verification/M2-SFX-E2E-MATERIAL/**`（report/inventory/diagnosis JSON）+`experiments/M2-SFX-E2E-MATERIAL/**`（2 个脚本）+Task/Handoff；禁改面零 diff；cases.json 结构零变化（本次零改动）。

## 下一任务建议（必填）

- **Review（先行）**：DeepSeek Harness 对 `40a8ceec` 做 r1 静态 Review（重点：AC1 端到端证据链、cases.json 只增、许可快照 sha256、检测域发现的 directional 口径）。可直接转发指令：「对分支 agent/zcode/M2-SFX-E2E-MATERIAL tip `40a8ceec`（Task M2-SFX-E2E-MATERIAL，base 73252798）执行非作者 Review：主报告 `verification/M2-SFX-E2E-MATERIAL/sfx-e2e-report.md`，按 Task AC1-AC4 与禁改面核对，重点抽检 qual-BJ06.json 的 SFX translate_details 8 条与报告 §1.3 表、cases.json BJ13-15 追加条目与 material-inventory.json 的 sha256 一致性、sfx-detect-diagnosis.json 的 panel 类混淆判读。」
- **候选后续 Task（需 Codex 释放+用户裁决，非本 Task 范围）**：
  - **SFX 误路由 speech 的损害形态处置（r1 R1 升级登记，供集成方搬 STATUS）**：损害形态=「检测域扩展的真实动因强化」——BJ13 实证 SFX 被误路由为 speech 后经对话链乱译并渲染进成品页（与 SfxPolicy 无关），把损害从「漏检即无 region」升级为「用户可见错误内容」；该证据是 DETECT-EVAL §4.4 域扩展裁决清单的**优先级权重输入**。可转发指令：「对 M2-SFX-E2E-MATERIAL 遗留的检测域缺口，按 sfx-e2e-report.md §3.2 影响面（r1 修订）登记独立 Task：SFX 误路由 speech 损害形态处置（检测域扩展：后分类/阈值重冻结/再训练评估，含 BJ13 speech 误路由→sfx 域的后分类回收路径），沿 DETECT-EVAL §4.4 七项集成前条件，优先级权重依据=用户可见渲染损害实证。」
  - SFX 检测域扩展（BJ 毛笔竖排 SFX 的 panel/text/bubble 混淆归属裁决：后分类器/阈值重冻结/再训练评估——沿 DETECT-EVAL §4.4 七项集成前条件；r1 R2 后混淆归属未定，需更大样本）。
  - BJ06 全 17 region 纳入 TA3-B 正式质量口径（remote 轨 similarity Gate 的 ja 侧样本扩充）。
- densho810 报告邮件=用户待办（TA2B 草稿覆盖本批同源新增，无需新草稿）。
