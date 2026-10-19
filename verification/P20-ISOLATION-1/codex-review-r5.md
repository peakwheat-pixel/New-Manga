---
task_id: P20-ISOLATION-1
reviewer: Codex
author: Antigravity
base_commit: dbeca3babfb8689da113b5ef263501bcdf6ece61
reviewed_head: 078a593582d0f31c87a3813237d857ac96127203
decision: changes_requested
---

# P20-ISOLATION-1 独立复审 R5

## 1. 结论

**decision = `changes_requested`。** R4 的交付头已对齐到 `e8cc6d1e4`，R010 断言计数已更正为 15，`library_bridge.rs` pin 的行尾来源已追溯；本轮也在当前代码上补齐了冷启动、四页可达和 bundle/resource hash 的重测证据。仍不能批准：Task 的 AC4 从创建时就包含内存不得恶化的要求，本轮同一父子进程链口径测得 467.35 MB，高于其既有的 443.3 MB 基线 24.05 MB（5.4%）。

本 Review 绑定 `dbeca3babfb8689da113b5ef263501bcdf6ece61..078a593582d0f31c87a3813237d857ac96127203`。产品交付 `delivery_head` 仍是 `e8cc6d1e4`；`078a593` 包含随后产生的 AC4 重测和四页 smoke 证据。审查依据为本 Task、R1–R4、`pre-r4-audit.md`、AC4 重测及其 NFR/smoke 原始记录、P20/P20-MEM-OPT-1 AC 与 r27/r28 pin 裁定。本轮未运行产品测试或修改实现。

## 2. R4 返修复核

| R4 项 | R5 结论 | 依据 |
|---|---|---|
| `delivery_head` 对齐 | **完成** | Task 与 Handoff 均指向 `e8cc6d1e4`。该字段是交付元数据，不改写历史证据 pin。 |
| `library_bridge.rs` pin 追溯 | **来源已追溯；原值保留** | `f2bae7687bbc…` 匹配 commit `1dc0df7304a9` 的 CRLF 变体；当前工作区是 LF，故不匹配旧 pin。 |
| AC4 当前代码重测 | **三项通过，内存子项未通过** | `ac4-rerun-20261020.md` 及 `verification/P20/nfr-20261020-r4/`、`verification/P20/smoke-20261020-r4/`。被测 EXE SHA 为 `be593a88…`。 |
| R010 断言数 | **完成** | Task 记录 15 条 `ASSERT PASS`、`script_fails=0`，与 trace 相符。 |

## 3. AC4 裁定与五项问题

### 3.1 AC4 是否 MET

**AC4 未 MET。** 不能只按“正文三项回归均通过”判 PASS，因为 Task 的原始 AC4 明文还要求“`P20-MEM-OPT-1` 的内存目标亦不得因此恶化”。该要求不是后续追加：Task 初始提交 `9b6488604` 的 AC4 已包含内存不恶化条款；后续提交把三项回归结果写入 AC 原句，并以“以下为原说明”标出保留的原始要求。该标注解释了文字结构，不能删除原 AC 的验收效力。

本次证据分别支持：冷启动 0.841 s ≤ 2.0 s、四页 smoke `checks=5 fails=0`、四份 `core_service.exe` SHA 均为 `cd8dcc5e…`，三项 PASS；父子链内存为 467.35 MB，对比 443.3 MB 基线增加 24.05 MB / 5.4%，内存不恶化 FAIL。名字通配得到的 1149.75 MB 混入其他应用，本 Review 不以该值判定；父子链 467.35 MB 已按 AC 口径复核记录，足以判定回归。

### 3.2 绝对门槛与相对不回归

“不得恶化于一个从未达标的数字”在当前有效门槛下不成立。443.3 MB 当初高于旧 350 MB 门槛，但用户随后将 P20 AC3 的绝对上限调整为 480 MB；443.3 MB 低于现行 480 MB，且 P20 当前记录将内存列为 PASS。因此，443.3 MB 是已接受的历史实测基线，不是现行门槛下的失败值。

这两种验收条件应分别解释：

- **绝对门槛**：P20 AC3 的当前上限是 ≤480 MB；本次 467.35 MB 满足。
- **相对不回归**：本 Task AC4 要求内存表现不因隔离改动恶化；按其引用的 443.3 MB 基线，本次增加 5.4%，未满足。

两者不应混成“是否超过 350 MB”。如果后续用户决定 AC4 只保留绝对门槛，应在授权的 Task 修订中明确写成 ≤480 MB，并明确撤销相对不回归条件；本 Review 不替用户改写 AC。

### 3.3 AC4 未通过时的状态、集成及 P20 AC6

- Task 维持 `in_review` / `changes_requested`，不能转 `done`。`closed_with_limitations` 也不适用：当前 AC 仍有一项未满足，且尚无用户对该限制的关闭裁决。
- `integration_commit` 维持 `null`。本 Task 直接在主线交付不等于已通过 Review、集成验证和 closeout。
- Plan 中本 Task 保持 `in_review`，done 计数保持 42，不增加到 43。
- **P20 AC6 的产品行为验收可判达成**：R010 修正后的真实桌面注入证明草稿在强杀、重生和恢复后仍在并可提交，且隔离库记录得到核验；原 AC6 的主窗口存活、提示、自愈也有运行证据。此判断只针对 P20 AC6，不代表 P20 其他 AC 或本 Task closeout 已完成。

### 3.4 可执行的 AC4 收口路径

当前 AC4 缺少的具体条件是：按父子进程链和可比的稳态采样方法，将内存结果证明为不高于已接受的 443.3 MB 基线；若达不到，则需要用户明确裁决修订/豁免 AC4 的相对条件。性能优化是独立产品工作，本 Task 的返修不应无限期承担优化实现：可另立有授权的内存优化 Task；本 Task 在此期间保持 `changes_requested`，或由用户裁决是否以限制关闭。不能由 Reviewer 擅自拆除 AC4 子项、把它改成新 Task，或将未满足 AC 标成 PASS。

### 3.5 `library_bridge.rs` pin 与 checker FAIL

**保留旧 pin 与当前 checker FAIL；不追加一条声称可以消除旧 FAIL 的 superseding pin。** r27/r28 要求历史 basis 不明的 pin 保留原值、维持现行 checker 行为，不能按 CRLF/LF 关系重算或放宽通过条件。已追溯到 CRLF 候选来源可作为诊断事实，但不能证明旧 pin 当时的 basis，也不能覆盖原行。

单独新增当前文件的 pin 不会让现有旧 pin 自动停止被检查；在没有获授权的 supersession 语义/checker 迁移时，它不能解决报错，反而可能造成误称“FAIL 已清”。因此本轮不改 pin，也不把该 FAIL 判成数据损坏；登记为 **legacy-unresolved 的已知治理限制，FAIL 保持可见**。未来若消费者确需当前源码证明，应在另行授权的记录中追加明确标识取代关系的新证据，保留旧行和原值，并按 r28 为新 pin 声明 basis；旧 FAIL 的处理仍需独立授权。

## 4. Architecture 与 Verification

| 视角 | 判断 | 证据与限制 |
|---|---|---|
| Architecture | **无新增架构阻断** | 本轮审查的返修是交付元数据、计数和运行证据；没有基于它们推断共享契约或 Schema 已变更。实现代码的既有结论见 R4，本轮未重审产品代码 diff。 |
| Verification | **AC4 不通过，Review 不批准** | 冷启动、四页和 hash 相等通过；按父子链采样的内存相对基线增加 5.4%。R010 真实桌面注入及 AC4 原始重测证据按既有记录核验，未在本轮重跑。 |
| Governance pin | **已知限制，维持 FAIL** | 旧 pin 命中历史 CRLF 变体但不匹配当前 LF 文件；依 r27/r28 保留 pin 与 checker 既有判定，不伪报 PASS。 |

## 5. Findings

| ID | 级别 | 文件/位置 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R-017 | P1 | Task AC4；`ac4-rerun-20261020.md` | AC4 含内存不得恶化条件；当前父子链值 467.35 MB，高于 443.3 MB 基线。故三项功能回归通过仍不足以将 AC4 判为 MET。 | EXE SHA `be593a88…`；NFR 链口径 11 个进程共 467.35 MB；对比 `P20-MEM-OPT-1` 的 443.3 MB。 | 同口径把值降至 ≤443.3 MB，或由用户明确裁决修订/豁免相对不回归条款；不得只按 480 MB 绝对上限将本 AC 判 PASS。 | **open** |
| R-018 | P2 | Task Canonical Evidence：`EVID-P20-ISOL-SRC` | 当前 checker 因旧 SHA 与工作区 LF 字节不一致而 FAIL。历史 CRLF 候选不能自动改变 pin basis；新 pin 也不能在当前语义下消除旧行错误。 | Task 的 R4 返修记录；r27/r28 pin basis 裁定。 | 保留旧值与 FAIL，登记为 legacy-unresolved 已知限制；若未来需要迁移，另行授权并保留 supersession 来源链。 | **已裁定保留；FAIL 仍在** |

## 6. 验证记录

| 场景 | 方法 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| AC4 冷启动 | 核对三轮原始记录及均值 | Windows 桌面；被测 EXE SHA `be593a88…` | PASS：0.841 s ≤ 2.0 s | `verification/P20-ISOLATION-1/ac4-rerun-20261020.md`、`verification/P20/nfr-20261020-r4/` |
| 四页可达 | 核对 smoke trace 与截图 | 同上 | PASS：`checks=5 fails=0` | `verification/P20/smoke-20261020-r4/` |
| `bundle==resource` | 核对四份副本 SHA | 同上 | PASS：均为 `cd8dcc5e…` | `ac4-rerun-20261020.md` |
| 内存不恶化 | 核对父子链逐进程测量及基线 | 父子链 11 进程；同口径 | **FAIL**：467.35 MB vs 443.3 MB，+5.4% | `verification/P20/nfr-20261020-r4/chain-memory.json`；`doc/tasks/P20-MEM-OPT-1.md` |
| AC3 草稿保全 | 核对真实注入 trace、截图及 Task 所记隔离库查询；本轮未重跑 | `r010-20261018-0944` | PASS（既存证据） | `verification/P20-ISOLATION-1/` 对应 R010 运行目录；Task AC3 |
| pin 追溯 | 核对 R4 记录与 r27/r28 裁定；本轮未运行 checker | `e16f538f…` pin；历史候选 `1dc0df7304a9` | FAIL 保留为 legacy-unresolved 限制 | Task「R4 返修记录」；`verification/P09-GOVERNANCE-DEBT-20261019/codex-adjudicate-pin-basis-r27.md`、`codex-adjudicate-pin-basis-contract-r28.md` |
| 新测试 / 治理 checker | 未执行 | 只读 Review | NOT_RUN | 用户本轮限定只写 Review 文件；本结论不冒充新运行结果 |

## 7. Task 状态与下一步

保持 Task `in_review` / `changes_requested`，Plan 行不变、done=42、`integration_commit: null`。下一步由 Codex/用户确定 AC4 相对内存条件：授权单独的内存工作并按同口径复测，或明确裁决修订/豁免 AC4 后再复审。只有用户明确允许按限制关闭时，才考虑 `closed_with_limitations`；关闭记录须保留 AC4 内存子项未通过及 R-017 原始状态，不得将其改写为 PASS。当前无需向其他 Agent 派发实现任务，直到该产品取舍/范围得到授权。
