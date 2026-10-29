# V11R-B-3 · I1 返修处置表（独立审查 P1/P2 + 集成测试基础设施缺陷 A/B）

Owner: ui-studio · Branch `v11r/ui-studio` · 基础：B-3 delivery head + 二次 merge main（含 ui-shell Shell/V2、DS 返修）
复现：`cd apps/desktop-avalonia && dotnet build NewManga.sln -warnaserror && dotnet test NewManga.sln`
证据：`build-i1.log` / `test-i1.log`（App 232 通过 / 6 跳过；DS 40；Host 42/24；ThemeEngine 159；CoreClient 45/22）

| 编号 | 结论 | 处置 |
|---|---|---|
| P1-1 Region 命中/hover 死代码 | **已修** | `StudioRegionOverlay` 删除 `IsHitTestVisible=false`，改 `Background=null`（空区不拦截拖拽、Box 为真实命中目标且 `PointerPressed` Handled=**true**）；hover/select 回调恢复可达。**缺口：headless 指针合成在本机不稳定，指针测试未随提交（follow-up：真实窗口或 Windows 输入层验证）** |
| P1-2 Modal 焦点写死 | **已修** | `StudioLeaveModal` 真实焦点：打开捕获 `FocusBeforeOpen` → `DispatcherPriority.Loaded` 聚焦「取消」；Tab/Shift+Tab 焦点陷阱；`Esc`=取消；关闭回焦触发元素。删除写死字段（旧 `leave-modal.json` 待 curate 重生成） |
| P2-3 保存失败文案透明 | **已修** | 移除 `Foreground=Brushes.Transparent` 本地值，改用 `studio-state-failed` 样式类 |
| P2-4 单一 selection（R-16） | **已修** | `StudioSelection` 改为 `ShellState.Selection` 的投影+路由（唯一权威）；新增 `StudioScopeKind{Chapter,SelectedPages,Page,Region}`；**显式多选优先于 Region**（FUSION 硬规则 1）；`SetContext` 原子写；测试改为断言新语义 |
| P2-5 token 裸值 + conformance 测试 | **未完成** | `StudioTheme.axaml` Padding/Width 与 C# 几何常量仍是字面值；conformance 扫描测试与 `design-system-usage.md` 生成器修复未做（登记为返修剩余项） |
| P2-6 loading 骨架/截图 | **未完成** | `state-loading.png` 与胶片条/检查器骨架未加（登记） |
| P2-7 错误三重复呈现 | **已修** | 错误态仅保留一个就地块：`HostBannerVisible` 时隐藏 `ErrorBanner`，`EmptyOverlay` 同步；`States_EmptyErrorPartial_RenderInPlace` 断言更新 |
| P2-8 错误路径不完备 | **已修** | `LoadAsync` 增加 `InvalidOperationException/IOException/TimeoutException` → Error + `ErrorText`，异常不再逸出 async 视图 |
| P2-9 键盘可达（R-17） | **部分** | `StudioWorkspaceView.TryHandleKey(key, modifiers)` 已实现（仅 Page 模式、仅 Studio 专有键，其余返回 false）；**shell `IWorkspaceView` 接口未合入，接线归 INT-1**；Tab 遍历交互测试未交付 |
| P2-10 杂项 | **部分** | `BuildGate` 订阅 `IHostController.Changed`（只读/就绪实时反映）；死代码 `Hairline()` 删除；`ReOcrRegion` 映射改为独立 `StudioCommand.ReOcrRegion`（不再误用 CreateRegion）；**图标 DEVIATIONS 登记、`region-badges.json` hover 声明、全量证据 curate 未完成** |
| 缺陷 A 测试证据写仓导致锁/flake | **已修** | `StudioEvidence` 默认写 `%TEMP%/newmanga-evidence/<task>/`；仅 `NEWMANGA_EVIDENCE_SYNC=1` 时写仓库；新增 `scripts/curate-evidence.ps1 -Task <ID>`；Capture 路径已含任务+测试名 |
| 缺陷 B DS 样式断言 | **未触发** | 全量测试 0 失败，无旧值断言需改 |

## 未完成项（需后续返修窗口）
1. P2-5 token 迁移 + Studio conformance 测试 + `design-system-usage.md` 生成器修复。
2. P2-6 loading 骨架与 `state-loading.png`。
3. P2-9 交互测试（modal 焦点真断言、Region 指针 hover/click）与 shell `IWorkspaceView` 接线（INT-1）。
4. P2-10 图标 DEVIATIONS 登记、`region-badges.json`/`leave-modal.json` 等证据重生成（需 curate 脚本 + TEMP 证据）。
5. 证据目录中 B-3 旧 JSON 仍含 `modal_default_focus:"取消"` 字面量，curate 后会以真实测试结果覆盖。
