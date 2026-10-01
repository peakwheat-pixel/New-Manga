# Handoff — M2-SFX-PROD-1（SFX 检测生产集成第一刀）

- Owner=ZCode · Reviewer=DeepSeek Harness（非作者）· Integrator=编排会话代行 Codex
- base=`2f37b63a`（Task 释放声明其 commit 基准；实施分支从 rebaseline 后的 `60f18d0d` 拉出——`60f18d0d` 即含 `2f37b63a` 的三裁决释放，两者同链，`git diff --check 60f18d0d..HEAD` 已按此口径留痕）· branch=`agent/zcode/M2-SFX-PROD-1`
- **delivery_head=`038e8faf`**；commit 链：`a6b72e8c`（claim）→ `6a346a15`（AC1-AC4 实现）→ `bedbba69`（AC5 测试）→ `63a482fb`（AC6/AC7 envelope+构建+GATE+探针）→ `038e8faf`（AC8 回归修复+纪律留痕）
- 状态：**in_review**（AC1-AC8 全部完成，待 DSH 非作者 review）

## 1. 实现范围（交付物）

| 文件 | 变更 |
|---|---|
| `src/infrastructure/providers/detection_sfx.py` | **新增**。`SfxDetectionProvider`（chiqui7 ONNX 独立 SFX provider）+ `MangaSfxParallelDetectionProvider`（装配并联 composite）+ 推理口径函数（`_letterbox`/`_sfx_boxes`/`_map_back`/`_nms`） |
| `src/bootstrap/core_assembly.py` | 装配段并联 + `_detected_region_type` 分派函数 + `_create_detected_region` 增 `provider_label` 参 |
| `src/infrastructure/providers/handlers.py` | `handle_detect` 的 region_creator 调用增第 5 参 `candidate.provider_label`（注释同步） |
| `requirements.txt` | 追加 `onnxruntime==1.30.0`（pin+注释） |
| `packaging/m2ac5/{core_sidecar.spec,build_sidecar.ps1,requirements-build.txt}` | onnxruntime 闭包断言 + `Copy-SfxWeights` + verbatim pin 行 |
| `tests/providers/test_detection_sfx.py` | **新增** 22 测试 |
| `tests/core/test_sfx_assembly.py` | **新增** 11 测试 |
| `tests/providers/{test_detect_handler,test_detector_weights_lookup,test_detection_manga,test_detector_assembly}.py` + `tests/pipeline/test_regionless_rebinding.py` + `tests/providers/t111_support.py` | 既有测试适配（见 §5） |
| `verification/M2-SFX-PROD-1/**` | envelope.md/results.json/envelope_run.py、frozen-sfx-probe.py/results.json、gate-cleanstart.json、gate-production-stdout.log、raw/ac8-discipline.txt |
| `doc/tasks/M2-SFX-PROD-1.md` | AC 回填 + frontmatter |

零触碰：`src/ports/**`（契约零修订，label 前缀方案成立）、`detection_manga.py`、`detection_doctr.py`（两既有 provider 行为零变化）、MERGE_* 常数、`experiments/**`、`apps/**`、`tauri.conf.json`、`run_clean_start_e2e.py`、权重（零 tracked）。

## 2. 六条代理裁决落地

1. **独立并联 provider**：`SfxDetectionProvider` 实现 `ports.detection` Protocol（`detect(request)->DetectionResult`），只产出 sfx 类候选。fail-closed 四纪律同款：缺权重文件=typed `PROVIDER_NOT_CONFIGURED`（消息含三种处置指引）；sha256 不符=typed `PROVIDER_FAILED`（**hash 门先于 onnxruntime import**——junk 文件测试证明）；匿名 `sfx-<n>` label（caller 分配 id）；空页零候选（不伪造）。懒加载 onnxruntime/numpy/PIL。**不进 MERGE_***：provider 不 import 任何合并常数，候选为独立 block 级（SFX 是整体艺术字）。
2. **onnxruntime==1.30.0**：requirements.txt + requirements-build.txt 双 pin（verbatim 模式）+ 主/build venv 安装（代理）。
3. **装配**：非 mock 分支 backend 选择后 `NEWMANGA_SFX_DETECTION=on|off`（默认 **on**=用户裁决落地；非法值 assembly raise ValueError，与 backend env 同语义）；权重查找**原样复用** `_resolve_detector_weights_path`（`NEWMANGA_SFX_WEIGHTS` override > data root 探测 > frozen 包内探测 > 默认——函数本身目录/文件混合语义天然支持文件名，零修改）。**mock 模式跳过真实 SFX provider**（登记决策：deterministic mock 已代表整个 detect 面，acceptance 种子 regions 流程零扰动）。composite 语义（登记决策）：primary provenance 原样（composite 是装配形态非第三 provider）；sfx 候选 reading_order 排在 primary 最大值之后；**typed sfx 失败安全降级**——`ProviderError` 族捕获，options 记 `sfx_provider_status=degraded: <CODE>` + stderr 一行，manga 链继续（方向性论证：误标 sfx=对白被跳过（重），SFX 不可用=回到已发布现状（轻）；非 typed 异常（编程错误）传播）。
4. **阈值 conf≥0.50 冻结**：`SFX_CONF_THRESHOLD=0.5` + `NEWMANGA_SFX_CONF_THRESHOLD` 覆盖（装配 fail-fast + provider `__post_init__` (0,1] 门）。语义登记：阈值即 harvest filter（评估脚本在 0.25 harvest、`conf_ge_primary` 标记；生产直接 0.5 进候选集——0.25-0.5 带的框不检出也不参与 NMS 竞争，属口径显式参数化，已在 docstring 披露）。
5. **AC3 接线**：`handle_detect` 传 `provider_label`（第 5 位置参）→ `_detected_region_type`（模块级纯函数）按 `sfx-` 前缀分派 `RegionType.SFX`，其余 label（manga-*/unmapped-*/空）保持 `RegionType.SPEECH` 历史默认。**未触契约**。
6. **权重随包**：`Copy-SfxWeights`（sha256 校验复制 `yolo11s-seg.onnx` → `<bundle>/models/detector/`，`-SkipWeights` 一并跳过、`-SfxWeightsSource` 可重定位）+ spec 闭包断言 → **发布形态 SFX 开箱可用**（frozen 探针证明）。

## 3. 推理口径复刻（评估 → 生产）

逐行对齐 `experiments/M2-SFX-DETECT/eval_sfx_mangabubble.py`（只读蓝本）：letterbox `min(size/w,size/h)` + PIL BILINEAR + 114 灰**左上贴图**（非居中）、imgsz 读 ONNX metadata（chiqui7=1024）、output0 `(1,40,N)` 后 sigmoid 分数（实证，不再激活）、conf filter → xywh→xyxy → **class-agnostic NMS IoU 0.7 于全类竞争后取 sfx 类**（过滤顺序 load-bearing：先滤 sfx 再 NMS 会改变幸存集）、`/scale` 回映。生产化偏离（docstring 披露）：输入为 raw pixel buffer（rgb24/rgb32，生产 `page_frame` 契约）、页界 clip + NaN typed 拒绝 + degenerate skip（manga R9 同款防御，坐标映射算术不变）。

**数字迁移验证**：real ONNX 测试与 frozen 探针都在 K07_R123 上复现评估 payload（conf 0.9313、box [201.1, 1134.0, 383.4, 1340.9]，frozen 级几何误差 ≤0.05px——评估 payload 0.1px 记录精度内，实测最大 Δ=0.0224px）——评估口径的数字结构性可迁移。

## 4. Envelope 与体积（AC6/AC7，证据=verification/M2-SFX-PROD-1/）

- **CPU ms/页**：warm median **132–140ms**（n=5/页；K07_R123 136.9 / K07_R121 135.3 / K08_R019 131.9 / 合成页 139.9）；cold 129–344ms（含 session build + 41MB sha256）。**释放时"YOLO11s 预期 <100ms/页"未达到**（高 30-40%）——如实登记：仍在交互可接受量级（detect 为任务级步骤），GPU EP 后置。
- **体积**：NSIS **503,209,268 B = 479.90 MiB**（sha256 `1bf31cf8…2d2c`，GATE CS-E2 绑定）vs DETECT-2 基线 438.86 MiB = **+43.03 MB**（权重 41.23MB + onnxruntime 压缩后 ~1.8MB；闭包目录 35.8MB）。Task 预估 ~490MB——NSIS LZMA 使实际比预估省 ~10MB。
- **GATE**：25/25 PASS（runner 零改动；运行后 `verification/M2-AC5/raw/**`、`gen/schemas/**`、`permissions/autogenerated/**` 已按还原纪律 `git checkout --` 还原；证据先复制到本 Task 目录）。
- **frozen 探针**（`frozen-sfx-probe.py`，DETECT-3 模式）：SF-1 frozen 进程内真实 SFX 推理（`sfx-1` conf 0.93128 + manga 候选并列）；SF-1b 几何锚点 ≤0.05px（评估 payload 0.1px 记录精度内；实测最大 Δ=0.0224px）；SF-2 `off`=零 sfx label 的 manga-only 面；SF-3 断权重 typed 降级、manga 存活、stderr 一行。

## 5. 既有测试适配（AC8 回归修复，无 src 变化）

装配默认 on 后，DETECT-2/3 的 4 个装配测试经 `_wired_detector` helper 直取 detector，撞上 composite 包装（`AttributeError: weights_dir` / `isinstance` 失败）。修复=三个 helper 增加 `getattr(detector, "primary", detector)` 穿透（backend 选择与权重查找语义在 primary 上，primary 行为未变）；另 3 个 region_creator 测试 lambda 增第 5 形参 `provider_label=""`。**全部为 test-helper 修改，`src/**` 零变化**——reviewer 请重点复核这一判断：helper 穿透是否弱化了原断言（结论：未弱化，断言对象从"装配产出的 detector"精确化为"装配选出的 primary"，composite 形态由 `tests/core/test_sfx_assembly.py` 单独钉住）。

## 6. 测试与纪律数字（AC8）

- pytest 全量：**1563 passed + 1 skipped 0 failed**（`test_registry_readiness` env-conditioned skip 与基线一致）；三套件（core/providers/pipeline）**520 passed + 1 skipped**。
  - **集成修正注记（DSH r1 C1/R1，2026-10-01）**：上行为 Owner 交付口径，其中 pipeline 口径为**套件范围变更**（pipeline 替换 m2_acceptance，不与基线 437+1sk 对比，显式声明）。**基线口径三套件（providers/core/m2_acceptance）集成实测 = 479 passed + 1 skipped**（providers 317+1sk / core 127 / m2_acceptance 35；delta 分解与 1 skip 归属见 Task §集成修正记录）；全量集成复跑 1568+1sk 0 failed（Owner 1563 + 集成修正新增 5 条测试）。
- cargo test：44 passed + 1 ignored（exit 0）；vitest：5 files / 31 tests passed。
- `git diff --check 60f18d0d..HEAD` EXIT=0；禁改面专项 diff 空；权重零 tracked；MERGE_* 零触碰（`raw/ac8-discipline.txt`）。

## 7. Known limitations（review 与后续范围）

1. **SFX 翻译语义=后续产品范围**：本刀只把 region 标为 `region_type=sfx` 使 SfxPolicy 门（默认 SKIP）生效；SFX 的 OCR/翻译是艺术字处理路径，非对白 OCR——未实现、未规划在本刀。
2. **SFX 候选与 manga 候选的空间重叠不去重**：同一 SFX 可能同时被 ogkalu 检出为 text region（现状行为，不因本刀恶化）+ chiqui7 标为 sfx region。评估报告 §4.4 条件 5（合并去重规则）= 后续 slice；当前两 region 并存，行为保守（skip 门只作用于 sfx region）。
3. **composite 降级语义**为 Owner 裁量（§2.3）：SFX typed 失败不拖垮 detect step。若 reviewer/integrator 认为应 fail-closed at step（同 manga 语义），改动点是 `MangaSfxParallelDetectionProvider.detect` 单处。
4. **envelope 未达 <100ms 预期**（§4）；单机实测，跨硬件未采样；GPU EP 后置。
5. **阈值 0.5 的 harvest 语义差异**（§2.4）：0.25–0.5 带不参与 NMS 竞争；若后续要求评估口径的 0.25 harvest 竞争集，需独立 harvest/emit 双阈值（未做，登记）。
6. **类内混淆残余**（评估 §3.3）：chiqui7 把部分 SFX 判为 text 类——本刀不解决（生产里它们继续被 ogkalu/chiqui7-text 路径处理）；正式 SFX GT 重标注与质量验收=后续 slice。
7. **PIL 未显式 pin**：letterbox 依赖 torchvision 的硬传递依赖（requirements.txt 注释登记）；torchvision 未来解除依赖则 fail typed `PROVIDER_DEPENDENCY_MISSING`。
8. mock 模式无 SFX（登记决策，§2.3）——acceptance 流程若未来需要 SFX 面，须另行设计 mock sfx provider。

## 8. 给 Reviewer（DSH）的复核锚点

- 口径复刻：`detection_sfx.py` docstring + `_letterbox`/`_sfx_boxes` vs `experiments/M2-SFX-DETECT/eval_sfx_mangabubble.py`（NMS 全类竞争顺序、左上贴图、/scale）。
- 契约零修订：`git diff 60f18d0d..HEAD -- src/ports/` 为空；label 前缀分派链 `handle_detect` → `_detected_region_type`。
- composite 降级语义与 mock 跳过：§2.3 两处 Owner 裁量，需裁决。
- frozen 证据：`frozen-sfx-probe-results.json`（SF-1 conf 0.93128 vs dev 0.9313）。
- 测试适配的"helper 穿透不弱化断言"判断（§5）。
