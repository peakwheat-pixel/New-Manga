# M2-SFX-E2E-MATERIAL 集成记录（代行 Codex / 编排会话）

- 分支 `agent/zcode/M2-SFX-E2E-MATERIAL`；链：7-rulings release `24a89d7d` → `40a8ceec`(implement) → `04966987`(handoff，r1 被审头) → `f53dd445`(返修，r2 被审头) → 集成（merge 内，无独立修正刀——r1 条件已由返修全闭，集成方核验无新增修正）
- Review 链：DSH r1 **有条件通过**（R1 P1=AC3 影响面被自家产物反证：BJ13 两目检 SFX 被误路由 speech 走对话链乱译进渲染；R2 P2=诊断复用 DETECT-EVAL 已废止单侧 coverage+隐去同位置 text 框；`doc/reviews/M2-SFX-E2E-MATERIAL-40a8ceec-dsh-r1.md`）→ Owner 返修 R1-R10 全 closed（R1 选项①：损害形态重写「SFX 误路由 speech→对话链乱译→进渲染，与 SfxPolicy 无关」+14/16 限定+独立 Task 候选登记；R2 诊断重生成=逐参照枚举相交框，BJ13 text conf 0.744/0.844 IoU 0.452/0.544 vs panel 大框 IoU 仅 0.029/0.037→**归属未定**；R10 cases.json 新口径「PASS=放行且译文非空」重算零 diff 零改判）→ DSH r2 **approved（可集成）**（`doc/reviews/M2-SFX-E2E-MATERIAL-f53dd445-dsh-r2.md`）

## 正式结论

1. **SFX 翻译链端到端闭环实证**（BJ06）：gate 放行 8/8→译文落库 8/8 非空（final_source=machine）；质量抽检 ≤6 字符 8/8、无音节直译、ハチン→啪 文化对等；speech 对照零扰动（8/9 逐位+1/9 合法重译）。SFX 家族 DETECT→PROD→SEM→ENTRY→PRIMARY 全链闭环。
2. **新素材入池**：densho810 vol03 许可复证（三条 JASRAC 页位清单，R4 补 11巻/77頁）→BJ13/14/15 三页入池（cases.json 97→100 只增）；BJ13 sfx=PASS（R10 新口径：放行且译文非空）、BJ14/15=NOT_RUN。
3. **检测段=真实瓶颈（如实）**：chiqui7 sfx 类对 BJ 毛笔竖排 SFX 0 命中；**误路由损害形态（speech 乱译进渲染页）=DETECT-EVAL §4.4 域扩展裁决清单的优先级权重输入**（独立 Task 候选已登记，等用户裁决释放）。
4. 成本 68 请求 ≈40,735 est token（预算 40.7%）；key 零明文。

## 集成运行时项

- post-merge 三套件：**603+1skipped 0 failed**（close 前复跑）
- r2 新发现 6 项 P4/OBS 随手登记（详见 r2 报告）
- follow-up 候选（等用户裁决）：SFX 误路由损害形态处置=检测域扩展；densho810 报告邮件=用户待办（新入池页沿 TA2B 框架）
