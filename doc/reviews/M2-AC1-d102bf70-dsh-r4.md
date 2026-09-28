---
task_id: M2-AC1
reviewer: DeepSeek Harness (非作者)
author: ZCode (heavy_task_executor)
base_commit: 7db0e7b6ef77b5d403e3d485dc1378d4c786bc7d
reviewed_head: d102bf70 (branch tip；r3 返修 793693a5 + whitespace d102bf70)
previous_review: doc/reviews/M2-AC1-cd261f70-dsh-r3.md (decision: approved, 条件批准)
decision: approved
review_mode: 静态 Review（沙箱仍无法执行 git / pytest / cargo / npm）
---

# Review r4：M2-AC1 end-to-end acceptance on the M2 baseline

- Task=M2-AC1
- reviewed head=branch tip `d102bf70`（r3 返修 `793693a5` + whitespace `d102bf70`）
- 演进：`7d157858`(r1) → `5a59ddfe`(r1 返修) → `d8c1173b`(r2) → `521d96ca`(r2 返修) → `b9d9a8ab`(日志重采) → `a57e4834`(终版 gate) → `cd261f70`(r3) → `793693a5`(r3 返修) → `d102bf70`(whitespace)
- base=`7db0e7b6ef77b5d403e3d485dc1378d4c786bc7d`
- decision: **approved**（无条件；仅余 P3×1 / P4×4 建议项）

## 0. Review 口径与沙箱限制

**仍为纯静态 Review。** 本会话 `pwsh` 工具在本沙箱内依旧不可用（任何命令返回
`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\M2-AC1-zcode)`）。
我**未执行**任何 git / pytest / cargo / npm / `run_e2e.py`，**未复跑任何测试**；结论均来自**读取证据文件并与声明逐项对照**。commit 与文件的实际对应关系**无法用 git 验证**。`git show a74ce105:…` 的取回命令我也**未能实际执行**，仅核验其书写正确、路径存在且被写在三处。

## 1. 逐条 R3-xx 复核结论

### R3-01（P2，唯一必改：全仓回归行如实陈述）— **通过**

- `doc/tasks/M2-AC1.md` **L63** 现为：**"非本 Task 引入的 2 failed**：最终重采 `2 failed, 1320 passed, 5 skipped, EXIT 1`——失败集中在 Legacy QML 行点击测试 `tests/ui_shell/test_repair13_import_entry.py`（Task 禁改域 `tests/ui_shell/**`，与本 Task 19 路径零交集）；同一时刻在零 M2-AC1 改动的主 checkout @1347a67c 复现完全相同 2 失败（base 对照）；同工作区当天早些时候曾 **1322 passed / EXIT 0**（历史日志取回：`git show a74ce105:verification/M2-AC1/pytest-full-suite.log`）→ 判为会话级环境回归；失败原样保留未隐藏"。
- Handoff **L55** 同口径（"**非本 Task 引入的 2 failed**：… `git show a74ce105:verification/M2-AC1/pytest-full-suite.log` … 失败原样保留"）。
- 与证据一致：`pytest-full-suite.log` L405 `2 failed, 1320 passed, 5 skipped` / L406 `# EXIT: 1`；`ui-shell-base-control-20260928.log` 复现同 2 个 FAILED。
- **r3 的 P2 阻断项已完全消除**：不再有"PASS / EXIT 0"与 FAIL 日志并存的矛盾陈述；Integrator 照抄不会再得到错误口径。

### R3-02（P3，场景计数统一）— **通过（含 1 处残余，见 R4-02）**

- Task **L61**：`GATE PASS **45 场景**，含 EVN-pyside6 环境门…r1 前 36 场景旧格式存档` ✅
- Handoff **L52**：`GATE PASS **45 场景**…e2e-evidence 为 r1 前 36 场景旧格式存档` ✅
- `e2e-evidence/NOTE.md` **L10**：`（36 场景 vs 终版 45 场景）` ✅
- 我逐条复核 `"id":` 计数：`e2e-gate-full/raw/e2e-gate.json` = **45**（12 env/build 含 `EVN-pyside6` + 15×2 样本 + 1 跨样本 + 1 总判定）；`e2e-evidence/raw/e2e-gate.json` = **36**。三处新数字**均正确**。
- 残余：同一 NOTE.md **L5** 仍写"（r1 返修后、完整构建版、**44 场景**）"，与本文件 L10 自相矛盾 → **R4-02**。

### R3-03（P3，AC3 引用方式）— **通过**

Handoff **L49** 现为：`PASS（restart-desktop-pid-differs / restart-core-pid-differs 场景两样本均 PASS；具体 PID 数值随每次运行不同，见 gate JSON，如终版 desktop 40300→25468、core 42264→39912）`，证据列改为 `e2e-gate.json restart-*-pid-differs 场景`。
我核对终版 gate JSON L151–L164：desktop `40300→25468`、core `42264→39912` —— **与所举例值一致**，且"数值随运行不同"的限定已写明。

### R3-04（P3 治理，补 disposition）— **通过**

`verification/M2-AC1/` 下现同时存在：
- `review-dsh-r1-disposition.md`（既有）
- `review-dsh-r2-disposition.md`（新增，28 行）：R2-01..R2-07 逐条 disposition + 证据指针；R2-01 如实写"**fixed（r3 复核进一步修正，见 R3-01/R3-02/R3-03）**"并承认"首轮更新遗留三处"；R2-02 如实记录 vitest 重定向缺陷由 R3-05 补齐 ✅
- `review-dsh-r3-disposition.md`（新增，23 行）：R3-01..R3-08 逐条 + §遗留 ✅

三份 disposition 链条完整，Codex 集成时可逐条对照。

### R3-05（P4，vitest 日志重采）— **通过**

`vitest.log` 现为 18 行：L1 `# toolchain: node v24.15.0 / npm 12.0.1`、**L2 `# worktree HEAD: cd261f70844e9bd42b0375454ec73d05650bc6eb`**、**L3 `# worktree clean: 1 dirty paths`**、L14 `19 passed`、**L15 `Start at 12:12:16`**、L18 `# EXIT: 0`。
- **确系新运行**：r3 我读到的同一文件为 `Start at 11:32:17` / `Duration 335ms`；现为 `12:12:16` / `318ms`，且新增 HEAD 与 clean 头。Owner 对"r2 轮重定向缺陷导致未落盘"的解释与我 r3 的观察一致，**指正被接受并已修复**。
- 交付内容未被削弱：`commandSurface.test.ts (8 tests)`、合计 `19 passed`，与 r3 口径相同。

### R3-06（P4，head 演进链）— **基本通过（末环未命名，见 R4-05）**

Handoff **L63** 现完整列出：`aaf21a13`→`7d157858`（r1 被审）→`5a59ddfe`（r1 返修 + r1 disposition 链接）→`d8c1173b`（r2 被审 + r2 报告链接）→`521d96ca`（r2 返修 + r2 disposition 链接）→`b9d9a8ab`（日志重采）→`a57e4834`（终版 gate 45 场景）→`cd261f70`（r3 被审 + r3 报告链接）→ r3 返修提交（R3-01..08 + r3 disposition 链接）。
每环带报告/处置链接 ✅。末环写"r3 返修提交"而未命名 `793693a5`/`d102bf70` → **R4-05**（轻微）。

### R3-07（P4，历史日志取回命令）— **通过**

三处齐备：
- Task **L63**：`（历史日志取回：git show a74ce105:verification/M2-AC1/pytest-full-suite.log）` ✅
- Handoff **L55**：`` `git show a74ce105:verification/M2-AC1/pytest-full-suite.log` `` ✅
- `e2e-evidence/NOTE.md` **L14**：`` `git show a74ce105:verification/M2-AC1/pytest-full-suite.log` `` ✅

命令书写正确（路径与文件实际所在位置一致），且我已确认 `a74ce105` 是 Handoff 提交链中记录的 r1 证据提交。

### R3-08（P4，base 对照日志重采）— **通过（质量提升明显）**

`ui-shell-base-control-20260928.log` 现为 80 行，逐项满足我的要求：

| 我 r3 的保留意见 | 现状 | 行号 |
|---|---|---|
| 无时间戳，"同一时刻"不可核验 | `# captured at: 2026-09-28T12:13:04+08:00`（ISO） | L5 |
| 对照 commit 与 base 关系未写明 | `@ 1347a67c145f3f99a7199af0827fb18c8a007190 (zero M2-AC1 changes; 1347a67c is 7db0e7b6 + docs only)` | L1 |
| 未标注是定向而非全量对照 | `# scope: tests/ui_shell/test_repair13_import_entry.py only (5 tests) — targeted control, not a full-suite run` | L2 |
| 无解释器/工具链头 | `# interpreter: …TASK-012-py312/Scripts/python.exe` + `# Python 3.12.3` | L3–L4 |
| 无 EXIT | `# EXIT: 1` | L80 |
| 缺少根因线索 | 完整 QML stderr（L6–L41）+ 两个失败完整 traceback（L44–L78）：`ChapterList.qml:31 Cannot read property 'chapterListModel' of null`、`BookDetailPanel.qml:17 'selectedBook' of null`、`BookshelfToolbar.qml:59/66/71/77 … of null` 等 | L6–L78 |

- 根因线索与我 r3 的"点击注入对会话状态敏感"判断一致：QML viewmodel context 的多个属性在会话中为 `null`，导致行点击无法把 `currentChapterId` 传到 `bookDetailPanel`（L51–L57 `assert detail.property("currentChapterId") == chapter_id` 失败），`btnImport` 因此保持 disabled（L67–L71）。
- **环境事件披露（r3 §2）据此进一步成立，接受维持不变**：失败集中在 Task 禁改域 `tests/ui_shell/**` 与 `src/ui/qml/**`，零 M2-AC1 改动 checkout 复现同 2 失败，Task 强制门（4/26/19/45）全部不受影响。

## 2. 终版证据复核（静态，未变）

| 项目 | 核验 | 判定 |
|---|---|---|
| gate JSON 未被本轮扰动 | 仍为 416 行、lab `m2ac1-e2e-kjlttumy`、L2 `implementation_commit=b9d9a8ab2c5e4608bfcd6d7e388b5725c719d539` | ✅ |
| verdict / 场景 | L415 `"verdict": "PASS"`；45 个 `"id":` 全部 `"status": "PASS"` | ✅ |
| runner 绑定 | L4 `runner_executable` = TASK-012-py312 venv；L14–L19 `EVN-runner-python` = 同路径 + `3.12.3`；L7–L12 `EVN-pyside6` = 6.11.2 PASS | ✅ |
| 确定性 | 跨 r1/r2/r3 三次 full gate：`f66af60a9846`/`4afc67386c25` 与 `pixel_sha b191d8e5fad6` 完全一致 | ✅ |
| 四条强制门 | 4 passed EXIT 0 / 26 passed EXIT 0 / 19 passed EXIT 0 / GATE PASS 45 场景 | ✅ 均有可核验日志 |

## 3. 新增 findings（r4）

| ID | 级别 | 文件/行 | 问题与影响 | 证据 | 建议 |
|---|---|---|---|---|---|
| R4-01 | P3 | `doc/handoffs/M2-AC1-zcode-delivery-20260928.md` L35（§范围审计）；`doc/tasks/M2-AC1.md` L62 | §范围审计 仍只覆盖 `git diff --name-status 7db0e7b6..035bbdf9`（19 路径），而 Task L62 的"范围与 whitespace"行承诺"固定 **reviewed head**；…**全路径审计**见 Handoff §范围审计"。reviewed tip `d102bf70` 相对 base 的路径集合自 r2 起已新增 `verification/M2-AC1/**`、`doc/reviews/**`、`doc/handoffs/**` 等（本轮又新增 3 个 disposition/NOTE 文件与 4 个日志重采）。这些**都在 Task L44 允许清单内**（`verification/M2-AC1/**`、本 Task 文件、`doc/handoffs/M2-AC1-*.md`）或评审惯例允许（`doc/reviews/**`），但**未在 §范围审计 中逐项列出**，Task 行所指向的"全路径审计"因此不覆盖其声明的 head。这是 r2 R2-01 建议中"reviewed-tip 路径计数"一半未落实的残余 | Task L62 vs Handoff L35；`glob verification/M2-AC1/*.md` 新增 `review-dsh-r2/r3-disposition.md` | 在 Handoff §范围审计 补一行 reviewed-tip 增量枚举（或明确写"§范围审计 覆盖实现 commit `035bbdf9`；其后的 reviewed-tip 增量全部落在 Task 允许清单的 `verification/M2-AC1/**` 与 `doc/handoffs/**`、`doc/reviews/**` 面"）。**非阻断**：结论本身（无越界路径）未被推翻 |
| R4-02 | P4 | `verification/M2-AC1/e2e-evidence/NOTE.md` L5 | 同一文件内自相矛盾：L5 写"（r1 返修后、完整构建版、**44 场景**）"，L10 已改为"36 场景 vs 终版 **45** 场景"。R3-02 的计数修正漏改了 L5 这一处 | NOTE.md L5 vs L10；终版 gate JSON 实测 45 | 把 L5 的"44 场景"改为"45 场景"（或删除该处数字，只留 L10 的口径） |
| R4-03 | P4 | `verification/M2-AC1/review-dsh-r3-disposition.md` L14 | 该处置声明"**四日志格式统一**（interpreter/toolchain + HEAD + **clean 计数** + EXIT）"，与实测不符：`cargo-test.log`（L1–L2）与 `pytest-m2-acceptance.log`（L1、L3）**均无** `# worktree clean` 行，仅 `vitest.log`（L3）与 `pytest-full-suite.log`（L4）有。同句"cargo/vitest/m2-acceptance 头部 HEAD=521d96ca"亦与 `vitest.log` L2（`cd261f70`）矛盾。处置文件的表述精度即 Codex 的核对依据，宜准确 | `grep "worktree clean"` 命中 2/5 个日志（另含对照日志无该行） | 修正为"四日志均有 HEAD + EXIT；其中 vitest/pytest-full-suite 含 clean 计数；cargo/m2-acceptance 捕获于干净 tip `521d96ca`，vitest 重采于 `cd261f70`" |
| R4-04 | P4 | `verification/M2-AC1/pytest-full-suite.log`（头部 L1–L12） | 该日志**无时间戳**，而 Task L63 / Handoff L55 陈述"同一时刻 / 同时刻复现"。目前"同时刻"只能靠旁证（`ui-shell-base-control` 的 `captured at: 12:13:04+08:00` 与 `vitest.log` L15 `Start at 12:12:16` 落在同一会话窗口）。建议全仓日志也记录 ISO 时间戳，使该陈述可直接核验 | Task L63 / Handoff L55 的措辞 vs `pytest-full-suite.log` L1–L12 无时间戳 | 在四套件日志头部统一加 `# captured at: <ISO8601>`（对照日志已有此字段，可直接对齐） |
| R4-05 | P4 | Handoff L63（演进链末环） | 末环写"→ r3 返修提交（R3-01..08 处置，disposition）"而**未命名** `793693a5`（r3 返修）/`d102bf70`（whitespace），与本链其余各环均写具体 hash 的风格不一致；front-matter L6 亦仅写"branch tip" | Handoff L6、L63 | 补上 `793693a5`、`d102bf70`，使链尾可精确定位 |

**级别汇总（r4 新增）**：P0=0、P1=0、P2=0、P3=1（R4-01）、P4=4（R4-02…R4-05）。**均非阻断项。**

**r3 findings 最终台账**：R3-01 ✓通过、R3-02 ✓通过（余 1 处计数，R4-02）、R3-03 ✓通过、R3-04 ✓通过、R3-05 ✓通过（经时间戳证实真重采）、R3-06 ✓基本通过（R4-05）、R3-07 ✓通过、R3-08 ✓通过（质量显著提升）。

## 4. 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| `git diff --name-status` / `git diff --check` | 未执行（沙箱 `pwsh` 不可用） | — | **NOT_RUN** | §0 |
| `git show a74ce105:verification/M2-AC1/pytest-full-suite.log` | 未执行（同上）；仅核验命令书写与路径 | — | **NOT_RUN** | Task L63、Handoff L55、NOTE.md L14 |
| `python -m pytest tests/m2_acceptance -q` | 未执行；引用 Owner 日志 | TASK-012-py312；HEAD `521d96ca` | **NOT_RUN（引用 PASS：4 passed, EXIT 0）** | `pytest-m2-acceptance.log` L1–L6 |
| `cargo test --locked` | 未执行；引用 Owner 日志 | cargo 1.98.1；HEAD `521d96ca` | **NOT_RUN（引用 PASS：26 passed, 0 failed, EXIT 0）** | `cargo-test.log` L1–L2、L58 |
| `npm test`（vitest） | 未执行；引用 Owner 日志 | node v24.15.0 / npm 12.0.1；HEAD `cd261f70`；1 dirty path | **NOT_RUN（引用 PASS：3 files, 19 passed, EXIT 0；已确认真重采，`Start at 12:12:16`）** | `vitest.log` L1–L3、L14、L15、L18 |
| 全仓 pytest | 未执行；引用 Owner 日志 | TASK-012-py312；HEAD `521d96ca` | **NOT_RUN（引用 FAIL：2 failed, 1320 passed, 5 skipped, EXIT 1；非本 Task 引入，披露已接受，表格陈述已如实修正）** | `pytest-full-suite.log` L3–L12、L405–L406；`ui-shell-base-control-20260928.log` L1–L5、L79–L80 |
| `python verification/M2-AC1/run_e2e.py`（终版证据） | 未执行；引用 gate JSON | `implementation_commit` = `b9d9a8ab…`；runner = TASK-012-py312 venv | **NOT_RUN（引用 PASS：45 场景全 PASS，verdict PASS）** | `e2e-gate-full/raw/e2e-gate.json` L2、L4、L415 |
| R3-02 计数核验（静态） | 逐条枚举 `"id":`；grep 全库残留旧计数 | reviewed tip | **PASS（45 / 36 三处一致；仅 NOTE.md L5 残留"44"，见 R4-02）** | 两 gate JSON；`grep "44 场景\|27 场景"` |
| R3-05 重采核验（静态） | 比对 vitest 的 `Start at`、`Duration`、头部字段 | r3 vs r4 | **PASS（11:32:17/335ms → 12:12:16/318ms，新增 HEAD+clean）** | `vitest.log` L1–L3、L15–L16 |
| R3-08 对照日志核验（静态） | 逐项对照我 r3 的 5 条保留意见 | 对照 checkout `1347a67c` | **PASS（时间戳/关系/scope/解释器/EXIT/根因线索全部补齐）** | `ui-shell-base-control-20260928.log` L1–L5、L79–L80 |
| R3-01 表格陈述核验（静态） | 读 Task L63 与 Handoff L55，与 `pytest-full-suite.log` 比对 | reviewed tip | **PASS（PASS/EXIT 0 与 FAIL 日志并存的矛盾已消除）** | Task L63；Handoff L55 |

**Architecture 面结论**：**通过，自 r2 起未变**。本轮改动限于文档与验收日志（`doc/tasks`、`doc/handoffs`、`verification/M2-AC1/**`）；生产代码路径（`mock_local_providers` 唯一入口、ac1 命令面三重钉死、生产 registry 判别测试）零改动，gate 证据文件未被扰动。

**Verification 面结论**：**通过（无条件）**。四条 Task 强制门 + E2E gate（45 场景）均有可核验证据；`EVN-pyside6` 环境门、`implementation_commit`/`runner_executable` 机器绑定、跨三次 gate 运行的摘要与像素摘要一致性共同支撑 AC1–AC6。唯一不通过的全仓行已被**如实披露**为"非本 Task 引入的 2 failed"，并附零改动 checkout 的定向对照与完整根因线索——该处置比"绿色通过"更具可审计性。

## 5. 结论

**decision: approved（无条件）**

- **r3 的 8 条全部落实**：唯一 P2（R3-01）已修正且与证据一致；3 条 P3 中 R3-02/R3-03/R3-04 全部通过；4 条 P4 全部通过，其中 R3-05 经运行时间戳证实为**真正重采**，R3-08 的对照日志重采质量显著超过我的要求（补齐 commit 关系、scope、解释器、ISO 时间戳、EXIT 与完整根因线索）。
- **无 P0/P1/P2**。r4 仅新增 P3×1（范围审计未覆盖 reviewed tip）与 P4×4（NOTE.md L5 计数残留、r3 disposition 的一处表述不准、全仓日志缺时间戳、演进链末环未命名 commit），**全部为非阻断的建议项**。
- AC1–AC6 与终版 gate 证据链完整、未被本轮触碰；`implementation_commit=b9d9a8ab`、45 场景全 PASS、确定性三次一致。

**建议（不阻断，交 Codex 集成时择机处理）**：R4-01 补 reviewed-tip 的范围审计说明；R4-02 修正 NOTE.md L5；R4-03 修正 r3 disposition 的日志格式表述；R4-04 四日志统一加时间戳；R4-05 演进链末环补 hash。

**仍待 Codex 裁决（非 Owner 权限，自 r1 起维持）**：**F-008** —— `apps/desktop/src-tauri/build.rs`、`capabilities/m2rc1-commands.json`、`gen/schemas/*.json` + `permissions/autogenerated/ac1_*.toml` 三组 ACL 联动文件的范围追认。技术论断（属 Task L41 条款的机制必然产物、无生产面扩张）已由 F-003 的单测守卫强化，但**范围授予须由 Codex 在 integration record 中显式记录**。

**剩余风险**：Qt/字体渲染的跨机确定性仍是已声明的同机假设（三次同机一致，不外推）；planner regionless `LOCK_CHANGED` 缺口未修，需另行登记 Task；Legacy QML `test_repair13_import_entry.py` 的 2 个失败为会话级环境回归（根因线索指向 QML viewmodel context 注入为 null），**建议由 Codex/Qoder 另行登记诊断，不在本 Task 内处理**；F-006/F-010ab 维持 deferred；`git diff --check` 与集成门复跑仍应由 Codex 单独立证。

**复审方式**：本报告为 r4 终轮静态复核；若后续有新的返修 head，请附对应 disposition，复审追加新记录，不抹掉 r1–r4 记录。

---
*本报告为只读评审产物，未修改任何实现文件、测试、Task 文件或证据。所有行号引用基于 reviewed tip 工作区静态内容。*
