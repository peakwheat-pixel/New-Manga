P02PRE-R1F post-run documentation Review continuation #2 — same DeepSeek Harness session

这是一次独立、只读、范围狭窄的文档集成复审。请在同一 session `session-3f962413-c20f-4e85-83e8-ba22b7e6853c` 续接。原 post-run verdict `CHANGES_REQUESTED (0/0/2/2)` 保持不变；本次只判断 Codex 对 finding 的 disposition 和当前文档修复是否准确、一致、可恢复。你不是实现作者。

## 冻结输入与验证要求

仓库=`G:\CODEX\New Manga`，branch=`main`，reviewed HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`。请只读检查下表列出的精确输入文件；如环境允许，可用只读文件读取能力检查内容。不要执行 shell/Git/PowerShell 命令，不要调用 host getter/API，不要写入或修改任何文件。若某一来源不可访问，请把相应判断标成 `NOT_VERIFIED`，不要猜测。文件 pins 由 Codex 在派发前独立计算；不要因你的 sandbox 无法计算 hash 而把已给出的 pins 当作可疑，也不要声称自己复算过。

| Input | bytes | SHA-256 |
|---|---:|---|
| `doc/REBASELINE_PLAN.md` | 282002 | `3A77BC3140707D0F172FC45CA1919B050180A4B507AE4E9098D97B1555785FED` |
| `doc/STATUS.md` | 289222 | `2E3FD493A67403CB9F6EDE882A644BE584A426F74F522AA23F964EFEE7BE428C` |
| `doc/00_INDEX.md` | 58334 | `008F60FA72E6854CC16FA7D13B9A78423C97AC70C544EBB53BE383867A35E070` |
| `doc/tasks/README.md` | 37494 | `086112004ADD6C5C7D4EEB06EAC5B1390508D47BC1FC5B66DF4EDFED79E59C98` |
| `doc/tasks/P02.md` | 222177 | `ADD47CD06DA68206F0DA8572D905EAE0865CCAD783BBE7342E8AC26A683787DB` |
| `doc/tasks/P02PRE-R1F.md` | 33571 | `EA0C8F6DF5DE7501F56EDA77199FF6FD0EBCA5E214206B1DDFCF082626127A83` |
| `doc/tasks/P02PRE-R1G.md` | 6677 | `F47B1249D57BD630F927E6E964E2243396999008CE584172E13C67D75995321B` |
| `verification/P02/p02pre-r1f-manifest-20261011.md` | 46327 | `0AD7266DCF6D170AB43254F44D6232B3B99655EFD8445007D55DE5FB84B236B8` |
| `verification/P02/p02pre-r1g-manifest-20261011.md` | 10362 | `4774F702D7584E8B7BD1D2CD06B2A87297F48B8182F11A7ADC8738ED21E96E95` |
| `verification/P02/p02pre-r1f-postrun-adjudication-20261011.md` | 8716 | `ADD2C7538E3B2029E7C4487A072A36561AA387059BC016BAC93F35E01A79C685` |
| `verification/P02/p02pre-r1f-evidence-20261011.json` | 23131 | `DCB22B8EE1FC7ED824FDE12CDA68BE208DCDBAD9D88531C5E3171C0396F7CF70` |
| `verification/P02/p02pre-r1f-capture-20261011.stdout.log` | 0 | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `verification/P02/p02pre-r1f-capture-20261011.stderr.log` | 676 | `6346D824673ECFEE4ED6AC9A80758A3B27C66F1D226F26D179EAB0A9AECD81EA` |
| `verification/P02/p02pre-r1f-capture-20261011.exit` | 3 | `F1B2F662800122BED0FF255693DF89C4487FBDCF453D3524A42D4EC20C3D9C04` |
| `verification/P02/dsh-p02pre-r1f-postrun-review-followup1-20261011.stdout.md` | 7704 | `67DCF1502498188D49A7E9779FF6956CEF80CAF64BB21BBD53DF886BD237FBDF` |
| `verification/P02/codex-checkpoint-p02pre-r1f-postrun-20261011.md` | 9911 | `6257EB26628E69ADC1E6F3BDFCE641223E9840CBB090BF526B4896F4574FAE89` |
| `doc/templates/REVIEW.md` | 3915 | `048DD2C001BC16CE68B46460C2D23AA32BA1119091CA1E2ABA3EE4EE63ED4762` |

## 固定事实（不要重新解释成更强结论）

R1F 的 Windows PowerShell `5.1.26100.9549` 子进程确实启动一次，在 main `.git/index` prehash 处因 `Get-FileHash` `CommandNotFoundException` 停止，exit=1，one-shot 已消耗。实际证据只显示 identity=`PASS_WITH_EVIDENCE`；Git inventory/hash、scratch、后续 environment/path/ACL/TEMP/cache/WER/protected hash/registry/profile getters 未到达。底层命令不可用原因=`UNPROVABLE`。这不是 AC1–AC7 失败；没有 AC 运行。现有材料不证明 PowerShell 7 不兼容。

Owner waiver 和所有 Gate 必须原样保持：`private_registry_absence=UNPROVABLE`; Technical Gate=`NOT_SATISFIED`; Owner Risk Acceptance=`APPROVED`; Gate Disposition=`WAIVED_BY_OWNER`; Build Authorization=`AUTHORIZED_WITH_EXCEPTION`; 精确文本 `technical condition unmet; user explicitly accepted residual risk`; Build Gate=`BLOCKED`; Hard Build Barrier=`EFFECTIVE`; Build/Cargo=`NOT_RUN`; AC1–AC7=`BLOCKED / NOT_RUN`。本复审不是新的 waiver，也不释放 Gate。

## Review questions

1. 当前顶部状态文档是否把 R1F capture 写为真实执行后的 `FAILED_PRECONDITION`，并将 AC 清楚标成未运行而非失败？是否仍有顶部导航把当前状态错误写成 pre-run/capture `BLOCKED / NOT_RUN`？历史快照可以保留，但必须显式标记为历史。
2. R1F post-run Review finding `R1F-POST-01` 是否在 Plan、STATUS、Index、任务导航、P02 Task、R1F Task/manifest 与新 rolling checkpoint 中一致修复？其余 F2–F4 是否明确转入 R1G，且没有假称已完成？原 `CHANGES_REQUESTED` 是否保留？
3. 当前 DAG 和 recovery point 是否互相一致：R1F 的文档集成/独立窄复审是唯一 ACTIVE；R1G 是依赖 R1F 收口的 READY，Owner=`Antigravity`、Reviewer=`DeepSeek Harness`、Integrator=`Codex`，固定 branch/worktree/base；R2、Build Gate、Build/Cargo、AC1–AC7 保持 BLOCKED/NOT_RUN？
4. R1G 的 PowerShell 7.6.6 选择理由是否准确表述为“R1F 的冻结 PS 5.1 one-shot 已失败且不可重跑，因此对一个新候选使用新 executor 并先做独立能力预检”；是否避免声称 PS 7 不兼容或 child 能力已验证？
5. 是否保留 `.tmp.driveupload` no-read、no-reset/clean/stash/delete，以及原 pre-run checkpoint 和 R1F one-shot artifacts 不可修改等边界？

请只指出有证据的缺陷；不要要求额外阶段、改动 scope 或更强证明。没有问题就明确批准本次文档集成；若需要修复，列具体路径/行号、证据和最小改法。

## 输出

遵循冻结的 `doc/templates/REVIEW.md` 格式，中文报告，给出 YAML header、decision 和 finding counts、Verification 表、无占位符 Findings 表、Remaining risks。结论必须限定于“R1F post-run 文档集成”。不要把本次 verdict 替换/改写原 verdict。不要输出内部思维链，不做任何工具调用或改文件。明确说明哪些内容因无法访问而 `NOT_VERIFIED`。