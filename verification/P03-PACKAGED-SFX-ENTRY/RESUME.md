# P03 Codex Integration Resume Point

时间：2026-10-09（Asia/Shanghai）；Task=`P03`；TaskStatus=`in_review`；ExecutionState=`R6_APPROVED_CODEX_INTEGRATION_PENDING`。

## 当前权威检查点

- Repository=`G:/CODEX/New Manga`；Git common directory=`G:/CODEX/New Manga/.git`。集成 worktree=`G:/CODEX/New Manga.worktrees/P03-review-prep-85482c5b`；branch=`codex/P03-integration-4c04459`。恢复后先核对 live `main`、worktree HEAD 与两个 checkout 的状态。
- Task base=`31abde9bf4b73aea2851931dcd48faa0f750b318`；Owner=Antigravity；Reviewer=DeepSeek Harness；Integrator=Codex。现有主线 integration commit=`d717c049a41544a6d592943a0b0fe1b76a41a050`。
- DSH R5 session=`session-089283e0-246f-44e3-9c2f-14dea850e4e2` 对 exact head=`7677e9c324da2fde618e7cd6fdba2363abeb1f1b` 作出 `approved`；未解决 P0/P1/P2=0/0/0，P3=1、P4=4。报告、原 prompt、JSONL、stderr、exit 已归档并挂载。DSH 自身 shell/Git/tests/Gate=`NOT_RUN`（Win32 5），Web/Desktop visibility=`unverified`。Codex 非作者独立复审同一 head 未发现新 P0–P3。
- DSH R6 session=`session-21ca547a-c9ba-4b60-9e9c-afe54db7009a` 对 exact head=`f09100d5b96aea26e4f525fb4c7c10d6d9d9f1cb` 作出 `approved`；未解决 P0/P1/P2=0/0/0，P3=2、P4=3。报告/prompt/raw JSONL/stderr/exit 已保存并挂载；DSH 自身 shell/Git/tests/Gate=`NOT_RUN`（Win32 5），Web/Desktop visibility=`unverified`。Codex 非作者独立复审同一 head 未发现新 P0–P3。
- Exact-head evidence：log 28 = 146 paths、zero out-of-scope、diff-check EXIT=0；log 29 两个只读 normalization verifier 均6/6、EXIT=0；log 30 对 d717 Gate ZIP 11 项逐一与保留目录 byte comparison，全相同、EXIT=0。Hashes 在 manifest。
- R6 exact-head log 31 = 155 paths、zero out-of-scope、diff-check EXIT=0；R6-02 要求 Codex AC5 收口时更新六份当前导航/状态文档，不能沿用“R5待审”字样。
- Source code remains `d717c049`；logs 23–25 bind snapshot 16 actual-predicate PASS、targeted tests 40 passed / 0 skipped、same-installer packaged Gate 28/28 PASS，均 EXIT=0。Product runner/test blobs relative to d717 are unchanged。
- Root checkout's 24 dirty/untracked entries and the two retained untracked raw Gate directories are protected。P03 remains `in_review` until Codex completes integration AC5。
- 恢复链接：[P03 r3 Handoff](../../doc/handoffs/P03-PACKAGED-SFX-ENTRY-140a6686-r3.md)。

## 下一条直接指令

1. 核对 live root/worktree Git 与权威 Task/Plan/Status；保留根 checkout 原有24项用户/Qoder/Agent dirty 和两个 raw Gate 输出目录，不 stage、改写、stash 或清理。
2. 核对 R5/R6 报告/prompt/raw/exit hashes、Codex review、manifest 与 logs 28–31。不要重复运行 40 tests、16 snapshot 或 28-case installer Gate：runner/test blobs 相对已验证的 `d717c049` 零变化。
3. 完成 Codex AC5 integration check，并更新 STATUS、REBASELINE_PLAN、00_INDEX、tasks/README、12_ROADMAP 和派生 ROADMAP；核实候选祖先与差量、installer/source 同一 SHA、范围与 `git diff --check`，通过后 fast-forward、记录真实 integration commit，Task/P03 置 `done`。
4. 按权威 Plan 重核依赖，创建并释放 P01（Owner=Codex、Reviewer=DSH），同步 Plan/Status/索引/依赖图/恢复点。P01 缺失的独立报告记录 `NOT_VERIFIED`；R2 challenge 空集与 T2 release 产品决定保留给用户。
5. 保存下一次自动推进提示词和恢复点。本会话的关机授权只在 P03 完成及恢复资料保存后执行，不延伸到下次会话。

## 保护边界

不修改 P03 allowed_paths 以外的产品代码、K07/ONNX 外部输入、用户漫画源文件/数据库/Lock/current-pinned Revision、Qoder 历史或其他 Agent dirty。禁止 push、外发、部署、删除或清理。
