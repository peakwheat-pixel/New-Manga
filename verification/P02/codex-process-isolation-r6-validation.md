# P02 Process Isolation r6 N-04/N-05 修订验证记录

- 时间：2026-10-09 15:34 UTC（2026-10-09 23:34 Asia/Shanghai）。Owner=Codex；非作者 Reviewer=DeepSeek Harness；Integrator=Codex。r6 base=`1c7efb172b8e9d766e38f84cf3728a90bb5953d0`；candidate commit 固定后补录。
- r5 formal Review=`APPROVED_WITH_CONDITIONS`（仅设计，P0/P1/P2/P3=`0/0/0/2`），N-04/N-05 是唯二条件；r6 范围见 scope delta § r6。

| Check | Result | Evidence |
|---|---|---|
| N-04 exact permission | PASS | r5 extension 文件许可现明确允许追加 r5 extension，并只就地扩写 r3/r4 extension 中 r3-start 原 :52 许可行（不改其他既有文字）；scope delta 的 r6 extension 再精确列明此改动。 |
| N-05 EOF repair | PASS | scope delta 移除末尾字面两个字节 `` `n ``，保留 UTF-8 文本并以单个 LF 结束；无末尾空行。 |
| Scope audit | PASS | 实质文档差量仅 `verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md` 的 r5 N-04许可、N-05 EOF 与新增 r6 scope；其余 changed/untracked files 仅 r5/r6 审计附件。P02 Task、plan、host inventory、STATUS、REBASELINE_PLAN、Owner allowlist、产品/契约均未修改。 |
| Project route validator | EXIT=0 | `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`：196 unique nodes、依赖与分类、21 planned nodes DAG、路线状态和链接通过；产品 tests/build/GUI=`NOT_RUN`。 |
| Whitespace | EXIT=0 | `git diff --check 1c7efb172b8e9d766e38f84cf3728a90bb5953d0` 无 whitespace error；仅 `core.autocrlf` LF→CRLF warning。 |
| Frozen r3 Sandbox config | UNCHANGED | base 与 working file 均 2609 bytes，SHA-256=`9af445134c6c6d3cec900b6d5c903a3c7fe19a104e0eab10f7c0886280de664d`，逐字节相同。 |
| Root protected manifest | MATCH | `G:/CODEX/New Manga`=`main@549a6544f0be1eec66c09ece393fd1a409f10bf3`；203/203 path/status/kind/size/SHA-256 matches；missing/extra/mismatch=0；staged=0；canonical entries SHA-256=`3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`。本轮 author changed/untracked paths 与 root dirty paths overlap=0。 |

## 未执行与精确 Gate 状态

未查询/更改 Windows Feature，未提权，未启动/连接 Sandbox，未运行 Smoke/build/runner/Vitest/GUI/WebView 或任何产品 AC。Windows Sandbox Feature=`UNKNOWN`；Smoke admission=`NOT_ADMITTED`；Smoke=`NOT_AUTHORIZED / NOT_RUN`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；P02 AC1–AC7=`BLOCKED / NOT_RUN`；Hard Build Barrier 继续有效。上述检查不能推导运行态 Gate 或产品验收。

## 下一步

提交 r6 candidate 后在 clean detached worktree 派 DSH exact-head 非作者 Review，确认 N-04/N-05、r5 evidence 完整性与 r3 XML hash。仅在 Review 通过并已记录后集成，再做集成后路线/文档检查；之后按批准范围执行本机非提权只读 preflight。
