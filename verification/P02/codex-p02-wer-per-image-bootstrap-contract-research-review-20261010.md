---
task_id: P02M9R
reviewer: /root/p02_isolation_advisor
author: /root/p02_manifest_reviewer
base_commit: cddff58469b56e181019a8ddfeade80684bc7eb9
reviewed_head: cddff58469b56e181019a8ddfeade80684bc7eb9
decision: approved
approval_scope: STATIC_RESEARCH_ONLY
---

# P02M9R：WER per-image / views / T0 静态合同研究独立 Review

## 1. Verdict 与对象固定

**Verdict=`APPROVED_AS_STATIC_RESEARCH_ONLY`；P0/P1/P2/P3=`0/0/0/0`。在本次记录范围内未发现需要修订的 finding。** 批准对象是下面固定 bytes/SHA 的研究报告，不能用于批准任何本机 registry/WER 查询、profile/ACL/API、preflight、Create、build/Cargo 或 AC。执行条件仍 `NOT_RESOLVED / BLOCKED`。

| 项目 | Reviewer 独立核对结果 |
| --- | --- |
| Owner 报告 | `verification/P02/codex-p02-wer-per-image-bootstrap-contract-research-20261010.md` |
| bytes | `17105`，与 Owner/派发值一致 |
| SHA-256 | `6207483ED6CE62650C346D18D42FC81CD5102C44A028BAF0DE4F131AF60411F3`，与派发值一致 |
| HEAD | `cddff58469b56e181019a8ddfeade80684bc7eb9`，实际 `git rev-parse --verify HEAD` 核对 |
| branch | `main`，实际 `git symbolic-ref --short HEAD` 核对 |
| Reviewer 独立性 | 本 Reviewer 未参与 P02M9 报告创作/修改；唯一写入本 Review。此前 authored 的 M7 是另一报告，不将其结论当 M9 Review 的替代证据。 |
| runtime model ID / effort | `MODEL_RUNTIME_NOT_EXPOSED`，不推测实际 backend |
| 日期 | 当前环境 `2026-10-11`（Asia/Shanghai）；文件名沿用冻结 Task 的日期 |

独立重读完整报告，未以 Owner 摘要替代审查。检查 live Task 的 `2026-10-10 16:19 UTC P02M9` 派发和后续 `16:24 UTC` 接续，Plan/STATUS/Index 当前顶部，协作协议及 Review 模板。允许/禁止边界与父任务的固定派发一致。未扫描工作区全量状态；没有修改 Owner、Task、Plan、STATUS 或 manifest。

## 2. 范围与依据

审查以下问题：

- Microsoft 正式来源能否支持报告对 per-image / HKCU 限制的事实判断。
- 通用 WOW64 view 规则是否被错误外推到 WER reader 或目标 EXE。
- destination、环境展开及 known-folder 说明能否冻结当前有效配置。
- r3 T0 first-read 与 r5 bootstrap 冻结要求之间的依赖，是否只是静态推导。
- source version、不可变 header 与 floating 文档是否分层；资料空白是否被误记为 PASS。
- 本机未知、未执行操作和用户 private-registry 单项 waiver 是否准确保留。

具体项目依据：`verification/P02/appcontainer-readonly-preflight-r3.md:20`、`:22`、`:24`–`:28`；`verification/P02/p02-owner-risk-waiver-execution-manifest-r5-20261010.md:39`、`:64`、`:122`、`:142`、`:145`。这些只作为规格内容，不是已执行证据。

## 3. Architecture：合同、安全和范围核对

| 报告位置 | 独立核对 | 结论 |
| --- | --- | --- |
| :19、:35；global → per-image | Microsoft [Collecting User-Mode Dumps](https://learn.microsoft.com/en-us/windows/win32/wer/collecting-user-mode-dumps) 明确 HKLM LocalDumps 下 per-application 设置覆盖 global，并以 `MyApplication.exe` 举例；崩溃后、退出前收集；LocalDumps 独立于其余 WER 开关。报告没有将示例推成路径/hash/架构唯一匹配合同。 | 来源支持。 |
| :20、:37、:91；HKCU | Microsoft [WER Settings](https://learn.microsoft.com/en-us/windows/win32/wer/wer-settings) 在 DumpFolder、DumpCount、DumpType、CustomDumpFlags 四项下都明确不支持 HKCU，包括 global / application-name 两种写法。报告没有把一般 WER 双 hive 说明推广到 LocalDumps 优先级。 | 来源支持。 |
| :39；额外观察候选 | 报告明确 HKCU 可成为未来额外观察候选，但不把它当有效政策源，且新增 per-image/view/value 读取须另冻结。r5 :39 当前只列两根键/三目录，未冻结 override/实际值。 | 不扩大当前读取权限。 |
| :45；HKLM SOFTWARE view | Microsoft [WOW64 key table](https://learn.microsoft.com/en-us/windows/win32/winprog64/shared-registry-keys) 给 HKLM SOFTWARE Redirected，并说明子键继承父规则除非另列例外；表未列 WER 单独例外。报告采用覆盖系统上的条件式推导。 | 通用 key view 推导合理；不等于 WER 实现读取 view。 |
| :47、:49；reader / target 绑定 | Microsoft [Alternate Registry View](https://learn.microsoft.com/en-us/windows/win32/winprog64/accessing-an-alternate-registry-view) 定义默认 view、KEY_WOW64 flags 与 shared key 例外；[Registry Redirector](https://learn.microsoft.com/en-us/windows/win32/winprog64/registry-redirector) 另列 ARM 视图。两页均不是 specific WER actor 的政策读取合同。报告明确保留 actor/EXE/架构 unknown。 | 来源与未知分离正确。 |
| :53、:55、:57；destination | [ExpandEnvironmentStringsW](https://learn.microsoft.com/en-us/windows/win32/api/processenv/nf-processenv-expandenvironmentstringsw) 描述环境展开，并非 WER 内部环境选择；[KNOWNFOLDERID](https://learn.microsoft.com/en-us/windows/win32/shell/knownfolderid) 给 LocalAppData PERUSER、ProgramData FIXED 的默认位置。报告没有把 default/controller 展开串当作实际 WER destination，也没有断言 dump 均在 scratch。 | 不能关闭实际 destination；报告结论准确。 |
| :61、:63；T0 顺序 | r3 :22 要 T0 是任何 Phase A 读取前第一项且覆盖全部五对象；:26–:28 用环境相关目录。r5 :145 明确要求冻结 bootstrap identity/path/module 许可，不能满足旧 T0 表述时停止。报告在“没有已冻结可信输入”条件下指出依赖循环，而非宣称任何实现永远不可能。 | 规格推导支持 `NOT_RESOLVED`。 |
| :65、:67；flags / 全进程副作用 | 正式 [KNOWN_FOLDER_FLAG](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/ne-shlobj_core-known_folder_flag) 及固定 header 区分 CREATE、DONT_VERIFY、DEFAULT_PATH、INIT。报告没有以 DONT_VERIFY 证明 absence，没有以 flags 证明 controller/loader/helper 全程无写，也未把 T0/T1 一致当期间无短暂写。 | 未作未经支持的安全推断。 |
| :69；未来顺序 | 标注“未释放”，新 bootstrap 观察区间须另冻结、独立 Review，并要求独立强制边界/证据；不借静态报告更改旧 first-read 要求。 | 合理候选，非执行批准。 |
| :96；waiver / Gate | private-registry absence 单项 waiver 未扩大到 WER/T0；报告保持 Hard Build Barrier 与 BLOCKED/NOT_RUN。 | 与当前 Task 边界一致。 |

**Architecture 结论：APPROVED，仅针对静态报告。** 未发现分层、授权或证据升级问题。其安全停止结论应保留。

## 4. 来源、版本与检索限制核对

Reviewer 本轮独立打开报告 S1–S9 的官方 URL、MicrosoftDocs 两个 source blob、H1/H2 full-commit raw URL；核对主要声明及字段。支持情况：

- [Collecting User-Mode Dumps 源文](https://github.com/MicrosoftDocs/win32/blob/docs/desktop-src/wer/collecting-user-mode-dumps.md) 的 `ms.date=07/18/2024` 与报告记录相符；[WER Settings 源文](https://github.com/MicrosoftDocs/win32/blob/docs/desktop-src/wer/wer-settings.md) 为 `03/12/2021`，Learn 页面编辑日期为 `2022-05-17`，报告如实分开。
- `docs` 分支和 Learn URL 可变；编辑日期不是 commit/OS build。报告 :31 明记 `DOC_IMMUTABLE_REVISION=NOT_CAPTURED`，没有假称正式政策文档已固定为不可变版本。本文未取得文档 commit，也没有复现 Owner 每次 history/API 访问失败；失败记录属于 Owner 的实际操作陈述，不能变成 Reviewer 独立执行记录。
- [WerApi.h 固定 source](https://raw.githubusercontent.com/microsoft/win32metadata/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68/generation/WinSDK/RecompiledIdlHeaders/um/WerApi.h) 本轮可读，网页行数 `1003`，`:479` 为 `WerReportAddDump`、`:640` 为 `WerSetFlags`；`LocalDumps` 文本检索无匹配。该 negative search 只覆盖该 header，不证明所有公开来源不存在合同。
- [ShlObj_core.h 固定 source](https://raw.githubusercontent.com/microsoft/win32metadata/75ec935a4f1ac56345daa9f7f0bc21db3e68ac68/generation/WinSDK/RecompiledIdlHeaders/um/ShlObj_core.h) 可读，`:900`–`:928` 的 flags 与报告相符，声明位置与报告记录一致。没有将 Microsoft metadata/recompiled header 当成已安装 SDK 或 WER DLL 实现。
- 报告对自身未核 SDK release number 明记 `NOT_IDENTIFIED`；不影响 full-commit 固定，不能据此推断主机 runtime。H1/H2 对 LocalDumps 政策/T0 无完整保证，结论没有超出资料。

S1 还明确：默认不启用，启用需管理员权限，custom crash reporting 不在此 feature 支持范围，service dump 位置依 service account；这些进一步限制静态默认路径推断。报告未提议启用/修改这些配置，也没有从“默认不启用”得出本机未启用，因此没有形成安全结论缺陷。本文不新增读取/启用授权。

## 5. Findings

在上述固定对象和记录范围内未发现问题。P0/P1/P2/P3=`0/0/0/0`。无需作者修订；报告自己列出的未解决安全条件是执行 blocker，不是该静态研究不合格的 finding。

## 6. Verification：实际执行与证据边界

Shell=`PowerShell`；cwd=`G:\CODEX\New Manga`；venv=`N/A`。以下 stdout/exit 为本轮工具返回值的记录；没有运行产品验证或机器状态 preflight。

| 场景 | 实际步骤 | 结果与证据 |
| --- | --- | --- |
| object binding | `Get-Content` 完整重读；`Get-Item` + `Get-FileHash -Algorithm SHA256` 只用于报告文档 | PASS；exit0，bytes/SHA 见 §1，与派发精确相等。 |
| baseline | `git --no-optional-locks -c core.fsmonitor=false rev-parse --verify HEAD`；`git --no-optional-locks -c core.fsmonitor=false symbolic-ref --short HEAD` | PASS；exit0，HEAD/branch 见 §1。未运行 Git status、build 或 hook/helper 命令；未声称测得 index 前后 hash。 |
| Task/治理边界 | Task last20、STATUS/Plan top5、Index top3、协议 top35、Review 模板 | PASS；exit0；当前 M9 派发及非作者 Reviewer 与 scope 相符。 |
| 规格引用 | `rg -n` 查询 r3 与 r5 的 T0/WER/bootstrap 文本 | PASS；r3 :22/:24–:28、r5 :39/:145 支持报告推导。首次 Reviewer 输入 r5 文件名缺少 `-20261010`，显示 file-not-found；随后 `rg --files verification/P02 -g '*manifest*r5*'` 定位到正确文件并成功读取。该错误没有被当成正文证据。 |
| 官方合同/版本 | `web.open` / `web.find` §3–4 所列一手 URL 与 full revision | PASS，限于静态支持性核对；未获得不可变政策文档 revision，保留边界。网页 `find KEY_WOW64` 一次未匹配，随后直接打开正文 :31–:50 成功读到 flags；未把该工具无匹配当 API 无定义。 |
| Windows registry/WER/env/token/profile/path/ACL | 不执行，Task 明禁 | NOT_RUN。 |
| 原生 controller/probe / T0/T1 / crash/dump 测量 | 不执行，Task 明禁且未冻结 | NOT_RUN / BLOCKED。 |
| OS/API/ETW/driver/service/Sandbox/build/Cargo/AC | 不执行 | NOT_RUN。 |
| 全进程副作用 / 写闭包 / destination closure | 本轮只审合同充分性，无 runtime evidence | NOT_VERIFIED / BLOCKED。 |

**Verification 结论：本静态 Review 所需 object、HEAD、来源与规格核对已完成；执行安全验证未运行且仍 BLOCKED。** 静态 Review 的 PASS 仅指文档核对，不是 WER、P02PRE、Create 或 Build Gate PASS。

关键本机未知继续保留：实际 WER/global/per-image/policy 配置、registry views/reader、所有 controller/probe/helper 映像身份与架构、raw/expanded DumpFolder、展开 actor/user、目录 ACL/reparse/ID、自动 debugger/custom crash reporter、其余 queue/archive/report destinations、bootstrap 未覆盖期间的副作用。没有本机证据能由本文填补。

## 7. 结论、复审与推荐下一步

Codex 可对 §1 固定报告作 **静态研究 adjudication**；推荐保留 `wer_per_image_rules=PARTIALLY_DOCUMENTED`、`host_wer_configuration=NOT_READ / NOT_VERIFIED`、`wer_view_destination_binding=NOT_RESOLVED / BLOCKED`、`t0_bootstrap_safe_order=NOT_RESOLVED / BLOCKED`。不得以本 Review 改为 READY 或扩大 registry/per-image/view/environment 读取范围。

下一步 Agent=`Codex /root`（Integrator）；可直接转发：请复算 M9 Owner 与本 Review bytes/SHA、核对 baseline/Reviewer 独立性并写相应 adjudication，集成静态结论；保持 WER/T0 blockers、private-registry 单项 waiver 与 Hard Build Barrier 原值。新增 bootstrap/读取 manifest 只能在单独冻结范围后由非作者 Review，当前不得运行 OS/API/Create/build。Reviewer 不直接修改共享治理或 Owner 文本。

如果没有另已释放的静态治理工作，本 Reviewer 无需下一步操作；交付后停止，等待 Codex adjudication。Owner 报告若字节改变，须新 pin 并复审，不将此 Review 自动转移到新对象。
