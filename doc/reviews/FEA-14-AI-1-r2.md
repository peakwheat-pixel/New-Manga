---
task_id: FEA-14-AI-1
reviewer: DSH r2 独立复核子 agent（lead 会话 session-408d4e24-3789-4111-acde-983899601dad 派发；全新上下文，未参与实现/返修）
reviewer_kind: subagent
author: dsh
base_commit: 36c4376d1
reviewed_head: 2737d035ae3b1588000eb22fe17765fbdfcd9a27
decision: approved
---

# Review：FEA-14-AI-1（r2 独立复核）

## 0. 审查对象与环境

| 项 | 值 |
|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` |
| 被审 head | `2737d035ae3b1588000eb22fe17765fbdfcd9a27`（开始 18:37:47 与结束复核实测均未变） |
| 提交链 | `13d9e39e1`（实现）→ `aac1aba9d`（v14 测试适配）→ `9e1ec59f7`（初版证据）→ `41d54395a`（初版证据 pin，被 r1 审）→ `1b5bdb1f2`（r1 处置）→ `17618c0fb`（r1 处置证据）→ `2737d035a`（证据 pin 回填，HEAD） |
| diff 基线 | `36c4376d1`（卡面 `base_commit`；= EDIT-1 收口 + AI-1 冻结提交） |
| 审查时点 | 2026-11-10 18:37:47 – 18:52 前后 +08:00（关键命令时点见 §5） |
| 环境 | Windows；Python 3.14.6 / pytest 9.1.1；.NET SDK 10.0.401（测试目标 net9.0，构建产物为既有 `bin/obj`）；PowerShell 7.6.8 |
| 只读纪律 | 未 commit / push；未改源码、测试、契约、卡面或证据；探针脚本与复跑日志均在 `%TEMP%`（`ai1_r2_*.py`、`ai1-r2-*.log`）；探针/隔离库全部在 `%TEMP%`，未写真实 `%APPDATA%`；`dotnet test` 仅生成被忽略的构建产物，`git status` 未出现 |
| 工作树 | 开始 `git status --porcelain` 为空；写入本报告前仍为空、HEAD 未变；结束后仅本报告 `??` |

说明：本次不采信卡面自述。所有 PASS 均来自本次实测、逐行脚本比对或源码/字节核对；未实测项列入 §6 NOT_RUN。

## 1. 结论

**`approved`。** P0 = 0，P1 = 0，**P2 = 0**，P3 = 7（F-03/F-04/F-05/F-08 为 r1 已登记/接受的 P3 继续有效；F-06 残余注释 + N-01/N-02 为 r2 新登记；均不阻断）。

r1 的两条 P2 均已真正关闭：

- **F-01（P2）已关闭**：P23 的「引用重指派 + 软删」已收敛为 store 单一事务 `delete_with_reassign`（同一个 `with self._conn` 内 UPDATE refs + UPDATE templates），service 只调用该方法；故障注入测试真实存在并通过；本次独立故障注入复现「软删语句抛错 → 引用仍指向目标、替换侧为空、目标仍可见且 `deleted_at IS NULL`」，恢复后重试删除成功。
- **F-02（P2）已关闭**：C-07 正式成员表 `Changed` 已为 `（事件）`；自写逐行比较 83/83 行（79 方法 + 4 非方法）`ALL_MATCH: True`；pin = `8ccaba05…` = 文件 SHA-256；FROZEN §1/§1B/§2#3/§5 与载体自洽；`--check` EXIT 0；`verify_pins` 18/18。

产品面未发现新 P0/P1/P2：schema v14 additive、v1–v13 迁移 NAME/SQL 逐字节不变、v13→v14 行级 preserved；P21–P25 行为与 typed 错误未回退；Host 六处 5 方法签名一致、NullHost 降级不抛；证据 provenance 与 allowed_paths 符合；18 个 pin 中仅 C-07 变化。

## 2. F-01–F-09 逐项关闭表

| ID | r1 级别 | r2 判定 | 本次证据 | 状态 |
|---|---|---|---|---|
| **F-01** | P2（阻断） | **已关闭** | `src/infrastructure/sqlite/prompt_templates.py:99-110` 新增 `delete_with_reassign`：一个 `with self._conn` 内先 `UPDATE OR REPLACE prompt_template_references` 再 `UPDATE prompt_templates SET deleted_at`；`src/application/ai/prompt_templates.py:121-124` 只调用该方法，旧的 `reassign_references`+`update_template` 组合已不在删除路径。测试 `tests/storage/test_prompt_templates.py:163-204` 用代理连接在软删语句抛 `RuntimeError`，断言引用仍在目标、目标仍可见；本次定向 pytest 8 passed。**独立探针**（`%TEMP%\ai1_r2_service.py`）：注入后半删复现失败，输出 `refs still on target: [('translation','owner-x','label-x')]`、`refs empty on replacement: []`、`target still visible: True`、`target not soft-deleted in DB: True`；恢复后 `delete succeeds after recovery: True`、引用移至 replacement。 | **closed / fixed** |
| **F-02** | P2（阻断） | **已关闭** | 自写脚本 `%TEMP%\ai1_r2_c07.py` 解析 `python tools/generate_api_inventory.py` stdout 与 `doc/plan/FEA-C07_API_INVENTORY.md` 正式成员表：`IReaderProgressSink 1/1 match=True`、`IHostController 83/83 match=True`（79 方法 + 4 非方法）、`IRunController 6/6 match=True`，`ALL_MATCH: True`；`Changed` 行为 `Changed（事件）→ EventHandler?`，另 3 个非方法为（属性），与 C# 源码 `event EventHandler? Changed` 等逐一相符。`Get-FileHash` = pin `8ccaba05cbc21eec04a366f8bfa2be2dea4515ba90e6d5aab95b11a7c47f0509`；v1.7 原 pin `89781583…` 经 `git show 36c4376d1:…` 原始字节 SHA-256 复核一致；FROZEN §1（v1.8 + v1.7 保留）/§1B/§2#3 `1/79/6=86`/§5 与载体、README、卡面 AC5 同步；`--check` EXIT 0；`verify_pins` 18/18。 | **closed / fixed** |
| **F-03** | P3（接受/登记） | **登记继续有效** | 独立探针复现：A、B 对同一 `(kind,owner_id)` 各有 label，`delete(A→B)` 后 replacement 只剩 `(B, translation, owner-z, 'A-label')`，B 原 label 被 `UPDATE OR REPLACE` 覆盖（引用身份 kind+owner 不丢）。卡面 `doc/tasks/FEA-14-AI-1.md:89` 与 `verification/FEA-14-AI-1/README.md:34` 已登记，留 AI-2/后续 errata。 | **accepted / registered** |
| **F-04** | P3（接受） | **接受继续有效** | 探针：新建 v1 → 更新 v2 → 相同 name/body 再保存为 v3（no-op 也递增）；与卡面「每次保存 +1」一致，卡面 `:90`、README `:35` 已写明。 | **accepted** |
| **F-05** | P3（接受/登记） | **登记继续有效** | 探针：用户模板可命名为内置名 `Default Translation`；`mine` 与 `Mine` 可并存；DB partial unique index 对未软删重名插入抛 `IntegrityError`（软删后名字可复用）；卡面 `:91`、README `:36` 已登记「不覆盖内置名、不做大小写/空白规范化，待 ADJ」。 | **accepted / registered** |
| **F-06** | P3（接受/建议修） | **部分关闭（残余 P3，不阻断）** | 已把 `LATEST - 1` 断言改为 `13`、全链改为 `14`，并在 `tests/storage/test_issue_markers.py:58-60` 补注释说明「测试现跨 v13→v14」；但 `:65` 内联注释仍写 “A real v12 book/chapter/page row must survive the v13 table creation”，与当前 pre-state 不符（应为 v13 行存活到 v14）。只影响测试可读性，不影响产品；不阻断。 | **partially closed / P3 residual** |
| **F-07** | P3（接受） | **已关闭** | `apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs`：未知 `templateId` Save → null、Save/Copy 校验名称唯一、Delete 校验 replacement（必填/非自身/存在/非内置）、引用按模板 id 存储并在删除时迁移；`PromptTemplatePortTests.cs` 扩为 5 个测试（NullHost 降级、版本、内置只读/复制、删除迁移引用、与 Core 同型拒绝）。本次 `dotnet test --filter FullyQualifiedName~PromptTemplatePortTests` = 5 passed / 0 failed，全量 888 passed。与 Core 语义核对未发现掩盖真实差异（差异仅剩 Fake 不校验 name/body 长度上限等测试替身简化，属可接受）。 | **closed / fixed** |
| **F-08** | P3（登记/接受） | **已裁决登记** | 卡面 §裁决 `:81` 明确「DDL 计划 §2.4 `version`（不可变）→ 调用方不可指定、由 Core 单调 +1 管理」；实现 P22 更新 +1、P24 副本 v1。README `:39`、卡面 r1 处置 `:94` 可查，跨卡口径已落盘。 | **accepted / registered** |
| **F-09** | P3（观察） | **已关闭** | `tests/storage/test_upgrade_schema_data.py:97-103` 的 `LATEST_TABLES` 已补 `font_assets`、`reading_preferences`、`reading_bookmarks`、`issue_markers`、`prompt_templates`、`prompt_template_references`；与 v10–v14 实际建表（v10 两表 / v11 一表 / v12 无表 / v13 一表 / v14 两表）逐一对应；回归 1268 passed 覆盖。 | **closed / fixed** |

**r2 新登记 P3（均不阻断）**：

| ID | 级别 | 文件 / 行 | 问题 | 建议/状态 |
|---|---|---|---|---|
| **N-01** | P3 | `src/infrastructure/sqlite/prompt_templates.py:90-97` | `reassign_references` 在 F-01 修复后已无调用方，且 docstring “delete already shadows” 具误导性；未来删除路径若误用会重新引入「重指派/软删分两事务」缺陷。 | 建议后续维护卡删除或私有化；**registered** |
| **N-02** | P3 | `doc/tasks/FEA-14-AI-1.md:151` | Closeout Record 仍写「**r1 独立复核待派发**」，而 r1 已完成 `changes_requested`、已处置并生成证据；卡面簿记落后一拍。 | 收口时改为 r1→处置→r2 实际链；**registered** |

**r1 已通过项无回退**：

| r1 已通过项 | r2 复核 | 证据 |
|---|---|---|
| P21–P25 wire 形状与 typed 错误 | 无回退 | `tests/core/test_prompt_template_wire.py` 自 r1 后未改；8 passed；独立探针覆盖 `TEMPLATE_NAME_EXISTS`/`TARGET_NOT_FOUND`/`INVALID_REQUEST` 路径 |
| Host 六处 5 方法 | 无回退 | 脚本逐文件抽取参数表：`IHostController`/`HostController`/`NullHostController`/`HostRuntime`/`CoreServiceClient`/`FakeHostController` 五方法参数逐字一致 |
| NullHost 降级 | 无回退 | 5 个端口测试中 `NullHost_PromptTemplatePorts_DegradeWithoutThrowing` 通过 |
| schema v14 additive | 无回退 | 独立探针：v1–v13 `NAME`/`SQL` 逐字节相同（13/13）；v14 仅两表 + 两索引 |
| allowed_paths / 契约范围 | 无回退 | 35 条变更路径全部命中卡面 allowed_paths，`OUTSIDE []`；18 个 pin 源仅 C-07 变 |
| 证据 provenance | 已重生成且一致 | 见 §4 #5 |

## 3. AC 逐项判定

| AC | 判定 | 依据（本次实测） |
|---|---|---|
| **AC1 数据面/v14** | **MET** | 独立探针：base `36c4376d1` 的 `MIGRATION_V1..V13_{NAME,SQL}` 与 HEAD 逐字节相同（13/13）；`default_migrations()` = v1..v14；v14 SQL SHA-256 `3142ecfc41eea13c7f126843ae425ea0fba3b9bd012e518432c1f66aa0eaaf97`；v13 库（含真实 book/chapter/page/issue_markers 行）升级 v14：`APPLIED [14]`、`ROWS_PRESERVED True`（`schema_migrations`/`application_metadata` 元数据行除外，属迁移簿记预期变化）、两新表 0 行、两索引存在。 |
| **AC2 P21/P24** | **MET** | P21 键集精确 `{template_id,name,version,builtin}`、`builtin_count=2`、内置在前；P24 缺省名 `Default Translation (copy)`、version=1、body 与内置一致、`builtin=false`；显式名/重名/未知 builtin 均 typed；wire 测试与独立探针一致。 |
| **AC3 P22** | **MET** | 新建 v1；按 id 更新 v2（no-op 亦 v3）；跨模板与更新重名 → `TEMPLATE_NAME_EXISTS`（wire `conflict`）；空/空白/超长 name、空白 body → `INVALID_REQUEST`；内置 id → `INVALID_REQUEST`；未知 id → `TARGET_NOT_FOUND`。 |
| **AC4 P23/P25** | **MET** | P25 返回 `{kind,owner_id,label}`、无引用空数组、未知/软删 → `TARGET_NOT_FOUND`；P23 replacement 缺失/空/自身/内置/不存在均 typed；成功路径引用行在同一事务内指向 replacement、目标软删后 P21 不可见、P25/P23 再触达 → `TARGET_NOT_FOUND`；无引用删除也强制 replacement。**F-01 已修复，卡面「同一事务」口径成立。** |
| **AC5 契约/门禁** | **MET** | 自写逐行：79 方法 + 4 非方法共 83/83 = stdout，`ALL_MATCH: True`（含 `Changed（事件）`）；S5 计划节无数据行（25/25 全部落地）；pin `8ccaba05…` = `Get-FileHash`；`--check` EXIT 0；`verify_pins` 18/18；FROZEN §1/§1B/§2#3/§5 与载体自洽。**r1 判 AC5 NOT MET 的原因（`Changed` 行与 stdout 不一致）已被 F-02 修复消除。** |
| **AC6 证据** | **MET** | 4 日志头均 `HEAD=1b5bdb1f2eed2d1ab8f8f531c8d8651b32158ba4` + 顺序 dirty；计数 pytest-ai 8 / regression 1268 / App 888 passed·0 failed·11 skipped / pins 18/18 + API 1/79/6=86；卡面 5 行 sha256 与工作树文件逐一匹配；`17618c0fb` tree 含 README + 4 日志；卡面 5 行 commit 均 `17618c0fb`；本次复跑计数一致（§5）。 |

## 4. 必查项判定

| # | 必查项 | 判定 | 本次证据 |
|---|---|---|---|
| 1 | schema v14 additive / v1–v13 字节不变 / v13→v14 行级 preserved | **PASS** | 见 AC1；另确认 `application_metadata.schema_version` 由 13→14 属迁移簿记，业务表行级快照全等 |
| 2 | C-07 逐行 = stdout / pin / S5 空 / 4 非方法标注 | **PASS** | 83/83 行 `ALL_MATCH: True`；`Changed（事件）`、`Snapshot/StartRequests/ExportDirectorySuggestion（属性）` 与源码 `event`/属性声明一致；pin `8ccaba05…`；S5 表仅表头无数据行；v1.7 pin `89781583…` = base 原始字节 SHA-256 |
| 3 | P23 事务原子性 | **PASS** | 单一 store 方法 + 单一 `with self._conn`；故障注入测试存在且通过；独立探针证明失败时引用未移动、目标未软删，恢复后重试成功 |
| 4 | Fake 保真（F-07） | **PASS** | 未知 id Save→null、名称唯一、Delete replacement 四类校验、引用按 id 迁移；5 个端口测试通过；与 Core 语义逐路径核对未见掩盖真实差异 |
| 5 | 证据 provenance | **PASS** | 4 日志 HEAD=`1b5bdb1f2`；计数 8/1268/888/18+79-86；5 个 sha256 与卡面逐行一致（按工作树字节 `Get-FileHash`）；`17618c0fb` tree 含同 5 文件，且 `git diff --name-status 17618c0fb..HEAD` 仅卡面 pin 行（证据未被改写）；卡面 commit pin=`17618c0fb`。注：日志工作树为 CRLF、Git blob 因 `core.autocrlf=true` 归一为 LF，sha256 以工作树为准，属仓库既有证据口径 |
| 6 | allowed_paths / 范围 | **PASS** | `git diff --name-only 36c4376d1..HEAD` = 35 路径；自写 glob（`**` 语义）逐路径匹配 30 条 allowed_paths，`OUTSIDE []`；`doc/contracts` 零改动 |
| 7 | 18 pins / 其它契约字节 | **PASS** | 18 个 pin 源文件 base↔HEAD blob 逐一比较：仅 `FEA-C07_API_INVENTORY.md` 变化；`doc/plan` 另仅 `FEA-CONTRACT-FROZEN-C07.md`（记录）变化；`doc/reviews` 仅新增 AI1 载体与 r1 报告；无其它契约字节改动 |
| 8 | 扫新 P0/P1/P2 | **未发现** | 重点核对：① 事务方法回滚 = 实测正确；② Fake 改动未放宽产品路径断言；③ C-07 其它 82 行及 4 个非方法行与 stdout 全等；④ 删除语义无新半写路径；⑤ F-03 覆盖语义仍为已知登记项。仅见 §1 的 P3（残余注释/死方法/卡面旧文字） |

## 5. 门禁与测试表

| # | 命令 / 探针 | 时点（2026-11-10 +08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `python -m pytest tests/storage/test_prompt_templates.py tests/core/test_prompt_template_wire.py -q` | 18:39:14 – 18:39:17 | `8 passed in 1.83s` | 0 |
| 2 | `python -m pytest tests/storage tests/core tests/fea09/test_v7_migration.py tests/fea11/test_source_gate_unify.py -q` | 18:39:11 – 18:41:16 | `1268 passed, 1 warning in 124.56s` | 0 |
| 3 | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --nologo` | 18:39:11 – 18:45:06 | 通过 888 / 失败 0 / 跳过 11 / 总计 899，5m45s（与 #2 并行，仅时长变长；计数与证据 5m36s 一致） | 0 |
| 4 | `dotnet test ... --filter "FullyQualifiedName~PromptTemplatePortTests" --no-build` | 18:45:20 – 18:45:21 | 通过 5 / 失败 0 | 0 |
| 5 | `pwsh -NoProfile -File tools/governance/check.ps1` | 18:42:02 – 18:42:03 | `Governance check: PASS (3 warnings)` | 0 |
| 6 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-14-AI-1.md` | 18:42:03 – 18:42:04 | `Governance check: PASS (3 warnings)` | 0 |
| 7 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 18:42:05 | `PIN AUDIT: PASS (all 18)`；`OK C07 8ccaba05cbc2` | 0 |
| 8 | `python tools/generate_api_inventory.py --check` | 18:42:05 | 渲染计数 `IReaderProgressSink 1 / IHostController 79 / IRunController 6 / 合计 86`；`OK: rendered counts match FEA-C07 doc` | 0 |
| 9 | 自写 C-07 逐行比较 `%TEMP%\ai1_r2_c07.py` | 18:38 前后 | `IReaderProgressSink 1/1`、`IHostController 83/83`、`IRunController 6/6`，`ALL_MATCH: True`；79 方法 + 4 非方法 | 0 |
| 10 | 自写 schema 探针 `%TEMP%\ai1_r2_schema.py` | 18:40 – 18:41 | v1–v13 逐字节相同；`APPLIED [14]`；`ROWS_PRESERVED True`；两新表 0 行；两索引存在；v14 SQL sha256 `3142ecfc…` | 0 |
| 11 | 自写 P21–P25/事务/F-03–F-05 探针 `%TEMP%\ai1_r2_service.py` | 18:41 – 18:44 | 全部预期：typed 路径、P23 成功/失败回滚、no-op v3、内置同名/大小写、partial unique index、REPLACE label 覆盖 | 0 |
| 12 | 自写 allowed_paths 检查 `%TEMP%\ai1_r2_scope.py` | 18:42 | `CHANGED 35`、`OUTSIDE []`、`SCOPE_OK True` | 0 |
| 13 | 18 pin 源 base↔HEAD blob 比较（PowerShell + `git rev-parse`） | 18:41 | 17 SAME / C07 CHANGED；`doc/plan` 仅 C-07 inventory + FROZEN-C07 变化 | 0 |
| 14 | 证据字节/树核对（`git ls-tree 17618c0fb`、`Get-FileHash`、`git show`） | 18:46 | 5 文件齐；5 个 sha256 与卡面一致；日志头 `HEAD=1b5bdb1f2eed2d1ab8f8f531c8d8651b32158ba4`；卡面 commit pin `17618c0fb` | 0 |
| 15 | `git diff --check 36c4376d1..HEAD` | 18:45 | 无 whitespace 错误 | 0 |

补充：`git diff --name-status 17618c0fb..HEAD` 仅 `doc/tasks/FEA-14-AI-1.md`（5 行 commit pin 回填），证据文件在 `17618c0fb` 后未被改写。

## 6. NOT_RUN（如实）

- **真实 Host↔Core 进程级 IPC**：5 个新 `CoreServiceClient` 方法未对活 Core 调用；仅静态核对序列化/解析 + C# 全量编译 + 5 个端口测试（NullHost/Fake）间接覆盖。
- **P24 真实 Core 端到端**：客户端缺省 name 投射空串、version=1 的 limitation 仅登记，未以活 Core + P21 刷新验证。
- **模板 UI/编辑器/预览、内置模板最终集合与文案**：属 AI-2/UI 卡，NOT_RUN。
- **真实 AI 模型/网络调用**：PREQ §6 明确本清单不触发，NOT_RUN。
- **引用行写入方（译文/任务/规则）**：本卡不创建引用；P23 重指派仅用 fixture/探针行验证；未来写入方的 label 合并/并发语义未测。
- **并发**（同一模板并发 save/delete、删除期间重新指派）、**万级模板性能**、**真实大库迁移**：NOT_RUN。
- **FEA-15 正式验收声明**：未审。
- 本次 `dotnet` 与 pytest 回归并行执行，未跑串行基线；计数一致，仅时长变化。
- **跨平台/全新克隆的证据 sha256 复现**：本报告按仓库既有口径对工作树字节做 `Get-FileHash`（日志工作树 CRLF、blob LF，`core.autocrlf=true` 下 Windows 检出可复现）；未在 Linux 检出验证。

## 7. 处置建议

1. **F-01/F-02 可关**：r2 结论为 `approved`；建议 DSH 收口时把 `doc/plan/FEA-CONTRACT-FROZEN-C07.md` §1B「v1.8 … r2 复核待派发」与 §1B 处置行更新为「AI-1 r2 approved，v1.8 字节已复核并重冻」，并同步卡面 `Closeout Record`（当前仍写「r1 独立复核待派发」，P3）、`reviewer`/`reviewer_kind` 与 STATUS/PLAN/LEDGER 生命周期。
2. **P3 清理（可随后续维护卡）**：① 删除或私有化 `src/infrastructure/sqlite/prompt_templates.py:90-97` 现已无调用方的 `reassign_references`（其 docstring “delete already shadows” 已误导，易被未来删除路径误用而重新引入 F-01）；② 修正 `tests/storage/test_issue_markers.py:65` 的 v12→v13 旧注释（F-06 残余）；③ 卡面 Closeout 行更新为 r1/r2 实际链。
3. **保留登记项**：F-03（REPLACE 覆盖 label）、F-05（内置名/规范化范围）继续作为 AI-2/后续 errata 输入；F-08 版本口径（调用方不可指定、Core 单调 +1）作为跨卡口径保留。
4. 本报告只对 `2737d035a` 有效；head 变化即失效，需重新审查。

## 8. 审查者声明

本报告由 lead 会话 `session-408d4e24-3789-4111-acde-983899601dad` 派发的**全新上下文子 agent**出具；审查者未参与 FEA-14-AI-1 的实现、测试、证据生成或任何返修，审查期间只读。唯一仓库写入为本报告 `doc/reviews/FEA-14-AI-1-r2.md`；探针脚本、隔离数据库与本轮复跑日志全部在 `%TEMP%`，未写真实 `%APPDATA%`，未 commit/push（`dotnet test` 的忽略构建产物除外，`git status` 未见）。PASS 仅基于本次 2026-11-10 18:37–18:52 的实测、逐行脚本比对与源码/字节核对；未执行项已列入 §6，未把未实测项写成 PASS。写报告前复核：`git rev-parse HEAD` = `2737d035ae3b1588000eb22fe17765fbdfcd9a27`（未变），`git status --porcelain` 为空；写报告后复核（18:50:20）：HEAD 仍为 `2737d035a`，`git status --porcelain` 仅 `?? doc/reviews/FEA-14-AI-1-r2.md`，`check.ps1`（默认 + `-TaskPath`）复跑 `PASS (3 warnings)` / EXIT 0。本报告只对 `2737d035a` 的字节有效；head 变化即自动失效。
