# SETTINGS-OPEN-A-1 独立 Review r2

- 审查者：`reviewer-settings-a`（独立 Review，非实现者）
- 审查对象：**commit `6a303a9d2c66f6ffbfee2aec6ebde359312a6b33`**（`fix(settings): repair batch-A review findings ...`）
  - 实际 parent：`fd31d0b8b83c656cbd3db5412c68f0652356afd2`（r1 实现 `87ae85a` + 两个 docs-only commit；产品代码与 `87ae85a` 相同）
  - 分支 `main`，未 push。收到提交通知时工作区干净；审查期间 Lead 在补 m6 逐分区 GUI 证据，工作区出现未跟踪的 `screenshots/08-ocr-saved.png`、`09-typeset-saved.png`、`10-typeset-panel-r2.png`（以及本报告 `review-r2.md`），属证据补录、不在 `6a303a9` 内（见 §5 R3）。
- 审查时间：2026-10-22 21:24–21:40 +08:00
- 审查方式：读取 `git diff 87ae85a 6a303a9`（27 个文件）、新增测试与证据；对 B1/M1 用真实 `RenderService._prepare_region` 与 Core 校验器做独立探针；在 commit 树上重跑全部验收命令（见 §3）。
- 复审基准：`review-r1.md` 的 2 blocker（B1/B2）+ 5 major（M1–M5）+ 6 minor + 3 nit。

## 1. 结论

**approved**（代码与测试层面；无 blocker / major 残留）。

r1 的 B1、B2、M1、M2、M3、M4、M5 与 m1/m2/m3/m5 均已按说明修复，独立测试和手动探针通过；m4 的治理检查已 PASS；m6 的逐分区 GUI 烟测仍由 Lead 在补（见 §5 R3）。合入/关闭前还需完成 §5 的 R1–R3 非代码事项（delivery pin、allowed_paths/治理更新、m6 证据），它们不改变本 commit 的代码合入判断。

## 2. r1 findings 复核

| r1 id | 状态 | 独立验证要点 |
|---|---|---|
| B1 blocker | **已修复** | `_merge_defaults(domain_style, style, defaults)` 用 RAW domain `TextStyle` 判断持久化；真实 `_prepare_region` 探针显示默认 Region 全部 inherit、持久化 Region 反向覆盖、无 typeset 保持历史行为；`tests/rendering/test_typeset_defaults_merge.py` 4 passed（旧实现证据 3 failed/1 passed）。详见 §2.1 |
| B2 blocker | **已修复** | `fill_color` 已从 Core 白名单/提取器/设计/前端类型/默认值/归一化/payload/面板彻底移除；Core 对 `fill_color` 写入返回 `INVALID_REQUEST`；typeset 三方键集均为 10 键。详见 §2.2 |
| M1 major | **已修复** | Core `typeset` 跨字段校验（auto=false 且 manual null → `INVALID_REQUEST`，不落库，已核 wire 测试）；前端保存按钮因内联错误禁用；全局 manual 模式探针成功渲染 24px。详见 §2.3 |
| M2 major | **已修复** | `text_align` 在 Core 白名单/提取器、前端类型/值域/下拉、设计表中均收窄为 `left \| center`；旧持久化 `start/right` 显示折叠为 left 且永不写回。详见 §2.3 |
| M3 major | **已解决** | M2-C1 §5.3 与 P15 §7 均加了 2026-10-22、授权来源、原表保留、wire/错误/幂等不变的增量修订注记，明确"按节收窄、未知 section 仍透传"。措辞足以消除"实现与冻结契约冲突"。详见 §2.4 |
| M4 major | **已修复** | Task/Handoff/core-report 的 `base_commit` 已统一为真实 `1fa2c3c58413b6bce972bd20fb044438d538d3d6`；`git rev-parse 6a303a9^` 一致。 |
| M5 major | **已修复** | 新增 `tests/rendering/test_typeset_defaults_merge.py`（4 项）直接断言 `RenderOp`/`LayoutRequest`；旧实现 3 failed 原始输出已入库 `core-r2-b1-old-impl-failure.txt`。 |
| m1 minor | **已修复** | 设计 §3.4 把 `manual_font_size` 统一为 `1–500`（`doc/design/SETTINGS_SECTION_SCHEMAS.md:79`），Core `settings_sections.py:85` 与前端 `sections.ts:350-351` 一致。 |
| m2 minor | **已修复** | `EditableSettingsSection = "ocr" \| "translate" \| "inpaint" \| "typeset" \| "sfx"`（`client.ts:71-84`）；`getSection/saveSection/useSettingsSection` 参数均为该 union；`client.p15.test.ts:207-240` 用运行时镜像 + `@ts-expect-error` 恢复守卫，`tsc --noEmit` 通过即生效。 |
| m3 minor | **已修复** | `tests/core/test_core_service_settings.py:220-221` 拒绝循环已含 `translate`。 |
| m4 minor | **已修复** | `tools/governance/check.ps1` → **PASS**（2 warnings：2 个非终态 Task、STATUS 达 80% 预算）；TASK_LEDGER/REBASELINE_PLAN/STATUS 已更新。 |
| m5 minor | **已修复** | 任务书验收主命令改为 `npm --prefix apps/desktop/frontend test`（`doc/tasks/SETTINGS-OPEN-A-1.md:76`）；`frontend-npm-test-raw.txt` 已重跑为 npm 通道 367 tests。 |
| m6 minor | **部分完成** | inpaint 保存+重启复查证据已在库（`gui-smoke.md:12-17`、`screenshots/07-restart-persisted.png`）；OCR/翻译/排版逐分区烟测仍未提供（Lead 说明在补）。见 §5 R3。 |

### 2.1 B1 独立验证（真实渲染 seam）

修复点：
- 调用点 `src/application/rendering/service.py:478`：`_merge_defaults(region.style, style, style_defaults)`；
- 合并实现 `src/application/rendering/service.py:677-719`：只有 domain `TextStyle` 的原始字段非空/非零（`:697/699/704/713`）才让 Region 覆盖 defaults；其余（包括 domain 无法表达的 `line_spacing/text_align/text_direction/font_size_offset`）取 defaults；
- `style_defaults=None` 时仍走历史 `from_domain` 路径（无合并）。

独立探针（真实 `RenderService._prepare_region`，非测试文件内的断言）：

```text
# defaults: text_color=#112233, stroke_enabled=False, stroke_color=#0000FF, stroke_width=4.0,
#           line_spacing=2.0, text_align=center, text_direction=vertical,
#           font_size_offset=-2, auto_font_size=True
DEFAULT REGION -> text_color #112233 | stroke_enabled False | stroke_color #0000FF |
                  stroke_width 4.0 | align center | dir TextDirection.VERTICAL |
                  font_size 24.0 | line_spacing 2.0
PERSISTED REGION (font/font_size/text_color/stroke pair) -> font Persisted Font |
                  text_color #ABCDEF | stroke_enabled True | stroke_color #123456 |
                  stroke_width 2.0 | align center | dir VERTICAL | font_size 30.0 | auto False
NO TYPESET -> text_color #000000 | stroke_width 0.0 | align start | font_size 26.0
```

- 回归测试 `tests/rendering/test_typeset_defaults_merge.py`（113/138/157/188 四个用例）单独运行 `4 passed in 0.07s`；旧实现证据 `core-r2-b1-old-impl-failure.txt` 为 `FFF.`（3 failed, 1 passed），失败信息与 r1 独立探针的旧行为一致（`stroke_enabled True / stroke_width 0.0 / align start`）。
- **partial typeset 语义**：实测"只保存 `text_color`"时，`typeset_style_defaults` 以 `RenderTextStyle` 代码默认补全缺省键，默认 Region 得到 `stroke_width=3.0/描边开/白描边`、`line_spacing=1.0`、`text_align=start`。这与设计 §3.4 新增段落（`doc/design/SETTINGS_SECTION_SCHEMAS.md:81-85`："Region 未持久化字段继承全局 typeset 默认；全局默认缺省时才落到代码常量"）一致；"未保存 typeset 时行为与历史逐字节一致"也已由 `test_without_defaults_the_historical_style_is_kept` 覆盖。副作用（只存文字颜色会启用 3px 描边）已被设计冻结，见 §5 R5 供产品侧知悉。

### 2.2 B2 独立验证（三方键集 = 10 键）

- Core 白名单 `src/bootstrap/settings_sections.py:72-84`：`text_color, stroke_enabled, stroke_color, stroke_width, line_spacing, text_align, text_direction, auto_font_size, font_size_offset, manual_font_size`（10）。
- 提取器 `src/infrastructure/providers/handlers.py:1045`：颜色循环只剩 `text_color/stroke_color`；`:1024` `_TYPESET_TEXT_ALIGNS` 同步收窄。
- 设计 `doc/design/SETTINGS_SECTION_SCHEMAS.md:69-79`：开放 10 行；`:85` 明确 `font_family`/`fill_color` 不开放且"若后续需要背景填充，须先实现真实消费者与测试"。
- 前端 `sections.ts:353-365` 的 `TypesetSettingsDraft` 10 字段；`TypesetSettingsPanel.tsx` 已无填充控件；测试断言 `typeset-fill-color` 不存在、保存 payload 恰为 10 键（`TypesetSettingsPanel.test.tsx:95,135`）。
- Core 探针：`validate_settings_section("typeset", {...,"fill_color":"#FFFFFF"})` → `REJECT: does not accept key 'fill_color'`；合法 10 键 payload 接受并规范化。
- 全仓 `fill_color` 残留仅测试中的"应被拒绝/不应映射"断言与 `RenderTextStyle` 旧字段（无消费者），无产品面。

### 2.3 M1/M2 独立验证

- **M1**：`settings_sections.py:127-141` 在规范化后检查 `auto_font_size is False and manual_font_size is None` → 抛 `SettingsSectionError`（消息含两字段名）。探针：`{"auto_font_size": false, "manual_font_size": null}` → REJECT；`false + 24` → OK；`true + null` → OK。wire 级测试 `test_settings_section_validation.py:391` 断言 `INVALID_REQUEST` 且 `pipeline_defaults.settings.get("typeset") is None`（不落库）。前端 `sections.ts:455-458` 同步报错，`TypesetSettingsPanel.test.tsx:243` 断言保存被阻断并显示内联错误；全局 manual 模式探针得到 `op.font_size=24.0, auto=False`（不再 render-blocking）。
- **M2**：Core `settings_sections.py:79` 只允许 `left|center`，探针 `right` → INVALID_REQUEST；提取器 `handlers.py:1024/1063` 同步；前端 `sections.ts:323/326/414` 类型/值域/归一化（`start|right` → `left`，永不写回），下拉仅两项；设计 `:75` 注明 `right` 未实现不开放。渲染器本身未改（`right` 不再可达），无需改 compositor。

### 2.4 M3 措辞判断

- `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:262`：明确"上述第 4 条的'透传'按节增量收窄，不整体推翻本节既有语义"，列出四节白名单、`INVALID_REQUEST`、不落库、未知 section 仍透传，且"wire 形状、错误码、宿主同步纪律与幂等语义均不变"。
- `doc/contracts/P15_SETTINGS_IPC_CONTRACT.md:272`：明确四节已在批次 A 冻结开放，其余分区仍未开放，历史两张表保留。
- 判断：**足以消除"commit 与冻结契约冲突"**——两份文档原文保留、新增注记带日期/授权来源/任务指针，且限定了变更边界（仅按节收窄、wire 不变）。§5 R4 只建议补一条 doc rev/revision-history 指针便于检索（不影响冲突结论）。

## 3. 独立测试原始结果（commit `6a303a9`）

| 命令 | 原始结果 | exit |
|---|---|---|
| `python -m pytest tests/core tests/pipeline tests/rendering -q` | `832 passed, 2 warnings in 51.22s` | 0 |
| `python -m pytest tests/core/test_settings_section_validation.py -q` | `100 passed in 1.31s` | 0 |
| `python -m pytest tests/rendering/test_typeset_defaults_merge.py -q` | `4 passed in 0.07s` | 0 |
| `npm --prefix apps/desktop/frontend test` | `Test Files 37 passed (37)` / `Tests 367 passed (367)`，Duration 3.59s | 0 |
| `cd apps/desktop/frontend && .\node_modules\.bin\tsc --noEmit` | 无输出 | 0 |
| `pwsh -NoProfile -File tools/governance/check.ps1`（只读） | `Governance check: PASS (2 warnings)`：2 个非终态 Task（WARN）；STATUS 2838 bytes/32 lines 达 80%（WARN） | 0 |

与 Lead 预期一致（832 / 37 files·367 / tsc 0）。r2 新增：`tests/core` 校验 91→100（+9）、`tests/rendering` 69→73（+4）、前端 364→367（+3）。

## 4. 范围核对（r2 commit，27 个文件）

| 分组 | 文件 | 是否在 `allowed_paths` |
|---|---|---|
| 前端 settings（6） | `TypesetSettingsPanel.tsx/.test.tsx`、`client.ts`、`client.p15.test.ts`、`sections.ts`、`useSettingsSection.ts` | 是 |
| Core（3） | `application/rendering/service.py`、`bootstrap/settings_sections.py`、`infrastructure/providers/handlers.py` | 是 |
| 测试（3） | `tests/core/test_settings_section_validation.py`、`tests/core/test_core_service_settings.py`、`tests/rendering/test_typeset_defaults_merge.py` | 是（r2 已把 `tests/rendering/**` 加入 allowed_paths） |
| 契约/设计/任务/Handoff/状态（9） | `doc/contracts/M2-C1_...`、`doc/contracts/P15_...`、`doc/design/SETTINGS_SECTION_SCHEMAS.md`、`doc/tasks/SETTINGS-OPEN-A-1.md`、`doc/handoffs/SETTINGS-OPEN-A-1-87ae85a.md`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md` + `gui-smoke.md` | contracts/design/task/handoff/STATUS 是；**`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md` 不在 allowed_paths**（见 §5 R2） |
| 证据（6） | `verification/SETTINGS-OPEN-A-1/{core-report.md, ui-report.md, core-r2-b1-old-impl-failure.txt, frontend-npm-test-raw.txt, review-r1.md, screenshots/07-restart-persisted.png}` | 是 |

- 无 Schema/migration、无依赖变更、无 Provider/Network/凭据/SFX wire 语义修改；`settings_update_section` 的 wire 形状与错误码未变（契约注记亦如此声明）。
- `doc/REBASELINE_PLAN.md`/`doc/TASK_LEDGER.md` 的内容正确（check PASS），但它们是 Lead/Integrator 的治理指针文件，未在 Task `allowed_paths` 中；建议将其加入 allowed_paths 或在本 Task/Handoff 明确记录"Lead 集成动作"。

## 5. 剩余 findings（不阻塞代码合入；合入/关闭前处理）

- **R1（minor，交付 pin/证据仍停在 r1）**：`doc/tasks/SETTINGS-OPEN-A-1.md:16` 仍 `delivery_head: 87ae85a...`（Handoff 头 `:6` 同）；`core-report.md:7/13/155` 仍写"r2 未 commit/工作区改动，HEAD 未移动"；Task `AC2`（`:54`）仍标"返修中"未勾、`AC5`（`:57`）未勾；测试表 `:74-79` 仍写"r2 待重跑/待补/待执行"；`REBASELINE_PLAN.md:26` / `STATUS.md:7` 仍写"返修 r2 中"。**合入/关闭前**应把 delivery pin 更新为 `6a303a9d2c66f6ffbfee2aec6ebde359312a6b33`（或显式记录 r1+r2 两个 commit），并刷新报告/表格/STATUS/Plan；否则 canonical 交付 pin 指向已被 r1 Review 否决的 `87ae85a`。
- **R2（minor，范围）**：r2 commit 修改 `doc/REBASELINE_PLAN.md` 与 `doc/TASK_LEDGER.md`，但二者不在 Task `allowed_paths`。内容/check 均正确；建议把这两个治理指针加入 allowed_paths（标注 Lead/Integrator 专属），或在 Task/Handoff 记录集成例外，避免下一次范围审查歧义。
- **R3（minor，m6 证据，审查期间仍在进行）**：`6a303a9` 内的 `gui-smoke.md` 只有 inpaint（保存 + 重启回读）；审查期间（约 21:27–21:32）工作区已出现**未提交**证据 `screenshots/08-ocr-saved.png`、`09-typeset-saved.png`、`10-typeset-panel-r2.png`，我核对了 dev-preview `library.db` 的 `pipeline_defaults.settings_json`：已实际落库 `ocr.script=korean` 与 10 键 `typeset` 段（`auto_font_size=true, manual_font_size=null, stroke_enabled=false, ...`），说明 OCR/排版逐分区保存已执行；但 `gui-smoke.md` 文本与截图**都还没 commit**，翻译参数分区尚未见到。关闭前请把逐分区证据落 commit 并更新 `gui-smoke.md`（或按 Task 规则明确 NOT_RUN）。typeset 的页面渲染效果仍以 `tests/rendering` 回归为准（Lead 已接受不做真实页面 E2E）。
- **R4（nit，契约可检索性）**：M3 的增量修订只内嵌在 §5.3/P15 §7 正文，M2-C1 文档 rev 2.11 / P15 rev 2.7 的 revision header 未加指针；建议补一行 revision-history 便于后人定位（不影响冲突消除结论）。
- **R5（nit，partial typeset 可见副作用）**：只保存 `text_color` 时，未持久化 stroke 的 Region 会从历史 `stroke_width=0` 变为代码默认 `3.0`（白色描边开）。设计 §3.4 `:81-85` 已冻结该语义（可解释为"继承全局默认"），但属于用户可见变化；建议后续在 UI 文案或设计备注中说明，或批次 B 再评估。
- **R6（nit，stroke 组语义）**：`_merge_defaults` 在 Region 持久化了 `stroke_width/stroke_color` 时整组取合成值（`stroke_enabled=True`），因此全局 `typeset.stroke_enabled=false` 不会关闭这类 Region 的描边；设计 `:81` 的持久化标记只列 stroke 对，未明说该组语义。当前新架构没有 Region 级样式写入面，影响低；建议在设计 §3.4 补一句组语义。
- **R7（nit，证据可读性）**：`core-r2-b1-old-impl-failure.txt` 中 `D03 ��11.4` 有控制台编码乱码（内容与断言仍可读）；`frontend-tsc-raw.txt` 在 r2 未重录（文件为空，tsc 无输出，等价），ui-report 声称"r2 重跑"与文件状态不完全对应；可在关闭时顺手修正。
- **R8（nit，预算）**：`check.ps1` PASS 但 `doc/STATUS.md` 已达 80% 预算（2838/3200 bytes）；后续更新注意不要越过 3200。

## 6. 亲自验证 / NOT_RUN

**亲自验证（已做）**
- 通读 r2 commit 全部源码/测试/设计/契约/报告 diff；核对 `git diff 87ae85a 6a303a9`（27 文件）与 `git show --stat`。
- **B1**：真实 `RenderService._prepare_region` 探针（默认 Region 全字段继承、持久化 Region 反向覆盖、partial typeset、无 typeset 历史行为）；`test_typeset_defaults_merge.py` 4 passed；旧实现失败证据内容核对（未重跑旧实现，见 NOT_RUN）。
- **B2**：Core 校验器探针（fill_color 拒绝）；提取器/设计/前端类型与 payload 读码；10 键三方一致；全仓 `fill_color` 残留检查。
- **M1/M2**：Core 校验器探针（跨字段 4 组合、`right` 拒绝）；wire 测试读码；真实 `_prepare_region` 的全局 manual 模式探针（24px、auto=False、无 skip）。
- **M3**：两份契约注记原文与边界逐句读；判断足以消除冲突。
- **M4**：`base_commit` 三处 + `git rev-parse 6a303a9^` 一致。
- **m1–m5**：设计 1–500、前端 union + `@ts-expect-error`（`tsc` 通过即证明守卫有效）、translate 拒绝循环、npm 主命令、`check.ps1` PASS 全部实测/读码。
- **测试**：§3 全部命令在 commit 树重跑并记录原始计数；另确认 r2 新增测试数（+9/+4/+3）。
- 范围：27 文件逐一映射 allowed_paths；确认无 Schema/migration/依赖/其他分区改动。

**NOT_RUN / 未独立验证**
- 旧实现 3 failed 的**现场重跑**（需要临时还原 `_merge_defaults` 或改产品代码，Review 不做；仅核对已入库原始输出，其失败断言与 r1 独立探针一致）。
- OCR/翻译/排版逐分区 GUI 烟测与重启复查的**提交后证据**：审查期间已看到未提交的 OCR/排版截图（08/09/10）与 DB 中实际落库的 ocr/typeset 段，但翻译参数分区未见到、`gui-smoke.md` 未更新、这些文件均未 commit（见 R3）。
- 真实 Tauri 应用中的页面渲染 E2E（Lead 明确不做；以 `tests/rendering` 回归为准）。
- Rust/Tauri 构建与测试（本次 diff 无 Rust 改动；未运行）。
- 契约文档的长期生效（需要 Codex/契约 owner 认可；本 Review 只判断措辞已消除冲突）。
- `tests/providers` 的 2 个既有 env 失败（r1 已确认与本 diff 无关，本次未重跑）。

## 7. 审查快照与合入前 checklist

- 审查 commit：`6a303a9d2c66f6ffbfee2aec6ebde359312a6b33`；parent `fd31d0b8b83c656cbd3db5412c68f0652356afd2`（代码基线 `87ae85a`）。
- 关键文件 SHA-256（commit 树）：
  - `src/application/rendering/service.py` `D8FAECDBE6CD404439C5442E150EBA4DE6F07A2951A60749F2C65A0333A5A5C4`
  - `src/bootstrap/settings_sections.py` `B49417D9DB7CDB001D0406A4A6133B390BD44CEE1FAF955B51641DBCA99C03D6`
  - `src/infrastructure/providers/handlers.py` `52511ADB1FD28226284195FC8586DA3CEA0F664CB4AE10A03B09CF3DC3A8B2B2`
  - `tests/rendering/test_typeset_defaults_merge.py` `EA08DBE622860281B880CBB12B6B20342F9489FBCBF62CE7BC3BF05EEA4BD0E3`
  - `apps/desktop/frontend/src/settings/sections.ts` `AB7D1645F8601D6DB4C5C8B11B5C38021E3D7ED4D9DBC4D76AB6A8B68F08EC16`
  - `apps/desktop/frontend/src/settings/client.ts` `21E1E5DEB384D36D16E50E3F51F94F99030239DBDE35EDF331FFC3CD09E30386`
  - `doc/design/SETTINGS_SECTION_SCHEMAS.md` `22647465ECC0FEBEA3F94F2DFBD9B3968F688FDC8B0F939EF0281BEE039665AE`
- 合入/关闭前 checklist：
  1. [ ] 更新 `delivery_head`/Handoff/报告/STATUS/Plan 到 `6a303a9`（或显式记录 r1+r2），刷新 Task 测试表与 AC2/AC5（R1）。
  2. [ ] 处理 `doc/REBASELINE_PLAN.md`/`TASK_LEDGER.md` 的 allowed_paths/集成例外记录（R2）。
  3. [ ] 补齐 OCR/翻译/排版逐分区 GUI 烟测证据，或按 Task 规则明确 NOT_RUN（R3）。
  4. [ ] 可选：补 M2-C1/P15 revision-history 指针（R4）、设计 §3.4 stroke 组语义与 partial 副作用说明（R5/R6）。
- 结论不变项：代码层无 blocker/major；r2 提交可以直接进入集成，集成目标应为 `6a303a9`（不要使用 r1 的 `87ae85a`）。
