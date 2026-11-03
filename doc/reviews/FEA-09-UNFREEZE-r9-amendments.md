# FEA-09 UNFREEZE 修订提案 r9（r8 + R8-001/R8-002 最小语义）

状态：**PROPOSAL r9 — 待第九次独立复核**（2026-11-04）
作者：DSH；依据：`doc/reviews/FEA-09-UNFREEZE-r8-review.md`（Codex 独立，`changes_requested` P0=0/P1=2，reviewed_head `a7f636300`，SHA-256 `240293a2…`）。
**r9 = r8 + 下列两条冻结语义**；r8 其余不变。r7/r8 review 已原字节归档（r7 `9fcae9c6…`、r8 `240293a2…`）。

## R8-001：Reader 响应边界与恢复（替换 r8 §1.2 Reader 行）

```text
分类（采用 r7 §1.1 全码枚举，冻结）：
PAGE_UNAVAILABLE_CODES = {SOURCE_ACCESS_DENIED, SOURCE_GRANT_EXPIRED, SOURCE_GRANT_REVOKED,
  SOURCE_PASSWORD_REQUIRED, SOURCE_PASSWORD_INVALID, SOURCE_FORMAT_UNSUPPORTED,
  SOURCE_ENTRY_MISSING, SOURCE_BUDGET_EXCEEDED, FILE_IDENTITY_CHANGED,
  SOURCE_PROJECT_MISMATCH, INPUT_REVISION_CHANGED}
其余全部 code（含 C-16 §6 中未列出的内部/协议/注册表/操作类、未知 code）→ 整请求失败：
返回原错误 envelope，不返回部分 pages、不返回 unavailable。
逐页 R 错误 ∈ PAGE → unavailable_pages[{page_id,reason_code,logical_order}]；
∈ 其余 → 整请求失败。
```

- `logical_order`/`pages[].order` 共用 V 全集 0-based 序（`sort_order ASC, page_id ASC`）。
- **resume 冻结**：锚点 = 进度页的 logical_order `a`（若进度页不在 V 或其 R 失败，使用其逻辑序）。
  - 首个返回可读页 = 满足 `logical_order >= a` 的最小可读页；
  - 若不存在，取可读页中最小 `logical_order`（回绕）；
  - 若整章无可读页 → `pages:[]` + `unavailable_pages`=V 全集；
  - `initial_position` = 首个返回可读页的 logical_order（无可读页时 = a）。
  - 锚点本身可读 ⇒ 包含（>= 规则）。
- 旧客户端忽略 `unavailable_pages`；旧 Core 不返回该字段；该字段仅在 reader 成功响应中出现。
- 客户端收到成功 ⇔ 无 REQUEST_LEVEL 错误；成功时 pages 可空但 unavailable 保留全集（产品可显示原因）。

## R8-002：过期与秘密失败错误消歧（替换 r8 §2.1 ⑥ 与 r8 §2 继承项）

```text
唯一决策顺序（只冻结"同输入唯一结果"，不冻结代码结构）：
1) capability 缺失/探测异常 → CORE_CAPABILITY_MISSING (protocol,false)
2) binding 非 healthy / binding 版本/entry 与 DB 不一致 → SOURCE_ACCESS_DENIED (authorization,false)
3) grant 自身过期（Auth-G / Secret-G 任一） → SOURCE_GRANT_EXPIRED (authorization,true)
4) Auth-G 条件（scope/facts/locator 与 binding 一致）不满足 → SOURCE_ACCESS_DENIED
5) cache 命中（仍需 1–4）→ 返回；不要求 token/claim，不计数，冷却不阻断
6) 冷却中 → SOURCE_PASSWORD_INVALID (validation,false)
7) Secret-G 选择/secret_ref expiry/token/path/对象/claim 失败：
   - 无 Secret-G 匹配 / secret_ref.expires_at <= now → SOURCE_PASSWORD_REQUIRED (validation,false)
   - 多匹配 / claim 重放 → SOURCE_ACCESS_DENIED (authorization,false)
   - path 非法/对象非法/token 与路径不匹配 → SOURCE_PASSWORD_REQUIRED (validation,false)
8) 解密：DPAPI/口令错误 → SOURCE_PASSWORD_INVALID (validation,false)，计数 +1
9) 成功 → 计数清零、返回
双层过期规则：grant 自身 expiry 归第 3 步（GRANT_EXPIRED）；secret_ref.expiry 归第 7 步（REQUIRED）。
两者同时过期 ⇒ 第 3 步先命中 → GRANT_EXPIRED（唯一结果）。
```

- 错误 category/retryable 一律以 C-16 §6 为准（表中已逐条列出）；不新增/不改码。
- 计数/并发/终止/清理、AES ZIP、PDF 接缝、零泄漏审计沿用 r6 §2/r8 §2。
- impl-design 同步本顺序（只作为实现映射，不改变契约）；实现 Review 用"同输入唯一 + 负例矩阵"校验。

## 同步与流程

- r8 §1.2 Reader 行、§2.1 ⑥ 由本文件替换；其他条款（V/witness/R、迁移断言、投影最低集、资源不可变、能力、授权不变量、A→B、冻结流程）不变。
- 冻结：r9 approved 且 P0/P1=0 → A 语义提交（C-05/C-15/M2-C1 2.12-a）→ 三指纹/old-new blob → 已提交字节复核 → 仅元数据冻结；B 基于 A 定稿字节同流程；M2-C1 单独登记。
- 未运行项（pytest/.NET/build/IPC/DPAPI/迁移/竞态/泄漏）NOT_RUN（实现阶段补）。
