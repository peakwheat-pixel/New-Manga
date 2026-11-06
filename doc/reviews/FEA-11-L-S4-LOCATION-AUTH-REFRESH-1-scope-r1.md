---
task: FEA-11-L-S4-LOCATION-AUTH-REFRESH-1
title: FEA-11-L-S4-LOCATION-AUTH-REFRESH-1 scope review r1（`refresh_source_location_auth` 死代码与撤销/重注册后的 location auth 刷新；权威 scope 评审）
reviewer: fresh subagent（独立上下文；未参与本卡/SCAN-2/L-S1 实现或返修；只读被审字节）
session: 委托子会话（isolation：不共享父会话上下文；会话 id 未在本会话暴露，身份来源见 §9）
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: 独立 scope review（fresh context / read-only / 非作者 / 非实现审查者）
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 821b309a0f6145ba085af2581541ee946cd5f949
reviewed_head_note: 任务书给的是 `d782c52a4`（main，声称 clean）。实测：评审开始时 HEAD=`d782c52a4`，工作树**并非 clean**（`?? doc/tasks/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1.md`，即被审占位卡本身未跟踪）；评审期间另一会话提交 `821b309a0`（docs-only：L-S1 scope review、L-S1 PREQ-1 卡、**本卡 L-S4 占位卡入库**、TASK_LEDGER 重算），`git diff --name-status d782c52a4..821b309a0` 只有 4 个 doc 文件、`src/**`/`tests/**`/`doc/plan/FEA-C1*` 零变化。故 reviewed_head 取 `821b309a0`；**代码与契约事实在 `d782c52a4` 与 `821b309a0` 上逐字节相同**。
verdict: READY-TO-FREEZE
verdict_scope: 按「拆卡」口径——**L-S4-A（零契约：C-15 §2/§3.3 原地刷新落到两个既有写路径 + 死代码合并 + 判别测试）= READY-TO-FREEZE**；**L-S4-B（零交互自动恢复只读枚举切片）= 需 C-16 v1.5 UNFREEZE（1/18 pins，新 host-control 命令）+ 另卡**。**按现卡面原文（含「只读切片无法恢复→修复后可恢复」的整体承诺）不可冻结**：目标超出「刷新事实」能兑现的范围（见 §2.1、§4.1、§6.2 D-1）。
---

# FEA-11-L-S4-LOCATION-AUTH-REFRESH-1：权威 scope review r1

> **结论先行。**
>
> 1. **死代码事实成立且为「零调用」**：`refresh_source_location_auth` 定义于 `src/infrastructure/sqlite/library.py:2293-2310`，在 `src/**` 与 `tests/**` 中**仅此 1 处命中**（无任何调用者，也无测试直接/间接调用）；`service.py:504-515` 存在**一份同义内联 UPDATE**，且只在 `kind == "relink"` 分支执行。**「撤销/重注册后 location auth 不更新」可复现**，根因是**没有任何写路径在「同一物理身份重新注册」时刷新该行**，不是函数写错。
> 2. **正确语义已被冻结契约写死，本卡不需要改契约**：C-15 §2 约束语义（`doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md:204`）与 §3.3 源复用规则（同文件 `:233`）逐字要求「重授权/重新注册**原地更新**该行的 `registry_id/authorization_generation/last_verified_at`，不新建重复 location；**跨 Registry 命中同一物理身份时同样复用并原地更新注册信息**」。本卡是**实现既有冻结条款**（conformance），不是新增语义 → **L-S4-A 零契约**（§3）。
> 3. **真正的缺口是「缺触发器」，而不是「缺函数」**：生产 Host 的 `Register` 每次生成**新的 `registry_id` + `generation=1`**、`Revoke` 置 `RevokedAt` 且 `Authorize` 永久拒绝已撤销条目（`SourceAccessRegistry.cs:34-52 / 56-74 / 76-86`）→ 用户「撤销→重注册」后 Core 的 location 永远停在旧 `(registry_id, generation)`；冷启动/周期枚举把它作为 target 返回，Host 端 `TryMap`（`SourceScanScheduler.cs:2162-2169`）与 `VerifyEnumeratedTarget`（同文件 `:1561-1610`）会 typed skip（`SOURCE_GRANT_REVOKED` / `SOURCE_REGISTRY_UNAVAILABLE` / `SOURCE_REGISTRY_BUSY`）且**不做路径回退**（`:1514-1519` 的 `ResolveRegistryEntry` 只在非枚举 target 上生效）。因此仅「把死函数接上」**不会**让只读切片自动恢复；恢复必须经过一次**既有写路径**（重导入/同步 apply）。**「零交互自动恢复」需要新 host-control 命令 → C-16 新版本 UNFREEZE（1 pin）。**
> 4. **裁决：`READY-TO-FREEZE`（A 面）**。建议 DSH 把本卡收窄为 **L-S4-A**（零契约、写域小、可判别），把「枚举切片零交互自动恢复」**移出**并登记 limitation `L-S4-1`；如要零交互恢复，另开 `FEA-11-L-S4-B`（载体：C-16 v1.5，1/18 pins）。**卡面现文「用户撤销后重授权仍被旧 auth 阻断」→「只读切片无法恢复」的因果链只有 A 面修完仍不闭环，不得据此宣称可恢复。**

---

## 0. 只读基线与实测命令（未跑项一律标 NOT_RUN）

| 项 | T0（评审开始 07:16） | T1（评审结束 07:36） | 来源 |
|---|---|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` | 同 | 实测 |
| HEAD | `d782c52a403d96c45f7097ffc0cb4bca37024aa1` | `821b309a0f6145ba085af2581541ee946cd5f949` | `git rev-parse HEAD` |
| 工作树 | **1 个未跟踪**：`?? doc/tasks/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1.md`（被审占位卡本身） | **外部改动（并发会话）**：tracked `M doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md`、`M doc/plan/FEA-CONTRACT-FROZEN-C15.md`、`M doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`、`M doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1.md`；未跟踪 `?? doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C15.md`、`?? verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1/`。**本评审唯一新增**：`?? doc/reviews/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1-scope-r1.md`（本报告） | `git status --porcelain=v1`（T0 07:16 / T1 07:36） |
| 并发会话 | — | **另一会话正在做 `FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1`（C-15 v1.5 UNFREEZE）**：C-15 草案 mtime `07:28:15`，载体/PREQ 卡已落盘 | 文件 mtime、`git log`、`doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1.md` 存在 |
| `verify_pins.ps1` | **PASS (all 18)**（C15 `d8c0a3bcfc21`、C16 `ad25fb3c89bb`、C17 `aefa0fa5b17e`） | **FAIL (1)**：`C15 pin=d8c0a3bcfc21 actual=f9e376a0ed4c`（**由并发会话未提交的 C-15 v1.5 编辑导致，非本评审产物**） | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` |
| `check.ps1`（默认） | **FAIL (2 errors, 3 warnings)**：TASK_LEDGER 陈旧（声明 527 Task/9 非终态，实际 528/10——由**本卡占位文件尚未入库**造成） | **FAIL (2 errors, 3 warnings)**：声明 528 Task/10 非终态，实际 529/11（并发会话继续加卡；07:36 实测 `doc/tasks/*.md` 已 530 个） | `pwsh -NoProfile -File tools/governance/check.ps1` |
| 定向 pytest `tests/fea11 tests/core` | — | **1158 passed, 10 warnings, 76.72 s, EXIT 0** | 实测（日志 `%TEMP%\ls4-core-fea11.log`） |
| 全量 `pytest tests -q -p no:warnings --tb=no` | — | **3305 passed, 10 skipped, 243.86 s, EXIT 0**（跑后 `git status` 无**由测试产生**的 tracked 变化；`verification/` 下仅出现并发会话新建的 `FEA-11-L-S1-...-PREREQ-1/`，非测试产物） | 实测（`%TEMP%\ls4-full-pytest.log`） |
| 全量 `dotnet test apps/desktop-avalonia/NewManga.sln` | **NOT_RUN**（本卡推荐 **Host 零改动**，见 §4.3） | NOT_RUN | — |
| `NEWMANGA_FEA11_IPC=1` 真实 IPC | **NOT_RUN**（未改动 Host/Core 行为，无新证据需求） | NOT_RUN | — |
| `generate_api_inventory.py --check` | **NOT_RUN**（只读评审 + 并发会话正改 `doc/plan/**`，此刻跑无判别力） | NOT_RUN | — |
| 冻结字节只读核对 | C-15 `:204/:233/:323`、C-16 `:37-72/:89`、C-17 `:169/:186/:228/:239-262/:279/:289/:294` 逐条读取 | 同 | `read`（HEAD 字节） |

**并发写入声明（必须）**：评审期间共享 `main` 工作树被**另一会话**持续写入（C-15 v1.5 UNFREEZE 预热：草案 + 冻结记录 + 矩阵 + 载体 + 证据目录 + 新 PREQ 卡）。本评审**未修改、未删除、未暂存、未提交**这些文件中的任何字节；上述 `M`/`??` 全部非本报告产物。因此**T1 的 pins/check 红灯不可归因于本卡**；L-S4 冻结/实施前必须由 Lead 在**clean 且已提交**的树上重跑门禁（见 §6.2 D-6）。

---

## 1. Q1 事实核实

### 1.1 死代码（定义位置 / 调用计数 / 内联重复）

| 事实 | 证据（path:line） |
|---|---|
| 定义（唯一实现） | `src/infrastructure/sqlite/library.py:2293-2310`（`def refresh_source_location_auth(self, source_id, content_digest, volume_serial, file_id, registry_id, authorization_generation, last_verified_at) -> int`；UPDATE 三列 + 按物理身份四键定位，返回 `rowcount`） |
| 调用者 | **零**：`Select-String -Path (src/**, tests/**) -Pattern 'refresh_source_location_auth'` → **仅 1 命中**（就是 `:2293` 的定义行）。无任何测试引用。 |
| 同类内联实现（重复代码） | `src/application/sources/service.py:504-515`：`if kind == "relink" and grant is not None:` → `UPDATE source_locations SET registry_id=?, authorization_generation=?, last_verified_at=? WHERE location_id=?`（**只按 `location_id`、只在 relink**；与死函数语义等价但键不同） |
| 该内联块的执行上下文 | `_execute_decisions`（`service.py:429`）在 `BEGIN IMMEDIATE` 事务内被调用（`service.py:239`、`:262-264`），提交前还会重验授权（`:276-279`） |
| 存储类归属（决定「接哪里」） | `SqliteLibraryRepository`（`library.py:62`）与 `SourceSyncStore`（`source_sync.py:42`）**共用同一个 `conn`**（`src/bootstrap/core_assembly.py:1216`、`:1236`）→ 死函数挂在 import 侧仓库上，sync apply 侧根本**看不见**它（这解释了内联重复，也决定了 §2.4 的实现位置问题） |

**Q1-1 判定：死代码成立（零调用 + 一份内联重复）。** 但它「死」的**后果**有限——relink 路径已经在做同义刷新；真正没人做的是**「同一物理身份重新注册」**这条路径（1.2/1.3）。

### 1.2 「撤销 / 重注册 / 重授权」的确切语义（Host 侧事实）

| 动作 | 实现 | 结果 |
|---|---|---|
| 注册（首次/重新注册） | `SourceAccessRegistry.cs:34-52` | `Register(locator, roots)` **无条件追加新条目**：`new SourceAuthorization(Guid.NewGuid().ToString("N"), locator, 1, ...)` → **新 `registry_id`、`generation=1`** |
| 撤销 | 同文件 `:76-86` | 同条目 `Generation+1` 且 `RevokedAt=now`（**id 不变**） |
| 撤销后授权 | 同文件 `:56-74`（`:61`） | `RevokedAt is not null` → `SOURCE_GRANT_REVOKED`，**永不复活**；`Generation != expectedGeneration` → `SOURCE_REGISTRY_BUSY` |
| 重置 | 同文件 `:88-96` | 整库移入 `quarantine/`，新建空库（所有旧 `registry_id` 消失） |

**推论（关键）**：用户「撤销 → 重新授权」在产品内**只能**得到**全新的 `registry_id`（generation 回到 1）**（或 reset 后全新库）。因此 Core 侧若不做原地刷新，`source_locations.registry_id/authorization_generation` **必然**永久陈旧——这与「函数写没写对」无关，是**没人调用**。

### 1.3 可复现的代码路径（撤销/重注册后 auth 不更新）

1. **写入口只有一处会插 location**：import 的页单元 `commit_referenced_page_unit`（`library.py:2514-2559`，`:2534-2559` 为 `INSERT INTO source_locations`）**只在 `source is not None` 时插入**；而 `insert_source` 的取值是 `first_page and existing_source_id is None`（`runtime.py:556-557`）。
2. **「同一物理身份已存在」时什么都不写**：`_existing_metadata`（`runtime.py:592-607`）按 `(content_digest, volume_serial, file_id)` 命中既有 source/version → `source_id` 复用 → `insert_source=False` → `_commit_page_unit` 里 `source=None`、`location=None`（`runtime.py:794-815`）→ **location 的 `registry_id/authorization_generation` 保持旧值**。
3. **「整源已引用」时更早返回**：`runtime.py:396-410` 在 `already_referenced and will_import == 0 and duplicate_policy == "skip"` 时直接 `outcome="skipped"` 返回，**零写**（连页单元都不执行）→ 重导入不会刷新。
4. **sync apply 只在 relink 刷新**：`service.py:504-515`；`resync`/`repoint` 若物理身份未变（`same_container`）不会新建 location，也**不会**走这段 → 同样不刷新。
5. **枚举直接读该行**：`source_sync.py:82-94`（`l.registry_id`、`l.authorization_generation AS generation`）→ `scanner.py:96-193`（`list_scan_targets`，`:111-116` 只做 typed skip，不修值）。
6. **Host 侧判死**：`SourceScanScheduler.cs:2162-2169`（跨目标映射时 `entries.TryGetValue(registryId) && Generation == generation` 不满足 → **target 直接被丢弃**）；`:1561-1610`（已登记 target 的执行期复核：`:1580-1583` 未知 registry → `SOURCE_REGISTRY_UNAVAILABLE`；`:1585-1588` 已撤销 → `SOURCE_GRANT_REVOKED`；`:1590-1597` 代次漂移 → `SOURCE_REGISTRY_BUSY`），且**枚举 target 不走路径回退**（`:1505-1512` 先判 `IsEnumerated` 并短路，`:1514-1519` 的 `ResolveRegistryEntry` 只对非枚举 target 生效）。
7. **无自愈路径**：scan 零写（`scanner.py:1-8` 模块 docstring 明示「Scans never write to the database」；C-17 v1.1 `:228` 只读枚举）；plan/apply 需先 scan → **循环**。故 SCAN-2 的「只读切片无法恢复」**可复现且是结构性的**。

### 1.4 影响面（哪条链路、影响多大）

| 链路 | 是否受影响 | 事实依据 |
|---|---|---|
| **冷启动 / 周期只读枚举 → Host 扫描切片（SCAN-2）** | **是（主症状）** | 1.3 步骤 5–7；Host 侧 `TryMap` 直接丢 target 或 `VerifyEnumeratedTarget` typed skip；`SourceScanSchedulerTests.cs:1134-1220` 把 skip 语义**固化为预期** |
| **缺失观察（missing observation）** | **是（错向 fail-closed）** | `scanner.py:589-609` 用 location 的 `registry_id/generation` 与 Host 观察逐项比对 → 刷新前用户的合法 missing 观察会被判 `SOURCE_PLAN_STALE`；刷新后对齐 |
| **导入** | **是（不刷新；但不破坏页/binding 正确性）** | 1.3 步骤 1–3；`tests/fea09/test_referenced_flow.py:371-393` 只断言 skip 计数，未断言 auth |
| **Run / 页面读取（resolve/读取授权）** | **否** | 读取按 live grant + facts 校验（C-16 §2 `:67-72`）；binding 的 `authorization_generation` 允许 ≤ 当前 Host generation（C-15 `:233`、`:323`；C-17 `:294`） |
| **同步 apply（relink）** | **否（已刷新）** | `service.py:504-515`；但测试只用同值（`tests/fea11/test_source_relink.py:110-112` 断言 `location_id=="sl-s1"`、`generation==1`），**无判别力** |

**严重度定性**：不阻断读取/Run，但**静默丢失监控**（该源永久不再被扫描/枚举），且用户「重新授权」这一显式动作在产品内**没有可见的正向效果**——属**P2 正确性 + 契约一致性缺陷**，与既有评审的定级一致（`doc/reviews/FEA-11-RUN-GRANT-2-scope-r1.md:291` 记 P2「可穿插（小）」；`doc/reviews/FEA-11-SCAN-2-scope-r1.md:378` 记 S-4 为 P2）。

### 1.5 现有测试覆盖（关键空白）

| 场景 | 现有覆盖 | 判别力 |
|---|---|---|
| Host：撤销/代次漂移 → typed skip，不自动重授权 | `SourceScanSchedulerTests.cs:1134-1154`（revoked → `SOURCE_GRANT_REVOKED`）、`:1156-1175`（drift → `SOURCE_REGISTRY_BUSY`）、`:1177-1220`（缺失/被替换根 → `SOURCE_REGISTRY_UNAVAILABLE`）、`:1120`（`TryMap` 未知 registry → false） | **有**（但方向相反：固化「不恢复」） |
| Core：枚举值跟随 `source_locations` 行 | `tests/core/test_core_scan_target_commands.py:321-352`（先 gen=1；直改 DB 为 gen=5/新 digest 后枚举随之变化） | **有**（证明「只要有人写，枚举就跟着变」） |
| 真实 IPC：registry 身份与 Core 行对齐 | `Fea11ScanIpcTests.cs:49-60`：**测试自己用 SQL 直改 location 行**（注释明写「fixture-only alignment; no product code writes this DB」） | **反向证据**：生产无写者，测试靠 fixture 绕过 |
| **「撤销→重注册→刷新→枚举恢复」** | **无**（`grep refresh_source_location_auth tests` → 0；`grep 'revoke' tests/fea11` 命中均与 registry 重注册无关） | **空白** |
| 「撤销后不得自动放行」 | Host 侧有（上表第 1 行）；**Core 侧无**（无「刷新必须凭 live grant」的负测） | **半空白** |

**Q1 结论**：死代码 = 事实；auth 不更新 = 可复现；**验证空白的正是「重注册/重新授权」这条主干**，而现有测试全用静态 `registry_id="reg-1" generation=1`（`tests/fea11/conftest.py:170`、`:291-309`），**无法判别**任何刷新行为。

---

## 2. Q2 正确语义

### 2.1 该函数应在何时被调用

| 事件 | 应刷新？ | 依据 / 理由 |
|---|---|---|
| 用户撤销（Host `Revoke` / Core `RevokeSourceReadGrant`） | **绝对不** | 撤销必须零放行：Core 侧 `source_read_refs.revoke_grants`（`core_service.py:4916-4938` → `source_read_refs.py:230-251`）只动内存 + 代次地板；写 DB 等于「撤销即重授权」。C-17 `:169`「不能自动恢复撤销的授权」、`:186`「不能自动重新授权」 |
| 用户重新注册（Host `Register` 新条目） | **不直接**（Host 动作不触 Core） | Host 的 registry 是私有的（`SourceAccessRegistry.cs`）；C-16 §1 命令面里没有「登记 Core location」的写命令 |
| **同一物理身份的重新导入 / 同步 apply（有 live grant 证明当前授权）** | **是（本卡核心）** | C-15 `:204`、`:233`：重授权/重新注册**原地更新**；跨 Registry 命中同一物理身份同样复用并原地更新 |
| 重授权后第一次**扫描**（scan） | **否** | C-17 `:228`（枚举只读、零写）、`scanner.py:1-8`（scan 从不写） |
| Host `Authorize`（每次授权） | **否**（建议不做，除非 DSH 裁决 D-3） | 授予读权限 ≠ 注册源；把每次 grant 变成 DB 写会把 Run/manual scan 全部变成写者（见 §3.3 讨论） |
| 启动/冷启动 | **否** | 只读枚举；C-17 `:279`「零写」 |

### 2.2 最小语义（可直接写成实现约束）

```
refresh_source_location_auth(source_id, digest, volume, file_id, registry_id, generation, now)
前置（全满足才写；否则零写 + 既有 typed 语义）：
  P1 调用点已持有 live grant（self._access.resolve(grant_id) 成功；未撤销/未过期）
  P2 grant 的物理身份 == 目标 location 行身份（content_digest/volume_serial/file_id 三键同一）
  P3 目标行 = 该 source 的 current 行（is_current=1）
  P4 调用发生在既有写事务内（页单元 / BEGIN IMMEDIATE），不新增独立事务
写：
  UPDATE source_locations
     SET registry_id=?, authorization_generation=?, last_verified_at=?
   WHERE source_id=? AND content_digest=? AND volume_serial=? AND file_id=?
   且（建议加固）is_current=1
不写：
  location_id / source_id / 身份三键 / size_bytes / observed_at / is_current / 任何 version/entry/binding/page
约束：
  C1 同 registry_id 时 generation 不得回退（Host 只增）；跨 registry_id 允许任意 generation（新注册恒 1）
  C2 幂等：值相同 → rowcount 0，不产生任何副作用
  C3 fail-closed：P1/P2/P3 任一不成立 → 不写、不报假成功
```

### 2.3 必须保持的不变量

| # | 不变量 | 反例（必须被判红） |
|---|---|---|
| I-1 | **撤销不自动放行** | 以 revoked registry 的 `(registry_id, generation)` 直调刷新 → 行被更新 |
| I-2 | **身份校验，无路径回退** | 用「同一路径、不同文件」的 grant 刷新（identity 不符）→ 行被更新 |
| I-3 | **fail-closed** | grant 解析失败/过期 → 仍写（或吞异常继续） |
| I-4 | **不新增 location 行**（C-15 `:204` 的 `UNIQUE` + 部分唯一） | 刷新后 `source_locations` 行数 +1，或产生两个 `is_current=1` |
| I-5 | **不改 source_id/身份键/digest/is_current** | 刷新把 `content_digest` 或 `volume/file id` 顺手改了 |
| I-6 | **审计可核对** | `last_verified_at` 恒 NULL 或写成非 ISO；日志出现路径/secret |
| I-7 | **幂等** | 同值重复调用产生 rowcount>0 的抖动或并发异常 |
| I-8 | **不越权到 binding** | 刷新顺带把 `page_bindings.authorization_generation` 抬到新值（C-15 `:233`/`:323` 明确旧 binding 允许 ≤，不需要也不应改写） |

### 2.4 三个实现陷阱（会直接决定 AC 是否可判别）

1. **folder 身份键陷阱（P2）**：import 侧 `_volume_serial/_file_id` 对 folder **退回首个成员文件的 facts**（`runtime.py:879-892`），而 C-15 `:216` 写的是「目录 identity=volume serial+file id」——二者**疑似不一致**（是否属真缺陷需另卡确认，本评审不下结论）。**对 L-S4 的硬约束只有一条**：刷新**必须复用写入时同一算法/同一来源**（`scanned.container_digest` 的 manifest + 同 `_volume_serial/_file_id`），**不得**改用 `grant.folder_entries[0][1]` 重新推导或改用「目录 file id」——否则 folder 源会**静默 0 行更新**（看似成功、实际不刷新）。**建议**：刷新键取自**目标 location 行自身**（`get_source_location_current`，`source_sync.py:703-712`），再与 grant 身份比对，而不是重新计算键。
2. **事务边界**：刷新必须在既有写事务内（import 页单元 `library.py:2514-2559`、sync apply `service.py:239` 之后）。**不得**为刷新单开事务，否则破坏 C-15 §6.4 的页级原子性，并可能留下「刷新成功但导入失败」的半写。
3. **store 归属**：死函数在 `SqliteLibraryRepository`（import 侧），sync apply 侧只有 `SourceSyncStore`（两者共用 `conn`，`core_assembly.py:1216/1236`）。**不得**为了调用而在 sync 侧复制第二份 SQL（那正是当前 `service.py:504-515` 的病根）。可行路径：**一份模块级 SQL helper**（或两者共享的 mixin），两个 store 各暴露一个薄方法。

---

## 3. Q3 契约 / UNFREEZE 判定

### 3.1 判定（明确）

| 方案 | 是否需要 UNFREEZE | pins | 说明 |
|---|---|---|---|
| **L-S4-A**（把 C-15 `:204/:233` 的原地刷新落到 import 复用路径 + sync apply，去重死代码，补测试） | **零契约**（**不需要**） | **0/18** | 只改 `src/**` + `tests/**`；wire/DTO/命令/能力/错误码/schema/迁移/依赖全部零变化 |
| **L-S4-B**（零交互自动恢复：新增 host-control 命令，如 `ReattestSourceLocation`，Host 在重新授权后主动通知 Core 刷新） | **需要** | **1/18**（**C-16 v1.5**：§0 新能力 + §2.x 新命令） | 会改变「谁在什么时机可以写 location auth」的授权面；C-17 不需要改（若走 host-control 面）；C-06 不需要改 |

> **结论：本卡按 A 面冻结 = 零契约。B 面只有在 DSH 明确要求「零交互恢复」时才立项，且必须先走 C-16 v1.5 UNFREEZE 载体 + 独立 byte-level 复核。**

### 3.2 冻结面逐项核对

| 冻结面 | 是否被 A 触碰 | 依据 |
|---|---|---|
| **C-15 v1.1**（Source 存储） | **不改字节；只兑现既有条款** | `doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md:204`（原地更新/不新建）、`:233`（源复用规则 v3：跨 Registry 复用并原地更新）、`:323-325`（撤销必须即时、generation 递增不使 binding 失效）。刷新只写**既有三列**（`schema.py:629-648` 已存在），无 DDL。 |
| **C-16 v1.4**（source-read wire） | **不改** | §2 grant 形状/四维 scope/失败码优先级（`:37-72`）、§2.4「零 DB 写」（`:89`）均不涉及 location 刷新；撤销通道语义（`:23`、`:205`）不变；无新命令、无新能力、无新错误码。 |
| **C-17 v1.1**（sync） | **不改** | `ScanTarget` 字段集不变（`:261-262`）；枚举仍零写（`:228`、`:279`）；apply 授权基线等值（`:289`）与 binding 读兼容（`:294`）不变；「不得自动重新授权」（`:169`、`:186`）不被违反（刷新**不是**授权决定，见 3.4）。**注意**：刷新会**改变枚举返回值**（registry_id/generation），这是**数据**变化而非 wire 形状变化。 |
| M2-C1 / C-05 / C-06 / C-14 | 不改 | 无命令面/协议号/能力变化；`CORE_PROTOCOL_MINOR=3` 不变 |
| `schema.py` / `migrator.py` / 依赖 | 不改 | 三列已存在（`schema.py:629-648`），无迁移 |
| 错误码闭集 | 不改 | A 面不新增任何 code；负路径沿用 `SOURCE_ACCESS_DENIED`/`SOURCE_GRANT_REVOKED`/`SOURCE_PLAN_STALE` |
| **C-15 与 L-S1 的并发风险** | **需注意** | 并发会话正在把 C-15 升到 v1.5（Registry 文件级损坏 vs 根身份不可用拆分）。该修订**不放宽**授权（其草案明文「不得自动重授权/自动恢复」「缺失根 ≠ 无授权」），与 A 面不冲突；但**两份卡若同时改 `doc/plan/**` 会造成 pin 竞争** → 本卡 Out 掉契约字节即可规避（§4.3）。 |

### 3.3 为什么这不算「改契约」——以及一条被否决的捷径

- **A 面是 conformance**：冻结文本已经**命令**Core 在重注册时原地更新（C-15 `:204/:233`）。实现没做 = 实现缺陷。把它做成实现修复**不产生任何新语义**，因此不触发 UNFREEZE 流程（与 `doc/reviews/FEA-11-RENDITION-1-scope-r1.md:21` 的「契约充分 → 不需要 UNFREEZE」同构）。
- **被否决的捷径（D-3 备选）**：在 `RegisterSourceReadGrant`（`core_service.py:4906-4914`）里顺手刷新 location。**不建议**：①它把「读授权注册」与「源注册」两种语义合并，等于让**任何一次 grant 铸造**（含 Run/manual scan）都获得写 location 的能力，授权面被无意放宽；②HOST `Authorize` 每次调用都会铸造（`SourceScanScheduler.cs:1533-1539`），刷新将变成高频写；③C-16 §2 的 grant 注册是签名/会话面（`:37-72`），在其上叠加 DB 写会让 `RegisterSourceReadGrant` 从「内存注册」升级为「状态变更」，**至少需要契约澄清**（保守按「需 UNFREEZE」处理）。若 DSH 坚持此路径，应当按 B 面（1 pin）处理，而不是当零契约。

### 3.4 刷新 ≠ 自动重新授权（安全口径）

- **授权决定**发生在 Host（用户显式动作 + `Authorize` 的根/代次/撤销校验，`SourceAccessRegistry.cs:56-74`）；Host 只对**非撤销**条目铸 grant。
- **刷新只是记录事实**：Core 被告知「这个物理身份现在由 `registry_id=X, generation=G` 覆盖」；它**不能**凭空产生授权（P1 要求 live grant）。
- 因此 `I-1`（撤销不自动放行）与 C-17 `:169/:186` 都保持：撤销条目**无法**铸出 grant → **无法**触发刷新。

---

## 4. Q4 范围与拆卡

### 4.1 单卡还是拆分

| 候选 | 内容 | 契约面 | 规模 | 建议 |
|---|---|---|---|---|
| **A. 函数接线 + auth 语义（本卡）** | 死代码合并为单点；import 复用路径与 sync apply 在「同物理身份 + live grant」时原地刷新；测试 | **零** | 小（1 个 SQL 单点 + 2 个调用点 + 测试） | **本卡冻结即做** |
| **B. 恢复流程（零交互）** | 新 host-control 命令 + Host 在重新授权后调用；或 Host 枚举期路径回退 | **C-16 v1.5（1 pin）**；若选 Host 路径回退还需改 Host 语义 + 既有测试 | 中 | **另卡，须 DSH 裁决是否值得** |
| C. Import「整源 skip」是否也刷新 | 在 `runtime.py:396-410` 的 skip 早返回前做一次条件刷新 | 零（但改变「skip = 零写」的既有预期） | 极小 | **并入 A，但必须由 DSH 显式裁决**（D-2） |

**不建议合成一张卡**：B 会把零契约小修复升级为「契约 + Host + App」三面改动，且与 L-S1 的 B 卡（恢复/重授权 UI）严重重叠（`doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-scope-r1.md:29/:130` 已把 L-S4 列为 L-S1-B 的前置）。

### 4.2 推荐 In（A 面）

1. **单点化**：把 `service.py:504-515` 的内联 UPDATE 改为调用唯一实现；建议把该实现放到两 store 均可用的位置（共享 SQL helper / mixin），**不得**复制第二份（§2.4-3）。
2. **import 复用路径刷新**：在 `_commit_page_unit`（`runtime.py:719-828`）的页单元事务内，当 `existing_source_id is not None`（重注册场景）且已解析的 live grant 身份与既有 location 行一致时，写入 `(registry_id, authorization_generation, last_verified_at)`；`insert_source=True`（新源）路径保持现状（插入即带对值）。
3. **sync apply 刷新条件从「仅 relink」扩到「live grant 证明身份不变」**（`service.py:504-515`）：relink 行为不变；`resync`/`repoint` 在 `same_container`（身份未变）时同样刷新；身份变化时保持既有「先置旧行 `is_current=0` 再插新行」（`service.py:737-760`）不变。
4. **（可选，D-2）整源 skip 的一次条件刷新**：仅当 `existing_source_id` 存在、live grant 身份一致、且值确实不同时，执行一次单行刷新；否则保持纯 skip。
5. **测试**（见 §5.2）与 `verification/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1/**` 证据。
6. **卡面修正**：把目标从「修复后只读切片可恢复」改为「**重注册后由下一次写路径（重导入/同步 apply）刷新 location auth；只读枚举随后跟随**」，并登记 limitation `L-S4-1`（无写路径介入时仍不恢复；零交互恢复见 B 面）。

### 4.3 推荐 Out

- Host / Avalonia（`apps/**`）：枚举期路径回退、`TryMap` 放宽、App 恢复入口 —— 全部属 B 面；且会撞 C-17 `:279` 的 fail-closed 口径与 `SourceScanSchedulerTests.cs:1134-1220` 的既有断言。
- 契约字节（`doc/plan/FEA-C1*`、`doc/contracts/**`）、冻结记录/矩阵、pins。
- `schema.py`/`migrator.py`/依赖/`CORE_PROTOCOL_MINOR`。
- 任何新命令/新能力/新错误码（= B 面）。
- 自动重新授权、启动即修复、后台自愈扫描。
- 真实用户数据、`git push`、`TASK_LEDGER` 手工编辑（DSH 用 `tools/governance/task_ledger.py --write` 重建）。
- 顺手修 folder 身份键缺陷（§2.4-1）：**登记 limitation**，不在本卡改。

### 4.4 allowed_paths（文件级建议）

```yaml
allowed_paths:
  - src/infrastructure/sqlite/library.py            # 唯一实现的家（或迁出到共享 helper）
  - src/infrastructure/sqlite/source_sync.py        # 若单点放在 sync store / 共享 helper 暴露
  - src/application/sources/service.py              # relink 内联 → 单点；刷新条件扩展
  - src/application/importing/referenced/runtime.py # 复用路径页单元内刷新
  - tests/fea11/test_source_relink.py               # 刷新判别（跨 registry/generation）
  - tests/fea11/test_source_scan.py                 # 枚举跟随刷新（Core 侧闭环）
  - tests/fea09/test_referenced_flow.py             # 重导入复用刷新 / skip 语义
  - tests/core/test_core_scan_target_commands.py    # 枚举=location 行（可扩展为刷新后断言）
  - doc/tasks/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1.md
  - doc/reviews/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1-*.md
  - doc/handoffs/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1-*.md
  - verification/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1/**
```

> 现卡 `allowed_paths` 只有 4 条 doc/verification 路径（`doc/tasks/...:20-25`），**冻结时必须整块替换为上面的实现面**，否则 Owner 无法实施。

### 4.5 AC 草案（v3：可判别 / fail-closed / 零漂移 / 门禁）

| AC | 断言 | 判别方法（必须能变红） |
|---|---|---|
| **AC-LS4-1 单点实现** | `grep -rn "UPDATE source_locations SET registry_id" src` **只命中 1 处**（单点实现），`refresh_source_location_auth` 有 ≥2 个生产调用者 | 删除调用点 → 目标测试 RED；保留第二份内联 UPDATE → grep 计数 =2 → 判红 |
| **AC-LS4-2 重导入刷新** | 同物理身份第二次导入（已存在 source）后，current 行 `registry_id/new_generation` = 新 grant；`location_id/source_id/content_digest/volume_serial/file_id/is_current` 不变；location 行数不变 | 回退实现 → 断言旧值 → RED；另加「行数 +1 / 两个 current」反例断言 |
| **AC-LS4-3 sync apply 刷新** | relink 与「身份不变」的 resync 均刷新到 grant 值；身份变化时走新行（旧行 `is_current=0` 且 auth 不变） | 把条件改回 `kind == "relink"` → resync 用例 RED |
| **AC-LS4-4 fail-closed 负测** | ①revoked/expired grant → 解析失败、**零写**；②identity 不符 → **零写**（snapshot 比对）；③folder 用错误身份键 → **零写**（不得静默「成功」） | 去掉任一前置校验 → 对应用例 RED；snapshot 逐表比对（含 `source_locations`） |
| **AC-LS4-5 撤销不自动放行** | 以已撤销 registry 的 `(registry_id, generation)` 走刷新路径 → 不产生任何恢复；Host `Authorize` 仍 `SOURCE_GRANT_REVOKED` | 人为让刷新绕过 grant 解析 → 用例 RED |
| **AC-LS4-6 幂等/单调** | 同值重复刷新 → rowcount 0、无抖动；同 `registry_id` generation 不得下降；跨 registry 允许 1 | 注入「generation 回退」用例 → RED |
| **AC-LS4-7 枚举闭环** | 刷新后 `source_list_scan_targets` 返回新 `registry_id/generation`（Core 侧断言）；Host 侧**不**要求在本卡改（用既有 `TryMap`/`Verify` 语义说明「刷新前 skip、刷新后可通过」） | 不刷新 → 枚举仍旧值 → RED |
| **AC-LS4-8 审计** | `last_verified_at` 为非空 ISO；日志/异常不含路径、secret、grant token | 抓日志断言 0 命中 |
| **AC-LS4-9 零漂移** | `git diff --name-only <base>..HEAD -- doc/plan doc/contracts src/infrastructure/sqlite/schema.py src/infrastructure/sqlite/migrator.py apps/** requirements.txt` **为空**；`CORE_PROTOCOL_MINOR=3`；`verify_pins` 18/18；scope diff ⊆ allowed_paths | 任一非空 → 判红 |
| **AC-LS4-10 门禁/证据** | 全量 `pytest tests` ≥ 现行基线（本评审实测 **3305 passed/10 skipped**）且 0 回归；`tests/fea11`+`tests/core` 全绿（本评审实测 1158 passed/76.7 s）；`check.ps1`（默认 + `-TaskPath`）PASS；证据 sha256 齐备；`NOT_RUN` 明示 | 任一失败/未跑未标 → 判红 |

### 4.6 门禁前置（阻断性，但属 DSH 动作）

`check.ps1` 当前 **FAIL**（TASK_LEDGER 陈旧，§0）。冻结/释放前必须由 Lead 在 clean 树上跑 `tools/governance/task_ledger.py --write` 并提交；否则 AC-LS4-10 天然不可达。**不属于 Owner 的 allowed_paths**。

---

## 5. Q5 测试 / 证据

### 5.1 现有 fixture 能否覆盖目标场景

| 目标场景 | 现有 fixture 能力 | 结论 |
|---|---|---|
| 「撤销 → 重注册 → 刷新」 | `tests/fea11/conftest.py:170/:291-309` 的 `mint_grant(registry_id=..., generation=...)` **可传不同 registry/generation**；`seed_source_location` 同样可指定 | **可构造**（无需新 fixture） |
| 「重导入复用路径」 | `tests/fea09/conftest.py:125` 与 `tests/fea09/test_referenced_flow.py:371-393` 已有真实 zip + 复用流程 | **可构造**（补断言即可） |
| 「撤销后不得自动放行」 | Host 侧有；Core 侧可复用 `tests/fea11/test_source_scan.py` 的 stale/zero-write 快照模式（`tests/fea11/test_source_scan.py:261-279`） | **可构造** |
| 「只读切片恢复」 | Host 侧已有 `SourceScanSchedulerTests` 枚举验证（`EnumeratedTarget(...)` 辅助），但**本卡不改 Host**；Core 侧断言到枚举值即可 | **部分**（Core 断言足够；Host 端到端 = B 面） |
| 全量 .NET | 需 `dotnet test`（成本高、已知 shard flaky） | **不需要**（Host 零改动；在卡面标 NOT_RUN 并说明理由） |

### 5.2 必须新增的测试（最少集）

1. `refresh` 单测：命中 1 行 / 0 行（identity 不符）/ 同值 0 行（幂等）/ 同 registry generation 回退拒绝 / folder 身份键不匹配 0 行。
2. import 复用刷新：第二次导入（**新 `registry_id` + generation=1**，或同 `registry_id` + generation=2）后 location 三列更新、四键与行数不变。
3. sync apply 刷新：relink 用**不同** generation（改现有用例 `tests/fea11/test_source_relink.py:110-112` 的同值断言）+ resync 同身份刷新。
4. 负测：「撤销的 registry」无法刷新（零写 snapshot）；identity 不符零写。
5. Core 闭环：刷新后 `list_scan_targets` 的 `registry_id/generation` 跟随（扩 `tests/core/test_core_scan_target_commands.py:321-352` 的同类断言）。
6. （若采纳 D-2）整源 skip 的条件刷新 + 「skip 不再绝对零写」的显式断言。

### 5.3 全量门禁成本 / flaky（实测 + 既有记录）

| 项 | 值 | 来源 |
|---|---|---|
| `pytest tests` 全量 | **3305 passed / 10 skipped / 243.86 s / EXIT 0** | **本评审实测**（T1） |
| `pytest tests/fea11 tests/core` | **1158 passed / 76.72 s / EXIT 0** | **本评审实测** |
| .NET 全量 | 基线 **1527 passed / 0 failed / 86 skipped**（2026-11-06）；已知 shard 偶发 1–2 例 flaky（隔离复跑 PASS） | `doc/STATUS.md:20`；`doc/tasks/FEA-11-SCAN-2.md:156`（RUN1/RUN2 flaky、RUN3 全绿） |
| 已知污染风险 | 历史记录：全量 pytest 会重写 tracked 的 `verification/FEA-09/logs/wire-redacted.ndjson`（`doc/reviews/FEA-11-RUN-GRANT-2-scope-r1.md:38`）。**本评审实测 3305 例跑完后未见该文件被改动**（该历史现象本轮未复现；`git status` 中 `verification/` 下只有并发会话新建的 `FEA-11-L-S1-...-PREREQ-1/`），但卡面仍应要求「跑完核对 `git status`，必要时恢复」 | 本评审实测 + 既有记录 |
| Python 噪声 | 用例会打印 PySide6/QML `TypeError: ... of null` 警告（不影响 PASS），日志检索时需按 `passed|failed` 过滤 | 本评审实测 |

---

## 6. Q6 优先级与 DSH 裁决要点

### 6.1 与队列中其他项的对比

| 项 | 性质 | 用户可见性 | 成本 | 契约面 | 相对建议 |
|---|---|---|---|---|---|
| **L-S1**（Registry 根级韧性） | 可用性/安全 fail-closed 粒度 | 高（全库不可读） | 中（Host-only 读取面 + C-15 v1.5） | 1 pin（进行中） | **先做**（已是下一候选；并发会话正在推进） |
| **L-S4（本卡 A）** | 契约一致性 + 静默监控丢失 | 中（重注册后该源不再被扫描） | **小**（1 SQL 单点 + 2 调用点 + 测试） | **0 pin** | **紧随 L-S1**（且是 L-S1-B 的前置） |
| **2C 长 Run 续期（L-G1）** | 功能缺口（长 Run >300 s 失权） | 中高（长任务中断） | 中（需设计 + 可能契约） | 可能 1+ pin | 排在 L-S4 之后或并行设计；需独立 scope review |
| **L-R11**（gate 统一） | 一致性/审计（第三套谓词风险） | 低 | 小-中 | 0 | 可穿插 |
| **C-04b**（8 项文档 residual） | 文档 | 无 | 极小 | 0 | 穿插 |
| **SCAN-2 RH-1…5** | 可观测性/limitation | 低 | 小 | 0 | 穿插 |
| **UI P3** | 视觉/交互打磨 | 低 | 小 | 0 | 最后 |

**推荐顺序**：**L-S1 → L-S4-A →（2C 设计另卡）→ L-R11 → C-04b / SCAN-RH / UI P3**。与 L-S1 scope review 的结论一致（`doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-scope-r1.md:222/:228`：L-S4「与 B 卡绑定，紧随 A」）。

### 6.2 需 DSH 裁决的问题（含推荐）

| # | 问题 | 推荐 | 影响 |
|---|---|---|---|
| **D-1** | 卡面是否按 A/B 拆？本卡是否只做 A（零契约）？ | **是**。本卡 = A；「零交互恢复枚举切片」= L-S4-B（另卡，C-16 v1.5，1 pin）；卡面登记 limitation `L-S4-1` | 决定是否需要 UNFREEZE 流程与证据规模 |
| **D-2** | 是否允许在 import「整源 skip」路径写一次条件刷新？ | **允许**（仅当 live grant 身份一致且值不同；幂等；单行；同一事务）；卡面与证据必须明写「skip 不再绝对零写」。若反对，则登记 limitation（该场景永不恢复） | 决定「已全量导入的源重注册后能否恢复」——这是最常见的用户路径 |
| **D-3** | 是否采纳「在 `RegisterSourceReadGrant` 里刷新」这条捷径？ | **不采纳**（§3.3：授权面放宽 + 高频写 + 契约需澄清）；如坚持 → 按 B 面 1 pin 处理 | 决定授权面是否被无意扩大 |
| **D-4** | 单点实现放哪？（`SqliteLibraryRepository` / `SourceSyncStore` / 新共享 helper） | **新共享 SQL helper 或 store mixin**，两 store 各一薄方法；禁止复制第二份 SQL | 决定 allowed_paths 与后续可维护性 |
| **D-5** | folder 身份键与 C-15 `:216`「目录 identity=volume serial+file id」**疑似不一致**（`runtime.py:879-892` 用首成员 file_id）是否本卡修？ | **不修**，登记 limitation `L-S4-2`（需另卡确认是否真缺陷）；本卡只要求「刷新复用写入时同一算法」，不改身份模型 | 防止本卡扩到身份语义 |
| **D-6** | 冻结/实施前是否强制 clean 树 + 重建 TASK_LEDGER？ | **是**。当前 `check.ps1` FAIL、`verify_pins` C15 MISMATCH 均来自并发会话未提交字节；必须在 clean 且已提交的 head 上重跑 | 否则 AC-LS4-9/10 不可判 |

---

## 7. 风险

| # | 风险 | 等级 | 缓解 |
|---|---|---|---|
| R1 | **语义外溢**：刷新使枚举从「skip」变「可通过」，读起来像「自动恢复」 | 中 | AC-LS4-5 + 卡面口径：恢复前提是**用户已在 Host 重新授权**；刷新只记录事实（§3.4） |
| R2 | **folder 身份键陷阱** → 静默 0 行更新（假成功） | **高** | AC-LS4-4③；刷新键取自 target 行自身；禁止用成员 facts 重新推导（§2.4-1） |
| R3 | **事务边界**：为刷新单开事务 → 破坏页级原子性/半写 | 高 | AC-LS4-2/3 的事务断言；只在既有事务内写（§2.4-2） |
| R4 | **「skip=零写」预期被改**（若采纳 D-2） | 中 | D-2 显式裁决 + 卡面/证据明示 + 断言该写仅 1 行 |
| R5 | **测试无判别力**：现有 fixture 全 `reg-1/gen1`，同值刷新测不出 | 高 | AC-LS4-2/3 强制使用不同 `registry_id` 或 generation≥2；变异测试 |
| R6 | **与 L-S1 并发冲突**（C-15 v1.5 正在改 + 共享工作树） | 中 | 本卡 Out 契约字节；冻结前要求 clean 树（D-6）；不要并行改 `doc/plan/**` |
| R7 | 把 Host 拉进写域（路径回退/枚举放宽）以「顺便修好」 | 中 | Out 明确禁止；撞 C-17 `:279` 与 `SourceScanSchedulerTests.cs:1134-1220` |
| R8 | 枚举与刷新竞态：刷新瞬间枚举读到新旧混合 → Host typed skip | 低 | 只读快照 + fail-closed 是安全结果；在 limitation 中说明 |
| R9 | `get_source_location_current` 不返回 `last_verified_at`/`is_current`（`source_sync.py:703-712`）→ 测试无法从投影断言审计列 | 低 | 测试直连 `conn` 断言（现有测试已用直连模式，`tests/core/test_core_scan_target_commands.py:341-346`） |
| R10 | 并发会话使门禁红灯被误读为本卡缺陷 | 中 | 本报告 §0 时间戳 + 归因；DSH 裁决 D-6 |

---

## 8. 证据锚点索引（结论 → 可复核位置）

| 结论 | 锚点 |
|---|---|
| 死代码定义 / 零调用 | `src/infrastructure/sqlite/library.py:2293-2310`；`Select-String` 全 `src`+`tests` 仅 1 命中 |
| 同义内联且仅 relink | `src/application/sources/service.py:504-515` |
| import 只在新建源时写 location | `src/application/importing/referenced/runtime.py:556-557`、`:794-815`；`src/infrastructure/sqlite/library.py:2514-2559` |
| 整源 skip 早返回（零写） | `src/application/importing/referenced/runtime.py:396-410` |
| 物理身份复用判定 | `src/application/importing/referenced/runtime.py:592-607`；`src/infrastructure/sqlite/library.py:2251-2263` |
| folder 身份键取自首成员 | `src/application/importing/referenced/runtime.py:879-892` |
| 枚举读 location 行 | `src/infrastructure/sqlite/source_sync.py:82-94`；`src/application/sources/scanner.py:96-193` |
| 缺失观察比对 location | `src/application/sources/scanner.py:589-609` |
| Host 注册/撤销/授权语义 | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs:34-52`、`:56-74`、`:76-86` |
| Host 枚举映射/执行期复核/无路径回退 | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs:2162-2169`、`:1505-1512`、`:1561-1610`、`:1885-1926` |
| Host 固化 skip 的测试 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceScanSchedulerTests.cs:1120`、`:1134-1220` |
| 真实 IPC 用 SQL 直改 location（旁证无写者） | `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11ScanIpcTests.cs:49-60` |
| 枚举跟随 location 行（可判别基础） | `tests/core/test_core_scan_target_commands.py:321-352` |
| relink 测试无判别力（同值） | `tests/fea11/test_source_relink.py:110-112` |
| import skip 无 auth 断言 | `tests/fea09/test_referenced_flow.py:371-393` |
| 契约：原地刷新 | `doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md:204`、`:233`、`:323-325` |
| 契约：grant 形状/失败码 | `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md:37-72`、`:89`（§2.4 零 DB 写） |
| 契约：枚举字段/零写/不得自动重授权 | `doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:228`、`:239-240`、`:261-262`、`:279`、`:169`、`:186`、`:289`、`:294` |
| SCAN-2 L-S4 原文 | `doc/tasks/FEA-11-SCAN-2.md:132`、`:252`；`verification/FEA-11-SCAN-2/host-shard-record.md:110`；`doc/reviews/FEA-11-SCAN-2-scope-r1.md:378` |
| 本卡占位现文 | `doc/tasks/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1.md:3`、`:7`、`:20-25`、`:36-38`、`:42-48` |

---

## 9. 真实性声明

1. **唯一写入**：本评审只写了 `doc/reviews/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1-scope-r1.md` 这一个文件。**未**修改/删除/移动任何生产代码、测试、契约、冻结记录、矩阵、Task 卡、STATUS、REBASELINE_PLAN、TASK_LEDGER 或证据字节；**未**执行 `git add`/`git commit`/`git push`。
2. **独立性**：评审者为独立上下文的 fresh subagent，未参与本卡、`FEA-11-SCAN-2`、`FEA-11-L-S1-*` 或 `FEA-11-RUN-GRANT-*` 的实现、返修或前轮审查；只读被审 head 与背景文件。
3. **并发披露**：评审期间共享 `main` 工作树被另一会话持续写入（C-15 v1.5 UNFREEZE 预热：`M doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md`、`M doc/plan/FEA-CONTRACT-FROZEN-C15.md`、`M doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`、`M doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1.md`、`?? doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C15.md`、`?? verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1/`；`doc/tasks` 计数由 528 涨到 530），并提交了 `821b309a0`（docs-only：L-S1 scope review、L-S1 PREQ-1 卡、**本卡占位卡入库**、TASK_LEDGER 重算）。上述字节**与本评审无关**，本评审未读取、未引用其作为任何结论依据；`M`/`??` 全部保留原状。**本评审在仓库内唯一新增的字节是本报告文件本身。**
4. **事实优先级**：所有代码/契约断言均来自**本轮命令在 reviewed_head 字节上的实测**（`git show HEAD:` 读取 C-15 冻结条款以排除并发工作树编辑的干扰），未采信卡面、既有 Review 或 Handoff 的自述；引用既有 Review 时已标注为「既有记录」。
5. **未跑项**：全量 `dotnet test`、`NEWMANGA_FEA11_IPC=1` 真实 IPC、`generate_api_inventory.py --check`、`scope_validation.py` 均 **NOT_RUN**（理由见 §0）；本评审的 `check.ps1`/`verify_pins.ps1` 结果带**时间戳与并发归因**，不代表 clean 树结论。
6. **判别力声明**：本报告未通过任何「破坏-恢复」实验验证既有测试的判别力（只读约束下无法改动生产/测试字节）；§5.2 的判别要求是给实现卡的**待验证项**，不是本轮已完成证据。
