# FEA-09 UNFREEZE 修订提案 r13（r12 + R12-001）

状态：**PROPOSAL r13 — 待第十三次独立复核**（2026-11-04）
作者：DSH；依据：`doc/reviews/FEA-09-UNFREEZE-r12-review.md`（Codex 独立，`changes_requested` P0=0/P1=1/P2=0，reviewed_head `a7f636300`）。
**r13 = r12 + 下列 R12-001 冻结语义**；其余不变（无 wire/DTO 变更；R11-002 已 CLOSED）。

## R12-001：Reader 页集/分派/移出页恢复（替换 r12 §R11-001 全部）

```text
1) pages[] 语义（冻结，兼容 M2-C1）：
   pages[] = 该章节**全部可读页**（V 真且 R 可读），按规范 V 序（sort_order ASC, page_id ASC）完整返回；
   不因 initial_position 截断前后缀。可读页集与保存进度无关。
2) start_position 分派（冻结）：
   - "beginning" → 忽略保存进度；initial_position=首可读页 + offset 0；saved_progress 不删除/不改写。
   - "resume" → 以下恢复规则；无保存进度时等同 beginning。
3) resume 锚点（冻结）：
   - 保存页可读：initial_position={保存页, 保存 offset}。
   - 保存页属于 V 但不可读：锚点 a=该页在 V 序中的 logical_order；
     initial_position={首个 logical_order>=a 的可读页（无则回绕到最小可读页），offset 0}。
   - 保存页已不在 V：若 DB 页行存在，a = 该章 V 页中 `sort_order` 严格小于保存页 sort_order 的页数
     （即插入位置；同 sort_order 按 page_id 规范序）；无页行则 a=0；
     initial_position={首个 logical_order>=a 的可读页（无则回绕），offset 0}。
   - 不变量：initial_position.page_id ∈ pages[]；offset 为 0..1 归一化（沿用既有 DTO）。
4) 无可读页：
   - 章节无页（V 空）→ TARGET_NOT_FOUND（既有）。
   - V 非空但零可读页 → TARGET_NOT_FOUND（既有；不返回成功空集、不扩展 reader wire）。
   - 不可读页诊断仅经管理/诊断读路径（get/list 投影）。
5) 旧客户端兼容：pages[] 仍为章节可读全集；initial_position 属于 pages[]；beginning/resume 语义与既有 M2-C1 一致；
   跳过页不进入 pages[]；行为与现有客户端导航兼容。
6) 错误边界：逐页 R 错误 ∈ PAGE_UNAVAILABLE_CODES（11 码，正式 SOURCE_* 名称）→ 跳过该页；
   其余错误 → 整请求失败（原 envelope，无部分结果）。
```

## 同步与冻结

- 替换 r12 §R11-001；其余条款不变。
- 冻结流程沿用 r11 §6：r13 approved 且 P0/P1=0 → 语义修订提交（C-05/C-15/C-16）→ 三指纹/old-new blob → 已提交字节复核 → 仅元数据冻结（FROZEN/矩阵/载体 §8/旧 pin）→ check+17 pins；M2-C1 无字节变更登记（版本/指纹/no-diff/行为兼容依据）。
- 未运行项（pytest/.NET/build/IPC/DPAPI/迁移/竞态/泄漏）NOT_RUN。
