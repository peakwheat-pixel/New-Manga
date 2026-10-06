---
task_id: M2-SFX-GPU-EP-1
author: ZCode
recipient: Codex（集成）/ DeepSeek Harness（非作者 Review）
base_commit: 48e83a33（daa34e4e 之上的 release commit，含 T5-TILE-KO 落地终态）
delivery_head: 见 git log（AC4/AC5b 证据 commit `36259aaf` 之后为 docs commit）
status: delivered
---

# Handoff：M2-SFX-GPU-EP-1 — SFX 推理 EP 切换 GPU（DML）

## 交付结果

AC1-AC5 全 PASS。生产 SFX 推理从 `onnxruntime==1.30.0`（CPU 包）+硬编码
`CPUExecutionProvider` 切换为：

- **依赖**：`onnxruntime-directml==1.24.4`（PyPI directml 线顶点=1.24.4，
  即 T5 perf 实测 1.08s/页的 build；同一 import 名与 pyd 名，wheel 额外
  捆绑 DirectML.dll；`requirements-build.txt` VERBATIM 同步）；
- **EP 配置化**：`NEWMANGA_SFX_EP`（`dml` 默认=用户裁决 2026-10-06 |
  `cpu`=pre-GPU 行为原样），非法/空值 fail-fast ValueError 命名变量、
  detect 期每次读取、先于权重解析（T5 env 纪律）；EP 是 engine 级属性，
  随首次 detect 缓存至 provider 实例生命周期（与 conf_threshold 字段同级）；
- **DML 初始化失败语义（Owner 裁量并登记）**：自动回退 CPU EP +
  `device`（有效 EP）/`sfx_ep`（env 请求值）/`sfx_ep_fallback`（原因）
  三键审计进 detect options，绝不静默；显式 `cpu` 请求失败保持 typed
  `ProviderError` 无回退；回退只覆盖 init，run() 期失败维持既有 typed
  路径；EP 非供应链安全面——sha256 权重门仍先于任何 runtime import；
- **manga 面/contracts/apps 零 diff**；权重（v2b 944e8114）、tile 口径
  （T5 冻结）、conf 0.5 门零变化。

变更路径（全部在 Task 允许面内）：

- `requirements.txt`（仅 onnxruntime 行+注释）、
  `packaging/m2ac5/requirements-build.txt`（VERBATIM 同步行）、
  `packaging/m2ac5/core_sidecar.spec`（SFX_BINARY_IMPORTS + DirectML.dll）
- `src/infrastructure/providers/detection_sfx.py`（EP 常量段/`_ep_config`/
  `_EpProvenance`/`detect` fail-fast+options/`_engine_or_raise`/`_build_engine`）
- `tests/providers/test_detection_sfx.py`（+10 用例）、
  `tests/core/test_sfx_assembly.py`（+2 组合语义用例）
- `experiments/M2-SFX-GPU-EP-1/verify_gpu_ep_parity_perf.py`（AC2+AC3 脚本）
- `verification/M2-SFX-GPU-EP-1/**`（deploy-record.md + raw/*）
- `doc/tasks/M2-SFX-GPU-EP-1.md`（claim+交付记录回填）、本 Handoff

提交链（分支 `agent/zcode/M2-SFX-GPU-EP-1`，base `48e83a33`）：

1. `6d367d5c` claim（ready→owner_claim，用户裁决 2026-10-06「部署形态=GPU」）
2. `725aeac4` test 先红（EP 配置 8 用例，7 failed+1 passed 回归保护）
3. `3867f3c4` AC1 实现+AC5a 绿（97 passed；requirements 双文件+EP 配置化）
4. `016e1259` AC2/AC3 证据（双 EP 面逐页对比+性能+venv 换装 log）
5. `36259aaf` AC4 spec+AC5b 回归（闭包断言+GATE 证据链前置+回归+部署记录主体）
6. docs commit（Task 交付记录+Handoff+部署记录 §7 回填）

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC5a 先红 | `pytest tests/providers/test_detection_sfx.py -k "ep_config or ..."` | T1.1.1-impl-py312（当时仍 CPU 包）@ test commit | 红（7 failed） | `raw/tests-ep-red.log` |
| AC1/AC5a 绿 | `pytest tests/providers/test_detection_sfx.py tests/core/test_sfx_assembly.py` | 同 venv @ impl `3867f3c4` | PASS（97 passed，含真实权重单测） | `raw/tests-ep-green.log` |
| venv 换装 | pip uninstall onnxruntime + install onnxruntime-directml==1.24.4（生产 venv+m2ac5-build） | 两 venv | DML 可用（get_available_providers 含 DmlExecutionProvider） | `raw/venv-swap-{prod,m2ac5-build}.log` |
| AC2+AC3 双面对比 | `T1.1.1-impl-py312/Scripts/python.exe experiments/M2-SFX-GPU-EP-1/verify_gpu_ep_parity_perf.py` | directml 1.24.4 @ `016e1259`；v2b pin 原样；双面经生产 env 门 | **AC2：非逐位一致，max\|Δconf\|≤2e-06、max\|Δxyxy\|≤0.0002px、gate_flips=0、matched 集逐页全不变（KO 双 GT 口径）、GPU run-to-run 逐位稳定；AC3：KO DML 1.106s/页 vs CPU 10.447s/页（T5 呈报 1.08/10.46 复现），BJ 普通页 0.065s vs 0.203s** | `raw/gpu-ep-parity-perf.{json,log}` |
| AC5b 全量回归 | `pytest -q`（repo root） | directml 1.24.4 venv @ `36259aaf` | **1822 passed+1 skipped+1 failed（test_catalog 既有 BASELINE_FAILURE）=基线 1812+10 新测试吻合一致** | `raw/pytest-full-regression.log` |
| AC4 sidecar 构建 | `powershell -File packaging/m2ac5/build_sidecar.ps1 -Force` | m2ac5-build venv（directml）@ `016e1259` | EXIT=0；**构建期闭包断言 PASS**（…+`onnxruntime_pybind11_state.pyd, DirectML.dll`） | `raw/build-sidecar-dml.log` |
| AC4 NSIS | `npx --yes @tauri-apps/cli@2 build` | 同上 | EXIT=0 → **512,645,237 B / 488.90 MiB**（sha `61df0299…`）；vs T4 终态基线 438.86 MiB = **+50.04 MiB**（onedir `_internal/onnxruntime` 35.8MB→63.11MiB） | `raw/tauri-build.log` |
| AC4 GATE | `python packaging/m2ac5/run_clean_start_e2e.py` | dev venv + 本轮 NSIS 包 | **PASS 25/25（EXIT=0）**：python purged/install sha/四 exe/probe 13 场景/AC1 验收环 run1+run2/zero-touch Z1-Z4 | `raw/gate-clean-start-e2e.log` |

未运行/限制（如实）：①AC2 逐位一致性=**非逐位**（float32 求和顺序级漂移
1e-06 conf / 1e-4 px），按合同以量化数字+门/匹配零影响登记，非「基本一致」
式含糊；②BJ 普通页 n=2 directional 观测（本机未观察到小图 GPU 劣化，不外
推）；③EP 为 engine 级缓存属性，换 EP 需新 provider 实例/进程重启（代码注
释+部署记录 §1.2）；④GATE CS-Z3 计数含 runner 自身 python.exe（沿既有
runner 口径，门条件=sidecar 进程存活 0）；⑤tauri build 行尾重写文件已按
README 纪律 checkout 还原。

## 接收方式

- worktree：`G:/CODEX/New Manga.worktrees/M2-SFX-GPU-EP-1-zcode`，branch
  `agent/zcode/M2-SFX-GPU-EP-1`，base `48e83a33`，head=docs commit。
- 复现命令：见上表；数据路径（gitignored 外部树）与权重 sha 断言写死在
  `experiments/M2-SFX-GPU-EP-1/verify_gpu_ep_parity_perf.py` 头部。
- Reviewer（DSH 非作者）建议核查面：①`_ep_config` fail-fast 时序（先于权重
  解析的单测实证方式）与缓存语义登记；②DML 回退三键审计的完整性（`device`
  键从硬编码 "cpu" 改为有效 EP 的兼容面）；③AC2 diff_preds 排序配对口径
  （(-conf, xyxy) 双侧排序 zip）与 gate_flips 定义；④venv 换装对其它
  provider 的潜在影响面（onnxruntime 的 src 运行时消费方唯一=detection_sfx
  ——doctr 面走 torch、manga 面走 torch/transformers，均不 import
  onnxruntime；torch 面零触碰）；⑤GATE
  25/25 与包体积数字复核。

## 下一任务建议（必填）

- Task ID / 标题：M2-SFX-GPU-EP-1 r1 独立 Review（DSH 非作者，静态+证据复核）
- 推荐 Agent / Reviewer：DeepSeek Harness（Owner=ZCode 非作者隔离成立）
- 推荐原因与前置依赖：本 Task 已交付待审；依赖=本分支 docs commit head；无新
  授权需求。
- Recovery point：`G:/CODEX/New Manga.worktrees/M2-SFX-GPU-EP-1-zcode`，
  branch `agent/zcode/M2-SFX-GPU-EP-1`，base `48e83a33`，head=docs commit
  （见 Task frontmatter 回填）。
- 允许修改路径：`doc/reviews/M2-SFX-GPU-EP-1-<head>-dsh-r1.md`（新建）。
- 禁止范围与新增授权条件：零 src/零 tests 修改；结论写 review 文件，status
  变更与集成由 Codex 处置。
- 交付物：r1 review 报告（逐 AC 判定+证据抽查+P 级登记）。
- 验证命令、环境与完成 Gate：AC2/AC3 重跑约 2-3 分钟（脚本双面自动）；
  GATE 重跑需 NSIS 在位（本 worktree target 树已含，重装约 5-8 分钟）；
  Gate=逐 AC 判定完成+证据引用可复算。
