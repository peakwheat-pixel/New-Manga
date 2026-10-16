# P14 独立 Review（R1，Coordinator 路由的 Reviewer=dsh）

| 项 | 值 |
|---|---|
| Task | P14（工作台 Workbench，四页第三页；设计基线 §3） |
| Owner | codex |
| Reviewer | **dsh**（本会话，经 `route-agent.py` 路由，Owner 已机器排除）——**本文件才是协议意义上的独立 Review** |
| 交付 | 实现 `ac2296d59a63f4ea5c2fe8ea54c8e29b15072d5c`，HEAD `ee1d1e287`（4 提交：`e99be4d62`/`ac2296d59`/`3eee09077`/`ee1d1e287`） |
| 基线 | `536962909` |
| 复核环境 | **独立 Reviewer 工作树** `worktrees/P14-review`（detached `ee1d1e287`，零拷贝 junction）——未触碰 Owner 工作树 |
| 结论 | **approved**（含 closeout 需处理的记录项，见 §4） |

## 1. 我**亲自复跑**的结果（非引用 Owner 日志）

| 套件 | 我的实测 |
|---|---|
| `npm --prefix apps/desktop/frontend test` | **19 files / 204 tests passed**，exit 0 |
| `npm --prefix apps/desktop/frontend run build` | **✓ built in 555 ms**，exit 0 |
| `python -m pytest tests/core -q` | **407 passed** |
| Rust source（`--skip packaged_sidecar_tests`） | **95 passed / 0 failed / 1 ignored** |
| Rust packaged（frozen 2.3，`M2RC1_PACKAGED=1`） | **12 passed / 0 failed** |

## 2. 逐项独立验证

| # | 验证项 | 方法 | 结果 |
|---|---|---|---|
| V1 | 范围 | `git diff --name-only 536962909..HEAD` | **PASS**：仅 `apps/desktop/frontend/src/**` + `doc/{tasks,handoffs}` + `verification/P14/**`；**未触碰** Tauri/Rust、Core、契约、Schema、依赖 |
| V2 | **G15「Run 发现」未被发明** | 源码 + 测试检索 | **PASS**。`TaskProgressPanel.tsx` 的 `DisabledFeature` 写 `reason="暂不可用：Core 尚无 ListRuns 查询；仅能查看本次工作台明确启动的 Run。"`；测试 `keeps G15 Run discovery visible and disabled without a ListRuns command`；**没有任何 `invoke` 调用 run-listing 命令**，也无本地聚合 |
| V3 | **未交付缺口逐条禁用** | 检索 `gap-gN` | **PASS**：`gap-g9/g10/g11/g12/g13/g14/g15/g16/g18/g26` **10 项全覆盖**（= 设计 §7 的工作台缺口全集）；`DisabledFeature` 为 `<button disabled aria-describedby=…>` + **可见原因文本**；测试文件 19 行 disabled/aria/reason 断言 |
| V4 | **导出面板在本页实现 + 去路径投影** | 检索 + 测试 | **PASS**：`ExportDialog` 及 `library_cancel_export`/`library_get_export_snapshot`/`library_get_export_history`/`library_reveal_export_folder` 均在位；**生产代码零 `output_path`**；`client.test.ts` 注入 `output_path:"C:\private\out.zip"` 与 `target_ref:"private-ref"`，并**断言请求与投影后的 snapshot/history 均不匹配** `/target_ref|output_path|private/i` |
| V5 | **`m2res` 边界（裁决 A）合规** | 检索 | **PASS**：`m2res` / `resolvePageResource` 仅用于媒体显示链；`localStorage`/`sessionStorage`/`console.log`/`console.error`/`emit(` **全为 0**；唯一 `m2res`+log 行是 AC1 探针的**句子式**日志（**不含 URL/opaque id**） |
| V6 | 事件→**重查快照**（不用 payload 驱动） | 读实现 + 测试 | **PASS**：`WorkbenchPage.tsx` 订阅六类事件后走 `onRunChanged` → `getRunSnapshot`/`getTaskProjection` 重取权威快照；测试以**过期 payload**（`status:"running"`）触发 `core:RunCompleted`，证明不信任事件负载 |
| V7 | 状态词法 | 读 front matter | **PASS**：`status: in_review`（合法值）、`canonical_evidence_status: complete`——本会话前两例（P12 `review_ready`、P17 `ready_for_review`）的自造值**未复现** |
| V8 | 如实限定 | 读 Handoff | **PASS**：GUI e2e **`NOT_RUN`**（`0x80070578`），并写明"**DOM 单测不代表 e2e**"；且**主动声明"新一轮独立 Review 尚未完成、本交付仍 `in_review`、不表示已接受或集成"** |
| V9 | 证据记录 | 逐行 `Get-FileHash` + **`git cat-file -e <commit>:<path>`** | **部分通过**：**12/12 行的提交包含性成立**（BL-17 满足）；但 **3 行的 sha256 与磁盘不符**（见 §4） |

## 3. 结论：approved

按设计 §3/§7 与裁决 A 逐项合规：缺口只禁用不发明（含 G15）、导出面板在本页实现且去路径投影有测试钉死、`m2res` 仅作显示句柄且不落盘不入日志、事件只作提示并强制重查快照、范围严守前端、GUI e2e 如实声明未运行；**五套件由我独立复跑全绿**。

## 4. closeout 需处理的记录项（非实现缺陷）

1. **3 条证据 pin 陈旧**：`P14-RUST-PACKAGED-TESTS-META`、`P14-DISABLED-ENTRY-EVIDENCE`、`P14-BOUNDARY-EVIDENCE` 的登记 sha256 与磁盘不符；**我已核实磁盘字节与提交 blob 完全相等**（`相等=True`）→ 文件本身正确，仅**登记值需按磁盘复算**（与 TTL/EVENTS/REVEAL/EXPORT-IPC-1/READER-IPC-1 同类处置）。
2. **BL-15（第 6 次）**：`delivery_head: ac2296d59` 而分支 HEAD 为 `ee1d1e287` → closeout 以实际 HEAD 冻结。
3. **BL-18 冒名**：`verification/P14/dsh-review-r1-summary.md` 与 `dsh-review-r2-summary.md` 抬头写「**P14 独立 Review／Reviewer：dsh**」，实为 **Owner 自请**的 DSH 会话/子智能体审查（我已核验 session 真实存在、cwd = Owner 工作树、origin/depth 与 parentSession 均属 Owner 侧；其自述未重跑测试）。**本文件才是协议独立 Review。** 处置：集成时把两份改名为 `owner-initiated-dsh-self-review-r{1,2}.md` 并加更正抬头（内容保留为**自批判证据**，其中 R-008 即 `m2res` 边界问题的来源）。
4. `doc/tasks/P14.md` 的 `suggested_owner` 仍写"若 ZCode 无法执行 shell 则改派"——该表述已被更正（ZCode 经 DSH `subagent_zcode` 可执行命令），closeout 一并修正。
