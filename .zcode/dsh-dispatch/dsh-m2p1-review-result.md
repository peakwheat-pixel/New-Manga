## 结论行

**decision: approved_with_conditions**

四轴均无 P0/P1 阻断项：修复语义与诊断报告 §5.1 完全一致，走的是完整重绑路径（非半修），测试矩阵覆盖 AC2/AC3 且断言具备判别力，范围只在允许清单内。条件是实现方/Owner 侧的两处证据链对齐（见 P2），属集成记录问题，不属代码缺陷。

---

## 四轴小结

### 轴 1 — 修复语义轴：correct

- 当前实现 `src/application/tasks/service.py:921-959`，核心在 `:952-958`：`replace(item, region_id=primary, target_id=primary) if item.unit_id != unit.unit_id and item.region_id is None`。`unit_id` 排除条件保证 detect 单元自身不被改写（它是唯一被传入的 `unit`），`region_id is None` 保证已 region-scoped 的 plan 单元不被触碰——两个守卫在加入 `target_id` 重绑后语义不变，与诊断报告 §5.1「同时重绑、不改 unit_id、只绑 primary」逐条吻合（`doc/research/DIAG-M2-REGIONLESS-LOCK-CHANGED-001.md:63-69`）。
- 时序正确：`service.py:650-656` 在 detect 提交成功后调用 backfill，`_mark_terminal`/`_persist` 在其后；`_record_step_attempt` 在下一次循环（`service.py:787`）才发生，因此 `service.py:605-618` 的快照必然取自重绑后的 `unit.target_id`。索引式循环 `service.py:760-763` 确实每轮重读 `task.units`（同级注释 `:755-759` 已说明），与 `:948-951` 注释一致。
- docstring 声明与实现一致：`:927-932` 写明 `PlanUnit.target_id ≡ 写目标` 及 `_record_step_attempt` 以 target_id 为快照键；`:934-937` 写明不改 `unit_id` 的原因（`terminal_unit_ids` 为键）；`:939-942` 保留多 Region 只绑 primary 的既有语义。实现就是该声明，无过度声明功能（措辞精度问题见 P3）。

### 轴 2 — 测试判别力轴：strong（抽查 R0/R1/N1/N7 + N2/N6 旁证）

- **R1**（`tests/pipeline/test_regionless_rebinding.py:306-340`）：`executed_unit_ids == planned_unit_ids`（`:324`）固定「不改 unit_id」；`detect_unit.target_id == PAGE_ID / region_id is None`（`:332-333`）固定 detect 单元未被误改；`ocr_unit.target_id == ocr_unit.region_id == primary_id`（`:336-337`）直接固定 AC1 的核心断言；`terminal_step_units == planned_step_units == 2`（`:340`）封住终态计数不丢不双计。判定：真实固定语义，非弱断言。
- **R0**（`:257-303`）：`run COMPLETED`、`ocr_step.target_id == region_id == primary`、`input_refs` 含 `region` 键（`:282-285`）、`region_revisions` 恰 2 条且 `revision_no` 1→2（`:289-298`）、`current_revision_id` 前进到第二版且 `ocr_text` 落库（`:300-303`）。这正是被修缺陷的「先绿」正命题，判别力充分。
- **N1**（`:450-500`）：篡改 `step_run.input_refs["region"]`（`:469`）后断言 `LOCK_CHANGED`（`:490`）且 `region_revisions == 1`（`:493-500`）。判别力成立：若走到 catalog 的锁分支会得到 `INPUT_REVISION_CHANGED`（`service.py:660-661`），只有 `RegionStepWriter._persist` 的前置守卫（`src/infrastructure/providers/step_writes.py:219-231`，异常在写 INSERT 之前抛出、`:278-280` 回滚）才会产生 `LOCK_CHANGED`，故该断言真的锁定了「守卫仍生效 + 零写」。半修判别已在 docstring `:453-460` 说明（措辞偏松，见 P3）。
- **N7**（`:645-729`）：真实走 `recover_running_runs()` → `plan_run(mode="continue")` → `execute_run`，断言 `step_runs` 累积为 4、两次 COMPLETED OCR 分别落在两个 Region、`terminal_unit_ids` 重置为 0、无重复 Region（`:692-729`），与诊断报告 §4「重启自愈、必须固定两条路径」对应。
- 未发现「假绿」型风险：fixture 通过 `build_production_pipeline` 真实装配（`:244-249`）；N1/N2/N6/N7 直接替换 `service._executor._handlers[STEP_OCR]`（`:476-477`、`:520-521`、`:628-629`、`:666-667`），被替换的是 `_typed` 包装后的真实 handler（`src/infrastructure/providers/handlers.py:179-192`），错误码穿越 seam 的路径未被绕过；N2/N6 的「零写」是有依据的（`step_writes.py:117-121` 在写之前因 region_locked / deleted 抛错）。

### 轴 3 — 范围与文档轴：pass，一处记录不一致

- 范围独立核验：以 `G:\CODEX\New Manga`（release 记录声明 main@33826641，`verification/M2-P1/release-33826641.md:7`）为 base 代理比对，base 文件 1070 行、`_backfill_detected_regions` 位于 `921-946`（26 行）；worktree 文件 1083 行、函数 `921-959`（39 行）——**净差正好 +13 行且全部落在该函数内**，函数前后锚点行（915-920 / `_cancel_remaining` 定义）逐行一致，可确认 `src/application/tasks/service.py` 只有该函数被修改。新增测试文件在 main 不存在（glob 无结果）。三条命令结果与集成方实跑一致（`verification/M2-P1/evidence-78e9637f.md:21-27,64,101-104` ↔ `doc/handoffs/M2-P1-78e9637f.md:39-41`）。
- AC4 证据节奏核实：`reproduce.py:419-430` 的 exit 1 是通用 else 分支，单看退出码并非强判别；但证据日志同时给出了「修复后正命题形状」（ocr completed、`target_id=region_id=primary`、`input_refs={'region': ...}`、primary 2 版、planned=terminal=2，`evidence-78e9637f.md:64-92`），且 `[PASS] detect step ran` 排除了「harness 空跑」的假 NOT_REPRODUCED，故 AC4 结论可接受（措辞见 P3）。
- 唯一实质不一致：**审查面向的 delivery head `59acb340…` 在仓库中零记录**。`doc/tasks/M2-P1.md:15`、`doc/handoffs/M2-P1-78e9637f.md:7/51/77`、`evidence-78e9637f.md:8` 全部固定为 `78e9637f`；grep `59acb340` 无任何命中。见 P2 #1。

### 轴 4 — 回归风险轴：pass（full-rebind 路径已闭环，无阻断）

- 走的是**完整重绑**而非半修：handler 的 StepResult 用 `unit.target_id` 作为 `target_id`/`output_target_ids`（`handlers.py:362-369`，其余 region 步骤同构 `:445-449,492-500,539-548,630-634,688-693,751-756,810-817`），故重绑后 `result.target_id == unit.target_id == region`，`commit_step_result` 的 mapping 校验通过（`service.py:635-637`），catalog 落到 **Region 分支**（`src/infrastructure/sqlite/pipeline.py:588-600`）而非 Page 分支（`:601-610`）——诊断报告警告的「半修 ⇒ TARGET_NOT_FOUND」路径已被绕过。Region 快照形状也匹配：`_region_from_id` 产出 `current_revisions={"region": rev}`（`pipeline.py:722`），`_record_step_attempt` 的 `input_refs` 因此带 `region` 键（`service.py:605-606`）。
- 其他消费者：`target_id` 在 `src/` 的全部使用点（service/handlers/store）均以 `unit.target_id` 为写目标或在 `_find_step` 中按 `unit_id` 定位（`service.py:1072-1083`），没有任何代码从 `unit_id` 反解 target，也无 `unit_id.split` 类解析（grep 无命中）；`commit_step` 只消费 `step_run.input_refs/lock_snapshot`（`service.py:642-643`），`unit.expected_revisions/expected_lock` 属审计字段，重绑后保持 Page 形状不影响守卫（见 P3 #2）。
- 持久化往返兼容：`_unit_dict/_unit` 对 `target_id` 是纯字段对称读写（`pipeline.py:176-203`）；注意 `SqlitePipelineStore.get` 命中缓存即返回同一实例（`pipeline.py:497-507`），M2-P1 的 backfill 生效依赖这一身份语义（与 TASK-049 索引循环注释 `service.py:755-759` 同源），非本 Task 引入，但值得记录（P3 #6）。

---

## Findings 分级列表

### P0（阻断）
none

### P1（必须）
none

### P2（建议）

1. **交付 head 记录不一致，集成记录需对齐。** 审查面向的 delivery head=`59acb340…`；但 `doc/tasks/M2-P1.md:15`、`doc/handoffs/M2-P1-78e9637f.md:7,51`、`verification/M2-P1/evidence-78e9637f.md:8` 全部登记 `78e9637f…`，全仓 grep 无 `59acb340`。建议集成方在集成记录中同时写明 `code+test head=78e9637f` 与 `5 路径 tip=59acb340`，并确认 `78e9637f..59acb340` 仅含 `doc/tasks/M2-P1.md`、`doc/handoffs/M2-P1-78e9637f.md`、`verification/M2-P1/evidence-78e9637f.md` 三个文档/证据路径（这 3 个恰好补齐"5 路径"），无 `src/**`、`tests/**` 改动。`M2-P1.md:52` 的允许范围与 `verification/M2-P1/release-33826641.md:18-19` 均支持该判断，但需以 git 事实落盘。

### P3（观察）

1. **`handle_term_extract` 的 `book_id` 查找在 regionless 首跑路径上由命中变为未命中**（`src/infrastructure/providers/handlers.py:723-730`：`target.target_id == unit.target_id` 在 `run.targets` 中匹配）。重绑后 `unit.target_id=region`，而 page-scope run 的 `run.targets` 仍持 Page（`service.py:244-255`），故 `book_id=None`（base 上为 book）。当前**无功能影响**：`handle_term_extract` 的 TM 分支要求 `self._tm_store is not None`（`src/application/translation/knowledge/term_extraction.py:103-107`），而生产装配是 `terms=TermExtractionService()`（无 tm_store，`src/bootstrap/core_assembly.py:765`）；且该错配在「有 Region 的 page-scope 二次运行」路径上本就已存在（base 即如此）。R3 在 `color` 步即止（`handlers.py:652-657`），未覆盖此步。建议留作 fan-out/调度切片的记录项。
2. **重绑后 `expected_revisions`/`expected_lock` 仍为 Page 形状**（`service.py:952-958` 未更新，`pipeline.py:186-187` 原样持久化）。诊断报告已定性其为审计字段、从不参与守卫（守卫只用 `step_run.input_refs/lock_snapshot`，`service.py:642-643`、`pipeline.py:580-583`），故非缺陷；但「target_id 已 Region、expected_* 仍 Page」对后续消费者是潜在陷阱，可在 fan-out 或后续 Task 中清理/断言。
3. **R2 断言为代理级**：`tests/pipeline/test_regionless_rebinding.py:369-377` 用「secondary `region_revisions`==1 + 无 ocr step」代理 AC2 措辞中的「非 primary `NOT_STARTED`」，未直接断言 secondary 的 stage_state。
4. **R3 未固定失败步骤身份**：只有 `error_code == "PROVIDER_NOT_CONFIGURED"` 与「恰好一个 failed step」（`:399-403`），未断言失败发生在 `color`（由 `handlers.py:652-657` 与只注册 OCR provider 推出），措辞上略宽于「下一个真实能力缺口」。
5. **N1 的半修判别只有散文、无断言**：`tests/...:453-460` 说明「半修 ⇒ TARGET_NOT_FOUND 或 target 类型不匹配」，但没有任何用例固定 `commit_step` 以 Page target 提交 region 修订时的 rowcount 0 路径（`pipeline.py:601-610`）。AC3 只要求「注释说明」，故属达标；若要更强判别可加一条反向用例。
6. **无冷启动/跨实例 reload 用例**：`pipeline.py:497-507` 缓存同一实例，R1/N7 读到的 backfill 快照与 loop 内是同一对象；「中途重绑后的 unit 冷读回填」仅由代码对称性保证（`pipeline.py:176-203`），无测试。
7. **docstring 两处措辞精度**：①`service.py:939-942` 沿用 base 的「the first Region (``reading_order`` 1)」，实际 `primary = region_ids[0]` 是 detector 候选顺序（`src/ports/detection/ports.py:99-116` 不排序），仅 fixture 恰好同序；②`service.py:934-937`「在 plan 阶段已经标记终态」易读成所有单元均终态，实际只有 `decision.is_terminal` 者被标记（`service.py:305`）。
8. **AC4 措辞**：`verification/M2-P1/release-33826641.md:20` 称 exit 1 为「强判别」，但 `reproduce.py:424-430` 的 exit 1 是通用否定分支（detect 根本未跑也会走此分支）。本次证据日志已含修复后正命题形状（`evidence-78e9637f.md:64-92`），结论仍成立，建议以后把「强判别」定义为「日志中的正命题形状」而非退出码。

---

## 是否达到可集成标准

**达到。** 修复为单函数最小改动（base↔delivery 该文件净 +13 行全部落在 `_backfill_detected_regions` 内）、走完整重绑路径、测试矩阵对 AC2/AC3 有真实判别力、诊断复现脚本翻绿、范围在允许清单内，无 P0/P1。集成需满足两个条件：**(a)** 按 P2 #1 对齐并落盘 `78e9637f`（code/test）与 `59acb340`（5 路径 tip）的归属，确认其间无 src/tests 改动；**(b)** 按 Task `doc/tasks/M2-P1.md:80` 与 AC5 在集成 head 复跑三条命令（pytest 三文件 / `reproduce.py` 预期 EXIT=1 / `git diff --check`），并把集成 head 写入 `doc/tasks/M2-P1.md` 与集成记录。满足后即可进入 `done`。

---

## 下一步（推荐）

由 Integrator（Codex，当前由 ZCode 会话代行）执行集成 + 集成 head 复跑，并顺带修正 P2 #1 的 head 记录；随后关闭 M2-P1、更新 `doc/STATUS.md` 与 `doc/REBASELINE_PLAN.md`。

可直接转发的指令：

> 请以 Integrator 身份集成 M2-P1：分支 `agent/antigravity/M2-P1-regionless-region-rebinding`，base=`338266417437e3007345aaa8496c5e936745dfd6`，审查对象 tip=`59acb340318359b6c94278c968edcafb125268c1`（code/test head=`78e9637fab8aa456b03f15bc1c632e6966b21a22`）。先确认 `78e9637f..59acb340` 仅含 `doc/tasks/M2-P1.md`、`doc/handoffs/M2-P1-78e9637f.md`、`verification/M2-P1/evidence-78e9637f.md` 三个路径；再在集成 head 复跑 `& "G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe" -m pytest tests/pipeline/test_regionless_rebinding.py tests/providers/test_detect_handler.py tests/providers/test_bootstrap_providers.py -q`（预期 21 passed EXIT=0）、`& $py verification/DIAG-M2-REGIONLESS-LOCK-CHANGED-001/reproduce.py`（预期 NOT_REPRODUCED EXIT=1）、`git diff --check 33826641..<集成head>`（预期 EXIT=0）；把 code head / tip / 集成 head 三者一并写入 `doc/tasks/M2-P1.md` 与集成记录，并将 Task 状态推进为 `done`。注意：Review 侧（DSH）沙箱无 shell，本次四条轴结论均为只读静态审查（含以 main@33826641 为 base 代理的函数级比对），未独立执行任何命令；`git diff --check` 以集成方实跑为准。
