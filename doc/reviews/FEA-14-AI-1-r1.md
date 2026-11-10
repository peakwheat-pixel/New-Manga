---
task_id: FEA-14-AI-1
reviewer: DSH r1 独立复核子 agent（lead 会话 session-408d4e24-3789-4111-acde-983899601dad 派发；全新上下文，未参与实现/返修）
reviewer_kind: subagent
author: dsh
base_commit: 36c4376d1
reviewed_head: 41d54395a6707530dfd465f04be7efe77322171a
decision: changes_requested
---

# Review：FEA-14-AI-1（r1 独立复核）

## 0. 审查对象与环境

| 项 | 值 |
|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` |
| 被审 head | `41d54395a6707530dfd465f04be7efe77322171a`（开始与结束时均未变） |
| 提交链 | `13d9e39e1`（实现）→ `aac1aba9d`（v14 测试适配 + allowed_paths）→ `9e1ec59f7`（证据）→ `41d54395a`（证据表 commit pin 回填，HEAD） |
| diff 基线 | `36c4376d1`（卡面 `base_commit`；EDIT-1 收口 + AI-1 冻结提交） |
| 审查时点 | 2026-11-10 18:05:45 – 18:21:22 +08:00（关键命令时点见 §5） |
| 环境 | Windows；Python 3.14.6 / pytest 9.1.1；.NET SDK（net9.0）；PowerShell 7 |
| 只读纪律 | 未 commit / push；未改源码、测试、契约、卡面或证据；探针脚本、隔离库与复跑日志全部在 `%TEMP%`（`ai1_r1_*.py`、`ai1-r1-*.log`），探针/隔离库未写真实 `%APPDATA%`；`dotnet test` 按门禁要求生成忽略的 `bin/obj` 构建产物，`git status` 未出现 |
| 工作树 | 开始时 `git status --porcelain` 为空（0 行）；审查结束（写完本报告后）仅 `?? doc/reviews/FEA-14-AI-1-r1.md`；HEAD 未变 |

说明：本次未采信卡面自述。所有 PASS 均来自本次实测、逐行脚本比对或源码核对；未实测项列入 §6 NOT_RUN。

## 1. 结论

**`changes_requested`。** P0 = 0，P1 = 0，**P2 = 2**，P3 = 7（F-03–F-09，登记/接受）。

产品主体本身实测通过：schema v14 additive（v1–v13 NAME/SQL 逐字节未变，v13→v14 行级无损、新表为空）、P21–P25 wire 形状与 typed 错误、Host 六处 5 方法、P21/P22/P24/P25 与 P23 行为面、18 pins 中仅 C-07 变化、证据 provenance 与 allowed_paths 均符合任务要求。

阻断项有两条：

1. **F-01（P2）**：P23 删除的「重指派 + 软删」**不在同一事务**。`reassign_references` 与 `update_template` 各自 `with self._conn` 提交；故障注入证明重指派已落库、目标仍可见，与卡面 §裁决 `doc/tasks/FEA-14-AI-1.md:77`、实现说明 `:97` 及 README `:34` 的「同一事务」明确不符。
2. **F-02（P2）**：C-07 v1.8 正式成员表 `Changed` 行类别注解为 `（属性）`，而 `generate_api_inventory.py` stdout 为 `（事件）`（v1.7 原字节正确，v1.8 重建时回归）。自写全量行比较 83/83 行中仅此 1 行不一致，`ALL_MATCH: False`，故卡面 AC5 的「成员表逐行 = 脚本 stdout（`ALL_MATCH: True`）」不成立；pin `58dbae4c…` 覆盖的是该错误字节，修正文档需重算 pin 并同步 FROZEN/载体/README/卡面。

## 2. Findings

| ID | 级别 | 文件 / 行 | 问题 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| F-01 | **P2（阻断）** | `src/application/ai/prompt_templates.py:122-124`；`src/infrastructure/sqlite/prompt_templates.py:90-97`、`:58-71` | `delete_template` 先 `reassign_references`（内部 `with self._conn` 提交），再 `update_template`（第二次 `with self._conn` 提交）；两次独立事务，不满足卡面「在同一事务内把引用重指派到 replacement 后软删目标」（`doc/tasks/FEA-14-AI-1.md:77`、`:97`；`verification/FEA-14-AI-1/README.md:34`）。 | `%TEMP%\ai1_r1_probe.py` 故障注入：把 `store.update_template` 替换为抛错函数后调用 `delete_template`；输出 `refs after failure (raw): [('<template>', 'task', 'owner-y')]`、`target still visible: True` —— 重指派已提交、软删未提交。 | 在 store 增加单一事务方法（一个 `with self._conn` 内执行 `UPDATE OR REPLACE` + `UPDATE ... SET deleted_at`），service 改调该方法；补一个故障注入/回滚测试；随后重跑定向与回归证据。 | open |
| F-02 | **P2（阻断）** | `doc/plan/FEA-C07_API_INVENTORY.md:118`（另见 `doc/plan/FEA-CONTRACT-FROZEN-C07.md:15/31/43/96`、`doc/reviews/CONTRACT-UNFREEZE-2026-11-10-AI1.md:8/12`、`doc/tasks/FEA-14-AI-1.md:88`、`verification/FEA-14-AI-1/README.md:16`） | 正式成员表 `Changed` 行写作 `（属性）`，脚本 stdout 为 `（事件）`；`Changed` 在 `IHostController.cs` 是 `event EventHandler?`。v1.7 原字节为 `（事件）`，v1.8 重建成员表时回归。 | 自写解析器比较 doc 与 `python tools/generate_api_inventory.py` stdout：`IReaderProgressSink 1/1 match=True`、`IRunController 6/6 match=True`、`IHostController 83/83 rows`，仅索引 82 行不一致：doc `Changed（属性）` vs stdout `Changed（事件）`；`ALL_MATCH: False`。`generate_api_inventory.py --check` 只比计数，故 EXIT 0 不能发现此差异。 | 把该行改回 `（事件）`；重算 C-07 pin；同步 FROZEN §1 新 pin/前一 pin、§1B、§2#3、§5、UNFREEZE 载体、README 与卡面 AC5；复跑逐行比较至 `ALL_MATCH: True`。 | open |
| F-03 | P3（登记/接受） | `src/infrastructure/sqlite/prompt_templates.py:90-97` | replacement 已存在相同 `(kind, owner_id)` 引用时，`UPDATE OR REPLACE` 删除 replacement 原行、保留被删模板的行，label 被静默覆盖（引用身份 kind+owner 未丢，仅展示 label 以被删模板行为准）。 | 探针：A、B 两模板对同一 `owner-x` 各有 label `A-label`/`B-label`；`delete(A → B)` 后 replacement 只剩一行 `(B, translation, owner-x, 'A-label')`，`B-label` 消失。 | 可接受但须登记；未来引用写入方卡应定义 label 合并/保留规则，或改用 `INSERT ... ON CONFLICT DO UPDATE` 明确取值并记录；不要依赖 REPLACE 的隐式删除语义。 | accepted / registered |
| F-04 | P3（接受） | `src/application/ai/prompt_templates.py:94-103` | P22 更新时即使 name/body 与现值完全相同也 `version += 1`（no-op 保存也递增）。 | 探针：新建后以相同 name/body 再保存，`version after no-op save 2`。 | 符合卡面「每次保存 +1」（`doc/tasks/FEA-14-AI-1.md:68/79`），非缺陷；建议在 AI-2/UI 卡说明「无变化保存也递增」，避免 UI 以版本变化判断内容是否变化。 | accepted |
| F-05 | P3（登记/接受） | `src/application/ai/prompt_templates.py:81`、`:95-97`、`:137`；`src/infrastructure/sqlite/schema.py:977` | name 唯一仅覆盖 `prompt_templates` 未软删行（partial unique index）且 service 为精确匹配：不覆盖内置模板名；大小写/空白变体视为不同名。 | 探针：用户模板可命名为 `Default Translation`（与内置同名）；`mine` 与 `Mine` 可并存（visible 5 条）。 | 与 DDL「name 唯一（软删不占用）」一致；「是否把内置名纳入命名空间、是否大小写/空白规范化」属未来裁决（任务点 ③），登记不阻断。 | accepted / registered |
| F-06 | P3（接受/建议修） | `tests/storage/test_issue_markers.py:57-92`（重点 `:60-62`、`:76-77`、`:83`、`:90`） | v14 后 `MIGRATIONS[:-1]` 变为 v1..v13，测试实际从「v12→v13」漂移为「v13→v14」，但测试名与注释仍称 v12→v13；v13 建表不再单独覆盖。 | 源码：`:60` `MigrationRunner(conn, MIGRATIONS[:-1])`；`:61` 断言 13；`:83` 断言 14；`:62` 注释「A real v12 ... survive the v13 table creation」已不成立。 | 建议把 pre-state 固定为 `MIGRATIONS[:12]`（或单独跑 `MIGRATIONS[:13]` 再跑全链）并更新注释；至少修正误导性注释。不影响本卡产品结论（v13 已由 EDIT-1 覆盖，v14 由新测试覆盖）。 | accepted（建议后续修） |
| F-07 | P3（接受） | `apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs:377-420` | Fake 与 Core 语义有差：未知 `templateId` 的 Save 会新建（Core 为 `TARGET_NOT_FOUND`）；Save/Copy 不校验重名（Core 为 `TEMPLATE_NAME_EXISTS`）；Delete 不校验 replacement 存在/非自身；GetReferences 忽略 `templateId` 返回全部。 | 源码核对；4 个 `PromptTemplatePortTests` 通过，未覆盖这些差异。 | 仅 UI 测试替身，本卡无 UI，不阻断；建议 AI-2/UI 前收紧或在注释中登记 limitation。 | accepted |
| F-08 | P3（登记/接受） | `verification/FEA-14-S5-PREQ-1/ddl-v10-plan.md:41`；`doc/tasks/FEA-14-AI-1.md:68/79` | DDL 计划 §2.4 写 `version（不可变）`，AI-1 卡与实现按「每次保存 +1」。 | 文档对比。 | AI-1 卡是后出且更具体的口径，按卡实现；建议在 PREQ/DDL 计划或 AI-1 收口处补一句 errata，避免未来误读。 | accepted / registered |
| F-09 | P3（观察） | `tests/storage/test_upgrade_schema_data.py:72-97` | `LATEST_TABLES` 只列到 v8 表，未含 v10/v11/v13/v14 新表；v14 新表未被该清单断言。既有漂移；v14 升级由参数化测试与定向测试覆盖。 | 源码核对；回归 1267 passed。 | 不影响本卡结论；后续维护时补齐 v10–v14 表名。 | accepted / observation |

## 3. AC 逐项判定

| AC | 判定 | 依据（本次实测） |
|---|---|---|
| **AC1 数据面/v14** | **MET** | 自写探针：base `36c4376d1` 的 `MIGRATION_V1..V13_{NAME,SQL}` 与 HEAD 逐字节相同（13/13 OK）；`default_migrations()` = v1..v14；v13 库插入真实 book/chapter/page/issue_marker 行后升级 v14：`APPLIED [14]`、`ROWS_PRESERVED True`、`prompt_templates`/`prompt_template_references` 两表 0 行；两索引存在。 |
| **AC2 P21/P24** | **MET** | P21 `{templates:[{template_id,name,version,builtin}],builtin_count}`，键集精确，`builtin_count=2`，内置在前、自建 filter 未软删；P24 缺省名 `Default Translation (copy)`、`version=1`、body 与内置一致、`builtin=false`；显式名/重名/未知 builtin 均 typed（见 §4）。 |
| **AC3 P22** | **MET** | 新建 version=1；按 id 更新 version+1；跨模板与更新重名 → `TEMPLATE_NAME_EXISTS`（wire category `conflict`）；空/空白/超长 name、空 body → `INVALID_REQUEST`；内置 id → `INVALID_REQUEST`（不落库）；未知 id → `TARGET_NOT_FOUND`。附 P3：F-04（no-op 也递增）、F-05（唯一性范围）。 |
| **AC4 P23/P25** | **MET（AC 字面行为面）** | P25 返回 `{kind,owner_id,label}`；无引用空数组；未知/软删 → `TARGET_NOT_FOUND`；P23 replacement 必填、存在、非自身、非内置（缺失/空/自身/内置/未知均 typed）；重指派后目标软删、P21 不可见、P25/P23 再触达 → `TARGET_NOT_FOUND`；无引用删除同样要求 replacement。**但卡面 §裁决 `:77` 的「同一事务」未满足（F-01）**，故该裁决口径不成立；AC 字面未写「同一事务」，故 AC 本身不因 F-01 判 NOT MET。 |
| **AC5 契约/门禁** | **NOT MET** | pin `58dbae4c…` = 文件 SHA-256（实测）；统计 79/86；S5 计划节无待实现行（25/25）；`--check` EXIT 0；`verify_pins` 18/18；FROZEN §1/§1B/§2#3/§3/§5 主体自洽。**但正式成员表 `Changed` 行与脚本 stdout 不一致（F-02），`ALL_MATCH: False`，AC5 的「逐行一致（ALL_MATCH: True）」不成立。** |
| **AC6 证据** | **MET** | 4 个日志头均为 `HEAD=aac1aba9d` + `dirty=[?? verification/FEA-14-AI-1/]`；计数 pytest-ai 7 / regression 1267 / App 887 passed·0 failed·11 skipped / pins 18/18 + API 79-86；卡面 5 行 sha256 与 README/日志逐一匹配；`9e1ec59f7` tree 含 5 文件，卡面 commit pin 指向该 commit；本次复跑计数一致（§5）。NOT_RUN 如实（§6）。 |

## 4. 必查项判定

| # | 必查项 | 判定 | 本次证据 |
|---|---|---|---|
| 1 | schema v14 additive | **PASS** | v1–v13 NAME/SQL 逐字节相同；v14 SQL sha256 `3142ecfc41eea13c7f126843ae425ea0fba3b9bd012e518432c1f66aa0eaaf97`，仅新增两表 + 两索引；`default_migrations()` 顺序 1..14；v13→v14 行级 preserved、新表空。 |
| 2 | P21 列表 | **PASS** | 探针返回 `builtin_count=2`；每条键集 = `{template_id,name,version,builtin}`；内置在前（`builtin-translate-default`/`builtin-sfx-detect`），自建未软删；`{}` 之外多余键 → `INVALID_REQUEST`（wire 测试）。 |
| 3 | P22 保存 | **PASS** | 见 AC3；另实测 name 上限 120、body 上限 20000（超长 → `INVALID_REQUEST`；具体数值未在卡面/README 写明，建议 README 补记这两个实现上限）。 |
| 4 | P23 删除 | **PASS（行为）/ FAIL（同一事务）** | replacement 必填/存在/非自身/非内置均 typed；引用重指派后目标软删、目标引用面 `TARGET_NOT_FOUND`；`UPDATE OR REPLACE` 覆盖语义见 F-03；**F-01 证明重指派与软删分两事务**。 |
| 5 | P24 复制 | **PASS** | 未知 builtin → `TARGET_NOT_FOUND`；缺省名 `"<builtin name> (copy)"`；显式名/重名 → typed；副本 version=1、body 与内置一致、`builtin=false`。 |
| 6 | P25 引用 | **PASS** | 返回 `{references:[{kind,owner_id,label}]}`；无引用空数组；未知/软删 → `TARGET_NOT_FOUND`；内置当前空（当前无引用写入方；若未来有行指向内置，实现会返回实际行，属数据驱动，口径边界仅登记）。 |
| 7 | Host 六处 | **PASS（静态 + 编译 + 测试）/ 真实 IPC NOT_RUN** | 六处 5 方法签名逐字一致（`IHostController`/`HostController`/`NullHostController`/`HostRuntime`/`CoreServiceClient`/`FakeHostController`）；NullHost 返回空/false/null 不抛（4 个端口测试通过）；Client 序列化/解析静态核对：P21 `{}`→templates、P22 template_id?+name+body→template_id+version、P23 template_id+replacement_id→deleted、P24 builtin_id+name?→template_id、P25 template_id→references；P24 客户端缺省 name 空串/version=1 的 limitation 已在卡面 `:99` 与 README `:35` 登记。真实 Host↔Core IPC 未对活 Core 调用（NOT_RUN）。 |
| 8 | C-07 v1.8 | **FAIL（逐行）/ PASS（其余）** | 逐行比较：79 方法全对，`Changed` 行 `（属性）` vs stdout `（事件）` → `ALL_MATCH: False`（F-02）。pin `58dbae4c14d7ec4b946bbf27a237415b938a7160e9c8b311db6dd0377da9dfef` = `Get-FileHash`；v1.7 pin `89781583…` = base blob hash；统计 79/86；S5 计划节表格无数据行（25/25 已落地）；FROZEN §1（v1.8 + v1.7 保留）/§1B/§2#3 `1/79/6=86`/§3 25/25/§5 v1.8 行自洽（除 `ALL_MATCH` 声明外）；`--check` EXIT 0；18/18。 |
| 9 | 契约字节 | **PASS** | 18 个 pinned blob 的 base→HEAD 比较：仅 `FEA-C07_API_INVENTORY.md` 变化；`doc/plan` 下另仅 `FEA-CONTRACT-FROZEN-C07.md`（记录）变化；`doc/reviews` 下仅新增 `CONTRACT-UNFREEZE-2026-11-10-AI1.md`；无其他契约字节改动。 |
| 10 | 证据 provenance | **PASS** | 4 日志头 `HEAD=aac1aba9d3f84e82f60ac891cc19a78a7e3474d8` + `dirty=[?? verification/FEA-14-AI-1/]`；计数与卡面一致（7 / 1267 / 887/0/11 / 18/18+79-86）；5 个 sha256 与卡面逐一相同；`9e1ec59f7` tree 含 README + 4 日志；卡面 5 行 commit pin 均 `9e1ec59f7`；本次复跑计数一致。 |
| 11 | 范围 | **PASS** | `git diff --name-only 36c4376d1..HEAD` = 33 路径，自写 glob 检查 `OUTSIDE=[]`（30 条 allowed_paths）；工作树 clean、HEAD 审查期间未变（开始/结束均记录）。 |
| 12 | AC 独立判定 | **AC1–AC4/AC6 MET；AC5 NOT MET** | 见 §3；NOT_RUN 见 §6，未把未实测项写成 PASS。 |
| 13 | 扫新问题 | **F-01/F-02 阻断；F-03–F-09 登记** | 见 §2；特别核实了 ① P23 重指派覆盖（F-03）、② 内置集合/文案属 AI-2（P3 无冲突）、③ name 唯一仅未软删行（F-05）、④ P22 no-op 递增（F-04）、⑤ Fake 保真度（F-07）。 |

## 5. 门禁与测试表

| # | 命令 / 探针 | 时点（2026-11-10 +08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `python -m pytest tests/storage/test_prompt_templates.py tests/core/test_prompt_template_wire.py -q` | 18:13:09 – 18:13:10 | `7 passed in 1.21s` | 0 |
| 2 | `python -m pytest tests/storage tests/core tests/fea09/test_v7_migration.py tests/fea11/test_source_gate_unify.py -q` | 18:07:18 – 18:09:15 | `1267 passed, 1 warning in 116.56s` | 0 |
| 3 | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --nologo` | 18:07:18 – 18:12:55 | `通过 887 / 失败 0 / 跳过 11 / 总计 898`，5m25s（与 #2 并行，故时长较证据 4m48s 长；计数一致） | 0 |
| 4 | `dotnet test ... --filter "FullyQualifiedName~PromptTemplatePortTests"` | 18:17:00 – 18:17:03 | `通过 4 / 失败 0`（4 个新端口测试） | 0 |
| 5 | `pwsh -NoProfile -File tools/governance/check.ps1` | 18:13:16 – 18:13:17 | `Governance check: PASS (3 warnings)` | 0 |
| 6 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-14-AI-1.md` | 18:13:18 – 18:13:19 | `Governance check: PASS (3 warnings)` | 0 |
| 7 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 18:12:45 – 18:12:46 | `PIN AUDIT: PASS (all 18)`；C07 = `58dbae4c14d7` | 0 |
| 8 | `python tools/generate_api_inventory.py --check` | 18:10:30 | 计数 `IReaderProgressSink 1 / IHostController 79 / IRunController 6 / 合计 86`；`--check` 只比计数，不验成员行 | 0 |
| 9 | 自写 C-07 行比较（doc vs 脚本 stdout；83/83 行） | 18:14 前后 | `IReader 1/1 True`、`IRun 6/6 True`、`IHostController 83/83`，仅 `Changed` 行注解不一致；`ALL_MATCH: False`（F-02） | 0（脚本本身） |
| 10 | 自写 schema 字节/升级探针 `%TEMP%\ai1_r1_probe.py` | 18:10 前后 | v1–v13 全 OK；`BASE_LAST_VERSION 13`；`HEAD_VERSIONS [1..14]`；v13→v14 `APPLIED [14]`、`ROWS_PRESERVED True`、两新表 0 行 | 0 |
| 11 | 自写服务语义探针（同 #10 脚本后半） | 18:10 前后 | P21/P22/P23/P24/P25 typed 路径均符合；F-01 原子性故障注入、F-03 覆盖、F-04 no-op 递增、F-05 同名/大小写均复现 | 0 |
| 12 | 自写 allowed_paths 检查 `%TEMP%\ai1_r1_scope.py` | 18:14 前后 | `CHANGED 33`、`OUTSIDE []`、`SCOPE_OK True` | 0 |
| 13 | `git diff --check 36c4376d1..HEAD` | 18:19 前后 | 无 whitespace 错误 | 0 |

## 6. NOT_RUN（如实登记）

- **真实 Host↔Core 进程级 IPC**：5 个新 `CoreServiceClient` 方法未对活 Core 调用；本次仅静态核对序列化/解析，并以 C# 编译 + 4 个端口测试（NullHost/Fake）间接覆盖。真实 IPC 读写映射未测。
- **P24 真实 Core 端到端**：客户端缺省 name 投射为空串、version=1 的 limitation 仅登记，未以活 Core/P21 刷新验证。
- **模板 UI/编辑器/预览、内置模板最终集合与文案**：属 AI-2/UI 卡，NOT_RUN。
- **真实 AI 模型/网络调用**：PREQ §6 明确本清单不触发；NOT_RUN。
- **引用行写入方（译文/任务/规则）**：本卡不创建引用；P23 重指派仅用测试/fixture 行验证；未来写入方的 label/并发语义未测。
- **并发**（同一模板并发 save/delete）、**万级模板性能**、**真实大库迁移**：NOT_RUN。
- **FEA-15 正式验收声明**：未审。
- **F-01 修复后的崩溃恢复**：仅以故障注入证明当前非原子；未测试修复方案（尚不存在）。
- 本次未运行 `dotnet` 与 pytest 串行基线；两者并行执行，仅时长变化，计数与证据一致。

## 7. 处置建议

1. **F-01（P2）**：把 P23 的「重指派 + 软删」收敛为单一存储层事务（例如 `soft_delete_with_reassignment(source, replacement)`，内部一个 `with self._conn`），service 只调用一次；补一个注入异常断言「要么都未发生、要么引用与软删同时生效」的测试；重跑定向/回归/App 门禁并刷新证据。
2. **F-02（P2）**：把 `doc/plan/FEA-C07_API_INVENTORY.md:118` 改回 `Changed（事件）`；重算 pin（当前 `58dbae4c…` 作废为新前一 pin）；同步 `FEA-CONTRACT-FROZEN-C07.md` §1/§1B/§2#3/§5、`CONTRACT-UNFREEZE-2026-11-10-AI1.md` pin 行、README 与卡面 AC5；用逐行脚本复验 `ALL_MATCH: True`（仅 `--check` 不够）。
3. **P3 登记**：把 F-03（REPLACE label 覆盖）、F-04（no-op 递增）、F-05（内置名/规范化边界）、F-06（v13 测试漂移）、F-07（Fake 保真度）、F-08（DDL 计划 `version` 口径）、F-09（`LATEST_TABLES` 漂移）写入 README 的 limitation/后续卡输入，避免丢失；F-06/F-07 可在本轮顺带修正。
4. 修复后由 DSH 指定新的独立上下文复核（r2），不得以本 r1 报告或同一会话自审；本报告只对 `41d54395a` 有效，head 变化即失效。

## 8. 审查者声明

本报告由 lead 会话 `session-408d4e24-3789-4111-acde-983899601dad` 派发的**全新上下文子 agent**出具；审查者未参与 FEA-14-AI-1 的实现、测试、证据生成或任何返修，审查期间只读。唯一仓库写入为本报告 `doc/reviews/FEA-14-AI-1-r1.md`；探针脚本、隔离数据库与本轮复跑日志全部在 `%TEMP%`，探针/隔离库未写真实 `%APPDATA%`，未 commit/push（`dotnet test` 的忽略构建产物除外，`git status` 未见）。PASS 仅基于本次 2026-11-10 18:05–18:21 的实测、逐行脚本比对与源码核对；未执行项已列入 §6，未把未实测项写成 PASS。写报告前复核：`git rev-parse HEAD` = `41d54395a6707530dfd465f04be7efe77322171a`（未变），`git status --porcelain` 为空；写报告后复核（18:21:22）：HEAD 仍为 `41d54395a`，`git status --porcelain` 仅 `?? doc/reviews/FEA-14-AI-1-r1.md`，`check.ps1`（默认 + `-TaskPath`）复跑 PASS（3 warnings）。本报告只对 `41d54395a` 的字节有效；head 变化即自动失效。
