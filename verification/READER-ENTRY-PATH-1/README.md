# READER-ENTRY-PATH-1：`reader` 页**有程序化入口**，但缺一个 CLI 触发参数

基线 `e12e6299e`。承接上一轮承诺"用读代码而非推测挖 reader"。

## 1. 此前的结论（部分正确、部分不完整）

我此前实测：`--page=reader --exit-after=15000` 启动后**截图显示的是"资料柜"页面**，
据此判断"`--page=reader` 只切 `SpaceId.Library`，看阅读器必须按 F11"。

**实测结论仍然成立**，但"必须人工按键"**不完整** —— 代码里有**程序化入口**。

## 2. 代码事实（读到的，不是推测）

### 2.1 有一个真实的 shell 命令

`ShellCommands.cs:37`：

```csharp
public const string LibraryImmersiveReader = "library.reader.immersive";
```

`:111`：注册为 `"沉浸阅读"`，绑定 `SpaceId.Library` + `ShellKeyGesture(F11)`。

### 2.2 它的处理只是**触发事件**

`AppShellViewModel.cs:1188-1190`：

```csharp
case ShellCommandIds.LibraryImmersiveReader:
    ImmersiveReaderRequested?.Invoke(this, EventArgs.Empty);
    return;
```

### 2.3 事件由 composition root 消费（创建沉浸窗口）

`ImmersiveReaderWindow.cs:10-12` 注释：
"The shell view model … borderless fullscreen reader host for the default V2 shell …
no decorations, design-system canvas backdrop, **Esc/F11 closes** and the shell …"

### 2.4 测试是怎么驱动的

`F11HotkeyTests.cs:58-59`：

```csharp
Assert.True(window.TryHandleGlobalKey(Key.F11));
await window.LastImmersiveToggle;
```

⇒ **测试用 `TryHandleGlobalKey(Key.F11)` 驱动**。

**★ 更正（独立裁决指出）**：`TryHandleGlobalKey` 不是"测试窗口的方法" ——
它是**生产窗口的 public 方法**（`MainWindow.axaml.cs:298/384`），`OnKeyDown` 也调用它。
⇒ 真实键盘 F11 与测试驱动的**是同一条代码链**：
`OnKeyDown` / `TryHandleGlobalKey` → `AppShellViewModel.cs:1099/1188-1190` → 事件 → `App.axaml.cs:512-534` 开窗。

## 3. 结论：缺的不是能力，是一个 CLI 入口

| 需要什么 | 现状 |
|---|---|
| 打开沉浸阅读器的**能力** | ✅ 有（`library.reader.immersive` 命令 → 事件 → 窗口） |
| **程序化触发**该命令 | ⚠️ 只有两条现成路径：**命令面板（UI）** 或 **`TryHandleGlobalKey(F11)`（测试窗口）** |
| **启动时自动触发** | ❌ **`AppOptions` 没有"启动时执行命令"的参数**（16 个参数里没有） |

**⇒ 若要自动取证 `reader` 页，最小改动是给 `AppOptions` 加一个参数**
（例如 `--run-command=library.reader.immersive`），启动完成后执行一次。

**但这会改动产品代码**（`AppOptions` + `App.axaml.cs` 的启动流程），
**属"扩大范围"** —— 按 goal 纪律应**先裁决**，不擅自做。

## 4. 立即可用的替代（不改产品代码）

**用测试窗口的既有驱动方式**：`F11HotkeyTests` 已经证明
`TryHandleGlobalKey(Key.F11)` 能在 **headless 下打开沉浸窗口**并断言
（`immersive.IsVisible`、`Page.ViewModel.PageCount == 8`、Esc 还原）。

⇒ **`reader` 页的 GUI 行为在 headless 层"已被验证"**（`F11HotkeyTests` 9 个 + `V2ImmersiveReaderTests` 4 个，全绿）。
**未验证的只是"真实窗口在真实桌面上的全屏/边框切换"** —— 那才是真正需要人看的。

**⇒ 条件 4 的 `reader` 项应拆成两半**：
1. **GUI 逻辑**：✅ 已被 `F11HotkeyTests` / `V2ImmersiveReaderTests` 覆盖（headless，全绿）；
2. **真实桌面渲染**（全屏、无边框、Esc 还原的视觉表现）：❌ 需人工看一眼。

## 5. 未做

- **未加** `--run-command` 之类的 CLI 参数（属产品改动，待裁决）。
- 未在真实桌面截图沉浸窗口（需要真实按键或上述参数）。
- 未核实 `ImmersiveReaderWindow` 在 composition root 里的**确切订阅点**（只读到注释与事件触发点，
  未逐行读 `App.axaml.cs` 的订阅代码）。

## 6. 裁决结果（ZCode，2026-11-15）

**裁决：不加 `--run-command` 参数；接受把 `reader` 项拆成两半。**

裁决者核实的补充事实：

- **订阅点**：`App.axaml.cs:512-534` 的 `WireImmersiveReader` 订阅 `ImmersiveReaderRequested`，
  **惰性 `new ImmersiveReaderWindow(...)` + `Show(host)`**，toggle 语义（可见则 Close）
  ⇒ **沉浸窗口是事件驱动的运行时按需创建，不是启动产物**。
- **`--page=reader` 显示资料柜是设计如此**：`App.axaml.cs:452-453` 注释明写
  "reader is an overlay inside Library"，`:502` 把它映射到 `SpaceId.Library`。
  ⇒ 我的实测结论成立，但**这是映射语义而非缺陷**。
- **改动面**：`AppOptions.cs`（16 参数解析+校验）加字段 + 命令 id 白名单校验（fail-closed），
  再在 `App.axaml.cs:104-118` 启动序列插执行逻辑，且**只在 V2 shell 有意义**（legacy/Fluent 无此命令）
  ⇒ **是真实的产品面改动，非一行补丁**。
- **参数性质**：`--page` 注释自称 "evidence hook"（`App.axaml.cs:451`），`--exit-after` 是自动关窗定时器
  ⇒ **确属调试/取证参数**。加同类参数**在性质上是同类扩展**，"扩大范围"的说法**偏严**。
- **但裁决的关键理由是"值不值"而非"该不该"**：
  **加参数只能让窗口被打开，而全屏/无边框/视觉表现机器判不了，取证仍需人眼看；
  人既要在场，顺手按 F11（产品真实功能）成本为零。收益≈0，成本为正。**

**⇒ 落地：不加参数。`reader` 项按下表拆分收口。**

| 子项 | 状态 | 依据 |
|---|---|---|
| **GUI 逻辑**（打开/关闭/Esc 阶梯/回到原页/PageCount） | ✅ **已验证** | `F11HotkeyTests`（9 个 AvaloniaFact）+ `V2ImmersiveReaderTests`（4 个），headless 全绿，且驱动的是**生产 public 方法** |
| **真实桌面渲染**（全屏、无边框、视觉表现） | ❌ **需人工按 F11 看一眼** | headless 判不了视觉 |
