# M2-TA2C → ZCode 中断交接（2026-09-29）

## Recovery / ownership

- TaskStatus=`in_review`；ExecutionState=`CHECKPOINTED`；用户明确要求交接给 ZCode。
- 实现作者/原 Owner=Codex Desktop；**后续执行者=ZCode（用户指定，代行 Codex 集成职责）**；非作者 Reviewer=DeepSeek Harness，Owner != Reviewer 继续成立。不得把 ZCode 的接手续作写成原始实现作者，也不得由作者自审。
- 主仓库 `G:/CODEX/New Manga`：`main@7b198e52a5fa1ff2049538f3be7d303c5ff4eabb`（交接时实测，含 release 与 active 状态）；主工作区有其他作者既存 dirty/untracked 文件，快照 `main-preintegration-status.txt`，不得覆盖、stash 或清理。
- Task linked worktree=`C:/Users/49745/.codex/worktrees/no-hf-comic-assets/New Manga`；branch=`agent/codex/M2-TA2C-no-hf-assets`；Git common dir=`G:/CODEX/New Manga/.git`；固定 base=`d4d3977907bc64177ef85c61da4c95901f135fc6`；release=`ff2dee6c0dc0a20991dd2bfc3436b690d091e6e4`；当前交付 HEAD=`8cb3a135c58d7a7a7b3d07fc5bba75c17aa6deb7`（本 checkpoint 另作元数据提交，先以 `git rev-parse HEAD` 复核）。
- 当前 tracked 工作树干净；有 DSH 复审转录 `verification/M2-TA2C/dsh-review-r2.{jsonl,err.log}`、`dsh-review-r2b.{jsonl,err.log}` 未跟踪。r2 续接会话 EXIT=1，`INVALID_REQUEST 422`，final 为空，**不是有效 Review**。r2b 为新独立会话，在交接检查时 PID=63960 仍运行并写 `dsh-review-r2b.jsonl`；检查该进程是否结束及输出最终状态，不能把半截 JSONL 当 verdict。
- DSH r1 固定被审 HEAD=`2c12ba1e`，真实结果 `changes_requested`（0×P0/P1、2×P2、7×P3），见 `doc/reviews/M2-TA2C-2c12ba1e-dsh-r1.md`。P2-1/P2-2 已在 `93f7b4b4` 修正，`0676865b` 加断言；P3-2 提前校验实验令 1 个测试失败，已撤回，最终 HEAD=`66dc361d` 的 25 项测试 PASS。新 Handoff=`doc/handoffs/M2-TA2C-66dc361d.md`，Handoff HEAD=`8cb3a135`，需完成新固定 HEAD 独立复审。

## 已完成 / 真实资产

- 单一套件 `test_assets/comic_golden_suite`；附件 ZIP SHA-256、静态风险见 `attachment-audit.md`，**未执行附件脚本**。
- 原有 KO Cleaned Webtoon 10 Case / 80 文件 / 884,913,245 bytes、原有 JA Pepper&Carrot 10 页 + 2 ZIP / 12 媒体文件 / 40,284,868 bytes 均保留；没有从 HF 重取 844 MiB。
- 新 KO Pepper&Carrot E04P02/P03/P07 三张 JPEG + 官方 language-pack ZIP，共 4 文件 / 16,292,579 bytes，位于 Task worktree ignored `韩漫_KO/02_public_ground_truth_peppercarrot/ep04/`；三页 `READY` 仅资产完整性。主工作区此新增 KO 目录**尚未复制**，集成后需非覆盖复制并核对 SHA-256/大小。
- inventory 92 文件 / 63,317,229 bytes，逐文件 SHA-256；KO Webtoon 80 文件 SHA-256 另见 `ko-webtoon-audit.json`。L0 20 定义/20 READY；L1/L2 各 68 定义/23 READY/8 MISSING/37 MISSING_GATED_ASSET。应用 Pipeline 共 577 段全部 `NOT_RUN`；OpenMantra 因 CC BY-NC 使用范围不明 0 文件，Manga109/eBDtheque/TextMasks 等按真实访问状态保留，Artificial Manga code-only 不计可运行。

## 已运行 / 剩余验证

- 作者 fixed code HEAD=`66dc361d`：`python -m pytest tests/m2_test_assets -q` → 25 passed，EXIT=0（`pytest-assets-r2.log`）；`asset-cli-r2.log` → JA10/KO10 Smoke、KO 新3 READY，regression 23/8/37，重复下载 downloaded=0，全部 EXIT=0。
- `python -m pytest tests/m2_acceptance -q --tb=no` → 与接手前完全相同失败集合，8 failed / 24 passed / 3 skipped，EXIT=1，`BASELINE_FAILURE`（`acceptance-baseline.log` / `acceptance-r2.log`）。`tests/core` 因 PySide6 缺失 4 collection errors、1 skipped，EXIT=2，`BLOCKED_BY_ENV`（`core-environment-detail.log`）。
- r1 DSH 在沙箱因 pytest `tmp_path` WinError 5 不能独立全跑，`NOT_RUN/BLOCKED_BY_ENV` 如实记录；它独立复算本地资产/ZIP/hash/ignore，结果通过。
- 剩余：取得有效 r2 Reviewer verdict；如 `approved`，记录报告和 findings disposition，按治理规则集成 branch→main，复制新 KO ignored 文件，主线复跑资产测试、CLI、Git ignore/媒体跟踪、acceptance 失败集合对照，更新 Task/STATUS/Plan/Index、Handoff/integration evidence，再置 `done`。若 `changes_requested`，按新 findings 返修并重新审查。禁止在有效独立 Review 前合并或宣称批准。

## 风险、清理与恢复安全

- 本轮 DSH 新会话的转录文件在工作区异步写入，接手前核验 `git status --short --branch`、`git rev-parse HEAD`、`Get-CimInstance Win32_Process` 是否仍有该 PID，确定最新原始输出和 EXIT；无进程但缺最终 `final`/EXIT=0 则标 Reviewer `NOT_RUN` 并重新派发。
- DSH r1 留空 `.dsh-review-tmp/`；本会话尝试删除该目录和空 stderr 文件时，命令被自动策略拒绝（blocked by policy）。目录不在 Git 跟踪/状态中，无需冒险绕过；r1 空 stderr 已作为证据提交。r2/r2b 的 raw/err 待最终确定后由 ZCode 在 Task 范围内按可用工具处理，不要删除部分转录来伪造 Review。
- 不改生产 Schema/migration/Pipeline/Provider/UI/依赖/Library，不执行附件脚本，不下载 gated/许可不明内容，不把任何漫画原图或 ZIP `git add -f`。

## 下一精确步骤

1. 只读确认 r2b 进程已结束，解析 `dsh-review-r2b.jsonl` 的 `session`/非空 `final`、记录 CLI EXIT 与 reviewed_head。若仍运行，等待其完成；若 422/空 final，另派独立非作者 Review 或记 reviewer_unavailable，不得集成。
2. 有效 r2 verdict 若 approved，复核其固定 HEAD=`8cb3a135`、P2-1/P2-2 closure 与未解决问题；在 `doc/reviews/` 存档报告、在 Task 记录状态。若有 P0/P1/关键验证缺口则返修。
3. 在 `main` 仅对授权路径串行集成；主工作区 preexisting dirty 文件保持原字节。新 KO ignored 4 文件从 Task worktree 安全非覆盖复制，SHA-256 对 `local_asset_inventory.json`，集成后复验并留下 raw EXIT 日志。
