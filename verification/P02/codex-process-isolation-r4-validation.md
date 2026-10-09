# P02 Process Isolation r4 候选验证记录

- 时间：2026-10-09 15:04 UTC（2026-10-09 23:04 Asia/Shanghai）。
- Owner=Codex；Reviewer=DeepSeek Harness（非作者）；Integrator=Codex。pre-review author HEAD=`92361e3578eedb93d7cf6c4c5a4db06652d31fe9`，r4 文档尚未提交；r3 `wsb` XML 保持不变。

| Check | Result | Evidence |
|---|---|---|
| Project route validator | EXIT=0 | `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`：196 unique nodes；依赖引用/节点分类/路线状态/导航链接通过；21 个 planned nodes 无循环。输出中的 live HEAD 是 r3 committed base `92361e3`；该工具不是产品测试。 |
| Whitespace/diff check | EXIT=0 | `git diff --check` 无 whitespace errors；Git 仅提示 `core.autocrlf` 将把当前 LF 工作树文件转为 CRLF。 |
| Frozen r3 config | PASS | canonical UTF-8/LF=2609 bytes，SHA-256=`9af445134c6c6d3cec900b6d5c903a3c7fe19a104e0eab10f7c0886280de664d`；XML parse=11 mappings / 1 RW / 10 RO，无 `LogonCommand`；含 VS/Installer/SDK RO roots，不含 Git mapping。 |
| Clone sequence | PASS | P02 Task boundary、proposal setup、proposal Smoke step 2、Build plan 4 处抽取出完全相同的 4 命令：clone flags/source/destination、`remote remove origin`、`core.autocrlf true`、固定 `checkout --detach`。 |
| Manifest schema self-check | PASS | 以三种记录（root directory、fully hashed file、metadata-only file）断言固定字段、类型、`null`/hash-state 组合、64-char lowercase SHA-256 与 canonical minified UTF-8 JSON 无 BOM。此为 schema 自检，未生成/采集运行时 HostFolder manifest。 |
| r3 checkpoint erratum | PASS | `git show 92361e3:<addendum>` 精确为 4790 bytes / SHA-256=`dfaa8ecc8e49f5c70e1835d5adeb23a2a4da76e09ec94fe4c39ddf9cbc107c47`；start snapshot 与 delivery 值并列记录；start checkpoint 不再声称 delivery artifacts 未修改。 |
| Root protected manifest | PASS | 203/203 status/path/size/SHA-256 匹配；missing/extra/mismatch=0；canonical entries hash=`3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`；validation record 写入后的 author 当前 18 个 changed/untracked paths 均在授权范围，且与 root 203 项交集=0。 |
| Scope audit | PASS | 当前 author 变更仅 `doc/tasks/P02.md` 的 `Codex-only scratch-build output boundary` 段与 `verification/P02/**` 子任务附件；scope extension 冻结至 R4 Review。 |

## 未执行及下一步

- 未查询/更改 Windows Feature，未提权、启动/连接 Sandbox、执行 Smoke、产品 build、runner、Vitest、GUI 或 WebView。
- Feature=`UNKNOWN`；Smoke=`NOT_AUTHORIZED / NOT_RUN`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；P02 产品验收仍 BLOCKED；Hard Build Barrier 有效。
- 下一条准确动作：显式 stage 本 scope 文件，固定 r4 commit 和 delivery checkpoint；在新的 clean detached review worktree 对精确 commit 派 DSH exact-head review。复审通过也只允许后续非提权只读 preflight；任何 Sandbox/Smoke/Build 仍需独立 Gate。
