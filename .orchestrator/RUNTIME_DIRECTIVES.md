# Runtime Directives（用户当轮明确指令）

本文件记录**当前生效的用户明确指令**，供跨轮次恢复时优先遵守。
权威优先级遵循恢复真实性原则：Live Git/FS > guarded governance > 本文件 > Agent 自述。
本文件不是治理文件（不改 DAG/Task 状态）；治理指针仍以 `doc/STATUS.md` / `doc/REBASELINE_PLAN.md` 为准。

| id | 生效时间（Asia/Shanghai） | 指令 | 执行方式 | 失效条件 |
|---|---|---|---|---|
| DIR-1 | 2026-10-15 23:34 | **不打断当前任务**（P06 正在进行，Owner=antigravity） | P06 继续运行至其自身完成/BLOCKED，不 kill、不抢占、不重派 | P06 收口后自动失效（一次性） |
| DIR-2 | 2026-10-15 23:34 | **接下来的任务 Owner 为 codex，直到 codex 额度用完** | 后续每个新释放 Task 的 Owner 路由使用 `route-agent.py --prefer-agent codex`；Owner 参与状态写入 `.orchestrator/tasks/<task>-role.json` | codex 进入 `QUOTA_EXHAUSTED`/`AUTH_FAILED`/`UNAVAILABLE` 时：用 `coordinator-lease.py set-agent-state` 更新 runtime，随后按 router 自然 fallback 重新路由（REBALANCE） |

| DIR-3 | 2026-10-16 17:10 | **只保留一个 Active Coordinator 会话**（用户裁决；起因：出现两个共享同一 lease 的 dsh 会话） | 本会话 dsh 以原子 CAS takeover 递增到 epoch 6 并独占新 lease；其他会话持有的 epoch 5 旧 lease 一律 STALE_COORDINATOR，不得再充当 Coordinator，亦不得抢回 | 用户改判 |
| DIR-4 | 2026-10-17 23:28 | **禁止失败后无限循环**：无论派发给 dsh 自身还是其他 agent，同一失败（同一命令/同一脚本/同一断言/同一隔离根）**最多重试 2 次**；达到上限必须先**停止执行**，输出原始错误输出 + 已尝试假设 + 根因分析 + 修正方案，经 Coordinator 确认后才可再次执行 | ① 所有派发 prompt 必嵌「有限重试条款」（见下节可直接复制文本）；② Owner 达上限即**停手上报**，不得自行"改脚本重跑"；③ Coordinator 发现循环迹象（如重复创建同名隔离根、`codex` 进程数异常增长、长时间 0 提交）**必须立即 `job_kill`** 并如实登记通道、理由与保留产物 | 用户改判 |
| DIR-5 | 2026-10-17 23:58（2026-10-18 00:14 更新） | **目标轮次上限 1000；第 990 轮起停止推进任务** | 到达第 990 轮时：**不再开始新任务、不再派发新 Owner**；只做收尾：产出完整 **Handoff**（现状 / Git pin / 证据 / 未决项 / 恢复点）+ 一份**可直接粘贴给新会话的启动提示词**（含仓库、DAG 与 Task 现状、下一步、硬约束、当前 Coordinator epoch） | 用户改判 |

## 执行备注

- DIR-2 不改变 Reviewer 独立性：Reviewer 仍必须 ≠ Owner，且不得参与该 Task 的 implementation/repair。
- DIR-2 不覆盖 capsule 内的硬 Gate：PREFLIGHT 仍须真实探测；若 codex 预检失败，按 Anti-Thrash 记录失败并 REBALANCE。
- 用户未授权跳过任何 Gate、未授权 push、未授权触碰用户 dirty 内容。

## Codex 派发约定（BL-3 修复，2026-10-16 实测生效）

本机用户级 `~/.codex/config.toml` 设 `[windows] sandbox = "elevated"`，其 elevated provisioning 已结构化失败
（`codex doctor`：`✗ sandbox elevated Windows sandbox provisioning recorded a structured failure`），
导致 `codex exec -s workspace-write` 报 `helper_unknown_error: setup refresh had errors`。

**已实测的修复方式（不改用户配置、不需提权）**：派发命令追加 `-c windows.sandbox="unelevated"`。

```powershell
codex exec --skip-git-repo-check -s workspace-write `
  -c windows.sandbox="unelevated" `
  -m gpt-6-luna -c model_reasoning_effort="xhigh" -o <result-file> <prompt>
```

- 合法值仅 `elevated` / `unelevated` / `mxc`（由 CLI 错误信息确认）。
- 2026-10-16 探测：`-s workspace-write -c windows.sandbox="unelevated"` → **exit 0，命令真实执行，无 setup 错误**。
- 因此**优先使用 workspace-write 沙箱**；`danger-full-access` 仅作为该 workaround 失效时的后备，
  且必须附带"主仓零改动自证"要求。
- 根治方式（可选，需用户决定）：升级/repair Codex CLI（doctor 报告有 0.163.0 可用），
  或在用户配置中把 `[windows] sandbox` 改为 `unelevated`。


## ZCode 派发约定（2026-10-16 实测，UI-DESIGN-1）

本机无 `zcode` PATH 命令；桌面版内置 CLI 为 `E:\Program Files\ZCode\resources\glm\zcode.cjs`，
必须用 `node` 调用并注入三个环境变量（缺 `ZCODE_DATA_BASE_DIR` 会回退到旧数据目录导致模型解析失败）：

```powershell
$env:ZCODE_DATA_BASE_DIR = 'G:\zcode'
$env:ZCODE_BUILTIN_PROVIDER_CONFIG_FILE = 'E:\Program Files\ZCode\resources\config\provider\zcode-builtin.json'
$env:ZCODE_PERSONAL_PROVIDER_CONFIG_FILE = 'G:\zcode\.zcode\v2\provider_config.json'
node $z --prompt <自包含提示> --cwd <worktree> --mode edit --json --locale zh-CN
```

**2026-10-16 更正（重要，推翻同日早先结论）**：ZCode **并非**"无法执行命令"。

- **DSH 原生子智能体路径可用**：用 `subagent_zcode` 派发时，ZCode **可执行 shell**（实测：逐字读回 `doc/REBASELINE_PLAN.md` 的 READY 行，并自报 `SHELL=是`）。
- **受阻只发生在"原始 CLI headless + `--mode edit`"这条路上**：该模式没有 permission client，权限层对 **Bash** 一律拒绝，错误原文 `No permission client configured for Bash`
  （被拒：`powershell`/`pwsh`、`git add`/`git commit`、`certutil`、复合命令与重定向；可用：`git status`/`git rev-parse`/`git diff`/`git log`/`grep`/`ls`/`echo` 等只读白名单）。
- **结论**：这是**我的派发方式缺陷**，不是 agent 能力缺陷。**ZCode 是有效的 Owner/Reviewer 人选**（含需要跑测试与提交的 Task），尤其 UI/UX。

**派发纪律（更正后）**：

1. **首选 DSH 原生通道**：`subagent_codex` / `subagent_agy` / `subagent_zcode`（受管、有完成通知、结果回传），不要用 PowerShell 里的原始 CLI 子进程自造派发；
2. 若确需原始 CLI：必须选用**已获用户授权**的模式（`zcode-dispatch` skill 说明：headless `--prompt` 默认 `yolo`；`build` 变更前请求确认；`edit` 命令仍需确认；**只有用户已授权完整访问时才用 `yolo`**），并且必须注入三个环境变量；
3. 不得因该限制而伪造命令输出；被拒时如实登记原文。

**其它实测**：首次 `--version`/探测调用曾以 `exit -1073740791`（`0xC0000409`，node 崩溃）失败，
重试即成功——属瞬时故障，第二次成功结果为准；不得据此判定 ZCode 不可用。

## 派发通道实测（2026-10-16，用户纠正后）

**用户指令**：DSH 派发任务**必须**通过 DSH 原生子智能体通道 —— `subagent_codex` / `subagent_agy` / `subagent_zcode`（由 DSH 插件 `@deepseek-ai/dsh-tool-subagent`、`@deepseek-ai/dsh-subagent`、`dsh-tool-subagent-control`、`dsh-subagent-fork-in-process`、`dsh-hooks-codex` 提供）。**不要**用 PowerShell 里的原始 CLI 子进程自造派发。

实测结果：

| 通道 | 结果 | 证据 |
|---|---|---|
| `subagent_zcode` | ✅ **成功** | 逐字读回 `doc/REBASELINE_PLAN.md` 的 READY 行；自报 `SHELL=是`（可执行 shell） |
| `subagent_codex` | ❌ **连续 2 次失败** | 两次均 `Product subagent failure (product: Codex; stage: turn; category: product-error)`，**无收尾消息** → 判定为**系统性**（非瞬时），需排查 DSH 侧 Codex 后端配置 |
| `subagent_agy` | ⏳ 未实测 | 下次真实派发时验证 |
| 原始 CLI `codex exec` | ✅ 可用 | 本会话多次成功（P14 正运行于此路径） |
| 原始 CLI `node zcode.cjs --mode edit` | ❌ 拒 Bash | `No permission client configured for Bash`（通道缺陷，非 agent 缺陷） |

**纪律**：
1. 优先 DSH 原生通道；`subagent_codex` 失败时，**如实报告并改用 `subagent_agy`/`subagent_zcode`**，或（经用户同意）回退原始 CLI；
2. **不得**因某通道失败而伪造派发成功；
3. 原始 CLI 仅在 DSH 通道不可用时作回退，并在交付记录中**注明所用通道**。

### 通道故障更新（2026-10-16 23:15）

- **`subagent_codex` 连续 3 次失败**：`7a08f404`、`0bd6fcba`、`2165cd45` 均以
  `Product subagent failure (product: Codex; stage: turn; category: product-error)` 结束且**无收尾消息**
  → 判定为**系统性**（非瞬时）；**排查修复前不要再派发到该通道**。
- **处置**：按用户"经 DSH 原生通道派发"的指令改用 **`subagent_agy`** 承担 `P15-C1`；
  该选择同时保持**职责分割**（`P15` 的 UI 预期由 ZCode 承担，契约不宜由将实现它的同一 agent 起草）。
- **对照事实**：原始 CLI `codex exec` 仍可用（P14 曾跑完），但**不再作首选**（属"自造派发"）。
- `subagent_zcode` 已验证可用（含 shell）。

## 子智能体通道根因（2026-10-16 23:2x，已定案）

**`subagent_codex` / `subagent_agy` 失败与 codex/agy 本身无关，而是 DSH 侧缺适配器 bundle。**

证据链：
1. DSH 内核（app.asar）声明 `const ON_DEMAND_BUNDLES = ["@deepseek-ai/dsh-subagent-claude-code", "@deepseek-ai/dsh-subagent-codex"];`
   → codex 子智能体是**按需安装**的 bundle。
2. DSH 运行时 `~/.dsh/dsh-local/dsh/node_modules/@deepseek-ai/` 实际**只有** `dsh-subagent`、`dsh-subagent-fork-in-process`、`dsh-subagent-in-process-driver`、`dsh-subagent-spawn-in-process`、`dsh-tool-subagent`、`dsh-tool-subagent-control`；
   **`dsh-subagent-codex` 缺失**（`claude-code`/`agy`/`antigravity` 亦缺）。
3. 失败形态与缺失位置吻合：缺少适配器 → `subagent_codex` 在 **turn** 阶段 product-error；`subagent_agy` 在 **spawn/transport** 阶段失败。
4. **排除项**：日志里的 `rmcp … AuthRequired`（tldraw MCP OAuth）与 `codex_models_manager: failed to refresh available models` 在**成功的原始 CLI 运行中同样出现** → 均**非致命**（且 `codex-dispatch` 技能明记后者"无害"）。

**修复路径（需用户决定，不在 DSH 应用内擅自安装）**：在 DSH 内安装 on-demand bundle `@deepseek-ai/dsh-subagent-codex`（如 DSH 设置的 bundle 安装入口）。在此之前**不要**再派发 `subagent_codex`/`subagent_agy`。

## codex 调用方式变更（用户 2026-10-16 指示）

**今后 codex 一律按 `codex-dispatch` 技能调用**（原始 CLI，但遵循技能的参数与纪律）：

- `codex exec --skip-git-repo-check -s <read-only|workspace-write> -c windows.sandbox=unelevated -m gpt-6-luna -c model_reasoning_effort=xhigh -o <result.md> "<prompt>"`
- 结果读 `-o` 文件；**session id 从 stderr 的 `session id: <uuid>` 提取**并留档；
- 续接：`codex exec resume --skip-git-repo-check -m gpt-6-luna -c model_reasoning_effort=xhigh -c sandbox_mode="read-only" -o <r2.md> <session-id> "<prompt>"`（**resume 不接受 `-s`**，选项须在 SESSION_ID 之前，**不要用 `--last`**）。
- **cwd 约定（与编排隔离的取舍）**：技能的"会话在桌面版项目下可见"要求 cwd == 项目根；但**写任务必须跑在 worktree 内**（隔离优先）。因此：**只读任务**用项目根（可见性优先）；**写任务**用 worktree（安全优先，可见性用技能的 `mount_codex_session.py --fix-cwd` 补救，需先退出桌面版）。

## 派发有限重试条款（DIR-4，2026-10-17 用户新增）

**用户原话**："给 dsh 本身或者其他 agent 派任务时，要求他们不要失败后无限循环，在失败一定次数后，停止并分析原因，给出方案后再再次执行任务、脚本。"

### 硬性规则

| 规则 | 内容 |
|---|---|
| R1 重试上限 | 同一失败面（同一命令 / 同一脚本 / 同一断言 / 同一隔离根 / 同一 API 错误）**最多重试 2 次**；第 3 次触发**强制停止** |
| R2 停止即上报 | 停止后必须输出：① 原始错误输出（不截断关键行）② 已尝试的假设与每次结果 ③ 根因分析 ④ 修正方案（含将改变什么）⑤ 需要 Coordinator/用户决定的问题 |
| R3 禁止改脚本重跑 | **不得**用"微调脚本再跑一次"规避 R1；若方案确需改脚本，必须走 R2 上报 → 获批 → 作为**新一轮**计数 |
| R4 计数可观测 | 每次尝试必须在交付/日志中留痕（第 N 次、命令、退出码），使 Coordinator 可独立判断是否已触限 |
| R5 Coordinator 止损义务 | 观察到循环迹象（同名隔离根重复创建、agent 进程数异常增长、长时间 0 提交、无 Handoff 迹象）时，Coordinator **必须立即 `job_kill`**，并登记：通道、理由、已保留产物、恢复点 |
| R6 区分"失败"与"等待" | 长任务无输出、UI 处于"导入中"等**不**计为失败，不得据此 kill（见交接文件 §6 致命错误 4） |

### 可直接复制进派发 prompt 的文本

```text
【有限重试纪律（DIR-4，用户强制要求）】
1. 同一失败（同一命令/脚本/断言/隔离根/API 错误）最多重试 2 次；第 3 次必须停止，不得再执行。
2. 停止后立即上报，内容必须包含：
   (a) 原始错误输出（关键行不得截断）；(b) 每次尝试的命令与退出码；
   (c) 根因分析；(d) 修正方案（说明将要改变什么）；(e) 需要我裁决的问题。
3. 禁止"改脚本重跑"式规避上限；确需改脚本时，先上报方案、获批准后重新计数。
4. 首次 GUI/环境失败即停下上报，不要连续重试到耗尽时间。
5. 不得用伪造 PASS、跳过测试、注释掉断言等方式"让流程通过"。
6. 无进展则如实上报 BLOCKED，并保留全部现场产物（不删除、不清理、不 reset）。
```

### 反面案例（必须避免重演）

`FEAT-IMPORT-MULTI-1`（2026-10-17）：隔离数据根被重复创建 4 次
（`feat-import-multi-20261017` / `-r2` / `-r3` / `-r4`），GUI 脚本内含**硬 `throw`**，
每次失败即"改脚本重跑" → **25 分钟、0 提交、无 Handoff**，`codex` 进程达 6 个，
最终由 Coordinator `job_kill` 止损（只停派发脚本，worktree 与 27 份证据完整保留）。

