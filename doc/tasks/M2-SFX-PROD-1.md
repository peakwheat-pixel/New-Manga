---
id: M2-SFX-PROD-1
title: "SFX 检测生产集成第一刀：chiqui7 独立 provider + region sfx 分派 + 权重随包（用户三裁决 2026-10-01：做/许可通过/路线 A）"
kind: feature
status: in_review
approval: user_ruling_2026-10-01_sfx
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-SFX-DETECT-EVAL, M2-PROD-DETECT-2, M2-PROD-DETECT-3]
base_commit: 2f37b63a
branch: agent/zcode/M2-SFX-PROD-1
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-PROD-1-zcode
delivery_head: 038e8faf（owner 交付 tip；implement=6a346a15 → tests=bedbba69 → build/envelope=63a482fb → 回归修复+纪律留痕=038e8faf；claim=a6b72e8c）
tip_note: handoff=doc/handoffs/M2-SFX-PROD-1-038e8faf.md；envelope=verification/M2-SFX-PROD-1/envelope.md（warm 132-140ms/页）；GATE 25/25 证据=verification/M2-SFX-PROD-1/gate-cleanstart.json；frozen 探针 PASS=frozen-sfx-probe-results.json（SF-1 conf 0.93128 复现 dev 0.9313）
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

- [x] AC1（SFX provider）：`src/infrastructure/providers/detection_sfx.py`——onnxruntime 推理复刻评估口径（letterbox 左上贴图/BILINEAR/imgsz 读 metadata=1024/post-sigmoid 分数/class-agnostic NMS 0.7 于全类竞争后取 sfx 类/`/scale` 回映，偏离披露于模块 docstring：raw pixel 输入/页界 clip/NaN 拒绝/degenerate skip/conf=harvest 阈值语义）；sfx 类（cls=2）only；sha256 pin `d87389af…b646`（hash 门先于 onnxruntime import）；fail-closed 四纪律；匿名 `sfx-<n>` label；懒加载 onnxruntime/numpy/PIL；ONNX metadata names 断言（R8 纪律，drift=ProviderInvalidOutput）。
- [x] AC2（装配并联）：`core_assembly.py` 非 mock 分支 `MangaSfxParallelDetectionProvider` 并联（`NEWMANGA_SFX_DETECTION=on|off` 默认 on；off=byte-identical pre-SFX 面；mock 分支跳过 SFX=已登记决策）；权重经 `_resolve_detector_weights_path` 原样复用（文件型，`NEWMANGA_SFX_WEIGHTS` 覆盖 > data root > frozen 包内 > 默认）；`NEWMANGA_SFX_CONF_THRESHOLD` 覆盖（非法值装配 fail-fast，范围 (0,1] 由 provider 校验）。composite 语义：primary provenance 原样、sfx 候选追加于 primary reading_order 最大值之后、**typed sfx 失败安全降级**（options 记 `sfx_provider_status=degraded:<code>` + stderr 一行，manga 链继续；非 typed 异常传播）。
- [x] AC3（region 分派接线）：`handlers.handle_detect` 的 region_creator 增第 5 参 `provider_label`（契约零修订——ports/** 零触碰）；`core_assembly._detected_region_type`（模块级可测）按 `sfx-` 前缀分派 `RegionType.SFX`，其余 label 保持 SPEECH 默认；SFX 候选不进 MERGE_*（provider 不 import 合并常数，独立 block 级候选）。
- [x] AC4（requirements）：`onnxruntime==1.30.0`（pin+注释：评估 proven 构建、权重 sha256、PIL 经 torchvision 传递依赖登记）；主 venv 与 build venv 已安装。
- [x] AC5（测试）：`tests/providers/test_detection_sfx.py` 22 测试（fail-closed 矩阵/hash 门先于 runtime import 的 junk 文件证明/sfx 过滤+坐标回映/class-agnostic NMS 竞争证明/阈值语义/NaN+越界 typed/rgb32+rgb24/names drift（stub onnxruntime）/composite 三态）；`tests/core/test_sfx_assembly.py` 11 测试（真实装配三态矩阵/env fail-fast/override 传导/分派矩阵/SPEECH+SFX region 落库）；`test_detect_handler.py` label 传递+sfx 分派端到端；real ONNX 条件 skip 复现评估 payload（K07_R123 conf 0.9313 锚点）；既有测试不回退（DETECT-2/3 装配测试 helper 穿透 composite 取 primary——test-helper 修改，src 零变化）。
- [x] AC6（envelope）：CPU 实测 warm median **132–140 ms/页**（n=5/页，4 页含 3 评估帧+合成页；cold 129–344ms 含 session build+41MB sha256）；「<100ms」预期未达如实登记（交互可接受量级，GPU EP 后置）；体积：NSIS **479.90 MiB**（基线 438.86 MiB +43.03MB）+ onnxruntime 闭包 35.8MB（压缩后 ~1.8MB）。见 `verification/M2-SFX-PROD-1/envelope.md`。
- [x] AC7（sidecar/发布形态）：build venv onnxruntime==1.30.0；spec `onnxruntime` 进 ML_HIDDENIMPORTS + `onnxruntime_pybind11_state.pyd` binaries 断言（对齐 `_assert_ml_closure` 模式，构建失败而非发布降级）；`Copy-SfxWeights` sha256 校验复制；PyInstaller 构建闭包断言 PASS（8584 pure modules 含 onnxruntime）；NSIS 479.90 MiB sha256 `1bf31cf8…2d2c`；**GATE 25/25 PASS**（runner 零改动，`verification/M2-AC5/raw` 与 gen/schemas、permissions 已还原）；**frozen 探针 PASS**（SF-1 frozen 进程内真实 SFX 推理 conf 0.93128=dev 0.9313、SF-1b 几何锚点 <0.02px、SF-2 off=manga-only、SF-3 断权重 typed 降级 manga 存活）。
- [x] AC8（回归与纪律）：pytest 全量 **1563 passed + 1 skipped**（test_registry_readiness env-conditioned）**0 failed**；三套件（core/providers/pipeline）**520 passed + 1 skipped**；cargo test 44 passed + 1 ignored；vitest 5 files / 31 tests passed；`git diff --check 60f18d0d..HEAD` EXIT=0；禁改面（ports/**、detection_manga.py、detection_doctr.py、experiments/**、tauri.conf.json、run_clean_start_e2e.py）专项 diff 空；权重零 tracked；MERGE_* 零触碰（`verification/M2-SFX-PROD-1/raw/ac8-discipline.txt` 留痕）。

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
