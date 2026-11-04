---
task_id: FEA-09-UI-1
author: Codex（全新返修实现上下文 /root；非 Reviewer）
recipient: DeepSeek Harness
base_commit: 7f4f4d3cda882cc4c3bb7c24c37a180480333a17
delivery_head: 未提交工作树（环境阻塞，非完成交付）
status: blocked
---

# Handoff：FEA-09-UI-1 返修 r2（待裁决）

## 交付结果

**未完成，待裁决。** 用户明确授权本全新 Codex 会话接替额度不可用的 ZCode 返修；仅改 Task allowed_paths，未 commit/push，未派发、未自审。起步 main/head 与指定基线一致且 clean。

| R | 已写变更 | 实际验证 |
|---|---|---|
| R1 | SourceImportModels：token 创建即登记清理上下文；未 accepted finally Delete+Revoke+清上下文；start ACK accepted 校验；统一失败清理覆盖 replan/拒绝/异常/取消。 | Release 编译通过；能力缺失/注册失败/start 拒绝/replan 失败 4 例真实负测**初始化 BLOCKED**，不能认定修复验收完成。 |
| R2 | ImportDockViewModel：暂时 null/异常保留 operation 与状态未知活动态，自动恢复轮询、可取消/关闭保护；仅 terminal/not-found 释放；HostController 成功 receipt 清 LastError；password finally 清空。 | null 与 IOException→恢复 polling→cancel 两例 VM PASS。 |
| R3 | SourceImportModels：删除 App 递归/自然排序/直接 Registry.Authorize；folder 路径+sourceKind=folder 交 Host IssueAsync；身份消费 Host registry id，App 只消费 grant；VM/View 增目录选择入口。 | 只编译；folder/Core 兼容性未验证。若最小接缝不通，须按裁决改 typed unavailable，禁止补写 Host/Core 语义。 |
| R4 | Host.Tests 新 Fea09UiImportIpcProductionTests + Support/Fea09ProductionFixture，真实 new HostController(HostOptions)+ImportDockViewModel→HostRuntime→stdio；普通/整源 skip、AES、单源错密重试、第一页真提交后暂停取消/重试去重、源变化、folder、清理负测、动态审计。 | 新 11 例+旧 5 例合计16例全部 fixture 创建失败，未进入业务断言；仅编译通过。旧直连 coordinator 5例保留原字节为下层测试；fake VM 17例不充 AC-4。 |
| R5 | VM/coordinator 拒绝 >1 encrypted 源，SOURCE_PASSWORD_REQUIRED + 中文提示逐源确认，不扩 wire。 | VM 负测 PASS。 |
| R6 | View 绑定 CountsText，行显示已提交/待处理页数。 | 真实 Avalonia 控件文本测试 PASS。 |
| R7 | 汇总与行分别显示 skipped_pages/skipped_sources。 | 0页/1源整源skip VM与控件 PASS；真实重复源用例待 IPC。 |

变更路径清单见 `verification/FEA-09-UI-1/logs/repair-scope-diff.json`。核心涉及 4 个 App 生产文件、2 个 App.Tests 文件、2 个 Host.Tests 新文件，以及本 Task/Handoff/verification。未改 NullHostController、IHostController、组合根、其他页面、冻结契约、FEA-08/09 closeout。旧 Handoff/r1 Review/裁决/DSH 集成日志原字节保留。

## 验证证据

所有日志带 runner/解释器/命令与 EXIT；全量 TRX、逐项失败/skip 明细已入库。

| 门禁 | 实际结果 | 证据（verification/FEA-09-UI-1/ 下） |
|---|---|---|
| dotnet build apps/desktop-avalonia/NewManga.sln -c Release --nologo --no-restore | PASS 0 warning / 0 error，EXIT=0 | logs/repair-build.log |
| dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build（无 filter） | **FAIL 1306 passed / 11 failed / 74 skipped / total1391，EXIT=1**；8程序集全部完成 | logs/repair-full.log；logs/repair-full-inventory.json；logs/test-results/*.trx |
| 定向 ReferencedImportUiTests | PASS 17/17，EXIT=0 | logs/repair-vm.log |
| NEWMANGA_FEA09_IPC=1 + NEWMANGA_BUILD_PYTHON=C:/Python314/python.exe；Host.Tests filter FullyQualifiedName~Fea09UiImportIpc | **BLOCKED 16/16 fixture 初始化失败，EXIT=1**；业务 NOT_RUN | logs/repair-ipc.log |
| C:/Python314/python.exe tools/generate_api_inventory.py --check | PASS，EXIT=0；IHostController54/Reader1/Run6，冻结清单未变 | logs/repair-api.log |
| PowerShell tools/governance/verify_pins.ps1 | PASS 17/17，EXIT=0 | logs/repair-pins.log |
| PowerShell7 tools/governance/check.ps1 | 当前最终结果见 gates.json（首次 PASS 3 warnings） | logs/repair-governance.log |
| 范围+冻结面+FEA-09恢复 | 以最终 scope inventory 为准；git checkout 因 .git/index.lock 禁写而失败，已用 git show HEAD:path 的原始 blob 字节恢复污染文件；FEA-09 diff 为空 | logs/repair-fea09-restore.json；logs/repair-scope-diff.json |
| 密码审计 | 当前 Task evidence/日志/异常文本静态扫描见 JSON；生产 request+response/registry 动态审计 BLOCKED，不能写 PASS | logs/repair-password-audit.json |

测试数不减少：上一交付 1313+0+63=1376；新增4个VM用例+11个IPC用例=15，总数1391。全量11失败都在未修改的既有测试：Host6（native DPAPI、SecretStore、registry ACL、junction安全测试），App5（4个 residual2 workspace 创建、1个字体扫描遇既有不可读 registry 目录）；原文及堆栈逐项保存在 TRX，未经本会话修复或豁免。74 skip=原63+新增11 IPC环境门，全部名称与原因见 inventory，未人为减少测试。

## 接收方式与风险

仓库 G:/CODEX/New Manga，main，HEAD 仍 7f4f4d3cda882cc4c3bb7c24c37a180480333a17。无新 commit，无 push。

**阻塞**：当前沙箱仅允许源码仓库写入（和系统temp），不允许项目规定的 G:/CODEX/New Manga.workspace；IPC 在创建隔离目录时 UnauthorizedAccessException。AGENTS/WORKSPACE_GOVERNANCE 禁止把新Task环境随意搬到仓库/temp，本会话未绕过。全量还实证当前沙箱 native DPAPI/ACL/junction 不可用。PowerShell 默认执行器 Windows740 后改用 Node child_process；子进程仅补 APPDATA/NuGet cache、设置 AVALONIA_TELEMETRY_OPTOUT=1；初次编译环境失败已保留日志，最终 no-restore 构建通过。

**剩余产品风险**：R1生产失败出口没有动态证明；R3 folder grant/Core兼容性未证明；R4新launcher、测试hook、源变化判别与replan失败码尚未实际执行，可能需要修正。不要把本工作树当成 ready-for-review 或已满足全部 AC。动态密码审计尚未覆盖新生产成功/失败分支。不得因此改冻结契约或Host/Core。

## 下一任务建议

- Task：继续同一 FEA-09-UI-1 返修，不释放新Task。
- Agent：DSH先处置执行环境；随后由获授权实现者恢复；全门禁通过后另一个全新上下文Codex复审，本返修会话不得自审。
- Recovery point：G:/CODEX/New Manga，main，base=head 7f4f4d3cda882cc4c3bb7c24c37a180480333a17 + 本次dirty文件，见scope inventory与repair-checkpoint。
- Scope：沿用Task allowed_paths；不得改冻结C-05/C-15/C-16/C-07、FEA-08/09 closeout、组合根、其他页面；不commit/push；禁止扩大共享wire/Host/Core。
- Gate：相邻workspace可写且原生保护能力可用后，先核对HEAD/dirty与本Handoff，再跑真实IPC并修正未验证代码；再Release build/全量dotnet test/真实IPC/API inventory/check/pins17/17/范围/密码全域审计，恢复FEA-09证据；更新AC/EV，再由独立上下文Codex复审。
- 可直接转发：**“DSH：FEA-09-UI-1返修停在待裁决。仓库G:/CODEX/New Manga，main，base=head 7f4f4d3cd，未提交工作树见doc/handoffs/FEA-09-UI-1-repair-7f4f4d3cd.md。请先提供允许写G:/CODEX/New Manga.workspace且可用native DPAPI/ACL的执行环境，再按既有allowed_paths恢复返修，验证R1/R3/R4与新production IPC fixture；完整门禁通过后交另一全新上下文Codex复审。不得commit/push或修改冻结契约、closeout、组合根及其他页面。”**

补充恢复核验：FEA-09/logs/wire-redacted.ndjson 与 HEAD 的原始字节逐字节相同（SHA-256 5bc320343d0a00ceb962578ad07fbc68eeb2e013dd3611cd870ca38885195e3e），git diff --quiet EXIT=0；git status 仍显示 M。因 .git/index.lock 禁写未刷新索引，保留此状态差异供 DSH 核对，未修改 .git。此为字节比较事实，不声称已取得干净 git status。
