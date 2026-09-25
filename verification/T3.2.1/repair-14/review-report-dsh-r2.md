---
task_id: T3.2.1-REPAIR-14
round: 2
reviewer: DeepSeek Harness
author: Antigravity
base_commit: 4ab6f58c06cb0691413e2630cb48a145c18c383a
reviewed_delivery: 43b24eefaa1d517f51c7fd8dba7c658a58415d89
reviewed_head: 2f0d26645a5e3597977859f0624d72f561d38ba1
supersedes: verification/T3.2.1/repair-14/review-report-dsh.md (Round 1, changes_requested @ 4301939)
decision: approved
---

# Review（Round 2）：T3.2.1-REPAIR-14

Reviewer 为 DeepSeek Harness（独立非作者）。本结论只对 `43b24ee`（产品与验证）与 `2f0d266`（含 Handoff）有效，分支后续变化不延用。

## 范围与依据

| 项 | 值 |
|---|---|
| Fixed base | `4ab6f58c06cb0691413e2630cb48a145c18c383a` |
| Delivery（产品+验证） | `43b24eefaa1d517f51c7fd8dba7c658a58415d89`，parent=`9cff94f` |
| Tip（含 Handoff） | `2f0d26645a5e3597977859f0624d72f561d38ba1`，parent=`43b24ee`，仅新增 Handoff |
| 分支 | `agent/antigravity/T3.2.1-repair-14`，tip 与上述一致 |
| Handoff | `doc/handoffs/T3.2.1-REPAIR-14-43b24ee.md`（114 行） |
| Round 1 结论 | `4301939` `changes_requested`（R14-001、R14-002 为 P1） |
| Review 环境 | 独立 worktree `G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-repair-14-r2`，branch `agent/deepseek/T3.2.1-review-repair-14-r2`，基于 `2f0d26645a5e`；Python 3.12.3（`T3.2.1-packaging-py312`） |
| 独立 artefact | [dsh-review-r2-independent-run.log](dsh-review-r2-independent-run.log)、[dsh-review-r2-ac4-rerun.log](dsh-review-r2-ac4-rerun.log) |
| 作者工作区 | 复核前后 `git status --porcelain` 均为空 |

**派发 SHA 澄清（R14-011）**：派发指令给出的 handoff head `2f0d266bb0368a5c378e90635436eeaf8cb2451f` **在本仓库中不存在**（`git cat-file -t` → `could not get object info`）。分支实际 tip 为 `2f0d26645a5e3597977859f0624d72f561d38ba1`（共享 7 位前缀 `2f0d266`）。本 Review 以实际存在的对象为准；`43b24ee` 与 `2f0d26645a5e` 均为可达对象，交付内容本身未受影响。

审查覆盖：`base..delivery` 全部 17 个路径、Round 2 产品/测试 diff、AC4 探针源码与运行日志、两张截图（**Reviewer 亲自查看**）、EXE 二进制（**Reviewer 独立复算哈希**）、全部证据日志。未覆盖：父 T3.2.1 Gate 与 AC3 相关范围。

## Round 1 findings 处置核验

| 编号 | 级别 | Round 1 要求 | Round 2 独立核验 | 结论 |
|---|---|---|---|---|
| R14-001 | P1 | `git diff --check` 声明须为 exit 0，且清单须覆盖全范围 | 独立复跑：`git diff --check base..43b24ee` → **exit 0**；`base..2f0d26645a5e` → **exit 0**。尾部空白与 EOF 空行均已清除（Round 1 的 5 处全部消失） | **CLOSED** |
| R14-002 | P1 | 固定 EXE 两次启动验证或缺豁免登记 | 见下节「AC4 独立核验」 | **CLOSED**（附 R14-008 表述问题） |
| R14-003 | P2 | 收敛 E303 连续空行 | `viewmodel.py` 相对 base 现仅新增 1 行（`self._apply_books()`），其下 1 个空行，PEP8 合规；测试文件类间恰为 2 个空行。Round 1 指出的 59-60 与 77-79 均已收敛 | **CLOSED** |
| R14-004 | P2 | 日志 UTF-8 可读 | `post-repair-verification.log` 现为 `title=修复验证漫画`，无 mojibake；独立复跑同样正常 | **CLOSED** |
| R14-005 | P2 | Task 状态同步（Codex 侧） | 主线 `master` 的 `doc/tasks/T3.2.1-REPAIR-14.md` 已更新：`status: changes_requested`、`base_commit/branch/worktree` 齐备、`implementation_release: RELEASED`；master tip `75fa4d7` | **CLOSED**（`delivery_head/evidence_head` 仍指 Round 1 值，属正常流程待更新） |
| R14-006 | P2 | 纠正探针性质表述 | 新 Handoff 中「完全一致」仅出现在引述被纠正措辞的说明句（§2 R14-006 行）；§3 已改用「服务装配层重启验证」 | **CLOSED** |
| R14-007 | Note | 判别力与全量回归 | 独立复跑一致：**184 passed in 11.06s, exit 0**（详见验证表） | **CLOSED** |

## AC4 独立核验（Round 1 R14-002）

| 核验动作 | 独立结果 |
|---|---|
| EXE 存在性 | `G:\CODEX\repair14-build-out\NewManga\NewManga.exe` **存在**，50,521,372 字节 |
| EXE SHA-256 | Reviewer **独立复算** = `6aee41b2e36d203e3404000ac89f4f5efaee5d075c8888669fb0760133cc0145`，与 `repair14-delivery-exe.sha256`、`ac4-exe-gui-run.log:8` 声明**完全一致** |
| 产物完整性清单 | `repair14-delivery-artifact-manifest.sha256` 共 **5437 行**（`NewManga.exe` + `_internal/**` 全量哈希） |
| 截图真实性来源 | `src/bootstrap/app.py:1139-1164` 的 `--screenshot` 路径为**真实产品代码**：`window.show()` 后经 `QQuickWindow.grabWindow()` 抓取真实渲染帧再保存，非脚本合成 |
| 截图 01（提交版） | Reviewer **亲自查看**：书架空态——「还没有作品」+「新建作品/导入作品」，右侧「未选择作品」 |
| 截图 02（提交版） | Reviewer **亲自查看**：左侧作品卡片「固定包验证作品·第…／Fixed Package Manga…／进度 —」，右侧详情面板「固定包验证作品·第一卷」+ 标签/进度/收藏/归档 + 章节列表「01 第01话／分页：从右到左 · 0 页」；空状态消失 |
| **AC4 探针独立重跑** | Reviewer 在独立 worktree 内重跑 `verify_ac4_exe_gui.py`：**exit 0**，两次真实 OS 进程启动（Session 1/Session 2 均 exit 0），重启后 `SQLite books count after restart: 1` |
| 重跑截图 | 01=40330 字节、02=68449 字节；与提交版（40329/68405）**非 bit-identical**，符合真实 GUI 渲染的非确定性；Reviewer 亲自查看重跑版 02，渲染内容与提交版一致 |

**结论**：R14-002 的验证目标（重启后书架卡片与作品详情可见、SQLite 行数保持 1、无重复/数据破坏）在**真实固定包 GUI 路径**上成立，且经 Reviewer 独立复现。原 P1 解除。

## Round 2 Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R14-008 | P2 | `verification/T3.2.1/repair-14/verify_ac4_exe_gui.py:103-115`、`:179`；`ac4-exe-gui-run.log:17-19,37`；Handoff §2 R14-002 行／§3 AC4 行 | 代码与日志声称「Session 1：首启空态、**建书**、优雅退出」，但脚本实际在 Session 1 进程**结束之后**才通过 `assemble_services` 直接写库播种（第 108-115 行），截图 01 亦证明 Session 1 内无任何建书动作。Task R14-AC4 的字面要求是「**首启创建作品**后正常关闭」。影响：AC4 的验证目标已达成（重启后渲染既有作品），但表述与实现不符，且「首启建书」未按字面完成。 | `verify_ac4_exe_gui.py:103-115` 位于 `p1` 结束之后；`ac4-exe-gui-run.log` 第 17 行 `--- Seeding Book in Data Root ---` 出现在第 14 行 `Session 1 Exit Code: 0` 之后 | 二选一：① 修正 Handoff/脚本日志措辞为「Session 1 空态退出后由脚本播种数据」；② 若 Codex 要求逐字满足 AC4，则改为在 Session 1 GUI 内完成建书（需交互或新增产品侧建书参数）。**不影响验证有效性**，请 Codex 裁定 | open |
| R14-009 | P2 | `repair14-delivery-exe.sha256`、Handoff §2 R14-002 行 | 固定包 EXE 位于仓库外 `G:\CODEX\repair14-build-out\`，且 `git ls-tree -r 43b24ee` 中**无任何打包脚本或 spec**（仅两个 sha256 记录文件）。产物哈希与 5437 行清单证明了完整性，但**无法复现构建**，第三方不能重建该 EXE。 | `git ls-tree -r --name-only 43b24ee` 仅含两个 `.sha256`；EXE 路径在仓库外 | 建议 Codex 记录该验证路线的环境前提，或将打包脚本/spec 纳入父 T3.2.1 Gate 的交付范围 | open |
| R14-010 | P2 | Handoff §2（「13 个变更路径」）／§4（17 项）；`diff-check.log` 第 12-28 行（16 项） | 三处变更清单计数互不一致，且均与实际不符：实际 `base..43b24ee` 为 **17 项**、`base..2f0d26645a5e` 为 **18 项**（含两个 Handoff）。作者 `diff-check.log` 的 16 项漏了 Round 1 的 `doc/handoffs/T3.2.1-REPAIR-14-56bd33a.md`；Handoff §4 的 17 项含本轮 Handoff 却漏 Round 1 Handoff。影响：清单精确性，不影响 R14-001 结论（`git diff --check` 覆盖整个范围且 exit 0）。 | `dsh-review-r2-independent-run.log` `[3]` 段：count=17 及逐项列表 | 集成时以 `git diff --name-status base..<head>` 的实际输出为准；修正 Handoff 计数 | open |
| R14-011 | P2 | 派发指令（非交付物） | 派发提供的 handoff head `2f0d266bb0368a5c378e90635436eeaf8cb2451f` 在仓库中不存在；实际 tip 为 `2f0d26645a5e3597977859f0624d72f561d38ba1`。若下游直接引用该 SHA 将无法解析。 | `git cat-file -t 2f0d266bb036…` → `fatal: could not get object info` | 修正派发/登记记录中的 SHA；建议以完整 40 位 SHA 记录，避免 7 位前缀歧义 | open |
| R14-012 | Note | `verify_ac4_exe_gui.py:74-75,188-190`；`post-repair-verification.py`（Round 2 版） | 两个探针会**就地重写被审证据文件**（截图、`ac4-exe-gui-run.log`、`post-repair-verification.log`）。Reviewer 复跑后必须 `git checkout --` 恢复，否则被审工作区出现非提交差异。 | 本轮复跑后 `git status` 曾显示 3 个证据文件为 `M`，恢复后干净 | 探针输出应写往独立路径（或加 `--out` 参数），避免覆盖已提交证据 | open |

## 验证

全部由 Reviewer 在独立 worktree 实际执行；输出见 [dsh-review-r2-independent-run.log](dsh-review-r2-independent-run.log) 与 [dsh-review-r2-ac4-rerun.log](dsh-review-r2-ac4-rerun.log)。

| 场景 | 命令 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| R14-001 空白审计（delivery） | `git diff --check base..43b24ee` | 43b24ee | **PASS** exit 0 | log `[1]` |
| R14-001 空白审计（tip） | `git diff --check base..2f0d26645a5e` | 2f0d26645a5e | **PASS** exit 0 | log `[1]` |
| 受保护路径 | `git diff --exit-code base..43b24ee -- src/domain src/application src/ports packaging requirements.txt requirements-dev.txt doc/tasks doc/STATUS.md doc/REBASELINE_PLAN.md` | 43b24ee | **PASS** exit 0，零差异 | log `[2]` |
| 变更范围 | `git diff --name-status base..43b24ee` | 43b24ee | **PASS** 17 路径，全部在 Task 冻结范围内（3 M + 14 A） | log `[3]` |
| 全量回归套件 | `python -m pytest tests/ui_shell tests/reading_export/test_qml_contract.py tests/core/test_bootstrap.py` | py3.12.3 / 43b24ee | **PASS** `184 passed in 11.06s`，0 skipped，exit 0 | log `[4]` |
| 装配层重启探针 | `python verification/.../post-repair-verification.py` | 同上 | **PASS** exit 0（isEmpty=False、bookCount=1、rowCount=1、title 正确） | log `[5]` |
| 复现探针（应不再复现） | `python verification/.../reproduction.py` | 同上 | **PASS（行为已改变）** exit 1 | log `[6]` |
| EXE 哈希独立复算 | `Get-FileHash NewManga.exe -Algorithm SHA256` | 本机产物 | **PASS** 与声明一致 | log `[7]` |
| R14-003 空行 | 逐行快照 | 43b24ee | **PASS** 本轮改动无连续空行（仅 base 既有的 22/23，非本次引入） | log `[8]` |
| R14-004 编码 | 读取日志标题行 | 43b24ee | **PASS** `title=修复验证漫画` | log `[9]` |
| **AC4 真机重跑** | `python verification/.../verify_ac4_exe_gui.py` | 本机 EXE | **PASS** exit 0；两次独立进程；重启后 books=1 | [ac4-rerun](dsh-review-r2-ac4-rerun.log) |
| 截图人工核验 | Reviewer 查看 01/02（提交版与重跑版） | — | **PASS** 空态 vs 已水合书架（卡片+详情+章节） | 截图文件本身 |

补充说明：`[4]` 段 stderr 中 `PrimaryNavigationRail.qml:30/38`、`ReaderView.qml:204` 的 `TypeError` 属既有 QML 加载噪声，相关文件不在本次 diff 内，**非本次引入**。

## 结论与复审

**Architecture：PASS。** 产品改动为单行构造期 hydration，仍未越出 `ui → application` 依赖方向，未触碰 `src/domain/**`、`src/application/**`、`src/ports/**`、Schema、packaging（受保护路径 diff 为空）。

**Verification：PASS。** Round 1 的两项 P1 均已闭环，且 AC4 在**真实固定包 GUI 路径**上由 Reviewer 独立复现；184 passed 独立复跑一致；空白与受保护路径审计 exit 0。

**decision: `approved`** ——`43b24ee`（含 Handoff `2f0d26645a5e`）可交 Codex 集成。

剩余风险均为非阻塞 P2/Note：R14-008（AC4「首启建书」表述与实现不符，验证目标已达成）、R14-009（EXE 构建不可复现）、R14-010（变更清单计数不一致）、R14-011（派发 SHA 不可解析）、R14-012（探针就地覆盖证据）。建议 Codex 在集成记录中一并处置 R14-008 与 R14-010 的表述，并按需决定 R14-009 是否纳入父 Gate。

本次 Review 不改变父 T3.2.1 Release Gate（`OPEN`）、父 AC3（`BLOCKED`）或 REPAIR-13 的状态。复审如追加新 head，应保留本记录并另行登记 disposition。
