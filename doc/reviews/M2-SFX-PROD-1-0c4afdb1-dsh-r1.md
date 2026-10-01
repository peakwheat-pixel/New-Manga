## Verdict
**approved_with_conditions**

无 P0/P1，无功能性缺陷，无需 Owner 返修代码。代码面（推理口径复刻、契约零修订、fail-closed 四纪律、装配/分派接线、闭包与发布形态）与证据面（GATE 25/25、frozen 探针、real ONNX 锚点）主线成立；条件集中在**账目口径、几处"声称强于观测"的表述、以及三处 Owner 裁量需集成方追认**，均可由集成方在集成 commit 中闭合或登记，不需要回到 Owner 返修。

---

## 逐项核对表

| 项 | 结论 | 依据（文件:行） |
|---|---|---|
| **A 口径复刻保真度** | **通过（附 R4）**：letterbox（`min` 缩放/`int(round)`/PIL BILINEAR/114 灰/**左上 paste (0,0)**/`/255`→float32/CHW/`ascontiguousarray`）、NMS（`argsort` 降序贪心/`_iou` 无 clamp）、filter 顺序（conf→xywh→xyxy→**全类 NMS→再取 sfx**）、post-sigmoid、`/scale` 回映逐行一致；偏离仅 docstring 已披露的 4 项（raw buffer/页界 clip/NaN typed/degenerate skip）。pin 三处逐字一致 | 蓝本 `experiments/M2-SFX-DETECT/eval_sfx_mangabubble.py:64-131` ↔ `src/infrastructure/providers/detection_sfx.py:353-473`；pin=`detection_sfx.py:109-111`=`build_sidecar.ps1:193`=`requirements.txt:326`=`verification/M2-SFX-DETECT-EVAL/external-evidence-inventory.json:355-356`（41,227,478B）；hash 门顺序 `detection_sfx.py:263-281` |
| **B 契约零修订与接线** | **通过**：diff 26 文件中 `src/ports/**` 零出现；`region_creator` 唯一装配点（`build_production_handlers` 仅 `core_assembly.py:956` 一处调用）；第 5 参有默认 `""` 向后兼容；分派为 `sfx-` 前缀精确匹配，`manga-<n>`/`doctr-<n>`/`unmapped-<n>`/`""` 全部落 SPEECH 无碰撞；`detection_sfx.py` 不 import 任何 `MERGE_*` | `handlers.py:174,287-295`；`core_assembly.py:658-673,929-953`；`tests/core/test_sfx_assembly.py:132-144`；`create_region` 默认 `RegionType.SPEECH`=`application/editing/service.py:247-255` |
| **C 两处 Owner 裁量** | **方向均成立，建议采纳**：①mock 跳过=务实（composite 包裹 mock 会让 acceptance 每页吃一条降级警告、扰动确定性），但存在验收面覆盖缺口（mock 链无 SFX 端到端）；②composite typed 降级**不违背** fail-closed（步骤的唯一必需承诺=speech region 落库仍兑现；主检测器缺权重仍 typed 失败不变）；"误标 sfx（SfxPolicy 默认 SKIP→对白不译）重于 SFX 不可用（回到 pre-SFX 现状）"成立。**缺口**：降级只进 options+stderr，步骤仍 COMPLETED → 发布版"记录但不呈现" | `core_assembly.py:869-871,884-901`；`detection_sfx.py:504-543`；`RegionType.SFX`=`domain/regions/entities.py:20-25`；`sfx_policy` 默认 SKIP=`domain/tasks/models.py:186`、`editing/service.py:254` |
| **D 阈值语义** | **通过（建议补一句文档）**：0.5 冻结、env 覆盖、非法值装配 fail-fast（`"abc"`→`float()` ValueError；`"1.5"`/`"0"`→provider `__post_init__` (0,1] ValueError）均成立；0.25–0.5 harvest 差异已披露——且可证明**不影响数字可迁移**：NMS 按 conf 降序贪心，一个框是否幸存只取决于排名更前的框，故去掉 <阈值框不改变 ≥阈值幸存集（建议把这条性质写进 docstring，避免读者误以为口径有实质偏离） | `detection_sfx.py:117,151-158,397-410`；`core_assembly.py:885-890`；`tests/core/test_sfx_assembly.py:105-124` |
| **E 测试质量与 helper 穿透** | **通过（附 R1）**：22 collected（`test_detection_sfx.py`，含 3 个 `REAL_SKIP` 条件 real）+11（`test_sfx_assembly.py`）+1 handler 端到端；real 测试锚点 = 评估 payload 逐字（conf 0.9313 / box [201.1,1134.0,383.4,1340.9]）。**helper 穿透不弱化断言**：穿透对象就是装配选出的 `primary` 本身（composite 不改 primary 属性），原断言字段（`isinstance`/`provider_id`/`weights_dir`/`weights_path`）语义等价；"顶层是 composite"由 `test_sfx_assembly.py:74-96` 单独钉住。**账目问题见 R1** | `tests/providers/test_detection_sfx.py:516-570`；`test_detector_assembly.py:62-68`；`test_detector_weights_lookup.py:67-72`；`test_detection_manga.py:452-456`；`onnx-sfx-frames.json:1183-1211` |
| **F GATE 与探针** | **通过（附 R2/R3/R12）**：`gate-cleanstart.json` 25 条场景全部 `PASS`、`verdict=PASS`，CS-E2 绑定 `1bf31cf8…2d2c`；runner 零改动（diff 无 `run_clean_start_e2e.py`）；探针 SF-1（conf 0.93128→round 后=0.9313）/SF-2（off=零 sfx label）/SF-3（断权重+stderr 一行+manga 存活）与 `frozen-sfx-probe-results.json` 对齐；闭包断言 `onnxruntime` hiddenimport + pyd binaries | `verification/M2-SFX-PROD-1/gate-cleanstart.json:12,35-36,273-274`；`frozen-sfx-probe-results.json:SF-1..SF-3`；`core_sidecar.spec:85,120-121,168-188` |
| **G 范围纪律** | **通过（附 R8）**：26 文件全部落在 Task 允许路径（`detection_sfx.py` 新增 / `core_assembly.py` / `handlers.py` / `requirements.txt` / `packaging/m2ac5/**` / `tests/**` / Task+Handoff+`verification/M2-SFX-PROD-1/**`）；禁改面（`ports/**`、`detection_manga.py`、`detection_doctr.py`、`experiments/**`、`tauri.conf.json`、`run_clean_start_e2e.py`、`apps/**`）零出现；权重零 tracked（diff 无二进制）；AC8 留痕存在但强度偏弱（R7） | diff 26 条 `diff --git`（`review-input.diff:1,14,94,139,232,297,312,332,450,1025,1052,1258,1271,1284,1368,1386,1962,1980,1998,2078,2144,2276,2344,2655,2946,2959`） |

---

## Findings

**R1｜[P2]｜`doc/tasks/M2-SFX-PROD-1.md:57`、`doc/handoffs/M2-SFX-PROD-1-038e8faf.md:53`｜"三套件 520 passed + 1 skipped"与基线"437+1 skipped"口径不可比。** 基线三套件（`doc/tasks/M2-SFX-DETECT-EVAL.md:59`、`M2-PROD-DETECT-3.md:120`）是 **providers 291+1sk / m2_acceptance 35 / core 111 = 437+1sk**；Owner 的三套件换成了 **core/providers/pipeline**（m2_acceptance 被替换为 pipeline），数值自洽（291+23=314 / 111+11=122 / pipeline 84 → 520），但 AC8 原文写的是"三套件基数（437+1skipped）不回退"，按此口径未被验证。**建议**：按 providers/core/m2_acceptance 复跑并登记 437→470 的 delta；若要启用 pipeline 口径，须显式声明套件变更并附 m2_acceptance 独立计数（`test_registry_readiness` 那 1 skip 的归属也需一并说明）。

**R2｜[P3]｜`verification/M2-SFX-PROD-1/envelope.md:33-34`（vs `:40-41`）｜体积基线张冠李戴 + 单位混用。** `:33` 写"M2-AC5 基线安装包（DETECT-2 记录）**439.45 MB**"——439.45 **MiB** 实为 **M2-PROD-DETECT-3** 的 NSIS（460,795,026 B，`doc/tasks/M2-PROD-DETECT-3.md:63`），DETECT-2 是 **438.86 MiB**（`:41` 自述）。同一文档两处基线互相矛盾；且 `+43.03 MB` 是十进制 MB 增量（503,209,268−460,181,312=43,027,956 B），与 MiB 基线并列易误读。**建议**：`:33` 改为 438.86 MiB 并注明基线选择理由（或改用更近的 DETECT-3 基线 → 增量 42.41 MB），增量统一标注十进制 MB/ MiB 两者。

**R3｜[P3]｜`doc/tasks/M2-SFX-PROD-1.md:56`、`doc/handoffs/M2-SFX-PROD-1-038e8faf.md:57`、`verification/M2-SFX-PROD-1/envelope.md:52`｜"几何误差 < 0.02 px"与实际观测不符。** `frozen-sfx-probe-results.json` SF-1b：x0 Δ=0.0055、y0 Δ=0.0107、**x1 Δ=0.0205、y1 Δ=0.0224**（评估 payload 把 box `round(v,1)`，理论最大误差 0.05px）。探针容差 ±2.0px，`PASS` 判定正确；但"<0.02px"这一精确声称不成立。**建议**：改为"≤0.05px（评估 payload 的 0.1px 记录精度内）"或直接引实测最大 0.0224px。

**R4｜[P3]｜`src/infrastructure/providers/detection_sfx.py:333-345`（调用点 `:302`）｜"imgsz 读 metadata"的机制声称在真实权重上不成立。** 真实 metadata 是 `"imgsz": "[1024, 1024]"`（`experiments/M2-SFX-DETECT/onnx-sfx-frames.json:34,1193`），`int("[1024, 1024]")`→ValueError→**恒走 `SFX_DEFAULT_IMGSZ=1024` fallback**；评估蓝本本就硬编码 1024（`eval_sfx_mangabubble.py:204`），故行为一致、结果正确。但：①`test_engine_imgsz_comes_from_metadata` 用 `"768"`（真实 metadata 不存在的形态）证明该路径，属**人造证明**；②若未来权重 metadata 变为可解析的其它值，生产会改用新值而评估蓝本仍 1024 → **口径静默分叉**；③options 只记最终值，无法区分"metadata 说 1024"与"metadata 不可解析降级 1024"。**建议**：`_parse_imgsz` 支持 list/JSON 形态（或显式拒绝并记录 metadata 原文到 options），测试改用真实形态 `"[1024, 1024]"`。

**R5｜[P3]｜`detection_sfx.py:205-208`、`:251-302`、`:529-543`｜失败路径无负缓存：hash 不符/session 失败时**每页**重复 sha256(41MB)+重建 session 尝试。** `_engine` 只在成功时写入；`ProviderError` 使 `_engine` 保持 `None`，下一个页面重新进入 `_build_engine`（41MB sha256 约百毫秒量级）。正确性无碍（仍 fail-closed），但错误配置下变成每页持续惩罚 + 每页一条 stderr（长章节任务下日志噪音）。**建议**：缓存失败状态（last error 短路到下次显式重试），或在 composite 层对降级警告做一次限流。

**R6｜[P3]｜`detection_sfx.py:542` vs `doc/tasks/M2-SFX-PROD-1.md:51`｜降级状态字符串不一致。** 实现是 `f"degraded: {error.error_code}"`（冒号后**带空格**，实测断言 `tests/providers/test_detection_sfx.py:498` = `"degraded: PROVIDER_NOT_CONFIGURED"`），Task/handoff 写 `degraded:<code>`（无空格）。**建议**：两处统一（或明确 `<CODE>` 前的空格是格式的一部分）。

**R7｜[P3]｜`verification/M2-SFX-PROD-1/raw/ac8-discipline.txt`（12 行）、`gate-production-stdout.log`（7 行）｜证据留痕为结论式摘要，非可复核原始输出。** `ac8-discipline.txt` 未给被检路径模式、权重 grep 模式与命令原文；`gate-production-stdout.log` 只是 CS-R production 单场景日志，被 envelope.md `:47` 称为"stdout 见（GATE stdout）"——**GATE runner 全量 stdout 缺失**（DETECT-2 有 `raw/cleanstart-runner-stdout.log`）。实质结论可由 diff 26 文件清单独立复核，但留痕等级低于本项目既有标准。**建议**：把 `git diff --name-only 60f18d0d..HEAD -- <禁改面路径>` 的原始输出与 GATE 全量 stdout 归档进 `raw/`。

**R8｜[P3]｜`doc/STATUS.md:14`｜改动不在 Task §允许清单，且本仓存在同类越界先例。** Task `允许` 未列 `doc/STATUS.md`；`doc/tasks/M2-SFX-DETECT-EVAL.md:59` 明确把"Owner 改写 STATUS"判为越界（R7）。本次仅回填 Active Task 行的 `in_review`/`delivery_head`/handoff 链接（diff 单行），事实正确、风险低。**建议**：集成方追认，或按先例在集成 commit 中承接 STATUS 回填。

**R9｜[P4]｜`core_assembly.py:647-654`（被 `:894-898` 的 SFX lookup 复用）｜frozen 缺 SFX 权重时的 stderr 指引指向错误的 env。** 复用 `_resolve_detector_weights_path` 的代价：警告文案写 `NEWMANGA_DETECTOR_WEIGHTS`，对 SFX 应为 `NEWMANGA_SFX_WEIGHTS`；且 frozen 下该通用警告会与 SFX 自身的降级警告并存（同一缺失打两条）。**建议**：加一个可选参数覆盖 env 名，或在 SFX 侧另打一条专属提示。

**R10｜[P4]｜`core_assembly.py:878-890`｜mock 分支下 `NEWMANGA_SFX_DETECTION` / `NEWMANGA_SFX_CONF_THRESHOLD` 非法值不 fail-fast。** 校验位于 `else`（非 mock）分支内，`mock_local_providers=True` 时非法值被静默忽略，与"非法配置 fail-fast，绝不静默默认"的声明不完全一致（mock 为验收专用，影响面小）。**建议**：把 mode 校验提到分支外。

**R11｜[P4]｜`tests/providers/test_detection_sfx.py:146-155`｜"hash 门先于 runtime import"的证明力依赖环境。** 在已装 onnxruntime 的机器上 junk 文件测试只证明"hash 先于 session build"，无法区分"先 import 再 hash"；只有无 onnxruntime 机器才会因 `PROVIDER_DEPENDENCY_MISSING` 暴露顺序。**建议**：monkeypatch `importlib.import_module` 断言未被调用（顺序的直接证明，且与机器无关）。

**R12｜[P4]｜`verification/M2-SFX-PROD-1/envelope.md:47`｜GATE 分组求和 3+2+3+3+5+4+4=24 ≠ 25/25。** `gate-cleanstart.json` 中 CS-A 实为 6 条（`CS-A1-run1`、`CS-A1-run2`、A2..A5），25 条全部 PASS、总数结论正确，仅分组描述漏计 run2。**建议**：改为"CS-A 5 场景 6 条记录"。

**R13｜[P4]｜`packaging/m2ac5/core_sidecar.spec:120-121,168-188`｜闭包断言只钉 `onnxruntime_pybind11_state.pyd`，未钉 `capi/onnxruntime.dll`。** 与既有 torchvision 断言同模式，且 DLL 由 PyInstaller 内置 hook 带入——本次已由 GATE + frozen 探针 SF-1 真实推理**实证覆盖**，故不构成缺口，仅登记：若未来 pyd 被收集而 DLL 未被收集，构建会通过而发布期才暴露。

**R14｜[P4]｜测试矩阵（`tests/core/test_sfx_assembly.py:147-154` 自述）｜"装配 detector=composite → 真 handler → 装配 `_create_detected_region` closure"这条完整链无单条测试串联。** 现为两半各自覆盖：handler 传第 5 参（`test_detect_handler.py:289-350`，用自定义 creator）+ 分派函数（`test_sfx_assembly.py:132-200`，手工复现 closure 两步）。逻辑拼装覆盖充分，但若 closure 签名/调用位置漂移，无单条测试会红。**建议**：后续 slice 加一条"真装配 + mock sfx detector"的端到端（也正好补 C① 的 mock 覆盖缺口）。

---

## 裁量裁定建议（集成方采纳建议）

**① mock 跳过 SFX provider —— 采纳（不要求返修）**
理由：在 mock 面挂真 composite 会让 acceptance 每页产生降级警告与 `sfx_provider_status` 扰动，与"deterministic mock 代表整个 detect 面"的验收语义冲突；Owner 已在 `handoff §7.8` 登记该边界。**建议条件**：在 acceptance 面补一个 mock sfx 探针（或在 readiness/provenance 面显式标注"mock 面不含 SFX"），并把 R10 的 env 校验提到分支外。

**② composite SFX typed 失败降级 —— 采纳（方向正确），但补一处可见性**
不违反 fail-closed：fail-closed 的对象是"步骤的必需能力"（主检测器不可用仍 typed 失败，未变），SFX 是可选附加能力，其不可用使步骤回到 pre-SFX 现状而非伪造成功；"误标 sfx=对白被 SKIP 不译（重）"vs"SFX 不可用=漏检（轻）"的方向性论证成立，与用户三裁决的 precision-first 冻结（conf≥0.5）自洽。**唯一实质缺口**：降级只落在 `detect` 的 provenance options + stderr 一行，步骤仍 `COMPLETED`，发布版用户看到的是"SFX 静默不工作"（若安装后权重被 AV 隔离/删除）。**建议（非阻塞条件）**：把 `sfx_provider_status` 暴露到 provider readiness / 诊断面板一次即可；改动点确如 Owner 所述是 `MangaSfxParallelDetectionProvider.detect` 单处（或 provider 侧一次性告警），可逆。

**③ helper 穿透 `getattr(detector, "primary", detector)` —— 采纳，未弱化断言**
断言对象从"装配产出的 detector"精确为"装配选出的 primary"，而穿透取到的就是同一个对象（composite 仅持有而不修改 primary 的 `provider_id`/`provider_type`/`model`/`weights_dir`/`weights_path`）；`test_detector_weights_lookup.py:72` 若不穿透则连 `weights_dir` 都不存在（AttributeError），故穿透是回归修复的正确手段而非放宽。丢失的"顶层是 composite"断言由 `tests/core/test_sfx_assembly.py:74-96` 单独钉住，净覆盖未降。**建议**：保留现写法；若想进一步收紧，可让 composite 对 `weights_dir`/`weights_path` 做显式委托（而非改测试）——但那会削弱"composite 不是 primary"的可见性，非必要。

---

## NOT_VERIFIED

1. **全部运行时复跑**：pytest 1563+1sk / 三套件 520+1sk / cargo 44+1ig / vitest 31——纯静态未复跑；仅核对内部算术与套件归属（见 R1）。
2. **GATE 25/25 与 frozen 探针 SF-1/2/3 实跑**：只读 `gate-cleanstart.json` / `frozen-sfx-probe-results.json` / `envelope-results.json`，未独立重跑；探针容差、断言条件已逐行读过，判定逻辑正确。
3. **NSIS 实物**：503,209,268 B 与 sha256 `1bf31cf8…2d2c` 仅来自 JSON 自述与 envelope.md，未复算字节/哈希；闭包目录 35.8MB / 8584 pure modules 同。
4. **权重与外部树**：`yolo11s-seg.onnx`（41,227,478 B）本体与 `d87389af…b646` 未复算，一致性建立在 `external-evidence-inventory.json` 记录之上；real ONNX 测试是否真跑由"skip 仅 1 条"间接推断（若 real 被跳过应是 4 skipped）。
5. **onnxruntime==1.30.0 的可得性/安装态**：主 venv 与 build venv 的安装、PyInstaller hook 对该版本的行为未验证（依赖 frozen 探针实证）。
6. **Git 层**：`git diff --check 60f18d0d..HEAD` EXIT=0、禁改面专项 diff 空、权重零 tracked、`base_commit=2f37b63a` 与分支起点 `60f18d0d` 的同链关系、`delivery_head=038e8faf` 与 `0ec02ea3` 的回填关系——沙箱不可执行 git，均未独立复核（diff 26 文件清单可交叉佐证范围纪律）。
7. **`+2620/-21` 行数**：未精确统计（与新增文件规模相符）。

---

## 集成方闭合清单

- **C1**：统一 pytest 三套件口径——按基线 `providers/core/m2_acceptance` 复跑（预期 437→470）并登记；若保留 `pipeline` 口径，显式声明套件变更 + 单列 m2_acceptance 计数（R1）。
- **C2**：修正 `verification/M2-SFX-PROD-1/envelope.md:33` 的基线（438.86 MiB / DETECT-2，或改用 DETECT-3 基线并重算增量），统一增量单位（R2）。
- **C3**：把"<0.02 px"改为实测/精度上限表述（≤0.05px，实测最大 0.0224px）于 Task `:56`、handoff `:57`、envelope.md `:52`（R3）。
- **C4**：三处裁量（mock 跳过 / composite 降级 / helper 穿透）逐条追认或驳回；若采纳②，登记"SFX 降级可见性增强"为后续 slice 并给出触发条件（本文档"裁量裁定建议"）。
- **C5**：处置 `doc/STATUS.md:14` 的越界（追认或由集成 commit 承接），口径与 `M2-SFX-DETECT-EVAL` R7 先例对齐（R8）。
- **C6**（若项目标准要求）：补 `raw/` 的 GATE 全量 stdout 与禁改面检查的原始命令输出（R7）；顺手修 R4（`_parse_imgsz` 支持真实 metadata 形态 + 测试改真实值）、R6（degraded 字符串）、R12（GATE 分组描述）。

---

## 推荐下一步

请集成方按 C1–C6 在集成 commit 中闭合账目与证据项并追认三处裁量后合并，同时把"SFX 降级可见性"与"跨权重版本的 imgsz/harvest 口径登记"排入后续 slice。
