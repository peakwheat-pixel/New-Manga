# P19 R3 收口清单（R3-001…R3-006 逐项 → 证据 → 状态）

- 生成：2026-10-18（Asia/Shanghai），Coordinator dsh（epoch 7）
- 来源判定：`verification/P19/codex-review-r3.md`（Codex，非作者）
- 用途：R4 逐项复核的对照表；**未闭合项一律不得据文字叙述判 PASS**（R3-003 教训）

| R3 ID | 级别 | R3 要求 | 本轮处置 | 证据 | 状态 |
|---|---|---|---|---|---|
| R3-001 | P1 | AC2 四页主流程真实验收（导入→Run→导出→翻页） | **已闭合**：8 次迭代（每次失败面不同，根因全部由 DB/UIA 转储证明为 runner 缺陷而非产品缺陷）→ 末次 `checks=27 fails=0 exit_code=0`。关键突破依 Codex R4 的路径判定（见 `codex-review-r4.md` §2）：**从章节行「翻译」入口进入工作台**（侧栏直达会使 `WorkbenchPage.listBooks()` 保持陈旧），Run 前置 `hasChapter`、导出前置 `selectedPageCount>0`（须先在页列表选页）。 | `verification/P19/ac2-main-20261018-0128/**`（UIA 转储 + 12 张截图 + trace + `run-metadata.txt`）；前序 `-0044/-0047/-0051/-0110/-0116/-0120/-0124`；隔离根 DB 直查：`books=1 chapters=1 pages=2`，两页 sha256/字节数与 fixture 逐项一致 | **CLOSED（真实 GUI，独立复核待 R5 覆盖）** |
| R3-002 | P1 | AC3 全域请求/返回/事件/错误扫描 + WebView 边界证明 | 已由 `P19-AC3-1` 交付（58 命令 × 4 面 + WebView 边界）；分支已合并入 main `7b1fcc45a` | `verification/P19-AC3-1/command-matrix.md/.csv`、`webview-boundary.md/.json`、`raw/**` | **CLOSED（已集成，独立审查待 R4 覆盖）** |
| R3-003 | P1 | Handoff、evidence pins、commit、resource manifest、closeout 与 Plan 指针一致闭环 | ① Resource Manifest 事实修正（旧记录 `worktrees/P19` **不存在**）→ 已提交 `a0dba4519`；② 隔离根盘点入账（22 个 `%TEMP%\p19*`，CLEANUP_AFTER_CLOSEOUT）；③ 本条为**收口清单**；④ Closeout Record + Canonical Evidence 待 AC2 跑完后填 | `doc/tasks/P19.md`（Resource Manifest 段）、本文件 | **PARTIAL** |
| R3-004 | P2 | AC2/AC4 新实测缺**原始轨迹/UIA 转储/截图/时间戳/退出码** | **已闭合**：旧缺口坐实（`ac2-run2..12` 仅 app 日志；`d-run*` 无截图）。新 runner 每步产出 UIA 转储 + 截图 + `trace.log` + `run-metadata.txt`（含 `exe_sha256`/时间戳/`checks`/`fails`/`exit_code`）。AC2 8 轮 + AC4 v3 3 轮全部按此归档并已入库（`2117933b0`）。R4 复核确认"新三轮已满足 R3-004 归档完整性"。 | `verification/P19/ac2-main-*/**`、`d-run-20261018-005{3,5,6}/**`、三个 runner 脚本 | **CLOSED** |
| R3-005 | P2 | 复跑用**全新输出目录/拒绝覆盖**，关键断言失败**退出非零** | v2 缺陷已确认（默认覆盖 `d-run-v2`；断言失败仍 exit 0）。**不改 v2**（保持其已 pin 的 sha256 有效），新增 `run-d-acceptance-v3.ps1`：默认时间戳目录 + 拒绝覆盖（exit 4）+ 断言计数（失败 exit 1）+ 运行元数据（新增截图，R3-004） | `run-d-acceptance-v3.ps1`（自测：语法 0 错、拒绝覆盖 exit 4） | **CLOSED（脚本层）** |
| R3-006 | P2 | FEAT-CREATE-1/2 标 done 但 delivery head 缺失、canonical evidence `pending` | 已核实为**纯记账缺失**：`FEAT-CREATE-1/2`、`FEAT-CREATE-3/4`、`P19-BOOT-1`、`P19-UI-FIX-1` 的 `integration_commit` **全部验证为 main 祖先**，证据目录均在主仓 → **P19-AC3-1 的漏合并是孤例**。回填由 Codex 在治理窗口执行 | 本轮 `git merge-base --is-ancestor` 批量核验 | **OPEN（记 Codex 治理项）** |

## 交叉发现（本轮新增，须并入 R4 审查）

1. **stale sidecar 机制已查明**：`apps/desktop/src-tauri/target/core-sidecar` 是 **Junction**，worktree 与主仓共享。因此"sidecar 已更新"≠"产品已更新"：`target/debug/resources/core-sidecar/core_service.exe` 与 `m2rc1-desktop.exe` 必须一并重建。
   - 证据（本轮实测）：main bundle `94c45710`→（Owner 构建后）`e8f68222`，而 main resource 仍为 `00419440`、exe 仍为 21:03:36 → **bundle≠resource**。
   - 故 **AC2 之前必须执行 `rebuild-and-verify.ps1`**（其 Gate 一即为 `bundle==resource SHA256`）。
2. **AC2 的前置上下文**：工作台 `启动`/`导出选择页` 在无"选中作品/章节"时恒 `IsEnabled=False`（`d-run-v2` 转储实证）；`ac2-plan-r1.md` 第 3 步亦要求"选择作品与章节"。`run-ac2-mainflow-v1.ps1` 已加入 `BOOK_SELECTED` 步骤。
3. **导入对话框确认**：UIA **不暴露**"完成"按钮 → 必须发 `{ENTER}`；type-ahead 无效 → 必须 `SelectionItemPattern.Select()`/`AddToSelection()`。`gui-run-20` 已实证 `Ctrl+A` 全选 2 项成功，其唯一失败点即"找完成按钮"。
4. **Rust source 基线更替**：107 → **108**（FEAT-IMPORT-MULTI-1 新增 1 个测试）；packaged 12/0（`109 filtered out`）。后续 R4 与 P20 应以 **108** 为基线口径。
5. **【R3-003 具体缺陷，本轮新发现】Canonical Evidence 中存在"未纳入版本控制"的条目**：
   - `verification/P19/codex-review-r1.md` 位列 Canonical Evidence 表，`commit` 列为**空**，且 `git log -- <path>` 返回空、`git ls-files --error-unmatch` 判定 **tracked=False** → 该证据**从未提交**，因而不构成可验证的 Canonical Evidence。
   - 同目录此前还有 **33 个未跟踪文件**（含 `ac2-run2..12/**`、`d-run/**`、以及本轮新增的 `run-ac2-mainflow-v1.ps1`、`run-d-acceptance-v3.ps1`、`rebuild-and-verify.ps1`、`gen-evidence-pins.ps1`、`r3-closure-checklist.md`）。
   - **收口动作**：把该纳入的证据 `git add` 并提交，使证据表每一行都指向版本控制内的对象；`commit` 列填该文件**实际进入版本控制的 commit**。
   - ⚠️ **例外（硬约束）**：`verification/P19/codex-review-r2.md` 是**用户未提交（dirty）**文件，**不得** add/commit/改写；其 pin 继续按当前磁盘字节记录并在收口说明中标注该归属。

