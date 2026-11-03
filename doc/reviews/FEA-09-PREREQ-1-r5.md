# FEA-09-PREREQ-1 契约独立复核 r5

## 0. 元信息

| 项目 | 记录 |
|---|---|
| Reviewer | Codex，用户直接指派的独立审查会话 `/root` |
| 独立性 | 未参与契约起草或 r1–r4 返修；本会话不参与后续实现、返修 |
| 模型 | GPT-6 系列 Codex；没有可验证的精确模型 ID |
| 日期 | 2026-11-03；结束核验时间 17:20:06，Asia/Shanghai |
| 仓库 | `G:\CODEX\New Manga` |
| 分支 | `main` |
| Git common directory | `G:/CODEX/New Manga/.git` |
| reviewed_head | `90b9600b13e531b3c00407d4af918737037b133a` |
| r4 差异基线 | `2e3ed0cf90966a59f5402cb0bc6a0d23b7fdbc8e` |
| Task 差异基线 | `6e274dd94c5b64d8fbc3f9d578363d3c502a2b68` |
| 审查前后 status | `git status --porcelain=v1` 均无输出 |
| 结束 HEAD | 与 reviewed_head 相同 |
| 辅助 Agent | 未使用 |

### 被审文件指纹

以下 `git hash-object` 均等于 `HEAD:<path>` blob ID。另以原始字节比较确认工作树文件与 HEAD blob 内容完全相等，故下列 SHA-256 同时也是对应 blob 内容的 SHA-256。结束复算全部不变。

| 文件 | `git hash-object` / HEAD blob ID | 工作树 SHA-256 |
|---|---|---|
| `doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md` | `d80ead9e78253d9bc72c088c1e91a4231c40280f` | `fa912075f487701083eab662b7f89b9e8d8897024c9a832d9812ce5c87802090` |
| `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | `8f9a06e0d41cc808add990af38246671939a0e02` | `379dafb9eb125566b13923b2048de652c1187b85f0d2305538ee18055b9676b2` |
| `doc/plan/FEA-C05_PAGE_VISIBILITY_DRAFT.md` | `84658ad9f4dd44ffa9d8ae00e70dc086dfc95bc2` | `13ff436af7bfbdc2a65181153a2b6140902e4aff1a8665a28e1c9c5b60167a39` |
| `doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md` | `6a6e5744c7452adba08af33d1db1023a89c1491d` | `a779a7c1691b4414dcf99fd4452f837516f07accb44f9a9b263262c860fa9eb4` |
| `doc/reviews/CONTRACT-UNFREEZE-2026-11-03.md` | `52d83585a37d54fa53711f2a4c15a5146f1a65ed` | `ac227e19ab9be38e97e6fb7ac744e96bbfe1b1162ce2835451c42eff6eac208a` |

### 历史报告原字节核验

本轮读取原报告，并按原 Findings 核对，未以返修摘要替代原文。

| 报告 | 字节数 | SHA-256 | 结果 |
|---|---:|---|---|
| r1 | 25,469 | `d3ba756e7ccbb2c30653f833d6d3ebe0c4c19479f3f53627cc2b606632d54ae3` | 一致 |
| r2 | 23,339 | `d50f3a54020715e8ed2e226946a1034dae7e1b7a52a19b6e7c851f3d6a117e1a` | 一致 |
| r3 | 29,556 | `c029ad6abbb097db72a2ea31adaf24fd2d71a5c3657d6c4d21d4f8e4f1ca83fc` | 一致 |
| r4 | 25,502 | `4f5928a1693e325fd449efadd45f8cafa77790ad0f40329965aef0dff287fdfb` | 一致 |

### 命令与执行方式

常规 `exec_command` 分别以 PowerShell、cmd 启动，均在进程创建阶段返回 Windows error 740，没有执行其中命令。随后通过 Node 文件读取 API 与 `child_process.execFile` 完成只读检查和内存测试，未申请提权。

后续 Git 调用使用：

```text
git --no-optional-locks -c safe.directory=G:/CODEX/New Manga ...
```

该参数仅作用于当前进程，未修改 Git 配置。

| 检查 | 实际结果 |
|---|---|
| branch、HEAD、common directory、前后 status | EXIT 0 |
| `hash-object`、`rev-parse HEAD:<path>`、`cat-file blob` | EXIT 0；指纹及字节比较一致 |
| `git diff --name-status <r4-head> HEAD` | EXIT 0；6 个文档路径 |
| `git diff --name-status <task-base> HEAD` | EXIT 0；17 个文档路径 |
| 生产代码、测试、依赖、打包、原 FROZEN 记录及 pin 检查器差异检查 | EXIT 0；指定范围无差异 |
| `git diff --check <r4-head> HEAD` | EXIT 0；无输出 |
| `pwsh -NoProfile -File tools/governance/check.ps1` | EXIT 0；PASS，3 warnings |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | EXIT 1；FAIL(2)，仅 C-05/C-06 |
| `py.exe -B -c <数据库主程序>` | EXIT 0 |
| `py.exe -B -c <PDF/receipt 模型程序>` | EXIT 0 |
| `py.exe -B -c <扩展数据库程序>` | 首次 fixture 错误 EXIT 1；修正内存 fixture 后 EXIT 0 |

首次扩展测试误在同一页复用 `binding_version=1`，被正确拒绝；修正为另建其他 book 的页后通过。该失败属于审查程序 fixture，不是产品 finding。另一次尝试设置 PowerShell 输出编码被受限语言模式拒绝；最终以原命令重跑，并按实际终端编码解码，得到无 stderr 的门禁输出。

**未修改声明：未修改仓库、冻结字节、Git 配置或用户数据；未执行 add、commit、push；未创建磁盘脚本、数据库或证据文件。全部数据库使用 `:memory:`，Python 使用 `-B`。报告仅通过标准输出交付，由 DSH 原字节归档。**

## 1. Verdict

**`changes_requested`**

本轮 Findings：**P0=0 / P1=0 / P2=2**。

R4-001、R4-002、R4-004 已闭环。R4-003 的固定示例和字段命名已修正，但新增的 accepted 取消示例仍与 `pending_pages` 定义矛盾，跳过场景的剩余页公式基数也未明确。另有三处 C-16 同批依赖版本仍引用 C-15 v4。

**当前四份契约尚不建议同批冻结；PREREQ-1 尚不能 done。** 剩余修改限于 C-16 计数条款和版本引用，无需生产代码改动。

## 2. R4 findings 闭环表

`FIXED` 表示契约问题闭环，不代表产品实现已经通过测试。

| ID | 状态 | 原文条件与本轮依据 |
|---|---|---|
| R4-001 | **FIXED** | C-15 `:40–44` 分别保留 complete 集合与旧 `V_artifact` 集合守恒；第 3 条已明确限定旧完整性谓词不成立的半写/placeholder 保持 incomplete，并明确旧 complete 但不可见行保持 complete、仍不可见。合法无 artifact、软删、父书删除反例已实跑，不再与断言冲突。 |
| R4-002 | **FIXED** | C-15 `:225–229` 已要求相同算法、decoder 名称/版本/参数的可比 pixel 证据；不可比先重算；匹配必须一对一唯一。重复 occurrence 明确禁止 ordinal/locator 锚定自动保续，整组 needs_confirmation，并保留旧 PageId、人工版本、进度。唯一页插入、重复页插入/删除/重排及 profile 变化的模型结果见 §5。 |
| R4-003 | **PARTIAL** | 固定示例 remaining 已改为 7，item/totals 字段同名且算术一致；部分取消、部分失败、unsupported-only 三例成立。整 source skip 与部分已引用的 source 级计数归属已有说明。但 accepted 即取消要求 counts 全 0，与“pending_pages=未处理页数”冲突；公式中的“计划总页数”未明确是否排除已引用/策略跳过页。见 R5-001。 |
| R4-004 | **FIXED** | C-15 引用已为 §3.2；PREREQ-1 AC-7 已为 17/17 且缺记录失败；FEA-09 AC-7 明列 `SOURCE_PROJECT_MISMATCH` 同事务拒绝与回滚负测，AC-8 为 17/17；`git diff --check` 无输出。另发现的同批版本残留单列 R5-002。 |

## 3. r1–r3 不回退抽查

| 项目 | 结果 | 本轮依据 |
|---|---|---|
| C-05 模式分派，R2-001 | **保持 FIXED** | managed 仅进入原 `V_artifact`；referenced 必须进入 `V_ref`，不能借 valid artifact 绕过 incomplete/非 healthy 条件。 |
| C-05 原 managed 语义 | **保持** | 去除新增 §3.1/§3.2 后，原 §3 内容完整保留；VISIBLE_TYPES、稳定性及原参考 SQL 未改。 |
| C-06 方向、四维 scope、双侧 Verify | **保持 FIXED** | Host dispatch 前铸造；Host 解析授权根，Core 读取/commit 前本地验证；无 Core→Host RPC 的隐含依赖。 |
| 即时撤销、失联，R1-003 | **未发现回退** | 持久化 generation→废止→提交边界停止→ACK；EOF/transport 失败废止全部 grant；未退回 TTL 模型。 |
| 加密 Plan，R2-002 | **保持 FIXED** | Plan 不消费密码、不解密；只绑定容器摘要和可读结构元数据；Start 重验后解密。 |
| WireLog 脱敏，R2-005 | **保持 FIXED** | 覆盖 Register、Plan、Start 及响应、secret_ref 整对象、嵌套 path；原行和 hex 均须来自脱敏字节。仅确认契约，未运行生产扫描。 |
| location 唯一，R3-001 | **保持 FIXED** | source 内物理身份唯一、单一 current、跨 Registry 原地重授权；实际更新及约束负测通过。 |
| 项目归属，R3-006 | **保持 FIXED** | C-15 明确应用层同事务守卫；C-16 错误码及 FEA-09 AC-7 责任均存在。参考守卫回滚通过，不冒充生产 handler 测试。 |
| 迁移回调边界，R2-006 | **保持 FIXED** | 同连接只读 DB 查询；资源仅经注入 verifier；禁止写、Host/网络及第二连接；typed rollback 条款保留。 |
| 旧 managed 写入维护，R1-006 | **未发现回退** | 各创建路径显式维护完整性列；live 判重与含软删 max order 分开。 |
| 报告归档，R2-008 | **保持 FIXED** | r1–r4 字节数及完整 SHA-256 均核验一致。 |
| PDF 身份与观察分离 | **保持并补齐** | page-identity 不含 decoder/scale；跨版本采用可比 pixel 证据，重复组不自动保续。 |
| receipt、版本控制信息 | **仍有残留** | R3-004 经 R4-003 延续的问题尚未全闭；R3-005 对应的版本一致性出现 v4 残留。分别列 R5-001/002。 |

## 4. UNFREEZE 合规核验

### 差异范围

r4 reviewed_head 至本轮 HEAD：

```text
M doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md
M doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md
M doc/reviews/CONTRACT-UNFREEZE-2026-11-03.md
A doc/reviews/FEA-09-PREREQ-1-r4.md
M doc/tasks/FEA-09-PREREQ-1.md
M doc/tasks/FEA-09.md
```

Task 基线至 HEAD 共 17 个文档路径，包含当前治理指针、两份候选契约、C-05/C-06、UNFREEZE、历史报告和相关 Task。

指定范围检查确认：

- `src/**`、`apps/**`、`tests/**` 无差异。
- 依赖、打包无差异。
- 既有 `FEA-CONTRACT-FROZEN-*` 记录无差异。
- `verify_pins.ps1` 尚未修改，仍为 15 项 map。

### 最小性与原语义

C-05/C-06 相对原冻结版本的变更集中于 referenced 可见性、三谓词拆分、授权方向、四维 scope、双侧 Verify、撤销与相应接口说明。未发现无关产品扩域。

原 C-05 §3 在去除新增段落后完整保留；C-06 原九条安全约束连续文本完整保留。原冻结内容 SHA-256 与 UNFREEZE 载体一致：

```text
C05 b34db88768790a982c00d6b78a9649c24047e15d2ba86e3c0bf6a5a293ec8d25
C06 b798dd8a9b3839ac0c8e18e19dd3d515080075db53d83726e18cf76343beaef8
```

载体已登记同批 v5 复核、最后元数据编辑、重算 pin、更新当前冻结记录并保留历史、更新 matrix 的顺序。**流程载体合规；尚未获得可执行重冻的 approved 结论。**

C-15 标题、状态与变更记录为 v5；C-16 标题、状态与变更记录为 v5，但三处仍引用 C-15 v4，见 R5-002。

### 当前 pin 结果

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

EXIT 1。**恰好 C-05/C-06 待重冻，其余 13 项匹配。** 当前结果没有覆盖 C-15/C-16，不能表述为 17 项通过。

## 5. 独立复跑结果

### 5.1 方法与环境

```text
Python 3.14.6
SQLite 3.50.4
```

通过 `py.exe -B -c PROGRAM`，直接导入真实代码：

```python
from infrastructure.sqlite.schema import default_migrations, Migration
from infrastructure.sqlite.migrator import MigrationRunner, read_schema_version
from infrastructure.sqlite.connection import SchemaTooNewError
```

从 C-15 第一个 SQL fenced block 提取原文，构造：

```python
Migration(7, "v7__source_storage", sql)
```

全部连接为 `:memory:`，启用 `PRAGMA foreign_keys=ON`。未修改迁移器。

| 程序/输入 | UTF-8 SHA-256 |
|---|---|
| C-15 提取 SQL | `abbf4e5f9415f392596faebc38690b6a58dd7f96941f51802621b68a2a3f8a91` |
| 数据库主程序 | `6f2a6aa367d474168826d455781c3ef175ecf0f4340fbb3b386849afe04fc867` |
| PDF/receipt 模型程序 | `568f7fa420391eceb7646555fd003a1b9724fd03cd5b4bc9b0040fe3ed853203` |
| 修正 fixture 后的扩展数据库程序 | `bc905fa66fbbe928dadb758c8f374c3961aaa64d8109e3ad8c8a1600ae0fc2b6` |

### 5.2 六个旧版本升级、回填与双集合守恒

分别建立真实 v1–v6 schema 并插入合法 fixture，先补齐至 v6，捕获基线，再执行 v7。

测试覆盖：

- 无 artifact 的完整页。
- 完整软删页。
- 父书已删除的完整页。
- 导入元数据不完整、但 original revision valid 的可见页。
- placeholder。
- 区域人工文本、区域 Lock、page Lock。
- artifact current 指针、pinned revision。
- 已存在的阅读进度。

结果：

```text
UPGRADE 1 ->7 COMPLETE [] V [('half', 0)]
UPGRADE 2 ->7 COMPLETE [('deleted',), ('full',), ('parentdeleted',)] V [('half', 0)]
UPGRADE 3 ->7 COMPLETE [('deleted',), ('full',), ('parentdeleted',)] V [('half', 0)]
UPGRADE 4 ->7 COMPLETE [('deleted',), ('full',), ('parentdeleted',)] V [('half', 0)]
UPGRADE 5 ->7 COMPLETE [('deleted',), ('full',), ('parentdeleted',)] V [('half', 0)]
UPGRADE 6 ->7 COMPLETE [('deleted',), ('full',), ('parentdeleted',)] V [('half', 0)]
```

六个起点均满足：

| 检查 | 结果 |
|---|---|
| 旧 pages 全列逐值比较 | 不变，仅追加新列 |
| complete 集合独立比较 | 守恒 |
| 同一时间及父级条件下的 managed V 集合、顺序 | 守恒 |
| 旧完整但不可见行 | complete 且仍不可见 |
| artifact-only 可见半写行 | incomplete 且仍按原 managed V 可见 |
| 人工文本、Lock、artifact/current/pinned、阅读进度 | 对应表全行比较不变 |
| `PRAGMA foreign_key_check` | 无结果 |
| `source_sync_plans`、`source_operations` | 未创建 |

因此 R4-001 的合法旧库反例不再被新第 3 条断言误阻。

真实 `_COMPLETE_PAGE_WHERE` 使用相关列非 NULL 判据；合法旧 schema 同时约束非 NULL 宽高为正，因此与本次回填的正宽高条件一致。本测试不推广到绕过约束构造的损坏库。

### 5.3 FK、唯一、部分唯一与 location 重授权

以下负测均被拒绝：

```text
VERSION_CROSS_SOURCE   FOREIGN KEY constraint failed
ENTRY_CROSS_SOURCE     FOREIGN KEY constraint failed
BINDING_CROSS_SOURCE   FOREIGN KEY constraint failed
CACHE_CROSS_SOURCE     FOREIGN KEY constraint failed

DUP_ORDINAL           UNIQUE(version_id, ordinal)
DUP_SORT_KEY          UNIQUE(version_id, stable_sort_key)
DUP_PROJECT_ENTRY     UNIQUE(project_id, entry_id) current
DUP_CURRENT_PAGE      UNIQUE(page_id) current
SECOND_CURRENT        UNIQUE(source_id) current
```

location 补充结果：

```text
REAUTH_IN_PLACE ACCEPTED
DUP_PHYSICAL_LOCATION_HISTORICAL REJECTED
  UNIQUE(source_id, content_digest, volume_serial, file_id)
LOCATION_CURRENT_TO_HISTORY_AND_NEW_CURRENT ACCEPTED
```

物理身份重复负测使用 `is_current=0`，确认其拒绝原因确实是物理身份唯一键，而非仅被 current 部分唯一键拦截。

另实跑确认：

```text
SUPERSEDED_HISTORY_AND_OTHER_BOOK_REFERENCE ACCEPTED
```

即 superseded 历史可保留，同 entry 可被其他 book 的独立页引用。

### 5.4 项目归属与资源边界

DDL 单独接受“页实际属于 b、binding 声称 other”的行，符合契约明确声明的数据库边界。

同事务参考守卫查询 `page→chapter→book` 后检测不符并回滚：

```text
PROJECT_GUARD_REFERENCE SOURCE_PROJECT_MISMATCH ROLLBACK
```

资源参考查询取得：

```text
original revision managed_path = managed/half.png
pages.managed_original_ref     = NULL
```

参考可读性模型结果：

```text
available=True  -> ACCEPT
available=False -> SOURCE_MIGRATION_RESOURCE_UNVERIFIED
```

**项目守卫与资源模型均为审查参考程序，不是生产 handler、真实文件读取或尚未实现的 validation callback 运行证据。**

### 5.5 PDF 身份与匹配反例

按 C-15 v5 条款建立独立匹配模型：仅相同 profile 证据可直接比较；旧、新两侧均唯一才自动保续；重复组不使用 ordinal/locator。

```text
UNIQUE_INSERT
  [NEEDS_CONFIRMATION, EA, EB]

DUP_INSERT
  [NEEDS_CONFIRMATION, NEEDS_CONFIRMATION, NEEDS_CONFIRMATION]

DUP_DELETE
  [NEEDS_CONFIRMATION]

DUP_REORDER
  [NEEDS_CONFIRMATION, NEEDS_CONFIRMATION, EB]

NEW_SIDE_DUP
  [NEEDS_CONFIRMATION, NEEDS_CONFIRMATION, EB]
```

判据如下：

| 场景 | v5 规则结果 |
|---|---|
| 唯一页前插一页 | 未变唯一内容保续 EntryId；新增页不借位置保续 |
| 重复页插入 | 重复整组确认 |
| 重复页删除 | 即使新侧仅剩一份，旧侧仍不唯一，须确认 |
| 重复页重排 | 重复组确认；其他唯一页可保续 |
| 旧侧唯一、新侧重复 | 不满足一对一唯一，不自动保续 |
| 仅元数据变化，观察 profile 也变化 | 先取得相同 profile 的重算证据，再匹配；不能直接比较不同 profile |
| 无可比证据 | 不满足自动保续条件；模型拒绝自动匹配 |

另按 page-identity 公式确认：

- 容器摘要改变，版本内 page-identity 改变。
- decoder/scale 不参与 page-identity。
- 跨版本保续使用 pixel 匹配证据，不能直接用新 page-identity 查旧页。

**以上是摘要公式及规则模型实验，未运行 PDFium 或真实 PDF 编辑、解码。**

### 5.6 旧写者拒写与 v7 失败回滚

六个升级库均被仅认识 v1–v6 的真实迁移器以 `SchemaTooNewError` 拒绝。

这是应用迁移入口拒写，不是 SQLite 引擎禁止任意 SQL。

在 v7 SQL 尾部注入：

```sql
INSERT INTO missing_table VALUES(1);
```

从空库及 v1–v6 起点执行，全部满足：

```text
ROLLBACK 0 ->6 NO_V7_SCHEMA PASS
ROLLBACK 1 ->6 NO_V7_SCHEMA PASS
ROLLBACK 2 ->6 NO_V7_SCHEMA PASS
ROLLBACK 3 ->6 NO_V7_SCHEMA PASS
ROLLBACK 4 ->6 NO_V7_SCHEMA PASS
ROLLBACK 5 ->6 NO_V7_SCHEMA PASS
ROLLBACK 6 ->6 NO_V7_SCHEMA PASS
```

v7 六张新表、pages 新列及版本元数据共同回滚；此前已成功提交的旧版本迁移保留。

### 5.7 receipt 算术

固定形状的 item/totals 同名且一致：

```text
imported_pages=12
skipped_sources=0
failed_sources=0
unsupported_entries=1
pending_pages=7
remaining_pages=20-12-1=7
```

部分取消、部分失败、unsupported-only 三例算术成立。

accepted 即取消反例：

```text
计划总页数=20
committed_boundary=0
counts 全0
remaining_pages=20

pending_pages 定义：未处理页数
实际未处理页数=20
示例 pending_pages=0
```

两者不能同时按现有定义成立。

跳过基数反例：

```text
源共20页，8页已引用，其余12页本次全部提交，unsupported=0。

若“计划总页数”=源总页数20：
remaining_pages=20-12=8

若“计划总页数”=排除已引用页后的本次计划12：
remaining_pages=12-12=0
```

正文没有选定上述基数。整源跳过同样存在“remaining=源页数”或“remaining=0”的不同解释。source 级 skipped 归属虽已明确，页级剩余边界仍不可唯一计算。

### 5.8 治理原始输出

最终按实际编码解码的 `check.ps1` 输出：

```text
Governance scope: 15 current documents; no historical directory scan.
Task: doc\tasks\FEA-09-PREREQ-1.md
WARN: 存在 11 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3125 bytes / 29 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：5162 bytes / 64 lines
Governance check: PASS (3 warnings)
```

EXIT 0，stderr 为空。pin 输出及 EXIT 见 §4。机械检查通过不替代契约语义复核。

## 6. 新 Findings 表

| ID | 级别 | 位置 | 问题、影响与最小修订 |
|---|---|---|---|
| **R5-001** | **P2** | C-16 `:94–97`，尤其 `:96` | **receipt 取消示例与 pending 定义冲突，跳过页的公式基数未冻结。** accepted 即取消要求 counts 全 0，但 pending_pages 定义为未处理页数，已知 20 页时应有 20 页未处理。部分已引用后完成、整源跳过时，“计划总页数”是否排除这些页未明确，remaining 无唯一结果。最小修订：统一 pending/remaining 的实体单位及基数；明确已引用/策略跳过页如何从本次计划中结算；修正 accepted 取消示例，补整源跳过、部分已引用后完成的计数实例。四个既有示例应给出相同字段集或明确默认值，保证 item/totals 可直接相加。无需增加生产范围。 |
| **R5-002** | **P2** | C-16 `:6`、`:161`、`:173` | **同批依赖仍引用 C-15 v4。** 标题、状态和 UNFREEZE 已为 v5，但依据、接口表及冻结条件三处仍写 v4；其中冻结条件指向的 v4 正是被 r4 拒绝的候选。最小修订：在条款定稿提交中统一指向最终被审候选，并明确草案轮次与首次冻结版本号的对应关系；冻结记录不能把本轮 v5 复核追溯为 v4 approved。 |

本轮未发现新的 P0/P1；上述 P2 仍使本次“R4 全闭环、最终冻结就绪”的目标未满足。

## 7. 未覆盖／无法核验项

1. 尚未实现的生产 validation callback、违规回调拦截、异常映射及真实资源失败回滚。
2. 真实 PDF 解码、重编码、插页、重复 occurrence 确认与绑定发布。
3. source-read 生产 IPC、撤销/commit 竞态、ACK 超时、EOF 后后台停止。
4. Windows 原生 DPAPI、ACL、跨进程/跨 session 锁、原子替换和断电恢复。
5. ZipCrypto/PDFium 密码产品路径、内存清零及实际日志秘密扫描。
6. build、全量 Python/.NET 回归、UI 端到端和旧 FEA-06 四 PNG 本轮指纹复跑。
7. 任意损坏库、全部人工数据组合及真实用户库；仅覆盖代表性合法 fixture。
8. 扩展后的 17 项 checker 尚不存在，未执行其缺记录、缺契约、缺 pin、错 pin 负测。
9. 本轮未写报告、Handoff 或 EV；归档及生命周期更新由 DSH 执行。
10. 未重开或重新验收 FEA-08；未对 FEA-09 进行 scope review。

## 8. 冻结建议

**需最小返修；当前四份契约不可据本报告直接同批冻结。**

最小修订集仅为 R5-001、R5-002：统一 C-16 的计数基数、取消/跳过示例及三处版本引用。C-15 的本轮两项 P1 修复无需因本报告重做；C-05/C-06 未发现需要新增语义修改。

完成修订并获得新的独立复核 approved 后，冻结前最后动作如下：

1. **固定条款定稿 head。** 归档本报告，记录逐项 disposition；修改后的 C-16 字节需重新复核，不能沿用本轮未批准结论。
2. **统一最终版本并最后编辑状态。** C-05/C-06 改为 `FROZEN v1.1`；C-15/C-16 首次正式冻结按拟定 `FROZEN v1.0` 登记，并明确其对应最终草案轮次。若采用其他正式版本号，由 DSH 在冻结前统一所有载体和引用，避免将“草案 v5”与“冻结版本”混用。
3. **最后编辑后计算三种指纹。** 工作树原始字节 SHA-256、`git hash-object`、固定提交 `git cat-file blob <commit>:<path>` 内容 SHA-256，并记录 blob ID。§1A 明确口径，§1B 明确 reviewed bytes 与最终冻结字节差异。
4. **更新 FROZEN-C05/C06。** 更新当前 v1.1 pin、复核依据和冻结条件；保留 v1.0 pin、旧 Review 及已有 pin 修正历史；当前 pin 与历史 pin 必须可区分。
5. **建立 FROZEN-C15/C16。** 登记最终版本、固定提交、三种指纹、逐项条件、边界及 §1A/§1B。
6. **更新 freeze matrix。** 更新 C-05/C-06 重冻注记，追加 C-15/C-16；冻结全集为 17 对象，其余契约与历史证据保持原字节。
7. **扩展 `verify_pins.ps1` 并验收失败分支。** 不能仅增加 map 后保留缺记录 skip。
8. **归档 check/vpins 原始日志。** 包含 cwd、head、命令、解释器/环境、EXIT、原始 stdout/stderr；最终要求 check PASS、vpins 17/17。按 Task 另完成四 PNG 和范围检查。
9. **完成生命周期和集成验证。** Task AC/v3 状态标记、Handoff、EV、delivery/integration head、资源清单及 closeout、ledger、STATUS、PLAN、rolling checkpoint 全部同步；DSH 完成集成验证后才设 done。

### 17 项 pin 扩展验收

固定全集：

```text
C01b C02 C03 C04b C05 C06 C07 C08 C09
C10 C11 C12 C13 C14 C15 C16 FEA01
```

新增 map 项：

```powershell
'C15'='FEA-C15_SOURCE_STORAGE_DRAFT.md'
'C16'='FEA-C16_SOURCE_READ_WIRE_DRAFT.md'
```

验收必须同时满足：

- 17 个当前冻结记录、契约及 pin 全部存在并匹配。
- 明确实际校验数量为 17，不把 skip 算成功。
- 缺记录、缺契约、缺 pin、pin 不匹配均返回非零。
- 当前 `MISSING-RECORD ... skipped` 分支在冻结 Gate 中改为失败。
- C-05/C-06 读取当前 pin，保留且不误读历史 pin。
- 其他 13 项 pin 口径不变。
- 负测使用内存或 Task 隔离 fixture，不修改真实冻结文件。
- 扩展前保留现有 15 项基线，扩展后留存 17 项及失败分支的原始日志。

## 9. 结论与推荐下一步

**PREREQ-1 当前不能冻结并 done；FEA-09 当前不能据此前置进入 scope-r2。**

修正 R5-001/002、取得新独立复核 approved、完成四份契约最终冻结、17 项门禁及 PREREQ-1 集成收口后，**FEA-09 可以进入 scope-r2 文档复审**。这不等于 ready，也不自动授权实现。

推荐下一步为 **DSH 在现有 FEA-09-PREREQ-1 内完成最小文档返修**，随后任命未参与返修的新独立上下文复核。

| 字段 | 建议 |
|---|---|
| Task | `FEA-09-PREREQ-1`：r5 剩余契约问题闭环 |
| Agent | DSH 返修及处置；新独立上下文 Reviewer 复核 |
| Recovery point | `G:\CODEX\New Manga`，`main`；Task base=`6e274dd94c5b64d8fbc3f9d578363d3c502a2b68`；本轮 head=`90b9600b13e531b3c00407d4af918737037b133a` |
| Scope | 当前 Task 已授权 C-16、UNFREEZE、Task 及必要治理文档；冻结动作待 approved 后执行 |
| 禁止范围 | 生产代码、依赖、用户数据、其他冻结契约及历史证据；禁止 push，不重开 FEA-08 |
| Deliverables | r5 原字节归档、逐项 disposition、修订固定 commit 与指纹、新 Review；通过后补冻结记录/Handoff/EV |
| Verification | 重跑 receipt 取消/跳过反例、版本引用检查、内存迁移及约束/回滚、check/vpins；NOT_RUN/LIMITED 如实保留 |

可直接转发：

> DSH：请在 `G:\CODEX\New Manga`、`main` 处理 FEA-09-PREREQ-1 r5。Task base=`6e274dd94c5b64d8fbc3f9d578363d3c502a2b68`，reviewed_head=`90b9600b13e531b3c00407d4af918737037b133a`；先核实当前 HEAD/工作树，原字节归档本报告。范围限当前 Task 授权文档：修正 C-16 accepted 取消的 pending 计数，明确整源跳过及部分已引用时 remaining 公式的计划基数，补齐自洽实例，并统一第 6/161/173 行同批 C-15 版本引用。提交逐项 disposition、固定 commit 和新指纹；重跑 receipt 反例、内存迁移/约束/回滚及只读 check/vpins，任命未参与返修的新独立上下文复核。禁止修改生产代码、依赖、用户数据或历史冻结证据，禁止 push，不重开 FEA-08。approved 后才执行四份契约冻结、17 项 checker 扩展与负测、原始日志归档及 Task/Handoff/EV/ledger/STATUS/PLAN/checkpoint 收口；完成 PREREQ-1 后再提交 FEA-09 scope-r2。