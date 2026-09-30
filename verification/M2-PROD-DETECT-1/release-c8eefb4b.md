# Release: M2-PROD-DETECT-1（生产检测器集成第一刀）

- 日期：2026-09-30（Asia/Shanghai）
- 授权：用户对本会话推荐下一步（「docTR 检测器生产集成 Task——回复『释放生产集成』即可启动」）回复**「继续」**（2026-09-30），即授权按推荐推进；Codex 范围化释放由编排会话代行（用户全权授权 2026-09-28/30）。
- 登记 commit：本文件与 [Task](../../doc/tasks/M2-PROD-DETECT-1.md) 同 commit 入 main；release base = `c8eefb4b`（main @integration(M2-DOCTR-QUAL-C1) 收口）。
- 冻结：branch=`agent/zcode/M2-PROD-DETECT-1`；worktree=`G:/CODEX/New Manga.worktrees/M2-PROD-DETECT-1-zcode`（从 release commit 检出）；Owner=ZCode（子 agent），非作者 Reviewer=DeepSeek Harness，Integrator=编排会话代行 Codex。

## 释放侦察事实（live，2026-09-30）

- 生产检测器：`src/infrastructure/providers/detection_doctr.py`（405 行）——T1.1.1 选型，fail-closed 四纪律（无运行时下载/SHA-256 pin/缺失=PROVIDER_NOT_CONFIGURED/匿名 label），冻结合并策略 MERGE_*（T1.1.1 gate，改动=契约变化）。
- 装配：`src/bootstrap/core_assembly.py` L686-706 硬编码 DoctrDetectionProvider；权重默认 `<data root>/models/detector/fast_base-688a8b34.pt`（`NEWMANGA_DETECTOR_WEIGHTS` 覆盖）、device `NEWMANGA_DETECTOR_DEVICE`（默认 cpu）；mock_local_providers 验收路径独立。
- 接口：`ports/detection/ports.py`——DetectionRequest（编码字节）/DetectionResult/RegionCandidate（匿名 label+polygon+coordinate space），provider 中立，业务 ID 由 caller 分配 → **预期契约零修订**。
- 依赖：requirements.txt 有 python-doctr==1.1.0 + torch==2.14.0 + torchvision==0.29.0（CPU wheels=支持配置；GPU 是单独决策）→ **transformers==5.17.0 + safetensors 为本 Task 授权的新增项**；torch 2.14.0 CPU × transformers 5.17 兼容性未知（C4 全程 torch 2.11.0+cu128 GPU）→ AC3 首先闭合。
- 权重快照（本地，不入库）：`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector/`（model.safetensors `037930a8…` 171,543,900 B / config `b6d70793…` / preprocessor `7e9e2245…`，HF revision `16e8a622`，Apache-2.0）。
- C4 GPU envelope 引用基线：38.9s/511 regions ≈ 76ms/region（cuda）；CPU 未测（本 Task AC5 闭合）。

## 代理裁决（用户可撤销）

- 默认 backend=manga（`NEWMANGA_DETECTOR_BACKEND` 可切回 doctr）；对无 manga 权重用户是行为变化（docTR 可用→manga typed 缺失+配置指引）——wire 变化实质，集成记录再登记。
- 契约零修订优先；确需改即停待裁决。
- sidecar 分发形态优化（体积/NSIS 带模型）后置，本 Task 只要求构建回归与 clean-start 回归通过。
