---
task_id: M2-AC1
reviewer: DeepSeek Harness (非作者)
author: ZCode (heavy_task_executor)
base_commit: 7db0e7b6ef77b5d403e3d485dc1378d4c786bc7d
reviewed_head: cd261f70 (branch tip；r2 返修 521d96ca → 日志重采 b9d9a8ab → gate 证据 a57e4834 → whitespace cd261f70)
previous_review: doc/reviews/M2-AC1-d8c1173b-dsh-r2.md (decision: approved, 条件批准)
decision: approved
review_mode: 静态 Review（沙箱仍无法执行 git / pytest / cargo / npm）
---

# Review r3：M2-AC1 end-to-end acceptance on the M2 baseline

- Task=M2-AC1
- reviewed head=branch tip `cd261f70`
- 演进：`7d157858`（r1）→ `5a59ddfe`（r1 返修）→ `d8c1173b`（r2 被审）→ `521d96ca`（r2 返修）→ `b9d9a8ab`（日志重采）→ `a57e4834`（终版 gate 证据）→ `cd261f70`（whitespace）
- base=`7db0e7b6ef77b5d403e3d485dc1378d4c786bc7d`
- decision: **approved（条件批准）**

## 0. Review 口径与沙箱限制

**仍为纯静态 Review。** 本会话 `pwsh` 工具在本沙箱内依旧不可用（任何命令返回
`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\M2-AC1-zcode)`）。
我**未执行**任何 git / pytest / cargo / npm / `run_e2e.py`，**未复跑任何测试**；所有结论来自**读取证据文件并做内容自洽性核对**。`521d96ca` / `b9d9a8ab` / `cd261f70` 等 commit 与文件的实际对应关系我**无法用 git 验证**。

## 1. 逐条 R2-xx 复核结论

### R2-01（P2 必须，Handoff 证据表数字）— **不通过**

| 我 r2 要求 | 现状 | 判定 |
|---|---|---|
| cargo 25→26 | Handoff L53 = "26 passed, 0 failed，含 F-003 ACL 全命令断言与 F-011 argv 钉死" | ✅ 与 `cargo-test.log` L56 `26 passed` 一致 |
| vitest 18→19 | Handoff L54 = "3 files, 19 passed" | ✅ 与 `vitest.log` L12 `19 passed` 一致 |
| AC6 场景口径 | Handoff L52 = "最终 gate GATE PASS **44** 场景" | ❌ **实际 45**（见下） |
| front-matter delivery_head | Handoff L6 = `035bbdf9 / a74ce105 / 5a59ddfe / branch tip（见 §接收方式 head 演进）` | ✅ 已改为演进表述 |
| §接收方式 演进链 | Handoff L63 有 `aaf21a13 → 7d157858 → 返修 head`，但**未命名** r1 返修 commit（`5a59ddfe`），亦未含 `d8c1173b/521d96ca/b9d9a8ab/a57e4834/cd261f70` | △ 不完整 |
| 全仓回归行 | Handoff L55 = "PASS（1322 passed, 5 skipped, exit 0…）"，引用 `pytest-full-suite.log` | ❌ **所引日志现为 `2 failed, 1320 passed, 5 skipped` / `# EXIT: 1`** |
| AC3 行 PID | Handoff L49 = "desktop 34580→8720、core 22156→35268" | ❌ 该组是 **r1 旧运行**的数值；当前 gate JSON 为 40300→25468 / 42264→39912 |

**结论：不通过。** 我要求的"数字与验证日志一致"只落实了 cargo/vitest 两行；AC6 场景数（44 vs 45）、全仓回归陈述（PASS/EXIT 0 vs FAIL/EXIT 1）、AC3 引用（旧 PID）三处仍与证据不符。详见 R3-01/R3-02/R3-03。

### R2-02（P2 必须，日志 HEAD/dirty 标注）— **不通过（4 缺 1）**

我实测四个日志的头部（`grep worktree` 全量）：

| 日志 | worktree HEAD | worktree clean | EXIT |
|---|---|---|---|
| `cargo-test.log` | L2 `521d96ca13c76057b1567aea516d03c10ace782f` ✅ | 无 | L58 `# EXIT: 0` |
| `pytest-m2-acceptance.log` | L3 `521d96ca…` ✅ | 无 | L6 `# EXIT: 0` |
| `pytest-full-suite.log` | L3 `521d96ca…` ✅ | L4 `# worktree clean: 1 dirty paths` ✅ | L406 `# EXIT: 1` |
| `vitest.log` | **无 HEAD 行** ❌ | 无 | L16 `# EXIT: 0` |

- **r2 的核心问题已解决**：`cargo-test.log` 的 HEAD 不再是"不含被测代码的提交"，且 `pytest-full-suite.log` 明确披露了 dirty 状态（`1 dirty paths`）——这正是我要求的"记录 HEAD + 工作区状态"。
- **但 r3 简报所述"cargo / vitest / pytest-m2-acceptance 头部 worktree HEAD=521d96ca"与文件不符**：`vitest.log` 只有 L1 `# toolchain: node v24.15.0 / npm 12.0.1`，**没有 HEAD 行**；且其正文 `Start at 11:32:17` / `Duration 335ms` / `19 passed` 与我 r2 读到的内容**逐字相同**（r1 为 `Start at 11:02:34`），说明 **vitest 未在 521d96ca 重采**，仍是 r2 捕获的同一文件。
- 实质影响评估：前端代码在 r2 捕获之后未见改动（`commandSurface.test.ts` 仍为 8 tests，`App.tsx`/`driver.ts` 未变），故 `19 passed` 结论**仍然成立**；缺陷仅在标注一致性与"统一四份日志格式"的承诺未兑现。**判定：不通过（需补 vitest HEAD，或四个日志统一补 dirty 计数），但非实质验证缺失。**

### R2-03（P3，旧存档 stale 标注）— **通过（含一处数字错误）**

- `verification/M2-AC1/e2e-evidence/NOTE.md` 已建立（12 行）✓，正确说明：旧格式无 `implementation_commit`/`runner_executable`、`EVN-python` 实为 PATH 系统 Python 3.14.6 的工具链探测（F-005 歧义）、并指向 `e2e-gate-full/` 为准。**满足 R2-03 的要求。**
- **但 L10 的数字两处皆错**："（27 场景 vs 44 场景）" —— 我逐条数该存档 `e2e-gate.json` 的 `"id":` 共 **36** 条，最终 gate 为 **45** 条。见 R3-02。

### R2-04（P4，新场景 null/缺键健壮性）— **通过**

`verification/M2-AC1/run_e2e.py`：

- L309 `saved2 = run2.get("saved") or {}`；L343 `exported = run2.get("exported") or {}` —— null 容忍 ✅
- L310–L311 `isinstance(..., list)` 守卫；L313–L315 `page_sort_key` 容忍非 dict/非 int；L317–L323 `pages_comparable()` 要求 dict + int `index` + str `sha256` ✅
- L325–L331 不可比对时 `gate.record(...,"FAIL",{"error":"saved pages missing index/sha256 keys"})` 并 `return None` —— 记 FAIL、不崩溃、fail-closed ✅
- L356–L359 `output_path` 的 `isinstance`/非空校验（r1 F-010c）仍在 ✅

### R2-05（P4，implementation_commit 静默空串）— **通过**

`run_e2e.py` L469–L489：`except (OSError, TimeoutExpired) → "UNKNOWN"`（L484–L485），并新增 L486–L488 `if completed.returncode != 0 or not commit: return "UNKNOWN"`。静默空串路径已消除 ✅。当前 gate JSON L2 `implementation_commit = b9d9a8ab2c5e4608bfcd6d7e388b5725c719d539`（非空、与 r3 简报一致）。

### R2-06（P4，ACL 测试 doc 注释陈旧）— **通过**

`apps/desktop/src-tauri/src/main.rs` L435–L438 现为"the app manifest declares exactly the **ten** live commands (seven resource-channel + three M2-AC1 acceptance; R2-06)"，与紧随其后的循环（L455–L464，probe ∪ ac1 共 10 条命令）一致 ✅。

### R2-07（P4，PySide6 环境探测 → BLOCKED）— **通过**

`run_e2e.py` L91–L99：`try: import PySide6` 成功取 `PySide6.__version__`，失败（`OSError/ImportError`）记 `EVN-pyside6` FAIL；L105 `usable = pyside6_ok` 并入环境判定；`main()` L425–L429 在 `not env_usable` 时写 `E2E-gate = BLOCKED`、`write_gate`、`return 2` ✅（符合 gate docstring L13 的"unusable environment → BLOCKED, never PASS"）。
证据：gate JSON L7–L12 `EVN-pyside6` = `{"version":"6.11.2"}` PASS；该场景现在**可失败**，不再是我 r2 指出的恒真场景。

## 2. 环境事件披露的接受性判定

**判定：披露成立，接受。**

事实链（我核对到的证据）：

1. `verification/M2-AC1/pytest-full-suite.log` L3 `# worktree HEAD: 521d96ca…`、L4 `# worktree clean: 1 dirty paths`、L5–L12 NOTE，L405 `2 failed, 1320 passed, 5 skipped, 1 warning in 73.43s`、L406 `# EXIT: 1` —— **失败与 EXIT 1 原样保留，未隐藏**。
2. 失败明细（L375–L392）集中在 `tests/ui_shell/test_repair13_import_entry.py` 的两个 Legacy QML 行点击用例：`test_current_chapter_alias_follows_row_click`、`test_import_entry_enabled_after_row_click`（L386–L388 `assert btn.isEnabled()` 失败）。
3. 基线对照 `verification/M2-AC1/ui-shell-base-control-20260928.log`：L1 `# base control: G:/CODEX/New Manga @ 1347a67c (pre-Task main; zero M2-AC1 changes)`，L2–L3 列出**同样两个** FAILED 用例，L4 `2 failed, 3 passed`。

**接受理由**：

- 受影响文件位于 `tests/ui_shell/**`（Legacy PySide6/QML 面），而 Task §禁止范围明确"不修改 Legacy PySide6/QML"，M2-AC1 的 19 路径 diff 与 `src/ui/**`、`tests/ui_shell/**` **无交集**——失败域与改动域不相交。
- "非本 Task 引入"有**独立可复现的对照**：在零 M2-AC1 改动的 checkout（`1347a67c`）上复现同两个失败。这是判定"环境/既有回归"的正确对照形态。
- 失败模式（QML 行点击后 `btnImport.isEnabled()` 仍 False）与"点击注入对桌面会话状态敏感"的解释自洽，且同一工作区当天早些时候曾 1322 passed。
- Task 强制门（`tests/m2_acceptance` 4 passed EXIT 0、cargo 26、vitest 19、gate 45 场景）均不受影响，且 Task L65 规定"只运行实际有改动的语言套件；E2E 与范围 Gate 必须执行"——全仓行本属"Owner 加跑"。

**保留意见（不否定披露，但应补强）**：

1. 对照日志**无时间戳**，故"同一时刻（same time of day）"不可从证据核验；建议两侧都记录运行时间。
2. 对照基于 `1347a67c`（pre-Task main），而非 Task 固定 base `7db0e7b6`；作为"与本 Task diff 无关"的对照这是合理的（甚至更干净），但应在 NOTE 中写明二者的关系。
3. 对照日志只有 4 行：无 `# EXIT:`、无工具链/解释器头，且只跑了该文件的 5 个测试（对定位这 2 个失败而言足够，但应标注其为**定向对照**而非全量对照）。
4. **两处治理表格未随之更新**：`doc/tasks/M2-AC1.md` L63 与 Handoff L55 仍写"PASS（1322 passed, 5 skipped, EXIT 0）"，而它们引用的正是这份显示 FAIL 的日志。这是必须修的（R3-01）。

## 3. 最终 gate 证据核验（静态）

| 项目 | 声明 | 我的核验 | 判定 |
|---|---|---|---|
| verdict | GATE PASS | gate JSON L415 `"verdict": "PASS"`；45 个场景**全部** `"status": "PASS"`（无 FAIL/NOT_RUN/BLOCKED） | ✅ |
| 场景数 | 45（含 EVN-pyside6） | 我逐条数 `"id":` = 45：12 env/build（含 `EVN-pyside6`）+ 15×2 样本 + 1 跨样本 + 1 总判定 | ✅ |
| `implementation_commit` | `b9d9a8ab…` | L2 `b9d9a8ab2c5e4608bfcd6d7e388b5725c719d539` | ✅ 与简报一致 |
| `runner_executable` | TASK-012-py312 venv | L4 `G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe`；L14–L19 `EVN-runner-python` = 同路径 + `3.12.3` | ✅ |
| 新增 `EVN-pyside6` | 有 | L7–L12，`{"version":"6.11.2"}` PASS | ✅ |
| 确定性（跨三次 gate 运行） | — | `independent-samples-identical-summaries` L395–L406 仍为 `f66af60a9846`/`4afc67386c25`；`export-png` L236 `4afc67386c25` size 1122；`export-png-decodes` L243–L247 仍为 `pixel_sha b191d8e5fad6`、240×320 | ✅ **三次独立 full gate（r1/r2/r3）摘要与像素摘要完全一致**，确定性证据进一步增强 |
| 重启真实性 | PID 跨启动不同 | L151–L164：desktop 40300→25468、core 42264→39912 均 PASS；样本 b 同类 | ✅ |

## 4. 新增 findings（r3）

| ID | 级别 | 文件/行 | 问题与影响 | 证据 | 建议 |
|---|---|---|---|---|---|
| R3-01 | P2 | `doc/tasks/M2-AC1.md` L63；`doc/handoffs/M2-AC1-zcode-delivery-20260928.md` L55 | 两处仍宣称"全仓回归 **PASS**（1322 passed, 5 skipped, EXIT 0；零回归）"，而**它们共同引用的** `pytest-full-suite.log` 现在是 `2 failed, 1320 passed, 5 skipped` / `# EXIT: 1`。PASS 陈述与所指证据直接相反；Integrator 若照抄会把"EXIT 0"写进 integration record，正是 REVIEW 模板「证据纪律」禁止的口径。叠加：早前 1322-passed 的那份日志已被覆盖，只能经 git 历史取回 | `pytest-full-suite.log` L3–L12、L405–L406；`ui-shell-base-control-20260928.log` L1–L4 | 把两行改为如实陈述："返修期实测 2 failed + 1320 passed（Legacy QML 会话级环境回归，见日志 NOTE；base 对照 @1347a67c 复现同 2 失败）→ 与本 Task diff 无关；早前同工作区 1322 passed EXIT 0 见 `git show a74ce105:verification/M2-AC1/pytest-full-suite.log`"。**这是本轮唯一的必改项** |
| R3-02 | P3 | `doc/tasks/M2-AC1.md` L61；Handoff L52；`verification/M2-AC1/e2e-evidence/NOTE.md` L10 | 场景计数三处不一致且与证据不符：Task L61/Handoff L52 写 **44**（实际 **45**，新增 `EVN-pyside6`）；NOTE.md 写"**27** 场景 vs 44 场景"（旧存档实际 **36**，最终 **45**） | 我逐条数 `"id":`：`e2e-gate-full/raw/e2e-gate.json` = 45；`e2e-evidence/raw/e2e-gate.json` = 36 | 三处统一改为正确数字（45 / 36 vs 45）。注意 `EVN-pyside6` 使场景数从 44 增至 45，r2 报告里的"44"也需在此口径下更新 |
| R3-03 | P3 | Handoff L49 | AC3 行把 **r1 旧运行**的具体 PID（desktop 34580→8720、core 22156→35268）当作当前证据引用；当前 gate JSON 为 desktop 40300→25468、core 42264→39912。用已作废运行的具体数值指代现状，属证据引用失准 | Handoff L49 vs `e2e-gate-full/raw/e2e-gate.json` L151–L164 | 改为引用场景 id（`restart-*-pid-differs`）并注明"数值随每次运行不同，本处仅示例"，或更新为当前运行的数值 |
| R3-04 | P3（治理） | `verification/M2-AC1/`（缺 `review-dsh-r2-disposition.md`） | 目录下只有 `review-dsh-r1-disposition.md`；**R2-01..R2-07 没有 disposition 文件**，处置仅散见于 r3 简报与本轮文档改动中。r1 有 disposition 文件、r2 没有，流程不一致；Codex 集成时无法逐条对照 r2 findings 的 disposition | `glob verification/M2-AC1/**/*.md` → 仅 `review-dsh-r1-disposition.md`、`e2e-evidence/NOTE.md` | 补 `verification/M2-AC1/review-dsh-r2-disposition.md`（F/R2-xx → fixed/deferred/open + 证据指针），与本轮报告一同入库 |
| R3-05 | P4 | `verification/M2-AC1/vitest.log` L1 | R2-02 残留：无 `worktree HEAD` 行，且未在 `521d96ca` 重采（正文 `Start at 11:32:17`/`335ms` 与 r2 逐字相同）。四个日志格式未统一（仅 `pytest-full-suite.log` 有 dirty 计数） | `grep "worktree (HEAD\|clean)"` 命中 3 个日志，vitest.log 零命中 | 在 tip 重跑 vitest 并补 `# worktree HEAD: …` / `# worktree clean: …` 头；或统一四个日志的头格式 |
| R3-06 | P4 | Handoff L6、L63 | head 演进链未命名 r1 返修 commit（`5a59ddfe`），也未包含 r2/r3 的 `d8c1173b/521d96ca/b9d9a8ab/a57e4834/cd261f70`；front-matter 只写"branch tip（见 §接收方式）" | Handoff L6、L63 | 补全演进链（r1 被审 → r1 返修 → r2 被审 → r2 返修 → 日志重采 → gate 证据 → tip），便于后续审计按 commit 定位 |
| R3-07 | P4 | `verification/M2-AC1/pytest-full-suite.log` L5–L12 | 早前 1322-passed 的全仓日志被本次重采**覆盖**；NOTE 只说"see the pytest-full-suite.log at commits a74ce105/5a59ddfe"，未给出取回方式，审计者不会自动想到 `git show <commit>:<path>` | 同左 | 在 NOTE 中写明取回命令，或把历史日志另存为 `pytest-full-suite-<commit>.log` 一并入库 |
| R3-08 | P4 | `verification/M2-AC1/ui-shell-base-control-20260928.log` L1–L4 | 对照日志无时间戳、无 `# EXIT:`、无解释器/工具链头，故"同一时刻"与执行环境不可核验；且未标注它只跑了该文件的 5 个测试（定向对照而非全量对照） | 该文件仅 4 行 | 补时间戳 + `# EXIT: 1` + 解释器头 + 一行"scope: tests/ui_shell/test_repair13_import_entry.py (5 tests) only" |

**级别汇总（r3 新增）**：P0=0、P1=0、P2=1（R3-01）、P3=3（R3-02/R3-03/R3-04）、P4=4（R3-05…R3-08）。

**r2 findings 最终台账**：通过 5（R2-04、R2-05、R2-06、R2-07，以及 R2-03 主体）；不通过 2（R2-01、R2-02）；R2-03 附带一处数字错误（R3-02）。

## 5. 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| `git diff --name-status` / `git diff --check` | 未执行（沙箱 `pwsh` 不可用） | — | **NOT_RUN** | §0 |
| `python -m pytest tests/m2_acceptance -q` | 未执行；引用 Owner 日志 | TASK-012-py312 / 3.12.3；HEAD `521d96ca` | **NOT_RUN（引用 PASS：4 passed, EXIT 0）** | `pytest-m2-acceptance.log` L1–L6 |
| `cargo test --locked` | 未执行；引用 Owner 日志 | cargo 1.98.1；HEAD `521d96ca` | **NOT_RUN（引用 PASS：26 passed, 0 failed, EXIT 0）** | `cargo-test.log` L1–L2、L56、L58 |
| `npm test`（vitest） | 未执行；引用 Owner 日志 | node v24.15.0 / npm 12.0.1；**无 HEAD 标注** | **NOT_RUN（引用 PASS：3 files, 19 passed, EXIT 0；未重采，见 R2-02/R3-05）** | `vitest.log` L1、L12、L16 |
| 全仓 pytest | 未执行；引用 Owner 日志 | TASK-012-py312；HEAD `521d96ca`；1 dirty path | **NOT_RUN（引用 FAIL：2 failed, 1320 passed, 5 skipped, EXIT 1；披露成立、接受，见 §2；但两处表格未同步，见 R3-01）** | `pytest-full-suite.log` L3–L12、L405–L406；`ui-shell-base-control-20260928.log` |
| `python verification/M2-AC1/run_e2e.py`（完整构建版，终版证据） | 未执行；引用 gate JSON | `runner_executable` = TASK-012-py312 venv；`implementation_commit` = `b9d9a8ab…` | **NOT_RUN（引用 PASS：45 场景全 PASS，verdict PASS）** | `e2e-gate-full/raw/e2e-gate.json` L2–L4、L7–L12、L415 |
| 场景计数核验（静态） | 逐条枚举 `"id":` | reviewed tip | **PASS**（45 = 12 env/build + 15×2 + 1 跨样本 + 1 总判定） | 同上，L7–L412 |
| 跨运行确定性（静态） | 比对 r1/r2/r3 三次 gate 的摘要与像素摘要 | 三个不同 head | **PASS**（`f66af60a…`/`4afc6738…` 与 `pixel_sha b191d8e5fad6` 三次完全相同） | 同上 L395–L406、L236、L245 |
| R2-04/05/07 代码核验（静态） | 读 `run_e2e.py` L91–L105、L309–L359、L469–L489 | reviewed tip | **PASS** | 同左 |
| R2-06 代码核验（静态） | 读 `main.rs` L431–L438 | reviewed tip | **PASS**（"ten live commands"） | 同左 |
| R2-01/R2-02 一致性核验（静态） | `grep "worktree (HEAD\|clean)"` 四个日志；比对 Handoff/Task 表与 gate JSON/日志 | reviewed tip | **FAIL**（vitest 无 HEAD；Handoff L52/L55/L49 与 Task L61/L63 数字不符，见 R3-01/R3-02/R3-03） | §1、§4 |

**Architecture 面结论**：**通过**。本轮改动为 `run_e2e.py`（验收 harness）、`main.rs` 注释与文档；未触碰生产代码路径，`mock_local_providers` 唯一入口、ac1 命令面三重钉死、生产 registry 判别测试均未变。

**Verification 面结论**：**通过（AC1–AC6 依据完整且较 r2 更强）**。四条 Task 强制门（4/26/19/45）均有可核验日志与 JSON，且 gate 的确定性与像素确定性现在有**三次独立运行**的交叉印证。唯一扣分是**文档数字与证据不一致**（R3-01 P2；R3-02/R3-03 P3）与 vitest 日志未重采（R3-05）；这些都是记录问题，不改变 AC 结论。

## 6. 结论

**decision: approved（条件批准）**

- r2 的 7 条中，**4 条通过**（R2-04/05/06/07），**R2-03 主体通过**（附带数字错误），**2 条不通过**（R2-01、R2-02）。
- AC1–AC6 全部有证据支撑，且在 r3 得到**增强**：终版 gate 45 场景全 PASS（含新增 `EVN-pyside6` 环境门），`implementation_commit`/`runner_executable` 机器绑定齐备，三次独立 full gate 的摘要与像素摘要完全一致。
- 我 r2 提出的"证据健壮性"两点（null 容忍、静默空串）与两点代码/注释问题（ACL 注释、PySide6 BLOCKED）均已落实。
- **无新增 P0/P1**。剩余为 1 条 P2 + 3 条 P3 + 4 条 P4，全部是**文档/证据标注**类问题。

**批准条件（必须，交 Codex 集成前处理）**：

1. **R3-01（必须）**：把 `doc/tasks/M2-AC1.md` L63 与 Handoff L55 的全仓回归陈述改为如实反映 `pytest-full-suite.log` 的 `2 failed / 1320 passed / EXIT 1` 及环境事件披露（base 对照 + 与本 Task 无交集），并给出早前 1322-passed 日志的取回路径。**这是本轮唯一阻断集成记录的项**。
2. **R3-02（必须，一并修）**：统一场景计数为 45（Task L61 / Handoff L52 / NOTE.md L10；NOTE 中旧存档应为 36）。
3. **R3-03、R3-04（建议同批）**：更新 Handoff L49 的 PID 引用方式；补 `review-dsh-r2-disposition.md`。

**说明（为何仍判 approved 而非 changes_requested）**：R3-01 是**文档陈述**与证据不符，不是验证缺失或结论错误——AC1–AC6 的证据链完整、失败域与改动域不相交、且失败被主动披露并附独立对照。同时必须明确：这是**连续第三轮**出现同一类"文档数字/引用与证据不一致"，若 Owner 在本轮不修 R3-01/R3-02，Codex 不应把 Handoff/Task 表的数字直接写入 integration record。

**剩余风险**：Qt/字体渲染的跨机确定性仍为已声明的同机假设（三次同机一致，不外推）；planner regionless `LOCK_CHANGED` 缺口仍未修，需另行登记 Task；Legacy QML `tests/ui_shell/test_repair13_import_entry.py` 的 2 个失败为**会话级环境回归**，本轮未定位根因（建议由 Codex/Qoder 另开诊断，勿在本 Task 内处理）；F-006/F-010ab 仍 deferred；`git diff --check` 与集成门复跑仍应由 Codex 单独立证。

**复审方式**：若继续返修，请给新 head 与 R3-xx 的逐条 disposition；复审追加新 head 记录，不抹掉 r1/r2/r3 记录。

---
*本报告为只读评审产物，未修改任何实现文件、测试、Task 文件或证据。所有行号引用基于 reviewed tip 工作区静态内容。*
