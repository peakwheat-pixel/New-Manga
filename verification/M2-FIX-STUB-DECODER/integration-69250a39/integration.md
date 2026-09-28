# M2-FIX-STUB-DECODER 集成记录（integration-69250a39）

## ① 身份与授权

| 项 | 值 |
|---|---|
| Integrator | Codex（ZCode 子 agent 会话代行 Codex 身份，用户授权 2026-09-28） |
| Owner | ZCode（另一子 agent，用户授权 2026-09-28）——**Owner ≠ Integrator** |
| Reviewer | DeepSeek Harness（非作者静态 Review r1） |
| 主 repo | `G:/CODEX/New Manga`，分支 `main`，集成前 HEAD=`fc419905c6a5b151f089d9fd78f7fccea97efb7b`（release commit，核实一致） |
| Owner worktree | `G:/CODEX/New Manga.worktrees/M2-FIX-STUB-DECODER-zcode`，分支 `agent/zcode/M2-FIX-STUB-DECODER`，HEAD=`69250a39ac3ff48c13c28cfd34241eb9fb78a494`，`git status --porcelain` 空 |
| base | `f5d91425`；交付 tip=`5cacebfa25ef17ea3a487ac4fcb11a4590636661`（amend 后）；最终 tip=`69250a39`（Task 回填 commit） |
| 执行环境 | Windows x64 · Git Bash（GNU bash 5.2.37 msys）· `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3 · pytest 9.1.1） |
| 执行时间 | 2026-09-29T00:58–01:01 +08:00 |

## ② DSH r1 结论与归档

- 结论：**approved_with_conditions**，0×P0 / 0×P1 / 0×P2，6×P3 全不阻塞。
- 报告归档：`doc/reviews/M2-FIX-STUB-DECODER-69250a39-dsh-r1.md`（原字节复制自 `/tmp/m2fixstub-review/dsh-r1-result.md`）。
- SHA256（两文件一致）：`d17b4262466ce4b9382b63319859f44c40aeb3c498db03692b61908c3a7d7fe6`。

## ③ C1 固定 head 复跑（worktree `69250a39` 代跑，关闭 C1）

每条日志带头（shell / `python --version` / `git rev-parse HEAD` / ISO 时间戳）、尾记 EXIT。

| # | 命令（$py、wt=Owner worktree） | 期望 | 实际 | EXIT | 日志 |
|---|---|---|---|---|---|
| 1 | `$py -m pytest tests/core/test_stub_decoder.py -v` | 2 passed | **2 passed**（0.34s） | 0 | `raw/c1-test_stub_decoder.log` |
| 2 | `$py -m pytest tests/core/ -q` | 76 passed | **76 passed**（7.68s；日志含 QML 无关 stderr 噪音，不影响判定） | 0 | `raw/c1-tests_core.log` |
| 3 | `$py -m pytest tests/m2_acceptance -q` | 32 passed + 2 xfailed | **32 passed, 2 xfailed**（9.64s；F-1/F-2 strict xfail 未翻 XPASS） | 0 | `raw/c1-m2_acceptance.log` |

三条日志头 `git rev-parse HEAD` 均为 `69250a39ac3ff48c13c28cfd34241eb9fb78a494`（真实固定 head）。**C1 关闭。**

## ④ C2 范围与最小性复算（关闭 C2，替代 Owner 自检）

| # | 命令 | 期望 | 实际 | EXIT |
|---|---|---|---|---|
| 1 | `git diff --name-status fc419905..5cacebfa` | 仅 Task 允许路径；tests 侧仅 A `tests/core/test_stub_decoder.py` | `A doc/handoffs/M2-FIX-STUB-DECODER-owner-delivery.md`、`M doc/tasks/M2-FIX-STUB-DECODER.md`、`M src/bootstrap/core_service.py`、`A tests/core/test_stub_decoder.py`、`A verification/M2-FIX-STUB-DECODER/raw/02..05.log`、`A verification/M2-FIX-STUB-DECODER/verification-results.md` —— 全部允许路径 | 0 |
| 2 | `git diff f5d91425..5cacebfa -- src/`（+numstat） | 仅 `core_service.py` +3/-1 | `3 1 src/bootstrap/core_service.py`；diff 内容 = 2 注释行（:54-55，注明 `mime_type="image/rgb"` 取值理由）+ 1 代码行（:56 构造改 `mime_type="image/rgb"`） | 0 |
| 3 | `git diff --check f5d91425..5cacebfa` | 无输出，EXIT=0 | 无输出 | 0 |
| 补充 | `git log --format=%H%n%s 0f4f881a..69250a39` | （DSH §3 写"期望 3 条"） | 实际 2 条：`5cacebfa`（accept/amend 结果）+ `69250a39`（task backfill，message 逐字含 `delivery tip=5cacebfa`）；amend 前身 `550b4269` 为 dangling commit 仅存 reflog，与 DSH §0 ledger 描述及 Owner 披露的 whitespace-only amend 轨迹一致 | 0 |

日志：`raw/c2-scope-recheck.log`。**C2 关闭。**

## ⑤ P3-1..P3-6 处置表

| 条目 | 内容摘要 | 处置 | 状态 |
|---|---|---|---|
| P3-1 | 交付描述"一行注释"与实际 +3/-1 不符 | 本集成记录正式记作 **+3/-1**（2 注释行 `core_service.py:54-55` + 1 代码行 `:56`），与 `git diff --numstat` 一致 | 已关闭（集成侧） |
| P3-2 | `mime_type` 具体值 `"image/rgb"` 未被测试承重（仅非空 str 断言）；值当前无消费者 | 不扩张本 Task 范围；登记为可选后续加固（收紧断言为 `== "image/rgb"`），如做随未来 core_service 测试维护顺带 | 已登记（不阻塞） |
| P3-3 | 新测试耦合私有名 `_PassthroughImageDecoder` / `core.importer._decoder` | 经 DSH 核对符合仓库既有惯例（`test_core_assembly.py:225` 等），identity 断言由既有测试覆盖 | 已登记（无需处理） |
| P3-4 | 红/绿证据不绑定 commit；Owner 披露省略回滚再证红 | **集成侧补做红证**：在 tip `69250a39` 上把 `core_service.py:56` 临时改回 `format="rgb"` → 新套件 **2 failed**，两用例红点均为 `TypeError: DecodedImage.__init__() got an unexpected keyword argument 'format'` @ `src\bootstrap\core_service.py:56`，EXIT=1；随后 `git checkout --` 还原（EXIT=0），`git status --porcelain src/` 输出空（零残留）。日志 `raw/p3-4-red-evidence.log` | 已关闭 |
| P3-5 | `delivery_head` 未落 Task frontmatter | 本集成修正 commit 回填 `delivery_head: 5cacebfa25ef17ea3a487ac4fcb11a4590636661`（注意：交付 tip=5cacebfa；最终 tip=69250a39 为 Task 回填 commit） | 已关闭（见 Task frontmatter） |
| P3-6 | `assemble_production_core` 中 `font_catalog/layout_engine/compositor=object()` 同类 stub（`core_service.py:84-86`） | 范围外观察**保留原样**，本次不扩张；image import 链已真实走通，渲染/排版类命令需另立 Task | 已登记（另立 Task，归主会话/规划） |

## ⑥ 集成动作

| 项 | 值 |
|---|---|
| merge 命令 | `git merge --no-ff agent/zcode/M2-FIX-STUB-DECODER -m "integration: merge M2-FIX-STUB-DECODER stub signature fix (owner tip 69250a39, DSH r1 approved_with_conditions 0xP0/P1/P2, C1-C2 closed)"` |
| merge 结果 | 无冲突（'ort' strategy），10 files changed, +411/-14 |
| merge hash（$MERGE） | `121a281cbf65f62c57b177efc44fa4649b11c9ae` |
| 集成修正 commit | `integration(M2-FIX-STUB-DECODER): …`（本记录 + DSH 报告归档 + Task frontmatter 回填；hash 见 commit 历史） |
| 无关改动保护 | merge 前后 `git status --porcelain` 均含 35 行无关未提交改动（apps/desktop/**、permissions/**、verification/M2-RC2/** 等），未被 add / checkout / 覆盖 |
| 集成 head 复跑 | 见 §⑦ |

## ⑦ 集成 head 复跑

- 命令：`$py -m pytest tests/core/test_stub_decoder.py tests/m2_acceptance -q`（主 repo 集成修正 commit 上）
- 结果：**34 passed, 2 xfailed**（= 新套件 2 + m2_acceptance 32；strict xfail 2 保持 xfailed），EXIT=0。
- 日志：`raw/integration-head-rerun.log`。

## ⑧ 集成后收尾边界

- 不 push、不删除分支、不动 Owner worktree 历史。
- `doc/STATUS.md` 与 `doc/REBASELINE_PLAN.md` 不由本集成修改（主会话编排收口负责）。
