> 【集成轮落盘注记】本报告为 DSH r2（非作者，只读，静态）复核原文，由集成方自 headless 会话输出原样落盘；审查对象 head=cdc2305c，Verdict=approved_with_conditions 建议集成（r1 条件 9/9 实质闭合，新发现 N-P3-1+5×N-P4 全为登记/措辞级）。集成方随后在本分支顺笔闭合全部文档级条件（fbb5b7f4：N-P3-1 回退覆盖面收窄+run-time EPFail 未审计通道登记、N-P4-1 delivery_head↔tip 映射、N-P4-2 banner 载体更正+断言句并入修订段、N-P4-3 §2 载体指针、N-P4-4 三形态矩阵标注、N-P4-5 头部状态+pycache 清理；src 仅注释零行为变更，两文件 EP 单测 98/98 复核绿）。集成 Gate 实测（shell）：src 面仅 detection_sfx.py、contracts/apps 零 diff、44 文件全在允许路径、worktree clean、全量回归 1823+1sk+1 failed（test_catalog 既有登记）。

# M2-SFX-GPU-EP-1 r2 独立复核报告（DSH，非作者，只读）

## ① 前置声明

**角色与边界**：本会话为 DSH 非作者 Reviewer，r2 复核轮，**全程只读**，未新建/修改任何文件（含 Handoff 建议的 `doc/reviews/…-dsh-r2.md`，按本次指令直接输出报告全文；归档由集成侧处置）。

**可核与不可核**：
- 本 worktree 内 **pwsh 不可用**（3 次尝试均 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`，升级 `danger-full-access` 因无审批通道被拒）。**因此无法执行任何 Git 级核验**：`git diff/status/log/diff --name-status`、contracts/apps 零 diff、worktree clean、"相对 base 零 diff" 均**未能由我独立重算**。
- 作为替代，我核了 **reflog 原文**（`G:/CODEX/New Manga/.git/worktrees/M2-SFX-GPU-EP-1-zcode/logs/HEAD`，15 行）、**生产/验证 venv 的 onnxruntime wheel 源码与 METADATA**、以及全部 `verification/**` 载体与源码本体。commit 链哈希因此可确认（见下）。
- **运行级声称**（pytest 全量、GATE、tauri/build 实际执行、GPU/CPU 实测时延）按「作者声称 + 静态一致性」采信并逐条标注。运行在 worktree 外 venv 的进程行为我未重跑。
- r1 报告原文不在本分支（`doc/reviews/M2-SFX-GPU-EP-1*` 无文件），我按 Task §「r1 review-fix」的复述与本次 r2 清单条目核对。

**已确认的 commit 链（reflog 实证，非声称）**：
`48e83a33`(base) → `6d367d5c` → `725aeac4` → `3867f3c4` → `016e1259` → `36259aaf` → `b1ddd114`(amend→`4fa38540`) → `3c20e9f0` → `79056618` → `29078d40` → `e921b913` → `1e9f2324` → `cdc2305c`(tip，docs)。与清单完全一致。

---

## ② Verdict

**approved_with_conditions**
**r1 条件闭合度：9/9 条目均已按实质闭合**（0×P0、0×P1、0×P2 残余）；新增发现 **1×P3、5×P4**，全部为**登记/措辞/载体精度级**，无一需要重跑 Gate 或改动 src 行为逻辑。

| 级别 | 数量 | 内容 |
|---|---|---|
| P0/P1/P2 | 0 | r1 唯一 P1（回退审计不可达+错值）已决定性闭合 |
| P3（新） | 1 | ORT **run() 期 EPFail 内部回退**不在 init 读回审计覆盖内；「回退只覆盖 init」表述不精确（N-P3-1） |
| P4（新/差注） | 5 | Handoff delivery_head 期望值不符（N-P4-1）、§1.3「stderr EP Error banner」未被决定性 log 佐证（N-P4-2）、parity json 被 r2run 覆盖而 §2/§3 未加指针（N-P4-3）、三形态矩阵缺「directml wheel + 真无 DX12 设备」实机跑（N-P4-4）、deploy-record 头部状态行过期+3 份 r2run 日志缺命令头/EXIT（N-P4-5） |

**不判 changes_requested 的理由**：r1 的 P1 已闭；P3/P4 均不需返工重跑（N-P3-1 只需登记/收窄措辞，N-P4-* 只需文档一行级修正），且交付体本身可直接集成。

---

## ③ 逐条核对表

| # | 核对项 | 判定 | 关键证据 |
|---|---|---|---|
| 1 | P1-1 修复本体（读回反推/兜底角色/反查表/三键方向） | **通过** | `src/infrastructure/providers/detection_sfx.py:443-445, :893-964, :729-735` |
| 2 | 决定性验证（CPU-only wheel 实机 + 三键 + 警告原样入 log） | **通过** | `raw/wrapper-fallback-cpu-wheel.{json,log}`；venv METADATA 实测 1.30.0 |
| 3 | stub 用例（真实非 raise 形态；先红后绿） | **通过** | `tests/providers/test_detection_sfx.py:1434-1495`；`raw/tests-p11-wrapper-fallback-red.log`、`raw/tests-p11-green.log` |
| 4 | r1 误读更正（§1.3） | **通过** | `deploy-record.md:64-112`（:109-112 明写「误读」） |
| 5 | P3-1 frozen DML 改推断+缺口登记 | **通过**（附差注） | `deploy-record.md:276-284`；差注见 N-P4-2/§5 注 |
| 6 | P3-2 AC2 口径注记；P3-3 T5 对账口径注记 | **通过** | `deploy-record.md:154-159`；`:161-165` |
| 7 | P4-1 base 唯一化 / P4-2 载体 / P4-3 device 键同名注 / P4-4 暖引擎注 / P4-5 delivery_head | **全部通过**（P4-5 附差注 N-P4-1） | Task `:14`；Handoff `:5`；`raw/bundle-sizes.log`；代码 `:404-407`、`:421-425`；Handoff `:6` |
| 8 | Gate 复验证据（回归/AC2-3/build/tauri/GATE/M2-AC5 还原） | **通过**（静态可核部分） | 5 份 r2run log + `bundle-sizes.log` + `m2ac5-gate-artifacts-r2run/cleanstart-gate.json` |
| 9 | 返修面纪律（路径/contracts-apps/「显著」/clean） | **通过（静态）**；Git 级与 clean 未独立验证 | 全域 grep 枚举 + `.gitignore`；见 ⑨ 详述 |

### 1) P1-1 修复本体 —— 通过

- **读回反推**：`_build_engine` 在构造成功分支（`else`，:935-964）读 `session.get_providers()`；首 provider ≠ 请求 provider 即写 `_EpProvenance(requested=ep_mode, effective=反查值, fallback_reason=...)`，否则 `effective=requested`。空列表退化为请求值（:948-950），不误报。
- **反查表**：`:443-445` `_EP_MODE_BY_PROVIDER_NAME`（`DmlExecutionProvider→dml`、`CPUExecutionProvider→cpu`），未知名原样记录（:956-958），符合「审计值随 runtime 不臆测」。
- **三键方向**：`detect` 的 options 为 `("device", ep_prov.effective)` / `("sfx_ep", ep_prov.requested)` / 条件性 `sfx_ep_fallback`（:729-735），即 **device=实际、sfx_ep=请求、sfx_ep_fallback=原因**，与 r1 要求一致。
- **except 降级为防御兜底**：`:899-934` 保留显式 CPU 重建，但注释（:908-915）明确「**通常 wrapper 自己处理并正常返回**，此分支只在异常逃逸包装层/禁回退构建时触发」；显式 `cpu` 失败仍 typed（:900-907）。
- **机制前提经我独立复核为真**（这是 r1 P1 的事实基础）：
  - 生产 venv `T1.1.1-impl-py312`（= directml 1.24.4，`raw/venv-swap-prod.log`）= `onnxruntime/capi/onnxruntime_inference_collection.py:482` `super().__init__(enable_fallback=int(kwargs.get("enable_fallback",1))==1)`；`:503-519` `except (ValueError, RuntimeError)` → `_create_inference_session(self._fallback_providers, None)` → `return`（不抛）；`:556-577` 对 DML-only 环境 `_fallback_providers=["CPUExecutionProvider"]`。**r1 引用的行号 482/503-519/576-577 与该 wheel 逐行吻合**（部署记录 §1.3 的引用可追溯、无误）。
  - 决定性 venv `M2-SFX-GPU-EP-1-cpu-verify`（METADATA 实测 `Version: 1.30.0`）同样是 `disable_fallback` 前正常返回的构造语义。
- 旁证：`device` 键无消费方——`src/**` 内除 SFX 自身外仅 `detection_manga.py:404`、`detection_doctr.py:130`（torch device，另一 provider 的 options）与 inpaint/device manager；`apps/**` 对 `sfx_ep|"device"` **零命中**，P4-3「无消费方」成立。

### 2) 决定性验证 —— 通过

- `raw/wrapper-fallback-cpu-wheel.log`：`onnxruntime 1.30.0`、`available_providers=['AzureExecutionProvider','CPUExecutionProvider']`（**确无 DML**）、v2b sha `944e8114`（生产 pin）、随后 `detect OK route=letterbox` 且三键 = `sfx_ep='dml'/device='cpu'/sfx_ep_fallback='requested dml but onnxruntime built the session on CPUExecutionProvider (wrapper-level fallback/EP unavailable)'`，`VERDICT: PASS`，`EXIT=0`。
- **ORT 警告原样入 log ✓**：`:5-6` 完整保留 `…\M2-SFX-GPU-EP-1-cpu-verify\Lib\site-packages\onnxruntime\capi\onnxruntime_inference_collection.py:197: UserWarning: Specified provider 'DmlExecutionProvider' is not in available provider names.Available providers: 'AzureExecutionProvider, CPUExecutionProvider'`；我核对该 wheel `:195-201` 原文逐字一致。
- 脚本（`experiments/M2-SFX-GPU-EP-1/verify_wrapper_fallback_cpu_wheel.py`）**确为生产代码原样**：`sys.path` 注入 `src` 后 `from infrastructure.providers.detection_sfx import SfxDetectionProvider`（:82）、不设 `NEWMANGA_SFX_EP`（默认 dml）、并前置断言 `DmlExecutionProvider not in available`（:73-76）与权重 pin（:78-79）。json 的 `checks` 四项与脚本一致。
- 未独立验证项：该 venv 的实际执行过程（我只核了 wheel/venv 静态事实与产物自洽）。

### 3) stub 用例 —— 通过

- 形态**正确**（非 raise）：`_WrapperFallbackSession.__init__` 只记录 providers、从不抛（:1462-1463）；`get_providers()` 返回 `['CPUExecutionProvider']`（:1468-1471）；`run()` 返回零输出。断言 `calls["providers"] == [["DmlExecutionProvider"]]`（:1489）**钉死「只有一次构造」**，正是「包装层自吞、无第二次构造」的真实形态。
- **先红实证**：`raw/tests-p11-wrapper-fallback-red.log:66-72` 失败点 `assert options["device"] == "cpu"` → `AssertionError: assert 'dml' == 'cpu'`，即**旧实现的 device 错报**；:75 仅 1 failed、`EXIT=1`。旧 stub（`_FakeSession`）也已补 `get_providers` 模拟正常构造（`test_detection_sfx.py:324-331`），旧用例 `test_engine_dml_failure_falls_back_to_cpu_with_audit`（:1387-1409，raise 形态）保留为**兜底分支**钉子，语义分工清晰。
- **后绿**：`raw/tests-p11-green.log` `98 passed in 3.70s / EXIT=0`，相对首轮 97 passed = +1 个新用例，与全量回归 +1 等量递增自洽。载体弱点见 N-P4-5（该 log 无命令头/测试清单行）。

### 4) r1 误读更正 —— 通过

`deploy-record.md:64` 标题即含「r1 P1-1 机制更正后终版」；`:68-78` 重写机制；`:109-112` 明确写「初版报告把 tests-ep-green.log 的 ORT 警告当『本仓 except 回退路径的反向实证』——**误读**……当时无任何 `sfx_ep_fallback` 观测」。Task `:66` 同步。**更正如实、未留旧断言冒充。**

### 5) P3-1 —— 通过（附差注）

`deploy-record.md:276-284` 已把 frozen 面 DML 改为「**推断，不是实测**」：明示 GATE 25 场景**全部不触及 sfx 检测/DML**（probe=资源通道、AC1 环=mock ocr/translate），DirectML.dll 实体在位「只证明加载路径成立，不构成 frozen 进程内 DML 推理的运行证据」，packaged sfx-detect 探针属 M2-PROD-DETECT-2 已知 NOT_RUN 结构缺口、需 Codex 立契约、本 Task 不扩权。**缺口登记完整。**
差注：同节上方 `:262-265` 仍以断言语气写「frozen sfx detect 链在无 env 干预下默认走 DML」，与下方修订并存（结论以修订段为准）。建议并入 N-P4-2 一并顺笔。

### 6) P3-2 / P3-3 —— 通过

- P3-2：`deploy-record.md:154-159` 写清「位次 zip」配对口径 + 「matched 集不变」严格语义应为**索引对（gt_index, pred_index）集合相等**，并自曝「GPU 面 `bit_identical=false` 下微重排使索引集不等同于同一物理框，跨面最近邻 IoU 复核未做，留作可选强化」。
- P3-3：`:161-165` 明确对账**仅 v2b 可比**（derived 35/56、npd 48/135 与 T5 逐位吻合）；chiqui7 56/56+41/135 属另一权重、不可比；BJ **未做 GT 匹配**，只记 n_pred=5 与 TRAIN-V2 的 v2b BJ 5/5@0.5 自洽。

### 7) P4-1…P4-5 —— 全部通过（P4-5 附差注）

- **P4-1 ✓**：Task frontmatter `base_commit: 48e83a33`（`:14`）与 `owner_claim`（`:6`）统一，Handoff `base_commit: 48e83a33`（`:5`）；reflog 首条即 `reset: moving to 48e83a338ff4…`，base 唯一化成立。
- **P4-2 ✓**：`raw/bundle-sizes.log` 载体在位，且与 Task/记录数字逐值吻合：NSIS 首轮 `512645237 B / 488.9 MiB (61df0299…)`、onedir `1225505427 B`、`_internal/onnxruntime 66170520 B`、`DirectML.dll 18527776 B`、baseline `460181312 B`、delta `52463925 B / 50.03 MiB`，末两行补 r2run `512675022 B / 488.93 MiB (4c9ef883…)`、delta `52493710 B / 50.06 MiB`。（载体为**汇总型**日志，非逐行 `Get-Item` 原文——内容满足「实测载体」意图，形式差注见 N-P4-5。）
- **P4-3 ✓**：代码 `:404-407` 明写「`device` 是 SFX 的 **EXECUTION-PROVIDER** 键，与 manga/doctr 的 torch-device `device` 同名但记录 onnxruntime provider；src/ 与 apps/ 无分支消费」。我的全域 grep 支持该断言。
- **P4-4 ✓**：代码 `:415-425` 写清 EP 为 engine 级、随首 detect 缓存，「fail-fast 只守 env 合法性、**不重解析引擎**，暖引擎下后续 env 变更不反映进 options」；`deploy-record §1.2:54-59` 同步登记。
- **P4-5 —— 通过（差注 N-P4-1）**：Handoff `:6` `delivery_head: 1e9f2324（最终证据锚……其后 docs commit 仅文档）`。**已落具体 hash、不再悬空**，符合 r1「落最终 hash」的原意与自指约束（承载该 frontmatter 的提交本身无法写自己的 hash）；但与本轮清单期望值 `cdc2305c`（tip）**字面不一致**——见 N-P4-1。

### 8) Gate 复验证据 —— 通过（静态可核部分）

| 项 | 判定 | 证据（逐值核对） |
|---|---|---|
| 全量回归 | ✓ | `raw/pytest-full-regression-r2run.log:399` `1 failed, 1823 passed, 1 skipped`（`PYTEST_EXIT=1`），唯一失败 `tests/m2_test_assets/test_catalog.py::test_manifest_has_unique_cases_and_exact_taxonomy`（`assert 122 == 97`）= 首轮 `pytest-full-regression.log:399` 同一既有失败；**1822 → 1823 passed = +1 与新增 1 用例等量递增，无其它回归** |
| AC2/AC3 重跑 | ✓ | `raw/gpu-ep-parity-perf-r2run.log:2` `source HEAD 79056618…`（绑定修复 commit）；`:4` `onnxruntime 1.24.4 providers=['Dml','CPU']`；逐页 Δconf/Δxyxy/gate_flips/matched set_eq 与首轮**逐值相同**；verdict 行完全一致（`gate_flips_total: 0`、`ko_all_matched_sets_equal: true`、`gpu_run_to_run_all_bit_stable: true`） |
| AC3 波动双录 | ✓ | r2run KO DML 均值 `(1.069+2.325+1.116+0.333)/4 = 1.211 s/页`、CPU `10.372`、BJ `0.064/0.206`，与 Task `:70`/Handoff `:73` 的「1.211 vs 首轮 1.106 / CPU 10.372 vs 10.447」一致；首轮数字见 `gpu-ep-parity-perf.log`（1.106/10.447）——run 间波动**如实双录** |
| sidecar 重构建 | ✓ | `raw/build-sidecar-r2run.log:1` `HEAD=790566180ff1…`；`:417` 闭包断言含 `onnxruntime_pybind11_state.pyd, DirectML.dll`；`:422` `OK (HEAD=79056618…)` |
| tauri/NSIS | ✓ | `raw/tauri-build-r2run.log:67-69` `Finished 1 bundle … (488.93 MiB)`（= 512,675,022 B）；`bundle-sizes.log:8` sha `4c9ef883e1f8…` |
| GATE 重跑 | ✓ | `raw/gate-clean-start-e2e-r2run.log` 共 **25 行 `[PASS]`**（CS-E1/E2/E3、I1/I2、L1-L3、P1-P3、A1×2/A2-A5、R1-R4、Z1/Z4/Z2/Z3）、`:4` CS-E2 sha `4c9ef883…`、`:47` `GATE: PASS`、`:48 CHAIN_EXIT=0`；快照 `raw/m2ac5-gate-artifacts-r2run/cleanstart-gate.json:12` `verdict: PASS`、`:4` sha 同 |
| M2-AC5 落点还原 | ✓（内容级） | 直接读 `verification/M2-AC5/raw/` 与主仓同名文件对比：`cleanstart-gate.json` 为 M2-AC5 时代内容（`M2-AC5-zcode` 工作树、sha `5410e29e…`、lab `m2ac5-cleanstart-r3u1k_ci`）；全域 grep `M2-SFX-GPU-EP-1|4c9ef883` 在该目录 **0 命中** → 未被 r2run 污染。reflog `e921b913`/`1e9f2324` 亦记载「被 29078d40 的 `git add -A` 入库后还原」。**「相对 base 零 diff」我无法用 Git 重算**（shell 不可用），仅内容级佐证 |

### 9) 返修面纪律 —— 静态通过，Git 级未独立验证

- **路径面**：我对全域出现 `NEWMANGA_SFX_EP|onnxruntime-directml` 的文件做了枚举，本 Task 触碰面 = `requirements.txt:30-45`、`packaging/m2ac5/requirements-build.txt:52-59`、`packaging/m2ac5/core_sidecar.spec:113-125`、`src/infrastructure/providers/detection_sfx.py`、`tests/providers/test_detection_sfx.py`、`tests/core/test_sfx_assembly.py`、`experiments/M2-SFX-GPU-EP-1/**`、`verification/M2-SFX-GPU-EP-1/**`、`doc/tasks/M2-SFX-GPU-EP-1.md`、`doc/handoffs/M2-SFX-GPU-EP-1-zcode-20261006.md` —— 全部在 Task `:39` 允许面（含 `experiments/M2-SFX-GPU-EP-1/**`）内；其余命中均为其它历史 Task 文件（T5/TRAIN/STATUS/PLAN）。
- **contracts/apps 零 diff**：我无法 diff 校验；旁证=提交信息+Task 声明、且 apps/ 内无任何 SFX EP 引用（grep 0 命中）、`ports/detection` 未出现在触碰面。
- **「显著」纪律 ✓**：全域 grep「显著」在本 Task 全部交付物中**仅出现在禁用声明句**（Task `:43`、`deploy-record.md:180,219`、`gpu-ep-parity-perf.json:191`、脚本 `:317`），无一处用于证据描述。
- **worktree clean 未独立验证**：`apps/desktop/src-tauri/target/`（构建产物、NSIS 在内）与 `experiments/.../__pycache__/*.pyc` 均在 `.gitignore`（`apps/desktop/.gitignore:1`、根 `:1-2`）覆盖下，不构成 Git 级 dirty；`git status` 未能执行。

---

## 新发现（不构成 r1 条件未闭，均为登记/措辞级）

**N-P3-1（P3）ORT run() 期 EPFail 内部回退不在审计内，「回退只覆盖 init」表述不精确。**
生产 wheel `T1.1.1-impl-py312/.../onnxruntime_inference_collection.py:278-305`（`InferenceSession.run`，即本 provider `_sfx_boxes` 调用的入口）与 `:366-376`（`run_with_ort_values`）在捕获 `C.EPFail` 且 `_enable_fallback=True` 时，会 `set_providers(self._fallback_providers)` 并**静默重跑到 CPU**（仅 `print` 两行到 stdout）。本 provider 的三键只在**构造期**读回一次（`detection_sfx.py:947-964` → options `:729-735`），因此该形态下 `device` 仍报 `dml`。Task `:52`/`deploy-record.md:86-87`/代码 `:411-413` 的「回退只覆盖 init，run() 失败维持既有 typed 路径」对 EPFail 不成立。**影响面**：结果仍正确（CPU 执行成功）、可用性不受损、ORT 有 banner（非全静默），故不回到 P1；但「绝不错值审计」的契约在 run-time 通道有缺口。**建议（不阻塞集成）**：把该句收窄为「本仓回退逻辑只覆盖 init；ORT 包装层另有 run-time EPFail 内部回退，属已知未审计通道」，或登记为后续切片（run 后复读 `get_providers()` 代价高，需权衡）。

**N-P4-1（P4）Handoff `delivery_head=1e9f2324`，与本轮清单期望 `cdc2305c`（tip）字面不符。**
`doc/handoffs/…:6` 写 `delivery_head: 1e9f2324（最终证据锚…；其后 docs commit 仅文档）`；reflog 末条（`cdc2305c`）正是更新该值为 `1e9f2324` 的 docs 提交——**承载 frontmatter 的提交无法自指**，取「末个证据锚」是合规解；但 r1 条件若按「= tip」验收则未字面满足。**建议**：集成时在 Handoff/§7.3 落一行 `tip=cdc2305c（delivery_head→tip 映射）`，或由 Owner 在集成前 amend；非返修事项。

**N-P4-2（P4）§1.3/代码注释的「仅 stderr 打 EP Error banner」未被决定性证据佐证。**
`deploy-record.md:73` 与 `detection_sfx.py:938-940` 称回退时「仅 stderr 打 EP Error banner」；但：① 包装层用 `print(...)`（`…inference_collection.py:508-511`）即 **stdout 而非 stderr**；② 决定性 log 中**只有** `:197` 的 UserWarning、**无** `*************** EP Error ***************` banner（`raw/wrapper-fallback-cpu-wheel.log:5-7`）——实机走的是「不可用 provider 被 native 层丢弃/归一化后正常返回」，而非 except 重建。审计结论不受影响（两形态都落到「构造正常返回 + CPU session」，正是读回反推的适用面），但机制叙述应改为「warning/丢弃或异常重建，两者均正常返回」。**建议**：随 §1.3 顺笔修正。

**N-P4-3（P4）`gpu-ep-parity-perf.json` 已被 r2run 覆盖，而 §2/§3 表仍引用首轮数字且指向该 json。**
json 现为 `source_head=79056618`、KO DML `1.211`/CPU `10.372`（`:5,131-160`）；deploy-record §2/§3 引用的是首轮 `1.106/10.447/0.065/0.203` 并把该 json 列为载体；首轮数字现仅存于 `gpu-ep-parity-perf.log`，且 §7.3 只绑 sidecar/tauri/GATE 的 r2run。**建议**：§2/§3 加一行「json 载体为 r2run（1.211/10.372）；首轮数字见 gpu-ep-parity-perf.log；§7.3 同绑 parity/perf 重跑」。

**N-P4-4（P4）三形态矩阵缺「directml wheel + 真无 DX12 设备」的实机跑。**
矩阵①为 **CPU-only wheel（无 DML provider）** 实机；②③为 stub。真实第二形态（directml wheel 已装、机器无 DX12/驱动坏 → DML 构造失败）**未实机跑**，仅由读回逻辑与 stub 覆盖（逻辑上成立：最终 session 首 provider=CPU → `device=cpu`）。**建议**：在 §1.3 明标该形态为「逻辑+stub 覆盖，NOT_RUN」，避免读者把矩阵①当成三场景全覆盖。

**N-P4-5（P4）记录新鲜度与日志载体格式（合并 3 条小项）**：① `deploy-record.md:6` 头部仍写「状态：owner_claim（交付中）……待 r1」，与 `in_review`/待 r2 及 §7.3 返修记录不一致；② `raw/tests-p11-green.log`、`raw/build-sidecar-r2run.log`、`raw/tauri-build-r2run.log` 无命令头/显式 `EXIT=` 行（同 Task 其它日志均有），而 `bundle-sizes.log` 为汇总而非 `Get-Item` 原文；③ `experiments/M2-SFX-GPU-EP-1/__pycache__/*.pyc` 存在于工作树（`.gitignore` 覆盖，无 Git 影响，可随手清理）。

---

## ④ 结论与建议

**建议集成（approved_with_conditions）**。r1 的**唯一 P1（回退审计不可达 + device 错报）已决定性闭合**：修复本体的读回反推、反查表、三键方向、兜底角色降级均与 r1 要求逐条对应；失败机制我已在**生产 wheel 源码上独立复核**（行号与 r1 引用逐行吻合），决定性验证用**真 CPU-only wheel（METADATA 实测 1.30.0、进程内无 DML）+ 生产代码原样 detect** 拿到三键实测，stub 用例形态正确且先红（旧实现 `device='dml'`）后绿（98 passed + 全量 1823 = +1 等量递增）。P3-1/P3-2/P3-3 与 P4-1/2/3/4 应闭项均已在交付物中落字；P4-5 已落具体 hash。

**集成时须处理的条件（全部为文档级，无需重跑 Gate / 不改 src 行为）**：
1. N-P4-1：在 Handoff/§7.3 落 `delivery_head(1e9f2324) ↔ tip(cdc2305c)` 映射（或由 Owner amend）。
2. N-P4-2 + §5 差注：§1.3 与 `detection_sfx.py:938-940` 的「stderr EP Error banner」改为「stdout banner / 或 provider 被丢弃后正常返回」，并把 `:262-265` 的断言句并入修订段。
3. N-P3-1：收窄「回退只覆盖 init」表述，登记 ORT run-time EPFail 未审计通道。
4. N-P4-3 / N-P4-4 / N-P4-5：§2/§3 加 r2run 指针并绑 §7.3；§1.3 标第二形态 NOT_RUN；头部状态行改 `in_review（r1 review-fix，待 r2）`。

**未能独立验证项（如实登记）**：Git 级 diff/status/name-status 与「M2-AC5/raw 相对 base 零 diff」（shell 在本会话不可用）；pytest/GATE/tauri/pyinstaller 与 GPU-CPU 实测的实际执行过程；`M2-SFX-GPU-EP-1-cpu-verify` venv 内进程行为（仅核静态 wheel/venv 事实）。

**推荐下一步**：由 Codex（集成方）在本分支 `cdc2305c` 上执行上述 4 项文档级条件（一处 amend 或集成记录即可），随后收口 merge；无需新授权、无需重跑 Gate。后续可选独立切片：`packaged sfx-detect 探针`（M2-PROD-DETECT-2 已知 NOT_RUN 缺口，须由 Codex 先立命令面契约）。此外建议登记 N-P3-1（ORT run-time EPFail 审计通道）为后续候选切片，不阻塞本次集成。
