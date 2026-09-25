# M2-R1 — 证据清单与覆盖（Evidence Manifest）

| 项 | 值 |
|---|---|
| Task | [M2-R1](../../doc/tasks/M2-R1.md)（`kind: research`） |
| 报告 | [`doc/research/M2-R1_QT_RUNTIME_FEASIBILITY.md`](../../doc/research/M2-R1_QT_RUNTIME_FEASIBILITY.md) |
| 固定代码 base | `6a68fdeb92d8a1c7903166a8076d6260bf8fa79a` |
| Owner 开工 HEAD | `5d989bab6c5c8a24a5112303f95c2b8eea356bdc` |
| 被测环境 | Python 3.12.3 + PySide6_Essentials 6.11.2 + Qt 6.11.2 + Windows 11 `10.0.26200`（隔离 venv，见 `01-environment.log`） |
| 证据根 | `verification/M2-R1/**`（本 Task 授权路径内） |

## 1. 覆盖矩阵

| 探针 | 平台 | 条件 | 独立进程数 | 退出码 | 原始日志 |
|---|---|---|---|---|---|
| `probes/qt_platform_probe.py` | `windows` | 主矩阵 | 3 | 0/0/0 | `02-probe-windows.log` |
| 同上 | `offscreen` | 主矩阵 | 3 | 0/0/0 | `03-probe-offscreen.log` |
| 同上 | `minimal` | 主矩阵 | 3 | 0/0/0 | `04-probe-minimal.log` |
| `probes/qt_font_remediation_probe.py` | `offscreen` | `baseline` | 1 | 0 | `05-supplementary-font-remediation.log` |
| 同上 | `offscreen` | `fontdir`（`QT_QPA_FONTDIR=C:\Windows\Fonts`） | 1 | 0 | 同上 |
| 同上 | `offscreen` | `appfont`（`msyh.ttc`） | 1 | 0 | 同上 |
| 同上 | `minimal` | `fontdir` | 1 | 0 | 同上 |
| 同上 | `minimal` | `appfont` | 1 | 0 | 同上 |
| `probes/qt_eventloop_probe.py` | `windows` / `offscreen` / `minimal` | `QTimer(300ms)` + `exec()` + HWND 普查 | 6（3×2） | 0（全部） | `06-eventloop-and-window-census.log` |

合计 **18 次独立进程运行，退出码全部为 0**，无 Python 异常、无 QPA 插件加载失败、无挂起。

主矩阵每次运行驱动**四个** AC2 要求的对象：`QGuiApplication`、`QFontDatabase`（+ 生产 `QtFontCatalog`）、生产 `QtTextLayoutEngine`（横向 + 竖向）、生产 `QtImageCompositor`（`compose_page` + `compose_region`）。

## 2. 证据完整性（关键产物 sha256，前 32 位十六进制）

### 2.1 输入基准图（探针内纯 stdlib 生成，用于判定"合成是否真的改变像素"）

| 产物 | 字节 | sha256（前 32） | 出现次数 | 一致性 |
|---|---|---|---|---|
| `input_base.png` / `input_clean.png` | 682 | `a5f9021b328bd79e65aac0186530ab76` | 18 份（3 平台 × 3 次 + 冒烟） | **全部相同**（输入确定，可复算） |

### 2.2 合成输出页图（`compose_page`，两个 op：横向 + 竖向）

| 平台 | 字节 | sha256（前 32） | 3 次运行 | 结论 |
|---|---|---|---|---|
| `windows` | 2689 | `a7768dd3e9980211a1c90a250d9d0482` | 3/3 相同 | 跨进程逐字节确定性 |
| `offscreen` | 1095 | `656d0ac6e5aa7d28cab996c22fc28184` | 3/3 相同 | 跨进程逐字节确定性 |
| `minimal` | 1095 | `656d0ac6e5aa7d28cab996c22fc28184` | 3/3 相同 | **与 offscreen 完全相同** |

### 2.3 合成输出区域图（`compose_region`）

| 平台 | 字节 | sha256（前 32） |
|---|---|---|
| `windows` | 2152 | `6a413a509dacfa7c6bfd49a736ec9e2a` |
| `offscreen` | 1034 | `83e38c265d7cd9cb8d5289ed35081879` |
| `minimal` | 1034 | `83e38c265d7cd9cb8d5289ed35081879` |

### 2.4 字体补救输出页图（单 op；与主矩阵不同图，不可横向比像素数）

| 条件 | 字节 | sha256（前 32） |
|---|---|---|
| `offscreen` + `addApplicationFont(msyh.ttc)` | 2169 | `c5438e91f21ebc212e155a03d3421e5a` |
| `offscreen` + `QT_QPA_FONTDIR` | 2132 | `784ae5c30accf78f7f3a557723e3bf04` |
| `offscreen` / `minimal` 基线、`minimal` 两种补救 | 1034 | `83e38c265d7cd9cb8d5289ed35081879`（与 offscreen 基线区域输出同形） |

> `probe.json` 每次运行的 sha256 **不同**（含 `pid`、时间戳、耗时），这是预期行为；判定确定性使用的是上表中的 PNG 与 JSON 内的数值列，而非 JSON 文件自身的 hash。

完整逐文件 hash 清单见 [`07b-artifact-hashes.log`](07b-artifact-hashes.log)。

## 3. AC 对照

| AC | 判定 | 证据 |
|---|---|---|
| **R1-AC1** 记录生产 Python/PySide6/Qt/Windows 版本来源、解释器路径、安装包版本与隔离方式；版本不匹配时限制结论 | **PASS** | `01-environment.log`（生产口径 `requirements.txt` 行、隔离 venv 路径、Python 3.12.3、PySide6 6.11.2、shiboken6 6.11.2、Qt 6.11.2、Windows 11 26200、QPA 插件清单）；报告 §2，裁定"匹配生产口径，不记 BLOCKED" |
| **R1-AC2** 分别实测 `windows`/`offscreen`/`minimal` 下的 `QGuiApplication`、`QFontDatabase`、`QtTextLayout`、Qt compositor；给出无可见 GUI 证据 | **PASS** | `02/03/04-probe-*.log`（主矩阵，每平台 3 次）；`06-eventloop-and-window-census.log`（HWND 普查：windows 3 个隐藏/0 可见，offscreen、minimal 各 0 个）；报告 §3.1–§3.3 |
| **R1-AC3** 每平台记录重复运行/退出稳定性、失败类型、退出码、输入输出 Hash 或尺寸；区分平台与部分可行组合 | **PASS** | 9 次主矩阵退出码 0/0/0；PNG sha256 跨 3 次相同（§2.2）；报告 §3.1/§3.4 稳定性表；§3.5 平台分级 `windows` PASS / `offscreen` PARTIAL（可补救）/ `minimal` PARTIAL（不可补救）；**未观察到任何失败类型**（照实记录为"静默退化"，非"无风险"） |
| **R1-AC4** 将 M2D1-22 从 `UNVERIFIED` 收敛为实测结论或保留有明确 blocker 的 `UNVERIFIED`；给出 Core/Qt adapter 边界建议且不冒充实现批准 | **PASS** | 报告 §4：3 条已证实 + 1 条保留 `UNVERIFIED`（QML/QQuickWindow 在 offscreen/minimal 下未测，blocker 明确）+ 对矩阵分类的建议交 Codex；报告 §5 六条建议并明确"不释放实现、不选型" |
| **R1-AC5** `src/**`、`tests/**`、打包、Schema、依赖、T3.2.1 证据零修改；实验只接触隔离临时数据 | **PASS** | `08-delivery-scope-and-diff-check.log`（`git diff --name-only <base> <delivery>` 全部落在授权路径；`git diff --check` 干净；`src/**`、`tests/**`、`requirements*.txt` 零命中）；`src`/`tests` 内 `__pycache__` 计数 0；生产依赖清单未改；探针不导入 `bootstrap.app`、不开 SQLite、不碰用户数据根 |

## 4. 安全与只读性

- 全部运行使用 `python -B` + `PYTHONDONTWRITEBYTECODE=1`；运行后实测 `src/**`、`tests/**` 内 `__pycache__` 数量为 **0**。
- 探针**只导入** `infrastructure.rendering.*` 与 `ports.rendering.*`（只读），**不导入** `bootstrap.app`、**不打开**任何 SQLite 数据库、**不读写**真实用户数据根。
- 字体补救探测只**读取**系统字体文件（`C:\Windows\Fonts\msyh.ttc`，19,704,352 字节）作为 `addApplicationFont` 输入，未复制、未安装、未修改。
- 隔离 venv 位于 `%TEMP%\M2-R1-venv`，由独立 CPython 3.12.3 创建；生产解释器 `C:\Python314`（3.14.6）与生产 site-packages 未被写入。
- 探针从不创建或 `show()` 任何 `QWindow`；事件循环仅 300 ms 后 `quit()`。

## 5. 冒烟运行与工具记录

- `raw/smoke/` 是本 Task 探针的**首次冒烟运行**（windows 平台，验证探针可运行），其数值与主矩阵 `windows/run1` 一致，但**不作为矩阵证据**，故单列。
- 本 Task 未出现探针缺陷重跑或失败尝试；18 次正式运行全部一次通过。`raw/*/probe.json` 内 `errors` 数组均为空。
- `05-supplementary-font-remediation.log` 与 `06-eventloop-and-window-census.log` 为**补充探测**（超出 AC2 最低要求），用于量化"字体缺失能否补救"与"无 GUI 下事件循环是否稳定退出"。

## 6. 未测项（不构成本清单的覆盖）

QML / `QQuickWindow` / AppShell 在 `offscreen`/`minimal` 下的行为、生产入口 `main()` 三个模式、真实文档端到端渲染链、DPI/多显示器缩放、长期运行与内存、非 PNG 的 imageformats 插件、产品测试套件（`NOT_RUN`）——详见报告 §6。
