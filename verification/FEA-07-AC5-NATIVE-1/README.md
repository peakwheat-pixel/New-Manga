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
