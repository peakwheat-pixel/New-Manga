# FEA-09-PREREQ-1 契约独立复核 r4

## 0. 元信息

| 项目 | 记录 |
|---|---|
| Reviewer | Codex，用户直接指派的独立审查会话 `/root` |
| 独立性 | 未参与被审契约起草、r1–r3 返修；本会话不参与后续实现或返修 |
| 模型 | GPT-6 系列 Codex；本会话未提供可验证的精确模型 ID |
| 时间 | 2026-11-03；结束核验时间 17:09:55，Asia/Shanghai |
| 仓库 | `G:\CODEX\New Manga` |
| 分支 | `main` |
| Git common directory | `G:/CODEX/New Manga/.git` |
| reviewed_head | `2e3ed0cf90966a59f5402cb0bc6a0d23b7fdbc8e` |
| r3 差异基线 | `47133516263c868d0de2445d024d03e651fc56e7` |
| Task 差异基线 | `6e274dd94c5b64d8fbc3f9d578363d3c502a2b68` |
| 审查前后 status | `git status --porcelain=v1` 均无输出 |
| 结束 HEAD | 与 reviewed_head 相同 |
| 辅助 Agent | 未使用 |

### 被审文件指纹

以下 `git hash-object` 均与 `HEAD:<path>` blob ID 相同。另以原始字节比较确认：工作树字节与 HEAD blob 字节完全相等，因此下列 SHA-256 同时也是对应 Git blob 内容的 SHA-256。结束检查全部不变。

| 文件 | `git hash-object` / HEAD blob ID | 工作树 SHA-256 |
|---|---|---|
| `doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md` | `e13a6e14236b6b08b5ca1d7778c0dc38a994bfcb` | `0b3c9f1d81dbefd7a6fc56195973da1a91597b6580cfde7988f32bba4dcf2f68` |
| `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | `4dd3f3a6f8cf92963df1fa2deb098f592fb51693` | `81531afc8fe001ef4d4a62337199fb2c08bb7496ac5fec0bc28de13cbd31d5c7` |
| `doc/plan/FEA-C05_PAGE_VISIBILITY_DRAFT.md` | `84658ad9f4dd44ffa9d8ae00e70dc086dfc95bc2` | `13ff436af7bfbdc2a65181153a2b6140902e4aff1a8665a28e1c9c5b60167a39` |
| `doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md` | `6a6e5744c7452adba08af33d1db1023a89c1491d` | `a779a7c1691b4414dcf99fd4452f837516f07accb44f9a9b263262c860fa9eb4` |
| `doc/reviews/CONTRACT-UNFREEZE-2026-11-03.md` | `25480938ff9d7c54e123b1f3b56e51844f47577e` | `60c4a516bcde589018b923e5fed096341fe0d44d378473f60943addf819f621f` |

### 历史报告原字节核验

已读取三份归档原文，按原 Findings 及其验收条件核验。

| 报告 | 字节数 | SHA-256 | 结果 |
|---|---:|---|---|
| r1 | 25,469 | `d3ba756e7ccbb2c30653f833d6d3ebe0c4c19479f3f53627cc2b606632d54ae3` | 与指定值一致 |
| r2 | 23,339 | `d50f3a54020715e8ed2e226946a1034dae7e1b7a52a19b6e7c851f3d6a117e1a` | 与指定值一致 |
| r3 | 29,556 | `c029ad6abbb097db72a2ea31adaf24fd2d71a5c3657d6c4d21d4f8e4f1ca83fc` | 与指定值一致 |

三份报告的 Git blob ID 分别为：

```text
r1 50552e9f40ae5b5cbbe10c03d0979fd474d72065
r2 156739229a805129a4678563647d3d4ffc5191b3
r3 7bf474e4f5a381055e6807a0066e57ff4d113f09
```

### 命令结果与执行方式

常规 `exec_command` 使用 PowerShell、cmd 两次均在进程启动阶段返回 Windows error 740，未执行其中的读取命令。随后使用 Node 文件读取 API 和 `child_process.execFile` 完成检查，未申请提权。

Git 最初报告工作区所有者不同；后续调用仅使用进程级参数：

```text
git -c safe.directory=G:/CODEX/New Manga ...
```

未修改 Git 配置，并通过 `GIT_OPTIONAL_LOCKS=0` 禁用可选锁写入。

| 检查 | 结果 |
|---|---|
| HEAD、branch、common directory、前后 status | EXIT 0；见上表 |
| 各文件 `git hash-object`、`rev-parse HEAD:<path>`、`cat-file blob` | EXIT 0；指纹一致 |
| `git diff --name-status 47133516263 HEAD` | EXIT 0；5 个文档路径 |
| `git diff --name-status 6e274dd94 HEAD` | EXIT 0；16 个文档路径 |
| `git diff --name-only 920c09525 HEAD -- src apps tests 'doc/plan/FEA-CONTRACT-FROZEN-*'` | EXIT 0；无输出 |
| `git diff --check 47133516263 HEAD` | EXIT 2；Task 第 164 行 trailing whitespace |
| `pwsh -NoProfile -File tools/governance/check.ps1` | EXIT 0；PASS，3 warnings |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | EXIT 1；FAIL(2)，仅 C-05/C-06 |
| `py.exe -B -c <内存数据库程序>` | EXIT 0 |
| `py.exe -B -c <匹配及计数补充程序>` | EXIT 0 |

**未修改声明：未修改仓库、冻结字节、Git 配置或用户数据；未执行 add、commit、push；未创建磁盘脚本、数据库或证据文件。数据库均为 `:memory:`，Python 使用 `-B`。报告仅通过本次输出交付。**

## 1. Verdict

**`changes_requested`**

本轮 Findings：**P0=0 / P1=2 / P2=2**。

v4 已修复 location 双规则，并实质补充 PDF 身份职责分离、迁移双集合和项目归属守卫。但以下问题仍阻止冻结：

1. 迁移断言仍把“旧不可见”要求为 incomplete，与完整集合守恒直接冲突。
2. PDF 重复页匹配仍允许位置锚定产生错误保续；跨版本像素证据也缺少可比渲染条件。

receipt 和控制信息另有未闭环项。**当前四份契约不可同批冻结，PREREQ-1 不可 done。**

## 2. R3 findings 闭环表

`FIXED` 仅表示契约问题闭环，不表示尚未实现的产品行为已经运行通过。

| ID | 状态 | 原文条件与本轮依据 |
|---|---|---|
| R3-001 | **FIXED** | C-15 `:89–93`、`:202`、`:231` 已统一为 source 内物理身份唯一、每 source 一个 current、重授权原地更新。跨 Registry 命中复用已明确。旧“新代次插入重复 location”反例仍被 DDL 拒绝，与新正文一致；原地更新及历史/current 转换实跑成功。 |
| R3-002 | **PARTIAL** | `:225–229` 已分离版本内验证身份和跨版本 pixel 匹配；唯一内容页的插页、重编码、仅元数据变化模型均可保续。但重复页仍称需 ordinal/locator 锚定，未排除插页后位置相同而 occurrence 不同的误匹配；pixel 观察允许随 decoder/scale 更新，却未定义跨版本比较时如何取得可比证据。见 R4-002。 |
| R3-003 | **PARTIAL** | `:40–41` 已正确分开 complete 集合与 `V_artifact` 集合，二者独立守恒可计算且实跑成立；`:44` 已明确 original revision `managed_path`、非空 page ref 及缺文件拒绝。但 `:42` 仍要求“旧不可见/半写行仍为 incomplete”，合法完整但不可见旧页反例仍无法满足全部断言。见 R4-001。 |
| R3-004 | **PARTIAL** | receipt enum 已含 accepted；计数单位已有定义。但固定示例 `remaining_pages=3`、`pending_pages=7`，item/totals 使用不同单复数字段却未给映射；缺少完整的 accepted 取消、部分失败及 unsupported 终态示例。见 R4-003。 |
| R3-005 | **PARTIAL** | C-15/C-16 标题、状态及同批引用已更新为 v4；载体失败语义定位已修正；Task 已纳入 `verify_pins.ps1` 写域和 matrix 重冻注记。但 C-15 仍引用不存在的 §3.3；Task AC-7 仍要求 15/15，与交付物及 AC-5 的 17 项冲突。见 R4-004。 |
| R3-006 | **PARTIAL** | C-15 `:203` 已明确同事务 `page→chapter→book == project_id` 守卫、`SOURCE_PROJECT_MISMATCH` 和 rollback；C-16 `:136` 已登记错误码，且不声称 DDL 覆盖。但“AC-7 含该负测”的引用未实际落入 PREREQ-1 或 FEA-09 的 AC-7，责任落点未闭合。见 R4-004。 |

## 3. r1/r2 不回退抽查

| 项目 | 结果 | 依据 |
|---|---|---|
| R2-001 模式分派 | **保持 FIXED** | C-05 §3.1 与 C-15 §4.1 一致；managed 只用原 artifact 谓词，referenced 不能借 valid artifact 绕过完整性。原 C-05 §3 字符串完整保留。 |
| R2-002 加密 Plan | **保持 FIXED** | C-16 §3/§5 保留有限预览、无密码不解密、不要求明文摘要；Start 先重验容器及 generation，再解密。新 token、重试与清理规则保留。 |
| R2-005 WireLog 脱敏 | **保持 FIXED** | §7.1 仍覆盖 Register、Plan、Start 及响应、整对象 secret_ref、嵌套 path、原行与 hex；要求在可保存 Frame 构造前脱敏。未运行生产脱敏测试。 |
| R2-008 报告归档 | **保持 FIXED** | r1/r2/r3 均已原字节归档并通过完整指纹核验。 |
| R2-006 回调边界 | **保持 FIXED** | 同连接只读查询、注入资源 verifier、禁止写/Host/网络/第二连接及 typed rollback 规则保留。 |
| R2-009 referenced 可见性引用 | **保持 FIXED** | C-06 §4 仍明确进入 `V_ref`，不创建 artifact/revision。 |
| R1-003 撤销/失联 | **未发现回退** | 持久化→废止→提交边界停止→ACK，以及 EOF fail-closed 均保留。 |
| R1-006 managed 写入维护 | **未发现回退** | C-15 §4.3 保留所有 managed 创建路径显式维护完整性列；live 判重与含软删 max order 分开。 |
| R1-011 Registry | **未发现回退** | 逐根身份、DataRoot 派生锁、跨 session 文件排他、持锁重载、损坏 fail-closed 和 DPAPI LIMITED 边界均保留。 |

这些判断不关闭 R3 留下的 PDF、迁移及 receipt 问题，也不构成实现验收。

## 4. UNFREEZE 合规核验

### 差异范围

r3 reviewed_head 至当前 HEAD 实际仅有：

```text
M doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md
M doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md
M doc/reviews/CONTRACT-UNFREEZE-2026-11-03.md
A doc/reviews/FEA-09-PREREQ-1-r3.md
M doc/tasks/FEA-09-PREREQ-1.md
```

从 Task 基线比较另含 STATUS、PLAN、ledger、rolling checkpoint、C-05/C-06、r1/r2、scope-r1 及相关 Task 的建立或更新，共 16 个文档路径。没有生产代码、测试、依赖或打包变化。

`verify_pins.ps1` 已获 Task 精确写域授权，当前尚未修改。未发现其它冻结契约或原 FROZEN 记录变化。

### 原语义及 pin 历史

逐 hunk 审阅及字符串检查确认：

```text
OLD_C05_SECTION3_PRESERVED true
OLD_C06_NINE_RULES_PRESERVED true
```

原冻结 blob SHA-256：

```text
C05 b34db88768790a982c00d6b78a9649c24047e15d2ba86e3c0bf6a5a293ec8d25
C06 b798dd8a9b3839ac0c8e18e19dd3d515080075db53d83726e18cf76343beaef8
```

与载体旧 pin 一致。变更集中在 referenced 可见性、授权方向、scope、双侧 Verify、撤销和相应引用，未发现无关产品扩域。

载体规定的复核→最后元数据编辑→计算 pin→更新冻结记录并保留历史→更新 matrix 顺序正确。当前尚未满足 approved 条件。

### pin 实际输出

```text
OK C01b 3c9f5af7d74f
OK C02 bb365ca891a7
OK C03 b77e7968a00b
OK C04b 694ce5bc8c8b
MISMATCH C05 pin=b34db8876879 actual=13ff436af7bf
MISMATCH C06 pin=b798dd8a9b38 actual=a779a7c1691b
OK C07 3fdb44e49afe
OK C08 453f993c1a16
OK C09 dc51226b336c
OK C10 ec8fd862f95f
OK C11 44f4273f7ad1
OK C12 f49835860143
OK C13 8faf1e805eac
OK C14 05056cbf65f9
OK FEA01 0370c18932b1
PIN AUDIT: FAIL (2)
```

**恰好 C-05/C-06 待重冻，其余 13 项 OK。** 当前检查器未覆盖 C-15/C-16，不能声称新全集通过。

## 5. 独立复跑结果

### 5.1 方法

环境：

```text
Python 3.14.6
SQLite 3.50.4
```

通过 `py.exe -B -c PROGRAM` 执行内存程序，直接导入真实：

```python
from infrastructure.sqlite.schema import default_migrations, Migration
from infrastructure.sqlite.migrator import MigrationRunner, read_schema_version
from infrastructure.sqlite.connection import SchemaTooNewError
```

从当前 C-15 第一个 SQL fenced block 提取原文，构造：

```python
Migration(7, "v7__source_storage", sql)
```

所有连接使用 `:memory:`、`PRAGMA foreign_keys=ON`。没有修改迁移器源码。

程序 UTF-8 SHA-256：

```text
数据库主程序
71a9e3be498016e079c45f0bf1c9e7281cbbb2c217173bd2af4937fcad3cc8e8

匹配、资源参考谓词及计数补充程序
6aa87bd4dd2488c636b4e3c6ecddf7e318a7564c3ca1bf0e2877af21a53f7414
```

### 5.2 v1–v6→v7、回填及双集合

分别建立真实 v1–v6 schema 并插入 fixture；先补齐真实迁移链至 v6，再捕获 v7 前基线并升级。v1 结构页保留 NULL 导入元数据，没有伪造来源。

| 检查 | 实际结果 |
|---|---|
| 六个起点升级到 v7 | 全部成功 |
| 旧 pages 全列逐值比较 | 全部不变；仅追加新列 |
| 区域人工文本、区域 Lock | 全行比较不变 |
| current revision、pinned revision | artifact revision 全行比较不变 |
| 完整 managed 页、软删完整页 | 回填 complete |
| 半写、placeholder | 保持 incomplete |
| 旧 complete 集合→新 managed complete 集合 | 独立比较成立 |
| 旧 `V_artifact`→新 managed V | 同一时间及父级条件下，ID 与顺序比较成立 |
| FK 检查 | 全部为空 |
| 两张预留表 | 未创建 |

关键输出：

```text
UPGRADE 1 ->7 COMPLETE [] V [('half',)]
UPGRADE 2 ->7 COMPLETE [('deleted',), ('full',)] V [('half',)]
UPGRADE 3 ->7 COMPLETE [('deleted',), ('full',)] V [('half',)]
UPGRADE 4 ->7 COMPLETE [('deleted',), ('full',)] V [('half',)]
UPGRADE 5 ->7 COMPLETE [('deleted',), ('full',)] V [('half',)]
UPGRADE 6 ->7 COMPLETE [('deleted',), ('full',)] V [('half',)]
```

其中：

- `half` 缺导入元数据，但有 valid original current revision，故 V 为真、完整性为 incomplete。
- `full` 导入元数据完整，但没有 artifact，故 V 为假、完整性为 complete。
- `deleted` 为完整软删页，也属于 complete 集合。

前两条双集合守恒已正确成立；但 C-15 第 3 条断言仍无法成立：

```text
ASSERTION3_COUNTEREXAMPLE
invisible full status = complete
visible half status = incomplete
```

因此不能把“不在 V 中”当作 incomplete 的判据。

### 5.3 资源校验对象与拒绝

从合法 artifact-only 可见页实际查询得到：

```text
original revision managed_path = managed/half-original.png
page.managed_original_ref     = None
```

这支持 v4 不再要求此类页必有 page ref。

另以注入可读资源集合运行参考谓词：

```text
RESOURCE_REFERENCE_PRESENT ACCEPT
RESOURCE_REFERENCE_MISSING SOURCE_MIGRATION_RESOURCE_UNVERIFIED
```

**该补充测试仅验证资源判据可计算及拒绝分支；不是生产 validation callback、真实文件读取或 callback rollback 的运行证据。** 当前真实 MigrationRunner 尚无草案要求的 validate 参数。

### 5.4 FK、唯一、部分唯一及 location

实际负测结果：

```text
VERSION_CROSS_SOURCE REJECTED FOREIGN KEY constraint failed
ENTRY_CROSS_SOURCE REJECTED FOREIGN KEY constraint failed
BINDING_CROSS_SOURCE REJECTED FOREIGN KEY constraint failed
CACHE_CROSS_SOURCE REJECTED FOREIGN KEY constraint failed

DUP_ORDINAL REJECTED UNIQUE constraint failed
DUP_SORT_KEY REJECTED UNIQUE constraint failed
DUP_PROJECT_ENTRY REJECTED UNIQUE constraint failed
DUP_CURRENT_PAGE REJECTED UNIQUE constraint failed

SUPERSEDED_HISTORY_OTHER_BOOK_REFERENCE ACCEPTED
```

重授权与 current：

```text
REAUTH_IN_PLACE [('s1', 'reg-new', 2)]

OLD_REAUTH_INSERT REJECTED UNIQUE constraint failed:
source_locations.source_id,
source_locations.content_digest,
source_locations.volume_serial,
source_locations.file_id

SECOND_CURRENT REJECTED UNIQUE constraint failed:
source_locations.source_id

HISTORICAL_CURRENT [('l1', 0), ('l-next', 1)]
```

说明新正文已与 DDL 对齐：旧反例插入应被拒绝，跨 Registry 原地更新成功。

### 5.5 项目归属守卫

运行同事务参考守卫得到：

```text
PROJECT_GUARD_REFERENCE SOURCE_PROJECT_MISMATCH ROLLBACK
PROJECT_MISMATCH_DDL_ALONE_ACCEPTED (documented boundary)
```

即同事务检查能够拒绝错误归属并回滚；DDL 单独接受错误归属仍是明确边界。

这不是生产绑定 handler 测试。契约守卫已写明，但负测 AC 引用仍需落实。

### 5.6 PDF 匹配模型

在内容指纹唯一且证据可比的模型中：

```text
PDF_INSERT_UNIQUE [None, 'EA', 'EB']
PDF_REENCODE_SAME_PIXELS ['EA', 'EB']
PDF_METADATA_ONLY_SAME_PROFILE ['EA', 'EB']
PAGE_IDENTITY_CONTAINER_CHANGE true
RENDITION_CHANGE_IDENTITY_STABLE true
```

版本内身份与跨版本匹配职责分离的方向成立。

重复页反例：旧版本为两个相同像素 occurrence，分别为 E0、E1；新版本在最前插入相同像素页。按正文允许的 ordinal 锚定：

```text
insertedA -> E0    正确 lineage：无旧 entry
oldA0     -> E1    正确 lineage：E0
oldA1     -> 无    正确 lineage：E1
```

位置可以消除候选数量，却不能证明 occurrence 身份；此场景必须进入歧义确认。

另实际计算同一纯色图的 1×1 与 2×2 `pixel-digest/1`，摘要不同。若容器仅元数据变化，而观察列已按另一 scale 更新，直接比较旧/新观察会失去全部候选。草案尚未定义可比 profile 的选择、重算或证据不足分支。

**以上是摘要公式和匹配规则的独立模型实验，未运行 PDFium、真实 PDF 插页或重编码。**

### 5.7 旧写者拒写、v7 失败回滚

六个升级后的库均被仅认识 v1–v6 的真实迁移器以 `SchemaTooNewError` 拒绝。

这是应用迁移入口拒写，不是 SQLite 引擎禁止任意 SQL。

在 v7 SQL 尾部注入：

```sql
INSERT INTO no_such_table VALUES (1);
```

从空库及 v1–v6 起点执行，全部满足：

```text
ROLLBACK 0 ->6 NO_V7_TABLES_COLUMNS METADATA_6
ROLLBACK 1 ->6 NO_V7_TABLES_COLUMNS METADATA_6
ROLLBACK 2 ->6 NO_V7_TABLES_COLUMNS METADATA_6
ROLLBACK 3 ->6 NO_V7_TABLES_COLUMNS METADATA_6
ROLLBACK 4 ->6 NO_V7_TABLES_COLUMNS METADATA_6
ROLLBACK 5 ->6 NO_V7_TABLES_COLUMNS METADATA_6
ROLLBACK 6 ->6 NO_V7_TABLES_COLUMNS METADATA_6
```

v7 六张表、pages 新列及版本元数据共同回滚；先前成功的 v1–v6 保留。

### 5.8 receipt 与治理

固定 receipt 示例实际算术检查：

```text
remaining_pages = 3
counts.pending_pages = 7
RECEIPT_FIXED_EXAMPLE_REMAINING_EQUALS_PENDING False
```

治理输出：

```text
Governance scope: 15 current documents; no historical directory scan.
Task: doc\tasks\FEA-09-PREREQ-1.md
WARN: 存在 11 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3125 bytes / 29 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：5162 bytes / 64 lines
Governance check: PASS (3 warnings)
```

EXIT 0。机械 PASS 不覆盖契约语义问题。

## 6. 新 Findings 表

| ID | 级别 | 位置 | 问题与最小修订 |
|---|---|---|---|
| **R4-001** | **P1** | C-15 `:40–44`，尤其 `:42` | **迁移第 3 条仍混淆不可见与不完整。** 元数据完整但无 artifact、软删或父级删除的旧页可以不可见且 complete；实跑 `full` 即为反例。按第 3 条拒绝它会误阻合法旧库，强改为 incomplete 又破坏第 1 条守恒。将该条限定为“旧完整性谓词不成立的半写/placeholder 行保持 incomplete”，不可见集合只由第 2 条守恒约束。 |
| **R4-002** | **P1** | C-15 `:216`、`:226–229`；C-14 SC-S09/SC-S12；C-01b SC-28 | **PDF 跨版本匹配尚缺安全且可执行的证据条件。** 重复页插入后 ordinal/locator 可产生唯一但错误的 occurrence 映射；另任意 scale/decoder 观察不能直接跨版本比较。需明确可比渲染 profile 或重算规则、证据缺失处理，以及全体匹配的一对一约束。重复内容不得仅凭变化后 ordinal/locator 自动保续；没有独立身份依据时整组进入确认，保留旧 PageId、人工版本及进度，不自动迁移。补唯一页插入、重复页插入/删除/重排、仅元数据变化并伴随观察 profile 变化的判据。 |
| **R4-003** | **P2** | C-16 `:96–110` | **receipt 固定形状与计数仍未完全一致。** 固定示例 remaining=3、pending=7；item 的 `skipped_source/failed_source` 与 totals 的复数键未明示聚合映射。整 source 跳过的定义也未说明“部分成员已引用、其余导入”的计数归属。统一示例与映射，明确部分重试的跳过单位；补 accepted 即取消、12 页提交后取消、12 页提交后失败、unsupported-only 四个完整自洽示例。无需扩大产品范围。 |
| **R4-004** | **P2** | C-15 `:200/:203`；PREREQ-1 Task `:100–102`；FEA-09 AC-7/AC-8 | **控制信息和验收责任仍有残留。** 跨版本规则指向不存在的 §3.3，实际为 §3.2；PREREQ-1 AC-7 仍为 15/15；“AC-7 含项目归属负测”在两份 Task 均无对应明确条目。修正节号、将冻结后门禁统一为 17/17，并明确 `SOURCE_PROJECT_MISMATCH` 由 FEA-09 哪项 AC/测试承担。Task 第 164 行另有 trailing whitespace，一并清理。 |

## 7. 未覆盖／无法核验项

1. 尚未实现的生产 validation callback、违规回调拦截、非 SQLite 异常映射及真实资源验证回滚。
2. 实际 PDF 解码、插页、重编码、重复 occurrence 确认与绑定发布；本轮只有规则模型实验。
3. source-read 生产通信、撤销与提交竞态、ACK 超时、EOF 后后台停止。
4. Windows 原生 DPAPI、ACL、跨进程/跨 session 锁、磁盘原子替换。
5. ZipCrypto/PDFium 密码产品路径、清零及真实日志秘密扫描。
6. build、全量 Python/.NET 回归、UI 端到端、四 PNG 原始字节复跑。
7. 任意损坏库、全部人工数据组合及真实用户库；数据库测试仅覆盖代表性合法 fixture。
8. 扩展后的 17 项 pin 检查器尚不存在，未声称其负测通过。
9. 未重开或重新验收 FEA-08。

## 8. 冻结建议

**需返修。当前 C-05 v1.1、C-06 v1.1、C-15 v4、C-16 v4 不可同批冻结。**

最小修订集为 R4-001…R4-004；无需修改生产代码，也无需为这些问题改动 C-01b/C-14 冻结字节。

修订并通过新独立复核后，冻结前最后动作如下：

1. **先定稿条款并提交固定 head。** C-15/C-16 若继续修订，由 DSH 明确最终版本并同步载体、Task 和全部引用；不得把本次 v4 审查追溯当成后续字节已 approved。
2. **最后编辑状态行。** C-05/C-06 为 FROZEN v1.1，C-15/C-16 为实际最终冻结版本；载体同步结论。冻结提交不得夹带未经复核的条款修改。
3. **计算三种指纹。** 最后编辑后记录工作树原始字节 SHA-256、`git hash-object`、固定 commit 的 `git cat-file blob <commit>:<path>` 内容 SHA-256及 blob ID；在 §1A 明确字节口径，在 §1B 列出复核字节与冻结字节差异。
4. **更新 FROZEN-C05/C06。** 更新当前 pin、v1.1 复核依据和条件清单；保留 v1.0 pin、旧复核、既有 pin 修正历史。不要让检查器误读历史 pin。
5. **建立 FROZEN-C15/C16。** 记录最终版本、固定 head、pin、冻结条件逐项证据、边界及 §1A/§1B。
6. **更新 freeze matrix。** C-05/C-06 加重冻版本注记，追加 C-15/C-16；当前冻结全集为 **17 个对象**，相关总数同步。其它既有契约条款和历史证据保持原字节。
7. **扩展 `verify_pins.ps1`，且缺记录失败。** Task 已精确授权此路径。
8. **归档原始门禁日志。** 包含命令、cwd、head、环境、EXIT、原始输出；最终要求 check PASS、vpins **17/17**。另按 Task 完成四 PNG 等证据，不使用历史 PASS 冒充本轮。
9. **完成生命周期。** 更新 Task 逐项 AC 与 v3 状态标记、Handoff、Canonical Evidence、delivery/integration head、资源清单及 closeout；同步 ledger、STATUS、PLAN、rolling checkpoint。DSH 集成验证与 closeout 完成后才设 done。

### 17 项 pin 扩展方案

在既有 15 项 map 加入：

```powershell
'C15'='FEA-C15_SOURCE_STORAGE_DRAFT.md'
'C16'='FEA-C16_SOURCE_READ_WIRE_DRAFT.md'
```

同时修正当前：

```powershell
MISSING-RECORD ... skipped
```

分支，使冻结 Gate 中缺记录增加失败计数并返回非零。仅加 map 而继续 skip，不能证明实际校验了 17 项。

验收全集：

```text
C01b C02 C03 C04b C05 C06 C07 C08 C09
C10 C11 C12 C13 C14 C15 C16 FEA01
```

扩展前保存当前 15 项基线；扩展后要求：

- 17 个当前记录、契约和 pin 全部存在且匹配。
- 明确已验证数量为 17，不能把 skip 算成功。
- 缺记录、缺契约、缺 pin、pin 不匹配均 EXIT 非零。
- 负测使用内存或 Task 隔离 fixture，不破坏真实冻结文件。
- C-05/C-06 当前记录与历史 pin 可清楚区分。
- 其它 13 项 pin 口径保持不变，不借机迁移历史 hash basis。

## 9. 结论与推荐下一步

**PREREQ-1 当前不能冻结或 done；FEA-09 当前不能据此前置进入 scope-r2。**

在上述最小返修、新独立复核 approved、四份契约最终冻结、17 项 pin 门禁及 PREREQ-1 集成收口完成后，**FEA-09 可以进入 scope-r2 文档复审**。这一步不要求提前具备实现证据，也不等于 ready 或实现授权；scope-r2 仍须核对 scope-r1 处置、写域、AC、UI 协同边界及 Appointment。

推荐下一步由 **DSH** 在现有 PREREQ-1 内处置，不释放新实现 Task。

可直接转发：

> DSH：请在 `G:\CODEX\New Manga`、`main`，以 `base/head=2e3ed0cf90966a59f5402cb0bc6a0d23b7fdbc8e` 为恢复点，先确认 HEAD 与工作树，再处置 FEA-09-PREREQ-1 r4 的 R4-001…R4-004。范围限当前 Task 授权契约、UNFREEZE 载体、Task 和必要治理文档：限定迁移 incomplete 断言，补齐 PDF 可比证据与重复 occurrence 歧义规则，统一 receipt 示例/计数，修正章节及 17 项门禁与项目归属负测责任。交付逐项 disposition、固定 commit、最终版本和指纹，并复跑内存迁移、反例及只读 check/vpins；所有 NOT_RUN/LIMITED 如实保留。随后任命未参与返修的新独立上下文复核。禁止生产代码、依赖、用户数据或历史冻结证据修改，禁止 push，不重开 FEA-08。approved 前不重冻、不关闭 PREREQ-1；完成最终冻结、17/17 门禁和集成 closeout 后，再提交 FEA-09 scope-r2。