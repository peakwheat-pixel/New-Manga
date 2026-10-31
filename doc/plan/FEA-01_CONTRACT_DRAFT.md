# FEA-01 契约变更清单（草案）

状态：**DRAFT / 未冻结 / 不释放实现 Task**
日期：2026-11-01
作者：DSH（Lead / Architect / Integrator）
依据：FEA-00 r1（[FEA-00-dsh-r1](../reviews/FEA-00-dsh-r1.md) §5.4）、r2 技术复核（[FEA-00-dsh-r2-technical-recheck](../reviews/FEA-00-dsh-r2-technical-recheck.md)）、r7 独立 Review（[FEA-00-dsh-r7](../reviews/FEA-00-dsh-r7.md)，`changes_requested`）、**r8 独立 Review（[FEA-00-dsh-r8](../reviews/FEA-00-dsh-r8.md)，`approved`：0 P0 / 0 P1 / 9 P2）**、方案 r4（`doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md` @ `74a772167`，LF sha256 `8895aebe…`）、[AD-003](../AD-003_REFERENCED_SOURCE_ARCHITECTURE.md)、[ADJ-001](../contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md)

**边界声明**：本文件是变更清单草案，**不是 ADR、不是冻结契约、不是 Task 释放，也不构成实现授权**。其中任何条目在方案修订、独立复审通过（新 hash）与用户裁决完成前**不得实施**；`check.ps1 PASS` 不构成架构语义证据。

---

## 1. 冻结顺序（门禁链）

```
用户裁决（§3 待决项）
  → 方案修订（R7-01 / R7-02 等）
  → 新 hash 独立复审通过          ← 2026-11-01 已完成（r8 `approved`，`74a772167`）
  → C-01…C-12 逐条冻结
  → FEA-01 冻结
  → Task 释放
  → 实现
```

任一门禁未过，**Source 线（FEA-08/09/11/12/13）保持 BLOCKED**。

### 1.1 r7 结论摘要（2026-11-01）

- r1 的 2 项 P0（F-01/F-02）**不再列为 P0**：销案条件已由方案之外的 AD-003（`G-ADR: SATISFIED`）与 ADJ-001（`G-DELETE-SEMANTICS: SATISFIED`）满足；r1 的 14 项 P1 在文本层面全部已处置。
- 仍为 `changes_requested`，卡在两处 P1：
  - **R7-01**：方案未同步 AD-003/ADJ-001，仍把已完成的裁决写成"待记录/待裁定"（D01/D07 对象过期）；
  - **R7-02**：显式彻底删除未映射 ADJ-001 的 PD-01–PD-10（无 Core 只读预览、`inventory_digest` 绑定、确认前零变化门禁）。
- 处置：转方案作者（Codex）修订 → 新 SHA-256 上重新 Appointment 复审 → 再进入契约冻结。

### 1.2 r8 结论摘要（2026-11-01，方案 r4）

- **`approved`（0 P0 / 0 P1 / 9 P2）**：R7-01 / R7-02 均已实质处置，R7-03–R7-08 全部有处置（R7-05/07/08 无残留）。
- 本轮 9 条 P2 不阻断：R8-01/02（§13.3 基线/指令混写）、R8-03（候选名未标「候选」）、R8-04（PD-01 漏 `BOOK_BUSY`）、R8-05（F09 锚点失效）、R8-06/07（旧口径残留）、R8-08（56/56 只对 r3）、R8-09（两份权威文档自身 `G-REVIEW` 未获批）。
- **approved 不等于契约冻结**：下一步仍是 C-01…C-12 逐条冻结（本清单的工作面）。

---

## 2. 变更包清单

| ID | 变更包 | 涉及权威/共享面 | 必须冻结的内容 | 关联 finding | 决策状态 |
|---|---|---|---|---|---|
| **C-01a** | 架构默认存储语义（记录） | AD-003、AD-002 顶部横幅 | 用户 ADR 记录本身（Decision authority: User） | F-01 | **已满足（AD-003 `G-ADR: SATISFIED`）** |
| **C-01b** | 存储契约冻结 | AD-002 责任表与哨兵、AGENTS.md、下游五项反转清单 | Managed Copy → ReferencedSource 的契约文本；旧 Managed 双读；备份完整性/回收站触原件/迁移方向/资源通道信任根/删除授权五项反转 | F-01 | **OPEN（待冻结）** |
| **C-01c** | 检查器哨兵口径 | `tools/governance/check.ps1:261-275` 双哨兵断言面 | 已实现并经 r6c `approved`；方案 D01 应**引用**而非重述 | F-01 | **已实现** |
| **C-02** | V11R 契约条款级修订单 | `V11R_AVALONIA_CONTRACT.md` §1.1/§1.2/§2.2/§2.3/§2.4/§3/§4/§6.1/§6.3 | 逐条「现行文本 → 修订文本/适用域 → 审查判据 → 例外登记」；重申 R-03（Fluent = 视觉风格，不是 FluentAvalonia 依赖）；`nm.fluent.visual/1` 的定位与校验器归属；**三处口径不一（§4.1 vs §15.2 九条）以逐条修订单为准（R7-08）** | F-03、F-35、F-36、R7-08 | 成立（草案，待冻结） |
| **C-03** | 外观持久化与字段迁移 | `ThemeSettings`/`LayoutProfile`/`IThemeService`/`IThemePersistence`、新 `presentation-settings.json` | 唯一写者（建议 `presentation-settings.json` 单点，ThemeEngine 降为 sink-only）；旧文件停止写的时点；字段迁移矩阵（保留/迁 Core 按书偏好/迁 scale schema/废弃）；动效三态与分类模型 | F-06、F-16、F-36 | 成立（草案，待冻结） |
| **C-04a** | 删除语义（已冻结） | ADJ-001 PD-01–PD-10 | 语义 = 已冻结；方案 §9 应改为**引用**而非重述 | F-02 | **已满足（ADJ-001 `G-DELETE-SEMANTICS: SATISFIED`）** |
| **C-04b** | 删除协议字段/码表 | `M2-C1 §5.11`、`PreviewPermanentDeleteBooks`、`inventory_digest` | 只读预览、确认绑定摘要、确认前零变化门禁的字段与错误码 | F-02 | **D07 待冻结（先核 ADJ-001 §5/§6.1）** |
| **C-04c** | PD→方案映射 | 方案 §9.1/§9.2、FEA-12-CORE AC | PD-01–PD-10 逐条映射到方案流程与 AC | R7-02 | **已由 r4 §9.1 覆盖（r8 复核十个编号全部落位，F-02 占位 0 命中）；待 C-04b 字段冻结后闭合** |
| **C-05** | 页可见性/完整性谓词 | `src/infrastructure/sqlite/library.py` 读面、`core_service` 页解析 | 新增显式完整性标记，区分「崩溃半写」与「引用模式合法无副本」；5 处读路径改造；不削弱崩溃安全不变量 | F-11 | 成立 |
| **C-06** | Source 授权面 | 导入/资源控制面、Host issuer、新 `SourceReadService`、`SourceAccessRegistry` | grant 种类（一次性导入 ≤5min / 可续租 `source-read`，不可混用）；续租/撤销/过期；递归授权根模型；registry 持久化与 generation；读取预算；`ManagedRootTrust` 每根每代等价快照 | F-12、F-15、F-31 | 成立 |
| **C-07** | 应用端口与兼容面 | `IHostController`/`IRunController`/CoreClient/Registry/Dispatcher/命令清册 | 由代码生成的方法清单（替换冻结文档的「36」口径）；request-scoped error；能力握手；增量为准；旧签名不变的可验证基线 | F-22、F-25 | 成立（委托 FEA-01 生成清单） |
| **C-08** | Run 快照与幂等 | `IRunController`、PreparedRun、配置快照、凭据引用、任务投影 | preview 与发送同源；不可变内容 pin；retry 是否复用 source run 快照；控制 pending 状态；真实完成口径；断线 receipt | F-07、F-08、F-17、F-26 | 成立 |
| **C-09** | 删除/备份/迁移 | Trash/purge/GC、`nmbak`/`migrator`、Windows 回收站桥 | 软删/恢复/TrashEntry 新命令面；三路径统一 ProtectionPolicy；备份覆盖清单（`settings/*.json`、`catalog.sqlite` 现状缺失项）；`backup/2`；`DatabaseId`；自动备份调度归属；独占写锁与 pin | F-13、F-14、F-30、F-32 | 成立（D07 表述待更新） |
| **C-10** | 交互契约与需求追溯 | 新交付物（FEA-01 附件） | 手势优先级与移动阈值、快捷键作用域、可编辑态、draft owner 规则；「需求→能力→Task→AC→证据」矩阵。**手势阈值 / 可编辑态仍缺（R7-07）** | F-10、F-18、F-39、R7-07 | **部分**（追溯矩阵 / draft owner / 快捷键成立） |
| **C-11** | 候选 Task 表补列与前置 Gate | 方案 §12 | 每行补 `write_scopes`/`shared-file owner`/验证等级/`evidence_dir`/per-task 回退/需求映射；H1/H2/H3/H4b 写成候选前置 Gate；补「Fluent 四页设计冻结」前置 Task（F-04 指出该基线不存在） | F-04、F-05、F-41、F-42、R7-03 | 成立（席位列口径待更新） |
| **C-12** | 治理检查器定位 | `tools/governance/check.ps1:261-275` | 明确它**不检测**「保留哨兵 + 覆盖性决策」，也**不扫描** `doc/design/**`；断言面以 r6c 批准的实现为准；不得作为架构一致性证据 | F-01 | **定向正确、文本需更新（并入 R7-01）** |

**说明**：「成立」= 方案已按 r1 要求给出草案，等待冻结；「缺失/部分」= 方案文本尚未覆盖，需修订；「已满足」= 方案之外的权威文档已满足，方案只需引用。

---

## 3. 需你拍板的裁决项

来源：r1 §5.3；已由 AD-003/ADJ-001 覆盖的标注「已记录」。

| # | 取舍 | 现状/冲突 | 建议默认 | 状态 |
|---|---|---|---|---|
| U-01 | 是否把 AD-002 默认存储语义改为 ReferencedSource（F-01） | AD-002 `Decision authority: User`；AGENTS.md 只允许落在该架构 | 需用户明确裁决（ADR） | **已记录（AD-003）；契约冻结待办（C-01b）** |
| U-02 | 用户「彻底删除」是否解除 Lock/current/pinned（F-02） | 冻结 `M2-C1 §5.11.2` = 移除；方案 = 拒绝 | 建议区分：用户显式彻底删除可解除（沿用冻结语义），仅回收站到期 GC 阻受保护项 | **已由 ADJ-001 冻结（PD-01–PD-10）；待你确认采用冻结语义**（决定 C-04b 字段/门禁方向） |
| U-03 | 首阶段浮窗是否允许与主窗同时编辑同一区域（F-10） | 方案只读镜像；需求暗示可编辑 | 建议按 `(SessionId, RegionId)` draft owner + 分字段并发；否则明确降级只读 | **待你裁决** |
| U-04 | Fluent 是否豁免 V11R §2.2 圆角/阴影/模糊禁令（F-03） | V11R 硬规则 + R-14 唯一例外清单；需求要求亚克力/层次 | DSH 起草 per-scheme 例外登记（与 R-14 同构）并经用户确认 | **待你裁决** |
| U-05 | 阅读器翻页效果/动效分类是否纳入首阶段（F-36/F-39） | 需求要求；方案无归属 | 纳入，但首阶段可降级为跟随系统 + 单一强度 | **待你裁决** |
| U-06 | 引用原件后是否承诺完全离线阅读/重建 | 方案默认仅引用 + 有限缓存 | 保持方案默认；离线另定存储与空间预算 | **待你裁决** |
| U-07 | 外部卷支持范围（网络盘/可移动盘/云占位） | 方案列了待定 | 先验证本地 NTFS；不可证一致读取的卷显式受限 | **待你裁决** |
| U-08 | 凭据与字体备份范围 | 方案默认不备份密钥 | 保持默认；恢复时要求重新授权 | **待你裁决** |

---

## 4. 治理缺口登记（r7 与 r2 共同指出）

| # | 缺口 | 处置 |
|---|---|---|
| G-01 | 方案 §16 引用未落库的会话级审查（`a66dc75c`、`759f940f`），`doc/reviews/` 无对应产物 | **已处置（r4 §16 移除两处引用，改为指向 `FEA-00-dsh-r2-technical-recheck`，并声明会话级口头复核不作为审查证据）** |
| G-02 | `FEA-00-dsh-r7` Appointment 登记缺失 | **已补**：`doc/reviews/FEA-00-dsh-r7-appointment.md` |
| G-03 | `doc/00_INDEX.md` 未登记 r7 报告与 Appointment | **已补**（r7 与 r8 均已登记） |

---

## 5. 与现役主线的关系

- **SAFETY-6 不依赖本清单**：其 AC1（进度刷新）/AC2（derived 结论）落在数据安全修复，写域为 `apps/desktop-avalonia/**`、`src/**`、`scripts/**`，与本清单的契约面（AD-002/V11R/ThemeSettings/命令面）不重叠。
- **本清单冻结后也不回滚 SAFETY-6**：ApplicationCore 抽取后，进度刷新逻辑仍是其输入之一。
- **治理指针串行写**：`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md` 由 DSH 单点更新，避免与并行执行体冲突。

---

## 6. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立草案；按 r1 §5.4 收录 C-01…C-12 与 U-01…U-08；标注 AD-003/ADJ-001 已覆盖项 | DSH |
| 2026-11-01 | 吸收 FEA-00 r7 独立 Review（`changes_requested`）：C-01 → a/b/c、C-04 → a/b/c，C-10 标「部分」、C-12 补断言面；冻结链加入「修订后新 hash 复审」；登记 G-01…G-03 | DSH |
| 2026-11-01 | 吸收 FEA-00 r8 独立 Review（`approved`，0 P0 / 0 P1 / 9 P2）：更新依据为方案 r4（`74a772167`）；C-04c 改为已覆盖；G-01/G-03 关闭；U-02 标注 ADJ-001 已冻结；冻结链标注「新 hash 复审」已完成 | DSH |
