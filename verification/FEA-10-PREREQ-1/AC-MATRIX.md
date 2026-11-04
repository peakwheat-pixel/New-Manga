# FEA-10-PREREQ-1 AC Matrix

Owner：Codex 本实现会话；2026-11-04。状态：实现快照待上下文独立 Review；无 commit/push。指定 base `1254d4e01608d3c9577872abb1dedea5661889aa`；实际 HEAD `e45baa8b5946a1d581f30b025db045c77e99a6df`。

| AC | 结果 | 当前证据与限制 |
|---|---|---|
| AC1 | MET | [逐条登记对照](REGISTRATION-COMPARISON.md)、[既有 Run 文本保留检查](logs/registration-comparison.log)、M2-C1 增量；wire 2.12 登记与 Core 默认 minor 3 分离 |
| AC2 | MET | [Host 定向测试](logs/host-projection-tests.log)：23 passed/0 failed/0 skipped；正式白名单、保留 code/requestId、unknown 安全降级、固定三新码映射 |
| AC3 | MET | 同一生产投影函数：去除三新码的 pre-registration 集合→unknown/false；正式集合→冻结 category/retryable；源错误不改写，未添加任何恢复/重试操作或 UI 专属分支 |
| AC4 | MET（DSH 复跑） | DSH 原生环境：build EXIT=0（0/0）；全量 1344 passed/0 failed/74 skipped EXIT=0；定向 CoreClient 13/13、Host 23/23；check.ps1 在 PLAN/STATUS 同步后 PASS；pins 17/17；见 `logs/dsh/{build,full-test,commands}.md` |
| AC5 | PARTIAL | 固定交付 commit 已由 DSH 建立；独立实现 Review 待进行；DSH 集成已记录。本会话未自审 |

| Gate/命令 | EXIT | 结果 |
|---|---|---|
| `dotnet build apps/desktop-avalonia/NewManga.sln -c Release --nologo` | 1 | FAIL：NuGet GetRestoreSettingsTask 的 path1 为 null；`logs/build-initial.log` / `logs/build-direct-environment.log` |
| `dotnet build apps/desktop-avalonia/NewManga.sln -c Release --nologo --no-restore -p:UsedAvaloniaProducts=`（补充） | 0 | PASS：所有项目编译，0 warnings / 0 errors；使用缓存并关闭遥测 target，不替代原门禁 |
| `dotnet test apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/NewManga.CoreClient.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~CoreProtocolTests\|FullyQualifiedName~AsciiWireTests"` | 0 | 13 passed / 0 failed / 0 skipped |
| `dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --no-build --filter FullyQualifiedName~Fea10PrereqProjectionTests` | 0 | 23 passed / 0 failed / 0 skipped |
| `dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build` | 1 | 全量未过滤：1333 passed / 11 failed / 74 skipped |
| `pwsh -NoProfile -File tools/governance/check.ps1` | 1 | READY DAG 与 Task 认领/交付状态不一致；初次 3、最终 4 warnings（含尝试日志未逐项登记提醒）。Plan/STATUS 写域外，待 DSH |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 0 | 17/17；C-01b/C-05/C-08/C-13/C-15/C-16 等冻结字节保持 |
| `git diff --check` / 范围检查 | 0 / 1 | whitespace 检查 PASS；全部 tracked diff 在写域；全树检查另有会话期间外部出现的两份未跟踪 Review/Appointment，来源待 DSH 核对，保留不动；FEA-09 evidence diff 为空 |

全量结果按项目：

| 项目 | passed | failed | skipped |
|---|---:|---:|---:|
| CoreClient | 136 | 0 | 22 |
| Host | 72 | 6 | 45 |
| App | 665 | 5 | 7 |
| Appearance | 21 | 0 | 0 |
| Presentation.Avalonia | 38 | 0 | 0 |
| ThemeEngine | 253 | 0 | 0 |
| DesignSystem | 117 | 0 | 0 |
| ApplicationCore | 31 | 0 | 0 |

11 项失败的直接观察：Host 2 项 DPAPI/保护失败、4 项目录权限/链接清理失败；App 4 项 FEA-06-RESIDUAL-2 仓外 task-env 创建权限失败、1 项字体扫描读取既有 FEA-09 native-registry 私有目录权限失败。完整名称/堆栈见全量日志。未在 base 上重跑，**不声称已证明全部为既有失败**；不修改写域外实现/测试或权限。

74 项 skip 的逐项原因见 [skipped-tests.json](logs/skipped-tests.json)：原始环境无 NEWMANGA fixture 变量；sidecar fixture 缺失或真实 IPC 未 opt-in。既有 Run 真实 sidecar 回归因此 NOT_RUN。PrepareRun/AcceptRun 的真实运行、性能、丢 ACK/重启 receipt 测试不属于本卡运行实现，NOT_RUN，归 FEA-10。

FEA-09 日志恢复：测试重写 wire-redacted.ndjson；git checkout 因 `.git/index.lock` 权限失败，改以只读 `git cat-file --filters HEAD:...` 的 checkout-filtered 字节还原；后续 Git diff 为空，见 [恢复日志](logs/fea09-restore.log)。没有修改冻结 pin、FEA-08/FEA-09 closeout 或共享组合根。

环境详情见 [ENVIRONMENT.md](ENVIRONMENT.md)。Review/集成/closeout 前仍需 DSH 处置原定 build、全量 FAIL/skip、权威指针，以及由新上下文审查固定交付。

最终范围待裁决：本会话开始 Git status 为空；收尾时另出现 `doc/reviews/FEA-10-appointment.md` 和 `doc/reviews/FEA-10-scope-r6.md`。本 Owner 未创建/编辑/删除它们，未将其纳入交付 manifest；整个工作树范围检查 EXIT=1，不把别人的文件清除以制造 clean。本 Owner 的实现/文档/测试/证据均在 allowed_paths；DSH 需核对并发来源。

## DSH 集成复跑（2026-11-04）

- build：`dotnet build apps/desktop-avalonia/NewManga.sln -c Release --nologo` → EXIT=0，0 warnings / 0 errors（`logs/dsh/build.log`）。
- 全量：`dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build` → **1344 passed / 0 failed / 74 skipped**，EXIT=0（`logs/dsh/full-test.log`）。
- 定向：CoreClient `CoreProtocolTests|AsciiWireTests` **13/13**；Host `Fea10PrereqProjectionTests` **23/23**。
- 范围：tracked diff 全部 allowed_paths；FEA-09 canonical 证据已恢复、无 diff；冻结字节未改（pins 17/17）。
- 说明：Owner 环境的 build restore 失败与全量 11 项失败为 Codex 沙箱环境限制；DSH 原生环境复跑全绿，不改变实现字节。
