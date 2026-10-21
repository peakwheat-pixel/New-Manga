---
task: WORKSPACE-DECLARATION-REMEDIATION-1-REVIEW-R3
reviewer: Codex
author: workspace-hardening
base_commit: f0f19596f
reviewed_head: 31d0705413c48a76b7e8abd07d2dde0acde6f99c
implementation_head: 2c38980c98385be79e4d67e801a954d698955c80
decision: changes_requested
review_mode: read_only
---

## 1. 结论（A–F）

- **A — F-01：未通过。** 普通的已存在 CJK/空格顶层目录会被探测，正反例也存在；但解析到 workspace/managed root 的顶层 junction 会被当成 prose 跳过，既无 fatal error，也未登记保护。
- **B — F-05：通过。** 控制字符比例检查对所有长度生效；24B 的短二进制夹具覆盖了指定情况。正常文本的 TAB、LF、CR 被排除在控制字符计数之外，正常 GB18030 文本仍可解码并产生 legacy warning。
- **C — F-06/TRIAGE：部分通过。** `RESIDUAL.md` 的 76 条 message 均与 audit JSON 完整匹配。6 条 destination generalized 与 `ENV-BUNDLE-1-FU1` unknown disposition 确实仍是 fatal；但 TRIAGE 的 file+locator 索引把 6 条同位置的 source 错误也误标为 destination generalized。
- **D — 快照/日志：部分通过。** HEAD、7416 个 tracked 文件名及其清单 SHA 可复算，`same_snapshot=true` 与记录值相符；但这些值不能证明实际扫描内容相同，且快照记录中的 after command 缺少日志里的 `--out`。before/after 日志包含命令、cwd、shell 和 exit；Handoff 的 7 errors / 2 warnings 与治理日志一致。
- **E — 真实性/回归：部分通过。** audit JSON 与 r2 的计数和分类完全一致；30 条 evidence pin、28 条 manifest 均校验通过，保护差异记录为 0 dropped。80+20 测试、双 replay 的交付日志均符合声明；本次没有重跑这些会写入夹具或证据的流程。`run_evidence.py` 自身没有单独的命令/exit 记录，不能独立确认其精确 exit。
- **F — 残余裁定：通过。** 76 条继续保留为 fatal；本 Task 不应为降数放宽 fail-closed 规则。

## 2. Findings

1. **P1 — F-01：已存在的顶层 generalized junction 被 prose 路径绕过。**  
   在 [`clean_workspace.py:987`](/G:/CODEX/New%20Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/tools/governance/clean_workspace.py:987)，`_probe_identity()` 对已解析但命中 generalized root 的 identity 返回 `None`。[`add_declaration()`](/G:/CODEX/New%20Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/tools/governance/clean_workspace.py:1003) 和 `add_evidence_pin()` 随后把它作为 prose warning 跳过，不会执行注释所称的正常解析路径。因此，仓库顶层 CJK/空格名称若是指向 workspace/managed root 的 junction，可能既不报 fatal，也不保护实际目标。该函数还把所有 `GuardError` 都折叠成 `None`，可能把解析失败误当作 prose。现有正例仅覆盖普通目录，负例覆盖不存在的 CJK 名称；未覆盖 generalized junction。建议区分“不存在的 prose”和“存在但不安全/不可解析的 identity”，并覆盖 source 与 evidence pin 两种入口。

2. **P2 — 快照指纹不足，same-snapshot 声明证据不完整。**  
   [`run_evidence.py:80`](/G:/CODEX/New%20Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/verification/WORKSPACE-DECLARATION-REMEDIATION-1/run_evidence.py:80) 只记录 HEAD 和 `git ls-files` 文件名列表；不包含 tracked 文件内容或 untracked 扫描输入，而 audit JSON 显示扫描了 1504 个 untracked 文件。末次 snapshot 在 before audit 执行前就已采集，不能覆盖两次 audit 的完整时间区间。此外，`audit-snapshots.json` 的 after command 漏掉了实际 `audit-after.log` 中的 `--out` 参数。建议对实际扫描输入取内容指纹，并在两次 audit 前后采集快照，同时从实际 argv 原样生成命令记录。

3. **P2 — TRIAGE 的同文件同 locator 结果发生覆盖。**  
   [`build_reports.py:119`](/G:/CODEX/New%20Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/verification/WORKSPACE-DECLARATION-REMEDIATION-1/build_reports.py:119) 按 `(file, locator)` 保存单个结果；同一表格行的 source 与 destination 错误互相覆盖。[`TRIAGE.md:46`](/G:/CODEX/New%20Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/verification/WORKSPACE-DECLARATION-REMEDIATION-1/TRIAGE.md:46) 起有 6 条 `DECL_GENERALIZED` source 错误被标成 `DECL_DESTINATION_GENERALIZED`。这些行仍显示 fatal，但逐项归因不准确。真正的 6 条 destination generalized 和 `ENV-BUNDLE-1-FU1` 的 `DECL_UNKNOWN_DISPOSITION` 与 r3 audit 一致且仍 fatal。

4. **P2 — `run_evidence.py` 的自身 exit 缺少直接记录。**  
   `environment.json` 的 `failures` 为空，且各个子运行日志均有结果；但交付证据中没有 `run_evidence.py` 自身的命令/cwd/shell/exit 日志或 exit 文件。因此只能确认其生成数据与 exit 0 声称一致，不能独立证明该进程的精确 exit。

## 3. AC1–AC7 判定

| AC | 判定 | 依据 |
|---|---|---|
| AC1 | PARTIAL | RESIDUAL 完整；TRIAGE 的同 locator 错误归因有 6 条错映射。 |
| AC2 | PASS | JSON 例外清单与提交 pin 一致；已有日志记录新测试通过。 |
| AC3 | FAIL | 普通存在/不存在正反例覆盖，但 generalized junction 会被 prose 跳过，属于 P1 fail-closed 缺口。 |
| AC4 | PASS | 全长度控制字符检查及 24B 短二进制夹具符合要求；正常 GB18030 内容仍走 legacy warning。 |
| AC5 | PASS | 不完整 schema、generalized destination 和 malformed row 保持 fatal，audit 分类符合记录。 |
| AC6 | PASS | 76 行 message 全量匹配 audit JSON，未见 240 字符截断。 |
| AC7 | PARTIAL | 80+20 测试、replay、保护差异日志符合声明；same-snapshot 证明不足，`run_evidence.py` 自身 exit 未直接留证。 |

## 4. 残余裁定

r3 audit 为 **1858 declarations / 1264 roots / 76 errors / 236 warnings**。与 r2 audit JSON 的计数和 11 类错误分布完全相同：

- `TABLE_SCHEMA_INCOMPLETE` 44：保留 fatal；另立任务补齐必要列，或由有权责任人明确标记为叙述表。
- `DECL_GENERALIZED` 6、`DECL_ENV` 4：共 10 条，继续保留；具体路径或环境变量语义另行裁定。
- `DECL_DESTINATION_GENERALIZED` 6：继续保留 fatal，缩窄目标或按授权另行处理。
- `FILE_UNREADABLE` 3、`JSON_PARSE` 2：继续保留；在独立范围内修复文件或使用受审阅的精确 path+sha 例外。
- 其余 11 条：`DECL_RELATIVE_UNRESOLVED` 6、`DECL_UNKNOWN_DISPOSITION` 2、`DECL_RELATIVE_AMBIGUOUS` 1、`TABLE_ROW_ARITY` 1、`DECL_DESTINATION_UNRESOLVED` 1。继续保留并按各自来源另立裁定/修复任务。

不建议为满足某个错误数量目标而放宽解析或保护规则。当前 Task 的下一步建议是返修上述 Findings 后再独立复审。

## 5. 运行证据

本次只读命令均为 exit 0：

- `git status --short --branch`：指定 worktree 在审查前后均干净；当前 HEAD 仍为 `31d0705413c48a76b7e8abd07d2dde0acde6f99c`。
- `git diff --name-status f0f19596f...31d0705413c48a76b7e8abd07d2dde0acde6f99c`：改动均落在 Task `allowed_paths`；未见删除或历史文件改动。
- `C:\Python314\python.exe -B -`：只读复算 audit 分类、RESIDUAL 76 行 message、snapshot 元数据、28 项 manifest；均 exit 0，RESIDUAL mismatch 为 0、manifest hash mismatch 为 0。
- 逐条 `git show <commit>:<path>` SHA 校验：30/30 Canonical Evidence pins 匹配，均 pin 到 `2c38980c98385be79e4d67e801a954d698955c80`。
- 只读比较 r2 `a431d7084` 与 r3 audit JSON：计数及 11 类分布一致，exit 0。
- F-01 的纯内存 mock 探针：exit 0；复现 generalized real target 被当成 `DECL_SOURCE_NOT_A_PATH`/`DECL_EVIDENCE_NOT_A_PATH` warning，未写文件。
- 已提交 `new-tests.log` 记录 20/20 exit 0，`existing-tests.log` 记录 80/80 exit 0；两份 replay 日志均记录 15/15 REJECT、0 删除、0 violations，environment 记录 18/18 source。
- `protection-delta.json`：`dropped_declarations` 为 0，旧/新 protected roots 均为 1264。
- `governance-check.log` 记录 exit 1、7 errors / 2 warnings，与 Handoff 数字一致。

`NOT_RUN`：本次未执行 `run_evidence.py`、测试套件、真实 audit、incident replay、`protection_delta.py` 或 `check.ps1`，以免运行会写入夹具、报告或证据的流程。本次未修改文件，也未执行 git 写命令、push、GC 或 prune。