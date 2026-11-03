# FEA-09 UNFREEZE 修订提案 r2（A 包：C-05 v1.2 / C-15 v1.1；B 包：C-16 v1.1 / M2-C1 rev 2.12）

状态：**PROPOSAL r2 — 待独立复核（r1 changes_requested 处置稿）**（2026-11-04）
作者：DSH；r1 → r2 依据：`doc/reviews/FEA-09-UNFREEZE-r1-review.md`（Codex 独立，`changes_requested` P0=0/P1=6/P2=3，reviewed_head `68a46dfe5`，SHA-256 `9fd8efb6…`）。
修订方式：**两包分批复核/冻结**；每包固定 reviewed bytes → 独立复核 approved（P0/P1=0）→ 冻结提交（三种指纹、§1B 差异、旧 pin 保留）。r1 提案字节保留为历史。

## 0. r1 处置（U-001…U-009）

| ID | 处置 |
|---|---|
| U-001 | 接受：负例仅当 **两个 witness 都失败**；artifact witness 不受 page 尺寸/时间约束（只看 P1/P2–P5），copy witness 才看 page 完整列与 `created_at≤t`；旧失败表/§4.3 标注仅适用 copy 分支。 |
| U-002 | 接受：冻结 artifact-witness 只读投影——共享 Page 扩域 `original_available: bool`；`managed_original_ref` 可为 NULL、width/height 可为 0 **仅当** `original_available=False`；get/list/projection 必须返回该行（typed 不可读），禁止静默过滤/伪造 provenance；读取/解析 typed 失败。DSH 在 FEA-09 allowed_paths 增 `src/domain/pages/entities.py` 并记录。 |
| U-003 | 接受：C-15 断言 3 同步改写（旧 complete 无 artifact 页经 copy witness 可见 ≠ "仍不可见"）；完整性守恒与可见性扩展分开陈述。 |
| U-004 | 接受：resolve `secret_ref` 必须与**同一页绑定的有效签名 grant** 的 secret 严格匹配；Host 每次 resolve 前用 `RegisterSourceReadGrant` 铸造 fresh grant（same scope/roots/facts/locator + 新 secret_ref）；Core 验证 grant/scope/identity/expiry/token 后才消费，拒绝任意路径。 |
| U-005 | 接受：冻结密码状态机（计数键、原子性、3 次锁定码/category/retryable/cooldown、cache hit 不消费秘密、所有终止分支清理责任、PDF raster 密码接缝）。 |
| U-006 | 接受：新增能力 `source.resolve-secret/1`；Host 铸造 secret 前校验，缺失 → `CORE_CAPABILITY_MISSING` 并删除 secret；补旧/新 Host×Core 四象限兼容表；M2-C1 独立 amendment 登记（不并入 17 pin）。 |
| U-007 | 接受：迁移验证以**同一事务连接**构造 repository，固定 t/排序，核验 get/list/reader projection 三者；非空资源禁止跳过 verifier；破坏 SQL 或 mapper 必须失败。 |
| U-008 | 接受：删除 "1298 页" 误导表述；反例编号纠正；M2-C1 版本统一为 rev 2.12。 |
| U-009 | 接受：冻结流程补三种指纹（工作树 SHA-256、blob ID、blob SHA-256）、§1B 只含元数据差异、历史 pin/Review 原字节保留。 |

## A 包：C-05 v1.2 + C-15 v1.1（I001）

### A1. C-05 v1.2 精确条款

**§3.1 追加（插入 P1–P5、P7/P8 之后；P1–P5 与 referenced 分支字节不变）**

```text
V(p,t) ≡ (p.source_mode='managed' ∧ V_managed(p,t))
       ∨ (p.source_mode='referenced' ∧ V_ref(p,t))

V_managed(p,t) ≡ V_artifact(p,t) ∨ V_copy_original(p,t)
V_artifact(p,t) = §3 P1–P5（不要求 pages.integrity_status / 尺寸；witness 只看 artifact 与 revision 时间）
V_copy_original(p,t) =
  P1 ∧ p.source_mode='managed' ∧ p.integrity_status='complete'
  ∧ p.source_hash IS NOT NULL ∧ p.managed_original_ref IS NOT NULL
  ∧ p.width > 0 ∧ p.height > 0 ∧ p.created_at <= t
V_ref(p,t) = 现有 P1∧P7∧P8∧P5（字节不变）
```

- **witness 独立性**：任一合格 witness 使 `V` 真；一个 witness 失败**不否定**另一个；`V` 不保证 original 可读。
- **R 与资源选择**（managed）：优先当前 `original` artifact 的 `integrity_status='valid'` revision；否则回退 `pages.managed_original_ref`；两者都经受管根校验；缺失/越根/不可读 → typed 失败（`SOURCE_ENTRY_MISSING`/内部资源错误），不得回退任意路径，不得因 R 失败隐藏 V。
- **投影形状（U-002 冻结）**：
  - 完整列优先；缺列时可用**合格 original revision** 的 `file_hash/managed_path/width/height/size_bytes` 回填（只读投影，不写回、不伪造 provenance）。
  - 仅有非 original artifact（thumbnail/clean 等）且无 `managed_original_ref`/尺寸：`V` 真、行必须出现在 get/list/projection，标记 `original_available=false`（共享 Page 扩域；`managed_original_ref=NULL`、尺寸可 0）；resolve typed `SOURCE_ENTRY_MISSING`。
  - 禁止静默丢行；多 artifact 去重按 page 粒度。
- **反例矩阵（冻结）**：

| # | artifact witness | copy witness | 期望 |
|---|---|---|---|
| 1 | 合格 original revision | 列不完整 | V 真；投影按 original 回填；R 可读 |
| 2 | 无 | copy 完整 | V 真；R 可读 |
| 3 | 合格非 original（thumbnail 等） | 失败 | V 真；`original_available=false`；R typed 失败 |
| 4 | 失败/无 | 失败 | V 假（含零/负尺寸、`created_at>t`、半写、父级软删） |
| 5 | 失效 artifact + copy 成功 | 成功 | V 真（witness 独立） |
| 6 | 两 witness 均成功 | 成功 | V 真，不重复页 |
| 7 | artifact revision 未来/非 valid/NULL/dangling/非 VISIBLE_TYPES | 失败 | artifact witness 失败；copy 独立判定 |
| 8 | referenced 页存在 artifact | — | 不得经 managed 分支穿透 |

**§5 失败语义标注**：现有"current_revision NULL/缺失/integrity"行仅描述 `V_artifact`；copy witness 独立；`V` 真而 R 失败时 typed、不得显示空页/回退路径。

**§8 变更记录**：`2026-11-04 | v1.2 UNFREEZE：V_managed=V_artifact∨V_copy_original、witness 独立性、投影/资源选择/反例矩阵（R1-I001；裁决 B；独立复核 r2）。`

### A2. C-15 v1.1 精确条款

**§1 断言 2**：

```text
expected = 旧 artifact 可见集合(managed) ∪ 旧 copy-original 集合（旧列：source_hash/managed_original_ref 非空、width>0、height>0、父级未删、created_at<=t）
迁移后 managed V 集合（逐 page_id/顺序）= expected；artifact 分支与 copy 分支分别守恒；
禁止要求 V=complete，也禁止要求 V=旧 artifact 集合；
验证执行：同一迁移事务连接构造 repository，固定 t，核验 get_page/list_pages/reader_projection 三者与 expected 一致；非空集合时 verifier 不得跳过；人为破坏任一查询/mapper 必须验证失败。
```

**§1 断言 3**：改为"旧 `_COMPLETE_PAGE_WHERE` 集合 = 迁移后 managed `is_complete_page` 集合（逐 page_id）；旧 complete 无 artifact 页保持 complete 且经 copy witness 可见；旧 complete 但父级软删页保持 complete 且不可见；不得把 incomplete 提升 complete。完整性守恒与可见性扩展分开断言。"

**§1 断言 5**：资源对象 = V 可见 managed 页解析到的 (合格 original revision `managed_path` 否则 `pages.managed_original_ref`)；无路径 → `SOURCE_MIGRATION_RESOURCE_UNVERIFIED`；缺失/不可读同上；**不得隐藏 V 页**；非空待验资源必须注入 verifier（禁止 None 跳过）。

**§4.1/4.2/新增 4.4**：V 用 C-05 v1.2；五读路径注明 get/list/projection 必须支持 artifact-witness 只读投影（`original_available=false`）；resolve managed 资源选择与 typed 失败；reader projection 对两类旧页均返回行。

**表头/§0/变更记录**：C-15 v1.1；记录 r2 复核与 pin 重算。

### A3. M2-C1（A 包同步注记，不并入 17 pin）

- rev 2.12 注记：managed 页 `page-original-{page_id}` 资源选择=合格 current original revision → 否则 Page Managed Copy；稳定键/first-publish-wins 不变；当选中 revision 的 `file_hash` 与已发布 artifact 摘要不一致时，允许同键重发布（自愈），不得返回旧内容。
- 登记原指纹、条款 diff、兼容矩阵、错误面、批准身份；不声称 17/17 覆盖 M2-C1。
- 本注记**不改协议 minor**（只改实现选择规则，不改请求/响应字节）。

## B 包：C-16 v1.1 + M2-C1 rev 2.12-b（I005）

### B1. C-16 v1.1 精确条款

**§0 能力**：新增 capability `source.resolve-secret/1`；Core `core.ping.capabilities` 追加。Host 在铸造/发送 resolve secret 前检查；缺失 → `CORE_CAPABILITY_MISSING`（不得发送 secret，立即删除本地 secret 文件）。旧 Core 行为：忽略未知可选字段，加密源 resolve 仍 typed `SOURCE_PASSWORD_REQUIRED`（兼容矩阵见 §B3）。

**§3 追加「Resolve 密码通道」**：

```text
- 前置：Host 每次 resolve 加密 referenced 页前，用 RegisterSourceReadGrant 铸造 fresh grant：
  同一 registry/generation/roots/container facts/entries（scope 不变）、新 grant_id、新 secret_ref（32-byte token + path + expires_at≤300s 且≤单次请求）；
  Host 校验 Core capability source.resolve-secret/1 后才创建 secret 文件；失败/超时/拒绝立即删除。
- resolve_page_resource 可选 payload 字段 secret_ref（仅 {token,path,expires_at} 元数据，wire 无明文）。
- Core 验证顺序：binding healthy → grant(bound source/version/entry) live → 新 secret grant live 且其 signed secret_ref 与 payload 完全一致 → scope/roots/identity 与 binding 源一致（container digest+volume+file+locator）→ 才允许读取并把 secret 一次性消费。
  不接受任何未绑定 grant 的 secret_ref，不接受任意路径；secret 只用于解密，不扩大授权。
- 消费与清理：Core 读取后立即零填充删除文件（失败也删）；密码只在局部变量，用后清零；cache hit 且无需解码时**不要求 secret**；若请求携带 secret，Core 必须验证并删除该文件（不得残留）。
- 失败计数：键=(page_id, accepted_source_version)，进程内原子计数；连续 3 次失败 → 返回 SOURCE_PASSWORD_INVALID（category=validation，retryable=false），冷却 300s 后重置；成功即重置；并发请求在锁内计数；撤销/EOF/超时/取消/进程崩溃时 Host 与 Core 双端清理各自 secret。
- 错误映射：缺失/过期/token 不匹配/文件不可读 → SOURCE_PASSWORD_REQUIRED；DPAPI/口令错误或锁定 → SOURCE_PASSWORD_INVALID；AES ZIP → SOURCE_FORMAT_UNSUPPORTED（不请求密码）。
- PDF raster：document_raster.open(data, password=...) 接缝扩展；密码仅传 adapter 局部。
- 脱敏：secret_ref/signing_key/password 在 WireLog.Frames/NDJSON、Host/Core 日志、receipt、UI、verification 证据零出现；审计含 hex/base64/url-encoded 形式。
```

**§6 错误码**：复用两码；补 resolve 映射与锁定时 `retryable=false`。**§7**：脱敏规则扩展至 resolve secret。**§10 变更记录**：v1.1 记录。

### B2. M2-C1 rev 2.12-b

- `ResolvePageResource` 请求 `{page_id, secret_ref?}`；可选字段仅新 Core 识别；登记兼容矩阵/错误面/指纹；不 bump 协议 minor（保留 2.3），但 Host 必须先协商 `source.resolve-secret/1`。
- 若复核认为已有命令面变更必须 bump，则备选：保留 2.3 + capability 门禁（推荐），并在载体中记录裁决依据。

### B3. 四象限兼容矩阵（冻结）

| Host\Core | 旧 Core（无 capability） | 新 Core（有 capability） |
|---|---|---|
| 旧 Host | 现状：加密 resolve typed REQUIRED（无 secret） | 现状 + 新能力未使用；行为不变 |
| 新 Host | 检测 capability 缺失 → typed `CORE_CAPABILITY_MISSING`，删除 secret，不发送 | 加密 resolve 全链；非加密/非 referenced 页字节不变 |

## C. 冻结流程与交付（两包各自执行）

1. 本 r2 精确条款 → 独立复核（新上下文）；approved 且 P0/P1=0 才继续。
2. 语义修订提交：仅改契约正文（C-05/C-15 或 C-16 + M2-C1 注记）；记录 working-tree SHA-256、blob ID、blob SHA-256；§1B 差异只含元数据（状态/日期/依据/复核身份/pin）。
3. 冻结提交：更新 FROZEN 记录（版本/日期/sha256/复核 r2 approved）、`FEA-CONTRACT_FREEZE_MATRIX.md`、UNFREEZE 载体 §8（原 §1–§7 字节保留）、旧 pin 保留；`verify_pins.ps1` 17/17、`check.ps1` PASS。M2-C1 单独记录指纹与批准依据。
4. 同步 FEA-09 Task/AC/Handoff/EV/STATUS/PLAN/checkpoint；登记 C-04b/C-08/C-09/导出消费方影响。
5. 实现：A 包 → R1-I001；B 包 → R1-I005；各自测试矩阵（Reviewer r1 §9 全项）+ 新独立实现复核 + DSH 集成。

## D. 测试矩阵（冻结，供实现与复核）

A：artifact-only/columns-only/交叉/thumbnail-only；get/list/projection 一致；typed R 失败不隐藏 V；多 artifact 不重复；页/章节/书删除；page/revision 未来时间；NULL/dangling/non-valid current；非 VISIBLE_TYPES；referenced 不穿透；v1–v6 升级与 v7 读回归；固定 t/排序；完整性/人工数据/Lock/current/pinned 守恒；缺文件/越根/不可读/verifier 缺失不切入口；同连接验证、破坏 SQL/mapper 必失败、回滚无半迁移。
B：ZipCrypto ZIP/CBZ、真加密 PDF import→fresh secret→resolve；无密/错密/重试成功/三次锁定/并发/重放/TTL/撤销/EOF/超时；签名不匹配、跨页/源/版本、路径替换/reparse、cache hit/miss、重启/孤儿清理；四象限兼容；密码与 secret 全形式零泄漏；原处理/缓存键失效；Python/.NET/build/真实 IPC/check/17 pins，未运行项 NOT_RUN。

## E. 明确不做

补 ORIGINAL 行/迁移资源；改 referenced 分支/grant 四维 scope/import 状态机/WireLog 结构；协议 major/minor bump（除复核裁定）；新增命令/错误码（复用两密码码）；依赖；UI 接线（FEA-09-UI-1）。
