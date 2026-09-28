approved_with_conditions

# M2-FIX-EXPORT-LINEAGE 非作者静态 Review（DSH r1）

审查对象：branch `agent/zcode/M2-FIX-EXPORT-LINEAGE`，base `8b0d9040`，Task frontmatter `delivery_head=0ec1f052ff4a3b3875d9e242deb9fb3cb381fa5a`。
审查方式：**只读静态核验**（read/grep/glob），无 shell、无执行、无写入；一切测试结果与 git 事实均以落盘日志与源码交叉比对为准。作者身份隔离成立（Owner=ZCode 子 agent，Reviewer=DSH，Integrator=Codex）。

**结论先行**：方案 A 的代码实现经逐行核验**正确、最小、同源、向后兼容**，F-1 已在断言层被真实修掉（先红证据与代码红点完全对齐），无 P0、无产品代码缺陷。但 AC5（证据纪律）**自评 PASS 不成立**：交付 tip 无任何绑定日志、amend 轨迹未披露；整树 `git diff --check` EXIT≠0 且未按仓库既有两次先例做 whitespace-only 清理；范围自检无 raw 证据；三处文档对 fallback 行的描述与代码相反。条件全部落在证据/记录层，故给 `approved_with_conditions`。

---

## A. verified-by-reading：五轴正面核验

### 轴 1 方案 A 最小性与正确性 —— 通过

| 检查点 | 证据 | 判定 |
|---|---|---|
| 改动面最小 | `src/application/export/service.py` 仅 3 处：`:479-500`（签名加 2 个 keyword-only 参数 + 序列化 2 键）、`:293-302`（COMPLETED 传参）、`:503-519`（缺省 + 类型校验）。全仓 `_scope_snapshot(` 仅 2 调用点（`:297`（实为 `:293-302` 内）、`:460`），无第三调用方 | 通过 |
| 与落库同源 | `:299-300` 直接把 `result.included_stale_page_ids/.included_missing_page_ids` 传入；而 `result_kwargs`（`:227-236`）来自 `_stale_scope()`（`:218`、`:371-378`）→ 无二次推导、无重算，内存与持久严格同源 | 通过 |
| 非 translated 模式不误报 | `_stale_scope` 在 `mode != "translated"` 时返回 `(), ()`（`:372-373`）→ 落库为空 list，非 `None` | 通过 |
| `included ids` 是否可能为 None → 序列化成什么 | 不可能为 None：`_stale_scope` 返回 tuple，`result_kwargs` 恒定注入；`_scope_snapshot` 再做 `list(...)`（`:496-497`）。**无 `null` 落库路径** | 通过 |
| skip/cancel/failed 分支 | `:248`、`:268`、`:280` 三处显式 `scope=None` → `:460` fallback `scope or _scope_snapshot(request) or "{}"` → **新行必然含 `included_*_page_ids: []`**（默认参数 `:482-483`）。语义正确（未发布任何页 = 空集合），但文档描述相反（→ P2-2） | 代码通过 / 文档错 |
| ABORT 零记录 | `StaleExportError` 抛于 `:219-220`，早于任何 `_record`；`test_ac2_stale_abort_fail_closed_zero_side_effects`（`tests/...:450`）零改动 | 通过 |
| 解析兼容/拒收对称 | `:515-518`：缺键 `setdefault(key, [])`（兼容），存在但非 list → `ExportError`（拒收）；`null` 亦被拒（非 list），语义正确。`repeat()` 只消费 `page_ids/mode/overwrite_policy/stale_policy`（`:338-354`），不受影响 | 通过 |
| `reading_export.py` 零改动是否合理 | `scope_snapshot_json` 全程当**不透明字符串**：读 `:164`、写 `:197`/`:218`/`:229`、legacy import `:472`/`:505`；无任何按 key 拆解 | 合理（改动事实待集成复核 → not_verified） |
| `schema.py` 零触碰 | `schema.py:442` 仅既有列 `scope_snapshot_json TEXT NOT NULL DEFAULT '{}'`；`src/**` 内 `included_stale|included_missing` 仅 `service.py` 内存/持久两点 + UI 计数（`viewmodel.py:286-287`） | 通过（diff 事实待复核） |
| 契约/IPC 面 | `doc/03_DATA_MODEL.md:1858-1875` 只列 ExportHistory **列名**，不约束 scope JSON 内键；`doc/contracts/**` 与 `apps/**`（Rust/TS）对 `scope_snapshot/included_*` **零命中**；UI `_history`（`viewmodel.py:172-185`）不消费该 JSON | 方案 A 确为契约中立，冻结选择正确 |

### 轴 2 xfail 移除纪律 —— 通过

- **先红真实且可跨 Task 对齐**：`raw/red-pre-fix-test_ac2_history.log:24-64` 的 traceback 是**临时移除 12 行装饰器**后的原样形态（失败点 `:46` 的 `set() == {stale_page_id}`，报点 `:66` = `...py:572`）。独立交叉核对：`verification/M2-AC4/integration-890f0c74/raw/integration-pytest-new-suite-runxfail.log:30-41` 的装饰器恰为 **12 行**，同断言报点 `:84` = `:584`；`584 - 12 = 572` **精确吻合**，且两处断言文案、diff 形态、异常类型逐字同形。红点确为原 `:584` 持久断言，非环境噪声。
- **时间序正确**：red `:6` = `2026-09-28T17:12:41Z` → green `:4` = `17:13:18Z`（标记仍临时移除、单场景转 PASS）→ regression `17:14:47Z` / rerun `17:15:41Z`。标记的**正式移除**发生在转绿之后并入交付 commit，符合 AC2「先证实修复再移除标记」。
- **XPASS 无意外、计数自洽**：`tests/m2_acceptance` 我数得 **35 个 `def test_`**（跨 4 文件），`34 passed + 1 xfailed = 35` ⇒ 无 XPASS、无 skip、只剩 F-2；`tests/core` 我数得 **76 个 `def test_`** = 76 passed。两组数字与日志逐字吻合，AC4 的「34 vs 预期 33，+1=新增 legacy 场景」解释在算术上成立。
- F-2 marker 完好：`tests/...:853-863` `strict=True`，F-2 场景体（`:864+`）未见改动痕迹（diff 事实待复核 → not_verified）。

### 轴 3 legacy 三通道有效性 —— 通过

- **通道 1（`:609-639`）承重**：手工 INSERT 的正是 pre-fix 13 列行形（`render_profile_snapshot_json=""` 与 `_dump_json(None)`（`service.py:534-537`）一致；`file_hash` 64 hex），scope JSON 恰为 pre-fix 5 键；`:630-631` 先自证 fixture 无新键（fixture sanity），再断言旧键完好 + 双新键解析为 `[]`。与 pre-fix 行形一致，**未伪造**。
- **通道 2（`:641-680`）真走到 import 路径**：不是 mock，直接调用 production `import_legacy_export_history`（`reading_export.py:398-535`）并断言 `imported == 1` + 行可读 + 解析空集。
- **首跑 1 failed 的修正如实**：我独立复核 `raw/regression-final.log:96-99`（`assert 0 == 1`）的归因成立 —— `src/bootstrap/core_assembly.py:849-850` 装配期已对同一 conn 跑过 one-time import，文件缺失 → `reading_export.py:418-435` 写入 `missing_empty` 标记 → 二次调用在 `:410-415` 直接 `return 0`。测试改法（`:645-649` 先删 `application_metadata` 标记行）复现「升级前 legacy 文件存在」态，属**测试自身修正，非产品缺陷**；首跑日志如实保留未删改。
- **通道 3（`:682-689`）拒收合理**：非 list（字符串）→ typed `ExportError`，断言文案与 `service.py:518` 一致，证明「损坏≠空」。
- 顺带观察（不阻断）：通道 2 必须绕过生产 one-time 标记，说明真实升级中若曾以「文件缺失」判定过 `missing_empty`，后到的 legacy 文件将永不被导入 —— 既有产品行为、不在本 Task 范围，本测试的绕行是合理且必要的。

### 轴 4 P3-7 评估充分性 —— 通过

- 窗口描述与代码逐点一致：`_record` 先 `store.read()`（`service.py:452`）再 `store.write()`（`:472`）；write 内为事务型逐行 upsert + 全量 `DELETE ... NOT IN`（`reading_export.py:181-240`，互删在 `:238`）。「A read=[X] / B read=[X] / A write([X,A]) / B write([X,B]) → B 物理删 A 行」的推演**成立**。
- 「本修复不改变窗口」**成立**：改动不含任何 store 调用、不新增 read/write、不改时序（`_scope_snapshot` 为纯计算，且 COMPLETED 路径因 `or` 短路不再二次调用）。
- 「生产单线程假设未验证」已如实标注（`verification-results.md:69`），符合「只评估不修」的冻结裁定。

### 轴 5 范围与证据纪律 —— 部分通过（见问题清单）

- 静态核对的落点无越界：`src/**` 内本 Task 相关符号只出现在 `service.py`；测试文件仅动 F-1 场景 + docstring + import + 新增 legacy 场景（diff 事实待复核）。
- 日志带头带 EXIT：红/绿/两次回归均带 `git HEAD` + `EXIT*`；但头部有缺陷（→ P3-2）。
- 范围自检**无 raw 证据**（→ P2-1）；交付 tip **无绑定日志**（→ P1-1）。

---

## B. 分级问题清单

### P1-1｜证据未绑定交付 tip，amend 轨迹零披露（AC5「固定 HEAD」半项不成立）

- `verification/M2-FIX-EXPORT-LINEAGE/raw/final-tip-rerun.log:3` 记 `git HEAD: e05696fd1f44f076d1e4cc3483e5c1bdb70fbd2d`，文件标题自称「final tip rerun (delivery tip)」。
- `verification/M2-FIX-EXPORT-LINEAGE/raw/diff-check-evidence.log:1` 记「post-delivery **cba8db48**」。
- 其余全部日志停在 claim：`raw/red-pre-fix-test_ac2_history.log:4`、`raw/green-post-fix-pre-marker.log:3`、`raw/regression-final.log:4`、`raw/regression-final-rerun.log:4` 均 `HEAD=4e76b2fa...` 且注「unstaged」/「claim + unstaged fix」。
- 而声明 tip 为 `doc/tasks/M2-FIX-EXPORT-LINEAGE.md:17` `delivery_head: 0ec1f052...`；`verification/M2-FIX-EXPORT-LINEAGE/verification-results.md:14-16` 的 ledger 表 #2/#3 只有占位符（「hash 见交付后 frontmatter」「（回填 commit）」），回填后未更新。
- **理由**：交付区间内不存在任何在 `0ec1f052`（或回填 tip）上执行的日志；`e05696fd`/`cba8db48` 仅出现在日志首行，Task/verification/Handoff 三处零解释 ⇒ 无法判定历次 amend 是否只改文档/日志。仓库有**两次明确先例**要求逐字披露：`verification/M2-FIX-STUB-DECODER/verification-results.md:52`（登记 amend 前身 `550b4269` 与 whitespace-only 性质）、`verification/M2-AC4/raw/git-diff-check-owner-tip.log:12-13,20-21`（登记 check1/check2、pre-amend `f615d5da`/`130dd7db`）。AC5 自评 PASS 缺依据。

### P1-2｜冻结 AC5 的整树 `git diff --check` EXIT=0 未达成，Owner 自行降级为等效口径

- 冻结原文：`doc/tasks/M2-FIX-EXPORT-LINEAGE.md:58`「`git diff --check <base>..<delivery-head>` exit 0」。
- 实际：`verification/M2-FIX-EXPORT-LINEAGE/verification-results.md:79` 自述整树 `EXIT=2`；`raw/diff-check-evidence.log:12-23` 列出 6 处行尾空白（`raw/red-pre-fix-test_ac2_history.log:46/56/59`、`raw/regression-final.log:35/54/69`，均经我逐行核对确为 pytest 缩进/`E` 前缀行）。
- **理由**：披露诚实（非隐瞒），但 AC 条文未被满足而自评为「PASS（事实精确披露）」；且该 6 处空白是 pytest 输出的**格式固有产物**（空源码行被 pytest 加 4 空格缩进、断言明细行以 `E`+空格起始），先例已证明清理不损伤证据。裁决见 §D。

### P2-1｜范围自检（AC5 前半）无 raw 证据落盘

- `doc/handoffs/M2-FIX-EXPORT-LINEAGE-owner-delivery.md:32` 与 `verification-results.md:74-80` 声称执行了 `git diff --name-status` 与 `schema.py` 命中计数，但 `verification/M2-FIX-EXPORT-LINEAGE/raw/` 下 6 个日志（red/green/regression-final/regression-final-rerun/final-tip-rerun/diff-check-evidence）**无一条** name-status 输出或计数输出——我逐文件读完确认。
- 对照先例：`verification/M2-FIX-STUB-DECODER/raw/06-scope-self-check.log:6-18` 把 name-status 清单与 `EXIT=0` 完整落盘。
- **理由**：「仅落允许路径」「`schema.py`/`reading_export.py` 零命中」目前只有散文声明（代码层我静态复核成立），属不可复算证据；集成方无法据此关闭范围项。

### P2-2｜「未完成导出记录不带 included 键」与代码实际相反（三处文档）

- 代码事实：`service.py:248/268/280` 三处 `scope=None` → `:460` fallback `_scope_snapshot(request)`（默认参数 `:482-483`，序列化 `:496-497`）⇒ SKIPPED/CANCELLED/FAILED 行**必然携带** `included_stale_page_ids: []` 与 `included_missing_page_ids: []`。
- 文档事实：`verification-results.md:35`「fallback 路径…**保持不变**（不带新键）」、`:58`「SKIPPED/CANCELLED/FAILED 记录的 scope…**不带 included 键**」、`doc/handoffs/M2-FIX-EXPORT-LINEAGE-owner-delivery.md:57`「未完成导出（CANCELLED/FAILED/SKIPPED）记录**不带 included 键**」。
- **理由**：两处结论都错——(1) 键存在，只是值为空；(2)「保持不变」不成立（fallback 行新增 2 键，本 Task 实际改变了非 COMPLETED 行的 JSON 形状）。语义上写空 list 是诚实的（未发布任何页），但错误披露会成为后续「未完成导出 included 语义」候选的错误前提，并让集成方误判最小扰动边界。

### P3-1｜persisted `included_missing_page_ids` 无端到端断言（覆盖缺口）

- F-1 场景 `tests/...:576` 只断言 `result.included_stale_page_ids` 与 `:581-584` 只断言 persisted **stale**；seed 同时造出 missing 页（helper `:219-267` 中 `page_b` 无译文，快照后只提交 page_a 的 revision），另一 CONTINUE 场景 `:534`（内存 missing）+`:547-552`（仅 `stale_policy`）也未覆盖持久 missing。
- 代码对称（`:496-497`）故风险低，但 AC1 明列两键；建议在授权范围内补 1 行 persisted missing 断言，或由集成记录显式登记为已知缺口。

### P3-2｜日志头不完整；`python:` 行是 shell 报错而非版本串

- 5 个日志头部为 `python: /usr/bin/bash: line N: G:/CODEX/New: No such file or directory`（`red:3`、`green:2`、`regression-final:3`、`regression-final-rerun:3`、`final-tip-rerun:2`）——说明头部取版本命令因路径未加引号失败，**没有版本串**；`verification-results.md:7` 声称「日志头有原样版本串」不成立（版本仅见于 pytest 自带头行 `Python 3.12.3, pytest-9.1.1`，`red:11`）。
- `raw/green-post-fix-pre-marker.log` 与 `raw/final-tip-rerun.log` 缺 `shell:`/`command:` 行，与 AC5「命令日志带 shell、解释器、固定 HEAD、EXIT」不完全一致（HEAD/EXIT 有）。

### P3-3｜释放先于实施的时间序不可判定

- `verification/M2-FIX-EXPORT-LINEAGE/release-8b0d9040.md:3` 与 `doc/STATUS.md:29` 记「2026-09-29 **02:1x**」；而证据时间戳为 `red:6` `17:12:41Z`、`green:4` `17:13:18Z`、`regression:6` `17:14:47Z`、`rerun:6` `17:15:41Z` = +08 的 `01:12–01:15`，**早于所记释放时间**。二者必有一错（时间戳为近似值，或实施先于释放）。建议集成方以 `git log --format=%cI` 核定 release/claim commit 的提交时间后回填一处口径。

### P3-4｜`history()` 仍无 included ids 直读字段，需集成方明确采纳本 Task 冻结口径

- `ExportRecord`（`service.py:175-191`）无该字段，`_record_from_row`（`:540-555`）不映射；UI `_history`（`viewmodel.py:172-185`）也不暴露 ⇒ 只能 `json.loads(record.scope_snapshot_json)` 取回。
- 方案 A 冻结口径（Task `:46`、`:54`）下 AC1 成立，F-1 场景也是按 JSON 解析断言的；但 M2-AC4 `AC1(a)` 的字面措辞是「`history()` **字段覆盖** `included_stale_page_ids`」（`doc/tasks/M2-AC4.md:49`）。建议集成记录显式写明「以 scope_snapshot_json 内键 + `_parse_scope` 可解析 = AC1(a) 满足」，避免 M2-AC4 AC1(a) 复判再生争议。

---

## C. not_verified 清单（需集成方代跑并落痕）

统一环境：`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`；先取实际 tip：`TIP=$(git rev-parse HEAD)`，记下回填 commit（预期 `b0ef7f76`）。

1. **ledger / amend 轨迹核定**
```
git -C "G:/CODEX/New Manga.worktrees/M2-FIX-EXPORT-LINEAGE-zcode" log --format='%H %cI %s' -6
git -C ... cat-file -t e05696fd ; git -C ... cat-file -t cba8db48      # 是否仍可达/为 dangling 前身
git -C ... reflog show --date=iso HEAD | Select-String 'e05696fd|cba8db48|0ec1f052'
```
期望：能解释 `e05696fd`/`cba8db48` 的来历（amend 前身）与 `0ec1f052 → b0ef7f76` 关系，否则 P1-1 升级。

2. **范围与零改动事实**
```
git diff --name-status 8b0d9040..$TIP
git diff --stat 8b0d9040..$TIP -- src/infrastructure/sqlite/schema.py src/infrastructure/sqlite/reading_export.py   # 期望空
git grep -n "included_stale\|included_missing" 8b0d9040..$TIP -- src/infrastructure                              # 期望空
git diff 8b0d9040..$TIP -- tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py                   # 应只含 F-1 marker 移除+docstring+_parse_scope/legacy import+新 legacy 场景
```
期望关闭 P2-1，并证明 F-2 场景与其余断言零改动（AC2/AC5）。

3. **在**新 tip**绑定 HEAD 的复跑（替掉 `4e76b2fa`/`e05696fd` 的旧绑定）**
```
"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" -m pytest tests/m2_acceptance -q      # 期望 34 passed, 1 xfailed, EXIT=0
"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" -m pytest tests/core -q                # 期望 76 passed, EXIT=0
"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" -m pytest tests/m2_acceptance -q --runxfail   # 期望 1 failed(F-2)/34 passed, EXIT=1（证明无第二处隐藏 xfail、无 XPASS 掩盖）
```

4. **判别性核验（可选，判别 F-1 断言确实压在本次代码路径上；先备份并还原）**
   临时删除 `src/application/export/service.py:299-300` 两个参数实参 → F-1 场景应红；还原后 `git status --porcelain src/` 必须为空。

5. **whitespace 清理后的整树口径（先例等价性证明）**
```
git diff --check 8b0d9040..$NEW_TIP                                                       # 期望 EXIT=0（原 6 处）
git diff --ignore-all-space $PRE_CLEAN_TIP..$NEW_TIP -- verification/M2-FIX-EXPORT-LINEAGE/raw/   # 期望空输出（仅行尾空白变化）
```

6. **未验证事实（我无法静态确认）**：`reading_export.py`/`schema.py` 在上述区间零改动；`tests/m2_acceptance` 其余场景断言逐字未改；`0ec1f052` 的实际内容与 `4e76b2fa`+unstaged 测试内容逐字一致。以上均由 1、2 与 3 覆盖。

---

## D. 对 diff-check 口径的明确裁决

**裁决：要求 whitespace-only 清理后重验（不接受以「整树 EXIT=2 + 等效口径」作为最终交付状态）。**

理由与边界：

1. 冻结 AC5（`doc/tasks/M2-FIX-EXPORT-LINEAGE.md:58`）的判据是整树 `exit 0`；`verification-results.md:79` 的「PASS（事实精确披露）」属**自行降级判据**，即便披露诚实也不能自评为 PASS。
2. 该 6 处空白是 pytest 对空源码行/断言明细行的**格式固有缩进**（非证据语义），仓库内已有两次同题先例且均以清理收口：`verification/M2-AC4/raw/git-diff-check-owner-tip.log:12-13`（「stripped trailing whitespace … whitespace-only edit, content otherwise byte-identical」→ amend）与 `verification/M2-FIX-STUB-DECODER/verification-results.md:52`（「按 M2-AC4 先例做 whitespace-only 清理（traceback 内容逐字保留，仅去行尾空格）后 amend」）。因此**授权 Owner 做同样操作**，不视为篡改证据。
3. 执行约束（硬性）：
   - 只允许删除行尾空格，traceback 文案/字节其余部分逐字保留；不得顺带改任何断言、路径、EXIT 行；
   - `raw/diff-check-evidence.log` 必须**手写重写**（不得再把带行尾空白的三口径输出原样粘入，否则重演 M2-AC4 check-2 的自指陷阱），并登记 `pre-clean tip`（当前 `0ec1f052`）、清理后 tip、以及 `--ignore-all-space` 空 diff 的证明；
   - 清理后**必须在新 tip 复跑两条 pytest + `--runxfail`**并将新 HEAD 写入新日志（顺带关闭 P1-1），旧日志保留其运行时刻 HEAD 与 amend 说明。
4. 若 Owner 不可用，可由 Integrator 代行，但必须在 `verification/M2-FIX-EXPORT-LINEAGE/integration*/` 内显式记明「代行清理 + pre-clean hash + 等价性证明」；**不得以沉默方式接受整树 EXIT=2**。仅当 Integrator 以 Codex 身份在集成记录中显式改写 AC5 判据（并说明理由）时，才可豁免，且该豁免须留痕。

---

## E. 结论与推荐下一步

**结论**：代码层 `approved`——方案 A 实现最小、同源、兼容与拒收对称，ABORT 零记录语义未被扰动，`schema.py`/`reading_export.py` 零改动的设计前提我静态确认成立，F-1 先红-转绿链真实且行号可跨 Task 对齐，legacy 三通道承重，P3-7 评估准确。**证据层 `changes_requested` 级**——AC5 的两半（固定 HEAD、整树 diff --check EXIT=0）与范围自检均未按冻结标准闭合，三处文档存在与代码相反的事实描述。

**条件（合并前必须关闭，均在允许路径内）**：
- C1（P1-1/P1-2）按 §D 完成 whitespace-only 清理 + amend，整树 `git diff --check` EXIT=0，并在新 tip 复跑三组命令、把新 HEAD 写进日志；在 `verification-results.md §8` 登记 amend 轨迹（pre-clean tip、等价性证明）。
- C2（P1-1）解释 `e05696fd`/`cba8db48` 的来历（amend 前身/dangling），并更新 ledger 表（`verification-results.md:14-16`）为实际 hash。
- C3（P2-1）补 raw 范围自检（`git diff --name-status` 清单 + `schema.py`/`reading_export.py` 零命中计数 + EXIT）。
- C4（P2-2）修正 `verification-results.md:35`、`:58` 与 `handoff:57` 的「不带 included 键」表述为「键存在、值为空 list」，并撤回「fallback 路径保持不变」的措辞。
- C5（P3-1，建议）补 persisted `included_missing_page_ids` 端到端断言或显式登记覆盖缺口。
- C6（P3-2/P3-3，建议）修日志头（引号包裹解释器路径、补 shell/command），并以 `git log --format=%cI` 校正 release 时间口径。

**推荐下一步（可直接转发）**：

> 你是 ZCode（M2-FIX-EXPORT-LINEAGE 作者，worktree=`G:/CODEX/New Manga.worktrees/M2-FIX-EXPORT-LINEAGE-zcode`，branch=`agent/zcode/M2-FIX-EXPORT-LINEAGE`）。DSH r1 结论为 `approved_with_conditions`（报告：`reviews/M2-FIX-EXPORT-LINEAGE-<tip>-dsh-r1.md`）。请在**允许路径**内关闭条件 C1–C4（C5/C6 建议一并处理）：(1) 对 `verification/M2-FIX-EXPORT-LINEAGE/raw/red-pre-fix-test_ac2_history.log` 的 46/56/59 行与 `raw/regression-final.log` 的 35/54/69 行做**仅行尾空白**清理（traceback 文案逐字保留），手写重写 `raw/diff-check-evidence.log` 并登记 pre-clean tip=`0ec1f052`；amend 后在**新 tip** 复跑 `tests/m2_acceptance -q`、`tests/core -q`、`tests/m2_acceptance -q --runxfail` 并把新 HEAD/EXIT 写入日志；(2) 在 `verification-results.md §8` 如实登记 amend 轨迹（含 `e05696fd`/`cba8db48` 来历）并补 name-status/schema 计数的范围自检 raw 日志；(3) 修正 `verification-results.md:35/:58` 与 Handoff 风险条目中「SKIPPED/CANCELLED/FAILED 不带 included 键」为「键存在、值为空 list」；(4) 更新 ledger 表为实际 hash。完成后回填 Task `review`/`dispatch_state`，交 Codex 集成复跑。禁止改 `schema.py`、禁止改 F-2 场景与无关断言。

无需 Reviewer 侧追加动作；DSH 侧不再有阻塞项。
