---
id: M2-SFX-PROD-1
title: "SFX 检测生产集成第一刀：chiqui7 独立 provider + region sfx 分派 + 权重随包（用户三裁决 2026-10-01：做/许可通过/路线 A）"
kind: feature
status: in_progress
approval: user_ruling_2026-10-01_sfx
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-SFX-DETECT-EVAL, M2-PROD-DETECT-2, M2-PROD-DETECT-3]
base_commit: 2f37b63a
branch: agent/zcode/M2-SFX-PROD-1
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-PROD-1-zcode
---

# M2-SFX-PROD-1：SFX 检测生产集成第一刀

## 来源与用户裁决（2026-10-01，逐字）

1. **要做**（SFX 检测可行性认定通过）。
2. **chiqui7 能用，不在乎**（AGPL 元数据争议 vs HF MIT tag——许可裁决接受 MIT 解释，争议登记不阻塞）。
3. **路线 A**（加装 chiqui7 独立 SFX 检测器，+41.2MB 权重，安装包体积可接受）。

## 目标

chiqui7/yolo11-manga-seg（ONNX）作为**独立 SFX 检测 provider**接入生产：检出 sfx 类候选 → region 标记 `region_type=sfx` → 既有 SfxPolicy 门（skip/manual/translate）自动生效。发布形态**开箱可用**（onnxruntime 轻量栈 + 41MB 权重随包——与 DETECT-1/2 的重 ML 栈路线不同，这是 SFX 集成的架构优势）。

## 已核实事实（释放侦察）

1. **SfxPolicy 默认=SKIP**（`src/domain/tasks/models.py:186` `sfx_policy: str = SfxPolicy.SKIP.value`）→ **误标 sfx = 对白被跳过不翻译（严重）** → 阈值冻结 **conf ≥ 0.50**（precision 优先；评估 @0.5 数据 11/29 支撑；阈值常数与 conf=0.5 的 manga provider 同模式，登记可调）。
2. **RegionType.SFX 已存在**（`src/domain/regions/entities.py:25`）+ `decide_sfx_translation` 判据（`src/application/translation/context/gate.py`）+ 渲染/规划两侧共用（TASK-035 落地）——管线消费面齐备。
3. **评估基线**（M2-SFX-DETECT-EVAL @`cf4e55ec`）：chiqui7 sfx 类 11/29@0.5（非自比 8/18）、ogkalu 硬盲区部分相交 6/7；推理口径=ONNX letterbox **左上贴图**+BILINEAR+class-agnostic NMS 0.7（与 Ultralytics 预训练管线偏离已披露）——**生产实现复刻评估口径**（数字可迁移，偏离登记）。
4. **权重**：`G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights/yolo11s-seg.onnx`（41,227,478 B，sha256 见 `external-evidence-inventory.json`）+ onnxruntime 1.30.0（CPU EP）已在 C4 GPU venv 验证。
5. **契约面**：`ports/detection/ports.py` 的 RegionCandidate 无类型槽——**契约零修订优先**：SFX 候选用匿名 label 前缀 `sfx-<n>` 标识，detect step 的 region 创建按前缀分派 `RegionType.SFX`；如侦察发现前缀方案不可行需契约改动，**即停下登记待裁决**。

## 设计决策（代理裁决，用户可撤销）

1. **独立并联 provider**（`SfxDetectionProvider`，新文件）：与 MangaDetectionProvider 并联装配，只产出 sfx 类候选；不改动两个既有 provider 行为。
2. **onnxruntime 轻量栈**：requirements 追加 `onnxruntime==1.30.0`（CPU wheels pin；GPU EP 后置）；懒加载同款纪律（无 onnxruntime 机器照常启动，typed 错误）。
3. **阈值冻结 conf≥0.50**（裁决见事实 1；`NEWMANGA_SFX_CONF_THRESHOLD` 可覆盖，默认 0.5）。
4. **权重随包**：build_sidecar.ps1 复制 yolo11s-seg.onnx 进 `core-sidecar/models/detector/`（sha256 校验），**onnxruntime 进闭包**（build venv 追加 onnxruntime；spec 允许 onnxruntime 收集）→ 发布形态 SFX 开箱可用（`NEWMANGA_SFX_DETECTION=on|off`，默认 **on**——用户裁决"要做"的直接落地；off=跳过 SFX provider 装配）。
5. **fail-closed 四纪律同款**：无权重/文件缺失=PROVIDER_NOT_CONFIGURED（typed，消息含指引）；hash 不符=PROVIDER_FAILED；匿名 label `sfx-<n>`；空页=零候选；无下载。
6. **SFX 候选与对白候选的合并语义**：SFX 候选**不进** MERGE_* 冻结合并（那是 word→block 对白口径）；作为独立候选与 manga 候选并列进入 region 创建，各自 region_type。

## Acceptance Criteria

- [ ] AC1（SFX provider）：`src/infrastructure/providers/detection_sfx.py`——onnxruntime 推理（复刻评估口径：letterbox 左上贴图/BILINEAR/NMS 0.7 class-agnostic/坐标回映，偏离披露注释）；sfx 类（cls=2）only；conf 阈值（env 可覆盖默认 0.5）；sha256 pin `yolo11s-seg.onnx`；fail-closed 四纪律；匿名 `sfx-<n>` label；懒加载。
- [ ] AC2（装配并联）：`core_assembly.py` 检测器装配段增加 SFX provider 装配（`NEWMANGA_SFX_DETECTION=on|off` 默认 on；权重默认 `<data root>/models/detector/yolo11s-seg.onnx`，env 覆盖，包内回退同 DETECT-2 查找语义——文件型）；mock 路径不受影响。
- [ ] AC3（region 分派接线）：detect step/region 创建路径按 label 前缀 `sfx-` 分派 `RegionType.SFX`（最小改动；侦察后若该路径涉及契约改动即停登记）；SFX 候选不进对白合并。
- [ ] AC4（requirements）：`onnxruntime==1.30.0` 追加（pin+注释）。
- [ ] AC5（测试）：SFX provider 单测（fail-closed 矩阵/sfx 类过滤/阈值/label 前缀/空页）+ 装配（on/off/包内回退）+ region 分派 + real 测试（真实 ONNX 权重，条件 skip）；既有测试不回退。
- [ ] AC6（envelope）：CPU ms/页实测（n≥3）入 `verification/M2-SFX-PROD-1/envelope.md`；体积对比（安装包 439.45→~490MB 预期，如实记录）。
- [ ] AC7（sidecar/发布形态）：build venv 追加 onnxruntime + spec 允许收集 + 权重随包（sha256 校验复制）+ GATE 25/25 + **发布形态探针**（frozen 进程 SFX 检测端到端——core.detect 是 manga 面不适用，独立探针验证装配级 frozen SFX 检测可用，同 DETECT-2 探针模式）。
- [ ] AC8（回归与纪律）：pytest 三套件基数（437+1skipped）不回退；cargo/vitest 留痕；`git diff --check` EXIT=0；禁改面（ports/**、detection_manga.py、detection_doctr.py、experiments/**、tauri.conf.json、run_clean_start_e2e.py）零触碰。

## 允许/禁止

允许：`src/infrastructure/providers/detection_sfx.py`（新增）、`src/bootstrap/core_assembly.py`（检测器装配段+region 分派所需最小面）、detect step/region 创建文件（分派接线，侦察定）、`requirements.txt`（追加 onnxruntime）、`packaging/m2ac5/{core_sidecar.spec,requirements-build.txt,build_sidecar.ps1}`（最小适配）、tests/**、Task/Handoff/verification/M2-SFX-PROD-1/**。
禁止：`src/ports/**` 契约、两个既有 provider 行为、MERGE_* 常数、`apps/**`、tauri.conf.json、run_clean_start_e2e.py、experiments/**（只读）、C4/C1/SFX-EVAL 产物改动、权重入库。

## 依赖、风险与阻塞

- 依赖：M2-SFX-DETECT-EVAL（候选与口径）、M2-PROD-DETECT-2/3（装配与打包链先例）。
- 风险：①**label 前缀分派若触契约**→停下登记（合法分支）；②onnxruntime 进闭包的 PyInstaller 兼容（DLL 面）→warn 断言模式兜底；③误检 sfx 走 skip 的产品风险→阈值 0.5 保守冻结+登记可调；④CPU 推理延迟未测→envelope 实测（YOLO11s 小模型预期 <100ms/页）。
- 阻塞：无。

## 遗留与边界

- 正式 SFX GT 重标注与质量验收（条件 1）→ 后续 slice（评估报告口径）。
- GPU EP（onnxruntime-gpu）→ 后置（CPU envelope 实测后定）。
- SFX OCR/翻译语义（SFX 翻译是艺术字处理，非对白 OCR 路径）→ 产品后续范围。
