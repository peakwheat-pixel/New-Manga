# STATUS 形状与权威来源裁定（r15）

日期：2026-10-20（Asia/Shanghai）  
裁定人：Codex / Lead、Architect、Integrator  
范围：裁定 STATUS 与 REBASELINE_PLAN 的状态归属、STATUS 体量约束、两个 proposed Task 的登记位置及是否另立设计债 Task。本轮只新增本文件；不改 `doc/**`、`tools/**`、`src/**`、`tests/**` 或其他既有证据，不执行 Git 写命令，不调用 `coordinator-lease.py`。

## 1. 事实核对

- 当前 `doc/STATUS.md` 为 3187 UTF-8 bytes / 27 行，预算为 3200 bytes / 45 行；权威指针节的 DAG 行再次逐项列出 READY、BLOCKED、proposed、in_review 和终态节点。
- `doc/REBASELINE_PLAN.md` 自述为唯一 DAG；协作协议 §4 明确 Plan 是 DAG/READY 权威，STATUS 是唯一 Active Task 与运行状态权威。
- STATUS 已另有“当前 Task”和“Gate 与保留项”节，记录 P20 当前运行状态及 Gate；权威指针节另列本轮证据与恢复点。
- `GOV-EVIDENCE-UNIQUE-1` 与 `MANAGED-READ-ROOT-TRUST-1` 已在 Plan 标为 proposed；两者当前不需要在 STATUS 再登记状态。前者 Task 文件仍标 `proposed`，并明确尚未释放。
- `GOV-UNTRACKED-BACKLOG-1` Task 文件标为 `proposed`，但本次读取的 Plan 中没有该节点；STATUS 现有 DAG 摘要行也没有它。此差异不通过 STATUS 摘要补写来掩盖，登记应由 Codex 在获准的 Plan 生命周期更新中处理。

## 2. 裁定：选择 A，节点状态不在 STATUS 重复

Plan 是项目 DAG、节点关系和 READY/其他计划状态的唯一来源。STATUS 不应复制 Plan 的节点状态列表；否则每次节点变化都要求双写，并制造不一致窗口。STATUS 保留对 Plan 的指针，集中记录当前唯一 Active Task、运行状态、Gate、当前证据与恢复点。运维需要完整节点清单时，沿指针读取 Plan。

### `## 当前权威指针` 完整替换文本

```markdown
## 当前权威指针

- DAG 与节点状态：[REBASELINE_PLAN](REBASELINE_PLAN.md)（唯一权威）。
- 当前 Active Task 与运行状态：见本文件「当前 Task」；Gate 与保留项：见本文件「Gate 与保留项」。
- 本轮证据：P09 [R3](../verification/P09-AC3-DELETE-1/codex-review-r3.md) + [T2](../verification/P09-AC3-DELETE-1/t2-fullsuite-triage.md)；P20 [CB-R4](../verification/P20-CLOSE-BOUND-HARDEN-1/codex-review-r4.md) + [FPS-R4](../verification/P20-AC4-FPS-1/codex-review-r4.md)。
- 恢复点：[checkpoint-r12](../verification/PROJECT-ORCHESTRATION-20261016/)；日志 `.orchestrator/{INFLIGHT,OPLOG}`。
```

该文本满足当前权威指针的用途：DAG 指向唯一来源；运行状态和 Gate 指向 STATUS 内各自专节；当前证据和恢复点保持可定位。它不另造第二份任务状态索引。替换是建议文本，本轮没有写入 STATUS。

## 3. STATUS 预算与结构约束

保留现有硬上限 3200 UTF-8 bytes / 45 行，不因本次腾出空间而下调到 3000，也不把预算取消。上限是防止运行文档膨胀的机械护栏，不是要求占满的目标。对 STATUS 增加结构规则：只保留当前运行必需信息；DAG 状态不复制；新增内容应归入既有职责节，只有新的运行职责才新增节。字节/行数上限继续兜底，结构规则决定内容边界。裁定不要求再建立另一套复杂的逐节行数配额。

## 4. Proposed Task 在 STATUS 的登记规则

`MANAGED-READ-ROOT-TRUST-1` 与 `GOV-EVIDENCE-UNIQUE-1` 的状态由 Plan 记录即可，STATUS 无须列出 ID 或 proposed 状态。Task 文件仍是各自范围、验收与生命周期事实来源；Plan 是其 DAG 状态权威。它们尚为 proposed，不是 Active Task。

`GOV-UNTRACKED-BACKLOG-1` 同样不应只为补充 STATUS 摘要而写入 STATUS。当前 Plan 缺少该节点，因此按协作协议 §4 的 proposed 释放条件，它尚未完成 DAG 登记；Codex 应在之后获准的生命周期写入中核实依赖和冻结字段，将节点登记到 Plan，并仅在满足释放条件后把 Task 状态改为 ready。STATUS 只在它成为唯一 Active Task 或成为必须呈现的运行状态时更新相应运行信息，不维护所有 proposed 节点名册。本轮授权仅限本裁定文件，不执行上述生命周期更新。

因此，“只在 Plan 和 STATUS 出现”的两个 proposed Task 应从 STATUS 的重复状态清单中移除，但保留 Plan 记录；新 Task 以同一规则处理，先补 Plan 权威登记，不以 STATUS 代替 Plan。

## 5. 是否另立设计债 Task

不另立 Task。此次是按现有协作协议纠正 STATUS 的重复索引，属于一次文档编辑；结构原则已由 Plan/STATUS 的现有权威分工给出，不需要新增治理机制或扩展产品范围。获得相应文档写入授权后，按第 2 节替换该节并核对预算即可。若未来发现协作协议与治理检查器彼此要求 STATUS 复制 DAG 状态，再依据该新证据立窄 Task 处理契约冲突；目前没有此事实。

## 6. Git 状态对比

写入前，本轮实测 `git status --porcelain --untracked-files=all` 为 **1592 条目**，LF 连接文本 SHA-256：`1e64a0a86b26947ba824ae9f584d04664f647677621a9d1aac29d6f8fa1036af`。该结果与 r14 的写前快照一致。唯一目标文件写入前不存在。

写入后应保持原有 1592 条目，并新增本文件一条 `??`，共 **1593 条目**；核验时将目标条目从写后状态剔除，剩余文本 SHA-256 应与写前相同。没有运行任何 Git 写命令；所有既有 dirty/untracked 状态均属原作者并保留。