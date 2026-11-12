# 审计 DAG

P0: AUDIT-00 基线盘点 → P1: AUDIT-01/02 架构/静态 → P2: AUDIT-03/08 导入/数据 → P3: AUDIT-04/05/06/07 OCR/SFX/翻译/图像 → P4: AUDIT-09 UI → P5: AUDIT-10/11/12 性能/安全/交付 → P6: AUDIT-13/14 E2E/需求覆盖 → P7: 去重整改 → P8: 证据复核/Release Gate。

独立只读子任务：inventory_scan（Luna medium）、data_security（Sol medium）、pipeline_audit（Sol medium）；仅主控写入。所有专项需要明确结果/限制；无证据不能PASS。

2026-11-12 范围裁决：段 A 固定基线 `349e61faff5f93067af5d4ce2d9e394e0d665b8c`，其既有结果封存；段 B 当前审计基线为 `10e4ee013835605800d3830fb960ae8d3aa04167`，AUDIT-00–14 均需按真实证据复核。素材仅元数据级只读；不得传播素材或实施任何远端处置。

2026-11-12 ZCode 测试范围裁决：AUDIT-01–14 原始逐项清单缺失，全部登记为 `BLOCKED-ORIGINAL-CHECKLIST-MISSING`（未测试）；不得从阶段标签重建检查点。该缺口不阻断限定 suite 级证据采集，suite 通过不改变逐项状态。当前 suite 顺序：probes → Python Core pytest → 8 个 Avalonia `.NET` 测试项目逐项 → smoke `core,wire` → governance。`frontend/rust/desktop/npm-audit/packaged` 为 `NOT_RUN-legacy`；真实 GUI 为 `BLOCKED`。执行边界与命令见 `reports/TEST-EXECUTION-ADJUDICATION-2026-11-12.md`。
