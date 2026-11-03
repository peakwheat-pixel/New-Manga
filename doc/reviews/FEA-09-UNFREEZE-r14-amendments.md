# FEA-09 UNFREEZE 修订提案 r14（r13 + R13-001/R13-002）

状态：**PROPOSAL r14 — 待第十四次独立复核**（2026-11-04）
作者：DSH；依据：`doc/reviews/FEA-09-UNFREEZE-r13-review.md`（Codex 独立，`changes_requested` P0=0/P1=2/P2=0，reviewed_head `a7f636300`，SHA-256 `8f1a520c…` 为 r13 提案）。
**r14 = r13 + 下列两处替换**；其余不变。r12 review 已补归档（`doc/reviews/FEA-09-UNFREEZE-r12-review.md`）。

## R13-001：scroll_offset_y 单位（替换 r13 §R12-001 第 3 条不变量句）

```text
offset 语义（沿用 M2-C1，不归一化）：
- Webtoon：scroll_offset_y = 逻辑 Page 原图像素坐标（非负整数；既有语义）。
- 分页章节：scroll_offset_y = 0。
- resume 且保存页可读：initial_position={保存页, 保存 scroll_offset_y 原值}。
- 保存页不可读/已移出/回绕/beginning/无进度：initial_position={替代可读页, scroll_offset_y: 0}。
- 不变量：page_id ∈ pages[]；offset 为 M2-C1 既有单位（像素/分页 0），不引入 0..1 归一化。
```

## R13-002：移出页锚点（替换 r13 §R12-001 第 3 条"保存页已不在 V"段）

```text
保存页已不在 V 且 DB 页行存在时：
  canonical order = (sort_order ASC, page_id ASC)；
  锚点 a = V 页中满足 (P.sort_order, P.page_id) < (保存页.sort_order, 保存页.page_id) 的页数
          （完整二元组比较，含同 sort_order 的 page_id 比较；0-based 插入位置）。
  例：V=[(10,a),(10,c)]、保存页=(10,b) → (10,a) 小于保存页 → a=1 → 首个 logical_order>=1 的可读页 = (10,c)。
- 无 DB 页行 → a=0。
- initial_position={首个 logical_order>=a 的可读页（无则回绕到最小可读页），offset 0}。
```

## 同步与冻结

- 替换 r13 §R12-001 中对应两句；其余条款（pages[]=可读全集、beginning/resume 分派、saved_progress 保留、零可读/V 空→TARGET_NOT_FOUND、错误边界、管理诊断路径、无 wire 扩展）不变。
- 冻结：r14 approved 且 P0/P1=0 → 语义修订提交（C-05/C-15/C-16）→ 三指纹/old-new blob → 已提交字节复核 → 仅元数据冻结（FROZEN/矩阵/载体 §8/旧 pin）→ check+17 pins；M2-C1 无字节变更登记（版本/指纹/no-diff/行为兼容依据）。
- 未运行项（pytest/.NET/build/IPC/DPAPI/迁移/竞态/泄漏）NOT_RUN。
