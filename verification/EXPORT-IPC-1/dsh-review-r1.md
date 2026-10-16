# EXPORT-IPC-1 独立 Review（R1）

| 项 | 值 |
|---|---|
| Task | EXPORT-IPC-1（Tauri host 接线导出控制/查询面 + 去路径投影；P14 最后一块前置） |
| Owner | antigravity |
| Reviewer | dsh（epoch 6；独立于 Owner，`route-agent.py` 机器排除 Owner） |
| 交付 | 实现 `a4c8f9ac05fd20bd1a97a0b22a290d515fe5c475`（feat）；HEAD `fee223e36`（其后为 docs 提交） |
| 基线 | `cb07e9981` |
| 结论 | **approved**（含 1 项**阻断级证据记录缺陷**，已由 Coordinator 在 closeout 机械更正并显式记录，见 §3） |

## 1. 独立验证且成立的部分

| # | 验证项 | 方法 | 结果 |
|---|---|---|---|
| V1 | 范围 | `git diff --name-only cb07e9981..HEAD` | 契约、`build.rs`、`capabilities`、`gen/schemas/**`、3 个新权限定义 `library_{cancel_export,get_export_snapshot,get_export_history}.toml`、`src/{library_bridge,main}.rs`、`packaged_sidecar_tests.rs`、Task/Handoff/verification —— **全在允许范围**；worktree clean |
| V2 | 契约先冻结（AC1） | 读 §5.8 | **PASS**。新增「**白名单安全投影（Zero Path Exposure）**」：三命令名 + 参数已冻结；投影形状 `ExportProgressSnapshotView` / `ExportHistoryEntryView` 显式给出，其中 `output` **只保留 `{format, sha256}`**、**`output_path` 被刻意排除**；明文"必须**白名单显式重建**（禁止删字段回退）"，并引用 §5 行 164 与 §10.3 L853 |
| V3 | **路径零泄露（AC3，本 Task 核心）** | 读实现 + 测试 | **PASS**。三个白名单重建函数 `project_export_{lineage,snapshot,history}`；`test_project_export_snapshot_whitelist_zero_path` 与 `test_project_export_history_whitelist_zero_path` 注入含 `C:\...\secret\exported.zip` / `D:\Private\...` 的 Core 响应并**断言序列化结果不含 `output_path`**；另有断言投影**不含 `target_ref`**（`assert!(projected.get("target_ref").is_none())`、`assert!(!serialized.contains("target_ref"))`） |
| V4 | 错误净化 | 读 Tauri command 层 | **PASS**。命令层用 `map_err(\|error\| error.code)`，**剥离 Core/系统原始 message** → 错误响应不可能夹带路径 |
| V5 | **`ExportTargetRef` 单次消费语义未被破坏** | 全文件搜 `StartExport` / `ExportTargetRef` | **PASS**。唯一的 `StartExport` 调用是既有的 HOST-ISSUER-1 `start_export_to_path`（L1171-1172）；本组三条命令**既不调用 `StartExport`、也不读写 `ExportTargetRef`**；Handoff 亦明确确认 |
| V6 | 拒绝面 | 读 `packaged_sidecar_tests.rs` | **PASS**。`GetExportSnapshot`/`CancelExport` 对未知 `export_id` 均断言**域级 `EXPORT_NOT_FOUND`**（非 `PROTOCOL_MALFORMED`）；**空历史返回 `{"exports": []}` 而非错误**（`test_project_export_history_empty_cases`） |
| V7 | 四处同步 | 读 diff | **PASS**。`PRODUCTION_COMMANDS` / `generate_handler!` / `build.rs` app-manifest（计数注释 31→34 / 24→27）/ `capabilities` + tauri-build 自动生成权限定义**同一提交** `a4c8f9ac0`；probe=7 / AC1=6 冻结形状不变 |
| V8 | 证据真实性与 pin | **逐个重算磁盘 sha256** | **PASS**。4 条 Canonical Evidence 的 sha256 **全部与磁盘匹配**；归档日志真实：source **88 passed / 0 failed / 1 ignored**、frozen packaged **11 passed / 0 failed**、Core pytest **405 passed** |
| V9 | 如实限定未被夸大 | 读 Handoff「风险与遗留」 | **PASS**。明确写出：**未在 frozen bundle 上执行一次成功导出**（需真实 book/chapter 夹具）、**GUI e2e 未运行**（无头无法取得 WebView2 窗口句柄）、并确认单次写授权完好 |

## 2. 结论：approved

契约先行冻结 + 白名单重建投影 + 测试钉死"零路径/零 target_ref"、拒绝面与空态，且**完全未触碰** `ExportTargetRef` 的注册/消费路径，故 §10.3 单次写授权语义保持。三套件全绿（88/0/1、11/0、405）。**实质质量达标。**

## 3. 阻断级证据记录缺陷（已由 Coordinator 在 closeout 机械更正）

**finding（severity: blocking，但属"记录字段"而非实现缺陷）**：Task 与 Handoff 记录的完整提交 SHA **`a4c8f9ac0cfae60e51532f8ebf9ef1d02c892b15` 不存在**。

- 实测：`git cat-file -t a4c8f9ac0cfae60e51532f8ebf9ef1d02c892b15` → **`fatal: could not get object info`**；
- 真实提交：**`a4c8f9ac05fd20bd1a97a0b22a290d515fe5c475`**（前 8 位相同，**后 32 位为错误值**）；
- 影响面：Task 的 **4 条 Canonical Evidence 行**（commit 列）+ 两处 front matter（`delivery_head`）+ Handoff 的 6 处引用 —— **12+ 处**；
- 后果：治理检查器的 `commit 包含所 pin 文件` 校验会在 closeout **对 4 条证据行全部报错**；且该引用无法用于复现/回退。

**为何判为可更正的记录缺陷而非实现返修**：底层产物与 pin 均真实（V8 全部匹配）、代码与测试健全（V1–V7、V9）；错误仅限于**一个可由 `git rev-parse` 唯一确定的字段值**。依既有先例（Coordinator 在 closeout 冻结 `delivery_head`、复算并更正 sha256 pin），由 closeout **机械替换为真实 SHA** 并在 Closeout Record 中**显式记录该缺陷与更正**。

**必须继承的教训（建议登记 BL-17）**：owner 记录 commit 时**必须用 `git rev-parse HEAD` 的原样输出**，不得手工补全短 SHA；closeout 校验必须包含 `git cat-file -e <sha>:<path>`（本缺陷只有该命令能发现）。

## 4. 记录性事项（closeout 处理）

- **BL-15（第 5 次）**：`delivery_head` 记实现提交 `a4c8f9ac0…`（并**错误渲染**其完整值），而分支 HEAD 为 `fee223e36` → closeout 以实际值冻结。
- Handoff 的"下一任务建议"标记为该 Task 的**独立 Review**（已完成即本文件）；集成由 Coordinator 执行。
