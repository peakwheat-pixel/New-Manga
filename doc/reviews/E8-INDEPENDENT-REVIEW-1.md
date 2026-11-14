---
task: E8-STUDIO-BINDING
reviewer: independent-context subagent (agent-4)
reviewed_head: 9614f18bf
verdict: ACCEPT_WITH_LIMITATIONS
date: 2026-11-15
---

# E-8 四卡独立复核（上下文独立子 agent）

## 结论：**ACCEPT_WITH_LIMITATIONS**

核心 8 条 `IsEnabled` **真修**、有可回退变红的测试、真实 App **10→1** 可复核；
但**根因叙述与影响面有事实错误**，3/4 改动属 no-op 或仅消日志，测试只固定 1 处。

## ★ 复核揪出的事实错误（DSH 必须原样登记）

### 错误 1：属性归属的类搞错了（**两次都错**）

D SH 先判"`StudioPageViewModel` **缺** `IsEnabled`"（错），
"更正"后仍写 "`StudioPageViewModel.IsEnabled:202`" —— **还是错**。

**实际**：`IsEnabled` 属于 **`StudioHudSlotViewModel`**（类声明 `StudioPageViewModel.cs:182`），
`StudioPageViewModel` 本身在 **`:235`**（sealed，父类 `StudioObservable` 无此属性）。

### 错误 2："控件没有可解析的 DataContext" **不成立**

**实际**：三个控件都**从 `StudioPageWorkspace` 继承 `DataContext = viewModel`**
（`StudioPageWorkspace.cs:48`），改前日志原文正是 `...on 'StudioPageViewModel'` —— 说明**继承确实生效**。

**真实根因**：**裸绑定解析到继承的 Page VM**，而属性在 **slot / inspector 子 VM** 上。

**★ 自相矛盾的证据**：`StudioPageWorkspace` 的 11 处裸绑定**全部命中 Page VM 所以不报错** ——
这条事实**恰恰证明"继承存在"**，却被 DSH 用来支持"无可解析 DataContext"。**逻辑自伤。**

### 错误 3："4 处修复" **夸大** —— 真实修复只有 1 处

| 改动 | 复核判定 |
|---|---|
| `StudioHudRingControl:47` `{ Source = captured }` | ✅ **真修复**（8 条错误消失） |
| `StudioInspectorPanel:70` `{ Source = _inspector }` | ⚠️ **仅消日志**：`ApplyActiveTab()` 在 `:144` 调用并在 `:217` **命令式写 `_header.Text`**，标题**从未不显示** |
| `StudioLeaveModal:42/46/53` 三处 | ❌ **本就 no-op**：modal 继承同一个 Page VM，裸绑定本就可解析。**改前 10 条日志里没有一条 `Leave*` 就是反证** |

### 错误 4："该弹窗 startup 时不构建" **不实**

**实际**：`StudioPageWorkspace:83` **无条件** `new StudioLeaveModal`；
同一次启动已记录 8 条 HUD 错误即证明 workspace 已挂载、modal 绑定**已求值**。

### 错误 5：剩余那条日志的机制描述不准

DSH 写"图片源为 null"；**实际**是 **`CurrentPage == null`（未开书）导致绑定路径不可解析**。
"预期空态噪音"的**定性可接受**，机制描述不准。

## 复核确认成立的部分

- **主张 D 成立**：`HudSlots` 恰 8 个（`StudioHudRing.cs:56-66`），循环每 slot 建一 Button；
  全仓 `Bind(IsEnabledProperty` 仅 3 处，另两处均带 `Source` ⇒ 无 `Source` 的 `IsEnabled` 失败**恰为 8**。
- **主张 C 计数可复核**：改前 `GATE4-READER-PAGE-1\logs\library\startup.log` = **10 条**（05:22）；
  改后 = **1 条**（07:23）。**caveat**：两次运行外观态不同（before `fallback=False`、after `fallback=True`+迁移），
  `appdata` 均指向真实 `%APPDATA%`，且**无 exe 路径/哈希/脚本记录**。
- **代码属实**：三处 `Source` 均在位且类型拥有该属性；`StudioLeaveModal` 字段确为 `_viewModel`（`:18`）。

## 测试覆盖缺口（复核指出）

| 缺口 | 说明 |
|---|---|
| `ActiveTabLabel` 无测试 | panel **未公开** `_header`（私有）；且 `:217` 命令式同步使**任何文本断言在绑定坏掉时仍绿** ⇒ 只有"无绑定错误"断言才有判别力 |
| `StudioLeaveModal` 3 处无测试 | **"需模拟完整状态机"的说法不成立** —— `V2StudioPageTests.LeaveModal_ThreeExits` 已驱动该状态机，加断言成本很低；但这类断言**去掉 `Source` 后仍绿**（本就工作），只能钉行为、**不能钉本次改动** |
| **缺类别级守卫** | `StartupDiagnosticsTests` 只断言特定行存在，**不检查 `[Binding]`**；应加"startup.log 不含 `[Binding]`"或 headless 组合零绑定错误断言 |

## 独立复核未能完成的事项（复核自陈，诚实）

- **未运行**构建/测试（只读约束）⇒ `954/0/11/965` 与"实测变红"**未独立复现**，仅按代码判定会红。
- 未追到改后日志所用二进制的来源（无 exe/hash/构建记录），也未区分 `lib`/`smoke` 两次运行的 `--page`。
- 未逐字核对 `capture-reader.ps1` 的启动参数。
- 未审计 E-8 之外的指针/状态一致性。
