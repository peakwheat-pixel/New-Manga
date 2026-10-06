---
id: M2-SFX-TILE-WIDTH-CALIB-1
title: "SFX tile 路由宽≠600/690 逐宽校准：多宽页 directional 评测与阈值维持/修订提案"
kind: feature
status: owner_claim
owner_claim: ZCode 2026-10-04 @worktree M2-SFX-TILE-WIDTH-CALIB-1-zcode（base=d298ecd0=释放登记 tip；授权=user 2026-10-04 批准进行2 非阻塞候选③；默认零 src、AC3 三选一硬门=诚实）
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
approval: user_2026-10-04_批准进行2（已登记非阻塞候选③：T5 deploy-report §3①/KO-TILE §9 既有缺口+§3④ 跨域激活代价）
depends_on: [M2-SFX-T5-TILE-KO]
base_commit: 72807d30
branch: agent/zcode/M2-SFX-TILE-WIDTH-CALIB-1
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-TILE-WIDTH-CALIB-1-zcode
review_events: []
created: 2026-10-04
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
