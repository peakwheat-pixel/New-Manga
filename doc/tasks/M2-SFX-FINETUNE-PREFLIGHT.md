---
id: M2-SFX-FINETUNE-PREFLIGHT
title: "SFX fine-tune V1 技术预检：训练路线可行性实证+训练环境就绪+许可备案（T0；零 src）"
kind: spike
status: ready
approval: user_ruling_2026-10-04_训练质量效率优先_许可降权备案
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
depends_on: [M2-SFX-DETECT-DOMAIN-EXT-DIAG, M2-SFX-PROD-1, M2-REGION-OVERLAP-ARBITRATION]
base_commit: 74fa71e9
branch: agent/zcode/M2-SFX-FINETUNE-PREFLIGHT
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-FINETUNE-PREFLIGHT-zcode
integration_commit: null
---

# M2-SFX-FINETUNE-PREFLIGHT：SFX 微调 V1 技术预检

## 来源与目标

用户二次裁决（2026-10-04，见 DOMAIN-EXT-DIAG 二次裁决段）：启动 SFX 微调 V1 项目；许可降权备案不阻断；**最高原则=训练质量与效率**。本 Task 为训练线第一环：实证三条训练路线的技术可行性，定案 V1 路线，搭好训练环境——**避免直接开训后才发现权重不可得/显存不够/导出不兼容浪费算力**。

## Acceptance Criteria

- [ ] AC1 路线 A 技术实证（chiqui7 续训，效率首选）：①HF `chiqui7/yolo11-manga-seg` 是否提供**原生 .pt 训练权重**（生产现用 41MB ONNX 不能直接微调——Ultralytics 对 ONNX 回训支持有限，必须查证）；②训练代码/配置完整性（Ultralytics yolo11 seg 训练入口）；③**四类监督策略定案**：只标 sfx 时 bubble/panel/text 目标会被当背景导致其他类退化——从「四类全标 / 域内回放混合 / 冻结非 sfx 输出头」三选项按质量成本比定案并给理由；④imgsz=1024 生产口径兼容。
- [ ] AC2 路线 B/C 备胎登记（各一段静态评估，不深投入）：B=`yolo11-manga-seg` 独立 sfx 类；C=RT-DETR 系 Apache 基座（ogkalu 栈现成）。仅当 A 实证受阻才升级深评。
- [ ] AC3 训练环境就绪：隔离 venv `task-envs/M2-SFX-FINETUNE-gpu-py312`（沿 DOCTR-QUAL GPU venv 先例，RTX 5070 Ti 实测 torch+CUDA 可用）；**显存摸底**：yolo11s-seg imgsz1024 小 batch 冒烟实测峰值显存与 it/s，推算可行 batch 与预计训练时长。
- [ ] AC4 ONNX 导出+生产适配冒烟：任一路线模型（可用现役 yolo11s-seg.onnx 复刻）经「训练格式→ONNX 导出→`detection_sfx.py` 生产推理序列加载（imgsz metadata 解析/conf 门/类别映射）」全链冒烟 EXIT=0——证明未来训练产物能进生产通道。
- [ ] AC5 许可备案（非阻断）：登记 chiqui7/AGPL+Ultralytics 官方立场+用户 2026-10-04 接受声明；素材来源（HF webtoon/densho810/P&C）许可现状各一行备案。**不产出资格门**。
- [ ] AC6 零 src/生产面改动：全部在 experiments/task-envs/verification。

## 允许修改范围

`experiments/M2-SFX-FINETUNE-PREFLIGHT/**`、`verification/M2-SFX-FINETUNE-PREFLIGHT/**`、`doc/tasks/M2-SFX-FINETUNE-PREFLIGHT.md`、`doc/handoffs/M2-SFX-FINETUNE-PREFLIGHT-*.md`、新建 `task-envs/M2-SFX-FINETUNE-gpu-py312`（外部树）。

## 禁止范围

`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、生产权重/registry/env 默认值。

## 测试要求

| 场景/AC | 计划命令/步骤 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 .pt 可得性 | HF 模型页/仓库实证（网络） | 代理 127.0.0.1:7890 | NOT_RUN | 无 |
| AC3 显存摸底 | 冒烟训练 20 iter 记录 peak VRAM | GPU venv | NOT_RUN | 无 |
| AC4 导出链 | train→export onnx→生产序列加载推理 | 同上 | NOT_RUN | 无 |

## 依赖、风险与阻塞

depends_on 均已 done。风险：路线 A 若无 .pt 原生权重→升级 B/C 深评（停点=交编排裁决）；HF 下载走用户代理。GPU 独占注意与其它任务错峰。

## 交付与运行记录

- Handoff：尚无。Review：尚无。
