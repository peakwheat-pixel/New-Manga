# P02PRE-R1H round-four exact integration record

日期：2026-10-12（Asia/Shanghai）；Integrator=`/root`。

## Review gate and source

- 已由 Codex 独立 adjudicate round-four non-author Review：`APPROVED_STATIC_CONTENT`，P0/P1/P2/P3=`0/0/0/0`；11/11 source/candidate pins pre/post `MATCH`。Report=`verification/P02/codex-subagent-p02pre-r1h-static-review-remediation4-20261012.md`（8769 / `0BE345FDA968A0F9194CA99ECD35D110F3F5F81C76116AFF65E7BAF574069C0F`）；adjudication=`verification/P02/p02pre-r1h-remediation4-adjudication-20261012.md`。
- Integration source branch=`agent/codex/P02PRE-R1H`，worktree=`C:\Users\49745\.codex\worktrees\p02pre-r1h-codex`，reviewed source HEAD=`7e7d0bce8dd86a2302d2a9eb278702d9c70354ff`，tree=`c9afca4e9bfd8d1b6a6c3ad5a8a33e0e12c3d87b`，frozen Task base=`946938bd0696dfddd01f87d61fe6723c63ecdc86`。Root 在 main 未改 HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9` 上执行精确集成；主仓 `.git/index` 前后 hash 均=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`。

## CreateNew 证据

- 集成前先核对三个目标路径不存在；随后以 Windows PowerShell 7.6.6/Core 读取 candidate pins/source bytes，并对每一目标用 `.NET FileMode.CreateNew` + exclusive write。目标存在、路径碰撞会抛错，不使用覆盖写入或 copy overwrite。
- 受控 status 同一命令在集成前：exit=0，960 NUL records / 63848 bytes / SHA-256=`2E64EDFCE86E30892A1ABC20949A80F37EDDF8D752DE508459CCAFE0948E304D`，stderr=0。集成后：exit=0，963 records / 63987 bytes / SHA-256=`A877E1B685B7024632E1F56A4D2FBB427E8DC040F56C628D84288D7B13BE262F`，stderr=0。差异仅 3 条新增 untracked paths，即以下 candidate files；无移除记录。`.tmp.driveupload` 为独立 Git pathspec 排除，未访问。

| File | Integrated bytes | Expected SHA-256 | Match |
|---|---:|---|---|
| `verification/P02/p02pre-r1h-capture.ps1` | 93124 | `0BD41442800BA2336B277C3F8C16C41D4DDF983B2B5D5967378A9EF564078DA3` | yes |
| `verification/P02/p02pre-r1h-selfcheck.ps1` | 57623 | `EEFB41141EBE162503047C20CAF4F41D5E8E01EEF2FCEE0C90DA7185A8164CF1` | yes |
| `verification/P02/p02pre-r1h-handoff-20261012.md` | 8651 | `394CCF80E58017798CA2994C0505F2F5B5BB571143D21C655CEFC77B6173520F` | yes |

All destinations were absent immediately before integration; source bytes were validated against the frozen reviewed candidate pins; after `CreateNew`, target size/hash matched exactly. No source code or index commit was changed.

## Current verification state

- Candidate exact integration=`PASS_WITH_EVIDENCE` for the three paths above.
- Parser, isolated selfcheck (including its memory mutation fixtures), no-profile child preflight, final pre-run, capture, tests outside these named checks, Build/Cargo, AC1–AC7 runtime, and OS dynamic boundary=`NOT_RUN` at record creation time.
- This record does not mark AC4 complete until the Task-prescribed parser/selfcheck/preflight each have separate truthful execution evidence. It does not authorize capture or release the Build Gate.
