# C4 硬件/真机/外部条件 · 正式 waiver 载体（MAINT-1，2026-11-14）

用途：满足 DoD §1「done + 显式 waiver（裁决记录写明 NOT_APPLICABLE 原因并保留 NOT_RUN 证据）」与 §3「硬件类转 OUT + waiver」。
性质：**append-only 裁决记录**。不改任何 Task 卡、Review、`verification/**` 的历史字节；不把 `NOT_RUN` 写成 PASS。

裁决人：DSH（`MAINT-1` owner，用户 2026-11-14 全权授权）。**用户可事后推翻**；推翻后按对应节点重开实现卡。

## 1. 分类原则（与 RESIDUAL-CLOSEOUT-PLAN §0/§11.1 一致）

- 只有**依赖本机不可得的外部条件**才进 C4：真实硬件矩阵（双屏/拔屏/DPI）、原生 IME、原生 a11y/UIA、真机截图与人工目视、真实用户库升级回退、真实模型 API、Linux 运行、打包 sidecar 的 C-17 同步链。
- **不得**把工程可闭环项塞进 C4 来合法化未做的工作。三处曾差点误判，已纠正并在此登记：
  1. `FEA-07` AC1/AC2/AC5 的"无硬件"说法被 §11.1 推翻（本机实测 2 活动显示器）→ 真实状态是**原生交互矩阵未执行**，仍属 C4 但原因措辞改为"未执行"。
  2. `FEA-15-A3-1` 的日志根问题**已降级为 C3**（源码显示为有意的发行默认），不进本载体。
  3. `FEA-11` folder relink 判别测试属 C1（可构造），不进本载体。

## 2. 逐项 waiver

| # | 节点 | 项 | NOT_APPLICABLE 原因 | 保留的 NOT_RUN 证据 |
|---|---|---|---|---|
| W1 | FEA-14-READ-1 / READ-2 | 真实 UI 手势 / IME / 多屏 / DPI / 主题 / 托盘 / 真实进程重启 | 需真实交互会话注入，本环境无法构造 | 两卡 limitation 段明列 `NOT_RUN`；本循环 P2 仅覆盖首屏可达 |
| W2 | FEA-14-EDIT-1 | 真实 Host↔Core IPC 映射 / EDIT UI 人工操作 / 管线联动 / 万级性能 | 真实 IPC 需完整 sidecar 链；性能需基准机 | `FEA-14-EDIT-1` limitation ④ |
| W3 | FEA-14-AI-1 | 真实 AI/网络调用、P24 活 Core 端到端、大库并发 | 需真实 provider 凭据与费用；大库需数据集 | `FEA-14-AI-1` limitation ⑦；`V1_COMMITMENT_MANIFEST:27`（模型 API `NOT_RUN`） |
| W4 | FEA-14-FONT-1 | 真实字体渲染消费、大文件/占用文件压测 | 渲染消费属 FONT-2 范围（C3）；占用文件需真实锁 | `FEA-14-FONT-1` limitation 段 |
| W5 | FEA-14-LIB-1 | 真实 Host↔Core 进程级联调、Volume 实体、万级章性能 | 同 W2；Volume 实体属 LIB-2 范围（C1） | `FEA-14-LIB-1` limitation ⑤ |
| W6 | FEA-15-A3-1 | 真实手势 / IME / 多屏 / DPI / 主题 / 托盘 | 同 W1 | `FEA-15-A3-1` limitation 段 `NOT_RUN` |
| W7 | FEA-15-ACCEPT-1 | 真实 clean install、可见 UI 全验收、真实用户库升级回退 | 需干净环境/真实用户库/安装权限 | `verification/FEA-15-ACCEPT-1/README.md`；P2 冒烟仅首屏；`13_RELEASE_GATE.md` BLOCKED |
| W8 | FEA-15-PIN-BASIS-ENFORCE-1 | Linux 运行 `NOT_RUN` | 本机无 Linux 运行环境 | 该卡 Closeout `保留限制` 段 |
| W9 | FEA-11-HOST-AUTH-* 系 | 打包 sidecar 腿（早于 C-17） | sidecar 产物早于 C-17 v1.1，需重新打包发行才能验 | `Fea11Scan2HostRuntimeTests.cs:16-17/:57-59`；Q8 处置记录 |
| W10 | FEA-07 系 | 原生双屏/拔屏/DPI 矩阵、原生 IME、A003 真库往返 | 原生交互矩阵未执行（非"无硬件"） | `FEA-07` limitation L-R4a/L-R4b；ADJ §11.1 |

## 3. 与 DoD 的对应

- 本载体只解决 **C4 类**：把上述项从"悬空 limitation"变为"有裁决、有原因、有 NOT_RUN 留痕"。
- **不解**：C1（约 13 项，需实现）、C2（5 项，需 errata/UNFREEZE/ADJ）、C3（7 项，需逐个 OUT 载体）。
- 因此本轮**不改变** DoD §1/§3 的未达成判定；本载体是达成路径上的一个前置件。

## 4. 可推翻性

任一项若获得外部条件（真实双屏/干净安装环境/真实 provider 凭据/Linux 环境/重新打包的 C-17 sidecar），立即作废对应 waiver，改开实现或验证卡，并以 append-only 记录推翻原因。
