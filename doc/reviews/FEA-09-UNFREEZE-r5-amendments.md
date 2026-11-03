# FEA-09 UNFREEZE 修订提案 r5（最小语义冻结 + 实现设计委托）

状态：**PROPOSAL r5 — 待第四次/第五次独立复核**（2026-11-04）
作者：DSH（Lead / Architect / Integrator）；依据：r4 review（Codex 独立，`changes_requested` P0=0/P1=4/P2=3，reviewed_head `a7f636300`，SHA-256 `ae3a775b…`）、r3 review（已原字节归档：`doc/reviews/FEA-09-UNFREEZE-r3-review.md`，SHA-256 `75d89a73…`，reviewed_head `a7f636300`）。
**方法变更（DSH 架构裁决）**：r1–r4 把实现级细节（DTO 形状、调用方分派、状态机逐步、文件对象所有权）写入契约，导致每轮出现新的实现面 P1。r5 回到**契约应有的抽象层**：契约只冻结**可观察语义与不变量**；DTO/端口/状态机等实现设计集中在 `doc/handoffs/FEA-09-impl-design-I001-I005.md`，由**实现 Review** 独立审查，不进入冻结字节。r5 依据 r4 findings 逐项给出"语义条款 + 实现设计委托"，并明确不变量可测。

## 0. r4 findings 处置

| ID | 契约层处置（冻结） | 实现设计委托（不冻结） |
|---|---|---|
| R4-001 | V 行不得丢弃；可完整构造 domain Page 的行保持现有 `get_page/list_pages` 契约；不可完整构造但 V=true 的行必须以**只读降级投影**可观测（字段最少集：page_id/chapter_id/sort_order/source_mode/visibility_witness/source_hash?/original_ref?/width_px?/height_px?/original_available/integrity_status）；降级投影不参与写入、不伪造 provenance；未知 ID 仍 None。 | `PageRepository` 端口签名、PageView 字段类型、调用方分派与 DTO 映射表写入 impl-design；实现 Review 校验。 |
| R4-002 | wire `pages[]` 形状/正尺寸/可读页语义不变；`unavailable_pages` 为**可选 additive**，元素 `{page_id,reason_code,logical_order}`（logical_order=该页在 V 全集中的 0-based 序）；全不可读章节返回 `pages:[] + unavailable_pages` 全集；`initial_position` 仍指向逻辑顺序（含不可读页空位），首屏从该序起返回可读页；仅 RTyped 失败进入 unavailable，发布/内部错误不得归入。 | CoreClient 解析、UI-1 占位与 resume 交互写入 impl-design/UI-1 Task；实现 Review 校验。 |
| R4-003 | 加密 resolve 授权仅需：binding healthy + 恰一个 live 签名 grant G 满足 token/session/generation/expiry 且其 scope 的 source/version/entry/rendition 与 binding 一致；多于一个匹配 → DENIED；registry 撤销/G 撤销/EOF → fail-closed；binding/status/version 变化 → DENIED；不再要求 import-bound grant live。 | 候选选择代码位置、四维逐字段匹配函数、准入后读取前重验点写入 impl-design；实现 Review 校验。 |
| R4-004 | 威胁模型（冻结）：Host 私有目录写权限被攻破 = Host 身份被攻破，DPAPI 秘密已不可信；契约要求的防护是**降低误用/重放/路径注入**：token 仅 `[A-Za-z0-9_-]{22,64}`；路径必须为 `<DataRoot>/host/source-secrets/<token>.bin` 的规范绝对路径；祖先链不得 reparse；必须 `lstat` 普通文件 + 独占句柄打开 + 同句柄读取/零填充/删除；任何未通过上述验证的路径绝不读取/清理；启动孤儿清扫仅 Host 负责、仅本目录、仅 token 模式且超 TTL。 | 打开标志/identity 映射/句柄生命周期实现细节写入 impl-design；实现 Review 校验。 |
| R4-005 | 唯一决策顺序（冻结）：capability → binding → G/token/scope → 路径/对象规则 → claim → 读取/解密。错误优先级表冻结；冷却/计数规则冻结（仅解密失败计数、3 次、300s、成功重置、cache hit 不计数不消费、取消/超时/授权失败不计数）；claim 后进入不可跳过 finally 清理；Host 负责超时/取消侧文件清理，Core 只清理已验证并 claim 的对象。 | claim/finally 代码结构写入 impl-design；实现 Review 校验。 |
| R4-006 | C-04b **无 wire/字节改动**：删除目标与保护披露沿用既有协议；内容摘要现有字段/digest 覆盖不变（可读页内容摘要语义不变，unavailable 不新增字段）；unavailable 仅为 UI-1 展示需求（Task）。 | UI-1 Task 增展示要求；C-04b 消费方负责人 DSH 登记"无改动"依据。 |
| R4-007 | r3 review 已归档并记录 SHA-256/reviewed_head（见头部）；r4 已原字节归档。 | — |

## A 包（冻结条款）

### A1. C-05 v1.2（替换 §3.1 总定义；P1–P5/P7/P8 字节不变）

```text
V(p,t) ≡ (source_mode='managed' ∧ (V_artifact ∨ V_copy_original))
       ∨ (source_mode='referenced' ∧ V_ref)
V_artifact = 原 P1–P5（不受 pages 尺寸/完整性/created_at 约束）
V_copy_original = P1 ∧ integrity_status='complete' ∧ source_hash/managed_original_ref 非空
                  ∧ width>0 ∧ height>0 ∧ pages.created_at<=t
V_ref = 现有分支（字节不变）
witness 独立：任一为真即 V；R 与 V 分离：V 真不保证可读，R 失败 typed，不得隐藏 V。
```

- §3.2/§5 措辞同步（artifact 失败行仅描述 V_artifact；copy 独立）；反例 1–8 保留（修正 R 可读前提与两 witness 条件）。
- §8 变更记录 v1.2。

### A2. C-15 v1.1（冻结条款）

1. 正尺寸基线 `_LEGACY_COMPLETE_WHERE_POSITIVE`；v7 回填 SQL 改用该谓词（v7 未发布）；断言 1/3 按 r3 文本；零/负/NULL 尺寸行保持 incomplete 并进恢复清单。
2. 断言 2：expected=旧 artifact 集合 ∪ 旧正尺寸 copy 集合（固定 t/父级/顺序）；分支守恒；同一迁移事务连接；核验 get/list/pure projection 三者；非空资源禁跳 verifier；破坏 SQL/投影必失败；禁止调用 wire resolve/publish handler。
3. 断言 5：合格 original revision path 否则 managed_original_ref；无路径/缺失/不可读 → `SOURCE_MIGRATION_RESOURCE_UNVERIFIED`；不得隐藏 V 页；verifier 缺失且待验非空 → 失败。
4. §4.1 V=C-05 v1.2；§4.2 get/list 必须可见 V 全集（可读 Page、降级只读投影）；reader 纯投影同时产出可读/不可读两部分；新增 §4.4 最低投影字段集（R4-001 契约列）与"不得回写/不得伪造 provenance/未知 ID None"。
5. §2 v7 回填谓词修订已在 UNFREEZE 载体内登记；迁移版本号不变。

### A3. M2-C1 2.12-a（A 定稿，单独登记）

- managed resolve 选择：合格 current original revision → 否则 `pages.managed_original_ref`；稳定键不变。
- 资源不可变：同 resource_id 已发布摘要与当前选择不一致 → `INPUT_REVISION_CHANGED`（conflict，retryable=false），不替换；仅 artifact 缺失自愈（仍比较记录摘要）；并发发布单飞。
- Reader：可选 `unavailable_pages`（元素 field 见 R4-002）；`logical_order` 记录 V 全集序；`pages[]` 形状/正尺寸不变。
- 记录原指纹、diff、兼容矩阵、错误面、批准身份；不并入 17 pin；A 定稿字节作 B 基线。

## B 包（冻结条款）

### B1. C-16 v1.1

- 新能力 `source.resolve-secret/1`；Host 创建 secret 前检查；缺失/探测异常 → `CORE_CAPABILITY_MISSING`，不创建文件；旧 Core 忽略未知字段 → 加密 resolve typed REQUIRED。
- resolve 请求仅 `{page_id, secret_token?}`；token 无 path；路径来自签名 grant G。
- 授权/验证/消费/错误/清理语义按 R4-003/R4-004/R4-005 冻结条款；错误码复用 REQUIRED/INVALID；AES ZIP unsupported。
- 密码/token/path 全形式零泄漏；PDF raster 密码接缝；§10 变更记录。

### B2. M2-C1 2.12-b

- `ResolvePageResource {page_id, secret_token?}`；capability 强制配对；四象限兼容矩阵；B 基线=A 定稿字节；版本链唯一；不 bump minor（复核若要求则记录裁决）。

## C. 冻结流程

1. r5 → 新上下文独立复核（仅语义条款；实现设计委托不评价细节）；approved 且 P0/P1=0。
2. A 语义修订提交（C-05/C-15/M2-C1 2.12-a）→ 逐文件三指纹 → 已提交字节复核 → 仅元数据冻结提交（FROZEN 记录/矩阵/载体 §8/旧 pin 保留；check+pins）。
3. B 语义修订提交（C-16/M2-C1 2.12-b，基于 A 字节）→ 同流程。
4. 实现设计文档 `doc/handoffs/FEA-09-impl-design-I001-I005.md`（r5 同时提交）承载 DTO/端口/状态机细节；实现 Review 独立校验；实现前 DSH 在 Task 登记写域。
5. 释放 I001/I005 实现；各自测试矩阵（r3/r4 增量）+ 新独立实现复核 + DSH 集成 + EV 收敛。

## D. 实现设计委托（不冻结；引用文档）

`doc/handoffs/FEA-09-impl-design-I001-I005.md` 记录：PageRepository 端口与 PageView 类型、调用方分派表、DTO 映射、Reader 排序/resume 实现、fresh G 选择函数、secret 打开/claim/finally 代码结构、错误表逐条实现、测试矩阵映射。**任何实现细节变更不得违反本契约冻结条款**；违反由实现 Review 拒绝。

## E. 测试矩阵

A：V 全集可观测（可读 Page/降级投影混合、不丢行、未知 ID None）；witness 组合 1–8；typed R 不隐藏 V；迁移三路径同连接/固定 t/分支守恒/正尺寸基线/zero-size 恢复清单/verifier 缺失失败/破坏 SQL 必失败；Reader unavailable logical_order/全不可读/initial_position 规则；M2-C1 兼容。
B：四象限；token/路径规则（reparse/替换/大小写/../）；授权（fresh G、多匹配 DENIED、撤销/EOF fail-closed、binding 变化 DENIED）；claim/replay/并发准入/计数/冷却/cache hit/取消/超时/崩溃孤儿；无泄漏；PDF 接缝；Python/.NET/build/真实 IPC/check/17 pins，未运行 NOT_RUN。

## F. 不做

不改 referenced 分支/grant 四维 scope/import 状态机/WireLog 结构；不新增命令/错误码；不加依赖；不动 C-06 字节；不实现 UI；不补 ORIGINAL 行；不改协议 major/minor（除复核裁定）。
