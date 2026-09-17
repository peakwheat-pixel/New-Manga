---
task_id: TASK-039
reviewer: ZCode 子 agent（窗口授权同体审查；结论仅 approved_subagent/changes_requested，T1 后须 Codex+DeepSeek 外部 post-hoc 复审）
author: ZCode（窗口第二轮 W6 Owner）
base_commit: 047164e
reviewed_head: 38fbde4（docs head 0a81255 = 纯文档追加，未触碰 reviewed_head 内容）
decision: approved_subagent
---

# Review：TASK-039（修复 planner `_clean_available` 继承缺陷，head 38fbde4）

Reviewer 为窗口内 ZCode 子 agent，与实现者同属 ZCode（窗口授权条款允许，但 `approved_subagent` **不等同**跨 Agent 独立批准；期满后由 Codex + DeepSeek Harness 补外部 post-hoc 复审）。

## 范围与依据

- **diff 口径澄清**：`git diff 047164e..38fbde4` 包含 W5（TASK-038）已集成内容——W6 分支按 Task 指示 `git merge master` 快进至 post-W5 HEAD（6533c39 父为 0297d4a）。**TASK-039 实现本体 = `git diff 6533c39..38fbde4`**（= `git show 38fbde4`），恰 3 文件 +303/−4：`src/application/tasks/service.py`、`tests/pipeline/test_clean_availability.py`（新建）、`verification/TASK-039/discriminability-pre-fix.log`。文档区间 `38fbde4..0a81255` 仅 TASK-039 handoff / Task 文档 / full-suite-runs.log。
- 依据：TASK-039.md（AC ①–⑤、允许/禁止范围）、handoff TASK-039-38fbde4.md、REVIEW 模板两轴口径、09_COLLABORATION §6 及窗口例外条款、`git show 047164e:src/application/tasks/service.py`（修前源）、`src/infrastructure/providers/handlers.py`（机理）、`_COMMAND_STEPS`/`_forced_steps`（矩阵结构核对）。
- **未审到部分**：W5（TASK-038）内容不在本次审查对象内（已有独立 review fcf791f + 集成 f835ac9）；`tests/providers` 未触碰（与 handoff 声明一致）。

### Git 布局检查（§2 口径）

`--show-toplevel` = `G:/CODEX/New Manga.worktrees/TASK-039-zcode`；`--git-common-dir` = `G:/CODEX/New Manga/.git`（同一仓库 linked worktree ✓）；branch = `agent/zcode/TASK-039-clean-availability`；HEAD = `0a81255`；`git status --short` 干净。

## Standards（轴状态：executed）

**隔离偏差声明**：本次为单线程子 agent，无并行独立线程；按 §6 第 6 条兜底做了**两遍相互隔离**的检查——第一遍只对白名单/禁止范围/仓库标准条款逐条过 diff（不看 AC），第二遍只对 Task AC 原文逐项过 diff（不想标准），未用一遍通读充当两轴。

逐条核对（依据文件 + 条款）：

1. **白名单**（TASK-039.md 允许修改范围）：实现本体 3 文件全部在白名单（`src/application/tasks/service.py`、`tests/pipeline/**`、`verification/TASK-039/**`）；文档提交仅 TASK-039.md / handoff / verification log。`git diff 6533c39..0a81255` 对 `doc/STATUS.md`、`doc/tasks/README.md`、`doc/00_INDEX.md`、`src/bootstrap/**`、`AGENTS.md` **零触碰**（grep diff 为空）。
2. **禁止范围**（TASK-039.md）：对实现 diff grep `decide_route|acceptable_routes|preferred_route_order|route_gate|sfx|skip_policy|schema|migration` **零命中**；`src/infrastructure/pipeline/**`、`src/application/translation/pipeline/**` 零改动；新测试文件 grep `skip|xfail` 零命中，无既有测试文件被修改（diff 仅新增文件，无断言放宽/删除）。
3. **AGENTS.md / 02 技术架构**：QML 不触碰；分层方向保持（见 Architecture 轴）。
4. **09_COLLABORATION §3.6/§4**：passed/skipped 分列 ✓（0 skipped）；证据入库 `verification/TASK-039/**` ✓。
5. **Fowler baseline 判断项**（仓库未记录标准的方面，均为判断项非硬违规）：
   - possible Duplicated Code：`test_clean_availability.py` 的 `_service`（:61）与 `_service_on_ocr_ready_region`（:148）结构高度重复，可合并为带 catalog 参数的单 helper。影响小，不阻断。
   - possible Dead Code：`test_clean_availability.py:107` 的 `@pytest.mark.parametrize` 挂在 helper `_catalog_with_ocr_ready_region()` 上（非测试函数），为无效装饰器 → 见 R-003。

**小结**：Standards 轴 2 个发现（R-003 P3、R-001 涉及证据登记准确性 P2），最严重项 R-001。

## Spec（轴状态：executed）

逐条对照 TASK-039.md AC 原文：

- **AC ①（根因，须行级证据）——满足，机理陈述属实**。修前 `git show 047164e:src/application/tasks/service.py` `_clean_available`：`return stages.get("clean", StageState.NOT_STARTED).is_valid or previous.get("inpaint") is PlanDecision.RUN`。机理核实：`StageState.is_valid` 仅 `COMPLETED` 为真（domain/tasks/models.py:144-147）；`handle_inpaint` 的 stage 提交经 `_commit_artifacts`（handlers.py:732-756），其返回 `{}, {unit.step_type: StageState.COMPLETED}` → 对 inpaint 即 `{"inpaint": COMPLETED}`，Clean **指针**走 `adopt_current` CAS（handlers.py:751-755）；全仓生产代码 grep `"clean"` 无任何 stage 写入者（仅 artifact type/存储目录/UI 模式名）。→ 判据一对真实数据恒 false 的根因陈述**属实**；既有夹具手写 clean stage（test_pipeline.py:81 r1）的"隐蔽原因"陈述也属实。
- **AC ②（修复 + 守卫不放宽）——满足**。三分支：同 run `inpaint is RUN` → 有效 `clean` stage → `probe(page_id)`。修前 `A or B`，修后 `B or A or (probe and probe(page_id))`：probe=None 时布尔等价（or 交换律），既有 81 个 pipeline/core 测试全数保持为最强佐证；probe 只能在 artifact 真实存在时把本会 BLOCKED 翻成 RUN，不能反向（or 链末端、只增 True）。命令枚举核实：`_RERENDER = ("render",)` 服务 RERENDER_ALL/SELECTED/SINGLE/REGION 同一元组、同一 forced 集（service.py:103-105,514-515）——handoff"SINGLE 语义与 ALL/SELECTED 同判据路径"成立。**生产注入点（bootstrap）未实现且已如实登记**：grep `clean_probe` 全仓仅 service.py 内部 3 处，bootstrap 零引用、零改动 ✓（未偷偷改 bootstrap）。
- **AC ③（对照矩阵）——满足，口径张力见 R-004**。矩阵断言与 `_COMMAND_STEPS` 结构逐项一致：`_RETRANSLATE=(translate,render)`、`_REINPAINT=(segment,mask_refine,inpaint)`（无 render，结构性不受影响）、`_RERENDER=(render,)`、`_REOCR=(ocr,)`（无 render）；同 run 短路由 `_FULL_TRANSLATION` 的 `retranslate_region_full` 覆盖；手写 clean stage 尊重有独立用例。**probe=present 时 translate 族 render RUN 的口径独立判定：作者"修复泛化"口径成立**。理由：(a) `_clean_available` 是全部 render 单元的共享判据（唯一调用点 service.py:437），物理上无法只修 RERENDER 族而不影响含 render 步的 TRANSLATE/RETRANSLATE 族——若按命令族分支才是未经授权的新行为；(b) 生产现状 probe 未注入，生产行为与修前逐字节一致，"不波及"在当前生产完全成立；(c) probe=present 下的翻转方向只有 BLOCKED→RUN 且仅当 artifact 真实存在，与 AC ② 守卫语义一致；(d) REOCR_*/REINPAINT_* 无 render 单元，结构性不触发改动。该口径应留档供 post-hoc 复审参考。
- **AC ④（判别力 + 回归）——判别力与回归实测成立；登记叙述两处失实（R-001、R-002）**。实测见验证表：本 Reviewer 独立实跑 38fbde4 全仓 **780 passed / 0 skipped、exit 0**（与作者 ×5 日志及 W5 基线 772+8=780 交叉吻合）；`tests/pipeline+tests/core` 实测 **89 passed**（≠ handoff 写的 81，见 R-001）；判别力日志文件真实（7 failed/1 passed exit 1）但其"唯一通过"归因叙述与日志矛盾（见 R-002）。
- **AC ⑤**——未完成属**符合时序**（待本 Review 与集成后登记），AC 勾选状态与实际一致，非缺陷。
- **scope creep**：无 diff 中来源未要求的行为（probe 默认 None、bootstrap 未动）。

**小结**：Spec 轴 3 个发现（R-001 P2、R-002 P2、R-004 P3 口径登记），最严重项 R-001/R-002（均为文档叙述失实，不涉代码行为）。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态/修订 commit |
|---|---|---|---|---|---|---|
| R-001 | P2 | doc/handoffs/TASK-039-38fbde4.md「验证证据」表第 2 行 | 表登记"pipeline+core 回归 \| commit `38fbde4` \| 81 passed / 0 skipped"。实测 `38fbde4` 上为 **89 passed**（81+新增 8 例）；81 实为修前 base `047164e` 的数量。数字与 commit 不匹配，误导后续复审对回归覆盖的判断（不影响代码正确性，全仓 780 口径真实） | 本 Review 实跑：`pytest tests/pipeline tests/core -q -p no:cacheprovider -rf` → `89 passed in 4.93s` EXIT=0；collect-only：pipeline+core=89、新文件=8 → 修前=81；W5 全仓 772+8=780 交叉印证 | 集成前以文档提交修订该行（81→89，或注明 81 为 base `047164e` 数并补 89 的 `38fbde4` 实测） | open |
| R-002 | P2 | doc/handoffs/TASK-039-38fbde4.md「AC ④」段；doc/tasks/TASK-039.md 交付记录同句 | 两处声称判别力"唯一通过项是'probe=missing 时 BLOCKED 保持'守卫测试"。日志 `discriminability-pre-fix.log` FAILED 列表**包含**该守卫测试（`test_render_only_command_stays_blocked_when_probe_reports_missing`）；实际唯一通过 = `test_hand_written_clean_stage_still_counts_for_future_writers`（该例不传 `clean_probe` kwarg，修前构造可用且手写 clean stage 判据成立）。机理：修前 `PipelineService.__init__` 不接受 `clean_probe`，传 kwarg 的 7 例全部 TypeError 失败。判别力结论（7 failed / exit 1）本身成立，但归因与自家日志直接矛盾 | 日志第 4 行 `FAILED ...::test_render_only_command_stays_blocked_when_probe_reports_missing`；7 个 FAILED 名单反推唯一通过例 | 集成前以文档提交把归因改为"唯一通过=手写 clean stage 用例（修前判据对该夹具即满足）；守卫例失败系修前构造器无 `clean_probe` kwarg（TypeError）" | open |
| R-003 | P3 | tests/pipeline/test_clean_availability.py:107-125 | `@pytest.mark.parametrize` 挂在 helper `_catalog_with_ocr_ready_region()` 上，为无效装饰器；其数据表中 `translate_region`/`reocr_single`/`reinpaint_region` 预期未作为执行断言存在，读者易误认为参数化用例在跑。行为无影响（pytest 忽略非 test 函数上的 mark），8 例计数不受影响 | `grep -n "pytest.mark" tests/pipeline/test_clean_availability.py` 仅 ：107 一处且紧邻 `def _catalog_with_ocr_ready_region()` | 删除该装饰器及死数据表（或改写为真正的参数化测试）；可顺带合并 `_service`/`_service_on_ocr_ready_region`（possible Duplicated Code，判断项） | open（可 deferred 至后续测试卫生切片） |
| R-004 | P3 | doc/handoffs/TASK-039-38fbde4.md「AC ③」矩阵 probe=present 列 vs TASK-039.md AC ③ 原文 | AC ③ 字面"TRANSLATE_*/RETRANSLATE_* 规划决策与理由**逐项不变**"与矩阵（probe=present 时 retranslate render BLOCKED→run）存在表述张力。**本 Review 独立判定作者"修复泛化"口径成立**（判定理由见 Spec 轴 AC ③ 四点），非缺陷行为，但字面张力应留档 | `_clean_available` 唯一调用点 service.py:437（`step_type == "render"`）；probe=None 下 81 个既有测试逐字节保持；生产 bootstrap 未注入 probe | 登记口径供 post-hoc 复审；如后续注入生产 probe，集成验证须覆盖 translate 族 render 翻转场景 | accepted（口径裁定） |

在记录范围内未发现其他问题：无越界改动、无守卫放宽、无 skip/xfail、无 P0/P1。

## 验证

Reviewer 实跑 shell 口径：**Git Bash（Git for Windows / MINGW64）会话直接调用** `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`，`PYTHONDONTWRITEBYTECODE=1`，worktree `G:/CODEX/New Manga.worktrees/TASK-039-zcode`（HEAD=0a81255，src 与 38fbde4 一致）。与作者口径（`powershell.exe -NoProfile` 包装继承 PATH 含 openssl）不同：本 Reviewer 未包装、直接 Git Bash 调用，无 ssl 导入错误，两次实跑均正常完成——两口径在本次均可复现，exit 0。

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| pipeline+core 回归 | `python -m pytest tests/pipeline tests/core -q -p no:cacheprovider -rf` | TASK-012-py312 venv / 0a81255(=38fbde4 src) | **PASS：89 passed / 0 skipped，exit 0**（作者记 81，见 R-001） | 本 Review 实跑输出 |
| 全仓回归 | `python -m pytest -q -p no:cacheprovider -rs -rf` | 同上 | **PASS：780 passed / 0 skipped，exit 0**（与作者 ×5 日志一致） | 本 Review 实跑输出；verification/TASK-039/full-suite-runs.log |
| 用例数交叉验证 | `pytest ... --collect-only -q`（pipeline+core；新文件） | 同上 | **PASS：89 = 81(修前) + 8(新增)**；W5 全仓 772+8=780 吻合 | collect-only 输出 |
| 判别力核对 | 逐行核对 discriminability-pre-fix.log FAILED 名单 vs 8 例名单 | 38fbde4 日志文件 | **PASS（日志真实）/ FAIL（叙述）：唯一通过=手写 clean stage 例，非守卫例**（R-002） | 日志第 3-10 行 |
| 禁止范围 grep | diff grep `decide_route\|acceptable_routes\|preferred_route_order\|route_gate\|sfx\|schema\|migration`；seam/bootstrap/AGENTS/STATUS diff stat | 6533c39..0a81255 | **PASS：零命中/零触碰** | 本 Review grep 输出 |
| 根因机理 | 修前源 `git show 047164e:...service.py`；`handle_inpaint`/`_commit_artifacts`（handlers.py:732-756）；全仓 `"clean"` stage 写入者 grep | 047164e + 0a81255 | **PASS：无人写 `clean` stage，判据一恒 false 属实** | 本 Review 引用行号 |
| skip/xfail 排查 | grep `skip\|xfail` 于新测试文件 | 38fbde4 | **PASS：零命中** | grep 输出 |

## 结论与复审

**decision = `approved_subagent`**（固定 reviewed_head `38fbde4`）。理由：修复本体正确且最小（三分支保序、probe=None 判定等价、守卫未放宽）、白名单与禁止范围零违规、根因机理核实属实、判别力与全仓回归经本 Reviewer 独立实跑证实（89/780 passed、exit 0）。R-001/R-002 为 Handoff 与 Task 文档中的**证据叙述失实**（不涉代码行为，但违反"测试结果只能适用于记录的 commit"的准确性精神），**建议 Codex 集成前要求 Owner 以纯文档提交修订**（不影响 reviewed_head）；R-003 测试卫生可 deferred；R-004 口径已裁定并留档。

剩余风险：(1) 生产 probe 注入点（bootstrap）在白名单外移交后续装配切片——注入前生产 render-only 命令保持既有 BLOCKED 行为（不比修前差），注入时须按 R-004 口径补集成验证；(2) 窗口内 `approved_subagent` 不等同独立批准，本结论对 T1 后外部 post-hoc 复审**可被推翻**。
