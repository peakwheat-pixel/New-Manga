# RES-P02-AC6-CDP-RECOVERY Closeout A7 运行调查与结果补充报告

- **Task ID**：`RES-P02-AC6-CDP-RECOVERY`
- **RunId**：`res-p02-ac6-cdp-recovery-closeout-a7`（对应底层采样运行 `p02-newtime-ac-20261014-i2/ac6-contrast-a7`）
- **执行角色**：antigravity（Owner）
- **主控决策**：Codex（epoch=3）
- **产品源码基线**：`49d2a2f9c56462f5602b00ad4b824c5381abb1ab`
- **任务代码 HEAD**：`a8d9219ba192c9a7feb1437240e51535938073fa`
- **固定 EXE**：`G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO/apps/desktop/src-tauri/target/release/m2rc1-desktop.exe`，9,367,040 bytes，SHA-256 `92AC7B8EFB646FE77DF8245B13C9AF9314BEF415B2F0E007B1CDCEA729BC13FD`
- **原始 a7 证据目录**：`verification/P02-NEW-TIME-X6-AC1-AC7/runs/p02-newtime-ac-20261014-i2/ac6-contrast-a7/`
- **本轮 closeout 派生目录**：`verification/RES-P02-AC6-CDP-RECOVERY/closeout-a7/`

---

## 1. a7 交互式桌面会话采集背景与执行差异说明

在先前的 I2 阶段以及 RES 实验排查中，DSH 派发链与后台任务因 Win32 桌面/窗口站环境限制，固定 EXE 在启动创建 WebView2 控制器时抛出 `WindowsError: HRESULT(0x80070578) 无效的窗口句柄`，导致主窗口未建立、`msedgewebview2.exe` 未拉起，CDP 端口 9333 无法连通。

本次 a7 采样通过在**当前用户交互式桌面会话**（Console Session 1，具备完整 Win32 顶层窗口创建能力）中直接运行采样脚本完成：
- **执行命令**：`node apps/desktop/frontend/e2e/p02-new-time/ac6-contrast.mjs`
- **直接采集差异**：本次为交互式桌面会话直接运行，无外层 runner 包装，因此直接产出并记录 `execution-metadata.json`，**无外层 `runner-execution.json`**。此处如实记录直接采集差异，严格禁止补造虚假 runner 文件。
- **采集元数据验证**：`execution-metadata.json` 记录 `node_exit_code=0`，完成时间 `2026-10-15T04:51:21.893Z`。

---

## 2. AC6 a7 真实计数与实测结果

I2 采样脚本针对表单控件使用 `value` / `placeholder` 读取文本并在运行时逐行判定背景层与 alpha 合成。在 a7 运行中，AC6 首次取得完整的真实 DOM 样本与对比度计算表：

| 指标 | a7 实测数据 | 说明 |
|---|---|---|
| **样本总数 (`samples`)** | 10 | 覆盖 Console、Workbench 核心控制项与输入框 |
| **计算成功数 (`computed`)** | 10 | 所有 10 个样本均成功提取前景色、背景色并计算比值 |
| **对比度通过数 (`passed`)** | 10 | 全部 10 个样本对比度均达到或超过阈值（正文 4.5:1，非文本/禁用 3.0:1） |
| **对比度失败数 (`fails`)** | 0 | `fails: []` |
| **不可验证数 (`not_verifiable`)** | 0 | `not_verifiable: []`，I1 的漏采与未决项完全消除 |
| **Alpha 合成触发 (`alpha_compositing_triggered`)** | `false` | 全局顶层标识为 `false` |
| **Design Token 映射 (`token_mapping`)** | `mapped: 0, unmapped: 10` | 保持既有产品现状，均为 React 运行时行内样式 |
| **浅色主题 (`light_theme`)** | `NOT_APPLICABLE` | 应用中无浅色主题开关或入口 |

### 关键样本：`[data-testid="page-id-input"]`

- **选择器**：`[data-testid="page-id-input"]`
- **前景色 (`foreground`)**：`rgb(216.0, 224.0, 232.0)`
- **背景色 (`background`)**：`rgb(16.0, 20.0, 24.0)`
- **背景来源 (`backgroundSource`)**：`INPUT[page-id-input]`
- **背景图层 (`backgroundLayers`)**：`[{"on": "INPUT[page-id-input]", "color": {"r": 16, "g": 20, "b": 24, "a": 1}}]`
- **Alpha 合成应用 (`alpha_compositing_applied`)**：`false`（原生背景色完全不透明，alpha=1）
- **对比度比值 (`contrast_ratio`)**：`13.87`（远高于 4.5:1 阈值）
- **对比度判定 (`contrast_result`)**：`PASS`

---

## 3. P-04 不实原因澄清与修正（闭合 R3-01 证据层）

在 I1 报告及后续历史分析中，曾推测 `page-id-input` 的 `NOT_VERIFIABLE` 是因为“半透明背景”“祖先链缺少不透明底色”或“alpha 合成算法保护性返回”。

**实测澄清与纠偏**：
1. **真实原因**：I1 采样器使用的是基于 `textContent` 的通用可见文本过滤，而 HTML `<input>` 元素的文字内容存储在 `value` 或 `placeholder` 属性中，导致 I1 将其判定为 `hasVisibleText: false`（`present: false`）。
2. **算法与数据证伪**：在 I2 将采样逻辑修正为支持表单控件 `value`/`placeholder` 后，a7 实测明确证明 `page-id-input` 的底色是原生完全不透明的 `#101418`（`rgb(16, 20, 24)`，alpha=1），并未涉及半透明背景，也未触发任何 alpha 合成退让分支（`alpha_compositing_applied=false`）。
3. **结论**：早期关于半透明底色与合成保护的推测完全不属实。现由 a7 实测数据彻底澄清并纠正。R3-01 证据层正式闭合。

---

## 4. 保留的既有产品 Finding 与 Mock 限制

除 AC6 a7 成功测定并修正 P-04 之外，本轮完整保留以下既有已知产品 Finding 与架构/Mock 限制，不掩盖任何未决产品缺陷：

1. **P-01 (PRODUCT_A11Y_KEYBOARD, Severity P3)**：
   - 目标：`RelabelConfirmDialog / RevisionRestoreDialog`
   - 现状：确认对话框在 React 产品代码中未绑定 Escape 按键监听，用户通过键盘按 Escape 无法关闭对话框。此为既有产品代码缺陷，依然保留。
2. **P-02 (PRODUCT_DESIGN_TOKENS, Severity P3)**：
   - 目标：Workbench & Console 界面
   - 现状：所有采样的 10 个元素均使用 React 运行时行内颜色，未接入 F design token 映射系统（0 mapped, 10 unmapped）。
3. **P-03 (PRODUCT_FEATURE_SCOPE, Severity P3)**：
   - 目标：浅色主题系统
   - 现状：当前 React 应用未实现浅色主题切换或入口，处于 `NOT_APPLICABLE`。
4. **Mock IPC 与合成数据限制**：
   - AC1/AC2 沿用 I1 真实 IPC 证据；
   - AC3 保持 311ms quiet period 与 stale guard 证据；
   - AC4/AC5 仍基于 Real WebView + Mock IPC / Synthetic DB 运行（如空合成 DB 导致某些多区域历史分支在早期尝试未走通）。

---

## 5. 现存历史失败记录（完整保留）

本报告完整保留并记录以下历史失败与对照尝试，严禁篡改或隐瞒：

### 5.1 I1 保留失败尝试
- `ac3-debounce-a2`：observer wrapper 未进入 `ACTIVE`（status=FAIL, verdict=ERROR）。
- `ac4-write-refresh`：未找到 `[data-testid="region-frame-syn-region-ac4-001"]`（status=FAIL, verdict=ERROR）。
- `ac4-write-refresh-a2`：未找到 `[data-testid="region-frame-syn-region-ac4-001"]`（status=FAIL, verdict=ERROR）。
- `ac5-keyboard`：未找到 `[data-testid="inspector-revision-history"]`（status=FAIL, verdict=ERROR）。

### 5.2 I2 AC6 失败尝试
- `a1` (端口 9334)：45 秒超时，`CDP endpoint never appeared: TypeError: fetch failed`，`node_exit_code=1`。
- `a2` (端口 9335)：45 秒超时，同样未建立 CDP，`node_exit_code=1`。
- `a3` (端口 9336)：45 秒超时，进程快照确认 WebView2 命令行无 remote debugging port，`node_exit_code=1`。
- `a4` (端口 9333 recovery)：45 秒超时，端口 9333 空闲仍未建立端点，`node_exit_code=1`。

### 5.3 非交互式环境崩溃对照实验（RES 阶段实验 1–3）
- 实验 1（代理清理对照）、实验 2（进程/端口监控）、实验 3（直接 node 启动进程追踪）均复现 Win32 顶层窗口创建失败抛出 Rust Panic `0x80070578 无效的窗口句柄`。

---

## 6. 状态结论与工作边界

- **证据采集层**：a7 采样已成功完成，原字节无篡改，产出真实可信的 10 个样本及对比度 13.87 的通过数据。
- **严禁过度宣称**：禁止将 AC6 证据采集成功等同于整个产品或父 Task 完成。
- **任务状态**：本任务结论仅为 `READY_FOR_BOUNDED_REVIEW`。
- **后续流程**：禁止 Owner 自行审查或合并主线；后续由 DSH 进行独立的 Bounded Review，并由主控 Codex 执行集成裁决。
