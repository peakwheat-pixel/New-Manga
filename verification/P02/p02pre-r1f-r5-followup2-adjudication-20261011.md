# P02PRE-R1F Review Round 5 follow-up #1 — Codex adjudication

时间=`2026-10-11`；Task=`P02PRE-R1F`；Repo=`G:/CODEX/New Manga`；branch=`main`；base HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`。当前工作区 dirty，既有未知作者内容与所有新证据均保留；没有 reset/clean/stash/覆盖/删除/提交。

## 独立 Review 与输入 pins

- 非作者 Reviewer=`DeepSeek Harness`；DSH session=`session-4ecb00e0-7c96-4b40-a5cc-96ff702a347c`；headless CLI exit=`0`。
- Decision=`CHANGES_REQUESTED`；counts=`P0/P1/P2/P3=0/0/0/4`。
- Review stdout=`verification/P02/dsh-p02pre-r1f-review-r5-followup-20261011.stdout.md`，`16554 bytes / SHA-256 998905D33EF2FC18766999AE7D184A559836DB9F0AF138AF521787411C934B5D`。
- Review stderr=`verification/P02/dsh-p02pre-r1f-review-r5-followup-20261011.stderr.log`，`160606 bytes / SHA-256 894F6D4F8A8C328EF4E2558043FFC9AEB7758F1E4D80089B40255DEBDA120A91`。
- Exit artifact=`verification/P02/dsh-p02pre-r1f-review-r5-followup-20261011.exit`，`3 bytes / SHA-256 13BF7B3039C63BF5A50491FA3CFD8EB4E699D1BA1436315AEF9CBE5711530354`，内容=`0\r\n`。
- 本轮送审 exact bytes：Task=`doc/tasks/P02PRE-R1F.md`，`19182 / 396E58F012F86F1F697B8800647CF863A380743A5817992F887AD5CAE7A1F452`；manifest=`verification/P02/p02pre-r1f-manifest-20261011.md`，`18245 / 0D1EB5488712435ED9ACB18A4E3D54D1845EAF69E4FD7F53F345C8C60C6959D1`；script=`verification/P02/p02pre-r1f-capture.ps1`，`64626 / 83C0126123C9799B594CF4F152D1B03AD7BC26E194EBD65E34309B23053A8E91`；self-check=`verification/P02/p02pre-r1f-r5-reviewfix-selfcheck-20261011.json`，`2694 / F2FCE66ECAE8E1BAC1AB8B795C2E004D91D8EE7061389415C76B92F7176FE39F`。
- Reviewer 声明只读六个输入文件，没有修改/删除/创建项目文件，没有运行 capture、host getter、registry 或 ACL 操作，也没有读取 `.tmp.driveupload` 内容或 metadata。一次 `Get-ChildItem` / `Get-FileHash` 命令尝试被 DSH 文件沙箱在授权阶段拒绝；未产生命令输出或文件访问。报告是静态 Review，不是运行验证或 Gate PASS。

## Findings adjudication

| Finding | Codex 决定 | 处置与边界 |
|---|---|---|
| R5F-F1 / P3：manifest 把旧 parser R7 写成最终目标；Task 对 Review Round 5 与 parser R5–R8 的命名混用 | `ACCEPTED / FIXED` | manifest 将 R7 明确标为旧候选 artifact，当前最终 parser 定为 R8；Task 中相关行使用 `Review Round 5`、`parser R5`、`Review Round 5 follow-up #2` 等完整名称。 |
| R5F-F2 / P3：PowerShell `LinkType` 属性可能不存在，空值会被写成空字符串 | `ACCEPTED / FIXED` | script 新增 `Get-LinkTypeEvidence`：属性缺失或空值输出 `NOT_AVAILABLE_ON_ENGINE`，非空值照原样记录；self-check 覆盖两种缺失情形与非空值。仍不读取/解析 link target。真实 host 字段值留给后续实际 capture 记录；本轮没有调用 host getter。 |
| R5F-F3 / P3：protected-hash 两组清单有重复 key，可能重复读取同一证据文件 | `ACCEPTED / FIXED` | 删除第二数组中重复的 Review Round 5、自检和 adjudication 项；Codex 对 script 内两数组做静态路径计数：`63 keys / 63 unique / 0 duplicates`。此计数不是 capture 运行证据。 |
| R5F-F4 / P3：字符串 canonicalization 不展开 Win32 DOS 8.3 alias | `ACCEPTED / FIXED` | `Test-SafeRepositoryRelativePath` 在任何 candidate filesystem getter 之前拒绝任何含 `~[0-9]` 的 path component；self-check 覆盖 `TMPDRI~1/...`。此类路径 fail-stop，不进行 `Get-Item`/hash/ACL；合法项目名若含相同模式也会安全停止，属于有意的保守边界。 |

## 新候选与隔离自检

- Task=`doc/tasks/P02PRE-R1F.md`，`21428 bytes / SHA-256 81D4EB50480475B41BCA366C37078B93370E85B1AB8AB6CFAC73F89649765E73`。
- manifest=`verification/P02/p02pre-r1f-manifest-20261011.md`，`20571 bytes / SHA-256 06B724979F8F4065372DACDE0BBE713013864FE4431BD5BE1ACE871DEAE5F946`。
- script=`verification/P02/p02pre-r1f-capture.ps1`，`65533 bytes / SHA-256 6B7556C784607B9CA52EC0879895676C13FE1AD67E0639A0C64269C700240CD1`。
- isolated self-check=`verification/P02/p02pre-r1f-r5-followupfix2-selfcheck-20261011.json`，`2308 bytes / SHA-256 1696B781A65D87D210F4CA909891FAF7ACCD088167091DF1EEB381E41A2CF1E2`。父级 PowerShell `7.6.6` 仅编排；child=`Windows PowerShell 5.1.26100.9549`；exact source parent/child hash 相同；parse=`PARSE_OK`、7 个纯函数 assertions=`PASS`、parse errors=0、assert output=0、child stderr=0、capture/host getter/registry/ACL write=false。
- isolated self-check wrapper attempt #1 绑定了本次候选 source，但将完整 Base64 放在 command line 导致 child 未启动；其结果=`HARNESS_FAILURE / CHILD_NOT_STARTED`，不是脚本失败。独立报告=`verification/P02/p02pre-r1f-followupfix-selfcheck-wrapper-attempt1-20261011.md`（`1179 bytes / SHA-256 CABB770B21701E96A083D1FB22E55122ECD89CCA5EE86114A5393697027D9703`）。之后改用 redirected stdin 并用新的唯一 self-check artifact 重跑；未覆盖失败证据或旧候选。

## 尚未验证与当前 Gate

- Review Round 5 follow-up #1 的总体结论仍是 `CHANGES_REQUESTED`；Codex 已处理 4 项 P3，但新候选尚未获得独立 Review。当前必须派发 follow-up #2，只读复核新的 Task/manifest/script/self-check/adjudication exact bytes；Reviewer 不运行命令、host getter、capture 或写共享文件。
- Reviewer 未打开原 R1 manifest（不在其输入清单），因此 R1 继承的逐项 path/environment/protected-hash 配置对账仍是 `UNPROVEN`；本报告不把该子项升级为 PASS，留 Codex pre-run reconciliation。
- Windows PowerShell parser R8=`NOT_RUN`；R1F capture=`BLOCKED / NOT_RUN`；没有 host getter、profile、registry/ACL 写入、build/Cargo 或 AC1–AC7。
- `private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；原文=`technical condition unmet; user explicitly accepted residual risk`。Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`。本次 Review、自检和用户 waiver 都不是 Gate PASS。
- Windows Sandbox 未查询、安装、启用或启动。后续仍按唯一 DAG 和 rolling checkpoint 自动推进。
