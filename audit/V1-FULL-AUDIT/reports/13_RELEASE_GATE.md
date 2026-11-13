# 13 Windows / V1 Release Gate（Codex 裁决后版本）

**结论：BLOCKED**
**产品基线：** 10e4ee013835605800d3830fb960ae8d3aa04167
**裁决来源：** Codex 七轮独立 Review（`d92859c9a`、`226eb048`、`42810143b`、`6350081a`、`1ae79bb99`、`c2f5bc827`、`9bd7264ca`；对应 `reports/CODEX-*REVIEW-2026-11-13.md`）均明确维持 BLOCKED，不满足 PASS 或 CONDITIONAL。

## 阻断依据

1. **未修复的开放 finding 共 7 项**：3 项原已 triage（`SEG-B-PROBES-001`、`SEG-B-PROBES-002` 为 Medium / High confidence；`NM-AUD-0001` 为 P2）加 4 项 Codex 新裁 finding（`AUDIT-07-CAND-001` P2；`AUDIT-09-CAND-001` P3；`AUDIT-12-CAND-001` P3 交付工具；`AUDIT-14-CAND-001` P3 优先级文档，非产品 P0–P3 计数）。产品 P0=0、P1=0、P2=2、P3=2；P0/P1 为当前已分配数量，不表示已证明不存在。SEG-B 两项保持独立量表，不映射 P 级。修复不在本审计授权范围。
2. AUDIT-02 为 BLOCKED；AUDIT-01/03/08/11 为 FAIL；AUDIT-04/05/06/07/09/10/12/13/14 为 PARTIAL，部分检查面仍有具名 NOT_RUN。
3. 当前 Python Core 全量 pytest 为 3,519 passed / 16 failed / 10 skipped / 11 warnings，EXIT 1；Avalonia TestHost 为 8/8 runner EXIT 1、TRX 0 tests；Core/Wire smoke EXIT 1 且 7 项 Core hook 为 BLOCKED-SANDBOX-GRANT。
4. 没有当前基线安装包 provenance 和 clean Windows install / upgrade / rollback / uninstall 验证；历史 zip/setup 不绑定当前基线，本 Task 未安装、执行或发布。
5. `AUDIT-11-INC-001` 当前远端可见性未知（Codex 维持 INVESTIGATE，不分配 severity）；不得写成已公开或已消除。
6. 真实 manga / 模型 / 付费 API / 完整 UI 流程没有形成覆盖关键路径的端到端证据；部分结果仅来自 synthetic fixtures。
7. Codex 五轮 Review 结论均为 **REJECT**：历史 REJECT 原因是状态/计数/重复 ID/门禁 pin 等；第五轮确认 483/483 pins 与计数自洽，仅剩当前摘要与专项报告/索引旧措辞的文档收敛；AC3/AC4 尚不能据此收口。该 REJECT 与产品发布阻断相互独立但同向。

## Gate 解释

原始审计准入规则允许最终审计中存在 FAIL / BLOCKED / NOT_TESTED，但关键证据缺失或有未处置风险时不能以主观信心改判 PASS 或 CONDITIONAL。当前符合 BLOCKED 条件。AUDIT-09 的 Release build EXIT 0、522 条 pins 的字节可核验性与治理门禁通过，只证明各自窄面，不解除产品发布阻断。

本 Gate 代表产品发布准备度，不等同于审计文档是否完成。审计文档返修（Codex REJECT 所指）已完成/进行时，产品发布阻断仍不变。

## Release Gate 解锁所需证据

- 由 Owner / Integrator 明确处置并验证 7 项开放 finding；数据安全、restore contract、sidecar 生命周期、导出 P2、Reader 提示与 publish 输出路径修复均应单独 Task 实现并独立 Review。
- 完成 `AUDIT-11-INC-001` 的只读远端可见性调查或由产品 Owner 明确接受该未知风险；任何删除、history rewrite 或发布动作另需授权与审查。
- 补齐可安全执行的完整 GUI / Core / Host 关键流程与 Avalonia TestHost；所有 blocked/skipped 项继续保留原结果。
- 对当前固定产品 commit 生成并固定 Windows 包，完成 clean install、启动、升级/回退、四个一级页面可达性与卸载矩阵。
- 完成模型/API 与代表性质量验证，或由产品 Owner 明确接受有边界的限制；没有人工 GT 时不宣称识别准确率达标。
- 完成当前交付 head 的 Canonical Evidence / default governance / TaskPath / verify_pins / API inventory 门禁，并取得独立最终 Review（AC3/AC4 收口后）。

**当前决定：不建议发布，不满足 PASS 或 CONDITIONAL。**
