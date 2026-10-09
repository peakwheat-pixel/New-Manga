# P01 AC7 正式非作者 Review：只读固定差量审查

你是 DeepSeek Harness Reviewer，不是 P01 Owner。请对下面的固定 Git head 完成独立正式 Review。此会话的工作目录应为本条消息声明的独立 reviewer worktree；只使用文件只读工具 glob/read，不要调用 pwsh、cmd、Git、terminal 或任何写入工具。本机 DSH shell 曾因 SetNamedSecurityInfoW (Win32 5) 失败；本轮不要求 Reviewer 执行 shell 检查。

## 固定对象与材料指纹

- Task：P01《台账元数据与Review载体取证》
- base_commit：826bea12a132c5af2ac0cd1244d00e9170093c71
- reviewed_head：91ab1ef8ddaa1d00b0b34880a103937b4831590d
- reviewed tree：6f8477d7fbc428b94aa031ae4fce1196cfb7e647
- Owner branch/worktree：agent/codex/P01-metadata-audit；G:/CODEX/New Manga.worktrees/P01-metadata-audit-codex
- 本 Review 的独立 worktree：G:/CODEX/New Manga.worktrees/P01-c8-review-dsh；该 worktree 应处于 detached HEAD 且精确对应 reviewed_head。
- 完整差量包：verification/P01/dsh-review-c8-input.diff；由调用方从 base..reviewed_head 用 git diff --binary --no-ext-diff --unified=10 生成；2090 行、208116 bytes、SHA-256=9751461597b7a1d6e614609918d7c83eb49dcbc12f8d0479d787b1c524c183ca。
- Codex fixed-head Gate：verification/P01/ac7-c8-fixed-head-check.log；SHA-256=3c000cbeeca7ab7f0cd06362fb3c0a9403491b9078005ef5ef28b95ff48a0554；该日志由 Codex 运行，不得说成 DSH 自己运行。
- Task AC 与冻结范围：doc/tasks/P01.md
- P01 逐项审计依据：verification/P01/metadata-audit.md
- Owner handoff：doc/handoffs/P01-9b124936.md
- 历史 Review：doc/reviews/P01-6f24006c-dsh-r1.md 与 doc/reviews/P01-3e67d53-dsh-r2.md；它们的 blocked decision 必须保持不变。
- 当前协作和Review标准：AGENTS.md、doc/09_COLLABORATION.md §6、doc/templates/REVIEW.md。

## 必须完整阅读

1. 先读取差量包全部2090行。若 read 工具有范围参数，用它支持的 offset/limit 语义分段读取，逐段前进直到完整EOF，并自行核对没有遗漏/截断。不要仅凭本prompt、文件名或Owner摘要作结论。确认差量包指纹与上列一致；如果无法核验完整覆盖或内容被截断，明确记录并决定 blocked。
2. 读取 P01 Task、metadata-audit、P01 Handoff、C8 Gate日志、R1/R2报告以及以下来源：GC2、DETECT3、ANNOTATE-R2、SYNTH 四个来源Task；对应Handoff；P01报告中列出的 Review/verification carriers。允许用glob/read定位引用；不得查看/修改无关用户数据。
3. 检查完整base..head差量和来源AC，关注allowed_paths、字段证据、carrier身份/fixed head/hash、NOT_VERIFIED边界、用户裁决/来源Task状态保护、导航和路线校验器、恢复点准确性、超范围产品或测试变更。所有finding须给级别、文件与行/hunk、触发和影响、证据及建议。没有发现时写明覆盖范围内未发现问题。
4. 报告中分别给出 Architecture 与 Verification 结论。当前C8 Gate日志显示：43 paths；base祖先PASS；allowed-path越界0；产品/代码差量0；range diff-check EXIT=0；在P01绝对路径运行route validator EXIT=0；ANNOTATE-R2来源Task unchanged；root main仍为714138de3da06013e3ea35395e0c11b3d15fc371且24项dirty pathset unchanged。请独立阅读日志并判断证据是否可信/充分，不要声称自己复跑了这些命令。
5. Reviewer shell/Git/Python执行状态须写NOT_RUN (Win32 5环境约束)。产品测试/build/GUI为NOT_RUN且本Task无产品差量。若这些缺项在你的判断中属于关键未验证路径，不可approve；说明具体缺口。P01允许来源Review carrier缺失为NOT_VERIFIED，Task明确允许只记录，不要借此生成Review批准或篡改来源Task。
6. 只读，不修改文件，不创建commit，不集成，不运行外部副作用。

## 报告格式

按 doc/templates/REVIEW.md 写正式Review Markdown，frontmatter需含：
task_id=P01
reviewer=DeepSeek Harness
author=Codex
base_commit=826bea12a132c5af2ac0cd1244d00e9170093c71
reviewed_head=91ab1ef8ddaa1d00b0b34880a103937b4831590d
decision=pending / changes_requested / approved / blocked

报告须包含：审查范围/未覆盖项、Architecture、Verification表、Findings（没有则明确0）、各 finding disposition、最终是否可交Codex Integration Gate及理由。只能选实际decision；C3/C6旧blocked不可改写。严禁只给计划、写模糊“看过了”，或伪报完整读取、命令、PASS。
