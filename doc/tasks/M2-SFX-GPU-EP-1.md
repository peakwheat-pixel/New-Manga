---
id: M2-SFX-GPU-EP-1
title: "SFX 推理 EP 切换 GPU（DML）：onnxruntime-directml 依赖面+EP 配置化+数值一致性验证+打包闭包与 GATE 重跑"
kind: feature
status: in_review
owner_claim: ZCode @2026-10-06（branch agent/zcode/M2-SFX-GPU-EP-1；claim base=48e83a33=daa34e4e 之上的 release commit、含 T5-TILE-KO 落地终态；授权=用户裁决 2026-10-06「部署形态=GPU」）
delivery: ZCode 2026-10-06（AC1-AC5 全 PASS：依赖换 onnxruntime-directml==1.24.4+NEWMANGA_SFX_EP 配置化默认 dml+DML 失败回退 CPU 三键审计；AC2 漂移量化 max|Δconf|≤2e-06/max|Δxyxy|≤0.0002px 门零翻转 matched 集全不变；AC3 KO DML 1.106s/页 vs CPU 10.447s/页；闭包断言+DirectML.dll、NSIS 488.90MiB、GATE 25/25 PASS；回归 1822+1sk+1 failed=基线一致；status owner_claim→in_review 停写待 DSH 非作者 r1）；r1 review-fix 2026-10-06（changes_requested 1×P1 全闭：回退审计读回反推 get_providers+真实失败形态 stub 用例先红后绿+CPU-only wheel 决定性验证 PASS；P3/P4 应闭全闭；Gate 复验 1823+1sk+1 failed=等量递增）
approval: user_ruling_2026-10-06_GPU（T5-TILE-KO 收口呈报的部署形态终选）
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
depends_on: [M2-SFX-T5-TILE-KO]
base_commit: 48e83a33（=daa34e4e 之上的 release commit、实际 fork 点，含 T5-TILE-KO 落地终态；r1 P4-1 与 owner_claim/HANDOFF 统一以此为准）
branch: agent/zcode/M2-SFX-GPU-EP-1
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-GPU-EP-1-zcode
review_events: []
created: 2026-10-06
---

# Task: M2-SFX-GPU-EP-1 — SFX 推理 EP 切换 GPU（DML）

## 背景与授权

T5-TILE-KO（done @merge `5e70af4e`）性能双档呈报：KO 长条页 CPU 生产 EP 均值 10.46s/页 vs GPU DML 1.08s/页（onnxruntime-directml 1.24.4 独立 venv，RTX 5070 Ti，tile 序列调用生产代码本体）。用户 2026-10-06 裁决部署形态=**GPU**。PROD-1 envelope 遗留边界「GPU EP 是后置优化项」由本 Task 闭合。

现役生产事实：`requirements.txt:41` `onnxruntime==1.30.0`（CPU 包）；`_build_engine` 硬编码 `providers=["CPUExecutionProvider"]`（detection_sfx.py:764 附近，T5 后行号）；PROD-1 闭包断言含 `onnxruntime_pybind11_state.pyd`（frozen onedir `_internal/onnxruntime/` 35.8MB→NSIS 压缩 ~2MB）；生产引擎=「轻量栈裁决：无 torch」。

## 验收条件

- **AC1 依赖与 EP 配置化**：`requirements.txt` `onnxruntime`→`onnxruntime-directml`（版本 pin=本机实测裁量，与 onnxruntime 1.30.0 API 同构；T5 perf venv 用过 1.24.4 可作参考但不锁死）；`_build_engine` EP 配置化——`NEWMANGA_SFX_EP` env（`dml`|`cpu`，**默认 dml=用户裁决**；非法值 fail-fast ValueError 先于权重解析，沿 T5 env 纪律）；**DML 初始化失败语义**（无 DX12 GPU/驱动缺失机器）=Owner 设计裁量并登记——候选方向：自动回退 CPU EP+审计登记（`sfx_ep` 进 options；EP 不属供应链安全面，sha 门纪律不受影响；回退保证行为永远可用，pytest 真实权重测试在无 GPU 机器也因此不炸），不得静默无审计。
- **AC2 数值一致性验证（硬门）**：GPU DML EP 下现役 v2b 权重检出 vs CPU EP 基准对比——KO 4 页（pre-k01/02/08/09）+BJ 考卷 2 页（pre-bj17/18）conf/坐标逐页对比：逐位一致则登记；有浮点差则量化登记（max |Δconf|/|Δxyxy|）并评估对 conf≥0.5 门与匹配结果的影响（matched 集是否不变），**不得只报「基本一致」不带数字**。
- **AC3 生产路径性能复测**：经生产代码路径（非 perf 脚本旁路）实测——KO 4 页 GPU DML 时延（对照 T5 呈报数据 1.08s/页）+**普通页 GPU vs CPU 时延对照**（小图 GPU 可能无收益甚至劣化，如实登记）；结论写进部署记录。
- **AC4 打包面**：`packaging/m2ac5/build_sidecar.ps1` 闭包断言随 onnxruntime-directml 更新（DirectML.dll/pyd 收集确认）；GATE（`run_clean_start_e2e.py`）重跑 PASS；包体积变化实测登记（DML 包比 CPU 包大，vs T4 终态基线）。
- **AC5 测试与文档**：EP 配置单测（默认 dml/非法值 fail-fast/显式 cpu/off 组合语义）先红后绿；全量回归与基线一致（1812+1sk+1 failed test_catalog 既有登记，EP 相关测试在 GPU 机器全绿）；部署记录+Task/Handoff；PROD-1 envelope 遗留边界闭合登记（在部署记录注明即可，不改历史文件）。

## 纪律与限制

- 允许路径：`requirements.txt`（仅 onnxruntime→onnxruntime-directml 行）、`src/infrastructure/providers/detection_sfx.py`（EP 配置段+`_build_engine` providers 参数）、`src/**` 若 EP 语义需要触及装配/审计段（逐文件声明）、`packaging/**`（闭包断言+GATE）、`tests/**`、`doc/tasks/M2-SFX-GPU-EP-1.md`、`doc/handoffs/`、`verification/M2-SFX-GPU-EP-1/**`、`experiments/M2-SFX-GPU-EP-1/**`。
- 禁区：`contracts/**`（输出面零变化）、`apps/**`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`。
- 权重不换（v2b 944e8114 现役）、tile 口径不动（T5 冻结）、`SFX_CONF_THRESHOLD=0.5` 不动。
- DML 依赖装不进 venv 时（版本冲突等）如实登记 BLOCKED 停等，不得用旁路 mock 冒充 GPU 结果。
- directional 纪律：性能数字不作质量判定；「显著」禁用。
- 权重/GT 不入 Git（gitignored）。

## 交付记录（Owner=ZCode，2026-10-06）

**结果：AC1-AC5 全 PASS。生产 SFX 推理切至 onnxruntime-directml==1.24.4 + `NEWMANGA_SFX_EP`（dml 默认=用户裁决 | cpu），DML 初始化失败自动回退 CPU EP+三键审计；AC2 数值硬门=非逐位一致但漂移 max|Δconf|≤2e-06 / max|Δxyxy|≤0.0002px、conf≥0.5 门零翻转、KO 双 GT 口径 matched 集逐页全部不变；AC3 生产路径 KO DML 1.106s/页（对照 T5 呈报 1.08 同量级）vs CPU 10.447s/页；闭包断言+DirectML.dll 构建期 PASS、NSIS 488.90MiB（+50.04MiB vs T4 终态基线）、GATE 25/25 PASS；全量回归 1822+1sk+1 failed（test_catalog 既有登记）=基线一致（1812+10 新测试吻合）。PROD-1 envelope 遗留边界「GPU EP 后置优化项」闭合（部署记录 §5 登记）。status owner_claim→in_review 停写，待 DSH 非作者 r1 Review。**

| AC | 判定 | 核心证据 |
|---|---|---|
| AC1 依赖与 EP 配置化 | **PASS** | `requirements.txt`+`requirements-build.txt`（VERBATIM 同步）`onnxruntime==1.30.0`→`onnxruntime-directml==1.24.4`（PyPI directml 线顶点=1.24.4=T5 实测 build，pip index 实测）；`_build_engine` EP 配置化：`NEWMANGA_SFX_EP` dml\|cpu 默认 dml，fail-fast ValueError 先于权重解析（detect 期每次读取，暖引擎也校验；单测以「缺失权重时 raise ValueError 而非 ProviderNotConfigured」实证时序）；**DML 失败语义（Owner 裁量并登记）=自动回退 CPU EP+`device`/`sfx_ep`/`sfx_ep_fallback` 三键审计，显式 cpu 失败保持 typed 无回退，回退只覆盖 init；EP 非供应链安全面（sha 门先于 import 零变化）**；engine 5 元组沿 DSH r1 R4 provenance 模式；manga 面/contracts/apps 零 diff。commit `3867f3c4` |
| AC2 数值一致性硬门 | **PASS（漂移量化+零影响）** | 双面均经生产 env 门（无 session swap 旁路），v2b pin 原样：KO 4 页 max|Δconf| 1e-06~2e-06 / max|Δxyxy| 0.0001px；BJ 2 页 Δconf=0.0 / Δxyxy 0~0.0002px；**gate_flips=0 全 6 页（conf≥0.5 门零翻转）；KO 双 GT 口径 matched 集逐页全不变（pre-k08 14/27+14/35、pre-k09 17/24+26/42、pre-k01 2/2+5/48、pre-k02 2/3+3/10，derived+npd (gt,pred) 索引对集合相等）**；GPU run-to-run 逐位稳定全 6 页。`raw/gpu-ep-parity-perf.{json,log}` |
| AC3 生产路径性能复测 | **PASS（如实登记）** | KO 4 页：GPU DML 均值 **1.106s/页**（1.00/1.96/1.13/0.33）vs CPU 均值 10.447s/页——T5 呈报双面（1.08/10.46）复现同量级；BJ 普通页 GPU 0.065s vs CPU 0.203s——本机未观察到小图 GPU 劣化（directional，n=2，不外推）。同上 raw 证据 |
| AC4 打包面 | **PASS** | `core_sidecar.spec` SFX_BINARY_IMPORTS+`DirectML.dll`；build_sidecar -Force 全量重建 EXIT=0，构建期闭包断言 PASS（PYZ onnxruntime+extensions `onnxruntime_pybind11_state.pyd, DirectML.dll`，HEAD=016e1259）；tauri build EXIT=0 → NSIS **512,645,237 B / 488.90MiB**（sha 61df0299…，**+50.04MiB vs T4 终态基线 438.86MiB**；onedir `_internal/onnxruntime` 35.8MB→63.11MiB）；**GATE run_clean_start_e2e.py 重跑 PASS 25/25**（EXIT=0；install sha 校验/四 exe/packaged probe 13 场景/AC1 验收环 run1+run2/zero-touch Z1-Z4 全过）。`raw/build-sidecar-dml.log`、`raw/tauri-build.log`、`raw/gate-clean-start-e2e.log` |
| AC5 测试与文档 | **PASS** | EP 配置单测先红（`raw/tests-ep-red.log` 7F+1P）后绿（`raw/tests-ep-green.log` 97 passed 含真实权重单测；+10 用例：默认 dml/大小写容忍/非法值先于权重 fail-fast/空值 fail-fast/providers 请求记录/DML 回退三键审计/显式 cpu typed 无回退/装配 cpu 同形/off 不触碰 EP env）；全量回归 **1822 passed+1 skipped+1 failed（test_catalog 既有 BASELINE_FAILURE）**（`raw/pytest-full-regression.log`）=基线 1812+10 吻合一致（directml 1.24.4 venv）；本回填+[部署记录](../../verification/M2-SFX-GPU-EP-1/deploy-record.md)+[Handoff](../handoffs/M2-SFX-GPU-EP-1-zcode-20261006.md)；PROD-1 遗留边界闭合登记在部署记录 §5 |

**偏差与限制登记**：①venv 换装双实录（生产 venv T1.1.1-impl-py312 + m2ac5-build，各卸 CPU 包装 directml 1.24.4，`get_available_providers` DML 可用；无版本冲突，未 BLOCKED）；②回退语义的反向实证：换装前 CPU 包环境下真实权重单测自然走回退路径（ORT 警告+CPU 会话建成+绿，tests-ep-green.log warning 段）——无 GPU 机器行为可用性由此佐证；③EP 为 engine 级属性随首detect 缓存（provider 实例生命周期，与 conf_threshold 字段同级），env 更换 EP 需新实例/重启（代码注释+部署记录 §1.2 登记）；④GATE CS-Z3 计数含 runner 自身 python.exe（沿既有 runner 口径，sidecar 进程存活=0 为门条件）；⑤tauri build 行尾重写文件已按 README 纪律 checkout 还原。

**交付链**：`6d367d5c` claim → `725aeac4` test 先红 → `3867f3c4` AC1 实现+绿 → `016e1259` AC2/AC3 证据 → `36259aaf` AC4 spec+AC5b 回归 → `4fa38540` docs → r1 返修段（下）。

## r1 review-fix（DSH changes_requested：0×P0、1×P1、0×P2、3×P3、6×P4；报告由编排侧归档）

**P1-1（必闭，已闭）——回退审计在真实 ORT 下不可达+错值**：DSH 取证证明 onnxruntime 包装层 `InferenceSession.__init__` 自带 CPU 回退（`enable_fallback` 缺省 True，生产 wheel `onnxruntime_inference_collection.py:482,503-519,576-577`）：DML 初始化失败被包装层吞掉、以 CPU 会话**正常返回不抛异常**→初版 except 分支（异常驱动回退）在三真实场景（无 DX12/驱动坏/CPU-only wheel）不可达，且 `device` 错报 "dml"=静默降级+错值审计；初版 stub 直接 raise 验证了不存在的失败形态（单测绿=假绿）。

**修复（读回反推）**：构造后 `session.get_providers()` 反推 effective EP——请求 dml 而首 provider 非 `DmlExecutionProvider` = 包装层回退，写入三键审计（`device=cpu` + `sfx_ep=dml` + `sfx_ep_fallback="requested dml but onnxruntime built the session on CPUExecutionProvider (wrapper-level fallback/EP unavailable)"`）；except 分支降为防御兜底（逃逸出包装层的异常/禁回退构建），注释修正角色。**验证三矩阵**：①决定性验证 PASS——独立 venv `M2-SFX-GPU-EP-1-cpu-verify`（onnxruntime==1.30.0 CPU-only 包，进程内无 DML，=生产 venv 换装前状态）+生产代码原样 detect，三键实测 `sfx_ep='dml'/device='cpu'/sfx_ep_fallback=wrapper-level`（`raw/wrapper-fallback-cpu-wheel.{json,log}`）；②真实失败形态 stub 用例先红后绿——`test_engine_wrapper_level_cpu_fallback_gets_three_key_audit`（构造器不抛异常+无第二次构造+读回驱动；红证据 `raw/tests-p11-wrapper-fallback-red.log` 实证旧实现 device 错报 dml）；③原异常驱动用例保持绿（兜底分支）。EP 单测 98 passed（`raw/tests-p11-green.log`）。**初版证据误读已更正**（deploy-record §1.3）：tests-ep-green.log 的 ORT 警告是包装层内建回退的表现，非本仓 except 分支实证。

**应闭项（全闭）**：P3-1 deploy-record §7.2 frozen DML 声明改为「推断非实测」标注+缺口登记（GATE 25 场景 0 触 sfx/DML；DirectML.dll 实体在位只证加载路径；packaged sfx-detect 探针需命令面扩展=PROD-2 已知 NOT_RUN 缺口，不扩权）；P3-2 AC2 配对口径注记（位次 zip+索引对集合语义+重排风险极低）；P3-3 T5 对账注记（仅 v2b 可比 35/56+48/135；chiqui7 不可比；BJ 未做 GT 匹配只记 n_pred=5 与 TRAIN-V2 自洽）；P4-1 frontmatter base_commit 唯一化为 48e83a33；P4-2 体积数字补 `raw/bundle-sizes.log` Get-Item 级载体（NSIS 512,645,237 B、onedir 1,225,505,427 B、_internal/onnxruntime 66,170,520 B、delta 52,463,925 B=+50.03 MiB）；P4-4 暖引擎 env 不反映 options 注记（代码注释+deploy-record §1.2）；P4-5 Handoff delivery_head 落最终 hash；P4-3 device 键同名注（代码注释；无消费方，无功能破坏）。

**Gate 复验**：EP 单测先红（3c20e9f0）后绿（79056618）；AC2/AC3 脚本重跑绑定 `source_head=79056618`，verdict 与首轮完全一致（Δconf≤2e-06/Δxyxy≤0.0002px/gate_flips=0/matched 集全不变/run-to-run 稳定；AC3 directional 数字 KO DML 均值 1.211s/页 vs 首轮 1.106s/页=run 间波动如实双录，CPU 10.372 vs 10.447，BJ 0.064/0.206，`raw/gpu-ep-parity-perf-r2run.log`）；全量回归 **1823 passed+1 skipped+1 failed（test_catalog 既有）**=1822+1 新用例等量递增（`raw/pytest-full-regression-r2run.log`）；sidecar/tauri/GATE 重构建绑定返修后源码（`raw/{build-sidecar-r2run,tauri-build-r2run,gate-clean-start-e2e-r2run}.log`）。
