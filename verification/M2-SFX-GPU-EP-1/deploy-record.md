# M2-SFX-GPU-EP-1 部署记录（Deployment Record）

Task: M2-SFX-GPU-EP-1 — SFX 推理 EP 切换 GPU（DML）
Owner: ZCode；base=48e83a33；branch=`agent/zcode/M2-SFX-GPU-EP-1`
授权：用户裁决 2026-10-06「部署形态=GPU」（T5-TILE-KO 收口呈报 CPU 10.46s/页 vs GPU DML 1.08s/页）
状态：owner_claim（交付中）；Reviewer=DeepSeek Harness（非作者，待 r1）

## 0. 交付摘要

生产 SFX 推理从 `onnxruntime==1.30.0`（CPU 包）+硬编码 `CPUExecutionProvider`
切换为 `onnxruntime-directml==1.24.4` + EP 配置化：`NEWMANGA_SFX_EP`
（`dml` 默认=用户裁决 | `cpu`=pre-GPU 行为原样），非法值 fail-fast
ValueError 先于权重解析（沿 T5 env 纪律）；DML 初始化失败自动回退 CPU EP
并以 `sfx_ep` / `device` / `sfx_ep_fallback` 三键审计（不静默）。
contracts/**、apps/**、manga 检测面零 diff；权重（v2b 944e8114）、tile 口径
（T5 冻结）、conf 0.5 门全部不动。

## 1. AC1 依赖与 EP 配置化 — PASS

### 1.1 依赖面

| 文件 | 变更 |
|---|---|
| `requirements.txt` | `onnxruntime==1.30.0` → `onnxruntime-directml==1.24.4`（含版本裁量注释） |
| `packaging/m2ac5/requirements-build.txt` | 同行 VERBATIM 同步（PROD-2 冻结纪律：build venv 与 runtime 逐字一致） |

**版本 pin 裁量说明**：PyPI 的 `onnxruntime-directml` 发布线顶点即 **1.24.4**
（`pip index versions` 实测：1.24.4 为最新；onnxruntime 主仓 CPU 包 1.30.0
的对应 directml 构建不存在）。1.24.4 正是 T5 perf venv 实测 1.08s/页的
build——本 Task AC2/AC3 数字与其同版本、同机器，可比性最强。API 同构：同一
import 名 `onnxruntime`、同一 pyd 名 `onnxruntime_pybind11_state.pyd`，wheel
额外捆绑 `DirectML.dll` + `onnxruntime_providers_shared.dll` 于
`onnxruntime/capi/`。

**互斥性**：directml 包与 CPU 包同环境互斥（装一换一）。两个 venv 已换装并
记录：

| venv | 用途 | 换装后 |
|---|---|---|
| `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312` | 生产/pytest | onnxruntime-directml 1.24.4，`get_available_providers()=['DmlExecutionProvider','CPUExecutionProvider']`（raw/venv-swap-prod.log） |
| `G:/CODEX/New Manga.task-envs/m2ac5-build` | PyInstaller 打包 | 同上（raw/venv-swap-m2ac5-build.log） |

### 1.2 EP 配置化（src/infrastructure/providers/detection_sfx.py）

- `SFX_ENV_EP = "NEWMANGA_SFX_EP"`，值 `dml`（默认）|`cpu`；strip+lower
  容忍；空值/非法值 fail-fast `ValueError` 命名变量。
- **时序**：`detect()` 在 `_validate_request` → `_tile_config()` 之后、
  `_engine_or_raise()` 之前调用 `_ep_config()`——非法值先于权重解析、先于
  任何推理（与 T5 tile env 同一纪律、同一位置模式）；且每次 detect 都读，
  暖引擎也逃不过校验。单测
  `test_ep_config_illegal_value_fails_fast_before_weights_resolution` 以
  「weights_path 指向不存在文件时 raise ValueError 而非
  ProviderNotConfigured」实证时序。
- **engine 缓存语义**：providers 在 InferenceSession 构造时固定，是
  engine 级属性——EP 随首次 detect 解析并随 engine 缓存至 provider 实例
  生命周期结束（与 `conf_threshold` 字段同级）；换 EP = 新 provider 实例
  或进程重启；暖引擎下后续 env 变更**不反映**进 options（`sfx_ep` 记录
  引擎构建时的请求值，fail-fast 读只守 env 合法性、不重解析引擎，r1
  P4-4 注记）。
- `_build_engine(weights_path, ep_mode=None)` 返回 5 元组
  `(session, imgsz, imgsz_source, imgsz_raw, _EpProvenance)`——EP
  provenance 沿 DSH r1 R4 imgsz provenance 同一模式随 engine 传递。

### 1.3 DML 初始化失败语义（Owner 设计裁量，登记；r1 P1-1 机制更正后终版）

**设计：自动回退 CPU EP + 三键审计，绝不静默、绝不错值。**

- **机制（r1 P1-1 更正）**：onnxruntime 的 Python 包装层
  `InferenceSession.__init__` 自带 CPU 回退（`enable_fallback` 缺省 True，
  生产 wheel `onnxruntime_inference_collection.py:482,503-519,576-577`）——
  DML 初始化失败（无 DX12 GPU / 驱动缺失 / CPU-only wheel）被包装层吞掉
  （except `(ValueError, RuntimeError)`），以 `["CPUExecutionProvider"]`
  重建并**正常返回**（仅 stderr 打 EP Error banner）。因此**主回退路径不
  经过本仓的 except 分支**；有效 EP 的权威来源是构造后的
  `session.get_providers()` 读回：请求 dml 而首 provider 非
  `DmlExecutionProvider` = 包装层回退，写入同一套三键审计。本仓 except
  分支保留为**防御兜底**（覆盖逃逸出包装层的异常形态 / 禁用回退的构建），
  其内做显式 CPU 重建（原因含异常类型名）。
- 审计三键进 detect options：`device`=<有效 EP>（`cpu`）、`sfx_ep`=<引擎
  构建时 env 请求值>（`dml`）、`sfx_ep_fallback`=原因（包装层回退形态
  "requested dml but onnxruntime built the session on
  CPUExecutionProvider (wrapper-level fallback/EP unavailable)" / 兜底形态
  "dml init failed; fell back to cpu (<异常类型名>)"）；
- **显式 `cpu` 请求失败 = typed `ProviderError`，无回退**（显式请求不允许
  悄悄降级为其它东西）；
- 回退只覆盖**初始化**：会话构建成功但 run() 失败维持既有 detect 期 typed
  失败路径不变；
- **供应链安全面不受影响**：SHA-256 权重门仍先于任何 runtime import
  （检查顺序 1.EP env → 2.文件存在 → 3.sha → 4.import → 5.session →
  6.metadata 断言），EP 不是 pin 对象，sha 门纪律零变化；
- **三形态验证矩阵**：
  1. **包装层回退（真实主形态）——决定性验证 PASS**：独立 venv
     `M2-SFX-GPU-EP-1-cpu-verify`（onnxruntime==1.30.0 CPU-only 包，进程内
     无 DML provider，= 生产 venv 换装前状态）+ 生产代码原样 detect：
     `sfx_ep='dml'`、`device='cpu'`、
     `sfx_ep_fallback='requested dml but onnxruntime built the session on
     CPUExecutionProvider (wrapper-level fallback/EP unavailable)'`——
     `raw/wrapper-fallback-cpu-wheel.{json,log}`（VERDICT: PASS；ORT
     "not in available provider names" UserWarning 原样入 log）；
  2. **包装层回退的 stub 钉子**：
     `test_engine_wrapper_level_cpu_fallback_gets_three_key_audit`（构造器
     不抛异常、无第二次构造、get_providers 读回驱动三键；先红——红证据
     `raw/tests-p11-wrapper-fallback-red.log` 实证旧实现 device 错报
     "dml"——后绿）；
  3. **异常驱动兜底**：`test_engine_dml_failure_falls_back_to_cpu_with_audit`
     （stub 对 DML raise / 对 CPU 成功，断言 providers 序列
     `[Dml]→[CPU]` + 三键）+ `test_engine_cpu_failure_is_typed_no_fallback`
     （显式 cpu 失败 typed 无回退）。
- **r1 证据误读更正**：初版报告把 tests-ep-green.log 的 ORT 警告当「本仓
  except 回退路径的反向实证」——**误读**。该警告是 ORT 包装层内建回退的
  表现（构造器正常返回，本仓 except 未执行），当时无任何 sfx_ep_fallback
  观测；正确机制与决定性验证如上。

### 1.4 主检测器（manga）面零改动声明

`detection_manga.py`（ogkalu RT-DETR-v2，torch/transformers 栈）无
onnxruntime session、无 ExecutionProvider 概念，本 Task 零触碰；
`contracts/**`、`apps/**` 零 diff（git 证据见交付链）。EP 配置化严格 SFX
专属：新常量/env/逻辑全部在 detection_sfx.py 内。

## 2. AC2 数值一致性硬门 — PASS（非逐位一致，漂移量化+门/匹配零影响）

证据：`raw/gpu-ep-parity-perf.json` + `raw/gpu-ep-parity-perf.log`
（脚本 `experiments/M2-SFX-GPU-EP-1/verify_gpu_ep_parity_perf.py`，双面均经
生产 env 门+生产 detect，无 session swap 旁路；v2b pin 原样；每页 warm-up
1 次不计 + 计测 1 次取 preds；GPU 面第 3 次 detect 做 run-to-run 稳定性）。

结论：**非逐位一致**（float32 求和顺序级差异），漂移量化如下（逐页）：

| 页面 | 路由 | n_pred CPU→GPU | max abs Δconf | max abs Δxyxy (px) | conf≥0.5 门翻转 | GPU run-to-run |
|---|---|---|---|---|---|---|
| pre-k08 | tile | 23→23 | 1e-06 | 0.0001 | 0 | 逐位稳定 |
| pre-k09 | tile | 50→50 | 1e-06 | 0.0001 | 0 | 逐位稳定 |
| pre-k01 | tile | 23→23 | 1e-06 | 0.0001 | 0 | 逐位稳定 |
| pre-k02 | tile | 5→5 | 2e-06 | 0.0001 | 0 | 逐位稳定 |
| pre-bj17 | letterbox | 2→2 | 0.0 | 0.0 | 0 | 逐位稳定 |
| pre-bj18 | letterbox | 3→3 | 0.0 | 0.0002 | 0 | 逐位稳定 |

**matched 集不变性**（KO 4 页，双 GT 口径，(gt_index, pred_index) 索引对
集合相等判定）：

| 页面 | derived GT (56 档) | npd GT (135 框) | 集合相等 |
|---|---|---|---|
| pre-k08 | 14/27 → 14/27 | 14/35 → 14/35 | 两者均 True |
| pre-k09 | 17/24 → 17/24 | 26/42 → 26/42 | 两者均 True |
| pre-k01 | 2/2 → 2/2 | 5/48 → 5/48 | 两者均 True |
| pre-k02 | 2/3 → 2/3 | 3/10 → 3/10 | 两者均 True |

**判定**：Δconf ≤ 2e-06（conf 值本身 0.5-0.9+ 量级，相对漂移 ~1e-06）；
Δxyxy ≤ 0.0002 px（亚微米像素级）；conf≥0.5 门零翻转（gate_flips=0 全
6 页）；matched 集逐页全部不变。**检出行为在 GPU DML 与 CPU EP 下等价**
（在 conf≥0.5 生产门与 GT 匹配口径下不可区分）。

**配对口径（r1 P3-2 注记）**：`max |Δconf|/|Δxyxy|` 按双侧 `(-conf, xyxy)`
排序后的**位次 zip** 比较；"matched 集不变"指 **(gt_index, pred_index)
索引对集合相等**——`pred_index` 是生产候选顺序位次，GPU 面 `bit_identical
=false`（全 6 页）下理论上存在微重排使"索引对相等"不严格等同于"同一物理
框"；Δ≤2e-06/0.0002px 使该风险极低，但口径应读作**索引集不变**（跨面
最近邻 IoU 配对复核未做，留作可选强化）。

**T5 对账口径（r1 P3-3 注记）**：与 T5 基准的可比对账**仅限 v2b**——KO
derived 14+17+2+2=35/56、npd 14+26+5+3=48/135，与 T5 v2b 基准逐位吻合；
T5 的 chiqui7 56/56+41/135 与 BJ chiqui7（6 preds）属另一权重，本 Task 未
跑、不可比。BJ 考卷页本 Task **未做 GT 匹配**（只记 n_pred 与双面漂移；
n_pred 2+3=5 与 M2-SFX-TRAIN-V2 记录的 v2b BJ 5/5@0.5 自洽）。

## 3. AC3 生产路径性能复测 — PASS（如实登记）

同一次运行的计测面（wall clock，每页 warm-up 后计测 1 次）：

| 域 | CPU EP（均值/逐页） | GPU DML（均值/逐页） | 对照 |
|---|---|---|---|
| KO 4 长条页 | 10.447 s/页（9.59/17.83/11.06/3.30） | **1.106 s/页**（1.00/1.96/1.13/0.33） | T5 呈报 CPU 10.46 / GPU 1.08 —— 双面均复现 |
| BJ 普通页 ×2 | 0.203 s/页（0.204/0.202） | **0.065 s/页**（0.065/0.064） | 小图 GPU 未见劣化 |

- KO 域生产路径 GPU 时延 1.106 s/页与 T5 perf 呈报 1.08 s/页同量级一致
  （T5 为独立 venv + session swap 口径，本轮为生产 env 门口径，数字互证）。
- **普通页如实登记**：本机（RTX 5070 Ti）上 BJ 考卷页 GPU 反而快
  （0.065 vs 0.203 s）——本轮**未观察到**「小图 GPU 无收益/劣化」形态；
  此为 directional 观测（n=2、单机、禁用「显著」措辞），不外推所有小图。
- provider elapsed_ms 与 wall clock 一致（KO GPU 均值 1100.75 ms）。

## 4. AC4 打包面 — PASS

- `core_sidecar.spec`：`SFX_BINARY_IMPORTS` 增 `DirectML.dll`
  （`onnxruntime_pybind11_state.pyd` 名不变——directml wheel 同名 pyd）；
  ML_HIDDENIMPORTS `onnxruntime` 名不变（同一 import 名）。
- `build_sidecar.ps1 -Force` 全量重建（HEAD=016e1259，pyinstaller 6.22.3，
  m2ac5-build venv directml 1.24.4）EXIT=0
  （raw/build-sidecar-dml.log）；**构建期闭包断言 PASS**：
  `closure assertion: core_service PYZ carries transformers,
  transformers.models.rt_detr, transformers.models.rt_detr_v2, onnxruntime
  (8584 pure modules) + extensions torchvision/_C_stable.pyd,
  torchvision/image_stable.pyd, onnxruntime_pybind11_state.pyd,
  DirectML.dll`。
- GATE（`packaging/m2ac5/run_clean_start_e2e.py`）：PASS（见 §7.2）。
- 包体积实测：见 §7.1。

## 5. AC5 测试与回归 — PASS

- 先红：`raw/tests-ep-red.log`（7 failed + 1 passed——passed 项为「显式 cpu
  失败 typed」回归保护，旧行为已满足该现状面）。
- 后绿：`raw/tests-ep-green.log`（tests/providers/test_detection_sfx.py +
  tests/core/test_sfx_assembly.py = 97 passed，含真实权重单测）。
- 新增测试矩阵（10 条）：EP 默认 dml / 显式值大小写容忍 / 非法值先于权重
  解析 fail-fast / 空值 fail-fast / session providers 请求记录（默认 DML、
  env cpu→CPU）/ DML 失败回退+审计三键 / 显式 cpu 失败 typed 无回退；
  装配面：EP=cpu 装配同形、off 跳过装配不触碰 EP env（组合语义登记）。
- 全量回归：**1822 passed + 1 skipped + 1 failed（test_catalog 既有
  BASELINE_FAILURE）**（raw/pytest-full-regression.log，EXIT=1 仅因既有
  登记项）——基线 1812+1sk+1 failed + 本 Task 新增 10 测试 = 1822，逐项
  吻合，**与基线一致**（生产 venv 已是 directml 1.24.4 环境下跑得）。
- PROD-1 envelope 遗留边界闭合登记：PROD-1 登记的「GPU EP 是后置优化项」
  由本 Task 闭合（此处即为登记处；历史文件不改写）。

## 6. 纪律声明

- directional 纪律：§2/§3 全部数字为 directional 证据（n 小、单机、低统计
  功效），不作质量判定，未使用「显著」。
- 权重/GT 不入 Git（v2b 944e8114 与 npd/derived GT 均在 gitignored 外部
  task-envs 树）。
- tile 口径（T5 冻结）、权重 pin、conf 0.5 门零变化（AC2 的 KO 页全部
  `sfx_route=tile`、BJ 页全部 `sfx_route=letterbox` 即口径未动的运行期
  实证）。

## 7. 构建链与回归实测

### 7.1 包体积变化（vs T4 终态基线）

载体：`raw/bundle-sizes.log`（Get-Item/Get-ChildItem 实测，r1 P4-2 补录；
本表全部数字以其为准）。

| 口径 | CPU 包终态（T4 时代基线） | DML 包（本 Task 实测） | Δ |
|---|---|---|---|
| onedir `_internal/onnxruntime/` | 35.8 MB（Task 合同引 PROD-1 记录） | **66,170,520 B / 63.11 MiB** | **+27.3 MiB**（DirectML.dll 18,527,776 B / 17.67 MiB + onnxruntime.dll/providers_shared.dll 增量） |
| onedir 整包 `core-sidecar/` | —（未单列基线） | 1,225,505,427 B / 1168.73 MiB | — |
| NSIS 安装包 | 460,181,312 B / 438.86 MiB（M2-PROD-DETECT-2 release-notes，T4 未重建包体沿用该闭包形态） | **512,645,237 B / 488.90 MiB**（sha256 `61df0299…`，GATE CS-E2 + bundle-sizes.log） | **+52,463,925 B / +50.03 MiB** |

注：T4-SWITCH 只替换权重 pin 未重建包体，其「终态基线」= PROD-2 时代
onnxruntime CPU 包闭包（438.86 MiB NSIS / 35.8MB onnxruntime 目录）。
+50 MiB 主体即 DirectML.dll 及 onnxruntime DML 构建的 native 依赖
（NSIS 压缩后 onnxruntime 目录增量 27.3 MiB → 安装包面 50.04 MiB，含
directml wheel 其它文件的压缩差异），可接受性属用户部署形态裁决范围
（裁决已选 GPU）。

### 7.2 tauri build + GATE 重跑 — PASS

- tauri build EXIT=0（raw/tauri-build.log，Rust release 1m01s + NSIS 打包）；
  `gen/schemas/**` + `permissions/autogenerated/**` 行尾重写已按 README
  纪律 `git checkout --` 还原（worktree clean 确认见 Handoff）。
- **GATE `run_clean_start_e2e.py` = PASS（25/25 场景全 PASS，EXIT=0**，
  raw/gate-clean-start-e2e.log）：
  - 环境：CS-E1 python purged / CS-E2 installer sha256 `61df0299…` /
    CS-E3 空格无害路径；
  - 安装与库面：CS-I1 四 exe 装齐 / CS-I2 packaged catalog_loader 种子 /
    CS-L1 core.ping ready / CS-L2 ListBooks envelope / CS-L3 shutdown；
  - probe：CS-P1/P2（13 场景全过）/P3 digest sha 一致；
  - AC1 验收环：CS-A1 run1+run2 COMPLETED / CS-A2 restart 新 PID /
    CS-A3 SQLite+reader+PNG export（见 log）/ production mode 真窗口；
  - zero-touch：CS-Z1 安装目录零写入 / CS-Z2 用户源文件字节一致 /
    CS-Z3 无 sidecar 进程残留 / CS-Z4 宿主真实 APPDATA 未触碰。
- 本轮 GATE 跑在 **directml 闭包**上：安装包内 `_internal/onnxruntime/capi/`
  含 DirectML.dll（闭包断言构建期已验），frozen sfx detect 链在无 env
  干预下默认走 DML（有 DX12 GPU 的本机）——frozen 面为 AC1 配置化的
  自然结果，未新增 frozen 专属改动。
- **落点处置登记**：GATE runner 的内置产物落点是
  `verification/M2-AC5/raw/`（M2-AC5 Task 时代目录，不在本 Task 允许面）。
  本轮运行覆盖的工作区副本已快照至
  `raw/m2ac5-gate-artifacts/`（6 文件：gate verdict JSON+五路 stdout），
  `verification/M2-AC5/raw/` 原样还原（保持 M2-AC5 时代历史证据不被跨
  Task 改写）；本 Task GATE 证据以
  `raw/gate-clean-start-e2e.log`（runner 完整 stdout）+
  `raw/m2ac5-gate-artifacts/cleanstart-gate.json`（verdict）为准。
- **frozen 面 DML 证据口径（r1 P3-1 修订）**：「frozen sfx detect 链默认走
  DML」在本仓库内是**推断，不是实测**——GATE 的 25 个场景全部不触及
  sfx 检测/DML（probe 为资源通道、AC1 环为 mock ocr/translate）， DirectML.dll
  的**实体在位**（构建闭包断言 + 盘上产物
  `_internal/onnxruntime/capi/DirectML.dll` 与 pyd 同目录）只证明加载
  路径成立，不构成 frozen 进程内 DML 推理的运行证据。packaged sfx-detect
  探针需要 frozen 命令面扩展（M2-PROD-DETECT-2 的已知 NOT_RUN 结构性
  缺口，须 Codex 立契约），本 Task 不扩权、留作缺口登记。源码形态的
  DML 默认行为由 AC2/AC3 双面证据与 EP 单测覆盖。
