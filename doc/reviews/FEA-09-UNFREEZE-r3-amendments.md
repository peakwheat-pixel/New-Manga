# FEA-09 UNFREEZE 修订提案 r3（A 包：C-05 v1.2 / C-15 v1.1 / M2-C1 2.12-a；B 包：C-16 v1.1 / M2-C1 2.12-b）

状态：**PROPOSAL r3 — 待第三次独立复核**（2026-11-04）
作者：DSH；依据：`doc/reviews/FEA-09-UNFREEZE-r2-review.md`（Codex 独立，`changes_requested` P0=0/P1=6/P2=2，reviewed_head `68a46dfe5`，SHA-256 `b0c5ec75…`）、r1 review/disposition。
本轮只闭合 R2-001…R2-008 并给出精确条款；**不修改任何生产代码**。两包分别冻结；A 先行，B 基于 A 定稿的 M2-C1 字节。

## 0. R2 findings 逐项处置

| ID | 处置摘要 |
|---|---|
| R2-001 | 新增只读 `PageView` 投影类型（C-15 §4.4）；不扩域 domain `Page`；缺值字段固定为 NULL（`source_hash` 绝不用非 original hash），mode 限定 managed，禁回写 provenance。 |
| R2-002 | 冻结 `PageView` 与 wire `ReaderProjection` 的边界；M2-C1 2.12-a 增可选 `unavailable_pages:[{page_id,reason_code}]`（additive，零 minor bump）；迁移回调只用**纯投影构建器**，不得调用 publish/resolve handler。 |
| R2-003 | 冻结正尺寸旧基线 `_LEGACY_COPY_WHERE_POSITIVE`；v7 回填 SQL 改为正尺寸（v7 尚未发布，可修订）；断言 1/3 同步；零尺寸/未来/软删反例保留。 |
| R2-004 | resolve 请求只收 `secret_token`（无 path）；Core 从**签名 grant**取 path；冻结 token→私有目录映射、reparse/替换拒绝、同一对象消费删除、未验证路径绝不清理、replay 拒绝。 |
| R2-005 | 冻结准入/claim/计数线性化：每 key 单准入、token 原子 claim、仅 decrypt 失败计数、cache hit 不消费、冷却起点/重置/清理责任表。 |
| R2-006 | 冻结资源**不可变内容**：同 `resource_id` 内容摘要不一致 → typed `INPUT_REVISION_CHANGED`，不替换；仅 artifact 文件缺失时自愈重发布；original→copy 回退同样受摘要约束；并发发布单飞。 |
| R2-007 | 冻结流程改为：语义修订提交（契约正文）→ 三指纹 → 新独立复核**已提交字节** → 仅元数据冻结提交；§1B 仅元数据差异。 |
| R2-008 | 新增下游影响表（C-04b/C-08/C-09/C-14/导出/UI-1）；M2-C1 A/B 版本链与指纹顺序固定；B 基线=A 定稿字节。 |

## A 包（I001）：C-05 v1.2 + C-15 v1.1 + M2-C1 2.12-a

### A1. C-05 v1.2 精确条款

**§3.1 整体替换**（不是追加；P1–P5/P7/P8 原字节保留）：

```text
V(p,t) ≡ (p.source_mode='managed' ∧ (V_artifact(p,t) ∨ V_copy_original(p,t)))
       ∨ (p.source_mode='referenced' ∧ V_ref(p,t))

V_artifact(p,t) = 原 P1–P5（artifact/revision；不受 pages 尺寸/完整性/created_at 约束）
V_copy_original(p,t) =
  P1 ∧ p.source_mode='managed' ∧ p.integrity_status='complete'
  ∧ p.source_hash IS NOT NULL ∧ p.managed_original_ref IS NOT NULL
  ∧ p.width > 0 AND p.height > 0 ∧ p.created_at <= t
V_ref(p,t) = 现有 P1∧P7∧P8∧P5（字节不变）
```

- witness 独立；`V` 不推出 R。
- **R（managed）**：优先合格 `original` artifact revision 的 `managed_path`；否则 `pages.managed_original_ref`；受管根校验；失败 typed；不得因 R 失败隐藏 V。
- **投影（C-15 §4.4 的只读 PageView）**：`V=true` 时 get/list/reader 投影必须可见；不可读行不得丢弃。
- 反例矩阵维持 r2 1–8，但修正：
  - 反例 1/2 "R 可读" 改为"当且仅当文件存在、受管根校验通过、读取成功"；
  - 反例 4/7 明确"两 witness 均失败才 V 假；page 尺寸/时间只约束 copy，revision 时间只约束 artifact"。
- §3.2 表与 §5 失败语义同步（旧 artifact 失败行仅描述 V_artifact；copy 独立；V 真 R 假 → typed）。

### A2. C-15 v1.1 精确条款

**§4.4 新增「只读 PageView 与不可读页」**

```text
PageView（只读投影，非 domain 实体）字段：
  page_id, chapter_id, book_id, source_mode, sort_order, source_order, created_at,
  visibility_witness: 'artifact'|'copy'|'artifact+copy',
  original_available: bool,          -- DB 投影可知存在合格 original 资源；不表示实时可读
  original_ref: str|null,            -- 合格 original revision managed_path 或 pages.managed_original_ref
  source_hash: str|null,             -- 仅合格 original revision file_hash 或 pages.source_hash；绝不用 thumbnail/clean hash
  source_size_bytes: int|null,
  width_px: int|null, height_px: int|null,   -- 无合格值则 NULL，不得用 0/假值
  artifact_revision_id: str|null, integrity_status: str, deleted_at: null

- get_page/list_pages/reader 纯投影构建器返回 PageView；不得用 Page（domain）承载不可读行。
- PageView 绝不接受 add_page/update_page/import 回写；写路径仍用 domain Page（严格非空 hash/ref/正尺寸）。
- original_available=false 的 PageView：get/list 必须先返回（typed 不可读），R 返回 SOURCE_ENTRY_MISSING/内部资源错误；禁止静默过滤。
- 同一页多 artifact 按 page 去重；选择顺序：合格 original revision（valid + current + created_at<=t）→ pages.managed_original_ref → 无。
```

**§4.2 五读路径**：get/list 返回 PageView；reader 纯投影构建器返回 `{pages: PageView[], unavailable_pages:[...]}`；wire handler 只做投影→DTO 映射，不发布资源（发布仍由 resolve 命令负责）。

**§1 断言 1/3（R2-003）**

```text
_LEGACY_COMPLETE_WHERE_POSITIVE =
  source_hash IS NOT NULL AND managed_original_ref IS NOT NULL
  AND width IS NOT NULL AND height IS NOT NULL AND width > 0 AND height > 0
断言1：旧正尺寸 complete 集合 = 迁移后 managed is_complete_page 集合（逐 page_id）；
      旧 NULL/零/负尺寸行保持 incomplete，进入待恢复清单；不得提升 complete。
断言3：旧正尺寸 complete 无 artifact 页保持 complete；未删/父未删/created_at<=t 时经 copy witness 可见；
      deleted_at 非空或 created_at>t 时保持 complete 但不可见；软删/未来反例必须保留。
v7 回填 SQL：UPDATE pages SET integrity_status='complete' WHERE <_LEGACY_COMPLETE_WHERE_POSITIVE>；
（v7 尚未发布；本次 UNFREEZE 同时修订 §2 回填谓词，迁移版本号不变。）
```

**§1 断言 2**：expected = 旧 artifact 可见集合 ∪ 旧正尺寸 copy 可见集合（固定 t/父级）；artifact/copy 分支各自守恒；同一事务连接、固定 t；核验 get/list/reader 纯投影三者；非空资源禁跳 verifier；破坏 SQL/mapper 必失败。**迁移回调禁止调用 wire handler（会 resolve/publish/缓存/last-used）**，只用纯投影构建器。

**断言 5**：资源对象=合格 original revision managed_path 否则 managed_original_ref；无路径 → `SOURCE_MIGRATION_RESOURCE_UNVERIFIED`；missing/unreadable 同；不得隐藏 V 页；verifier 缺失且待验非空 → 失败。

### A3. M2-C1 2.12-a（A 包同步，不并入 17 pin）

- **ResolvePageResource** managed 资源选择：合格 current original revision → Page Managed Copy；稳定键 `page-original-{page_id}` 不变。
- 资源不可变：同一 resource_id 已发布内容摘要与当前选择源摘要不一致 → `INPUT_REVISION_CHANGED`（conflict，retryable=false），**不替换内容**；artifact 文件缺失才同键重发布自愈；并发发布单飞；不得仅比较 revision.file_hash。
- **ReaderProjection（R2-002）**：新增可选 `unavailable_pages:[{page_id, reason_code}]`（additive，零 minor bump；旧客户端忽略）；`pages[]` 仍只含可读页（正尺寸/resource_ref 保持不变）。纯投影构建器同时输出两部分；wire handler 不 resolve/publish。
- 记录原指纹、条款 diff、兼容矩阵、错误面、批准身份；不声称 17/17 覆盖 M2-C1；A 定稿字节作为 B 基线。

## B 包（I005）：C-16 v1.1 + M2-C1 2.12-b

### B1. C-16 v1.1 精确条款

**§0 能力**：新增 `source.resolve-secret/1`；Host 在创建 secret 文件与发送请求前检查；缺失/探测异常 → `CORE_CAPABILITY_MISSING`（fail-closed），不创建秘密文件。旧 Core 忽略未知可选字段，加密 resolve 仍 typed REQUIRED。

**§3 追加「Resolve 密码通道」**

```text
请求：resolve_page_resource {page_id, secret_token?}
- secret_token 是 opaque token（无常量路径）；Host 每次 resolve 前用 RegisterSourceReadGrant 铸造 fresh grant：
  同 registry/generation/roots/facts/entries（scope 不变）、新 grant_id、新 secret_ref{token,path,expires_at≤300s且≤单次请求}。
- Host 先 probe capability source.resolve-secret/1；创建 <DataRoot>/host/source-secrets/<token>.bin（"NMSSR1\0"+DPAPI CurrentUser；token 仅 [A-Za-z0-9_-]{22,64}；目录私有 ACL；拒绝 reparse）。
- Core 验证顺序（全部通过才允许消费）：
  1) binding healthy → 2) import-bound grant live（find_bound_for_source）→
  3) 存在 live 签名 grant G：G.secret_ref.token == secret_token，且 G.session/generation/expiry 有效，且 G.scope 的容器 facts/kind/locator 与 binding 源一致 →
  4) G.secret_ref.path 是 <DataRoot>/host/source-secrets/ 下规范绝对路径（大小写/../reparse 拒绝），打开独占句柄校验文件 identity(volume/file id/size) 与 token 映射一致 →
  5) 原子 claim token（每进程 consumed 集合 + 锁）；replay → SOURCE_ACCESS_DENIED。
- 消费：打开同一句柄读取 → 零填充 → 删除（失败也删/尽最大努力）；密码仅局部变量并清零；被拒绝/未 claim 的路径绝不清理（Host 自己清理）。
- 一次性/重放：token claim 成功即标记 consumed；claim 前失败不标记；cache hit 不 claim、不要求 token；请求携带 token 但无需解码时，Host 在响应后删除其文件，Core 不消费。
- 准入/计数线性化：每 (page_id, accepted_source_version) 单准入 semaphore；只有已完成 claim 且解密失败（SOURCE_PASSWORD_INVALID）才计数；连续 3 次 → 该 key 冷却 300s（从第 3 次失败起算），冷却期直接 typed SOURCE_PASSWORD_INVALID（category=validation，retryable=false），不 claim token；成功重置；进程重启清空；并发请求串行准入、不得并行解密。
- 错误映射：token 缺失/未知/过期/文件不可读/路径非法 → SOURCE_PASSWORD_REQUIRED；DPAPI/口令错误/冷却 → SOURCE_PASSWORD_INVALID；AES ZIP → SOURCE_FORMAT_UNSUPPORTED（不请求密码）；授权/scope/identity 失败 → 既有 SOURCE_ACCESS_DENIED/FILE_IDENTITY_CHANGED。
- PDF raster：document_raster.open(data, password=...) 接缝；bytes→UTF-8 文本解码失败 → SOURCE_PASSWORD_INVALID；无密码调用保持。
- 脱敏：token/path/password/secret 在任何 wire log/NDJSON/日志/receipt/UI/证据中零出现；审计含 hex/base64/url-encoded。
```

**§6/§7/§10**：错误映射、脱敏、v1.1 变更记录。

### B2. M2-C1 2.12-b

- `ResolvePageResource {page_id, secret_token?}`；secret_token 仅新 Core 识别；capability 强制配对；旧 Core 忽略未知字段仍 typed。
- 记录 B 基线=A 定稿 M2-C1 指纹；版本链唯一（2.12-a → 2.12-b），不并行改写。
- 协议 minor 保持 2.3；复核若要求 bump 则另记裁决。

### B3. 四象限兼容矩阵（冻结）

| Host\Core | 旧 Core | 新 Core |
|---|---|---|
| 旧 Host | 现状（加密 resolve REQUIRED） | 现状；新能力未使用 |
| 新 Host | capability 缺失/异常 → `CORE_CAPABILITY_MISSING`，不创建 secret，typed | 加密 resolve 全链；非加密/非 referenced 字节不变 |

## C. 冻结流程（R2-007，A/B 各执行）

1. 本 r3 → 第三次独立复核（新上下文）approved 且 P0/P1=0。
2. **语义修订提交**：仅契约正文（A：C-05/C-15 + M2-C1 2.12-a；B：C-16 + M2-C1 2.12-b）；提交后固定每文件三种指纹（工作树 SHA-256、blob ID、blob SHA-256）写入载体。
3. **已提交字节的新独立复核**（只读该 commit 的契约字节）approved。
4. **仅元数据冻结提交**：FROZEN 记录（版本/日期/sha256/两次复核身份）、矩阵、载体 §8、旧 pin 保留；`verify_pins` 17/17、`check` PASS；M2-C1 单独记录指纹。
5. 再释放对应实现包（A→I001、B→I005），各自测试矩阵 + 新独立实现复核 + DSH 集成。

## D. 下游影响表（R2-008）

| 消费方 | 影响与处置 |
|---|---|
| C-04b 删除预览/内容摘要 | 目标集合仍用 `V`；不可读 V 页计入目标，但内容摘要只对可读页；A 载体记录"无字节改动"依据 |
| C-08 Run 快照 | 快照可含 unreadable 页，resource_ref=null+reason_code；不改变快照守恒断言；A 载体登记 |
| C-09 备份/迁移 | 迁移资源门禁不变（断言 5 已覆盖）；备份字节不变；A 载体登记 |
| C-14 缓存/lease | rendition cache key/失效规则不变（B 的 secret 消费不影响 cache）；A/B 均登记"无改动" |
| 导出 | 只导出可读页；unreadable V 页按 typed skip/错误呈现；FEA-14 消费方 Task 登记 |
| UI-1 | 承接不可读页占位（reason_code）、密码重试/冷却/能力缺失提示；不新增 C-07 方法；Task UI-1 增要求 |
| M2-C1 | A：2.12-a（managed 选择/不可变/Reader unavailable_pages）；B：2.12-b（secret_token）基于 A 定稿字节；均单独登记指纹，不并入 17 pin |

## E. 测试矩阵（A/B 各自，冻结）

A：真 artifact-only / 真 columns-only / 交叉 / thumbnail-only / 两 witness 均失败；PageView 字段 NULL 规则；get/list/reader 一致且不丢行；typed R 失败不隐藏 V；多 artifact 不重复；页/章节/书删除；page/revision 未来时间；NULL/dangling/non-valid current；非 VISIBLE_TYPES；referenced 不穿透；v1–v6 升级、v7 读回归；固定 t/排序；正尺寸基线/零尺寸恢复清单；人工数据/Lock/current/pinned 守恒；缺文件/越根/不可读/verifier 缺失不切入口；同连接纯投影；破坏 SQL/mapper 必失败；迁移回滚无半迁移；M2-C1 Reader unavailable_pages 兼容。
B：ZipCrypto ZIP/CBZ、真加密 PDF import→fresh secret→resolve；无密/错密/重试/3 次冷却/并发准入/replay/TTL/撤销/EOF/超时/崩溃孤儿；签名/token 不匹配、跨页/源/版本、路径 reparse/替换、未验证路径不清删；cache hit 不消费；四象限；密码与 token 全形式零泄漏；PDF 密码接缝；Python/.NET/build/真实 IPC/check/17 pins，未运行项 NOT_RUN。

## F. 明确不做

补 ORIGINAL 行/迁移资源；改 referenced 分支/grant 四维 scope/import 状态机/WireLog 结构；协议 major/minor bump（复核否定保留 2.3 时按裁决）；新增命令/错误码；依赖；UI 实现（UI-1）；不改 C-06 字节（本方案不新增 grant 字段/不放宽授权）。
