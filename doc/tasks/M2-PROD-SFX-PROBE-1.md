---
id: M2-PROD-SFX-PROBE-1
title: "packaged sfx-detect 探针：frozen 进程内 SFX 真实推理（DML）运行证据"
kind: feature
status: in_review
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
approval: user_2026-10-04_批准进行2（已登记非阻塞候选②：M2-PROD-DETECT-2 裁决⑥ NOT_RUN 结构缺口的 sfx slice）
depends_on: [M2-SFX-GPU-EP-1]
base_commit: 72807d30
branch: agent/zcode/M2-PROD-SFX-PROBE-1
worktree: G:/CODEX/New Manga.worktrees/M2-PROD-SFX-PROBE-1-zcode
review_events: []
created: 2026-10-04
---

# Task: M2-PROD-SFX-PROBE-1 — packaged sfx-detect 探针

## 背景与授权

M2-PROD-DETECT-2（done @merge `9e44fb21`）裁决⑥：frozen 命令面（`core.ping`/`ListBooks`/`core.shutdown`，M2-IPC1 冻结）无 detect RPC，**frozen 进程内 ML import/detect 结构性不可达**，AC5 判 PARTIAL，登记后续 slice「命令面扩展 + frozen 进程内 detect 验证」。M2-SFX-GPU-EP-1 收口再次登记该缺口（候选②）：**frozen 进程内 DML 运行证据需命令面扩展**。用户 2026-10-04 批准进行2，释放本 Task。

现状：manga 检测器的闭包外等价探针 6/6 PASS（PROD-DETECT-2 L1-L4）；GATE 25 场景探针全为资源通道；SFX 权重 v2b+onnxruntime-directml 已随包（GPU-EP-1 AC4 闭包断言含 `onnxruntime_pybind11_state.pyd`+`DirectML.dll`）。

## 验收条件

- **AC1 命令面扩展（契约敏感——先核实冻结范围再动手）**：为 sidecar 提供一条**新增** probe 路径触发 sfx detect。实现路径 Owner 裁量，顺序约束：①先核实 M2-IPC1/M2-C1 对 sidecar 命令面的冻结粒度（IPC 命令集 vs CLI 入口）；②优先选择**不触碰既有冻结命令语义**的 additive 方案（新增 probe 子命令/独立探针入口均可）；③若判定必须修订冻结契约，仅允许「纯新增」修订——在 Task 内登记契约修订草案（rev 号+diff 面），交集成轮核验，**不得改写既有命令行为**。
- **AC2 frozen 进程内 sfx detect 真实运行**：对安装后环境（GATE runner 安装目录或 NSIS 静默安装）触发一次真实 sfx detect（v2b 生产权重，输入=合成漫画页或 K01 页），记录：EXIT 码、候选数、耗时、**options 三键**（`device`/`sfx_ep`/`sfx_ep_fallback`——预期 device=dml，无 fallback；如遇 wrapper 回退形态则如实登记不视为失败）。候选=0 不得静默判 PASS（登记原因并评估）。
- **AC3 既有面零破坏**：既有 frozen 命令行为零变化（单测/探针复核）；GATE 重跑 PASS 25/25（新 probe 不进 runner 场景集亦可，独立探针证据即可，但 GATE 必须复跑证明无回归）；包体积变化如实登记。
- **AC4 回归与纪律**：受影响 pytest 套件与基线一致（等量递增）；`git diff --check` EXIT=0；禁改面专项 diff 为空。
- **AC5 文档**：探针结果 JSON+log 落 `verification/M2-PROD-SFX-PROBE-1/`；部署/探针记录+Task 回填+Handoff；PROD-DETECT-2 AC5 NOT_RUN 子项以注记方式声明由本 Task 闭合。

## 纪律与限制

- 允许路径：`packaging/m2ac5/**`（如探针入口需要）、sidecar 命令注册面文件（`src/**` 逐文件声明）、`apps/desktop/src-tauri/**` 仅当探针需要 Tauri 侧触发（尽量不需要；如需则先在 Task 偏差登记说明最小 diff 面）、`tests/**`、`experiments/M2-PROD-SFX-PROBE-1/**`、`verification/M2-PROD-SFX-PROBE-1/**`、`doc/tasks/M2-PROD-SFX-PROBE-1.md`、`doc/handoffs/`、契约文档仅在「纯新增修订」时按 AC1③ 登记。
- 禁改：`contracts/**` 既有 DTO/命令语义、`doc/STATUS.md`/`doc/REBASELINE_PLAN.md`（集成方收口面）、M2-AC5 runner 场景集（25/25 保持）。
- 分支 `agent/zcode/M2-PROD-SFX-PROBE-1`，worktree 独立；构建/GATE/安装类长命令一律后台+log 落盘+轮询；`build_sidecar.ps1` 后必须 `tauri build` 才能拿到含 probe 的安装包（先例：tauri build 姿势见三确认批次教训）。
- 权重/页图零入库（外部树）；fresh checkout 须先跑 build_sidecar.ps1（如实登记 NOT_RUN 前置）。

## 设计登记（AC1① 冻结粒度核实 + AC1② 探针路径提案，Owner=ZCode 2026-10-04）

### AC1① 冻结粒度核实结论

- **M2-C1**（`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`，当前 rev 1.4 草案）：冻结面是 **React ↔ Tauri ↔ Python Core 的 transport-neutral 消息边界**（产品 UI 面命令集、Tauri command allowlist 三处同步纪律）。它约束的是「产品命令通道」，不约束 sidecar onedir 里的独立 CLI 入口 exe 清单。
- **M2-IPC1**（runtime 事实源 `src/bootstrap/core_service.py`）：冻结面是 **core_service.exe 的 stdio JSON-lines 命令面**（`core.ping`/`ListBooks`/`core.shutdown`；其后 `core.detect`（M2-PROD-DETECT-3）、`settings.*`（M2-SETTINGS-IPC-CHANNEL）、`set_region_type`/`list_regions`（M2-REGION-RETYPE-CORE）均为 additive widening + envelope minor bump 先例，`PROTOCOL_MINOR=3`）。
- **catalog_loader 先例**：`catalog_loader.exe` 是「launcher 侧 catalog seeding CLI——packaged 环境无系统 python 可跑 dev 的 `python -m` seeding；**产品命令面零扩展**」（`packaging/m2ac5/README.md` §3）——仓库既有形态已确立「不挂 IPC 命令面的独立 frozen 入口 exe」不算命令面扩展。
- **GATE 场景集核实**：`run_clean_start_e2e.py` CS-I1 对 `SIDECAR_EXES` 是 **at-least 语义**（只断言四个必需 exe 存在，不校验目录恰等）；CS-Z3 进程残留按名单查。新增第五入口不触碰 25 场景任何断言（已读源核实）。
- **Rust host 核实面**：packaged 分支按固定文件名解析 sidecar exe（`host_bridge.exe`/`core_service.exe`），不对 `resources/core-sidecar/` 目录做封闭枚举；新增文件零影响（GATE CS-Z1 安装目录零写入为安装前后 hash 对比，探针 exe 属安装包一部分，前后一致）。

### AC1② 探针路径提案（选定：独立探针入口，不动 IPC）

给 frozen 闭包新增第五个入口 `sfx_detect_probe.exe`（onelook = dev 形态 `python -m bootstrap.sfx_detect_probe`），启动即对样例页跑**一次生产 `SfxDetectionProvider.detect`**（与 `core.detect` handler / pipeline detect step 所用的同一 provider 类，装配语义一致）并打印 JSON（候选数/耗时/options 三键 `device`/`sfx_ep`/`sfx_ep_fallback` + 权重 sha/解析来源），随后退出。不触碰 IPC 命令面、不经 Tauri、既有命令行为零变化。

- 新增 `src/bootstrap/sfx_detect_probe.py`（生产探针模块；`main()` 可编程驱动，样例页=PIL 程序化合成（零入库），`--page <png>` 可注入真实页（v2b 锚点 K07_R123，conf 0.9047 已知锚）；typed 错误也打 JSON+非零 EXIT）；权重解析：`--weights` > `NEWMANGA_SFX_WEIGHTS`（非空取用，与装配 override 语义一致）> frozen in-bundle 探测（`Path(sys.executable).parent/models/detector/yolo11s-seg.onnx`，`sys.frozen` 时）——探针不猜数据根。
- 新增 `packaging/m2ac5/entries/entry_sfx_detect_probe.py` 薄包装（entry 先例姿势）。
- `core_sidecar.spec`：ENTRIES +1（探针 entry **不**进 ML hiddenimports 面——不拉 torch/transformers；专用 hiddenimports `["onnxruntime"]` + 专用闭包断言（onnxruntime pure 模块 + `onnxruntime_pybind11_state.pyd`/`DirectML.dll` binaries），断言失败=构建失败，先例姿势）。
- `build_sidecar.ps1`：layout sanity gate exe 名单 +1。
- 零触碰：`src/bootstrap/core_service.py` 命令分发表、`contracts/**`、`apps/desktop/src-tauri/**`、GATE runner 场景集。
- **AC1③ 判定：不适用**——本方案不触碰任何冻结契约（M2-C1 §5 命令表、M2-IPC1 stdio 命令面、Tauri allowlist 零 diff），无需契约修订草案。

### AC2 实测面（预登记）

runner = `verification/M2-PROD-SFX-PROBE-1/packaged-sfx-detect-probe.py`（PROD-DETECT-2 `packaged-detect-probe.py` 先例姿势，独立探针不进 GATE 场景集）：对 **NSIS 静默安装后**的环境（purged PATH）依次跑 ①安装的 `sfx_detect_probe.exe` 内置合成页（结构性冒烟：EXIT=0、JSON 可解析、三键在场；候选数如实记录——合成页不在训练分布，候选=0 在此入口不判 FAIL、登记原因）；②同 exe `--page` 注入 K07_R123 真实页（真实推理判定面：预期候选>0，v2b 锚点 conf≈0.9047；记录 EXIT/候选数/耗时/三键；`device=dml` 无 `sfx_ep_fallback` 为预期形态，如遇 wrapper 回退形态如实登记不判失败）。页图零入库：真实页留在 gitignored task-envs 外部树，证据只记路径+sha256。

## 交付回填（Owner=ZCode 2026-10-04 实测，delivery_head=33e824e4）

**全部 AC PASS，status=in_review，Reviewer=DSH（非作者）**。证据：`verification/M2-PROD-SFX-PROBE-1/deploy-record.md`（总记录）+ `packaged-sfx-detect-probe-results.json`（verdict=PASS）+ `raw/**`。

| AC | 判定 | 要点 |
|---|---|---|
| AC1 命令面扩展 | **PASS（additive 零契约修订）** | 第五 frozen 入口 `sfx_detect_probe.exe`（catalog_loader 独立入口先例形）；M2-C1/M2-IPC1 冻结粒度核实=设计登记段；AC1③ 不适用（无契约修订草案、无 rev bump）；`core_service.py` 命令分发表/Tauri 面/contracts 零 diff |
| AC2 frozen 进程内真实运行 | **PASS** | 安装后环境（GATE 安装态、purged PATH+全 `NEWMANGA_*` 清除）：K07_R123 真实页 EXIT=0、**候选=1、conf=0.9047（v2b 锚点逐位一致）**、elapsed_ms=696、**三键 device=dml / sfx_ep=dml / sfx_ep_fallback=null（无 wrapper 回退，预期形态）**；合成页 EXIT=0、候选=4、1846ms 同三键；权重 `bundle_probe` 解析且 sha256=生产 pin |
| AC3 既有面零破坏 | **PASS** | GATE PASS 25/25 EXIT=0（M2-AC5/raw 落点按 GPU-EP-1 先例快照+还原）；SP-L3 既有命令面 stdio 冒烟 ready/stopped；包体积 NSIS 580,540,551 B / 553.65 MiB（+64.72 MiB vs GPU-EP-1 基线，主体=第五入口内嵌 PYZ，与既有 ML/Qt 入口同形态，deploy-record §3 登记） |
| AC4 回归与纪律 | **PASS** | pytest **1835 passed + 1 skipped + 1 failed（test_catalog 既有）** = 基线 1823 + 新增 12 逐项吻合；`git diff --check` EXIT=0；禁改面专项 diff 空；权重/页图零入库 |
| AC5 文档 | **PASS** | deploy-record + results JSON + raw logs + Task 回填 + Handoff；**PROD-DETECT-2 AC5 NOT_RUN 子项（sfx slice）以 deploy-record §5 声明闭合**（manga slice 属另一缺口未覆盖） |

构建链（fresh worktree 全链如实登记）：frontend build → `build_sidecar.ps1 -Force`（HEAD=2b4e4946，闭包断言 PASS ×2：core_service 8584 modules ML 全量面 + **sfx_detect_probe 8455 modules onnxruntime 面**+pyd/DirectML.dll）→ `tauri build`（NSIS `3ffa03f5…`）→ GATE → 探针 runner。已知注释过时（留集成裁量）：`main.rs:378-379` sidecar exe 名单注释仍列四个，纯注释无功能引用，本 Task 保持 src-tauri 零 diff。
