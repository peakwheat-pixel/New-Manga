---
id: M2-SFX-TILE-WIDTH-CALIB-1
title: "SFX tile 路由宽≠600/690 逐宽校准：多宽页 directional 评测与阈值维持/修订提案"
kind: feature
status: in_review
owner_claim: ZCode 2026-10-04 @worktree M2-SFX-TILE-WIDTH-CALIB-1-zcode（base=d298ecd0=释放登记 tip；授权=user 2026-10-04 批准进行2 非阻塞候选③；默认零 src、AC3 三选一硬门=诚实）
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
approval: user_2026-10-04_批准进行2（已登记非阻塞候选③：T5 deploy-report §3①/KO-TILE §9 既有缺口+§3④ 跨域激活代价）
depends_on: [M2-SFX-T5-TILE-KO]
base_commit: d298ecd0（owner 分支实际 fork 点，merge-base 实证；release commit 自身的 parent=72807d30=释放登记 base——DSH r1 P2-1 统一取实际 fork 点，集成 diff 范围以本值为准）
branch: agent/zcode/M2-SFX-TILE-WIDTH-CALIB-1
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-TILE-WIDTH-CALIB-1-zcode
review_events: [r1 DSH approved_with_conditions 2026-10-06（0×P0/P1、2×P2、10×P3、7×P4；P2-1/P2-2+采纳 P3/P4 由集成 docs-only 返修闭合，报告 doc/reviews/M2-SFX-TILE-WIDTH-CALIB-1-c01ef086-dsh-r1.md，评测数字零变化）]
created: 2026-10-04
delivery_commit: 6b90b80b（证据+结论；docs commit 见 git log 尾部）
handoff: doc/handoffs/M2-SFX-TILE-WIDTH-CALIB-1-zcode-20261004.md
report: verification/M2-SFX-TILE-WIDTH-CALIB-1/width-calib-report.md
---

# Task: M2-SFX-TILE-WIDTH-CALIB-1 — tile 路由宽≠600/690 逐宽校准

## 背景与授权

T5-TILE-KO（done @merge `5e70af4e`）冻结口径：宽≤690 且 aspect≥8.0 路由 tile（tile_h=1024/overlap=128/NMS IoU 0.5），校准数据仅覆盖 KO 域观测宽 **600/690**（KO-TILE-CALIB §9：GT 页集仅 690/600 宽）；deploy-report §3① 登记「宽≠600/690 的 KO 形页按常量阈值参数化路由，未逐宽重校」；§3④（DSH r1 P3-2）登记「路由按页面形状全局生效，非 KO 长条页亦走 tile（≈20× 代价），跨域激活的代价评估与阈值复标留后续 Task」。用户 2026-10-04 批准进行2，释放本 Task。

## 验收条件

- **AC1 多宽页评测集**：汇集宽≠600/690 的长条/宽页样本（来源裁量并如实登记：own-manga KO/webtoon 域页、既有 case 其他宽度页、合成变体[已知真值页经宽度重采样]）；每宽度档登记页数与 GT 来源（真实 GT/伪 GT[partial/pseudo]/合成精确 GT），**自锚风险逐来源声明**。
- **AC2 directional 评测**：对每宽度档跑生产 tile 口径 vs letterbox 口径（经生产代码路径 `SfxDetectionProvider.detect`，env 覆盖 off 即 letterbox），记录：候选数/匹配数（按可用 GT）/耗时（tile 预期 ≈20×，逐宽实测）；权重=v2b 生产 pin 原样（如需 chiqui7 对照走 sha 先验断言+finally 恢复先例）。
- **AC3 校准结论（硬门=诚实，不是改代码）**：产出逐宽表现表+三选一结论并给证据：(a) 冻结阈值在未校准宽度上表现可接受→**维持现状**，缺口以本 Task 证据关闭（零 src 变更合法 done）；(b) 特定宽度表现劣化→产出阈值修订提案（env 默认/常量改动的**提案**，不实施——实施属后续 Task，须引用本证据）；(c) 证据不足以裁决→如实登记 NOT_CONCLUSIVE+补样建议。**禁止无证据改冻结常量。**
- **AC4 纪律与文档**：评测脚本+raw 证据落 `experiments/`+`verification/`（JSON 逐字段自洽，禁「显著」措辞，directional 声明）；宽度重采样若产生新图，落外部树不入 Git；权重 sha 先验断言+finally 恢复（先例）；Task 回填+Handoff。

## 纪律与限制

- 允许路径：`experiments/M2-SFX-TILE-WIDTH-CALIB-1/**`、`verification/M2-SFX-TILE-WIDTH-CALIB-1/**`、`doc/tasks/M2-SFX-TILE-WIDTH-CALIB-1.md`、`doc/handoffs/`；**默认零 src 变更**——若 AC3 结论为 (b) 仍只交提案文档，不改 src。
- 禁改：`src/**`、`tests/**`、`packaging/**`、`contracts/**`、`apps/**`、`doc/STATUS.md`/`doc/REBASELINE_PLAN.md`。
- 分支 `agent/zcode/M2-SFX-TILE-WIDTH-CALIB-1`，worktree 独立。
- 环境：生产等价 venv=`T1.1.1-impl-py312`（现装 onnxruntime-directml 1.24.4）；GPU 默认（DML），tile 页 CPU 会 ~10s/页勿用；长命令后台+log+轮询；权重/GT 外部树路径：`weights-v2b/`、own-manga 素材树（Owner 盘点后引用实际路径）。

## 交付与运行记录

- **2026-10-06 Owner（ZCode）交付**，base `d298ecd0`，delivery_head `6b90b80b`（docs commit 见 git log 尾部）。提交链：`7aebe44c` claim → `c67b825b` 盘点登记（INPUTS.md）→ `c9887f81` 评测脚本 → `6b90b80b` 证据+结论 → docs（本回填+Handoff）。
- **AC1 评测集**：素材盘点硬结论=真实素材零「宽≠600/690 且 aspect≥8.0」KO/webtoon 页（own-manga 6 卷 2018 页全普通宽页、韩漫_KO 金标套件 70 图全 600/690 宽、train-v2 aspect≥8 仅 pre-k01~k10）；按合同两条授权路径补样=10 宽度档 14 页（原生锚点 W690/W600 真实 GT 51+3 框；重采样 640/480/320/800/1024 派生 GT 相似变换精确+插值损失声明；程序合成 384/560/680 精确 GT 46-49 框/页）；页图在 gitignored 外部树（sha 断言 manifest），逐来源自锚风险声明见 INPUTS.md §3。
- **AC2 评测**：生产 `SfxDetectionProvider.detect`（本 worktree src），每档 tile（默认 env）vs letterbox（`NEWMANGA_SFX_TILE=off`）× conf 0.5 主/0.2 参考；权重 v2b pin 原样 sha 先验断言零重指；DML GPU；match_gt 蓝本逐字（IoU≥0.5）；warm-up 不计+计测。
- **锚点自检（硬断言）**：原生档 tile conf0.5 逐页复现 T5 parity raw（pre-k08 14/27、pre-k09 17/24、pre-k02 2/3 全 MATCH）——harness 测的就是生产序列。
- **AC3 结论（硬门=诚实）**：**(a) 维持现状**——域内重采样档 640/480/320 tile conf0.5 recall 0.647/0.686/0.686 与原生 690 档 0.608 同量级（precision 同量级），letterbox 面 10 档×双 conf 全零候选（结构性事实逐宽复现），合成档（字形域偏移声明内）tile 优势保持（precision 0.818-0.923），域外 800/1024 维持 letterbox 结构性零检出=路由谓词语义一致；无任何宽度档出现支持阈值修订的劣化证据，**冻结常量零改动、零 src 合法 done**。directional 限制如实（每档 1-2 页、W600 仅 3 框、重采样混合宽度与有效分辨率两因素）。
- **§3①④ 缺口关闭登记**：deploy-report §3①「宽≠600/690 未逐宽重校」以本证据关闭；§3④ 跨域激活代价获 GPU 档 directional 实测补强（w≤690 非 KO 域长条页 tile ms/tile 16.3-18.4ms[页级 ~0.8s/页随 tile 数/页高线性]、tile:letterbox ≈6.5-12×；GPU 档口径，T5 ≈20× 为 CPU 档口径并记）。
- **AC4 纪律**：零 src/tests/packaging/contracts/apps/STATUS/REBASELINE diff；directional 措辞；权重/合成页/GT 不入 Git；运行期脚本 bug 两处（锚点条件误含重采样页、域外打印 KeyError）写盘前修复重跑、跨进程域内数字逐位一致（报告 §4）。
- **Handoff**：[doc/handoffs/M2-SFX-TILE-WIDTH-CALIB-1-zcode-20261004.md](../handoffs/M2-SFX-TILE-WIDTH-CALIB-1-zcode-20261004.md)（recipient=DeepSeek Harness 非作者独立 Review→编排代行 Codex 集成）。
- **未运行项（如实）**：chiqui7 对照面（合同「如需」条款，无权重变更不触发）；CPU 档耗时（合同明令禁止 CPU tile）；更极端宽度（<320）无素材。
- **2026-10-06 集成返修（DSH r1 条件闭合，docs-only、评测数字零变化）**：P2-1 base_commit 统一 d298ecd0（merge-base 实证）；P2-2 conf 0.2 口径「原生 vs 重采样」排序翻转如实登记（报告 §2 脚注+§5）；P3-1 耗时比收紧 ≈6.5-12×（逐档 6.5-11.6×）；P3-2 docstring 与实际行为对齐+§5 登记上限侧（700-1024）tile 面未测；P3-3 宽度阶梯非独立声明（INPUTS §3.5）；P3-4/P3-5/P3-6 限制注记（锚点断言覆盖面/match_gt 返回字段省略/EP 键未落 raw）；P3-7 跨轮一致性主张收紧（未入库不作证据）；P3-8 §5 头句限定真实内容重采样档；P3-9 ms/tile 主口径；P3-10 脚本 env 恢复补 finally（控制流对齐合同字面，无数字路径变化，证据不重跑）；P4-3/P4-7 INPUTS 补登；P4-1/P4-2/P4-4/P4-5/P4-6 接受现状注记（报告 §7）。
