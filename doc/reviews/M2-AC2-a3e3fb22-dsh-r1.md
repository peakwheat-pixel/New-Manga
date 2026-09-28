---
task_id: M2-AC2
reviewer: DeepSeek Harness (non-author, static review)
decision: changes_requested
reviewed_head: a3e3fb226f42dc071ac79689563be9aaba187121
round: 1
---

## decision: approved_with_conditions

（测试模块本体可集成；但 Handoff 的 AC5 判定与 AC6 记录纪律须先修正，见 Conditions）

---

## 一、范围与纪律轴

delta 确为纯新增验收资产：唯一代码文件 `tests/m2_acceptance/test_data_integrity.py` 只 import 产品模块（test_data_integrity.py:34-46），Task 允许清单与交付路径完全对齐（doc/tasks/M2-AC2.md:40-43、doc/tasks/M2-AC2.md:47）；零 `src/**` 改动与集成方 git 结论一致。为防止"为绿弱化"，我逐行核查 492 行测试：全文无 `skip`/`xfail`/`importorskip`/`pytest.mark`、无被吞的异常、无弱化的 `approx`，所有关键断言是硬断言（test_data_integrity.py:114、288、322、350-352、434）。"验收失败即合法交付"的纪律被遵守：AC4 region 锁与 AC5 断言的写法都是"OCR/重装配真的发生才会绿"（test_data_integrity.py:288、350），反证不存在把失败场景绕开的痕迹。唯一纪律瑕疵在证据侧而非测试逻辑（见 P1/P3）。

## 二、断言判别力轴

**AC1** 三重断言并不存在：测试只有字节（:147）、size（:150）、目录顶层名单（:149）三行，**没有 mtime 断言**（Task AC1 明确要求"字节与 mtime 不变"，doc/tasks/M2-AC2.md:33）；更关键的是导入走内存 `data_provider`（test_data_integrity.py:103-113），`source_path` 只被测试自己 `write_bytes` 后从未被 Core 打开，因此"字节不变/目录清单"在结构上恒真，无法判别 Core 是否有保护行为。另 `sha256_bytes` 与被测实现是同一函数（test_data_integrity.py:45 vs src/application/importing/images/service.py:35,78），属自证而非独立 oracle。

**AC2** managed 缺失检测可检出但断言偏松：生产上 `missing` = 页不存在或 ref 为空（src/bootstrap/core_assembly.py:187-198），`invalid` = 引用逃逸 managed root（:203-204）或文件在盘上消失（:205）；测试删文件命中的是第二个 `invalid` 分支，却只断言 `!= "ok"`（test_data_integrity.py:220），无法钉死"被正确判为 invalid"与"被降级为 missing"、也无从区分"越权引用"这一安全语义。测试仅覆盖 `image_state` 读面，未覆盖 provider 读面的 typed 错误（src/bootstrap/core_assembly.py:251-254），而 Task AC2 写的是"typed 错误**或**明确缺失状态"，故只覆盖了一支。

**AC3** mock provider 真跑，判别力足够：绑定写入在 create_run 之前（test_data_integrity.py:256），输入是真实可解码 PNG（:253-255，`synthetic_page_png` 为真 PNG，src/bootstrap/acceptance_bridge.py:126-143），且 mock OCR 返回非空固定文本（src/infrastructure/providers/mock_local.py:38,90-100）。因此若 OCR 未跑，`:288`（revisions 必须 +1）、`:291`（ocr_text 必须变化）、`:292`（current 必须前移）三条会同时红——**不会假绿**；人工译文保留断言的判别力成立（:280、293-297）。

**AC4** region 锁的 `LOCK_CHANGED` 确来自写守卫而非前置失败：测试按 plan 后、execute 前翻锁（test_data_integrity.py:343-346），OCR handler 先跑 provider 再进写路径（src/infrastructure/providers/handlers.py:314-350），写守卫在 `apply_ocr`/`_persist` 之前因 `staged.region_locked` 抛 `LockBlocked`（src/infrastructure/providers/step_writes.py:117-122），经 `_typed` 保留 code（src/infrastructure/providers/handlers.py:204-215）→ `StepRun.error_code = "LOCK_CHANGED"`（src/application/tasks/service.py:660-664）；若是前置失败则 planner 直接跳过、无 StepRun，`:350` 会红。零写断言（revisions 数不变，:351-352）成立。但 restore 溯源只断言真值非空（:434-436），未断言 `restored_from_revision_id == source.region_revision_id`，也未直接断言 `current_revision_id` 指向 v4；pinned 场景只断言 DB 行 `is_pinned`（:391-395），未断言 artifact 文件在 `CleanupService.run()` 前后存在（Task AC4 的原文要求），且假 inventory 只含 cache 文件（:373-380），没走"业务路径被拒"分支（src/application/maintenance/cleanup.py:214-243）。

**AC5** 重装配后的 hash/Lock/pin/current/人工文本断言完整（test_data_integrity.py:467-483），但 Task AC5 的"既有 `recover_running_runs` 语义可从装配层触达"**没有任何断言**：测试只借重装配间接执行了 src/bootstrap/core_assembly.py:804 的调用，既未造遗留 RUNNING run，也未断言其被 reap 成 INTERRUPTED（语义定义在 src/application/tasks/service.py:886-901）。这属于"被调用"级覆盖，非语义覆盖。

## 三、语义澄清轴

双层锁语义与代码完全一致：`RegionText.translation_locked`（src/domain/regions/entities.py:139）与 Region 顶层 `region_locked`/`translation_locked`（src/domain/regions/entities.py:231-232）确为两组字段（DB 列 vs `text_json` 内），`save_manual_translation` 只置 text 层三件套（src/domain/regions/entities.py:172-178）并产生新 revision（src/application/editing/service.py:521-529）。Task AC3 的修正措辞忠实于代码事实：OCR 链只读顶层 `region_locked`、不读 text 锁（src/infrastructure/providers/step_writes.py:118），故 OCR 照写 `ocr_text` 并推进 current；翻译链读三锁并拦为候选（src/infrastructure/providers/step_writes.py:158-165 → src/application/tasks/service.py:660-682），与"StepResultCandidate 机制属于翻译链"一致（doc/tasks/M2-AC2.md:35、doc/handoffs/M2-AC2-owner-delivery.md:36）。唯一措辞精度问题见 P3-4：service 层在调用 entities 之前就已拦截（src/application/editing/service.py:491-496），生产路径不会看到 `PermissionError`。

## 四、登记项轴

登记项属实且影响面判断正确：src/bootstrap/core_service.py:51-54 的 stub 传 `format="rgb"`，而 `DecodedImage` 只有 `width/height/mime_type`（src/application/importing/images/ports.py:11-17），任何经该 stub 的导入必然 `TypeError`；sidecar 命令面仅 `core.ping`/`ListBooks`/`core.shutdown`（src/bootstrap/core_service.py:257-325），确不含 import，故 M2-IPC1 未受影响——Handoff "未来 core_service 扩 ImportPages 命令前必须替换"的结论成立。补充一点 Handoff 未写全的影响面：`assemble_production_core` 是这条 stub 的唯一装配入口（src/bootstrap/core_service.py:81），因此 M2-AC2 自备 decoder 绕开它（test_data_integrity.py:48-53、84-93）是必要的，且该 stub 目前无任何测试覆盖。

---

## Findings

- **P0**：none
- **P1-1（证据纪律 / AC 判定表不符）**：AC5 的 `recover_running_runs` 子承诺无任何语义断言，Handoff 的 AC 表仍判 AC5 **PASS** 且 "NOT_RUN/BLOCKED：无"（doc/handoffs/M2-AC2-owner-delivery.md:25、:42-44），与 Task AC6 的"FAIL/BLOCKED/NOT_RUN 分开报告"（doc/tasks/M2-AC2.md:38）相悖。风险：集成方会把"重装配不崩"当作"recover 语义已验收"。
- **P2-1（AC1 判别力）**：Task AC1 的"字节 + mtime + 目录清单"三重断言实际缺失 mtime，且字节/清单两项在 `data_provider` 架构下结构上恒真；`sha256` 断言与实现共用 helper，非独立 oracle（test_data_integrity.py:45,103-113,146-150）。
- **P2-2（AC2 判别力）**：用 `!= "ok"` 代替 `== "invalid"`，未钉死 `missing`/`invalid` 语义边界与"越权引用 vs 文件消失"的区分；未覆盖 provider 读面的 typed 错误支（test_data_integrity.py:215-222）。
- **P2-3（AC4 restore 溯源）**：只断言 `restored_from_revision_id` 非空，未断言等于源 revision id，也未直接断言 `current_revision_id` 指向新 v4（test_data_integrity.py:429-436）。
- **P2-4（AC4 pinned artifact）**：未验证 pinned revision 关联的 artifact 文件在 `CleanupService.run()` 前后仍存在；假 inventory 只给 cache 文件，未走业务路径被拒分支（test_data_integrity.py:371-395）。
- **P3-1（AC6 记录）**：verification-results.md 无显式 EXIT 行、无 `git diff --check` 段，HEAD 记为 `01af7732` 而非 delivery head `a3e3fb22`（verification/M2-AC2/verification-results.md:3,26,30）；Handoff 文字与集成方实跑补足了事实，但原始日志本身不满足"记录 EXIT/固定 HEAD"。
- **P3-2（措辞）**：测试 docstring 声称走 `assemble_production_core`，实际调 `assemble_core_services` 并自备 adapters（test_data_integrity.py:4-5 vs :84-93；NOTE 已解释绕开 stub，但两处措辞并存）。
- **P3-3（脆弱断言）**：`len(revisions) == 4` 与硬编码 `revision_no == 4`/`1` 依赖 `create_region` 恰好占 v1（test_data_integrity.py:430-433、456）。
- **P3-4（措辞精度）**：Handoff 语义发现 1 称 `apply_machine_translation` 的 `PermissionError` 触发保护；entities 层确实如此（src/domain/regions/entities.py:167-168），但 service 层提前拦截并返回 `LOCK_CHANGED`（src/application/editing/service.py:491-496），生产路径不会抛 `PermissionError`。
- **P3-5（可移植性）**：本模块未像 M2-AC1 那样对 PySide6 缺失做显式 skip 声明，环境缺 Qt 时表现为 error（不假绿，仅可用性差异）。

---

## 是否达到可集成标准

**测试模块本体达到可集成标准**：纯新增、10 passed 且全套 14 passed 零回归、零 `src/**` 改动、断言整体不可被"绕过 OCR/写守卫/重装配"骗绿，集成不会破坏现有行为。

**但"以 Handoff 现有 AC 判定表作为集成依据"未达到标准**：AC5 被判 PASS 而其实只做了"装配可达"级覆盖（P1-1），AC6 的 EXIT/HEAD 记录也在原始日志中缺失（P3-1）。因此给 **approved_with_conditions**。

**Conditions（集成前须满足，任一方式）**：
1. Owner 修订 Handoff 与 Task AC5 表述，把 `recover_running_runs` 明确标注为"仅装配路径可达、无语义断言"（或登记 NOT_RUN）；或在同一允许范围内补一条 run 级断言（造 RUNNING run → 重装配 → 断言 INTERRUPTED）。
2. 建议同批顺手提升 AC1/AC2/AC4 判别力：补 mtime 快照断言、用 `hashlib.sha256` 独立计算、把 `!= "ok"` 收紧为 `== "invalid"`、断言 `restored_from_revision_id` 等于源 id。这些均为测试文件内改动，不触碰产品代码。
3. verification 日志补记 `git diff --check <base>..<delivery-head>` 原始输出与各命令 EXIT，并写明 delivery head。

## 推荐下一步

把上述 Conditions 1（必须）与 2/3（建议）作为最小返工交回 Owner ZCode（保持作者归属、单 commit、仍在允许清单内），返工后由 Codex（新 ZCode 会话）执行集成；不建议 Codex 以"仅补文档"方式单方面改写 AC 判定表。

可直接转发的指令：
> 你是 ZCode（M2-AC2 Owner）。分支 `agent/zcode/M2-AC2-data-integrity`，worktree `G:/CODEX/New Manga.worktrees/M2-AC2-zcode`。DSH Reviewer 结论为 approved_with_conditions，请按 review 的 P1-1 与 P2/P3 项做一次最小返工（单 commit，仍限 `tests/m2_acceptance/test_data_integrity.py`、`doc/tasks/M2-AC2.md`、`doc/handoffs/M2-AC2-*.md`、`verification/M2-AC2/**`）：① 补 `recover_running_runs` 语义断言或把该子项显式标为未覆盖（二者择一，并同步 Handoff AC 表与 NOT_RUN 段）；② 补 AC1 mtime/独立 sha256 断言、AC2 `== "invalid"`、AC4 `restored_from_revision_id` 等值断言与 pinned artifact 文件断言；③ verification 日志补 EXIT 与 `git diff --check` 原始输出并记录 delivery head。完成后重跑 `pytest tests/m2_acceptance/test_data_integrity.py -q` 与 `pytest tests/m2_acceptance -q`，更新 Handoff 与 delivery head，交 Codex 集成。
