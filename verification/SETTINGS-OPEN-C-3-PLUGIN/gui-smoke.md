# GUI smoke — SETTINGS-OPEN-C-3-PLUGIN

- Time: 2026-10-23 ~11:51–11:54 +08:00
- App: `tools/dev/dev-preview.ps1`（Tauri dev window，隔离数据根）
- Window: m2rc1-desktop.exe（pid 43088），URL http://localhost:5188/

## 步骤与结果

1. 启动 dev preview → 书架页 → `⚙️ 设置`（UIA Invoke）。
2. 分类列表：**11 开 1 关**；`Plugin/Hooks` 仍为 disabled + "未开放"徽标（与 C-2 关闭时一致，C-3 不打开分区）。
3. UIA 读取该按钮的可访问名：`Plugin/Hooks，未开放：插件系统尚未实现`——即 §4.5 冻结文案已替换通用"等待 section schema 冻结"，不再是"schema 待冻结"的旧理由。
4. 面板保持不可达（nav disabled，无法进入）；无任何可点控件（§4.5：无运行时不得提供 enable/reload/open-dir 按钮）——`screenshots/01-settings-plugin-closed.png`。
5. 其余 11 个开放分区行为不变（设置页默认 Provider 面板正常渲染）。

## 限制与备注

- 因分区保持未开放，插件占位面板在 UI 中不可达；其只读文案与"无按钮"由 `DisabledSection.test.tsx` 组件级测试固定（渲染 plugins 版断言 §4.5 description 且 `querySelector("button") === null`）。
- 未新增任何 Tauri/Core/wire 面；未改 P15 白名单与 `plugins` 键集。
