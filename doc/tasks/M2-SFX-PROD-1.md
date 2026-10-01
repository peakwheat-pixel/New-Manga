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
- [x] AC2（装配并联）：`core_assembly.py` 非 mock 分支 `MangaSfxParallelDetectionProvider` 并联（`NEWMANGA_SFX_DETECTION=on|off` 默认 on；off=byte-identical pre-SFX 面；mock 分支跳过 SFX=已登记决策）；权重经 `_resolve_detector_weights_path` 原样复用（文件型，`NEWMANGA_SFX_WEIGHTS` 覆盖 > data root > frozen 包内 > 默认）；`NEWMANGA_SFX_CONF_THRESHOLD` 覆盖（非法值装配 fail-fast，范围 (0,1] 由 provider 校验）。composite 语义：primary provenance 原样、sfx 候选追加于 primary reading_order 最大值之后、**typed sfx 失败安全降级**（options 记 `sfx_provider_status=degraded: <code>` + stderr 一行，manga 链继续；非 typed 异常传播）。
- [x] AC3（region 分派接线）：`handlers.handle_detect` 的 region_creator 增第 5 参 `provider_label`（契约零修订——ports/** 零触碰）；`core_assembly._detected_region_type`（模块级可测）按 `sfx-` 前缀分派 `RegionType.SFX`，其余 label 保持 SPEECH 默认；SFX 候选不进 MERGE_*（provider 不 import 合并常数，独立 block 级候选）。
- [x] AC4（requirements）：`onnxruntime==1.30.0`（pin+注释：评估 proven 构建、权重 sha256、PIL 经 torchvision 传递依赖登记）；主 venv 与 build venv 已安装。
- [x] AC5（测试）：`tests/providers/test_detection_sfx.py` 22 测试（fail-closed 矩阵/hash 门先于 runtime import 的 junk 文件证明/sfx 过滤+坐标回映/class-agnostic NMS 竞争证明/阈值语义/NaN+越界 typed/rgb32+rgb24/names drift（stub onnxruntime）/composite 三态）；`tests/core/test_sfx_assembly.py` 11 测试（真实装配三态矩阵/env fail-fast/override 传导/分派矩阵/SPEECH+SFX region 落库）；`test_detect_handler.py` label 传递+sfx 分派端到端；real ONNX 条件 skip 复现评估 payload（K07_R123 conf 0.9313 锚点）；既有测试不回退（DETECT-2/3 装配测试 helper 穿透 composite 取 primary——test-helper 修改，src 零变化）。
- [x] AC6（envelope）：CPU 实测 warm median **132–140 ms/页**（n=5/页，4 页含 3 评估帧+合成页；cold 129–344ms 含 session build+41MB sha256）；「<100ms」预期未达如实登记（交互可接受量级，GPU EP 后置）；体积：NSIS **479.90 MiB**（基线 438.86 MiB +43.03MB；集成重建绑定见 AC7 与 §集成修正）+ onnxruntime 闭包 35.8MB（压缩后 ~1.8MB）。见 `verification/M2-SFX-PROD-1/envelope.md`。
- [x] AC7（sidecar/发布形态）：build venv onnxruntime==1.30.0；spec `onnxruntime` 进 ML_HIDDENIMPORTS + `onnxruntime_pybind11_state.pyd` binaries 断言（对齐 `_assert_ml_closure` 模式，构建失败而非发布降级）；`Copy-SfxWeights` sha256 校验复制；PyInstaller 构建闭包断言 PASS（8584 pure modules 含 onnxruntime）；NSIS **503,238,932 B = 479.93 MiB sha256 `43da4060…f62e`（集成重建绑定，2026-10-01；Owner 交付构建 503,209,268 B = 479.90 MiB `1bf31cf8…2d2c`，Δ=+29,664 B 纯 py 层）**；**GATE 25/25 PASS**（集成重建后复跑，CS-E2 绑定新 sha256，runner 零改动，`verification/M2-AC5/raw` 与 gen/schemas、permissions 已还原；全量 stdout=`raw/cleanstart-runner-stdout.log`）；**frozen 探针 PASS**（集成复跑 4/4：SF-1 frozen 进程内真实 SFX 推理 conf 0.93128=dev 0.9313 与交付构建逐位一致、SF-1b 几何锚点 ≤0.05px（评估 payload 0.1px 记录精度内；实测最大 Δ=0.0224px）、SF-2 off=manga-only、SF-3 断权重 typed 降级 manga 存活）。
- [x] AC8（回归与纪律）：pytest 全量 **1563 passed + 1 skipped**（test_registry_readiness env-conditioned）**0 failed**；三套件——**基线口径（providers/core/m2_acceptance，DSH r1 C1 集成实测为准）479 passed + 1 skipped**（providers 317+1sk / core 127 / m2_acceptance 35；基线 437+1sk = 291+1sk / 111 / 35，delta 分解见 §集成修正）；Owner 交付时报告的「core/providers/pipeline 520+1sk」为**套件范围变更口径**（pipeline 替换 m2_acceptance，非基线可比，显式声明）；cargo test 44 passed + 1 ignored；vitest 5 files / 31 tests passed（cargo/vitest 集成期零触碰，引 Owner 交付数字）；`git diff --check 60f18d0d..HEAD` EXIT=0；禁改面（ports/**、detection_manga.py、detection_doctr.py、experiments/**、tauri.conf.json、run_clean_start_e2e.py、apps/**）专项 diff 空；权重零 tracked；MERGE_* 零触碰（`verification/M2-SFX-PROD-1/raw/ac8-discipline.txt` 留痕 + 集成修正补原始命令输出）。

## 允许/禁止

允许：`src/infrastructure/providers/detection_sfx.py`（新增）、`src/bootstrap/core_assembly.py`（检测器装配段+region 分派所需最小面）、detect step/region 创建文件（分派接线，侦察定）、`requirements.txt`（追加 onnxruntime）、`packaging/m2ac5/{core_sidecar.spec,requirements-build.txt,build_sidecar.ps1}`（最小适配）、tests/**、Task/Handoff/verification/M2-SFX-PROD-1/**。
禁止：`src/ports/**` 契约、两个既有 provider 行为、MERGE_* 常数、`apps/**`、tauri.conf.json、run_clean_start_e2e.py、experiments/**（只读）、C4/C1/SFX-EVAL 产物改动、权重入库。

## 依赖、风险与阻塞

- 依赖：M2-SFX-DETECT-EVAL（候选与口径）、M2-PROD-DETECT-2/3（装配与打包链先例）。
- 风险：①**label 前缀分派若触契约**→停下登记（合法分支）；②onnxruntime 进闭包的 PyInstaller 兼容（DLL 面）→warn 断言模式兜底；③误检 sfx 走 skip 的产品风险→阈值 0.5 保守冻结+登记可调；④CPU 推理延迟未测→envelope 实测（YOLO11s 小模型预期 <100ms/页）。
- 阻塞：无。

## 集成修正记录（DSH r1 `approved_with_conditions` 闭合，2026-10-01）

- Review：`G:/CODEX/New Manga.task-envs/M2-SFX-PROD-1/dsh-review-r1.md`（Findings R1-R14 + 裁量裁定建议 + 闭合清单 C1-C6）。Integrator=acting Codex 授权（集成执行者），merge 由编排会话执行。

### 三处裁量追认（acting Codex，全部采纳 DSH 建议）

1. **mock 跳过 SFX provider——追认采纳**（R10 校验外移随本修正落地；acceptance 面 SFX 覆盖缺口登记后续 slice「mock 面 SFX 覆盖探针」）。
2. **composite SFX typed 失败降级——追认采纳**（不违背 fail-closed：步骤必需承诺=speech region 落库仍兑现；precision-first 方向论证成立；唯一实质缺口=降级只进 options+stderr、发布版"记录但不呈现"，登记后续 slice「SFX 降级可见性暴露到 readiness/诊断」，非阻塞）。
3. **helper 穿透 `getattr(detector, "primary", detector)`——追认采纳，保留现写法**（断言对象=装配选出的 primary 本身，净覆盖未降；"顶层是 composite"由 `test_sfx_assembly.py` 单独钉住）。

### 逐条处置（R1-R14 / C1-C6）

| 项 | 处置 |
|---|---|
| R4[P3] | **src 修复（唯一触发重建项）**：`_parse_imgsz` 支持真实 metadata 形态（字符串化 JSON list `"[1024, 1024]"` 解析取主值；plain int 兼容）；不可解析→fallback 默认 1024 且 options 记录二态来源（`imgsz_source=metadata_parsed|fallback`）+ fallback 时记录原文（`imgsz_metadata_raw`）；`test_engine_imgsz_comes_from_metadata` 改用真实形态 `"[1024, 1024]"` 并断言 source，另加「不可解析→fallback+options 记录」测试；`test_parse_imgsz_matrix` 更新为二元组矩阵 |
| R9[P4] | **src 顺手**：`_resolve_detector_weights_path` 增可选 keyword `env_name`（默认 `NEWMANGA_DETECTOR_WEIGHTS` 不变），SFX 调用传 `NEWMANGA_SFX_WEIGHTS`——frozen 缺权重 stderr 指引不再指向错误 env；两条对称测试钉死两种文案 |
| R10[P4] | **src 顺手**：`NEWMANGA_SFX_DETECTION`/`NEWMANGA_SFX_CONF_THRESHOLD` 非法值校验外移到 mock 分支之外（mock 也 fail-fast），两条 mock-branch fail-fast 测试 |
| R6[P3] | doc 统一：Task AC2 与 handoff §2.3 的 `degraded:<code>`→`degraded: <code>`（对齐实现带空格；实现零改动） |
| R3[P3] | doc 三处（Task AC7 / handoff §3+§4 / envelope SF-1b）：`<0.02px`→`≤0.05px（评估 payload 0.1px 记录精度内；实测最大 Δ=0.0224px）` |
| R2[P3] | doc：envelope.md 体积基线更正为 **438.86 MiB（M2-PROD-DETECT-2 NSIS，460,181,312 B）**，注明 DETECT-3 基线 460,795,026 B（439.45 MiB）与基线选择理由；增量统一 MiB/MB 双标注（本轮 NSIS 重建后重算，见 envelope） |
| R12[P4] | doc：envelope.md GATE 分组改「CS-A acceptance 5 场景 6 条记录」（3+2+3+3+**6**+4+4=25） |
| C1/R1[P2] | **口径统一（集成实测执行计数为准）**：基线口径三套件（providers/core/m2_acceptance）= **479 passed + 1 skipped**（providers **317+1sk** / core **127** / m2_acceptance **35**）。delta 分解：基线 437+1sk（291+1sk/111/35）+ Owner 交付（providers +23；core +14——`test_sfx_assembly.py` 报告"11 测试"为函数计数，其中 `test_detected_region_type_matrix` parametrize 6-case 展开使执行计数=14）+ 集成修正新增 5（providers +3：imgsz fallback 记录/2 条 env-name 文案测试；core +2：mock fail-fast ×2）。**1 skip 归属**：`tests/providers/test_registry_readiness.py:237` env-conditioned（dev venv 有意携带 ML 栈，与基线一致）。Owner 的「pipeline 口径 520+1sk」（core/providers/pipeline，m2_acceptance 被 pipeline 替换）保留为显式套件变更声明，不与基线 437+1sk 对比。全量复跑 **1568 passed + 1 skipped 0 failed**（=Owner 1563 + 集成修正 5） |
| C5/R8[P3] | **STATUS 越界追认**：Owner 对 `doc/STATUS.md:14` Active Task 行的单行回填（in_review/delivery_head/handoff 链接）追认为合法——事实正确、低风险，与 `M2-SFX-DETECT-EVAL` R7 先例对齐（Owner 可回填状态行，不得写结论叙述）；本节即为该追认的集成登记 |
| C6/R7[P3] | **证据补强**：`raw/cleanstart-runner-stdout.log`（GATE runner 全量 stdout，DETECT-2 先例同款命名）+ `raw/ac8-discipline.txt` 补原始命令输出（禁改面专项 diff 的命令与逐行输出、权重 grep、MERGE_* grep） |
| R5[P3] | 不修，登记遗留（SFX 引擎失败路径无负缓存） |
| R11[P4] | 不修，登记遗留（hash 门先于 runtime import 的顺序断言依赖环境） |
| R13[P4] | 不修，登记遗留（闭包断言未钉 `capi/onnxruntime.dll`） |
| R14[P4] | 不修，登记遗留（装配→handler→closure 全链无单条端到端测试） |



## 遗留与边界

- 正式 SFX GT 重标注与质量验收（条件 1）→ 后续 slice（评估报告口径）。
- GPU EP（onnxruntime-gpu）→ 后置（CPU envelope 实测后定）。
- SFX OCR/翻译语义（SFX 翻译是艺术字处理，非对白 OCR 路径）→ 产品后续范围。
- **SFX 降级可见性暴露（DSH r1 裁量②条件，后续 slice，非阻塞）**：composite typed 降级目前只进 detect options + stderr 一行，发布版用户看不到"SFX 静默不工作"（如权重被 AV 隔离/删除）；改动点=`MangaSfxParallelDetectionProvider.detect` 单处（或 provider 侧一次性告警）+ readiness/诊断面板呈现。触发条件：任何 readiness/诊断面板 slice 启动时，或用户报告 SFX 无效时优先。
- **mock 面 SFX 覆盖探针（DSH r1 裁量①条件，后续 slice）**：mock acceptance 链无 SFX 端到端覆盖；在 acceptance 面补 mock sfx 探针（或在 readiness/provenance 面显式标注"mock 面不含 SFX"）。触发条件：任何需要 SFX 验收面覆盖的后续 slice。
- **R5（DSH r1）：SFX 引擎失败路径无负缓存**：hash 不符/session 失败时每页重复 sha256(41MB)+重建 session 尝试 + 每页一条 stderr（仍 fail-closed，正确性无碍）。触发条件：错误配置下长章节任务的日志噪音/性能投诉，或 composite 层降级警告限流 slice。
- **R11（DSH r1）：hash 门先于 runtime import 的证明依赖环境**：有 onnxruntime 的机器只证明"hash 先于 session build"；建议 monkeypatch `importlib.import_module` 断言未调用。触发条件：下次触碰 `detection_sfx.py` 加载顺序时一并收紧。
- **R13（DSH r1）：闭包断言未钉 `capi/onnxruntime.dll`**：仅钉 `onnxruntime_pybind11_state.pyd`；DLL 由 PyInstaller 内置 hook 带入，本次 GATE+SF-1 真实推理实证覆盖。触发条件：onnxruntime 升级或 PyInstaller hook 变更时补 pin。
- **R14（DSH r1）：装配 composite→真 handler→closure 全链无单条端到端测试**：现为两半各自覆盖；建议后续加"真装配 + mock sfx detector"端到端（可与 mock 覆盖探针合并）。触发条件：closure 签名/调用位置漂移导致的两半各自绿但链路红时。
