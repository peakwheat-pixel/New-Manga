# M2-FIX-EXPORT-LINEAGE 集成记录（integration-d395ef70）

- 日期：2026-09-29（本地 +08）
- 集成者：**Codex（代行，ZCode 子 agent 会话，用户授权 2026-09-28）**；Owner=ZCode（另一子 agent），**Owner≠Integrator 保持**。
- 集成方式：`git merge --no-ff agent/zcode/M2-FIX-EXPORT-LINEAGE` 进 main，无冲突。
- **integration merge = `d71883ec9a6c6fccb14b62908c02790bb3beb99c`**（parent1=`aa1e0c7c` release，parent2=Owner 最终 tip）。
- Owner 分支 ledger：base=`8b0d9040` → claim `4e76b2fa` → 交付 `0ec1f052`（r1 delivery_head，dangling 可达）→ r2 amend 重建 `297c9655`（delivery_head）→ r2 回填 amend 链 `db975e7a → f412cd47 → 46a444c8 → d395ef70`。
- merge 载荷：13 文件，879 insertions / 29 deletions；`src/application/export/service.py` +32/-? 行（方案 A）、`tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py` +142/-?（F-1 xfail 移除 + legacy 三通道场景 + C5 断言）；`reading_export.py`/`schema.py` 零改动（merge diff 无此二文件）。

## 1. Review 链（双轮，均为 DSH 非作者 Review）

| 轮次 | 对象 | 结论 | 报告（本仓归档） | SHA256 |
|---|---|---|---|---|
| r1 | `0ec1f052`（r1 delivery_head） | `approved_with_conditions`（代码层 approved；证据层条件 C1-C6） | [doc/reviews/M2-FIX-EXPORT-LINEAGE-0ec1f052-dsh-r1.md](../../reviews/M2-FIX-EXPORT-LINEAGE-0ec1f052-dsh-r1.md) | `4914deeca0f541c49c53dcd52c020ad084df0067ddcd6b63f927036290d8a63c` |
| r2 | `297c9655` + 回填 tip | **`approved`**（C1-C6 全部真实关闭；无 P0/P1/P2；3 条 P3 N1-N3 由集成收口） | [doc/reviews/M2-FIX-EXPORT-LINEAGE-d395ef70-dsh-r2.md](../../reviews/M2-FIX-EXPORT-LINEAGE-d395ef70-dsh-r2.md) | `957062103489de64d790098c3a94ceb6b4a5391c3e884c730c59f65bc6f87e48` |

两份报告均为原字节复制（`cp` 后 sha256sum 源/目标一致）；原始会话产物在 `/tmp/m2fixexp-review/`（非持久）。

## 2. DSH r2 §4 not_verified 八组代跑（集成方执行）

环境：Git Bash（bash 5.2.37，MINGW64）、Python 3.12.3（`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`）、run-at HEAD=`d395ef70b311b0d960cddcb0680e9fc423c0b09c`、branch=`agent/zcode/M2-FIX-EXPORT-LINEAGE`、worktree 工作区干净。日志（带头：shell/解释器/HEAD/branch/ISO/命令；带尾：EXIT）：[raw/](raw/)。

| # | 命令（DSH r2 §4 原样） | 期望 | 实测 | EXIT | 日志 |
|---|---|---|---|---|---|
| ① | `git rev-parse HEAD && git log -1 --format='%H %cI %s'` | HEAD=`d395ef70…` | `d395ef70b311b0d960cddcb0680e9fc423c0b09c`，%cI=2026-09-29T01:43:21+08:00 | 0 | [integ-1-tip-identity.log](raw/integ-1-tip-identity.log) |
| ② | `git diff --check 8b0d9040..HEAD` | 空输出 EXIT=0 | stdout 0 字节 | 0 | [integ-2-tree-diff-check.log](raw/integ-2-tree-diff-check.log) |
| ③ | `git diff --ignore-all-space 0ec1f052..297c9655 -- …/raw/`（+无 `-w` 对照） | Proof1 空；对照仅空白删空 hunk | Proof1 空输出；对照 hunk 全为 `-   `→`+`（red:46/56/59、regression-final:35/54/69，traceback 文案逐字保留） | 0；对照 `--quiet` EXIT=1（有差异，符合预期） | [integ-3-cleanup-equivalence.log](raw/integ-3-cleanup-equivalence.log) |
| ④ | `git diff --name-status` + `--ignore-all-space --stat 0ec1f052..297c9655` | 5 文件、11+/6- | 5 文件（Handoff/test/red 日志/regression 日志/verification-results）；`3 files changed, 11 insertions(+), 6 deletions(-)`（Handoff 2+2、verification-results 4+4、test +5） | 0 | [integ-4-proof3-namestat.log](raw/integ-4-proof3-namestat.log) |
| ⑤ | `git cat-file -t e05696fd; git cat-file -t cba8db48` + `reflog show --date=iso HEAD \| head -20` | 均 commit | 均 `commit`；reflog 轨迹 `cba8db48`(01:19:33)→`e05696fd`(01:21:40)→`b0ef7f76`(01:22:18)→reset `4e76b2fa`→`297c9655`(01:36:09)→`db975e7a`→`f412cd47`→`46a444c8`→`d395ef70`(01:43:21)，与 verification-results §9.1/§9.2 ledger 逐条一致 | 全 0 | [integ-5-c2-reflog.log](raw/integ-5-c2-reflog.log) |
| ⑥ | `git log --format='%h %cI %s' -8` + 逐 commit `%cI` | 时间序成立 | release `aa1e0c7c`=01:07:24+08 < claim `4e76b2fa`=01:12:09 < 交付 `0ec1f052`=01:18:42 < r1 回填 `b0ef7f76`=01:22:18（见 §6 C6 口径） | 0 | [integ-6-time-ledger.log](raw/integ-6-time-ledger.log) |
| ⑦ | `git diff --stat 297c9655..HEAD` | 除证据日志零差异 | 7 文件全部为 Handoff/Task 文档与 verification 证据（4 个 raw 日志 + verification-results + 2 doc），**无 `src/**`、无测试语义差异** | 0 | [integ-7-runat-vs-delivery.log](raw/integ-7-runat-vs-delivery.log) |
| ⑧ | 三组回归：`tests/m2_acceptance -q` / `tests/core -q` / `tests/m2_acceptance -q --runxfail` | 34 passed+1 xfailed EXIT=0 / 76 passed EXIT=0 / 恰 1 failed=F-2 EXIT=1 | A：`34 passed, 1 xfailed in 9.19s`；B：`76 passed`；C：恰 1 failed=`test_ac4_books_without_pages_are_not_presented_as_zero`（F-2，断言点 `:890`） | A=0 / B=0 / C=1（期望值） | [integ-8-regression-three.log](raw/integ-8-regression-three.log)、[integ-8b-core-summary.log](raw/integ-8b-core-summary.log) |

失败判据（②非空 / ⑧数字不符 / ⑦出现 `src/**` 或测试语义差异）**均未触发**。

注记（如实）：
- ⑧B 组主日志中 pytest 摘要行被 QML stderr 噪音（`PrimaryNavigationRail.qml` TypeError 等，属无关测试噪音）顶出 `tail -3` 窗口，故补跑同命令抓摘要行落 integ-8b-core-summary.log（`76 passed in 7.52s`，EXIT=0）；补记日志 v1 的 interpreter 行因 `$py` 未加引号分词失败（与 r1 期旧日志头部同款问题），已重写修正并在 note 中披露。
- ③组 v1 曾记录普通 `git diff` EXIT2=0；本仓 `diff.exitCode` **未设置**，`git diff` 默认不以差异设置退出码，故 v1 记录按 git 默认语义有效但不构成差异判断；已重跑加 `--quiet`（EXIT=1=差异存在）作硬判据，v1 语义更正在日志 note 与本行同时留痕。集成方初次复核时曾把 `core.autocrlf=true` 的输出误读为 `diff.exitCode=true`，已在此更正。
- CRLF 观察（r2 §3 观察项 a，随②确认关闭）：`core.autocrlf=true` 生效（来源：系统级 `C:/Program Files/Git/etc/gitconfig`，主 repo 与 Owner worktree 同源）。旧日志（green-post-fix-pre-marker / regression-final-rerun / final-tip-rerun）命令输出区段的 CRLF 在检入时已被规范化为 LF 入 blob，②的整树 `diff --check` 空输出即证明其不触发；与 r1 六处清理结论无交集，无残留。

## 3. P3-N1/N2/N3 收口（DSH r2 §3，集成方修正）

- **N1（Handoff fallback 措辞）**：[doc/handoffs/M2-FIX-EXPORT-LINEAGE-owner-delivery.md](../../handoffs/M2-FIX-EXPORT-LINEAGE-owner-delivery.md) 「Review 重点建议」行的「`_record` fallback 路径（SKIPPED/CANCELLED/FAILED）不带 included 键」改为「**fallback 行键存在、值为空 list 的语义边界**」，并标注「集成方修正 N1」。与代码（`service.py:248/268/280` 传 `scope=None` → `:460` fallback 默认参序列化两键）、同文件风险条、verification-results §3/§6 对齐。
- **N2（amend 差异行数记账口径）**：澄清——`verification-results.md` §9.2 所称「C4 文档 4 行」仅指 `verification-results.md` 自身 4 行改动；`raw/diff-check-evidence.log` `--stat` 的 6 行 = **Handoff 2 行 + verification-results 4 行**（test 5 行为 C5 断言）。两组数字各指其面、合计自洽（11 insertions/6 deletions），Owner 文件不改，以本节为准。
- **N3（终态 hash 登记）**：**final tip = `d395ef70b311b0d960cddcb0680e9fc423c0b09c`**（组① `git rev-parse HEAD` 实测；交付物内此前仅登记至 `46a444c8` 及「最终收口 tip」，本行补齐）。集成 merge= `d71883ec9a6c6fccb14b62908c02790bb3beb99c`。

## 4. F-1 关闭声明

- F-1（export history 持久层不含 `included_stale_page_ids`/`included_missing_page_ids`）在本 Task 修复并随本集成关闭：`@pytest.mark.xfail(strict)` 已移除；先红留痕 = 原 `:584` 持久断言 EXIT=1（raw/red-pre-fix-test_ac2_history.log），修复后转 PASS。
- 套件现状：`tests/m2_acceptance -q` = **34 passed, 1 xfailed**（仅剩 F-2），EXIT=0；`tests/core -q` = **76 passed** EXIT=0；`--runxfail` 恰 1 failed=F-2 EXIT=1（集成 head 复跑见 §5）。
- M2-AC4 集成时登记的承接条件「F-1 修复 Task 范围含对应 xfail 移除」**已履行**；M2-AC4 的 F-1 xfail 证据保留为历史，不再需要动作。
- F-2（ListBooks page_count unknown 通道）仍为 xfail，归 [M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN](../../../doc/tasks/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN.md)（proposed/NOT_RELEASED），本集成未触碰。

## 5. 集成 head 复跑（main @ 集成修正 commit）

- `$py -m pytest tests/m2_acceptance -q` → 34 passed, 1 xfailed，EXIT=0（raw/postmerge-m2acceptance.log）
- `$py -m pytest tests/core -q` → 76 passed，EXIT=0（raw/postmerge-core.log）
- 日志与集成修正 commit 同步入库。

## 6. C6 时间口径（集成方采信声明）

- 采信 `verification-results.md` §9.3 的 `%cI` 核定：release `aa1e0c7c`=2026-09-29T01:07:24+08 先于 claim=01:12:09 先于 red 证据=01:12:41(+08 折算)，时间序成立（集成方组⑥复跑一致）。
- `verification/M2-FIX-EXPORT-LINEAGE/release-8b0d9040.md` 与历史 STATUS 所记「02:1x」为近似偏晚记载；release evidence 文件为 release commit 历史证据，本集成**不回改**，以 §9.3 与本记录为准。

## 7. P3-7 并发评估（采信，不在集成扩修）

- `reading_export.py:176-240` write 路径的 read-modify-write + `DELETE … NOT IN` 并发互删窗口：**采信 Owner §7 静态评估**（assessed-not-fixed，冻结裁定；生产单线程假设未验证）。本集成不为 P3-7 顺带扩修；修复候选是否登记留 planning。

## 8. 集成范围与禁止项核对

- 集成方改动限于：`doc/reviews/M2-FIX-EXPORT-LINEAGE-*-dsh-r{1,2}.md`（新增归档）、`verification/M2-FIX-EXPORT-LINEAGE/integration-d395ef70/**`（新增集成记录）、`doc/handoffs/M2-FIX-EXPORT-LINEAGE-owner-delivery.md`（仅 N1 一行，集成方修正标注）、`doc/tasks/M2-FIX-EXPORT-LINEAGE.md`（终态回填）、`doc/REBASELINE_PLAN.md`（该 Task 行改 done）。
- 未触碰：`src/**`、`tests/**`（语义）、`schema.py`、`reading_export.py`、`doc/STATUS.md`（主会话收口）、Owner worktree 历史、未 push、未删分支；主 repo 既有无关未提交改动（apps/desktop/**、permissions/**、verification/M2-RC2/** 等）零接触。
