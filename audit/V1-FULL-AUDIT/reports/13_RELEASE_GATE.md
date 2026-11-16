# 13 Windows / V1 Release Gate（Codex 裁决后版本）

**结论：BLOCKED**
**产品基线：** 10e4ee013835605800d3830fb960ae8d3aa04167
**裁决来源：** 2026-11-14 用户指令：所有任务交 DSH，DSH 自动裁决/规划、全部授权、无需用户介入。ZCode 当前不可用（`Select a model` / 缺 `@zcode/tui`；quota 1310 为历史），Codex 最终回退复审（`reviewed_head=89e16b9d6`）结论 **ACCEPT_WITH_LIMITATIONS**（审计交付可接受，非产品通过），并维持 BLOCKED；最新已记录四项门禁批次为 `46a8fe6e`，最终门禁在 DSH 集成后的 delivery head 重跑并记录。

## 阻断依据

1. **未修复的开放 finding 共 7 项**：3 项原已 triage（`SEG-B-PROBES-001`、`SEG-B-PROBES-002` 为 Medium / High confidence；`NM-AUD-0001` 为 P2）加 4 项 Codex 新裁 finding（`AUDIT-07-CAND-001` P2；`AUDIT-09-CAND-001` P3；`AUDIT-12-CAND-001` P3 交付工具；`AUDIT-14-CAND-001` P3 优先级文档，非产品 P0–P3 计数）。产品 P0=0、P1=0、P2=2、P3=2；P0/P1 为当前已分配数量，不表示已证明不存在。SEG-B 两项保持独立量表，不映射 P 级。修复不在本审计授权范围。
2. AUDIT-02 为 BLOCKED；AUDIT-01/03/08/11 为 FAIL；AUDIT-04/05/06/07/09/10/12/13/14 为 PARTIAL，部分检查面仍有具名 NOT_RUN。
3. 当前 Python Core 全量 pytest 为 3,519 passed / 16 failed / 10 skipped / 11 warnings，EXIT 1；Avalonia TestHost 为 8/8 runner EXIT 1、TRX 0 tests；Core/Wire smoke EXIT 1 且 7 项 Core hook 为 BLOCKED-SANDBOX-GRANT。
4. 没有当前基线安装包 provenance 和 clean Windows install / upgrade / rollback / uninstall 验证；历史 zip/setup 不绑定当前基线，本 Task 未安装、执行或发布。
5. `AUDIT-11-INC-001` 当前远端可见性未知（Codex 维持 INVESTIGATE，不分配 severity）；不得写成已公开或已消除。
6. 真实 manga / 模型 / 付费 API / 完整 UI 流程没有形成覆盖关键路径的端到端证据；部分结果仅来自 synthetic fixtures。
7. Codex 十一轮回退 Review 结论均为 **REJECT**：历史原因是状态/计数/重复 ID/门禁 pin 等；第九轮确认 535/535 pins 与计数自洽，仅剩当前指针同步（AUDIT_PLAN/AUDIT_STATUS/Task AC4·Rolling/FINAL/13_GATE）。AC3/AC4 尚不能据此收口；该 REJECT 与产品发布阻断相互独立但同向。

## Gate 解释

原始审计准入规则允许最终审计中存在 FAIL / BLOCKED / NOT_TESTED，但关键证据缺失或有未处置风险时不能以主观信心改判 PASS 或 CONDITIONAL。当前符合 BLOCKED 条件。AUDIT-09 的 Release build EXIT 0、535 条 pins 的字节可核验性与治理门禁通过，只证明各自窄面，不解除产品发布阻断。

本 Gate 代表产品发布准备度，不等同于审计文档是否完成。审计文档返修（Codex REJECT 所指）已完成/进行时，产品发布阻断仍不变。

## Release Gate 解锁所需证据

- 由 Owner / Integrator 明确处置并验证 7 项开放 finding；数据安全、restore contract、sidecar 生命周期、导出 P2、Reader 提示与 publish 输出路径修复均应单独 Task 实现并独立 Review。
- 完成 `AUDIT-11-INC-001` 的只读远端可见性调查或由产品 Owner 明确接受该未知风险；任何删除、history rewrite 或发布动作另需授权与审查。
- 补齐可安全执行的完整 GUI / Core / Host 关键流程与 Avalonia TestHost；所有 blocked/skipped 项继续保留原结果。
- 对当前固定产品 commit 生成并固定 Windows 包，完成 clean install、启动、升级/回退、四个一级页面可达性与卸载矩阵。
- 完成模型/API 与代表性质量验证，或由产品 Owner 明确接受有边界的限制；没有人工 GT 时不宣称识别准确率达标。
- 完成当前交付 head 的 Canonical Evidence / default governance / TaskPath / verify_pins / API inventory 门禁，并取得独立最终 Review（AC3/AC4 收口后）。

**当前决定：不建议发布，不满足 PASS 或 CONDITIONAL。**

## 条件 6 登记（append-only，2026-11-16，DSH R16）

条件 6 = 上文 `:30` 的「完成当前交付 head 的 Canonical Evidence / default governance / TaskPath / verify_pins /
API inventory 门禁，并取得独立最终 Review（AC3/AC4 收口后）」。

- **独立最终 Review 已登记**：`doc/reviews/MAINT-1-GATE-CONDITION-6-FINAL-REVIEW-2026-11-14.md`（182 行，
  引入 `d38c624f7`），verdict `MECHANICAL_PASS / CONDITION_6_NOT_CLOSABLE`（`:4`）；其四项完成态缺口
  （① MAINT-1 无 Canonical Evidence 载体 ② 交付 head 未冻结 ③ 三指针精度 ④ 本 Review 未登记）已逐项关闭。
- **判定（仅条件 6）**：由「未关闭 / `NOT CLOSABLE`」改为 **已关闭**；逐项实测（命令 + EXIT + 文件:行）见
  `doc/reviews/MAINT-1-GATE-CONDITION-6-CLOSURE-2026-11-16.md`。
- **其余阻断依据不变**：本文件 `:7-15` 的 7 条阻断与 `:32` 的发布决定**未改**，Gate 总体仍 **BLOCKED**
  （条件 3 人眼目视 / 条件 4 签名与真机安装矩阵 / 条件 5 人工 GT 质量基线 仍开放）。
