# M2-PROD-SFX-PROBE-1 部署/探针记录（Deployment & Probe Record）

Task: M2-PROD-SFX-PROBE-1 — packaged sfx-detect 探针：frozen 进程内 SFX 真实推理（DML）运行证据
Owner: ZCode；base=d298ecd0；branch=`agent/zcode/M2-PROD-SFX-PROBE-1`；worktree=`G:/CODEX/New Manga.worktrees/M2-PROD-SFX-PROBE-1-zcode`
授权：用户 2026-10-04 批准进行2（M2-PROD-DETECT-2 裁决⑥ NOT_RUN slice，契约敏感=纯新增约束）
状态：in_review；Reviewer=DeepSeek Harness（非作者）

## 0. 交付摘要

给 frozen 闭包新增**第五个独立探针入口** `sfx_detect_probe.exe`（dev 形态 `python -m bootstrap.sfx_detect_probe`）：启动即对样例页跑**一次生产 `SfxDetectionProvider.detect`**（与 `core.detect` handler / pipeline detect step 同一 provider 类）并打印 JSON（候选数/耗时/三键 `device`/`sfx_ep`/`sfx_ep_fallback` + 权重 sha/解析来源/页 sha），随后退出。**不触碰 IPC 命令面、不经 Tauri、零契约修订**——catalog_loader「独立 frozen 入口 exe、产品命令面零扩展」先例形（AC1②，Task 文档设计登记段）。

- 允许路径内 diff：`src/bootstrap/sfx_detect_probe.py`（新增）、`packaging/m2ac5/**`（entry 薄包装/spec/sanity gate）、`tests/core/test_sfx_detect_probe.py`（新增 12 测试）、`verification/M2-PROD-SFX-PROBE-1/**`（runner+证据）、`doc/tasks/`、`doc/handoffs/`。
- **零触碰实证**：`contracts/**`、`apps/desktop/src-tauri/**`（含 `bootstrap.core_service` 命令分发表所在 src 面以外的 Rust host）、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、GATE runner 场景集——专项 diff 全空（verify commit 面核查）。
- 已知注释过时（留集成轮裁量，不构成本 Task diff）：`apps/desktop/src-tauri/src/main.rs:378-379` 注释列举 sidecar exe 名单为四个（spec 现为五入口）——纯注释、Rust host 按固定名探测（`dir.join("host_bridge.exe").is_file()`），不枚举目录，无功能引用；本 Task 保持 src-tauri 零 diff 不改。

## 1. AC1 命令面扩展（additive，零契约修订）— PASS

核实结论（详见 Task 文档设计登记段）：

- **M2-C1**（`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` rev 1.4）：冻结面=React↔Tauri↔Python Core transport-neutral 消息边界 + Tauri command allowlist 同步纪律；不约束 sidecar onedir 独立 CLI 入口 exe 清单。
- **M2-IPC1**（runtime 事实源 `src/bootstrap/core_service.py`）：冻结面=core_service.exe stdio JSON-lines 命令面（`core.ping`/`ListBooks`/`core.shutdown` + 后续 additive widening `core.detect`/`settings.*`/`set_region_type`/`list_regions`，`PROTOCOL_MINOR=3`）。本 Task 零触碰该文件与命令分发表。
- **AC1③ 判定：不适用**——探针入口不挂 stdio 命令面、不经 Tauri，无契约修订草案、无 rev bump。

## 2. AC2 frozen 进程内 sfx detect 真实运行 — PASS

载体：`packaged-sfx-detect-probe-results.json`（verdict=PASS）+ `raw/sp-l{1,2}-*.log` + `raw/probe-runner.log`。
环境：NSIS 静默安装目录（GATE 安装态 `%TEMP%\m2ac5-cleanstart\install`），purged PATH（剔除 python/venv/conda/WindowsApps）+ **全 `NEWMANGA_*` 清除**（零 env 干预安装态；r1fix 重跑 log `cleared env names (0)` 表示宿主环境本就无该类变量、零干预——非「曾存在被剔除」，DSH r1 P4-2）；权重=in-bundle v2b（`weights_resolved_from=bundle_probe`，sha256=生产 pin `944e8114…` 逐字一致）。

| 场景 | 输入 | EXIT | 候选数 | elapsed_ms | device | sfx_ep | sfx_ep_fallback |
|---|---|---|---|---|---|---|---|
| SP-L2（AC2 实质判定面） | K07_R123 真实页（M2-SFX-T4-SWITCH v2b 锚点页，页 sha256 `b3b7c4a6…`，页图留在 gitignored 外部树零入库） | 0 | **1** | **696** | **dml** | **dml** | **null（无回退）** |
| SP-L1（结构冒烟面） | 内置 PIL 合成 sfx 页（程序化生成、零入库） | 0 | 4（conf_max=0.798） | 1846（含 DML session 冷启动） | dml | dml | null |

- **候选数评估（AC2 硬门）**：真实页候选=1 且 conf_max=**0.9046692252159119**，与 v2b 锚点（M2-SFX-T4-SWITCH `v2b-k07-r123-anchor.json` conf `0.9046694040298462`）**同源同页**（r1fix 重跑实测 `page_file_sha256=28dab503…` 与锚点 `frame_sha256` **逐位一致**）、conf 差 **1.79e-7**，落在 GPU-EP-1 登记的 GPU↔CPU 漂移窗口（≤2e-06）内；回归测试容差 abs=1e-3（DSH r1 P1-1 措辞更正：原「逐位一致」为错误陈述——DML 与 CPU 形态存在既有末位漂移，任何证据不得写「位级可复现」）——非零候选达标，无静默 PASS。合成页候选=4 同样非零。
- **r1fix 重跑（DSH r1 C3 判据加固后，真实安装态，`raw/r1fix/` + `packaged-sfx-detect-probe-results-r1fix.json`）**：SP-P0/SP-L1/SP-L2/SP-L3 **4/4 PASS**，新判据（`python.frozen is True` + SP-L2 权重 pin + DSH r2 R-2 三键在场 `sfx_ep_fallback` 键判据）在场且通过；SP-L2 conf 与首轮交付**逐位一致**（0.9046692252159119，DML 同机同形态确定性）；`page_file_sha256=28dab503aca3c903111488c03e857b430d309421a4a54bab335a63bbe7b9cec4` 与 v2b 锚点 frame_sha256 逐位一致（同页同文件级互证，DSH r1 P4-8 闭合）；SP-L3 以 minor=3 envelope 冒烟（DSH r1 P4-3）ready/stopped 正常；r2 顺笔轮（R-2 落代码/R-8 stdout 归档）以终态判据重跑仍 4/4 PASS（`raw/r1fix/probe-runner.log`）。原始交付证据（`raw/` + `packaged-sfx-detect-probe-results.json`）零触碰（`--raw-subdir r1fix` 隔离）。
- **三键（AC2 要求）**：`device=dml`、`sfx_ep=dml`、`sfx_ep_fallback=null`——**预期形态达成（无 wrapper 回退）**；`sfx_route=letterbox`、`imgsz=1024`（metadata_parsed）、`conf_threshold=0.5` 同录于 JSON options。
- （DSH r1 P4-6：原「source 形态 dev 冒烟 n=1/conf=0.9047/793ms 与 frozen 互证」对账句因无 raw 落盘支撑已删除；frozen 证据以本表 raw log 为准。）

## 3. AC3 既有面零破坏 — PASS

- **GATE `run_clean_start_e2e.py` = PASS（25/25，EXIT=0**，`raw/gate-clean-start-e2e.log`）：installer sha256 `3ffa03f5…` 与本 Task 包一致；E1-E3/I1-I2/L1-L3/P1-P3/A1-A3/CS-A4/CS-A5/Z1-Z4 全 PASS（verdict 快照 `raw/m2ac5-gate-artifacts-thisrun/cleanstart-gate.json`；DSH r1 P4-4 补登 CS-A4/A5，25 场景逐 id 重算=25）。新探针不进 runner 场景集（设计登记）；SP-L3 另做既有命令面 stdio 冒烟（core.ping=ready/core.shutdown=stopped，EXIT=0）。
- **GATE 落点处置（GPU-EP-1 先例）**：runner 内置产物写 `verification/M2-AC5/raw/`（git 追踪的历史证据目录，非本 Task 允许面）。GATE 前已将 6 个将被覆盖文件快照至 `raw/m2ac5-gate-artifacts/`（含逐文件 sha256），GATE 后 `git checkout -- verification/M2-AC5/` 原样还原（git status clean 实证）；本轮 verdict 快照存 `raw/m2ac5-gate-artifacts-thisrun/`。
- **包体积变化（如实登记，`raw/bundle-sizes.log`）**：

| 口径 | GPU-EP-1 基线 | 本 Task 实测 | Δ |
|---|---|---|---|
| NSIS 安装包 | 512,675,022 B / 488.93 MiB（sha256 `4c9ef883…`） | **580,540,551 B / 553.65 MiB**（sha256 `3ffa03f551be5e4439f068d43a6c9f21aa42257bf9baf3cb7213eba1f8dfbfff`） | **+67,865,529 B / +64.72 MiB** |
| onedir `core-sidecar/` | 1,225,505,427 B / 1168.73 MiB | 1,293,443,537 B / 1233.52 MiB | +67,938,110 B |
| `sfx_detect_probe.exe` 本体 | —（不存在） | 67,901,644 B / 64.76 MiB | 增量主体 |

  增量主体=第五入口 exe 内嵌 PYZ。**归属更正（DSH r1 P2-1，构建分析面证据 `raw/build-sidecar.log:440` 起分析区间 + warn-archive 对照：`warn-sfx_detect_probe.txt` 满含 torch/transformers/doctr 搜索、`warn-catalog_loader.txt` 同类零命中）**：8455 pure modules 不是「onnxruntime 面」而是**第二份 torch/transformers/doctr 闭包**（≈core_service 的 8584）——机理=探针 import 生产 `SfxDetectionProvider`，模块图经 `detection_sfx → detection_manga → detection_doctr`，`detection_doctr.py:226` 函数体内静态 `from doctr.models import detection_predictor` 被 modulegraph 跟进，doctr→torch→transformers 整链入 PYZ；「onnxruntime 目录 66,170,520 B 与基线一致」只说明共享 `_internal` 未膨胀，不能推出 PYZ 未膨胀。原交付「探针 entry 不拉 torch/transformers」声明被构建证据推翻，`core_sidecar.spec` 注释已同步更正为事实口径。**增量取舍登记（DSH r1 P2-2 三选一，集成裁决=选 (a)）**：(a) **接受**重复闭包——零产品风险、回退路径简单（revert spec ENTRIES 第五行 + build_sidecar.ps1 sanity gate 行）、+64.72 MiB 与既有入口各自内嵌 PYZ 同构（`core_service.exe`/`acceptance_bridge.exe` 各 68.5 MB），非打包回归；(b) 挂 `core_service.exe` 一次性 CLI 模式（0 B）**被拒**——会分叉产品主入口的启动行为，与「零触碰既有冻结入口」纪律冲突；(c) 瘦身探针 import 面（断开 `detection_doctr` 静态 import / 共享 PYZ）属产品 src 结构重构，留后续 slice 裁量。

## 4. AC4 回归与纪律 — PASS

- 全量 pytest（T1.1.1-impl-py312 生产 venv，worktree 根）：**1835 passed + 1 skipped + 1 failed（`tests/m2_test_assets/test_catalog.py` 既有 BASELINE_FAILURE，Task 合同明示）** = 基线 1823 + 本 Task 新增 12（`tests/core/test_sfx_detect_probe.py`）逐项吻合（`raw/pytest-full-regression.log`）。
- `git diff --check`（DSH r1 P3-3 更正：原句「提交完成后工作区口径 EXIT=0」属口径空转——提交后无未暂存改动该命令恒 EXIT=0，不构成对交付内容的检查；r1fix 轮已按真实 range 口径重跑落盘）：`git diff --check d298ecd0..b1dd1ad4` git 输出 55 行=**27 处 trailing whitespace + 1 处 `new blank line at EOF`（tauri-build.log:302）跨 6 个 raw 证据 log**（GATE stdout 副本 ×3 / r1-library-probe / sp-l3 / tauri-build；前 5 文件为 git blob 层 CR-at-EOL——工作区同为 CRLF 的 sp-l1/sp-l2 log 与 gate.json 未入报，证明入报集由 blob 行尾决定；tauri-build.log 与 CR 无关、系 blank-at-EOF——DSH r2 R-4 计数拆分与机制精确化）。控制台输出忠实形态沿 GPU-EP-1 先例豁免、不改证据（原「豁免」叙述所依据的「22 处」数字经实测更正）；**排除 `raw/**` 后 EXIT=0**（代码+docs 面零 whitespace 问题）。证据：`raw/r1fix/range-diff-check-delivery.log`、`range-diff-check-delivery-excl-raw.log`、`range-diff-check-r1fix-chain.log`（含返修 commit 的全链，附命令头+EXIT 标注）。
- 禁改面专项 diff（contracts/、apps/desktop/src-tauri/、doc/STATUS.md、doc/REBASELINE_PLAN.md、GATE runner 场景集）为空（工作区+commit 链 d298ecd0..HEAD 双面核查）。
- 权重/页图零入库：v2b 权重与 K07_R123 均在 gitignored task-envs 外部树，证据只记路径+sha256。

## 5. AC5 文档 — PASS（本记录即载体）

- 探针结果 JSON：`packaged-sfx-detect-probe-results.json`；logs：`raw/`（probe-runner、sp-l1/l2/l3、build-sidecar、tauri-build、gate、pytest、bundle-sizes、GATE 落点快照两目录）。
- 部署/探针记录=本文件；Task 回填+Handoff=`doc/tasks/M2-PROD-SFX-PROBE-1.md` + `doc/handoffs/M2-PROD-SFX-PROBE-1-zcode-20261004.md`。
- **PROD-DETECT-2 AC5 NOT_RUN 子项闭合声明（DSH r1 §4.1 精确边界）**：M2-PROD-DETECT-2 `packaged-detect-probe-results.json` 的 `boundary_note`（"frozen in-process ML import/detect stays NOT_RUN until the frozen command surface extends"）中 **sfx slice 由本 Task 闭合——依据 catalog_loader 先例，以独立 frozen 入口（非命令面扩展）闭合**。本 Task 证明的是：随包发布的 frozen PyInstaller 入口进程内（同一 onedir、同一 in-bundle v2b 权重、同一 `SfxDetectionProvider` 装配类）能跑通生产 detect 并给出三键，即 NOT_RUN 缺口的**闭包面**闭合；它**不是**「产品 sidecar `core_service.exe` 进程内 detect 可达」的闭合，也不是 manga slice 的闭合（后者属另一缺口，本 Task 未覆盖）——后续不得把「命令面扩展」当作该 NOT_RUN 的既定收敛条件。frozen 进程内 DML 真实推理运行证据见本文 §2（历史文件不改写，此处即为登记处）。

## 6. 构建链实测（fresh checkout 全链，`raw/*.log`）

1. frontend：`npm install --no-audit --no-fund` + `npm run build` EXIT=0（`raw/frontend-build.log`；fresh worktree 无 gitignored dist，前置必跑）。
2. `build_sidecar.ps1 -Force`（fresh worktree 首跑=全量 PyInstaller，HEAD=**2b4e4946** 绑定，pyinstaller 6.22.3，m2ac5-build venv onnxruntime-directml 1.24.4）EXIT=0（`raw/build-sidecar.log`）：
   - 闭包断言 PASS ×2：`core_service PYZ carries transformers, transformers.models.rt_detr, transformers.models.rt_detr_v2, onnxruntime (8584 pure modules) + extensions torchvision/_C_stable.pyd, torchvision/image_stable.pyd, onnxruntime_pybind11_state.pyd, DirectML.dll`（与 GPU-EP-1 逐字一致）；**`sfx_detect_probe PYZ carries onnxruntime (8455 pure modules) + extensions onnxruntime_pybind11_state.pyd, DirectML.dll`**（本 Task 新增断言；断言口径=onnxruntime 引擎在场，PYZ 实际另含第二份 torch/transformers/doctr 闭包——DSH r1 P2-1 归属更正见 §3）。
   - 权重复制 sha256 验证 ×2（manga 三文件 + sfx v2b onnx）。
3. `npx --yes @tauri-apps/cli@2 build` EXIT=0（`raw/tauri-build.log`）；`gen/schemas/**`+`permissions/autogenerated/**` 行尾重写已按 README 纪律 `git checkout --` 还原（worktree clean 实证）。
4. GATE（TASK-012-py312 venv）PASS 25/25（§3）。
5. 探针 runner（TASK-012-py312 venv，stdlib-only）PASS 4/4（§2）。

## 7. 纪律声明

- 全部数字为实测证据（单机单轮，directional 口径，不作外推）；探针 elapsed_ms 为 provider 自报（含 DML session 冷启动的 SP-L1 与暖 session 单页计测的 SP-L2 形态已在表中区分）。
- 探针候选数为运行事实，**不构成检测质量判定**（质量口径属 M2-SFX-DETECT-EVAL/T4/T3 评价链）。
- 本机无 wrapper 回退形态观测（GPU-EP-1 §1.3 的回退矩阵不因本 Task 扩展）；`sfx_ep_fallback` 通道在探针 JSON 中为可观测字段，如未来出现回退将原样入 JSON（runner 如实登记不判失败；SP-L2 判据自 r1fix 起为 **EXIT=0 + JSON 可解析 + `python.frozen is True` + 候选>0 + 三键在场 + 权重 sha256=pin**——DSH r1 P2-3 判据加固后口径，r1 时点仅三键+候选）。runner 另自带一份 `SFX_WEIGHTS_SHA256` 常量 pin（DSH r1 P4-5：失效即 FAIL 方向安全；pin 迁移时须与探针 JSON `weights.expected_sha256` 两处同步）。
