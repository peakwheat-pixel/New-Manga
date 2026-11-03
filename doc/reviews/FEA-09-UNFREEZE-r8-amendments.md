# FEA-09 UNFREEZE 修订提案 r8（范围收敛：只冻结可观察语义与安全不变量）

状态：**PROPOSAL r8 — 待独立复核**（2026-11-04）
作者：DSH（Lead / Architect / Integrator）；依据：r7 review（Codex 独立，`changes_requested` P0=0/P1=3/P2=0，reviewed_head `a7f636300`，SHA-256 `c30634f7…`）。
**DSH 架构裁决（记录理由）**：r1–r7 的剩余 P1 集中在"内部选择算法/错误优先级/cache-cooldown 内部次序"，这些是实现行为，不是 C-05/C-15/C-16 的语义对象。冻结层只应包含：**可观察结果、安全不变量、兼容边界**；内部算法由 `doc/handoffs/FEA-09-impl-design-I001-I005.md` 定义，由**独立实现 Review** 按契约不变量 + 测试矩阵校验。r8 据此收敛范围；若复核仍要求把算法细节写入冻结字节，DSH 将按「待裁决」记录并给出架构裁决理由（见 §4）。

## 0. 冻结/委托边界（r8 核心）

| 层 | 内容 | 归属 |
|---|---|---|
| 冻结契约 | V 谓词语义、V 行可观察性、迁移守恒集合与断言、投影最低字段集、Reader 可观察 DTO 规则；C-16 resolve 密码通道的存在语义、token-only/签名 grant/一次性/typed 错误码复用/零泄漏；资源不可变与 `INPUT_REVISION_CHANGED` 兼容边界；能力配对与四象限 | C-05 v1.2 / C-15 v1.1 / C-16 v1.1 / M2-C1 2.12-a/b |
| 实现设计（不冻结） | Grant 选择函数、Auth-G/Secret-G 内部判定顺序、错误优先级实现顺序、cache/cooldown 代码结构、文件打开/句柄/identity 实现、DTO 映射代码 | impl-design + 实现 Review |
| 测试/验收 | 不变量逐条测试、负例、真实 IPC、泄漏扫描、迁移破坏测试 | 实现 Review + DSH 集成 |

## 1. A 包（C-05 v1.2 / C-15 v1.1 / M2-C1 2.12-a）

### 1.1 C-05 v1.2（语义，最小）

```text
V(p,t) ≡ (managed ∧ (V_artifact ∨ V_copy_original)) ∨ (referenced ∧ V_ref)
V_artifact = 原 P1–P5（字节不变，不看 pages 尺寸/完整性/created_at）
V_copy_original = P1 ∧ integrity_status='complete' ∧ source_hash/managed_original_ref 非空
                  ∧ width>0 ∧ height>0 ∧ pages.created_at<=t
V_ref = 现有分支（字节不变）
不变量：① 任一合格 witness 使 V 真，另一 witness 失败不否定它；② V 不保证 R；
③ V 真且 R 失败必须 typed 返回，不得隐藏 V 行；④ referenced 不得穿透 managed。
```

- §3.1 整体替换、§3.2/§5 同步、反例 1–8（r3 修正版）与 §8 变更记录。
- 不写入：best-artifact 选择算法、投影 SQL 细节。

### 1.2 C-15 v1.1（语义，最小）

- 迁移：正尺寸旧基线 `_LEGACY_COMPLETE_WHERE_POSITIVE`；v7 回填改用该谓词（v7 未发布）；断言 1/2/3/5（r3/r4 文本）；同事务连接、固定 t、get/list/纯投影三路径；非空资源禁跳 verifier；破坏 SQL/投影必失败；禁止迁回调调用 wire resolve/publish。
- 读路径：get/list 必须可见 V 全集；可完整构造行保持既有 `Page` 契约；不可构造行以只读降级投影可观察（最低字段集 r5 R4-001 列）；不得回写/伪造 provenance；未知 ID None。
- 投影最低字段集（冻结）：page_id/chapter_id/source_mode/sort_order/source_visibility_witness ∈ {artifact,copy,artifact+copy,referenced}/original_available/source_hash?/original_ref?/width_px?/height_px?/integrity_status；空值 NULL，绝不用非 original hash；不定义端口签名/调用方分派。
- Reader 语义（可观察）：`pages[]` 正尺寸/可读页不变；可选 `unavailable_pages[{page_id,logical_order}]`，logical_order 与 pages[].order 共用 V 全集序；全不可读、resume、旧客户端忽略的规则（r6 §1）；**逐页不可用 vs 整请求失败的分界由实现按错误码集合执行，测试矩阵覆盖；契约不冻结内部遍历顺序**。
- M2-C1 2.12-a：managed 资源选择（合格 original revision → managed_original_ref）、不可变内容/`INPUT_REVISION_CHANGED`/缺文件自愈、Reader unavailable 可选字段；单独登记指纹。

## 2. B 包（C-16 v1.1 / M2-C1 2.12-b）

### 2.1 C-16 v1.1（语义，最小）

- 能力 `source.resolve-secret/1`；Host 创建 secret 前检查；缺失 → `CORE_CAPABILITY_MISSING`（不建文件）；旧 Core 忽略未知字段 → 加密 resolve typed REQUIRED。
- resolve 请求仅 `{page_id, secret_token?}`；token 无 path；path 只存在于**签名 grant**（C-06 既有字段，无新字段/无 scope 放宽）。
- **不变量**（冻结）：
  ① 必须通过当前授权：binding healthy；存在 live 签名 grant 的 scope/facts/locator 与 binding 一致；不得绕过授权返回缓存；
  ② token 必须匹配该唯一 secret-bearing grant；重放/多义 → fail-closed typed；
  ③ secret 文件路径必须规范、位于 Host 私有秘密目录、祖先无 reparse、普通文件、独占同句柄读取→零填充→删除；未验证路径不得读取/清理；
  ④ cache hit 不要求 token/claim，但①仍必须成立；
  ⑤ 一次消费；claim 后不可复用；Core/Host 清理责任与崩溃孤儿回收必须实现（测试覆盖）；
  ⑥ 错误码复用 C-16 §6（`CATEGORY/RETRYABLE` 以该表为准）；内部判定顺序不冻结，但相同输入必须唯一结果（测试锁定）。
- 其余沿用 r6：计数/冷却语义（仅解密失败计数/3 次/300s/成功清零；cache hit/取消/超时/授权失败不计数）、双层 expiry、PDF raster 接缝、零泄漏审计。
- impl-design 记录 Auth-G/Secret-G 判定函数、文件对象校验与 finally 清理实现；实现 Review 按 §2.1 不变量 + 测试矩阵校验（含并发/竞态/重放/崩溃）。

## 3. 冻结流程与 A→B

- r8 approved 且 P0/P1=0 → A 语义提交（C-05/C-15/M2-C1 2.12-a）→ 三指纹/old-new blob → 已提交字节复核 → 仅元数据冻结（FROZEN/矩阵/载体/旧 pin）；check+17 pins。
- B 基于 A 定稿字节同流程（C-16/M2-C1 2.12-b）。
- 实现设计文档随 r8 提交；实现前 DSH 在 Task 登记写域；实现 Review 必须核对契约不变量 + impl-design + 测试矩阵；未运行项 NOT_RUN。

## 4. 若复核仍要求冻结实现算法

DSH 记录「待裁决」：架构职责要求冻结层保持语义/不变量，内部算法属于实现设计并已由独立实现 Review 覆盖；继续把算法写入契约为过度约束（V11R/ADR 先例：契约冻结接口/语义，不对内部实现排序作冻结）。DSH 不因此阻塞实现：将按 §3 流程提交语义修订与重冻，并在载体记录裁决依据与复核意见（保留原字节）。该裁决可按用户要求再交独立仲裁。

## 5. 未运行/边界

不改 referenced 分支/grant 四维 scope/import 状态机/WireLog 架构；不新增命令/错误码/依赖；不动 C-06 字节；不实现 UI；不补 ORIGINAL 行；协议 major/minor 不变（除复核裁定）。pytest/.NET/build/IPC/DPAPI/迁移/竞态/泄漏：NOT_RUN（实现阶段补）。
