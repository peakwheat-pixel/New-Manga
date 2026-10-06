## 一、固定事实与方法

| 项 | 值 |
|---|---|
| 仓库 | `G:/CODEX/New Manga.worktrees/RC4-review-preflight`（linked worktree，common dir=`G:/CODEX/New Manga/.git`） |
| 固定 head | `bb7f3dcba9685f761bbb9ee5e271b1f91c3e7811`（读 `.git/worktrees/RC4-review-preflight/HEAD` 确认） |
| Task base | `44421008`（Task 元数据字段；Task 第 64 行自述"审计基线，Owner worktree 起点取 release commit"） |
| Task | M2-RC4-DOMAIN-COMMANDS，`status: ready`（Task 第 5 行），Reviewer=DeepSeek Harness（第 9 行） |
| 方法 | 纯静态只读：契约/Task/C1 保护条款/既有实现与服务/端口/Rust allowlist/依赖清单逐处比对；不运行代码、不改文件、不联网 |

**只读边界遵守**：未修改任何文件，未读仓库外凭证，未联网，未调用其他 agent，未安装依赖。

### 方法限制（必须随结论携带）

- **pwsh 不可用**：本 worktree 上两次调用均以 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)` 失败（沙箱初始化），因此**未运行 git/测试**；`git status` 脏状态、`git log`、diff 面均未实测，只用文件系统读取（HEAD 文件、源码、文档）。
- **未运行任何测试**。394 focused + 105 frontend（`verification/M2-RC4-DOMAIN-COMMANDS/rebaseline-20261007.md:17`，绑定 main@`3dc16a9d` / main@`915daf61`）是既有基线，**不是 RC4 产品验证**，本次也未复跑。
- 产品代码仍为基线：`core_service.py:289-291` 仍是 `font_catalog=object()/layout_engine=object()/compositor=object()`；`restore_revision` 无 IPC、应用层未传期望 current ID（`rebaseline-20261007.md:11`）；三命令、preview 发布、UI 解禁均未实现。**本报告不声称 RC4 已实现。**
- 本次是**契约预检**，不是实现批准；最终代码须另行固定 head 审查。

---

## 二、Architecture 面结论（可否落在冻结 seam 内）

**可实施性骨架成立**，三条命令均有既有 seam/服务/端口可复用，无需新 ports/Schema，与 Task `allowed_paths` 兼容：

| 契约要求 | 既有事实 | 判定 |
|---|---|---|
| restore 事务内零写守卫 | `RegionRevisionCommitter.commit_region_revision(..., expected_current_revision_id, lock_snapshot)` 已存在（`application/editing/ports.py:72-79`），SQLite 实现已在 `BEGIN IMMEDIATE` 内比较并 rollback（`infrastructure/sqlite/regions.py:201-253`） | 不需要改 ports；契约第 15 行"编号校验→传 current ID"设计无 TOCTOU（每次写都换 revision id，ID 比较等价编号比较） |
| 恢复为新 restored revision、历史/pin 不动 | `service.py:694-716` 已 `origin=RESTORED` + `restored_from_revision_id` + 新 revision；pin 为专用单语句（`sqlite/regions.py:183-195`） | 可行 |
| 历史读取 | `RegionRepository.list_revisions/get_revision` 已在 port（`ports.py:30-34`）；`RevisionSummary` 所需字段全在 `RegionRevision`（`domain/regions/entities.py:313-327`） | 可行，无 port 变更 |
| rerender_page 同步渲染 | `RenderService.rerender_page` 已存在（`service.py:145-221`），无 AI 端口引用 | 可行 |
| skip 区域原文像素回填 | `ImageCompositor.compose_region(base, clean, box, op)` 已存在（`ports/rendering/ports.py:108-118`） | 复用即有接口可行（见 P1-1：契约未承载该语义） |
| preview 资源通道 | `application/resource_channel/service.py` 已有 issue/resolve/TTL 300s/revoke；`ALLOWED_SCOPE_CLASSES=("derived-read-only","managed-read-only")`；Rust `StdioCoreChannel` 已把 derived/managed/catalog 传给 host_bridge（`core_bridge.rs:115-144`） | 通道存在，但引发生命周期与跨进程配置未冻结（见 P2-5） |
| Rust allowlist/ACL | `PRODUCTION_COMMANDS`(9) + probe/ac1 过滤机制已存在（`main.rs:51-65,106-127`）；测试 pin 为 7/6/9 | 加三命令可直接扩展，probe/AC1 零扩权机制成立 |

**已确认合规（非缺陷，避免误报）**：Pillow **不是新依赖**——`requirements.txt:42-44` 明确 PIL 由 `torchvision` 硬 `Requires-Dist: pillow` 保证，故契约第 16 行"已安装 Pillow、不引入新依赖"成立。产品边界（阈值 0.90、BJ13 维持现状、A/B/C 不重开、不启动补标/补画）在契约与 Task 禁止范围（Task 第 45 行）内均未被触碰；契约第 3/11 行明确"不释放通用 PipelineRun 命令族、不伪造 PipelineRun"，与用户"不要把完整 PipelineRun 扩展当本 slice 前提"的裁决一致。

---

## 三、分级 findings（条款、触发、影响）

### P1-1｜契约未冻结 sfx skip/manual 区域的成品像素语义，与来源设计稿冲突，验证 Gate 断言不可判定

- **违反/缺口条款**：契约第 11 行（`rerender_page` 仅"消费当前 clean"+"遵守 SFX skip/manual 与 Region lock 现有门"）、Task AC3（第 30 行"sfx skip/manual 不绘制旧译文"）、契约验证 Gate（第 24 行"skip 图像像素断言"）——三者均未定义 skip/manual 区域在成品图中的像素来源。
- **来源冲突（硬证据）**：`doc/design/M2-SFX-MISROUTE-UI-MITIGATION/design.md:259` 明确"**sfx+skip 语义下 rerender 产出 = 原文保留图**"；`design.md:46/253` 明确"已渲染成品图上的错误译文不会因改标消失，恢复原文需要 rerender""原图完好，成品图需重跑渲染才恢复原文"。RC4 契约以该设计稿 §4.1–4.4 为来源（契约第 3 行），但未承载该语义。
- **触发条件**：页内存在 `sfx` + `skip`/`manual` 区域，且其原文像素已在 clean（inpaint）中被擦除时执行 `rerender_page`。
- **影响**：按契约字面复用现状路径（`service.py:188-197` 对 skip 只 `continue`、不产生 op，`compose_page(clean, ops)`），成品图该区域为 inpaint 背景、**原文丢失**——直接与设计稿 §4.4 和用户"改标只减害、保留原文"目标相悖；同时 Gate 第 24 行的"skip 图像像素断言"**没有期望值**，无法判 FAIL（判别力为零），AC3 因此不可验收。
- **要求**：契约补一条冻结条款（skip/manual 区域从 ORIGINAL 的 bbox 恢复像素；ORIGINAL 缺失时的 fail-closed 行为），并把"skip 区域成品像素 == ORIGINAL 对应 bbox 像素"写进验证 Gate。用户已确认实施复用 `compose_region`、无新 ports/schema，但**必须进契约文本**，否则实现无冻结依据、审查无判据。

### P2-2｜restore 的 Lock 语义自相矛盾，"恢复快照 Lock"与"不得自动解锁"无优先级；Gate 的 Lock 断言无期望

- **条款**：契约第 10 行同一段并存两句——"沿现有 restore 语义恢复快照内人工文字和 **Lock**"与"**不得自动解锁**、清理历史或覆盖源文件"；第 24 行 Gate 又要求"真实 SQLite restore（历史/pin/人工文字/**Lock**…）"。
- **既有实现事实**：revision snapshot 含四个锁字段（`entities.py:267-288`），`restore_from_snapshot` **无条件覆盖**（`entities.py:290-310`），seam 用 staged 快照整体 `UPDATE` locks（`sqlite/regions.py:266-274`）。
- **触发条件**：当前 revision 的锁比源 revision 更严格（例如用户在改标后加/保留锁，再恢复到更早 revision）。
- **影响**：恢复会把 `region_locked/translation_locked/inpaint_locked` 静默改回快照值 → 人工 Lock 丢失；而契约同时禁止"自动解锁"，且 §10（`M2-C1_TYPED_IPC_CONTRACT.md:351`）要求"Preserve … Lock … across commands"。两种解读（取快照值 / 取更严值）都合理但未冻结，实现者只能猜；Gate 的 Lock 场景无期望值，不可判定。
- **要求**：冻结优先级并写入 Gate 断言（建议明确"恢复语义是否包含锁回退"，若包含则 undo/恢复必须带显式确认）。

### P2-3｜`rerender_page` 声称的"Region lock 现有门"与现状不符，错误码集合不含 LOCK_CHANGED

- **条款**：契约第 11 行"遵守 SFX skip/manual 与 **Region lock 现有门**"；错误码枚举（MISSING_REQUIRED_INPUT / TARGET_NOT_FOUND / INPUT_REVISION_CHANGED / COMPOSITION_BASE_CHANGED / ARTIFACT_WRITE_FAILED）**不含** `LOCK_CHANGED`。
- **现状事实**：页级 `rerender_page` **没有**任何 lock 检查（`service.py:145-221`，逐 region 只走 `_prepare_region`）；`region_locked` 门只在单区域 `rerender_region` 存在（`service.py:233-236`）。
- **触发条件**：锁定区域所属页执行 `rerender_page`。
- **影响**：三种可能行为都没有冻结依据——忽略锁（与契约"遵守现有门"字面不符）、跳过锁区域（新语义未登记）、整页返回 LOCK_CHANGED（新错误码未登记）；AC1/AC3 的 typed error 验收因此无法写断言。

### P2-4｜`rerender_page` 的冲突/写失败错误码集合与实现可产出集合不一致

- **条款**：契约第 11 行"提交冲突=INPUT_REVISION_CHANGED 或 **COMPOSITION_BASE_CHANGED**，写失败=**ARTIFACT_WRITE_FAILED**"。
- **现状事实**：
  - `COMPOSITION_BASE_CHANGED` 只在 `rerender_region` 传入（`service.py:319` 的 `composition_base_changed=True`）；页级 `rerender_page` 调用 `_commit_translated` 时**不传**（`service.py:215-221`），冲突只会得到 artifact 层的 `INPUT_REVISION_CHANGED`（`sqlite/artifacts.py:205-215`）。
  - artifact 提交的 SQLite 异常 → `CommitStatus.DB_FAILED` + `error_code="COMMIT_CONFLICT"`（`sqlite/artifacts.py:174-181`），`_commit_translated` 把状态映射为 `WRITE_FAILED` 但 **error_code 原样透传**（`service.py:510-524`）；哈希不符另有 `ARTIFACT_HASH_MISMATCH`（`sqlite/artifacts.py:147-151`）。
- **触发条件**：页级重渲染提交期发生 current 变化或 DB 异常。
- **影响**：契约错误集合不是实现可产出的集合；实施者若直通 `error_code`，wire 会出现契约外码（`COMMIT_CONFLICT`/`ARTIFACT_HASH_MISMATCH`），若映射则契约需登记映射表（沿 §5.4"零新错误语义"纪律）。

### P2-5｜preview 引用形态/生命周期与 Core↔host 配置传递未冻结（安全红线相关）

- **条款**：契约第 11 行"preview 为现有 resource channel 可读取的**不透明资源标识**"、`preview: {resource_id, revision}`；第 17 行"预览仅 Core 将已提交 PNG 发布到现有 derived 只读根并通过 ResourceCatalogStore 登记；Rust 仅向生产 Core 子进程传递同一 catalog/derived 配置"。
- **事实与冲突**：
  1. §10.2（`M2-C1…:381`）要求"WebView 可见引用必须是**不透明随机映射 ID**，不得编码或暴露 path/resource identifier"；而 `resource_id` 是 catalog 主键名（`catalog_loader.py:10-16` 的人工命名、`catalog_store.py:62-81` 主键 upsert），不是随机映射 ID。契约未说明 preview 是"待 Rust host 再 issue 的 catalog 键"还是"已 issue 的不透明引用"。
  2. §10.1 T6（`M2-C1…:373`）要求"revision switch/删除/pin 释放触发**立即撤销**"；但 `resource_catalog` 以 `resource_id` 为主键 upsert 覆盖，契约**未定义每次重渲染的 resource_id 生成规则**，同一 id 复用会让 T6 按 revision 撤销不可实施。
  3. 跨进程：`ResourceCatalogStore` 是独立 SQLite 文件、注释自述"product wiring swaps this adapter for the product DB in a later slice"（`catalog_store.py:9-14`）；issue 侧跑在 **host_bridge**（`core_bridge.rs:115-144`），而生产 rerender 跑在 **core_service**（`main.rs:563-577` 的 `StdioLibraryChannel::spawn` **只传 data_root，不传 derived/catalog**）。契约要求的配置传递是**新增工作**，必须显式登记（`library_bridge.rs` 在 allowed_paths 内，可做）。
  4. TTL/撤销状态是 host_bridge 进程内存态（`application/resource_channel/service.py:245-279`），重启后 preview 引用为 `REF_UNKNOWN_ID`；契约未登记该生命周期边界。
- **触发条件**：Core 直接把 `{resource_id, revision}` 下发 WebView；或后续重渲染复用同一 resource_id；或 host_bridge 重启。
- **影响**：可能稀释/违反 §10.2 T5.4 与 §10.1 T6 已裁决语义；preview 读取在重启后失败；契约"绝不将 managed path 交 WebView"的表面合规掩盖了"标识不透明性 + 可撤销性"的实质缺口。

### P2-6｜C1 §5 typed command catalog 未登记 `rerender_page`（与设计稿 D10 的命令面也不一致）

- **条款**：契约第 3 行"来源：M2-C1 §5/§8/§10"，第 7 行冻结三个新 wire 名。
- **事实**：`M2-C1_TYPED_IPC_CONTRACT.md` §5 表（112-132 行）**没有** `rerender_page`/`RerenderPage` 行；`ListRegionRevisions`/`RestoreRegionRevision` 行也**没有 1.6 指针**——而 1.3/1.4/1.5 三版都在 §5 表加了指针/行（表格内嵌注记）。§5.4 的 RC-4 候选登记清单（`:201`）只列 suspect/review_state/文本/D7 RevisionSummary/D8 reader 摘要，**不含 page 级 rerender 命令**。设计稿把"重渲染本页"绑定 `rerender_single`（`design.md:259`）并登记"run 通道 runtime 未实现（PROPOSAL 层）"（`design.md:279`）。
- **触发条件**：集成 Gate 或后续 agent 按 C1 §5 目录核对 minor 3→4 的命令增量。
- **影响**：typed command catalog 与实际冻结面不一致；契约"来源含设计稿 §4.1–4.4"与 §4.4/D10 的 run 通道命令面不一致（RC4 有意改同步命令，但未登记取舍）；`rerender_page` 作为**新增命令**缺 C1 登记行，minor bump 的依据只能靠 RC4 文件自身。

### P3-7｜`rerender_page` 的页存在性检查（TARGET_NOT_FOUND）无落点

契约第 11 行要求"页不存在=TARGET_NOT_FOUND"，但 `RenderService` 无 page 仓库 port（`service.py:107-140` 依赖集）且本 Task 禁止改 ports；现状先例是 handler 层 `self._core.repository.get_page(page_id)`（`core_service.py:737-746`）。契约未写明由 core_service 承担，实施者可能误判为"无 clean"（现状页级真实路径：clean 缺失即 `MISSING_REQUIRED_INPUT`）。

### P3-8｜`MISSING_REQUIRED_INPUT` 的语义覆盖不全

契约把该码只绑定"无 clean"，但现有 `rerender_page` 还用同一码表示**字体/布局解析失败导致的整页 blocked**（`service.py:198-201`）。实施者若严格按契约映射，会把这类失败降级为 `UNKNOWN/internal`，造成错误码漂移。

### P3-9｜`reports` 的值域未冻结

契约 DTO `reports: [{region_id,status,skip_reason,font_substituted}]` 未冻结 `status` 与 `skip_reason` 值域；现状为 `"rendered"|"skipped"` 及自由文本 `"skip_policy"/"empty_final"/"style_resolution_failed: …"`（`service.py:69-70,535-536,418-425`）。§3.1（`M2-C1…:91`）要求 enum wire 值必须显式、不静默降级；读面值域不冻结会让前端无法判分支。

### P3-10｜`preview_error` 的安全短语约束未显式化

契约"错误消息固定安全短语，细节仅 stderr"出现在错误码列举之后；`preview_error` 是 **result 内字段**，契约未显式覆盖。若实施者透传 `OSError` 文本（含绝对路径），即触发 §10.2"绝对路径下发禁止"与 §8 `message` 约束红线。

---

## 四、契约是否可实施

**方向可实施，但不能作为实现验收依据。**

- 可实施性成立：三条命令均落在既有 seam/服务/端口内（`commit_region_revision` 已支持事务内 expected；`restore_revision`/`list_revisions`/`set_revision_pinned`/`RenderService.rerender_page`/`compose_region`/resource channel issue+TTL+revoke/Rust allowlist 三视图全部存在），**无需新 ports、无 Schema 变更**，与 allowed_paths 一致；用户裁决（阈值 0.90、BJ13 维持现状手动改标+skip、A/B/C 不重开、不启动补标/补画、自主 RC4、不把完整 PipelineRun 扩展当前提）在契约文本中未被违反。
- 必须先关闭：**P1-1（skip 像素语义，来源设计稿硬要求 + Gate 不可判定）**；以及 P2-2/3/4（Lock 优先级、lock 门与错误码集合）、P2-5（preview 引用/生命周期/跨进程配置，涉及 §10.1 T6、§10.2 T5.4 已裁决语义）、P2-6（C1 §5 登记）。P3 项建议一并精确化以保 AC1/AC3 可测。
- 建议处置：由 Codex（契约唯一修改方）在 `doc/contracts/M2-RC4_DOMAIN_COMMANDS.md` 补条款 + 在 C1 §5 表加 `rerender_page` 行/指针（rev 1.6 增量内），Gate 增加可判定期望（skip 区域像素 == ORIGINAL bbox；锁的期望值；错误码映射表；preview 引用的不透明性与撤销规则）。契约修订后再交 Owner 实施，最终代码另行动固定 head 审查。

---

## 五、推荐下一步

**推荐下一步**：Codex 对 `doc/contracts/M2-RC4_DOMAIN_COMMANDS.md`（rev 1.6 增量）与 `M2-C1_TYPED_IPC_CONTRACT.md` §5 表做一次**契约返修**，优先补 P1-1（sfx skip/manual 原文像素恢复 + Gate 期望），同步冻结 P2-2/3/4/5/6；返修 head 固定后再由 DeepSeek 做一次"契约增量 vs 来源设计稿/错误码集合"的窄面复核，然后才进入实施与最终代码固定 head 审查。在 P1-1 关闭前，不建议把当前契约作为 AC 验收依据，也不建议据此宣布任何 RC4 完成度。

（本报告为只读契约预检；无文件被修改；394 focused + 105 frontend 为既有基线，不构成 RC4 产品验证；本次不代表最终实现批准。）