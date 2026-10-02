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
2. **AC1 BJ06 端到端（SFX 家族链最终闭环）**：`--sfx-policy translate --determinism-track remote --meter-translation` → pipeline_completed=True（run1 357.6s + run2 336.9s、17/17 region 零 defect、export OK `c1d503f4…`）；chiqui7 检出 17 region（8 sfx + 9 speech，与首跑同分布）；SFX gate 放行 8/8（`sfx_policy` 字段实测 skip→translate）；**SFX 译文落库 8/8 非空**（final_source=machine）；质量抽检（directional）：≤6 字符 8/8、无音节直译、`ハチン→啪` 文化对等典型；speech 9/9 不受扰（8/9 与首跑逐位一致、1/9 语义等价合法重译）。任务书背景「9 个 SFX region」实测 8（KO-RERUN §3.2 同口径），登记笔误级偏差。K11 裁决项 7 正面关闭。
3. **AC2 素材搜寻/核定/入池**：densho810 路线（优先级 a）；许可一手快照 sha256 `2bb1dc9f…`（条款逐条复证：二次利用フリー/署名/1 个月报告/Kindle 禁令/JASRAC 页位）；vol03 全卷 221 页缩略图目检→9 候选 100dpi 复查→**BJ13（vol03_p0048 ピ一一ーン！×2）/BJ14（vol03_p0060 オギャァ×3）/BJ15（vol03_p0159 オギャァ×2+对白）** 入池；DPI 150 渲染（2946×4167）、逐页 sha256 入 `material-inventory.json`；cases.json 97→100 **只增**（+214/-0，程序化 append、冲突 fail-closed）；像素入本 worktree gitignored 套件目录、源 PDF（TA2B worktree）只读引用——**本 worktree 以外零写入**。
4. **AC3 新素材端到端**：3/3 pipeline_completed（export OK×3、speech 16 region 翻译正常、BJ13 sfx region 1/1 落库『．．．』→『……』）+ **检测域缺口如实登记**：chiqui7 sfx 类对 BJ 大型毛笔竖排 SFX 盲区（7 目检实例：sfx 类 0 命中、6 个被 panel 类 0.92-0.97 高置信覆盖、BJ13 唯一 sfx region=T 恤印花误报 conf 0.82）——directional，`diagnose_sfx_detect.py` 零 src 改动复放生产推理序列取证。
5. **AC4 纪律**：合计 68 请求 ≈40,735 est token（预算 10 万的 40.7%）；key env 注入+scrub_secrets、入库文件 leak 扫描 CLEAN；禁改面零 diff；manifests 只增不改。
6. **合并能力结论**：SFX 翻译语义链（gate 放行→SEM-1 特化→DeepSeek 转换→落库）在 ja 域闭环实证（BJ06 8/8 + BJ13 1/1）；**检测段是 SFX 端到端覆盖的真实瓶颈**（新素材域 panel 类混淆），域扩展属 DETECT-EVAL §4.4 既有裁决清单，本 Task 零生产改动。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 BJ06 e2e | `run_qualification.py --case BJ06 --sfx-policy translate --determinism-track remote --meter-translation`（独立 out-dir/pixel-root，首跑产物零改动） | 融合 venv `M2-TA3-B-ocr`，worktree @24a89d7d | PASS（pipeline_completed=True） | `verification/M2-SFX-E2E-MATERIAL/bj06-run/summaries/qual-BJ06.json`、`run.log` |
| AC1 质量抽检+speech 对照 | summary JSON 解析（8 条 SFX 逐条表 + 首跑对照） | 同上 | PASS（directional；表见主报告 §1.3/§1.4） | `verification/M2-SFX-E2E-MATERIAL/sfx-e2e-report.md` |
| AC2 许可快照 | curl densho810.com/free/ → sha256 → 关键词逐条复证 | — | PASS（义务沿 TA2B 框架） | Git 外 `task-envs/M2-SFX-E2E-MATERIAL/license-evidence/`；`material-inventory.json` |
| AC2 目检与入池 | `render_vol_pages.py`（40dpi 全卷→contact sheet 目检→100dpi 复查→150dpi 正式渲染）+ `register_new_cases.py`（append-only） | 同上 | PASS（3 页入池；cases.json +214/-0） | `material-inventory.json`、`test_assets/comic_golden_suite/manifests/cases.json`（BJ13-15） |
| AC3 新素材 e2e | `run_new_asset_e2e.py`（复用 run_case 原样，policy/metering 强制） | 同上 | PASS（3/3 pipeline_completed） | `verification/M2-SFX-E2E-MATERIAL/new-assets-run/summaries/` |
| AC3 检测诊断 | `diagnose_sfx_detect.py`（conf≥0.25 全类保留 + 参照框 coverage 分类 + 预览目检） | 同上 | 完成（缺口如实登记，directional） | `verification/M2-SFX-E2E-MATERIAL/sfx-detect-diagnosis.json` |
| AC4 纪律 | `git status --porcelain` / `git diff --check` / 禁改路径 grep / key leak 扫描 | @40a8ceec | PASS（禁改面零触碰；leak CLEAN） | 本 Handoff + 主报告 §4/§5 |

未运行/不适用：BJ01-BJ12 其余页、BJ14/15 的 SFX gate 段（页面无 sfx region，NOT_RUN 如实登记于 cases.json pipeline_status）；正式 SFX 翻译质量 Gate（属 TA3-B 全量口径，本 Task 为 directional 抽检）。

## 接收方式

- 分支 `agent/zcode/M2-SFX-E2E-MATERIAL`（base `73252798`，delivery_head `40a8ceec`），worktree 同 Task frontmatter。
- 复现命令：主报告 §6（BJ06 跑/渲染/新素材跑/诊断/cases 登记五段，key 需先 `export TA3B_TRANSLATE_API_KEY=$(cat …/deepseek.key)`）。
- Review 检查建议：①qual-BJ06.json 的 8 条 sfx translate_details 与抽检表逐条对照；②cases.json diff 仅 BJ13/14/15 追加；③`material-inventory.json` 与 Git 外快照 sha256 一致性；④`diagnose_sfx_detect.py` 判读（sfx-detect-diagnosis.json + Git 外预览 3 张）。

## 下一任务建议（必填）

- **Review（先行）**：DeepSeek Harness 对 `40a8ceec` 做 r1 静态 Review（重点：AC1 端到端证据链、cases.json 只增、许可快照 sha256、检测域发现的 directional 口径）。可直接转发指令：「对分支 agent/zcode/M2-SFX-E2E-MATERIAL tip `40a8ceec`（Task M2-SFX-E2E-MATERIAL，base 73252798）执行非作者 Review：主报告 `verification/M2-SFX-E2E-MATERIAL/sfx-e2e-report.md`，按 Task AC1-AC4 与禁改面核对，重点抽检 qual-BJ06.json 的 SFX translate_details 8 条与报告 §1.3 表、cases.json BJ13-15 追加条目与 material-inventory.json 的 sha256 一致性、sfx-detect-diagnosis.json 的 panel 类混淆判读。」
- **候选后续 Task（需 Codex 释放+用户裁决，非本 Task 范围）**：SFX 检测域扩展（BJ 毛笔竖排 SFX 的 panel 类混淆处置：后分类器/阈值重冻结/再训练评估——沿 DETECT-EVAL §4.4 七项集成前条件）；BJ06 全 17 region 纳入 TA3-B 正式质量口径（remote 轨 similarity Gate 的 ja 侧样本扩充）。
- densho810 报告邮件=用户待办（TA2B 草稿覆盖本批同源新增，无需新草稿）。
