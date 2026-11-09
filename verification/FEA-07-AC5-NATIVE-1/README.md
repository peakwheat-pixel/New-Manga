# FEA-07-AC5-NATIVE-1 — 原生双屏矩阵（真实 AOC 2K + Philips 4K）

| 项 | 值 |
|---|---|
| 环境 | Windows console session 1 活跃；NVIDIA RTX 5070 Ti |
| 显示器 | `\\.\DISPLAY1` **AOC AG273QS3R4B** 2560×1440@165（主，@100%）；`\\.\DISPLAY2` **Philips 279M1RV** 3840×2160@120（@150%） |
| 应用 | `NewManga.App.exe`（Release，隔离 `--data-root/--log-dir/--theme-home`） |
| manifest | `app.manifest:6-7` → `dpiAware true/pm` + **`dpiAwareness PerMonitorV2`**；csproj `ApplicationManifest` 引用 |
| 采集时间 | 2026-11-09 08:40–09:33 Asia/Shanghai |

## 结果汇总

### 1. 混合 DPI 跨屏拖动（真实鼠标手势，非 SetWindowPos）

| 配置（2K / 4K） | 2K 上窗口 | 拖到 4K 后 | DPI 切换 | 完全在 4K 内 |
|---|---|---|---|---|
| 100% / 150% | 1408×792 @96 | **2112×1188 @144** | 96→144 ✅ | ✅ |
| 100% / 125% | 1408×792 @96 | **1760×990 @120** | 96→120 ✅ | ✅ |
| 100% / 200% | 1408×792 @96 | **2816×1584 @192** | 96→192 ✅ | ✅ |
| 150% / 200% | 1558×792 @144 | **2077×1056 @192** | 144→192 ✅ | ✅ |

- 物理尺寸严格按目标屏缩放比放大（DIP 尺寸保持）：1408→2112（×1.5）、1760（×1.25）、2816（×2.0）。
- 截图：`evidence/screenshots/*drag*.png`（2K/4K 各一张，含 SHA256）。
- **对照（探针伪影，非缺陷）**：用 `SetWindowPos` 直接注入物理尺寸时窗口按 DIP 保持放大并越出屏缘；真实拖动路径正确。

### 2. 拔屏（OS 级，`DisplaySwitch.exe /internal` ≈ 移除第二屏）

- 应用窗口在 4K (3616,200) 2592×1458@150% → `/internal` 后：**(703,134) 1728×972@100%**、**完全落在主屏内**、**进程存活**；`/extend` 后 4K 恢复 3840×2160@150% @(2560,0)。
- 证据：`evidence/undock-os-*.json` + `screenshots/*undock*.png`。

### 3. 每屏缩放切换（UI 自动化「设置 → 显示 → 缩放」，逐屏）

- 工具 `tools/set-scale-uia.ps1`（先选 `显示器 N`，再选 `缩放`）；本机 `DisplayConfig SET_DPI_SCALE` 返回 rc=87 不可用，注册表 `DpiValue` 广播也不生效，**UIA 是唯一可行路径**。
- 映射：`显示器 1` = AOC（主）；`显示器 2` = 4K。
- 已实测并恢复：2K 100/125/150%、4K 125/150/200%；结束时恢复 2K **100%** / 4K **150%**。

### 4. 恢复点

- `display-state-before-native-20261109-084020.json`：原始 `DISPLAY1 1920×1080@59@100%` + `DISPLAY2 3840×2160@120@150% @(1920,0)`。
- 当前（矩阵后）：`DISPLAY1 2560×1440@165@100%`（已调原生 2K）+ `DISPLAY2 3840×2160@120@150%`。
- **AOC 分辨率尚未恢复为原始 1920×1080**（等用户裁决保留原生或恢复）。

## 限制 / 未覆盖（不得写成 PASS）

- **Inspector 浮窗**：生产代码 `WindowBroker.RegisterSecondary` 零调用、无 `WindowRole.Floating` 实例 ⇒ 「主窗+Inspector 浮窗归属」无法原生验证（与 L-R4a-1 同源）→ 登记 limitation。
- **未 flush 编辑态 fail-closed**：需要「打开章节→产生未保存编辑→拔屏」的真实交互序列，本卡未执行 → `NOT_RUN`。
- **物理拔线**：用 OS 级 `/internal` 模拟，未做真实拔 DP/HDMI 线（可另行补）。
- **原生 IME**：未执行（`NOT_RUN`）。
- 换主屏、全屏切换子项：未单独执行（`NOT_RUN`）。

## 证据清单

- `evidence/displays-*.json`（DPI 感知拓扑，含 EDID 名）
- `evidence/display-state-*.json`（原始/当前模式与恢复点）
- `evidence/native-mixed-dpi-move-*.json`（程序化摆位对照）
- `evidence/drag-mixed-dpi-*.json`（真实拖动，4 组配置）
- `evidence/undock-os-*.json`（拔屏）
- `evidence/scale-uia-*.json`（逐屏缩放切换记录）
- `evidence/screenshots/*.png`（7+ 张，逐图 SHA256 见 JSON）

## 5. 物理拔屏（2026-11-09，用户手动拔 4K 线）

| 阶段 | 拓扑 | 主窗 | 判定 |
|---|---|---|---|
| 拔屏前 | AOC 2K(主) + **4K** | 4K 上 (3616,200) 2592×1458@150% | 就位 |
| **拔掉 4K** | AOC 2K(主) + Mi TV 1080p | **最小化**（iconic，-32000,-32000），进程存活 | 未自动迁移（D-AC5-1） |
| 手动恢复 | 同上 | 主屏 (703,134) 1728×972@100%，完全在主屏内 | 可恢复、可用 |
| **插回 4K** | AOC 2K(主) + **4K** | **自动回到 4K 原几何** (3616,200) 2592×1458@150% | 恢复正确 |

- 证据：`evidence/physical-state-*.json`（4 份）、`evidence/physical-unplug-before.log`、`evidence/screenshots/*phys*.png`。
- 与 OS 级 `/internal` 拔屏对比：OS 级会自动迁移窗口；物理移除事件下应用被 OS 最小化、需手动恢复 → 登记 D-AC5-1（P3，产品缺口/limitation）。

## 6. 追加原生子项（2026-11-09）

| 子项 | 方法 | 结果 |
|---|---|---|
| **中文 IME 输入** | 命令面板（Ctrl+K）聚焦 Edit → 载入 `00000804` 键盘布局并激活 → 逐键 `nihao` + 空格提交 | ✅ **组合成功，值 = "你好"**（`evidence/extra-ime-*.json`，`imeComposed=true`） |
| **换主屏** | `ChangeDisplaySettingsEx(CDS_SET_PRIMARY)` 把 4K 设为主屏 → 采样 → 恢复 AOC 为主屏 | ✅ 双向 `rc=0`、应用存活、窗口/DPI 正确（`evidence/extra-primary-switch-*.json` + before/after 截图） |
| **全屏切换** | 最大化按钮 + `F11` + `F`/`Esc` 键盘 | ⚠️ **NOT_RUN**：应用全屏仅在 **Reader 页**实现（`ReaderWorkbenchPages.cs:2599 WindowState.FullScreen`，热键 `Key.F:2649`）；隔离空库无章节可开阅读器 → 无法触发；`F11` 实测无效果 |
| **未 flush 编辑态 + 拔屏** | 命令面板输入未提交文本 `draft` → `DisplaySwitch /internal`（移除第二屏）→ 重新读取输入缓冲 | ✅ **缓冲保留**（`bufferRetainedAfterUnplug=true`）、进程存活（`evidence/unsaved-edit-unplug-*.json` + 截图） |

- 说明：全屏与「Reader 内 F 键」相关，属于需要**真实章节内容**的子项；本卡在隔离空库下执行，故如实记 `NOT_RUN`，未写成 PASS。
- 未 flush 编辑态使用 OS 级显示移除（`/internal`）驱动（物理拔线已在 §5 单独验证）；两者结论一致（进程存活、窗口/内容不丢）。

## 7. 全屏（Reader-only）尝试与结论

- 全屏实现位于 Reader 页：`ReaderWorkbenchPages.cs:2599`（`WindowState.FullScreen`）、热键 `Key.F:2649`；主窗 `F11` 实测无效果（`evidence/extra-fullscreen-*.json` 中 `afterFKey/afterEsc` 与最大化态一致）。
- 触发全屏需要**真实章节内容**；本卡在隔离空库下尝试用「导入文件夹」UIA 自动化灌入合成漫画（2 话 × 3 页，ASCII 路径），文件夹选择对话框自动化多次未能稳定完成（日志见 `evidence/attempts/`）。
- 结论：**`NOT_RUN`**（未写 PASS）。补齐条件：在应用里手动导入一个漫画文件夹（两次点击），或由环境提供已导入库，即可补测 Reader 全屏。

### 全屏（沉浸 ReaderWindow）实测结果 —— `NOT_RUN` + 缺陷候选 D-AC5-2

- 实现事实：沉浸窗口为独立 `ReaderWindow`（`ReaderWorkbenchPages.cs:2576-2602`：`SystemDecorations.None` + `WindowState.FullScreen`），入口为 Reader 页按钮/双击或应用级 `F11`（`MainWindow.TryHandleGlobalKey` → `ToggleImmersiveAsync` → `OpenImmersiveReader`）。
- 已导入真实内容（169 页）并打开 Reader 页（封面/第 1 页可见），随后尝试：
  1. **用户手动 F11**（点击画面后）→ 无窗口出现；
  2. 自动化 `SendKeys(F11)`（焦点在按钮，确认非文本框、`GetForegroundWindow` 为应用）→ 6s×200ms 轮询内无新顶层窗口；
  3. 双击页面图像 → 无沉浸窗口；
  4. 对照实验：`SendKeys(RIGHT)` 翻页后 **wire 无新 `resolve_page_resource`** ⇒ 键盘事件未送达 Reader（本会话输入路由异常）。
- wire 旁证：11:22:04–05 出现 `resolve_page_resource` + `SaveReadingProgress`（`ReaderWindow.Closed` 才 flush）⇒ 说明 F11 路径**部分执行过**（窗口创建/关闭），但未在桌面保持可见。
- 结论：**`NOT_RUN`**，不写 PASS；登记 **D-AC5-2**（沉浸全屏在本会话无法出现，疑似 `OpenImmersiveReader` 在本会话抛异常或输入未送达；需在**本地控制台会话**复现确认是环境还是产品缺陷）。
- 判定材料：`evidence/probe-f11-*.json`、`evidence/open-immersive-*.json`、`evidence/reader-fullscreen*.json`；截图含用户漫画内容，仅存仓外 `G:\CODEX\New Manga.workspace\FEA-07-AC5-NATIVE-1\ac5-fullscreen\`（哈希已记录）。

### D-AC5-2 补充：F11 可送达但沉浸窗口不出（2026-11-09 14:10）

- 用户在浏览器按 F11 可全屏 ⇒ **远程键盘正常**；点击应用窗口后再按 F11 → **主窗被最小化、无沉浸窗口**。
- 自动化：`SendInput`（rc=2 事件）、`PostMessage WM_KEYUP/DOWN`（rc=3）均只造成主窗最小化；100ms 轮询 4 分钟无新顶层窗口（`evidence/watch-immersive-20261109-140944.json`）。
- 推断：`OpenImmersiveReader()` 的 `window.Show()`（FullScreen + 无边框 `ReaderWindow`）在本会话未完成；主窗被系统最小化而非恢复 ⇒ 产品缺陷候选（需本地控制台复现）。
- AC5「全屏切换」子项：**`NOT_RUN`**（不写 PASS）。
