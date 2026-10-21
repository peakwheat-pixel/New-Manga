---
task: WORKSPACE-CLEANUP-TOOL-HARDENING-1-REVIEW-R3
reviewer: Codex
author: dsh-workspace-hardening
base_commit: b8a1e519703f13af73b320dded117004b4bb189a
reviewed_head: 59f401143
implementation_head: 30946decf
decision: changes_requested
review_mode: read_only
---

## 1. 结论（F-02/F-05）

**F-02：运行时修复成立，源码说明尚未修完。** 扫描范围内的 JSON 读取或解析失败会无条件记为 `JSON_PARSE` 并拒绝清理；MIGRATE、ARCHIVE、无 marker 三个夹具都通过真实 CLI，断言 exit 2 且候选仍存在。但 `scan_repo_declarations` 的 docstring 仍说无 `PRESERVE` marker 的 malformed JSON 只记 warning，与实现及 Handoff 相反。该文档矛盾列为 R3-F02-DOC，阻塞批准。

**F-05：通过。** `30946decf` 同时包含最终 `governance-check.log` 与 `manifest.sha256`。我逐项核验了 27 条 evidence 行：工作区文件 SHA-256、行内 SHA-256、`30946decf:path` blob 内容 SHA-256 全部一致，且 commit 中都有对应文件。manifest 的 11/11 项也与工作区和 commit blob 一致；manifest 不自列，Task 没有自 pin 或 SHA-only 行。日志为 LF（CR=0），与 Handoff 的 LF 归一说明一致。`30946decf..59f401143` 只改了 Task 和 Handoff；`b8a1e519..30946decf` 的 26 个变更路径均在 `allowed_paths` 内。

Handoff 的审计口径已修正：7392 tracked + 1504 untracked 是**枚举路径数**；2271 `.md` + 1147 `.json` 是**实际解析文件数**。

## 2. Findings

### R3-F02-DOC — P2：扫描函数说明仍写着旧的 malformed JSON 规则

[clean_workspace.py](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tools/governance/clean_workspace.py:1161>) 声称含 `PRESERVE` marker 的 malformed JSON 才是 fatal，无 marker 则记录 warning；实际代码对扫描范围内的解析失败一律登记 `JSON_PARSE` 并拒绝清理。

请将该 docstring 改为与当前规则一致：扫描范围内任何 JSON 解析失败都是完整性错误，与 disposition marker 无关。保留矛盾说明会误导后续维护，并可能把本轮修复的安全规则改回旧行为。MIGRATE、ARCHIVE 和无 marker 的 CLI 夹具见 [test_tools_fixtures.py](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-CLEANUP-TOOL-HARDENING-1/verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/test_tools_fixtures.py:653>)。

## 3. AC1–AC7 判定

| AC | 判定 | 核验摘要 |
|---|---|---|
| AC1 | MET | 路径身份、父子覆盖和 junction 保护有对应测试及记录。 |
| AC2 | MET（运行时） | JSON 失败一律拒绝；新增三种 malformed JSON 真实 CLI 反例通过。源码 docstring 矛盾见 R3-F02-DOC。 |
| AC3 | MET | 80 项测试记录覆盖逐文件 size/SHA 清册与 apply 门禁。 |
| AC4 | MET | 新增 malformed JSON 夹具通过；exit 2，候选目录仍存在，未删除。 |
| AC5 | MET（夹具验证） | 默认 dry-run、release-window 和 apply 行为在隔离夹具验证；真实仓库 apply 未运行。 |
| AC6 | MET | 两个回放报告均为 15/15 REJECT、0 删除、0 violations，且覆盖 18/18 source。 |
| AC7 | MET（保留既存失败） | 新测试 80/80、`test_ac_gate.py` 12/12；既有 `run-resource-manifest-cases.py` 如实记录为 0/32、exit 1，未宣称通过。 |

## 4. 是否可进入集成

**目前不可进入集成。** 总体决定为 `changes_requested`，需要先修正 R3-F02-DOC，再以新 head 请求复审。

真实仓库审计记录 163 条完整性错误，包括 69 条 `JSON_PARSE`、57 条 `DECL_BARE_NAME` 和 7 条未解析 destination；工具因此 exit 2、fail-closed。这是未解决的仓库声明风险，不是成功获得清理授权。其他保留限制也如实列出：扫描纳入 1504 个非忽略 untracked 声明路径；guard core 位于 `clean_workspace.py`；apply 只在 `%TEMP%` 夹具验证；进程占用检查未实现。

主仓库 `STATUS` 仍记此 Task 为 `ready`、Owner 返修中及 Codex R1 `changes_requested`；本审查只绑定目标分支的 `59f401143`，没有修改状态文件。

## 5. 运行证据

**本轮实际执行的只读核验：**

| 命令/核验 | 结果 |
|---|---|
| `git rev-parse HEAD`、`git status --short --branch`（目标 worktree） | exit 0；HEAD=`59f401143de1ef0679805aa8609a30d7449583ee`，worktree 干净。 |
| `git diff --name-only 30946decf..59f401143` | exit 0；仅 Task、Handoff。 |
| `python -B -` 内联只读 Git blob、27 行 pin、manifest SHA 核验 | exit 0；27/27、11/11 全部一致。 |
| `python -B -` 内联读取已冻结日志与 AC 报告 | UTF-8 版本 exit 0；确认审计错误明细 163 条及其分类、回放结果和测试记录。首轮摘要脚本因 Windows GBK 控制台无法编码日志字符而 exit 1；仅输出失败，未写文件，修正编码后核验成功。 |

**本轮未运行测试或治理检查（NOT_RUN）；以下是对冻结证据的读取结果：**

| 项目 | Reviewer 本轮 | 冻结记录 |
|---|---|---|
| 新测试套件 | NOT_RUN | exit 0；80 tests，80 项 JSON 结果均为 `ok`。 |
| 两个事故回放 | NOT_RUN | 各 exit 0；15/15 REJECT、0 删除，18/18 source 覆盖。 |
| 真实声明审计 | NOT_RUN | 预期 exit 2；JSON 中有完整 163 条错误明细，工具 fail-closed。 |
| `test_ac_gate.py` | NOT_RUN | exit 0；12/12 cases behaved as specified。 |
| `run-resource-manifest-cases.py` | NOT_RUN | exit 1；0/32，记录为既存 `TASK_LEDGER` / `check.ps1` 仓库状态失败。 |
| `check.ps1 -TaskPath ...` | NOT_RUN | 冻结日志 exit 1；5 errors、4 warnings。没有将其表述为通过。 |

R2 Review 未找到独立的仓库文件；本轮依据用户提供的 R2 findings，并核对 Task/Handoff 中对应记录。审查期间未执行真实删除、移动、分支清理、GC、prune 或 push，也未执行 Git 写命令；最终 worktree 状态仍干净。

**推荐下一步：** 修正 `scan_repo_declarations` 的 docstring，以新 head 请求复审；在重新获批前不要进入集成。