---
task_id: M2-SETTINGS-UI-SFX-POLICY
author: ZCode
recipient: Codex（Integrator，契约裁决与集成）；DeepSeek Harness（非作者 Reviewer，mock 通道面）
base_commit: f534c3e7
delivery_head: 8c798aed
status: blocked_on_contract
---

# Handoff：M2-SETTINGS-UI-SFX-POLICY（设置页 SFX 策略键接入）

**结论速览：AC1 勘察判定 = BLOCKED_ON_CONTRACT（需新 Tauri 命令，触 M2-C1 冻结契约面）——已按任务书即停登记移交集成方；AC2（UI）+ AC3（测试）已按任务书许可先行完成，全程 mock invoke 通道，Rust/Python/契约零改动。**

## 交付结果

### AC1 IPC 通道勘察结论（落笔前完成，全部有代码锚点）

1. **生产 invoke 表面盘点（`apps/desktop/src-tauri/src/main.rs:557-563`）**：生产模式注册恰好 5 个命令——`issue_resource_url` / `revoke_ref` / `revoke_resource_refs`（资源通道）、`core_ping` / `library_list_books`（core/library）。probe 模式另有 `probe_config` / `probe_write_results` / `probe_exit` / `probe_issue_url`（main.rs:530-538）；ac1 测试模式另有 `ac1_request` / `ac1_write_results` / `ac1_exit`（main.rs:544-551）。**任何模式都没有 settings 读/写命令——既无通用 get/update，也无逐键命令**。前端 `commandSurface.test.ts` 同样 pin 了该表面（production=3 产品命令 + probe/ac1 各自模式面）。
2. **前端现状**：产品 React 应用**尚无设置页**（App.tsx = M2-RC2 运行时探针宿主 + LibraryPanel 书架面板；与任务书"既有设置页"假设不一致的事实偏差，见下）。既有设置控件模式不存在；可复用的既有模式 = LibraryPanel 的 client 注入式组件 + 显式错误块 + 无自动重试。
3. **Python core 侧（零改动已可用）**：读 = `PipelineDefaultsService.read().settings["sfx"]["policy"]`（`src/application/settings/pipeline_defaults.py:59`）；写 = `save_settings_section("sfx", {"policy": ...})`（同文件 :105，`ocr.script` 同通道 upsert 语义）。键语义（三值/默认 skip/装配生效/仅新建 region）= M2-SFX-TRANSLATE-ENTRY 交付，`verification/M2-SFX-TRANSLATE-ENTRY/integration.md`。
4. **契约判定**：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` 冻结 React↔Tauri↔Python 消息边界；settings 通道不在其命令目录（§5 目录纯 PROPOSAL、无 runtime）。接通 UI 必须新增 Tauri 命令（建议对 `settings_get` / `settings_update_section`，见下）+ core 桥方法 + main.rs 三处手工同步面（`command_allowlist` 常量 / `generate_handler!` 字面清单 / build.rs app-manifest，main.rs:518-524 注释自证"keep all three in sync"）+ capabilities + 前端 commandSurface pin 更新。**按任务书 AC1 判定规则："需新命令=触冻结契约，即停登记移交集成方" → BLOCKED_ON_CONTRACT**。`doc/contracts/**` 在禁改面内，未触碰。
5. **建议通道形状（集成方裁决材料，非交付承诺）**：
   - `settings_get` → 返回 `PipelineDefaults.settings` 投影（如 `{"sfx":{"policy":"skip"},"ocr":{...}}`）；缺省/非法值前端已折叠为默认 skip（Core 仍是 fail-fast 权威）。
   - `settings_update_section`，参数 `{section: string, values: object}` → 桥接 `save_settings_section(section, values)`；本 Task 仅传 `{section:"sfx", values:{policy}}`。
   - 命令名已在前端常量+测试 pin（`client.ts` 的 `SETTINGS_GET_COMMAND`/`SETTINGS_UPDATE_SECTION_COMMAND` + `client.test.ts` 首 CASE），裁决改名时该 pin 即漂移警报。

### 事实偏差登记（任务书 vs 代码现状）

任务书 AC2 写"设置页适当分区（翻译/检测相关组）加控件"，预设既有设置页存在；实际不存在。处置（最小键接入协议内，未扩产品范围）：新建**最小 Settings 区组件**（`SettingsPanel`）挂载于 App.tsx 中 LibraryPanel 旁，内含"翻译与检测 (Translation & Detection)"分组；视觉完全复用 LibraryPanel 既有语言（section 边框/按钮/错误块样式），未发明新风格。未来设置页 Task 可整体迁收该组件（client 注入式，零耦合）。视觉/交互升级按 UI 协议说明留待 Qoder 后续审查。

### UI 落点（AC2）

- 组件：`apps/desktop/frontend/src/settings/SettingsPanel.tsx`（挂载点 `App.tsx` 尾部，`<LibraryPanel />` 之后）。
- 分区：section 标题"设置 (Settings)"→ fieldset"翻译与检测 (Translation & Detection)"→ 控件"SFX 翻译策略"。
- 控件：三值 select（`跳过翻译 (skip)` / `翻译 (translate)` / `手动处理 (manual)`，`data-testid="sfx-policy-select"`）+ 保存按钮（draft≠生效值才启用，保存中禁用，`data-testid="sfx-policy-save-btn"`）。
- 当前生效值行：`当前生效值：<标签>`；值为默认 skip 时追加"（默认）"（unset/非法折叠显示默认，Core 仍 fail-fast 权威）。
- 作用域提示（原文照登，事实源=M2-SFX-TRANSLATE-ENTRY r1 R1）：**"保存后重新打开应用生效；仅对此后新建检出的 region 生效（既有页面需重新检出）"**。
- 保存流：`SettingsClient.saveSfxPolicy(draft)` → mock 通道 invoke；失败显式错误块（复用 LibraryPanel 错误块样式，"系统不会自动重试"语义），加载失败同款。
- 快照证据：`verification/M2-SETTINGS-UI-SFX-POLICY/settings-panel-ssr-snapshot.md`（六态 renderToString：default-skip / translate / manual / unset-null / loading / load-error）。

### 变更路径与提交列表

| commit | 内容 |
|---|---|
| `8c798aed`（delivery_head） | `implement(...)`：`frontend/src/settings/`（types/client/SettingsPanel + 2 测试文件）+ `frontend/src/testSupport/mockDom.ts`（LibraryPanel 内联 Mock DOM 提取复用，补 select options/value 面）+ `frontend/src/App.tsx`（+2 行挂载）+ verification 快照。**8 文件 +830 行，Rust/Python/契约零 diff** |
| 本 handoff commit | `doc/handoffs/M2-SETTINGS-UI-SFX-POLICY-8c798aed.md` + Task frontmatter/交付记录回填 |

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| 纪律·基线 | `npx vitest run`（改动前） | node v22 / f99a6c55（批次 release HEAD） | **5 文件 31 passed 0 failed** | 会话记录 |
| AC3 全量 | `npx vitest run`（改动后） | 同上 / 8c798aed | **7 文件 48 passed 0 failed**（基线 31 + 新增 17：client 7 + 组件 10）；既有 31 条零修改 | 本行即证据 |
| AC3 保存调用参数 | `client.test.ts`：saveSfxPolicy 三值各断言 `invoke("settings_update_section", {section:"sfx", values:{policy}})` 精确参数；settings_get 读取断言 | 同上 / 8c798aed | PASS（mock invoke 通道） | `apps/desktop/frontend/src/settings/client.test.ts` |
| AC2/AC3 渲染+挂载 | `SettingsPanel.test.tsx`：三值 selected 标记/unset→默认/作用域文案原文/无变化禁用保存/loading/load-error/2 条 createRoot 挂载流（settings_get 读取渲染、失败显式错误+无重试） | 同上 / 8c798aed | PASS | `apps/desktop/frontend/src/settings/SettingsPanel.test.tsx` |
| AC4 快照 | 临时 esbuild 脚本六态 renderToString（已删，生成方式登记在快照文件头） | 同上 / 8c798aed | 6 态生成 | `verification/M2-SETTINGS-UI-SFX-POLICY/settings-panel-ssr-snapshot.md` |
| 类型纪律 | `npx tsc --noEmit` | 同上 / 8c798aed | EXIT=0 | 会话记录 |
| 禁改面自检 | `git status --porcelain` + `git diff --check` + `git diff f99a6c55..8c798aed --stat` 核对 | 8c798aed | EXIT=0；改动面仅 `apps/desktop/frontend/src/**` + `verification/M2-SETTINGS-UI-SFX-POLICY/**`；`doc/contracts/**`、`src/**`（Python）、`src-tauri/**`（**零 diff，既有命令语义零变化**）、`packaging/**`、`doc/STATUS.md` 零触碰 | commit diff 即证据 |
| NOT RUN：cargo | 未动 Rust，无需求（任务书：cargo 零需求若未动 Rust） | — | NOT_RUN（预期） | — |
| NOT RUN：Python 侧 | 键已可用（M2-SFX-TRANSLATE-ENTRY 21 条绿），本 Task 预期零改动、未动 | — | NOT_RUN（预期） | — |

**未运行/未覆盖（如实）**：真实 Tauri IPC 往返未验证（生产表面无该命令——这正是 BLOCKED_ON_CONTRACT 的内容）；mock 成功不证明生产通道可用；select 的用户事件级交互（change/click 派发）未模拟——无 jsdom/testing-library 依赖，交互语义由 client 层参数断言+挂载流覆盖（测试栈扩展登记为后续候选，未擅自引入新依赖）；可视化截图未做（WebView 运行宿主属后续设置页 Task，SSR 快照为登记形态）。

## 接收方式

- 分支 `agent/zcode/M2-SETTINGS-UI-SFX-POLICY`，worktree `G:/CODEX/New Manga.worktrees/M2-SETTINGS-UI-SFX-POLICY-zcode`，base `f534c3e7`（Task 授权基线；分支 fork=批次 release `f99a6c55`），delivery_head `8c798aed`。
- 复现命令（worktree 根）：
  `cd apps/desktop/frontend && npm install && npx vitest run`
  预期 `7 files, 48 passed`；`npx tsc --noEmit` 预期 EXIT=0。
- 无新依赖（未改 package.json）、无 schema 迁移、无契约变更、无 Rust/Python 改动。

## 下一任务建议（必填）

- Task ID / 标题：**契约裁决与 settings IPC 通道落地**（建议 Task：M2-IPC-SETTINGS-CHANNEL，由集成方/Codex 释放；本 Task 解除阻断后仅需小步回填真实通道）。
- 推荐 Agent / Reviewer：裁决与释放=Codex；通道实现=ZCode 或 Antigravity（Rust 侧）；Review=DeepSeek Harness（非作者）。
- 推荐原因与前置依赖：本 Task 证明唯一缺环=Tauri settings 命令；Python 侧与 UI 组件均已就绪，通道落地后本 Task 的 mock 常量换真实命令名+App 挂载即可端到端。
- Recovery point：仓库 `G:/CODEX/New Manga`，branch `agent/zcode/M2-SETTINGS-UI-SFX-POLICY`，base `f534c3e7` / delivery_head `8c798aed`。
- 允许修改路径（建议）：`src-tauri/**`（新命令+三处 allowlist 同步+capabilities）、`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`（按契约修订流程）、`apps/desktop/frontend/src/settings/**`（命令名对齐）、`apps/desktop/frontend/src/resourceChannel/commandSurface.test.ts`（表面 pin 更新）、`tests/**`（Rust/Python 对齐测试）。
- 禁止范围与新增授权条件：Python `src/**` 预期零改动（桥接已可用）；`packaging/**`、`doc/STATUS.md` 照旧集成方专属。
- 交付物：settings get/update 命令（Rust）+ 契约修订登记 + 前端真实通道对齐 + 三侧测试。
- 验证命令、环境与完成 Gate：`cargo test`（src-tauri）+ `npx vitest run` 全绿 + Python 三套件不回归（530+1skipped 基线）+ 禁改面零触碰。
- 可直接转发给集成方的指令：`请 Codex 对 M2-SETTINGS-UI-SFX-POLICY 做 BLOCKED_ON_CONTRACT 裁决（handoff: doc/handoffs/M2-SETTINGS-UI-SFX-POLICY-8c798aed.md §AC1）：判定 settings_get / settings_update_section 命令面与 wire shape（建议形状在案），按 M2-C1 契约修订流程释放 settings 通道 Task；本 Task 的 UI/测试已 mock 通道先行落地（48 vitest 全绿），通道名裁决后仅需前端常量对齐回填。`

## 风险与遗留

1. **BLOCKED_ON_CONTRACT（本 Task 主登记）**：生产表面无 settings 命令；在契约裁决前，用户经 UI 保存 sfx.policy 不可达（仍只有脚本 `save_settings_section` 路径）。前端已把建议命令名 pin 进测试，改名即触发漂移警报。
2. **设置页尚不存在**：本 Task 落的是最小 Settings 区组件（挂于现运行时宿主页）；独立设置页（产品四页之一）及其导航属后续 Task。Qoder 视觉/交互审查按 UI 协议说明另行派发（handoff 已登记，不阻塞契约裁决）。
3. **语义如实性**：作用域提示按 r1 R1 登记口径（仅新建 region 生效、re-assemble 时机）；若未来 region 级策略更新入口（`Region.apply_sfx_policy`，已登记候选）落地，文案需随之更新。
4. **回退方法**：单 commit 代码面（新文件+App.tsx 2 行），revert `8c798aed` 即完整回退；无数据/契约/schema 影响。
