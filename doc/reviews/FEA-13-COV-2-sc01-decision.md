# FEA-13-COV-2 裁决：SC-B01「源引用与授权元数据入包」（R-004）

- 裁决人：DSH（Lead / Integrator；用户 2026-11-08 全部授权）
- 日期：2026-11-09
- 触发：`FEA-13-BK2-1` Review r1 R-003 把 C-09 SC-B01 的「源引用与授权元数据入包」移交片 2；`FEA-13-COV-2` Review r1/r1b 的 R-004 指出本片未落实也未裁决。

## 裁决

1. **本片（FEA-13-COV-2）不实现 SC-B01 的源引用/授权元数据入包**。理由：
   - 该数据当前写域在 **Host 侧**（`SourceAccessRegistry` 私有存储 `<DataRoot>/host/source-access/registry.v1.dat`，C-06 冻结语义），不在 Core `nmbak` 的写域内；
   - 强行并入本片会把「覆盖清单」扩成跨层契约变更（Host→Core staging 输入面），超出片 2 冻结范围。
2. **单列后续 Task**：`FEA-13-SRC-6`（proposed，占位）——「备份包源引用/授权元数据段（SC-B01 ④）」，依赖 `FEA-13-COV-2` + Host registry 的备份交接面；**不进入本次 6 片主序列**，由 DSH 在片 2–5 收口后决定是否立项。
3. **C-09 冻结记录不新增 errata**：SC-B01 的该项仍属有效要求，只是实现载体另行立项；为避免静默丢失，本裁决文件与 `FEA-13-COV-2` 卡 `out_of_scope` 同时登记。
4. BK2-1 卡内 R-003 处置表的「④ 归片 2」措辞已收窄为「独立裁决」；本文件为该措辞的落地裁决。

## 不构成什么

- 不构成 SC-B01 的修改或撤销；
- 不构成 `FEA-13-SRC-6` 的释放授权；
- 不改任何契约字节与 18 pins。
