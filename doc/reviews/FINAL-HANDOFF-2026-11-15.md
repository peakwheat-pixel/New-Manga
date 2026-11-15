# 最终交接摘要（2026-11-15，goal 100 轮收尾）

基线 `6ca93fa0b`。一页纸：**现状 → 剩余 → 怎么接手**。

---

## 1. Gate 判定

**`BLOCKED`** —— 但**"可评估"已达成**（六条各有明确判定、实测依据、谁可提供）。

**"通过"未达成，我不把它写成通过。**

| 条件 | 状态 | 剩什么 |
|---|---|---|
| **1** | ✅ **MET** | 8 项 finding **逐项开文件核实**；L-R1-1 四项有源码+测试+**图**三重证据 |
| **2** | ✅ **MET** | 调查完成；处置四项需 Owner 授权 |
| **3** | **接近满足** | **真机物理屏幕上的显示**（headless 与安装产物截图都已具备） |
| **4** | **AC1–AC6 ✅ / AC7 5/5 页** | 签名（GitHub 两步）；0.1.1 逐条断言（需重装） |
| **5** | **`NOT_RUN`** | 人工 GT（有书面判据：V1 审计 `05:20`） |
| **6** | ✅ **MET** | — |

---

## 2. 本会话最重要的一个技术突破

**根因**：`Start-Process` **cmdlet** 在本环境挂起；`[System.Diagnostics.Process]::Start(ProcessStartInfo)` 正常（**26 ms 返回**）。

**⇒ 从此 Agent 能自行启动 GUI 并截图。** 这条解开了条件 3 / 条件 4 AC7 的整个僵局。

> **我此前的诊断"GUI 无法在窗口站初始化"是错的**，已在 `RELEASE-GATE-RE-ASSESSMENT` §3 与
> `GATE3-FOUR-PAGE-WALKTHROUGH-1` §9.6 更正。

---

## 3. 视觉证据清单（三类，互补）

| 类型 | 位置 | 说明 |
|---|---|---|
| **安装产物真截图** | `verification/GATE3-FOUR-PAGE-WALKTHROUGH-1/installed/` | 5/5 页；`host.log` 实测 `core_service ready`+`host_bridge ready`；**逐张目视确认** |
| **源码构建真截图** | `verification/GATE3-FOUR-PAGE-WALKTHROUGH-1/` | 同上（修复了"截早了"） |
| **headless 渲染** | `verification/FEA-06-RESIDUAL-1/png/`（四页）<br>`verification/READER-OVERLAY-HEADLESS-PNG-1/`（沉浸阅读器）<br>`verification/L-R1-1-VISUAL-EVIDENCE-1/`（四项控件） | 1180×780 / 1024×768；`Window.CaptureRenderedFrame()` |

**四页** = 资料柜 / 工位 / 控制台 / 阅读器（overlay）。
**`--page=settings` → 控制台空间；`--page=reader` → 资料柜空间**（阅读器是 Library 内 overlay，需 F11）。

---

## 4. 三条待人工（成本都很小）

| # | 事项 | 成本 | 一次解锁 |
|---|---|---|---|
| **1** | 打开已安装 app（`%LOCALAPPDATA%\Programs\NewManga\app\NewManga.App.exe`），点四页 + 在资料柜按一次 **F11** | ~3 分钟 | 条件 3 物理显示 + AC7 阅读器 + L-R1-1 可见性 |
| **2** | GitHub 两步：默认分支 → `public-release`；Actions → `build-release` → Run（`version=0.1.1`、`sign=false`） | ~2 分钟 | 签名路径（**不需买证书**，SignPath 免费 OSS 通道） |
| **3** | 质量基线判断，或明确接受 `NOT_RUN` | 取决于你 | 条件 5 |

**第 2 项的凭据状态已实测**：`gh auth status` → 未认证；`GH_TOKEN`/`GITHUB_TOKEN` 均 unset。

---

## 5. 一件我判断"能做但不该做"的事

**重打包补 SFX 权重 / 重跑安装矩阵**。

- **技术上完全可行**（setup.exe 齐全、脚本齐全）
- 但**会三次卸载/重装用户机器上的软件**
- 我的判断：**收益（证据从汇总升到逐条）< 风险（可能留下半装的系统）**
- 完整执行步骤与风险清单在 `verification/INSTALLER-011-ASSERTION-PLAN-1/`

**⇒ 需要你一句"可以动我的安装"我才做。**

---

## 6. 本会话我犯的 14 个错误（全部原样登记）

| # | 错误 | 类型 |
|---|---|---|
| 1 | `L-F1-3` 判"需真人定义口径" | 没读裁决 |
| 2 | `E-9` 判"需新增持久化"，前提"root==父目录"错 | 没读实现 |
| 3 | `yolo11s-seg.onnx` 判"全盘不存在" | 搜索范围不完整 |
| 4 | 签名判"需买证书" | 没查路径 |
| 5 | `reader` 判"必须按键" | 没读命令链 |
| 6 | `INSTALLER-MATRIX-1` 未查实物就改状态 | 先改后查 |
| 7 | 只搜 `*.axaml` 说控件不存在 | 搜索范围不完整 |
| 8 | **"GUI 无法启动，根因窗口站"（诊断错误）** | 推断替代核实 |
| 9 | "截早了"误判成"数据根不一致" | 归因错误 |
| 10 | "模型已就位"说得像交付包也完整 | 表述过宽 |
| 11 | 说"做尽"但没 grep 现成能力 | 搜索范围不完整 |
| 12 | 计划写新测试（一条 env 变量就够） | 搜索范围不完整 |
| 13 | 写 `FEA-06-RESIDUAL-1/png/` 后才查 | 先做后验 |
| 14 | **跑 capture 变量覆盖了 `FEA-06-RESIDUAL-3` 的 5 个文件** | 先做后验 |

**错误集中在两类**：**搜索范围不完整**（3/7/11/12）与**先做后验**（6/13/14）。

**固化的规则**：
1. 宣布"不存在/做尽"之前，必须证明搜索覆盖了**所有可能的实现形式**（XAML / C# 构建 / git 索引 / 文件系统 / **测试目录**）；
2. 任何 `NEWMANGA_CAPTURE_*` 运行前，**先读它的写盘路径并 `git status` 该目录**。

---

## 7. 怎么接手

**先读这三份**（按顺序）：

1. `doc/reviews/EVIDENCE-INDEX-2026-11-15.md` —— 按条件导航到每项证据
2. `doc/reviews/RELEASE-GATE-RE-ASSESSMENT-2026-11-15.md` —— 判定口径 + 六条判定 + **§10/§11 最终口径**
3. `doc/reviews/RELEASE-GATE-HANDOFF-2026-11-15.md` —— 四项阻塞四元组

**四件套**（每轮必跑）：

```powershell
pwsh -NoProfile -File tools/governance/check.ps1            # PASS + 3 warnings
pwsh -NoProfile -File tools/governance/verify_pins.ps1      # 18/18
python tools/generate_api_inventory.py --check              # 1/80/6=87
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests  # 955/0/11/966
```

**两块要留意的"记录卫生"问题**（不是缺陷，是表格陈旧）：

- `doc/tasks/CHAPTER-MANUAL-SORT.md`：`status: done` 但 **AC1–AC10 全未勾**（实现确实完整，见 `CHAPTER-MANUAL-SORT-VERIFY-1`）
- `doc/tasks/GATE4-PAGES-UPGRADE-1.md`：`status: done` 但 AC 表停在 `NOT_RUN`（实物证据在 workspace）

---

## 8. 一句话

**Gate 没有通过；但每一条"为什么没通过""谁能补""证据在哪"都写下来了，而且每一处都经得起第三人打开复核 —— 包括我自己的 14 次误判。**
