# M2-SFX-EPFAIL-AUDIT-1 非作者独立 Review（DSH r2 定点复审）

复审对象：worktree `G:\CODEX\New Manga.worktrees\M2-SFX-EPFAIL-AUDIT-1-zcode`｜branch `agent/zcode/M2-SFX-EPFAIL-AUDIT-1`｜轴心 commit：`cf013b01`（r1 审查点）→ `6c2825ce` → `2356fb8f` → `22ea8a09` → `9db9a8ad` → `d388a7bf`（**分支 tip**，Git common-dir 分支 reflog 实证，共 5 个返修 commit，与题述一致）。纯静态审查（无 shell/写权限）：逐文件读码+读证据，未执行命令、未写文件。

## 1. 终判

**approved（建议集成，无阻塞条件）。** r1 的 1×P1、1×P2、2×P3、8×P4 **逐条成立闭合**（详见 §2），返修自身无 P0/P1/P2 级新缺陷，仅余 4 条 P4 级备注。AC1 已从 r1 的 PARTIAL 转为 **PASS**：透传落点（`detection_sfx.py:1399-1431`）+ 生产持久化链路（`handlers.py:278-299` → `ports/detection/ports.py:118-127` 的 `options`）连通后，run-time EPFail 键可达生产 detect provenance，§0 的闭合声明不再过度；AC2/AC3/AC4 维持 PASS。

## 2. r1 逐条处置核对本

| r1 项 | 判定 | 证据（一句） |
|---|---|---|
| **P1-1** composite 未透传 run-time 审计键 | **通过** | `src/infrastructure/providers/detection_sfx.py:1399-1431`：tail 追加处按 `if "sfx_ep_runtime_check" in sfx_options` 条件性追加**单键**（值原样），稳态 `runtime_audit=()` → 逐字节不变；注释 `:1399-1409` 明示不透传 `device/sfx_ep/sfx_ep_fallback` 及 typed 降级分支不承载；`tests/providers/test_detection_sfx.py:1651-1707` 断言键值逐字 + `sfx_ep`/`sfx_ep_fallback` 不出现 + primary `device` 原样；红 `raw/tests-epfail-r1fix-red.log:62,67`（`KeyError` at tests:1699，1 failed/1 passed/82 deselected）、绿 `raw/tests-epfail-r1fix-green.log:4-5,10,14`（2 passed；全文件 84 passed；assembly 19 passed）自洽；落点下游 `handlers.py:278-299`+`ports.py:118-127` 使键进入持久化 provenance。 |
| **P1-1 附带**：闭合声明收窄或透传二择 | **通过** | 采透传方案后 `deploy-record.md:9` 的「本 Task 闭合该登记」在生产面成立，无需收窄；同时把「只透传 sfx 专属键、三键仍留在 sfx 面」登记进 `deploy-record.md:110-118`（§2r）、`doc/tasks/…:61`、`doc/handoffs/…:17`，属**显式登记**而非静默省略。 |
| **P2-1** 1% 预算口径差 100× | **通过** | `experiments/M2-SFX-EPFAIL-AUDIT-1/measure_get_providers_cost.py:174-207`：`one_percent_budget_us = page_us*0.01`（11,060）、gate 同用该值、两占比并列 + `unit_note`；`raw/epfail-audit-get-providers-cost.json:60-70` 重跑再生（HEAD=2356fb8f）：`one_percent_budget_us=11060.0`、预算占比 `0.00027486`（=2.7486e-4%）、页占比 `2.75e-06`；`…cost.log:5-8` 同步（cpu 0.0297/dml 0.0304 μs）；四处文案一致：`deploy-record.md:23-25,45`、`doc/tasks/…:46,50,63`、`doc/handoffs/…:17,25`；全仓 grep 无残留旧值（`0.0303/0.0305/1106000 当口径`/`3e-06`/`0.121` 仅出现在「前版误用」说明句中）。 |
| **P3-1** 形态 2 无钉子 | **通过** | `tests/providers/test_detection_sfx.py:1710-1767`：首 run 触发 provider 翻转后 CPU 重跑抛错 → 当页 `pytest.raises`、无 options；同实例第二次 detect → `sfx_ep_runtime_check` 出现且三键语义不变（`device/sfx_ep=dml`、无 fallback）；`src:1175` 的 `session.run` 无宽泛 except（异常原样传播，用例成立）；红 log:4 如实登记该钉子「按构造绿（回归钉非新行为）」。 |
| **P3-2** 红 log「3 passed」叙述 | **通过** | `deploy-record.md:64`、`doc/tasks/…:51`、`doc/handoffs/…:26` 均改为「3 passed = 2 条新辅助用例 + 1 条被 `-k runtime` 选中的既有用例 `test_hash_mismatch_fails_before_any_runtime_import`」。 |
| **P4-1** base 双值 | **通过** | `doc/tasks/…:12` 注记 72807d30=合同释放登记 base / d298ecd0=实际 fork 点（含 merge-base 实证），并以 d298ecd0 为准；`d388a7bf` 补齐右括号（现行内全/半角括号配平，YAML 纯标量无 `": "` 冲突）。 |
| **P4-2** 「属性存在但不可调用」不兜底 | **通过** | `deploy-record.md:33` 明确该形态不兜底及理由（真实 ORT session 不命中）。 |
| **P4-3** 只比对 `providers[0]` | **通过** | `detection_sfx.py:538-542` 加 wheel 升级复核面注释（本 wheel fallback 恒 `["CPUExecutionProvider"]`，wrapper `:541-577`），与 `deploy-record.md:53` 归因依赖对齐。 |
| **P4-4** 键值内嵌因果归因 | **通过（按约定不动）** | r1 已判可接受；返修未改 `:546-552` 值文案，登记仍在 `deploy-record.md:122`（§5.1）。 |
| **P4-5** green log `EXIT_K Runtime=0` | **通过** | `deploy-record.md:67` 以标签排版歧义说明处理，**不重生成**既有证据（符合题述要求）。 |
| **P4-6** 测量口径=单次原语 | **通过** | `deploy-record.md:23,45`、`doc/tasks/…:50`、`json:61 unit_note`、脚本 `:183` 均注明「口径=单次原语 `get_providers()` 调用」。 |
| **P4-7** parity 跨 worktree 依赖 | **通过** | `verify_epfail_audit_parity.py:44-50` 注释说明基准行读自主 checkout 且缺失即判 False（不静默降级）。 |
| **P4-8** 脚本门 vs 人工对表 | **通过** | 同脚本 `:240-245` 明确两层口径：脚本门=同量级（dconf≤1e-05/dxyxy≤0.001）、人工对表=逐数字一致（不做逐数字断言以免浮点假红）。 |
| **回归与兼容** | **通过** | `raw/pytest-full-regression-r1fix.log:3,401-402`：`1 failed, 1828 passed, 1 skipped`＝基线 1823+首轮 3+返修 2，唯一 failed=既有 `test_catalog.py::test_manifest_has_unique_cases_and_exact_taxonomy`；`tests-epfail-r1fix-green.log:12-14`：`tests/core/test_sfx_assembly.py 19 passed` 零破坏；`tests/core/test_sfx_assembly.py` 无 `runtime_check/sfx_ep` 断言 → 透传为纯增量。 |
| **返修新增面自洽** | **通过** | `detection_sfx.py` 行数 1405→1433（+28＝P4-3 注释 5 行 + 透传注释 11 行 + 透传代码 11 行 + `+ runtime_audit` 1 行），与「仅 composite 组装 + 注释」的声称逐项吻合；sfx provider `detect` options 段（`:801-831`）与 `_runtime_ep_audit` 逻辑（`:530-553`）除注释外未动；`runtime_audit` 追加于 summary 键之后、条件为「键存在」→ 稳态与首轮基线逐字节一致。 |

## 3. 新发现分级（P0-P4）

无 P0/P1/P2/P3；以下 4 条均为 P4（备注/可选补强），不构成集成条件。

- **P4-1 新增面：composite 稳态「零追加」无直接断言。** 新用例只覆盖「有键 → 透传」（`tests/providers/test_detection_sfx.py:1696-1707`）；既有 composite 稳态用例用的是无 `get_providers` 面的 `_fake_session`（`:546-559`、`:569-572`），走的是「跳过」分支而非条件为假分支。建议在 `test_composite_appends_sfx_past_primary_reading_order_max` 内补一行 `assert "sfx_ep_runtime_check" not in options`（或用 provider 列表不变的 stub session）钉住 `src:1410-1420` 的 false 路径。
- **P4-2 新增面：AC3 parity 证据未随修复刷新。** `raw/epfail-audit-parity-prek01.json:5` 仍 `source_head=0afb22dd`。论证成立（修复只改 composite options 组装，parity 脚本 `:156-175` 直连 `SfxDetectionProvider`，数值路径零接触），故结论不变；若集成方要「同 HEAD 证据锚」，重跑成本约 15 s（cpu 11.3 s + dml 1.1 s），可顺带补一份。
- **P4-3 记录完备性：交付链 hash 未落全。** `deploy-record.md:139-140` 把 `22ea8a09`/`9db9a8ad` 记作「（verify-fix commit）/（docs-fix commit）」且未列 `d388a7bf`；§2r 插在 §4.2 与 §5 之间（章节序略乱）；`doc/handoffs/…:6,35` 的 `delivery_head=22ea8a09` 与分支 tip `d388a7bf`（docs 后继）并存但已自述「tip 以分支头为准」。建议集成时把三个 hash 补进链表、并统一 review 报告命名取 tip hash。
- **P4-4 既有措辞（非本次返修引入）：「typed 失败路径」用词不精确。** 运行期 EPFail 重试失败的异常是 ORT 的 `RuntimeError` 族，`detection_sfx.py:1318-1328` 的 composite 只捕 `ProviderError`、`handlers.py:278-299` 的 `handle_detect` 无 try/except，最终由 `src/application/tasks/service.py:796-797` 归为通用 `STEP_FAILED`——「不变」成立、但并非 typed provider 错误码。该措辞沿自 Task 合同 `doc/tasks/…:27` 与 GPU-EP-1 登记，建议 Codex 集成收口时改述或确认 pipeline 层映射口径。

## 4. 残留风险与集成建议

**残留风险（均已登记或属既有面，不阻塞）**
1. **INIT 期三键仍不在生产 composite provenance**：本次只透传 run-time 键（`sfx_ep_runtime_check`），`device/sfx_ep/sfx_ep_fallback` 因 `device` 与 primary torch 面同名而按 r1 建议不透传（`src:1403-1405`、`deploy-record.md:114`）——即 GPU-EP-1 的 INIT 回退三键在生产持久化面仍不可见。属 GPU-EP-1 面遗留，建议 Codex 决定是否单列后续切片（如需，最小改法是 sfx 专属前缀键）。
2. **形态 2 的生产落地前提**：首 run 失败后 provider 列表状态是**会话态**，需同一进程/同一装配实例的后续 detect 才能观测（失败单元的剩余 unit 会被取消，`tasks/service.py:817-819`；进程/装配重建则状态丢失）。这批页本身会硬失败（用户可见），丢的是「归因到 EP 回退」这一条。建议在 `deploy-record.md` §5 补一句「无后续成功 detect 时该归因不落盘」的限定。
3. **composite 新增每页一次 `dict(sfx_result.options)`**（`src:1410`，约 μs 量级 ≪ 1% 预算 11,060 μs）——如实登记为可忽略即可。
4. **实机真实 EPFail 仍 NOT_RUN**（`deploy-record.md:125`）：探测面可见性由 wrapper 同 API 重放 + stub 覆盖，口径与 GPU-EP-1 验证矩阵②一致，属诚实登记而非新缺口。
5. **静态审查不可核验项**：本沙箱无法执行 `git diff --name-only`，「禁改面零 diff / 仅允许路径」仍建议集成 Gate 用 git 复核（`deploy-record.md:72` 的声称我仅能以全仓 grep `EPFAIL-AUDIT-1` 命中集合 + 行数增量佐证）。

**集成建议**
- 建议集成（无前置条件）：落地为 `doc/reviews/M2-SFX-EPFAIL-AUDIT-1-d388a7bf-dsh-r2.md`（tip=`d388a7bf`；如需沿用 Handoff 证据锚可写 `22ea8a09`），并在 Task `review_events` 记录 r1 changes_requested + r2 approved 两次事件（当前 `doc/tasks/…:15` 仍为 `[]`，与 GPU-EP-1 同款未用惯例，属集成方收口面）。
- Gate 建议：`git diff --name-only d298ecd0..d388a7bf` 只含 `src/infrastructure/providers/detection_sfx.py`、`tests/providers/test_detection_sfx.py`、`experiments|verification/M2-SFX-EPFAIL-AUDIT-1/**`、`doc/tasks/`、`doc/handoffs/`；复跑 `python -m pytest tests/providers/test_detection_sfx.py -k "runtime or ep_ or composite" -q`（期望 84 passed 级）与全量回归（期望 `1 failed, 1828 passed, 1 skipped`，failed=test_catalog 既有）。
- 可选补强（P4-1/P4-2）可随集成顺笔，不必再开返修轮；P4-4 措辞建议由 Codex 在集成说明中改述或裁决。
- 下一步建议：本 Task 进入 Codex 集成收口（merge + STATUS/任务状态处置）；无需再向 ZCode 派返修指令。
