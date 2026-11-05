---
id: FEA-11-MATCH-1
title: FEA-11 页匹配 pixel profile 提取与旧库 fixture（C-17 §7.3 续）
kind: implementation
governance_version: 3
status: done
approval: scope 已按 ZCode SCOPE-ADJ-2026-11-05 冻结，**DSH 2026-11-06 释放（ready）**：承接 FEA-11 AC11-3 的 L-4 缺口（r1 R-012 / r7-acceptance L-4）；释放时由 DSH 固定 base_commit、Owner 与上下文独立 Reviewer；**2026-11-06 实施交付（in_review）**：Owner=`fea12-dsim-impl`（DSH Agent Teams，Lead `lead`），交付 head `b4ad109da`，AC-M1…AC-M6 MET（`.NET` NOT_RUN），check.ps1 PASS；**r1 独立上下文 Review approved（P0/P1=0；P2×3/P3×7）**；**2026-11-06 r2 最小返修交付 head `e8b0b2db8` → r2 窄面 Review approved（P0/P1/P2=0）→ done closeout（AC-M1…M6 全 MET；delivery `869b6d5d5`；AC11-3 回填 MET 带 L-M1/L-M4 limitation）**
suggested_owner: codex
owner: fea12-dsim-impl（DSH Agent Teams 成员；Lead `lead`）
reviewer: 独立上下文 fresh subagent（r1 `doc/reviews/FEA-11-MATCH-1-r1.md` session `b9716b1a-a95a-41bf-9400-533dc797e7b0`；r2 窄面 `doc/reviews/FEA-11-MATCH-1-r2.md` session `2658835c-a883-472a-89a5-e0e2f5c01c3e`；均未参与实现）
depends_on:
  - FEA-11-PREREQ-1
base_commit: 2d9a4a219   # 释放点 main head（AC4-GAPS-1 closeout 后）
branch: null
worktree: null
integration_commit: 869b6d5d5
delivery_head: 869b6d5d5   # 交付 head（含证据/卡/Handoff）；实现+测试 head=e8b0b2db8；r1 交付 c12023ab6（含 7bd8efe47/2d61e43c3/b4ad109da）
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-11-MATCH-1
allowed_paths:
  - doc/tasks/FEA-11-MATCH-1.md
  - doc/reviews/FEA-11-MATCH-1-*.md
  - doc/handoffs/FEA-11-MATCH-1-*.md
  - src/application/sources/scanner.py
  - src/application/sources/matcher.py
  - src/application/sources/model.py
  - tests/fea11/test_source_match.py
  - tests/fea11/test_source_scan.py（仅 W1 窄批：该用例期望值 + docstring，约 1–2 行）
  - tests/fea11/test_source_sync.py（仅 DSH 2026-11-06 窄批 **W1b**：本地 `_seed_two_page_source(legacy_v7_evidence=False)` 路径补真实 pixel profile，不改断言）
  - tests/fea11/test_source_relink.py（仅 **W1b**：本地 `_seed` 补真实 pixel profile，不改断言）
  - tests/fea11/test_source_sync_storage.py（仅 **W1b** 授权范围；实际经 `test_source_sync` 共享 helper，未改行）
  - tests/fea11/fixtures/**
  - verification/FEA-11-MATCH-1/**
out_of_scope:
  - PDF（及任何非 image/folder/zip/cbz 源）pixel profile：缺 document_raster seam 与原始 RGB 端口，归后续卡（L-M1）
  - 导入路径（src/application/importing/referenced/**）写 profile；不扩 referenced/runtime.py（L-M2）
  - 旧证据按冻结参数重算、same-container 路径 profile 回填
  - src/application/sources/service.py、ports.py、src/bootstrap/core_assembly.py 任何改动（L-M3；如需须重新报 DSH 窄批）
  - wire/命令/错误码/能力/DTO 字段、v8 DDL/迁移、新依赖
  - C-17/C-15/C-08/ADJ-001/M2-C1 rev 2.13 任何字节
  - Host/.NET/App/UI、FEA-12/13/14 范围、真实用户数据/AppData/外部卷/回收站、push
---

# FEA-11-MATCH-1：页匹配 pixel profile 提取与旧库 fixture

> **状态：`done`（r1 approved → r2 最小返修 → r2 窄面 Review approved（P0/P1/P2=0）→ closeout；Owner=`fea12-dsim-impl`；delivery head `869b6d5d5`，实现+测试 head `e8b0b2db8`）。** r1 独立上下文 Review approved（P0/P1=0；P2×3/P3×7，报告 `doc/reviews/FEA-11-MATCH-1-r1.md`）；r2 已按 findings 最小返修：R1-01 改名不可比 counterpart → `ambiguous/incomparable`（保留 bind 可能）、R1-02 字节分支重复守卫判别测试可达、R1-03 全部证据日志按真实机器时间重生成并重签 pin，并同批处置 R1-04/R1-05/R1-06/R1-07/R1-08/R1-09/R1-10/R1-11；R1-12 属卡外登记后续。门禁（r2 tree）：`tests/fea11` **108 passed**、`test_source_match.py` **20 passed**、全量 **3203 passed / 10 skipped**、pins **18/18**、`check.ps1 -TaskPath` **PASS**、契约/schema/依赖/apps 零 diff、`.NET` NOT_RUN。r2 窄面 Review：`doc/reviews/FEA-11-MATCH-1-r2.md`（session `2658835c…`）**approved（P0/P1/P2=0；P3×3 已在本 closeout 处置）**；`integration_commit=869b6d5d5`。

## 来源与目标

- 承接链：`FEA-11`（`closed_with_limitations`）L-4「AC11-3：生产 scan 不写 pixel profile；旧库 fixture/独立 match 测试缺失」；r1 R-012 判据更强（生产路径 new entry 不写 pixel profile，pixel 匹配实际不可达）。用户 2026-11-05 授权启动。
- 冻结依据：`G:\CODEX\New Manga.workspace\FEA-11\scope-review\FEA-11-MATCH-1-scope.md`（独立只读 scope review）+ ZCode SCOPE-ADJ-2026-11-05 裁决（Lead 2026-11-05 下发；含每卡必改项）。
- 代码事实（基线 `604a2d343`）：`src/application/sources/scanner.py:501-510` 候选 entry 的 pixel 列恒 `None`、`decoder_name/version` 恒空、`decoder_params_json` 恒 `"{}"`；`scanner.py:517-542` 仅在旧行已有 `pixel_digest` 时构造 `PixelProfile`；`scanner.py:545-555` 对 JSON **字符串字面量**做 `json.dumps` 再哈希（双重编码缺陷）；`matcher.py:38-45` 可比性只比 algorithm/decoder/version/params（缺 W/H/orientation）；`matcher.py:115-144` 重复检测不含 `pixel_digest`；`matcher.py:161-178`、`299-311` counterpart-less 重复成员产出非法 `DiffItem`（ambiguous 要求双侧非空，`model.py:590-592`）。
- 目标（一个可观察交付）：变更容器路径下，scan 对可解码 entry 产出**完整、可跨版本比较**的 `pixel-digest/1` profile 并经 apply 持久化；旧证据缺失/不可比/重复时**诚实降级**且 scan 输出始终可被 plan 校验接受；真实 v7 库（生产迁移 + 真实导入）作 fixture 的独立 match 测试通过；冻结契约/wire/DDL 零漂移。

## Scope（冻结）

### In（本卡写域与验收边界）

| # | 冻结内容 | 落点 |
|---|---|---|
| I1 | 变更容器路径的 new entry pixel profile 生产：`pixel-digest/1`、decoder 元数据、`width/height/orientation`、`params_digest`；取字节必须走既有严格校验读路径（先 grant/lease 后解码） | `scanner.py` |
| I2 | profile 可比性判据补全为 7 维：`algorithm + decoder + decoder_version + canonical params + width + height + orientation` 全等 | `matcher.py` |
| I3 | 重复 pixel occurrence → 整组 `ambiguous/duplicate_group`；禁 ordinal/locator 自动锚定 | `matcher.py` |
| I4 | 旧证据缺失/不可比的降级（`missing_old`/`incomparable`）+ counterpart-less 重复成员修正（旧侧无新对应→`missing/none`；新侧无旧对应→`added/none`）；保证每条 DiffItem 满足 C-17 §5.3 非空约束 | `matcher.py`、`model.py`（仅既有字段/组合守卫） |
| I5 | 生产 v7 fixture + 独立 match 测试：`migrations[:7]` 建 v7 → 真实 FEA-09 导入 → 迁 v8 → scan/match；`tests/fea11/test_source_match.py` | `tests/fea11/**` |
| I6 | 门禁与证据：pins 18/18、`check.ps1`、全量 pytest 基线 **3183 passed / 10 skipped**（DSH 2026-11-06 实跑定界；卡内旧数 3152 作废）、冻结契约零 diff、无新依赖、`apps/**` 零 diff | `verification/FEA-11-MATCH-1/**` |

### Out（明确排除，登记为 limitation）

PDF pixel profile（无 raster seam，L-M1）；导入路径写 profile（L-M2）；旧证据重算；same-container 回填；`service.py`/`ports.py`/`core_assembly.py` 任何改动（L-M3）；wire/命令/错误/能力/DTO/DDL/迁移；Host/.NET/App/UI；性能架构优化；`FEA-11-AC4-GAPS-1`/`FEA-11-SCAN-1` 的写域。

### 卡内冻结实现常量（契约未定义项；只写卡 + 测试，不写契约字节）

| # | 常量 | 冻结值 |
|---|---|---|
| C1 | 解码帧/缩放/色彩管理 | 仅首帧 `frame=0`；不缩放；不应用 ICC 变换；不做网络/外部查询 |
| C2 | 取字节路径 | 仅经既有严格校验读路径（`read_entry_bytes`/`read_verified_bytes`；先 grant/lease 后解码）；不得直接 `open()` 源路径、不得顺手缓存 |
| C3 | 解码预算 | 沿用 `src/application/importing/referenced/reader.py` 同源预算语义（`max_bytes`、`max_decode_bytes`、`max_entries`；先 header 尺寸预算再完整解码）；超预算 → 该 entry `pixel=None` + 合法 `reason`，**scan 整体成功** |
| C4 | EXIF 转置归一化 | 与 `render_entry_png`（`reader.py:174-176`）同源约定：`ImageOps.exif_transpose` 后再取像素；EXIF 1–8（含镜像 2/4/5/7）按各自转换处理；缺失 tag 视为 1；非法 9/0/错误类型不猜测 → `pixel=None` + `reason=unsupported` |
| C5 | 尺寸与方向 | `width/height` = **转置后最终像素栅格**尺寸（均 > 0）；`orientation` 恒记 **1**（表示输出已正向，不是原始 EXIF tag）；EXIF 2/4/5/7/9 经转置消除；落库/枚举仍只允许 `1/3/6/8`（`schema.py` CHECK） |
| C6 | RGB 归一 | 8-bit RGB、逐行、无行 padding；非 RGB/RGBA 先按 renderer 同源规则转 RGB；含**非全不透明** alpha（RGBA 或调色板透明度）首版不产 profile → `pixel=None` + `reason=unsupported`（L-M7） |
| C7 | `pixel_digest` | `sha256(ASCII(f"{W}x{H}") + b"\x00" + RGB_bytes)`，小写 hex；禁止哈希 PNG/JPEG 编码字节；禁止交换 W/H 而不变换像素 |
| C8 | `params` canonical | `decoder_params_json` 必须是 canonical JSON 对象字符串：`json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False, allow_nan=False)`；比对时先解析为对象再 canonical 比较（`_profiles_comparable` 不得比较原始字符串字面量）；`params_digest = sha256(canonical_json.encode("utf-8")).hexdigest()`；**修复 `scanner.py:545-555` 的 JSON 字符串双重编码**。冻结 params 对象：`{"alpha":"opaque-only","color_management":"none","exif_transpose":true,"frame":0,"mode":"RGB","pillow_version":"12.3.0","profile":"fea11-match-rgb/1"}`（Pillow pin 见 `requirements.txt:12`）；升级 Pillow 必须改 decoder 侧常量，不得静默沿用旧 digest 判可比 |
| C9 | decoder 标识 | `decoder="referenced-import"`、`decoder_version="1"`（**DSH 2026-11-06 裁决修正**：原卡值 `referenced-import/1` 含 `/`，违反冻结 C-17 §5.2 `PixelProfile.decoder! ID` 与 §5 类型表「ID=非空不含路径/控制字符 string(1..128)」；`model.py::_ID_RE` 实测拒绝。改为「解码器名 + 版本」两个合法 ID；属**卡级常量更正，不改冻结契约字节**） |
| C10 | `EntryEvidence.reason` 映射 | 闭集沿用 C-17 §5.2（`encrypted｜unsupported｜missing_evidence｜incomparable`，`model.py:440-445`），不新增 `budget` 枚举。生产映射：确认加密→`encrypted`；不支持格式/损坏解码/非法 EXIF/不可表示的透明 profile→`unsupported`；解码预算超限→`unsupported`；`content_digest` 缺失→`missing_evidence`。`reason` 与 `DiffItem.evidence`、`SourceObservation.reason_code` 是不同层，不得混填 |
| C11 | 降级边界 | 仅 **profile 提取**失败允许有限诊断；grant/lease/identity/digest 校验失败、容器扫描失败继续 typed 拒绝，**禁止 catch-all 吞掉授权/完整性错误**；不完整目标不得凭 add/bind 确认内容变更（C-17 `:274`） |
| C12 | 提取范围 | 只在**容器已变化**（`same_container=False`）路径对 new candidate entries 提取；同容器路径复用已提交行、不重解码；PDF 不在提取范围 |

## Acceptance Criteria

- [x] **AC-M1 生产 profile 提取、持久化与降级** <<MET>>
  - 变更容器路径下每个可解码 entry 产出完整 `PixelProfile`：`algorithm='pixel-digest/1'`、`decoder='referenced-import'`、`decoder_version='1'`、`params_digest=sha256(canonical params JSON)`、`width/height>0`、`orientation=1`、`pixel_digest=sha256("WxH\0"+RGB)`；字段集合与 C-17 §5.2 `PixelProfile`（`:241`）逐项一致。
  - 独立复算：测试独立用 Pillow 按 C1–C7 复算同一约定下的 `sha256("WxH\0"+RGB)` 并比对，另加 1 个硬编码 golden；使用**非方形、非对称**图（如 4×3 / 5×2）覆盖 EXIF 无 tag/1–8/9；镜像 2/4/5/7 必须真正镜像，不得仅旋转或丢 tag。
  - `params` canonical：对象键序/空白等价输入得到同一 digest；非法/未知 params 不得伪装成 `{}`；修复双重编码后 golden 从“字符串字面量哈希”变为“canonical 对象哈希”。
  - 持久化：完整 apply 后 `source_entries` 行带非空 `pixel_digest/pixel_digest_algorithm/width/height/orientation/decoder_name/decoder_version/decoder_params_json`（列已存在，`schema.py:667-695`），且 `decoder_params_json` 与 live candidate 的 canonical params 一致。
  - 降级：解码失败/预算超限/加密/缺失 `content_digest` → 该 entry `pixel=None` + C10 合法 `reason`；scan 不抛异常，totals 仍等于明细；scan 零 DB 写（前后 **sqlite_master 全表**快照相等，R1-05）。**R1-09 口径**：`encrypted` 目前仅 `_reason_for_import_error` 映射层单测，zip 加密成员扫描级端到端未构造（容器级 typed 拒绝可能先行拦截），不声称端到端已证。
  - 负测：有限诊断成功 ≠ 可发布 healthy——不完整目标不得凭 add/bind 确认内容变更（C-17 `:274`）。
- [x] **AC-M2 可比性（C-17 §7.3 第 2 行）** <<MET>>
  - `_profiles_comparable` 扩展为 7 维全等（algorithm/decoder/decoder_version/canonical params/width/height/orientation）；
  - `unique_pixel` 仅在「该像素证据在两侧各恰好 1 次」且 7 维可比时成立；否则不得保续；
  - `same_content` 关系成立条件在测试中断言（字节同一，或 profile 全等且坐标等价）；`_publication_relation` 的两条分支（真 pixel 路径 geometry 相等、唯一字节路径 `old_geometry=(None,None)` 兜底）都必须断言 relation 值。
  - 判别力：构造同 `pixel_digest`、同 W/H、但 `orientation` 不同（或 `decoder_version`/params/algorithm/decoder 不同）的旧行 → 改前判 `unique_pixel`，改后必须 `ambiguous/incomparable`。
- [x] **AC-M3 重复 pixel occurrence → 整组待确认（C-17 §7.3 第 3 行）** <<MET>>
  - occurrence 统计纳入 `pixel_digest`（与 `content_digest`/`locator` 同口径、按侧独立）；任一侧 ≥2 即整组 `ambiguous/duplicate_group`；禁止 ordinal/locator 自动锚定；唯一字节分支也不得绕过重复 pixel 组。
  - 组内成员不得自动 keep/bind；决策只允许 `bind`/`defer`；`defer` 不发布新 binding，旧 binding 保持原状态（本卡装置为 `healthy`，R1-11 文案统一）；PageId/人工 revision/Lock/进度/保护零变化（ADJ-001 §4、C-17 §5.3 `:270`）。
  - 覆盖 1:2、2:1、重名与同像素交叠、每个 occurrence 保留；所有输出通过 plan 校验；totals=最终 diff（含 scanner 对未绑定旧项的过滤）。
- [x] **AC-M4 旧证据缺失/不可比降级 + counterpart-less 修正（C-17 §7.3 第 4 行）** <<MET>>
  - 旧行无 profile（含 v7 形态）或 profile 不可比 → `ambiguous` + `missing_old`/`incomparable`；不得 `unique_pixel`；无完整可比证据时不得输出 `changed/direct`（`changed` 是“两侧完整可比且像素不同”的确定性断言）。
  - 唯一允许的“无需重算等价”：唯一 `content_digest` 相等（字节同一 ⇒ 像素同一）→ `unique_pixel`；且必须先排除重复组并验证坐标关系。
  - **counterpart-less 修正**：真正无跨侧候选时，旧侧重复成员→`missing/none`、新侧重复成员→`added/none`；不得保留 `duplicate_group` evidence 配单侧空（validator 要求其 classification=ambiguous，而 ambiguous 必须双侧非空）；“贪心配对后未占用”不等于“无对应”，1:N/N:1/交叠重复组仍整组待确认。
  - 禁止从新图伪造旧证据：不写旧版本行、不补旧 profile、不把 `missing_old` 提升为 `unchanged`。
  - 判别力：真实 v7 行（首个 bound entry 有 W/H、`pixel=NULL`；其余 entry 皆 NULL）在新容器字节已变 → 改前对带 W/H 那条判 `changed/direct`，改后必须 `ambiguous/missing_old`；字节同一成员仍 `unique_pixel`（防回归）；PDF 容器变化不得自动 `unique_pixel`/按 ordinal 保续。
  - **R1-01 边界**：旧 profile 存在但不可比、同一像素 occurrence 位于**不同 locator**（容器重打包改名 + Pillow/decoder/params 变更）时，必须 `ambiguous/incomparable`（双侧非空，可 `bind` 保留 PageId），不得 `missing+added`，也不得伪造旧证据；orientation/params/decoder_version 三种维度均有判别测试。
  - totals 语义变化显式登记（见「预期行为变更」）。
- [x] **AC-M5 生产 v7 真实导入 fixture + 独立 match 测试** <<MET>>
  - fixture 由**生产路径**生成：`MigrationRunner(conn, default_migrations()[:7])` 建 v7 → 真实 `ReferencedImportPlanner`/`ReferencedImportRuntime` 导入真实 zip → 迁 v8 → scan/match；不得用 `conftest.add_source_tree` 手写行替代“真实导入”。
  - 断言旧行形态诚实：`pixel_digest IS NULL`、`pixel_digest_algorithm IS NULL`、非首个导入页 entry 的 `width/height IS NULL`；bound entry 会写 `DECODER_NAME`（`runtime.py:864`）——**不得断言所有 `decoder_name` 为空**。
  - `tests/fea11/test_source_match.py` 至少含：①纯 matcher 单测（rows in / classified pairs out，无 DB/无文件）；②scan 级集成（真实 zip + 真实 HMAC grant + 真实严格读）；③scan 只读（scan 前后 DB 全表快照相等）；④两代 resync（导入后第二代起像素匹配可达）；⑤真实 apply 从 live candidate 保留非空 canonical params，以及 scan 过期/丢失时 apply 以 `SOURCE_PLAN_STALE`（cause=expired）typed 失败、零内容/绑定/profile/operation/publication 提交（R1-07）。
  - fixture 落隔离根 `G:/CODEX/New Manga.workspace/FEA-11-MATCH-1/`（或 conftest 既有隔离根），不提交二进制 DB，不复写 tracked `verification/FEA-09/**`。
- [x] **AC-M6 契约/门禁零漂移** <<MET>>
  - 无新命令/错误码/能力/DTO 字段；M2-C1 rev 2.13 NO_INCREMENT（不改 `PROTOCOL_MAJOR/MINOR`）。
  - C-17/C-15/C-08/ADJ-001 字节零 diff；`verify_pins.ps1` **18/18**；`check.ps1`（默认与 `-TaskPath`）PASS。
  - pytest 全量不低于 **3183 passed / 10 skipped**（DSH 2026-11-06 于 base head `71e4b42b4` 实跑定界：`3183 passed, 10 skipped`，EXIT 0；卡内旧数 3152 作废；不得以旧卡数字代替实跑）；不得新增 skip。
  - `apps/**` 零 diff；无新依赖（Pillow `12.3.0` 已 pin）；冻结契约/`schema.py`/`apps` 的 `git diff --name-only` 为空；真实依赖/DDL 证据文件为 `requirements.txt`+`schema.py`+`migrator.py`（**仓库无 `pyproject.toml`**，R1-10 已移除该空条件）。
  - 证据落 `verification/FEA-11-MATCH-1/`（EV/MATRIX/日志/命令 EXIT）。

## 允许修改范围

frontmatter `allowed_paths` 为准（`evidence_dir` 已显式列入）：

- 生产：`src/application/sources/scanner.py`（profile 提取、reason 映射、params canonical 化）、`src/application/sources/matcher.py`（可比性、重复组、counterpart-less、配对优先序）、`src/application/sources/model.py`（**仅**既有字段/组合守卫，不新增 DTO/字段）。
- 测试：新增 `tests/fea11/test_source_match.py`；`tests/fea11/fixtures/**`（仅小型文本 fixture）；**W1 窄批**：`tests/fea11/test_source_scan.py` 仅该用例期望值 + docstring（约 1–2 行）。
- 文档/证据：本卡、Handoff、Review、`verification/FEA-11-MATCH-1/**`。

## 禁止范围

- 不改 C-17/C-15/C-08/ADJ-001/M2-C1 任何字节；不新增命令/错误码/能力/DTO 字段。
- 不改 v1–v8 迁移 SQL/checksum、`schema.py`、任何 DDL。
- 不旁路 grant/lease/identity 读源；不直接 `open()` 源路径；scan 期间不得写 DB/缓存/持久化 profile。
- 不得从新图伪造旧证据（不写旧版本行、不补旧 profile、不把 `missing_old` 提升为 `unchanged`）。
- 不得按 ordinal/locator 自动锚定重复 occurrence，不得自动搬运人工成果；不得放宽 `model.py` 的双侧非空约束。
- 不扩 `service.py`/`ports.py`/`core_assembly.py`/`referenced/**`；不触碰 `FEA-11-AC4-GAPS-1`/`FEA-11-SCAN-1` 写域。
- 不删测试/放宽断言制造通过；不把 `skipped` 计入 passed；不引用旧卡数字替代释放日实跑。
- 不改 `apps/**`、治理指针（`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md` 由 Lead 维护）；不自审；不 push；不触碰真实用户数据/AppData/外部卷/回收站。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC-M1 profile 提取/持久化/降级 | `C:/Python314/python.exe -m pytest tests/fea11/test_source_match.py -q -p no:cacheprovider`（独立复算 + golden + apply 持久化 + 降级） | 隔离 fixture；Pillow 12.3.0 | **PASS**（20 passed，EXIT 0） | `verification/FEA-11-MATCH-1/{AC-MATRIX.md,EV.md,logs/pytest-match.log}` |
| AC-M2 可比性 | 同上（参数化 7 维 + scan 级 1 例 + relation 断言） | 纯单测 + 真实 zip | **PASS** | `logs/pytest-match.log`、`AC-MATRIX.md` |
| AC-M3 重复组 | 同上（1:2/2:1/重名/同像素交叠 + scan→plan 全链） | 隔离 fixture | **PASS** | `logs/pytest-match.log`、`AC-MATRIX.md` |
| AC-M4 降级/counterpart-less | 同上（真实 v7 fixture 全链 + 单测矩阵） | 生产 v7 + 真实导入 | **PASS** | `logs/pytest-match.log`、`AC-MATRIX.md` |
| AC-M5 真实 v7 fixture/只读 | 同上（旧行形态查询 + DB 全表快照 + 两代 resync + scan 丢失零提交） | 隔离 root（conftest 既有 `workspace/FEA-11/fixtures`）；生产 v7 | **PASS** | `logs/pytest-match.log`、`logs/pytest-fea11.log`（108 passed） |
| AC-M6 门禁 | `pytest tests/fea11 -q`；`pytest tests -q -p no:warnings --tb=no`；`check.ps1`（含 `-TaskPath`）；`verify_pins.ps1`；`git diff --name-only <base>..<head> -- doc/plan doc/contracts src/infrastructure/sqlite/schema.py src/infrastructure/sqlite/migrator.py requirements.txt apps` | 仓库根；释放日基线实跑 | **PASS**：fea11 **108 passed**（R2-02 修正）；全量 **3203 passed / 10 skipped**；check 见 `logs/gates.log`；pins 18/18；零 diff | `verification/FEA-11-MATCH-1/{EV.md,changed-files.txt,logs/*.log}` |

## 预期行为变更（Review 不判回归）

1. **W1（已批准窄批）**：`tests/fea11/test_source_scan.py:160` 现断言 `scan["totals"]["changed"] == 1`；AC-M4 收紧后该用例必须改为：保留 `content_digest` 变化与 `unchanged == 0`，新增 `changed == 0`、`ambiguous == 1`、对应 `evidence == "missing_old"`，并同步 docstring（约 1–2 行）。
2. **totals 语义**：A2（旧 pixel 缺失但 W/H 存在）由 `changed` 改判 `missing_old`；A5（counterpart-less 重复成员）由非法 ambiguous 改判 `missing`/`added`。两处改变用户可见 totals，按 C-17 §5.3 收敛，Review 不判回归。
3. **首次 resync 仍降级（L-M2）**：导入路径不写 profile，字节改变且缺旧 profile 的**首次** resync 不能自动像素匹配；pixel 匹配自第二代起可达。卡面不得宣称“旧库也可自动匹配”。
4. **PDF 不承接**：不得宣称承接 AC11-3 的“PDF 插页”或“PDF 必然全 missing + 全 added”；PDF 容器变化按诚实待确认处理（L-M1）。
5. **AC-M4 收紧的夹具影响（DSH 2026-11-06 窄批 W1b）**：真实 **W/H-only 旧 entry**（v7 形态，`pixel=NULL`）由 `changed/direct` 改判 `ambiguous/missing_old`——这是生产语义变化，仅影响真实 W/H-only 旧证据。既有测试夹具（`tests/fea11/test_source_sync.py::_seed_two_page_source(legacy_v7_evidence=False)`、`test_source_relink.py::_seed`）原先把 W/H 近似为“完整证据”属**夹具事实错误**；W1b 只在各自本地 seed helper 内为旧 entry 补**真实完整 pixel profile**（同一 png 字节按冻结参数算 W/H/digest/decoder/params canonical，`UPDATE source_entries`），**不再有生产语义变化**、**未放宽任何断言**；`test_source_sync_storage.py` 经共享 helper 自动恢复。`tests/fea11/test_source_scan.py` 的 W1 用例则是真实 W/H-only 场景，期望按 AC-M4 改为 `ambiguous/missing_old`。
6. **R1-01 边界修复（r2）**：旧 profile 不可比且同一像素 occurrence 跨 locator（改名/重排 + Pillow/params/decoder 变更）由 `missing+added` 改判 `ambiguous/incomparable`（双侧非空、可 bind 保留 PageId），不伪造证据；本卡装置下无用户可见 regression，属 AC-M4 口径补全。

## 依赖、风险与阻塞

- 硬依赖：`FEA-11-PREREQ-1`（C-17 v1.0 FROZEN、v8 DDL 冻结）。前置完成态：`FEA-11`（closed_with_limitations，L-4）、`FEA-11-LINEAGE-1`（done，`same_content` 读侧等价已闭合，本卡不写 lineage）。
- 并行边界：`FEA-11-SCAN-1`、`FEA-11-AC4-GAPS-1` 写域不重叠；本卡不得顺手改调度/CAS 证据。`FEA-11-HOST-AUTH-1` 零 diff。
- 主要风险：
  - R1 解码语义未冻结 → 已由 C1–C9 卡内冻结 + 独立复算 + golden 约束；不得各实现一套 digest。
  - R2 性能：zip 场景每 entry 重读整容器 + 整文件 sha256（`reader.py:50-64`；`referenced/scanner.py:234-246`），scan TTL ≤ 300s（`scanner.py:32`）；超预算按 entry 降级并记录测量，不改架构。
  - R3 reason 无 budget 枚举 → 固定 `unsupported`（C10），不新增枚举、不抛错。
  - R4 EXIF 2/4/5/7/9 不可表示 → 转置归一化消除 + `orientation=1`（C5/L-M7）。
  - R5 PDF 退化 → OUT/L-M1，不宣称覆盖。
  - R6 counterpart-less 修正改变 totals → 显式登记（预期行为变更 #2）。
  - R7 W1 测试冲突 → 已批准窄批；禁止删测试/放宽断言。
  - R8 全量 pytest 可能改写 tracked `verification/FEA-09/logs/wire-redacted.ndjson`（既有 debt）→ 门禁脚本显式 `git checkout` 恢复并记录。
  - R9 alpha 透明图 → 首版不产 profile（L-M7），不宣称“所有可解码图必有 profile”。
- 阻塞解除标准：本卡 scope 已冻结 → Lead 释放（固定 base/Owner/Reviewer）→ 实施 → 证据齐备 → 独立上下文 Review（不得自审）→ DSH 集成 closeout。

## 残余 limitation（预登记 L-M1…L-M7）

- **L-M1**：PDF entry 不产出 pixel profile（缺 raster seam 与原始 RGB 端口）→ PDF 重同步不得宣称自动插页匹配；按待确认/不可验证处理，另卡。
- **L-M2**：导入路径（`referenced/runtime.py`）不写 profile → 字节改变且缺旧 profile 的首次 resync 不能自动像素匹配；pixel 匹配自第二代起可达。
- **L-M3**：`service.py::_entries_from_target` 重建 helper 存在潜在保真缺陷（丢弃 `decoder_params_json`/`size_bytes`）；按裁决所述 GC 触发链不可达（`take_live_scan` 缺失/过期即 `SOURCE_PLAN_STALE`），生产正常路径保留 live candidate。本卡不扩 `service.py`；若后续证明可达须重新申请窄批。
- **L-M4**：「按冻结参数重算旧证据」未实现（需旧字节 + 新 grant）。
- **L-M5**：无解码语义/预算的可观测诊断计数（如不做 stderr 计数则明确写“无”）。
- **L-M6**：性能未优化：zip 场景 O(n×容器大小) 读放；仅登记测量值，不改架构。
- **L-M7**：EXIF 2/4/5/7/9 经转置归一化后不再可区分；首版不支持含非全不透明 alpha 的图（`pixel=None`/`reason=unsupported`）；不宣称“所有可解码图必有 profile”。
- **卡外后续（R1-12，不修）**：非图片成员（如 CBZ 内 `ComicInfo.xml`）在 `scanned.entries` 中 `content_digest=None`，变更容器 apply 全量 INSERT 可能触发 `source_entries.content_digest NOT NULL`；base（`2d9a4a219`）已存在、不在本卡 allowed_paths，登记后续探针/修复卡。

## 交付与运行记录

- 交付日期：2026-11-06（Asia/Shanghai）；Owner=`fea12-dsim-impl`（DSH Agent Teams，Lead `lead`）；**未 push**。
- r1 commits：`7bd8efe47`（scanner/matcher 实现）、`2d61e43c3`（`test_source_match.py` 19 用例 + W1/W1b）、`b4ad109da`（C8 strict params）、`c12023ab6`（r1 卡/证据/Handoff）。
- **r1 独立上下文 Review approved（P0=0/P1=0；P2×3、P3×7）**：报告 `G:/CODEX/New Manga.workspace/FEA-11/review-match-1/FEA-11-MATCH-1-r1.md`（Lead 落盘 `doc/reviews/FEA-11-MATCH-1-r1.md`）。
- r2 commit：`e8b0b2db8`（R1-01 改名不可比降级 + R1-02 判别测试可达 + R1-04 死代码 + R1-05 全表快照 + R1-07 具体 code + R1-08 changed 守卫；R1-03 证据日志真实机器时间重生成并重签 pin；R1-09/R1-10/R1-11 文档口径；R1-12 卡外登记）。
- Handoff：`doc/handoffs/FEA-11-MATCH-1-handoff.md`（含 §0 r2 findings 处置表）。
- 实际测试（2026-11-06，tree=`e8b0b2db8`）：`tests/fea11` **108 passed**；`test_source_match.py` **20 passed**；全量 `pytest tests` **3203 passed / 10 skipped**（基线 3183/10，+20 新增，0 回归/0 新增 skip）；`verify_pins.ps1` **PASS 18/18**；`check.ps1 -TaskPath` **PASS (3 warnings)**；`doc/plan`/`doc/contracts`/`apps`/`schema.py`/`migrator.py`/`requirements.txt` 零 diff；`.NET` **NOT_RUN**（`apps/**` 零 diff）。
- 环境：Windows 11 / Python 3.14.6 / Pillow 12.3.0（既有 pin）/ SQLite v8。
- 遗留项：L-M1…L-M7（未变化）；R1-12 卡外后续（见残余 limitation 末尾）；R8 未发生（全量 pytest 未改写 tracked `verification/FEA-09/**`）。共享工作树另有**他卡**未提交 `apps/**` WIP，不属本卡、未 add。
- 最终由 DSH 填写 `integration_commit` 并改 done。

## Canonical Evidence

唯一当前证据（sha256 pin；文件均随本文档提交进入 Git）：

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-M1 | AC-M1/M2/M3/M4/M5 | `verification/FEA-11-MATCH-1/EV.md` | - | `5033409a819bd8faaeb8b5d154b08d0506e4c4998acc2e8fe2bfa86ba5aaed68` | CANONICAL |
| EV-M2 | AC-M1…M6 矩阵 | `verification/FEA-11-MATCH-1/AC-MATRIX.md` | - | `5a96600bf4b415ec47379465b0a5a8e610089a8b077e6e51f48699df3acc2e40` | CANONICAL |
| EV-M3 | 隔离测试 108 passed | `verification/FEA-11-MATCH-1/logs/pytest-fea11.log` | - | `04b61ce0044d2e6487cb5418db80653df82e8043c79c893b6c028ddf0345da35` | CANONICAL |
| EV-M4 | 本卡 20 passed | `verification/FEA-11-MATCH-1/logs/pytest-match.log` | - | `e5ba1d608deaf04b7b8347f7fc6fe708658a28896a089a5f2782ac26f2f782ee` | CANONICAL |
| EV-M5 | 全量 3203/10 | `verification/FEA-11-MATCH-1/logs/pytest-full.log` | - | `c750fa0e8965b375051c4d784eaf0a54781d63eff4f322e915c02715ed789c9f` | CANONICAL |
| EV-M6 | 基线 3183/10 | `verification/FEA-11-MATCH-1/logs/pytest-baseline.log` | - | `39802e47d34202e1e9545c7c4235f240b43907661e5956405f9b41044a9ed0f5` | CANONICAL |
| EV-M7 | pins 18/18 | `verification/FEA-11-MATCH-1/logs/verify-pins.log` | - | `1d914f736c97f83933e58584c6cb002f21792876017f84cb3530dbee804acf8a` | CANONICAL |
| EV-M8 | 零漂移 | `verification/FEA-11-MATCH-1/logs/static-diff.log` | - | `3b5927ff316ade17215cf0d4a10361f145eccf7bec91b706915ceede4b8fd581` | CANONICAL |
| EV-M9 | 变更清单 | `verification/FEA-11-MATCH-1/changed-files.txt` | - | `2b7bb65c1617239cdc9bfc12f9df2f3e2343219b4ec117d379fa5c680b84d66b` | CANONICAL |
| EV-M10 | check.ps1 PASS（R1-06：登记后复跑） | `verification/FEA-11-MATCH-1/logs/gates.log` | - | `09cae20fab4f29f6fe0448295d1a9e465bc317cb881ae0a9a9198280dd25bf63` | SOURCE_PIN |
| EV-R1-REVIEW | r1 独立复审（approved P0/P1=0） | doc/reviews/FEA-11-MATCH-1-r1.md | - | 3f88c269e0e729c54c0cacac8aec8ff0e2aae24583de0943f31d07b4b63224de | CANONICAL |
| EV-R2-REVIEW | r2 窄面复审（approved P0/P1/P2=0） | doc/reviews/FEA-11-MATCH-1-r2.md | - | f19f6c2c1d260235e027afdd6ff6cfd9986163bca74f6acf369775035792cfde | CANONICAL |

check.ps1 运行结果与门禁摘录见 `verification/FEA-11-MATCH-1/logs/gates.log`（命令/EXIT/输出；已以 `SOURCE_PIN` 登记在 EV-M10）。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main 工作树；本卡在 `main` 上层提交，未新建 worktree） | NOT_APPLICABLE | — | — | 未创建 |
| temp | `G:\CODEX\New Manga.workspace\FEA-11\fixtures`（pytest `tmp_path` + conftest 既有隔离根） | PRESERVE_REFERENCED | `G:\CODEX\New Manga.workspace\FEA-11\fixtures` | verification/FEA-11-MATCH-1/EV.md | pytest 自清理隔离根；保留不清理（无 tracked 文件写入、无独有产物）；真实 zip/v7 导入 fixture 已用 |
| evidence | `verification/FEA-11-MATCH-1/`（仓库内证据） | PRESERVE_REFERENCED | `verification/FEA-11-MATCH-1` | verification/FEA-11-MATCH-1/EV.md | Canonical Evidence 已登记（EV.md/AC-MATRIX/changed-files/logs）；原位保留不清理 |

## Closeout Record

- Closeout date / DSH：2026-11-06 / DSH（Lead/Architect/Integrator）。
- 终态：`done`；delivery_head / integration_commit = **`869b6d5d5`**（含证据/卡/Handoff；实现+测试 head `e8b0b2db8`；r1 交付 `c12023ab6`）。
- Review 链：r1 独立复审 approved（P0/P1=0；P2×3/P3×7）→ r2 最小返修（R1-01/02/03 + P3 同批）→ r2 窄面 **approved（P0/P1/P2=0；P3×3）**；Reviewer 均为 fresh subagent（session 见 frontmatter）。
- AC 定稿：**AC-M1…AC-M6 全 MET**；W1/W1b 窄批按 DSH 裁决落实（补真实 pixel profile，未放宽断言）；C9 常量经 DSH 裁决更正为 `decoder="referenced-import"` + `decoder_version="1"`（C-17 §5.2 ID 规则；契约字节零改）。
- 证据真实性：r2 全部 7 份日志按真实机器时间重生成、与 mtime 一致（Δ+0.88…+4.83s）、晚于代码提交早于 docs 提交；10 条 Canonical Evidence 复算 10/10 MATCH；gates.log 的 check 自指属不可避免（closeout 复跑记最终 PASS）。
- 残余风险/limitation：**L-M1** PDF 不产 pixel profile（PDF 插页不承接）；**L-M2** 导入路径不写 profile（首次 resync 不自动像素匹配，第二代起）；**L-M3** `service.py::_entries_from_target` 保真缺陷（未扩写域；live scan 丢失→typed `SOURCE_PLAN_STALE`）；**L-M4** 旧证据按冻结参数重算未实现；L-M5 无解码诊断计数；L-M6 性能未优化（成本未标定）；L-M7 EXIF 镜像不可区分/非全不透明 alpha 不产 profile/不宣称所有可解码图必有 profile；R1-12（非图片成员 `content_digest=None` 的 apply NOT NULL 风险）为卡外既有问题，登记后续；directory-source 重复内容不合并 occurrence（与 zip 同机制但无 folder-source 专项断言）。
- r2 Review P3 处置：**R2-01** 「40 表」更正为运行期 36 张用户表（迁移 SQL 40 条 CREATE 含 4 个 *_v5 重建临时表；测试注释 comment-only、无行为变化）；**R2-02** 本卡测试表 fea11 107→**108**；**R2-03** r1/r2 Review 报告已落盘 `doc/reviews/` 并回填 `reviewer`。
- **AC11-3 回填（FEA-11）**：`MET（带 limitation：L-M1 PDF 插页 / L-M4 旧证据重算；另注 folder-source 无专项断言）`；已在 FEA-11 卡 Closeout 补充回填。
- 删除、迁移、归档数量/字节数：0（`FEA-11\fixtures` 为 pytest 自清理隔离根，无提交二进制）。
- 当前指针清理：STATUS / Plan / TASK_LEDGER 已更新；本卡为终态，不进入 READY DAG。
