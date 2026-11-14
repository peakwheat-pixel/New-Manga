# E8-STUDIO-BINDING-3：真实 App 验收（改前/改后同页面对照）

基线 `cef724f26`。补完 E8-STUDIO-BINDING-1 §6.4 欠的**真实 App 验收**。

## 1. 方法（可直接复现）

用与 `GATE4-READER-PAGE-1/capture-reader.ps1` **完全相同**的启动参数，只改 `--page`：

```
NewManga.App.exe --shell=v2 --page=library --exit-after=25000
  --data-root=<隔离根>\data --log-dir=<隔离根>\logs --sidecar-dir=<sidecar>
  --width=1400 --height=900 --legacy-shell-check=off
```

`--exit-after` 让 App **自己退出**（退出码 0），无需任何交互 —— 这正是之前卡住的地方
（F11 需要交互，而 `--exit-after` 不需要）。

## 2. 对照结果（**同一页面、同一参数，只差修复**）

| | `--page=library` 的 `startup.log` 里 `[Binding]` 条数 |
|---|---|
| **改前**（`...\GATE4-READER-PAGE-1\logs\library\startup.log`） | **10** |
| **改后**（本卡，同参数） | **1** |

**消失的 9 条**：8 条 `IsEnabled`（`StudioHudRingControl` 的 8 个 HUD slot）+ 1 条 `ActiveTabLabel`。

**剩下的 1 条**：

```
[Binding]An error occurred binding 'Source' to 'CurrentPage.Image' at 'CurrentPage': 'Value is null.'
```

## 3. 顺带确认：`--page=studio` 也是 1 条

用 `--page=studio` 另跑一次，同样是 **1** 条（同一 `CurrentPage.Image`）。
⇒ 该页面的 Studio 控件在两处都会构建，**修复对两条路径都生效**。

## 4. 结论

**E-8 的 9/10 条绑定错误已在真实 App 上确认消失。**

**剩下的 `CurrentPage.Image` 是不同类问题**：它不是"绑定路径解析失败"，而是"图片源值为 null"
（`Value is null`）—— 即当前页无图时的正常提示，还是一条真实缺陷需要单独判断，**本卡未处理**。

## 5. 仍未做（诚实）

- `StudioLeaveModal` 的 `SaveEnabled` 与 `StudioInspectorPanel` 的 `ActiveTabLabel` **没有单元测试**
  （前者需模拟离开确认状态机、后者需构造 `StudioInspectorViewModel`）。
  但**后者已在真实 App 日志里确认消失**（`ActiveTabLabel` 那条不见了），**前者没有独立证据**。
- 完整的无夹具三项目全量只跑了 App（954/0/11/965）；Host/CoreClient 本轮未跑（未改动它们）。
