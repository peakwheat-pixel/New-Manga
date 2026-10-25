# 审计 DAG

P0: AUDIT-00 基线盘点 → P1: AUDIT-01/02 架构/静态 → P2: AUDIT-03/08 导入/数据 → P3: AUDIT-04/05/06/07 OCR/SFX/翻译/图像 → P4: AUDIT-09 UI → P5: AUDIT-10/11/12 性能/安全/交付 → P6: AUDIT-13/14 E2E/需求覆盖 → P7: 去重整改 → P8: 证据复核/Release Gate。

独立只读子任务：inventory_scan（Luna medium）、data_security（Sol medium）、pipeline_audit（Sol medium）；仅主控写入。所有专项需要明确结果/限制；无证据不能PASS。
