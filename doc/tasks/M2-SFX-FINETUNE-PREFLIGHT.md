---
id: M2-SFX-FINETUNE-PREFLIGHT
title: "SFX fine-tune V1 技术预检：训练路线可行性实证+训练环境就绪+许可备案（T0；零 src）"
kind: spike
status: done
integration_commit: dedb97b2
owner_claim: 2026-10-04 09:09 +0800
approval: user_ruling_2026-10-04_训练质量效率优先_许可降权备案
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
depends_on: [M2-SFX-DETECT-DOMAIN-EXT-DIAG, M2-SFX-PROD-1, M2-REGION-OVERLAP-ARBITRATION]
base_commit: 4c12e8af
branch: agent/zcode/M2-SFX-FINETUNE-PREFLIGHT
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-FINETUNE-PREFLIGHT-zcode
integration_commit: null
delivery_head: 6b73c92a
---

# M2-SFX-FINETUNE-PREFLIGHT：SFX 微调 V1 技术预检

## 来源与目标

用户二次裁决（2026-10-04，见 DOMAIN-EXT-DIAG 二次裁决段）：启动 SFX 微调 V1 项目；许可降权备案不阻断；**最高原则=训练质量与效率**。本 Task 为训练线第一环：实证三条训练路线的技术可行性，定案 V1 路线，搭好训练环境——**避免直接开训后才发现权重不可得/显存不够/导出不兼容浪费算力**。

## Acceptance Criteria

- [x] AC1 路线 A 技术实证（chiqui7 续训，效率首选）：①HF `chiqui7/yolo11-manga-seg` 是否提供**原生 .pt 训练权重**（生产现用 41MB ONNX 不能直接微调——Ultralytics 对 ONNX 回训支持有限，必须查证）；②训练代码/配置完整性（Ultralytics yolo11 seg 训练入口）；③**四类监督策略定案**：只标 sfx 时 bubble/panel/text 目标会被当背景导致其他类退化——从「四类全标 / 域内回放混合 / 冻结非 sfx 输出头」三选项按质量成本比定案并给理由；④imgsz=1024 生产口径兼容。（**①否定：仓库仅 ONNX 无 .pt**——路线 A chiqui7 续训形态受阻；②通过；③定案选项 1 四类全标（选项 3 无法以可接受代价达成目标，排除——官方 freeze 配置面仅支持按层索引/模块名冻结、无按类通道冻结，类级屏蔽需自定义训练代码且共享 backbone/neck 仍漂移）；④通过）
- [x] AC2 路线 B/C 备胎登记（各一段静态评估，不深投入）：B=`yolo11-manga-seg` 独立 sfx 类；C=RT-DETR 系 Apache 基座（ogkalu 栈现成）。仅当 A 实证受阻才升级深评。（A 受阻已触发升级；B=无带 sfx 类的 .pt、anonimkaq4/ShadowB 候选登记；C=ogkalu RT-DETR-v2 Apache 无 sfx、生产链不同构，维持备胎）
- [x] AC3 训练环境就绪：隔离 venv `task-envs/M2-SFX-FINETUNE-gpu-py312`（沿 DOCTR-QUAL GPU venv 先例，RTX 5070 Ti 实测 torch+CUDA 可用）；**显存摸底**：yolo11s-seg imgsz1024 小 batch 冒烟实测峰值显存与 it/s，推算可行 batch 与预计训练时长。（torch 2.11.0+cu128；b2/b4/b8=1.94/4.03/7.49GB，推荐 batch=8）
- [x] AC4 ONNX 导出+生产适配冒烟：任一路线模型（可用现役 yolo11s-seg.onnx 复刻）经「训练格式→ONNX 导出→`detection_sfx.py` 生产推理序列加载（imgsz metadata 解析/conf 门/类别映射）」全链冒烟 EXIT=0——证明未来训练产物能进生产通道。（官方基座换头 nc=4 实训产物导出，类面与生产断言零漂移，SHA 门/全链/解析链注入 EXIT=0）
- [x] AC5 许可备案（非阻断）：登记 chiqui7/AGPL+Ultralytics 官方立场+用户 2026-10-04 接受声明；素材来源（HF webtoon/densho810/P&C）许可现状各一行备案。**不产出资格门**。（报告 §6 备案表）
- [x] AC6 零 src/生产面改动：全部在 experiments/task-envs/verification。（src/tests/contracts 零触碰；`git diff --check` 待 delivery commit 前复验）

## 允许修改范围

`experiments/M2-SFX-FINETUNE-PREFLIGHT/**`、`verification/M2-SFX-FINETUNE-PREFLIGHT/**`、`doc/tasks/M2-SFX-FINETUNE-PREFLIGHT.md`、`doc/handoffs/M2-SFX-FINETUNE-PREFLIGHT-*.md`、新建 `task-envs/M2-SFX-FINETUNE-gpu-py312`（外部树）。

## 禁止范围

`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、生产权重/registry/env 默认值。

## 测试要求

| 场景/AC | 计划命令/步骤 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 .pt 可得性 | `curl -s -x http://127.0.0.1:7890 https://huggingface.co/api/models/chiqui7/yolo11-manga-seg` | 代理 127.0.0.1:7890 | PASS（**否定性结论**：siblings 仅 `.gitattributes`/`README.md`/`yolo11s-seg.onnx`，无 .pt；README 无训练产物外链） | 报告 §1.1（API 响应原文摘录） |
| AC3 显存摸底 | `scripts/vram_probe.py`（coco8-seg 四类重映射，imgsz=1024 AMP，b2/b4/b8 各实测 40 iter≥20） | GPU venv | PASS（peak reserved 1940/4030/7488 MiB；36.5/57.3/67.0 img/s；推荐 batch=8） | `verification/M2-SFX-FINETUNE-PREFLIGHT/raw/vram_probe_summary.json` + console.log |
| AC4 导出链 | `scripts/export_smoke.py`（best.pt→export onnx imgsz=1024→生产 `_build_engine`→`SfxDetectionProvider.detect`）+ `scripts/nms_chain_probe.py`（解析链注入） | 同上 | PASS（EXIT=0：SHA 门命中→pin 重指→names 类面零漂移→imgsz metadata_parsed→(1,40,N) 同构；NMS/类过滤/映射注入精确匹配） | `raw/export_smoke.json`、`raw/nms_chain_probe.json`、`raw/export_smoke_console.log` |

## 依赖、风险与阻塞

depends_on 均已 done。风险：路线 A 若无 .pt 原生权重→升级 B/C 深评（停点=交编排裁决）；HF 下载走用户代理。GPU 独占注意与其它任务错峰。

## 编排裁决（2026-10-04，合同停点处置）

路线定案=**采纳 A′**（Ultralytics 官方 yolo11s-seg.pt 基座+BJ/KO 四类 GT+合成数据微调）。理由：路线 A 续训被五端点实证阻断（chiqui7 无 .pt，usedStorage 全 revision 排除）；B 实证无第二带 sfx 类模型；C 与 sfx 生产链不同构且无 sfx 面——A′ 为唯一可执行路径。采纳输入条件（按报告 §2/P3-8）：T1b 承诺最小标注量（页数下限）与召回基线回归口径；训练 dataset.yaml names 顺序逐字等于 SFX_CLASS_MAP（硬约束）。许可=用户 2026-10-04 降权备案已覆盖。T1b 标注轮待 schema（T1a 已冻结）+本裁决就绪，另行释放。

## 交付与运行记录

- 主报告：`verification/M2-SFX-FINETUNE-PREFLIGHT/preflight-report.md`（路线定案建议 A′、四类策略选项 1、显存实测、导出链证据、AC5 备案表）
- 路线定案建议：**A′＝Ultralytics 官方 yolo11s-seg.pt（AGPL）基座 + BJ/KO 四类 GT + 合成数据微调**；原路线 A（chiqui7 续训）实证受阻（无 .pt）；定案待编排裁决（合同停点）。
- Handoff：`doc/handoffs/M2-SFX-FINETUNE-PREFLIGHT-6b73c92a.md`。Review：DSH r1 已回，返修完成（见下）。

### DSH r1 返修记录（2026-10-04，owner=ZCode）

- 返修范围：`verification/M2-SFX-FINETUNE-PREFLIGHT/**`（报告修订 + 新增 raw 六件：HF API 主/revision/refs/tree/README 快照 + ultralytics docs freeze 原文快照，全部 `curl -x http://127.0.0.1:7890` 实测 HTTP 200）、Handoff（判语同步 + names 硬约束 + onnx 系版本附录 + 「DSH r1 修订段」处置对照表）、本文件、`vram_probe.py`（仅注释）。零 src/测试/STATUS/生产 pin 改动；未重跑 GPU 实验。
- 关键处置：P2-1 经集成方 `git show 74fa71e9` 验证为 DSH 误判（message 即 densho810 追报履行登记），保留原表述仅补溯源注；P2-2 选项 3 判语四处收敛；P2-3 usedStorage 全 revision 排除逻辑显式化（附 tree 端点 `lfs.oid`=生产 pin 的交叉证据）；P3-2 显存斜率改 925 MiB/张（1940→7488 over b2→b8）；P4-1/P4-2/P4-4/P4-6 按择要授权登记不修。逐条处置对照见 Handoff「DSH r1 修订段」。
