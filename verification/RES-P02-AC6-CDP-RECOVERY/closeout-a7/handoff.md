# RES-P02-AC6-CDP-RECOVERY Closeout A7 交接文档（Handoff）

- **Task ID**：`RES-P02-AC6-CDP-RECOVERY`
- **Owner**：`antigravity`
- **Lead / Integrator**：`Codex` (epoch=3)
- **Reviewer**：`dsh` (待执行 bounded review)
- **交付状态结论**：`READY_FOR_BOUNDED_REVIEW`
- **固定 Source HEAD**：`a8d9219ba192c9a7feb1437240e51535938073fa`
- **固定基线 Commit**：`49d2a2f9c56462f5602b00ad4b824c5381abb1ab`
- **固定 Package EXE 路径与校验**：
  - 路径：`G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO/apps/desktop/src-tauri/target/release/m2rc1-desktop.exe`
  - SHA256：`92AC7B8EFB646FE77DF8245B13C9AF9314BEF415B2F0E007B1CDCEA729BC13FD`
  - 大小：9,367,040 字节

---

## 1. a7 原始成功证据文件、SHA256、执行命令与退出码

原始证据目录：`verification/P02-NEW-TIME-X6-AC1-AC7/runs/p02-newtime-ac-20261014-i2/ac6-contrast-a7/`

### 1.1 文件清单与 SHA256 指纹

| 文件名 | 大小 (Bytes) | SHA256 校验和 | 说明 |
|---|---|---|---|
| `ac6-contrast.json` | 21,200 | `4B011CB7FA71289EC90F4CB7BBBDE1913CC5245B34AA3DA37EC4F64DE1944BD0` | 完整 10 样本 DOM 真实对比度计算表 |
| `execution-metadata.json` | 3,266 | `C11B4176D1FBCF00A0D9D3648CADB2E98E92239C681E16BBFF07AD781306462D` | 运行元数据，记录 exit code 0 与环境配置 |
| `ac6-workbench.png` | 27,967 | `72F2CD2703FAEE36CB7AB4E229C1AE7FD3540A1D70F70FEDF4A97C73F6ECECE2` | CDP 采集瞬间捕获的 Workbench 界面截图 |
| `ac6.stderr.log` | 398 | `F6EE38662C84F4864D761864D0B9DD8938A8364611B017A077480DBF51A39C1F` | 运行时 stderr 输出 |
| `ac6.stdout.log` | 0 | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` | 运行时 stdout 输出（空文件） |

### 1.2 采样执行命令与退出码

- **实际执行命令**：`node apps/desktop/frontend/e2e/p02-new-time/ac6-contrast.mjs`
- **执行退出码**：`0`（记录于 `execution-metadata.json#node_exit_code`）
- **直接采集差异说明**：本次采集直接运行于用户交互式桌面会话中，无外层 runner 脚本包装，因此直接产出并记录 `execution-metadata.json`，无外层 `runner-execution.json`。如实记录直接采集差异，严格禁止补造虚假 runner 文件。

### 1.3 核心数据核验点

- **总样本数**：10
- **计算数**：10
- **通过数**：10
- **失败数**：0
- **未决/不可验证数**：0
- **Alpha 合成触发**：`false`
- **`[data-testid="page-id-input"]` 实测值**：
  - 前景色：`rgb(216.0, 224.0, 232.0)`
  - 背景色：`rgb(16.0, 20.0, 24.0)`（`alpha=1`，不透明原生背景）
  - 背景来源：`INPUT[page-id-input]`
  - `alpha_compositing_applied`：`false`
  - 对比度比值：`13.87`（≥ 4.5）
  - 判定结果：`PASS`

---

## 2. 现存失败历史（完整保留）

本次交付完整保留既有失败历史，不进行任何形式的隐瞒或覆盖：

1. **I1 保留的 4 次失败尝试**：
   - `ac3-debounce-a2`：observer wrapper 未进入 `ACTIVE`。
   - `ac4-write-refresh`：未找到 `[data-testid="region-frame-syn-region-ac4-001"]`。
   - `ac4-write-refresh-a2`：未找到 `[data-testid="region-frame-syn-region-ac4-001"]`。
   - `ac5-keyboard`：未找到 `[data-testid="inspector-revision-history"]`。
2. **I2 AC6 的 4 次启动失败**：
   - `ac6-contrast-a1-failed` (9334)：CDP 未建立，45s 超时，`node_exit_code=1`。
   - `ac6-contrast-a2-failed` (9335)：CDP 未建立，45s 超时，`node_exit_code=1`。
   - `ac6-contrast-a3-failed` (9336)：CDP 未建立，45s 超时，`node_exit_code=1`。
   - `ac6-contrast-a4-failed` (9333)：CDP 未建立，45s 超时，`node_exit_code=1`。
3. **RES CDP 恢复排查阶段的 3 组对照实验**：
   - 在 DSH 非交互式桌面/窗口站环境内，固定 EXE 启动即触发 Win32 `0x80070578（无效的窗口句柄）` 崩溃，导致无法建立 CDP 连接。

---

## 3. 未验证项清单（Non-verified Items / Bounded Exclusions）

根据冻结的 Resolution 边界与既有已知限制，以下项明确列为本轮未验证/范围外限制：

1. **产品代码中的 Escape 键关闭对话框**：
   - React 前端代码中 `RelabelConfirmDialog / RevisionRestoreDialog` 尚未接入 Escape 按键事件处理逻辑，属于已知产品缺陷 Finding P-01。
2. **Design Tokens 接入**：
   - 界面当前使用 React 运行时行内样式，F token 体系尚未完成映射（0 mapped, 10 unmapped），属于已知 Finding P-02。
3. **浅色主题支持**：
   - 产品暂无浅色主题功能或入口，标记为 `NOT_APPLICABLE`，属于已知 Finding P-03。
4. **真实后端全量业务交互**：
   - AC3/AC4/AC5 在 I1 阶段基于 Real WebView + Mock IPC / Synthetic DB 进行验证，未包含真实完整持久化漫画项目加载的全链路验证。
5. **完全脱离交互式桌面的无窗口 CI/CD 自动化**：
   - 固定 EXE（Tauri/WebView2）依赖能创建顶层窗口的 Win32 用户会话暴露 CDP；在纯无窗口、无交互权限的后台作业会话中仍会触发 0x80070578 错误。

---

## 4. 派生产物与交付目录

本轮交付新增文件如下：
- `verification/RES-P02-AC6-CDP-RECOVERY/closeout-a7/rollup-summary.json`
- `verification/RES-P02-AC6-CDP-RECOVERY/closeout-a7/findings.md`
- `verification/RES-P02-AC6-CDP-RECOVERY/closeout-a7/handoff.md`
- `verification/RES-P02-AC6-CDP-RECOVERY/closeout-a7/owner-evidence-manifest.json`

---

## 5. 结论与权限约束

- **结论**：`READY_FOR_BOUNDED_REVIEW`（仅代表 AC6 证据采集层闭合，已具备供独立 Reviewer 审查的完整证据）。
- **禁止过度宣称**：禁止将证据采集成功写成整个产品或父 Task 完成。
- **禁止自审**：Owner（antigravity）不得审核自身工作。
- **禁止合并主线**：变更严格停留在任务分支，等待主控 Codex 集成裁决。
