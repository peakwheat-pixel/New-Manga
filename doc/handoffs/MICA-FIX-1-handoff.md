# Handoff — MICA-FIX-1

- 完成：Mica 可见化（透明根/半透明标题栏）+ 启动材质诊断日志（`%APPDATA%\com.newmanga.desktop\logs\window-material.log`）。
- 真机证据：`verification/MICA-FIX-1/mica/titlebar-solid.png` / `titlebar-pattern.png` / `two-wallpapers.json`；取样色 #FFFFFF→#F0EBF7。
- 诊断：`actual=Mica`（requested=Mica,Blur,None），确认非 None 回退。
- 回退：Win10/不支持环境仍用 `MicaFallback` 不透明（单测覆盖；真机 Win10 NOT_RUN）。
- 回归：test.ps1 102/102、vitest 60/567、pytest 3F/2739P/9S。
- 集成：93aaaeb8c（DSH）。
- 遗留：Win10 真机验证（环境限制）；DPI-DYNAMIC-1 另行处理。

## Record Decision（AC5 要求的三要素）

> 依 `doc/reviews/ADJ-HANDOFF-SCOPE-2026-11-16.md` 补写；内容只描述既有事实，不改产品代码。

### 1. 透明策略

- **Win11（build ≥ 22000）**：窗口材质取 `Mica`，请求提示顺序 `Mica → Blur → None`
  （`ShellSupport.cs:17`）。
- 实现位置：`AppShellV2.axaml.cs:154-158` —— 读 `WindowMaterial.ForCurrentOs()`，
  `"Mica"` 分支映射为 `WindowTransparencyLevel.Mica`；v2 壳与 legacy 壳应用**同一策略**（`:152` 注释）。
- 效果：透明根 + 半透明标题栏（真机证据见下方「取色/验证方法」）。

### 2. 回退策略

- **Win10 / 未知 OS**：`WindowMaterialKind.OpaqueFallback`，提示只有 `None`
  （`ShellSupport.cs:18`），即**不申请任何透明材质**，保持不透明背景，避免黑边/穿透。
- 单测覆盖：`ShellSupport` 的 `Choose(...)` 是按 `(major, build)` 纯函数判定，可无真机测试。
- **真机 Win10 核对 = NOT_RUN**（环境限制，已在卡面与上述 Handoff 正文登记）。

### 3. 取色方法

**产品代码本身不做取色** —— Mica 材质由 Windows DWM 合成，客户端只声明
`WindowTransparencyLevel.Mica`，不读取壁纸颜色、不做调色。

因此“取色”指的是**验证侧如何证明 Mica 确实生效**，方法为：

| 步骤 | 做法 |
|---|---|
| 1 | 设置不同壁纸（纯色 / 图案），`verification/MICA-FIX-1/mica/titlebar-solid.png` 与 `titlebar-pattern.png` 各一张 |
| 2 | 截图窗口标题栏区域，**目视比对**标题栏是否随壁纸变化（Mica 的特征就是随桌面背景着色） |
| 3 | 对照 `--diagnostics`/日志里的 `actual=Mica`（`requested=Mica,Blur,None`）确认**非 None 回退** |
| 4 | `two-wallpapers.json` 记录两次壁纸切换下的实测诊断输出 |

**这是人眼判定步骤** —— 已按 `HUMAN-VS-AGENT-SPLIT-1` 归入 `HUMAN-REQUIRED` 清单的 **H-01**。

### 判定边界（不夸大）

- **Agent 已完成**：透明/回退策略的代码与单测、诊断日志、截图与两份壁纸的证据采集；
- **需人**：最终确认「标题栏确实随壁纸着色、且非 None 回退」这一**视觉判断**。
