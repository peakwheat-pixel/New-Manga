# Rolling Checkpoint r12 — PROJECT-ORCHESTRATION-20261016

**写入时事实以 live Git/FS 为准；本文件是"上一稳定边界"的交接说明，不是权威状态。** 权威顺序：[STATUS](../../doc/STATUS.md) → [REBASELINE_PLAN](../../doc/REBASELINE_PLAN.md) → 各 Task → `git log`。前序：[checkpoint-r11.md](checkpoint-r11.md)（含 §10 补登）；用户重启暂停点与恢复处置：[pause-checkpoint-20261016.md](pause-checkpoint-20261016.md)（**已恢复**）。

## 1. live 事实

- main HEAD：`141c4ae3a`；**用户 dirty = 精确 19 项**（逐条见任一 Task 的禁用范围；**不得触碰**）。
- 治理：`pwsh -NoProfile -File tools/governance/check.ps1` → **PASS**（WARN：STATUS 3004B/3200、REBASELINE_PLAN 2472B/2500）。⚠️ 两文件接近上限，**下次实质更新前先压缩**；写入时**务必验证行数**（STATUS 22 行、PLAN 35 行）。
- Coordinator：**dsh，epoch 6**，lease `9ce79020a36e4fab8970e8ae6de5fb10`。**DIR-3：只允许一个 Active Coordinator**。
- **目标**：goal `goal-ab494681-8aab-4a5c-bac1-d5b813532474` → `phase: active` / `activation: armed`，上限 **100**（revision 8；用户明确要求恢复自动推进后由我 edit+resume）。

## 2. 已完成并集成（**13 个**）

ENV-BUNDLE-1 `7b9cbbe6`、ENV-BUNDLE-1-FU1 `b474c09b`、UI-DESIGN-1 `9e1221e1b`、P12 `465e3001e`、HOST-TTL-BOUNDARY-1 `23587397e`、EVENTS-FWD-1 `22920f8db`、RUN-IPC-1 `c3929bcc3`、EXPORT-REVEAL-1 `c9b113f96`、EXPORT-IPC-1 `aaca5d1ea`、READER-IPC-1 `ab47ef2b0`、P17 `f18b7fe8f`、P14 `2dc14cdd1`、**P15-C1 `f07221313`**（设置面契约：G21–G24 + 受限 G25）。

**四页 UI**：书架（P12）、工作台（P14）、阅读器（P17）**已 done**；**设置页 P15 在飞**。

## 3. 在飞：P15 设置页（Owner=ZCode）

| 项 | 值 |
|---|---|
| 通道 | **`subagent_zcode`（DSH 原生）**——本会话**首次成功的 DSH 原生派发** |
| 工作树 | `worktrees/P15`，分支 `zcode/P15`，基点 `22f0024cc`（含 `target/core-sidecar`、`frontend/dist`、`frontend/node_modules` 三个零拷贝 junction） |
| Reviewer | dsh（`route-agent.py` 路由，独立） |
| 硬边界 | **只开放契约 §7 清单内 4 个面**；**其余 11 分区（含 G2）禁用 + 原因**；禁止发明键域/新增 wire/改 Rust·Core·契约；**Secret/路径四处零暴露**；错误只用契约 §9 封闭投影 |

**复核重点（已预置）**：只开放清单内分区；禁用清单与设计 §5.4/§7 逐条对应；**Secret 不入普通 settings DTO** 的反例测试；状态矩阵五态与"保存失败保留用户输入"；**如实声明 GUI e2e 未运行**。

## 4. 已预写（待释放）

- **P15**：已 `ready` 并在飞（AC2 已内嵌契约的可编辑分区清单）。
- **P19 四页安全 E2E**（[doc/tasks/P19.md](../../doc/tasks/P19.md)，`proposed`，96 行）：**AC1 是硬门**——**验收方式待用户裁决**（A 分层验收+真机手工清单／B 真实 WebView2 环境／C jsdom 替代并明示不覆盖 IPC/ACL）；**未获裁决前不得开工**。释放条件：**P15 关闭 + AC1 裁决**。

## 5. 派发通道现状（**重要**）

| 通道 | 状态 |
|---|---|
| `subagent_zcode` | ✅ **可用**（含 shell）；**P15 正运行于此** |
| `subagent_codex` | ❌ **系统性失败**（连续 3 次 `product-error`/`stage: turn`）→ **根因：DSH 运行时缺 on-demand bundle `@deepseek-ai/dsh-subagent-codex`**（内核声明其为 on-demand，但 `~/.dsh/dsh-local/dsh/node_modules/@deepseek-ai/` 中不存在；agy/claude-code 适配器亦缺）。**修复需用户在 DSH 内安装该 bundle** |
| `subagent_agy` | ❌ `stage: spawn; category: transport`（同因：缺适配器） |
| 原始 CLI codex | ✅ 可用——**按 `codex-dispatch` 技能**调用（`-m gpt-6-luna -c model_reasoning_effort=xhigh -o <result.md>`；session id 取自 stderr；`resume` 用 `-c sandbox_mode=...` 而非 `-s`、不用 `--last`） |
| 排除的红鲱鱼 | `rmcp AuthRequired`（tldraw MCP）与 `models_manager refresh timeout` 在**成功运行**中同样出现 → **非致命** |

## 6. 必须继承的登记与教训

- **BL-11a**：fresh worktree 需 `target/core-sidecar`、`frontend/dist`、**`frontend/node_modules`** 零拷贝 junction；**不要删除或重建**（P14 Review 因缺第三个而 `npm` 跑不起来）。
- **BL-12**：治理检查器**未入库** → worktree 内不可运行。
- **BL-13**：生产启动 30 s 死线（测试已参数化 120 s；**生产仍 30 s**）。
- **BL-14（3 次证实）**：释放任何 UI Task 前必做 **W 行 → 生产命令映射**。
- **BL-15（6 次）**：`delivery_head` 自引用滞后 → closeout 一律以 `git rev-parse HEAD` 冻结。
- **BL-16**：冲突解析后**全树扫三种标记**；证据 pin 按**磁盘字节**复算。
- **BL-17**：owner 记录的 commit 必须**原样** `git rev-parse HEAD`；**`git rev-parse <40hex>` 不校验存在性**，**只有 `git cat-file -e <sha>:<path>` 能发现**编造尾部（EXPORT-IPC-1 实测踩中）。
- **BL-18**：`verification/<TASK>/*review*` **只能**由 Coordinator 路由的 Reviewer 写入；Owner 自请审查须命名 `owner-self-review-*` 并声明非独立。
- **BL-19**：**检查器只校验 STATUS"当前 Task"的证据表**（L136/L172–183），L158–163 只遍历 READY 节点查 `status: ready` → **`PASS` 不等于证据合规**；且证据 `class` **只允许 `CANONICAL`/`SOURCE_PIN`**（本会话已把 7 个 Task 的非 `REVIEW` 类修正）。
- **工具陷阱（本会话新增）**：`Set-Content -NoNewline` 传**数组**会把各行**拼接为单行**（STATUS/PLAN 曾因此塌陷为 1 行，治理捕获）；**写后必须验证行数**。
- **TTL 根因**：零裕量 → 新 grant 类型必须在 issuer 侧留裕量。
- **多方合并方法论**：删标记=并集**仅对纯叠加成立**且会留**重复计数**须按真实值统一；**生成文件重新生成**；**花括号失衡时确定性重建**（main 已验证版本 + 分支纯新增）；**每次合并后重跑全套**。

## 7. 环境限制（不得夸大）

- **无头 Windows 无法取得 WebView2 窗口句柄（`0x80070578`）** → **真实 GUI e2e 不可运行**；所有 UI Task 只能如实声明 `NOT_RUN`。**P19 的验收方式待用户裁决**。
- `core.autocrlf=true` → 幽灵 ` M`；判定真实改动用 `git diff`，只恢复**非用户**文件。
- PowerShell：`$PSNativeCommandArgumentPassing='Standard'`；含引号/撇号的 prompt 用 here-string；`verification/P04/diagnostic_*.jsonl` **不得入库**。

## 8. 恢复步骤（R1–R7）

1. `cd 'G:/CODEX/New Manga'`；`git rev-parse HEAD`；`git status --porcelain --untracked-files=no` 应**精确 19 项**。
2. 读 [STATUS](../../doc/STATUS.md) / [REBASELINE_PLAN](../../doc/REBASELINE_PLAN.md) 的 READY 行 → 本文件 → §3 的 P15 工作树状态。
3. `pwsh -NoProfile -File tools/governance/check.ps1` → 期望 PASS；若预算告警触顶**先压缩**。
4. `coordinator-lease.py status`；epoch 落后则 `takeover --expected-epoch <n>`（**DIR-3**）。
5. 查在飞：`.orchestrator/{INFLIGHT.json,OPLOG.ndjson}` + 各 worktree 的 `git log/status`（**OPLOG 是唯一 append-only 时间线**）。
6. **不得** `reset --hard` / `git clean` / 删除未知用户改动 / 伪造测试或 Review 结论。
7. 继续 `PLAN → ROLE ROUTE → PREFLIGHT → IMPLEMENT → SELFTEST → VERIFY → INDEPENDENT REVIEW → INTEGRATE → CLOSEOUT`；**释放前先跑 BL-14 前置核对**。

## 9. 下一步

1. **回收 P15 交付** → dsh 独立 Review（重点见 §3）→ 集成 → closeout → **四页全部完成**。
2. 之后 **P19** 成为下一候选（**须先取用户对 AC1 验收方式的裁决**）。
3. **ARCH-DOC-REBASELINE 的 AC7** 需 P17/P20 完成后由 **Codex** 逐消费者裁决。

## 10. 待用户裁决（不阻塞其余推进）

**G25 未列分区**是否在 v1 开放；**P18 产品发布门槛**；**P19 的 GUI e2e 验收方式**（能力层阻塞）；**BL-12**（检查器是否入库）、**BL-13**（生产 30 s 死线）；以及是否在 DSH 内安装 `@deepseek-ai/dsh-subagent-codex` 以恢复受管派发。

## 11. r12 补登（2026-10-17 00:29，P15-CORE-1 在飞时）

- **里程碑：四页 UI 全部完成**。P15 设置页 done（集成 `c78ded304`，closeout `ca070e0ba`）→ **书架 P12 / 工作台 P14 / 阅读器 P17 / 设置 P15 全部交付**；累计 **14 个 Task done**。
- **P15-C1 设置面契约**（`f07221313`）与 **P15 UI** 均已关闭；P15 的证据诚实性为**范例级**（保留未过滤首跑失败日志并如实命名说明其为 `M2RC1_PACKAGED=1` 环境门卫，非回归）。
- **RV-P15-04（BL-16 类第 7 次）**：证据 pin 若以 **LF 工作树字节**计算而提交为 **CRLF**，则**不可从 fresh checkout/主仓库验证** → **closeout 必须在主仓库按规范字节复算**。P15 的 7 条 pin 已在主仓库复算通过。
- **BL-20**：Task 允许范围必须**显式覆盖测试支持目录**（P17 `tests/core/**`、P15 `frontend/src/testSupport/**` 两次先例）。
- **新 DAG 节点**：`P15-HOST-1`（host 侧注册）与 **`P15-CORE-1`（Core 侧实现）**——**派发前置核对**实测发现 **Core 完全缺失** P15-C1 冻结的 17 条命令（9 条抽查 0 命中），故按 "Core Task → host 配对" 拆分。**READY = ARCH-DOC-REBASELINE、P15-CORE-1**；`P15-HOST-1` = `proposed`，依赖 P15-CORE-1。
- **在飞**：`P15-CORE-1`（Owner=Codex，经 **`/codex-dispatch` 技能经 CLI** 派发，`danger-full-access`；reviewer=dsh 独立；基线 pytest **407 passed** 已由双方独立确认）。
- **S1 主题**：**UI 完成 ≠ 端到端可用**——设置页 4 个开放面已由契约冻结但 host/Core 未实现，当前落入 §9 `SETTINGS_UNAVAILABLE`；`P15-CORE-1`+`P15-HOST-1` 即是补链。
- **待用户裁决（完整清单见 [decision-request-20261016.md](decision-request-20261016.md)）**：G25 扩大、P18 门槛、**P19 验收方式**（无头无 WebView2）、BL-12/13，以及 **P15 三项确认**（阅读方向挂载 / G25 扩大 / Network 测试面保留——建议均按默认）。
- **轮次提示**：目标 `active`/`armed`，上限 100；本会话在轮次上限附近，**若在 P15-CORE-1 交付前耗尽轮次**，恢复步骤见本文件 §8，`INFLIGHT.json` 与 `OPLOG.ndjson` 记录了该 job（`pwsh-117`）与 worktree 位置。

## 12. r12 补登（2026-10-17 06:55，P15-CORE-1A 在飞时）

- **用户裁决 A1**（2026-10-17）：`TestNetworkProfile` 的 `provider_profile_id` **改为必需**（目标恒为 Provider endpoint；缺省/非法 → `INVALID_REQUEST`）；A2 未采纳（留档）。
- **P15-CORE-1 因真实契约缺口失败关闭并被拆分**：Owner（Codex）在实现前发现"无目标却只能报 `passed`"的假阳性路径，**拒绝**自选公网/loopback/假目标与伪造阶段结果，引契约 §5.2/L194/L212 上报 → **裁决成立**。拆为 **1A**（G21+G24）、**1B**（G22+G23 不含 test）、**1C**（六阶段 test）。
- **P15-C1-FU1 已 done**（`94197afc9` / closeout `648361486`）：契约 rev **2.7**，删除假阳性路径、固化四项禁止、补全 **5 模式 × 6 阶段**判定表、兼容性如实论证（minor 6→7 为未发布前窄范围修订）。**pin 可移植性**：未改动文件主仓库一致；被改契约按 **RV-P15-04** 在主仓库复算 ✓。合并后 pytest **407**（确认契约改动未触及代码）。
- **当前 READY = ARCH-DOC-REBASELINE、P15-CORE-1A、P15-CORE-1B、P15-CORE-1C**；**在飞 1A**（job `pwsh-161`，worktree `worktrees/P15-CORE-1A`，分支 `codex/P15-CORE-1A`，基点 `b1f4d08c7`，Reviewer=dsh）。
- **写范围互斥纪律**：1A/1B/1C 三者**都改** `core_service.py` + `core_assembly.py` → **必须串行派发**（1A → 1B → 1C），**不得并行**（否则必然冲突且两处独立语义互相污染）。FU1（仅契约）与 1A（仅 Core）互斥 → 曾并行 ✓。
- **目标**：用户已将上限设为 **1000**（`active`/`armed`，revision 12），且 objective 文本已刷新为真实焦点。
- **BL-21（新）**：派发前置核对必须做**契约语义完备性**核对（不只命令存在性），并要求 Owner 以**契约行号**支撑"缺语义"主张。
