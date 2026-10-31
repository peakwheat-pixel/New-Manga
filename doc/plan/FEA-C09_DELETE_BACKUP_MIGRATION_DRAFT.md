# FEA-C09 删除 / 备份 / 迁移的数据边界（草案）

状态：**DRAFT / 未冻结 / 不释放实现 Task**
日期：2026-11-01
作者：DSH（Lead / Architect / Integrator）
依据：[FEA-01 契约清单](FEA-01_CONTRACT_DRAFT.md) 的 C-09、[C-01b 存储契约](FEA-C01b_STORAGE_CONTRACT_DRAFT.md)（SC-10a/10b、SC-30/31/33）、[ADJ-001](../contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md)、[AD-003](../AD-003_REFERENCED_SOURCE_ARCHITECTURE.md) §3.3/§3.4、代码现状（`nmbak.py`、`cleanup.py`、`library.py`）

**边界声明**：本文件是**草案**；不改冻结契约、不改代码。

---

## 1. 现状（代码事实）

| 面 | 现状 | 出处 |
|---|---|---|
| 备份打包 | `nmbak.py` 只打包 `library.db` + sidecar + `managed/`；**不含** `settings/*.json`、`catalog.sqlite`；`managed/trash-manifest.json` 被白名单排除（`:660-665`） | C-01b SC-10a/10b 已核 |
| 清理路径 | `cleanup.py:41` **`CACHE_SAFE_PREFIXES = ("cache/",)` 缓存前缀**；`:16-20` 是 docstring（非校验逻辑）；真实受管相对路径校验在 `:73-116` | C-01b SC-03/SC-24 |
| 软删/彻底删除 | `library/service.py:97-99` 软删；`trash.py:119/196` 页级；`library.py:1069-1101` 项目级永久删除 | C-01b SC-30 已核 |
| 数据根迁移 | 有迁移入口（历史 Task 已做幂等空操作验证） | SAFETY-6 AC3（MA-11 待裁决） |
| 回收站桥 | **无**（AD-003 §4 已记） | 依据：AD-003 §3.7 / ADJ-001 §3 流程 C（PD-06 = 失败回滚，不是回收站桥的依据） |

## 2. 契约条款（冻结候选）

### SC-B01 备份覆盖清单

- **必须包含**（默认）：`library.db`、sidecar、`managed/`（含 `trash-manifest.json`，**需扩白名单**）、**源引用与授权元数据**（AD-003 §3.3；Host 私有 registry 随备份纳入，备份包内加密）。
- **默认不包含**：外部原文件、`settings/*.json`（凭据）、`catalog.sqlite`（缓存，可重建）。
- **扩展点**：`nmbak` 白名单改为**显式清单**（每项一个条目 + 版本号），新增项须走独立 Task。

### SC-B02 备份恢复的完整性

- 恢复前校验：备份包的 manifest 完整性（文件数/字节/hash）+ Schema 版本兼容。
- **恢复冲突语义**（AD-003 §3.3）：默认**逐项 Defer**（不整库覆盖）；`UseBackup` 前必须先存受保护版本；冲突项需用户逐项确认。
- 不兼容 Schema → 拒绝恢复（`BACKUP_SCHEMA_INCOMPATIBLE`），**不**尝试自动降级。

### SC-B03 数据根迁移

- 迁移 = **复制到新根 → 校验 → 切换指针**；旧根**保留只读**（不删除）。
- 迁移 journal 记录「源根/目标根/开始时间/阶段/结果」+ **`DatabaseId`**（C-01b SC-18；回填前 identity 为 unknown）；崩溃后可从 journal 恢复。
- **独占维护锁 + staging + 校验 + commit marker**（C-01b SC-17）：迁移期间禁止其他写入；staging 完成后校验（文件数/字节/hash）；commit marker 落库后才切换指针。
- **不得**部分迁移后切换（原子性）。

### SC-B04 删除的三层边界

| 层 | 触达 | 依据 |
|---|---|---|
| **软删**（应用回收站） | 只置 `deleted_at`；不触文件 | ADJ-001 |
| **自动清理** | 只清可再生产物（derived/cache），不清人工修改/revision | ADJ-001 §3 |
| **显式彻底删除** | DB 行 + 清单内 managed 文件；**永不**触原文件 | ADJ-001 PD-02、C-04b |

### SC-B05 回收站桥（未实现）

- Windows 回收站桥是 PD-06 的前置；**未实现前**，显式彻底删除不得声称「已移入回收站」。
- 实现须满足 H5（recycle 失败不永久删除；无法保证 → 禁用该类型原件删除）。

## 3. 与 C-01b / C-04b / C-08 的接口

- **C-01b**：SC-10a/10b（备份清单）、SC-30/31/33（删除边界）、SC-33（迁移）由本草案细化。
- **C-04b**：删除协议是 SC-B04 的协议层落地。
- **C-08**：备份恢复后的 Run 快照必须可读（快照不含上下文页内容——已知缺口）。

## 4. 冻结条件

1. 独立复核通过；
2. C-01b 已冻结；
3. `G-DELETE-CONTRACT` 关闭（删除语义）+ **`G-CONTRACT` 关闭**（AD-003 存储契约）；
4. `check.ps1` PASS。

## 5. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立草案：现状表 5 项、SC-B01…SC-B05 五条、与三份契约接口、冻结条件 | DSH |
