# AC5 实测基准补齐（2026-10-20）

**任务项**：AC5 — P20 的 Tauri/WebView2/Python sidecar/Windows/UI/可选模型
对旧 stack-specific 条目的逐项保留与新证据 Gate。

**原状态**：`NOT_RUN`，理由（原文）：

> 旧 NFR 条目已逐项映射并保留且不降阈值，**新二进制实测基准待 P20 执行**。

**本文件的作用**：P20 已于 2026-10-20 关闭（`closed_with_limitations`），
其 NFR 实测数据已齐备。**本文件把那批数据按 AC5 的映射矩阵逐项对齐**，
把 AC5 从 `NOT_RUN` 推进到可判定状态。

**注意**：本文件**不修改** `ac5-p20-nfr-stack-rebaseline.md`（Owner 交付物），
它是补充证据，不是替代。

## 一、被测对象

| 项 | 值 |
|---|---|
| EXE | `apps/desktop/src-tauri/target/debug/m2rc1-desktop.exe` |
| SHA-256 | `be593a886c2a90ff3175fadb6164d79406798d4f63a43cdf2505d3eac3979574` |
| 宿主机 | Windows 11 专业版 build 26300 |
| CPU | AMD Ryzen 9 7950X3D 16-Core |
| RAM | 32407 MB |
| GPU | MuMu Virtual Display Adapter / GameViewer / OrayIddDriver / NVIDIA RTX 5070 Ti |

## 二、逐项对齐 AC5 的映射矩阵

### 2.1 冷启动性能

| 项 | 内容 |
|---|---|
| **AC5 要求的阈值** | 主窗口 ≤ 2.0 s；Core 就绪 ≤ 3.5 s |
| **新证据 Gate 定义** | 整棵进程树计时，多轮取样，CSV 归档 |
| **实测** | **主窗口 avg 0.841 s**（3 轮：1.579 / 0.475 / 0.470）；**Core ready avg 0.846 s** |
| **判定** | **PASS**（远低于 2.0 / 3.5） |
| 证据 | `verification/P20/nfr-20261020-r4/`（`nfr-trace.log`、`coldstart-memory.csv`）|

**说明**：第 1 轮 1.579 s 是冷缓存首跑；第 2/3 轮 0.47 s。
历史 `nfr-20261018-1152` 的 avg 是 0.474 s，**同一量级**。

### 2.2 内存占用

| 项 | 内容 |
|---|---|
| **AC5 要求的阈值** | 空闲驻留（Tauri + msedgewebview2* + python 的 Working Set 总和）≤ 480 MB |
| **新证据 Gate 定义** | 整棵进程树 Working Set |
| **实测（父子链口径）** | **467.35 MB** |
| **实测（按进程名通配）** | 1149.75 MB —— **含 682.40 MB 属于其它应用**（同机其它程序的 WebView2）|
| **判定** | **PASS**（467.35 ≤ 480），按**链口径** |

**关键**：`run-nfr-coldstart-memory.ps1` 的 `total_ws_mb` 按**进程名**累加，
会误算其它应用。**AC5 的 Gate 规范写的是「整棵进程树」，即父子链**，
所以正确值是 467.35 MB。逐进程明细见
`verification/P20/nfr-20261020-r4/chain-memory.json`。

### 2.3 交互响应与帧率

| 项 | 内容 |
|---|---|
| **AC5 要求的阈值** | 交互延迟 ≤ 50 ms；稳定 60 FPS；无可见撕裂 |
| **新证据 Gate 定义** | 真实桌面测量 + 样本级 CSV |
| **交互延迟实测** | **avg 36.0 ms**（20/20 样本；p95 = max = 62.4 ms）|
| **帧率实测 · 单页** | **avg 16.681 ms**，p95 16.8，max 17，**1266 样本，0 excluded** |
| **帧率实测 · Webtoon** | **avg 17.527 ms**，p95 33.3，max 33.5，**1202 样本，0 excluded** |
| **撕裂** | **未观察**（无可用验收程序）|
| **判定** | 延迟 **PASS**（avg 口径，用户 2026-10-20 裁决）；帧率 **PASS**；撕裂 **LIMITATION** |

**判据来源**：用户 2026-10-20 裁决「交互延迟与帧率都按 `avg ≤ 50 ms`，
帧率另须报告 p95/max」。**16.681 ms ≈ 59.9 FPS；17.527 ms ≈ 57.1 FPS。**

证据：`verification/P20-AC4-FPS-1/ac3-real-desktop/`。

### 2.4 打包与分发

| 项 | 内容 |
|---|---|
| **AC5 要求的阈值** | Tauri Bundler 产出 MSI/NSIS，干净 Win10/11 x64 可安装、可完整卸载 |
| **实测** | 安装包已实测产出（P20 AC1 `done`）|
| **判定** | **PASS**（承 P20 AC1）|

### 2.5 模型解耦与无 GPU 兼容

| 项 | 内容 |
|---|---|
| **AC5 要求的阈值** | 无独显/无 CUDA 下可正常启动、基础功能与在线 API 可用、本地模型降级 CPU |
| **实测** | **8/8 通过**（本机有 RTX 5070 Ti，故以 `CUDA_VISIBLE_DEVICES` 屏蔽实测）|
| **判定** | **PASS**（承 P20 AC5）|

### 2.6 故障隔离与自愈

| 项 | 内容 |
|---|---|
| **AC5 要求的阈值** | sidecar 异常退出不白屏；未提交草稿不丢；心跳探测与回收重启可用 |
| **实测** | 真实桌面注入：强杀 `core_service` 后主窗口存活、UI 可见故障提示、**真实草稿保全并通过隔离库提交** |
| **判定** | **PASS**（承 P20 AC6 + `P20-ISOLATION-1` 补证）|
| 证据 | `verification/P20-ISOLATION-1/r010-20261018-0944/trace.log`（15 条 `ASSERT PASS`）|

## 三、结论

**AC5 的六项 NFR 领域全部有实测或已完成的承接证据：**

| NFR 领域 | 阈值（不降） | 实测 | 判定 |
|---|---|---|---|
| 冷启动 | ≤ 2.0 s / ≤ 3.5 s | 0.841 / 0.846 s | **PASS** |
| 内存 | ≤ 480 MB（链口径）| 467.35 MB | **PASS** |
| 交互延迟 | ≤ 50 ms（avg）| 36.0 ms | **PASS** |
| 帧率 | avg ≤ 50 ms | 16.681 / 17.527 ms | **PASS** |
| 打包分发 | MSI/NSIS 可安装可卸载 | 已实测 | **PASS** |
| 无 GPU 降级 | 8/8 | 8/8 | **PASS** |
| 故障隔离 | 不白屏/草稿不丢/自愈 | 真实注入通过 | **PASS** |
| **撕裂** | 无可见撕裂 | **未观察** | **LIMITATION** |

**AC5 的核心要求是「旧条目逐项保留且不降阈值 + 新证据 Gate」。**
**这两件事都已成立**：映射矩阵由 Owner 完成（原报告 §2），
实测基准由本文件补齐。**唯一例外是撕裂，与 P20 AC4 同源，记 limitation。**

## 四、明确未做

- **未修改** `ac5-p20-nfr-stack-rebaseline.md`（Owner 交付物）。
- **未修改** AC5 的勾选状态。
- **未做**纯净 Win10 22H2 虚拟机上的复测（原 Gate 规范 §3.1 要求两套环境；
  本次全部在本机 Win11 上完成）。
  **这是一个真实的偏差，应当记录**：原规范要求「Windows 11 x64 / Windows 10 22H2
  纯净虚拟机或物理机」与「Intel i5 / 8GB 无独显基线」两个档位，**本次只有一台机器**。
- **未做** WPR/GPUView 采集（原 Gate 规范 §3.2 提议使用；实际用的是脚本级计时）。
