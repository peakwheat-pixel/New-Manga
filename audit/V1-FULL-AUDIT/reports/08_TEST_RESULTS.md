# 08 测试结果总览

**产品基线：** 10e4ee013835605800d3830fb960ae8d3aa04167
**解释规则：** 以下结果按 suite / 专项分别陈列；一个 suite PASS 不代表其他专项或完整产品通过。

## 段 B 广泛测试

| Suite | 结果 | 解释 |
|---|---|---|
| Python Core pytest | EXIT 1；3,519 passed / 16 failed / 10 skipped / 11 warnings | 保留 16 个失败及其完整日志；不在本审计范围内修复 |
| Avalonia TestHost | 8/8 runner EXIT 1；TRX 0 tests | BLOCKED-TESTHOST-ACCESS，未执行到测试用例 |
| Core/Wire smoke | EXIT 1；Wire 6 PASS，Core 4 PASS、7 BLOCKED-SANDBOX-GRANT | frontend / packaged SKIP |
| Audit-01/02 solution build | EXIT 0；0 warnings / 0 errors | 编译，不等于测试 |
| Audit-09 Release build | EXIT 0；0 warnings / 0 errors | 未安装或发布 |

## 定向专项测试

- AUDIT-03：Core 87 passed；ReferencedSource 77 passed；两组 EXIT 0。
- AUDIT-04：provider 175 passed；Core detection 40 passed；EXIT 0。
- AUDIT-05/06：SFX 247 passed / 3 deselected、translation context 84 passed；EXIT 0。
- AUDIT-07：pipeline 38、rendering 73、source-style 5、font-storage 6、searchable-export 7、revision-restore 7 各 EXIT 0；Core/rerender/export 127 passed / 3 failed，EXIT 1。
- AUDIT-08：有限合成 DB 284 passed / 0 skipped；EXIT 0。独立故障 probe 的 EXIT 0 表示 finding 成功复现，不表示产品恢复通过。
- AUDIT-10：4 项合成 microbench，每项 20 个 timed samples；无正式阈值、I/O 或 soak。
- AUDIT-13：Core acceptance 31 passed / 0 skipped；EXIT 0，只覆盖部分 synthetic A/D/E/G/H。

## 证据

各项原始命令、时点、generated HEAD、EXIT、日志与 JSON 由 AUDIT_EVIDENCE_INDEX.md 索引；全阶段状态见 AUDIT_TASKS.md。不得把 NOT_RUN、SKIP、BLOCKED 或候选 finding 混写成 PASS。
