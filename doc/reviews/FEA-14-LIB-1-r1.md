---
task_id: FEA-14-LIB-1
reviewer: 独立子 agent（全新上下文，未参与实现；只读）
reviewer_kind: subagent
author: dsh
base_commit: f97f54476
reviewed_head: 83e45cfe5
decision: changes_requested
---

# Review：FEA-14-LIB-1（r1）

## 0. 审查对象与环境

- 仓库 `G:\CODEX\New Manga`，分支 `main`；审查者由 lead 会话 `session-408d4e24-3789-4111-acde-983899601dad` 派发，为全新上下文子 agent，未参与本卡实现。
- **HEAD = `83e45cfe54fb05bd0f4b0f6620e333b2c8e8d03e`**；base = `f97f54476`。审查开始 `2026-11-10T15:05+08:00`、结束 `15:15+08:00`，两次 `git status --short` 均 **clean**，HEAD 未变。
- 变更面：`f97f54476..83e45cfe5`，**29 文件 / +843 / −29**（Core schema-v12、service、wire、Host 三层、C-07 UNFREEZE、7 个测试、证据）。
- 只读纪律：仓库内唯一写入为本文件；探针脚本与临时库写在 `%TEMP%`，未改源码/测试/契约/卡面/证据，未 commit/push。
- 本报告只对 `83e45cfe5` 的字节有效；head 变化即自动失效。

## 1. 结论

**`changes_requested`**（P0=0 / **P1=2** / **P2=4** / **P3=7**）。

正面：schema v12 确认 additive，v1–v11 迁移 SQL/名称逐字节未变；`custom_rank` 在 get/list/insert/update 四路径一致；patch 保留未提供字段、title 非空、重排全覆盖（缺/多/重复）、kind→方向不变量、重排后 sort_order 连续，均经实测成立；Host 三层签名一致且降级不抛；C-07 pin 与文件 sha256 一致、`verify_pins` 18/18、`--check` 69/76、`check.ps1` 双模式 PASS、定向 pytest 7 passed、storage+core+fea09+fea11 回归 **1245 passed**、过滤 App.Tests 22 passed。

阻断项：**P5/P6/P8 的“书不存在”错误映射错误（实测返回 `UNKNOWN/internal`，不是 `TARGET_NOT_FOUND`）**；**P5 `tags` 替换语义完全未实现，AC1 却标 MET**。另有 Host P8 投影读错键、create 的 sort_order 冲突、C-07 成员表未同步、allowed_paths 越界 7 文件等 P2。

## 2. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R-01 | **P1** | `src/bootstrap/core_service.py:5153,5167,5207`；泛化兜底 `:7076-7078` | P5/P6/P8 捕获的是 `ChapterNotFound`，而 `patch_book_metadata` / `reorder_chapters_strict` / `create_chapter_with_metadata` 对“书不存在”抛的是 **`BookNotFound`**（`src/application/library/errors.py:10-13`，二者为兄弟类）。异常逃逸到普通通道兜底，返回 `code=UNKNOWN, category=internal, message="Reader or export operation failed"`。违反 AC1/AC4“无书 → typed”、PREQ §8“错误一律 typed code”及 README 声称的 `TARGET_NOT_FOUND`。 | 临时库探针（`%TEMP%\lib1_review_probe.py`）：P5/P6/P8 传 `book_id="nope"` 均返回 `UNKNOWN/internal`；P7 缺失章返回 `TARGET_NOT_FOUND` 正确。 | 三处改捕 `BookNotFound`（该名已由 `:210` 导入），补 P5/P6/P8 的 wire 负例；同时把该分支兜底消息改为与 library 相符或使用 typed 错误。 | open |
| R-02 | **P1** | `src/application/library/service.py:207-215`（白名单）、`src/bootstrap/core_service.py:5148-5157`；卡面 `doc/tasks/FEA-14-LIB-1.md:59,66`；PREQ §8 P5 | Scope §1 与 AC1 明确要求“tags 替换语义”，PREQ §8 P5 的 `patch{…,tags?}` 也列了 tags；实现白名单不含 `tags`，传入即 `INVALID_REQUEST`。AC1 仍标 `<<MET>>`，与 `verification/FEA-14-LIB-1/README.md:31,39` 自认 `tags` = NOT_RUN 自相矛盾。 | 探针：P5 patch `{"tags":["t1"]}` → `INVALID_REQUEST`（"Book metadata values are invalid"）。仓库已有 `add_book_tag`/`remove_book_tag`/`list_tags_of_book`（`src/infrastructure/sqlite/library.py:310-332`）与 ports 声明，实现无需 schema 变更。 | 二选一：实现 tags 替换（关联表在 Core 事务内替换）并补测试；或由 DSH 出具范围/AC errata，把 tags 正式移出 AC1/P5 并把 AC1 改为 PARTIAL/MET-with-limitation。不得维持“未实现 + MET”。 | open |
| R-03 | P2 | `apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs:1695-1700`；DTO `:28` | P8 响应只有 `chapter_id,title,kind,number`（`core_service.py:5211-5216`），客户端却用 `ReadInt(result,"import_order")` 填 `ChapterSummary.SortOrder`；缺键时 `ReadInt` 返回 0（`:2239-2242`）。结果：新建章在 Host 投影中 **SortOrder 恒为 0**，且响应里的 `kind` 被丢弃。属于静默错误投影，LIB-2 UI 会直接踩中。 | 代码逐行核对；无任何 C# 测试覆盖该新方法。 | 让 Core 在读响应中增加可选键（PREQ 允许实现加可选键）并读 `sort_order`/`import_order` 的正确键；或引入含 `kind`、正确序号的专用 DTO；补客户端映射测试。 | open |
| R-04 | P2 | `src/application/library/service.py:255-272`（`:269-270`） | `create_chapter_with_metadata` 在给定 `import_order` 时同时把 `sort_order` 覆盖成同一值。实测已有 C1(sort=1)、C2(sort=2) 后，创建 `import_order=1` 的新章得到 sort=1，与 C1 重复，`ORDER BY sort_order` 出现并列、sort_order 序列不再唯一/连续，与 AC3 重排后“连续重写”的排序不变量冲突。 | 探针：`after = [('C1',1,1), ('Collide',1,1), ('C2',2,2)]`。 | 保留用户 `import_order`，`sort_order` 应追加（max+1）或按插入位整体位移；补重复 import_order/插入位测试。 | open |
| R-05 | P2 | `doc/plan/FEA-C07_API_INVENTORY.md:20,24,102,104,134`；`doc/plan/FEA-CONTRACT-FROZEN-C07.md:46` | C-07 只改了统计行（65→69、72→76），**正式成员表仍是 54 行**（无 FONT P1–P4、LIB P5–P8），S5 计划节仍写“**尚未实现**”“统计仍是代码实测 61”“目标 79/86”，与冻结记录 §3(a)“把对应行从计划追加移入正式成员表”直接冲突；`generate_api_inventory.py --check` 只比对计数行，掩盖了该不一致。FROZEN 记录 §2 条件 3 也仍写 `1/54/6=61`。 | `--check` EXIT 0（1/69/6=76）；逐行计数正式表 54 行。 | 在本次 UNFREEZE 内把 P1–P8 移入正式成员表、更新 §2/§5 与 S5 节口径并重算 pin（`verify_pins` 随动）；或由 DSH 明确登记为后续收口并给出 pin 计划。 | open |
| R-06 | P2 | 任务卡 `allowed_paths`（`doc/tasks/FEA-14-LIB-1.md:21-43`） | 29 个变更文件中 **7 个不在 allowed_paths**：`src/infrastructure/sqlite/schema.py`、`src/domain/books/entities.py`、`doc/reviews/CONTRACT-UNFREEZE-2026-11-10-LIB1.md`、`tests/storage/test_fonts.py`、`tests/storage/test_upgrade_schema_data.py`、`tests/fea09/test_v7_migration.py`、`tests/fea11/test_source_gate_unify.py`。其中 schema/entities 是本卡核心实现，UNFREEZE 载体是 C-07 流程必需，4 个测试是 v12 适配必需；协作协议 §4 要求“超出 allowed_paths 时暂停越界部分，在 Task 提出范围变更”，FONT-1 先例也把 schema.py 与这 4 个测试、`doc/reviews/CONTRACT-UNFREEZE-*.md` 列入清单。 | 逐路径匹配脚本：`changed=29, out_of_allowed=7`。 | 由 DSH 补全 allowed_paths 并记录“释放清单不完整”的更正；不追溯判为越权内容，但清单必须与交付面对齐。 | open |
| R-07 | P3 | `doc/plan/FEA-CONTRACT-FROZEN-C07.md:15-18,26-28,38,75-82` | v1.5 的冻结记录只替换了 sha 行：§1B“最后一次独立复核”仍止于 v1.2；§2 条件 3 仍写 `1/54/6=61`；§5 变更记录最后一行仍是 v1.2（v1.4/v1.5 均无）；“前一 pin”链只剩 v1.2/v1.1，v1.4 仅记在新 UNFREEZE 载体中。旧 pin 字节未丢（载体 §前 pin 保留），但冻结记录本身不可自洽追溯。 | 读文件 + `verify_pins` C07=`9c1eb974342a` PASS。 | 在冻结记录补 v1.5 行、§1B 复核引用、§2 条件 3 的 69/76 口径；保留 v1.4 原值。 | open |
| R-08 | P3 | `verification/FEA-14-LIB-1/logs/*`（4 个日志）；`README.md:11-16,31-41` | 4 个 Canonical 日志头均记 `HEAD=f97f54476`（实现前 base，工作树 dirty），最终交付 head 为 `83e45cfe5`（提交时间 15:03:39，日志 14:57–14:59），无法把证据钉到被审 head 字节。另 README AC3 写“未知章 → ChapterNotFound”，实际 strict reorder 对未知/缺失 id 一律 ValueError→INVALID_REQUEST（ChapterNotFound 在该路径不可达）；AC1 行称 wire P5 `TARGET_NOT_FOUND`，与 R-01 实测相反。 | 日志头逐行对照；探针 P6 extra id → INVALID_REQUEST。 | 在最终 head 重生成日志或注明生成时 HEAD/dirty 状态；修正 README AC1/AC3 描述，并把 R-01/R-02 结果同步进结论表。 | open |
| R-09 | P3 | `src/application/library/service.py:22,243` | `patch_chapter_metadata` 用 `datetime.now(timezone.utc).isoformat()`（微秒精度）写 `updated_at`，而全库统一用 `domain.books.entities.utc_now()`（毫秒，`timespec="milliseconds"`）；同一实体的时间戳格式不一致。 | 代码对照（`:179-183` 走 `apply_edit`→`utc_now`）。 | 改用 `utc_now()`；`import datetime` 移到文件头。 | open |
| R-10 | P3 | `tests/storage/test_fonts.py:50`；`tests/storage/test_library_metadata.py:33-40`；`FakeHostController.cs:254-279` | ① `read_schema_version(conn) == LATEST >= 11` 恒真，不再钉住 v11 版本语义；② `test_v12_adds_custom_rank_and_keeps_legacy_rows` 名字承诺 legacy row 守恒，但只迁移空库并断言列存在；③ Fake 新增 `LastReorderCalled/LastBookMetadata/...` 无任何测试消费，4 个新 C# 客户端方法零测试（R-03 由此逃逸）。 | 测试逐行；grep Fake 字段无测试引用。 | 恢复 v11 精确断言（或改为 `LATEST == SCHEMA_VERSION_V12` + 列存在）；给 v12 测试插入 v11 章行后再升级；补 wire/Host 负例。 | open |
| R-11 | P3 | PREQ §3/§8 P7；`verification/FEA-14-S5-PREQ-1/ddl-v10-plan.md:51-53`；卡面 AC2 | PREQ 把 P7 `kind/custom_rank/number` 语义指向 DDL v10 计划：`kind`=volume/episode/extra、`number_value` 数字排序、`books.normalized_title` 唯一索引；卡面/实现改成 `kind`=paged/webtoon、`number`=自由文本 `chapter_number`，且未实现 `kind` 列、`number_value`、`normalized_title`，卡面 out_of_scope 只写了 Volume，没有这三项 deferral 记录（ADJ §3 只把“重名规范化是否 NFKC”留用户裁决）。 | 三份文档对照。 | 由 DSH 裁一次：更新 DDL 计划的 LIB 口径与 P7 语义，或在卡面登记三项 deferral；不得让 PREQ/DDL 与实现静默分叉。 | open |
| R-12 | P3 | `custom_rank` 全链；PREQ §8 P6；卡面 AC3 | `custom_rank` 目前是 write-only：无读投影/Host 面，重排也不参考它；P6“自定义排序保位、数字排序重排”未实现（AC3 只要求 ordered_ids 严格重排，字面可过）。 | grep：`custom_rank` 仅 schema/entity/repo/patch 测试出现。 | 登记为 LIB-2 输入（自定义排序语义未实现）；若本卡声称 P6 语义，则需实现或改口径。 | open |
| R-13 | P3 | `src/bootstrap/core_service.py:5163,5201`；`service.py:229-231` | 边界小项：P6 拒绝空 `ordered_ids`（空书 no-op 无法表达）；P8 `isinstance(True,int)` 会把 bool 当 0/1 import_order；`custom_rank` 传 float 会静默 `int()` 截断；P8 允许重复 `import_order`（与 R-04 同源）。 | 代码核对。 | 收紧类型判断（排除 bool/float）或登记；空书语义补测试。 | open |

## 3. AC 逐项

| AC | 判定 | 依据 |
|---|---|---|
| AC1 书元数据 | **PARTIAL** | patch 保留未提供字段、title 非空、未知字段拒绝均已实测；但 `tags` 替换未实现（R-02），且 wire“无书”返回 `UNKNOWN` 而非 `TARGET_NOT_FOUND`（R-01）。卡面 `<<MET>>` 不成立。 |
| AC2 章元数据 | **MET** | kind/custom_rank/number/title/subtitle/notes 均落库；非法 kind→INVALID_REQUEST；无章→TARGET_NOT_FOUND；webtoon→vertical、paged→rtl 不变式实测成立。仅 R-09 时间戳格式 P3。 |
| AC3 章重排 | **MET** | 缺/多/重复→INVALID_REQUEST；成功路径 sort_order 连续重写（探针 1,2）；读取顺序与请求一致；验证先于写库。R-12 的“自定义/数字排序”不在 AC3 字面内，但应在 limitation 登记。 |
| AC4 创建带元数据章 | **PARTIAL** | title/kind/number/import_order 落库、响应四键、webtoon 方向继承均成立；但父书不存在→`UNKNOWN`（R-01），Host 投影 SortOrder 恒 0 且丢 kind（R-03），`sort_order=import_order` 造成重复/断档（R-04）。 |
| AC5 迁移/契约/门禁 | **PARTIAL** | v12 additive、v1–v11 字节不变、旧 v11 行升级后字段无损 + `custom_rank=NULL`、`--check` EXIT 0（69/76）、pins 18/18 均通过；但 P5 形状缺 tags（R-02），C-07 正式成员表/S5 节未同步（R-05），冻结记录 v1.5 记录不全（R-07）。 |
| AC6 证据 | **MET（带 R-08 P3）** | 定向 pytest 7 passed、回归 1245 passed、App 全量日志 874/0/11、日志含 EXIT、NOT_RUN 已登记；但 README 对 AC1/AC3 的描述不实，须随 R-01/R-02 更正。 |

## 4. 必查项逐项判定

| # | 必查项 | 判定 | 说明 |
|---|---|---|---|
| 1 | v12 additive、v1–v11 字节/校验和未改、custom_rank 四路径一致 | **CLOSED** | 脚本逐项比对 base/head 的 `MIGRATION_V1..V11_{NAME,SQL}`：11/11 相同；v12 仅 `ALTER TABLE chapters ADD COLUMN custom_rank INTEGER;`；旧 v11 库插入章行后升级到 12，行字段全保留、`custom_rank=NULL`；get/list 用 `_CHAPTER_COLUMNS`、insert/update 均含该列（`library.py:107,214-263`）。 |
| 2 | 语义务实：patch 保留、title 非空、重排全覆盖、kind 方向、create 字段 | **PARTIAL** | 前四项成立；create 的 kind/number/import_order 落库成立，但 sort_order 被写成 import_order 产生重复排序（R-04）；P5 tags 缺失（R-02）。 |
| 3 | wire P5–P8 形状 vs PREQ §8；Host 三层一致/降级；C-07 69/76 与 pin | **PARTIAL** | P6/P7/P8 键形状匹配；P5 缺 tags 语义；P5/P6/P8 缺书错误映射错误（R-01）；Host 四层签名一致、`IsReady` 降级返回 false/null 不抛；pin=`9c1eb974…` 与文件 sha256 一致、verifier 18/18；C-07 成员表未同步（R-05）。 |
| 4 | AC 全 MET 是否站得住 | **OPEN** | AC1/AC4/AC5 均不成立（R-01/R-02/R-03/R-04/R-05）；须处置后重判。 |
| 5 | 门禁实测（命令/时点/EXIT） | **CLOSED** | 见 §5；全部 EXIT 0；App.Tests 采用过滤抽样 22 passed（全量为日志证据）。 |
| 6 | 范围：diff ⊆ allowed_paths；无未授权契约字节 | **PARTIAL** | 7/29 越出 allowed_paths（R-06）；契约字节方面仅 C-07 inventory/freeze 更新（UNFREEZE 授权）与新增载体，C-02/C-03/P15 等未动，其余 17 pins 不变。 |
| 7 | v12 回归适配是否只改测试断言 | **CLOSED** | 4 个测试文件仅改版本断言/新增列快照/`new_columns` 条件；产品代码无隐藏行为变化；schema 变更仅 v12 一条。 |
| 8 | 扫新 P0/P1/P2 | **CLOSED** | 无 P0；新增 P1=2、P2=4 见 §2。 |

## 5. 门禁与测试（本次审查实测）

| # | 命令/检查 | 时点（+08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `git status --short` + `git rev-parse HEAD`（开始） | 15:05 | clean；HEAD=`83e45cfe5` | — |
| 2 | `python -m pytest tests/storage/test_library_metadata.py tests/core/test_library_wire.py -q` | 15:08 | **7 passed** in 3.57s | **0** |
| 3 | `python -m pytest tests/storage tests/core tests/fea09/test_v7_migration.py tests/fea11/test_source_gate_unify.py -q`（审查者重跑） | 15:11–15:13 | **1245 passed, 1 warning** in 97.87s（日志有同名结果 110.93s） | **0** |
| 4 | `dotnet test …NewManga.App.Tests.csproj --filter "FullyQualifiedName~ReaderReadingPreferencesTests\|FullyQualifiedName~ImportExportUiTests"` | 15:13–15:14 | **22 passed / 0 failed / 0 skipped** | **0** |
| 5 | `pwsh -NoProfile -File tools/governance/check.ps1` | 15:10 | PASS（3 warnings：11 非终态 / STATUS 3190 B·31 L / PLAN 6983 B·64 L） | **0** |
| 6 | `... check.ps1 -TaskPath doc/tasks/FEA-14-LIB-1.md` | 15:10 | PASS（同上） | **0** |
| 7 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 15:09 | **PIN AUDIT: PASS (all 18)**；C07=`9c1eb974342a` | **0** |
| 8 | `python tools/generate_api_inventory.py --check` | 15:08 | `OK: rendered counts match FEA-C07 doc`；1/69/6=**76** | **0** |
| 9 | Canonical 5 行 sha256 与文件比对 | 15:06 | **5/5 匹配**（EV-LB-001..005） | **0** |
| 10 | 迁移字节比对脚本（base vs head，v1–v11） | 15:12 | **v1–v11 identical: True**；base=[1..11] / head=[1..12] | **0** |
| 11 | 旧 v11 库升级探针（插入 books+chapters 行） | 15:12 | 版本 11→12；行字段全保留；`custom_rank=None` | **0** |
| 12 | wire 行为探针（P5/P6/P8 缺书、P5 tags、P7 缺章、P8 创建、sort 冲突） | 15:07 / 15:12 | 缺书 3 例=`UNKNOWN/internal`；P5 tags=`INVALID_REQUEST`；P7 缺章=`TARGET_NOT_FOUND`；P8 创建字段正确；重复 sort_order 复现 | **0** |
| 13 | diff 路径 vs allowed_paths 脚本 | 15:14 | changed=29；**out_of_allowed=7** | **0** |
| 14 | `git status --short` + `git rev-parse HEAD`（结束） | 15:15 | clean；HEAD 未变=`83e45cfe5` | — |
| 15 | App.Tests 全量 874/0/11 | 未重跑（日志 14:57） | 采用 `verification/FEA-14-LIB-1/logs/dotnet-app-tests.log`，**日志证据** | 0（日志） |

## 6. NOT_RUN

- 未重跑 App.Tests 全量（5m19s 级）；仅跑过滤抽样 22 passed，全量 874/0/11 仅采信日志（R-08 的 provenance 限制）。
- 未做真实 Host↔Core 进程级联调：4 个新 `CoreServiceClient` 方法未对活 Core 调用（仓库内也无 C# 测试）。
- LIB 可见 UI（书架/工作台账单编辑、拖拽重排）= NOT_RUN（登记于卡面/README，属 LIB-2/UI）。
- `tags` 替换语义、Volume 实体 = NOT_RUN（卡面 limitation/README 登记；本审不把它算作“已实现”）。
- 万级章重排性能、真实大库迁移、sqlite 磁盘写失败/半迁移 = NOT_RUN。
- 未审查 FEA-15 正式验收声明。

## 7. 处置建议（按优先级）

1. **R-01（必须）**：P5/P6/P8 改捕 `BookNotFound`，补三条 wire 负例；确认错误 envelope 为 `TARGET_NOT_FOUND/not_found`。
2. **R-02（必须）**：实现 P5 tags 替换（复用既有 `book_tags` 关联 API）并补测试；或取得 DSH 范围 errata 后把 AC1 正式改 PARTIAL，二者不可兼得“未实现 + MET”。
3. **R-03/R-04（应修）**：修正 P8 客户端投影键/加可选响应键；`create_chapter_with_metadata` 不再把 sort_order 覆盖成 import_order，补重复/插入位测试。
4. **R-05/R-06/R-07（应修/应登记）**：同步 C-07 正式成员表与 S5 节并重算 pin；补全 allowed_paths；补齐冻结记录 v1.5 行与 §2/§1B。
5. **P3**：R-08 证据说明、R-09 时间戳、R-10 测试强度、R-11 kind 语义裁决、R-12 custom_rank limitation、R-13 边界校验。

## 8. 审查者声明

本报告由 lead 会话 `session-408d4e24-3789-4111-acde-983899601dad` 派发的全新上下文子 agent 出具，未参与 FEA-14-LIB-1 实现；只读审查，唯一仓库写入为本文件。PASS 基于本次 2026-11-10 15:05–15:15 的实测、日志与逐行核对；未执行项已在 §6 记 NOT_RUN。本报告只对 `83e45cfe5` 有效。
