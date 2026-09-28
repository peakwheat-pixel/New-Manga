# M2-FIX-EXPORT-LINEAGE r2 非作者 Review（DSH，静态只读）

**总结论：approved**（C1–C6 全部真实关闭；无 P0/P1/P2 问题；仅 3 条 P3 文档级残留，建议集成会话顺手收口，无需再走一轮 Review）

- 审查对象：branch `agent/zcode/M2-FIX-EXPORT-LINEAGE`，base `8b0d9040`，delivery_head `297c9655`（Task frontmatter:h17 / Handoff:h6），回填 tip 本轮按会话所述 `d395ef70`（交付物内未登记该 hash，见 N3）。
- 本轮为纯静态核对：无命令、无文件修改；所有 `git`/pytest 动态断言列入 not_verified。

---

## 1. C1–C6 逐条核对

### C1 whitespace-only 清理 + 整树 diff --check + tip 绑定复跑 —— **通过**
- 六行清理登记齐全：`raw/diff-check-evidence.log:9-14`（pre-clean `0ec1f052` / cleaned `297c9655` / 逐行 `red:46,56,59`、`regression-final:35,54,69` / 行数 71、155 不变），等价性证明 `:17-19`（`--ignore-all-space 0ec1f052..297c9655 -- .../raw/` 空输出 EXIT=0），整树判据 `:22-24`（`git diff --check 8b0d9040..297c9655` 空 EXIT=0），amend 全量差异 `:27-38`（5 文件；`src/` 缺席）。
- 静态复核（我直接读文件）：
  - `raw/red-pre-fix-test_ac2_history.log` 共 71 行，h46 为空行、h56/h59 为单独 `E`（traceback 文案与 `:572` 断言行完整保留）；`raw/regression-final.log` 共 155 行，h35/h54/h69 为空行——与登记行号、行数逐一吻合。
  - 对全交付面（`verification/M2-FIX-EXPORT-LINEAGE/**` 含全部 `raw/*.log`、`tests/.../test_reader_export_lineage_library_pagecount.py`、`doc/handoffs/M2-FIX-EXPORT-LINEAGE-owner-delivery.md`）做 `[ \t]+$` 检索：**0 命中**，与「整树 diff --check = 0」互相印证。
  - `raw/final-tip-rerun-r2.log` 头部全新（`:1-9` shell/引号解释器/Python 3.12.3/run-at HEAD/branch/ISO/命令行），三组结果与声明一致：`:12-13` 34 passed+1 xfailed EXIT1=0、`:18` 76 passed、`:65-117` `--runxfail` 恰 1 failed（F-2）EXIT3=1，`:118` OVERALL。
  - Postscript 自曝偏差已落实：该日志 h91/h96 现为空行、全文件 118 行、无行尾空白（`raw/diff-check-evidence.log:47-55` 自登）。
- 唯一保留意见（非阻断，见 not_verified）：`8b0d9040..<最终 tip>` 的 diff --check 在 `46a444c8→d395ef70` 这段 amend 之后只有文字性「均复核=空」，无独立日志或 hash（`verification-results.md:107`）；`raw/scope-self-check.log:34-35` 的 EXIT4=0 跑于 `db975e7a`（其自身 h4 已声明 run-at）。我用工作区全量检索补上了这一环，但 git 侧仍需集成方复跑一次。

### C2 `e05696fd`/`cba8db48` 来历 + ledger 实际 hash —— **通过**
- `verification-results.md:88-98`（§9.1）逐条 reflog 表：`cba8db48`(01:19:33) → `e05696fd`(01:21:40) → `b0ef7f76`(01:22:18)，并注明 `cat-file -t` 均=commit；`:18` 给出 r1 期 ledger 全链；`:104-107`（§9.2）给出 r2 重建链 `0ec1f052 → 297c9655` 与回填链 `db975e7a → f412cd47 → 46a444c8 → final tip`；ledger 表 `:12-16` 已换实际 hash。
- 内部一致性交叉验证（静态可查的最强证据）：`raw/final-tip-rerun.log:3-4` 头部 HEAD=`e05696fd`、ISO `17:21:51Z`(=01:21:51+08)，落在 `e05696fd` 提交时刻 01:21:40 与 `b0ef7f76` 01:22:18 之间——与 §9.1「该日志是第 2 次 amend 并入、run-at=e05696fd」完全自洽；同样 `final-tip-rerun-r2.log`/`scope-self-check.log` 的 ISO（17:40:45Z/17:41:31Z）在 `db975e7a` 之后、amend 之前，自洽。
- 动态可达性（reflog/cat-file 实跑）列入 not_verified。

### C3 范围自检 raw 证据 —— **通过**
- `raw/scope-self-check.log` 四要素齐：①`:9-23` `git diff --name-status 8b0d9040..HEAD` 全清单 13 项 + EXIT1=0；②`:25-26` `schema.py` 空 diff + EXIT2=0；③`:28-32` `--stat` 双冻结路径空 + `grep -c` hit_count=0；④`:34-35` `git diff --check` EXIT4=0，`:37-38` allowed-path 判读 + OVERALL。
- 清单与 `verification-results.md:77-84`（§8）判读一致（含 `doc/STATUS.md`、`release-8b0d9040.md` 属 release commit `aa1e0c7c` 的说明）。
- 我另做内容级复核：`src/infrastructure/sqlite/` 全目录检索 `included_stale|included_missing` **0 命中**，支持「schema.py/reading_export.py 零改动、整体字符串存取」论断。

### C4 三处 fallback 措辞更正 —— **通过**（含 1 处未覆盖残留，见 N1）
- 三处均已改为「键存在、值为空 list」，且撤回「保持不变」：`verification-results.md:37`（§3 第 4 项，即所指 §3.4）、`:61`（§6）、`doc/handoffs/...-owner-delivery.md:58`（风险条）。三处均给出代码锚点 `service.py:248/268/280 → :460`，与实读代码一致（`service.py:248/268/280` 传 `scope=None`，`:460` `scope or _scope_snapshot(request) or "{}"`，`:482-483/496-497` 默认空参序列化两键）。
- 残留（新问题 N1）：`doc/handoffs/M2-FIX-EXPORT-LINEAGE-owner-delivery.md:41` 仍写「fallback 路径（SKIPPED/CANCELLED/FAILED）**不带 included 键**的语义边界」——与代码及本文档 `:58`、`§6` 相反。C4 字面所指三处已关闭，故本条判通过；该残留按新问题计。

### C5 F-1 场景补 persisted `included_missing_page_ids` 断言 —— **通过**
- `tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py:585-589`：`missing_page_id = seed.page_b.page_id` → `persisted_missing = set(scope.get("included_missing_page_ids") or ())` → `assert persisted_missing == {missing_page_id}`，与既有 stale 断言 `:581-584` 并列，恰 +5 行，与 `diff-check-evidence.log:29,35` 登记的「C5 +5 lines」一致；F-1 的 `@pytest.mark.xfail` 已无（该文件仅剩 `:858` F-2 一处 xfail，与 `--runxfail` 恰 1 failed 相符）。
- 附注（P3 观察，不构成条件）：该场景的 persisted-missing 未与内存 `result.included_missing_page_ids` 做同源交叉（同源交叉断言存在于另一场景 `:531-534`），故本场景只证「持久化非空且集合正确」，不证「与 ExportResult 同源」。

### C6 新日志头修正 + 时间口径 —— **通过**
- 新日志头齐备：`raw/final-tip-rerun-r2.log:1-9`（shell/branch/引号解释器/版本串/HEAD/ISO/command）、`raw/scope-self-check.log:1-7`、`raw/diff-check-evidence.log:1-5`（并披露「手写重写、不再粘贴带空白原文」）。`verification-results.md:51` 已说明 r1 期 5 个旧日志 `python:` 行为未加引号取版本命令的失败记录（我核对 `red/green/regression-final/regression-final-rerun/final-tip-rerun` 五个头部确为 `/usr/bin/bash: line N: G:/CODEX/New: No such file or directory`，与「5 个」计数一致），旧文件原样保留、口径以 pytest 头行为准，披露成立。
- 时间序：`verification-results.md:109-118`（§9.3）给出 `%cI` 表 release 01:07:24+08 < claim 01:12:09 < 交付(pre-clean) 01:18:42 < r1 回填 01:22:18，并说明证据 ISO 17:12:41Z–17:2x Z 折算后 red(01:12:41) 晚于 claim 32s、早于交付 commit；`release-8b0d9040.md:3`「02:1x」被明确标注为近似偏晚记载、旧文件不改。声明与披露自洽；`%cI` 数值本身需 git 复核（not_verified）。

---

## 2. r1 五轴正面结论是否仍成立（297c9655 vs r1 审的 0ec1f052）

静态逐点复核，结论**仍全部成立**；r2 差异确为「授权 whitespace 清理 + C5 断言 + C4/ledger 文档」：

| r1 正面结论 | 本轮静态复核 |
|---|---|
| 方案 A 最小性、不动 schema | `service.py:479-500` 仅加 2 个 keyword-only 参数并序列化 2 键；`src/infrastructure/sqlite/**` 新键 0 命中 |
| 数据源=ExportResult、同源 | `:227-236` 打包 `stale_ids/missing_ids` → `:283-302` COMPLETED 路径把 `result.included_stale_page_ids/included_missing_page_ids` 直传 `_scope_snapshot`；`:218-220` ABORT 在任何 `_record` 之前 raise，零记录语义不变 |
| `_parse_scope` 缺省空 list + 类型校验 | `:503-519` `setdefault(key, [])` + 非 list → `ExportError("corrupt export scope snapshot")`，`page_ids` 校验保持在前 |
| legacy 三通道断言有效 | 测试 `:592-694`：手工 INSERT 13 列旧行 `:614-644`、legacy JSON import（先清 `legacy_export_history_imported` 标记）`:646-685`、损坏值拒收 `:687-694` |
| 先红真实、F-2 零触碰 | `raw/red-pre-fix-...log:51-66` 红点=持久断言 `:572`（原 `:584`，临时移除 12 行装饰器后行号位移）EXIT=1；F-2 场景 `:858-894` 未改，且 r2 复跑 traceback 落到 `:890`，与当前文件行号一致（间接证明 test 文件在 run-at 与当前之间未漂移） |

---

## 3. 新增问题（按 P0–P3）

无 P0/P1/P2。以下 3 条均为 P3，非阻断：

- **P3-N1（文档事实残留，建议集成顺手改一行）** `doc/handoffs/M2-FIX-EXPORT-LINEAGE-owner-delivery.md:41` 仍称 fallback「不带 included 键」，与代码及同文件 `:58`、`verification-results.md:37/:61` 矛盾；该句是「Review 重点建议」指针，易误导只读 Handoff 的集成方。修法：改为「fallback 行键存在、值为空 list 的语义边界」。
- **P3-N2（数字口径不一致）** `verification-results.md:105` 称 amend 差异 = 「C4 文档 4 行」，而 `raw/diff-check-evidence.log:33-37` 自身 `--stat` 显示 Handoff 2 行 + verification-results 4 行 = **6 行**（合计 11 insertions/6 deletions 内部倒是自洽）。属记账口径问题，不涉及代码。
- **P3-N3（终态 hash 未登记）** 交付物只写「`46a444c8` 及最终收口 tip」（`verification-results.md:107`、`raw/diff-check-evidence.log:53-55`），全文检索 `d395ef70` **0 命中**；被审对象自身的最终 tip hash 无落盘登记。建议集成记录中补一行 `final tip = <hash>`。
- 观察项（非问题）：（a）三个旧日志（`green-post-fix-pre-marker.log` h6-15/17-18、`regression-final-rerun.log` h10/11/15-17、`final-tip-rerun.log` h6/7）在命令输出区段含 CRLF、头部为 LF（混合行尾），对 `git diff --check` 的影响取决于 `core.autocrlf`/blob 实际字节——r1 的 6 处结论未含这些行，说明当前环境不判 CR，但集成方复跑时应一并确认；（b）本 worktree 无 `reviews/**`（r1 报告不在本 worktree），C1–C6 原文以会话指令与 Task `:75-76` 记录为准。

---

## 4. not_verified（需集成方代跑，按建议顺序）

```bash
# 1) tip 身份与终态（对应 N3；期望 HEAD 与会话所述 d395ef70 一致）
git rev-parse HEAD && git log -1 --format='%H %cI %s'

# 2) 冻结 AC5 判据在【最终 tip】整树复算（期望空输出、EXIT 0）
git diff --check 8b0d9040..HEAD; echo "EXIT=$?"

# 3) 清理的等价性（期望 Proof1 空输出；再看无 -w 的 diff 只应有把行尾空白删空的 hunk）
git diff --ignore-all-space 0ec1f052..297c9655 -- verification/M2-FIX-EXPORT-LINEAGE/raw/
git diff 0ec1f052..297c9655 -- verification/M2-FIX-EXPORT-LINEAGE/raw/

# 4) Proof3 名单与行数复核（期望 5 文件、11+/6-；并核对 N2 的「4 行 vs 6 行」）
git diff --name-status 0ec1f052..297c9655
git diff --ignore-all-space --stat 0ec1f052..297c9655

# 5) C2 前身可达性 + r1/r2 amend 轨迹（期望均 commit）
git cat-file -t e05696fd; git cat-file -t cba8db48
git reflog show --date=iso HEAD | head -20

# 6) C6 时间序（期望 01:07:24 < 01:12:09 < 01:12:41 口径成立）
git log --format='%h %cI %s' -8
git log -1 --format=%cI aa1e0c7c; git log -1 --format=%cI 4e76b2fa; git log -1 --format=%cI 0ec1f052; git log -1 --format=%cI b0ef7f76

# 7) run-at 树 == 交付树（除证据日志外 test/src 零差异，支撑「tip 绑定复跑」）
git diff --stat 297c9655..HEAD

# 8) 回归三组复现（期望 34 passed+1 xfailed EXIT=0 / 76 passed EXIT=0 / --runxfail 恰 1 failed(F-2) EXIT=1）
"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" -m pytest tests/m2_acceptance -q
"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" -m pytest tests/core -q
"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" -m pytest tests/m2_acceptance -q --runxfail
```

失败判据：2) 非空 / 8) 数字不符 / 7) 出现 `src/**` 或测试语义差异 → 立即回退到 changes_requested 并指出具体 hunk。

---

## 5. 最终推荐

**可集成。** 六项条件（C1–C6）已逐条以文件内容核到行号级别关闭，r1 的五轴代码结论未被 r2 改动触动（`src/` 语义零变化、`schema.py`/`reading_export.py` 零命中、仅剩 F-2 一处 xfail）。

给 Codex（Integrator）的收口清单：
1. 按 §4 第 2、7、8 条做最终 tip 的一次整树 `diff --check` + 三组复现，并把结果写进 `verification/M2-FIX-EXPORT-LINEAGE/**` 集成记录（补 P3-N3 的 `final tip=<hash>`）。
2. 顺手修 P3-N1（Handoff:41 一行）与 P3-N2（`verification-results.md:105` 数字）——属文档更正、零语义，可在集成回填 commit 内完成，无需再开 Review 轮次。
3. 保持禁止范围：不回改 `service.py`/测试语义、不动 `schema.py`、不为 P3-7 并发窗口顺带扩修（`verification-results.md:64-73` 的冻结评估已足够留痕）；Owner≠Integrator 不变。
4. 集成后按协作协议回填 `doc/tasks/M2-FIX-EXPORT-LINEAGE.md` 的 `review:`/`integration_merge:` 与 `doc/STATUS.md`，并在 Task 关闭时给出下一 Task 建议。
