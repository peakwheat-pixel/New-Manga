# M2-SFX-EPFAIL-AUDIT-1 部署记录 — SFX 推理 run-time EPFail 通道审计

Owner: ZCode @worktree `M2-SFX-EPFAIL-AUDIT-1-zcode`（base=d298ecd0）｜授权: user 2026-10-04 批准进行2（非阻塞候选①）｜Reviewer: DeepSeek Harness（非作者）

## 0. 背景与闭合声明

M2-SFX-GPU-EP-1（done @merge `931a6d03`）交付的「DML 失败回退 CPU 三键审计」只覆盖**会话构建**（构造后 `session.get_providers()` 读回反推一次）。其 deploy-record **§1.3（r2 N-P3-1 收窄）** 如实登记：ORT Python 包装层在 `run()` 期对 `EPFail` 另有**内部静默重跑 CPU**（wrapper `onnxruntime_inference_collection.py:278-305`，仅 stdout 两行提示），该 run-time 通道不在三键审计内，登记为「已知未审计通道/后续候选切片」。

**本 Task 闭合该登记**：GPU-EP-1 deploy-record §1.3 的「已知未审计通道」状态由本记录声明闭合（按 Task 合同以注记方式闭合，不改历史文件语义；历史文件零改动）。

机制实证（生产 venv onnxruntime-directml 1.24.4 = 生产 wheel，源码 `onnxruntime_inference_collection.py`）：

- `InferenceSession.run`（:291-305）捕获 `C.EPFail` → 若 `_enable_fallback`（默认 True）→ 两行 stdout `print` → `set_providers(self._fallback_providers)`（dml 请求的 fallback 列表 = `["CPUExecutionProvider"]`，:577）→ `disable_fallback()`（**每 session 只回退一次**）→ 以 CPU 重跑并**正常返回**——调用方无任何异常；
- stdout 提示不可依赖（GPU-EP-1 r2 N-P4-2：frozen 面 banner 走 stdout 会被 native 窗口丢弃）；
- 除包装层内部重试外，run() 失败维持既有 detect 期 typed 失败路径不变（重跑亦失败 / fallback 已禁用 / 非 EPFail 异常 → 异常传播，无 options 可写，语义与 GPU-EP-1 交付一致零变化）。

## 1. AC1 设计（Owner 设计裁量，实测前置）

### 1.1 设计实测前置（合同硬要求）

「逐 detect 复读 get_providers 代价高」是 GPU-EP-1 时的权衡判断、未附数字。本 Task 按合同先实测（`experiments/M2-SFX-EPFAIL-AUDIT-1/measure_get_providers_cost.py`，生产 venv + v2b 生产权重 pin 944e8114，证据 `raw/epfail-audit-get-providers-cost.{json,log}`）：

- **`get_providers()` 单次调用 ~0.03 μs**（口径=单次原语 `get_providers()` 调用，P4-6；r1 P2-1 后重跑值：CPU session 0.0297 μs / DML session 0.0304 μs，5 轮中位数，各 100 万次顺序调用）——wrapper :214-216 就是 `return self._providers`，**纯 Python 属性读，无 native 调用**；原「代价高」判断不成立；
- **run-time fallback 状态读回可见性**：在同一 DML session 上原样重放 wrapper EPFail 分支的 `set_providers(['CPUExecutionProvider'])` 调用（一次性 native 重建实测 0.117 s，非稳态项）后，`get_providers()` 从 `['DmlExecutionProvider', 'CPUExecutionProvider']`（DML 构建后真实读回形态）变为 `['CPUExecutionProvider']`——**公共 API 面即可观测**；
- **1% 硬门（r1 P2-1 口径修正后重跑）**：1% 预算 = 基准页时延的 1%（1.106 s × 1% = **11,060 μs**；前版误用整页微秒数 1,106,000 μs，差 100×）。稳态每页一次读回 = 0.0304 μs，两个占比并列：**页占比 = 0.0304 μs / 1,106,000 μs = 2.75e-6 %**；**1% 预算占比 = 0.0304 μs / 11,060 μs = 2.7486e-4 %**。PASS（`raw/epfail-audit-get-providers-cost.{json,log}` 为重跑再生证据，非手改）。

### 1.2 所选设计：稳态逐 detect 一次读回 + 条件性追加审计键

每次 `detect` 在 run 完成后、组装 options 前读回一次 `session.get_providers()`（`_runtime_ep_audit`）：

- 读回首 provider 名 == 构建期 effective 名（`_EpProvenance.effective` 经 `_EP_PROVIDER_NAMES` 反查）→ **稳态，零追加**（options 与审计前面形态逐字节一致）；
- 不一致 → 追加**单一新键** `sfx_ep_runtime_check`，值：`"session providers changed at run time: <built> -> <now> (ORT wrapper run-time EPFail fallback)"`（`<built>`/`<now>` 为 `dml`/`cpu` token 反查，未知名字按「审计值跟随运行时、绝不猜」纪律原样记录）；
- session 无 `get_providers` 面（裸测试替身）→ 跳过检查（真实 ORT session 恒有该面——构建期读回已调用过同一方法）——审计绝不成为新故障点。注（r1 P4-2）：「属性存在但不可调用」的形态（`session.get_providers` 存在却抛异常）**不兜底**——该形态在真实 ORT session 不命中（wrapper 的 `get_providers` 是无副作用属性读），兜底反而会吞掉真实的 session 状态异常。

覆盖面（对登记通道的两种形态）：

1. **静默成功主形态**（EPFail → set_providers → 重跑成功 → 正常返回）：读回在 run 之后 → **当页 options 即携带新键**；
2. **重跑亦失败**（typed 失败传播）：该页无 options（既有语义），但 providers 变更是 **session 状态、非逐页事件** → 下一页成功 detect 的读回即观测到并追加键。

### 1.3 硬约束核对

| 约束 | 结果 |
| --- | --- |
| 不依赖 stdout | PASS——探测面是公共 `get_providers()`，stdout 零参与 |
| 稳态每页时延增量 ≤1% | PASS——单次原语调用 0.0304 μs = 页占比 2.75e-6 %、1% 预算（11,060 μs）占比 2.7486e-4 %（§1.1 实测，r1 P2-1 口径修正后） |
| 三键（device/sfx_ep/sfx_ep_fallback）语义与写入时点不变 | PASS——仍为构建期 `_EpProvenance`（引擎构建后一次、随 engine 缓存），新键纯追加；真实稳态 parity 复核断言两 face 三键照常（§4.1） |
| `NEWMANGA_SFX_EP` 解析与 fail-fast 时序不变 | PASS——`_ep_config()` 零改动，detect 入口 fail-fast 位置零改动 |
| run() 失败既有 typed 路径不变 | PASS——`_sfx_boxes`/`_detect_tiles` 的 run 调用零改动 |

### 1.4 落选设计及理由（登记）

- **(a) 纯异常/typed 失败触发的条件性读回**：无法覆盖静默成功主形态——wrapper 吞掉 `EPFail` 后正常返回，调用方零异常信号；「静默重跑 CPU 且页结果正常」恰是 §1.3 登记的通道本体。异常触发式只兜到重跑亦失败的少数形态。（本设计天然包含该面：读回在成功/失败两形态下都观测 providers 变化，无需单独的异常钩子。）
- **(b) 低频采样读回（每 N 页，env 可配）**：在 0.03 μs 实测下无必要——采样窗口内（第 k 页切换、k+1..k+N-1 页审计仍显旧状态）反而弱于逐页读回，且引入新 env 常量/config 面（冻结面无谓扩张）与默认值代价测算负担。
- **(c) 会话级私有属性探测**（`_enable_fallback`/`_providers`）：可达但依赖 wrapper 私有面（wheel 升级脆弱），公共 `get_providers()` 已暴露同一信息。

## 2. AC2 单测先红后绿 — PASS

证据：`raw/tests-epfail-red.log`（红）+ `raw/tests-epfail-green.log`（绿）。三用例（stub 注入 wrapper 形态，`tests/providers/test_detection_sfx.py` EP 段）：

1. `test_runtime_epfail_silent_rerun_gets_runtime_audit_key`——静默成功主形态：构建后 DML session（读回 `[Dml, CPU]` = 实测真实形态）首次 run 触发 wrapper 内部 fallback（providers 翻转 `[CPU]`、重跑成功、调用方零异常）；断言当页 `sfx_ep_runtime_check`（dml -> cpu 精确文案）+ 三键构建期语义不变（device/sfx_ep=dml、无 sfx_ep_fallback）+ 第二页键持续可见（session 状态非逐页事件）；
2. `test_runtime_steady_state_adds_no_runtime_key`——稳态零变化（无新键，AC3 等量递增的构造前提）；
3. `test_runtime_audit_skips_sessions_without_readback_face`——无读回面的裸测试替身跳过检查（三键照写）。

- **红**：对基线 claim `a336bd41` 跑新测试 = `1 failed, 3 passed`——唯一 failed 即核心测试 `KeyError: 'sfx_ep_runtime_check'`（基线无 run-time 审计）；3 passed = 2 条新辅助用例 + 1 条被 `-k runtime` 选中的既有用例（`test_hash_mismatch_fails_before_any_runtime_import`，名字含 "runtime" 被过滤器带入，r1 P3-2 精确化叙述）；
- **绿**：对 impl `0f4702d0` = 新用例 `4 passed`，全文件 `82 passed`（79 基线 + 3 新增）。

绿 log 注（r1 P4-5，不重生成既有证据）：`raw/tests-epfail-green.log` 中的 `EXIT_K Runtime=0` 字样是 shell echo 标签排版歧义——含义为「`-k runtime` 选择的用例集 EXIT=0」（写脚本时把标签写成了 `EXIT_K Runtime`），其下「# full file:」段与 `EXIT_FULL=0` 才是全文件跑的落点。

## 3. 供应链与禁改面 — 零变化

- SHA-256 权重门顺序（1.EP env → 2.文件存在 → 3.sha → 4.import → 5.session → 6.metadata 断言）零改动；EP 非 pin 对象，读回不触碰权重面；
- `contracts/**`、`apps/**`、`packaging/**`、`requirements.txt`、其他 provider、`doc/STATUS.md`/`doc/REBASELINE_PLAN.md` 零 diff（交付链 commit 只含允许路径：`src/infrastructure/providers/detection_sfx.py`、`tests/providers/test_detection_sfx.py`、`experiments/M2-SFX-EPFAIL-AUDIT-1/**`、`verification/M2-SFX-EPFAIL-AUDIT-1/**`、`doc/tasks/`、`doc/handoffs/`）。

## 4. AC3 数值与回归 — PASS

### 4.1 parity 抽 1 页复核（KO pre-k01，690x62133，tile 路由）

证据：`raw/epfail-audit-parity-prek01.{json,log}`（`experiments/M2-SFX-EPFAIL-AUDIT-1/verify_epfail_audit_parity.py`，沿用 GPU-EP-1 `verify_gpu_ep_parity_perf.py` 形态：双 EP face 走生产 env 门、diff_preds/match_gt verbatim、warmup+timed 协议）：

| 指标 | GPU-EP-1 基准行 | 本 Task 复跑 | 判定 |
| --- | --- | --- | --- |
| n_pred cpu/gpu | 23 / 23 | 23 / 23 | 一致 |
| max_abs_dconf | 1e-06 | 1e-06 | 逐数字一致 |
| max_abs_dxyxy_px | 0.0001 | 0.0001 | 逐数字一致 |
| gate_flips | 0 | 0 | 一致 |
| matched derived | 2/2 -> 2/2 set equal | 2/2 -> 2/2 set equal | 一致 |
| matched npd | 5/48 -> 5/48 set equal | 5/48 -> 5/48 set equal | 一致 |
| 审计稳态 | （无此面） | 两 face 零 `sfx_ep_runtime_check`、三键照常（device/sfx_ep=cpu/dml 各自、无 fallback 键） | PASS |

perf（directional，如实登记）：dml wall 1.122 s（provider_ms 1118）落 GPU-EP-1 `perf_ko.dml` 区间（min 0.333 / mean 1.211 / max 2.325 s）；cpu wall 11.299 s。**GPU vs CPU 漂移量级结论不因本 Task 变化。**

### 4.2 全量回归

`raw/pytest-full-regression.log`（worktree 根，生产 venv，HEAD=`0afb22dd`）：

```
1 failed, 1826 passed, 1 skipped, 1 warning in 144.69s
```

= 基线 1823 passed + 本 Task 新增 3 passed + 1 skipped + 唯一 failed=`tests/m2_test_assets/test_catalog.py::test_manifest_has_unique_cases_and_exact_taxonomy`（既有 BASELINE_FAILURE）。**等量递增成立。**

r1 review-fix 后全量回归（`raw/pytest-full-regression-r1fix.log`，HEAD=`2356fb8f`，P1-1 透传+2 新用例落地后）：

```
1 failed, 1828 passed, 1 skipped, 1 warning in 124.74s
```

= 基线 1823 + 首轮 3 + 返修 2 = **1828 passed** + 1 skipped + 同一 test_catalog 既有 failed。**等量递增维持。**

## 2r. r1 review-fix 补充（composite 透传 + 形态 2 钉子）

DSH r1 P1-1（composite `MangaSfxParallelDetectionProvider.detect` 未透传 run-time 审计键，编排裁决采透传方案 (a)）+ P3-1（形态 2 钉子），返修后补 2 用例（`raw/tests-epfail-r1fix-red.log` 红 + `raw/tests-epfail-r1fix-green.log` 绿）：

1. `test_composite_passes_through_runtime_epfail_audit_key`——静默回退 stub 页 → composite 输出携带 `sfx_ep_runtime_check`（值原样透传）+ 只透传该键（`sfx_ep`/`sfx_ep_fallback` 不出现、`device` 仍=primary 的同名键原样，不透传面 DSH r1 提醒成立）；
2. `test_runtime_epfail_retry_failure_page_then_next_success_observes_key`——P3-1 形态 2 钉子：同 provider 实例首次 run 触发 wrapper fallback（providers 已翻转，wrapper :301→:621）且 CPU 重跑仍失败 → 当页异常传播无 options；同实例第二次 detect 成功页 options 出现新键（session 状态持久）。

- **红**：对 cf013b01（P1-1 修复前）= `1 failed, 1 passed`——failed=composite 透传用例（`KeyError`，缺口实证）；形态 2 钉子按构造绿（钉的是已交付的 sfx 级 session 状态行为，回归钉非新行为，红形态如实登记）；
- **绿**：对修复 commit `6c2825ce` = 新用例 `2 passed` + 全文件 `84 passed`（82+2）+ `tests/core/test_sfx_assembly.py 19 passed`（既有 composite/assembly 用例零破坏）。

## 5. 已知限制

1. `sfx_ep_runtime_check` 观测的是「session providers 列表相对构建期发生变化」，归因「wrapper run-time EPFail fallback」基于：本仓代码从不调用 `set_providers`，而 wrapper 仅在 run() EPFail 分支调用它（同 wheel 版本内成立；wheel 升级需复核 wrapper 行为，属既有 EP 语义的同一复核面）。
2. wrapper fallback 每 session 只触发一次（`disable_fallback`）；第二次 EPFail 将异常传播（ORT `RuntimeError` 族）→ composite 只捕 `ProviderError`，该异常最终由 pipeline 层归为通用 `STEP_FAILED`（非 typed provider 错误码；行为与 GPU-EP-1 交付逐字节一致——r2 P4-4 措辞精确化：本文与其余交付文档的「typed 失败路径」应读作「既有失败路径」，映射口径以本条为准）。
3. 审计读回对「providers 列表为空」返回稳态（不追加键）——真实 ORT session 列表恒非空（至少含 CPU），该分支仅为测试替身形态兜底。
4. run-time 通道的实机 EPFail（真实 GPU 掉卡）未在本 Task 触发（NOT_RUN）——探测面可见性由「wrapper 同 API 调用重放 + stub 形态单测」覆盖；与 GPU-EP-1 验证矩阵②同一诚实口径。
5. GPU-EP-1 deploy-record §1.3 历史文件零改动；闭合声明仅存于本记录 §0。
6. 形态 2（重跑失败→下一成功页观测）的前提=同一进程/同一装配实例的后续 detect：失败单元的剩余 unit 会被取消、进程/装配重建则 session 态丢失——无后续成功 detect 时该归因不落盘（丢的仅是「归因到 EP 回退」一条，页本身仍用户可见硬失败）（r2 残留风险②登记）。
7. composite 每页新增一次 `dict(sfx_result.options)` 拷贝（μs 量级，≪1% 预算 11,060μs）——可忽略，如实登记（r2 残留风险③）。

## 6. 交付链

| commit | 内容 |
| --- | --- |
| `a336bd41` | claim：Owner claim base=d298ecd0（status→owner_claim） |
| `0f4702d0` | impl：`_runtime_ep_audit` + detect options 追加点 + EP 段注释闭合登记 |
| `0afb22dd` | test：3 用例 + 红/绿证据 log 入 verification/raw/ |
| `2bed03d0` | verify：实测/parity/回归证据 + experiments 脚本 + 本部署记录 |
| `cf013b01` | docs：Task 回填（status=in_review）+ Handoff |
| `6c2825ce` | r1 review-fix P1-1(+P4-3)：composite tail options 条件性透传 + wheel 升级复核面注释 |
| `2356fb8f` | r1 review-fix P1-1/P3-1 test：composite 透传用例+形态 2 钉子，红绿证据 raw/ |
| `22ea8a09` | r1 review-fix P2-1(+P4-7/P4-8)：1% 预算口径修正+微基准重跑（JSON/log 再生）+脚本注释 |
| `9db9a8ad` | r1 review-fix P2-1/P3-2/P4-1/P4-2/P4-5/P4-6：文档同步 + 全量回归 r1fix log |
| `d388a7bf` | r1 review-fix P4-1：base_commit 双值注记行补右括号（frontmatter 格式完整性） |

NOT_RUN 清单：实机真实 EPFail 触发（§5.4）；其余 AC 全部有证据。
