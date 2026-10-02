---
id: M2-SFX-E2E-MATERIAL
title: "SFX 端到端素材路线（用户裁决④全权授权）：ja BJ06 policy=translate 端到端验证 + SFX-rich 素材搜寻/下载/入池"
kind: feature
status: delivered_in_review
approval: user_ruling_2026-10-02_seven_items_full_authority_material
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-SFX-TRANSLATE-ENTRY, M2-TASKS-PRIMARY-SFX-GATE, M2-SFX-SEM-1, M2-TA3-B3-KO-FULLRUN]
base_commit: 73252798
branch: agent/zcode/M2-SFX-E2E-MATERIAL
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-E2E-MATERIAL-zcode
---

# M2-SFX-E2E-MATERIAL：SFX 翻译端到端验证与素材扩展

## 背景（用户裁决④：全权授权寻找、下载、测试）

KO-RERUN §7.7：K11 唯一 SFX region OCR 空=素材缺口。推荐路线=**ja BJ06 先行**（已有 9 个 SFX region，`dialogue-readiness-worksheet` SFX 骨架引用过，零新素材）+ 新素材扩展。用户全权授权素材的寻找/下载/测试。

## 交付（AC）

1. **AC1 BJ06 端到端验证（先行，零新素材）**：`run_qualification.py --case BJ06 --sfx-policy translate`（SFX-ENTRY 控件）+ `--determinism-track remote`——**SFX region 端到端翻译落库验证**（SFX-ENTRY 配置→PRIMARY 门全域→SEM-1 prompt 特化→DeepSeek 拟声词文化对等转换→译文落库）：SFX region 译文非空数量、文化对等质量抽检（对照 SFX-SEM-1 的 ≤6 字符/禁直译规范）、与 speech region 对照。这是 SFX 家族（DETECT→PROD→SEM→ENTRY→PRIMARY）全链的最终闭环实证。
2. **AC2 SFX-rich 素材搜寻与核定**：开放许可的 SFX-rich 漫画页搜寻（候选源：densho810 BJ 官方卷其他页（已有许可框架）/ Pepper&Carrot 其他语言包 / 其他 CC 开放漫画）——每候选登记：来源 URL、许可条款（一手证据快照，沿 CALIB license-evidence 先例）、SFX 密度评估（页面含拟声词图形文本的目检）、分辨率/版面适配性。**产出=候选清单+许可核定+SFX 密度评估，择优下载入池**（`test_assets/comic_golden_suite/` 沿 TA2B 目录纪律+checksum inventory），入池 case 登记（case_id 沿用家族命名）。
3. **AC3 新素材端到端测试**：入池页跑 SFX 检测（chiqui7）+ policy=translate 全链——SFX region 检出→gate 放行→翻译落库端到端；与 BJ06 结果合并为 SFX 端到端能力结论。
4. **AC4 纪律**：下载素材许可**一手证据**先行（无明确许可的来源直接排除）；densho810 素材沿用既有署名义务框架（TA2B 先例）；key 零明文；成本预算：BJ06 全链 ≈34 region×2 请求≈70 请求 + 新素材端到端单页——合计 est token 预算 10 万内（远低于全量口径）。

## 允许修改面

`verification/M2-SFX-E2E-MATERIAL/**`、`experiments/M2-SFX-E2E-MATERIAL/**`、`test_assets/comic_golden_suite/**`（新素材入池沿 TA2B 目录与 checksum 纪律——**素材文件本身走 gitignored 外部树+checksum 登记模式**，沿 TA2B/TA2C 先例）、`test_assets/comic_golden_suite/manifests/**`（case 登记）、Task/Handoff。

## 禁改面

`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、既有 case 产物与 manifests 条目（只增不改）、`doc/STATUS.md`、首跑/KO-RERUN 产物。

## 纪律

- **许可纪律最高优先**：来源许可一手快照先行、无许可即排除、署名义务登记（densho810 报告义务先例）。
- BJ06 跑用生产语义（policy=translate 是用户裁决④的配置选择——该对照跑本身登记为 directional）。
- 与 M2-TA3-B3-KO-FULLRUN 并行无文件交集（BJ06 是 ja case、FULLRUN 是 ko）。

## 交付与运行记录（2026-10-02 ZCode 实现）

- 交付：`verification/M2-SFX-E2E-MATERIAL/sfx-e2e-report.md`（主报告）+ `bj06-run/**` + `new-assets-run/**` + `material-inventory.json` + `sfx-detect-diagnosis.json`；工具 ×4 入 `experiments/M2-SFX-E2E-MATERIAL/`；cases.json 97→100（BJ13/BJ14/BJ15，+214/-0 只增）。
- **AC1 PASS（闭环达成）**：BJ06 `--sfx-policy translate --determinism-track remote --meter-translation`——pipeline_completed=True（run1+run2 completed、17/17 region 零 defect、export OK）；chiqui7 检出 8 sfx + 9 speech（与首跑同分布——任务书背景「9 个 SFX region」实测为 8，登记笔误级偏差）；SFX gate 放行 8/8、**译文落库 8/8 非空**（final_source=machine）；质量抽检 ≤6 字符 8/8、无音节直译、`ハチン→啪` 为文化对等典型（directional）；speech 9/9 不受扰（8/9 与首跑逐位一致、1/9 语义等价合法重译）；K11 裁决项 7 正面关闭（首跑 BJ06 sfx region OCR 全非空——素材缺口不在 BJ06）。
- **AC2 PASS**：densho810 路线（优先级 a）——许可一手快照（sha256 `2bb1dc9f…`，条款逐条复证）+ vol03 全卷 221 页目检（9 候选→3 页）；P&C（b）SFX 密度结构性≈0 未选、其他来源（c）未启用；BJ13（p0048 ピ一一ーン！×2）/BJ14（p0060 オギャァ×3）/BJ15（p0159 オギャァ×2+对白同页）入池：DPI 150 渲染、逐页 sha256、像素入本 worktree gitignored 套件目录、源 PDF 只读引用（本 worktree 以外零写入）、署名/报告义务沿 TA2B 框架。
- **AC3 PASS（链路）+ 检测域缺口如实登记**：BJ13/14/15 全链 3/3 pipeline_completed、export OK、speech 16 region 翻译正常、BJ13 sfx region 1/1 端到端落库；但 chiqui7 sfx 类对 BJ 大型毛笔竖排 SFX 召回为盲区（7 目检实例：sfx 类 0 命中、6 个被 panel 类 0.92-0.97 高置信覆盖、BJ13 唯一 sfx region=T 恤印花误报）——检测段=SFX 端到端覆盖的真实瓶颈（directional，与 DETECT-EVAL §4「检出+分类两层」结论收敛），域扩展属后续 Task+用户裁决，本 Task 零生产改动。
- **AC4 PASS**：合计 68 请求 ≈40.7k est token（预算 10 万的 40.7%）；key 零明文（env 注入+scrub_secrets）；禁改面零 diff（src/tests/contracts/packaging/apps/既有 case 产物/STATUS）；manifests 只增不改。
- Handoff：`doc/handoffs/M2-SFX-E2E-MATERIAL-<delivery_head>.md`。遗留：densho810 报告邮件=用户待办（TA2B 草稿覆盖同源新增）；SFX 检测域扩展与正式 SFX 质量 Gate=候选后续 Task。
