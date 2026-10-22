# P02PRE-R1H Round 5 独立静态 Review 派发（修订 pins）

你是非作者 Reviewer `/root/p02_r1h_remediation_review`。Integrator/Adjudicator=`/root`；Round5 Owner=`/root/p02_r1h_codex_owner`，不得审查自己的实现。优先使用项目指定 `gpt-6.1-sol/high`；如果当前无法配置，报告实际模型/力度，不得声称未使用的配置。

## 本次重新冻结原因

先前 dispatch `codex-p02pre-r1h-remediation5-review-dispatch-20261012.prompt.md` 只冻结了主仓 round4 集成文件，未单独 pin 新的 round5 尚未集成候选。你在核对时发现这一缺陷并立即停止；只看到了 selfcheck 的单行差异，没有形成 Review verdict、没有写 Review 报告、没有运行代码或动态操作。此次以新版 pins 重新开始实质 Review；此前 dispatch 不计作 Review。

## 冻结评审输入

- 仓库：`G:\CODEX\New Manga`
- Owner worktree：`C:\Users\49745\.codex\worktrees\p02pre-r1h-codex`
- branch：`agent/codex/P02PRE-R1H`
- delivery HEAD：`dd5d2e3bc8e0702da9d059131f6364a997897661`
- parent：`7e7d0bce8dd86a2302d2a9eb278702d9c70354ff`
- tree：`8cf6cf2dec8b375746b4c423f3c00ffe611a60d7`
- frozen Task base：`946938bd0696dfddd01f87d61fe6723c63ecdc86`
- 修订 pins：`verification/P02/codex-p02pre-r1h-remediation5-review-input-pins-r2-20261012.json`
- 本 dispatch：`verification/P02/codex-p02pre-r1h-remediation5-review-dispatch-r2-20261012.prompt.md`
- 唯一报告写入路径：`verification/P02/codex-subagent-p02pre-r1h-static-review-remediation5-20261012.md`

先确认 refs、merge-base、worktree status 与所有 pins。关键区别：`candidateFiles` 下的三项必须从 pinned Owner commit/worktree 读取，并逐项验证 path、git blob、bytes、SHA-256；`referenceInputs` 是主仓既有文件，仅作要求引用的背景与运行证据，不能当成 round5 候选字节。若任何项不符或报告路径已存在，停止并报告，不得修改任何别的文件。

## Review 范围

审查完整 frozen Task base→delivery HEAD candidate diff，以及 Task、manifest、Handoff 与本次失败运行证据。根因是 AC4 selfcheck line 380 的 AST member-expression allowlist 漏了 component loop condition 访问的精确 `$parts.Count`，错误拒绝正确候选。Round5 仅增加了精确 `'$parts.Count'`。判断它能否关闭真实失败，同时是否误放宽任何 AST 安全约束或掩盖其它问题。

复核完整 R1H-001..007 处理、no-follow/fail-stop、AST 正负例覆盖、Task/manifest 一致性、Handoff 对测试与 Gate 状态的准确性。按仓库 Review 模板记录 findings 和优先级，给 verdict 与 P0/P1/P2/P3 数量。静态 Review 不得将任何 AC 或 Gate 记为通过。

## 权限边界

只读 Git 元数据、diff、候选与输入文件及哈希。唯一允许写的路径是上面的新 Review 报告。禁止 parser/selfcheck/fixtures/preflight/capture、host getter/API、tests、Build/Cargo、AC1–AC7、OS dynamic 或 Windows Sandbox；禁止集成/改源码/改治理文件。不要访问 `.tmp.driveupload`；受控 `git status` 必须将 `:(exclude).tmp.driveupload` 作为独立 argv。

报告前后记录 reference pins 与 candidate commit/blob/bytes/SHA pins。记录模型/力度（实际可见时）、未执行项与静态 Review 的限制。完成后交 `/root` Codex adjudicate。