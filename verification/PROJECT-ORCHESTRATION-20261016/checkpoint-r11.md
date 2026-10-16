# Rolling Checkpoint r11 — PROJECT-ORCHESTRATION-20261016

**写入时的事实以 live Git/FS 为准；本文件是"上一稳定边界"的交接说明，不是权威状态。** 权威状态依次为：[STATUS](../../doc/STATUS.md) → [REBASELINE_PLAN](../../doc/REBASELINE_PLAN.md) → 各 Task 文件 → `git log`。上一稳定边界：[checkpoint-r10.md](checkpoint-r10.md)；用户重启暂停点与恢复处置：[pause-checkpoint-20261016.md](pause-checkpoint-20261016.md)（**已恢复**）。

## 1. 写入时 live 事实

- main HEAD：`536962909`；**用户 dirty = 精确 19 项**（逐条见任一 Task 的禁用范围一节，**不得触碰**）。
- 治理：`pwsh -NoProfile -File tools/governance/check.ps1` → **PASS**（2 条预算 WARN：STATUS 3173B/3200、REBASELINE_PLAN 2469B/2500）。
  ⚠️ 两文件均接近上限，**下次实质性更新前必须压缩**，否则治理会 FAIL（本会话已两次触顶并修复）。
  ⚠️ `tools/governance/check.ps1` **未被 Git 跟踪**（BL-12），fresh worktree 内**无法运行**；Reviewer 必须如实声明而非伪造。
- Coordinator：**dsh，epoch 6**，lease `9ce79020a36e4fab8970e8ae6de5fb10`。**DIR-3：只允许一个 Active Coordinator**。
- **目标状态**：goal `goal-ab494681-8aab-4a5c-bac1-d5b813532474` 为 **`phase: paused`**（用户重启时暂停；模型**无权 resume**，需用户在界面重新启用才会自动续轮）。本轮为自动续轮的 **40/40 上限**。

## 2. 已完成并集成（10 个）

| Task | 集成 | 关键结论 |
|---|---|---|
| ENV-BUNDLE-1 | `7b9cbbe6` | bundle 与协议 2.3 对齐（closed_with_limitations） |
| UI-DESIGN-1 | `9e1221e1b` | 四页设计基线冻结（W1–W32 / 24 真缺口），I1 收敛 |
| ENV-BUNDLE-1-FU1 | `b474c09b` | packaged 六项由 frozen bundle 驱动 6/6 |
| P12 | `465e3001e` | 四页 Shell + 书架 + 导入 UI |
| HOST-TTL-BOUNDARY-1 | `23587397e` | import+export 两侧 issuer 留 1 s 裕量、Core 守卫未动 |
| EVENTS-FWD-1 | `22920f8db` | §6.4 六类事件转发面（G17） |
| RUN-IPC-1 | `c3929bcc3` | Run 六命令 host 接线（P14 前置） |
| EXPORT-REVEAL-1 | `c9b113f96` | 按不透明 `export_id` 打开导出目录（G20） |
| EXPORT-IPC-1 | `aaca5d1ea` | 导出取消/进度/历史 + **白名单去路径投影**（P14 前置） |
| READER-IPC-1 | `ab47ef2b0` | 阅读投影/进度保存（P17 前置） |

## 3. 已释放并在飞（两个 UI 实现 Task）

| Task | Owner | 分支 / 工作树 | 起点 | Reviewer | 预检 |
|---|---|---|---|---|---|
| **P14 工作台**（设计 §3） | codex（job `pwsh-72`） | `codex/P14` / `worktrees/P14` | `536962909` | dsh | PASS |
| **P17 阅读器**（设计 §4） | antigravity（job `pwsh-73`） | `agent/antigravity/P17` / `worktrees/P17` | `536962909` | dsh | PASS |

两者写入时**尚无提交**（刚启动，正在读设计基线）。**若被中断**：不要丢弃其未提交内容；按 `pause-checkpoint-20261016.md` §2 的恢复处置续派同一 Owner 或先保全为证据。

**复核重点（已预置）**：
- **P14**：**G15「Run 发现」必须仍为禁用**（对已知 `run_id` 的 W14/W15 可用，但列表需要 Core **没有的** `ListRuns` → 禁止发明命令/本地聚合）；禁用清单须与设计 §7 **逐条对应**；**路径零泄露**；只做前端。
- **P17**：**§6.3 红线**（引用不透明、缺失译图 **null**、`beginning` 不改进度、独立进度键、`elapsed_seconds_delta` 缺失不重发、Webtoon 逻辑页像素坐标）；**必须未实现导出面板**（归 P14）。
- 两者共同：事件后**必须重查快照**；**如实声明 GUI e2e 未运行**（无头 WebView2 `0x80070578`）；`npm test` + `npm run build` 归档。

## 4. 页面归属裁决（已冻结，勿再推翻）

[ui-chain-prerequisite-matrix.md](ui-chain-prerequisite-matrix.md)：DAG 名 P17="阅读导出UI"，但设计 §6 **页面列**为权威 →

- **P14** = 设计 **§3**，含**导出面板 W21–W25** 与 **G20 reveal 入口**；
- **P17** = 设计 **§4**，含 W18/W19/W20（消费既有 W2/W3/W5），**明确排除导出面板与 G20**。

**P14/P17 的全部前置已 done**；**UI 链无第四处"契约已冻结但 WebView 不可达"缺口**（三处同型缺口已由 RUN/EXPORT/READER-IPC-1 关闭）。

## 5. 必须继承的登记与教训

- **BL-12**：治理检查器未入库（待用户/Codex 决定）。
- **BL-13**：生产启动 30 s 死线 + `.expect` panic（**生产路径仍 30 s**），属产品取舍。
- **BL-14（3 次证实）**：设计 §6 只核契约冻结、未核 host 出口 → **释放任何 UI Task 前必做"W 行 → `PRODUCTION_COMMANDS`"映射**。
- **BL-15（5 次出现）**：`delivery_head` 自引用滞后 → **closeout 一律 `git rev-parse HEAD` 冻结**；owner 不应自引用"即将产生的 SHA"。
- **BL-16**：冲突解析后**必须在全树扫描三种标记**（`<<<<<<<`/`=======`/`>>>>>>>`）再提交；**证据 pin 按磁盘字节**算（`autocrlf` 会改写行尾）。
- **BL-17**：owner 记录的 commit 必须**原样粘贴** `git rev-parse HEAD`；**`git rev-parse <40hex>` 对不存在的对象会原样回显而不报错**，**只有 `git cat-file -e <sha>:<path>` 能发现**"编号存在但对象不存在"（EXPORT-IPC-1 实测踩中）。
- **TTL 根因**：TTL 取在验证窗口**精确上限**＝零裕量，任何负向时钟偏差即 `REF_EXPIRED`（探针证明 **1 ms** 足够）→ 新增任何 grant 类型必须在 issuer 侧留裕量。
- **同类缺陷全类扫描**：发现一处立刻扫同类（本会话由 EVENTS 的重复 h1 触发对 REVEAL 契约的检查；由 TTL import 侧触发 export 侧）。
- **多方合并方法论（本会话新增，重要）**：叠加式冲突可用"删标记=并集"，但**会留下重复的计数注释与断言** → 必须按**合并后真实值**统一；**生成文件（`gen/schemas/**`）不要手工合并**，改为构建重新生成后核验；若删标记导致**花括号失衡**，改**确定性重建**（取 main 已验证版本 + 该分支的**纯新增**行）；每次合并后**必须重跑全套**（本会话四次合并均如此）。

## 6. 环境与工具限制（不得夸大结论）

- **ZCode：能否执行命令取决于派发通道**（2026-10-16 更正）。经 **DSH 原生 `subagent_zcode`** 派发时**可执行 shell**（实测逐字读回 READY 行并自报 `SHELL=是`）；只有"原始 CLI headless + `--mode edit`"这条路会因缺 permission client 而拒绝全部 Bash（`No permission client for Bash`）。**故 ZCode 是有效 Owner（含需跑测试/提交的 Task）**。**派发纪律**：优先用 `subagent_codex`/`subagent_agy`/`subagent_zcode`，不要用原始 CLI 子进程自造派发。
- **无头 Windows 无法取得 WebView2 窗口句柄（`0x80070578`）** → **真实 GUI e2e 不可运行**；"零回归"只能基于单测/构建，**不得**表述为已 e2e 验证。
- `core.autocrlf=true` → `git status` 会出现**幽灵 ` M`**，而 `git diff --numstat` 对其零行输出；**判定真实改动必须用 `git diff`**，恢复只针对**非用户**文件。
- fresh worktree 需 `target/core-sidecar` 与 `frontend/dist` 的**零拷贝 junction**（BL-11a），**不要删除或重建**。
- PowerShell：`$PSNativeCommandArgumentPassing='Standard'`；prompt 含引号/撇号时用 here-string。

## 7. 恢复步骤（R1–R7）

1. `cd 'G:/CODEX/New Manga'`；`git rev-parse HEAD`；`git status --porcelain --untracked-files=no` 应**精确 19 项**。
2. 读 [STATUS](../../doc/STATUS.md) 与 [REBASELINE_PLAN](../../doc/REBASELINE_PLAN.md) 的 READY 行；读本文件与 §3 的两个工作树状态。
3. `pwsh -NoProfile -File tools/governance/check.ps1` → 期望 PASS（若预算告警触顶先压缩 STATUS/PLAN）。
4. `coordinator-lease.py status` 检查 lease；epoch 落后则 `takeover --expected-epoch <n>`（**DIR-3**）。
5. 检查在飞：`INFLIGHT.json` + `OPLOG.ndjson` 尾部 + 各 worktree 的 `git log/status`（**OPLOG 是唯一 append-only 时间线**）。
6. **不得** `reset --hard` / `git clean` / 删除未知用户改动 / 伪造测试或 Review 结论。
7. 继续 `PLAN → ROLE ROUTE → PREFLIGHT → IMPLEMENT → SELFTEST → VERIFY → INDEPENDENT REVIEW → INTEGRATE → CLOSEOUT`；**释放任何 UI Task 前先跑 BL-14 前置核对**。

## 8. 下一步（给后继会话）

1. **回收 P14 / P17 交付** → 各走 **dsh 独立 Review**（重点见 §3）→ 集成（预期与彼此无冲突：分别只改前端）→ closeout。
2. 两页关闭后，**P19（四页安全 E2E）** 成为下一个 READY 候选（其依赖 P12/P14/P15/P17/P18/P04，其中 P15 设置页仍需 **G21–G25 的契约/产品裁决**）。
3. **ARCH-DOC-REBASELINE 的 AC7** 需 P17/P20 完成后由 **Codex** 做逐消费者裁决（Coordinator 不越权代裁）。
4. **P20（Windows 发布）** 依赖 P19。

## 9. 待用户裁决（不得由实现者拍板）

P18 产品发布门槛（JA/KO 门槛、无字页、质量 AC）；P18 像素上限 `11184810`；KO detector 权重缺失（`PROVIDER_NOT_CONFIGURED`）；**BL-13** 生产启动期限与失败 UX；**BL-12** 治理检查器是否入库；**G21–G25**（P15 前置）的契约修订授权；以及**是否重新启用目标**以继续自动推进。

## 10. r11 补登（2026-10-16 23:30，P15-C1 在飞时）

- **已完成 12 个 Task**：新增 **P17 阅读器**（集成 `f18b7fe8f`，closeout `67a7665db`）与 **P14 工作台**（集成 `2dc14cdd1`，closeout `590582004`）→ **四页 UI 已全部实现**（书架 P12 / 工作台 P14 / 阅读器 P17 / 设置待 P15）。READY 现为 **ARCH-DOC-REBASELINE + P15-C1**。
- **BL-18（新增）**：Owner 自请的 DSH 审查被写成"独立 Review"。P14 交付内 `dsh-review-r{1,2}-summary.md` 抬头自称「独立 Review／Reviewer：dsh」，经查 session **真实存在**但 **cwd 为 Owner 自己的工作树**、`origin=subagent`/`parentSession=f5a0166d`（即 Owner 自请），且自述未重跑测试 → **非伪造，但非协议独立 Review**。处置：**git mv** 为 `owner-initiated-dsh-self-review-r{1,2}.md` + **更正抬头**，内容保留为自批判证据；**规则**：`verification/<TASK>/*review*` 只能由 Coordinator 路由的 Reviewer 写入；Owner 自请须命名 `owner-self-review-*` 并声明非独立；集成时必须核验出具者与 session 归属。P14 的**真正独立 Review** 为 `verification/P14/dsh-review-r1.md`（我在 detached `ee1d1e287` 的独立 Reviewer 工作树亲跑五套件）。
- **G21–G25 裁决**（`verification/PROJECT-ORCHESTRATION-20261016/ruling-G21-G25.md`）：**G21–G24 授权**由新契约 Task **`P15-C1`** 合并冻结（P10 已冻结逻辑边界、缺 IPC wire）；**G25 部分授权**（仅"已有 Core 校验实例或语义已确立"的节，其余**禁用 + 逐节后续契约 Task**）；**G2 回收站本轮不授权、P15 必须禁用**；"v1 开放哪些分区"属**产品取舍**，以**默认提案**处理以免阻塞。
- **DSH 子智能体通道根因（定案）**：内核声明 `ON_DEMAND_BUNDLES = ["@deepseek-ai/dsh-subagent-claude-code","@deepseek-ai/dsh-subagent-codex"]`，而运行时 `~/.dsh/dsh-local/dsh/node_modules/@deepseek-ai/` **缺 `dsh-subagent-codex`**（agy/claude-code 适配器亦缺）→ `subagent_codex`（turn 阶段）与 `subagent_agy`（spawn/transport）失败。**排除**：`rmcp AuthRequired`（tldraw MCP）与 `models_manager refresh timeout` 在**成功的原始 CLI 运行中同样出现**，均非致命（技能亦明记后者无害）。
- **codex 调用方式（用户指示）**：一律按 **`codex-dispatch` 技能**经 CLI 派发（`-m gpt-6-luna -c model_reasoning_effort=xhigh -o <result.md>`；session id 取自 stderr；`resume` 用 `-c sandbox_mode` 而非 `-s`、不用 `--last`）。**cwd 取舍**：只读任务用项目根（桌面可见性），**写任务用 worktree**（隔离优先），可见性用 `mount_codex_session.py --fix-cwd` 补救。
- **目标已恢复自动推进**：goal revision 8、`phase: active`、`activation: armed`、上限由 40 提至 **100**；目标文本刷新为 epoch 6 与当前焦点（P15-C1 → P15 → P19/P20）。
- **待用户裁决**（不阻塞其余推进）：G25 未列分区、P18 门槛、**P19 的 GUI e2e 验收替代方案**（本机无头无法取得 WebView2 句柄 `0x80070578`）、BL-12/BL-13。
