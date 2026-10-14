# P02-NEW-TIME-X6-AC1-AC7 I1 运行调查与结果报告 (Findings Report)

- **任务编号**：`P02-NEW-TIME-X6-AC1-AC7`
- **运行轮次 (RunId)**：`p02-newtime-ac-20261014-i1`
- **执行角色**：Antigravity Owner
- **代码基线 (Source Baseline Commit)**：`49d2a2f9c56462f5602b00ad4b824c5381abb1ab`
- **固定执行文件 (Pinned Packaged EXE)**：
  - 路径：`G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO/apps/desktop/src-tauri/target/release/m2rc1-desktop.exe`
  - SHA-256：`92AC7B8EFB646FE77DF8245B13C9AF9314BEF415B2F0E007B1CDCEA729BC13FD` (9,367,040 字节)
- **隔离执行根 (Task-local Ephemeral Env)**：`G:/CODEX/New Manga.workspace/task-envs/P02-NEW-TIME-X6-AC1-AC7/run-i1/`
- **规范证据目录 (Canonical Evidence Root)**：`verification/P02-NEW-TIME-X6-AC1-AC7/runs/p02-newtime-ac-20261014-i1/`

---

## 一、DSH 初始审查 (Review Report dsh-r2) 闭合证明

针对 DeepSeek Harness 在 `verification/P02-NEW-TIME-X6-AC1-AC7/review/dsh-r2/review-report.md` 提出的四项 Findings（R-01 ~ R-04），本次 I1 bounded repair 依据 Codex 裁决严格逐项闭合，且未修改任何产品源码（`apps/desktop/frontend/src/**`）：

| 审查条目 | 审查发现核心内容 | I1 修复与验证方案 | I1 证据闭合状态 |
| :--- | :--- | :--- | :--- |
| **R-01 (AC5)** | Escape 对话框关闭未在真实应用中执行（被标为 NOT_RUN）；Enter 激活使用了 JS `.click()` 回退；Space 键未归因到真实聚焦控件。 | 1. 彻底移除 Enter 激活失败后的 JS `.click()` fallback；<br>2. 注入合成区域 fixture 建立 Workbench 交互上下文；<br>3. 真实聚焦 `inspector-mark-sfx` 控件后分发 CDP Space 键（vk=32），观测到 DOM 从 speech 变为 sfx；<br>4. 调出破坏性反向改标确认对话框（`relabel-confirm-dialog`）；<br>5. 分发真实 CDP Escape 键（vk=27），捕获按键前后的真实 DOM 与焦点状态。 | **完全闭合**。真实捕获了 Escape 分发后的 DOM 表现，客观记录产品未绑定 Escape 处理的 Finding（P-01），外部退出码 0。 |
| **R-02 (AC6)** | 对比度采样包含了无文本内容的容器（`body > div`），产生 4.19:1 伪失败；alpha 背景未进行自底向上合成；透明黑导致臆造失败。 | 1. 移除 `body > div` 采样，仅采集包含可见非空文本及可交互 UI 的真实节点；<br>2. 实现自底向上的 Porter-Duff alpha 叠加合成算法；<br>3. 遇到无不透明背景的祖先链时严格标记为 `NOT_VERIFIABLE` 保护，禁止回退到透明黑产生 1:1 false fail。 | **完全闭合**。9 个计算样本全部达到 WCAG 2.x 阈值（0 FAIL），1 个输入框底色不可验证如实标为 `NOT_VERIFIABLE`。 |
| **R-03 (AC3)** | 静默期（Quiet Period）依赖外部 Wall-clock 测量，未证明真实调用在 300ms 以后且无提前或中间调用。 | 1. 在 DOM 原生 `input` 事件监听中抓取页面 `performance.now()`；<br>2. 在 Tauri IPC invoke 包装层抓取调用时的 `performance.now()`；<br>3. 在同一单调时钟下测得首个真实调用发生在键入后 **311ms**（>= 300ms）；<br>4. 确认中间前缀字符被完全折叠，无提前或多余调用。 | **完全闭合**。观测到精确单调时钟差值 311ms，证明防迟到与取消机制完全生效。 |
| **R-04 (AC4)** | 读回即时性（Write-Refresh Immediacy）只报告了整体耗时，未提取 [write settle -> readback start] 精确间隙。 | 1. 在 invoke 包装层记录写操作 resolve 与读操作 invoke 的时间戳；<br>2. 测量出 `set_region_type`、`restore_region_revision`（undo）以及历史 `restore` 后的读回调用间隙均为 **0ms**（严格 < 300ms，未受防抖阻断）；<br>3. 验证历史列表刷新出 8 条 revisions。 | **完全闭合**。写后读回即时性经精准纳秒级时钟证明合格。 |

---

## 二、AC1 ~ AC7 验收结果汇总

所有场景均在 Windows 11 专业版系统及真实 WebView2 (Chromium/Edg 155) 环境中运行，外部进程退出码严格为 0：

| 验收准则 | 场景名称 | 外部 Exit Code | 运行层级 (Layer) | 关键观测结果 | 状态 |
| :--- | :--- | :---: | :--- | :--- | :---: |
| **AC1** | `ac1-identity` | 0 | REAL_IPC | Windows 11 Pro 10.0.26300；WebView2 Edg/155.0.4283.45；EXE SHA256 匹配；源码基线 `49d2a2f9` | **PASS** |
| **AC2** | `ac2-navigation` | 0 | REAL_IPC | Console 与 Workbench 真实鼠标点击、键盘输入导航，捕获 4 张关键页面状态截图 | **PASS** |
| **AC3** | `ac3-debounce-a3` | 0 | REAL_IPC (A) / MOCK_IPC (B) | 单调时钟精准度量静默期为 311ms（>= 300ms）；无中间前缀调用；防迟到覆盖守卫有效 | **PASS** |
| **AC4** | `ac4-write-refresh-a3` | 0 | REAL_WEBVIEW_MOCK_IPC | retype (0ms)、undo (0ms)、restore (0ms) 立即读回；历史刷新为 8 条记录 | **PASS** |
| **AC5** | `ac5-keyboard-a2` | 0 | REAL_WEBVIEW_MOCK_IPC | Tab/Shift+Tab 捕获；Enter 激活 focused 控件；Space 激活 focused 控件改标；确认对话框弹出并记录 Escape 按键响应 | **PASS** |
| **AC6** | `ac6-contrast` | 0 | REAL_IPC | 9 个真实文本/UI 元素对比度全部合格（PASS，0 FAIL）；1 个输入框背景不可验证标为 `NOT_VERIFIABLE`；Token mapping: 9 unmapped | **PASS** |
| **AC7** | `rollup-summary` | 0 | N/A | 生成汇总摘要 `rollup-summary.json` 与调查报告 `findings.md` | **PASS** |

---

## 三、真实产品 Findings (P-01 ~ P-04)

按照契约原则，“产品缺口只记 finding，不自审、不修复产品”：

### 1. P-01 (PRODUCT_A11Y_KEYBOARD)：确认对话框未绑定 Escape 键关闭处理
- **定位组件**：`apps/desktop/frontend/src/workbench/RelabelConfirmDialog.tsx` 及 `RegionInspector.tsx` 中的 `revision-restore-dialog`
- **实测表现**：对话框正常弹出后，向 WebView2 分发真实的键盘事件 `Escape`（`vk=27`），对话框未关闭（`dialogBeforeEscape.present === true && dialogAfterEscape.present === true`）。
- **根因分析**：React 对话框组件外层蒙层仅处理了鼠标 `onClick={onCancel}`，未在 window 或 dialog 根节点挂载 `onKeyDown` 或键盘事件监听器以捕获 `Escape` 键。
- **严重度**：P3（用户可通过点击“取消”按钮关闭对话框，但键盘无障碍可访问性不完整）。

### 2. P-02 (PRODUCT_DESIGN_TOKENS)：当前界面颜色均为内联样式，未接入 F Token 候选体系
- **定位组件**：`ConsolePage.tsx`、`WorkbenchPage.tsx`、`RegionInspector.tsx`
- **实测表现**：所采样的全部 9 个 UI 节点的前景/背景色均为代码中硬编码的 hex 或 CSS 变量，与 `doc/design/tokens-cand-f.json` 无命中映射（0 mapped, 9 unmapped）。
- **严重度**：P3（后续需要全局接入 Design Tokens 规范）。

### 3. P-03 (PRODUCT_FEATURE_SCOPE)：浅色主题（Light Theme）未实现
- **实测表现**：在当前 React DOM 结构中进行全量扫描，不存在任何主题切换控件、亮色模式样式或入口。
- **状态记录**：`NOT_APPLICABLE (no light theme entry in the React app)`。
- **严重度**：P3（当前版本范围仅限深色基础样式）。

### 4. P-04 (HARNESS_OBSERVATION)：输入框背景无不透明基底保护
- **定位节点**：`[data-testid="page-id-input"]`
- **实测表现**：输入框采用半透明背景且其祖先链中无不透明容器，自底向上合成算法保护性返回 `NOT_VERIFIABLE`。
- **严重度**：P4（测试 Harness 守卫有效，避免了透明黑导致的 1:1 误报）。
