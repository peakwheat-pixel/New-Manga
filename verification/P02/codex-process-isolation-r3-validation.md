# P02 Process Isolation r3 候选验证记录

- 时间：2026-10-09 14:42:15 UTC。
- 作者 branch=`codex/P02-process-isolation`，pre-delivery HEAD=`3555213a748a7b407400589e1490a387353dec16`；live root=`main@549a6544f0be1eec66c09ece393fd1a409f10bf3`。本文件记录文档/配置验证，不是产品或 Sandbox 运行结果。
- 当前 author status=`18` 项，所有差量仅在 `doc/tasks/P02.md` 的 Codex-only boundary 和 `verification/P02/**`；没有 staged content。

| Check | Exit | Evidence |
|---|---:|---|
| Project route validator | 0 | Planning snapshot base=e4242ecd419eb0eea098d2f63b40f709aa5caeea; live HEAD=3555213a748a7b407400589e1490a387353dec16; PASS: 196 unique nodes, all classifications and dependency references; PASS: 105 new architecture/governance integration records are audit-base ancestors; PASS: live P01/P02/P03/P08 Task states match the Plan; remaining P nodes stay proposed; PASS: every roadmap P-node declaration matches the Plan state; PASS: 21 unique planned nodes and roadmap graphs have no dependency cycles; PASS: delivery/navigation local links resolve; PASS: zero P01 production/code delta; P02 task-local E2E driver excluded; governance whitespace check; Product tests/build/GUI: NOT_RUN (planning-only) |
| git diff --check | 0 | EXIT=0; no whitespace errors |
| r3 WSB config assert | 0 | PASS: 11 mappings (1 RW/10 RO), canary host is inside scratch clone, bytes=2609, SHA-256=9af445134c6c6d3cec900b6d5c903a3c7fe19a104e0eab10f7c0886280de664d, no LogonCommand |
| r2 canonical hash erratum | 0 | PASS: 8/8 Git blob SHA-1 + canonical UTF-8/LF SHA-256 rows match reviewed r2 commit 3555213a |
| root protected manifest | 0 | PASS: 203/203 entries; missing/extra/mismatch=0; entries SHA-256=3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2; main@549a6544f0be1eec66c09ece393fd1a409f10bf3 |
| DSH r2 review record | 0 | PASS: review checkout clean at 3555213a748a7b407400589e1490a387353dec16; raw JSONL external size=431099, SHA-256=e59473d78b491a6bba66df69480ed8eb5fd032c6d2a73476e5e59f45ee2f1f1a |

## 未执行项

- Windows Optional Feature 查询、`wsb start/connect/exec`、Windows Sandbox、Smoke、Build、P02 runner、Vitest、GUI、WebView 均未运行。Sandbox feature 仍 `UNKNOWN`。
- 因此 Isolation Smoke=`NOT_AUTHORIZED / NOT_RUN`，Build Gate=`BLOCKED`，build=`NOT_AUTHORIZED / NOT_RUN`，P02 AC1–AC6=`BLOCKED`，Hard Build Barrier 有效。
- 路线 validator 属规划/治理自检，不构成产品构建、P02 AC 或隔离 Smoke 证据。
