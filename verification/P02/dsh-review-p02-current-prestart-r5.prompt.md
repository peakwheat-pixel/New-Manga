# DSH 独立 Review：P02 current prestart R5

## 任务与角色

你是本切片的独立、只读 Reviewer；本轮实现/文档修复由 Codex 完成。请从 detached review worktree 的实际 `HEAD` 开始，记录完整 `git rev-parse HEAD`、`git rev-parse 'HEAD^{tree}'`、parent 和 expected base=`4183e7f7cf366c27aa8ad8a0bc7300af48783470`。如果 HEAD/tree 无法固定，或完整差异超出下述允许范围，请停止并返回 `BLOCKED`。

当前父 Task=P02（唯一 Active 产品验证 Task）。本 Review slice 是 R4-01/02 的文档/证据修复。Owner=Codex；Reviewer=DeepSeek Harness；Integrator=Codex。候选分支=`codex/P02-process-isolation`；候选 worktree=`C:\Users\49745\.codex\worktrees\p02-process-isolation-plan\New Manga`。允许修改路径为 `doc/00_INDEX.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/P02.md`、`verification/P02/**`。禁止本 Review worktree 产生任何变更。

## 必查内容

1. R4-01：核验 R2、R3、R4 response metadata 中的 `response_sha256` 是否等于对应 committed Git blob bytes 的 SHA-256；检查计算口径明确为 UTF-8 LF。确认原始 DSH worktree 混合 EOL hashes 使用独立字段表达，且没有把 raw hash 冒充提交工件 hash。
2. R4-02：核对 `doc/00_INDEX.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md` 当前指针均指向 R5 package checkpoint；R4 与 R1–R3 的结果保留为历史，不得称其为当前状态。
3. 核对 R6 scope assertion 的 `hard_build_barrier_preserved=False / EXIT=1` 与 R7 `wsb start` 状态断言 `EXIT=1` 均原样保留、原因有证据且没有被描述成 PASS。确认 D12/R8 修正后 scope/status assertion 实际 EXIT=0，Index 明确写出 `wsb start=NOT_RUN`。
4. 核对 Build Gate=`BLOCKED`、build=`NOT_AUTHORIZED / NOT_RUN`、hook/cache=`BLOCKED / NOT_VERIFIED`、AC1–AC7=`BLOCKED / NOT_RUN`、Hard Build Barrier=`EFFECTIVE`，且无文档暗示 Sandbox、Smoke、Build、GUI 或产品测试已经运行。
5. 独立测量 expected base 到 exact HEAD 的完整变更路径数和 out-of-scope 数。允许路径严格限于上述四份 docs 和 `verification/P02/**`。

## 必须独立执行并报告 exit

- `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`
- `git diff 4183e7f7cf366c27aa8ad8a0bc7300af48783470 HEAD --check`
- `git diff HEAD^ HEAD --check`
- `git diff --name-only 4183e7f7cf366c27aa8ad8a0bc7300af48783470 HEAD` 并审核全部路径。

禁止运行 `wsb start`、Sandbox/guest commands、HostFolder 内容扫描/列表/哈希、Build、GUI 或产品测试。不得读取任何 DSH `*.stderr.txt` 文件、raw JSONL thinking/tool logs。缺少证据必须标为 `NOT_RUN`、`BLOCKED` 或 `UNKNOWN`，不可写成 PASS。Review 完成后不要改文件。

## 返回格式

- Decision：`APPROVED`、`CHANGES_REQUESTED` 或 `BLOCKED`。
- exact HEAD/tree、base、所有命令 exit、完整 diff path count、out-of-scope count。
- P0/P1/P2/P3/open 计数；逐项 findings 含 ID、severity、path:line、影响、最小修复。
- 覆盖范围与 `NOT_RUN` / `BLOCKED` / `UNKNOWN` 项；明确确认没有运行 Sandbox、HostFolder scan/hash、Build、GUI、产品测试，也没有读取禁止的 DSH 原始日志。