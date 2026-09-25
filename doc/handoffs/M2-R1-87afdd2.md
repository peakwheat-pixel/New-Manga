---
task_id: M2-R1
author: DeepSeek Harness
recipient: Codex (independent non-author Review and integration)
base_commit: 6a68fdeb92d8a1c7903166a8076d6260bf8fa79a
delivery_head: 87afdd2e87c46bc8f19d53e932fb641c2457e45b
status: in_review
---

# Handoff — M2-R1 Qt Runtime Feasibility Spike（Delivery `87afdd2`）

## 交付结果

用户批准的 M2 第一波研究任务 M2-R1 已完成并冻结。交付物是**证据与结论**，不是代码：

- 研究报告与平台实测矩阵：[`doc/research/M2-R1_QT_RUNTIME_FEASIBILITY.md`](../research/M2-R1_QT_RUNTIME_FEASIBILITY.md)。
- 原始证据：[`verification/M2-R1/**`](../../verification/M2-R1)（8 个日志/清单文件 + 3 个探针脚本 + 18 次运行的 JSON 与 PNG），索引见 [`07-evidence-manifest.md`](../../verification/M2-R1/07-evidence-manifest.md)，逐文件 sha256 见 [`07b-artifact-hashes.log`](../../verification/M2-R1/07b-artifact-hashes.log)。
- 本 Handoff；[`doc/tasks/M2-R1.md`](../tasks/M2-R1.md) 回填 checkpoint、AC 勾选、测试要求表与 delivery head。

**写集合**：`owner-start`(`5d989ba`) → `delivery`(`87afdd2`) 共改动 **79 个路径**，全部落在本 Task 授权路径（`doc/tasks/M2-R1.md`、`doc/research/M2-R1_QT_RUNTIME_FEASIBILITY.md`、`doc/handoffs/M2-R1-*.md`、`verification/M2-R1/**`）；**越界 0、禁止路径命中 0**（证据：[`08-delivery-scope-and-diff-check.log`](../../verification/M2-R1/08-delivery-scope-and-diff-check.log) §3/§4）。

`src/**`、`tests/**`、`requirements*.txt`、打包、SQLite Schema、`AGENTS.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/09_COLLABORATION.md`、`doc/AD-001_*`、其他 Task/Handoff/Review、`verification/M2-D1/**`、`verification/T3.2.1/**`：**零修改**（同日志 §4/§7）。

## 提交列表

| Commit | 说明 |
|---|---|
| `6a68fde` | 固定代码 base（本 Task 未修改其内容） |
| `58fa0df`、`5d989ba` | Codex 的第一波注册提交（仅 `doc/**`）——Owner 开工起点为 `5d989ba` |
| **`87afdd2`** | **本 Task Delivery**（报告 + `verification/M2-R1/**` + Task 回填） |
| 随后文档提交 | 本 Handoff + `08-*.log` + Task frontmatter / 报告 delivery 回填 |

## 验证证据

| 场景 / AC | 实际命令 / 步骤 | 环境与 commit | 结果 | 日志 / 产物 |
|---|---|---|---|---|
| 固定点 | `git rev-parse --show-toplevel/HEAD/--abbrev-ref HEAD/--git-common-dir/--git-dir`、`git status --porcelain` | Owner worktree，开工 `5d989ba` | PASS（worktree 空、分支与 Task 一致、common dir 为 `G:/CODEX/New Manga/.git`） | `01-environment.log:4-10` |
| AC1 环境与隔离 | 只读引用 `requirements.txt`；在 `%TEMP%\M2-R1-venv` 用独立 CPython 3.12.3 建 venv 并安装 `PySide6_Essentials==6.11.2`；`pip list`、`PySide6.__version__`、`qVersion()`、`QLibraryInfo`、QPA 插件清单、OS 版本 | Windows 11 `10.0.26200`；Python 3.12.3；Qt 6.11.2 | **PASS**（与生产口径匹配 → **不记 BLOCKED**） | `01-environment.log` |
| AC2/AC3 主矩阵 | 3 平台 × 3 次独立进程：`python -B verification/M2-R1/probes/qt_platform_probe.py --platform <p> --json ... --workdir ...`（`QT_QPA_PLATFORM` 在 import PySide6 前设置；`PYTHONDONTWRITEBYTECODE=1`） | 隔离 venv；`windows`/`offscreen`/`minimal` | **PASS**：9 次全部 `EXITCODE=0`、`errors=0`；windows families=221、offscreen/minimal=0；同一平台 3 次 PNG sha256 完全一致 | `02-probe-windows.log`、`03-probe-offscreen.log`、`04-probe-minimal.log`、`raw/<platform>/run{1,2,3}/` |
| AC2 无可见 GUI | Win32 `EnumWindows` 枚举本进程顶层 HWND（类名/标题/`IsWindowVisible`）；`qt_eventloop_probe.py` 跑 `QTimer(300ms)` + `exec()` | 同上，3 平台 × 2 次 | **PASS**：windows 3 个 HWND **0 可见**（`Qt6112ThemeChangeObserverWindow`、`Qt6112ScreenChangeObserverWindow`、`IME`）；offscreen/minimal **0 个 HWND**；`exec()` 全部返回 0，0.31 s 量级退出 | `06-eventloop-and-window-census.log` |
| AC3 补充：字体补救边界 | `qt_font_remediation_probe.py`：offscreen/minimal × {baseline, `QT_QPA_FONTDIR`, `addApplicationFont(msyh.ttc)`} | 同上 | **PASS（探测）**：offscreen+appfont → families=2、`fm.height=42`、真实字形；minimal+appfont → **返回 id=-1，无效**；`QT_QPA_FONTDIR` 仅对 offscreen 有效（families=68） | `05-supplementary-font-remediation.log`、`raw/supp-*/` |
| AC4 M2D1-22 收敛 | 报告 §4 逐条对照原夹具陈述；区分"已证实 / 保留 UNVERIFIED" | 同上 | **PASS**：3 条已证实 + 1 条保留 `UNVERIFIED`（QML/`QQuickWindow` 在 offscreen/minimal 下未测，blocker 明确） | 报告 §4 |
| AC5 只读范围 | `git diff --name-status/--stat/--check owner-start..delivery`；授权路径断言；`src`/`tests` 的 `__pycache__` 计数；依赖清单检出 | `87afdd2` | **PASS**：越界 0；`git diff --check` `exit=0`；`__pycache__`=0；`requirements*` 未改；探针 0 处 import `bootstrap`/`sqlite3` | `08-delivery-scope-and-diff-check.log` |
| 产品测试 | — | — | **NOT_RUN**（`src/**` 零修改；实验 venv 只装 Qt 栈，未装 pytest/torch 等），**不得记为 PASS** | — |

**探针安全与只读性**：探针只读导入 `infrastructure.rendering.*` 与 `ports.rendering.*`，**不导入** `bootstrap.app`、**不打开**任何 SQLite、**不读写**用户数据根；全部运行 `python -B` + `PYTHONDONTWRITEBYTECODE=1`，运行后 `src/**`、`tests/**` 内 `__pycache__` 计数为 **0**；字体补救只**读取** `C:\Windows\Fonts\msyh.ttc`（19,704,352 字节），未安装/未复制；探针从不创建或 `show()` 任何 `QWindow`。本 Task 无失败重跑，18 次正式运行一次通过（`raw/*/probe.json` 的 `errors` 均为空）；`raw/smoke/` 为探针首次冒烟运行，**不作为矩阵证据**。

## AC 对照

| AC | 结果 | 证据 |
|---|---|---|
| R1-AC1 环境/版本/隔离 | PASS | `01-environment.log`；报告 §2（含"与生产口径匹配，不记 BLOCKED"的裁定与限制） |
| R1-AC2 三平台四组件实测 + 无可见 GUI 证据 | PASS | `02/03/04-probe-*.log`、`06-eventloop-and-window-census.log`；报告 §3.1–§3.3 |
| R1-AC3 重复运行/退出码/失败类型/Hash·尺寸、区分部分可行组合 | PASS | 9 次 `EXITCODE=0`；PNG sha256 跨 3 次一致；报告 §3.1/§3.4/§3.5（`windows` PASS / `offscreen` PARTIAL 可补救 / `minimal` PARTIAL 不可补救） |
| R1-AC4 M2D1-22 收敛 + adapter 边界建议（不冒充批准） | PASS | 报告 §4（含保留 `UNVERIFIED` 与 blocker）、§5（六条建议，明确不释放实现、不选型） |
| R1-AC5 零修改与隔离（Owner 侧） | Owner 侧 PASS，**保持未由 Owner 关闭** | `08-*.log` §3/§4/§7；Task 完成 Gate 需 Codex Review 与集成后才关闭 |

## 关键结论摘要（供 Review 使用）

1. **M2D1-22 不再是 `UNVERIFIED`**：`windows`/`offscreen`/`minimal` 三平台下 `QGuiApplication`、`QFontDatabase`、生产 `QtTextLayoutEngine`、生产 `QtImageCompositor` **均可装配执行**，无可见 GUI，可重复，退出码 0。
2. **仓库夹具陈述成立**：`offscreen`/`minimal` 默认 `QFontDatabase.families()==0`（windows 221）；但真正的问题是**语义**而非可用性——文本渲染输出**实心替代方块（tofu）**、度量退化（`height=32`、`descent=0`、`inFont=False`），且**没有任何错误信号**（仅 `available=False`/`font_available=False`），compositor 照常出图。
3. **平台能力分级**：`windows` ⊃ `offscreen(+显式字体)` ⊃ `offscreen 默认` ⊃ `minimal`；`minimal` 对字体注入完全无响应（`addApplicationFont` 返回 `-1`），是本环境下唯一"连补救都不成立"的平台。
4. **不得跨平台外推**：offscreen 与 minimal 的输出 PNG 逐字节相同、且与 windows 不同——这为 Task 禁止范围"不把 offscreen 的成功推广为 windows/minimal 成功"提供了直接实测依据。
5. **对 M2-D1 矩阵的建议（交 Codex 决定，作者未改矩阵）**：建议把 M2D1-22 从独立 `UNVERIFIED` 切片改标为**已实测平台约束**，并作为 M2D1-13（`QtFontCatalog`）/ M2D1-14（`QtTextLayoutEngine`）REPLACE 候选的输入证据与硬约束（"字体来源必须显式、可注入、可诊断"）。
6. **唯一保留的 `UNVERIFIED`**：QML / `QQuickWindow` / AppShell 在 `offscreen`/`minimal` 下的行为本 Task 未测，**不得由本报告推断其可用或不可用**。

## 接收方式

Review 固定 base=`6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`、owner-start=`5d989bab6c5c8a24a5112303f95c2b8eea356bdc`、reviewed_head=`87afdd2e87c46bc8f19d53e932fb641c2457e45b`，并核对随后仅追加本 Handoff、`08-*.log` 与 frontmatter/报告 delivery 回填的文档提交。

复现（需要网络安装隔离 venv；不触碰生产解释器与依赖清单）：

```powershell
Set-Location 'G:\CODEX\New Manga.worktrees\M2-R1-deepseek'
$venv = Join-Path $env:TEMP 'M2-R1-venv'
& 'C:\Users\49745\AppData\Local\Programs\Python\Python312\python.exe' -m venv $venv
& "$venv\Scripts\python.exe" -m pip install 'PySide6_Essentials==6.11.2' 'shiboken6==6.11.2'
$env:PYTHONDONTWRITEBYTECODE = '1'
foreach ($p in 'windows','offscreen','minimal') {
  & "$venv\Scripts\python.exe" -B verification\M2-R1\probes\qt_platform_probe.py `
      --platform $p --json "$env:TEMP\$p.json" --workdir "$env:TEMP"
  "EXIT=$LASTEXITCODE"   # 期望 0
}
& "$venv\Scripts\python.exe" -B verification\M2-R1\probes\qt_eventloop_probe.py --platform windows --json "$env:TEMP\loop.json"
```

请覆盖 Architecture 与 Verification 两面：`UNVERIFIED`/`PARTIAL`/`NOT_RUN` 是否被误记为 PASS、平台结论是否被跨平台外推、`git diff --check` 与零修改断言是否成立、探针是否只读且未触真实数据根、以及 §5 建议是否越权（本 Task 不授权实现）。Reviewer 以单独 Review 文件记录结论，不改作者文档。若需修订返回 `changes_requested`；approved 后由 Codex 集成并把 M2-R1 标 `done`。

## 下一任务建议（必填）

- **Task / 标题**：**无需立即释放新 Task**；建议 Codex 先把本 Task 的 M2D1-22 收敛结论与 §5 建议**登记进 M2 规划**（更新 [REBASELINE_PLAN](../REBASELINE_PLAN.md) / [STATUS](../STATUS.md) 中 M2D1-22 的状态与 M2D1-13/14 的输入约束），再决定是否释放后继切片。若需要后继切片，本文证据支持的最小候选是 **「QML/QQuickWindow 在 offscreen/minimal 下的入口可行性」**（本 Task 唯一保留的 `UNVERIFIED`），或 **「渲染端口实现的字体来源与可诊断性设计」**（对应 M2D1-13/14）。
- **推荐 Agent / Reviewer**：Owner 建议 DeepSeek Harness（研究/实验面，具备本次探针与环境的可复用经验）；Reviewer 必须是 Codex（禁自审）。若未来切片涉及生产代码实现，Owner 应改由 ZCode/Antigravity 承担，DeepSeek Harness 转任非作者 Reviewer。
- **推荐原因与前置依赖**：QML 入口切片依赖本 Task Review `approved` 且 Codex 已登记 M2D1-22 的新状态；字体来源切片依赖 M2D1-13/14 的决策方向由 Codex/用户裁定（**属产品取舍，不得由研究者自决**）。
- **Recovery point**：仓库 `G:/CODEX/New Manga`；本 Handoff 固定 reviewed_head=`87afdd2`；新 Task 的 base 应在 M2-R1 集成后由 Codex 固定；branch/worktree **待 Codex 创建**，不得复用本实验 worktree。
- **允许修改路径**：待 Codex 冻结；预期仍为 `doc/tasks/<新 ID>.md`、`doc/research/**`、`doc/handoffs/**`、`verification/<新 ID>/**`。
- **禁止范围与新增授权条件**：禁改 `src/**` 生产代码、`tests/**`、打包、依赖清单、Schema、QML、T3.2.1 证据与历史 `verification/**`；不得把研究结论当作实现授权；字体来源/度量栈的技术选型必须由 Codex/用户另行裁定。
- **交付物**：新研究报告 + `verification/<新 ID>/**` 原始日志（含命令、环境、HEAD、原始输出、退出码、Hash）+ Handoff。
- **验证命令、环境与完成 Gate**：隔离 venv（匹配生产 Python 3.12 + PySide6 6.11.2）逐平台独立进程复现；`UNVERIFIED`/`NOT_RUN` 照实标记；完成 Gate = Codex 非作者 Review `approved` + 集成。
- **可直接转发给 Agent 的指令**：见下方"下一步"段落（在 Codex 冻结 Task 之前，本切片**尚未释放**，请勿自行启动）。

## 风险与遗留

- **本报告是研究结论，不构成任何实现授权**：未选择字体/度量/合成替代技术，未提出依赖变更。
- **保留的 `UNVERIFIED`**：QML/`QQuickWindow` 在 `offscreen`/`minimal` 下的行为；生产入口 `main()` 三个模式；真实文档端到端渲染链。
- **`minimal` 的 `addApplicationFont` 返回 `-1` 是 Qt 6.11.2 的实测事实**，不保证跨 Qt 版本不变。
- **`QT_QPA_FONTDIR` 在 offscreen 下未收录 `msyh.ttc`（TTC 集合）**，只收录部分 TTF；本 Task 未追查根因，仅记录现象。
- **产品测试 `NOT_RUN`**（源码零修改且实验环境未装测试依赖）。
- 本 Task **不改变** T3.2.1 Gate（`OPEN`/AC3 `BLOCKED`）与 M2 其他三个 Task（I1/I2/UI1）的任何状态；研究结论不得扩大其写集合。

## 实验附录（仅实验任务）

- **数据来源与许可**：无外部数据集。合成基准图由探针内纯 `zlib`/`struct` 生成（`sha256 a5f9021b…`，682 字节），确定性可复算。
- **模型/权重**：不适用（未调用任何模型）。
- **Provider / Runtime**：PySide6_Essentials 6.11.2 + shiboken6 6.11.2 + Qt 6.11.2（`cp310-abi3-win_amd64` wheel，来自配置的 PyPI 镜像），运行于 CPython 3.12.3 隔离 venv。
- **字体输入**：`C:\Windows\Fonts\msyh.ttc`（19,704,352 字节，只读）用于 `addApplicationFont` 补救探测；未改变系统字体配置。
- **硬件 / 网络策略**：本机 Windows 11 `10.0.26200`，2 屏（主屏 2560×1440）；仅安装阶段需要网络（PyPI 镜像），实验本身离线。
- **参数**：`QT_QPA_PLATFORM` ∈ {windows, offscreen, minimal}；文字 `漫画排版テスト Manga`（横向，32 px，含 2 px 描边）、`縦書きテスト`（竖向，28 px）；基准图 600×200 白底；事件循环 `QTimer` 300 ms。
- **运行次数**：主矩阵 3 平台 × 3 次；字体补救 5 条件 × 1 次；事件循环 3 平台 × 2 次；合计 18 次独立进程，全部退出码 0。
- **原始结果**：`verification/M2-R1/raw/**`（JSON + PNG）；逐文件 sha256 见 `07b-artifact-hashes.log`。
- **质量判断办法**：不采信"退出码 0 或 PNG 非空"；用 `inFont()`/`families()`/`hasFamily()` 判定字形可用性，用与输入基准图的逐像素差异数 + 人眼复核 PNG 判定渲染真实性，用跨进程 sha256 判定确定性。
- **失败样例与限制**：无失败运行；限制见报告 §6（QML 未测、DPI/多屏未测、长期运行未测、非 PNG imageformats 未测、`minimal` 补救失败）。
- **Secret**：本 Task 不涉及任何凭据，报告与证据中不含 Secret。
