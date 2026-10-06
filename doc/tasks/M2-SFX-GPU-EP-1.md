---
id: M2-SFX-GPU-EP-1
title: "SFX 推理 EP 切换 GPU（DML）：onnxruntime-directml 依赖面+EP 配置化+数值一致性验证+打包闭包与 GATE 重跑"
kind: feature
status: ready
owner_claim: —
approval: user_ruling_2026-10-06_GPU（T5-TILE-KO 收口呈报的部署形态终选）
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
depends_on: [M2-SFX-T5-TILE-KO]
base_commit: daa34e4e
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
