# P19 Handoff（Owner/执行者：dsh）—— 版本 R4（2026-10-18）

> 本版按 **Codex R4 独立复核**（`verification/P19/codex-review-r4.md`，`decision=changes_requested`）与后续实测重写，取代 R3 版中已被事实推翻的表述（R4 明确指出 R3 版"把导入写为未完成、AC3 写为待 P19-AC3-1"与 0047 导入实测及 `7b1fcc45a` 合并后的事实不一致）。

## 1. Task 与交付
- Task：[P19](../tasks/P19.md)；`status: closed_with_limitations`；`integration_commit` / `delivery_head` = `4c860d882a44580a955b5d090d8bc5d23180ede5`
- 验收方式：Task 记 **D+**（用户 2026-10-17 裁决），**实际执行通道为真实 WebView2 + UIA 语义**（本机构建 **CDP 不可用**：Tauri 覆盖 `WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS`）；该差异已在 R1/R4 与 Closeout Record 中持续披露
- 隔离：全部 GUI 运行使用 `%TEMP%\p19*` 全新隔离根（`NEWMANGA_DATA_ROOT`），运行前后核对用户真实 `%APPDATA%` 数据未变
- 产品状态：main 已重建并通过 **P20 发布 Gate**（frontend + frozen sidecar + cargo；`bundle==resource` = `6ab8ada366cbac79720818c4b42eb66888a44138366c50f73e55a55d83b0be5d`；smoke 窗口可达）

## 2. AC 状态（实测 + R4 复核）
| AC | 结论 | 依据 |
|---|---|---|
| AC1 验收方式 | PASS（口径已披露） | 用户裁决 D+；实际 D（WebView2+UIA），CDP 不可用已证据化 |
| AC2 四页主流程 | **PASS** | 8 轮真实 GUI；末次 `ac2-main-20261018-0128`：`checks=27 fails=0 exit_code=0`。①建作品 ②建章节 ③**多选导入 2 张**（DB `pages=2`，两页 sha256/字节数与 fixture 逐项一致）④**Run**（经章节行「翻译」入口，`启动 enabled=True`）⑤**导出**（选页后 `导出选择页 enabled=True`）⑥**阅读器翻页**（控制状态反转 + DB total=2） |
| AC3 安全边界 | PARTIAL | 全域扫描由 `P19-AC3-1` 交付（58 命令 × 4 面 + WebView 边界）；**设置路径回显已由 `SEC-FIX-PATH-ECHO-1` 修复**（本 Task 期间在含修复的 main 上重跑复现：`path:[redacted]`、`REPRO_RESULT=PASS`）；剩余为框架/设计限制（见 §4） |
| AC4 未开放能力不可操作 | PASS（含判据遗留） | 9 个分区 `en=False` + `invoke` 不可用（原始数据）；`disabled-not-invokable` 判据脆弱已列为遗留 |
| AC5 可复现与证据 | PASS | 每个 runner 逐步产出 UIA 转储 + 截图 + `trace.log` + `run-metadata.txt`（含 exe sha256/时间戳/退出码） |
| AC6 交付与关闭材料 | PASS | 24 条规范证据表（完整 40 位 commit + 磁盘字节 sha256）；Closeout Record 已填；Resource Manifest 含 22 旧根 + **12 个本轮新根** |

## 3. R3 findings 的最终处置
| ID | 级别 | 最终状态 |
|---|---|---|
| R3-001 | P1 | **CLOSED**：AC2 主流程实跑通过（末次 27/27）|
| R3-002 | P1 | **CLOSED**：`P19-AC3-1` 已并入 main `7b1fcc45a`；其扫描发现的路径回显已由 SEC-FIX 修复 |
| R3-003 | P1 | **CLOSED**：`codex-review-r1.md` 此前未跟踪 → 已入库（`2117933b0`）；证据表改为 governance 认可的 6 列格式并补全新证据 |
| R3-004 | P2 | **CLOSED**：新 runner 每步留原始产物（8 轮 AC2 + 3 轮 AC4）|
| R3-005 | P2 | **CLOSED（脚本层）**：v3 具全新目录 + 拒绝覆盖（exit 4）+ 断言失败非零；`PAGE_CHANGED` 判据改进未重跑（遗留） |
| R3-006 | P2 | **OPEN（Codex 治理项）**：`FEAT-CREATE-1/2` 等纯记账缺失，回填留待治理窗口 |

## 4. 已知限制与风险（P2，不阻断收口）
1. **产品刷新缺陷**：从侧栏直达工作台时 `WorkbenchPage.listBooks()` 不同步 → 列表显示"暂无作品"、`启动`/`导出选择页` 恒禁用。经章节行「翻译」入口的主流程不受影响（R4 独立确认）。
2. **框架/设计限制**：Tauri 2.12 不校验顶层未知键（58/58 命令的"请求面"）；错误面仅送 `error.code`（不校验闭集）。
3. **runner 判据遗留**：AC4 `PAGE_CHANGED` 依赖 Pane 名集合比较（UIA 刷新瞬时为空致误判）→ 已改为 `en`/`invoke` 判定，但未按其重跑。
4. **执行者自述失误（留痕）**：入口选错误报缺陷、导入中杀进程、对 Explorer 选择器误用 UIA；AC2 8 轮迭代中前 7 轮的失败**全部由 DB 与 UIA 转储证明确为 runner 缺陷**。
5. **测试基线**：Core **536** · 前端 **285/28 文件** · Rust source **108/0/1**（须设 `M2RC1_PYTHON`）· packaged **12/0/0**。

## 5. 下一步
1. **用户裁决**：`DOC`（ARCH-DOC-REBASELINE）的 AC7 逐消费者 Gate 裁决 → 释放 **P20**（其发布 Gate 已实测通过）。
2. **Codex 治理窗口**：R3-006 记账回填；`%TEMP%\p19*` 隔离根清理（34 个，`CLEANUP_AFTER_CLOSEOUT`）。
3. **可选**：将 §4.1 的侧栏刷新缺陷另立 P2 Task（用户裁决前不动）。
