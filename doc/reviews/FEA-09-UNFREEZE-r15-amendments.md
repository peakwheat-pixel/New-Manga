# FEA-09 UNFREEZE 修订提案 r15（r14 + R14-001）

状态：**PROPOSAL r15 — 待第十五次独立复核**（2026-11-04）
作者：DSH；依据：`doc/reviews/FEA-09-UNFREEZE-r14-review.md`（Codex 独立，`changes_requested` P0=0/P1=1/P2=0，reviewed_head `a7f636300`，r14 SHA-256 `afb924d2…`）。
**r15 = r14，仅一处替换（R14-001）**。

## R14-001：offset 数值类型（替换 r14 §R13-001 第 1 行）

```text
offset 语义（沿用 M2-C1 §6.3，不归一化、不取整）：
- Webtoon：scroll_offset_y = 逻辑 Page 源图像素坐标，**非负有限数值（number）**；
  合法范围（有限、非负、页高范围）沿用 M2-C1 §6.3 既有校验，不额外要求整数。
- 分页章节：scroll_offset_y = 0。
- resume 且保存页可读：initial_position={保存页, 保存 scroll_offset_y 原值}（含合法小数，不取整）。
- 保存页不可读/已移出/回绕/beginning/无进度：initial_position={替代可读页, scroll_offset_y: 0}。
- 不变量：page_id ∈ pages[]；offset 为 M2-C1 既有单位与校验，不引入 0..1 归一化、不取整。
```

## 其余

- r14 其余条款不变（R13-002 已 CLOSED）。
- 冻结：r15 approved 且 P0/P1=0 → 语义修订提交（C-05/C-15/C-16）→ 三指纹/old-new blob → 已提交字节复核 → 仅元数据冻结（FROZEN/矩阵/载体 §8/旧 pin）→ check+17 pins；M2-C1 无字节变更登记（版本/指纹/no-diff/行为兼容依据）。
- 未运行项（pytest/.NET/build/IPC/DPAPI/迁移/竞态/泄漏）NOT_RUN。
