# M2-TA3-B 释放证据（release @c4039415，2026-10-01）

## 授权
用户 2026-09-30 裁决（TA3-B 暂缓待 Provider 稳定+届时单独定义各阶段质量阈值）+ 2026-10-01「继续」推进（SFX 家族收官后推荐候选 1）。

## 侦察结论（两阶段拆分依据）
1. 素材就绪：TA2B BJ01-BJ12+P&C ja+KO 开放素材池（cases.json 特性 tags）。
2. 检测就绪：ogkalu+chiqui7 双 provider 生产上线；质量已被 C4/C1 深度验收——不重复验收（引用口径）。
3. OCR 未就绪可补：适配器在位、manga-ocr/PaddleOCR 主 venv MISSING（隔离 venv 安装）。
4. **翻译 BLOCKED_ON_USER**：Sakura 本地无服务响应；remote 需用户 endpoint+key——阶段二启动条件=用户二选一。
5. TA3-A runner（run_smoke.py）+ probe/backfill 工具=阶段二基座；inpaint=SimpleFillProvider（质量上限如实界定）。

## 阶段拆分
阶段一（本 Task）：阈值定义文档（各阶段口径+提案数值，用户可撤销）/OCR 安装冒烟/20 case 特性矩阵选取/阶段二执行计划。
阶段二（BLOCKED_ON_USER）：正式 run+OCR CER 实测+翻译人工评分+质量报告+独立 Review。
