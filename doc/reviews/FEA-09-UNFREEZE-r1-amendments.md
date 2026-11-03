# FEA-09 UNFREEZE 修订提案 r1（C-05 v1.2 / C-15 v1.1 / C-16 v1.1）

状态：**PROPOSAL — 待独立复核**（2026-11-03）
作者：DSH（Lead / Architect / Integrator）
依据：实现 Review r1 R1-I001/R1-I005；I001 独立裁决（`doc/reviews/FEA-09-I001-adjudication.md`，方案 B）；C-05 v1.1 / C-15 v1.0 / C-16 v1.0 FROZEN；C-15 §1/§4.1 现有断言；生产事实（正常导入不创建 ORIGINAL artifact；`application/rendering/service.py:232-238` 注释）。
载体：通过后扩写 `doc/reviews/CONTRACT-UNFREEZE-2026-11-03.md`（新增 §8，或新建 `CONTRACT-UNFREEZE-2026-11-04.md`），保留原字节与历史 §1–§7。
边界：**只修契约语义**（可见性等价分支、读路径投影、加密源 resolve 的短期 secret 通道）；不新增表/依赖/UI；不改变 referenced 分支、grant 四维 scope、密码 import 流程；不改既有冻结字节之外的条款。

## 0. 问题与裁决依据

### 0.1 R1-I001：managed 可见性缺 "Managed Copy original 等价物"
- 冻结 C-05 v1.1 §3.1：managed 分支 `V = V_artifact`（artifact/revision）。生产正常导入**不创建** ORIGINAL artifact（Page.managed_original_ref 即 immutable original）；按字面实现会让所有无 artifact 的导入页不可见（1298 基线级回归）。
- I001 独立裁决（Codex，未参与实现/Review）：选择 **B = UNFREEZE 澄清**。A（补 ORIGINAL 行 + 迁移回填）同样违反 C-15 §1（旧 artifact 集合守恒、旧 complete 无 artifact 行仍不可见），且需批量伪造 artifact/revision 身份。
- 结论：managed `V` 改为 `V_artifact ∨ V_copy_original`；artifact-only 旧页可见（投影/解析按 original revision）；columns-only 页可见（Managed Copy 即 original 等价物）；半写/零尺寸/父删/未来时间仍不可见。

### 0.2 R1-I005：加密源 resolve 无短期 secret 通道
- `resolve_page_resource` 现有冻结 payload 仅 `{page_id}`；加密源 import 完成后秘密已销毁，resolve 无法取得密码。
- I005 要求：Host 可为**单次读取**提供 fresh secret（一次性、销毁、不持久化），缺失/错密 typed；不得复用 StartImport 已销毁的 secret，不得把密码落盘/日志/wire 日志/receipt。
- 该扩展是 M2-C1 `ResolvePageResource` 的 additive 可选字段 + C-16 密码节扩展；属于契约修订，与 I001 同批 UNFREEZE。

## 1. C-05 v1.2 修订（精确文本）

### 1.1 头部
- `状态：**FROZEN v1.2（2026-11-04；v1.0 2026-11-01、v1.1 2026-11-03）** ...`
- 日期追加 `2026-11-04（v1.2 UNFREEZE）`
- 依据追加 `实现 Review r1 R1-I001 + 独立裁决（方案 B）`

### 1.2 §3.1 追加（替换 V 定义首段，保留 P1–P5/P7/P8 字节）

```text
V(p,t) ≡
  (pages.source_mode='managed'    ∧ V_managed(p,t))
∨ (pages.source_mode='referenced' ∧ V_ref(p,t))

V_managed(p,t) ≡ V_artifact(p,t) ∨ V_copy_original(p,t)

V_artifact(p,t) = §3 原 P1–P5（artifact/revision；不要求 pages.integrity_status，字节不变）
V_copy_original(p,t) =
  P1 ∧ pages.source_mode='managed' ∧ pages.integrity_status='complete'
  ∧ pages.source_hash IS NOT NULL ∧ pages.managed_original_ref IS NOT NULL
  ∧ pages.width > 0 ∧ pages.height > 0
  ∧ pages.created_at <= t
V_ref(p,t) = §3.1 现有引用分支（P1∧P7∧P8∧P5，字节不变）
```

- **witness 独立性**：`V_artifact` 与 `V_copy_original` 是两个独立 witness；一个不合格 artifact **不否定**合格的 copy-original witness，反之亦然；不得把 "artifact 优先" 误读为可见性短路。
- **资源选择（属 R，不属 V）**：managed 页读取优先当前 `original` artifact 的 valid current revision `managed_path`；无合格 original revision 时回退 `pages.managed_original_ref`（Managed Copy）。两者都须经受管根校验；缺失/越根/不可读 → typed 失败，不得回退任意路径。
- **投影**：get/list/projection 字段优先 pages 列；缺列时可用**合格** original revision 的 `file_hash/managed_path/width/height/size_bytes` 投影；不得伪造导入 provenance；仅有 clean/thumbnail 等 artifact 时不得冒充 original。
- **反例（冻结判据）**：
  ① artifact-only（导入列缺、有合格 original revision）→ 可见且可解析；
  ② columns-only（无任何 artifact、copy-original 完整）→ 可见且可读；
  ③ 合格 artifact 但 copy-original 缺列 → 可见（artifact witness），投影按 ④；
  ④ 半写（无 artifact 且 copy-original 不完整）、零/负尺寸、`created_at > t`、父级软删 → 不可见；
  ⑤ artifact 存在但 revision `integrity_status != 'valid'`/current 悬空/未来 revision/非 VISIBLE_TYPES → 不作为 witness（若 copy witness 合格仍可见）；
  ⑥ referenced 页不得经 managed 分支穿透。

### 1.3 §3.2 三谓词表更新
- `V(p,t)` 行改为 "C-05 v1.2 的模式分派（managed = `V_artifact ∨ V_copy_original`；referenced = 原引用分支）"。
- `R(p,t)` 行追加 managed 资源选择顺序（original revision → managed_original_ref）与 typed 失败要求。
- 失败语义新增一行：`managed artifact-only 页`：`R` 失败（资源缺失/越根）→ typed；`V` 仍真；不得显示空页或回退路径。

### 1.4 §8 变更记录新增
`2026-11-04 | v1.2 UNFREEZE：§3.1 增加 V_copy_original 等价分支、witness 独立性、投影/资源选择与反例判据；§3.2 V/R 更新。依据实现 Review r1 R1-I001 + 独立裁决 B；载体 CONTRACT-UNFREEZE...；待独立复核后重冻并重算 pin |`

## 2. C-15 v1.1 修订（精确文本）

### 2.1 头部/§0
- 状态 `FROZEN v1.1（2026-11-04；v1.0 2026-11-03）`；依据追加实现 Review r1/I001 裁决。
- §0 UNFREEZE 依赖追加：**C-05 v1.2**（managed 等价分支）与 **C-16 v1.1**（resolve 短期 secret）同批复核、重冻、pin 重算。

### 2.2 §1 迁移断言 2/5 更新
```text
2. 同一 t/父级条件下：
   expected_new_V = 旧 V_artifact(managed) ∪ 旧 copy-original complete 集合
   迁移后 C-05 v1.2 managed V 集合 == expected_new_V（逐 page_id 与顺序）
   且 artifact 分支、copy 分支分别守恒；不得要求 V 集合 == complete 集合；
   不得要求 V 集合 == 旧 V_artifact（copy witness 是新增合法来源）。
5. 旧 Managed 资源可读性：资源对象 = V 可见 managed 页解析到的 (original revision managed_path 若合格) 否则 pages.managed_original_ref；
   无任何可解析 original 路径的 V 页 → SOURCE_MIGRATION_RESOURCE_UNVERIFIED；缺失/不可读同上（回滚拒绝切换入口）。
   不得假定 V 页必有 managed_original_ref，也不得假定 V 页必有 artifact。
```
- 迁移验证必须调用**真实生产读路径**（`get_page/list_pages` 或 reader projection）核验 expected_new_V 一致，不能只比两份 SQL（R1-I001 要求；避免两 SQL 同空集的假通过）。

### 2.3 §4.1/§4.2 更新
- §4.1 `V(p,t)` 改为 C-05 v1.2 定义（managed = V_artifact ∨ V_copy_original）。
- §4.2 `get_page/list_pages` 改"V(p,t) per C-05 v1.2"；`resolve_page_resource` 行追加 managed 资源选择顺序与 referenced 加密源 secret 通道引用 C-16 v1.1；reader projection 行注明 artifact-only/columns-only 两类旧页投影规则。
- 新增 §4.4「Managed 投影与资源选择」：列优先、original revision 合法回填、禁伪 provenance、typed 失败；不得影响 referenced 分支。

### 2.4 变更记录
`2026-11-04 | v1.1 UNFREEZE：迁移断言 2/5 改为 V_artifact ∪ copy-original 且以真实生产读路径核验；§4.1 V 定义、§4.2 五读路径、新增 §4.4 投影/资源选择。依据 R1-I001 + 裁决 B；待独立复核/重冻/pin。 |`

## 3. C-16 v1.1 修订（精确文本）

### 3.1 头部
- `FROZEN v1.1（2026-11-04；v1.0 2026-11-03）`；依据追加 R1-I005。
- 协议面：不改 Core stdio 2.3 minor；`resolve_page_resource` 增加**可选**字段（additive，旧客户端字节不变）。

### 3.2 §3 追加「Resolve 读取的密码通道（R1-I005）」

```text
- 适用范围：source_mode='referenced' 且源为加密 ZIP/CBZ/PDF 的页 resolve。
- 请求：resolve_page_resource 可选 payload 字段 secret_ref（形状同 StartImportReferences：{token,path,expires_at}；仅 opaque 元数据，wire 不含明文）。
- Host 责任：每次 resolve 生成新的 32-byte token + <DataRoot>/host/source-secrets/<token>.bin（"NMSSR1\0"+DPAPI CurrentUser 密文；TTL ≤ 300s 且 ≤ 单次请求）；dispatch 前校验 grant 仍 live；失败/超时删除。
- Core 责任：从 secret_ref.path 一次性读取并立即零填充删除；只在局部变量持有密码并尽力清零；不得缓存/写入 DB/wire log/日志/receipt/证据；不得复用 import 阶段 secret。
- 缺失/过期/不可读 → SOURCE_PASSWORD_REQUIRED；解密失败/口令错误 → SOURCE_PASSWORD_INVALID；连续失败 ≥3 → 该页读取 fail-closed（不改变 import 的 3 次策略）。
- grant/scope/identity 校验顺序不变（先授权后 secret）；secret 只用于解密，不扩大授权范围；解密后仍只发布 decoded/re-encoded rendition（raw 禁止）。
- wire 脱敏：secret_ref 与 signing_key 一样在 WireLog/NDJSON/Host 日志/Ui 前脱敏（§7 既有规则扩展）。
```

### 3.3 §6 错误码
- 现有 `SOURCE_PASSWORD_REQUIRED`/`SOURCE_PASSWORD_INVALID` 复用（不新增码）；补充"resolve 路径同样映射"一行。

### 3.4 变更记录
`2026-11-04 | v1.1 UNFREEZE：§3 增加 resolve 加密源短期 secret 通道；错误码映射；M2-C1 1.9 additive 注记。依据 R1-I005；待独立复核/重冻/pin。 |`

## 4. M2-C1（rev 2.12 additive 注记，不改协议 major/minor）

- Revision history 追加 `2.12（2026-11-04，FEA-09 resolve 加密源 secret 通道）：ResolvePageResource 请求增加可选 secret_ref；其余字节/错误面不变；wire 脱敏沿用 §5.2。`
- `ResolvePageResource` 行更新请求列为 `{page_id, secret_ref?}`，并注明"可选；仅加密 referenced 源；旧客户端/旧 Core 无该字段行为不变"。
- M2-C1 不参与 FEA 契约 pin 审计；需 `check.ps1` 与文档一致性检查通过。

## 5. 重冻与实现计划（通过后执行）

1. 按本提案编辑 C-05/C-15/C-16 + M2-C1；扩写 UNFREEZE 载体（原字节保留，新增 §8 记录三项修订与复核身份）。
2. 更新 FROZEN 记录：C05 v1.2、C15 v1.1、C16 v1.1（sha256 重算/日期/复核 r1 approved）；`FEA-CONTRACT_FREEZE_MATRIX.md` 状态列；`verify_pins.ps1` 预期 17/17 PASS（pin 读取 FROZEN 记录）。
3. 实现 R1-I001（get/list 模式分派 + V_copy_original + artifact 投影 + 资源选择 + mapper；迁移验证走生产读路径 + 双向反例）+ R1-I005（resolve 可选 secret_ref、Host 侧 secret 签发/清理、M2-C1 wire、typed 错误、无泄漏测试）。
4. 新的独立实现复核（不得本会话自审）→ DSH 集成。

## 6. 请 Reviewer 回答

1. C-05 v1.2 `V_managed = V_artifact ∨ V_copy_original` 是否与 C-01b/ADJ-001、C-05 既有 P1–P5 冲突？witness 独立性/资源选择分离是否正确？
2. C-15 迁移断言 2/5 的新期望集合是否可判定、可回滚、无假阴/假阳？是否必须额外断言 production 读路径一致性（本提案已要求）？
3. C-16 resolve 可选 `secret_ref` 是否 additive 合规（协议 minor 不变）？密码生命周期/脱敏/typed 语义是否有漏洞？
4. M2-C1 rev 2.12 注记是否足够，还是必须独立 UNFREEZE/版本 bump？
5. 是否有应拆分为多个 CONTRACT 的问题（例如把 resolve secret 通道拆到独立契约）？推荐最小冻结批次与顺序。
6. 通过后实施 I001/I005 的风险点/测试必测清单。

## 7. 未包含（明确不做）

- 不补 ORIGINAL artifact 行、不迁移/复制用户资源；
- 不改 referenced 可见性分支、grant 四维 scope、import 异步状态机、WireLog 结构；
- 不改协议 major/minor、不新增命令/错误码、不增依赖；
- 不实现 UI 接线（FEA-09-UI-1）。
