# 审计 DAG

P0: AUDIT-00 基线盘点 → P1: AUDIT-01/02 架构/静态 → P2: AUDIT-03/08 导入/数据 → P3: AUDIT-04/05/06/07 OCR/SFX/翻译/图像 → P4: AUDIT-09 UI → P5: AUDIT-10/11/12 性能/安全/交付 → P6: AUDIT-13/14 E2E/需求覆盖 → P7: 去重整改 → P8: 证据复核/Release Gate。

独立只读子任务：inventory_scan（Luna medium）、data_security（Sol medium）、pipeline_audit（Sol medium）；仅主控写入。所有专项需要明确结果/限制；无证据不能PASS。

2026-11-12 范围裁决：段 A 固定基线 `349e61faff5f93067af5d4ce2d9e394e0d665b8c`，其既有结果封存；段 B 当前审计基线为 `10e4ee013835605800d3830fb960ae8d3aa04167`，AUDIT-00–14 均需按真实证据复核。素材仅元数据级只读；不得传播素材或实施任何远端处置。

2026-11-12 原始清单恢复后的执行计划（ZCode 裁决）：AUDIT-01–14 逐项目标以 `source/ORIGINAL-USER-AUDIT-INSTRUCTIONS-2026-10-24.txt` 为准，当前架构映射见 `reports/ZCODE-ORIGINAL-SCOPE-READJUDICATION-2026-11-12.md`。AUDIT-00 静态项目盘点 limited PASS；AUDIT-01 `FAIL`（`NM-AUD-0001` 经受控 helper 复现，ZCode 已 ACCEPT 并维持 P2）；AUDIT-02 `BLOCKED`，见 `reports/AUDIT-01-02-ARCHITECTURE-STATIC-2026-11-12.md`。既有 suite 映射和 AUDIT-11 安全静态阶段报告已完成，后者为 `FAIL`（`SEG-B-PROBES-001/002`），其矩阵其余项按报告列出的 PARTIAL/NOT_TESTED 保持原样。下一步顺序：AUDIT-08 隔离数据库 → AUDIT-05/06 契约/流程审阅 → AUDIT-14 覆盖/债务矩阵 → AUDIT-03/04/07/10/13 合成验证 → AUDIT-09/12 能力允许的静态/运行核验 → 完整问题/整改/Release Gate/最终报告。原 suite 执行边界见 `reports/TEST-EXECUTION-ADJUDICATION-2026-11-12.md`；frontend/rust/desktop/npm-audit/packaged 仍为 `NOT_RUN-legacy`，真实 GUI、TestHost、sandbox grant、干净 Windows、付费 API、私有素材内容仍按具体子项 `BLOCKED`，不得用替代证据冒充实测。
