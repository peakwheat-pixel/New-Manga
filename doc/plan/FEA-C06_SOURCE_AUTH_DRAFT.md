# FEA-C06 授权面（SourceAccessRegistry ⇄ source-read grant）草案

状态：**DRAFT / 未冻结 / 不释放实现 Task**
日期：2026-11-01
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
| 持久化 | Host 私有存储（不写 Core DB）；加密或受 ACL 保护，**不得**出现在备份包外泄面 |
| 条目字段（候选） | `{ registryId, locator, authorizedRoots[], identityFacts{ size, mtime, fileId? }, generation, createdAt, lastUsedAt }` |
| 语义 | 一条 registry 记录 = 一个「用户已授权读取的源根」；`generation` 每次授权变更递增 |
| 生命周期 | 用户显式授权创建；用户撤销/源不可达时失效；**不因导入完成而删除**（这些是引用源，需长期可读） |

### 2.2 `source-read` grant（新 grant 类型）

| 项 | 内容 |
|---|---|
| 申请方 | Core（导入/同步/重定位时），经 Host |
| 授予方 | Host（校验 `SourceAccessRegistry` + `identityFacts`） |
| grant 字段（候选） | `{ grantId, registryId, generation, expiresAt, scope{ paths[] } }` |
| 有效期 | **短期**（≤ 单次操作，建议 ≤300 秒）；**不得**作为长期通行证复用 |
| 与旧 grant 的关系 | 旧 `ImportPages` 一次性 grant **保持原语义**（≤300 秒、直属成员、进程内）；`source-read` 是**独立**的新 grant 类型，不复用旧类型 |
| 失败 | registry 不存在/过期/generation 不匹配/identity 变化 → `SOURCE_ACCESS_DENIED`（fail-closed，不降级读取） |

### 2.3 命令/字段（协议增量，候选）

| 命令 | 方向 | 入参 | 出参 |
|---|---|---|---|
| `RegisterSourceRoot` | UI → Host | `{ locator, roots[] }` | `{ registryId, generation }` |
| `RevokeSourceRoot` | UI → Host | `{ registryId }` | `{}` |
| `RequestSourceRead` | Core → Host | `{ registryId, generation, paths[] }` | `{ grantId, expiresAt }` |
| `VerifySourceRead` | Host 内部 | `{ grantId, path, identity }` | `{ ok, reason? }` |

新增命令按 **minor** 递增（wire v1 → v2）；旧 Host 不识别 → `PROTOCOL_VERSION_UNSUPPORTED`。

## 3. 安全约束

1. **一次性 ≠ 长期**：旧 `ImportPages` grant 不得被改造/复用于长期读取（AD-003 §3.2 明文）。
2. **fail-closed**：任何 registry/generation/identity 校验失败 → 拒绝，不回退到「直接读路径」。
3. **无路径泄漏**：错误码/日志不出现绝对路径（与 M2-C1 §5.11.5 同口径）。
4. **授权面不可被 UI 绕过**：UI 只能经 Host 命令申请，不得直接持有 registry/grant 内部结构。
5. **撤销即时**：`RevokeSourceRoot` 后，所有未过期 grant 立即失效（generation 递增）。

## 4. 与 C-01b / C-05 / C-04b 的接口

- **C-01b**：SC-21（引用源读取需独立授权面）由本草案落地；SC-07/SC-01 的「新导入不复制」依赖本授权面。
- **C-05**：源读取产生的 revision 进入可见性谓词（`integrity_status` 校验同口径）。
- **C-04b**：删除授权（PD-05/PD-06）与本授权面**独立**——删除不撤销源读取授权，反之亦然。

## 5. 冻结条件

1. 独立复核通过；
2. `G-CONTRACT` 关闭（AD-003/ADJ-001 授权语义冻结）；
3. `check.ps1` PASS。

## 6. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立草案：现状表、SourceAccessRegistry 条目、source-read grant、4 条命令、5 条安全约束、与三份契约接口、冻结条件 | DSH |
