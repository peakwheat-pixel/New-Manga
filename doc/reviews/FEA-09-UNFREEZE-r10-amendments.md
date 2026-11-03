# FEA-09 UNFREEZE 修订提案 r10（r9 + R9-001/R9-002 最小语义）

状态：**PROPOSAL r10 — 待第十次独立复核**（2026-11-04）
作者：DSH；依据：`doc/reviews/FEA-09-UNFREEZE-r9-review.md`（Codex 独立，`changes_requested` P0=0/P1=2，reviewed_head `a7f636300`，SHA-256 待归档后填）。
**r10 = r9 + 下列两条冻结语义**；r9 其余不变；R8-001 分类面与 R8-002 双层过期映射已 CLOSED，不再改。

## R9-001：Reader 恢复 DTO 语义（替换 r9 §R8-001 的 initial_position 行）

```text
wire DTO（M2-C1 不变）：initial_position = {page_id, scroll_offset_y}（既有形状，不改成数值）。
V 全集序：按 (sort_order ASC, page_id ASC) 的 0-based 序；unavailable_pages[].logical_order 同此序。
锚点恢复：
1) 进度页存在且属于 V 且 R 可读 → initial_position = {page_id: 进度页, scroll_offset_y: 保存 offset}；
   pages 从该页（含）开始按 V 序输出可读页（>= 锚点）。
2) 进度页存在、属于 V 但 R 不可读 → 锚点 a = 该页 logical_order；initial_position =
   {page_id: 首个 >=a 的可读页（无则回绕到最小可读页）, scroll_offset_y: 0}；该不可读页进 unavailable。
3) 进度页已不在 V（软删/移出）→ 用该页 DB 行的 sort_order 求锚点序 a（页行仍可读 sort_order；
   页行不存在则 a=0）；initial_position = {首个 >=a 的可读页，offset 0}（无则回绕）；不返回已移出页。
4) V 非空但全部不可读 → 成功返回 pages:[]、unavailable_pages=V 全集；
   initial_position = {page_id: V 序最小页, scroll_offset_y: 0}（该页必在 unavailable 中）。
5) V 为空（章节无页）→ 沿用 M2-C1 既有 TARGET_NOT_FOUND（不返回成功空集）。
6) 无保存进度 → a=0；规则同 2)（正常从首可读页开始）。
Webtoon offset：仅情形 1) 保留保存 offset；跳转/回绕/不可读锚点/无进度均 0。
旧客户端（不解析 unavailable_pages）：由于 initial_position 永远是"可读页或 V 内页"，旧客户端不会收到指向不存在页的初始位置；
不可读页对旧客户端表现为 pages 空缺位（无占位），不下发额外错误。
新 CoreClient 解析 unavailable 并交 UI-1；新/旧 Core 配对：旧 Core 不产生该字段（行为不变）。
```

## R9-002：完整错误优先级（替换 r9 §R8-002 决策顺序）

```text
“相关候选”定义（冻结）：
  Auth 候选 = 所有 live 或可判定 grant 中，scope 的 source/version/entry/rendition 与 binding 一致者；
  Secret 候选 = Auth 候选中 secret_ref != null 且 secret_ref.token == payload.secret_token 者；
  过期/撤销/签名只对**被选中参与本次授权判定**的候选检查；与本请求无关的其他 grant 不参与。

唯一顺序（同输入唯一结果；与 C-16 §2 优先级一致：签名→过期→撤销→授权）：
1) capability 缺失/探测异常 → CORE_CAPABILITY_MISSING (protocol,false)
2) binding 非 healthy / binding 版本/entry 与 DB 不一致 → SOURCE_ACCESS_DENIED (authorization,false)
3) 相关候选的签名校验：被选中 Auth/Secret 候选签名非法 → REF_SIGNATURE_INVALID
4) 相关候选中被选中者已过期（grant.expiry <= now）→ SOURCE_GRANT_EXPIRED (authorization,true)
5) 相关候选被撤销 / session 或 generation 失配 → SOURCE_GRANT_REVOKED (authorization,false)
   （若仅存在被撤销候选而无 live 候选，仍返回 GRANT_REVOKED，不降级为 DENIED）
6) Auth 候选为空（存在性授权失败）、registry/root/scope/identity 校验失败 → SOURCE_ACCESS_DENIED / FILE_IDENTITY_CHANGED
7) Auth 通过后：cache 命中 → 返回（不要求 token/claim，不计数，冷却不阻断）
8) 冷却中 → SOURCE_PASSWORD_INVALID (validation,false)
9) Secret 候选：0 个或 secret_ref.expires_at <= now → SOURCE_PASSWORD_REQUIRED (validation,false)；
   >=2 个 / claim 重放 → SOURCE_ACCESS_DENIED (authorization,false)；
   path/对象/token-path 匹配失败 → SOURCE_PASSWORD_REQUIRED (validation,false)
10) 解密失败 → SOURCE_PASSWORD_INVALID (validation,false)，计数 +1
11) 成功 → 计数清零、返回
双层过期：grant.expiry 在第 4 步、secret_ref.expiry 在第 9 步；两者同时过期 → 第 4 步先命中 → GRANT_EXPIRED（唯一）。
C-16 §6 category/retryable 逐字为准；不新增错误码。
```

- Auth 存在性：至少一个 Auth 候选通过 3)–6) 即授权通过；Secret 候选仅在 cache miss 的第 9 步要求唯一。
- impl-design 同步本顺序与 Reader DTO 规则；实现 Review 用同输入唯一 + 负例矩阵校验。

## 同步与流程

- 本文件替换 r9 对应两行；其余条款（V/witness/R、迁移、投影、资源不可变、能力、A→B、冻结流程）不变。
- r10 approved 且 P0/P1=0 → A 语义提交（C-05/C-15/M2-C1 2.12-a）→ 三指纹/old-new blob → 已提交字节复核 → 仅元数据冻结；B 基于 A 定稿字节同流程；M2-C1 单独登记。
- 未运行项（pytest/.NET/build/IPC/DPAPI/迁移/竞态/泄漏）NOT_RUN。
