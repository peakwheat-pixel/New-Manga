# AC1：verification 未跟踪证据逐项分类

生成依据：`git ls-files --others --exclude-standard -- verification/`；生成时排除本 Task 自身的 `verification/GOV-DEBT-CLEANUP-1/`，避免清单递归自包含。仅以当前 READY/在飞 Task、Task 的 Canonical Evidence 表、治理机制文档/脚本中的精确路径命中或当前 Task `evidence_dir` 作为“保留”引用证据。未命中的文件按文件类型说明独立证据价值。

基线文件数：1474；总字节：32081944。文件集合相对于生成时刻的 Git 未跟踪清单；本目录生成物不属于该集合。

## 分组计数

| verification 子目录 | 文件数 | 字节 |
|---|---:|---:|
| `codex-pause-checkpoint-20261010-1228.md` | 1 | 7065 |
| `codex-pause-checkpoint-20261010-update-restart.md` | 1 | 4171 |
| `M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD` | 2 | 10526 |
| `P02` | 1072 | 27183590 |
| `P02-DOC-PROVENANCE-1` | 1 | 8257 |
| `P02-NEW-TIME-BASELINE` | 33 | 146709 |
| `P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION` | 39 | 78750 |
| `P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION` | 60 | 163202 |
| `P02PRE-R1H-FORENSIC-RECOVERY` | 9 | 255945 |
| `P02PRE-R1H-H1-CURRENT-INPUT-REVIEW` | 15 | 115435 |
| `P02PRE-R1H-H2-COLLECTOR` | 25 | 225398 |
| `P02PRE-R1H-H2-RUN` | 17 | 89461 |
| `P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE` | 25 | 100085 |
| `P03-PACKAGED-SFX-ENTRY` | 11 | 787303 |
| `P04` | 38 | 351719 |
| `P08` | 8 | 933286 |
| `P09-AC3-DELETE-1` | 5 | 146342 |
| `P19` | 24 | 30164 |
| `P20-CLOSE-BOUND-1` | 1 | 19484 |
| `P22` | 69 | 713269 |
| `PROJECT-GOVERNANCE-20261012` | 2 | 85568 |
| `PROJECT-ORCHESTRATION-20261014` | 5 | 11027 |
| `PROJECT-ROADMAP-20261009` | 1 | 16185 |
| `PROJECT-ROADMAP-20261010` | 10 | 599003 |

## 分类计数

| 判定 | 文件数 | 字节 |
|---|---:|---:|
| 保留 | 194 | 1078667 |
| 建议入库 | 1280 | 31003277 |

建议清理（待用户授权）：0 个，0 字节。未确认同时满足无引用且有精确再生产命令或纯临时特征的文件，因此本轮不建议清理任何证据。

## 逐文件清单

| 文件 | 字节 | 判定 | 引用来源（文件:行） | 理由 |
|---|---:|---|---|---|
| `verification/codex-pause-checkpoint-20261010-1228.md` | 7065 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/codex-pause-checkpoint-20261010-update-restart.md` | 4171 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/antigravity-dispatch.json` | 10526 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/antigravity-dispatch.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02-DOC-PROVENANCE-1/provenance-investigation.md` | 8257 | 保留 | doc/tasks/P09-AC3-DELETE-HARDEN-1.md:61 (READY/在飞 Task) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/classify-resolution-closeout-20261013T2018Z-input.json` | 585 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:96 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/classify-resolution-closeout-20261013T2018Z-output.json` | 290 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:97 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/classify-resolution-closeout-20261013T2018Z.exit` | 1 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:98 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/codex-ac3-resolution-verify-20261013T2002Z.md` | 2227 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:99 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/codex-review-manifest-verify-20261013T2002Z.exit` | 1 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:100 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/codex-review-manifest-verify-20261013T2002Z.json` | 179 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:101 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/codex-review-manifest-verify-20261013T2002Z.stderr.txt` | 0 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:102 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/codex-selftest-ac3-branch-res-20261013T2002Z.command.txt` | 68 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:103 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/codex-selftest-ac3-branch-res-20261013T2002Z.env.txt` | 342 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:104 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/codex-selftest-ac3-branch-res-20261013T2002Z.exit` | 1 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:105 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/codex-selftest-ac3-branch-res-20261013T2002Z.stderr.txt` | 0 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:106 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/codex-selftest-ac3-branch-res-20261013T2002Z.stdout.txt` | 17135 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:107 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/convergence-post-dsh-codex-verify-20261013T2004Z-input.json` | 556 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:108 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/convergence-post-dsh-codex-verify-20261013T2004Z-output.json` | 1244 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:109 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/convergence-post-dsh-codex-verify-20261013T2004Z.exit` | 1 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:110 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-agent-preflight-20261013T1957Z.exit` | 1 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:111 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-agent-preflight-20261013T1957Z.json` | 2734 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:112 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-agent-preflight-20261013T1957Z.stderr.txt` | 0 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:113 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-preflight-attestation-basis.md` | 489 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:114 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-preflight-attestation.json` | 73 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:115 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-review-ac3-branch-p2-bounded-prompt.md` | 2833 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:116 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-review-ac3-branch-resolution-summary.md` | 2388 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:120 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-review-manifest-bounded-r1.json` | 918 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:121 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/evidence-manifest-ac3-branch-res-r1.json` | 5234 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:122 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/resource-preservation-manifest.json` | 8135 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:138 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-agent-preflight-20261014T0341.exit` | 1 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:123 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-agent-preflight-20261014T0341.json` | 2929 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:124 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-preflight-attestation.json` | 88 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:125 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-preflight-config.json` | 595 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:126 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-preflight-dry-run-20261014T0340.exit` | 1 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:127 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-preflight-dry-run-20261014T0340.json` | 2952 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:128 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-preflight-dry-run-20261014T0341.exit` | 1 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:129 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-preflight-dry-run-20261014T0341.json` | 3092 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:130 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-selftest-ac3-branch-res-20261013T1947Z.command.txt` | 89 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:131 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-selftest-ac3-branch-res-20261013T1947Z.env.txt` | 867 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:132 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-selftest-ac3-branch-res-20261013T1947Z.exit` | 2 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:133 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-selftest-ac3-branch-res-20261013T1947Z.stderr.txt` | 0 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:134 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-selftest-ac3-branch-res-20261013T1947Z.stdout.txt` | 17131 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:135 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-selftest-ac3-branch-res-20261013T1947Z.summary.md` | 5567 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md:136 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/codex-dsh-review-adjudication-r1.md` | 2908 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:115 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/codex-parent-integration-record-r1.md` | 980 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:121 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/codex-review-input-binding-r1.md` | 3198 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:106 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/codex-review-scope-diff-r1.patch` | 9308 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:107 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/codex-selftest-20261014T050945-environment.json` | 706 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:127 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/codex-selftest-20261014T050945-exit.txt` | 2 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:128 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/codex-selftest-20261014T050945-stderr.log` | 0 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:129 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/codex-selftest-20261014T050945-stdout.log` | 17695 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:130 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/codex-selftest-run-record-20261014T050945.md` | 1627 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:99 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/codex-verify-r1-20261014.md` | 3295 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:100 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/convergence-review-r1-input.json` | 373 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:118 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/convergence-review-r1-output.json` | 1264 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:119 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-bounded-review-evaluation-input-r1.json` | 118 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:110 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-bounded-review-evaluation-input-r2.json` | 116 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:117 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-bounded-review-evaluation-r1.json` | 336 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:105 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-bounded-review-evaluation-r2.json` | 376 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:116 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-bounded-review-followup-r1.md` | 2015 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:108 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-bounded-review-followup-result-r1.md` | 13964 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:113 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-bounded-review-followup-run-record-r1.md` | 2544 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:114 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-bounded-review-manifest-r1.json` | 5973 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:101 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-bounded-review-request-r1.md` | 2823 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:103 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-bounded-review-result-r1.md` | 7751 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:104 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-review-preflight-attestation-r1.json` | 228 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:131 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-review-preflight-attestation-r2.json` | 88 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:132 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-review-preflight-config-r1.json` | 201 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:133 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-review-preflight-config-r2.json` | 201 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:134 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-review-preflight-config-r3.json` | 264 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:135 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-review-preflight-r1-exit.txt` | 2 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:136 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-review-preflight-r1.json` | 0 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:137 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-review-preflight-r2-exit.txt` | 2 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:138 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-review-preflight-r2.json` | 2486 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:139 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-review-preflight-r3-exit.txt` | 3 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:140 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-review-preflight-r3.json` | 2455 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:102 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-review-preflight-r4-exit.txt` | 3 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:141 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-review-preflight-r4.json` | 2455 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:109 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-review-preflight-r5-exit.txt` | 3 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:142 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-review-preflight-r5.json` | 2455 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:112 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/path-correction-manifest-r1.json` | 4350 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:120 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/post-integration-selftest-fixture-inventory-r1.json` | 987 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:126 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/post-integration-selftest-r1.exit.txt` | 3 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:125 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/post-integration-selftest-r1.stderr.log` | 0 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:124 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/post-integration-selftest-r1.stdout.log` | 17489 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:123 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/post-integration-selftest-run-record-r1.md` | 1514 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:122 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/resource-closeout-inventory-r1.json` | 19199 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:143 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/revision-classification-E1-input.json` | 231 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:144 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/revision-classification-E1-output.json` | 377 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:145 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/revision-classification-I1-input.json` | 231 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:146 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/revision-classification-I1-output.json` | 269 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:147 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/revision-classification-T1-input.json` | 231 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:148 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/revision-classification-T1-output.json` | 268 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:149 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/selftest-20261014T0506+0800-stderr.log` | 0 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:150 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/selftest-20261014T0506+0800-stdout.log` | 17695 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:151 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/selftest-fixture-inventory-r1.json` | 1745 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:111 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/selftest-run-record-20261014T0506+0800.md` | 4577 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:98 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/zcode-preflight-attempt2-exit.txt` | 1 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:152 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/zcode-preflight-attempt2.json` | 2807 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:153 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/zcode-preflight-attestation.json` | 71 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:154 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/zcode-preflight-config.json` | 259 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:155 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/zcode-preflight-exit.txt` | 1 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:156 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/zcode-preflight.json` | 2679 | 保留 | doc/tasks/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.md:157 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02-NEW-TIME-BASELINE/codex-result-adjudication-20261014T0430CST-ac3fix.md` | 4612 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02-NEW-TIME-BASELINE/codex-source-review-adjudication-r2.md` | 2567 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02-NEW-TIME-BASELINE/codex-source-selftest-r2-environment.json` | 3143 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02-NEW-TIME-BASELINE/codex-source-selftest-r2-fixture-inventory.json` | 707 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02-NEW-TIME-BASELINE/codex-source-selftest-r2.command.txt` | 68 | 建议入库 | 无命中 | 命令、结果或辅助原始文本，保留独立复核材料。 |
| `verification/P02-NEW-TIME-BASELINE/codex-source-selftest-r2.exit.txt` | 3 | 建议入库 | 无命中 | 命令、结果或辅助原始文本，保留独立复核材料。 |
| `verification/P02-NEW-TIME-BASELINE/codex-source-selftest-r2.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02-NEW-TIME-BASELINE/codex-source-selftest-r2.stdout.log` | 17405 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02-NEW-TIME-BASELINE/codex-source-verify-r2.md` | 2118 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02-NEW-TIME-BASELINE/convergence-ac3-helper-shape-review-decision.json` | 1520 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02-NEW-TIME-BASELINE/convergence-ac3-helper-shape-review-input.json` | 801 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02-NEW-TIME-BASELINE/convergence-ac3-helper-shape-review-output.json` | 1471 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02-NEW-TIME-BASELINE/convergence-source-review-r2-input.json` | 620 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02-NEW-TIME-BASELINE/convergence-source-review-r2-output.json` | 1490 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02-NEW-TIME-BASELINE/convergence-source-review-r2.exit.txt` | 3 | 建议入库 | 无命中 | 命令、结果或辅助原始文本，保留独立复核材料。 |
| `verification/P02-NEW-TIME-BASELINE/dsh-result-review-manifest-20261014T0430CST-ac3fix.json` | 1251 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02-NEW-TIME-BASELINE/dsh-result-review-result-20261014T0430CST-ac3fix.md` | 18837 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02-NEW-TIME-BASELINE/dsh-review-preflight-r2-attestation.json` | 90 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02-NEW-TIME-BASELINE/dsh-review-preflight-r2-config.json` | 620 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02-NEW-TIME-BASELINE/dsh-review-preflight-r2.exit.txt` | 3 | 建议入库 | 无命中 | 命令、结果或辅助原始文本，保留独立复核材料。 |
| `verification/P02-NEW-TIME-BASELINE/dsh-review-preflight-r2.json` | 2610 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02-NEW-TIME-BASELINE/dsh-review-preflight-r2.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02-NEW-TIME-BASELINE/dsh-source-review-evidence-manifest-r2.json` | 6746 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02-NEW-TIME-BASELINE/dsh-source-review-manifest-r2.json` | 896 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02-NEW-TIME-BASELINE/dsh-source-review-r2.exit.txt` | 3 | 建议入库 | 无命中 | 命令、结果或辅助原始文本，保留独立复核材料。 |
| `verification/P02-NEW-TIME-BASELINE/dsh-source-review-r2.md` | 10841 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02-NEW-TIME-BASELINE/dsh-source-review-r2.prompt.md` | 3013 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02-NEW-TIME-BASELINE/dsh-source-review-r2.run-record.md` | 1666 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02-NEW-TIME-BASELINE/freeze/baseline-20261014T0430CST-ac3fix.freeze.json` | 3728 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02-NEW-TIME-BASELINE/freeze/freeze-preflight-v2-baseline-20261014T0430CST-ac3fix.json` | 12643 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02-NEW-TIME-BASELINE/freeze/p02-task-pre-run-20261014T0430CST-ac3fix.md` | 11391 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02-NEW-TIME-BASELINE/freeze/p02-task-review-head-83588bb.md` | 11636 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02-NEW-TIME-BASELINE/run-baseline-20261014T0430CST-ac3fix.json` | 24207 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/agy-p02pre-r1g-connectivity-probe-20261012.json` | 798 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/agy-p02pre-r1h-connectivity-probe-20261012.json` | 432 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/agy-p02pre-r1h-connectivity-probe-adjudication-20261012.md` | 677 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-cli-version-20261012.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-cli-version-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-cli-version-20261012.stdout.log` | 6 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-dispatch-20261012.md` | 8972 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-formal-20261012.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-formal-20261012.meta.json` | 12560 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-formal-20261012.prompt.md` | 4501 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-formal-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-formal-20261012.stdout.json` | 11999 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-formal-response-20261012.md` | 11457 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-migrate-20261012.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-migrate-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-migrate-20261012.stdout.log` | 154 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-revision2-20261012.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-revision2-20261012.meta.json` | 985 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-revision2-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-revision2-20261012.stdout.json` | 12977 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-revision2-migrate-20261012.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-revision2-migrate-20261012.stderr.log` | 849 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-revision2-migrate-20261012.stdout.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-revision2-prompt-20261012.md` | 4416 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-revision2-response-20261012.md` | 12443 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-smoke-20261012.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-smoke-20261012.meta.json` | 781 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-smoke-20261012.prompt.md` | 27 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-smoke-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/agy-p02pre-r1h-exec-a6-smoke-20261012.stdout.json` | 262 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/agy-p02pre-r1h-r6-exec-a6-input-manifest-20261012.json` | 7332 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/agy-p02pre-r1h-r6-exec-a6-input-manifest-r2-20261012.json` | 8493 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/agy-p02pre-r1h-r6-exec-a6-prompt-20261012.md` | 4501 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/agy-p02pre-r1h-r6-exec-a6-task-contract-20261012.md` | 3553 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/antigravity-owner-implementation-r1.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/antigravity-owner-implementation-r1.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/antigravity-owner-implementation-r1.stdout.jsonl` | 8262 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r2-correct-invocation.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r2-correct-invocation.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r2-correct-invocation.stdout.json` | 11211 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r2.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r2.prompt.md` | 8706 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r2.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r2.stdout.json` | 1312 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r3.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r3.prompt.md` | 6342 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r3.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r3.stdout.json` | 10090 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r4.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r4.prompt.md` | 7800 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r4.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r4.stdout.json` | 10782 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r5.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r5.prompt.md` | 5111 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r5.response.md` | 15250 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r5.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r5.stdout.json` | 15559 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r6.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r6.prompt.md` | 4907 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r6.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r6.stdout.json` | 11835 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r7.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r7.prompt.md` | 4161 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r7.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/antigravity-owner-stage-a-corrections-r7.stdout.json` | 14920 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/antigravity-p02pre-r1g-argumentlist-fix-20261012.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/antigravity-p02pre-r1g-argumentlist-fix-20261012.prompt.md` | 4698 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/antigravity-p02pre-r1g-argumentlist-fix-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/antigravity-p02pre-r1g-argumentlist-fix-20261012.stdout.json` | 11629 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/antigravity-p02pre-r1g-implementation-20261012.exit` | 5 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/antigravity-p02pre-r1g-implementation-20261012.exit-canonical-bytes-20261012.bin` | 3 | 建议入库 | 无命中 | 原始二进制产物；没有已核实的无损再生产命令。 |
| `verification/P02/antigravity-p02pre-r1g-implementation-20261012.exit-codex-observed.txt` | 5 | 建议入库 | 无命中 | 命令、结果或辅助原始文本，保留独立复核材料。 |
| `verification/P02/antigravity-p02pre-r1g-implementation-20261012.prompt.md` | 4376 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/antigravity-p02pre-r1g-implementation-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/antigravity-p02pre-r1g-implementation-20261012.stdout.json` | 9327 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/antigravity-p02pre-r1g-review-fixes-20261012.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/antigravity-p02pre-r1g-review-fixes-20261012.prompt.md` | 3559 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/antigravity-p02pre-r1g-review-fixes-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/antigravity-p02pre-r1g-review-fixes-20261012.stdout.json` | 10640 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/antigravity-p02pre-r1g-review-fixes2-20261012.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/antigravity-p02pre-r1g-review-fixes2-20261012.prompt.md` | 2579 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/antigravity-p02pre-r1g-review-fixes2-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/antigravity-p02pre-r1g-review-fixes2-20261012.stdout.json` | 9148 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/antigravity-p02pre-r1g-review-fixes3-20261012.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/antigravity-p02pre-r1g-review-fixes3-20261012.prompt.md` | 3495 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/antigravity-p02pre-r1g-review-fixes3-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/antigravity-p02pre-r1g-review-fixes3-20261012.stdout.json` | 13503 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/antigravity-p02pre-r1h-implementation-20261012.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/antigravity-p02pre-r1h-implementation-20261012.prompt.md` | 3434 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/antigravity-p02pre-r1h-implementation-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/antigravity-p02pre-r1h-implementation-20261012.stdout.json` | 7752 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/antigravity-p02pre-r1h-remediation-20261012.prompt.md` | 5353 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/antigravity-p02pre-r1h-remediation-followup-20261012.exit` | 25 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/antigravity-p02pre-r1h-remediation-followup-20261012.prompt.md` | 5249 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/antigravity-p02pre-r1h-remediation-followup-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/antigravity-p02pre-r1h-remediation-followup-20261012.stdout.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/antigravity-p02pre-r1h-round6-attempt4-20261012.exit` | 197 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/antigravity-p02pre-r1h-round6-attempt4-20261012.prompt.md` | 6553 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/antigravity-p02pre-r1h-round6-attempt4-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/antigravity-p02pre-r1h-round6-attempt4-20261012.stdout.jsonl` | 9236 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/antigravity-p02pre-r1h-round6-attempt4-followup1-20261012.exit` | 254 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/antigravity-p02pre-r1h-round6-attempt4-followup1-20261012.prompt.md` | 3080 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/antigravity-p02pre-r1h-round6-attempt4-followup1-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/antigravity-p02pre-r1h-round6-attempt4-followup1-20261012.stdout.jsonl` | 8616 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/appcontainer-isolation-candidate-r1.md` | 5880 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/appcontainer-isolation-contract-r2.md` | 16710 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/appcontainer-isolation-contract-r3.md` | 21506 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/appcontainer-isolation-contract-r4.md` | 27206 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/appcontainer-isolation-contract-r5.md` | 30789 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/appcontainer-isolation-contract-r6.md` | 31957 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/appcontainer-isolation-contract-r7.md` | 32969 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/appcontainer-readonly-preflight-r1.md` | 6163 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/appcontainer-readonly-preflight-r2.md` | 5376 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/appcontainer-readonly-preflight-r3.md` | 6339 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/build-preflight-lf-r1.md` | 2156 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-appcontainer-contract-r2-adjudication.md` | 5061 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-appcontainer-contract-r3-adjudication.md` | 7723 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-appcontainer-contract-r4-adjudication.md` | 4353 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-appcontainer-contract-r5-adjudication.md` | 4038 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-appcontainer-contract-r6-adjudication.md` | 5095 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-appcontainer-contract-r7-adjudication.md` | 7016 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-appcontainer-create-gate-alternative-20261010.md` | 7344 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-appcontainer-create-gate-alternative-adjudication-20261010.md` | 3859 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-appcontainer-create-gate-alternative-review-20261010.md` | 9417 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-autonomous-orchestration-refresh-review-20261010.md` | 13855 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-after-r3-review.md` | 5081 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-after-r4-dsh-review.md` | 4930 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-after-r5-dsh-review.md` | 5199 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-autonomous-orchestration-20261010.md` | 87094 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-before-r4-dsh-review.md` | 5106 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02-m7-m8-review-m9-20261010.md` | 6358 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02-manifest-r6-reconciliation-20261011.md` | 14766 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02-owner-risk-waiver-manifest-review-r1-20261010.md` | 5905 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02-owner-risk-waiver-manifest-review-r3-20261010.md` | 6552 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02-owner-risk-waiver-start-20261010.md` | 6132 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02-profile-folder-contract-m6-20261010.md` | 6630 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02-profile-folder-versioned-contract-m7-20261010.md` | 7168 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02-readonly-preflight-r0-20261011.md` | 13189 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02-readonly-preflight-r0s1-20261011.md` | 7583 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r0s3-20261011.md` | 5553 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r0s4-20261011.md` | 8662 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r0s5-20261011.md` | 4308 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1-20261011.md` | 7208 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1f-20261011.md` | 57630 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1f-postrun-20261011.md` | 12560 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1g-20261012.md` | 29023 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-integration-protocol-review-active-20261012.md` | 5823 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-integration-protocol-review-r2-active-20261012.md` | 29602 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-owner-remediation-round3-active-20261012.md` | 6015 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-owner-remediation-round4-active-20261012.md` | 5873 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-remediation5-review-active-20261012.md` | 5967 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-review-dispatched-20261012.md` | 5975 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-review-remediation-dispatched-20261012.md` | 8033 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-review-round2-dispatched-20261012.md` | 9635 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-review-round3-active-20261012.md` | 6279 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-review-round4-active-20261012.md` | 6018 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-round4-review-active-20261012.md` | 5445 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-round6-attempt4-baseline-blocked-20261012.md` | 5739 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-round6-attempt4-owner-active-20261012.md` | 7922 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-round6-attempt5-parser-pass-20261012.md` | 5428 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-round6-attempt5-review-findings-20261012.md` | 5938 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-round6-attempt6-antigravity-dispatch-20261012.md` | 5333 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-round6-attempt6-parser-pass-20261012.md` | 8696 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-round6-attempt6-r2-review-adjudicated-20261012.md` | 7031 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-round6-attempt6-review-20261012.md` | 6252 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-round6-attempt6-revision2-dispatch-20261012.md` | 5916 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-round6-attempt6-revision2-review-20261012.md` | 6442 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-round6-attempt6-zcode-dispatch-20261012.md` | 13895 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-round6-attempt6-zcode-handoff-20261012.md` | 14481 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-round6-executor-remediation-active-20261012.md` | 3797 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-round6-integration-protocol-review-active-20261012.md` | 6170 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-round6-integration-protocol-review-attempt2-active-20261012.md` | 7222 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-round6-integration-protocol-review-attempt3-active-20261012.md` | 4957 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-round6-owner-active-20261012.md` | 4941 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-round6-refreeze-active-20261012.md` | 4933 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-round6-review-active-20261012.md` | 5506 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-checkpoint-p02pre-r1h-round6-review-r3-freeze-active-20261012.md` | 7656 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-elevated-isolation-assessment-r2-adjudication-20261010.md` | 3459 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-elevated-isolation-method-assessment-20261010-r1.md` | 19484 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-elevated-isolation-method-assessment-20261010-r2.md` | 19618 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-elevated-isolation-method-assessment-review-20261010-r1.md` | 13068 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-elevated-isolation-method-assessment-review-20261010-r2.md` | 6859 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-execution-manifest-design-advice-20261010.md` | 26212 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-human-required-decision-20261010.md` | 11173 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-identity-derive-evidence-20261010.md` | 1779 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-isolation-architecture-assessment-20261010.md` | 11261 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-isolation-method-expert-assessment-20261010.md` | 5563 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-noncreating-registry-absence-adjudication-20261010.md` | 4018 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-noncreating-registry-absence-options-20261010.md` | 23759 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-noncreating-registry-absence-options-review-20261010.md` | 10971 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-owner-risk-waiver-manifest-r1-adjudication-20261010.md` | 5624 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-owner-risk-waiver-manifest-r3-adjudication-20261010.md` | 5393 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-owner-risk-waiver-manifest-r4-adjudication-20261010.md` | 3994 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-owner-risk-waiver-manifest-r5-adjudication-20261010.md` | 4279 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-owner-risk-waiver-manifest-r6-adjudication-20261011.md` | 5560 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-profile-folder-noncreating-contract-adjudication-20261010.md` | 4047 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-profile-folder-noncreating-contract-assessment-20261010.md` | 6053 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-profile-folder-noncreating-contract-assessment-review-20261010.md` | 7776 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-profile-folder-versioned-contract-adjudication-20261010.md` | 3985 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-profile-folder-versioned-contract-research-20261010.md` | 23075 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-profile-folder-versioned-contract-research-review-20261010.md` | 10860 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-unwaived-gate-feasibility-20261011.md` | 27825 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-unwaived-gate-feasibility-adjudication-20261011.md` | 4101 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-unwaived-gate-feasibility-review-20261011.md` | 5857 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-versioned-registry-absence-adjudication-20261010.md` | 5643 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-versioned-registry-absence-contract-20261010.md` | 23403 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-versioned-registry-absence-contract-review-20261010.md` | 13306 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-wer-per-image-bootstrap-adjudication-20261010.md` | 3127 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-wer-per-image-bootstrap-contract-research-20261010.md` | 17105 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-wer-per-image-bootstrap-contract-research-review-20261010.md` | 13059 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-zero-capability-registry-getter-adjudication-20261010.md` | 4259 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-zero-capability-registry-getter-contract-research-20261010.md` | 15483 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02-zero-capability-registry-getter-contract-research-review-20261010.md` | 14456 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r0-adjudication-20261011.md` | 11145 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r0s1-adjudication-20261011.md` | 9413 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r0s2-adjudication-20261011.md` | 8604 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r0s3-adjudication-20261011.md` | 6798 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r0s3-classification-20261011.md` | 15370 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r0s3-runtime-20261011.json` | 309 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r0s3-verification-20261011.md` | 6575 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r0s4-adjudication-20261011.md` | 8669 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r0s4-delivery-20261011.md` | 6368 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r0s4-verification-20261011.md` | 7455 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r0s5-adjudication-20261011.md` | 6611 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r0s5-delivery-20261011.md` | 6889 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r0s5-verification-20261011.md` | 6680 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1g-postrun-review-input-pins-post-20261012.json` | 3431 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1g-postrun-review-input-pins-pre-20261012.json` | 2751 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1g-review-input-pins-fallback-20261012.json` | 4587 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1g-review-input-pins-fallback-post-20261012.json` | 4411 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1g-review-input-pins-followup1-20261012.json` | 4679 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1g-review-input-pins-followup1-post-20261012.json` | 11289 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1g-review-input-pins-followup3-20261012.json` | 5171 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1g-review-input-pins-followup3-correction-20261012.json` | 1597 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1g-review-input-pins-followup3-post-20261012.json` | 3547 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1g-review-input-pins-remediation-20261012.json` | 4796 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-antigravity-followup-dispatch-pins-20261012.json` | 3827 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-attempt4-integration-verify-20261012.json` | 4400 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-attempt4-owner-delivery-pins-20261012.json` | 6890 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-attempt4-review-postpins-20261012.json` | 9226 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-attempt4-review-prepins-20261012.json` | 6568 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-attempt5-exec-postpins-20261012.json` | 6018 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-attempt5-exec-review-20261012.prompt.md` | 2621 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-attempt5-exec-review-followup1-20261012.prompt.md` | 2362 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-attempt5-exec-review-followup1-pins-20261012.json` | 4598 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-attempt5-exec-review-followup1-postpins-20261012.json` | 6807 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-attempt5-exec-review-followup2-20261012.prompt.md` | 3403 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-attempt5-exec-review-followup2-pins-20261012.json` | 6563 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-attempt5-exec-review-followup2-postpins-20261012.json` | 9547 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-attempt5-exec-review-pins-20261012.json` | 3045 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-attempt5-final-pre-run-20261012.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/codex-p02pre-r1h-attempt5-final-pre-run-20261012.json` | 17299 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-attempt5-final-pre-run-20261012.stderr.log` | 514 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/codex-p02pre-r1h-attempt5-final-pre-run-20261012.stdout.log` | 3695 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/codex-p02pre-r1h-attempt5-integration-verify-20261012.json` | 9566 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-attempt5-prerun-review-adjudication-20261012.md` | 5166 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-attempt5-prerun-review-pins-20261012.json` | 2485 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-attempt6-final-pre-run-20261012.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/codex-p02pre-r1h-attempt6-final-pre-run-20261012.json` | 12984 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-attempt6-final-pre-run-20261012.stderr.log` | 1237 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/codex-p02pre-r1h-attempt6-final-pre-run-20261012.stdout.log` | 3704 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/codex-p02pre-r1h-attempt6-final-pre-run-v2-20261012.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/codex-p02pre-r1h-attempt6-final-pre-run-v2-20261012.json` | 15768 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-attempt6-final-pre-run-v2-20261012.stderr.log` | 532 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/codex-p02pre-r1h-attempt6-final-pre-run-v2-20261012.stdout.log` | 82455 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/codex-p02pre-r1h-attempt6-input-verification-r2-20261012.json` | 12044 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-attempt6-integration-verify-20261012.json` | 19023 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-attempt6-output-target-precheck-20261012.json` | 4389 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-attempt6-r2-dsh-method-audit-20261012.json` | 1430 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-attempt6-r2-review-adjudication-20261012.md` | 6461 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-attempt6-r2-review-input-manifest-20261012.json` | 11617 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-attempt6-r2-review-input-verification-20261012.json` | 15217 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-attempt6-r2-review-post-verification-20261012.json` | 16653 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-attempt6-review-adjudication-20261012.md` | 6533 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-attempt6-review-input-verification-20261012.json` | 11559 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-attempt6-zcode-h1-review-adjudication-20261012.md` | 7665 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-attempt6-zcode-h1-review-input-verification-20261012.json` | 14002 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-codex-owner-dispatch-pins-20261012.json` | 3772 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-dispatch-input-pins-20261012.json` | 863 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-integration-protocol-dispatch-round6-20261012.prompt.md` | 3178 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-integration-protocol-dispatch-round6-attempt2-20261012.prompt.md` | 4990 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-integration-protocol-dispatch-round6-attempt3-20261012.prompt.md` | 5589 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-integration-protocol-pins-round6-20261012.json` | 8712 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-integration-protocol-pins-round6-attempt2-20261012.json` | 12457 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-integration-protocol-pins-round6-attempt3-20261012.json` | 13357 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-integration-protocol-remediation5-review-dispatch-20261012.prompt.md` | 2854 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-integration-protocol-remediation5-review-pins-20261012.json` | 3793 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-integration-protocol-review-r2-dispatch-20261012.prompt.md` | 4601 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-integration-protocol-review-r2-pins-20261012.json` | 5990 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-owner-remediation-20261012.prompt.md` | 5740 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-owner-remediation-round2-20261012.prompt.md` | 3777 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-owner-remediation-round2-pins-20261012.json` | 3010 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-owner-remediation-round3-20261012.pins.json` | 3440 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-owner-remediation-round3-20261012.prompt.md` | 3975 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-owner-remediation-round4-20261012.pins.json` | 2915 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-owner-remediation-round4-20261012.prompt.md` | 3793 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-owner-remediation-round5-20261012.prompt.md` | 3394 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-owner-remediation-round5-pins-20261012.json` | 2371 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-remediation-dispatch-pins-20261012.json` | 1547 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-remediation-review-dispatch-20261012.prompt.md` | 3282 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-remediation-review-input-pins-20261012.json` | 3120 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-remediation2-review-dispatch-20261012.prompt.md` | 4166 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-remediation2-review-input-pins-20261012.json` | 3866 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-remediation3-review-dispatch-20261012.prompt.md` | 3918 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-remediation3-review-input-pins-20261012.json` | 3599 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-remediation4-review-dispatch-20261012.prompt.md` | 3866 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-remediation4-review-input-pins-20261012.json` | 3952 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-remediation5-review-dispatch-20261012.prompt.md` | 2711 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-remediation5-review-dispatch-r2-20261012.prompt.md` | 3368 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-remediation5-review-input-pins-20261012.json` | 2900 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-remediation5-review-input-pins-r2-20261012.json` | 3941 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-review-followup-pin-reconciliation-20261012.json` | 4052 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-review-followup-pin-reconciliation-20261012.prompt.md` | 2446 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-review-input-pins-post-20261012.json` | 2070 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-review-input-pins-pre-20261012.json` | 1774 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-round6-review-dispatch-20261012.prompt.md` | 2105 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-round6-review-dispatch-r2-20261012.prompt.md` | 2228 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-round6-review-dispatch-r3-20261012.prompt.md` | 2450 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-p02pre-r1h-round6-review-pins-20261012.json` | 2613 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-round6-review-pins-r2-20261012.json` | 4 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-round6-review-pins-r3-20261012.json` | 4198 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-p02pre-r1h-zcode-remediation-dispatch-pins-20261012.json` | 4620 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/codex-phase-a-method-blockers-20261010-r10.md` | 11825 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-phase-a-method-blockers-20261010-r2.md` | 6961 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-phase-a-method-blockers-20261010-r3.md` | 9033 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-phase-a-method-blockers-20261010-r4.md` | 9987 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-phase-a-method-blockers-20261010-r5.md` | 10401 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-phase-a-method-blockers-20261010-r6.md` | 11135 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-phase-a-method-blockers-20261010-r7.md` | 11808 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-phase-a-method-blockers-20261010-r8.md` | 11700 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-phase-a-method-blockers-20261010-r9.md` | 11824 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-phase-a-method-blockers-20261010.md` | 5629 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-phase-a-method-blockers-review-r1-adjudication.md` | 6058 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-phase-a-method-blockers-review-r10-attempt1-adjudication.md` | 2941 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-phase-a-method-blockers-review-r10-attempt2-adjudication.md` | 2866 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-phase-a-method-blockers-review-r2-adjudication.md` | 5167 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-phase-a-method-blockers-review-r3-attempt2-adjudication.md` | 4097 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-phase-a-method-blockers-review-r3-attempt3-adjudication.md` | 3125 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-phase-a-method-blockers-review-r4-attempt1-adjudication.md` | 3105 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-phase-a-method-blockers-review-r5-attempt1-adjudication.md` | 3464 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-phase-a-method-blockers-review-r6-attempt1-adjudication.md` | 4143 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-phase-a-method-blockers-review-r7-attempt1-adjudication.md` | 3874 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-phase-a-method-blockers-review-r8-attempt1-adjudication.md` | 3348 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-phase-a-method-blockers-review-r9-attempt1-adjudication.md` | 3471 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1g-evidence-docs-review-20261012.md` | 2454 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1g-postrun-review-20261012.md` | 2788 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1g-postrun-review-20261012.prompt.md` | 4089 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1g-review-followup2-20261012.md` | 6016 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1g-review-followup3-20261012.md` | 3900 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1g-review-followup3-20261012.prompt.md` | 3294 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1h-attempt4-review-20261012.md` | 15285 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1h-attempt5-exec-review-20261012.md` | 11387 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1h-attempt5-exec-review-followup1-20261012.md` | 19583 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1h-attempt5-exec-review-followup2-20261012.md` | 19994 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1h-attempt5-prerun-review-20261012.md` | 5074 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1h-baseline-feasibility-advice-20261012.md` | 1906 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1h-integration-protocol-remediation5-review-20261012.md` | 8791 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1h-integration-protocol-review-r2-20261012.md` | 9375 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1h-integration-protocol-review-round6-20261012.md` | 8463 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1h-integration-protocol-review-round6-attempt2-20261012.md` | 8278 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1h-integration-protocol-review-round6-attempt3-20261012.md` | 27576 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1h-static-review-20261012.md` | 2308 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1h-static-review-remediation-20261012.md` | 7949 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1h-static-review-remediation-pin-addendum-20261012.md` | 5003 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1h-static-review-remediation2-20261012.md` | 8812 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1h-static-review-remediation3-20261012.md` | 9545 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1h-static-review-remediation4-20261012.md` | 8769 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1h-static-review-remediation5-20261012.md` | 8235 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1h-static-review-round6-20261012.md` | 7100 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/codex-subagent-p02pre-r1h-static-review-round6-r2-20261012.md` | 7200 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-appcontainer-contract-r2-review.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-appcontainer-contract-r2-review.prompt.md` | 4154 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-appcontainer-contract-r2-review.stderr.log` | 229680 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-appcontainer-contract-r2-review.stdout.md` | 52641 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-appcontainer-contract-r3-review-attempt2.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-appcontainer-contract-r3-review-attempt2.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-appcontainer-contract-r3-review-attempt2.stdout.jsonl` | 110580 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-appcontainer-contract-r3-review.prompt.md` | 3659 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-appcontainer-contract-r3-review.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-appcontainer-contract-r3-review.stdout.jsonl` | 18647 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-appcontainer-contract-r3-review.stdout.md` | 37918 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-appcontainer-contract-r4-dispatch-attempt1.log` | 513 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-appcontainer-contract-r4-review.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-appcontainer-contract-r4-review.prompt.md` | 3376 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-appcontainer-contract-r4-review.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-appcontainer-contract-r4-review.stdout.jsonl` | 213923 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-appcontainer-contract-r4-review.stdout.md` | 37351 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-appcontainer-contract-r5-review.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-appcontainer-contract-r5-review.prompt.md` | 3475 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-appcontainer-contract-r5-review.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-appcontainer-contract-r5-review.stdout.jsonl` | 125277 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-appcontainer-contract-r5-review.stdout.md` | 24338 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-appcontainer-contract-r6-review.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-appcontainer-contract-r6-review.prompt.md` | 3397 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-appcontainer-contract-r6-review.stderr.log` | 21106 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-appcontainer-contract-r6-review.stdout.jsonl` | 26109 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-appcontainer-contract-r6-review.stdout.md` | 26109 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-appcontainer-contract-r7-review.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-appcontainer-contract-r7-review.prompt.md` | 3813 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-appcontainer-contract-r7-review.stderr.log` | 102566 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-appcontainer-contract-r7-review.stdout.md` | 24532 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-appcontainer-design-r1-resume.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-appcontainer-design-r1-resume.prompt.md` | 1030 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-appcontainer-design-r1-resume.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-appcontainer-design-r1-resume.stdout.jsonl` | 63119 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-appcontainer-design-r1.prompt.md` | 1904 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-appcontainer-design-r1.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-appcontainer-design-r1.stdout.jsonl` | 78405 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-appcontainer-design-r1.stdout.md` | 30492 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0-review-20261011.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r0-review-20261011.mount.log` | 1279 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r0-review-20261011.prompt.md` | 5202 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0-review-20261011.stderr.log` | 408 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r0-review-20261011.stdout.md` | 29404 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s1-review-20261011.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r0s1-review-20261011.mount.log` | 315 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r0s1-review-20261011.prompt.md` | 3904 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s1-review-20261011.stderr.log` | 100149 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r0s1-review-20261011.stdout.md` | 21262 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s2-manifest-review-20261011.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r0s2-manifest-review-20261011.mount.log` | 300 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r0s2-manifest-review-20261011.prompt.md` | 2320 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s2-manifest-review-20261011.stderr.log` | 101893 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r0s2-manifest-review-20261011.stdout.md` | 19235 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s3-review-20261011.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r0s3-review-20261011.md` | 21146 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s3-review-20261011.prompt.md` | 2404 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s3-review-20261011.stderr.log` | 136179 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r0s3-review-20261011.stdout.md` | 16114 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s3-review-round1-20261011.md` | 16114 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s3-review-round2-20261011.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r0s3-review-round2-20261011.mount.log` | 338 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r0s3-review-round2-20261011.prompt.md` | 4270 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s3-review-round2-20261011.stderr.log` | 83014 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r0s3-review-round2-20261011.stdout.md` | 21146 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s4-review-20261011.md` | 31986 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s4-review-20261011.prompt.md` | 2850 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s4-review-r2-20261011.md` | 30529 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s4-review-r2-20261011.prompt.md` | 3500 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s5-review-20261011.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r0s5-review-20261011.md` | 17644 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s5-review-20261011.prompt.md` | 2057 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s5-review-20261011.stderr.log` | 34165 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r0s5-review-20261011.stdout.md` | 4759 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s5-review-r2-20261011.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r0s5-review-r2-20261011.md` | 14531 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s5-review-r2-20261011.prompt.md` | 3344 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s5-review-r2-20261011.stdout.md` | 3839 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s5-review-r3-20261011.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r0s5-review-r3-20261011.md` | 10056 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s5-review-r3-20261011.prompt.md` | 2801 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s5-review-r3-20261011.stdout.md` | 4967 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s6-review-20261011.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r0s6-review-20261011.md` | 29306 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s6-review-20261011.prompt.md` | 4358 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s6-review-20261011.stderr.log` | 108258 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r0s6-review-r2-20261011.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r0s6-review-r2-20261011.prompt.md` | 2058 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r0s6-review-r2-20261011.stdout.md` | 2677 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1-evidence-review-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1-evidence-review-20261011.md` | 15299 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1-evidence-review-20261011.prompt.md` | 3610 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1-evidence-review-20261011.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1-evidence-review-20261011.stdout.jsonl` | 103356 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-p02pre-r1-review-20261011.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1-review-20261011.md` | 16668 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1-review-20261011.prompt.md` | 3047 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1-review-20261011.stderr.log` | 404 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1-review-20261011.stdout.jsonl` | 145807 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-p02pre-r1-review-r2-20261011.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1-review-r2-20261011.md` | 18951 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1-review-r2-20261011.prompt.md` | 6100 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1-review-r2-20261011.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1-review-r2-20261011.stdout.jsonl` | 94518 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-p02pre-r1-review-r3-20261011.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1-review-r3-20261011.md` | 17502 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1-review-r3-20261011.prompt.md` | 5865 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1-review-r3-20261011.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1-review-r3-20261011.stdout.jsonl` | 75672 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-p02pre-r1-review-r4-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1-review-r4-20261011.md` | 18995 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1-review-r4-20261011.prompt.md` | 5859 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1-review-r4-20261011.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1-review-r4-20261011.stdout.jsonl` | 82278 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-p02pre-r1-review-r4-followup-2-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1-review-r4-followup-2-20261011.md` | 6572 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1-review-r4-followup-2-20261011.prompt.md` | 3626 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1-review-r4-followup-2-20261011.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1-review-r4-followup-2-20261011.stdout.jsonl` | 27843 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-p02pre-r1-review-r4-followup-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1-review-r4-followup-20261011.md` | 15629 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1-review-r4-followup-20261011.prompt.md` | 3326 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1-review-r4-followup-20261011.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1-review-r4-followup-20261011.stdout.jsonl` | 53111 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-p02pre-r1-review-r4-followup-3-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1-review-r4-followup-3-20261011.md` | 9399 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1-review-r4-followup-3-20261011.prompt.md` | 3404 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1-review-r4-followup-3-20261011.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1-review-r4-followup-3-20261011.stdout.jsonl` | 45496 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-p02pre-r1f-postrun-review-20261011.exit` | 5 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-postrun-review-20261011.prompt.md` | 5083 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-postrun-review-20261011.stderr.log` | 117811 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-postrun-review-20261011.stdout.md` | 0 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-postrun-review-followup1-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-postrun-review-followup1-20261011.prompt.md` | 1182 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-postrun-review-followup1-20261011.stderr.log` | 11955 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-postrun-review-followup1-20261011.stdout.md` | 7704 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-postrun-review-followup2-docs-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-postrun-review-followup2-docs-20261011.prompt.md` | 6173 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-postrun-review-followup2-docs-20261011.stderr.log` | 65860 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-postrun-review-followup2-docs-20261011.stdout.md` | 7526 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-postrun-review-followup3-docs-20261011.prompt.md` | 5051 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-postrun-review-followup4-docs-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-postrun-review-followup4-docs-20261011.prompt.md` | 5429 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-postrun-review-followup4-docs-20261011.stderr.log` | 105348 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-postrun-review-followup4-docs-20261011.stdout.md` | 13010 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-20261011.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-20261011.prompt.md` | 3563 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-20261011.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-20261011.stdout.md` | 203071 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview-20261011.prompt.md` | 5802 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview-20261011.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview-20261011.stdout.md` | 127548 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview10-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview10-20261011.prompt.md` | 6341 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview10-20261011.stderr.log` | 40398 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview10-20261011.stdout.md` | 9642 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview2-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview2-20261011.prompt.md` | 5726 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview2-20261011.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview2-20261011.stdout.md` | 100209 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview3-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview3-20261011.prompt.md` | 7030 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview3-20261011.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview3-20261011.stdout.md` | 252709 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview4-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview4-20261011.prompt.md` | 7635 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview4-20261011.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview4-20261011.stdout.md` | 146345 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview5-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview5-20261011.prompt.md` | 5719 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview5-20261011.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview5-20261011.stdout.md` | 196904 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview6-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview6-20261011.prompt.md` | 5720 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview6-20261011.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview6-20261011.stdout.md` | 176354 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview6.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview7-20261011.exit` | 49 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview7-20261011.prompt.md` | 6332 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview7-20261011.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview7-20261011.stdout.md` | 0 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview8-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview8-20261011.prompt.md` | 7211 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview8-20261011.stderr.log` | 28870 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview8-20261011.stdout.md` | 11853 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview9-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview9-20261011.prompt.md` | 6989 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview9-20261011.stderr.log` | 61730 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview9-20261011.stdout.md` | 1269 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-review-20261011.md` | 67 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-20261011.prompt.md` | 5005 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-20261011.stderr.log` | 31453 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-review-20261011.stdout.jsonl` | 15791 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-p02pre-r1f-review-r2-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-review-r2-20261011.prompt.md` | 4007 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-r2-20261011.stderr.log` | 17462 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-review-r2-20261011.stdout.md` | 12501 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-r3-20261011.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-review-r3-20261011.prompt.md` | 4682 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-r3-20261011.stderr.log` | 6302 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-review-r3-20261011.stdout.md` | 9922 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-r4-20261011.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-review-r4-20261011.prompt.md` | 4117 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-r4-20261011.stderr.log` | 19833 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-review-r4-20261011.stdout.md` | 0 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-r4-followup-20261011.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-review-r4-followup-20261011.prompt.md` | 4191 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-r4-followup-20261011.stderr.log` | 2516 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-review-r4-followup-20261011.stdout.md` | 9395 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-r4-retry-20261011.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-review-r4-retry-20261011.prompt.md` | 3900 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-r4-retry-20261011.stderr.log` | 15811 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-review-r4-retry-20261011.stdout.md` | 11248 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-20261011.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-20261011.prompt.md` | 4024 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-20261011.stderr.log` | 110376 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-20261011.stdout.md` | 21403 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-followup-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-followup-20261011.prompt.md` | 4741 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-followup-20261011.stderr.log` | 160606 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-followup-20261011.stdout.md` | 16554 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-followup2-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-followup2-20261011.prompt.md` | 3640 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-followup2-20261011.stderr.log` | 156116 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-followup2-20261011.stdout.md` | 15009 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-followup3-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-followup3-20261011.prompt.md` | 3438 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-followup3-20261011.stderr.log` | 119856 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-followup3-20261011.stdout.md` | 14724 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-followup4-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-followup4-20261011.prompt.md` | 3946 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-followup4-20261011.stderr.log` | 118238 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-followup4-20261011.stdout.md` | 13169 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-followup5-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-followup5-20261011.prompt.md` | 4252 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-followup5-20261011.stderr.log` | 28012 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-followup5-20261011.stdout.md` | 17711 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-followup6-20261011.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-followup6-20261011.prompt.md` | 4712 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-followup6-20261011.stderr.log` | 143429 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1f-review-r5-followup6-20261011.stdout.md` | 16273 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1g-remediation-review-20261012.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1g-remediation-review-20261012.prompt.md` | 5115 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1g-remediation-review-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1g-remediation-review-20261012.stdout.jsonl` | 115873 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-p02pre-r1g-remediation-review-followup1-20261012.prompt.md` | 7237 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1g-remediation-review-followup1-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1g-remediation-review-followup1-20261012.stdout.jsonl` | 167850 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-p02pre-r1g-review-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1g-review-20261011.prompt.md` | 4788 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1g-review-20261011.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1g-review-20261011.stdout.md` | 304370 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1h-attempt4-review-20261012.exit` | 195 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1h-attempt4-review-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1h-attempt4-review-20261012.stdout.jsonl` | 179413 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-p02pre-r1h-attempt5-exec-review-20261012.exit` | 7 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1h-attempt5-exec-review-20261012.stderr.log` | 32423 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1h-attempt5-exec-review-20261012.stdout.jsonl` | 11387 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-p02pre-r1h-attempt5-exec-review-followup1-20261012.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1h-attempt5-exec-review-followup1-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1h-attempt5-exec-review-followup1-20261012.stdout.jsonl` | 217044 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-p02pre-r1h-attempt5-exec-review-followup2-20261012.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1h-attempt5-exec-review-followup2-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1h-attempt5-exec-review-followup2-20261012.stdout.jsonl` | 178908 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-p02pre-r1h-attempt5-prerun-review-20261012.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1h-attempt5-prerun-review-20261012.prompt.md` | 2598 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1h-attempt5-prerun-review-20261012.stderr.log` | 104275 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1h-attempt5-prerun-review-20261012.stdout.jsonl` | 14724 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-cli-version-20261012.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-cli-version-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-cli-version-20261012.stdout.log` | 11 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-r2-cli-version-20261012.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-r2-cli-version-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-r2-cli-version-20261012.stdout.log` | 12 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-r2-connectivity-smoke-20261012.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-r2-connectivity-smoke-20261012.prompt.md` | 27 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-r2-connectivity-smoke-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-r2-connectivity-smoke-20261012.stdout.jsonl` | 543 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-r2-connectivity-smoke-20261012.summary.json` | 278 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-revision2-mount-20261012.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-revision2-mount-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-revision2-mount-20261012.stdout.log` | 242 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-revision2-review-20261012.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-revision2-review-20261012.meta.json` | 3852 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-revision2-review-20261012.prompt.md` | 3928 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-revision2-review-20261012.response.md` | 24811 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-revision2-review-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-revision2-review-20261012.stdout.jsonl` | 422129 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-revision2-review-20261012.summary.json` | 2978 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-smoke-20261012.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-smoke-20261012.prompt.md` | 27 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-smoke-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-smoke-20261012.stdout.md` | 7 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-static-review-20261012.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-static-review-20261012.prompt.md` | 6725 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-static-review-20261012.stderr.log` | 52850 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-static-review-20261012.stdout.md` | 22977 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-static-review-mount-20261012.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-static-review-mount-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-static-review-mount-20261012.stdout.log` | 207 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-zcode-h1-final-pre-run-review-20261012.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-zcode-h1-final-pre-run-review-20261012.prompt.md` | 6107 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-zcode-h1-final-pre-run-review-20261012.response.md` | 14078 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-zcode-h1-final-pre-run-review-20261012.stderr.log` | 146983 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1h-attempt6-zcode-h1-final-pre-run-review-20261012.stdout.log` | 14078 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1h-code-review-20261012.prompt.md` | 3019 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-p02pre-r1h-connectivity-probe-20261012.json` | 503 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/dsh-p02pre-r1h-integration-protocol-review-round6-attempt3.exit` | 64 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-p02pre-r1h-integration-protocol-review-round6-attempt3.mount.log` | 446 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1h-integration-protocol-review-round6-attempt3.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-p02pre-r1h-integration-protocol-review-round6-attempt3.stdout.jsonl` | 213473 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/dsh-p02pre-r1h-round6-attempt4-review-20261012.prompt.md` | 5905 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r1.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r1.prompt.md` | 3543 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r1.stderr.log` | 108098 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r1.stdout.md` | 25062 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r10-attempt1.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r10-attempt1.prompt.md` | 5106 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r10-attempt1.stderr.log` | 37102 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r10-attempt1.stdout.md` | 10963 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r10-attempt2.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r10-attempt2.prompt.md` | 3885 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r10-attempt2.stderr.log` | 15846 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r10-attempt2.stdout.md` | 10262 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r2.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r2.prompt.md` | 3458 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r2.stderr.log` | 99885 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r2.stdout.md` | 17987 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r3-attempt2.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r3-attempt2.prompt.md` | 4095 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r3-attempt2.stderr.log` | 88239 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r3-attempt2.stdout.md` | 21109 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r3-attempt3.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r3-attempt3.prompt.md` | 4004 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r3-attempt3.stderr.log` | 76138 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r3-attempt3.stdout.md` | 11963 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r3.prompt.md` | 3472 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r3.stderr.log` | 33587 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r3.stdout.md` | 21689 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r4-attempt1.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r4-attempt1.mount.log` | 216 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r4-attempt1.prompt.md` | 3855 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r4-attempt1.stderr.log` | 21834 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r4-attempt1.stdout.md` | 9423 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r5-attempt1.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r5-attempt1.prompt.md` | 3911 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r5-attempt1.stderr.log` | 23318 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r5-attempt1.stdout.md` | 9042 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r6-attempt1.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r6-attempt1.mount.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r6-attempt1.mount.log` | 216 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r6-attempt1.prompt.md` | 4533 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r6-attempt1.stderr.log` | 25492 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r6-attempt1.stdout.md` | 11044 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r7-attempt1.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r7-attempt1.mount.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r7-attempt1.mount.log` | 216 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r7-attempt1.prompt.md` | 5037 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r7-attempt1.stderr.log` | 69155 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r7-attempt1.stdout.md` | 10501 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r8-attempt1.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r8-attempt1.prompt.md` | 4900 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r8-attempt1.stderr.log` | 57574 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r8-attempt1.stdout.md` | 10356 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r9-attempt1.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r9-attempt1.prompt.md` | 5218 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r9-attempt1.stderr.log` | 66493 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-phase-a-method-blockers-review-r9-attempt1.stdout.md` | 11572 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/dsh-review-channel-probe-20261012.exit.txt` | 3 | 建议入库 | 无命中 | 命令、结果或辅助原始文本，保留独立复核材料。 |
| `verification/P02/dsh-review-channel-probe-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/dsh-review-channel-probe-20261012.stdout.jsonl` | 496 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/implementation-stage-a-972049f9-diff-check.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/implementation-stage-a-972049f9-diff-check.log` | 34326 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/implementation-stage-a-972049f9-dsh-review-complete-followup-worktree.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/implementation-stage-a-972049f9-dsh-review-complete-followup-worktree.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/implementation-stage-a-972049f9-dsh-review-complete-followup-worktree.stdout.jsonl` | 54623 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/implementation-stage-a-972049f9-dsh-review-complete-followup.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/implementation-stage-a-972049f9-dsh-review-complete-followup.prompt.md` | 1185 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/implementation-stage-a-972049f9-dsh-review-complete-followup.stderr.log` | 171 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/implementation-stage-a-972049f9-dsh-review-complete-followup.stdout.jsonl` | 206 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/implementation-stage-a-972049f9-dsh-review-count-reconciliation.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/implementation-stage-a-972049f9-dsh-review-count-reconciliation.prompt.md` | 931 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/implementation-stage-a-972049f9-dsh-review-count-reconciliation.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/implementation-stage-a-972049f9-dsh-review-count-reconciliation.stdout.jsonl` | 18494 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/implementation-stage-a-972049f9-dsh-review.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/implementation-stage-a-972049f9-dsh-review.prompt.md` | 3645 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/implementation-stage-a-972049f9-dsh-review.stderr.log` | 185 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/implementation-stage-a-972049f9-dsh-review.stdout.jsonl` | 522871 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/implementation-stage-a-r2-dsh-review.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/implementation-stage-a-r2-dsh-review.prompt.md` | 3083 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/implementation-stage-a-r2-dsh-review.stderr.log` | 119027 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/implementation-stage-a-r2-dsh-review.stdout.jsonl` | 37394 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/implementation-stage-a-r3-dsh-review.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/implementation-stage-a-r3-dsh-review.prompt.md` | 3723 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/implementation-stage-a-r3-dsh-review.stderr.log` | 85751 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/implementation-stage-a-r3-dsh-review.stdout.md` | 32178 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/implementation-stage-a-r4-dsh-review-followup.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/implementation-stage-a-r4-dsh-review-followup.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/implementation-stage-a-r4-dsh-review-followup.stdout.jsonl` | 25366 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/implementation-stage-a-r4-dsh-review.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/implementation-stage-a-r4-dsh-review.md` | 8238 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/implementation-stage-a-r4-dsh-review.partial.md` | 8190 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/implementation-stage-a-r4-dsh-review.prompt.md` | 6415 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/implementation-stage-a-r4-dsh-review.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/implementation-stage-a-r4-dsh-review.stdout.jsonl` | 212414 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/implementation-stage-a-r5-dsh-review.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/implementation-stage-a-r5-dsh-review.md` | 10462 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/implementation-stage-a-r5-dsh-review.prompt.md` | 4217 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/implementation-stage-a-r5-dsh-review.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/implementation-stage-a-r5-dsh-review.stdout.jsonl` | 167620 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/implementation-stage-a-r6-dsh-review.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/implementation-stage-a-r6-dsh-review.prompt.md` | 5246 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/implementation-stage-a-r6-dsh-review.stderr.log` | 98 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/implementation-stage-a-r6-dsh-review.stdout.jsonl` | 11148 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/implementation-stage-a-r7-dsh-review.stderr.log` | 136 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/orchestration-p04-owner-git-status-20261010.txt` | 1384 | 建议入库 | 无命中 | 命令、结果或辅助原始文本，保留独立复核材料。 |
| `verification/P02/orchestration-root-git-status-20261010.txt` | 14713 | 建议入库 | 无命中 | 命令、结果或辅助原始文本，保留独立复核材料。 |
| `verification/P02/p02-owner-risk-waiver-execution-manifest-r1-20261010.md` | 19626 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02-owner-risk-waiver-execution-manifest-r1-review-20261010.md` | 13990 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02-owner-risk-waiver-execution-manifest-r2-20261010.md` | 23990 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02-owner-risk-waiver-execution-manifest-r2-review-20261010.md` | 12779 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02-owner-risk-waiver-execution-manifest-r3-20261010.md` | 26594 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02-owner-risk-waiver-execution-manifest-r3-review-20261010.md` | 11724 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02-owner-risk-waiver-execution-manifest-r4-20261010.md` | 28347 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02-owner-risk-waiver-execution-manifest-r4-review-20261010.md` | 11629 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02-owner-risk-waiver-execution-manifest-r5-20261010.md` | 28956 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02-owner-risk-waiver-execution-manifest-r5-review-20261010.md` | 12410 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md` | 44307 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-review-20261011.md` | 23380 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02-readonly-preflight-r0-evidence-20261011.md` | 99592 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02-readonly-preflight-r0-manifest-20261011.md` | 11567 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02-readonly-preflight-r0-review-20261011.md` | 29404 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02-readonly-preflight-r0s1-evidence-20261011.md` | 5489 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02-readonly-preflight-r0s1-manifest-20261011.md` | 22925 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02-readonly-preflight-r0s1-review-20261011.md` | 21262 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02-readonly-preflight-r0s2-manifest-20261011.md` | 7710 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02-readonly-preflight-r0s2-review-20261011.md` | 19235 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02-readonly-preflight-r0s4-manifest-20261011.md` | 11747 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02-readonly-preflight-r0s5-manifest-20261011.md` | 10471 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r0s6-adjudication-20261011.md` | 3076 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r0s6-checkpoint-20261011.md` | 4695 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r0s6-delivery-20261011.md` | 5749 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r0s6-manifest-20261011.md` | 9073 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r0s6-verification-20261011.md` | 2742 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1-adjudication-20261011.md` | 11324 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1-capture.ps1` | 38729 | 建议入库 | 无命中 | 可执行验证脚本，保留复现程序与参数实现。 |
| `verification/P02/p02pre-r1-evidence-20261011.json` | 2588454 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1-manifest-20261011.md` | 12615 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1-windows-powershell-parse-20261011.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/p02pre-r1-windows-powershell-parse-20261011.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/p02pre-r1-windows-powershell-parse-20261011.stdout.log` | 45 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/p02pre-r1-windows-powershell-parse-r2-20261011.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/p02pre-r1-windows-powershell-parse-r2-20261011.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/p02pre-r1-windows-powershell-parse-r2-20261011.stdout.log` | 45 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/p02pre-r1-windows-powershell-parse-r3-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/p02pre-r1-windows-powershell-parse-r3-20261011.stderr.log` | 382 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/p02pre-r1-windows-powershell-parse-r3-20261011.stdout.log` | 45 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/p02pre-r1-windows-powershell-parse-r4-20261011.json` | 2086 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1f-adjudication-20261011.md` | 14478 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-capture-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/p02pre-r1f-capture-20261011.stderr.log` | 676 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/p02pre-r1f-capture-20261011.stdout.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/p02pre-r1f-capture.ps1` | 67582 | 建议入库 | 无命中 | 可执行验证脚本，保留复现程序与参数实现。 |
| `verification/P02/p02pre-r1f-evidence-20261011.json` | 23131 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1f-followupfix-selfcheck-wrapper-attempt1-20261011.md` | 1179 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-manifest-20261011.md` | 49783 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-parser-20261011.json` | 603 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1f-parser-windows-powershell-5.1-20261011.json` | 1285 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r2-20261011.json` | 1850 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r3-20261011.json` | 1766 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r4-20261011.json` | 2231 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r6-20261011.json` | 1337 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r7-20261011.json` | 1336 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r8-20261011.json` | 2595 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1f-postrun-adjudication-20261011.md` | 8716 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-postrun-docs-followup3-dispatch-failure-20261011.md` | 2806 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-postrun-followup4-runner-attempt1-failure-20261012.md` | 974 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-postrun-review-followup2-docs-adjudication-20261011.md` | 2933 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-postrun-review-followup4-docs-adjudication-20261012.md` | 5544 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-r2-selfcheck-20261011.json` | 1548 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1f-r5-adjudication-20261011.md` | 5478 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-r5-followup2-adjudication-20261011.md` | 6330 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-r5-followup2-review-adjudication-20261011.md` | 4950 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-r5-followup3-review-adjudication-20261011.md` | 4500 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-r5-followup4-review-adjudication-20261011.md` | 4000 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-r5-followup5-review-adjudication-20261011.md` | 4672 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-r5-followup6-review-adjudication-20261011.md` | 4960 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-r5-followup7-fixreview-adjudication-20261011.md` | 4461 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-r5-followup7-fixreview10-adjudication-20261011.md` | 3398 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-r5-followup7-fixreview2-adjudication-20261011.md` | 3401 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-r5-followup7-fixreview3-adjudication-20261011.md` | 5149 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-r5-followup7-fixreview4-adjudication-20261011.md` | 4132 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-r5-followup7-fixreview5-adjudication-20261011.md` | 4287 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-r5-followup7-fixreview6-adjudication-20261011.md` | 3879 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-r5-followup7-fixreview7-adjudication-20261011.md` | 2785 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-r5-followup7-fixreview8-adjudication-20261011.md` | 4794 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-r5-followup7-fixreview9-adjudication-20261011.md` | 3994 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-r5-followup7-review-adjudication-20261011.md` | 4965 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1f-r5-followupfix-selfcheck-20261011.json` | 2307 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1f-r5-followupfix2-selfcheck-20261011.json` | 2308 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1f-r5-followupfix3-selfcheck-20261011.json` | 2927 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1f-r5-followupfix4-selfcheck-20261011.json` | 2154 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1f-r5-followupfix5-selfcheck-20261011.json` | 2221 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1f-r5-reviewfix-selfcheck-20261011.json` | 2694 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1f-r5-selfcheck-20261011.json` | 2975 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1f-r5-selfcheck-retry-20261011.json` | 1694 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1g-antigravity-handoff-20261011.md` | 18665 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1g-argumentlist-delivery-adjudication-20261012.md` | 4541 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1g-author-selfcheck-20261011.json` | 2462 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1g-capture-20261011.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/p02pre-r1g-capture-20261011.stderr.log` | 398 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/p02pre-r1g-capture-20261011.stdout.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/p02pre-r1g-capture.ps1` | 81991 | 建议入库 | 无命中 | 可执行验证脚本，保留复现程序与参数实现。 |
| `verification/P02/p02pre-r1g-engine-preflight-20261011.json` | 4121 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1g-evidence-20261011.json` | 9025567 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1g-evidence-docs-adjudication-20261012.md` | 2699 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1g-integration-followup3-20261012.json` | 3553 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1g-manifest-20261011.md` | 26657 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1g-postrun-adjudication-20261012.md` | 2347 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1g-r009-r010-delivery-adjudication-20261012.md` | 3832 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1g-remediation-review-adjudication-20261012.md` | 4618 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1g-review-adjudication-20261012.md` | 6144 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1g-review-followup1-dispatch-adjudication-20261012.md` | 4151 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1g-review-followup2-adjudication-20261012.md` | 3091 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1g-review-followup3-adjudication-20261012.md` | 1817 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1g-runner-evidence-20261011.json` | 33238 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1g-selfcheck-20261011.json` | 6225 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1h-attempt4-review-adjudication-20261012.md` | 6063 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1h-attempt5-exec-review-adjudication-20261012.md` | 10377 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1h-capture.ps1` | 93124 | 建议入库 | 无命中 | 可执行验证脚本，保留复现程序与参数实现。 |
| `verification/P02/p02pre-r1h-engine-preflight-round4-20261012.json` | 5328 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1h-engine-preflight-round5-20261012.json` | 6990 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1h-handoff-20261012.md` | 8651 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1h-integration-execution-20261012.json` | 493429 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1h-integration-protocol-r2-adjudication-20261012.md` | 4247 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1h-integration-protocol-review-adjudication-round6-20261012.md` | 2806 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1h-integration-protocol-review-adjudication-round6-attempt2-20261012.md` | 3826 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1h-integration-protocol-review-adjudication-round6-attempt3-20261012.md` | 6886 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1h-integration-round4-20261012.md` | 3071 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1h-manifest-20261012.md` | 4760 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1h-remediation-review-adjudication-20261012.md` | 5928 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1h-remediation2-adjudication-20261012.md` | 4988 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1h-remediation3-adjudication-20261012.md` | 3715 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1h-remediation4-adjudication-20261012.md` | 3748 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1h-remediation5-adjudication-20261012.md` | 7015 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1h-review-adjudication-20261012.md` | 1543 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1h-round4-delivery-verification-20261012.md` | 2800 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1h-round6-attempt3-definitions-check-20261012.json` | 1502 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1h-round6-attempt5-exec-handoff-20261012.md` | 2391 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1h-round6-integration-protocol-20261012.md` | 16310 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1h-round6-integration-protocol-attempt1-20261012.md` | 11184 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1h-round6-integration-protocol-attempt3-20261012.md` | 11730 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1h-round6-integration-protocol-attempt5-20261012.md` | 11641 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1h-round6-integrator-20261012.ps1` | 40604 | 建议入库 | 无命中 | 可执行验证脚本，保留复现程序与参数实现。 |
| `verification/P02/p02pre-r1h-round6-integrator-attempt5-20261012.ps1` | 43464 | 建议入库 | 无命中 | 可执行验证脚本，保留复现程序与参数实现。 |
| `verification/P02/p02pre-r1h-round6-review-adjudication-20261012.md` | 3516 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/p02pre-r1h-selfcheck-round4-20261012.json` | 3121 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1h-selfcheck-round4-integrated-backup-20261012.ps1` | 57623 | 建议入库 | 无命中 | 可执行验证脚本，保留复现程序与参数实现。 |
| `verification/P02/p02pre-r1h-selfcheck-round4-recovery-20261012.ps1` | 57623 | 建议入库 | 无命中 | 可执行验证脚本，保留复现程序与参数实现。 |
| `verification/P02/p02pre-r1h-selfcheck-round5-20261012.json` | 4076 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/p02pre-r1h-selfcheck.ps1` | 57648 | 建议入库 | 无命中 | 可执行验证脚本，保留复现程序与参数实现。 |
| `verification/P02/r2-clean-commit-harness.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/r2-clean-commit-harness.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r2-clean-commit-harness.stdout.log` | 2989 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r2-clean-commit-probe.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/r2-clean-commit-probe.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r2-clean-commit-probe.stdout.log` | 1714 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r2-clean-commit-validation.md` | 3115 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/r2-diff-check.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/r2-diff-check.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r2-diff-check.stdout.log` | 148 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r3-clean-commit-diff-check.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/r3-clean-commit-diff-check.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r3-clean-commit-diff-check.stdout.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r3-clean-commit-validation.md` | 3692 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/r3-codex-supplemental-review.md` | 4873 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/r3-plan-validator.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/r3-plan-validator.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r3-plan-validator.stdout.log` | 659 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r4-clean-commit-validation.md` | 4344 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/r4-codex-independent-review.md` | 5997 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/r4-codex-tsc-exact.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/r4-codex-tsc-exact.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r4-codex-tsc-exact.stdout.log` | 161 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r4-exact-diff-check.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/r4-exact-diff-check.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r4-exact-diff-check.stdout.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r4-exact-full.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/r4-exact-full.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r4-exact-full.stdout.log` | 5065 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r4-exact-probeonly.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/r4-exact-probeonly.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r4-exact-probeonly.stdout.log` | 1789 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r4-handoff-plan-validator.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/r4-handoff-plan-validator.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r4-handoff-plan-validator.stdout.log` | 659 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r5-codex-diff-check.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/r5-codex-diff-check.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r5-codex-diff-check.stdout.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r5-codex-exact-full.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/r5-codex-exact-full.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r5-codex-exact-full.stdout.log` | 6305 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r5-codex-exact-head-review.md` | 5290 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/r5-codex-exact-probeonly.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/r5-codex-exact-probeonly.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r5-codex-exact-probeonly.stdout.log` | 2176 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r5-codex-failure-path.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/r5-codex-failure-path.stderr.log` | 1886 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r5-codex-failure-path.stdout.log` | 3652 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r5-codex-independent-review.md` | 4168 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/r5-codex-tsc-exact.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/r5-codex-tsc-exact.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r5-codex-tsc-exact.stdout.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r6-codex-artifact-hash-check.json` | 2877 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/r6-codex-commit-metadata.json` | 1026 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/r6-codex-diff-check.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/r6-codex-diff-check.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r6-codex-diff-check.stdout.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r6-codex-exact-full.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/r6-codex-exact-full.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r6-codex-exact-full.stdout.log` | 6809 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r6-codex-exact-probeonly.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/r6-codex-exact-probeonly.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r6-codex-exact-probeonly.stdout.log` | 2540 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r6-codex-exception-catch-run.log` | 1069 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r6-codex-exception-catch.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/r6-codex-exception-catch.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r6-codex-exception-catch.stdout.log` | 524 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r6-codex-finalize-failure-legacy-run.log` | 6601 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r6-codex-finalize-failure-run.log` | 6601 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r6-codex-finalize-failure.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/r6-codex-finalize-failure.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r6-codex-finalize-failure.stdout.log` | 6522 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r6-codex-missing-tsc-cwd-run.log` | 2145 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r6-codex-missing-tsc-cwd.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/r6-codex-missing-tsc-cwd.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r6-codex-missing-tsc-cwd.stdout.log` | 1769 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r6-codex-scope-check.json` | 1283 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/r6-codex-tsc-exact.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/r6-codex-tsc-exact.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/r6-codex-tsc-exact.stdout.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/review-stage-a-972049f9-checkpoint.md` | 10444 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/scope-review-r5.exit` | 449 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/scope-review-r5.prompt.md` | 2075 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/scope-review-r5.stderr.log` | 127592 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/scope-review-r5.stdout.md` | 16832 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/scope-review-r6-session-reuse.exit` | 563 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/scope-review-r6-session-reuse.stderr.log` | 195 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/scope-review-r6-session-reuse.stdout.md` | 0 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/scope-review-r6.exit` | 451 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/scope-review-r6.prompt.md` | 4421 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/scope-review-r6.stderr.log` | 33851 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/scope-review-r6.stdout.md` | 16920 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/zcode-dispatch-env-smoke-20261012-152149.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/zcode-dispatch-env-smoke-20261012-152149.meta.json` | 866 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/zcode-dispatch-env-smoke-20261012-152149.prompt.md` | 97 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/zcode-dispatch-env-smoke-20261012-152149.stderr.log` | 78 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/zcode-dispatch-env-smoke-20261012-152149.stdout.json` | 0 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/zcode-dispatch-env-smoke-a6-20261012-152336.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/zcode-dispatch-env-smoke-a6-20261012-152336.meta.json` | 934 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/zcode-dispatch-env-smoke-a6-20261012-152336.prompt.md` | 97 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/zcode-dispatch-env-smoke-a6-20261012-152336.stderr.log` | 78 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/zcode-dispatch-env-smoke-a6-20261012-152336.stdout.json` | 0 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/zcode-dispatch-smoke-20261012.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/zcode-dispatch-smoke-20261012.prompt.md` | 179 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/zcode-dispatch-smoke-20261012.stderr.log` | 154 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/zcode-dispatch-smoke-20261012.stdout.json` | 0 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/zcode-dispatch-smoke-after-restore-20261012.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/zcode-dispatch-smoke-after-restore-20261012.stderr.log` | 110 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/zcode-dispatch-smoke-after-restore-20261012.stdout.json` | 0 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/zcode-p02-proxy-env-snapshot-20261012-154808-639.json` | 1507 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/zcode-p02pre-r1h-exec-a6-dispatch-20261012.md` | 12638 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/zcode-p02pre-r1h-exec-a6-prompt-20261012.md` | 2553 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/zcode-p02pre-r1h-exec-a6-retry-20261012.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/zcode-p02pre-r1h-exec-a6-retry-20261012.stderr.log` | 100 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/zcode-p02pre-r1h-exec-a6-retry-20261012.stdout.json` | 0 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/zcode-p02pre-r1h-exec-a6-retry-desktop-20261012.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/zcode-p02pre-r1h-exec-a6-retry-desktop-20261012.stderr.log` | 110 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/zcode-p02pre-r1h-exec-a6-retry-desktop-20261012.stdout.json` | 0 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/zcode-p02pre-r1h-exec-a6.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/zcode-p02pre-r1h-exec-a6.stderr.log` | 154 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/zcode-p02pre-r1h-exec-a6.stdout.json` | 0 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P02/zcode-p02pre-r1h-p2-1-dispatch-20261012-attempt2.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/zcode-p02pre-r1h-p2-1-dispatch-20261012-attempt2.stdout.jsonl` | 0 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/zcode-p02pre-r1h-p2-1-dispatch-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/zcode-p02pre-r1h-p2-1-dispatch-20261012.stdout.jsonl` | 0 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/zcode-p02pre-r1h-p2-1-evidence-closure-prompt-20261012.md` | 9081 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/zcode-p02pre-r1h-p2-1-probe-20261012.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/zcode-p02pre-r1h-p2-1-probe-20261012.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/zcode-p02pre-r1h-p2-1-probe-20261012.stdout.jsonl` | 651 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/zcode-p02pre-r1h-p2-1-task-20261012.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/zcode-p02pre-r1h-p2-1-task-20261012.stderr.log` | 2865 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/zcode-p02pre-r1h-p2-1-task-20261012.stdout.jsonl` | 3694 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P02/zcode-p02pre-r1h-remediation-20261012.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P02/zcode-p02pre-r1h-remediation-20261012.prompt.md` | 5547 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/zcode-p02pre-r1h-remediation-20261012.stderr.log` | 154 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/zcode-p02pre-r1h-remediation-20261012.stdout.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P02/zcode-p02pre-r1h-round6-attempt6-handoff-20261012.md` | 5872 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02/zcode-p02pre-r1h-round6-attempt6-resume-prompt-20261012.md` | 9297 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P02PRE-R1H-FORENSIC-RECOVERY/adjudication.md` | 1973 | 保留 | doc/tasks/P02PRE-R1H-FORENSIC-RECOVERY.md:62 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-FORENSIC-RECOVERY/checkpoint.md` | 1825 | 保留 | doc/tasks/P02PRE-R1H-FORENSIC-RECOVERY.md:63 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-FORENSIC-RECOVERY/dsh-review-r1.md` | 15114 | 保留 | doc/tasks/P02PRE-R1H-FORENSIC-RECOVERY.md:64 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-FORENSIC-RECOVERY/dsh-review-r2.md` | 4831 | 保留 | doc/tasks/P02PRE-R1H-FORENSIC-RECOVERY.md:65 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-FORENSIC-RECOVERY/method-manifest.json` | 206933 | 保留 | doc/tasks/P02PRE-R1H-FORENSIC-RECOVERY.md:66 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-FORENSIC-RECOVERY/method-summary.md` | 7783 | 保留 | doc/tasks/P02PRE-R1H-FORENSIC-RECOVERY.md:67 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-FORENSIC-RECOVERY/recovery-report-r2.md` | 6443 | 保留 | doc/tasks/P02PRE-R1H-FORENSIC-RECOVERY.md:68 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-FORENSIC-RECOVERY/recovery-report.md` | 4572 | 保留 | doc/tasks/P02PRE-R1H-FORENSIC-RECOVERY.md:69 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-FORENSIC-RECOVERY/resource-closeout-r2.json` | 6471 | 保留 | doc/tasks/P02PRE-R1H-FORENSIC-RECOVERY.md:70 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW/applicability-matrix-r1.md` | 4195 | 保留 | doc/tasks/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW.md:96 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW/checkpoint.md` | 1727 | 保留 | doc/tasks/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW.md:99 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW/codex-adjudication-r1.md` | 3954 | 保留 | doc/tasks/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW.md:97 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW/codex-handoff-r1.md` | 2249 | 保留 | doc/tasks/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW.md:98 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW/codex-handoff-r2.md` | 2582 | 保留 | doc/tasks/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW.md:101 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW/dsh-applicability-review-r1.md` | 12868 | 保留 | doc/tasks/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW.md:94 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW/dsh-review-request-r1.md` | 2652 | 保留 | doc/tasks/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW.md:93 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW/h1-subject-task-r1.md` | 25016 | 保留 | doc/tasks/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW.md:88 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW/h2-run-task-r1.md` | 25680 | 保留 | doc/tasks/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW.md:89 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW/post-review-pins-r1.json` | 4974 | 保留 | doc/tasks/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW.md:95 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW/pre-review-pins-r1.json` | 6679 | 保留 | doc/tasks/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW.md:91 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW/pre-review-validation-r1.json` | 4177 | 保留 | doc/tasks/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW.md:92 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW/resource-closeout-r1.json` | 3583 | 保留 | doc/tasks/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW.md:100 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW/review-inputs-r1.json` | 6748 | 保留 | doc/tasks/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW.md:90 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW/task-contract-r1.md` | 8351 | 保留 | doc/tasks/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW.md:87 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/checkpoint.md` | 24221 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:201 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/codex-r6-independent-verification.json` | 4930 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:238 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/codex-r7-independent-verification.json` | 6911 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:264 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/dsh-source-review-r1.md` | 14868 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:202 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/dsh-source-review-r2.md` | 17291 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:175 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/dsh-source-review-r3.md` | 18631 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:188 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/dsh-source-review-r4.md` | 17785 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:198 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/dsh-source-review-r5.md` | 15491 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:221 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/dsh-source-review-r6.md` | 13834 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:246 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/dsh-source-review-r7.md` | 11869 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:273 (Canonical Evidence pin)<br>doc/tasks/P02PRE-R1H-H2-RUN.md:82 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/integration-verification-r7.md` | 2141 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:279 (Canonical Evidence pin)<br>doc/tasks/P02PRE-R1H-H2-RUN.md:85 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/source-review-r1-adjudication.md` | 3390 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:203 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/source-review-r1-input-verification.json` | 3342 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:204 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/source-review-r2-adjudication.md` | 4178 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:177 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/source-review-r2-input-verification.json` | 3947 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:176 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/source-review-r3-adjudication.md` | 4304 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:190 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/source-review-r3-input-verification.json` | 4195 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:189 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/source-review-r4-adjudication.md` | 4155 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:200 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/source-review-r4-input-verification.json` | 5175 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:199 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/source-review-r5-adjudication.md` | 4751 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:227 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/source-review-r5-input-verification.json` | 10648 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:222 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/source-review-r6-adjudication.md` | 3195 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:251 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/source-review-r6-input-verification.json` | 11114 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:247 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/source-review-r7-adjudication.md` | 2920 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:275 (Canonical Evidence pin)<br>doc/tasks/P02PRE-R1H-H2-RUN.md:84 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-COLLECTOR/source-review-r7-input-verification.json` | 12112 | 保留 | doc/tasks/P02PRE-R1H-H2-COLLECTOR.md:274 (Canonical Evidence pin)<br>doc/tasks/P02PRE-R1H-H2-RUN.md:83 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-RUN/checkpoint.md` | 2199 | 保留 | doc/tasks/P02PRE-R1H-H2-RUN.md:100 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-RUN/codex-adjudication-r1-input-verification.json` | 4426 | 保留 | doc/tasks/P02PRE-R1H-H2-RUN.md:133 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-RUN/codex-adjudication-r1.md` | 4836 | 保留 | doc/tasks/P02PRE-R1H-H2-RUN.md:132 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-RUN/codex-handoff-r1.md` | 2582 | 保留 | doc/tasks/P02PRE-R1H-H2-RUN.md:115 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-RUN/codex-handoff-r2.md` | 3008 | 保留 | doc/tasks/P02PRE-R1H-H2-RUN.md:137 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-RUN/dsh-result-review-r1.md` | 15351 | 保留 | doc/tasks/P02PRE-R1H-H2-RUN.md:119 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-RUN/dsh-result-review-r2.md` | 7777 | 保留 | doc/tasks/P02PRE-R1H-H2-RUN.md:125 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-RUN/dsh-result-review-r3.md` | 7098 | 保留 | doc/tasks/P02PRE-R1H-H2-RUN.md:130 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-RUN/preflight-freeze-r1.md` | 7466 | 保留 | doc/tasks/P02PRE-R1H-H2-RUN.md:95 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-RUN/resource-closeout-r1.json` | 4652 | 保留 | doc/tasks/P02PRE-R1H-H2-RUN.md:138 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-RUN/result-review-r1-post-pins.json` | 8490 | 保留 | doc/tasks/P02PRE-R1H-H2-RUN.md:120 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-RUN/result-review-r2-post-pins.json` | 4757 | 保留 | doc/tasks/P02PRE-R1H-H2-RUN.md:126 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-RUN/result-review-r3-post-pins.json` | 3937 | 保留 | doc/tasks/P02PRE-R1H-H2-RUN.md:131 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-RUN/runtime-verification-r1.json` | 3119 | 保留 | doc/tasks/P02PRE-R1H-H2-RUN.md:113 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-RUN/runtime-verification-r1.md` | 3140 | 保留 | doc/tasks/P02PRE-R1H-H2-RUN.md:114 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-RUN/runtime-verification-r2.json` | 3370 | 保留 | doc/tasks/P02PRE-R1H-H2-RUN.md:117 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-H2-RUN/runtime-verification-r2.md` | 3253 | 保留 | doc/tasks/P02PRE-R1H-H2-RUN.md:118 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/candidate-trace-r1.json` | 1171 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:84 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/checkpoint.md` | 2044 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:85 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/codex-adjudication-r1.md` | 2289 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:89 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/codex-adjudication-r2.md` | 3705 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:104 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/dsh-probe-exit-r1.txt` | 1 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:95 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/dsh-probe-stderr-r1.log` | 0 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:94 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/dsh-probe-stdout-r1.log` | 8 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:93 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/dsh-probe-version-r1.log` | 12 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:92 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/dsh-review-dispatch-r2.md` | 989 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:100 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/dsh-review-r1.md` | 9481 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:88 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/dsh-review-r2.md` | 9493 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:101 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/dsh-review-run-r1.json` | 1344 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:91 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/dsh-review-run-r2.json` | 2710 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:103 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/existing-pins-validation-r1.json` | 3144 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:82 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/input-freeze-r1.json` | 3980 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:81 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/integration-gate-r2.json` | 1633 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:106 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/post-review-pins-r1.json` | 3871 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:90 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/post-review-pins-r2.json` | 11050 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:102 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/pre-review-pins-r1.json` | 2728 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:86 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/r1-commit-normalization-map-r1.json` | 7402 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:97 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/resource-closeout-r2.json` | 6075 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:107 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/review-input-pins-r2.json` | 4667 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:99 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/review-request-r1.md` | 2062 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:87 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/review-request-r2.md` | 3346 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:98 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/store-inventory-r1.json` | 16880 | 保留 | doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md:83 (Canonical Evidence pin) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P03-PACKAGED-SFX-ENTRY/dsh-preflight.jsonl` | 514 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P03-PACKAGED-SFX-ENTRY/dsh-preflight.log` | 635 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P03-PACKAGED-SFX-ENTRY/dsh-preflight.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P03-PACKAGED-SFX-ENTRY/dsh-review-formal-r2-4c04459.exit` | 3 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P03-PACKAGED-SFX-ENTRY/dsh-review-formal-r2-4c04459.prompt.md` | 4548 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P03-PACKAGED-SFX-ENTRY/dsh-review-formal-r2-4c04459.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P03-PACKAGED-SFX-ENTRY/dsh-review-formal-r2-4c04459.stdout.jsonl` | 430641 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P03-PACKAGED-SFX-ENTRY/dsh-review-prompt.md` | 3932 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P03-PACKAGED-SFX-ENTRY/dsh-review.exit` | 8 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P03-PACKAGED-SFX-ENTRY/dsh-review.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P03-PACKAGED-SFX-ENTRY/dsh-review.stdout.jsonl` | 347022 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P04/ac2-static-mismatch.md` | 1214 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P04/antigravity-owner-r2-revision.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P04/antigravity-owner-r2-revision.prompt.md` | 4095 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P04/antigravity-owner-r2-revision.stderr.log` | 421 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P04/antigravity-owner-r2-revision.stdout.json` | 6719 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P04/codex-checkpoint-p04-r2-delivery-20261010.md` | 5154 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P04/codex-checkpoint-p04-r2-review-20261010.md` | 3629 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P04/codex-checkpoint-p04-r3-resume-20261010.md` | 4311 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P04/diagnostic_p22_16972_1792152234209.jsonl` | 2598 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P04/diagnostic_p22_23396_1792289621702.jsonl` | 2594 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P04/diagnostic_p22_24256_1792199847816.jsonl` | 2597 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P04/diagnostic_p22_25540_1792299756579.jsonl` | 2552 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P04/diagnostic_p22_27804_1792154545112.jsonl` | 2599 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P04/diagnostic_p22_30440_1792293769591.jsonl` | 2549 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P04/diagnostic_p22_32052_1792289621044.jsonl` | 2597 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P04/diagnostic_p22_35980_1792152127078.jsonl` | 2595 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P04/diagnostic_p22_36804_1792289717476.jsonl` | 2597 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P04/diagnostic_p22_38224_1792196848708.jsonl` | 2599 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P04/diagnostic_p22_39164_1792156457006.jsonl` | 2599 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P04/diagnostic_p22_40884_1792162567382.jsonl` | 2595 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P04/diagnostic_p22_41772_1792293480033.jsonl` | 2170 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P04/diagnostic_p22_5196_1792154806032.jsonl` | 2597 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P04/diagnostic_p22_53656_1792240292357.jsonl` | 2596 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P04/diagnostic_p22_8144_1792301653221.jsonl` | 2551 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P04/dsh-p04-owner-review-r2-resume.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P04/dsh-p04-owner-review-r2-resume.prompt.md` | 1272 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P04/dsh-p04-owner-review-r2-resume.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P04/dsh-p04-owner-review-r2-resume.stdout.jsonl` | 78654 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P04/dsh-p04-owner-review-r2.mount.json` | 316 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P04/dsh-p04-owner-review-r2.prompt.md` | 3591 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P04/dsh-p04-owner-review-r2.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P04/dsh-p04-owner-review-r2.stdout.jsonl` | 165811 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P04/dsh-p04-owner-review-r3-resume.stderr.log` | 28571 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P04/dsh-p04-owner-review-r3-resume.stdout.jsonl` | 0 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P04/dsh-p04-owner-review-r3.prompt.md` | 3506 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P04/dsh-p04-owner-review-r4.exit` | 2 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P04/dsh-p04-owner-review-r4.prompt.md` | 2395 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P04/task-graph-delta-p22.md` | 1071 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P08/dsh-r4.stderr.log` | 158563 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P08/dsh-r4.stdout.md` | 24597 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P08/dsh-r5.stderr.log` | 92042 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P08/dsh-r5.stdout.md` | 27999 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P08/dsh-r6.stderr.log` | 168663 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P08/dsh-r6.stdout.md` | 27088 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P08/dsh-r7.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P08/dsh-r7.stdout.jsonl` | 434334 | 建议入库 | 无命中 | 逐事件原始记录，保留顺序和会话/运行 trace。 |
| `verification/P09-AC3-DELETE-1/codex-review-r3.md` | 15315 | 保留 | doc/tasks/P09-AC3-DELETE-HARDEN-1.md:27 (READY/在飞 Task)<br>doc/STATUS.md:25 (机制文档) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P09-AC3-DELETE-1/t2-fullsuite-triage.md` | 7335 | 保留 | doc/tasks/P09-AC3-DELETE-HARDEN-1.md:29 (READY/在飞 Task) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P09-AC3-DELETE-1/t2-logs/P09-BASELINE-PRE-fullpytest.log` | 63070 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P09-AC3-DELETE-1/t2-logs/P09-BASELINE-T2-HEADminus1-fullpytest.log` | 58666 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P09-AC3-DELETE-1/t2-logs/P09-T2-bisect.log` | 1956 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P19/ac2-run10/app-err.log` | 4212 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P19/ac2-run10/app-out.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P19/ac2-run11/app-err.log` | 3476 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P19/ac2-run11/app-out.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P19/ac2-run12/app-err.log` | 2510 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P19/ac2-run12/app-out.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P19/ac2-run4/app-err.log` | 2602 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P19/ac2-run4/app-out.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P19/ac2-run4/trace.log` | 1603 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P19/ac2-run5/app-err.log` | 2418 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P19/ac2-run5/app-out.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P19/ac2-run5/trace.log` | 412 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P19/ac2-run6/app-err.log` | 2464 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P19/ac2-run6/app-out.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P19/ac2-run6/trace.log` | 1292 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P19/ac2-run7/app-err.log` | 2464 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P19/ac2-run7/app-out.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P19/ac2-run7/trace.log` | 415 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P19/ac2-run8/app-err.log` | 2786 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P19/ac2-run8/app-out.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P19/ac2-run8/trace.log` | 366 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P19/ac2-run9/app-err.log` | 2786 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P19/ac2-run9/app-out.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P19/ac2-run9/trace.log` | 358 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P20-CLOSE-BOUND-1/codex-review-r6.md` | 19484 | 保留 | doc/tasks/P20-CLOSE-BOUND-1.md:120 (Canonical Evidence pin)<br>doc/tasks/P20-CLOSE-BOUND-HARDEN-1.md:73 (READY/在飞 Task) | 被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。 |
| `verification/P22/antigravity-owner-p22-r10-handoff-fix.prompt.md` | 3018 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/antigravity-owner-p22-r10.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P22/antigravity-owner-p22-r10.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P22/antigravity-owner-p22-r10.stdout.json` | 7002 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P22/antigravity-owner-p22-r2.prompt.md` | 3993 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/antigravity-owner-p22-r3-handoff-fix.stdout.md` | 0 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/antigravity-owner-p22-r4-handoff-fix.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P22/antigravity-owner-p22-r4-handoff-fix.prompt.md` | 2963 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/antigravity-owner-p22-r4-handoff-fix.response.md` | 7764 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/antigravity-owner-p22-r4-handoff-fix.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P22/antigravity-owner-p22-r4-handoff-fix.stdout.json` | 8169 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P22/antigravity-owner-p22-r6.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P22/antigravity-owner-p22-r6.prompt.md` | 2020 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/antigravity-owner-p22-r6.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P22/antigravity-owner-p22-r6.stdout.json` | 7406 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P22/antigravity-owner-p22-r6.stdout.md` | 7047 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/antigravity-owner-p22-r7-handoff-fix.prompt.md` | 3103 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/antigravity-owner-p22-r7.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P22/antigravity-owner-p22-r7.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P22/antigravity-owner-p22-r7.stdout.json` | 8629 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P22/antigravity-owner-p22-r7.stdout.md` | 8243 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/antigravity-owner-p22-r8-handoff-fix.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P22/antigravity-owner-p22-r8-handoff-fix.prompt.md` | 2662 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/antigravity-owner-p22-r8-handoff-fix.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P22/antigravity-owner-p22-r8-handoff-fix.stdout.json` | 8748 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P22/antigravity-owner-p22-r8-handoff-fix.stdout.md` | 8289 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/antigravity-owner-p22-r9-handoff-fix.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P22/antigravity-owner-p22-r9-handoff-fix.prompt.md` | 2196 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/antigravity-owner-p22-r9-handoff-fix.stderr.log` | 0 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P22/antigravity-owner-p22-r9-handoff-fix.stdout.json` | 5891 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/P22/antigravity-owner-p22-r9-handoff-fix.stdout.md` | 5507 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/codex-p22-r10-review-adjudication.md` | 2953 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/codex-p22-r5-review-adjudication.md` | 3231 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/codex-p22-r6-review-adjudication.md` | 3797 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/codex-p22-r7-review-adjudication.md` | 2477 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/codex-p22-r8-review-adjudication.md` | 2836 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/codex-p22-r9-review-adjudication.md` | 3065 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/codex-p22-task-r4-malformed-snapshot-7ebd7d40.md` | 21531 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/codex-r2-review-adjudication.md` | 3460 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/codex-r3-review-adjudication.md` | 3325 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/dsh-p22-review-r10.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P22/dsh-p22-review-r10.mount.log` | 113 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P22/dsh-p22-review-r10.prompt.md` | 3290 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/dsh-p22-review-r10.stderr.log` | 48430 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P22/dsh-p22-review-r10.stdout.md` | 7438 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/dsh-p22-review-r4.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P22/dsh-p22-review-r4.prompt.md` | 3175 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/dsh-p22-review-r4.stderr.log` | 70844 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P22/dsh-p22-review-r4.stdout.md` | 14888 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/dsh-p22-review-r5.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P22/dsh-p22-review-r5.prompt.md` | 2069 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/dsh-p22-review-r5.stderr.log` | 76903 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P22/dsh-p22-review-r5.stdout.md` | 20711 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/dsh-p22-review-r6.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P22/dsh-p22-review-r6.prompt.md` | 3292 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/dsh-p22-review-r6.stderr.log` | 113003 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P22/dsh-p22-review-r6.stdout.md` | 15036 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/dsh-p22-review-r7.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P22/dsh-p22-review-r7.prompt.md` | 3779 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/dsh-p22-review-r7.stderr.log` | 88428 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P22/dsh-p22-review-r7.stdout.md` | 11646 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/dsh-p22-review-r8.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P22/dsh-p22-review-r8.prompt.md` | 2464 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/dsh-p22-review-r8.stderr.log` | 24249 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P22/dsh-p22-review-r8.stdout.md` | 13072 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/dsh-p22-review-r9.exit` | 1 | 建议入库 | 无命中 | 逐次运行退出码 sidecar；保留可审计的进程结果。 |
| `verification/P22/dsh-p22-review-r9.prompt.md` | 3340 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/P22/dsh-p22-review-r9.stderr.log` | 21608 | 建议入库 | 无命中 | 原始运行日志；可独立复核命令结果、错误和运行顺序。 |
| `verification/P22/dsh-p22-review-r9.stdout.md` | 16153 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/PROJECT-GOVERNANCE-20261012/cleanup-manifest.md` | 15203 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/PROJECT-GOVERNANCE-20261012/worktree-inventory.md` | 70365 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/PROJECT-ORCHESTRATION-20261014/checkpoint.md` | 4503 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/PROJECT-ORCHESTRATION-20261014/decision-dry-run.json` | 1055 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/PROJECT-ORCHESTRATION-20261014/decision-input.json` | 551 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/PROJECT-ORCHESTRATION-20261014/decision.json` | 1056 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/PROJECT-ORCHESTRATION-20261014/refresh-verification.json` | 3862 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/PROJECT-ROADMAP-20261009/ROADMAP.md` | 16185 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/PROJECT-ROADMAP-20261010/ARTIFACT-CHECK.json` | 1212 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/PROJECT-ROADMAP-20261010/CODE-DELTA.md` | 3817 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/PROJECT-ROADMAP-20261010/OVERVIEW.png` | 490356 | 建议入库 | 无命中 | 截图或图像证据，保留视觉状态快照。 |
| `verification/PROJECT-ROADMAP-20261010/OVERVIEW.svg` | 15049 | 建议入库 | 无命中 | 矢量证据或图示，保留可复核视觉/结构内容。 |
| `verification/PROJECT-ROADMAP-20261010/PLANNING-ADVICE.md` | 4068 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/PROJECT-ROADMAP-20261010/RESUME.md` | 8787 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/PROJECT-ROADMAP-20261010/ROADMAP.md` | 23573 | 建议入库 | 无命中 | 任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。 |
| `verification/PROJECT-ROADMAP-20261010/snapshot.json` | 22531 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
| `verification/PROJECT-ROADMAP-20261010/tasks.csv` | 8862 | 建议入库 | 无命中 | 结构化数据清单，保留筛选结果与统计输入。 |
| `verification/PROJECT-ROADMAP-20261010/USAGE.json` | 20748 | 建议入库 | 无命中 | 结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。 |
