# FEA-09 UNFREEZE 修订提案 r6（r5 + 最小语义增量）

状态：**PROPOSAL r6 — 待第六次独立复核**（2026-11-04）
作者：DSH；依据：`doc/reviews/FEA-09-UNFREEZE-r5-review.md`（Codex 独立，`changes_requested` P0=0/P1=2/P2=0，reviewed_head `a7f636300`，SHA-256 `b6714dff…` 为 r5 提案）。
**r6 = r5 + 以下两处冻结条款**；其余 r5 条款（含"契约语义冻结 + 实现设计委托"架构）不变。r5 已 CLOSED 的 R4-001/003/004/006/007 不再改。

## 0. R5 findings 处置

| ID | 处置 |
|---|---|
| R5-001 | 冻结 Reader 逐页不可用的**错误分类闭集**与传播规则；`pages[].order`/`logical_order` 共用 V 全集序；旧客户端忽略 unavailable 的配对范围与限制写死。 |
| R5-002 | 冻结 secret 通道**唯一条件→code/category/retryable 表**、唯一决策顺序（含 cache/cooldown 位置）、计数/并发/终止/token 过期双层校验与清理失败重试/孤儿规则。 |

## 1. R5-001（A 包，替换 r5 R4-002 契约行与 A2 §4.4 reader 段）

### 1.1 冻结错误分类闭集

```text
PAGE_UNAVAILABLE_CODES（逐页 unavailable；按优先级取首个）：
  SOURCE_ACCESS_DENIED, SOURCE_GRANT_REVOKED, FILE_IDENTITY_CHANGED,
  SOURCE_ENTRY_MISSING, SOURCE_BUDGET_EXCEEDED,
  SOURCE_PASSWORD_REQUIRED, SOURCE_PASSWORD_INVALID,
  SOURCE_FORMAT_UNSUPPORTED, INPUT_REVISION_CHANGED
REQUEST_LEVEL_CODES（不得进 unavailable，向上返回整请求错误）：
  CORE_CAPABILITY_MISSING, SOURCE_REGISTRY_UNAVAILABLE, INVALID_REQUEST,
  TARGET_NOT_FOUND, 以及任何非上述闭集的内部/发布/catalog 错误。
```

- reader wire：对每个 V 页取 R；错误 ∈ PAGE_UNAVAILABLE_CODES → 该页进 `unavailable_pages{page_id,reason_code,logical_order}`；错误 ∈ REQUEST_LEVEL_CODES → 整个请求失败（不返回部分结果）。
- **顺序**：`pages[].order` 与 `unavailable_pages[].logical_order` 共用 V 全集 0-based 序（`sort_order ASC, page_id ASC`）。可读页的 `order` 保留其全集序位置（不可读页形成空位），旧客户端仅按 pages[] 顺序展示。
- 全不可读章节：`pages:[]`、`unavailable_pages`=全集；`initial_position` 仍按逻辑序（含空位）计算；首屏从该序后第一个可读页开始；无任何可读页时返回空 pages 且不报错。
- **配对范围**：`unavailable_pages` 为 M2-C1 2.12-a 可选字段；新 CoreClient 解析并交给 UI-1；旧客户端忽略该字段（不崩溃、不显示不可读页）。旧 Core 永不返回该字段。
- 发布/内部错误不得吞成 unavailable（§Pass-through 表）；UI-1 只负责占位/跳转展示，不定义错误分类。

## 2. R5-002（B 包，替换 r5 R4-005 契约行与 B1 决策顺序/错误表）

### 2.1 唯一决策顺序（冻结）

```text
1) capability：需 secret 且 Core 无 source.resolve-secret/1 或探测异常 → CORE_CAPABILITY_MISSING（fail-closed，Host 删除本地 secret）
2) binding：page_bindings.status != 'healthy' 或 source/version/entry 不一致 → SOURCE_ACCESS_DENIED
3) G 选择：live signed grant 中恰一个 secret_ref.token == secret_token（无 → REQUIRED；多于一个 → DENIED）
   并验证 G.session/generation/expiry 与 grant scope(source/version/entry/rendition) 与 binding 一致（不满足 → DENIED）
4) 缓存：命中 → 直接返回；仍以 1)+2)+3) 的授权为前提；不要求/不消费 token、不计数、冷却不阻断缓存命中
5) 冷却：仅 cache miss 且已授权时检查；冷却中 → INVALID(retryable=false)，不 claim token
6) token/路径/对象：token 缺失/过期/路径不等于规范 <DataRoot>/host/source-secrets/<token>.bin/祖先 reparse/lstat 非普通文件 → REQUIRED；claim 重放/多匹配 → DENIED
7) claim → 读取 → 解密：DPAPI/口令错误 → INVALID（计数 +1）；成功 → 计数清零、返回
8) 任何 claim 后异常 → finally 走同句柄清理（零填充+删除尽最大努力）；Host 负责超时/取消侧清理与孤儿安全重试
```

### 2.2 冻结错误表（无重叠；继承 C-16 §6 既有 category/retryable 语义）

| 条件 | code | category | retryable |
|---|---|---|---|
| 能力缺失/探测异常 | `CORE_CAPABILITY_MISSING` | unavailable | false |
| binding 非 healthy/版本/entry 不一致 | `SOURCE_ACCESS_DENIED` | permission | false |
| G 无匹配 | `SOURCE_PASSWORD_REQUIRED` | validation | false |
| G 多匹配 / claim 重放 | `SOURCE_ACCESS_DENIED` | permission | false |
| token 缺失/过期/path 非法/对象非法 | `SOURCE_PASSWORD_REQUIRED` | validation | false |
| DPAPI/口令错误 | `SOURCE_PASSWORD_INVALID` | validation | false |
| 冷却中 | `SOURCE_PASSWORD_INVALID` | validation | false |
| AES ZIP | `SOURCE_FORMAT_UNSUPPORTED` | validation | false |
| 既有资源/identity 错误 | 沿用 C-16/既有码 | 沿用 | 沿用 |

- **过期双层校验**：消费前同时验证 `grant.secret_ref.expires_at` 与 grant 自身 expiry > now；任一过期 → REQUIRED。
- **计数/并发边界**：每 (page_id, accepted_source_version) 单准入 semaphore；仅第 7 步解密失败 +1；3 次连续失败 → 冷却 300s（第 3 次失败时刻起）；冷却结束清零；成功解密清零；cache hit/取消/超时/授权失败不计数；claim 后终止（取消/超时/异常）不复用 token（Consumed），清理失败由 Host 安全重试 + 启动孤儿回收；并发准入前不 claim/不计数。
- 缓存授权：cache hit 仍必须满足 1)+2)+3)（capability/binding/G 选择），但不需要 token 与 claim；禁止绕过授权返回缓存。
- 锁类型/函数位置/finally 写法继续委托 impl-design。

## 3. 其他同步

- r5 A2 §4.3/C-15 §4.3 的"incomplete 不可见"措辞按 r5 review 提示同步为"incomplete 且无合格 artifact witness 时不可见；有合格 artifact witness 时按 V_artifact 可见"（C-15 v1.1 正文改写）。
- r5 R4-002 契约行中 `RTyped` 字样删除，替换为 §1.1 闭集。
- impl-design 同步 §1.4（reader 分类）/§2.2（唯一顺序/错误表），不新增实现细节。
- 变更记录追加 `2026-11-04 v1.1/v1.2：r6 增量（Reader unavailable 错误闭集、secret 唯一错误表/缓存-冷却顺序）。`

## 4. 冻结判断

- r6 若 approved 且 P0/P1=0：进入 A 语义修订提交 → 三指纹/old-new blob → 已提交字节复核 → 仅元数据冻结；B 基于 A 定稿字节执行同流程。
- 未运行项（pytest/.NET/build/真实 IPC/DPAPI/迁移/竞态/泄漏）保持 NOT_RUN；实现后由实现 Review + DSH 集成补证据。
