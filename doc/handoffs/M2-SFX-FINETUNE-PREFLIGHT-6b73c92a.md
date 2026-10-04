---
task_id: M2-SFX-FINETUNE-PREFLIGHT
author: ZCode
recipient: Codex（编排会话代行，用户全权授权）
base_commit: 4c12e8af
delivery_head: 6b73c92a
status: delivered（待 DSH Review + 编排集成；status 保持 in_progress）
---

# Handoff：M2-SFX-FINETUNE-PREFLIGHT

## 交付结果

T0 技术预检全部完成（零 src）。提交链：claim `e2438ed3` → delivery `6b73c92a`（本 delivery_head）→ handoff（本文件）。

- **路线 A 实证（AC1，核心）**：`chiqui7/yolo11-manga-seg` HF 仓库 siblings 实测仅 `{.gitattributes, README.md, yolo11s-seg.onnx}`——**无原生 .pt**，模型卡无训练产物外链；ONNX 不可回训 → **「chiqui7 直接续训」形态实证受阻**。
- **路线定案建议（交编排裁决，合同停点）**：**A′＝Ultralytics 官方 `yolo11s-seg.pt`（AGPL，20.7MB，sha256 `1caa81c0…`）基座 + BJ/KO 四类 GT + 合成数据微调**——训练入口/导出/类别面与生产通道完全同构（AC4 已实证）；基座无 manga 域先验为如实登记的质量风险（域知识由数据线补）。
- **四类监督策略定案（AC1-③）**：**选项 1 四类全标为主线**（边际成本低：二次裁决已定全类真实标注+合成 exact GT；无伪标签噪声；chiqui7 现役 sfx 召回 11/29 意味着回放选项会系统性欠采样最难例）；选项 3「冻结非 sfx 输出头」**技术不可行**（Ultralytics `freeze` 官方文档实测：仅支持按层索引/模块名，cls 头为共享 conv 无按类子头）；选项 2 域内回放降为 fallback。
- **AC2 路线 B/C 备胎**：B=HF 全站无第二个带 sfx 类模型（chiqui7 唯一）；带 .pt 的近域候选 `anonimkaq4`（frame/speech_bubble/character，无 sfx，license `other` 未审计）/`ShadowB`（yolo26s MIT，无 sfx）仅可作替代初始化；C=ogkalu RT-DETR-v2 Apache 无 sfx 且生产链不同构，仅当 AGPL 翻回硬阻断时深评。
- 主报告：`verification/M2-SFX-FINETUNE-PREFLIGHT/preflight-report.md`。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 .pt 可得性 | `curl -s -x http://127.0.0.1:7890 https://huggingface.co/api/models/chiqui7/yolo11-manga-seg`（+ README raw 抓取） | 代理 127.0.0.1:7890 @6b73c92a | PASS（否定性：无 .pt） | 报告 §1.1（siblings 原文） |
| AC1-③ freeze 支持性 | curl `docs.ultralytics.com/usage/cfg` 抓取 freeze 定义 | 同上 | PASS（选项 3 不可行） | 报告 §1.3 引文 |
| AC3 venv+显存 | `scripts/vram_probe.py`（venv torch 2.11.0+cu128/ultralytics 8.4.172；coco8-seg 四类重映射；imgsz=1024 AMP；b2/b4/b8 各 **40 iter**，超出合同 20 iter） | RTX 5070 Ti 16GB @6b73c92a | PASS EXIT=0（1.94/4.03/7.49 GB；36.5/57.3/67.0 img/s；推荐 batch=8；训练时长方向性外推 1-2.5h/百 epoch @2k 张） | `raw/vram_probe_summary.json`、`raw/vram_probe_b{2,4,8}.json`、`raw/vram_probe_console.log` |
| AC4 导出链 | `scripts/export_smoke.py`：b2 best.pt→`export(format="onnx", imgsz=1024)`→生产 `_build_engine`（src 只读 import）→`SfxDetectionProvider.detect` 合成页两档 conf | 同上 @6b73c92a | PASS EXIT=0：SHA 门 `PROVIDER_FAILED` 正确命中→pin 进程内重指（src 零改动）→names `{0:bubble,1:panel,2:sfx,3:text}` **零漂移**→imgsz `[1024,1024]`→metadata_parsed→输出 `(1,40,21504)` 同构；**无类别差异**（官方栈换头导出天然对齐） | `raw/export_smoke.json`、`raw/export_smoke_console.log` |
| AC4 解析链非空路径 | `scripts/nms_chain_probe.py`：生产 `_sfx_boxes` + 注入 (1,40,4) 张量（NMS 抑制对/bubble 丢弃/sfx×2 保留/2× 映射） | 同上 @6b73c92a | PASS EXIT=0（逐坐标精确匹配） | `raw/nms_chain_probe.json` |
| AC5 备案 | ultralytics.com/license 实测访问 + 本地 `license-evidence.md` 既有证据复用 | — | PASS（备案表落报告 §6，零资格门） | 报告 §6 |
| AC6 零 src | `git diff --check`（EXIT=0）+ `git status` 改动面核验 | @6b73c92a | PASS（改动仅 doc/tasks、experiments/**、verification/**；venv/datasets/weights/runs 全在外部树） | 提交 `6b73c92a` 文件清单 |

未运行项：真实 manga 数据上的训练精度评估（超出 T0 预检边界，属 T1b 之后）；`anonimkaq4` license `other` 审计（仅登记为若采用其初始化的前置 slice）。冒烟精度数字一律不产（coco8 重映射数据，显存/速度/链路结论不含精度主张）。

## 接收方式

- 分支 `agent/zcode/M2-SFX-FINETUNE-PREFLIGHT`，worktree `G:/CODEX/New Manga.worktrees/M2-SFX-FINETUNE-PREFLIGHT-zcode`，base `4c12e8af`，head `6b73c92a`。
- 复现：`"G:/CODEX/New Manga.task-envs/M2-SFX-FINETUNE-gpu-py312/Scripts/python.exe" experiments/M2-SFX-FINETUNE-PREFLIGHT/scripts/<脚本>`（GPU 冒烟约 2 分钟 + 导出冒烟约 30 秒）；代理 127.0.0.1:7890 需在网。
- 接收者检查建议：①报告 §1.1 的 API 实证链（否定性结论的唯一事实源）；②export_smoke 的 SHA 门两步语义（先证门在位、再重指跑全链——src 零改动口径）；③四类策略定案理由 §1.3 与二次裁决的一致性。

## 下一任务建议（必填）

- Task ID / 标题：无新建 Task（T0 为预检 spike，交付=定案输入）；**等待编排对路线 A′ 的裁决**。
- 推荐 Agent / Reviewer：编排会话（裁决）→ DSH（本报告 Review）。
- 推荐原因与前置依赖：合同风险段明确「路线 A 若无 .pt → 停点=交编排裁决」；本预检触发该停点。A′ 裁决后 T1a（M2-SFX-DATA-INFRA，已 ready）即为下游第一环，其 manifest/合成 GT 设计与本报告四类策略（选项 1 全类）兼容。
- Recovery point：主仓库 branch `agent/zcode/M2-SFX-FINETUNE-PREFLIGHT` @`6b73c92a`（未集成的 author 持有分支）。
- 允许修改路径：无（待裁决后由编排释放）。
- 禁止范围与新增授权条件：A′ 采纳后训练实施需新 Task 授权（含生产 SHA pin 更新的 src 变更授权）；B 候选初始化变体需先释放 `anonimkaq4` 许可审计 slice。
- 交付物：本 Handoff + `preflight-report.md` + raw 证据 + 三脚本。
- 验证命令、环境与完成 Gate：Review 按 DSH 非-作者纪律；集成验证=三分支 replay（编排口径）。
- 可直接转发给 Agent 的指令：无需下一步操作（编排裁决前无可释放的下一 Task；T1a 已在主仓库 ready，无需本链转发指令）。

## 风险与遗留

1. **A′ 基座无 manga 域先验**（chiqui7 域知识因无 .pt 不可继承）——V1 质量上限取决于 T1a/T1b 数据投入；缓解项=`anonimkaq4` yolo11s@1024 初始化 A/B（前置：`other` 许可审计）。
2. **冒烟外推局限**：显存/it/s 基于 COCO 640px 小图；真实 manga 页同 imgsz 下 assign/mask 开销更高，训练时长外推已按 2-3× 折减（报告 §4.2）。
3. **生产 SHA pin 更新属 src 变更**：未来训练产物替换生产 ONNX 时须同步 pin——本 Task 零 src 未处理，需下游授权。
4. 路线定案为**建议**，编排裁决前不锁死；若裁决 B/C，本预检的显存/导出链结论仍适用（yolo11 架构面），C 需追加推理链重建评估。
5. GPU 独占窗口已用（约 2 分钟摸底），无遗留占用。

## 实验附录

- 数据来源与许可：coco8-seg（Ultralytics 官方资产，`https://ultralytics.com/assets/coco8-seg.zip`，8 张 COCO 图程序复制+标签 id%4 重映射为 chiqui7 四类名；仅测显存/速度/链路，零精度主张）。
- 模型/权重版本与 Hash：官方 `yolo11s-seg.pt` sha256 `1caa81c0195412efa411b632bcfb8c184939dddb6ae41f6a80c41b211ff257c3`（20,669,228 B，github.com/ultralytics/assets v8.3.0）；导出物 `best.onnx` sha256 `b1bb877fc2b331ddc843cf0783dbd9b325470eee44314846d78be70af8933d7e`（40,824,248 B）。
- Provider/Runtime：训练 torch 2.11.0+cu128 / ultralytics 8.4.172 / CUDA 12.8；推理复刻生产 `detection_sfx.py` CPU EP onnxruntime 序列（src 只读 import）。
- 硬件：NVIDIA GeForce RTX 5070 Ti 16,275.4 MiB。
- 网络策略：HF/GitHub/docs/ultralytics.com 全走用户代理 `http://127.0.0.1:7890`（curl -x / pip --proxy）。
- 参数：imgsz=1024、epochs=1、AMP=True、mosaic=1.0、rect=False、workers=2、seed=0、deterministic=True；b2/b4/b8 数据集=80/160/320 张（coco8 4 train 张 ×20/40/80）→ 各 40 iter。
- 运行次数：显存摸底 1 次/档（脚本重跑历史见 raw console，前两次失败为数据集下载缺失与 val 标签构建 bug，已修复，失败日志未保留——失败原因见提交记录与本附录）；导出冒烟 1 次。
- 失败样例：冒烟训练产物在合成页零检出（conf 0.01 亦零）——1-epoch 半随机 head 的预期 fail-closed 行为，已由 nms_chain_probe 注入补齐非空路径证据。
- 限制：本 Task 全部结论限于链路/资源可行性，不含任何检测质量结论。
- 建议：A′ 采纳后首训即用 batch=8 imgsz=1024 AMP；先 BJ 小域 100 epoch 看收敛再扩 KO+合成。
