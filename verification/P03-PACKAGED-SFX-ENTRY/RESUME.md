# P03 Codex Integration Resume Point

时间：2026-10-09（Asia/Shanghai）；Task=`P03`；TaskStatus=`in_review`；ExecutionState=`R4_DISPOSITIONS_RECORDED_R5_CANDIDATE_PENDING`。

## 当前权威检查点

- Repository=`G:/CODEX/New Manga`；Git common directory=`G:/CODEX/New Manga/.git`。集成 worktree=`G:/CODEX/New Manga.worktrees/P03-review-prep-85482c5b`；branch=`codex/P03-integration-4c04459`。开始恢复时先读取 live `main`、`git status` 与该 worktree HEAD；不要依据旧聊天状态。
- Task base=`31abde9bf4b73aea2851931dcd48faa0f750b318`；Owner delivery=`85482c5b001d452953c3ed797ce3c4ed64cae4e3`；Owner=Antigravity；非作者 Reviewer=DeepSeek Harness；Integrator=Codex。
- `doc/tasks/P03.md` 与 manifest 将 source integration commit 记为 `d717c049a41544a6d592943a0b0fe1b76a41a050`。R4 报告指出 main 已于 review 前从 `423ea5f1` fast-forward 到该提交；该历史事实已如实记录。后续候选必须按项目 Gate 复审，不把历史 fast-forward 当成 Review。
- DSH R4 session=`session-d27e8ea9-f983-4c1c-9258-a76cdaba0ac0`，base=`31abde9b…`，reviewed head=`d717c049…`，decision=`approved`，未解决 P0/P1=0/0；报告 SHA256=`3a389c2385f5fb7956636b3e94911875f80bc677a4c8673d4f8ec2c294fa755d`，raw JSONL SHA256=`39737ec10538469b8d8fa063b10d3e33f6be998b5fd7c61af0a69cd5d33ff8d3`。会话已挂载到本 worktree；DSH 自身 Git/pytest/Gate 仍为 `NOT_RUN`，Web/Desktop 可见性未核验。
- DSH R4 的 R4-01..06 与 Codex C-004/C-005 已按 Task 逐项处置；R4-07 为不影响行为的 P4 cosmetic，明确延期。固定 head `d717c049` 的 snapshot 16/16、targeted tests 40/40、packaged Gate 28/28 均 EXIT=0；证据为 logs 21–25 与 `raw-finalhead-d717-gate-output.zip`，manifest 记录 SHA。
- `P03` 仍为 `in_review`。R3-03 release-gate 第五 sidecar 遗漏继续登记给 P20，禁止在 P03 中修改范围外 runner 或历史 `main.rs` 注释。
- 恢复链接：[P03 r3 Handoff](../../doc/handoffs/P03-PACKAGED-SFX-ENTRY-140a6686-r3.md)。

## 下一条直接指令

1. 核对 live Git 与本文件：保留根 checkout 原有24项用户/Qoder/其他 Agent dirty 与 raw evidence；保护 worktree 的 untracked Gate 输出目录；只操作 P03 显式文件。
2. 读取 `integration/build-logs/21–25`、R4 prompt/report/raw/exit、`build-manifest.json` 和两份 RESUME。确认这些文件与当前 branch 的准确关系。
3. 在完全解决 R4 finding 的 P03 候选上重跑 `git diff --name-only 31abde9b..HEAD`、`git diff --check 31abde9b..HEAD` 和两份只读 normalization verifier；记录 shell、HEAD、路径数、EXIT。复核 AC1–AC4、同一 installer SHA、零越界和所有声明来源。
4. 按 [DSH dispatch Skill](C:/Users/49745/.agents/skills/dsh-dispatch/SKILL.md) 对该 exact HEAD 发起正式 DSH R5，并由已分配的 Codex 非作者 Reviewer 独立检查同一 base/head；新 finding 先修复、验证、固定新 head 后再审。
5. Review/Gate 全通过后，Codex 才能集成并把 P03 设为 `done`；按 live Plan 和依赖图重新核对后创建、冻结并释放 P01（Owner=Codex、Reviewer=DSH），更新 Task/Plan/Status/依赖图/RESUME。P01 缺失报告记 `NOT_VERIFIED`，不伪造 Review；R2 空集与 T2 释放等产品选择不由 Codex代决。
6. 保存下次自动推进提示词；P01 到 `ready` 后，将该提示词发给下一次 Codex 会话。当前会话的关机授权仅在本轮 P03 与恢复资料收口后执行，不延伸到下次会话。

## 保护边界

- 主 checkout `.qoder-credits/**`、既有 P03 DSH R2 原始材料、P08 DSH raw、Runner Guard dispatch artifacts、Root dirty files 与 Antigravity Owner worktree 的文件由其作者保留；不 stage、改写、stash、覆盖或清理。
- 不修改 `src/**`、`apps/**`、Schema、contracts、依赖、build spec/script；K07 与 ONNX 外部输入只读；不读写用户漫画文件、真实数据库、Lock 或 current/pinned Revision。Gate TEMP 和输出目录仅保留作恢复证据，不删除。
