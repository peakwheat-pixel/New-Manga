# P15 独立 Review（R1，Coordinator 路由的 Reviewer=dsh）

| 项 | 值 |
|---|---|
| Task | P15 设置页（设计基线 §5；契约 P15-C1 §7 开放清单） |
| Owner | ZCode（经 DSH 原生 `subagent_zcode`） |
| Reviewer | **dsh**（本会话，`route-agent.py` 路由；Owner 已机器排除） |
| 交付 | 实现 `e5f1a719bdaf482da027498671490c585a376bd3`；HEAD `ee19898fc`（证据补全） |
| 基线 | `22f0024cc` |
| 复核环境 | 独立 Reviewer 工作树 `worktrees/P15-review`（detached `ee19898fc`，含三 junction） |
| 结论 | **approved** |

## 1. 我**亲自复跑**（不引用 Owner 日志）

| 套件 | 我的实测 |
|---|---|
| `npm --prefix apps/desktop/frontend test` | **28 files / 274 tests passed**，exit 0 |
| `npm --prefix apps/desktop/frontend run build` | exit 0（557ms） |
| `python -m pytest tests/core -q` | **407 passed** |
| cargo source（`--skip packaged_sidecar_tests`） | **95 passed / 0 failed / 1 ignored** |
| cargo packaged（`M2RC1_PACKAGED=1`，`--test-threads=1`） | **12 passed / 0 failed** |

## 2. 逐项验证

| # | 验证项 | 方法 | 结果 |
|---|---|---|---|
| V1 | 范围 | `git diff --name-only 22f0024cc..HEAD` | **PASS**：仅 `apps/desktop/frontend/src/{settings,testSupport}/**` + Handoff/Task + `verification/P15/**`；**无越界**；**零** Rust/Core/契约/Schema/依赖改动 |
| V2 | **AC2 只开放清单内分区** | 读 `SettingsPage.tsx` + 契约 §7 | **PASS**：`provider` 开放（ProviderProfilePanel + CapabilityBindingPanel）、`network` 开放（NetworkProfilePanel）、`translation` **混合**（SfxPolicyControl 开放 + 「翻译参数/上下文策略」禁用）、其余 8 分类禁用；**11 个禁用行**（含 G2 专项原因、排版分类下的"阅读方向"）与契约 §7 禁用表**逐条一致** |
| V3 | 禁用态语义 | 读测试 | **PASS**：专设 describe "visible, not operable, reasoned (AC2)" + `assertDisabledSection` 断言 `aria-disabled=true`、原因含"等待 section schema 冻结"、**区内无可用控件** |
| V4 | **AC3 Secret 边界** | 读实现 + 测试 | **PASS**：`credential_put` 请求体恰为 `{target,intent}`（含禁键清单断言）；Profile 写入键集**精确等于**契约；`CredentialField` **渲染零 input**；`client.ts` **结构性不存在**通用 `updateSection` 透传；`errors.test.ts` **注入含路径与凭据的原始错误并断言投影后不含 "secret"** |
| V5 | **§9 封闭错误投影** | 读 `errors.ts` + `SettingsErrorBar.tsx` | **PASS**：`SafeSettingsMessageKey` 为封闭联合（严格 8 键）、`SETTINGS_MESSAGE_TEXT` 为 `Record<该联合,string>`、未知键兜底 `SETTINGS_UNAVAILABLE`；DOM 唯一出口按 `message_key` 渲染 + 封闭 category/phase/action 标签 |
| V6 | **AC4 状态矩阵** | 读实现 + 测试 | **PASS**：五态齐备；`null` 与 `{}` 可区分（null/空/已设三态测试）；**保存失败保留草稿**（测试名即证据：`"a failed save keeps the draft and shows the closed conflict projection (AC4)"`）；`INVALID_REQUEST` 字段级高亮 |
| V7 | AC1 布局与分类 | 读实现 | **PASS**：Nav 固定宽度 + content panel；**十二分类顺序 = 冻结数组**；切换为本地状态、**无子路由** |
| V8 | 无发明 wire | 命令名逐字比对契约 | **PASS**：Provider/Network/Binding/Resolution 专用命令名与契约冻结集**逐字一致**，且**17 个命令名由测试常量钉死**；既有 `settings_get`/`settings_update_section` 语义未改 |
| V9 | 既有测试未弱化 | diff | **PASS**：`client.test.ts`、`SettingsPanel.test.tsx` **未被改动**；测试总数由 220 → **274**（+54） |
| V10 | 证据诚实性 | 读 `verification/P15/**` | **PASS（范例级）**：5 份正确运行 **exit 0**；**保留**未过滤首跑的失败日志并**如实命名为 `cargo-test-unfiltered-first-run.log`（exit 101）**，且在 Handoff 中说明其为 `packaged_sidecar_tests.rs:23` 的 `M2RC1_PACKAGED=1` **环境门卫 fail-closed**，**非代码回归**（与我的独立复跑一致） |
| V11 | 交付卫生 | `git status` | **PASS**：cargo 重生成的 39 项 tauri 产物经核实**仅行尾噪音**且**已还原未提交**；`verification/P04/diagnostic_*.jsonl` **未入库** |
| V12 | 如实限定 | 读 Handoff | **PASS**：明确 `GUI e2e NOT_RUN`（`0x80070578`）、未实现其他三页、未自行发起 Review、未自行接收交付、未合并主线；治理检查器未入库亦如实声明 |

## 3. 结论：approved

设置页严格落在 P15-C1 契约 §7 的开放清单内：四个开放面全部经**冻结 wire** 实现、**11 个禁用分区**逐条"可见/不可操作/有原因"、**Secret 四处零暴露**（含三层反例测试）、错误走**封闭投影**、状态矩阵完整且**保存失败保留输入**、零产品代码越界、**证据诚实且自纠**。**五套件由我独立复跑全绿。**

## 4. Findings 与 closeout 处置

1. **RV-P15-01（P3，纵深防御，不要求返修）**：`client.ts` L138/148/173/408 以 `(error as Error)?.message` 作错误 code 并插值进 `SettingsClientError.message`。**判定不构成泄露**——`.message` **仅出现在 client 层**，组件层零使用、**无 `console.*`**，DOM 唯一出口 `SettingsErrorBar` 只按 `message_key` 渲染且未知键兜底为 `SETTINGS_UNAVAILABLE`。**建议加固**：未知错误直接映射固定白名单键，不携带原始文本。
2. **RV-P15-04（P2，记录缺陷，closeout 修正）**：**7 条证据 pin 均不可移植验证**。Owner 按其工作树的 **LF** 字节取哈希，而提交 blob 为 **CRLF**（`core.autocrlf=true`）→ 同一 pin 在**任何 fresh checkout 或主仓库**（检查器运行处）**校验失败**。**处置**：closeout 在**主仓库**按规范磁盘字节**复算全部 pin**，并登记该缺陷（**BL-16 类第 7 次**）。
3. **Host 侧 wire 配对缺口（新增 DAG 依赖，非本 Task 缺陷）**：G21/G22/G23 的专用命令由 P15-C1 **契约冻结**，但 **Tauri host 侧注册属后续配对 Task（Core 2.6）**；当前二进制内这些操作会落入 §9 `SETTINGS_UNAVAILABLE` 投影（UI 状态矩阵完整，wire 形状经**注入 invoke** 验证）。**处置**：**新建后续 Task `P15-HOST-1`**（host 侧注册三条命令面）并写入 DAG，使"UI 已交付但不可端到端操作"这一事实**有据可查**，不留在口头。
4. **BL-20 范围观察（已关闭为良性）**：`apps/desktop/frontend/src/testSupport/jsdomEvents.ts` 落在声明允许范围（`settings/**`）之外，但为**纯测试工具**且被 4 个面板测试实际引用（`setNativeInputValue` 8 处 / `setNativeSelectValue` 9 处），**非产品代码、不弱化**。已在 **BL-20** 登记通则以覆盖此类路径。
5. **待用户确认三项**（Owner 已在 Handoff 列出，均**未自行放宽**）：① "阅读方向"挂在"排版样式"分类下是否接受；② **G25 开放范围是否扩大**；③ **Network 连接测试面是否保留**。→ closeout 原样保留，纳入 [decision-request](../PROJECT-ORCHESTRATION-20261016/decision-request-20261016.md)。
