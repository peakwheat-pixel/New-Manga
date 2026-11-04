# FEA-09-UI-1 实现 Review r1（Codex 独立）处置与 DSH 裁决

- Reviewer：Codex，全新上下文 `/root`；未参与 FEA-09-UI-1 实现/返修；只读。
- reviewed_head：`e40c0f74bb13c75d724661420bd72f06e2d2518e`（parent `1a5894282`）。
- 报告：`doc/reviews/FEA-09-UI-1-impl-r1.md`（原字节；SHA-256 见 EV）。
- 结论：**changes_requested，P0=0 / P1=5 / P2=2**（R1–R7）。
- DSH 处置：**全部接受**；R3 由 DSH 冻结接缝裁决如下；返修后以新 head 交**全新上下文 Codex**复审（不得由返修者自审）。

## R1（P1）异常路径遗留密码 token / Secret-G
- 接受。最小修复：`SourceImportCoordinator` 在创建 token 的同一作用域**立即登记清理上下文**；所有未进入 accepted/成功交接的出口（能力缺失、Secret-G 注册失败、重新 plan 失败、start 被拒绝、取消、异常）统一：删除 token 文件（`SourceSecretStore.DeleteIfPresent`）+ `RevokeSecretGrantsAsync` + 零状态；补失败负测（能力缺失/注册失败/start 拒绝各 1）。

## R2（P1）receipt 暂时失败导致失去取消入口
- 接受。最小修复：VM 收到 null/暂时失败时保持 operation 与“状态未知（运行中）”活动状态，允许恢复轮询、取消、关闭保护；仅 receipt 终态或明确 typed 错误才释放；补暂时失败→恢复 polling→cancel 的 VM 负测。

## R3（P1）folder 接线越界 + reparse 递归风险
- 接受；**DSH 接缝裁决**：App 不自行递归/排序/授权。folder 源一律把目录路径与 `sourceKind="folder"` 交给 **Host `SourceReadCoordinator.IssueAsync`**（Host 已实现 EnumerateFolder：自然排序、隐藏/系统过滤、reparse 拒绝、预算），App 只消费返回 grant。若实现无法在最小改动内安全完成，则本 Task **限制 folder 引用导入入口为 typed unavailable**（不影响 Host/Core 已有 folder 能力），并在 AC/限制如实登记；不得在 App 复写 Host 授权/枚举语义。
- 需求：补断言证明 folder 路径不经 App 递归（或入口禁用 + UI 文案），并在 Handoff 明确。

## R4（P1）AC-4 缺少真实 UI→production controller→IPC 闭环
- 接受。最小修复：在 `NewManga.Host.Tests` 增加真实 IPC 测试（`NEWMANGA_FEA09_IPC=1`），使用 **`new HostController(HostOptions)`（生产 App adapter）+ `ImportDockViewModel`（真实 VM）** 走 plan→confirm→receipt；覆盖：普通文件成功、AES typed unsupported、单加密源错密重试、取消/已提交守恒、以及“确认前源变化→真实 Core 拒绝/UI 呈现 typed 拒绝”。既有直连协调器测试保留为下层证据；不得再声称 13 个 fake VM 测试构成 AC-4。
- 允许在 `apps/desktop-avalonia/tests/NewManga.Host.Tests/**` 内驱动 App/Host 生产类型（csproj 已引用 App）；若需要 App 内可见性调整，仅限 IVT/公开类型，不改冻结契约。

## R5（P1）多加密源共用一个一次性 token
- 接受。最小修复：同一 plan 含 **>1 个 encrypted 源**时，App 层直接 typed 拒绝（复用 `SOURCE_PASSWORD_REQUIRED` 或既有 validation 码 + 中文文案“一次仅支持一个加密源，请分别确认”），要求逐源独立确认/独立 token；不得扩展 Core wire；补 VM 负测。

## R6（P2）逐项提交边界未显示
- 接受：View 绑定 VM `CountsText`（已提交/待处理页数）；补 ViewModel/控件文本测试。

## R7（P2）整源跳过显示“跳过 0”
- 接受：分别显示 `skipped_pages` 与 `skipped_sources`；补整源已引用场景测试。

## 返修执行与复审
- Owner：ZCode（Appointment）；若 ZCode 额度不可用，按用户授权改由**未参与本 Task 实现的 Codex 全新会话**实现，返修者不得自审。
- 返修仅限既有 allowed_paths；不得改 C-05/C-15/C-16/C-07 冻结面、FEA-08/FEA-09 closeout、组合根、其他页面；不得 push/commit。
- 返修后门禁：build；全量 .NET（不减少）；真实 IPC（含新增 HostController+VM 闭环）；C-07 `--check` PASS；check.ps1；pins 17/17；`git diff` 范围；FEA-09 canonical 证据恢复。
- 复审：**全新上下文 Codex**（非本次返修者）；报告 `doc/reviews/FEA-09-UI-1-impl-r2.md`；approved 后 DSH 集成、回填 EV commit、Task done。
