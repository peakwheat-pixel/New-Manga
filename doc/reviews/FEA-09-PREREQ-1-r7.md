# FEA-09-PREREQ-1 契约独立复核 r7

## 0. 元信息

| 项目 | 实际值 |
|---|---|
| Reviewer | Codex，本次独立会话 `/root`；未参与契约起草、r1–r6 返修；不参与后续实现 |
| 模型 | GPT-6 系列；当前工具未提供更细型号的可核验标识 |
| 时间 | 2026-11-03，核验时间点 17:36:15 CST |
| 仓库 | `G:\CODEX\New Manga` |
| 分支 / Git common directory | `main` / `.git` |
| reviewed_head | `220979ba81f37e857f241049535caef7246c97b1` |
| Task base | `6e274dd94c5b64d8fbc3f9d578363d3c502a2b68` |
| r6 reviewed_head | `eb833a9ef51e8b2e94fac3a7baa964b5f0263348` |
| 审查前 status | `git status --porcelain=v1` 输出为空 |
| 审查后 status | 输出为空；HEAD、分支及五份被审文件指纹均未变化 |

**未修改声明**：未修改仓库、冻结记录或用户数据；未执行 add/commit/push；未创建报告文件或磁盘测试库。Python 使用 `-B`，SQLite 全部为 `:memory:`。报告仅在本次回复输出，由 DSH 原字节归档。

### 被审文件指纹

以下路径均相对仓库根目录。

| 文件 | `git hash-object` |
|---|---|
| `doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md` | `d80ead9e78253d9bc72c088c1e91a4231c40280f` |
| `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | `f90e342bb055cf5e2fe453067fcd7a5dd6c4411d` |
| `doc/plan/FEA-C05_PAGE_VISIBILITY_DRAFT.md` | `84658ad9f4dd44ffa9d8ae00e70dc086dfc95bc2` |
| `doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md` | `6a6e5744c7452adba08af33d1db1023a89c1491d` |
| `doc/reviews/CONTRACT-UNFREEZE-2026-11-03.md` | `c66dac9d6dbb01c5ee9066d69e0cc27e9948a670` |

| 文件 | 工作树原始字节 SHA-256 |
|---|---|
| C-15 | `fa912075f487701083eab662b7f89b9e8d8897024c9a832d9812ce5c87802090` |
| C-16 | `154c5a5725abf1b00709ac37b65e09718035229a544c761d0826b8b834617cc8` |
| C-05 | `13ff436af7bfbdc2a65181153a2b6140902e4aff1a8665a28e1c9c5b60167a39` |
| C-06 | `a779a7c1691b4414dcf99fd4452f837516f07accb44f9a9b263262c860fa9eb4` |
| UNFREEZE | `535696e8ddd07f3b37356d087653fd758df1f46dff69f4f2369bb9b920042dea` |

对五个文件另以 `git cat-file blob HEAD:<path>` 读取提交内容并计算 SHA-256，均与上表工作树 SHA-256 相同。

### 实际命令与执行方式

```text
git status --porcelain=v1
git branch --show-current
git rev-parse HEAD
git rev-parse --git-common-dir
git hash-object <被审路径>
git cat-file blob HEAD:<被审路径>
git diff --name-status <r6-head> HEAD
git diff --name-status <task-base> HEAD
git diff --check <task-base> HEAD
git diff <task-base> HEAD -- <C05/C06 路径>
pwsh.exe -NoProfile -File tools/governance/verify_pins.ps1
pwsh.exe -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-09-PREREQ-1.md
py.exe -B -c <内存迁移程序>
py.exe -B -c <约束与参考模型程序>
```

默认终端工具首次启动遭 Windows error 740；随后通过 Node `child_process` 直接调用 Git、PowerShell 和 Python 完成核验，没有提权。

## 1. Verdict

**approved**

**R6-001：FIXED。** 本轮未发现新的 P0/P1/P2 阻断。

批准下列四份契约在 DSH 完成最后元数据编辑、指纹登记与冻结门禁后**同批冻结**：

- C-05 v1.1；
- C-06 v1.1；
- C-15，最终被审草案 v5；
- C-16，最终被审草案 v7。

本结论批准契约内容冻结；当前仓库尚未完成冻结交付与 Task 集成收口，不能据此直接登记 `done` 或实现能力 PASS。

## 2. R6-001 闭环表

核验依据：r6 原文 R6-001、C-16 v7 §4、receipt 固定形状。

| r6 要求 | 本轮证据 | 结论 |
|---|---|---|
| planned 按页定义 | 明确 `planned_pages` 按页计数，等于 imported + unsupported + pending | FIXED |
| 排除已引用/策略跳过成员 | 新增 `skipped_pages`，明确按页排除出 planned | FIXED |
| 整 source 跳过 planned=0 | 示例⑤明确 planned=0、remaining=0、skipped_sources=1 | FIXED |
| 20 页中 8 页已引用、12 页提交 | 示例⑥明确 planned=12、imported_pages=12、skipped_pages=8、remaining=0 | FIXED |
| 四类既有示例自洽 | accepted 取消、部分取消、部分失败、unsupported-only 均给出 outcome/counts/remaining，并声明未列计数字段默认 0 | FIXED |
| item/totals 映射 | 两者使用同名六字段；totals 为各 item.counts 同名字段求和 | FIXED |
| 固定形状同步 | item.counts 与 totals 均已补 `skipped_pages` | FIXED |

按正文规则展开示例并复算：

| 场景 | planned | imported / committed | unsupported | pending | skipped_pages | skipped_sources | failed_sources | remaining |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| accepted 即取消 | 20 | 0 | 0 | 20 | 0 | 0 | 0 | 20 |
| 提交 12 页后取消 | 20 | 12 | 1 | 7 | 0 | 0 | 0 | 7 |
| 提交 12 页后失败 | 20 | 12 | 1 | 7 | 0 | 0 | 1 | 7 |
| unsupported-only | 20 | 0 | 20 | 0 | 0 | 0 | 0 | 0 |
| 整源已引用跳过 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| 8 页已引用、12 页提交 | 12 | 12 | 0 | 0 | 8 | 0 | 0 | 0 |

全部满足：

```text
planned = imported + unsupported + pending
remaining = planned - committed - unsupported = pending
```

计数默认值适用于 counts 字段；planned 由定义求得，committed 对应已提交页，remaining 使用固定公式。示例③的 `failed_sources=1` 对应同名 counts 字段；其 planned 按定义为 20。

原先“部分已引用后完成可能剩余 8 页”的歧义已消除。

## 3. r1–r5 不回退抽查

| 抽查项 | 结论与证据 |
|---|---|
| C-05 模式分派 | 保持 FIXED。managed 仅走原 `V_artifact`，referenced 仅走 `V_ref`；valid artifact 不能绕过 referenced 完整性分支。 |
| C-06 方向、四维 scope | 保持 FIXED。Host dispatch 前铸造并解析授权根；Core 本地 Verify；未引入 Core→Host RPC。 |
| 即时撤销/失联 | 保持 FIXED。持久化 generation、推送废止、提交边界停止、ACK 后返回成功；EOF/transport 失败废止全部 grant。 |
| 加密 Plan | 保持 FIXED。Plan 不消费密码、不解密，只绑定容器摘要及可读结构；Start 重验后解密。 |
| WireLog 脱敏 | 保持 FIXED。覆盖相关命令及响应、secret_ref 整对象、嵌套 path；原行与 hex 均须从脱敏字节生成。 |
| location 唯一 | 保持 FIXED。物理身份唯一、单 current、跨 Registry 原地重授权；内存负测及更新成功。 |
| PDF 匹配/重复 occurrence | 保持 FIXED。版本内 page-identity 与跨版本 pixel 匹配分工明确；要求可比 profile、一对一唯一匹配；重复组不按位置自动保续。 |
| 迁移双集合 | 保持 FIXED。complete 集合与 managed V 集合分别守恒；无 artifact/软删完整页与 artifact-only 半写页均未被错误改类。 |
| receipt | accepted、终态重放、请求冲突、accepted 前项目锁与终态释放保留；计数残余已由本轮闭环。 |
| project guard | 保持 FIXED。C-15 明确同事务应用守卫；C-16 有 typed 错误；FEA-09 AC-7 明确负测责任。 |
| 迁移 callback / managed 写入 | verifier 接缝、禁止操作、typed 回滚及完整性列维护要求均保留；未声称已实现。 |
| 报告归档 | r1–r6 完整 SHA-256 与指定历史指纹一致。 |

历史报告工作树 SHA-256：

```text
r1 d3ba756e7ccbb2c30653f833d6d3ebe0c4c19479f3f53627cc2b606632d54ae3
r2 d50f3a54020715e8ed2e226946a1034dae7e1b7a52a19b6e7c851f3d6a117e1a
r3 c029ad6abbb097db72a2ea31adaf24fd2d71a5c3657d6c4d21d4f8e4f1ca83fc
r4 4f5928a1693e325fd449efadd45f8cafa77790ad0f40329965aef0dff287fdfb
r5 c904a99b828d3762918f87ae0efb9f800b170d2a5ae7d860669f90e6c2e272f1
r6 9c2ff8107f4e329b01b063199ebfbaf856ee8e3cf178d5e6272c4c3e42e27174
```

## 4. UNFREEZE 合规核验

### 最小变更与原语义

相对 Task base 检查 C-05/C-06 完整 diff：

- C-05 原 §3 谓词正文连续保留；新增模式分派、referenced 分支、三谓词及相应说明。
- C-06 原九条安全约束逐条原文保留；方向、scope、Verify、撤销扩展均有载体登记。
- 未发现无关产品扩域。
- 旧冻结内容 SHA-256 与载体登记一致：

```text
C05 b34db88768790a982c00d6b78a9649c24047e15d2ba86e3c0bf6a5a293ec8d25
C06 b798dd8a9b3839ac0c8e18e19dd3d515080075db53d83726e18cf76343beaef8
```

UNFREEZE §4 当前引用为 C-15 v5 / C-16 v7；Task 最新变更记录同步 C-16 v7。历史变更行中的旧版本保留为历史记录。

### diff 范围

r6 reviewed_head→本轮 HEAD 仅四条路径：

```text
M doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md
M doc/reviews/CONTRACT-UNFREEZE-2026-11-03.md
A doc/reviews/FEA-09-PREREQ-1-r6.md
M doc/tasks/FEA-09-PREREQ-1.md
```

C-15、C-05、C-06、`verify_pins.ps1` 均未再修改。

Task base→HEAD 为 19 个文档路径，包含此前 FEA-09 范围处置、Task 建立及治理指针更新。核验结果：

```text
src/**、apps/**、tests/**：无差异
packaging/**、requirements*.txt：无差异
既有 FEA-CONTRACT-FROZEN-*：无差异
git diff --check <task-base> HEAD：无输出
```

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

EXIT **1**，stderr 为空。恰好 C-05/C-06 待重冻，其余 13 项匹配。此结果符合当前 UNFREEZE 状态，**不是最终冻结门禁 PASS**。

## 5. 抽验复跑结果

### 环境与方法

```text
Python 3.14.6
SQLite 3.50.4
cwd=G:\CODEX\New Manga
```

实际使用真实迁移器：

```python
from infrastructure.sqlite.schema import default_migrations, Migration
from infrastructure.sqlite.migrator import MigrationRunner, read_schema_version
from infrastructure.sqlite.connection import SchemaTooNewError
```

从 C-15 首个 SQL fenced block 提取原文，构造 `Migration(7, "v7__source_storage", sql)`；所有连接均为内存库并开启外键。

| 输入/程序 | UTF-8 SHA-256 |
|---|---|
| C-15 SQL | `abbf4e5f9415f392596faebc38690b6a58dd7f96941f51802621b68a2a3f8a91` |
| 六起点升级/回滚程序 | `aaefd35e93704cff6323bce9be10f10a163395498b70bc54c7dc2aa07422b988` |
| 最终约束/参考模型程序 | `8eaab53a361f477bd4321942d068a75a02482a10dcd10ad29a7c032c7e6ac0d3` |

### v1–v6→v7、回填与双集合

每个起点建立真实旧 Schema、插入 fixture，再补齐至 v6 并执行 v7。

```text
起点  complete 集合                  managed V 集合
v1    []                            [('half', 2)]
v2    [('deleted',), ('full',)]      [('half', 2)]
v3    [('deleted',), ('full',)]      [('half', 2)]
v4    [('deleted',), ('full',)]      [('half', 2)]
v5    [('deleted',), ('full',)]      [('half', 2)]
v6    [('deleted',), ('full',)]      [('half', 2)]
```

六个起点全部通过：

- pages 原有全部列逐值不变，仅追加两列；
- complete 集合和 managed V 集合、顺序分别守恒；
- 无 artifact/软删完整页保持 complete 且不可见；
- artifact-only 半写页保持 incomplete，按原 managed V 仍可见；
- 所测 page Lock、artifact/current/pinned 数据不变；
- `foreign_key_check` 为空；
- 两张预留表未创建；
- 仅认识 v1–v6 的真实迁移器均抛 `SchemaTooNewError`。

### 唯一/FK/location

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

首次 version 跨源负测被重复 content digest 唯一键提前拦截，未计作 FK 通过；隔离该冲突字段后重跑，得到上述 FK 拒绝。最终程序 EXIT **0**、stderr 为空。

重授权原地更新、旧 current→history→新 current 均成功。

### v7 回滚

在规范 SQL 尾部注入：

```sql
INSERT INTO missing_table VALUES(1);
```

六个起点均得到：

```text
ROLLBACK 1 ->6 NO_V7_SCHEMA PASS
ROLLBACK 2 ->6 NO_V7_SCHEMA PASS
ROLLBACK 3 ->6 NO_V7_SCHEMA PASS
ROLLBACK 4 ->6 NO_V7_SCHEMA PASS
ROLLBACK 5 ->6 NO_V7_SCHEMA PASS
ROLLBACK 6 ->6 NO_V7_SCHEMA PASS
```

确认 pages 原列/值不变、六张新表及新列无残留、版本停留 v6。升级/回滚程序 EXIT **0**、stderr 为空。

### page-identity、project guard、receipt

- 按规范公式复算：容器 digest 或 ordinal 改变会改变 page-identity；decoder/scale 不在公式输入中。
- 同事务项目归属参考查询检测错 book 后回滚，测试页无残留。
- 六类 receipt 算术模型全部通过，详见 §2。

以上 page-identity、project guard、receipt 为规范参考模型核验，**不是生产 handler 或真实 PDF 解码测试**。

### 治理检查

```text
Governance scope: 15 current documents; no historical directory scan.
Task: doc\tasks\FEA-09-PREREQ-1.md
WARN: 存在 11 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3125 bytes / 29 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：5162 bytes / 64 lines
Governance check: PASS (3 warnings)
```

EXIT **0**，stderr 为空。

### 未覆盖项

本轮未运行生产 IPC、原生 DPAPI、真实密码/PDF 解码、生产日志秘密扫描、撤销竞态、尚未实现的 migration validation callback、全量人工数据矩阵、build/.NET 全量测试或旧四 PNG 指纹核验。

未执行 17 项 checker 扩展与失败分支测试；这些是冻结收口动作，不登记为 PASS。

## 6. 新 Findings 表

| 级别 | 新增数量 |
|---|---:|
| P0 | 0 |
| P1 | 0 |
| P2 | 0 |

**无新增阻断。R6-001 已闭环，不再延续。**

## 7. 冻结批准与最后动作清单

**授予最终契约冻结批准：四份契约可同批冻结。** DSH 按以下顺序执行收口：

1. **原字节归档 r7**，登记 reviewed_head、五文件指纹与 R6-001 disposition。
2. **完成最后元数据编辑**：C-05/C-06 改为 `FROZEN v1.1`；C-15/C-16 明确正式冻结版本及其对应的草案 v5/v7；同步 UNFREEZE 完成状态。不得夹带语义返修。
3. **重算三种指纹**：工作树原始字节 SHA-256、`git hash-object`、固定提交 `git cat-file blob` 内容 SHA-256；记录 blob ID。§1A 写明口径，§1B 登记本次 reviewed bytes 与最终冻结字节的差异。
4. **更新 FROZEN-C05/C06**：当前 pin、版本、复核依据和条件；保留旧 v1.0 pin、历史 Review 与修正记录。
5. **建立 FROZEN-C15/C16**：版本、固定提交、三种指纹、条件逐项结果、边界、§1A/§1B。
6. **更新 freeze matrix 至 17 对象**：C-05/C-06 重冻注记，新增 C-15/C-16；其他契约与历史证据保持原字节。
7. **扩展 `verify_pins.ps1` 至固定 17 项**：

   ```text
   C01b C02 C03 C04b C05 C06 C07 C08 C09
   C10 C11 C12 C13 C14 C15 C16 FEA01
   ```

   缺记录不得再 skipped；缺记录、缺契约、缺 pin、错 pin 均须非零退出。确认 C-05/C-06 读取当前 pin，其他 13 项口径不变。负测使用隔离 fixture，不修改真实冻结文件。

8. **保存门禁原始日志**：扩展前基线、扩展后 17/17、所有失败分支、check、范围检查及旧四 PNG；记录实际命令、cwd、head、环境、stdout/stderr、EXIT。最终要求 check PASS、vpins **17/17**。
9. **完成生命周期交付**：Task Reviewer/Review/AC 与 v3 标记、Handoff、EV、delivery/integration head、Resource Manifest/closeout、ledger、STATUS、PLAN、rolling checkpoint。DSH 集成验证及 closeout 完成后才设 `done`。

本批准仅覆盖已审语义及上述冻结元数据处理；若再次修改契约语义，须固定新 head 并重新独立复核。

## 8. 结论与推荐下一步

**PREREQ-1 可以进入同批冻结收口。当前尚不能直接置 `done`；完成 §7 后，由 DSH 验证并关闭。**

**FEA-09 当前尚不能进入 scope-r2；PREREQ-1 冻结、17 项门禁及集成收口完成后，可以提交 scope-r2 文档复审。** scope-r2 不等于实现授权。不重开 FEA-08。

推荐下一步：**DSH 执行 FEA-09-PREREQ-1 冻结与集成收口。**

| 字段 | 指令 |
|---|---|
| Task / Agent | FEA-09-PREREQ-1；DSH |
| Recovery point | `G:\CODEX\New Manga`，`main`；base=`6e274dd94c5b64d8fbc3f9d578363d3c502a2b68`；reviewed_head=`220979ba81f37e857f241049535caef7246c97b1` |
| Scope | 当前 Task 授权的四契约冻结元数据、UNFREEZE、冻结记录、matrix、checker、交付证据及治理指针 |
| 禁止范围 | 生产代码、依赖、用户数据、其他冻结语义、历史证据改写及 push |
| Deliverables | r7 原字节归档、四契约冻结、17 项 pin 门禁与负测日志、Handoff/EV、Task 集成与 closeout |
| Verification | §7 全部动作；未执行项保持 NOT_RUN；完成后才置 done、提交 FEA-09 scope-r2 |

可直接转发：

> DSH：请在 `G:\CODEX\New Manga`、`main` 收口 FEA-09-PREREQ-1。Task base=`6e274dd94c5b64d8fbc3f9d578363d3c502a2b68`，r7 reviewed_head=`220979ba81f37e857f241049535caef7246c97b1`，Verdict=approved，R6-001 FIXED，无新 P0/P1/P2。先核实 HEAD/status 并原字节归档 r7；按报告 §7 完成 C-05/C-06 v1.1、C-15 草案 v5、C-16 草案 v7 同批冻结，登记最后元数据差异及三种指纹，更新/建立冻结记录与 17 对象 matrix，扩展 verify_pins 至 17 项且缺记录失败，保存正负门禁原始日志。完成 Task AC/v3、Handoff/EV、资源 closeout、ledger/STATUS/PLAN/checkpoint 及集成验证后才置 done。范围限当前授权文档、治理脚本和证据；禁止生产代码、依赖、用户数据、历史证据改写及 push，不重开 FEA-08。PREREQ-1 done 后再提交 FEA-09 scope-r2，由新的独立上下文复审。