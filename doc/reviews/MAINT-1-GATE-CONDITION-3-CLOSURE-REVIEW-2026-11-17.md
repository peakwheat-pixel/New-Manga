---
task_id: [MAINT-1-RELEASE-MONITOR]
kind: closure-review
reviewer: reviewer-c3
reviewer_kind: subagent
reviewer_source: lead 派发的独立上下文子 agent（`reviewer-c3`）；未参与条件 3 的取证、视觉裁定或关闭决策
author: DSH（Lead / Architect / Integrator）
base_commit: fa190a5a8
reviewed_head: 128e3074c
reviewed_at: 2026-11-17T20:00:00+08:00
subject: Release Gate 条件 3 关闭决策（"F11 沉浸阅读器全屏/无边框视觉"由 3 份书面视觉裁定关闭）
decision: ACCEPTED_WITH_FINDINGS
p0: 0
p1: 1
p2: 8
---

# Review：Release Gate 条件 3 关闭决策（2026-11-17）

> **decision 口径**：本文件按派发要求使用 `ACCEPTED` / `ACCEPTED_WITH_FINDINGS` / `REJECTED`，**不等同** REVIEW 模板的
> `approved`——本复核不构成集成批准、不构成产品发布验收、不构成人眼验证。按模板门槛，P1 未处置前不得把本文件当作
> "条件 3 记录无缺陷"的证明。

## 0 身份、时间、边界与方法

| 项 | 内容 |
|---|---|
| Reviewer | `reviewer-c3`（独立上下文子 agent，lead 派发） |
| 独立性 | 未参与条件 3 的取证、截图、三份视觉裁定、D9 立卡或关闭决策；只读仓库与本机环境 |
| 被审 head | `128e3074cc19e37ffbee05ee5b06ef00f569a154`（`128e3074c`，main，工作区 clean） |
| 复核时间 | 2026-11-17T20:00:00+08:00（+08:00） |
| 写入 | 仅本文件；未提交、未推送、未 checkout、未改任何被审文件 |
| 方法 | Git 对象核对 / 6 图 `Get-FileHash -Algorithm SHA256` / Pillow+numpy 像素复算（inline，无中间文件）/ 文档逐条比对 / 两条 `check.ps1` / `task_ledger.py` 只读运行 / 本机 OS·DPI·屏幕实测 |

**边界**：本复核判断"条件 3 的关闭决策是否站得住"，**不**评估条件 4/5，**不**把 Gate 总体或 `Technical Gate` 改成通过，
**不**替代人眼验收，**不**重新裁定阅读器视觉本身（只核其证据与推理是否可复核）。

## 1 被审对象

`128e3074c`（DSH，2026-11-17 19:50:44 +0800）共 8 个文件、+274/−11：

| 文件 | 变化 |
|---|---|
| `doc/reviews/MAINT-1-GATE-CONDITION-3-VISUAL-ADJUDICATION-2026-11-17.md` | +148（第三次裁定 `visual-c3c`） |
| `doc/tasks/READER-F11-STYLE-SCOPE-1.md` | +82（D9 新卡，`proposed`） |
| `verification/MAINT-1-RELEASE-MONITOR/condition3/README.md` | +16/−1（D7/D8/D9 更正） |
| `doc/reviews/RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md` | +11/−1（§3 判定 + 更正说明） |
| `doc/tasks/MAINT-1-RELEASE-MONITOR.md` | +13（关闭依据与仍不覆盖项） |
| `doc/TASK_LEDGER.md` | +7/−4（新增 1 张非终态卡） |
| `doc/STATUS.md` | +1/−1（条件 3 措辞；**同时删掉条件 4 的限定词**，见 F-3） |
| `doc/REBASELINE_PLAN.md` | +1/−1（表外节点加 `READER-F11-STYLE-SCOPE-1`） |

关闭依据链（4 层）：证据 `condition3/`（6 图 + README）→ 3 份裁定（同一文件 3 节，append-only）→ 授权路径
`CODEX-RULING-CORE-ENV2-FEA11-GATE-2026-11-17.md` Q3 → 落状态（§3 判定行、`STATUS:8`、`MAINT-1` 卡、新卡）。

## 2 七项逐条判定

| # | 必测问题 | 实测 | 判定 |
|---:|---|---|---|
| 1 | 五项最低证据是否齐备 | 见 §2.1：4 项满足、1 项（Windows 版本）**记录失真** | **部分不通过（F-1）** |
| 2 | 截图真实性 / 非 headless | 6 图 sha256 全部与 README 一致；**全部可回指到 workspace 原始捕获**（3 组逐字节相同、1 组同帧 JPEG 再编码）；画面含任务栏/时钟/副屏桌面像素 | **通过** |
| 3 | 裁定者独立性 / 像素级测量 | 3 名具名子 agent、append-only（3 提交 0 删除）、无 Lead 自审迹象；bbox/MAD/差分数字可复现；workspace 有 c3b 放大裁剪、c3c 分析脚本 | **通过（口径有 F-7）** |
| 4 | 关闭是否越权 / 是否把 NOT_RUN 说成通过 | 只改 §3 overlay 一行；skip/崩溃点/四页证据未动；新卡 AC 记 `NOT_RUN`；条件 4/5 状态未变 | **通过（记录层 F-3/F-4/F-5）** |
| 5 | D9 是否掩盖 / 是否否定关闭 | D9 像素级复现；已单独立卡、已披露；属**外壳一致性**缺陷，不是"全屏/无边框"缺陷 | **不否定关闭（限定后成立）** |
| 6 | 门禁 | 两条 `check.ps1` 均 `PASS (3 warnings)`、`EXIT=0` | **通过（台账漂移 F-6）** |
| 7 | 是否越界改条件 4/5 或 Technical Gate | `Technical Gate=NOT_SATISFIED` 原样；§4/§5 未改；`Release Gate BLOCKED` 原样 | **通过（STATUS 措辞弱化 F-3）** |

### 2.1 Codex Q3 五项最低证据逐条

Q3 原文（`doc/reviews/CODEX-RULING-CORE-ENV2-FEA11-GATE-2026-11-17.md:53`）："固定产品 head 与 exe hash；在真实窗口触发 F11
后保存原始截图；记录 Windows 版本、分辨率、DPI 与操作步骤；由未参与实现的 Codex 新上下文或 ZCode 对截图……作出具名书面判断，
并附截图 hash。"

| 项 | 实测 | 结论 |
|---|---|---|
| ① 产品 head + exe hash | exe 实测 `99,554,850 B`、`sha256=a3ec2133…739230`、`ProductVersion=0.1.1+71cecb95a10c42ffe02d1396ab065e1fc9c43ca9`（= 构建 head `71cecb95a`）；`condition3/README.md:9` 记了 exe sha256，**未记 head**；head 在 `verification/INSTALLER-MATRIX-1/README.md:25`（`app_build.repo_head`）与 exe 内嵌版本号可查 | **实质满足**（exe hash 直钉 + head 链上可取）；记录不全 → **F-2** |
| ② 真实窗口 F11 原始截图 | 6 图齐全；`c3-01/02`、`c3-03/04` 与 workspace 原始 PNG **逐字节相同**；`c3-05/06` 为同帧无损 PNG 的 q90 再编码（`mean\|Δ\|=1.176/1.175`）；三组均含真实桌面要素（见 §3） | **满足** |
| ③ Windows 版本 / 分辨率 / DPI | 分辨率 `2560×1440`、工作区 `2560×1392`（48 px 任务栏）、`AppliedDPI=96` 实测一致；**OS 记录不符**：文档写 `Windows 10 Pro / 2009 / build 26300`，本机实测 `Windows 11 专业版 / 26H2 / 10.0.26300.9711` | **不满足 → F-1** |
| ④ 操作步骤 | 第一组：启动→等 Host 就绪→截书架→`{F11}`→截；第三组：UIA `InvokePattern.Invoke()` 名为 `阅读` 的按钮→等 8 s→截→`{F11}`→等 8 s→截（`README.md:88-92`，采集脚本 `workspace\tmp\r22\capture-content3.ps1:31-65` 逐行对应） | **满足** |
| ⑤ 具名独立裁定 + 截图 hash | `visual-c3`/`visual-c3b`/`visual-c3c` 三名分节署名，各节含逐图 sha256 与判定；三段 append-only | **满足**（口径偏差 F-7） |

## 3 截图真实性：六图哈希与"非 headless"证据

命令：`Get-ChildItem condition3\*.png,*.jpg | Get-FileHash -Algorithm SHA256`，`.Hash.ToLower()` 与 `README.md` 逐字比对。

| 文件 | 尺寸 | 字节 | 实测 sha256 | README 记录 | 一致 |
|---|---|---:|---|---|---|
| `c3-01-library.png` | 2576×1408 | 112,324 | `c96f2c9ab1c073f9e1e47cbd6196143fa1b659e08cd600348a36a082801c6f1b` | 同左 | ✅ |
| `c3-02-f11-immersive-empty.png` | 2576×1408 | 46,166 | `108258b9ea37a9f3b752ba77766221b14a8b6fe61305c424ca746bb685829e76` | 同左 | ✅ |
| `c3-03-library-fullscreen.png` | 2560×1440 | 182,597 | `ef60d9ffc53c2820dcf55d328e2b9f67d26b301d4c7c5285ecc6bdb96d591c66` | 同左 | ✅ |
| `c3-04-f11-immersive-fullscreen.png` | 2560×1440 | 24,006 | `2183198b8daba875208c92efbbcfdca68374ab398f45a8c300115b072ee3d384` | 同左 | ✅ |
| `c3-05-reader-open-content.jpg` | 2560×1440 | 580,150 | `ba7b39fcae4cb634e18e4218f1dad5d4f190a41ece7cebe8cfd3ce7c65cfba6d` | 同左 | ✅ |
| `c3-06-f11-immersive-content.jpg` | 2560×1440 | 587,108 | `8ce0fc0a1a0c8cfc88b4179105da5083e4486fc0253190946635c749dae15535` | 同左 | ✅ |

**六图全部一致**，且三份裁定里引用的 hash 与上表相同（无二次改写）。

**原始捕获回指**（我单独做的比对，不是引用裁定）：

| 提交图 | workspace 原始文件 | 比对结果 |
|---|---|---|
| `c3-01` | `tmp\r20\f11c\01-library.png`（112,324 B） | sha256 前缀 `c96f2c9a` 相同、像素差 **0** |
| `c3-02` | `tmp\r20\f11c\03-f11-reader.png`（46,166 B） | sha256 前缀 `108258b9` 相同 |
| `c3-03` | `tmp\r20\f11e\01-library-fullscreen.png`（182,597 B） | sha256 **完全相同** |
| `c3-04` | `tmp\r20\f11e\02-f11-immersive-fullscreen.png`（24,006 B） | sha256 **完全相同** |
| `c3-05` | `tmp\r22\f11c\01-reader-open.png`（6,089,406 B） | 同帧，q90 再编码 `mean\|Δ\|=1.176`、`p99=8`、`max=132` |
| `c3-06` | `tmp\r22\f11c\02-f11.png`（6,630,224 B） | 同帧，q90 再编码 `mean\|Δ\|=1.175`、`p99=8`、`max=128` |

**非 headless 判定（四项独立证据）**：

1. **画面里有任务栏**：`c3-01` `y1400..1407` 条带 669 种颜色、均值 `(212,217,219)`；`c3-03` `y1392..1439` 2,673 种颜色、
   与画布同色 0%；`c3-05` 同带含搜索框/图标/时钟（`19:18`）与 `中/拼` 托盘文字。
2. **画面里有桌面像素**：2576 宽的 `c3-01/02` 右缘 `x2568..2575` 有 685–739 种颜色（壁纸样），上/左 8 px 为纯黑
   （`px(0,0)=(0,0,0)`，整行整列单色）——与 `GetWindowRect` 起点 `(-8,-8)` 的几何一致；本机确实有 `DISPLAY2`（`x=2560`）。
3. **有真实进程日志**：`c3-host.log` 含 `single-instance acquired`（命名互斥）、`core_service ready`、`host_bridge ready`、
   `credential port ready (Windows Credential Manager)`、`source watcher armed`；`c3-startup.log` 有 Avalonia 真实绑定错误
   （无交互桌面/离屏渲染不会有这类真实 shell 会话痕迹）。
4. **采集方式**：`capture-content3.ps1:34` 用 `Graphics.CopyFromScreen(0,0,…)` 整屏抓取；`:63` 用 `SendKeys.SendWait('{F11}')`
   向真实前台窗口发键；`:57` 用 UI Automation 的 `InvokePattern` 点真实按钮。

⇒ **不是 headless 渲染或合成图**。`c3-02` 与 `c3-04` 里任务栏带被画布覆盖，是"真全屏窗口覆盖任务栏"的**同位置正/负对照**，
不是"没拍到"。

## 4 裁定者独立性与像素级可复核性

### 4.1 独立性

- 三节裁定分别署名 `visual-c3`（19:00:10）、`visual-c3b`（19:10:56）、`visual-c3c`（19:46:01），均声明"独立会话上下文；
  未参与阅读器/overlay 实现、返修、取证、截图生成或前次裁定"。
- Git 历史显示该文件由 **3 个提交** append-only 增长：`f1860fe4b` +194/−0、`6a004f689` +159/−0、`128e3074c` +148/−0
  （`git log --numstat -- <file>`）⇒ 后两次裁定**没有改写**前一次的任何字节，符合"独立成节"的自述。
- workspace 有第三方痕迹可佐证真的做了像素工作：
  `tmp\visual-c3b\`（`f11_bottom_left_x6.png`、`f11_bottom_right_text_x14.png`、`f11_top_left_x6.png` 等放大裁剪）；
  `tmp\visual-c3c\`（`analyze1.py`、`bands.py`、`chips.py`、`compare.py`、`crops.py`、`edges.py`、`exe.py`、`db.py` 等 12 个脚本）。
- **无 Lead 自审迹象**：Lead（DSH）写的是证据 README、Gate 文档与状态；三份裁定是它们的输入而非产物。
- 独立性可核验性的弱点：只记 Agent 名，无 session/subtask ID、无派发记录入仓（本仓其他 Review 通常带 `session-…`/`workflow-…`）；
  `visual-c3`/`visual-c3b` 没有留下 workspace 目录。规则允许"Agent 名"（2026-10-31 用户裁决），故不判违规 → **F-7**。

### 4.2 像素级测量：我复算的结果

以下全部由我在被审 head 的图像上重算（非引用裁定文字）：

| 裁定量 | 裁定值 | 我的实测 | 结论 |
|---|---|---|---|
| `c3-02` 沉浸面 ink | 4,936 px / 0.138% | **4,936 px / 0.1377%** | 精确复现 |
| `c3-02` ink 列簇 | 25..83、109..132、2347..2398、2403..2516、2530..2550 | 25..48 / 56..83、109..132、2347..2398、2403..2516、2530..2550 | 精确复现 |
| `c3-02` `y≥1330` ink | 0 | **0** | 精确复现 |
| `c3-03` / `c3-04` 任务栏带 | 2,673 / 78 色；F11 91.9% 画布 | **2,673 / 78 色；91.89%** | 精确复现 |
| `c3-04` 底部带列簇 | 17..52 / 75..110 / 128..2456 / 2465..2477 / 2486..2551 | 同左（`2465..2477` 后拆成 2486..2507、2509..2511、2519..2551 三段字形） | 复现 |
| `c3-04` 底/左/右留白 | 下 16 行、左 17、右 8 | 下 16 行 ink=0、左 16 列 ink=0、右 8 列 ink=0 | 复现 |
| `c3-05↔c3-06` 同帧平移 67 行 | 2,296,160 px 差异 0 | 最优 `dy=67`；2540×904=**2,296,160 px**；maxdiff **1**、仅 2,862 px 差 1（0.06%）、MAD 0.0007 | **实质复现**（无损 PNG 上；裁定用"差异 0"是同一区域的四舍五入表述） |
| JPG↔原 PNG 同帧 | `mean\|Δ\|=1.176` | `1.176` / `1.175`，p99=8 | 精确复现 |
| D9 chip 高亮 | c3-05 有 Accent、c3-06 无 | c3-05 顶带 `(150,101,26)` 邻近色 **62 px**（bbox x2416..2523 / y77..106）；c3-06 全帧仅 **1 px** | 复现 |
| 页面内容非白占比 | 73.00% | 72.56%（阈值 `<245`、区域 1341×2542） | 口径差 0.44 pp |
| `c3-04` 画布占比 | 98.9031% | 98.6979%（精确画布色 3,638,401/3,686,400） | **差 0.205 pp（≈43 px），口径未复现**；不影响结论 |

⇒ 三份裁定的关键数字**不是编的**，主要量可逐项复现；两处小差异（画布占比、非白占比）属阈值/区域口径差异，未达 finding 级别，仅登记。

## 5 关闭是否越权

### 5.1 条件 3 的其余子项

| 子项 | 文档状态 | 我的核对 |
|---|---|---|
| 四页 × 关键流程覆盖矩阵 | ✅（经 r1/r2/r3 复核） | `doc/tasks/GATE3-COVERAGE-MATRIX.md` `status: done`、`delivery_head: 7f510afd7`；矩阵正文 `doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md` 存在 |
| skip 分流（App / Host / Sidecar） | ✅ | `GATE3-APP-SKIP-TRIAGE-1.md`、`GATE3-HOST-SKIP-TRIAGE-1.md` 均 `done`；`verification/GATE3-SIDECAR-COVERAGE-1/` 存在 |
| Host 2 个「失败」性质 | ✅ 已固化 | `verification/CRASHPOINT-FAIL-NATURE-1/` 存在 |
| 真实 GUI 四页走查 | ✅ 两轮各 5/5 | 根目录 5 张 `page-*.png`（源码构建，10:13–10:14）+ `installed/` 5 张（安装产物，10:18–10:19）；`host.log` 含 `core_service ready`/`host_bridge ready` |
| 阅读器 overlay（F11）视觉 | 本次 🔄→✅ | 6 图 + 3 裁定（本复核对象） |
| 历史失败路径保留 | 原样 | `verification/GATE3-READER-OVERLAY-1/`、`verification/READER-ENTRY-PATH-1/` 仍在，本次提交未触碰 |

**没有把其他 `NOT_RUN`/`blocked` 说成通过**：`128e3074c` 的 diff 只把 §3 "阅读器 overlay" 一行从 ❌ 改成 ✅；
skip 矩阵、崩溃点、四页走查的字节未变；新卡 `READER-F11-STYLE-SCOPE-1` 的三条测试项如实写 `NOT_RUN`。

### 5.2 条件 4/5 与 Technical Gate

| 检查 | 结果 |
|---|---|
| `Technical Gate=NOT_SATISFIED` | `doc/STATUS.md:22` 原样未改 ✅ |
| `Release Gate BLOCKED` | `doc/STATUS.md:8` 仍为 `BLOCKED` ✅ |
| 条件 4 | §4 字节未改，判定仍"未关闭"；`RELEASE-GATE4-SIGNED-MATRIX-1` 仍 `proposed` ✅（但 STATUS 措辞被弱化，见 F-3） |
| 条件 5 | §5 字节未改，`LIMITATION_ACCEPTED` 与"实测基线仍 `NOT_RUN`"保留 ✅ |
| 条件 1/2/6 | 未改 ✅ |

**越权判定**：按 AGENTS.md，DSH 负责"审查处置与 Task 生命周期"，Gate 逐条处置是其职权；唯一不可代裁的"Gate 总体是否
`SATISFIED`"仍保持 `NOT_SATISFIED` 且未提任何改判建议 ⇒ **不越权**。但**记录层**留下三处自相矛盾（F-3/F-4/F-5）。

## 6 D9 是否掩盖 / 是否否定条件 3 关闭

**D9 是什么**（`visual-c3c` T4，我像素级复核）：`V2LocalStyles` 只被 `AppShellV2.axaml` 引入，`ImmersiveReaderWindow` 未引入
⇒ F11 沉浸窗的顶/底带由白色变画布色、模式 chip 失去 Accent 选中高亮。

**实测佐证**：`c3-05`（主窗口内阅读器）顶带确有一处 `(150,101,26)` 邻近色簇（62 px，正落在 `Webtoon 纵向` chip 的边框位置）、
chip 填充为 Accent.Muted 色系；`c3-06`（F11）同位置只有 1 px 噪声级命中，两个 chip 的填充/边框一致
（`(242,241,237)` / `(216,215,211)` = Bg.Raised / Line.Default）——即**沉浸窗不显示当前模式**。两帧页面重叠区
2,296,160 px 差异 0（我实测 maxdiff=1、2,862 px 差 1）⇒ 差异**只在壳**。

**判断**：

1. D9 **不是**"全屏/无边框"缺陷：无标题栏/无窗口按钮/覆盖任务栏/内容区铺满/无黑边无遮挡，全部有像素支持。
2. D9 是**外壳一致性**缺陷（同页同态、两个窗口外观不一致；沉浸态丢失"当前模式"的可读指示）。它**不否定**
   "按一次 F11 看全屏/无边框视觉正常"这一条。
3. D9 **已被披露而非掩盖**：README `:110-112`、三次裁定 T4、`MAINT-1` 卡 `:444`、新卡 `:5-7` 四处登记；新卡 AC5 明确
   "不改变 Gate 条件判定"。
4. **但关闭措辞必须限定**：能成立的是"**F11 全屏/无边框视觉正常**"；**不能**外推为"沉浸阅读器整体视觉与主窗口一致/无缺陷"。
   若把条件 3 的剩余项解释成"沉浸阅读器整体视觉正常"，D9 就是反例。本次关闭文本采用的是窄解释（正确的是），
   故不因此给 `REJECTED`；但应在关闭记录里固定该解释（见 F-4）。

⇒ **D9 不影响关闭结论，但限定结论范围**；不构成 `REJECTED` 理由。

## 7 门禁

| 命令 | 输出（末行） | exit code |
|---|---|---:|
| `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/MAINT-1-RELEASE-MONITOR.md` | `Governance check: PASS (3 warnings)`（WARN：3 个非终态 Task；STATUS 3162 B/28 行达 80% 预算；PLAN 6751 B/64 行达 80% 预算） | **0** |
| `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/READER-F11-STYLE-SCOPE-1.md` | `Governance check: PASS (3 warnings)`（同上三条） | **0** |

**门槛注意**：两条门禁都通过，但`check.ps1` **不校验** `TASK_LEDGER` 与生成器是否一致（见 F-6），也不校验
"文档内部状态陈述是否互相矛盾"（见 F-4/F-5）——门禁绿不等于关闭记录无缺陷。

## 8 Findings

| ID | 级别 | 文件/行 | 触发与影响 | 实测值 vs 文档值 + 命令 | 建议 |
|---|---|---|---|---|---|
| F-1 | **P1** | `verification/MAINT-1-RELEASE-MONITOR/condition3/README.md:13-15`（引入于 `fa190a5a8`）；`doc/reviews/RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md:143` | 最低证据第 3 项（Windows 版本）记录失真；OS 家族/发布版本写错，会让后续维护者按错误平台解释 F11/任务栏/DWM 行为 | 文档 `Windows 10 Pro / 2009 / build 26300`；实测 `(Get-CimInstance Win32_OperatingSystem).Caption = Microsoft Windows 11 专业版`、`DisplayVersion=26H2`、`CurrentBuild=26300`、`UBR=9711`（`cmd /c ver` → `10.0.26300.9711`）；注册表 `ProductName` 仍是 "Windows 10 Pro"、`ReleaseId` 仍是 "2009"（Win11 遗留字段，易误读）；截图为 Win11 居中任务栏 | 以 append-only errata 更正为"Windows 11 Pro 26H2（build 26300.9711）"，并注明注册表字段不可作为 OS 名称 |
| F-2 | P2 | `condition3/README.md:9,88-99` | D5/D6/D10 三项补记未落地：产品构建 head 未直写、`winver` 原始输出/显示器拓扑未记、第三次取证段未记 exe hash 与采集脚本路径 | head `71cecb95a` 可在 `verification/INSTALLER-MATRIX-1/README.md:25` 与 exe `ProductVersion` 取得（我已核实 exe 实测一致）；本机为双 `2560×1440` 显示器 | 在证据 README 补 head、`winver` 输出、双屏拓扑、第三次取证的 exe hash + 脚本路径 |
| F-3 | P2 | `doc/STATUS.md:8` | 本次提交顺手删掉条件 4 的限定词，**弱化限制披露**（条件 4 状态本身未变） | `git show HEAD -- doc/STATUS.md`：`4 归 \`RELEASE-GATE4-SIGNED-MATRIX-1\`（proposed；签名/跨版本未做）` → `4 归 \`RELEASE-GATE4-SIGNED-MATRIX-1\`` | 恢复该限定词（或改写到不误导的等价表述） |
| F-4 | P2 | `doc/reviews/RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md:132-140,318,359-360,377` | 同一文档仍四处称条件 3 未关闭/需人眼：§3"剩余动作""归属 需人眼"、§8.2 `H-10`="条件 3 唯一剩余项"、§11"条件 3/4/5/6 未关闭"、§12"条件 3/4/5 仍开放" | 同文档 `:122-130` 已判"已由 Agent 书面视觉裁定关闭" | append-only 更正：明确 §3 剩余动作失效、`H-10` 由委托裁定路径取代、§11/§12 中条件 3 的表述被 §3 取代 |
| F-5 | P2 | `condition3/README.md:54-57,101` | 证据 README 自身结论与后文冲突：`:56` 仍写"条件 3 仍不是 MET / `PARTIAL_WINDOW_EVIDENCE` / 底部带与内容渲染仍缺"；`:101` 仍称"分页模式布局…有像素证据" | 同文件 `:108-109` 的 D8 明确"实为 Webtoon 纵向，分页模式布局**未被覆盖**"；实测 c3-06 为 fit-width Webtoon | 给旧结论加"已被下文 §补充取证/§第三次取证 取代"标注，删改 `:101` 的"分页模式布局" |
| F-6 | P2 | `doc/TASK_LEDGER.md:14-16` | 台账与生成器不一致，违反文件头"rerun the script"的契约；会让人误以为有 1 个未提交草稿 | 台账 `tracked 668 / untracked 1 / non-terminal tracked 2`；实跑 `python tools/governance/task_ledger.py` → `tracked 669 / untracked 0 / non-terminal tracked 3`（新卡已随本提交入库） | 重跑 `task_ledger.py --write` 并提交 |
| F-7 | P2 | `doc/reviews/MAINT-1-GATE-CONDITION-3-VISUAL-ADJUDICATION-2026-11-17.md:24-26,204-205,363` | 授权口径偏差与可核验性不足：Codex Q3 字面要求"未参与实现的 **Codex 新上下文或 ZCode**"，实际裁定者是 **DSH 子 agent**；三节只记 Agent 名，无 session/subtask ID 或派发记录 | Q3 原文 `CODEX-RULING…:53`；AGENTS.md 与 2026-10-31 用户裁决允许"作者派发的独立上下文子 agent"执行 Review ⇒ 实质合规，但关闭记录未引该依据 | 在关闭记录写明：裁定者独立性依据 2026-10-31 用户裁决 + AGENTS.md"角色与交付"；补派发时间/来源（有则记 ID） |
| F-8 | P2 | `condition3/README.md:98-99`；`G:\CODEX\New Manga.workspace\tmp\r22\f11c\` | 无损原图未入仓、未钉 sha256（只记字节数），且位于 `tmp\`（可回收）；裁定的精确测量只在这些 PNG 上可复现 | 我实测两 PNG 字节数与记录一致（6,089,406 / 6,630,224），但与 JPG 的对应关系目前靠裁定自述 + 我的复算 | 记录两 PNG 的 sha256，或把原图移入证据目录（体积允许时） |
| F-9 | P2 | `doc/tasks/READER-F11-STYLE-SCOPE-1.md:22-29,48-56` | 新卡 `allowed_paths` 不含产品源码，而 AC3 要求改 `ImmersiveReaderWindow` 的样式作用域；现在释放会立刻撞允许路径 | 卡面 `allowed_paths` 只有 doc/verification；AC3/§允许范围要求"改样式作用域引入" | 释放前由 DSH 扩展 `allowed_paths`（精确到 `ImmersiveReaderWindow.cs`/`.axaml`），或在 AC1 后把精确文件写进卡面再冻结范围 |

**P0：0。P1：1（F-1）。P2：8（F-2…F-9）。**

> F-1 的根因是注册表遗留字段误导（`ProductName=Windows 10 Pro`、`ReleaseId=2009`），不是伪造；它**不改变**任何
> 基于几何/像素的视觉结论（分辨率、工作区、DPI、任务栏覆盖均已实测一致），但确属"最低证据第 3 项"记录失真，必须更正。

## 9 结论

**decision: `ACCEPTED_WITH_FINDINGS`**

**条件 3 的关闭是否成立：成立，但仅在该关闭所采用的窄解释下成立，且记录需要在 F-1…F-9 处置后才可被引用为"无缺陷"。**

- 成立的部分：真实窗口 F11 证据真实、可回指原始捕获；"全屏/无边框、覆盖任务栏、顶部/底部带完整未裁切、内容真实渲染"
  均有可复现的像素证据；3 份裁定确实独立成节、未自审、关键数字可复现；调用的是 Codex Q3 允许的"委托书面视觉裁定"路径；
  未触碰条件 4/5/`Technical Gate`，未把任何 `NOT_RUN`/`blocked` 说成通过。
- 限定：能支持的是"**F11 全屏/无边框视觉正常**"，不是"沉浸阅读器整体视觉与主窗口一致"；D9（chip 失去选中高亮、
  顶/底带变画布色）是真实外观一致性缺陷，已单独立卡、未掩盖，**不否定**关闭。
- 不成立/待修的部分：Windows 版本记录失真（F-1，P1）；Gate 映射文档与证据 README 仍有多处"未关闭/需人眼"与旧结论
  （F-3/F-4/F-5）；台账漂移（F-6）；授权口径未写明（F-7）。
- **不得外推**：本文件不构成"条件 3 = MET"的结论，不构成人眼验证，不构成条件 4/5 的证据，不构成 Gate 总体
  或 `Technical Gate` 的通过。

**建议处置顺序**：① F-1 errata（一行）→ ② F-3/F-4/F-5 append-only 更正 → ③ `task_ledger.py --write` → ④ F-7/F-8/F-2
补记 → ⑤ F-9 留到 `READER-F11-STYLE-SCOPE-1` 释放前处理。以上均为文档动作，**不需要重新取证**。

## 10 声明

**本复核不构成产品发布验收；不构成人眼验证。**

- 我是 lead 派发的独立上下文子 agent `reviewer-c3`，未参与条件 3 的取证、截图、三份视觉裁定、D9 立卡或关闭决策；
  只读访问仓库、Git 对象、`condition3/` 证据、workspace 内原始捕获与本机环境；未运行产品、未修改任何被审文件，
  仅写本报告。
- 本文件不改变任何 Task/Gate 状态，不改写任何 `NOT_RUN`，不替代 DSH 的 Review Appointment 与集成验证责任。
- 结论只对 `reviewed_head: 128e3074c` 有效；head 变化后本文件自动成为历史记录，需在新 head 上另行复核。
- 我复算的像素数字由 inline Python（Pillow 12.3.0 / numpy 2.3.5）在提交图与 workspace 同帧 PNG 上取得；
  未落中间文件，命令与关键数值已写入 §3/§4，可原样复跑。
