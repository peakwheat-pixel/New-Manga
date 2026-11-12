# 05 OCR、SFX 与 AI 翻译审查

**产品基线：** 10e4ee013835605800d3830fb960ae8d3aa04167
**阶段结论：** AUDIT-04、05、06、07 均 PARTIAL。

| 专项 | 实测结果 | 主要限制 |
|---|---|---|
| AUDIT-04 OCR / Detection | 定向合成回归 175 + 40 passed，EXIT 0；检查 provider 选路、fake OCR adapter 和坐标算子 | 真实权重、人工 GT、日/韩文准确率、真实 CPU inference、GUI NOT_RUN |
| AUDIT-05 SFX | 合成定向批次 247 passed / 3 deselected，EXIT 0；分类、策略、重检测、人工保护、provider 降级与重叠仲裁有覆盖 | 真实权重、GT、UI NOT_RUN；同位 primary/SFX 双 Region 为 AUDIT-05-CAND-001，待裁决 |
| AUDIT-06 Translation | 上下文专项 84 passed，EXIT 0；检查 payload、chapter 上下文、Region 映射、重试、超时/暂停边界与人工 Revision 保护 | 真实 API / 费用 / 取消语义 NOT_RUN；spend cap/idempotency 与 glossary 强制优先级候选待裁决 |
| AUDIT-07 Repair / Typesetting / Export | 38 pipeline、73 rendering、5 source-style、6 font-storage、7 searchable-export、7 revision-restore 各组 EXIT 0；Core/rerender/export 组 127 passed、3 failed、EXIT 1 | 三个失败关联 reader export hook options，待 ZCode 判断；真实模型、GT、GUI、屏幕缩放、视觉质量与用户字体许可 NOT_RUN |

## 证据

- AUDIT-04：reports/AUDIT-04-OCR-DETECTION-2026-11-13.md
- AUDIT-05/06：reports/AUDIT-05-06-SFX-TRANSLATION-2026-11-13.md
- AUDIT-07：reports/AUDIT-07-REPAIR-TYPESET-EXPORT-2026-11-13.md
- 对应测试源、原始日志和 JSON：AUDIT_EVIDENCE_INDEX.md

Mock、合成素材或 fake engine 的成功结果只支持其明确覆盖的代码路径，不是识别准确率、真实模型效果或付费服务通过证据。相关候选不在本审计中修复。
