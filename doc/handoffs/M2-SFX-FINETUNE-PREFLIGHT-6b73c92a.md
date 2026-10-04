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
- **四类监督策略定案（AC1-③）**：**选项 1 四类全标为主线**（边际成本低：二次裁决已定全类真实标注+合成 exact GT；无伪标签噪声；chiqui7 现役 sfx 召回 11/29 意味着回放选项会系统性欠采样最难例）；选项 3「冻结非 sfx 输出头」无法以可接受代价达成目标，排除（官方 freeze 配置面仅支持按层索引/模块名冻结、无按类通道冻结，类级屏蔽需自定义训练代码且共享 backbone/neck 仍漂移——收敛判语见报告 §1.3）；选项 2 域内回放降为 fallback。
- **硬约束（DSH r1 登记，交下游训练 Task）**：训练 `dataset.yaml` 的 `names` 顺序必须逐字等于生产 `SFX_CLASS_MAP`（`0:bubble / 1:panel / 2:sfx / 3:text`）——类 id 顺序漂移即生产类面污染；AC4 的 names 逐字零漂移断言即对该契约守门（报告 §2 同步登记）。
- **AC2 路线 B/C 备胎**：B=HF 全站无第二个带 sfx 类模型（chiqui7 唯一；口径限定：沿用 M2-SFX-DETECT-EVAL 既有 surveyed 口径+本次两查询复核，非全站穷举证明）；带 .pt 的近域候选 `anonimkaq4`（frame/speech_bubble/character，无 sfx，license `other` 未审计）/`ShadowB`（yolo26s MIT，无 sfx）仅可作替代初始化；C=ogkalu RT-DETR-v2 Apache 无 sfx 且生产链不同构，仅当 AGPL 翻回硬阻断时深评。
- 主报告：`verification/M2-SFX-FINETUNE-PREFLIGHT/preflight-report.md`。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 .pt 可得性 | `curl -s -x http://127.0.0.1:7890 https://huggingface.co/api/models/chiqui7/yolo11-manga-seg`（DSH r1 补档：API/revision/main/refs/tree?recursive/README raw 快照五项，均 HTTP 200） | 代理 127.0.0.1:7890 @6b73c92a | PASS（否定性：无 .pt；usedStorage=41,227,478 B 逐字节=onnx 单文件 size 为全 revision 排除旁证；refs 仅 main 无 tag；tree `lfs.oid`=生产 pin） | 报告 §1.1 + `raw/hf_api_models_chiqui7*.json`、`raw/hf_tree_main_recursive.json`、`raw/hf_readme_main_snapshot.md` |
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
- Provider/Runtime：训练 torch 2.11.0+cu128 / ultralytics 8.4.172 / CUDA 12.8；导出面 onnx 1.23.1（opset 18）/ onnxslim 0.1.97 / onnxruntime 1.30.0（venv `pip list` 实测）。onnxslim 为导出时 Ultralytics **AutoUpdate 自动安装**（`raw/export_smoke_console.log:7-19`：`onnxslim>=0.1.82 not found, attempting AutoUpdate` → `AutoUpdate success 1.8s` → `+ onnxslim==0.1.97`）。**导出产物经 onnxslim slim（log:23 `slimming with onnxslim 0.1.97`），影响 best.onnx 的 sha256（`b1bb877f…`）——重跑导出需同版本 onnx/onnxslim 才能复现该 sha**。推理复刻生产 `detection_sfx.py` CPU EP onnxruntime 序列（src 只读 import）。
- 硬件：NVIDIA GeForce RTX 5070 Ti 16,275.4 MiB。
- 网络策略：HF/GitHub/docs/ultralytics.com 全走用户代理 `http://127.0.0.1:7890`（curl -x / pip --proxy）。
- 参数：imgsz=1024、epochs=1、AMP=True、mosaic=1.0、rect=False、workers=2、seed=0、deterministic=True；b2/b4/b8 数据集=80/160/320 张（coco8 4 train 张 ×20/40/80）→ 各 40 iter。
- 运行次数：显存摸底 1 次/档（脚本重跑历史见 raw console，前两次失败为数据集下载缺失与 val 标签构建 bug，已修复，失败日志未保留——失败原因见提交记录与本附录）；导出冒烟 1 次。
- 失败样例：冒烟训练产物在合成页零检出（conf 0.01 亦零）——1-epoch 半随机 head 的预期 fail-closed 行为，已由 nms_chain_probe 注入补齐非空路径证据。
- 限制：本 Task 全部结论限于链路/资源可行性，不含任何检测质量结论。
- 建议：A′ 采纳后首训即用 batch=8 imgsz=1024 AMP；先 BJ 小域 100 epoch 看收敛再扩 KO+合成。

## DSH r1 修订段（2026-10-04，返修 owner=ZCode）

DSH r1 review 意见逐条处置如下。修订范围：`verification/M2-SFX-FINETUNE-PREFLIGHT/**`（报告+新增 raw 六件）、本 Handoff、Task 文件、`vram_probe.py`（仅注释）；零 src/测试/STATUS/生产 pin 改动；未重跑任何 GPU 实验（全部修订基于既有 raw 证据与新增网络抓取）。

| 项 | 处置 |
|---|---|
| P2-1 densho810/`74fa71e9` | **按集成方验证覆核处置：DSH r1 该条为误判**。集成方已运行 `git show 74fa71e9` 验证：该 commit message 正是「doc(USER-TODO): densho810 追加利用报告已代发履行（用户指令授权）— vol03 48/60/159 页追报经 peak.wheat@gmail.com 发送至 info@densho810.com，已发邮件核验一致；报告窗口 2026-11-02 前达标；STATUS 用户待办③ 闭环」（返修 owner 在本 worktree 本地 `git show 74fa71e9 --no-patch` 复核逐字一致）；`74fa71e9` 同时被后续 Task 用作 base_commit 属巧合复用。处置=保留报告 §6「追加利用报告已发」表述，仅补可溯源性注（履行登记 commit + 集成方验证 + DSH r1 沙箱无 git 误判），未改为用户待办。 |
| P2-2 选项 3 判语 | 已按收敛判语改写（「无法以可接受代价达成目标，故排除」+freeze 配置面/自定义代码/共享 backbone 漂移三层理由）：报告 §0、§1.3、Task AC1、本 Handoff 四处同步；docs freeze 定义原文快照落 `raw/ultralytics_docs_cfg_freeze_snapshot.html`。 |
| P2-3 HF 原始响应补档 | 已用 `curl -x http://127.0.0.1:7890` 补抓 5 项落 `raw/`（主 API / revision/main / refs / tree?recursive=true / README raw 快照，2026-10-04 均实测 HTTP 200）；报告 §1.1 显式写出 usedStorage 排除逻辑（41,227,478 B 逐字节=onnx 单文件 size，若存在 20.7MB .pt 该数字至少 ≈62MB）；§3 加 AC2 口径限定「沿用 M2-SFX-DETECT-EVAL 既有 surveyed 口径+本次两查询复核，非全站穷举证明」。附产交叉证据：tree 端点 `lfs.oid` 与生产 SHA pin 逐字一致。 |
| P3-2 显存斜率 | 报告 §4.2「≈810 MiB/张」改「约 925 MiB/张（reserved 线性拟合 1940→7488 MiB over b2→b8）」；b12/b16 外推按新斜率同步重算（≈11.2/14.9GB）。 |
| P3-3 墙钟口径 | 报告 §4.2 表头「epoch 墙钟」改「整段 train() 墙钟（含初始化+final val）」，峰值 VRAM 两列标注含 final val，表下加口径注（raw console 各档 `Validating …best.pt` 段为证）。 |
| P3-5 vram_probe.py 注释 | docstring 与 `BATCH_REPEAT` 常量注释改为与实测一致（复制倍数 20x/40x/80x、train 图 80/160/320 张、每档 40 iter），补 wall/峰值覆盖 final val 口径注；仅注释改动，代码逻辑零变更，`py_compile` 通过。 |
| P3-6 names 硬约束 | 报告 §2 + 本 Handoff 交付结果段登记：训练 `dataset.yaml` 的 `names` 顺序必须逐字等于 `SFX_CLASS_MAP`（bubble/panel/sfx/text）。 |
| P3-7 onnx2torch | 报告 §1.1 补不采纳理由一行：权重/优化器状态缺失、算子兼容风险、无原训练配置。 |
| P3-8 A′ 输入条件 | 报告 §2 补采纳输入条件：T1b 承诺最小标注量（页数下限）与召回基线回归口径。 |
| P3-9 onnx 系版本 | 本 Handoff 实验附录补精确版本（onnx 1.23.1 opset 18 / onnxslim 0.1.97 / onnxruntime 1.30.0）、AutoUpdate 事件（console log:7-19）与「导出产物经 onnxslim slim 影响 sha256，重跑需同版本」口径。 |
| P4-3 pin 生命周期 | 报告 §5 SHA 门行明示：进程内常量重指未写回 src/env/registry、进程结束即失效、生产 pin 仍为 `d87389af4350954143a216bcfe40fd2ad93312cb136534e6073c9c740d98b646`。 |
| P4-5 mAP 免责 | 报告 §8 证据索引加注：raw 日志中 mAP 数字为合成/重映射冒烟副产物，不构成精度证据。 |
| P4-1 / P4-2 / P4-4 / P4-6 | **按 DSH r1 择要授权登记不修**：本次返修清单未要求文本改动，r1 意见原文留档于 review 记录，未在本文件复述（不虚构未核对的意见内容）。 |
