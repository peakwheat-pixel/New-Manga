# FEA-C06 授权面（SourceAccessRegistry ⇄ source-read grant）草案

状态：**FROZEN v1.2（2026-11-06 重冻；v1.0 于 2026-11-01 冻结、v1.1 于 2026-11-03）**（载体 [CONTRACT-UNFREEZE-2026-11-06-C06-C16](../reviews/CONTRACT-UNFREEZE-2026-11-06-C06-C16.md)；冻结记录 [FEA-CONTRACT-FROZEN-C06](FEA-CONTRACT-FROZEN-C06.md)；v1.2 独立 byte-level 复核见载体；v1.1 复核 r7 approved 见冻结记录）
日期：2026-11-01（v1.0）；2026-11-03（v1.1 UNFREEZE）；2026-11-06（v1.2 UNFREEZE）
作者：DSH（Lead / Architect / Integrator）
依据：[FEA-01 契约清单](FEA-01_CONTRACT_DRAFT.md) 的 C-06、[AD-003](../AD-003_REFERENCED_SOURCE_ARCHITECTURE.md) §3.2/§3.5、[ADJ-001](../contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md) PD-05/PD-06、代码现状（`src/application/importing/import_source_refs.py`、`src/application/resource_channel/`）

**边界声明**：本文件是**草案**，不冻结具体字段名；协议级冻结须在 `G-CONTRACT` 关闭后由 DSH 执行。

---

## 1. 现状

| 项 | 现状 | 出处 |
|---|---|---|
| 资源通道 | `resource_channel` 服务（wire v1），grant 三件套 = identity / size / digest 校验 | `src/application/resource_channel/service.py`、`dto.py` |
| 导入授权 | `ImportPages` 一次性 grant（≤300 秒、直属成员、进程内 registry） | `import_source_refs.py:153/108/192-203` |
| 长期授权 | **不存在**；`SourceAccessRegistry` 在 `src/` 0 命中（AD-003 §4 已记） | AD-003 §4 |
| 授权边界 | 现在的 grant 只覆盖「一次性导入」；引用源读取需要**长期**可证明的授权根 | AD-003 §3.5 |

## 2. 目标（冻结候选）

### 2.1 `SourceAccessRegistry`（Host 私有、持久化）

| 项 | 内容 |
|---|---|
| 归属 | **Host 侧**（不是 Core、不是 UI）；UI 不可见其内部结构 |
| 持久化 | Host 私有存储（不写 Core DB）；**随备份纳入**（AD-003 §3.3「源引用与授权元数据默认包含」），备份包内加密；**不得在备份包之外**泄露 |
| 条目字段（候选） | `{ registryId, locator, authorizedRoots[], identityFacts, generation, createdAt, lastUsedAt }`；**`identityFacts` 必须含内容 digest + volume serial + file ID**（AD-003 §3.2 明文「不得仅凭路径、mtime 或 size 断言同一文件」）；`size`/`mtime` 只作快速预筛，不单独构成身份 |
| 语义 | 一条 registry 记录 = 一个「用户已授权读取的源根」；`generation` 每次授权变更递增 |
| 生命周期 | 用户显式授权创建；用户撤销/源不可达时失效；**不因导入完成而删除**（这些是引用源，需长期可读） |

### 2.2 `source-read` grant（新 grant 类型）

| 项 | 内容 |
|---|---|
| 申请方 | Core（导入/同步/重定位时）；现有传输无 Core→Host RPC，故由 Host 承载操作请求并在 **dispatch 前**按 Registry 铸造 grant（C-06 v1.1；语义上 Core 仍是申请方，Host 是唯一授予方） |
| 授予方 | Host（校验 `SourceAccessRegistry` + 逐根 identity；铸造时完成 scope→授权根解析） |
| grant 字段（v1.1 冻结） | `{ grantId, registryId, generation, expiresAt, scope{ sourceId, version, entry[], rendition }, budget{ maxBytes, maxDecodeBytes, maxEntries }, entries[{entryKey, entryId?, locator, ordinal, path, facts}], secretRef?, signingKey, signature }`；`scope` **按 SourceId/version/entry/rendition 四维**限定（AD-003 §3.5），**不是**裸 `paths[]`；UI **不得**获得任意 `ReadFile(path)`；签名覆盖全部 signed fields |
| 有效期 | **短期**（≤ 单次操作，≤300 秒）；**不得**作为长期通行证复用 |
| 与旧 grant 的关系 | 旧 `ImportPages` 一次性 grant **保持原语义**（≤300 秒、直属成员、进程内）；`source-read` 是**独立**的新 grant 类型，不复用旧类型 |
| 撤销/失联（v1.1） | 用户撤销 → Host 持久化 generation+1 → 推送 `RevokeSourceReadGrant`（Host→Core）→ Core 立即废止 grant、下一提交边界停止并 ACK → Host 收到 ACK 后才向调用方返回成功；Core 检测 stdin EOF/transport 失败 → 全部 grant 立即失效（fail-closed）。**不得以 300 秒 TTL 代替即时撤销** |
| 授权建立（v1.2，第三生产者） | `source-read` grant→page binding 的**读授权**可由 Core 的 host-control 授权建立命令（C-16 v1.3 §2.4 `AuthorizeSourceReadForRun`）在 Run dispatch 前建立：Core 用与 Run 相同的 scope 展开器解析目标页，按签名 grant 的 `source_id/version/entry(locator\|ordinal\|entry_key)` 与 facts 校验当前 healthy binding 后，写入与导入/同步同构的**进程内** grant→binding 映射（零 DB 写）。该建立**不延长 ≤300s 有效期**、不改变撤销/失联语义、不得以路径回退；同一 binding 允许多份 grant，读时选择沿用既有 `find_bound_for_source`（live、最高 generation/`grant_id`）；建立失败必须 typed 且零业务写 |
| 失败 | registry 不存在/过期/generation 不匹配/identity 变化 → `SOURCE_ACCESS_DENIED`（fail-closed，不降级读取） |

### 2.3 命令/字段（协议增量，候选）

| 命令 | 方向 | 入参 | 出参 |
|---|---|---|---|
| `RegisterSourceRoot` | UI → Host | `{ locator, roots[] }`（`locator` = 用户选择的源展示名；`roots[]` = 授权根绝对路径列表，Host 校验规范化后互不包含、均在用户可选范围内） | `{ registryId, generation }` |
| `ListSourceRoots` | UI → Host | `{}` | `{ entries: [{ registryId, locator, roots[], generation, createdAt, lastUsedAt }] }`（重启后 UI 列出/撤销已授权根） |
| `RevokeSourceRoot` | UI → Host | `{ registryId }` | `{}` |
| `RequestSourceRead` | Host 铸造（操作 dispatch 前） | 语义请求：`{ registryId, generation, scope{ sourceId, version, entry[], rendition }, budget{ maxBytes, maxDecodeBytes, maxEntries } }`（v1.1 四维 scope） | `{ grantId, expiresAt }`；Host 是唯一授予方，无 Core→Host RPC |
| `VerifySourceRead` | 双侧（v1.1） | Host 铸造时：`{ grantId, scope, facts }` → 解析 scope→授权根并拒绝越根；Core 读取前/commit 前：签名/session/expiry/generation/identity facts 校验 | Host：`{ ok, reason? }`；Core：本地 typed 拒绝（不回 Host） |
| `RevokeSourceReadGrant`（v1.1 新增） | Host→Core（host-control） | `{ registryId, generation, grantIds[] }` | `{ revoked:true, grantsRevoked:n }` ACK；Host 收到 ACK 后才返回撤销成功 |
| `AuthorizeSourceReadForRun`（v1.2 新增） | Host→Core（host-control） | `{ grant_ids[]（1..64，closed shape）, command, scope }`：Run dispatch 前为本次 Run 建立 grant→binding 读授权；不携带路径；`command` 限定为可由 scope 展开的 Run 起始命令 | `{ bound_pages }`（成功）；任一目标页不可授权 → **整体 typed `SOURCE_ACCESS_DENIED`**、零绑定写入、Host 不得 dispatch（C-16 v1.3 §2.4） |

新增命令按 **minor** 递增（当前资源控制面 wire v1 → 本组命令 v1.1；**不改 major**）；旧 Host 不识别 → `PROTOCOL_VERSION_UNSUPPORTED`。**读取面**：`RequestSourceRead` 的 `scope` 必须按 `SourceId/version/entry/rendition` 表达并带预算，**不接受** `paths[]` 形式。

## 3. 安全约束

1. **一次性 ≠ 长期**：旧 `ImportPages` grant 不得被改造/复用于长期读取（AD-003 §3.2 明文）。
2. **fail-closed**：任何 registry/generation/identity 校验失败 → 拒绝，不回退到「直接读路径」。
3. **无路径泄漏**：错误码/日志不出现绝对路径（与 M2-C1 §5.11.5 同口径）。
4. **授权面不可被 UI 绕过**：UI 只能经 Host 命令申请，不得直接持有 registry/grant 内部结构。
5. **撤销即时**：`RevokeSourceRoot` 后，所有未过期 grant 立即失效（generation 递增）。
6. **越根拒绝**：符号链接/junction 指向授权根外 → 不跟随（reparse 拒绝），返回 `SOURCE_ACCESS_DENIED`（与 C-01b SC-22 一致）。
7. **读取预算**：每次 grant 有字节上限与解码尺寸上限；超限 → 拒绝（不截断）。
8. **`user-source` 不得进入 derived-cache grant**：源读取与 derived 缓存是两条独立通道（C-01b SC-20）。
9. **外部写/删只收敛到 registry + 回收站桥**：除 `SourceAccessRegistry` 与 Windows 回收站桥外，任何路径不得对外部源文件写/删（AD-003 §3.7）。
10. **即时撤销/失联 fail-closed（v1.1）**：撤销以 Host 持久化 generation+1 并收到 Core `RevokeSourceReadGrant` ACK 为线性化点；撤销成功后新读/新 commit 一律拒绝。Core 检测 Host 失联（stdin EOF/transport 失败）即废止全部 grant；不得以 TTL 或旧签名继续读取。
11. **commit 前确认（v1.1）**：每个提交单元在事务提交前重验本地 grant 有效性（撤销集合/generation/expiry/identity），任一失败中止后续单元；已提交单元保留（不声称整次导入原子）。

## 4. 与 C-01b / C-05 / C-04b 的接口

- **C-01b**：SC-21（引用源读取需独立授权面）由本草案落地；**SC-01**（新导入不复制）依赖长期读取授权；SC-07（旧 managed 双读）**不依赖**本授权面。
- **C-05 v1.1**：源读取产生的 referenced 页进入 C-05 v1.1 `V_ref` 分支（完整性由 binding/`integrity_status` 承载，**不**创建 artifact/revision）；artifact/revision 可见性谓词只适用于 managed/derived 页。
- **C-04b**：删除授权（AD-003 §3.7 / PD-02/PD-03；注意 PD-05=事务边界、PD-06=失败回滚）与本授权面**独立**——删除不撤销源读取授权，反之亦然。

> 注：ADJ-001 的 PD-05 = 事务边界、PD-06 = 失败回滚；删除**授权**在 AD-003 §3.7（`：95`）/PD-02/PD-03，不在 PD-05/PD-06。

## 5. 冻结条件

1. 独立复核通过；
2. **C-01b 已冻结**（SC-21/SC-22 由本草案落地）；
3. `G-CONTRACT` **对 C-06 不再构成阻塞**（本单承载 D05 的授权面子集：registry + source-read grant + 4 命令 + 9 条安全约束。**lease** 由 C-01b SC-25/29/31 承载；本单只含**per-request 解码预算**（`budget{maxBytes,maxDecodeBytes}`）；**D05 的缓存边界（策略/淘汰/持久化）仍由 C-01b/C-09 分担**；**重定位/同步、容器页映射** 目前**无承载条款**，仍属 D05 未覆盖项——Gate 保持 OPEN。见 [Gate 阻塞口径裁定](GATE-CLOSURE-RULING-2026-11-01.md) R-1′）；
4. **wire 版本由 DSH 批准**（v1.1 minor 增量）；
5. `check.ps1` PASS。

## 6. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立草案：现状表、SourceAccessRegistry 条目、source-read grant、4 条命令、5 条安全约束、与三份契约接口、冻结条件 | DSH |
| 2026-11-03 | **v1.1 UNFREEZE**：§2.2 明确 Host 铸造型发放与逐根 identity；grant 增加四维 scope/entries/budget/secretRef/signature 与撤销/失联线性化；§2.3 `RequestSourceRead`/`VerifySourceRead` 双侧归属修订 + 新增 `RevokeSourceReadGrant`；§3 增加约束 10/11。载体 [CONTRACT-UNFREEZE-2026-11-03](../reviews/CONTRACT-UNFREEZE-2026-11-03.md)；待独立复核后重冻并重算 pin | DSH；FEA-09-PREREQ-1 契约复核 r1 R1-002/R1-003 |
| 2026-11-06 | **v1.2 UNFREEZE**：§2.2 增「授权建立（第三生产者）」行；§2.3 增 `AuthorizeSourceReadForRun` 行；仅新增条目，既有 grant 形状/TTL≤300s/撤销/失联/错误闭集零改动。载体 [CONTRACT-UNFREEZE-2026-11-06-C06-C16](../reviews/CONTRACT-UNFREEZE-2026-11-06-C06-C16.md)；独立 byte-level 复核后重冻并重算 pin | DSH；FEA-11-RUN-GRANT-1-PREREQ-1 |
