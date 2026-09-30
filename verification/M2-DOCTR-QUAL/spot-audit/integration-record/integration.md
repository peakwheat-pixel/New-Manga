# M2-DOCTR-QUAL-C1 Integration Record

- Date: 2026-09-30（Asia/Shanghai）。Integrator=编排会话代行 Codex（用户全权授权 2026-09-28/30）；Owner=ZCode（子 agent）；人工判定=用户本人；非作者 Reviewer=DeepSeek Harness（静态）。Owner≠Reviewer≠Integrator 全程保持。
- **Integration merge = `316abf16`**（parents `0d4d07a9` + Owner tip `4d75efbc`，--no-ff，无冲突；16 文件全允许路径；已集成文件、C4 三个正式 JSON、c4 报告、license-evidence、阶段一 repro-evidence 主体零改动）。

## 交付链（两阶段）

release `0d4d07a9`（base=`4c87c843`，[release-4c87c843](../release-4c87c843.md)）→ 阶段一（agent 全自动）：claim `efdc07a0` → implement `7c6aa234` → handoff/回填 `e2c06791`（Task 置 `WAITING_USER_LABELING`）→ **用户会话指令变更流程**（AI 预判草稿 → 用户逐条人工审核，授权原文已登记 Task 禁止范围条款）→ 用户审核 50/50（47 确认 + 3 人工修订）→ 阶段二：报告 `2c9b7ee7`（r1）→ r2 返修 `4d75efbc`=**delivery_head**。

## Review 轨迹

- DSH r1 [changes_requested](../../../../doc/reviews/M2-DOCTR-QUAL-C1-4d75efbc-dsh-r1.md)（0×P0、4×P1、4×P2、4×P3、2×P4；**三条校准结论算术全部 PASS**，报告原字节 import SHA-256=`3c9319b4f5697ce7f05c6e8592568ee3aeb6d96a268316395f0e5d00e0548e73`）：R1 B1-U11 错分类、R2 分母域越权表述、R3 锚定效应/结论强度、R4 B1-U10 矛盾行、R5-R8 P2、R9-R14 P3/P4。
- Owner r2 返修 `4d75efbc`：R1-R14 逐条处置（文本/分类修订，无重抽样重跑）；重算后盲区 FP 25/30（n_eff=29）、幻觉 4、保守修正 0.9149 / 外推 0.9839 不变。
- DSH r2 [approved_with_conditions](../../../../doc/reviews/M2-DOCTR-QUAL-C1-4d75efbc-dsh-r2.md)（**r1 全部 P1 事实层闭合，独立复算+预览图视觉佐证**；报告原字节 import SHA-256=`7cdd38e02693224caa96e44165d4f6544aa46fdf78af8b93aa750c6a096d06ba`）：N1（P3，B1-U10 措辞与视觉证据+用户确认）、N2（P3，AC 勾选/STATUS 同步）、N4/N5（P4，残留表述）、复算 4 项 sha256、C4 cross-reference——全部集成方闭合项。

## 集成方复算与复跑（merge head `316abf16`）

- `summarize_c1_spot_audit.py` 实跑 EXIT=0，六项纪律校验全 PASS（50 行/分层枚举含 R1 B 层扩展/冻结配额/draft 逐字段 diff/A1+A2 划分/R9 stricter 映射）。
- sha256 复算：worksheet（集成后实值 `a660e3b4…`，报告 §7 已同步并注明 r2 版 `da93f4f9…` 变更原因=N1 措辞更正）、ai-draft `04f225ce…` 与登记一致、sample-json（集成后实值 `7fe79083…`，报告 §7 已同步并注明 r2 版 `4b60643f…` 变更原因=N5 verdict_note 加注）。
- `git diff --check 0d4d07a9..HEAD` EXIT=0；`git status --porcelain` 干净；m2_acceptance **35 passed** EXIT=0（产品面零影响）。

## 集成修正 commit（闭合 DSH r2 N1/N2/N4/N5；标注集成方修正）

- **N1**：B1-U10 rationale/user_rationale 措辞按 DSH r2 更正为「字符状纹样、语义不可辨（非可读文字）」（原「无具体形状」与预览图视觉证据不符），裁决方向与真值仍以用户裁决为准（=模型幻觉），**已在本收口汇报中向用户披露请终审确认**；用户原话依据保留于 user_rationale。
- **N2**：Task AC1-AC5 恢复勾选（r2 超范围退回）；AC6 随集成闭合勾选（注记 DSH r2 verdict + merge hash）。
- **N4**：报告 §0「相互加强」加方向性证据限定；§3.b 标题「确认」→「一致（方向性证据）」；Task 交付记录 r1 版数字加「r1 版、r2 已重算」注记。
- **N5**：脚本 docstring 校验项数 4→6；handoff「四项纪律校验」→六项 + R14 落点更正；sample JSON verdict_note 文本级加阶段二更新注记；repro-evidence 空表 sha256 标注；报告 §3.a/§1 K08 r3 简写统一为「按行切分、一对一匹配只覆盖部分 GT（非漏检）」；报告 §7 补 r1/r2/集成 commit hash + sha256 复算注记 + N3 统计来源口径更正（内容构成为人工归类）。
- DSH r1/r2 报告原字节 import 入 `doc/reviews/`（SHA-256 见上）。
- **教训登记**：sample JSON 集成中曾误用 `json.dumps` 全量重写导致 hash 漂移（`6b257cb2`≠登记值 `4b60643f`），`git checkout` 恢复后改为文本级插入——登记与已登记 hash 绑定的 JSON 文件禁止全量重序列化（DOC-FIX-STALE N-3 blob 基准教训同族）。

## C4 cross-reference（R12/N2 转交项）

C4 报告（只读，按历史忠实原则不改写正文）：其 §5.2「伪 GT 同源性」限定与 §7.2「抽检完成前保留」措辞，已由本 Task（C1）抽检证据**收窄**——贴合非伪造、低 coverage 匹配为系统性切分粒度差异（方向=模型偏细）。本登记与 [c1-spot-audit-report.md](../c1-spot-audit-report.md) §4/§5 为权威出处；后续读者以本记录为准。

## 结论与登记

- **校准结论（方向性证据，n=50 抽检、单标注者、锚定未测量）**：①Recall 分母 8/35 可校验域全查 = 7 噪声 + 1 切分粒度 + **0 真实文字漏检**，域内修正估计 0.9692–0.9703（FN-partial 27 不外推）；②Precision 0.8909 与下界方向一致——抽检 30 FP（n_eff=29）中盲区 FP 25（SFX 6/旁白告示牌海报 8/署名标题话数 7/手写商标 3/真实对白 1）、真幻觉 4，保守修正 0.9149 / 外推 0.9839（只依赖幻觉数）；③D 层零标注 region 文字率 5/10（全部 SFX/屏幕小字，无一对白），Wilson 95% CI [0.237, 0.763]。
- **C4 Gate PASS 的真实世界含义（方向性）**：PASS = 真实对白检测能力的保守下界；反方向限定六条见报告 §5.2。
- 遗留候选（登记不释放）：SFX 检测支持、FN-partial 27 框校验、B1-U10 用户终审确认（本收口汇报披露）。
- Owner branch/worktree 保留于 `4d75efbc`（`agent/zcode/M2-DOCTR-QUAL-C1` / `G:/CODEX/New Manga.worktrees/M2-DOCTR-QUAL-C1-zcode`）。
