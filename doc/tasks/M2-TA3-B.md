---
id: M2-TA3-B
title: "TA3-B：20 案例端到端质量验收——阶段一（阈值定义+OCR 安装冒烟+case 选取）；阶段二（正式 run）BLOCKED_ON_USER 翻译 endpoint 二选一（用户「继续」推进 2026-10-01）"
kind: qualification
status: in_progress
approval: user_directive_2026-10-01_continue_ta3b
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-TA3-A, M2-TA2B, M2-PROD-DETECT-1, M2-SFX-PROD-1]
base_commit: c403941560c5094c088b0ea8ba1b707f30e2ea51
branch: agent/zcode/M2-TA3-B
worktree: G:/CODEX/New Manga.worktrees/M2-TA3-B-zcode
---

# M2-TA3-B：20 案例端到端质量验收（拆两阶段）

## 来源与目标

- 来源：用户 2026-09-30 裁决「TA3-B=20-case 质量 qualification 暂缓待 Provider 稳定，届时**单独定义各阶段质量阈值**」；2026-10-01 用户「继续」授权推进（SFX 家族收官后推荐候选 1）。
- 目标：对产品核心链路（detect→OCR→translate→inpaint→render/export）在 20 case 上做**分阶段质量验收**。检测质量已被 C4/C1 深度验收（Recall 0.9618+抽检校准），本 Task **不重复验收**（引用既有口径）；重心=OCR（manga-ocr/PaddleOCR 从未质量验收）+ translate（SFX 语义新上线后的真实质量）+ 全链组合。

## 释放侦察结论（决定两阶段拆分）

1. **素材就绪**：TA2B 交付 BJ01-BJ12 + P&C ja（J48-J52）+ KO（K14-K25）开放素材池，cases.json 含特性 tags（黑白/RTL/竖排/气泡/SFX/复杂背景/小字大字）——20 case 按特性矩阵选取即可。
2. **检测就绪**：ogkalu 生产 provider（+chiqui7 SFX）。
3. **OCR 未就绪（可补）**：`ocr_local.py` 适配器在位（manga-ocr=ja、PaddleOCR=ko），主 venv 两模型依赖均 MISSING——需安装（隔离实验 venv）+单页冒烟。
4. **翻译 BLOCKED_ON_USER**：本地 Sakura（127.0.0.1:8080）无服务响应=模型未部署；remote OpenAI-compatible 需用户 endpoint+key（外部凭证，Owner/编排会话无法自行取得）。**阶段二启动条件=用户二选一**：(a) 提供 OpenAI-compatible endpoint+key；(b) 授权下载部署本地 Sakura 模型（GB 级）。
5. **TA3-A 基座**：`experiments/M2-TA3-A/run_smoke.py`（生产 seam 全链 runner）+ probe/backfill 工具可扩展；inpaint=SimpleFillProvider（基础填充，质量预期如实界定）。

## 阶段一（本 Task 交付，无外部依赖）

- [ ] AC1（阈值定义文档）：`verification/M2-TA3-B/quality-thresholds.md`——各阶段质量口径与阈值定义：①detect=引用 C4/C1 冻结口径（不重复验收，仅冒烟健全性）；②**OCR=主判定**——ja（manga-ocr）字符准确率 CER 逐 region 对照+KO（PaddleOCR）同法，抽检人工核对设计（AI 预判+用户审核模式，C1 先例）；③translate=拟声词文化对等抽检（SFX-SEM-1 语义落地核对）+对白可读性人工评分表（5 分制，n≥30 region）；④inpaint=SimpleFill 视觉残差定性抽检（如实界定"基础填充"上限）；⑤render/export=TA3-A 确定性框架引用；⑥全链=pipeline_failures=0 + 各阶段产物存在性。每阶段阈值数值由本 Task 提案（acting Codex 裁决登记，用户可撤销）。
- [ ] AC2（OCR 安装+冒烟）：隔离实验 venv 安装 manga-ocr+PaddleOCR（代理）+ 模型权重下载 + 各 1 页冒烟 EXIT=0（权重路径/尺寸登记；gitignored）。
- [ ] AC3（20 case 选取）：从 cases.json 按特性矩阵选 20 case（日漫 BJ/P&C 10+韩漫 KO 10；tags 覆盖矩阵说明）+ manifest（路径+SHA256+特性 tags）+ 与 TA3-A 的 5 case 关系说明（子集/超集）。
- [ ] AC4（阶段二执行计划）：正式 run 的 runner 扩展设计（基于 run_smoke.py）+ 翻译两选项的操作手册（用户二选一后阶段二即启）。
- [ ] AC5（纪律）：生产 src/requirements 零改动（实验 venv/文档/manifest only）；diff --check EXIT=0；权重零入库。

## 阶段二（BLOCKED_ON_USER，另行释放或本 Task 解锁）

- 正式 run（20 case 全链真实产物）+ OCR CER 实测 + 翻译人工评分 + 质量报告 + 独立 Review。

## 允许/禁止

允许：`verification/M2-TA3-B/**`、`experiments/M2-TA3-B/**`（新增，runner 扩展设计+case manifest）、隔离实验 venv（`G:/CODEX/New Manga.task-envs/M2-TA3-B-*/`）、Task/Handoff。
禁止：生产 src/**、requirements.txt、packaging/**、apps/**、TA3-A 产物改动（只读复用）、权重入库。

## 依赖、风险与阻塞

- 依赖：TA3-A（runner 基座）、TA2B（素材）、DETECT-1（检测 provider）、SFX-PROD-1（SFX 语义）。
- 风险：①manga-ocr/PaddleOCR 模型下载体积大（数百 MB）——代理可用，失败如实登记；②阈值提案的数值合理性（无历史基线，提案+用户可撤销）；③阶段二启动依赖用户输入。
- 阻塞：阶段二 BLOCKED_ON_USER（翻译 endpoint 二选一）；阶段一无阻塞。
