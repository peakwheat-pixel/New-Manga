# FEA-09 实现设计委托：I001 / I005（不冻结，供实现 Review 校验）

状态：**DESIGN-DELEGATED**（2026-11-04；由 DSH 在 UNFREEZE r5 中明确委托）
作用：承载 r1–r4 契约复核中属于**实现级**的细节；契约正文只冻结语义/不变量（见 `doc/reviews/FEA-09-UNFREEZE-r5-amendments.md`）。任何实现不得违反契约冻结条款；实现 Review 以本文件 + 契约条款双向校验。

## 1. I001（managed 可见性等价分支）

### 1.1 端口与类型
- `PageRepository.get_page(page_id) -> Page | None` 保持给可完整构造行（managed copy witness 完整 或 artifact witness 且有合格 original）；未知 ID → None。
- 新增 `get_page_view(page_id) -> PageView | None`：V=true 且无法构造 Page 时返回降级投影；可读行亦返回 Page 的等价 PageView（便于统一读路径）。
- `list_pages(chapter_id) -> list[Page | PageView]`：按 sort_order；可读 Page、降级 PageView；不得过滤 V 行。
- `list_page_views(chapter_id) -> list[PageView]`：纯投影构建器（迁移/一致性用），不发布/不解析/不写 last-used、不背连接。
- `PageView` 字段（最小）：page_id/chapter_id/book_id/source_mode/sort_order/source_order/created_at/visibility_witness ∈ {artifact,copy,artifact+copy,referenced}/original_available/source_hash?/source_size_bytes?/original_ref?/width_px?/height_px?/artifact_revision_id?/integrity_status/deleted_at(恒 null)。
- 写路径（add_page/update_page/import/binding）只接受 domain `Page`；PageView 不可写回。

### 1.2 SQL 与 mapper
- V SQL：`(managed AND (artifact-witness OR copy-witness)) OR (referenced AND V_ref)`；artifact witness=EXISTS 合格 current revision（VISIBLE_TYPES/valid/created_at<=t）；copy witness=§3 copy 列谓词。
- SELECT 取 pages 列 + 合格 original revision 回填列（file_hash/managed_path/width/height/size）；无合格值置 NULL，绝不用 thumbnail/clean hash。
- mapper：能构造 Page 用 Page；否则 PageView；禁止静默丢弃；多 artifact 按 page 去重。
- 读失败 R：get_page_view 上层 `resolve` 失败 typed（SOURCE_ENTRY_MISSING 或资源错误），不得返回空页。

### 1.3 迁移
- v7 回填 SQL 改正尺寸谓词；断言 1/2/3/5 按 C-15 v1.1；验证用同一事务连接、固定 t、get/list/pure-projection 三路径；verifier 非空必注入；破坏 SQL/mapper 测试必失败。
- 恢复清单 = 旧 incomplete + 零/负/NULL 尺寸行（page_id 列表，进迁移诊断文件；不改变回填集合）。

### 1.4 Reader
- 纯投影：`pages=[Page|PageView]`（V 全集排序）+ `unavailable=[{page_id,reason_code,logical_order}]`。
- wire：pages[] 仅可读页（既有 DTO 正尺寸/resource_ref）；首次打开按既有 resolve/publish；resolve typed 失败的 V 页进 unavailable；全不可读 → pages=[] + 全集 unavailable；initial_position 以逻辑序（含不可读空位）计算，首屏取该序之后的可读页；发布/内部错误不归入 unavailable（向上 typed）。
- CoreClient 解析 unavailable_pages；UI-1 Task 承接占位/跳转/密码重试。

## 2. I005（加密源 resolve 密码通道）

### 2.1 wire 与 Host 流程
- `ResolvePageResource` payload `{page_id, secret_token?: string}`；旧 Core 忽略未知字段。
- Host：capability `source.resolve-secret/1` 检查（缺失 → typed CORE_CAPABILITY_MISSING，不建文件）→ 生成 token `[A-Za-z0-9_-]{22,64}` → 写 `<DataRoot>/host/source-secrets/<token>.bin`（magic+DPAPI，私有 ACL，原子创建）→ 调 RegisterSourceReadGrant 注册 fresh G（scope 不变、secret_ref={token,path,expires_at≤300s 且≤单次请求}）→ 发送 resolve（带 token）→ finally 删除本地文件。
- Host 本地不持久化密码；默认清理：超时/取消/失败统一 finally 删除。

### 2.2 Core 决策顺序与错误表
1. capability（若需要 secret）→ 2. page/binding healthy → 3. G 选择：live grants 中恰一个 secret_ref.token==token 且 session/generation/expiry 有效、scope(source/version/entry/rendition) 与 binding 一致；0 或多于 1 → DENIED。
4. 路径规则：`<DataRoot>/host/source-secrets/<token>.bin` 规范绝对、祖先无 reparse、lstat 普通文件、独占句柄打开、同句柄复验 identity→claim token（进程内集合，原子）→ 读取/零填充/删除（同句柄；失败尽最大努力）。
5. 解密：PDF bytes→utf-8 失败或 DPAPI/口令错误 → INVALID；成功 → 继续；任何读取后异常走 finally 清理（已 claim 文件）。
6. 计数：仅解密失败 +1（key=(page_id,version)）；3 次 → 300s 冷却（第 3 次失败起点）；冷却期 typed INVALID retryable=false 不 claim；成功重置；cache hit 不要求/不消费 token；取消/超时/授权失败不计数。
7. cache hit：先查 rendition cache；命中直接返回（若带 token，Host finally 删除；Core 不 claim）。
8. 错误优先级：CAPABILITY_MISSING > DENIED（binding/grant/token/path/claim） > REQUIRED（token 缺失/过期/文件不可读/路径不匹配） > INVALID（解密） > 既有资源错误。
9. 启动清扫：Host 负责 token 模式 + 超 TTL 文件；Core 不另起清扫。

### 2.3 测试映射
- 单元：G 选择 0/1/多匹配、撤销/EOF/binding 变化；路径 reparse/替换/大小写/../；claim/replay/并发；计数/冷却/缓存；错误优先级；清理归属。
- 集成：ZipCrypto ZIP/CBZ、真加密 PDF import→resolve 全链；四象限；无泄漏扫描（Password/Token 明文/hex/base64/url）；真实 IPC（Host command adapter）1 passed 扩展含加密页。
- 回归：Python/.NET/build/check/17 pins；未运行项 NOT_RUN。

## 3. 与契约的关系
- 本文件不产生新冻结对象；契约条款与本文件冲突时以契约为准，并立即提交 UNFREEZE/勘误。
- 实现 Review 必须同时核对：契约冻结条款（语义）+ 本设计（实现）+ 测试矩阵（证据）。
