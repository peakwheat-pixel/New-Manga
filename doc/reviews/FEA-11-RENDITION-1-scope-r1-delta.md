---
task: FEA-11-RENDITION-1
title: FEA-11-RENDITION-1 第二独立审阅者 delta（不替代 scope-r1 主报告）
reviewer: fresh subagent（独立上下文；未参与实现；只读）
session: 8b4d1482-352b-42d0-9829-6ccf60716022（DSH fresh subagent）
parent_session: session-c2883c5f-dcf8-400d-b161-9c84f562486a
reviewer_kind: subagent
date: 2026-11-06
reviewed_head: 987d81981
verdict: READY-WITH-UNFREEZE（仅就"契约文本充分性"这一问；不推翻主报告对代码事实的裁决）
supersedes: 否
---

# FEA-11-RENDITION-1 第二独立审阅者 delta

> **定位声明（必读）**
>
> 1. 本文件**不是** r1 主报告，**不替代** `doc/reviews/FEA-11-RENDITION-1-scope-r1.md`。
> 2. 我开工时（2026-11-06 19:06 之后）目标路径**已存在**一份 53,619 字节的完整报告（`LastWriteTime 19:09:29`，frontmatter `verdict: READY-TO-FREEZE`，含 pytest/verify_pins/in-memory 探针实测）。该文件并非本会话产出：我在同一时间窗内只做了只读源码/契约核验，未运行 pytest/pins/探针，也未写入任何文件。
> 3. 按"只读审查者不覆盖另一审查者已签名字节"的纪律，我**没有覆盖**该文件。本 delta 只记录我独立得出、且与主报告**同向或分歧**的少数结论，供 Lead 合并/丢弃。
> 4. 若 Lead 已采纳主报告，可**整文件删除**本 delta，不影响任何事实链。
> 5. 局限：我只读了主报告前 50 行 + 约 40 行 grep 命中，**未通读**其 §4–§9。因此下文凡涉及主报告的表述，均以我已读到的片段为限，可能主报告已在未读部分给出更强论证。

---

## 1. 我独立核验的事实（与主报告不冲突的部分）

| 事实 | 证据（我实测） | 与主报告关系 |
|---|---|---|
| HEAD `987d81981`；`main` | `git rev-parse --short HEAD` | 一致（主报告写全 sha `987d81981baf6…`） |
| 工作树有 3 项 Lead 侧未提交内容：`M doc/tasks/FEA-11.md`、`?? doc/reviews/AC11-1-ADJUDICATION-INPUT-2026-11-06.md`、`?? doc/reviews/FEA-11-AC11-1-adjudication-2026-11-06.md` | `git status --short` | 一致（主报告 §1 已记录"审查中由 Lead 并发写入"） |
| 纯 referenced 页被 `_page_or_error` 拒绝 | `pipeline.py:1420-1434`：`row["source_hash"] is None or row["managed_original_ref"] is None` → `TARGET_NOT_FOUND` | 一致（主报告 :99/:120-123） |
| `_region_or_error` 同类门槛 | `pipeline.py:1477-1478`：SQL WHERE 直接要求 `managed_original_ref/width/height` 非空 → 不命中即 `TARGET_NOT_FOUND`（`:1481-1482`），与"region 不存在"不可区分 | 未在主报告已读片段出现；属 P3 |
| provider 图像源只读 managed original | `core_assembly.py:379-411`（`_page_image`），装配 `:1553`；5 个调用面 `handlers.py:360,490,683,892,1081` | 一致（主报告 §3 F4） |
| `run_source_guard` 只在 commit 进入 | `core_assembly.py:1623-1641`；`pipeline.py:886-887`（`commit_step` 内 `source_commit_guard`）；全仓 `gate_of_binding` 调用点不含 provider 读图 | 一致（主报告 F4 明写"gate 只在 commit"） |
| gate 谓词已有两份实现 | `core_service.py:4458`、`:4725`、`:5084-5099`（`_assert_source_sync_gate`）与 `core_assembly.py:1633` | 一致（主报告 F4） |
| §7.2 v2 key 已逐字实现 | `core_service.py:4607-4632`；同 key 异摘要 → `SOURCE_ACCESS_DENIED`（`:4634-4659`） | 一致（主报告 AC-R6 前提） |
| 选择函数已收敛 | `application/importing/referenced/resolve.py:47-139`（binding→entry→grant/generation→decoder/params），`:142-150` 渲染 | 一致（主报告 AC-R5） |
| Run 面 pending gate 现映射 `TARGET_NOT_FOUND` | `core_assembly.py:1633-1637`（`"source binding is pending acknowledgement"`），而非 §3.3 的 `SOURCE_ACCESS_DENIED` | **主报告 :109 记录事实但未标为契约冲突**；见 §2 分歧点 |

未独立复核（引用主报告，信任其证据）：F1（Run 无 source-read grant 通道）、F2（chapter/book-scope 整批失败）、`HostCommandRegistry.cs:30-37` 只用于命令级错误、`application/tasks/service.py:971` 的 `DB_FAILED` 投影。这些凡涉及 `apps/**` 的断言，我按纪律未打开 `.cs` 文件逐行核对。

---

## 2. 我的独立结论与分歧点

### 2.1 结论

- **代码事实层**：主报告的 READY-TO-FREEZE 前提（L10① 复现、F1 生产 Run 不可端到端、F4 gate 缺输入面）我**不反对**；我独立看到的证据与其中已读片段一致。
- **契约文本层**：我仍判 `READY-WITH-UNFREEZE`，理由是 **C-15 §4.2 的五读路径表（`FEA-C15_SOURCE_STORAGE_DRAFT.md:266-274`）恰好五行，没有 provider/Run 图像输入这一行**；C-17 §7.2"实际资源读取"（`FEA-C17_SOURCE_SYNC_DRAFT.md:337`）可两解。主报告选择"§4.2 只约束 resolve/发布面、不禁止进程内 provider 读取"，这是**可辩护的读法**，但它是**解释**而非契约字节；一旦 Owner 按相反读法实现（回退 managed original），审查只能靠解释争论。
- **代价对比**：补一行 doc 文本（U1/U2，零 schema/wire/依赖）的成本，远低于一次"读法争议 → 返修"。因此我建议 Lead **落 U1/U2**；若 Lead 判定文档冻结期不宜动 C-15/C-17，则必须在 Task `interpretation` 段写死同一读法，并由 Lead 在 STATUS/裁决记录里认账。

### 2.2 与主报告的两个具体分歧（供裁决，不要求改主报告）

- **D-A（§3.3 码映射，P1 级记录）**：§3.3 冻结文本写"pending → `SOURCE_ACCESS_DENIED`"；代码在 Run 面给的是 `TARGET_NOT_FOUND`（`core_assembly.py:1633-1637`）。主报告 AC-R4 #4 接受"目标展开 `TARGET_NOT_FOUND` 或读图 `PROVIDER_FAILED`（detail 记录 `SOURCE_ACCESS_DENIED`）"。我同意这是**工程上可接受**的投影，但它与 §3.3 的**码**字面不一致，必须在卡面/裁决记录里显式写明"§3.3 的码在 Run 面按 C-08 步骤级投影解释"，否则下一个审查者会以同一处再开 finding。**建议 Lead 一句话裁决即可，不必改契约。**
- **D-B（"两套 key"误用风险，P3→实现约束）**：`resolve.py:107-118` 的 `prepared["cache_key"]`（`"\0".join`，缺 page_id/binding_id/verified_digest）与 `RenditionCache.rendition_key`（含 kind 的 json.dumps）是**不同派生**；`core_service.py:4698` 用它写 `rendition_cache` 行，而 `acquire` 用 `rendition_key` 查。若 RENDITION-1 让 provider 复用缓存，**必须用 `acquire` 的同参**（source/version/entry/kind/decoder/decoder_version/params），**不得**把 `prepared["cache_key"]` 当缓存键。主报告未提这一点（未读部分可能有）；建议直接写进 Owner 的实现约束与 AC-R5 的静态断言。

### 2.3 我撤回的一条错误假设（记录以免误导）

开工时我倾向把"Run 流出现 `SOURCE_ACCESS_DENIED` → Host `AllowedRunErrorCodes` 未注册 → `category=unknown`"列为风险（依据 `M2-C1:270`）。读到主报告 `:112` 的证据（`HostCommandRegistry.cs:30-37` 仅用于命令级错误；step/task 码直接进 Run 快照、不经该表）后，我判断**该风险不成立于 step 级失败面**；但命令级 `StartRun` 若在**接受前**返回 `SOURCE_ACCESS_DENIED`（例如目标展开阶段）仍可能走命令投影。**该点未独立验证**，建议 AC-R7 加一条断言：记录 `StartRun` 在目标展开失败时实际到达 Host 的 code/category。

---

## 3. 对主报告 AC/范围的补充建议（最小集，不重写）

- **AC-R1 补**：混合 chapter-scope 展开成功（主报告已有）之外，补一条"region-scope 在 referenced 页 `width/height` 为 NULL 时仍 `TARGET_NOT_FOUND`，且 retryable 与 message 稳定"——`resolve.py:92-100` 会回退 `page.width`，若为 0 则在 `rendition_cache.acquire` 处变成 `SOURCE_BUDGET_EXCEEDED`（语义误导）。
- **AC-R2 补**：混合页（referenced + `managed_original_ref` 非空）中，managed original 与 binding 图**尺寸和内容都不同**，断言 `page_frame` 的 `width/height` + 像素 sha256 等于 binding 图，且 managed 路径零调用（spy）。
- **AC-R4 补**：无匹配 grant 场景（`find_bound_for_source` 未命中——`resolve.py:84-90` 只比较 generation，未验证未命中行为）必须 typed，不得落到 `KeyError`/`None`。
- **allowed_paths**：我同意主报告的"`tests/fea11/conftest.py` 与 `test_source_lineage_run.py` 不在 Owner 写域、需 Lead 增列"的保守取向；若 final 冻结时允许，建议只放开 `test_source_lineage_run.py` 的 stub 使用面（最小），`conftest.py` 仍由 Lead 或单列。

---

## 4. 摘要

- 目标路径已有完整主报告（`READY-TO-FREEZE`）；本 delta **不覆盖、不替代**，可整文件删除。
- 我独立核验的代码事实与主报告已读部分一致；我**不反对**其 L10①/F1/F4 结论。
- 唯一实质分歧是**契约文本层**：C-15 §4.2 五读路径表缺 provider 行、C-17 §7.2"实际资源读取"可两解 → 我判 `READY-WITH-UNFREEZE`，建议 U1/U2 两处零行为文本追加；若冻结期不动契约，须在 Task `interpretation` 写死读法并由 Lead 认账。
- 两条实现约束建议：①"§3.3 码在 Run 面投影"必须显式裁决；②provider 接缓存必须用 `acquire` 同参，禁用 `prepared["cache_key"]`。

---

RENDITION-1-SCOPE-DELTA: READY-WITH-UNFREEZE（仅契约文本层）— 代码事实层认可主报告 READY-TO-FREEZE；分歧仅在 C-15 §4.2 五读路径表缺 provider/Run 图像输入一行、C-17 §7.2「实际资源读取」可两解，建议 U1/U2 零行为文本追加；另建议显式裁决 §3.3 在 Run 面的码投影（现 `TARGET_NOT_FOUND`）与「provider 必须用 `acquire` 同参而非 `prepared["cache_key"]`」两条实现约束。本文件不替代 `FEA-11-RENDITION-1-scope-r1.md`。

---

## Lead 裁决（DSH，2026-11-06；本 delta 的定位与处置）

**仲裁：以 `doc/reviews/FEA-11-RENDITION-1-scope-r1.md` 为唯一权威 scope review（`READY-TO-FREEZE`）。** 本 delta 作为第二独立只读复核**存档**，不作为冻结依据、不推翻主报告；两份报告均记录审查者与来源（见 frontmatter `session`）。

| # | delta 议题 | Lead 裁决 |
|---|---|---|
| 1 | **U1/U2**（C-15 §4.2 加 provider/Run 行；C-17 §7.2 加限定句） | **不采纳 UNFREEZE。** C-17 §7.2 已把「resolve 与 issue/**实际资源读取**必须使用同一选择结果」写入冻结文本；C-15 §4.1 的 `R(p,t)` 是可读谓词、§4.2 只约束 resolve/发布面——组合已覆盖本卡读法。UNFREEZE 载体制造成本（载体+独立 byte-level 复核+重冻+pins 重算）高于收益，且本卡刻意为零契约字节。**改以冻结卡面「实现语义」段写死同一读法并由 DSH 认账**；实现者/复审者以卡面为准。 |
| 2 | **D-A：§3.3 pending 的码投影**（C-17 §3.3 写 `SOURCE_ACCESS_DENIED`；Run 面现为 `TARGET_NOT_FOUND`） | **按既有 family 投影，不改契约、不新增 `SOURCE_*` 到 Run 命令面。** 依据 C-17 §8:352「旧命令不重映射」+ C-08 步骤级投影：Run 目标展开/StartRun pending → 既有 `TARGET_NOT_FOUND`；provider 读图失败 → 既有 `PROVIDER_FAILED`/`INVALID_INPUT`，detail 记录 source 语义。已写入卡面 AC-R4 与 L-R8。 |
| 3 | **D-B：`prepared["cache_key"]` ≠ `RenditionCache.rendition_key`** | **本卡 provider 不接 `rendition_cache`**（Out/L-R7）；卡面新增实现约束：不得用 `prepared["cache_key"]` 作为任何缓存键；未来如接缓存必须用 `RenditionCache.acquire` 同参。AC-R5 增加「provider 不调用 `rendition_cache.acquire`、不发布 catalog」的静态/探针断言。 |
| 4 | 重复派发（同一路径两个 fresh subagent） | Lead 派发重叠所致，由 DSH 负责；保留两份证据（主报告权威 + 本 delta 存档），不要求合并、不删除。 |
| 5 | 工作树 3 项未提交 WIP | 已由 Lead 落盘为提交 `cdba15742`（`docs(fea-11-ac11-1)`）；本 delta 的 `reviewed_head: 987d81981` 为审查开始时 HEAD；契约/代码/测试零 diff。 |

**对实现的影响**：主报告 F1（Run 无 source-read grant 通道）→ 卡面冻结 `Core-only + L-R1`；F2（chapter/book-scope 整批失败）→ AC-R1 覆盖；F3 → I-4；F4/F5 → I-3；I-5（commit guard 投影改造）出域（L-R8）。本 delta 的 §3 补充建议（region-scope width/height NULL、混合页双图判别、无 grant typed、不得 KeyError）已并入卡面 AC-R1/AC-R2/AC-R4。

