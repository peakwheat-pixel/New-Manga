# M2-RC4-DOMAIN-COMMANDS 非作者独立 Review（静态只读）

```yaml
---
task_id: M2-RC4-DOMAIN-COMMANDS
reviewer: DeepSeek Harness（非作者，静态只读；审查基线 base=5954bb4be75fe0486b2d11b9cece56ae6f47f046）
author: Codex Executor（Core/Rust 37110749 + 58b3706d；React a27b3443 → 6f3544a2）
base_commit: 0fba60796c83a3039a260c5790353976bc891dd7
reviewed_head: 5954bb4be75fe0486b2d11b9cece56ae6f47f046
decision: approved_with_conditions
---
```

审读对象：`G:/CODEX/New Manga.worktrees/RC4-integration`（组合树）。依据：`doc/tasks/M2-RC4-DOMAIN-COMMANDS.md`、`doc/contracts/M2-RC4_DOMAIN_COMMANDS.md`、`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` rev 1.6（§5/§8/§10.1/§10.2）、`doc/09_COLLABORATION.md` §6，以及两份 Handoff、React 初版 Review、预检处置表、集成方 raw 日志。

**方法限制（随结论携带）**：本会话沙箱 **pwsh 不可用**（`pwsh -Command` 两次均以 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)` 失败，命令未执行：`echo hello` 亦同）。因此**未运行任何命令**——没有 `git diff/log/status`，没有 pytest/npm/cargo，**没有修改任何文件**。所有动态数字均为引用集成方 raw 日志（逐条给出文件:行），不是本次运行结果。

---

## §Findings

| ID | 级别 | 文件:行 | 触发与影响 | 证据与建议 | 状态 |
|---|---|---|---|---|---|
| RC4-01 | **P2** | `src/application/editing/service.py:434-462,734-784`；`src/bootstrap/core_service.py:798-846`；`tests/**` | `list_region_revisions` / `restore_region_revision` 的**成功路径、DTO 形状、`expected_revision` 过期冲突与事务内竞态**在 Python 侧**没有任何测试**。冻结契约验证 Gate（`doc/contracts/M2-RC4_DOMAIN_COMMANDS.md:24`）明文要求"真实 SQLite restore（历史/pin/人工文字/Lock、**过期与事务中竞态**）"。新的前置守卫 `service.py:750-751`（`current.revision_no != expected_revision_no → RegionRevisionChanged`）一旦写错，整个 Gate 会静默通过。 | 正证：`tests` 内 grep `restore_region_revision` / `list_region_revisions` / `list_revision_summaries` **零命中**；既有覆盖走 legacy 签名（`tests/editing/test_sqlite_regions.py:191-207`、`tests/editing/test_text_protection.py:150-190`、`tests/m2_acceptance/test_data_integrity.py:446-482`），`expected_revision_no=` 仅出现在 retype 用例（`tests/editing/test_region_retype.py:166`）；Rust `main.rs:1660-1692` 的真实 sidecar 只断言三条命令的 `TARGET_NOT_FOUND`。建议：补 wire 级用例（DTO/正整数校验/`TARGET_NOT_FOUND`/`INPUT_REVISION_CHANGED` 零写/restored revision 与历史摘要）；或由 Codex 显式登记该项为偏差。按 §6(12)③，本项当前记 **NOT_RUN**，不得记为通过。 | **open（有条件）** |
| RC4-02 | P3 | `src/application/rendering/service.py:227-267`；`verification/M2-RC4-DOMAIN-COMMANDS/raw/core-stdio-preview-attempt-2.log:3,35,39-44,96-98,162-176`；`tests/core/test_rc4_stdio_render_preview.py:227-239` | attempt-2 在 `37110749` 上：speech 区域 `status=="rendered"`（log:96）但 `crop((20,20,150,120))` 与纯色 `(240,64,32,255)` **逐像素完全相同**（log:162-176 失败）。最终在 `58b3706d` 上同一坐标/同一 fixture 的等价断言通过。仅把比较改为 `.convert("RGB")`**在逻辑上无法翻转该结果**（RGBA 全等 ⇒ RGB 全等）。 | 结论：`37110749→58b3706d` 之间存在**未被 Handoff 描述的行为/源码变化**（`doc/handoffs/...-core-58b3706d.md:29-30` 只列"managed 读取 typed 化 + 非法 skip_reason fail-closed"）。建议集成方补 `git diff 37110749..58b3706d -- src/` 口径：若有未描述 src 修复，则 Handoff 该轮描述不完整；若无，则该像素断言的判别力存疑（§6(12)②）。 | **open** |
| RC4-03 | P3 | `verification/.../combined-focused-final.log:3`、`combined-full-final.log:3`、`combined-cargo-final.log:2`、`combined-diffcheck-final.log:2`、`combined-react-fix-verify.log:3`、`baseline-skip-probe.log:3`、`combined-sidecar-build-1.log:1` | 全部"最终"Gate 日志绑定于 `78e4f24d` / `a1bd8acb` / `2f741407` / `a4e35e82`，**没有一份绑定 reviewed_head `5954bb4b`**。依 §6（"测试结果只能适用于记录的 commit"，`doc/09_COLLABORATION.md:174`）与 §6(12)①，现有证据不能直接声明覆盖被审 head。 | 建议：由集成方在同一处写明 `78e4f24d/a1bd8acb → 5954bb4b` 的 diff 事实（仅 docs/evidence 追加），或在 `5954bb4b` 复跑 Gate。本报告**不**把任何日志当作 `5954bb4b` 的验证。 | **open** |
| RC4-04 | P3 | `verification/.../integration/baseline-full-300b4007.log:50` vs `combined-full-final.log:407`；`doc/handoffs/...-core-58b3706d.md:39` | 同一证据集内两次全量 pytest 的 skip 口径不同：基线 **7 skipped**（1841 passed）vs RC-4 全量 **1 skipped**（1852 passed），差值 −6 **无任何解释**；两次日志均未用 `-rs`，剩余那 1 条 skip **无测试名**。skip 条件确为环境依赖（`tests/providers/test_detection_doctfy_real.py:15-22`、`tests/providers/test_detection_sfx.py:87-96` 依赖 task-envs 权重/帧）。 | 违反 §6(12)③（skip 逐条列来源与原因）与 ④（口径不同数字必须同处写明总数并解释差值）。建议在 Gate 说明中补 7 vs 1 的来源与那 1 条 skip 的名称。 | **open** |
| RC4-05 | P3 | `apps/desktop/src-tauri/gen/schemas/{capabilities,acl-manifests,windows-schema,desktop-schema}.json` | 三命令权限条目（`grep allow-rerender-page` 命中 4 个文件）已入库，但 Task `allowed_paths`（`doc/tasks/M2-RC4-DOMAIN-COMMANDS.md:39`）只授权 `capabilities/**`、`permissions/**`；`gen/` 未被任何 `.gitignore` 忽略（根/`apps/desktop` 均无 `gen` 规则）⇒ 属 tracked 生成物的越界改动。Handoff 已如实登记（`:44`），非隐瞒。 | 非作者 Reviewer 不能批准范围；建议 Codex 追认（与 REGION-RETYPE review P3-2 同类先例），或把 `gen/schemas/**` 写入 allowed_paths。 | **open（待追认）** |
| RC4-06 | P3 | `apps/desktop/src-tauri/src/main.rs:347-356`；`src/core_bridge.rs:433-443` | 契约约束 3 明文要求的"撤销失败 → fail-closed 新 preview、`preview=null`、`PREVIEW_UNAVAILABLE`、保留旧 key 重试"分支**没有任何可判别证据**：`MockCoreChannel::revoke_resource` 恒 `Ok`，无法注入失败，全仓无该分支断言（`PREVIEW_UNAVAILABLE` 仅出现在 `main.rs:353/367` 源码）。主路径（revoke-previous-first、跨页串行）有测试（`main.rs:1786-1850`，cargo 日志 `combined-cargo-final.log:299`）。 | 按 §6(12)②，判别力证据缺失即记 **NOT_RUN**。建议给 mock 增加可注入失败并补单测。 | **open** |
| RC4-07 | P3 | `apps/desktop/frontend/src/workbench/WorkbenchPage.tsx:315-318,588-599` | R-1 主体已闭合，但**卸载窗口残留**：卸载 cleanup 不递增 `imageRequestRef`/`operationRef`，rerender 预览闭包（`:588` 取号、`:595` 判 current）在组件卸载后仍判 current 并执行 `replaceImageUrl(url)`（`:599`），而该 URL 的 revoke 只依赖卸载时已跑过的 cleanup ⇒ object URL 永久泄漏。手工读路径有 `cancelled` 保护（`:277,305-307`），不受影响。 | 影响限于内存保留（blob 随文档存活），**不跨页污染、不改写当前状态**，低于原 R-1 严重度。建议卸载时 `imageRequestRef.current += 1` 或加 mounted 标志。 | **open（非阻塞）** |
| RC4-08 | P3 | `src/application/rendering/service.py:154-165,227-267`；`src/infrastructure/rendering/pillow_rendering.py:186-206` | 同一物理条件"必要输入不可用"出现两种 wire 码：NMFR clean 解码失败（`service.py:162-165`）→ `MISSING_REQUIRED_INPUT`；PNG 损坏/解码失败或原图与 clean 尺寸不一致（`pillow_rendering.py:189-206` → `service.py:261-267`）→ `ARTIFACT_WRITE_FAILED`。契约第 11 行把"缺 clean/必要原图、字体或布局不可用"归 `MISSING_REQUIRED_INPUT`，第 17 行要求"原图缺失/损坏 fail-closed"（未指定码）。两者均 fail-closed、零写，无安全影响。 | 建议统一为 `MISSING_REQUIRED_INPUT`，或在契约登记映射表。 | **open（非阻塞）** |
| RC4-09 | P4 | `apps/desktop/frontend/src/workbench/ViewerPanel.tsx:17-20`（"Core has no restore/rerender runtime command yet (PROTOCOL_MINOR=3)…render disabled"）、`:6-9`；`tests/core/test_core_detect.py:604`（名 `..._minor_3` 断言 4）、`tests/core/test_core_service_retype.py:132`（名 `...to_three...`）；`main.rs:893-894`（"ten live commands"）、`build.rs:37-39`（"five production commands"）；`main.rs:1338-1344` ignored 用例被 Handoff 描述为"既有 GATE 场景"（实为 digest 性能探针） | 陈旧注释/命名与现状矛盾，误导后续读者；无功能影响。相应文件均在 allowed_paths 内，属可顺手修正项。 | **open（nit）** |
| RC4-10 | P4 | `src/bootstrap/core_service.py:863-866,867-872` | `MISSING_REQUIRED_INPUT` 的 envelope `category="not_found"`；C1 §8 分类语义上更接近 `unavailable`。契约未冻结 category，UI 按 `code`/`category` 分支且已按 code 消费，故仅为口径建议。 | 建议下一轮契约澄清类别映射。 | **open（nit）** |
| RC4-11 | P4 | `main.rs:347-365` | `rotate_render_preview` 无 `previous == next` 守卫：若 Core 复用同一 catalog key，会"先撤旧、再登记同一 key"，使预览静默失效。Core 现为 `preview-<uuid4>` 每次新键（`render_preview.py:27`），属防御性缺失。 | 建议加等值短路。 | **open（nit）** |
| RC4-12 | P4 | `src/infrastructure/resource_channel/render_preview.py:27-39` | 每次 rerender 生成一个新 PNG 并 `catalog.upsert` 一行；轮换/撤消失败后**旧文件与旧 catalog 行不回收**，长期增长（契约未要求 GC）；另 `publish` 不校验源路径（调用方传 managed_path），只读源不写源。 | 建议登记 derived 预览 GC 为后续任务。 | **open（nit）** |
| RC4-13 | P4 | `apps/desktop/frontend/src/workbench/WorkbenchPage.test.tsx:698-721`（`:706`） | R-2 的冻结码用例中 fake 返回的 `preview_error` 与 UI 硬编码字面量相同，故 `:715` 无法区分"UI 硬编码"与"回显 Core"，初版 R-2 的判别用例（返回其他字符串）未保留。UI 侧硬编码 `PREVIEW_UNAVAILABLE`（`WorkbenchPage.tsx:576-578`）方向上是更安全的，属判别力弱化而非正确性缺陷。 | 建议补一条 Core 返回非冻结值的用例，断言 UI 仍显示冻结码。 | **open（nit）** |

---

## §审查重点逐条裁决（对 8 项）

**1. Core 三命令 DTO / 语义 / 枚举 / 错误短语 —— PASS。**
- DTO 逐字段吻合：`list` → `{region_id,current_revision_no,revisions[]}`，`RevisionSummary` 恰为契约 10 字段、无快照/路径/bytes（`editing/service.py:444-461`），`ORDER BY revision_no` 升序（`infrastructure/sqlite/regions.py:171`）；`restore` → `{region_id,revision_no,region_type,sfx_policy}`（`core_service.py:841-846`）；`rerender` → `{page_id,artifact_id,revision_no,reports[{region_id,status,skip_reason,font_substituted}],preview,preview_error}`（`core_service.py:892-907`），与契约第 9/10/11 行逐字对应。
- 语义：未知/软删除 region → `RegionNotFound`（`editing/service.py:189-193`）→ `TARGET_NOT_FOUND`（`core_service.py:1243-1258`）；页不存在在 handler 校验（`core_service.py:854-855`）→ `TARGET_NOT_FOUND`；缺失输入 → `MISSING_REQUIRED_INPUT`（`service.py:156-165,203-217,242-250`）且**页级冲突统一 `INPUT_REVISION_CHANGED`**（`core_service.py:859-860` 把 `COMPOSITION_BASE_CHANGED` 归一）、**其他写失败（DB/hash/TARGET_NOT_FOUND）统一 `ARTIFACT_WRITE_FAILED`**（`:861-862`），闭掉了预检 P2-4。
- `reports.status` 仅 `rendered/skipped`，`skip_reason` 在汇出前被白名单化（`service.py:201-206` 把 `style_resolution_failed: …` 等内部原因转为整页 blocked，不进 reports），契约第 11 行满足。
- 错误短语安全：`RegionConflictError("region revision changed since it was read")`（`core_service.py:838-840`）、`RegionLookupError` → 固定 `"region not found"/"page not found"`、`E_UNKNOWN` → 固定 `"page rerender failed"`；`outcome.detail`（可能含绝对路径）**仅进 stderr**（`:873-876`），`preview` 异常同样仅 stderr（`:889-890`）。✓
- 仅两个口径项：RC4-08、RC4-10。

**2. restore 语义 —— 代码 PASS / 证据 FAIL(NOT_RUN)。**
新建 `origin=RESTORED`、`review_state=NEEDS_REVIEW`、`restored_from_revision_id=source.region_revision_id` 的 revision（`editing/service.py:757-765`）；指针指向**新** revision（`sqlite/regions.py:267-274`，`service.py:783-784`），不移动回旧 revision、不 upsert 既有 revision（`_insert_revision` 只 INSERT）、不触碰 pin（`set_revision_pinned` 独立语句，restore 路径未调用）。事务内比较：`expected_current_revision_id=current.region_revision_id`（`service.py:766-769`）在 `BEGIN IMMEDIATE` 内比较并 **rollback 后返回**（`sqlite/regions.py:215-240`）⇒ 冲突零写；`LOCK_CHANGED` 同样零写（`:242-253`）且被映射为 `INPUT_REVISION_CHANGED`（`service.py:776-780` → `core_service.py:837-840`），与契约第 10 行单一冲突码一致。快照锁回退成立：`restore_from_snapshot` 恢复 region 级 3 锁 + `text.translation_locked`（`domain/regions/entities.py:285-287,303,307-309`），而 `lock_snapshot` 用**提交时观测到的当前锁**作乐观守卫（`service.py:770-774`），语义正确（回退 + 并发不可静默覆盖）。legacy `restore_revision` 仍始终传入观测到的 current ID（`:731,769`），契约"应用约束 1"满足。**但**过期/竞态与 wire 面证据缺失 → RC4-01。

**3. rerender fail-closed / skip 像素恢复 / 无 AI / 无新锁门 —— PASS。**
clean 缺失（`service.py:154-160`）、clean 不可读（`:162-165`）、必要原图缺失/不可读（`:227-250`）、字体/布局不可用（`:201-217`）全部 fail-closed 且不提交；skip/manual SFX 通过既有 `compose_region(clean, original, bbox, _empty_render_op)` 从原图恢复像素后再 `compose_page` 绘制剩余译文（`:251-260`，`ports/rendering/ports.py:108-118` 语义吻合），并**优先 ORIGINAL Artifact、缺失时用可选 `original_page_reader`**（`:228-238`），`core_assembly.py:756/1006` 仅透传、默认 `None` 保持旧调用行为（`core_service.py:308-338` 的 reader 从 `Page.managed_original_ref` 读并校验在 managed root 内，越界抛错 → fail-closed）。渲染路径**无任何 AI port 引用**（无 Detect/OCR/Translate/Inpaint），不创建 PipelineRun（provenance 仅 `step: render`/`ai_invoked: false`）；页级路径**不新增单区域锁门**（`_active_regions` 不过滤 `region_locked`，只有单区域 `rerender_region` 有 `LOCK_CHANGED`），锁定区域当前 final 正常参与渲染。契约第 11 行与预检处置 P2-3/P3-8 均满足。

**4. Pillow 适配器 + preview 发布 —— PASS（附 RC4-06/RC4-12）。**
`pillow_rendering.py` 为真实实现：字体表扫描 `:56-96`（缺失走 `_FALLBACK_CHAIN` 且 `available=False` → `service.py:521` `font_substituted`）、横排换行 `:131-157`、竖排分列 `:159-172`、fit 判定 `:122-129`、描边/对齐/基线 `:214-238`；仅 import PIL/os/re/io（无 Qt、无新第三方，`requirements.txt:42-44` 的 PIL 说明在预检时已存在、非本任务改动）；`decode_nmfr_frame:241-257` 校验容器/dims/字节数并对非法帧抛错。preview：`resource_id = preview-<uuid4>`（`:27`）随机、不编码业务 ID/路径/revision，catalog key 只作 `issue_resource_url` 入参，WebView 可见 URL 由 host 的 opaque grant 构造（`apps/desktop/src-tauri/src/resource_protocol.rs` 侧，由 Rust 分面确认）；发布只写 derived 只读根（`:20-25` 双重 containment 校验）、临时文件 + fsync + `os.replace`、登记 `derived-read-only`，返回仅 `{resource_id, revision}`（无绝对路径/base64）；`PREVIEW_UNAVAILABLE` 唯一产生点 `core_service.py:879-890`（原异常仅 stderr），Rust 再次白名单化（`main.rs:352-353,366-368`）。revoke-previous-first 的轮换在宿主侧实现正确（见第 5 条），其失败分支缺证据 → RC4-06。

**5. Rust 面：仅生产注册 / 零扩权 / 锁与轮换 —— PASS（附 RC4-05/RC4-11）。**
`PRODUCTION_COMMANDS` 12 项含三新命令（`main.rs:53-70`）；`command_allowlist` 在 `probe||ac1` 下剔除 IPC1/SETTINGS/RETYPE/RC4 四族（`:119-141`），字面注册三分支分别为 probe 7 / ac1 6 / production 12（`:757-765/771-778/784-797`），**probe/AC1 列表不含三命令**；测试把生产面钉为 12（`:938-960`）、7/6 由包含式与计数式双重约束（`:963-993/998-1028`），**未发现既有 pin 被"迁就实现"改写**。ACL：`capabilities/m2rc1-commands.json:6-26` 19 条与 `build.rs:55-89` 声明一致（含三命令），无 `plugin:` 面、无多余授权。`render_preview_resources` 互斥锁在**调用 Core 之前**取得并持至轮换完成（`:320-331`），`rotate_render_preview` 严格 revoke-previous-first（`:347-356`）、成功后才登记 next（`:358-365`）、撤销失败时回撤新 grant + `preview=null` + `PREVIEW_UNAVAILABLE` 并提前返回（`current` 未改写 ⇒ 旧 key 与已提交 artifact 均保留），契约约束 3 与 C1 T6 口径满足；错误只回 `error.code`（`:287/302/329`），锁中毒回固定 `CORE_UNAVAILABLE`，不向 WebView 下发路径，derived/catalog 只传给生产子进程且旧三参 `spawn` 保留（`library_bridge.rs:181-187`）。

**6. React 返修（6f3544a2）复核 —— R-1 主体闭合（残 RC4-07）、R-2 闭合（残 RC4-13）、R-3 闭合（残 RC4-09）。**
统一版本号 + page epoch 绑定成立：递增均在 `await` **之前**（`WorkbenchPage.tsx:264` 手工读、`:362` 切页、`:564` rerender 起始、`:588` 预览读），判定同时绑定 `requestId/pageId/pageEpoch`（`:267-270`），切页在同步 handler 内作废并清图（`:337-366`），迟到响应**只 revoke 自己创建的 URL**且不改写图片/错误（`:283-286`、`:595-597`），`rerender` 期间被更新的手工读会抢先生效并保留其选择（`:568-575`）；对应的两条真实 JSDOM 交错用例存在（`WorkbenchPage.test.tsx:596-634`、`:636-675`），且 Handoff 附红色探针 artefact（`raw/react-review-regression-red.log`）。R-2：非零 PNG fixture（`test.tsx:45-54`）→ 真实 chunk 读取断言（`:529-532` 校验 chunk URL/Blob size/字节相等），typed fetch failure（`:677-696` `REF_EXPIRED`）与 `PREVIEW_UNAVAILABLE` 不伪报渲染失败（`:698-721`；`WorkbenchPage.tsx:576-584`）。R-3：`RegionInspector.tsx:126` 已改为"10 秒内/当前页/无新操作 + 历史可读 + 恢复需确认"，恢复确认框明示"文字、类型、策略与锁状态（可能回退当前锁）"（`:287`）。三入口解禁且保留资格禁用（`ViewerPanel.tsx:242-266`，`canRerender` = pageId 非空）。undo 契约满足：保存改标前 revision_no + 改标结果 expected_revision + 原 suspect（`:447-454`），窗口内调用 `restore_region_revision`（`:484-488`）且**不调用 `set_region_type`**，失败不自动重试不乐观改状态（`:508-514`）。无 React 直连 DB/OS/模型，预览只传 `resource_id`+`revision`。

**7. 测试更新合法性（防"测试迁就实现"）—— 处置成立。**
- minor 3→4 有五处 pin 更新（`tests/core/test_core_detect.py:613`、`test_core_service.py:152,237`、`test_core_service_retype.py:136,139`、`test_core_service_settings.py:76,79`），冻结依据充分：C1 rev 1.6 首行与第 9 行"协议 minor 3→4"、第 131 行"协议 minor 4"、RC-4 契约第 3 行"envelope minor 3→4（新增命令）"、Task 第 28 行。原失败证据显示这些测试 pin 的是 rev1.5 时代的**当前实现值**（`reviewer-core-37110749-existing-tests.log:56-57,158-159,222-223`，测试自身语义即"tracks the current command surface"）⇒ 契约驱动的正当更新，非迁就实现。
- 两个 skip-SFX 场景（`tests/rendering/test_rerender.py:256-278`、`:582-618`）：原失败为 `assert 'blocked' is 'committed'`（`existing-tests.log:284,316`）。处置是**补 commit ORIGINAL Artifact 并把断言改为 `region_box_equal(rendered, original_png, (150,20,100,100))` 的真实 bbox 像素比较**——这正是契约第 17 行"优先已有 ORIGINAL Artifact，缺失时用 original_page_reader 读 Managed Copy"的一条合法生产路径；同时**保留**了"无 ORIGINAL 且无 reader"的 fail-closed 覆盖（`:280-296`），且未删除既有断言。
- 两个新测试是真实验证，非冒烟：`tests/core/test_rc4_stdio_render_preview.py` 用真实 `assemble_production_core` + 真实导入 + 真实 NMFR clean + 断言无 ORIGINAL 行（`:130-133`）+ 真实子进程 stdio（`:141-156`）+ 真实 `ResourceCatalogStore`/`host_bridge` issue-resolve 与 size/sha256 校验（`:175-223`）+ 像素断言（SFX 盒 == 原图 `:231-234`；区外 == NMFR 通道序 `:239`）；`tests/rendering/test_pillow_rendering.py` 断言换行/竖排/fit=False/描边红像素/NMFR 通道序与截断帧 fail-closed。三个受审测试文件无 skip/xfail/todo/`assert True`。
- 残余：RC4-02（58b3706d 变更描述与 attempt-2→3 的翻转不自洽，需 `git diff 37110749..58b3706d -- src/` 核对）、`list/restore` 两条命令 Python 侧零 wire 测试（RC4-01）、Handoff 把 7 个失败分组成"4+2+1"而实际是 5 个 minor 期望（措辞精度，非实质）。

**8. 范围纪律 —— 基本 PASS，一处需追认（RC4-05）。**
`src/application/rendering/service.py` 的改动我逐段核过，全部落在 Task 授权表述内：(a) managed 读取异常从裸 `OSError/ValueError` 包成 typed `MISSING_REQUIRED_INPUT`（`:162-165,241-250,303-304`）＝"错误消息固定安全短语"的必要错误修复；(b) `reports.status/skip_reason` 白名单化与 op 缺失整页 blocked（`:201-217`）＝契约第 11 行的必要保护；(c) skip/manual SFX 的原图 bbox 像素恢复（`:221-267,597-612`）＝契约第 17 行与 Task 第 30/38 行明确授权；(d) 新增**可选** `original_page_reader` 构造参数（`:120,141`）＝Task 第 38 行授权"core_assembly 透传给 RenderService"，`core_assembly.py:756/1006` 仅透传、默认 `None` 不改旧行为。`src/ports/**`、`src/domain/**`、`src/infrastructure/sqlite/**`、Schema 均未见 RC-4 新增（`grep original_page_reader|RenderPreviewPublisher|Pillow*` 无越界命中；ports 内两次 `preview`/`render_preview` 命中为既有内容）；`sqlite/schema.py` 未加表。唯一越界是 `gen/schemas/**`（RC4-05）。**限制**：因无 shell，无法枚举完整 diff 文件清单，本项结论基于"按契约/Handoff 引用的路径逐处核对 + 全仓 grep 反向排查"，不等价于 `git diff --name-only` 的完备性检查。

---

## §Architecture

**PASS（限本次范围）。**
- 分层与依赖方向正确：React 只经 `RegionClient`/`ResourceChannelClient` → Tauri invoke，未直连 SQLite/任意 OS 路径/模型；Rust 无 rusqlite，只把 `catalog.sqlite`/derived 的**配置**经 env 交给生产子进程；预览为不透明 catalog key + host 侧 opaque grant，WebView 只拿到资产 URL（`build_url(opaque_id)`），未见 managed path/base64 下发。Core 是唯一业务权威（页存在性、revision/lock 守卫、写失败都落在 Core 或 Core 的提交 seam）。
- 共享契约与冻结面一致：三条 wire 名与 snake_case/camelCase 约定逐字对应（`library_bridge.rs:402-430`、`region/client.ts:46-48,141-212`、`region/types.ts:94-134`）；C1 §5 的 1.6 行与 minor 4 已冻结；未新增 ports/Schema；未触碰阈值 0.90、BJ13、SFX 默认策略、A/B/C 或 Legacy `src/ui`。
- 安全与持久化：`expected_current_revision_id` 在 `BEGIN IMMEDIATE` 内比较并 rollback（零写）；`expected_revision` 前置校验 + seam 再校验（双查）；原图读取校验 containment；预览发布限 derived 只读根；错误细节仅 stderr。
- 两个边界观察（非缺陷，供集成方登记）：① `render_preview_resources` 是**全局** Mutex 且持锁跨越一次阻塞式 Core stdio round-trip（`main.rs:320-331`），吞吐上的取舍已在源码注释自述，且是"撤销/登记不倒置"的正确性代价；② 页级 preview grant 只在**下一次同页 `rerender_page`**（或显式 `revoke_resource_refs`/TTL 300s）时被撤销，其他生产者改写该页 translated artifact 时不在本旋转逻辑覆盖内——与契约约束 3 的冻结口径（"成功切换页产物 revision"）不冲突，但属 T6 完整语义的已知边界。

---

## §Verification

**我实际做的（静态只读，read/grep/glob；未运行任何命令、未改动任何文件）**：
1. 逐条比对三命令 DTO/错误码/枚举/短语与冻结契约（`core_service.py:798-907,1196-1365`）——吻合，P3/P4 口径项见 RC4-08/RC4-10。
2. 追读 restore 全链路：service 前置守卫 → seam 事务内比较与 rollback → 快照锁回退字段集（`editing/service.py:726-784`、`sqlite/regions.py:201-288`、`domain/regions/entities.py:267-309`）。
3. 逐段核 `rendering/service.py` 的 fail-closed、skip 枚举白名单、skipped-SFX 像素恢复、`_commit_translated` 错误映射；核 `pillow_rendering.py` 的布局/合成/字体替换/NMFR 解码真实实现；核 `render_preview.py` 的 key 随机性、containment、写路径与登记 scope。
4. 核 `core_assembly.py:756/1006` 与 `core_service.py:290-341,1413-1431` 的装配/env 透传，确认旧调用行为保持与 reader 的 containment 校验。
5. 核 Rust 三视图（`PRODUCTION_COMMANDS`/`command_allowlist`/`generate_handler!`）与 `build.rs`/capabilities/gen-schemas 的 19 条一致性，以及 `rotate_render_preview` 的加锁位置与 revoke-previous-first 顺序、错误只回 code。
6. 核 React R-1/R-2/R-3 的具体行号（版本号 + page epoch、迟到 revoke、非零 PNG、typed 失败、冻结码、Inspector 文案、三入口资格禁用、undo 不反向改标）与 `region/client.ts`、`region/types.ts`、`commandSurface.test.ts` 的 wire 形状。
7. 核测试合法性：5 处 minor pin 更新的契约出处、2 处 skip-SFX 断言的像素级比较与 fail-closed 保留、2 个新测试的真实装配/真实字节/真实像素、skip/xfail 扫描。
8. 核范围：`src/application/rendering/service.py` 改动逐段归类到 Task 授权表述；对 `ports/domain/sqlite/schema` 做反向 grep；发现 `gen/schemas/**` 越界（RC4-05）。
9. 引用集成方 raw 证据（仅引用，不声称自己运行）：`combined-focused-final.log:17,63`（399 passed/EXIT 0）、`combined-full-final.log:407-408`（1852 passed + 1 skipped + 1 failed=既有 `test_catalog` 122≠97 / EXIT 1）、`combined-cargo-final.log:293,299,305-307`（51 passed + 1 ignored / EXIT 0，含真实 sidecar RC-4 typed-error 与单锁轮换）、`combined-react-fix-verify.log:20-27,33-39`（11 files/117 tests + build，均 EXIT 0）、`combined-sidecar-build-1.log:1,545`（HEAD=78e4f24d、EXIT 0）、`combined-diffcheck-final.log:2-3,78`（`git diff --check` range **EXIT_range=2**，全部命中项均在 `verification/**` 日志内、`^(src|tests|apps|packaging|doc)/` 零命中 ⇒ "代码面 EXIT=0" 的表述成立，但需注意该命令的 range 面实际非 0）、`reviewer-core-37110749-{existing-tests,input-error-probe,layout-probe,pillow-probe}.log`（7 failed 原始基线 + typed 缺口探针 + Pillow 行为探针）。

**明确 NOT_RUN（我未运行、且现有 raw 中亦无证据）**：
- 任何命令/测试/构建/git 操作（本会话 shell 不可用）；
- `restore_region_revision` / `list_region_revisions` 的 wire 成功路径与 DTO、`expected_revision` **过期**与**事务内竞态**零写（RC4-01，契约 Gate 明文要求项）；
- Rust 撤销失败 → `PREVIEW_UNAVAILABLE`/保留旧 key 分支（RC4-06）；
- 真实 WebView/资产协议下的预览读取与 grant 生命周期（React 侧只证明发起 opaque URL chunk 读并挂载非空 fixture bytes；真实 WebView 验收未做，Handoff `:44` 已如实登记）；
- 真实缺字体环境下的 `font_substituted`（现有 Pillow 测试依赖本机字体表，Arial 在验证机可用）；
- `5954bb4b` 上的任何 Gate 复跑（RC4-03）；
- `serde_json` 在 `result=null` 时 `IndexMut` 的行为（`main.rs:366-368` 的 panic 风险）：静态无法判定，但成功路径 Core 必返回对象，实际可达性低——登记为未判定项，不计缺陷。

---

## §结论

**verdict = `approved_with_conditions`。**

未发现 P0/P1 缺陷，也未发现任何**阻断性的实现缺陷**：Core 三命令的 DTO、typed error、fail-closed、restore 语义（新 restored revision/零写守卫/锁回退）、rerender 语义（skip 原图恢复/无 AI/无新锁门）、Pillow 真实渲染、preview 不透明 key 与 revoke-previous-first 轮换、Rust 三命令仅生产注册与 probe/AC1 零扩权、React R-1/R-2/R-3 返修，均经静态逐条核对与冻结契约吻合；Owner 对组合树 7 failed 基线的处置（58b3706d）**经独立判断成立**，属契约驱动的测试更新与补强，不是"测试迁就实现"（详见 §审查重点 7）。

**blocking 理由（须关闭，否则不得置 done / 不宜按现状宣布 RC-4 完成）：**
1. **RC4-01（P2）**：`list_region_revisions` / `restore_region_revision` 缺少 wire 级与"过期/事务内竞态"真实 SQLite 证据——这是冻结契约验证 Gate 的明文条目，当前应按 §6(12)②③ 记 `NOT_RUN`。须补齐用例并留下带 shell/venv/commit/command/EXIT 的 raw 日志，或由 Codex 显式登记该偏差。
2. **RC4-03（P3）**：现有全部 Gate 日志绑定 `78e4f24d/a1bd8acb/2f741407`，未覆盖 `reviewed_head=5954bb4b`；须在同一处写明两 head 间仅 docs/evidence 差异（或在 `5954bb4b` 复跑），否则本 Review 与后续 merge 的验证口径无法对齐。
3. **RC4-05（P3）**：`apps/desktop/src-tauri/gen/schemas/**` 越出 Task `allowed_paths`，须由 Codex 追认（同类先例：REGION-RETYPE review P3-2）。

**非阻塞条件（建议同轮处理）**：RC4-02（`git diff 37110749..58b3706d -- src/` 说明行为翻转来源，或修正 Handoff 描述）、RC4-04（补 7 vs 1 skip 的口径解释与那 1 条 skip 名称）、RC4-06（补撤销失败分支的可判别单测）、RC4-07（卸载窗口 blob 泄漏，加一行版本递增即可）、RC4-08（统一"必要输入不可用"的错误码）。

**AC 层面提示（供 Codex 判 done 用）**：AC1/AC3/AC4 的证据面基本成立（三命令接通、真实 headless 文字渲染与 skip 像素恢复、React 点击与错误可见性均有 raw 日志）；**AC2 与 AC5 尚不满足**——AC2 的"history 摘要真实可追溯"与"事务内并发零写守卫"缺 wire/竞态证据（RC4-01），AC5 的集成 Gate 证据头与 reviewed_head 未对齐（RC4-03）。本 Review 为静态审读，不构成实现批准，也不代表 Integration Gate 通过。
