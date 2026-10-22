你是 P02PRE-R1F Round 5 修复版的独立只读 Reviewer。你不是实现者。只阅读下列精确冻结文件，不运行命令、capture script、host getter、registry/ACL API，不访问 `.tmp.driveupload` 内容，不改写任何共享文件。

项目目录：`G:\CODEX\New Manga`
Task=`P02PRE-R1F`；review base HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`，tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。工作树含未提交内容，作者未知；本次 Review 绑定下面逐文件 exact bytes/SHA，不以 branch 名或自然语言状态代替对象绑定。没有创建 commit，也不得改写或清理其它工作树内容。

## 精确 Review 输入

- `doc/tasks/P02PRE-R1F.md` — `19182 bytes / SHA-256 396E58F012F86F1F697B8800647CF863A380743A5817992F887AD5CAE7A1F452`
- `verification/P02/p02pre-r1f-manifest-20261011.md` — `18245 bytes / SHA-256 0D1EB5488712435ED9ACB18A4E3D54D1845EAF69E4FD7F53F345C8C60C6959D1`
- `verification/P02/p02pre-r1f-capture.ps1` — `64626 bytes / SHA-256 83C0126123C9799B594CF4F152D1B03AD7BC26E194EBD65E34309B23053A8E91`
- `verification/P02/p02pre-r1f-r5-reviewfix-selfcheck-20261011.json` — `2694 bytes / SHA-256 F2FCE66ECAE8E1BAC1AB8B795C2E004D91D8EE7061389415C76B92F7176FE39F`
- 原 Round 5 Review：`verification/P02/dsh-p02pre-r1f-review-r5-20261011.stdout.md` — `21403 bytes / SHA-256 8448A331D20AD36692D7A67738B2D7C5BFA7587A0AA1C922ECDE1A16C8F954E3`
- Codex Round 5 adjudication：`verification/P02/p02pre-r1f-r5-adjudication-20261011.md` — `5478 bytes / SHA-256 33CEBFCB72AA78B5373A1D40F4A13493CA1E14412D962A39AE05FFA07B8B0F50`

本候选的唯一 capture executor 仍固定为 `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`。新 self-check 的 child engine=`Windows PowerShell 5.1.26100.9549`；parent 编排 engine=`PowerShell 7.6.6`。请按冻结 executor 评估 target compatibility，不要将其中一个 engine 的证据误称为另一个。

原 Round 5 Review=`CHANGES_REQUESTED`，P0/P1/P2/P3=`0/1/2/5`。Codex 接受 F1–F8 并做了范围内修复；上面的 Codex adjudication 只供逐项对照，不能替代你自己的判断。请核查修复版是否完整、一致、安全、与 Task/manifest 相符，并报告任何仍未关闭的问题。

重点核查：

1. F1：逐组件遍历时普通 parent directory 是否允许继续；parent reparse 仍 stop；仅 leaf directory/non-regular 对象 stop；tracked symlink candidate 的 parent 不因 leaf Git mode 被误判。核对对应 in-memory assertions。
2. F2：`$GitMode=$null` 是否在函数绑定中保持 null；无 index mode 的 untracked regular leaf 是否按 Task/manifest 规定分类；reparse、directory 与 unsupported indexed modes 是否仍 stop。
3. F3：absolute/empty/`.`/`..`/ADS/trailing-dot/trailing-space/double-separator path 是否 fail-stop；归一化、canonical relative 与 repo boundary 检查的顺序是否保证 `.tmp.driveupload` 根及任意后代在脚本 per-candidate metadata/content getter 前排除。核对大小写与 `/`、反斜杠处理。
4. F4–F5：Task 的最终 parser artifact 是否统一为 R8；旧 parser round 与 Review round 是否清晰；首次 helper failure 是否精确说明绑定替换前 source 的 bytes/hash，未误称脚本解析失败。
5. F6–F7：成功与错误 repository record 是否都含 `errorOperation`/`error`；环境变量清单是否与固定 R1 清单逐项一致并准确为 35 项。
6. F8：status pathspec 是否精确限定并排除 root `.tmp.driveupload` subtree；文档是否诚实说明命令参数证据不等于 OS 级 Git 内部 no-read 证明，未夸大安全结论。
7. protected hash 清单是否可逐条读取，且新 self-check、Review follow-up、adjudication 与 R8 artifact 均纳入保护；唯一写入仍仅为一次 `CreateNew` evidence。
8. 所有缺陷、失败路径、计数、自检结果与阶段状态是否自洽；Review/self-check 不得被描述为 Gate PASS，也不得暗示 capture 已运行。

请只返回简体中文 Review，结构如下：

- Decision：`APPROVED` 或 `CHANGES_REQUESTED`
- counts：`P0/P1/P2/P3 = n/n/n/n`
- 每条 finding：ID、等级、文件/行号、可复现原因、最小修复建议；无 open findings 时明确写出
- 对重点 1–8 项分别标记 `PASS`/`FAIL`/`UNPROVEN` 并限定证据范围
- 明确声明只读了列出的文件，未运行命令、脚本、getter、capture，也未修改文件
- 明确说明此 Review 和 self-check 不是 P02PRE Gate、Technical Gate 或 Build Gate PASS；不得建议跳过 Windows PowerShell 5.1 R8 parse-only 或 Codex pre-run adjudication

结果将由 Codex 单独记录为 follow-up Review artifact；请不要创建或写入共享仓库文件。
