---
task_id: P15
author: ZCode
recipient: Codex
base_commit: 22f0024cc6c701b73f6d38a7bdca53fdc2ef34ac
delivery_head: null
status: in_review
---

# Handoff：P15 设置页 Settings（四页之设置）——前端实现

> `delivery_head` 在本 Handoff 所在的实现提交产生后，由后续文档提交回填（BL-15：不自引用即将产生的 SHA）。`status: in_review` 为合法状态词。

## 交付结果

**范围：仅前端（`apps/desktop/frontend/src/settings/**` + `src/testSupport/jsdomEvents.ts` 新测试助手），零改动 Tauri/Rust、Python Core、契约、Schema、迁移、依赖清单。**

实现提交包含：

| 路径 | 内容 |
|---|---|
| `src/settings/types.ts` | 扩展 G21/G22/G23 全部冻结 DTO（ProviderProfile/CapabilityBinding/NetworkProfile/NetworkTestResult/CredentialTarget）+ 前端输入校验助手（endpoint 无 userinfo/query/fragment、mode/scheme 匹配、TLS 危险确认前置） |
| `src/settings/errors.ts` | **P15-C1 §9 封闭错误投影**：`SettingsSurfaceError{category,phase,action,message_key}` 八值 message_key 固定中文文案；`projectSettingsError` 只消费稳定 code，敌意 payload（路径/stack/Bearer）在投影层被丢弃（有测试反例） |
| `src/settings/client.ts` | 保留既有 `getSfxPolicy/saveSfxPolicy`（既有测试零变化）；新增 P15-C1 §2 全部 17 个专用 wire 命令名常量 pin + 方法（G21 CRUD/绑定 set/clear/resolve、G22 credential_put/clear、G23 CRUD/test/default_set/clear/resolve）+ `getSfxSection()`（单节读取，JSON null 可区分）；错误码提取支持 `{code}` envelope；**结构性不存在通用 `updateSection(section,values)` 透传方法**（有测试断言） |
| `src/settings/SettingsPage.tsx` | **重写**：SettingsCategoryNav 200px 固定 + SettingsContentPanel；**十二分类顺序冻结**（Provider、网络/代理、OCR、翻译、图片修复、排版样式、模型/GPU、任务/并发、缓存/Revision、回收站、备份/恢复、Plugin/Hooks）；分类切换 React 本地状态**无子路由**；↑/↓ 键盘导航 |
| `src/settings/DisabledSection.tsx` | 禁用分区占位（可见标题 + disabled 控件 + 原因「等待 section schema 冻结」；无任何 input/select/textarea） |
| `src/settings/SfxPolicyControl.tsx` | SFX 策略面板（翻译分类下）：五态矩阵完整；null 未设置占位 + 默认值填充动作；保存 busy；**保存失败保留 draft** |
| `src/settings/ProviderProfilePanel.tsx` | G21 Profile 列表/新建/编辑/删除（两步确认）；G25 白名单字段级本地校验（INVALID_REQUEST 高亮）；失败保留草稿 |
| `src/settings/CapabilityBindingPanel.tsx` | G21 绑定 set/clear（global/book/chapter scope）；当前绑定 resolve 展示；Run 临时范围仅经 StartRun.overrides（面板文案明示） |
| `src/settings/NetworkProfilePanel.tsx` | G23 全面板：CRUD、全局选择 set/clear + resolve 来源显示、**TLS 关闭显式危险确认门**（未确认保存禁用；提交带 `confirm_disable_tls_verification: true`；行内 `tls_verification_state` 可见）、fallback 默认 false 且文案明示「不静默直连」、六阶段测试结果投影（passed/failed/not_run/not_applicable + `direct_fallback_used=false` 常显） |
| `src/settings/CredentialField.tsx` | G22 凭据面：**组件内无任何输入控件**（Secret 永不进 WebView，结构性保证）；只显示 configured/missing + masked hint + 一次性 put/clear |
| `src/settings/SettingsErrorBar.tsx` | 错误条组件（只渲染 §9 投影的固定文案 + category/phase/action） |
| `src/testSupport/jsdomEvents.ts` | jsdom 下 React onChange 不响应手动 input 事件的测试助手（native value setter + input/change 双事件；BookshelfToolbar onInput 双绑先例的提取） |
| 测试 | `SettingsPage.test.tsx`（AC1+AC2）、`SfxPolicyControl.test.tsx`（AC3/AC4）、`ProviderProfilePanel.test.tsx`、`NetworkProfilePanel.test.tsx`、`CapabilityBindingPanel.test.tsx`、`errors.test.ts`（§9 投影）、`client.p15.test.ts`（wire pin + payload 形状 + Secret 反例） |
| `verification/P15/*.log` | npm test / npm run build / pytest / cargo 原始日志 + 退出码 |

既有 `SettingsPanel.tsx`/`SettingsPanel.test.tsx`/`client.test.ts` **原样保留**（App.tsx 的 M2 探针 console 视图仍引用 SettingsPanel；未删除/弱化任何既有测试）。

### 十二分类 ↔ 分区开放/禁用对应（AC2）

| # | 分类（固定顺序） | 分区状态 |
|---|---|---|
| 1 | Provider | **开放**：Provider Profile（G21 专用 wire）+ Capability 默认绑定（G21 set/clear） |
| 2 | 网络/代理 | **开放**：Network Profile（G23 专用 wire，含全局选择与六阶段测试） |
| 3 | OCR | 禁用（等待 section schema 冻结） |
| 4 | 翻译 | **混合**：SFX 策略开放（唯一 `settings_update_section` 开放节，仅 `sfx.policy` 三值）；「翻译参数/上下文策略」分区禁用 |
| 5 | 图片修复 | 禁用 |
| 6 | 排版样式 | 禁用（排版/Text Style）+ 禁用（**阅读方向**——G24 只读解析无写 wire，作为该分类下独立禁用分区呈现） |
| 7 | 模型/GPU | 禁用 |
| 8 | 任务/并发 | 禁用 |
| 9 | 缓存/Revision | 禁用 |
| 10 | 回收站 | 禁用（G2 明确未授权） |
| 11 | 备份/恢复 | 禁用 |
| 12 | Plugin/Hooks | 禁用 |

AC2 清单全部 11 个禁用分区逐项有 DOM 断言（可见 + 不可操作 + 原因含「等待 section schema 冻结」）。

### AC 对照

| AC | 结果 | 依据 |
|---|---|---|
| AC1 布局与分类 | PASS | `SettingsPage.test.tsx`：200px nav + content panel DOM 断言；十二分类顺序等于冻结数组；切换本地状态无子路由（nav DOM 节点跨切换保持同一性） |
| AC2 可编辑范围 | PASS | 开放四分区全部走专用 wire / sfx.policy；`client.p15.test.ts` pin 全部 17 个命令名与 payload 白名单；无通用透传方法（结构 + 断言双保证）；11 个禁用分区逐项断言 |
| AC3 数据面与 Secret 边界 | PASS | `getSfxSection` 单节读取 JSON null 可区分（测试含 null/`{}`/set 三态）；Secret 不入 DTO 有三层反例测试：credential_put args 恰为 `{target,intent}`（禁键清单断言）、create/update payload 键集恰为 G25 白名单、CredentialField 组件渲染零 input 元素；错误投影敌意 payload 丢弃测试 |
| AC4 状态矩阵 | PASS | loading 骨架 / empty 未设置占位+默认填充 / error 就地错误条+code 本地化（INVALID_REQUEST 字段级高亮、CORE_UNAVAILABLE→SETTINGS_UNAVAILABLE 投影）/ disabled 灰置 / progress busy 态；保存失败保留输入（SFX/Provider/Network 三处测试） |
| AC5 范围与证据 | PASS（见下表） | 前端 vitest 274 passed（28 文件）exit 0；build exit 0；pytest tests/core 407 passed exit 0；cargo source-backed 95 passed/0 failed/1 ignored exit 0 + packaged frozen 12 passed/0 failed exit 0；**GUI e2e NOT_RUN**（无头 Windows WebView2 窗口句柄 `0x80070578`，如实声明；上述全部为 DOM 单测，不表述为 e2e） |
| AC6 交付 | 本 Handoff | 固定 commit + Task 更新 + Canonical Evidence（sha256 按磁盘字节、commit 列原样 `git rev-parse HEAD`、class 仅 CANONICAL/SOURCE_PIN）；未自行接收交付、未合并、未发起自我 Review |

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| 前端套件 | `npm --prefix apps/desktop/frontend test`（vitest run） | Windows，实现提交 | **274 passed / 0 failed，exit 0**（含既有全部测试） | `verification/P15/npm-test.log` |
| 前端构建 | `npm --prefix apps/desktop/frontend run build`（tsc && vite build） | 同上 | **exit 0**（tsc 零错误 + vite 产物 353.54 kB） | `verification/P15/npm-build.log` |
| Core 回归 | `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe -m pytest tests/core -q` | py312 venv，worktree | **407 passed / 0 failed，exit 0** | `verification/P15/pytest-tests-core.log` |
| Rust 回归（source-backed） | `M2RC1_PYTHON=C:/Python314/python.exe cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml -- --skip packaged_sidecar_tests`（P14 既有口径） | worktree 自建 target（未触碰 core-sidecar junction） | **95 passed / 0 failed / 1 ignored（12 filtered out），exit 0** | `verification/P15/cargo-test-source.log` |
| Rust 回归（packaged frozen EXE） | `M2RC1_PACKAGED=1 cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml packaged_sidecar_tests -- --test-threads=1 --nocapture` | frozen bundle 经既有 junction（core_service.exe 等真实进程） | **12 passed / 0 failed，exit 0** | `verification/P15/cargo-test-packaged.log` |
| Rust 首跑记录（未过滤口径） | 无 env 的 `cargo test --locked` 全量 | 同上 | 95 passed / **12 failed**——全部是 `packaged_sidecar_tests` 的**环境门卫 fail-closed**（`packaged_sidecar_tests.rs:23` 断言 `M2RC1_PACKAGED=1`，非代码回归）；按 P14 口径分跑后双绿 | `verification/P15/cargo-test-unfiltered-first-run.log` |
| GUI e2e | 未运行 | 无头 Windows | **NOT_RUN**（WebView2 句柄 `0x80070578`） | 本行声明 |

- **治理检查器**：`tools/governance/check.ps1` **未入库**（worktree 检出内不存在；仅主仓库 untracked 有一份），无法在工作树内运行——如实说明，不以其他输出冒充。
- 运行时说明：G21/G22/G23 专用 wire 为 P15-C1 冻结目标，**Host 侧命令注册属后续 Task**；在 Host 配对 Core 2.6 之前调用会失败并落入 §9 `SETTINGS_UNAVAILABLE` 投影（UI 侧完整实现状态矩阵，测试经注入 invoke 验证 wire 形状）。

## 接收方式

- 仓库：`G:/CODEX/New Manga`；Owner worktree：`G:/CODEX/New Manga.workspace/worktrees/P15`（branch `zcode/P15`，base `22f0024cc`）。
- 复现：worktree 内 `npm --prefix apps/desktop/frontend test`；日志已归档 `verification/P15/`。
- 前置：node_modules/dist 为指向主仓库的零拷贝 junction（未重建）。

## 待用户确认项（产品取舍，未自行放宽）

1. **阅读方向分区的归属**：AC2 禁用清单含「阅读方向」但十二分类无对应分类；本实现将其作为「排版样式」分类下的独立禁用分区呈现。如需独立分类入口须改 AC1 十二分类（产品决策）。
2. **G25 开放范围是否扩大**（如开放 G24 只读 OverrideSummaryPanel 展示）：本 Task 严格未实现 `settings_resolve_overrides` 调用；扩大须用户确认 + 逐节契约。
3. **连接测试（TestNetworkProfile）**：契约 §2 命令面含 `settings_network_profiles_test`，本 Task 按 AD001 §5.3 NetworkProfilePanel 职责实现了测试按钮与六阶段结果投影；若认为 P15 应只做 CRUD 不做测试面，可整块禁用（实现已隔离，移除按钮即可）。

## 下一任务建议（必填）

- Task ID / 标题：P15 独立 Review（DSH 或 Antigravity）→ 通过后 Codex 集成。
- 推荐 Agent / Reviewer：Reviewer = DSH（非作者）或 Antigravity；集成 = Codex。
- 推荐原因与前置依赖：P15 实现交付完成，按协作协议需非作者 Review + Codex 集成验证。
- Recovery point：仓库 `G:/CODEX/New Manga`，Owner worktree `G:/CODEX/New Manga.workspace/worktrees/P15`，branch `zcode/P15`，base `22f0024cc`；delivery_head 见 Task 文件回填值。
- 允许修改路径：`doc/reviews/P15-*.md`、Review 自建 evidence 目录。
- 禁止范围与新增授权条件：不得修改实现代码、契约、`doc/STATUS.md`/`REBASELINE_PLAN.md`；不得把自己的审查写成 Owner 自审。
- 交付物：Review 报告（按 REVIEW 模板）。
- 验证命令、环境与完成 Gate：复跑 `npm --prefix apps/desktop/frontend test`（274 expected）；审 AC2 禁用分区逐项断言与 Secret 反例测试；Gate = 无未解决 P0/P1。
- 可直接转发给 Agent 的指令：`请对 P15 设置页前端交付做独立 Review。Owner worktree G:/CODEX/New Manga.workspace/worktrees/P15（branch zcode/P15）。逐条核验 AC1 十二分类顺序与 200px 布局、AC2 十一禁用分区可见/不可操作/原因断言与 G25 白名单、AC3 null 区分与 Secret 不入 DTO 反例、AC4 五态矩阵与保存失败保留输入、AC5 证据日志与 GUI e2e NOT_RUN 声明。复跑 npm test（期望 274 passed）。只读；结论按 REVIEW 模板写入 doc/reviews/，交 Codex 裁定集成。`

## 风险与遗留

- Host 侧 G21/G22/G23 命令注册未实现（契约明示「不代表运行时已实现」）——设置页在当前二进制内 Provider/Network/凭据操作会得到通道失败投影；属后续 Host/Core 配对 Task（Core 2.6）。
- `SettingsPanel.tsx`（M2 探针旧组件）仍被 App.tsx console 视图引用，保留未动；后续 Shell 清理 Task 可移除。
- 前端表单交互在 jsdom 下依赖 onChange+onInput 双绑（BookshelfToolbar 既有先例）；`src/testSupport/jsdomEvents.ts` 记录了该环境事实。

## 实验附录

不适用（非实验任务）。
