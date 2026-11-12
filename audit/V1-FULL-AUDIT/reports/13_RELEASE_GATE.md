# 13 Windows / V1 Release Gate

**结论：BLOCKED**
**产品基线：** 10e4ee013835605800d3830fb960ae8d3aa04167
**适用范围：** 当前审计记录的 New Manga V1 / Windows 产品状态。

## 阻断依据

1. 已有三个未修复且已 triage 的产品 findings：SEG-B-PROBES-001（Medium / High confidence）、SEG-B-PROBES-002（Medium / High confidence）和 NM-AUD-0001（P2）。AUDIT-03、AUDIT-08、AUDIT-11、AUDIT-01 分别记录对应 FAIL；修复不在本审计授权范围。
2. AUDIT-02 为 BLOCKED；AUDIT-04/05/06/07/09/10/12/13/14 为 PARTIAL，部分检查面仍有具名 NOT_RUN 或候选待裁决。
3. 当前 Python Core 全量 pytest 为 3,519 passed / 16 failed / 10 skipped / 11 warnings，EXIT 1。Avalonia TestHost 为 8/8 runner EXIT 1、TRX 0 tests；Core/Wire smoke EXIT 1 且 7 项 Core hook 为 BLOCKED-SANDBOX-GRANT。
4. 没有当前基线安装包 provenance 和 clean Windows install / upgrade / rollback / uninstall 验证。历史 zip/setup 不绑定当前基线；本 Task 按范围未安装、执行或发布。
5. 11 个候选项仍需 ZCode 判定正式 finding、需求归属或优先级；AUDIT-11-INC-001 的当前远端可见性未知。
6. 真实 manga / 模型 / 付费 API / 完整 UI 流程没有形成覆盖本产品关键路径的端到端证据；部分结果仅来自 synthetic fixtures。

## Gate 解释

原始审计准入规则允许最终审计中存在 FAIL / BLOCKED / NOT_TESTED，但关键证据缺失或有未处置风险时不能以主观信心改判 PASS 或 CONDITIONAL。当前符合 BLOCKED 条件。AUDIT-09 的 Release build EXIT 0 和治理门禁通过，只证明各自窄面，不解除产品发布阻断。

本 Gate 代表产品发布准备度，不等同于审计文档是否完成。当前 P7 综合交付已形成；最终 ZCode fresh-context review、候选 adjudication 与 Task lifecycle 尚未完成，因此审计 Task 仍 in_progress。

## Release Gate 解锁所需证据

- 由 Owner / Integrator 明确处置并验证三个已 triage findings；数据安全、restore contract 或生命周期修复均应单独 Task 实现并独立 Review。
- ZCode 对 11 个候选和 AUDIT-11-INC-001 作正式处置；需求归属、severity、弃置理由和后续 Task 均写入台账。
- 补齐可安全执行的完整 GUI / Core / Host 关键流程与 Avalonia TestHost；所有 blocked/skipped 项继续保留原结果。
- 对当前固定产品 commit 生成并固定 Windows 包，完成 clean install、启动、升级/回退、四个一级页面可达性与卸载矩阵。
- 完成模型/API 与代表性质量验证，或由产品 Owner 明确接受有边界的限制；没有人工 GT 时不宣称识别准确率达标。
- 完成当前交付 head 的 Canonical Evidence / default governance / TaskPath / verify_pins / API inventory 门禁，并取得独立 final Review。
- 对私有素材传播风险形成可追溯调查结论；任何远端删除、history rewrite 或发布动作另需独立授权与审查。

**当前决定：不建议发布，不满足 PASS 或 CONDITIONAL。**
