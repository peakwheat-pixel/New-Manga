# M2-SFX-FINETUNE-PREFLIGHT — 技术预检报告（T0，零 src）

- Owner：ZCode ｜ Reviewer：DeepSeek Harness（非作者）｜ 日期：2026-10-04
- base_commit：`4c12e8af` ｜ claim：`e2438ed3` ｜ delivery_head：见 Handoff
- 环境：venv `task-envs/M2-SFX-FINETUNE-gpu-py312`（外部树）＝ torch 2.11.0+cu128 / CUDA 12.8 / ultralytics 8.4.172 / RTX 5070 Ti 16GB（与 `M2-DOCTR-QUAL-gpu-py312` 同 torch 组合，`torch.cuda.is_available()=True` 实测）
- 裁决语境：DOMAIN-EXT-DIAG 二次裁决（2026-10-04）——许可降权备案不阻断，**最高原则=训练质量与效率**

## 0. 结论速览

| 项 | 结论 |
|---|---|
| 路线 A（chiqui7 续训） | **实证受阻**：HF 仓库只有 `yolo11s-seg.onnx`，**无原生 .pt**，ONNX 不可回训 |
| 路线定案建议 | **A′：Ultralytics 官方 `yolo11s-seg.pt` 基座 + BJ/KO 四类 GT 微调**（全链已实证） |
| 四类监督策略 | **选项 1 四类全标为主线**；选项 3 冻结非 sfx 头技术不可行（Ultralytics 无按类冻结机制） |
| 显存摸底 | imgsz=1024 AMP：b2=1.94GB / b4=4.03GB / b8=7.49GB；吞吐 36.5/57.3/67.0 img/s；**推荐 batch=8** |
| 导出链 | `.pt→ONNX(imgsz=1024)→生产 _build_engine→SfxDetectionProvider.detect` **EXIT=0**，类别面逐字一致，无类别差异 |
| AC5 | 备案完成（不产出资格门） |

## 1. AC1 路线 A 技术实证

### 1.1 ①原生 .pt 可得性：**否定**（核心结论）

- 命令：`curl -s -x http://127.0.0.1:7890 "https://huggingface.co/api/models/chiqui7/yolo11-manga-seg"`（2026-10-04 实测）
- 文件清单（API `siblings` 字段原文）：`.gitattributes`、`README.md`、`yolo11s-seg.onnx` —— **仅一个 ONNX 文件，无任何 .pt/训练 checkpoint**；`usedStorage: 41227478`（≈41MB，即生产 ONNX 本体）；`sha: 7f5f5c04…`（与生产 pin `SFX_HF_REVISION` 一致，`detection_sfx.py:108`）。
- 模型卡 README（`https://huggingface.co/chiqui7/yolo11-manga-seg/raw/main/README.md` 实测）：只有类别面/预处理说明，**无训练代码、无权重下载外链、无 GitHub 链接**。
- 佐证：chiqui7 的 ONNX 权重元数据 license 声明为 `AGPL-3.0 License (ultralytics.com/license)`（`verification/M2-SFX-DETECT-EVAL/license-evidence.md:23`）——产物形态是 Ultralytics 导出物，仓库内未发布训练侧工件。
- 结论：**Ultralytics 不支持从 ONNX 回训；路线 A 的「chiqui7 直接续训」形态在本仓库现状下不可行**。训练只能换基座（见 §2 路线定案）。

### 1.2 ②训练代码/配置完整性：通过（以官方栈为准）

Ultralytics 官方训练入口完整可用：本预检在冒烟中实测 `YOLO("yolo11s-seg.pt").train(data=…, imgsz=1024, …)` 换头微调全流程（nc=80→4 自动重初始化 head）、`export(format="onnx", imgsz=1024)` 导出——即「未来训练产物进生产通道」所需的全部训练侧构件已在 venv 内跑通，无缺失依赖。

### 1.3 ③四类监督策略定案：**选项 1 四类全标为主线**

| 选项 | 评估 | 结论 |
|---|---|---|
| 1. 四类全标 | 质量上限最高：bubble/panel/text 有真 GT 监督，sfx 不受类不平衡背景污染；共享 backbone 梯度更丰富 | **✅ 定案主线** |
| 2. 域内回放混合（只标 sfx + chiqui7 ONNX 伪标签回放其余三类） | 成本低，但伪标签质量受限于 chiqui7 现役召回——BJ 域 sfx 零响应（pre-NMS peak 0.0855，`detection_sfx.py:181`）意味着**最难学的难例恰恰被系统性欠采样**；伪标签噪声直接进入监督信号 | ⚠️ fallback（仅在标注预算只够单类时启用，且需先做伪标签质量抽检） |
| 3. 冻结非 sfx 输出头 | **技术不可行**：Ultralytics `freeze` 参数官方文档（docs.ultralytics.com/usage/cfg，2026-10-04 实测）原文 "Freezes the first N layers of the model, or specific layers **by index or module name**"——只支持按层/模块冻结；cls 分支是**共享 conv 输出 nc=4 通道**，不存在按类别子头；冻结整个 cls 头则 sfx 也无法学习 | ❌ 排除 |

选项 1 定案理由（质量×成本比）：
1. **边际成本低**：用户二次裁决已定 V1=BJ+KO 双域真实标注+合成数据辅助；真实标注按全类 GT 产出时（T1a manifest 支持多类），同一次标注行为的全类边际成本远低于单类独立 pass；程序合成数据（T1a PoC）天然产全类精确 GT，零额外成本。
2. **质量上限**：无伪标签噪声；sfx 难例（正是本训练要修的 BJ13 形态缺口）在选项 2 下没有监督来源。
3. **效率**：chiqui7 sfx 类现役召回仅 11/29（非自比口径 `sfx-detect-eval-report.md:14`）——回放信号欠采样难例；全类监督对 1024 训练的收敛也更稳。

### 1.4 ④imgsz=1024 生产口径兼容：通过

冒烟训练日志实测 `Using 80 train … at imgsz=1024`；导出物 ONNX metadata `imgsz="[1024, 1024]"` 被生产 `_parse_imgsz` 列表解析路径命中（`imgsz_source=metadata_parsed`，`detection_sfx.py:499-507` 的 DSH r1 R4 逻辑），与 chiqui7 生产语义逐字一致。

## 2. 路线定案建议（交编排裁决）

**建议 A′：Ultralytics 官方 `yolo11s-seg.pt`（AGPL，20,669,228 B，sha256 `1caa81c0…`）为基座 + BJ/KO 四类 GT + 合成数据微调。**

- A′ 与被阻断的原路线 A 同为 Ultralytics yolo11-seg 训练入口：架构/导出/类别面/letterbox 口径与生产适配面**完全同构**（本预检 AC4 已实证导出物进生产序列零改动通过——含 names 类断言与 imgsz 解析）。
- 基座差异如实登记：官方基座是 COCO 80 类预训练，**无 manga 域先验**（chiqui7 的域先验不可继承，因其无 .pt）；域知识只能靠 BJ/KO GT+合成数据补——这正是 T1a/T1b 数据线的职责。
- AC1-② 实证：换头 nc=4 微调入口、`args.yaml` 全参数面（对照 `anonimkaq4` 公开训练配置 `rect`/`imgsz=1024`/`batch=8` 形态）均在位。

## 3. AC2 路线 B/C 备胎登记（A 受阻 → 按合同升级为静态深评一段，未超预检边界）

**路线 B（替代 manga-seg .pt）**：HF 全站搜索（`manga-seg` / `manga segmentation` 两查询，2026-10-04 实测约 20+ 仓库）**不存在第二个带独立 sfx 类的模型**——与 M2-SFX-DETECT-EVAL「chiqui7 是唯一 surveyed candidate with a dedicated SFX class」结论一致（`detection_sfx.py:8-11`）。带原生 .pt 的近域候选：

| 模型 | 类别面 | 权重 | 许可 | 对 A′ 的可用性 |
|---|---|---|---|---|
| `anonimkaq4/manga-page-element-segmentation` | 0:frame / 1:speech_bubble / 2:character（无 sfx 无 text） | yolo11s/m-seg `.pt` @1024 + args.yaml（公开训练配置） | `other`（未审计） | 仅可作**替代初始化**（manga 域先验比 COCO 近）；类别面不齐，换头仍需四类 GT |
| `ShadowB/Manga109-panel-balloon-text-yolov26-segmentation` | panel/balloon/text（无 sfx） | yolo26s `best.pt`（MIT） | MIT | yolo26 架构≠yolo11，生产 ONNX 输出面不同构；无 sfx 类 |

结论：B 不改变 A′ 主线——任何 B 候选仍需自建 sfx 监督+换头，且引入未审计许可面；`anonimkaq4` yolo11s@1024 的 args.yaml 可作 A′ 超参参照。B 维持备胎登记。

**路线 C（RT-DETR 系 Apache 基座）**：ogkalu 栈=`ogkalu/comic-text-and-bubble-detector`，**safetensors RT-DETR-v2**，Apache-2.0，0=bubble/1=text_bubble/2=text_free **无 SFX 类**（`verification/M2-SFX-DETECT-EVAL/sfx-detect-eval-report.md:23`）。C 的实质成本：生产推理链（`_build_engine` 的 (1,40,N) YOLO-seg 输出面、post-sigmoid cls、类无关 NMS、letterbox 口径）对 RT-DETR **全部不同构**，导出/解析/仲裁面需整链重建（相当于第二个 `detection_sfx.py` + 新 eval 标定）。许可优势（Apache 无 AGPL 争议）在用户已明示接受 AGPL 的裁决下不再是决定项。**C 维持备胎，仅当 AGPL 变成硬阻断（裁决翻回）时深评**。

## 4. AC3 训练环境就绪 + 显存摸底

### 4.1 venv

- 新建：`G:/CODEX/New Manga.task-envs/M2-SFX-FINETUNE-gpu-py312`（Python 3.12.3，与 DOCTR-QUAL 同解释器）
- 组合：`torch 2.11.0+cu128`（`--index-url https://download.pytorch.org/whl/cu128`，与 DOCTR-QUAL 实测同版本）+ `torchvision` + `ultralytics 8.4.172` + `onnxruntime` + `onnx`
- CUDA 实测：`torch.cuda.is_available()=True`，`NVIDIA GeForce RTX 5070 Ti`，总显存 16,275.4 MiB

### 4.2 显存摸底（AMP，imgsz=1024，rect=False，mosaic=1.0，workers=2）

数据=coco8-seg（8 张）程序复制+标签 id%4 重映射为 chiqui7 四类名（冒烟只测显存/速度/链路，不产生精度结论）；每档实测 40 iter（**超出合同要求的 20 iter**，由复制倍数自然形成，只多不少）。

| batch | peak VRAM (reserved) | peak VRAM (allocated) | s/iter (中位) | 吞吐 | epoch 墙钟 |
|---|---|---|---|---|---|
| 2 | **1,940 MiB** | 1,722.6 MiB | 0.0548 | 36.5 img/s | 43.3s/40iter |
| 4 | **4,030 MiB** | 3,343.1 MiB | 0.0698 | 57.3 img/s | 25.9s/40iter |
| 8 | **7,488 MiB** | 6,039.4 MiB | 0.1194 | 67.0 img/s | 34.3s/40iter |

- 证据：`raw/vram_probe_summary.json`、`raw/vram_probe_console.log`（逐档 ultralytics 原生日志，含 `imgsz=1024`/`amp=True` 训练参数回显）、逐档 `raw/vram_probe_b{2,4,8}.json`
- **可行 batch 推算**：显存随 batch 线性（≈810 MiB/张）→ b12≈11GB、b16≈14.5GB（贴近 16GB 上限）。**推荐 V1 batch=8**（2 倍显存安全边际 + 最高实测吞吐 67 img/s）；b12 可作数据管线成熟后的提速选项。
- **训练时长方向性外推**（局限：冒烟图为 COCO 640px 小图、实例稀疏，真实 manga 页实例更密，按 2-3× 折减）：2,000 张/epoch @b8 ≈ 30-90s → 100 epoch ≈ **1-2.5 小时/百 epoch**量级。V1 训练在单卡 5070 Ti 上完全可行。

## 5. AC4 ONNX 导出 + 生产适配冒烟：EXIT=0（无类别差异）

链路：AC3 产物 `b2/weights/best.pt`（官方 COCO 基座换头 nc=4 微调）→ `YOLO.export(format="onnx", imgsz=1024)` → 生产 `_build_engine` → `SfxDetectionProvider.detect`。脚本：`experiments/M2-SFX-FINETUNE-PREFLIGHT/scripts/export_smoke.py`（import src 只读，**src 零改动**）。

| 步骤 | 实测结果 |
|---|---|
| 导出 | `best.onnx` 40,824,248 B（38.9MB，与生产 chiqui7 41MB 同量级），sha256 `b1bb877f…` |
| SHA 门（供应链） | 以导出物直接调 `_build_engine` → **`PROVIDER_FAILED` 正确命中**（门在位且对外来权重生效）；随后测试进程内将 `SFX_WEIGHTS_SHA256` 重指向导出物实际 sha（仅运行时模块常量，src 文件零改动） |
| 类面断言（R8） | 导出物 metadata `names="{0: 'bubble', 1: 'panel', 2: 'sfx', 3: 'text'}"` 与生产 `SFX_CLASS_MAP` **逐字一致，零漂移**（官方栈换头导出天然对齐生产四类契约） |
| imgsz 解析（DSH r1 R4） | metadata `"[1024, 1024]"` → `imgsz=1024, imgsz_source=metadata_parsed`（列表解析路径命中） |
| detect 全链 | 合成 manga 页（1024×1536）conf=0.5 与 conf=0.01 两档：`DetectionResult` 构造合法（provider_id/arch/imgsz_source/class_filter options 全对）；0 候选=1-epoch 半随机权重的合法 fail-closed 结果 |
| 输出张量 | `(1, 40, 21504)`＝生产假设 `(1,40,N)`（4 xywh+4 cls+32 mask），零差异 |
| 解析链非空路径（补充） | `scripts/nms_chain_probe.py` 以生产 `_sfx_boxes` + 注入 (1,40,4) 张量验证：conf 门→类无关 NMS（IoU 0.81 对被抑制）→ sfx 类过滤（bubble 0.95 丢弃）→ /scale 映射（2× 精确）→ EXIT=0 |

结论：**未来 A′ 训练产物可直接进入生产 `detection_sfx.py` 通道**（仅需按供应链流程更新 pin 的 sha256——生产既有门语义）。证据：`raw/export_smoke.json`、`raw/export_smoke_console.log`、`raw/nms_chain_probe.json`。

## 6. AC5 许可备案（非阻断，不产出资格门）

| 项 | 备案内容 |
|---|---|
| Ultralytics 官方立场 | ultralytics.com/license（2026-10-04 实测访问）：**"All Ultralytics YOLO trained models fall under the AGPL-3.0 License by default"**；fine-tune/衍生权重属 AGPL 覆盖，开源合规要求公开完整对应源（含模型权重）或购 Enterprise License |
| chiqui7 争议现状 | HF 标签 `license:mit`（API 实测）vs 权重元数据 `AGPL-3.0`（`license-evidence.md:23`）——争议已由用户裁决接受（`detection_sfx.py:3-6` 既有记录）；本预检新增事实：A′ 基座为 **Ultralytics 官方 yolo11s-seg.pt，AGPL-3.0 无标签争议**，衍生权重 AGPL 属性更明确 |
| 用户接受声明 | Task frontmatter `approval: user_ruling_2026-10-04_训练质量效率优先_许可降权备案`；DOMAIN-EXT-DIAG 二次裁决段（`doc/tasks/M2-SFX-DETECT-DOMAIN-EXT-DIAG.md:69-74`）：版权/许可风险用户明示接受，降级为登记备案项，不作为训练流程阻断门 |
| 素材来源① HF webtoon（KO 域） | 二次裁决「KO HF 素材恢复训练资格」——备案在案，训练资格已恢复 |
| 素材来源② densho810 | 追加利用报告已发（vol03 48/60/159 页，窗口 2026-11-02 前达标，`74fa71e9`）——权限交涉进行中，训练使用=备案项 |
| 素材来源③ P&C | 沿二次裁决同批备案（风险用户明示接受，登记不阻断） |

## 7. 风险与遗留

1. **基座域先验缺口（A′ 最大质量风险）**：官方 yolo11s-seg.pt 是 COCO 预训练，无 manga 域先验；V1 质量取决于 BJ/KO GT 量与合成数据覆盖——T1a/T1b 数据线的实际投入决定上限。缓解：`anonimkaq4` yolo11s@1024 .pt（manga 域近基座）可作初始化 A/B 实验项，但需先审计其 `other` 许可。
2. **冒烟数字外推局限**：显存/速度基于 COCO 小图（实例稀疏）；真实 manga 页（~1100-1600px、密集气泡/text）同 imgsz=1024 下 mask/assign 开销更高，训练时长外推按 2-3× 折减给出。
3. **路线定案为建议**：A′ 定案需编排会话确认（合同停点=交编排裁决）；若编排选择 B 初始化变体，需追加许可审计 slice。
4. **生产 SHA pin 更新流程**：未来训练产物替换生产 ONNX 时须同步更新 `SFX_WEIGHTS_SHA256` pin——属 src 变更，不在本 Task 范围（AC6 零 src 已守住），留待释放的下游 Task。
5. GPU 独占：显存摸底期间独占 GPU 约 2 分钟，与其它任务无冲突窗口（错峰要求满足）。

## 8. 证据索引

| 证据 | 路径 |
|---|---|
| 显存摸底摘要/逐档/控制台 | `verification/M2-SFX-FINETUNE-PREFLIGHT/raw/vram_probe_summary.json`、`vram_probe_b{2,4,8}.json`、`vram_probe_console.log` |
| 导出链冒烟 | `raw/export_smoke.json`、`raw/export_smoke_console.log` |
| 解析链注入 | `raw/nms_chain_probe.json` |
| 实验脚本（零 src） | `experiments/M2-SFX-FINETUNE-PREFLIGHT/scripts/{vram_probe,export_smoke,nms_chain_probe}.py` |
| 外部树（不进 git） | venv/datasets/weights/runs：`G:/CODEX/New Manga.task-envs/M2-SFX-FINETUNE-gpu-py312/`；基座 `weights/yolo11s-seg.pt`（sha256 `1caa81c0…`） |
