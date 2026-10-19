# P02 AC3 GIT-TOPLEVEL-RESOLUTION：未合并分支的证据清点

**依据**：`codex-debt-ruling.md` §3「先由 DSH/Reviewer 对分支固定 head 和证据作事实清点」。
**本文件只记录事实，不含合并、复制或重钉授权**。

| 项 | 值 |
|---|---|
| 分支 | `agent/zcode/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION` |
| 固定 head | `0af8980884e9d027042ef145cd966577d86b5bc5` |
| head 是否为当前 HEAD 祖先 | **no** |
| 该分支上的证据文件数 | 72 |
| 其中本分支已入库的 | 0 |
| Task 表中 pin 但解析失败的行 | 23 |

## 23 个 pin 与分支内容的对照

- **在该分支上存在：18 个**
- **在该分支上也不存在：5 个**

分支上也不存在、因此即便合并该分支也无法解析的 pin：

- `doc/handoffs/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION-R1.md`
- `verification/P02-NEW-TIME-BASELINE/codex-parent-integration-r1.md`
- `verification/P02-NEW-TIME-BASELINE/codex-parent-integration-r1.json`
- `verification/P02-NEW-TIME-BASELINE/codex-post-resolution-selftest-r1.meta.json`
- `verification/P02-NEW-TIME-BASELINE/codex-post-resolution-selftest-r1.fixture-inventory.json`

## 该分支 72 个证据文件清单

- `codex-convergence-ac3-resolution-r1.exit.txt`
- `codex-convergence-ac3-resolution-r1.input.json`
- `codex-convergence-ac3-resolution-r1.stderr.log`
- `codex-convergence-ac3-resolution-r1.stdout.json` *(also pinned)*
- `codex-dsh-review-adjudication-r1.md` *(also pinned)*
- `codex-selftest-verify-r1.command.txt`
- `codex-selftest-verify-r1.exit.txt`
- `codex-selftest-verify-r1.meta.json` *(also pinned)*
- `codex-selftest-verify-r1.stderr.log`
- `codex-selftest-verify-r1.stdout.log`
- `codex-verify-ac3-resolution-r1.json` *(also pinned)*
- `codex-verify-ac3-resolution-r1.md` *(also pinned)*
- `dsh-evidence-manifest-r1-verify.command.txt`
- `dsh-evidence-manifest-r1-verify.exit.txt`
- `dsh-evidence-manifest-r1-verify.stderr.log`
- `dsh-evidence-manifest-r1-verify.stdout.json`
- `dsh-evidence-manifest-r1.command.txt`
- `dsh-evidence-manifest-r1.exit.txt`
- `dsh-evidence-manifest-r1.stderr.log`
- `dsh-evidence-manifest-r1.stdout.json`
- `dsh-evidence-manifest-r2-post-update-verify.command.txt`
- `dsh-evidence-manifest-r2-post-update-verify.exit.txt`
- `dsh-evidence-manifest-r2-post-update-verify.stderr.log`
- `dsh-evidence-manifest-r2-post-update-verify.stdout.json` *(also pinned)*
- `dsh-evidence-manifest-r2-verify.command.txt`
- `dsh-evidence-manifest-r2-verify.exit.txt`
- `dsh-evidence-manifest-r2-verify.stderr.log`
- `dsh-evidence-manifest-r2-verify.stdout.json`
- `dsh-evidence-manifest-r2.command.txt`
- `dsh-evidence-manifest-r2.exit.txt`
- `dsh-evidence-manifest-r2.stderr.log`
- `dsh-evidence-manifest-r2.stdout.json`
- `dsh-review-preflight-r1-attestation.json`
- `dsh-review-preflight-r1-config.json`
- `dsh-review-preflight-r1.command.txt`
- `dsh-review-preflight-r1.exit.txt`
- `dsh-review-preflight-r1.json` *(also pinned)*
- `dsh-review-preflight-r1.stderr.log`
- `dsh-review-preflight-r2-config.json`
- `dsh-review-preflight-r2.command.txt`
- `dsh-review-preflight-r2.exit.txt`
- `dsh-review-preflight-r2.json` *(also pinned)*
- `dsh-review-preflight-r2.stderr.log`
- `dsh-review-preflight-r3.command.txt`
- `dsh-review-preflight-r3.exit.txt`
- `dsh-review-preflight-r3.json` *(also pinned)*
- `dsh-review-preflight-r3.stderr.log`
- `dsh-source-review-r1.md` *(also pinned)*
- `dsh-source-review-r1.meta.json` *(also pinned)*
- `p02-ac3-resolution-dsh-review-evidence-manifest-r1.json` *(also pinned)*
- `p02-ac3-resolution-dsh-review-evidence-manifest-r2.json` *(also pinned)*
- `resource-closeout-r1.json` *(also pinned)*
- `selftest-temp-fixture-inventory-codex-r1.json`
- `selftest-temp-fixture-inventory-codex-r2.json` *(also pinned)*
- `zcode-owner-preflight-attestation-r1.json`
- `zcode-owner-preflight-command-r1.txt`
- `zcode-owner-preflight-command-r2.txt`
- `zcode-owner-preflight-command-r3.txt`
- `zcode-owner-preflight-config-r1.json`
- `zcode-owner-preflight-r1.exit.txt`
- `zcode-owner-preflight-r1.json` *(also pinned)*
- `zcode-owner-preflight-r1.stderr.log`
- `zcode-owner-preflight-r2.exit.txt`
- `zcode-owner-preflight-r2.json` *(also pinned)*
- `zcode-owner-preflight-r2.stderr.log`
- `zcode-owner-preflight-r3.exit.txt`
- `zcode-owner-preflight-r3.json` *(also pinned)*
- `zcode-owner-preflight-r3.stderr.log`
- `zcode-owner-selftest-1.exit.txt`
- `zcode-owner-selftest-1.meta.json`
- `zcode-owner-selftest-1.stderr.log`
- `zcode-owner-selftest-1.stdout.log`

## 边界声明

本清单不构成：合并授权、把 pin 指向 worktree 绝对路径的依据、
全量补入 72 个文件的依据，或对该 Task `integration_status: integrated` 的确认。
