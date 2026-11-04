# FEA-09-UI-1 返修 r1 + DSH 集成 Handoff（2026-11-04）

- Task：FEA-09-UI-1（引用源导入最小 UI/适配接线）
- base：`7f4f4d3cd`；返修实现：Codex 全新上下文（ZCode 429 额度不可用，按用户授权故障转移）；集成/门禁：DSH。
- 状态：返修完成，DSH 复跑全部门禁通过，交**全新上下文 Codex** 复审（不得由返修者自审）。
- 未 commit/push（本文件写入时）；提交由 DSH 完成。

## 返修内容（R1–R7）

| Finding | 修复 | 证据 |
|---|---|---|
| R1 token/Secret-G 异常清理 | token 创建即登记清理上下文；未 accepted 的所有出口统一 `DeleteIfPresent` + `RevokeSecretGrantsAsync` + 清空 | 真实 IPC G/H/I/J（capability/register/start/replan 失败）通过，token 0 残留 |
| R2 receipt 暂时失败失去取消 | 保留 operation 与“状态未知”运行态，可恢复轮询/取消；仅终态或 `SOURCE_OPERATION_NOT_FOUND` 释放 | VM 两例（null/异常）通过 |
| R3 folder 越界/递归风险 | App 不再递归/排序/授权；目录路径 + `sourceKind="folder"` 交 Host `IssueAsync`（EnumerateFolder） | 真实 IPC `F_FolderUsesHostEnumerationAndOrdering`：2 页，隐藏文件排除 |
| R4 AC-4 真实闭环缺失 | 新增 `Fea09UiImportIpcProductionTests`（`HostController(HostOptions)` + 真实 `ImportDockViewModel` + HostRuntime + Python stdio），11 例；旧 coordinator 5 例保留下层 | 16/16 真实 IPC 通过；证据 `ipc/production-ui-import-ipc.*` |
| R5 多加密源共用 token | >1 encrypted 源 App 层 typed `SOURCE_PASSWORD_REQUIRED` 拒绝；逐源独立确认 | VM 负测 + coordinator 双层校验 |
| R6 逐项提交边界未显示 | View 绑定 `CountsText`（已提交/待处理页数） | 真实 Avalonia 控件文本测试 |
| R7 整源跳过显示 0 | 汇总与行分别显示 skipped_pages/skipped_sources | VM+控件整源 skip 测试 |

## 门禁（DSH 复跑）

- build：**0 warning / 0 error**
- 全量 .NET：**1317 passed / 0 failed / 74 skipped**（基准 1300/0 不减少）
- 真实 IPC：**16/16**（11 production + 5 lower-layer；`NEWMANGA_FEA09_IPC=1`，真 Python Core stdio）
- `generate_api_inventory.py --check`：**PASS**（C-07 冻结清单未变，无 UNFREEZE）
- `check.ps1`：PASS（3 warnings）；`verify_pins.ps1`：**17/17 PASS**
- 范围：全部在 allowed_paths；FEA-09 canonical 证据复跑污染已恢复；未 push。

## 证据

- `verification/FEA-09-UI-1/AC-MATRIX.md`（AC-1…AC-5 MET + 限制）
- `verification/FEA-09-UI-1/ipc/production-ui-import-ipc.json` / `.wire.ndjson`（11 例真实闭环 + 密码审计）
- `verification/FEA-09-UI-1/ipc/ui-import-ipc.json` / `.wire.ndjson`（下层 coordinator 5 例）
- `verification/FEA-09-UI-1/logs/gates.json`、`logs/dsh-integration.json`、`logs/dsh-scope-diff.txt`
- 返修原始记录：`repair-checkpoint.md`、`logs/repair-*.log/json`、`logs/test-results/*.trx`（Owner 环境的失败记录保留为原字节，不作为通过证据）

## 限制

1. FEA-09 canonical 证据可被常规测试复跑重写（既有债务候选；DSH 已恢复原字节）。
2. 多加密源仅支持逐源独立确认/一次一个（未扩展 wire）。
3. 生产 fixture 用测试内 C# launcher 包装真实 Python Core（故障注入钩子在测试 launcher 内），HostRuntime/生产 adapter/VM 未替换。
4. UI 证据为控件级文本/状态，不含整窗口视觉/E2E 录制。

## 下一任务

- **FEA-09-UI-1 实现 Review r2**（全新上下文 Codex；不得由返修者自审）。
- 复审通过后：DSH 集成验证 + Task done + EV commit 回填 + closeout。
