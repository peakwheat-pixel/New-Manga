# UI-DESIGN-1 独立 Review（R1，rev 2）

| 项 | 值 |
|---|---|
| Task | UI-DESIGN-1（AD-001 四页 UI/UX 设计基线） |
| Owner | zcode |
| Reviewer | dsh（epoch 6；独立于 Owner，未参与设计写作） |
| 交付 commit | `aaf00e59e`（内容）→ `c59d20554`（证据 pin 回填） |
| 集成 commit | `a24001f9f`（**先于本 Review 完成**；见 §6 流程偏差披露） |
| 基线 | `c6f975d38842487c16491eea67a01cf134c337f8` |
| 结论 | **changes_requested（I1，1 项）** —— 交付质量高，但 §7 缺口分类存在**载重性事实错误**，会误导 DAG 释放决策 |

## 1. I1（必须返修，bounded）

**finding**：§7 把 **G6（导入来源选择）** 与 **G19（导出目标选择）** 登记为"wire 缺口、需 host 侧 Task 作为 P12/P17 前置"。
**事实**：这两项的用户可触发面**已由 HOST-ISSUER-1 实现并注册为 production-only Tauri command**。证据（当前 main `9a7754404`，均为只读核验）：

| 证据 | 位置 | 内容 |
|---|---|---|
| E-a | `apps/desktop/src-tauri/src/main.rs:409–436` | `library_import_file`：原生文件选择器（过滤 png/jpg/jpeg/webp/gif/bmp/pdf）→ `into_path` → `import_from_path` → 返回 `ImportSummary`；取消返回 `cancelled` |
| E-b | `apps/desktop/src-tauri/src/main.rs:438–458` | `library_import_folder`：原生目录选择器 → 同上 |
| E-c | `apps/desktop/src-tauri/src/main.rs:460–…` | `library_start_export`：`validate_export_request` → 原生 save 对话框 → 内部持有 `ExportTargetRef` → 启动导出；取消返回 `None` |
| E-d | `apps/desktop/src-tauri/src/main.rs:144`、`1421` | `HOST_ISSUER_PRODUCTION_ONLY_COMMANDS` 恰好含这三个命令，且 `assert_eq!(len, 3)` |
| E-e | `apps/desktop/src-tauri/src/main.rs:78–81`、`1146` | 三命令在 `PRODUCTION_COMMANDS` 中，注释："HOST-ISSUER-1: user actions use native pickers; refs and paths stay in Rust." |
| E-f | 全库检索 `open_folder|reveal|show_in_folder|open_path` | **不存在**"打开所在文件夹"命令 → **G20 是真缺口，设计判断正确** |

**为什么是载重错误**：§7 的"建议后续动作"会直接变成 Coordinator 的释放决策。若不纠正，就会为**已经完成的工作**释放一个 host 侧契约/实现 Task（项目明令禁止的 anti-thrash / 重复劳动）。本 Reviewer 在按 §7 释放下一 Task 前核对了实现，才避免了这次重复释放。

**内部不一致（同一错误的自证）**：§6 表注（文档 L374）已经正确地把 `issue_resource_url` / `revoke_ref` 当作"**既有实现事实**，非契约文本引用对象"来处理；而同一文档却把同等性质的三个 picker 命令排除在外。说明这不是范围选择，而是**遗漏了对已实现 host 命令面的检索**。

**返修要求（bounded，仅限本 Task 允许范围）**：
1. §7：把 G6 / G19 从"缺口"改为"**已由 HOST-ISSUER-1 实现**"，逐条附上 E-a…E-e 的 `文件:行` 证据，并说明其与 §5.7 HostControl 的关系——`HostControl` 仍不得由 WebView 调用（该约束不变），但产品级选择器命令已提供，**WebView 全程不接触原始路径**。
2. §6：为三个既有命令补绑定行（与资源通道行同性质：标注为"既有实现事实"），或在 §6 表注中集中登记，二者择一并保持自洽。
3. 保留 G20 为真缺口并注明缺什么（无"打开导出所在文件夹"命令；§10.3 要求的独立 host command）。
4. 复核 §7 其余条目是否还有同类"以契约文本存在性代替实现存在性"的判断（尤其 G16：文档已正确标注 `core_ping` 为"M2 探针实现事实、非契约冻结面"，此为其正确先例）。
5. 同步更新 §附 AC 对照表与 `verification/UI-DESIGN-1/selfcheck-output.txt`（canonical 复跑由 Reviewer 再次执行）。

**不做**：不得改动任何产品代码，不得新增 wire，不得借返修扩产品范围。

## 2. 已独立验证且成立的部分（不因 I1 撤销）

| 验证项 | 方法 | 结果 |
|---|---|---|
| V1 canonical 自检复跑（Owner 被 harness 拒绝，明确委托 Reviewer） | `pwsh -NoProfile -ExecutionPolicy Bypass -File verification/UI-DESIGN-1/selfcheck.ps1` | **exit 0，`RESULT: ALL CHECKS PASS`**（W=29 / G=26） |
| V2 契约引用语义核验 | 逐行读取被引契约行比对 | W1→L139 `ListBooks`（含 `page_count int\|null`）、W2/W3→L159/L160、W4→L143 `ImportPages` **2.2 FROZEN**、W17→L556–559 四事件、W26/W27→L236–248、W28→L721 —— **全部准确** |
| V3 缺口诚实性（抽查） | 核验声明 | G26 `ImportProgressChanged` 确为 `UNKNOWN/PROPOSAL`（M2-C1 §6.2，rev 2.2）→ 准确；G6 的**理由**（§5.7 禁止 WebView 调 HostControl）准确，但**结论**（因此缺选择面）不成立 |
| V4 范围与主仓保护 | worktree/main `git status` | worktree 改动全部在允许范围；主仓 `4dcd5a949`、**19 项 dirty 与用户清单逐项一致**，无 EXTERNAL_CHANGE |
| V5 结构完整性 | 552 行；§0–§10 + AC 附表 | 齐备 |
| V6 权威纪律 | §0 五层分级 | 清晰；LEGACY 一律标注"历史参考、非绑定"，未单独作为依据 |

**逐 AC 判定**：AC1 PASS；AC2 PASS；AC3 PASS（引用的契约行准确）；**AC4 部分 PASS —— 见 I1**；AC5 PASS；AC6 PASS；AC7 PASS；AC8 PASS（由 Reviewer 关闭）；AC9 PASS（由 Coordinator 补足，见 §5）。

## 3. 已接受的信息性记录（非返修项）

- **N1（派发通道，重要教训）**：ZCode 以本机 `--mode edit` headless 派发时，harness 权限层**拒绝全部 shell 命令**（`No permission client configured for Bash`），含 `powershell`、`git add`、`certutil` 与复合命令。后果：Owner 无法自跑自检、无法提交。Owner **未伪造任何输出**，处理正确（如实登记 + 等价白名单 bash 证据 + 委托复跑）。**建议**：写入 `.orchestrator/RUNTIME_DIRECTIVES.md`——需要执行命令或提交的 ZCode Task，要么改用允许命令的模式，要么在 Task 内把"自检复跑/提交"显式指派给 Owner 之外执行者。
- **N2**：Owner 等价运行日志保留为 `selfcheck-output-owner-equivalent.txt`（SOURCE_PIN），与 canonical 日志并存，不互相覆盖。
- **N3**：§6 行号相对基线 commit，契约修订后会漂移；机器核验以名字逐字检索为准（文档已自述）。

## 4. 本设计最有价值的正确输出：DAG 影响（已按 I1 修正）

| 缺口 | 阻塞 | 修正后结论 |
|---|---|---|
| ~~G6 / G19~~ | ~~P12 / P17~~ | **不再是缺口**：`library_import_file` / `library_import_folder` / `library_start_export` 已实现 → **P12/P17 不因选择面受阻** |
| **G20** | P17（导出后打开目录） | 真缺口：需 host 侧"打开所在文件夹"命令（按不透明 export_id） |
| **G17** | P14（工作台） | 真缺口：host→WebView 事件转发面未在任何契约冻结 |
| **G15** | 中断恢复 + NavBadge | 真缺口：无 `ListRuns`/活动 Run 查询 wire |
| **G21–G25** | P15（设置维护） | 真缺口：Provider Profile / 凭据交换 / Network Profile / 范围解析 / 分区 schema |

→ 结论：P12 的前置已被 HOST-ISSUER-1 满足，**P12 可以在 UI 实现侧释放**（设计冻结后）；P17 仍差 G20；P14 差 G17；P15 差 G21–G25。

## 5. 流程偏差披露（如实记录）

1. **集成早于 Review 完成**：Coordinator 在完成 V1–V6 后即把分支并入 main（`a24001f9f`），随后才在"释放下一 Task 前的 preflight 核对"中发现 I1。正确顺序应为 REVIEW 完成后再 INTEGRATE。**处置**：不 revert（避免破坏性操作）；I1 返修在分支上进行并二次集成；本次偏差与教训记录于此，供后续 Task 引以为戒。
2. **提交者 ≠ 作者**：`aaf00e59e` 由 Coordinator 按 Owner 预制命令**逐字重放**产生（Owner 的 `git add` 被拒），**内容未改**；此处明确区分作者（zcode）与提交者（dsh）。

## 6. 收敛计划

`I1 返修（Owner=zcode，bounded，仅文档） → Reviewer 复跑 canonical selfcheck + 复核 I1 五项 → I2（仅当返修未收敛时，上限 1 次） → 集成 → closeout`。
