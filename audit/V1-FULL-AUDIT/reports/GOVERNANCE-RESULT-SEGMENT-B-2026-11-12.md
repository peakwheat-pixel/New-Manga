# 段 B governance suite 结果

- Runner：`python audit/V1-FULL-AUDIT/tests/audit_runner.py governance`
- 实际命令：`pwsh -NoProfile -File tools/governance/check.ps1`
- 生成时 HEAD：`3e0c960a482f5420666faec82d9c0f89e8396159`；branch：`main`
- started：`2026-11-12T08:53:03.591884+00:00`；elapsed：`1.281s`
- EXIT=0，`Governance check: PASS (3 warnings)`。三条 warning 为：10 个非终态 Task 的治理提示、`doc/STATUS.md` 达预算 80%、`doc/REBASELINE_PLAN.md` 达预算 80%。完整 argv、stdout、生成 HEAD 和 EXIT 见 Canonical Evidence 所 pin 的 log/JSON。

此 runner suite 执行默认 `check.ps1`，不替代 `-TaskPath`、`verify_pins.ps1` 或 API 清单门禁。最终 Task pinbackfill 后仍需在最终审计 HEAD 复跑 default + TaskPath、18 pins、API 1/79/6=86，并如实记录。此结果不关闭 Task、不通过 Release Gate，也不改变 AUDIT-01–14 的具名阻断状态。
