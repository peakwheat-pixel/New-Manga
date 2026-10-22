# DSH 独立实现 Review — P02PRE-R1G

你是非作者 Reviewer。请只审查已提交候选文本与 Handoff，不要修改文件、启动脚本、运行 shell/Git/PowerShell/测试、host getter、engine preflight、capture、Build/Cargo/AC；不要调用任何 profile/registry/ACL API，不要读取或查询 `.tmp.driveupload`，不要触碰 Windows Sandbox。可直接只读打开下列冻结文件；不要推断未列出的运行结果。

## 固定任务与基线

- Task=`P02PRE-R1G — PowerShell 7 只读取证恢复`；Owner/author=`Antigravity`；Reviewer=`DeepSeek Harness`；Integrator/adjudicator=`Codex`。
- Worktree=`C:\Users\49745\.codex\worktrees\p02pre-r1g\New Manga`；branch=`agent/antigravity/P02PRE-R1G`。
- Base=`cddff58469b56e181019a8ddfeade80684bc7eb9`；reviewed delivery HEAD=`9ec34a8847f625331c729306fd303bd5df09ab92`；implementation commit=`9eb14e35d39bcfa9f6bd89553a94dd5d86da2cd3`。
- Codex 在 Review 前核验过 worktree clean、base/branch/common-dir 正确，base→HEAD 文件集合严格为三个分配文件。不要把这个 Codex 核验描述成你独立运行了 Git 命令。

## 冻结 Review 输入

| 文件 | bytes | SHA-256 |
|---|---:|---|
| `doc/tasks/P02PRE-R1G.md` | 10012 | `BB686F68873DD09160B403B4D85843E803FB8C84B94DB211683D658EDBAC0995` |
| `verification/P02/p02pre-r1g-manifest-20261011.md` | 10599 | `BC103E0B7032561DF20AA2D0F91D226ED690915F476054F25D805C0455693D3E` |
| `verification/P02/p02pre-r1g-capture.ps1` | 77907 | `BCE0785B7E8B26B8B06ED1D9CED4F8E03F0BA9B3E8A5A23AD135A29C240D3563` |
| `verification/P02/p02pre-r1g-author-selfcheck-20261011.json` | 2349 | `090DBBEAB0D1E47FE869D3FF86911E1B5CE73BA1776B5D61E8DB264A63F1740B` |
| `verification/P02/p02pre-r1g-antigravity-handoff-20261011.md` | 11465 | `BC5446543F371EF4B94D05CD492A14DA762894688651620654215C606D6B39EF` |
| `verification/P02/p02pre-r1f-capture.ps1` (read-only baseline) | 67582 | `5A3FE118A8758CCDF0BEDBE170D31B34DA6C338101096EAA825DE80DF70E8316` |
| `verification/P02/antigravity-p02pre-r1g-implementation-20261012.prompt.md` | 4376 | `9B6995017B6569783E4B9107FB92186A83D6876B9EA439B7B9B9F521A372520B` |
| `doc/templates/REVIEW.md` (format reference) | 3915 | `048DD2C001BC16CE68B46460C2D23AA32BA1119091CA1E2ABA3EE4EE63ED4762` |

The six frozen source pins listed in the Antigravity prompt matched before implementation dispatch. The R1F source and manifest are read-only references; do not treat their prior run results as R1G evidence.

## 审查范围

请完整阅读 Task/manifest、三项交付文件及 R1F source/diff 文本，重点检查：

1. 是否只实现 Task/manifest 授权的最小后继；对比 R1F 时，路径、身份、Git argv/order、96 protected paths、`.tmp.driveupload` path-only/no-read、tracked symlink no-follow、TEMP/cache/WER/registry/ACL getter allowlist、子进程与 fail-stop/唯一 `CreateNew` 语义是否保持。
2. 固定 PowerShell 7.6.6 executable、edition、PSHOME、language mode、`Get-FileHash`/`Get-Acl` 命令与模块 attestation/precondition 是否精确、可审计；任何 unknown child/API/write 或失败路径是否会 fail-stop。
3. `phases` 初始/进入/完成/失败状态与 `stopCategory` 分类是否一致；错误时未到达项是否诚实保留 `NOT_REACHED`，不冒称 PASS。
4. 路径规范化、repository boundary、staging 子树排除是否在所有 filesystem getter/hash/ACL 前生效；是否存在 ADS、8.3 alias、reparse/symlink 或路径编码绕过。
5. 唯一 evidence 写入是否确实使用 `CreateNew`；输出碰撞/序列化错误/大小上限/子进程失败是否能保护现场、不覆盖、不重试。
6. Author self-check JSON 与 Handoff 是否准确区分静态实现交付、NOT_RUN 检查和未获技术证据；不应将 Review 或 owner waiver说成 Gate PASS。Handoff 中 AC1–AC3 的作者自述只作待核 claims，不能由作者自评代替 Codex adjudication。

本轮只审实现与文档一致性。Candidate parse/self-check、PS 7.6.6 child capability preflight、host capture、profile/registry/ACL 动作、Build/Cargo/AC1–AC7 均被明确标作 `NOT_RUN`；不要声称这些运行检查通过。R1F one-shot=`STOPPED / FAILED_PRECONDITION`，不得建议重跑。

## 输出要求

按 `doc/templates/REVIEW.md` 给出独立 Review：固定 base/reviewed HEAD 与输入 pins；明确 `APPROVED` 或 `CHANGES_REQUESTED`；列出 P0/P1/P2/P3 finding counts；每个 finding 写 severity、文件/行（可确定时）、触发条件、影响、建议；说明实际覆盖与未覆盖范围、是否运行命令（应为未运行）、残余风险。没有发现也要明确报告 `0/0/0/0` 并说明不代表 runtime/Gate PASS。不要写入任何 Review 以外路径；结果由 dispatch runner 另行保存。
