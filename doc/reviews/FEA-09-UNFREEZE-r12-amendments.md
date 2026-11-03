# FEA-09 UNFREEZE 修订提案 r12（r11 + R11-001/R11-002）

状态：**PROPOSAL r12 — 待第十二次独立复核**（2026-11-04）
作者：DSH；依据：`doc/reviews/FEA-09-UNFREEZE-r11-review.md`（Codex 独立，`changes_requested` P0=0/P1=2，reviewed_head `a7f636300`，SHA-256 `de91043f…`）。
**r12 = r11 + 下列两条冻结语义**；r11 其余条款不变（无 wire/DTO 变更）。r1–r11 review 均已原字节归档于 `doc/reviews/FEA-09-UNFREEZE-r*-review.md`。

## R11-001：Reader 跳过/恢复边界（替换 r11 §2.3）

```text
可跳过 vs 整请求失败（冻结）：
- 逐页 R 错误 ∈ PAGE_UNAVAILABLE_CODES（C-05 v1.2/C-16 §6 既有 11 码：ACCESS_DENIED、GRANT_EXPIRED、
  GRANT_REVOKED、PASSWORD_REQUIRED、PASSWORD_INVALID、FORMAT_UNSUPPORTED、ENTRY_MISSING、
  BUDGET_EXCEEDED、FILE_IDENTITY_CHANGED、PROJECT_MISMATCH、INPUT_REVISION_CHANGED）
  → 跳过该页（reader 不输出），其余可读页正常返回；
- 其余任何错误（registry/capability/protocol/internal/invalid/target 等）→ 整请求失败，沿用原 envelope，
  不返回部分结果。
恢复（reader DTO 不变：initial_position={page_id,scroll_offset_y}）：
1) 若存在至少一个可读页：
   a) 保存进度页可读 → initial_position={保存页, 保存 offset}；pages 从该页（含）按 V 序输出可读页。
   b) 保存进度页属于 V 但不可读 → 取该页 V 序锚点 a；initial_position=
      {首个 logical_order>=a 的可读页，offset 0}（无则回绕到最小可读页）。
   c) 保存进度页已不在 V → 用其 DB 行 sort_order 求 a（无行则 a=0）；initial_position={首个 >=a 的可读页
      （无则回绕），offset 0}。
   d) 无保存进度 → a=0，规则同 c。
   invalid：initial_position 的 page_id 必须属于 pages[] 中实际返回的可读页。
2) 若 V 非空但零可读页 → **整请求失败**，返回既有 TARGET_NOT_FOUND（M2-C1 既有语义）；
   不返回成功空集，不在 reader wire 扩展不可读页列表；不可读页诊断仅经管理/诊断读路径（get/list 投影）获得。
3) V 为空（章节无页）→ TARGET_NOT_FOUND（既有）。
旧客户端：收到 pages[] 与 initial_position 且两者一致；跳过页不出现；行为与现有客户端兼容。
新 CoreClient/UI-1：管理路径显示不可读页诊断；reader 按上述规则展示可读页。
```

## R11-002：撤销/多义错误码（替换 r11 §3 第 4 条相关措辞）

```text
- 撤销（grant revoked / RevokeSourceReadGrant / EOF 后全部失效）→ SOURCE_GRANT_REVOKED
- grant 过期 → SOURCE_GRANT_EXPIRED
- 多义（>=2 个 Secret-G）或 claim 重放 → SOURCE_ACCESS_DENIED
- category/retryable 一律以 C-16 §6 原表为准；不新增码、不改既有映射。
```

## 同步与冻结

- 本文件替换 r11 §2.3 与 §3(4) 的冲突措辞；M2-C1 **无字节变更**登记需记录：精确版本、contract 指纹、no-diff 证据、Reader 行为兼容依据（R11-001 规则保持 pages[]/initial_position 均为可读页引用；零可读时既有 TARGET_NOT_FOUND）。
- 冻结流程沿用 r11 §6：r12 approved 且 P0/P1=0 → 语义修订提交（C-05/C-15/C-16）→ 三指纹/old-new blob → 已提交字节复核 → 仅元数据冻结（FROZEN/矩阵/载体 §8/旧 pin）→ check+17 pins。
- 未运行项（pytest/.NET/build/IPC/DPAPI/迁移/竞态/泄漏）NOT_RUN。
