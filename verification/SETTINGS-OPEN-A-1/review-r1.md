# SETTINGS-OPEN-A-1 独立 Review r1

- 审查者：`reviewer-settings-a`（独立 Review，非实现者；未参与本 Task 实现）
- 审查对象：**实现 commit `87ae85a678880bff840ac77b53f2700e586ad95c`**
  （parent `1fa2c3c58413b6bce972bd20fb044438d538d3d6`，分支 `main`，未 push）。
  审查期间 Lead 又提交了纯文档/证据 commit `6160a237aad7e74c5a32bed8bdde3b6c73fb94f4`（`docs(settings): record batch-A GUI smoke restart check and handoff`）；`git diff --stat 87ae85a 6160a` 仅新增 `doc/handoffs/SETTINGS-OPEN-A-1-87ae85a.md` 与 `screenshots/07-restart-persisted.png`，**产品代码两 commit 相同**，因此 §2 的代码结论对 `6160a` 同样成立；本 Review 以 `87ae85a` 为实现基点。
- 审查时间：2026-10-22 21:05–21:20 +08:00
- 审查方式：先在工作区完成静态审查并记录关键文件 SHA-256；收到 Lead 的提交通知后，在 `87ae85a` 上复核——关键源文件 SHA-256 与审查快照一致（`settings_sections.py`、`core_service.py`、`rendering/service.py`、`handlers.py`、`sqlite/pipeline.py`、`sections.ts`、`client.ts`、`test_settings_section_validation.py`），blocker 代码按 `git show 87ae85a:<path>` 逐行确认；全部测试在 `87ae85a` 树上重跑（见 §3），两 commit 之间无产品代码差异。
- 已读输入：`doc/tasks/SETTINGS-OPEN-A-1.md`、`doc/design/SETTINGS_SECTION_SCHEMAS.md`、`doc/contracts/P15_SETTINGS_IPC_CONTRACT.md` §7、`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` §5.3、`verification/SETTINGS-OPEN-A-1/core-report.md`、`ui-report.md`、`gui-smoke.md`、全部新增/修改的源码、测试与设计/任务文件（raw 日志与截图抽样核对），以及 `git diff --name-status 87ae85a^ 87ae85a` 的范围清单。

## 1. 结论

**changes_requested**

不能进入 commit/集成（当前已固定 commit `87ae85a`，但需返修后重新 Review）。原因：AC2 的"两条渲染路径使用新默认值"在实现上不成立——`typeset` 11 个键中 7 个会被 `_merge_defaults` 静默丢弃（blocker B1）；`typeset.fill_color` 全链路无消费者，是可保存但永远不生效的假控件，直接违反设计 §2.4"不伪造"（blocker B2）。其余 major 见 §2（跨字段组合可让所有渲染失败、`text_align=right` 无渲染实现、冻结契约未同步、证据 pin 无效等）。

A/C/D/F 四轴摘要：A（白名单/值域/未知键/不落库/规范化）实现与测试基本正确，缺陷在"值写入后是否真的被消费"（B1/B2）；C（`_redact` 精确豁免）验证通过，未发现 Secret/路径新暴露面；D（前端 payload 与 Core 白名单）逐键一致，六个仍禁用分区断言保留，无 mock 数据，但 `fill_color` 是假控件；F（范围）commit 40 个文件均在 `allowed_paths` 内，pnpm 环境产物未进入 commit，但契约/治理指针与证据 pin 有缺口。

Findings 计数：blocker ×2、major ×5、minor ×6、nit ×3（明细见 §2）。

## 2. Findings

### 2.1 汇总

| id | severity | 标题 | 位置 |
|---|---|---|---|
| B1 | **blocker** | `typeset` 默认样式在两条渲染路径上大部分不生效（`_merge_defaults` 优先级反了） | `src/application/rendering/service.py:473-475,674-705` |
| B2 | **blocker** | `typeset.fill_color` 无任何消费点（假控件），违反设计 §2.4 | `src/bootstrap/settings_sections.py:74`；`src/ports/rendering/ports.py:83-99` |
| M1 | major | 合法组合 `auto_font_size=false` + `manual_font_size=null` 会让所有区域渲染跳过/整页重渲染失败 | `src/bootstrap/settings_sections.py:83-85`；`src/application/rendering/style.py:130-134` |
| M2 | major | `text_align: right` 被接受并展示，但渲染器只实现 `center`，选右对齐实际仍是左对齐 | `src/bootstrap/settings_sections.py:79`；`pillow_rendering.py:227`；`qt_compositor.py:135` |
| M3 | major | 冻结 IPC 契约未同步：实现改变了 4 节的 `settings_update_section` 语义，契约仍写"透传/不白名单/分区未开放" | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:261`；`doc/contracts/P15_SETTINGS_IPC_CONTRACT.md:270,283-293` |
| M4 | major | 证据 pin 无效：Task `base_commit` 与 core-report 基线 hash 在仓库中不存在 | `doc/tasks/SETTINGS-OPEN-A-1.md:12`；`verification/SETTINGS-OPEN-A-1/core-report.md:8` |
| M5 | major | 新增测试只验证"透传/映射"，未验证 AC2 的合并结果与"Region 持久化样式覆盖默认值"，导致 B1 漏检 | `tests/core/test_settings_section_validation.py:626-641,683-698` |
| m1 | minor | `manual_font_size` 值域与设计 §3.4 不一致（设计 `>0`，实现/Core/UI 为 1–500） | `doc/design/SETTINGS_SECTION_SCHEMAS.md:80`；`settings_sections.py:85`；`sections.ts:349-350` |
| m2 | minor | `client.p15.test.ts` 结构守卫被弱化：`saveSection(section: string)` 是任意节名写入面 | `apps/desktop/frontend/src/settings/client.ts:230`；`client.p15.test.ts:207-219` |
| m3 | minor | 路径回显测试的 batch-A 拒绝循环漏了 `translate` | `tests/core/test_core_service_settings.py:220` |
| m4 | minor | 治理/交付元数据不一致：`check.ps1` FAIL；Task 仍 `status: ready`、`reviewer: tbd_independent`、AC 未勾；STATUS 超预算；基础 hash 错误也复制进 Handoff | `doc/tasks/SETTINGS-OPEN-A-1.md:6,10`；`doc/STATUS.md`；`doc/handoffs/SETTINGS-OPEN-A-1-87ae85a.md`（`6160a` 已提交） |
| m5 | minor | `pnpm --dir apps/desktop/frontend test` 在干净 commit 上不可复现（`ERR_PNPM_IGNORED_BUILDS`），任务书计划命令与实际可用通道（npm）不一致 | `doc/tasks/SETTINGS-OPEN-A-1.md:73`；`ui-report.md` §5 |
| m6 | minor | GUI 烟测仅覆盖 inpaint（保存 + 重启回读），未"逐分区"，也未覆盖 typeset 的渲染效果；重启说明文本在审查时仍未提交 | `verification/SETTINGS-OPEN-A-1/gui-smoke.md`（工作区有未提交的 restart 段）；`screenshots/07-restart-persisted.png`（`6160a`） |
| n1 | nit | `getSection` 把非对象 payload 静默当 null（掩盖数据损坏） | `apps/desktop/frontend/src/settings/client.ts:204-227` |
| n2 | nit | 保存成功后回读失败会被显示为"保存失败"（写入其实可能已成功） | `useSettingsSection.ts:82-100` |
| n3 | nit | 设计文档引用的消费点行号已漂移（如 `handlers.py:329/330/412/524/525/596/597/938`） | `doc/design/SETTINGS_SECTION_SCHEMAS.md:34-59` |

### 2.2 Blocker 详情

#### B1（blocker）`typeset` 默认样式在两条渲染路径上大部分不生效

- **位置**：`src/application/rendering/service.py:473-475`（`_prepare_region` 调用合并）、`:674-705`（`_merge_defaults`，其中 `:686-692` 的 stroke 分组、`:699-705` 的无条件覆盖）；默认值来源 `src/infrastructure/providers/handlers.py:1027-1093`；两条入口 `src/infrastructure/providers/handlers.py:802-805`（Pipeline render）、`src/bootstrap/core_service.py:1864-1869`（手动 `rerender_page`）；Region 样式合成 `src/application/rendering/style.py:91-105`（`from_domain`）。
- **问题**：`_merge_defaults(style, defaults)` 以 global defaults 为 base，但把 `font_size_offset / line_spacing / text_direction / text_align` **无条件**覆盖为 `style` 的值；`stroke_enabled / stroke_color / stroke_width` 在 `domain_set.stroke_width != 3.0` 时成组覆盖。`from_domain(TextStyle())`（新建 Region 的默认快照）会合成 `stroke_width=0.0`、`offset=0`、`line_spacing=1.0`、`text_align="start"`、`text_direction=AUTO`，因此：
  - `stroke_width=0.0 != 3.0` 恒成立 → global 的 `stroke_enabled/stroke_color/stroke_width` 恒被 region 合成值覆盖；
  - 其余 4 个字段本就不在 domain `TextStyle` 中（Region 无"是否持久化"信息），却被无条件覆盖。
  - 净效果：`typeset` 11 键中 7 键（`stroke_enabled`、`stroke_color`、`stroke_width`、`line_spacing`、`text_align`、`text_direction`、`font_size_offset`）在 **Pipeline render 与手动整页重渲染两条路径都不会生效**；只有 `text_color`（以及 `auto_font_size/manual_font_size` 组合）可能生效。
- **证据（亲自运行，非静态推断）**：用真实 `RenderService._prepare_region` + 新建 Region 默认 `TextStyle()` + 批量 A 合法 `typeset` 值（`stroke_enabled=False, stroke_color=#0000FF, stroke_width=4.0, line_spacing=2.0, text_align=center, text_direction=vertical, font_size_offset=-2, text_color=#112233`）探测得到的 `RenderOp`：

  ```text
  op.text_color      = #112233      # 生效
  op.stroke_enabled  = True         # 期望 False，被覆盖
  op.stroke_color    = #FFFFFF      # 期望 #0000FF，被覆盖
  op.stroke_width    = 0.0          # 期望 4.0，被覆盖
  op.text_align      = start        # 期望 center，被覆盖
  op.direction       = TextDirection.HORIZONTAL  # 期望 VERTICAL，被覆盖
  op.font_size       = 26.0         # offset=-2 未生效（期望 24.0）
  ```

  另外直接对 `_merge_defaults(from_domain(TextStyle()), typeset_style_defaults(...))` 的探测同样显示 `line_spacing=1.0 / text_align="start" / text_direction=AUTO / font_size_offset=0`，而 `fill_color` 虽被合并但无消费者（见 B2）。
- **影响**：违反 AC2"Pipeline `render` 步与手动整页重渲染两条路径都使用新默认值"；真实用户保存排版样式后，除文字颜色/字号开关外看不到任何变化。core-report §3.3/§7 与 Handoff AC2 的"完成"结论不成立。
- **建议**（不擅自修改，仅建议）：
  1. 重写合并优先级：以 `TextStyle()` 域默认值为"未持久化"基线，只有实际持久化字段才覆盖 defaults；不在 domain `TextStyle` 中的字段（`line_spacing/text_align/text_direction/font_size_offset/stroke_enabled/fill_color`）直接取 global defaults。
  2. 设计上需同时裁决一个副作用：`typeset_style_defaults` 用 `RenderTextStyle` 代码默认补全缺省键（例如 `stroke_width` 默认 3.0），而历史 Region 合成值是 0.0；修复合并后，"只保存了 `text_color` 的用户"其所有 Region 可能从 0 stroke 变为 3.0 stroke。需 Lead/设计明确 partial section 的语义并加渲染回归基线。
  3. 在 `tests/rendering` 增补"默认 Region + global defaults → RenderOp 字段断言"以及"Region 显式持久化值仍覆盖 defaults"的正反例；现有新测试（M5）只断言转发，无法捕获本缺陷。

#### B2（blocker）`typeset.fill_color` 无任何消费点（假控件）

- **位置**：白名单 `src/bootstrap/settings_sections.py:74`；提取 `src/infrastructure/providers/handlers.py:1044`；样式字段 `src/application/rendering/style.py:63`；`RenderOp` 定义 `src/ports/rendering/ports.py:83-99`（无 `fill_color`）；渲染器 `src/infrastructure/rendering/pillow_rendering.py:227,235-237`、`src/infrastructure/rendering/qt_compositor.py:135`（只消费 text/stroke color）；前端控件 `apps/desktop/frontend/src/settings/TypesetSettingsPanel.tsx:165-173`、默认值 `sections.ts:378-390`。设计依据冲突：`doc/design/SETTINGS_SECTION_SCHEMAS.md:71`（列入 `fill_color`）vs `:24`（"**不伪造**：没有消费点的设置不得开放……不在 UI 出现假控件"）。
- **问题**：仓库内（`src/**` 全量 grep）`fill_color` 只出现在 `style.py` 的 dataclass 字段、白名单与前端；`RenderOp`/layout/compositor 均不读取它。保存"填充颜色"不会对任何渲染结果产生作用，UI 却已开放并可保存。
- **证据**：`RenderOp` 字段列表（`ports/rendering/ports.py:83-99`）无 fill；`pillow_rendering.py` 只使用 `op.text_color`/`op.stroke_color`/`op.stroke_width`；`qt_compositor.py` 同样；全仓 Python grep 除上述定义/测试无消费点。
- **建议**：二选一后再提交——(a) 本批把 `fill_color` 从白名单、设计 §3.4 表与 UI 中移除（最小、符合 §2.4）；或 (b) 实现真实的填充/背景消费者并补测试，同时把消费者写进设计。当前 commit 保留该控件等于交付一个假控件，不建议放行。

### 2.3 Major 详情

#### M1（major）合法组合 `auto_font_size=false` + `manual_font_size=null` 会让所有渲染失败

- **位置**：`src/bootstrap/settings_sections.py:83-85`（只有单键值域，无跨字段约束）；`apps/desktop/frontend/src/settings/sections.ts:453-458`（空手动字号合法、无跨字段校验）；`TypesetSettingsPanel.tsx:150`（`saveDisabled` 只看范围错误）；`src/application/rendering/style.py:130-134`（`auto_font_size_enabled=False` 且 `manual_font_size=None` 抛 `StyleResolutionError`）；`src/application/rendering/service.py:512-522`（转 skip）；`src/bootstrap/core_service.py:1870-1894`（映射为 `MISSING_REQUIRED_INPUT`）。
- **证据（亲自运行）**：`typeset_style_defaults({"typeset": {"auto_font_size": False, "manual_font_size": None}})` → `_prepare_region` 返回 `report.status=skipped`、`skip_reason="style_resolution_failed: auto_font_size_enabled=False requires a manual_font_size"`；`rerender_page` 对非 `skip_policy/empty_final` 的 skip 直接 `_blocked("MISSING_REQUIRED_INPUT")`，Pipeline render 步会 fail。
- **建议**：Core 写入跨字段拒绝（`auto_font_size is False` 时要求 `manual_font_size != null`），UI 同步禁用保存并给出行内错误；或实现安全的自动回退。该规则设计未冻结，需 Lead 裁决后落到 Task/设计/测试。

#### M2（major）`text_align: right` 无渲染实现

- **位置**：白名单 `settings_sections.py:79`；前端值域 `sections.ts:324`；控件 `TypesetSettingsPanel.tsx:237-257`；渲染器只特判 center：`pillow_rendering.py:227`、`qt_compositor.py:135`。
- **问题**：`right` 是设计 §3.4 允许值并被 UI 展示，但两个 compositor 均把非 center 当作左对齐（start），用户选"右对齐"实际得到左对齐（当前又被 B1 完全掩盖，修复 B1 后就会暴露）。
- **建议**：在 Pillow/Qt 两个 compositor 实现 right 并加像素/布局测试；或把值域收窄为 `left | center` 并同步设计与 UI。

#### M3（major）冻结契约未同步

- **位置**：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:261`（§5.3 第 4 条：其余 section/键透传、本节不白名单化）；`doc/contracts/P15_SETTINGS_IPC_CONTRACT.md:270`（"`settings_update_section` 既有整节替换/透传语义保持 M2-C1 §5.3 不变"）与 `:283-293`（OCR/翻译/修复/排版仍列在"不开放编辑"表）；设计 `doc/design/SETTINGS_SECTION_SCHEMAS.md:3` 状态仍为 `proposed`（"冻结后以契约为准"）。
- **问题**：commit 后 Core 对 4 节在持久化前拒绝未知键/非法值，实质改变了 §5.3 的 wire 语义；但两个冻结契约仍写"透传、不白名单、分区未开放"。本 Task 的 `allowed_paths` 不含 `doc/contracts/**`，因此这不是 writer 能自行修的，但**集成前必须由 Codex/契约 owner 裁决并补契约修订/日期化 exception**；否则 commit 与冻结契约直接冲突。
- **建议**：在 P15 §7 / M2-C1 §5.3 增加指向 SETTINGS-OPEN-A-1 与用户裁决的修订注记（或记录明确的 integration exception），并把 design 状态推进为 frozen；再进入集成。

#### M4（major）证据 pin 无效

- **位置**：`doc/tasks/SETTINGS-OPEN-A-1.md:12` `base_commit: 1fa2c3c58bcb0d5eb4d144d87e71d1ca7b3d3eac`；`verification/SETTINGS-OPEN-A-1/core-report.md:8` 同一 hash；Handoff 也复制该值。
- **证据**：`git cat-file -e 1fa2c3c58bcb0d5eb4d144d87e71d1ca7b3d3eac` → exit 1；`git show -s ...` → `fatal: bad object`。真实 parent/基线是 `1fa2c3c58413b6bce972bd20fb044438d538d3d6`（`git rev-parse 87ae85a^`）。
- **影响**：AC5"固定 commit"与证据可追溯性不成立；该 hash 无法在仓库解析，属于证据错误（需更正 Task/报告/Handoff 三处）。
- **建议**：三处统一改为真实 `base_commit`，并在 commit 后回填 `delivery_head: 87ae85a678880bff840ac77b53f2700e586ad95c`。

#### M5（major）测试质量：AC2 缺少真正能捕获 B1 的测试

- **位置**：`tests/core/test_settings_section_validation.py:626-641`（只断言 `rerender_region` 把 `style_defaults` 转发给 `_prepare_region`）、`:683-698`（只断言 `typeset_style_defaults` 的输出）；无任何测试断言合并后的 `RenderOp`/实际渲染效果或"Region 持久化样式覆盖默认值"。
- **影响**：819 pytest + 364 vitest 全绿仍然无法发现 B1；core-report §7"AC2 已实现……其余键覆盖完整"因此是未经测试支撑的结论。E 轴其余方面：既有测试修改（`test_core_service_settings.py` / `SettingsPage.test.tsx`）属行为变化的合理更新，未删除无关断言；六个仍禁用分区断言保留（`SettingsPage.test.tsx:146-185,275-348`）；新测试对白名单/边界/不落库/前端 payload 有实质覆盖；未覆盖项为 AC2 合并语义、跨字段组合（M1）、`text_align=right`（M2）、`fill_color` 消费（B2）。
- **建议**：B1 修复时补 `tests/rendering` 级回归（默认 Region + global defaults 的 RenderOp 字段；显式持久化 Region 的反例），并把 `_prepare_region` 级探针转为正式测试。

### 2.4 Minor / Nit

- **m1** `manual_font_size` 值域不一致：设计 §3.4 写 `float，> 0`，Core 与前端实际为 `1–500`（`settings_sections.py:85`、`sections.ts:349-350`、`TypesetSettingsPanel.tsx:320`）。实测 `0.5`/`501` 被拒、`1`/`500` 接受。建议统一到设计（或更新设计并说明理由），Core/UI/设计三处同步。
- **m2** 结构守卫弱化：`client.p15.test.ts:207-219` 由"`saveSection` 必须 undefined"改为"是 function"；`client.ts:230` 的 `saveSection(section: string, ...)` 允许任意节名，而 Core 对未知 section 仍透传。建议把 section 参数收窄为冻结的 TS union（`"ocr" | "translate" | "inpaint" | "typeset" | "sfx"`），让"UI 不会提交白名单外的节"变成类型级约束，并在测试中恢复等价的守卫。
- **m3** `tests/core/test_core_service_settings.py:220` 的 batch-A 拒绝循环只有 `("ocr", "inpaint", "typeset")`，漏 `translate`（同样已白名单化），建议补齐。
- **m4** 治理/交付元数据：在 `87ae85a` 后 `pwsh -NoProfile -File tools/governance/check.ps1` 仍 `FAIL (5 errors, 1 warning)`——TASK_LEDGER 341/342 与实际不符、非终态 Task 计数、`doc/STATUS.md` 超预算（`87ae85a` 内 blob 3576 bytes > 3200；parent blob 3196 < 3200，故本次 Task 的 STATUS 行使其越界）、REBASELINE_PLAN 未登记非终态 Task/READY 节点。Task frontmatter 仍 `status: ready`、`reviewer: tbd_independent`、AC 未勾、`delivery_head: null`。Handoff 已由 `6160a` 提交（该 commit 仅含 Handoff + `07-restart-persisted.png`），但 Handoff 内 `base_commit` 仍复制了错误 hash。上述多数路径不在 writer 的 `allowed_paths`，应由 Lead/Codex 在集成前处理。
- **m5** 测试命令可复现性：在干净 commit 树上执行任务/报告主命令 `pnpm --dir apps/desktop/frontend test` 失败（原始错误见 §3），原因是 pnpm 11.25.0 依赖校验要求 `allowBuilds: esbuild`，而该配置只存在于环境产物 `pnpm-workspace.yaml`（已正确地从 commit 清理）。因此 `frontend-pnpm-test-raw.txt` 无法仅凭 commit 复现；仓库跟踪的是 npm 通道（`package-lock.json`）。建议把任务书/报告的主命令改为 `npm --prefix apps/desktop/frontend test`，并说明 pnpm 环境前置。
- **m6** GUI 烟测证据：`gui-smoke.md` 只验证了 `inpaint.background_complexity=medium` 一次保存（我核对了 dev-preview `library.db` 的 `pipeline_defaults.settings_json`，内容一致）；`6160a` 新增了 `screenshots/07-restart-persisted.png`（我已查看：重启后图片修复面板显示 background_complexity=medium，当前持久化值一致），但任务书要求的是"逐分区保存 + 重启复查"，OCR/翻译/排版三节未做真实 GUI 读写；更要紧的是未验证 typeset 对渲染的实际效果（B1 会导致其失败，当前烟测无法发现）。`ui-report.md:136` / `core-report.md:152` 仍把 GUI 烟测标为 NOT_RUN，报告与后来补的证据不同步；`gui-smoke.md` 的 restart 段在审查时仍是工作区未提交修改。
- **n1** `client.ts:204-227` 的 `getSection` 对非对象 payload 静默返回 null，把"数据损坏"与"未设置"混同；可接受，但建议至少保留可区分信号。
- **n2** `useSettingsSection.ts:82-100` 在"写入成功、回读失败"时显示保存失败；upsert 幂等使重试安全，但文案可能误导，建议区分"已保存/回读失败"。
- **n3** 设计文档消费点行号已漂移（如 OCR 实际 `handlers.py:331-332`、context budget `:414`、dilate/erode `:526-527`、quality `:598-599`、context pages `:945-946`）；不影响功能，但作为冻结依据建议同步。

## 3. 独立测试原始结果（均在 commit `87ae85a` 树上重跑）

| 命令 | 原始结果 | exit |
|---|---|---|
| `python -m pytest tests/core tests/pipeline tests/rendering -q` | `819 passed, 2 warnings in 51.87s` | 0 |
| `python -m pytest tests/core/test_settings_section_validation.py -q`（先前在内容等价的审查快照上运行；本次 819 已包含） | `91 passed in 2.39s` | 0 |
| `pnpm --dir apps/desktop/frontend test`（干净 commit） | **FAIL**：`[ERR_PNPM_IGNORED_BUILDS] Ignored build scripts: esbuild@0.21.5` → `pnpm install` exit 1；随后自动重建了 `pnpm-lock.yaml` / `pnpm-workspace.yaml`（已在复核后删除） | 1 |
| `npm --prefix apps/desktop/frontend test`（替代通道） | `Test Files 37 passed (37)` / `Tests 364 passed (364)`，Duration 3.41s | 0 |
| `cd apps/desktop/frontend; .\node_modules\.bin\tsc --noEmit` | 无输出 | 0 |
| `python -m pytest tests/providers -q`（额外执行，非必跑） | `2 failed, 440 passed, 3 skipped in 12.16s`；失败为 `test_detection_manga_real.py` 的既有环境问题（`transformers` 缺 `RTDetrV2ForObjectDetection`），diff 未触及该路径，未计入本 Task 结论 | 1 |
| `pwsh -NoProfile -File tools/governance/check.ps1`（只读） | `FAIL (5 errors, 1 warning)`：TASK_LEDGER 过期 ×2、STATUS 超预算、DAG 未登记、READY 未登记；WARN 2 个非终态 Task | 1 |

说明：
- 在收到提交通知前，我曾在未提交工作区跑过同一套 pytest/vitest/tsc，结果一致；收到通知后在 `87ae85a` 上重跑，数字如上。后续 `6160a` 仅新增 Handoff 与截图，`git diff --stat 87ae85a 6160a` 无产品代码差异，故测试结论对当前 HEAD 继续成立。
- 前端 `npm test` 与 `tsc` 均通过；`pnpm` 失败是环境/工具链问题（m5），不是代码失败。
- 本机 Python 3.14.6 / pytest 9.1.1 / node 24.15.0 / pnpm 11.25.0；我运行 pnpm 时自动重建的两个环境文件（`pnpm-lock.yaml`/`pnpm-workspace.yaml`）已在复核后删除，未改动任何产品文件。审查结束时工作区为：`verification/SETTINGS-OPEN-A-1/gui-smoke.md` 工作区修改（他人写入的 restart 段，未提交）+ 本文件 `review-r1.md` 未跟踪。

## 4. 范围核对（commit `87ae85a`，40 文件）

| 分组 | 文件 | 是否在 `allowed_paths` |
|---|---|---|
| 前端 settings（17） | `SettingsPage.tsx`、`SettingsPage.test.tsx`、`client.ts`、`client.p15.test.ts`（M）；`OcrSettingsPanel.tsx/.test.tsx`、`TranslationParamsPanel.tsx/.test.tsx`、`InpaintSettingsPanel.tsx/.test.tsx`、`TypesetSettingsPanel.tsx/.test.tsx`、`sections.ts`、`useSettingsSection.ts`、`SectionField.tsx`、`SectionPanelFrame.tsx`、`client.sections.test.ts`（A） | 是（`apps/desktop/frontend/src/settings/**`） |
| Core（5） | `settings_sections.py`（A）、`core_service.py`、`application/rendering/service.py`、`infrastructure/providers/handlers.py`、`infrastructure/sqlite/pipeline.py`（M） | 是 |
| 测试（3） | `tests/core/test_core_service_settings.py`（M）、`tests/core/test_settings_section_validation.py`（A）、`tests/pipeline/test_pipeline_production_seam.py`（M） | 是 |
| 文档（3） | `doc/STATUS.md`（M）、`doc/design/SETTINGS_SECTION_SCHEMAS.md`、`doc/tasks/SETTINGS-OPEN-A-1.md`（A） | 是 |
| 证据（12） | `verification/SETTINGS-OPEN-A-1/**`（core-report、ui-report、gui-smoke、3 份 raw log、6 张截图） | 是 |

- **未跟踪/环境产物**：`apps/desktop/frontend/pnpm-lock.yaml`、`pnpm-workspace.yaml` 不在任何 commit 内（正确）。Handoff `doc/handoffs/SETTINGS-OPEN-A-1-87ae85a.md` 由后续 docs-only commit `6160a` 提交（在 `allowed_paths` 内），AC5 的 Handoff 交付已补上。
- **禁止范围核对**：无 Schema/migration、无依赖变更（`package.json`/lock 未改）、无 Provider/Network/凭据/SFX wire 语义修改（仅 settings 存储层 `_redact` 精确键豁免）、未开放批次 B/C 分区、未新增 Secret/路径字段。commit 名称与内容一致。
- **说明**：`doc/tasks/SETTINGS-OPEN-A-1.md` 与设计文件本身是本次新增（untracked→commit），其 `allowed_paths` 中 `src/infrastructure/sqlite/pipeline.py` 是随 `_redact` 修复一起被加入的；由于无冻结基线可 diff，该扩展只能依据 core-report §5.1 的"Lead 授权"陈述，Review 无法独立验证授权本身（记录为流程事实）。

## 5. 亲自验证 / NOT_RUN

**亲自验证（已做）**
- 通读任务/设计/P15 §7/M2-C1 §5.3/两份实现报告；核对 `git show --stat 87ae85a`、`git diff --name-status 87ae85a^ 87ae85a` 与全部新增/修改的源码、测试、设计/任务文件（raw 日志与截图抽样核对）。
- AC1 值域与边界：用真实 `validate_settings_section` 探测四节合法/非法/边界/bool-int/NaN/Inf/未知键/未知 section；确认非法写不落库（`tests/core` 全绿，含新增 91 项与改动后的路径回显测试）。
- AC2 数据链：读 `handle_render`、`handle_rerender_page`、`rerender_region`、`_prepare_region`、`_merge_defaults`、`typeset_style_defaults`；用真实 `_prepare_region` 探针证明 B1，用 `skip_reason` 探针证明 M1；确认无 typeset 时 `None` 路径不变。
- C：`_redact` 精确豁免（`pipeline.py:883-903`）与新增安全回归（`tests/pipeline/test_pipeline_production_seam.py:133-180`）核验；确认 `api_key/password/auth_token/refresh_token/secret` 仍被丢弃、`context_token_budget` 落库并进入下一 Run 快照；无新 Secret/路径进入设置 DTO。
- D：逐键对照四面板实际提交 payload（`sections.ts`/四个 panel）与 Core 白名单（完全一致：ocr 2、translate 2、inpaint 4、typeset 11，无 `font_family`）；确认 null→"未设置"语义、错误走 `SettingsErrorBar` 封闭投影、六个仍禁用分区的按钮/徽标断言保留、无 mock 数据。
- F：commit 文件清单/范围/环境产物/治理检查（见 §4）。
- 证据：核对 `gui-smoke.md` 与 dev-preview `library.db` 的 `pipeline_defaults.settings_json`（内容一致：`inpaint.background_complexity=medium`，其余键为默认值）；查看截图 `02-ocr-panel.png`、`06-typeset-panel.png`、`07-restart-persisted.png`（重启后图片修复面板回读 medium，与 DB 一致）；核对 `git diff --stat 87ae85a 6160a`（仅 Handoff + 截图 07，无产品代码）。

**NOT_RUN / 无法验证**
- 未在真实 Tauri 应用中独立复跑 GUI 烟测（无 GUI 会话控制；仅核对 Lead 留下的 DB/截图证据）；未验证"重启后仍保留"与"新 Run 使用新值"的真实 UI 行为。
- 未在 pristine baseline（parent commit）上重跑基线测试，因此 ui-report"变更前 32 files / 327 tests"未独立复核；同时不能在共享工作区 revert 验证。
- 未运行 Rust/Tauri 构建与测试（本次 diff 无 Rust 改动；相关命令 NOT_RUN）。
- 未验证真实 Provider 端到端（OCR/翻译/修复调用）——本 Task 不影响 Provider wire，范围外。
- 未验证 `_redact` 豁免对其它未来 section 的长期影响（静态结论：精确键名、只在同名键时放行）。
- AC5 的"固定 commit 已 push/签收"未发生（`87ae85a` 与 `6160a` 均未 push）；Handoff 已随 `6160a` 提交，但 `gui-smoke.md` 的 restart 段仍为工作区未提交修改。

## 6. 审查快照（可复现性）

- 实现 commit：`87ae85a678880bff840ac77b53f2700e586ad95c`；parent：`1fa2c3c58413b6bce972bd20fb044438d538d3d6`；分支 `main`。
- 审查期间 HEAD 推进到 `6160a237aad7e74c5a32bed8bdde3b6c73fb94f4`（docs-only：Handoff + 截图 07），随后推进到 `fd31d0b8b`（docs-only：`gui-smoke.md` restart 段）；产品代码与 `87ae85a` 相同，blocker 结论不变。
- **审查后状态（不属本 Review 覆盖范围）**：本报告落盘后（21:10+）工作区出现返修改动且尚未提交——`apps/desktop/frontend/src/settings/sections.ts`（前端侧 M1/M2/B2：收窄 text_align、移除 fill_color、auto/manual 跨字段）、`doc/design/SETTINGS_SECTION_SCHEMAS.md`、`doc/contracts/M2-C1_...`/`P15_...`（M3 增量修订注记）。其中 **B1（Core `_merge_defaults`）在返修工作区仍未修改**，Core 白名单 `src/bootstrap/settings_sections.py` 也尚未同步移除 `fill_color`/收窄 `text_align`；这些改动必须提交并由新一轮 Review 验证后才能改变本结论。
- 关键文件 SHA-256（复核时工作区与 commit 一致）：
  - `src/bootstrap/settings_sections.py` `8691D5297BC5A7EEB3C76C26E8A27F5C04ED72A55CC1827F9A8B57239EFABB1A`
  - `src/application/rendering/service.py` `7225E5AB71AA3D5D560847987C67A775D9EF78B5C3D10DB9B2D4218BD4C0782D`
  - `src/infrastructure/providers/handlers.py` `50E533C75009D2233B24A8B9B827BFE6F731D4C73694F99755EF830DA33D3D44`
  - `src/infrastructure/sqlite/pipeline.py` `5B057E988BBD472009A0316A8D924177CDF993B800BBEB6796F408F9C1D8996A`
  - `src/bootstrap/core_service.py` `58DD72674FEAA8043695EC725FC3860A72366989B75DB9AF7066DC7F6870AEA5`
  - `apps/desktop/frontend/src/settings/sections.ts` `5E3C78E9928CBF7F71A8C2D84249CB841E2EEC5D793BF2E837FB0EA7629AEB77`
  - `apps/desktop/frontend/src/settings/client.ts` `EE7C8C5A8BE2F98F94298298C343CE80186E88B94C136C033A63731DF607A7FE`
  - `tests/core/test_settings_section_validation.py` `0369A7D76E3356297B98209D52A3435A2E11E53913C040A1BBE536EC6FC8AE5D`

## 7. 返修顺序建议（供 Lead/实现者）

1. **B1**：修 `_merge_defaults` 优先级 + `tests/rendering` 级回归（含 Region 显式持久化值仍覆盖 defaults 的反例），并裁决 partial `typeset` 的 stroke 默认语义。
2. **B2**：Lead/设计裁决 `fill_color` 去留；移除或补真实消费者+测试后再重审。
3. **M1/M2**：跨字段校验与 `text_align=right` 实现（或收窄值域），设计与 UI 同步。
4. **M3/M4/m4**：契约修订/exception、真实 base commit 回填、Task 元数据/AC/Handoff、REBASELINE_PLAN/TASK_LEDGER、STATUS 预算。
5. **m1/m2/m3/m5/m6**：值域对齐、前端 section union、测试补齐、主命令改 npm、GUI 烟测扩到逐分区+重启+typeset 渲染效果。
6. 返修后重新提交并由独立 Review 重跑 `pytest`/`npm test`/`tsc` 与 `_prepare_region` 探针，再进入集成。
