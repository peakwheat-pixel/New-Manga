# FEA-09-PREREQ-1 契约独立复核 r2

## 0. 元信息

| 项目 | 记录 |
|---|---|
| Reviewer | Codex，当前独立审查会话 `/root`；未参与被审契约起草或 r1 返修，不参与后续实现 |
| 模型 | GPT-6 系列；本会话未提供可验证的精确模型型号 |
| 辅助审查 | 独立上下文 `/root/standards`、`/root/spec`，仅只读审查 |
| 时间 | 2026-11-03，最终检查时间 16:44:07，Asia/Shanghai |
| 仓库 | `G:\CODEX\New Manga` |
| 分支 | `main` |
| Git common directory | `G:/CODEX/New Manga/.git` |
| reviewed_head | `b7e53c2bfdcc4fd52480b2e14cdca0d11d261d2a` |
| 返修差异基线 | `920c09525`，即 C-15/C-16 v1 草案提交 |
| Task 基线 | `6e274dd94c5b64d8fbc3f9d578363d3c502a2b68` |
| 工作树 | 审查开始、结束均干净；HEAD 未变化 |

被审文件指纹：

| 文件 | `git hash-object` | 工作树 SHA-256 |
|---|---|---|
| `doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md` | `f4e71bc4a1522c492d296351a024e6b38772e642` | `0c702fbefb843e3ed024416553fa14137c8d2251d877c8225bece9523d5bb9bb` |
| `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | `8a154c3d49475d2ce16f1f05cb4386f749d2ba56` | `69f990539891a30420257419ad62680c529fe7ed12fe8b9f5a5787994f2277de` |
| `doc/plan/FEA-C05_PAGE_VISIBILITY_DRAFT.md` | `9fca4286af5c4080562a23a1c8a8194a4b8d1f88` | `52408113f7832512fd6a66dcc8f37085cd3263ec65d7965041db6f83643dda18` |
| `doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md` | `114dbfb482d7a2fdae0900885dbe5fc04152b308` | `2c076c8ee1d6546f618e0bffb5b4b80056e467fae5f6e3e250b633d091b91623` |
| `doc/reviews/CONTRACT-UNFREEZE-2026-11-03.md` | `ff8b8234d497d94615d5fc29b00a544dedf354aa` | `810cdc4c4717e0aaf31ec33cecca5fcf65a2998991bee98097346bf07bb1316c` |

上述 SHA-256 在结束检查时再次计算，全部不变。

**证据限制：指定的 `doc/reviews/FEA-09-PREREQ-1-r1.md` 不存在。** 文件读取返回 `ENOENT`；以下命令亦无输出：

```text
git log --all --oneline -- doc/reviews/FEA-09-PREREQ-1-r1.md
```

因此，§2 是对用户本轮列明的 R1-001…R1-013 问题摘要逐项核验，不能冒充对 r1 原报告全部论据、建议和验收条件的原文闭环核验。

实际只读检查：

| 命令/操作 | 结果 |
|---|---|
| `git --no-optional-locks status --short` | 开始、结束均无输出 |
| `git rev-parse HEAD --git-common-dir --abbrev-ref HEAD` | HEAD、common directory、`main` 如上 |
| `git diff --stat 920c09525...HEAD` | 6 个文档文件变更，415 insertions、258 deletions |
| `git diff --name-status 6e274dd94 HEAD` | 任务建立以来的治理文档、草案、报告和 Task 变化；无生产代码 |
| `git diff 920c09525...HEAD -- <C-05> <C-06>` | 已逐 hunk 阅读 |
| `git diff --name-only 920c09525 HEAD -- src apps tests 'doc/plan/FEA-CONTRACT-FROZEN-*'` | 无输出 |
| `git hash-object <被审文件>` | 结果见上表；未使用 `-w` |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | EXIT 1，`PIN AUDIT: FAIL (2)` |
| `pwsh -NoProfile -File tools/governance/check.ps1` | EXIT 0，`Governance check: PASS (3 warnings)` |
| `python -B -c <内存审查程序>` | EXIT 0；Python 3.14.6、SQLite 3.50.4；结果见 §4 |

常规 `exec_command` 启动工具返回 Windows error 740；随后通过 Node `child_process.execFile` 执行上述命令，未申请提升权限。Python 使用 `-B`，数据库全部为 `:memory:`。

**未修改声明：未修改仓库文件、冻结记录、用户数据；未执行 git add、commit、push；未创建数据库文件或测试脚本文件。**

## 1. Verdict

**`changes_requested`**

本轮 Findings：**P0=0 / P1=6 / P2=3**。

DDL 的主要关系约束和逐版本失败回滚已得到独立运行证据，但可见性、加密 Plan、PDF 内容身份、授权代次与 location、日志脱敏仍有阻断问题。r1 原报告缺失也阻止完整闭环确认。

## 2. r1 findings 闭环表

以下 `FIXED` 仅表示本轮提供的对应问题摘要已由实际正文或独立实验覆盖，不代表恢复了缺失的 r1 原文。

| r1 ID | 状态 | 实际依据与判断 |
|---|---|---|
| R1-001 | **PARTIAL** | C-05 `:51–86` 已新增 referenced 分支，包含父级删除、页创建时间、稳定性与 `R`；原 §3 谓词字节保留。但 `:68` 的分支 OR 定义与 `:77` 的统一完整性条件不等价，且 artifact 分支未排除 referenced 页。C-15 `:241` 同样采用另一种定义。见 R2-001。 |
| R1-002 | **FIXED** | C-06 `:37–39`、`:52–53` 明确 Host 唯一授予、dispatch 前铸造、Host 解析授权根、Core 本地 Verify；四维 scope 有 locator/ordinal 对齐规则。C-16 `:19`、`:49–66` 与此方向一致。此处为契约静态确认，未声称实现 PASS。 |
| R1-003 | **FIXED** | C-06 `:42`、`:54`、`:69–70` 与 C-16 `:21`、`:150` 明确撤销命令、ACK、commit 前复验及 EOF fail-closed，不再以 TTL 替代撤销。运行时同步、ACK 超时和竞态仍须实现 Task 验证。 |
| R1-004 | **FIXED** | C-15 `:103–105`、`:132–135`、`:158–166`、`:186–187` 给出同源复合 FK、稳定排序键/ordinal 唯一、项目内 current entry 唯一及 cache 三列 FK；内存负测均按预期拒绝。 |
| R1-005 | **PARTIAL** | C-15 `:18`、`:219–221` 明确物理身份及 occurrence 不合并；但 `:199` 允许新授权代次创建 location，与 `:89` 唯一键直接冲突，已复现。跨 Registry 重复授权的 source 复用规则也未形成明确决策。见 R2-004。 |
| R1-006 | **FIXED** | C-15 `:254–260` 覆盖 managed 创建路径、同事务完整性维护、失败保持 incomplete、禁止 update 静默翻转；`:248–249` 正确区分 live 判重与包含软删页的 `max_source_order`，与 `library.py:304–337` 一致。可见性冲突另计 R2-001。 |
| R1-007 | **PARTIAL** | C-16 `:83–110` 已改为接受后后台执行、轮询和取消，符合现有 stdio/Export 先例。但 accepted 状态、取消、重放和项目忙锁的完整行为仍缺定义。见 R2-007。 |
| R1-008 | **PARTIAL** | C-16 `:73–79`、`:114–116` 补充密码与 plan 生命周期、有效期和确认重验；但无密码 Plan 无法生成加密 PDF/ZipCrypto 成员要求的内容 digest。见 R2-002。 |
| R1-009 | **PARTIAL** | C-16 `:93–108` 已明确 operation 指纹、冲突、会话内 receipt、自然键重试、一页事务和部分提交；但 accepted/cancelled/failed 重放，以及部分容器 outcome 与混合计数单位仍不完整。见 R2-007。 |
| R1-010 | **PARTIAL** | C-15 `:33–45` 已正确承认逐版本事务；SQL 失败实测停留 v6。新增 callback/基线/资源守恒要求，但 callback 的“只能查询 DB”与资源可读性验证边界尚需消歧；真实 callback 尚无实现可运行。见 R2-006。 |
| R1-011 | **FIXED** | C-15 `:264–286` 已明确逐根身份、命名互斥+文件锁、持锁重载、generation 比较、原子替换、缺失与损坏区分、显式 reset、DPAPI LIMITED 边界。未进行 Windows 原生验证。 |
| R1-012 | **PARTIAL** | C-15 `:208`、`:212` 已命名 `pixel-digest/1` 并区分 SourceVersion 与 rendition，但 PDF entry 内容身份仍依赖未冻结参数的像素结果，且允许更新相关观察列。跨版本身份保续尚不稳定。见 R2-003。 |
| R1-013 | **PARTIAL** | v7 实际新建 6 表、预留 2 表的范围可确认；但日志脱敏覆盖不全、C-06 仍引用旧 revision 模型、r1 引用悬空。见 R2-005、R2-008、R2-009。 |

## 3. UNFREEZE 合规核验

### 3.1 Git 差异范围

`git diff --stat 920c09525...HEAD` 对应本次返修提交，仅包含：

```text
doc/plan/FEA-C05_PAGE_VISIBILITY_DRAFT.md
doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md
doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md
doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md
doc/reviews/CONTRACT-UNFREEZE-2026-11-03.md
doc/tasks/FEA-09-PREREQ-1.md
```

因此，准确表述为：**两份原冻结契约、两份草案、一个新增载体和 Task 扩域记录发生变化**，并非只有五份被审文件变化。

从 Task 的 `6e274dd94` 基线比较，还包含 STATUS、PLAN、ledger、checkpoint、FEA-09 scope-r1 和相关 Task 的建立/更新。未发现 `src/**`、`apps/**`、`tests/**` 或其它冻结契约变更。

### 3.2 原冻结字节与语义保留

独立字符串比对确认：

- C-05 原 §3 可见性、稳定性和 `VISIBLE_TYPES` 段落完整保留。
- C-06 原九条安全约束完整保留。
- 两份原冻结记录未改动。
- 基线 C-05/C-06 blob 的 SHA-256 分别为载体登记的旧 pin：

```text
C05 b34db88768790a982c00d6b78a9649c24047e15d2ba86e3c0bf6a5a293ec8d25
C06 b798dd8a9b3839ac0c8e18e19dd3d515080075db53d83726e18cf76343beaef8
```

**字节保留成立，但语义保留尚未成立。** C-05 新增 `:77` 会为 managed 页加入原谓词不存在的额外条件，与载体 `:27`、`:40` 的行为不变承诺冲突。

### 3.3 pin 漂移

实际输出：

```text
OK C01b 3c9f5af7d74f
OK C02 bb365ca891a7
OK C03 b77e7968a00b
OK C04b 694ce5bc8c8b
MISMATCH C05 pin=b34db8876879 actual=52408113f783
MISMATCH C06 pin=b798dd8a9b38 actual=2c076c8ee1d6
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

结论：**恰好两项漂移，其余 13 项 OK。** 当前 FAIL(2) 与两份待重冻契约对应，不代表其新语义已通过审查。

### 3.4 流程顺序

载体 `:48–51` 明确：

```text
独立复核 → approved/P0/P1=0 → 最后元数据编辑
→ 计算最终 pin → 更新冻结记录及历史 → 更新 matrix
```

这符合冻结记录纪律。当前 C-15/C-16 和 UNFREEZE 载体都标为待复核；没有发现已用未冻草案释放生产实现的事实。

但仍有两点需修正：

1. 新文档对 C-05 的解释与原谓词发生冲突，不能靠引用 C-15 消除，必须修订新增条款后再审。
2. `verify_pins.ps1:6–13` 当前固定检查 15 项，**不包含 C-15/C-16**。同批冻结时必须明确扩展检查覆盖，不能把原有 15 项 PASS 当成新增两份契约已受校验。

## 4. 独立复跑结果

### 4.1 方法与实际调用

实际调用形式：

```text
python -B -c PROGRAM
```

程序通过 Node `execFile` 参数传入，未经过 shell 拼接、未落盘。最终程序 UTF-8 SHA-256：

```text
54bbd26aa5b33f878f753440e80428c347a234abd5d92fbdebbb83d0d1940f14
```

程序直接导入真实代码：

```python
sys.path.insert(0, str(pathlib.Path("src").resolve()))
from infrastructure.sqlite.schema import default_migrations, Migration
from infrastructure.sqlite.migrator import MigrationRunner, read_schema_version
from infrastructure.sqlite.connection import SchemaTooNewError
```

从 C-15 工作树正文提取第一个 SQL fenced block，构造：

```python
Migration(7, "v7__source_storage", sql)
```

所有连接使用：

```python
sqlite3.connect(":memory:")
PRAGMA foreign_keys=ON
```

真实 `default_migrations()` 执行 v1–v6，再由真实 `MigrationRunner` 执行 v7。没有使用草案作者的验证结论替代实跑。

### 4.2 回填、数据保留、约束

| 检查 | 实际结果 |
|---|---|
| 真实迁移链升级到 v7 | `version: 7` |
| 完整 managed 页回填 | p1、软删 p2 均为 `managed/complete` |
| 不完整/placeholder 页回填 | p3、p4、p5 均为 `managed/incomplete` |
| 旧页 ID、排序、source_order、hash、managed ref、宽高、Lock | 迁移前后逐项相等 |
| 人工区域文本、区域 Lock | `PRESERVED ('{"manual":"keep"}', 1)` |
| version 指向其它 Source 的 location | FK 拒绝 |
| entry 指向其它 Source 的 version | FK 拒绝 |
| binding 跨 Source/version 错配 | FK 拒绝 |
| 重复稳定排序键 | UNIQUE 拒绝 |
| 重复 ordinal | UNIQUE 拒绝 |
| 同项目重复 current entry | UNIQUE 拒绝 |
| 同页第二条非 superseded binding | 部分唯一索引拒绝 |
| superseded 历史 binding | 接受 |
| 同 entry 在其它 book 建引用 | 接受 |
| cache 的 source/version/entry 错配 | 三列 FK 拒绝 |
| 合法 cache 行 | 接受 |
| `PRAGMA foreign_key_check` | `[]` |
| 新建表 | `sources/source_locations/source_versions/source_entries/page_bindings/rendition_cache` |
| 两张预留表 | 未创建，符合正文 |

首轮 binding 错配负测先被项目 entry 唯一键拦截，不能证明 FK；已调整为不触发该唯一键的项目后复跑，最终得到：

```text
binding_cross_source: REJECTED FOREIGN KEY constraint failed
entry_cross_source: REJECTED FOREIGN KEY constraint failed
```

### 4.3 旧写者拒写与失败回滚

旧 `default_migrations()` 迁移器打开 v7 内存库：

```text
old_writer: SchemaTooNewError
```

此结论覆盖迁移器启动拒写门禁，不声称 SQLite 自身禁止任何任意 SQL 写入。

v7 DDL 尾部注入：

```sql
INSERT INTO no_such_table VALUES (1);
```

真实迁移器结果：

```text
rollback_from_v0:
{'schema': 6, 'metadata': '6', 'source_tables': 0, 'source_mode_column': False}

rollback_from_v6:
{'schema': 6, 'metadata': '6', 'source_tables': 0, 'source_mode_column': False}
```

这证明：

- v7 的表、列和版本元数据共同回滚。
- 从空库启动时，先前已成功的 v1–v6 仍保留。
- **整链不是一个事务**，C-15 v2 对此修订正确。

### 4.4 额外反例

同一 `registry_id/content_digest/volume_serial/file_id`，仅把 `authorization_generation` 从 1 改为 2，创建新 location：

```text
same_physical_new_generation:
REJECTED UNIQUE constraint failed:
source_locations.registry_id,
source_locations.content_digest,
source_locations.volume_serial,
source_locations.file_id
```

与 C-15 `:199` 的允许规则冲突。

另一个实验结果：

```text
wrong_project_page_parent: ACCEPTED
```

DDL 目前只分别检查 `page_id`、`project_id` 存在，不验证该页经 chapter 实际属于该 book。C-15 `:196` 已有项目归属不变量，因此实现必须在同一提交路径强制验证，不能宣称 DDL 已覆盖此关系。

### 4.5 C-16 与现有运行时

静态对照确认：

- `core_service.py:5655–5673` 为逐行同步 dispatch；长 handler 确实会阻塞后续 Cancel/GetReceipt。
- `core_service.py:3903–3906` 调用 Export runtime 的 `start`。
- `application/export/service.py:800`、`:835–840`、`:857` 存在后台线程启动及取消先例。

因此 C-16 的异步 Start→轮询方向可实施。

按操作能力检查、撤销 ACK、EOF、单页提交及自然键恢复已有明确要求；但本轮没有运行新协议实现。加密 Plan、日志脱敏和状态全集仍存在 §5 所列缺口。

## 5. 新 Findings 表

本轮 ID 同时承载重新发现的未闭环问题，不表示全部为 v2 新引入。

| ID | 级别 | 文件:行 | 问题、依据及最小建议 |
|---|---|---|---|
| **R2-001** | **P1** | C-05 `:68`、`:76–84`；C-15 `:241`；UNFREEZE `:27`、`:40` | **总可见性存在不等价定义。** `V_artifact∨V_ref` 保留原 artifact 条件；`:77` 却统一要求页完整性和页创建时间。旧 managed 页具有 valid revision、但页导入元数据不完整时，两者结果相反。另原 artifact 条件无 mode 限制，referenced 页有 valid artifact 时可绕过 incomplete/非 healthy 不可见要求。应在新增条款中明确模式分派，保留原 managed 行为，统一 C-05/C-15 定义，并加入上述反例判据。 |
| **R2-002** | **P1** | C-16 `:73`、`:87`、`:114–115`；C-15 `:208–212` | **加密 Plan 无法满足其内容摘要要求。** Plan 不允许使用密码，却必须生成 ordered entries 的 content digest；加密 PDF 的 pixel digest 依赖解密渲染，ZipCrypto 成员明文摘要也依赖解密。确认前重验同样无法按现有顺序完成。需选择安全 Plan 密码生命周期，或明确加密源有限预览、未知计数/摘要、解密验证与必要再次确认流程。 |
| **R2-003** | **P1** | C-15 `:208`、`:212–213`、`:220`；C-01b `:87` | **PDF 内容身份与 rendition 观察仍未彻底分离。** PDF entry 使用 pixel content digest，跨版本匹配也使用它；但 decoder/scale 变化允许更新 pixel 观察，未冻结身份摘要的 canonical 渲染参数。相同源字节不同 scale 会产生不同指纹；更新 content digest 又会破坏既有 binding 的 verified digest。需明确不可变的身份摘要来源及算法参数，把 rendition pixel observation 分离，覆盖 decoder/scale 升级后的 EntryId 保续。 |
| **R2-004** | **P1** | C-15 `:74–89`、`:199`、`:220–221` | **授权代次与 source/location 复用规则不闭合。** 正文允许新代次创建 location，DDL 却拒绝该插入，已独立复现。换新 Registry ID 又能绕开唯一键，正文没有明确选择已有 Source/location/version 的规则。需冻结重授权、重复注册、跨项目复用的决策，明确更新旧 location 还是插入新行，再令 DDL 与之相符。 |
| **R2-005** | **P1** | C-16 `:56`、`:88`、`:144–146`；`WireLog.cs:82–102` | **前置脱敏配方覆盖不足。** `:144` 只规定 RegisterSourceReadGrant 的 secret_ref/signing_key；StartImportReferences 自带 secret_ref，grant 中另有 entry path。按该配方执行仍会把 token/path 或绝对路径存入 Frames/NDJSON，与全局禁令冲突。现有 WireLog 同时保存原行及 hex。需覆盖全部相关命令、嵌套路径、原行及其 hex，在构造/加入可保存 Frame 前完成脱敏并逐项断言。 |
| **R2-006** | **P2** | C-15 `:35–43` | **迁移 callback 的允许操作边界不清。** `:36` 要求 callback 只能通过同一连接做只读查询，`:43` 又要求在事务提交前验证受管文件存在且可读。需明确允许通过已取得的可信受管根做文件系统只读验证，或另设受约束验证接缝；禁止写入、异常包装和 rollback 规则应保持明确。现有 runner 尚无该 callback，不能据 SQL 测试声称此项 PASS。 |
| **R2-007** | **P2** | C-16 `:92–108` | **状态与命令组合不完整。** 状态机含 accepted，但 receipt enum 不含；同指纹重放只定义 running/completed，遗漏 accepted/cancelled/failed；Cancel accepted 未定义，busy 也未说明 accepted 是否预占。部分容器已有提交但最终 failed/cancelled 时，outcome 与 page/source 混合计数缺完整例子。补状态×命令表、原子预占/释放规则和计数示例。 |
| **R2-008** | **P1** | UNFREEZE `:6`、`:44`；C-15 `:6`；C-16 `:6`；缺失路径 `doc/reviews/FEA-09-PREREQ-1-r1.md` | **r1 原报告证据缺失，无法完成要求的原文闭环。** 工作树读取 ENOENT，Git 全部 refs 的该路径历史为空。需由 DSH 原字节归档实际 r1 报告，记录来源和指纹，再由独立 reviewer 核对原文。不得用本轮摘要或修订声明重建报告。 |
| **R2-009** | **P2** | C-06 `:75`；C-05 `:53`；UNFREEZE `:29–36` | **C-06 残留旧可见性模型。** 仍称“源读取产生的 revision 进入可见性谓词”，与 referenced 不使用 artifact/revision 的新分支冲突。应在精确 UNFREEZE 范围中登记并修正这条引用，避免重新冻结后继续出现两个模型。 |

交叉一致性结论：

- **C-05 ↔ C-15：未通过**，见 R2-001。
- **C-06 ↔ C-16：授权方向、Verify、撤销原则一致**；日志配方和旧模型引用仍需修订。
- **C-14 SC-S09…S13：DDL 的身份关系、排序、项目唯一性已有落实**；跨版本 pixel 指纹保续仍有 R2-003。
- **C-14 SC-S14…S17 / C-01b：cache 类型、预算、可再生产物和禁止 raw 源发布的方向一致**，未验证运行时实现。
- **C-07：边界保持**。C-16 `:32`、`:159` 明确 FEA-09 不新增 `IHostController`，UI-1 如需新端口须另走 UNFREEZE；未改 C-07 字节。

## 6. 未覆盖/无法核验项

1. r1 原报告缺失，无法确认原文中的全部反例、建议和闭环条件。
2. 未运行尚未实现的 v7 validation callback，包括真实受管资源可读性失败、非 SQLite 异常包装及回滚。
3. 未运行 source-read 生产协议；撤销与 commit 的竞态、ACK 超时、EOF 时后台停止均仅完成契约静态审阅。
4. 未执行 Windows 原生 DPAPI、跨进程/跨 session 锁、文件 ACL、原子替换和损坏恢复。
5. 未运行 ZipCrypto/PDFium 密码产品路径、秘密清零或日志秘密扫描。
6. 未运行 UI、Core→Host→UI 端到端、真实文件操作或系统取消。
7. 未重跑 build/全量测试或四 PNG 指纹；本轮确认相关生产及冻结记录 diff 为空，不将其等同于运行验收。

## 7. 冻结建议

**需返修；当前不建议 C-05 v1.1、C-06 v1.1、C-15 v2、C-16 v2 同批冻结。**

最小修订集：

1. 统一 C-05/C-15 的模式分派和谓词，保护 managed 原行为，阻止 referenced 借 artifact 绕过完整性分支。
2. 补齐加密源 Plan/密码/确认流程，消除无密码计算明文或像素摘要的要求。
3. 冻结 PDF 身份摘要与 rendition 观察的分离规则。
4. 统一 location 唯一键与重授权/source 复用规则。
5. 补齐全部相关 wire 命令及路径字段的前置脱敏。
6. 补齐迁移验证边界、异步状态全集及 C-06 旧引用。
7. 原字节归档 r1 报告，完成原文闭环复核。

返修并经独立复核通过后，冻结前仍须完成：

- 在单独返修提交中定稿条款；冻结提交不得夹带条款修改。
- 最后修改状态行：C-05/C-06 为 FROZEN v1.1，C-15/C-16 为对应最终冻结版本。
- 对最终字节计算工作树 SHA-256、Git blob 指纹，记录复核字节与冻结字节差异。
- 更新 C-05/C-06 FROZEN 记录，保留 v1.0 和更早历史 pin；建立 C-15/C-16 FROZEN 记录。
- 更新 freeze matrix，并由 DSH 明确处理 Task 当前“既有行不改”与本次更新 C-05/C-06 注记的范围关系。
- 明确授权并扩展 pin 检查覆盖 C-15/C-16；检查全部应冻结对象，不能只保留旧 15 项。
- 重跑 `check.ps1`、扩展后的 `verify_pins.ps1`，留存真实命令、EXIT 和输出。
- 完成 Task 的 AC、Handoff、证据和治理指针同步后，再由 DSH 集成处置。

## 8. 结论与推荐下一步

**PREREQ-1 当前不能冻结或进入 done；FEA-09 当前不能据此进入 scope-r2 或释放实现。** FEA-08 保持既有终态。

推荐下一步为 **DSH 在当前 PREREQ-1 内完成最小契约返修，再任命新独立上下文执行 r3**。本审查会话不参与返修或实现。

可直接转发的指令：

> DSH：请在 `G:\CODEX\New Manga`、`main`，以 `b7e53c2bfdcc4fd52480b2e14cdca0d11d261d2a` 为本轮审查恢复点，处置 FEA-09-PREREQ-1 r2 的 R2-001…R2-009。先核实当前 HEAD/工作树，原字节归档缺失 r1 报告；在现有契约写域内修正可见性、加密 Plan、PDF 身份、重授权复用、日志脱敏及状态/引用问题，必要的精确扩域先记入 Task/UNFREEZE。禁止修改生产代码、用户数据、其它冻结契约，禁止 push，不重开 FEA-08。交付返修固定 commit、逐项处置和更新后的被审指纹；独立复跑 v7 约束/回滚并记录门禁真实结果。随后任命未参与返修的新独立上下文执行 r3；通过前不重冻、不关闭 PREREQ-1、不释放 FEA-09 scope-r2。