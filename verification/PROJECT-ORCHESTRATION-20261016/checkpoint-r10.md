# Rolling Checkpoint r10 — PROJECT-ORCHESTRATION-20261016

**写入时的事实以 live Git/FS 为准；本文件是"上一稳定边界"的交接说明，不是权威状态。** 权威状态依次为：[STATUS](../../doc/STATUS.md) → [REBASELINE_PLAN](../../doc/REBASELINE_PLAN.md) → 各 Task 文件 → `git log`。上一稳定边界见 [checkpoint-r9.md](checkpoint-r9.md)（HEAD `ca53a5b08`，epoch 6 起始）。

## 1. 写入时 live 事实（2026-10-16 19:4x）

- main HEAD：`40f7833ed`；**用户 dirty = 精确 19 项**（逐条见 [RUN-IPC-1.md](../../doc/tasks/RUN-IPC-1.md) 禁用范围一节，勿触碰）。
- 治理：`pwsh -NoProfile -File tools/governance/check.ps1` → **PASS**（2 条预算 WARN：STATUS 2958B/3200、REBASELINE_PLAN 2403B/2500）。⚠️ `tools/governance/check.ps1` **未被 Git 跟踪**（BL-12），故 fresh worktree 内**无法**运行它；Reviewer 必须**如实声明**而非伪造结果。
- Coordinator：**dsh，epoch 6**，lease `9ce79020a36e4fab8970e8ae6de5fb10`（LEASE_VALID）。**DIR-3：只保留一个 Active Coordinator**（用户 17:10 裁决）；epoch 5 lease 会被拒（`STALE_COORDINATOR`）。
- 运行时日志（均 untracked，不提交）：`.orchestrator/{INFLIGHT.json(schema v2 多 op),OPLOG.ndjson,BACKLOG.md,RUNTIME_DIRECTIVES.md,agents.json,runtime.json}`。

## 2. 本边界内已完成并集成的 Task（6 个）

| Task | 终态 | 集成 | 备注 |
|---|---|---|---|
| ENV-BUNDLE-1 | closed_with_limitations | `7b9cbbe6` | bundle 重建并与协议 2.3 对齐 |
| UI-DESIGN-1 | done | `9e1221e1b` | 四页设计基线冻结（W1–W32 / 24 真缺口），I1 收敛 |
| ENV-BUNDLE-1-FU1 | closed_with_limitations | `b474c09b` | packaged 六项由 frozen bundle 驱动 6/6 |
| P12 | done | `465e3001e` | 四页 Shell + 书架 + 导入 UI |
| HOST-TTL-BOUNDARY-1 | done | `23587397e` | import+export 两侧 issuer 留 1 s 裕量、Core 守卫未动 |
| EVENTS-FWD-1 | done | `22920f8db` | §6.4 六类事件转发面（G17），生产命令面仍 18；AC4 端到端如实 `BLOCKED` |

## 3. 写入时的在飞与 READY

- **在飞**：`RUN-IPC-1` 独立 Review（antigravity，Reviewer 工作树 `worktrees/RUN-IPC-1-review`）；`EXPORT-REVEAL-1` 重新交付（codex，把新 main 并入分支并**语义级**解冲突）。
- **READY（尚无 owner）**：`EXPORT-IPC-1`、`READER-IPC-1`。
- READY 行：ARCH-DOC-REBASELINE、EXPORT-REVEAL-1、RUN-IPC-1、EXPORT-IPC-1、READER-IPC-1。

## 4. 本边界最重要的一项结论：UI 链前置完整性已封闭

见 [ui-chain-prerequisite-matrix.md](ui-chain-prerequisite-matrix.md)：**W1–W32 + G20 全部映射完毕，没有第四处"契约已冻结但 WebView 不可达"缺口**。

- 同型缺口共**三处**，均已释放：`RUN-IPC-1`（Run 控制面）、`EXPORT-IPC-1`（导出取消/进度/历史，**必须剔除 `output_path`**）、`READER-IPC-1`（阅读投影/进度保存）。
- 集成四个 Task 后生产命令面达 **30 条**（18+6+3+2+1），probe/AC1 仍冻结在 **7/6**。
- **P14 前置 = RUN-IPC-1 + EXPORT-IPC-1**；**P17 前置 = EXPORT-REVEAL-1 + READER-IPC-1**；**P15 还需 G21–G25 的契约/产品裁决**。

## 5. 必须继承的登记与教训

- **BL-12**：治理检查器未入库（待用户/Codex 决定）。
- **BL-13**：生产启动 30 s 死线 + `.expect` panic（负载下会假阴性；FU1 只把**测试**默认改为 120 s）。**生产路径仍 30 s**，取值与失败 UX 属产品取舍，待用户/Codex 裁决。
- **BL-14（3 次独立证实）**：设计 §6 只核"契约是否冻结"、未核"host 是否已有出口"（正反两个方向：G6/G19 误报已实现为缺口；W11–W16/W18–W19/W22–W24 误报未实现为可用）。**强制前置步骤**：释放任何 UI Task 前，逐条把 W 行映射到 `PRODUCTION_COMMANDS`。
- **BL-15（3 次出现）**：Handoff 自引用 `delivery_head` → 记录永久滞后于分支 HEAD。**处置**：closeout 一律 `git rev-parse HEAD` 冻结实际值；owner 不应在 Handoff 里写"即将产生的 SHA"。
- **TTL 根因（已修，供将来复用）**：把 TTL 取在验证窗口的**精确上限**＝零裕量，任何负向时钟偏差即 `REF_EXPIRED`（探针证明 **1 ms** 足够）。**新增任何 grant 类型时，issuer 侧必须留裕量**。探针：`G:/CODEX/New Manga.workspace/tmp/guarded/{ttl,export-ttl}-boundary-probe.{py,log}`。
- **同类缺陷必须全类扫描**：发现一处后立即扫同类（本会话由 EVENTS 的重复 h1 触发对 REVEAL 契约的检查；由 TTL 的 import 侧触发对 export 侧的检查）。

## 6. 环境与工具限制（不得夸大结论）

- **ZCode**：headless `--mode edit` **拒绝所有 shell 命令**（`No permission client configured for Bash`）→ 不可用于需要跑测试/提交的 Task。
- **无头 Windows**：WebView2 无法取得窗口句柄（`0x80070578`）→ **真实 GUI e2e runner 无法运行**。因此"零回归"只能基于单测/构建，**不得**表述为已 e2e 验证。
- **CRLF 幽灵**：`core.autocrlf=true` 下 cargo 运行会让 `git status` 出现大量 ` M`，但 `git diff --numstat` 对其**零行输出**（内容未变）。**判定真实改动必须用 `git diff`**；恢复时**只恢复非用户文件**。
- **fresh worktree 前置**：`target/core-sidecar` 与 `frontend/dist` 缺一即 `cargo`/`tauri::generate_context!` 失败（BL-11a）→ 用 `New-Item -ItemType Junction` **零拷贝**补齐，**不要**删除或重建。
- PowerShell：设 `$PSNativeCommandArgumentPassing='Standard'`；prompt 内含引号/撇号时用 here-string（`@'...'@`）避免解析错误。

## 7. 恢复步骤（R1–R7）

1. `cd 'G:/CODEX/New Manga'`；`git rev-parse HEAD`；核对 README/AGENTS.md 的工作区规则。
2. 读 [STATUS](../../doc/STATUS.md)（当前 Task/在飞/READY）与 [REBASELINE_PLAN](../../doc/REBASELINE_PLAN.md) 的 READY 行；读本 Task 的 Review 与 Handoff。
3. `pwsh -NoProfile -File tools/governance/check.ps1` 确认 PASS；`git status --porcelain --untracked-files=no` 必须**精确 19 项用户 dirty**。
4. 用 `coordinator-lease.py status` 检查 lease；若 epoch 落后，用 `takeover --expected-epoch <n>` 取得唯一 Active Coordinator（**DIR-3**）。
5. 检查在飞：`INFLIGHT.json` + `OPLOG.ndjson` 尾部 + 各 worktree 的 `git log/status`（**OPLOG 是唯一 append-only 时间线**）。
6. **不得** `reset --hard` / `clean` / 删除用户未提交内容 / 伪造测试或 Review 结论。
7. 继续按 `PLAN → ROLE ROUTE → PREFLIGHT → IMPLEMENT → SELFTEST → VERIFY → INDEPENDENT REVIEW → INTEGRATE → CLOSEOUT` 推进；**释放任何 UI Task 前先跑 §5 的 BL-14 前置核对**。

## 8. 待用户裁决（不得由实现者拍板）

- **P18 产品发布门槛**（JA/KO 门槛、无字页、质量 AC 对应新链）；P18 像素上限 `11184810`；KO detector 权重缺失（`PROVIDER_NOT_CONFIGURED`）。
- **BL-13** 的生产启动期限取值与失败 UX。
- **BL-12** 治理检查器是否纳入版本控制。
- **G21–G25**（P15 设置/Provider/凭据/网络/分段 schema）的契约修订授权。
