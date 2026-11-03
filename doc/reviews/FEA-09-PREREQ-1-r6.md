# FEA-09-PREREQ-1 契约独立复核 r6

## 0. 元信息

| 项目 | 记录 |
|---|---|
| Reviewer | Codex，用户直接指派的独立审查会话 `/root` |
| 独立性 | 未参与契约起草或 r1–r5 返修；本会话不参与后续返修及实现 |
| 模型 | GPT-6 系列 Codex；无可验证的精确模型 ID |
| 结束核验时间 | 2026-11-03 17:30:33，Asia/Shanghai |
| 仓库 | `G:\CODEX\New Manga` |
| 分支 | `main` |
| Git common directory | `G:/CODEX/New Manga/.git` |
| reviewed_head | `eb833a9ef51e8b2e94fac3a7baa964b5f0263348` |
| r5 reviewed_head | `90b9600b13e531b3c00407d4af918737037b133a` |
| Task base | `6e274dd94c5b64d8fbc3f9d578363d3c502a2b68` |
| 审查前后 status | `git status --porcelain=v1` 均无输出 |
| 结束 HEAD | 与 reviewed_head 相同 |
| 辅助 Agent | 未使用 |

### 被审字节

以下工作树字节均与 `HEAD:<path>` blob 原始内容相等；结束复算均未变化。因此下列 SHA-256 也等于相应 blob 内容 SHA-256。

| 文件 | `git hash-object` | 工作树 SHA-256 |
|---|---|---|
| `doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md` | `d80ead9e78253d9bc72c088c1e91a4231c40280f` | `fa912075f487701083eab662b7f89b9e8d8897024c9a832d9812ce5c87802090` |
| `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | `13c53e376b4844d8b67a20521cce0df3a55769c8` | `07f4975a1f1437a05e6cb8c6eb47c72f50c49b12c443307e609debab608264f8` |
| `doc/plan/FEA-C05_PAGE_VISIBILITY_DRAFT.md` | `84658ad9f4dd44ffa9d8ae00e70dc086dfc95bc2` | `13ff436af7bfbdc2a65181153a2b6140902e4aff1a8665a28e1c9c5b60167a39` |
| `doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md` | `6a6e5744c7452adba08af33d1db1023a89c1491d` | `a779a7c1691b4414dcf99fd4452f837516f07accb44f9a9b263262c860fa9eb4` |
| `doc/reviews/CONTRACT-UNFREEZE-2026-11-03.md` | `a7e6d2504ddab7b83367e0c618b122c2ea8456ea` | `36dd386c57103b168527d94c0f27eb6db5e2bb242e60799b8db17ffc0077f08c` |

### 历史报告原字节核验

已读取历轮 findings 原文；下列字节数、完整指纹均与历史归档信息一致。

| 报告 | 字节数 | SHA-256 |
|---|---:|---|
| r1 | 25,469 | `d3ba756e7ccbb2c30653f833d6d3ebe0c4c19479f3f53627cc2b606632d54ae3` |
| r2 | 23,339 | `d50f3a54020715e8ed2e226946a1034dae7e1b7a52a19b6e7c851f3d6a117e1a` |
| r3 | 29,556 | `c029ad6abbb097db72a2ea31adaf24fd2d71a5c3657d6c4d21d4f8e4f1ca83fc` |
| r4 | 25,502 | `4f5928a1693e325fd449efadd45f8cafa77790ad0f40329965aef0dff287fdfb` |
| r5 | 27,237 | `c904a99b828d3762918f87ae0efb9f800b170d2a5ae7d860669f90e6c2e272f1` |

### 命令与执行方式

`exec_command` 的 PowerShell、cmd 两次尝试均在进程创建阶段遭 Windows error 740，命令未执行。随后通过 Node 文件读取及 `child_process` 执行只读 Git、PowerShell 门禁和内存 Python 程序，未提权。

实际执行包括：

```text
git status --porcelain=v1
git branch --show-current
git rev-parse HEAD
git rev-parse --git-common-dir
git hash-object <各被审文件>
git cat-file blob HEAD:<各被审文件>
git diff --name-status <r5-head> HEAD
git diff --name-status <task-base> HEAD
git diff --check <r5-head> HEAD
git diff <task-base> HEAD -- <指定生产/冻结记录/检查器范围>
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/verify_pins.ps1
py.exe -B -c <内存数据库程序>
py.exe -B -c <项目守卫与receipt参考程序>
```

Git 命令均成功；`diff --check` 无输出。Python 最终程序均 EXIT 0、stderr 为空。门禁结果见下文。

**未修改声明：未修改仓库、冻结字节、Git 配置或用户数据；未执行 add、commit、push；未创建磁盘脚本、数据库或证据文件。全部数据库使用 `:memory:`，Python 使用 `-B`。本报告仅输出，由 DSH 原字节归档。**

## 1. Verdict

**`changes_requested`**

本轮：**P0=0 / P1=0 / P2=1**，为 R5-001 尚未完全闭环的延续项。

accepted 取消计数、unsupported 算术和 C-15 版本引用已修正。但 r5 明确要求的两个跳过实例及四类示例统一字段/default 仍未补齐；部分成员已引用时，`planned_pages` 的排除规则仍只明确到整 source。

**当前不批准四份契约同批冻结。** 剩余修订限 C-16 计数条款，无需改动生产代码或重做 C-15 设计。

## 2. R5 findings 闭环表

| ID | 状态 | 原文要求与本轮核验 |
|---|---|---|
| **R5-001** | **PARTIAL** | accepted 即取消已改为 `pending_pages=planned_pages`，与未处理页数定义一致；新增 planned 基数及 unsupported 扣减公式，四类既有场景在已知基数下算术成立。但原文要求“补整源跳过、部分已引用后完成的计数实例”“四个既有示例应给出相同字段集或明确默认值”尚未完成。新增定义明确排除的是“已引用/策略跳过的 source”，没有直接明确部分成员已引用时排除这些页。见 R6-001。 |
| **R5-002** | **FIXED** | C-16 依据、§8 接口表、§10 冻结条件均引用 C-15 v5；全文无 `C-15 v4` 残留。C-16 标题、状态、变更记录为 v6；UNFREEZE §4.1 为 C-15 v5 / C-16 v6；Task 最新变更记录一致。首次正式冻结版本及 reviewed bytes 对应关系仍须在冻结元数据中登记，不得倒签为旧候选 approved。 |

四类既有示例的核验：

| 场景 | 算术 | 示例完整性 |
|---|---|---|
| accepted 即取消 | 已修正 | 缺统一的 item 字段/default 声明 |
| 20 页、1 unsupported、提交 12 页后取消 | `20−12−1=7` | 数值成立；未列全 counts 字段 |
| 同容器提交 12 页后失败 | 按前例基数可得 7 | 依赖“同容器”继承前例，未独立给全基数和字段 |
| unsupported-only | `N−0−N=0` | 数值成立；未列全 counts 字段 |

## 3. r1–r4 不回退抽查

`FIXED` 指契约问题闭环，不代表尚未实现的产品行为通过测试。

| 抽查项 | 结果与依据 |
|---|---|
| C-05 模式分派 | 保持 FIXED。managed 仅进入 `V_artifact`，referenced 仅进入 `V_ref`；不能借 artifact 绕过完整性/binding 条件。 |
| C-05 原 managed 语义 | 保持。去除新增 §3.1/§3.2 后，原 §3 连续文本完整保留；原谓词、稳定性、VISIBLE_TYPES、参考 SQL 未改。 |
| C-06 方向、四维 scope、双侧 Verify | 保持 FIXED。Host dispatch 前铸造、解析授权根；Core 读取及 commit 前本地验证；不依赖 Core→Host RPC。 |
| 即时撤销与失联 | 保持。持久化 generation→废止→提交边界停止→ACK；EOF/transport 失败废止全部 grant，未退回 TTL 模型。 |
| 加密 Plan | 保持 FIXED。Plan 不请求密码、不解密、不生成明文摘要；Start 重验容器/代次后才解密。 |
| WireLog 脱敏 | 保持 FIXED。覆盖 Register、Plan、Start 及响应、整对象 secret_ref、嵌套 path；原行及 hex 从脱敏字节生成。 |
| location 唯一 | 保持 FIXED。物理身份唯一、单 current、重授权原地更新；本轮约束负测及更新成功。 |
| PDF 身份与匹配 | 保持。page-identity 与 rendition 观察分离；跨版本要求可比 profile、一对一唯一匹配；重复组禁止位置锚定自动保续。 |
| 迁移双集合 | 保持 FIXED。complete 与 managed V 分别守恒；完整但不可见页不被强改 incomplete。内存复跑成立。 |
| 迁移回调边界 | 保持 FIXED。同连接只读查询、注入资源 verifier、禁止写/Host/网络/第二连接与 typed rollback 条款保留。 |
| 旧 managed 写入维护 | 未发现回退。显式维护完整性列；live 判重与含软删 max order 分开。 |
| receipt 状态/重放/忙锁 | accepted 枚举、accepted 取消、全部终态重放、accepted 前原子预占及终态释放均保留。计数剩余问题见 R6-001。 |
| project guard | 保持 FIXED。C-15 明确同事务应用守卫；C-16 错误码存在；FEA-09 AC-7 明确负测与回滚责任。 |
| 报告归档 | 保持 FIXED。r1–r5 原字节指纹全部一致。 |

本轮未运行生产 IPC、原生 DPAPI、真实密码解码、日志秘密扫描、PDFium 或撤销竞态测试。

## 4. UNFREEZE 合规核验

### 差异范围

r5 reviewed_head 至本轮 HEAD 仅有：

```text
M doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md
M doc/reviews/CONTRACT-UNFREEZE-2026-11-03.md
A doc/reviews/FEA-09-PREREQ-1-r5.md
M doc/tasks/FEA-09-PREREQ-1.md
```

C-15、C-05、C-06 均未再修改。

Task base 至 HEAD 共 **18 个文档路径**。指定范围核验确认：

- `src/**`、`apps/**`、`tests/**` 无差异。
- `packaging/**`、`requirements*.txt` 无差异。
- 既有 `FEA-CONTRACT-FROZEN-*` 无差异。
- `verify_pins.ps1` 无差异，仍为 15 项 map。
- `git diff --check <r5-head> HEAD` 无输出。

### 最小变更与原语义

C-05/C-06 相对原冻结版本的修改集中于 referenced 可见性、三谓词、授权方向、scope、Verify、撤销及对应接口说明，未发现无关产品扩域。

C-05 原 §3 与 C-06 原九条安全约束均核验连续文本保留。旧冻结字节 SHA-256 与载体一致：

```text
C05 b34db88768790a982c00d6b78a9649c24047e15d2ba86e3c0bf6a5a293ec8d25
C06 b798dd8a9b3839ac0c8e18e19dd3d515080075db53d83726e18cf76343beaef8
```

载体已登记复核、最后元数据编辑、重算 pin、更新冻结记录及 matrix 的流程。**载体流程合规，但本报告尚未批准执行重冻。**

### pin 实跑

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

EXIT **1**。恰好 C-05/C-06 待重冻，其余 13 项匹配；当前尚未覆盖 C-15/C-16。

## 5. 抽验复跑结果

### 方法与环境

```text
Python 3.14.6
SQLite 3.50.4
```

实际通过 `py.exe -B -c PROGRAM` 导入真实迁移代码：

```python
from infrastructure.sqlite.schema import default_migrations, Migration
from infrastructure.sqlite.migrator import MigrationRunner, read_schema_version
from infrastructure.sqlite.connection import SchemaTooNewError
```

从 C-15 首个 SQL fenced block 提取原文，构造：

```python
Migration(7, "v7__source_storage", sql)
```

全部连接为 `:memory:`，启用 `PRAGMA foreign_keys=ON`。

| 输入/程序 | UTF-8 SHA-256 |
|---|---|
| C-15 SQL | `abbf4e5f9415f392596faebc38690b6a58dd7f96941f51802621b68a2a3f8a91` |
| 最终迁移/约束程序 | `cb6e4e80c202be6ab59faef3ce618729a5bbc8873d39f28b345892986331d924` |
| 项目守卫/receipt 参考程序 | `2e70434db304ad988696513e69082416becfe9136499bb105d5f56522b35b968` |

首次约束程序的两个负测被其他唯一键提前拦截；随后隔离冲突字段重跑，以下结果来自最终程序。

### v1–v6→v7、回填与双集合

各起点先建立真实旧版本、插入 fixture，再补齐至 v6、捕获基线、执行 v7。

fixture 包括无 artifact 完整页、软删完整页、artifact-only 可见半写页、placeholder、page Lock、current/pinned revision。

```text
UPGRADE 1 ->7 complete=[] V=[('half', 2)] PASS
UPGRADE 2 ->7 complete=[('deleted',), ('full',)] V=[('half', 2)] PASS
UPGRADE 3 ->7 complete=[('deleted',), ('full',)] V=[('half', 2)] PASS
UPGRADE 4 ->7 complete=[('deleted',), ('full',)] V=[('half', 2)] PASS
UPGRADE 5 ->7 complete=[('deleted',), ('full',)] V=[('half', 2)] PASS
UPGRADE 6 ->7 complete=[('deleted',), ('full',)] V=[('half', 2)] PASS
```

六个起点均确认：

- pages 原有全部列逐值不变，仅追加两列。
- complete 集合与 managed V 集合、顺序分别守恒。
- 无 artifact/软删完整页保持 complete 且不可见。
- artifact-only 半写页保持 incomplete，仍按原 managed V 可见。
- artifact/current/pinned 数据不变。
- `foreign_key_check` 无结果。
- 两张预留表未创建。

本轮未重做 r5 的所有人工数据表及父级删除组合。

### 唯一/FK/location

最终隔离负测：

```text
DUP_PHYSICAL_HISTORY  REJECTED physical identity UNIQUE
SECOND_CURRENT       REJECTED source_id current UNIQUE
VERSION_CROSS_SOURCE REJECTED FOREIGN KEY
ENTRY_CROSS_SOURCE   REJECTED FOREIGN KEY
DUP_ORDINAL          REJECTED version_id,ordinal UNIQUE
DUP_SORT_KEY         REJECTED version_id,stable_sort_key UNIQUE
DUP_PROJECT_ENTRY    REJECTED project_id,entry_id UNIQUE
BINDING_CROSS_SOURCE REJECTED FOREIGN KEY
DUP_CURRENT_PAGE     REJECTED page_id current UNIQUE
REAUTH_AND_RELOCATION PASS
```

物理身份负测使用历史行 `is_current=0`，排除了 current 索引提前拦截。重授权原地更新及旧 current→history→新 current 均成功。

### 旧写者与 v7 回滚

六个升级库均被仅认识 v1–v6 的真实迁移器以 `SchemaTooNewError` 拒绝。

在 v7 SQL 尾部注入：

```sql
INSERT INTO missing_table VALUES(1);
```

结果：

```text
ROLLBACK 1 ->6 NO_V7_SCHEMA PASS
ROLLBACK 2 ->6 NO_V7_SCHEMA PASS
ROLLBACK 3 ->6 NO_V7_SCHEMA PASS
ROLLBACK 4 ->6 NO_V7_SCHEMA PASS
ROLLBACK 5 ->6 NO_V7_SCHEMA PASS
ROLLBACK 6 ->6 NO_V7_SCHEMA PASS
```

六张新表、pages 新列及 v7 版本记录均不残留；已成功提交的旧迁移保留。

这证明现有 runner 对所测 SQL 错误的逐版本回滚，**不证明尚未实现的 validation callback、违规操作拦截或真实资源验证已通过**。

### page-identity、project guard、receipt

按规范公式确认容器摘要变化使 page-identity 变化；decoder/scale 不在公式输入内。PDF 跨版本匹配仅静态核对本轮未改的 v5 条款，未运行真实 PDF 解码。

同事务项目归属参考查询结果：

```text
REFERENCE_PROJECT_GUARD SOURCE_PROJECT_MISMATCH ROLLBACK
```

该结果是参考守卫模型，不是生产 handler 验证。

receipt 参考算术：

| 场景 | planned | committed | unsupported | pending | remaining |
|---|---:|---:|---:|---:|---:|
| accepted 取消 | 20 | 0 | 0 | 20 | 20 |
| 部分取消 | 20 | 12 | 1 | 7 | 7 |
| 部分失败 | 20 | 12 | 1 | 7 | 7 |
| unsupported-only | 20 | 0 | 20 | 0 | 0 |
| 整源跳过的预期结果 | 0 | 0 | 0 | 0 | 0 |
| 8 页已引用、12 页提交的预期结果 | 12 | 12 | 0 | 0 | 0 |

后两行是用于说明应冻结结果的参考模型，**不是当前文档已经提供的实例**。

### 治理门禁

```text
Governance scope: 15 current documents; no historical directory scan.
Task: doc\tasks\FEA-09-PREREQ-1.md
WARN: 存在 11 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3125 bytes / 29 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：5162 bytes / 64 lines
Governance check: PASS (3 warnings)
```

EXIT **0**、stderr 为空。pin 门禁 EXIT 1，见 §4。

## 6. 新 Findings 表

无新增 P0/P1。以下为既有 R5-001 的剩余问题，单列追踪，不重复计算为两个 finding。

| ID | 级别 | 位置 | 问题、影响与最小修订 |
|---|---|---|---|
| **R6-001** | **P2** | C-16 `:87`、`:96`；R5-001 延续 | **部分成员跳过的计划基数及示例仍未完全冻结。** 新定义明确排除“已引用/策略跳过的 source”，而同段又允许“部分成员已引用、其余导入”。对于容器 20 页、8 页已引用、12 页提交，正文没有直接规定将这 8 页从 planned_pages 排除；Plan 形状也没有冻结部分成员时 `will_import` 的页数表达。实现仍可能分别得到 planned=12/remaining=0 或 planned=20/remaining=8。另 r5 明确要求的整源跳过、部分已引用后完成实例未补；四类既有示例没有统一字段集或默认值。最小修订：明确按页排除已引用/策略跳过成员，整源跳过 planned=0；补上述两个实例；给四类示例完整 counts/remaining/outcome，或明确省略字段默认值。无需增加生产范围。 |

## 7. 冻结批准与最后动作清单

**本轮不授予最终冻结批准。** 修复 R6-001 并取得新独立复核 approved 后，按以下顺序完成：

1. 将条款返修独立提交并固定 head；保留本报告原字节及逐项 disposition。
2. 最后编辑状态行：C-05/C-06 为 `FROZEN v1.1`；C-15/C-16 明确首次正式冻结版本与最终草案轮次对应关系，避免草案版本与冻结版本混用。
3. 最后编辑完成后计算三种指纹：工作树原始字节 SHA-256、`git hash-object`、固定提交 `git cat-file blob <commit>:<path>` 内容 SHA-256；记录 blob ID。§1A 明确口径，§1B 明确 reviewed bytes 与最终冻结字节差异。
4. 更新 FROZEN-C05/C06 当前 pin、复核依据及条件，保留 v1.0 pin、旧 Review、pin 修正历史。
5. 建立 FROZEN-C15/C16，记录版本、固定提交、三种指纹、逐项条件、边界及 §1A/§1B。
6. 更新 freeze matrix 的 C-05/C-06 重冻注记，追加 C-15/C-16；其余契约和历史证据保持原字节。
7. 扩展 `verify_pins.ps1` 至固定 17 对象，并验收失败分支。
8. 保存 check/vpins 原始 stdout/stderr、EXIT、cwd、head、环境和实际命令；最终要求 check PASS、vpins **17/17**。补 Task 要求的旧四 PNG 与范围检查。
9. 完成 Task AC/v3 标记、Handoff、EV、delivery/integration head、资源清单和 closeout、ledger、STATUS、PLAN、rolling checkpoint；DSH 集成验证后才置 done。

### 17 项 pin 扩展验收

固定全集：

```text
C01b C02 C03 C04b C05 C06 C07 C08 C09
C10 C11 C12 C13 C14 C15 C16 FEA01
```

新增 map：

```powershell
'C15'='FEA-C15_SOURCE_STORAGE_DRAFT.md'
'C16'='FEA-C16_SOURCE_READ_WIRE_DRAFT.md'
```

必须验证：

- 17 个当前冻结记录、契约及 pin 全部存在并匹配，实际检查数量为 17。
- 缺记录、缺契约、缺 pin、错 pin 均非零退出。
- 当前 `MISSING-RECORD ... skipped` 分支改为 Gate 失败。
- C-05/C-06 读取当前 pin，不误读保留的历史 pin。
- 其他 13 项 pin 口径不变。
- 负测使用隔离 fixture，不修改真实冻结文件。
- 保存扩展前 15 项基线、扩展后 17 项及所有失败分支原始日志。

以上扩展及负测本轮均 **NOT_RUN**，不得提前登记 PASS。

## 8. 结论与推荐下一步

**PREREQ-1 当前不能冻结并 done；FEA-09 当前不能据此前置进入 scope-r2。**

完成 R6-001、取得独立复核 approved、四份契约同批冻结、17 项门禁及 PREREQ-1 集成收口后，FEA-09 才可进入 scope-r2 文档复审；不自动获得实现授权。不重开 FEA-08。

推荐下一步：**DSH 在现有 FEA-09-PREREQ-1 内完成 C-16 最小返修，再任命新独立上下文复核。**

| 字段 | 指令 |
|---|---|
| Task | FEA-09-PREREQ-1，R6-001 闭环 |
| Agent | DSH 返修与处置；新独立上下文 Reviewer 复核 |
| Recovery point | `G:\CODEX\New Manga`，`main`；base=`6e274dd94c5b64d8fbc3f9d578363d3c502a2b68`；当前 head=`eb833a9ef51e8b2e94fac3a7baa964b5f0263348` |
| Scope | 当前 Task 授权的 C-16、必要载体/Task 文档；冻结待 approved |
| 禁止范围 | 生产代码、依赖、用户数据、其他冻结契约和历史证据；禁止 push |
| Deliverables | r6 原字节归档、disposition、修订固定 commit/指纹、新 Review；通过后冻结记录/Handoff/EV |
| Verification | 部分成员跳过、整源跳过及四类完整示例；内存迁移/约束/回滚；check/vpins；未验证项如实标记 |

可直接转发：

> DSH：请在 `G:\CODEX\New Manga`、`main` 处理 FEA-09-PREREQ-1 的 R6-001。Task base=`6e274dd94c5b64d8fbc3f9d578363d3c502a2b68`，reviewed_head=`eb833a9ef51e8b2e94fac3a7baa964b5f0263348`。先核实 HEAD/status，原字节归档 r6。范围限当前 Task 授权文档：明确 C-16 planned_pages 按页排除已引用/策略跳过成员，补整源跳过及“20 页中 8 页已引用、12 页提交后完成”实例，统一四类既有示例字段或默认值。提交 disposition、固定 commit 和指纹，由新独立上下文复核；禁止生产代码、依赖、用户数据、历史证据修改及 push，不重开 FEA-08。approved 后执行四份契约冻结、17 项 pin 扩展与失败分支验收、原始日志归档及 Task/Handoff/EV/ledger/STATUS/PLAN/checkpoint 收口；PREREQ-1 done 后再提交 FEA-09 scope-r2。