# FEA-09-PREREQ-1 契约独立复核 r3

## 0. 元信息

| 项目 | 记录 |
|---|---|
| Reviewer | Codex，独立审查会话 `/root`；未参与契约起草、r1/r2 返修，不参与后续实现 |
| 模型 | GPT-6 系列 Codex；本会话未提供可验证的精确模型 ID |
| 审查时间 | 2026-11-03 16:55–16:59，Asia/Shanghai |
| 仓库 | `G:\CODEX\New Manga` |
| 分支 | `main` |
| Git common directory | `.git`，对应 `G:\CODEX\New Manga\.git` |
| reviewed_head | `47133516263c868d0de2445d024d03e651fc56e7` |
| r2 差异基线 | `b7e53c2bfdcc4fd52480b2e14cdca0d11d261d2a` |
| 初稿差异基线 | `920c09525ed3afd4d64c44923d36127f690b4a98` |
| Task 基线 | `6e274dd94c5b64d8fbc3f9d578363d3c502a2b68` |
| 审查前后状态 | `git status --porcelain=v1` 均无输出；HEAD 未变化 |
| 辅助 Agent | 未使用 |

### 0.1 被审文件指纹

以下均为实际执行 `git hash-object` 和读取工作树原始字节计算的结果；结束检查时 SHA-256 全部不变。

| 文件 | `git hash-object` | 工作树 SHA-256 |
|---|---|---|
| `doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md` | `739eb3a480371ecc4796f2d0d08f827861ef7cae` | `f3cf18a8a5ae95118cb57ec768fd6a121a9ecc1a263f6deebe68f94dd54e7ec6` |
| `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | `64c2e01d5131ffd4ad947a4b0e2e91eb108e74ce` | `8cda967d17139733b148f37a1798ad9473deb658befcea14ffe9e9bf9bcc52e7` |
| `doc/plan/FEA-C05_PAGE_VISIBILITY_DRAFT.md` | `84658ad9f4dd44ffa9d8ae00e70dc086dfc95bc2` | `13ff436af7bfbdc2a65181153a2b6140902e4aff1a8665a28e1c9c5b60167a39` |
| `doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md` | `6a6e5744c7452adba08af33d1db1023a89c1491d` | `a779a7c1691b4414dcf99fd4452f837516f07accb44f9a9b263262c860fa9eb4` |
| `doc/reviews/CONTRACT-UNFREEZE-2026-11-03.md` | `1b3a795126e6041dff98e18d6994c300be311897` | `1005d96e58d6cddd7bbd9f58d1f1e68e53442c04950539b2073ccc1c57879141` |

### 0.2 历史报告原字节核验

已完整读取两份归档原文，以其 Findings 表和正文条件核验，没有用修订声明替代。

| 报告 | 字节数 | SHA-256 | 结果 |
|---|---:|---|---|
| `doc/reviews/FEA-09-PREREQ-1-r1.md` | 25,469 | `d3ba756e7ccbb2c30653f833d6d3ebe0c4c19479f3f53627cc2b606632d54ae3` | 与指定值一致 |
| `doc/reviews/FEA-09-PREREQ-1-r2.md` | 23,339 | `d50f3a54020715e8ed2e226946a1034dae7e1b7a52a19b6e7c851f3d6a117e1a` | 与指定值一致 |

对应 Git 指纹：

```text
r1 50552e9f40ae5b5cbbe10c03d0979fd474d72065
r2 156739229a805129a4678563647d3d4ffc5191b3
```

r1 原文最终计数采用其末尾更正：P0=0、P1=11、P2=2。

### 0.3 实际命令与执行方式

常规 `exec_command` 两次在启动阶段返回 Windows error 740，未执行其中的仓库命令。随后使用 Node 文件读取 API 和 `child_process.spawnSync` 执行只读检查，未申请提升权限。

| 命令或操作 | 实际结果 |
|---|---|
| `git status --porcelain=v1` | 开始、结束均无输出 |
| `git branch --show-current` | `main` |
| `git rev-parse HEAD` | 上述 reviewed_head，结束不变 |
| `git rev-parse --git-common-dir` | `.git` |
| `git hash-object <各被审文件>` | 见指纹表；未使用 `-w` |
| `git diff --name-status b7e53c2 HEAD` | 7 个文档文件，详见 §4 |
| `git diff --name-status 6e274dd94 HEAD` | 当前 Task 建立以来的治理文档、草案、报告和任务变化 |
| `git diff 920c09525 HEAD -- <C-05> <C-06>` | 已逐 hunk 阅读 |
| `git diff --name-only 920c09525 HEAD -- src apps tests 'doc/plan/FEA-CONTRACT-FROZEN-*'` | 无输出 |
| `git diff --check b7e53c2 HEAD` | EXIT 0，无输出 |
| `git cat-file blob 920c09525:<C-05/C-06>` | 原冻结 pin 与载体登记一致 |
| `rg --files`、`rg -n`、带行号内存读取 | 对照契约、Task、当前状态及相关真实代码 |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | EXIT 1，`PIN AUDIT: FAIL (2)` |
| `pwsh -NoProfile -File tools/governance/check.ps1` | EXIT 0，`Governance check: PASS (3 warnings)` |
| `python -B -c PROGRAM` | 内存迁移、约束、回滚及反例程序均 EXIT 0 |

一轮尝试设置 PowerShell 输出编码时，受限语言模式拒绝属性赋值；该次随后执行的检查器仍 EXIT 0。最终通过按 GBK 解码原始输出取得完整中文门禁结果，不把该编码设置尝试计为无错误执行。

**未修改声明：未修改仓库文件、冻结字节或用户数据；未执行 git add、commit、push；未创建磁盘测试脚本或数据库；未访问生产 AppData、真实外部源或用户密码。报告仅由本次标准输出交付。**

## 1. Verdict

**`changes_requested`**

本轮 Findings：**P0=0 / P1=3 / P2=3**。

r2 的多数问题已实质修正，历史报告归档也已恢复。但仍有三项冻结阻断：

1. C-15 location 规范同时保留互相冲突的两套规则。
2. PDF page-identity 虽消除了 decoder/scale 漂移，却破坏 C-14 的跨版本未变成员身份保续。
3. 迁移验证仍要求“可见集合＝完整集合”，与已经明确拆开的谓词冲突，合法旧库反例已复现。

**当前四份契约不可同批冻结，PREREQ-1 不可 done。**

## 2. r2 findings 闭环表

`FIXED` 表示契约问题闭环，不表示尚未实现的产品行为已运行通过。

| ID | 状态 | 原文条件与实际核验 |
|---|---|---|
| R2-001 | **FIXED** | C-05 `:53–76` 已明确模式分派，managed 仅用原 P1–P5，不新增 pages 完整性限制；referenced 无法经 artifact 绕过。C-15 `:244–250` 定义一致。原 C-05 §3 字符串完整保留。三项反例结果见 §5.4。迁移断言另有 R3-003，不否定本项 V 定义修正。 |
| R2-002 | **FIXED** | C-16 `:73–79`、`:114–116` 改为加密源有限预览，不请求密码、不解密、不要求明文或像素摘要；使用原始容器 digest 和可读结构元数据。Start 先重验容器及代次，再解密计算 entry digest；变化返回 stale 并重新预览。Import 每次密码重试生成新引用，消费、失败和终态清理已有明确条款。 |
| R2-003 | **PARTIAL** | C-15 `:210–214` 已将 page-identity 与 pixel observation 分离；固定源字节下更新 decoder/scale 不改变 content digest、EntryId 或 binding，内存验证成立。但 `:222` 仅按该身份匹配跨版本候选；容器摘要变化会使全部 PDF 页身份变化，与 C-14 SC-S09/SC-S12 不闭合。见 R3-002。 |
| R2-004 | **PARTIAL** | DDL `:89–93` 已采用 source 内物理身份唯一键及 current 部分唯一；`:224` 明确跨 Registry 命中复用、原地更新。内存更新成功。但规范性 `:201` 仍写旧 Registry 唯一键，并允许新代次插入 location，与 DDL、`:224` 冲突；插入反例被拒绝。见 R3-001。 |
| R2-005 | **FIXED** | C-16 `:144–146` 已覆盖全部携带敏感/路径字段的命令及响应，列明 Start、Plan、grant、secret_ref 整对象、嵌套 path；明确在构造可保存 Frame 前重写，原行及 hex 均从脱敏字节生成，并要求 Frames/NDJSON/日志零命中断言。现有 WireLog 尚未改造，本项只确认契约配方闭环。 |
| R2-006 | **FIXED** | C-15 `:35–43` 明确同连接只读 DB 查询，外部资源仅经注入 `IResourceVerifier` 对受管根做只读存在/可读验证；禁止写、网络、Host 调用及第二连接，保留 typed rollback。允许边界已消歧。验证集合仍有 R3-003。 |
| R2-007 | **PARTIAL** | C-16 `:92–97` 已补 accepted 取消、全部状态重放、accepted 前原子预占项目锁及终态释放。但冻结 receipt 形状 `:101` 仍遗漏 accepted；计数示例与固定形状、来源项/成员单位仍未完全对齐。见 R3-004。 |
| R2-008 | **FIXED** | r1/r2 归档均存在，字节数和 SHA-256 与指定值完全一致；本轮已按 r1 原文核验 R1-001…R1-013。原文核验发现的剩余问题如实列为 PARTIAL，没有将“归档恢复”当成所有 finding 自动关闭。 |
| R2-009 | **FIXED** | C-06 `:75` 已改为 referenced 页进入 `V_ref`，明确不创建 artifact/revision；载体 `:65` 登记这项修正。请求方向、双侧 Verify 和撤销范围仍有精确条目，无额外冻结契约漂移。 |

## 3. r1 findings 原文闭环表

| ID | 状态 | 按 r1 原文核验结果 |
|---|---|---|
| R1-001 | **FIXED** | C-05 已通过 UNFREEZE 承载 referenced 分支，包含父书/章节删除、页删除、时间、健康 binding；完整性、V、R 分离，managed 原行为保留。C-06 旧 revision 引用已修正。 |
| R1-002 | **FIXED** | C-06 `:37–54` 与 C-16 `:19`、`:49–66` 明确 Host 唯一授予、dispatch 前铸造、Host 授权根解析、Core 本地 Verify；四维 scope、locator/ordinal 和首次 EntryId 分配职责已登记。此为静态契约判断。 |
| R1-003 | **FIXED** | C-06 `:42`、`:69–70`，C-15 `:292`、`:301–304`，C-16 `:21`、`:150` 定义持久化撤销→Core 废止→提交边界停止→ACK，以及 EOF fail-closed。未用 TTL 替代即时撤销；运行时竞态尚待实现测试。 |
| R1-004 | **PARTIAL** | 同源 FK、排序键/ordinal 唯一、每页和每项目 current 唯一、cache 三列 FK 均实测成立。但 DDL 仍接受 page 实际所属 book 与 project_id 不符的 binding；正文声明所属关系，尚需明确应用提交守卫与负测责任。见 R3-006。 |
| R1-005 | **PARTIAL** | 同内容不同物理文件不合并、重复 occurrence 不折叠、歧义拒绝自动迁移已有规则。location 的旧条款冲突仍在；PDF 跨版本保续也未与上游一致。见 R3-001/R3-002。 |
| R1-006 | **FIXED** | C-15 `:265–269` 要求所有 managed 创建路径显式维护 mode/complete，半写保持 incomplete，禁止静默翻转；`:257–258` 区分 live 判重与包含软删的 max_source_order。真实旧代码 `library.py:299–337` 与该拆分一致。 |
| R1-007 | **PARTIAL** | 已冻结立即接受、后台工作、轮询、取消、项目预占和重放方向，符合真实 stdio/Export 先例；receipt accepted 形状及计数仍有 R3-004。 |
| R1-008 | **FIXED** | canonical plan、有效期、目标和策略绑定、确认时当前源重验、stale 重预览均已定义；加密 Plan 不消费密码，Import 使用新建一次性引用，消除跨阶段复用已消费文件的问题。 |
| R1-009 | **PARTIAL** | operation 指纹/冲突/重放、会话内 receipt、跨重启自然键、import_as_new 不绕过 entry 唯一性、已提交保留均已定义；receipt 状态和混合单位问题尚未全部闭合。见 R3-004。 |
| R1-010 | **PARTIAL** | 每版本事务、失败停留 v6、回调时点、同连接、禁止操作、资源接缝和 typed 失败已补齐，SQL 回滚实测通过。但验证断言仍混淆完整集合与可见集合，不能直接执行为可靠入口 Gate。见 R3-003。 |
| R1-011 | **FIXED** | C-15 `:278–294` 明确逐根 identity、DataRoot 派生锁、跨 session 文件排他、持锁重载、代次比较、原子替换、缺失/损坏/显式 reset 状态及原生 DPAPI LIMITED 边界。未将替身测试冒充原生通过。 |
| R1-012 | **PARTIAL** | decoder/scale 改变不再影响 PDF content identity，原问题的 rendition 漂移部分已修正；但新算法把容器版本内容带入每页匹配身份，产生 R3-002 的跨版本保续冲突。 |
| R1-013 | **FIXED** | wire 允许的是 opaque 引用元数据，禁止密码及可逆编码；缺失/过期统一 REQUIRED，口令/解密错误 INVALID；日志位置已补；receipt 引用 §4 正确；正文明确创建五张 Source 表加 cache、预留两表。版本标签遗漏另列 R3-005。 |

## 4. UNFREEZE 合规核验

### 4.1 Git diff 范围

从 r2 reviewed_head 到本轮 HEAD，实际仅有：

```text
M doc/plan/FEA-C05_PAGE_VISIBILITY_DRAFT.md
M doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md
M doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md
M doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md
M doc/reviews/CONTRACT-UNFREEZE-2026-11-03.md
A doc/reviews/FEA-09-PREREQ-1-r1.md
A doc/reviews/FEA-09-PREREQ-1-r2.md
```

没有生产代码、依赖、打包或其它冻结记录变化。

从 Task 基线比较，还包括 STATUS、PLAN、ledger、rolling checkpoint、scope-r1 和相关 Task 的建立/更新。不能把整个 Task 区间误写成只有上述七个文件。

### 4.2 原语义与历史保留

实际字符串比对：

```text
OLD_C05_SECTION3_PRESERVED true
OLD_C06_9_RULES_PRESERVED true
```

原 C-05 §3 的 V/S/VISIBLE_TYPES 段完整保留；新增模式分派明确原 V 只作为 managed 的 `V_artifact` 使用。

`git cat-file blob 920c09525:<path>` 原始字节 SHA-256：

```text
C05 b34db88768790a982c00d6b78a9649c24047e15d2ba86e3c0bf6a5a293ec8d25
C06 b798dd8a9b3839ac0c8e18e19dd3d515080075db53d83726e18cf76343beaef8
```

与 UNFREEZE 载体旧 pin 一致。两份原 FROZEN 记录未修改。

变更主要限于 referenced 可见性、授权通信落地、撤销与相应引用，未发现无关产品扩域。载体仍有章节定位和 v2 标签遗漏，见 R3-005。

### 4.3 pin 漂移真实输出

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

**恰好 C-05/C-06 两项待重冻，其余 13 项 OK。** 当前不能称为 15/15 PASS。

### 4.4 流程判断

载体已规定：

```text
独立复核 → approved 且 P0/P1=0 → 最后元数据编辑
→ 最终 pin → FROZEN 记录及历史 → freeze matrix
```

顺序正确。当前尚未满足 approved 条件，因此不能进入重冻。

Task 仍有两项冻结前治理缺口：

- 未将 `tools/governance/verify_pins.ps1` 纳入精确写域。
- Task 交付物仍称 matrix“既有行不改”，与载体更新 C-05/C-06 版本注记的要求不完全一致。

应由 DSH 在本 Task 内精确登记后处理，不由 reviewer 修改。

## 5. 独立复跑结果

### 5.1 环境与方法

实际调用：

```javascript
spawnSync("python", ["-B", "-c", program], {
  cwd: "G:/CODEX/New Manga",
  encoding: "utf8"
});
```

环境：

```text
Python 3.14.6
SQLite 3.50.4
```

程序直接导入真实代码：

```python
from infrastructure.sqlite.schema import default_migrations, Migration
from infrastructure.sqlite.migrator import MigrationRunner, read_schema_version
from infrastructure.sqlite.connection import SchemaTooNewError
```

从当前 C-15 第一个 SQL fenced block 提取原文：

```python
sql = re.search(
    r'\x60\x60\x60sql\n(.*?)\x60\x60\x60',
    contract_text,
    re.S,
).group(1)

v7 = Migration(7, "v7__source_storage", sql)
```

所有数据库：

```python
sqlite3.connect(":memory:")
PRAGMA foreign_keys=ON
```

最终主程序 UTF-8 SHA-256：

```text
57a454d8e0a461eaf0b461cb15d5ada382edee86837c4b6ceebd77dc46df385d
```

迁移前后可见性补充程序 SHA-256：

```text
b4284e36aec67b7784ba7372870d8f43b567f8a68093b2fb7e74c1211f593d0b
```

程序仅存在内存中，没有写入测试文件。

### 5.2 升级、回填与守恒

分别以真实迁移链构造 v1、v2、v3、v4、v5、v6，插入代表性行，再由真实迁移器升级到 v7。

| 检查 | 实际结果 |
|---|---|
| v1→v7 | 成功；v1 placeholder 补齐后仍 incomplete |
| v2/v3/v4/v5/v6→v7 | 全部成功 |
| 完整 managed 页 | full、deleted 回填 complete |
| 半写及 placeholder | half、placeholder 保持 incomplete |
| 旧 pages 全列 | 按原列数逐值比较，全部不变 |
| 人工区域文本与 Lock | regions 全行比较不变 |
| FK 完整性 | 全部 `PRAGMA foreign_key_check=[]` |
| 预留表 | source_sync_plans/source_operations 均未创建 |

本轮 fixture 覆盖页 ID、章节、排序、source_order、hash、managed ref、宽高、页 Lock、删除状态及人工区域文本/Lock；不代表全部真实用户数据组合。

### 5.3 关系约束、重授权与旧写者

最终运行输出摘要：

```text
VERSION_CROSS_SOURCE REJECTED FOREIGN KEY constraint failed
ENTRY_CROSS_SOURCE REJECTED FOREIGN KEY constraint failed
BINDING_CROSS_SOURCE REJECTED FOREIGN KEY constraint failed
CACHE_CROSS_SOURCE REJECTED FOREIGN KEY constraint failed

DUP_SORT_KEY REJECTED UNIQUE constraint failed
DUP_ORDINAL REJECTED UNIQUE constraint failed
DUP_CURRENT_PAGE REJECTED UNIQUE constraint failed
DUP_CURRENT_PROJECT_ENTRY REJECTED UNIQUE constraint failed

SUPERSEDED_HISTORY ACCEPTED
OTHER_BOOK_REFERENCE ACCEPTED
CACHE_VALID ACCEPTED
```

跨项目共享使用真实属于第二 book 的 chapter/page 验证，避免用错误归属行冒充合法共享。

version/location 首轮负测先被 source/version digest 唯一键拦截；随后改用不冲突的 digest 重新执行，最终得到上述 **FOREIGN KEY** 拒绝结果。

重授权：

```text
REAUTH_IN_PLACE [('l1', 's1', 'reg-new', 2)]
HISTORICAL_PLUS_CURRENT [('l1', 0), ('lnew', 1)]
```

即 Registry 改变、代次递增可原地更新；历史位置与一个 current 可共存。

按 C-15 `:201` 旧文字创建相同物理身份的新 location，即使设置非 current，仍得到：

```text
REAUTH_INSERT_OLD_TEXT_201 REJECTED UNIQUE constraint failed:
source_locations.source_id,
source_locations.content_digest,
source_locations.volume_serial,
source_locations.file_id
```

第二个 current：

```text
SECOND_CURRENT REJECTED UNIQUE constraint failed:
source_locations.source_id
```

每个升级后的库交给仅认识 v1–v6 的真实迁移器，均抛 `SchemaTooNewError`。这是应用启动迁移门禁，不代表 SQLite 引擎会阻止任意绕过应用的 SQL。

另一个明确边界：

```text
WRONG_PROJECT_PARENT_NOT_ENFORCED_BY_DDL ACCEPTED
```

DDL 没有验证 page→chapter→book 与 project_id 的一致性，见 R3-006。

### 5.4 可见性与 PDF 身份

按冻结模式分派等式执行反例：

```text
managed    artifact=True  complete=False → V=True
referenced artifact=True  complete=False → V=False
referenced artifact=False complete=True  → V=True
```

这验证 R2-001 所要求的判别结果；不把等式实验冒充产品读路径运行证据。

在真实 v6 内存库中，为导入元数据不完整的 `half` 页建立 valid current artifact revision，提交后升级：

```text
V6_VISIBLE [('half',)]
V7_VISIBLE [('half',)]
V7_COMPLETE [('deleted',), ('full',)]
C05_PRESERVED True
C15_ASSERTION False
```

因此 C-05 managed 可见性守恒成立，而 C-15 `:40` 要求的集合等式不成立。

PDF 身份观察：

```text
RENDITION_UPGRADE_ID_BINDING_PRESERVED
PDF_CONTAINER_CHANGE_ALL_PAGE_IDENTITIES_CHANGE True
```

前者通过更新 decoder/pixel/尺寸观察列，检查 entry content digest 和 binding verified_digest 不变。后者直接执行草案给出的摘要公式，证明容器摘要变化会改变同 ordinal 页的 page-identity；未运行 PDF 解码器。

### 5.5 v7 失败回滚

在 v7 SQL 尾部注入：

```sql
INSERT INTO no_such_table VALUES (1);
```

分别从空库及 v1–v6 起点运行真实完整迁移链，全部得到：

```text
ROLLBACK 0 ->6 NO_V7_TABLES_OR_COLUMNS METADATA_6
ROLLBACK 1 ->6 NO_V7_TABLES_OR_COLUMNS METADATA_6
ROLLBACK 2 ->6 NO_V7_TABLES_OR_COLUMNS METADATA_6
ROLLBACK 3 ->6 NO_V7_TABLES_OR_COLUMNS METADATA_6
ROLLBACK 4 ->6 NO_V7_TABLES_OR_COLUMNS METADATA_6
ROLLBACK 5 ->6 NO_V7_TABLES_OR_COLUMNS METADATA_6
ROLLBACK 6 ->6 NO_V7_TABLES_OR_COLUMNS METADATA_6
```

schema_migrations 与 application_metadata 均为 6；六张新增表及 pages 新列全部回滚。先前成功版本保留，与逐版本事务规范一致。

**没有运行尚不存在的 validation callback，也没有将 SQL 故障回滚当作资源验证 callback 已通过。**

### 5.6 C-16 可实施性与交叉一致性

| 面 | 结论 |
|---|---|
| 异步 Start/轮询/Cancel | 方向可实施。真实 stdio 在 `core_service.py:5660–5665` 同步 dispatch；Export `service.py:800–857` 已有后台线程、snapshot、cancel 先例。 |
| operation 指纹/重放/忙锁 | C-16 `:93–95` 已定义全部状态重放、指纹冲突、accepted 前预占及终态释放；运行时尚未实现。 |
| receipt | 条款与固定形状仍不一致，见 R3-004。 |
| 加密 Plan→Import | 有限预览→容器重验→确认后解密自洽；一次性引用生命周期已补齐。未验证原生密码路径。 |
| WireLog | 契约位置正确；现有 `WireLog.cs:82–102` 仍接收并保存原始 Frame，新实现必须在此之前脱敏。 |
| 能力按操作 | `source.read/1` 缺失或探测异常拒绝 source 操作，不沿用启动降级放行。 |
| 撤销 ACK/EOF | Host 持久化、Core 废止、提交边界和 ACK 顺序已有明确语义；竞态与超时需实现测试。 |
| 四维 scope/locator | C-06/C-16 方向与映射原则一致，禁止裸 paths 授权。 |
| C-05↔C-15 | V 定义一致；迁移断言仍冲突。 |
| C-14 SC-S09…S13 | FK/排序/绑定主要约束成立；PDF 跨版本保续不成立。 |
| C-14 SC-S14…S17、C-01b | cache key、可再生产物、预算、raw 源与 derived 隔离方向一致；未验证运行实现。 |
| C-07 | 保持冻结字节；FEA-09 不新增 IHostController，UI-1 若扩端口须另走 UNFREEZE。 |

### 5.7 治理检查真实输出

```text
Governance scope: 15 current documents; no historical directory scan.
Task: doc\tasks\FEA-09-PREREQ-1.md
WARN: 存在 11 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3125 bytes / 29 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：5162 bytes / 64 lines
Governance check: PASS (3 warnings)
```

EXIT 0。机械 PASS 不覆盖本报告发现的契约语义冲突。

## 6. 新 Findings 表

| ID | 级别 | 位置 | 问题及最小修订 |
|---|---|---|---|
| **R3-001** | **P1** | C-15 `:89–93`、`:201`、`:224` | **location 仍有两套冲突规范。** DDL 为 `(source_id,content_digest,volume_serial,file_id)` 唯一且每 source 一个 current；`:224` 要求重授权原地更新。`:201` 却继续声称唯一键含 registry_id，并允许新代次新建 location。后者已实测被拒。最小修订：删除旧规则，统一到 v3 的 DDL 和原地更新规则，明确跨 Registry 命中复用及历史/current 转换。 |
| **R3-002** | **P1** | C-15 `:210–214`、`:222`；C-14 `:42–45`、`:66–68` | **PDF page-identity 不能承担当前定义的跨版本匹配。** 每页摘要包含整个容器摘要，新增一页、修改元数据或改动其它页都会改变全部页摘要；`:222` 又只按该不可变身份确定候选。因此未变页无法按 C-14 保续，插页后更无法按内容匹配旧页。最小修订：保留 decoder/scale 隔离，同时明确“版本内验证摘要”与“跨版本成员匹配证据”各自职责，给出 PDF 重排/插页/仅元数据变化的保续算法和歧义确认规则。不得仅靠 container_digest+ordinal；如需改变 C-14 语义，先由 DSH 精确扩域及 UNFREEZE。 |
| **R3-003** | **P1** | C-15 `:38–43`，尤其 `:40` | **迁移断言仍混淆可见性与完整性。** 要求旧可见集合等于新 managed/complete 集合，与 C-05 明确保留“导入元数据不完整但 valid artifact 仍可见”冲突；complete 集合还包含软删页和无 artifact 页。合法 v6 反例得到 V=`half`、complete=`full/deleted`。最小修订：分别冻结旧 `_COMPLETE_PAGE_WHERE`→新完整集合守恒，以及同一 t/父级条件下旧 V_artifact→新 managed V 守恒；资源验证明确每种基线对应的可信资源引用，不能一律假定 visible 页有 managed_original_ref。 |
| **R3-004** | **P2** | C-16 `:92–108` | **状态/计数正文与冻结形状未同步。** `:92` 要求 receipt 含 accepted，但 `:101` 枚举仍不含。`:96` 的 unsupported 示例按成员计数、字段放 item 顶层，固定形状却放 counts；同时 failed/skipped 等仍称按来源项，来源项究竟为容器还是成员不够明确。最小修订：统一 enum 与固定 schema，定义每个 count 的实体单位，并给 accepted 取消、部分容器取消、部分提交后失败及 unsupported 的一致 JSON 示例。 |
| **R3-005** | **P2** | C-15/C-16 `:3`；C-16 `:6/:158/:170`；载体 `:24/:48`；Task 交付物/写域 | **冻结控制信息仍有残留。** 标题 v3、状态行仍 v2；C-16 和载体仍引用同批 C-15/C-16 v2。载体把新增失败行定位 §5，实际位于新增 §3.2。Task 未登记 pin 检查器写域，matrix 既有行不改与重冻注记要求冲突。最小修订：在冻结前独立文档提交中统一版本/章节和精确写域，保留历史原文，不在冻结提交中夹带条款修改。 |
| **R3-006** | **P2** | C-15 `:145–168`、`:198` | **book 归属不变量依赖应用层，但执行责任未明确。** DDL 只验证 page_id 与 project_id 分别存在，实测接受页属于 b1、binding 声称 b2 的行，可削弱“同实际项目 entry 1:1”。最小修订：明确在同一绑定提交事务内，经 page→chapter→book 校验 project_id，列出拒绝码和负测；或采用等价数据库约束。不得把当前 DDL 宣称为已覆盖项目归属。 |

## 7. 未覆盖／无法核验项

1. 尚未实现的 v7 validation callback、违规回调拦截、非 SQLite 异常映射及真实受管文件验证。
2. source-read 新协议运行时，包括撤销与 commit 竞态、ACK 超时、EOF 后后台停止。
3. Windows 原生 DPAPI、ACL、跨进程/跨 session 排他及磁盘原子替换。
4. ZipCrypto/PDFium 密码产品路径、秘密清零及实际日志秘密扫描。
5. 实际 PDF 插页/重排解析；本轮 PDF 反证依据冻结摘要公式，不冒充解码器测试。
6. 全量 build、Python/.NET 产品回归、UI 端到端及四 PNG 指纹重跑。
7. 任意损坏库、全部人工数据和 current/pinned Revision 组合；本轮是合法代表性 fixture。
8. 未重新审查或打开 FEA-08，其既有终态不变。

## 8. 冻结建议

**需返修；当前 C-05 v1.1、C-06 v1.1、C-15 v3、C-16 v3 不可同批冻结。**

最小修订集为 R3-001…R3-006。优先修正三项 P1，再同步 receipt、版本标签和应用层守卫责任。无需为此直接实施 Source 生产代码。

通过新的上下文独立复核后，冻结前最后动作：

1. **先提交条款返修并复核**，冻结提交只处理已获准的状态和冻结记录。
2. 统一最终版本；C-05/C-06 状态改 FROZEN v1.1，C-15/C-16 使用实际最终版本。
3. 最后元数据编辑完成后，计算工作树 SHA-256、`git hash-object` 和 Git blob SHA-256；记录与 reviewed bytes 的精确差异。
4. 更新 C-05/C-06 FROZEN 当前记录，原 v1.0 pin、旧复核和历史记录保留；建立 C-15/C-16 FROZEN 记录，含条件清单及 §1A/§1B。
5. 更新 freeze matrix：登记 C-05/C-06 重冻版本，追加 C-15/C-16，当前总数应与实际冻结对象一致。
6. **扩展 `verify_pins.ps1` 覆盖 C-15/C-16**。
7. 重跑检查器，归档真实命令、EXIT 和原始输出；预计冻结全集为 **17 项**，不能继续把旧 15 项 PASS 当作新契约已受校验。
8. 完成 Task AC、Handoff、证据 pin、ledger、STATUS/PLAN/checkpoint 同步，由 DSH 进行集成处置。

### `verify_pins.ps1` 扩展方案

由 DSH 先登记精确写域：

```text
tools/governance/verify_pins.ps1
```

在既有 map 增加：

```powershell
'C15'='FEA-C15_SOURCE_STORAGE_DRAFT.md'
'C16'='FEA-C16_SOURCE_READ_WIRE_DRAFT.md'
```

同时使本次冻结 Gate 对缺失 C-15/C-16 FROZEN 记录报失败。现有逻辑将 `MISSING-RECORD` 直接跳过，仅增加 map 可能出现“all 17”却未实际校验 17 个 pin，不能接受。

按协作协议 §4.4，在扩展前记录旧 15 项结果；扩展后验证：

- 四份最终冻结契约 pin 均匹配。
- 其它 13 项结果不变。
- 缺记录、缺契约、缺 pin、hash 不匹配均失败。
- 本轮冻结路径不得以 skip 计入成功数。

不得借此次扩展迁移其它历史 pin 口径。

## 9. 结论与推荐下一步

**PREREQ-1 当前不能冻结或 done；FEA-09 当前不能进入 scope-r2。** 完成返修、新独立复核、四份契约冻结及门禁、DSH 集成收口后，才可进入 scope-r2；这不自动授权实现。

推荐下一步：**DSH 在现有 FEA-09-PREREQ-1 内处置本报告，提交固定返修 head，再任命新独立上下文复核。**

可直接转发：

> DSH：请在 `G:\CODEX\New Manga`、`main`，以当前 `base/head=47133516263c868d0de2445d024d03e651fc56e7` 为恢复点，先核实工作树与 HEAD，再处置 FEA-09-PREREQ-1 r3 的 R3-001…R3-006。修改范围限本 Task 已授权契约、UNFREEZE 载体及必要治理文档；先消除 location 双规则、PDF 跨版本保续冲突、迁移完整性/可见性集合混用，再统一 receipt、版本标签和项目归属提交守卫规范。扩展 `tools/governance/verify_pins.ps1` 前先精确登记写域和验证范围；如需改变 C-14，先走精确 UNFREEZE，不直接改冻结字节。交付逐项 disposition、固定 commit、被审指纹和内存复跑结果，任命未参与返修的新独立上下文复核。禁止修改生产代码、依赖、用户数据或其它历史证据，禁止 push，不重开 FEA-08。复核通过前不重冻、不关闭 PREREQ-1、不释放 FEA-09 scope-r2。