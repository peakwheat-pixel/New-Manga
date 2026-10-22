# P02 AppContainer 契约 r3 Review 处置

日期：2026-10-10（Asia/Shanghai）
Integrator：Codex
Live baseline：`main@cddff58469b56e181019a8ddfeade80684bc7eb9` / tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`

## Review 对象与结论

- 契约：`verification/P02/appcontainer-isolation-contract-r3.md`，SHA-256=`30FA3DC10B5C84982018D0558B1262520615EDD17D5137335B808AF7429C3CC4`。
- Task：`doc/tasks/P02.md`，本轮派发 SHA-256=`74E3766600C75A41A0B4B18806BB2C494AB67305959846BB74082BC20B13CDE4`。
- DSH 正式报告：`verification/P02/dsh-appcontainer-contract-r3-review.stdout.md`，SHA-256=`50EA7BACBC1F64B6E835F39CF1519CA42EFD6BA4FB91A31C843B597A20388117`，CLI exit=`0`，session=`session-6e4e45bc-116c-4a3f-b860-f81190ca95bb`。
- DSH decision=`NOT_VERIFIED`，内容结论等同 `CHANGES_REQUESTED`；严重度计数 P0/P1/P2/P3=`0/3/8/8`。DSH 报告摘要写“Findings 总数 15”，但逐项编号为 P1-01..03、P2-01..08、P3-09..16，共 19 项，且严重度计数也合计 19。Codex 按 19 个实际 finding ID 逐项处置，不擅自改写 DSH 原报告中的 15。另 C-00 对象绑定能力未闭合。Codex 复算契约与 Task SHA 与 dispatch pin 一致；这不改变 DSH 的 `NOT_VERIFIED`。
- DSH 允许继续的范围仅为无 profile、无 ACL/label/registry 修改、无真实写探针的纯测量 OS preflight；这不是 profile 创建、Build 或产品测试批准。

## Finding disposition

| Finding | Codex 处置 | 约束/后续证据 |
|---|---|---|
| C-00 | **保持 `NOT_VERIFIED`** | DSH 会话不能独立计算 SHA；Codex hash 只证明本地当前字节匹配 dispatch pin。下一轮在 prompt 明列精确 SHA、Task SHA 和 review path；不得声称 DSH 已独立绑定 SHA。 |
| P1-01 私有 registry 创建前不存在性 | **OPEN / BLOCKED** | 不猜测 registry key。Microsoft Learn 将 `GetAppContainerRegistryLocation` 定义为取得当前 profile/current user 的 registry storage handle，未记录不存在时无副作用、目标 profile 存储的精确注册表路径或 view；Microsoft Q&A 工作人员亦未能从公开文档验证这些条件。故此项结果只能是 `UNPROVABLE / BLOCKED`，不得调用 `CreateAppContainerProfile`。参考：[GetAppContainerRegistryLocation](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerregistrylocation)、[Microsoft Learn Q&A 对公开契约的答复](https://learn.microsoft.com/en-us/answers/questions/6000195/supported-private-registry-reference-for-an-unchan)。 |
| P1-02 系统 DACL 只读可见性 | **接受，fail-closed** | 仅登记查询成功并实际枚举到的 ACL；`READ_CONTROL` 被拒/查询错误=`SYSTEM_ACL_UNREADABLE / BLOCKED`，ACE 缺失=`SYSTEM_ACL_MISSING / BLOCKED`。不提权、不设 ACL、不添加系统/盘符级回退。 |
| P1-03 既存 scratch 输出与 Low MIC | **接受并收窄** | 仅使用新建且精确登记的输出叶子；既有 target/cache/output 一律只读、不得复用或覆盖。Low label 不证明既有子对象可写；MIC 拒绝不算 AppContainer 隔离通过证据。无新叶子条件则 `BLOCKED`。依据：[Mandatory Integrity Control](https://learn.microsoft.com/en-us/windows/win32/secauthz/mandatory-integrity-control)。 |
| P2-01 `PYTHONUSERBASE` / user site | **采纳** | 后续任何隔离环境须将 `PYTHONUSERBASE` 指向 scratch 内精确路径，设置 `PYTHONNOUSERSITE=1`，并回读 `site.USER_BASE`/`sysconfig`；任何派生到 scratch 外写入路径均阻断。 |
| P2-02 负向 DACL control 继承 / MIC 混淆 | **采纳** | 负向 control 放入与允许 Package SID ACE 的父链分离的精确 scratch 子树；保持原 label/policy。拒绝必须同时有同一 token/desired-access 的 `AccessCheck` DACL 结果和实际控制对象拒绝；MIC 类拒绝为 `INCONCLUSIVE`。 |
| P2-03 `AccessCheck` 字段 / 写权限 | **采纳** | 分列 BOOL API return、`AccessStatus`、`GrantedAccess`、generic mapping、owner 与有效 `WRITE_DAC`/`WRITE_OWNER`；权限查询不替代 MIC。受保护路径不作真实写尝试。参考：[AccessCheck](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-accesscheck)、[Standard Access Rights](https://learn.microsoft.com/en-us/windows/win32/secauthz/standard-access-rights)。 |
| P2-04 一手来源不全 | **采纳** | 补齐 TokenInformationClass、`SeChangeNotifyPrivilege`、`S-1-15-2-2` 及 LocalDumps 依据：[TOKEN_INFORMATION_CLASS](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ne-winnt-token_information_class)、[Privilege Constants](https://learn.microsoft.com/en-us/windows/win32/secauthz/privilege-constants)、[Well-known SIDs](https://learn.microsoft.com/en-us/windows/win32/secauthz/well-known-sids)、[Collecting User-Mode Dumps](https://learn.microsoft.com/en-us/windows/win32/wer/collecting-user-mode-dumps)。 |
| P2-05 canary 根归属 | **采纳** | 每个 canary 以 scratch clone 根开头，写明完整相对路径；主仓 `verification/P02/tmp/**` 保持 deny。 |
| P2-06 WER / dump 外写面 | **采纳** | 在未来纯只读快照中登记 `%LOCALAPPDATA%\CrashDumps` 与 `%ProgramData%\Microsoft\Windows\WER\ReportQueue`、`ReportArchive` 的基线/结束状态。新 dump 或无法读取均阻断；不得修改 WER policy/registry。 |
| P2-07 exclusion manifest 漂移 | **采纳** | preflight 开始前固定、哈希并加时间戳记录排除清单；冻结后出现的新路径属于 `UNKNOWN / BLOCKED`，不可追认到 exclusion。 |
| P2-08 契约自带 SHA | **部分采纳** | 文件不能在自身字节内无歧义地写入自己的完整 SHA。采用 dispatch prompt + 独立 SHA manifest/verification 记录绑定，并明确仍需 Reviewer 有能力复算；不能把自述 hash 当独立验证。 |
| P3-09 特权 / 提权 | **采纳** | 禁止提权、take-ownership 与新 privilege；任何所需权限不具备即 `BLOCKED`。 |
| P3-10 profile/storage 命名 | **采纳** | 使用同一组固定术语 `profile directory`、`local-data directory`、`private registry storage`。 |
| P3-11 恢复后比较 | **采纳** | 如未来授权 scratch descriptor 变更，恢复后逐字段复读 owner/group、DACL ACE、mandatory label/policy、file ID；不匹配=`CLEANUP_BLOCKED`，禁止盲目重试覆盖。 |
| P3-12 表外对象只读 | **采纳** | 写入清单以外的对象（含 tracked 源码）一律只读。 |
| P3-13 `ERROR_ALREADY_EXISTS` / 残留 | **采纳** | 一律 `BLOCKED`；不复用、不覆盖、不删除，失败残留处理须单独授权。 |
| P3-14 MIC 阴性证据 | **采纳但非当前执行授权** | 后续若进入 synthetic probe，须单独证明预期 MIC 拒绝且不把它当 DACL/AppContainer 拒绝；当前没有 profile，不运行。 |
| P3-15 sibling path 语义 | **采纳** | `.task-envs` 与 `.worktrees` 均是仓库兄弟目录，保持 deny；不按字符串前缀混为仓库子目录。 |
| P3-16 moniker | **采纳** | moniker 是固定字面常量，不派生、不改写；不满足 API 输入限制即阻断。 |

## 继续条件与当前状态

可以继续的仅是精确声明且无写入副作用的测量或文档工作。P1-01 未解除前，不创建 profile、不调用会取得/初始化目标 private registry 的 API、不设置 ACL/label、不启动 probe、不运行 build/AC。P1-02/P1-03 的测量也不得被误解为能够绕过 P1-01。

截至本处置：profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；OS preflight=`NOT_RUN`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；Hard Build Barrier=`EFFECTIVE`；AC1–AC7=`BLOCKED / NOT_RUN`。本处置不改变 P02 产品范围、Owner allowlist 或 Build Gate。
