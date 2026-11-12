# 专项状态

## 段 A（历史基线 `349e61faff5f93067af5d4ce2d9e394e0d665b8c`）

- AUDIT-00: PASS（仅段 A 基线与清单；语义覆盖后续核对）
- AUDIT-01–14: NOT_TESTED（未完成；不迁移为段 B 结论）

## 段 B（当前产品基线 `10e4ee013835605800d3830fb960ae8d3aa04167`）

- AUDIT-00: PASS（仅当前 Git/environment/source baseline；启动入口、命令面、DB、资源 pin 和结构/模块索引待补；见 `reports/00_BASELINE-SEGMENT-B.md` 与 ZCode 恢复裁决）
- AUDIT-01: NOT_TESTED（待架构边界、异常传播、资源生命周期和依赖审阅）
- AUDIT-02: NOT_TESTED（待零安装静态扫描和重点代码复核）
- AUDIT-03: NOT_TESTED（待导入路径审阅和合成素材隔离验证）
- AUDIT-04: NOT_TESTED（待模型链路静态核对/合成 GT；真实素材准确率具名受限）
- AUDIT-05: NOT_TESTED（待 SFX 契约、状态机与错误路由逐项核对）
- AUDIT-06: NOT_TESTED（待翻译配置/重试/超时/并发审阅；真实付费 API 不在本轮授权）
- AUDIT-07: NOT_TESTED（待修复/排版/导出链路和许可核对）
- AUDIT-08: NOT_TESTED（已有 probe F1/F2 需登记；待隔离数据库异常模拟）
- AUDIT-09: NOT_TESTED（待 Avalonia 静态页面覆盖审阅；真实 GUI 运行具名 BLOCKED）
- AUDIT-10: NOT_TESTED（待可重复 Core 合成样本微基准；GUI 性能具名 BLOCKED）
- AUDIT-11: NOT_TESTED（待 Key、日志脱敏、路径、IPC 沙箱和依赖许可静态审阅；既有素材传播风险证据仅作背景）
- AUDIT-12: NOT_TESTED（待构建/打包静态审阅；干净 Windows 安装实测具名 BLOCKED）
- AUDIT-13: NOT_TESTED（待 E/F/G/H 合成场景；真实漫画场景具名 BLOCKED）
- AUDIT-14: NOT_TESTED（待 V1 承诺/实现/Mock/历史债务矩阵）

## 段 B suite 级状态（与 AUDIT-01–14 逐项状态分离）

- `pytest`（Python Core 限定证据）：EXIT 1；3,519 passed / 16 failed / 10 skipped / 11 warnings；失败详情见 `logs/pytest-segment-b-20261112T081732598825Z.log`，汇总见 `reports/PYTEST-RESULT-SEGMENT-B-2026-11-12.md`
- `probes`（审计工具探针）：EXIT 1；2 项隔离 probe 确认为 Medium / High confidence 风险，1 项目录穿越覆盖预期未复现且防线已验证；详见 `reports/PROBES-RESULT-SEGMENT-B.md` 与 `reports/PROBE-TRIAGE-SEGMENT-B-2026-11-12.md`
- `dotnet`（Avalonia headless，8 个测试项目逐项）：`BLOCKED-TESTHOST-ACCESS`；8/8 runner EXIT 1、TRX 0 tests、status guard 8/8 identical；原始结果与 ZCode 裁决见 `reports/DOTNET-RESULT-SEGMENT-B-2026-11-12.md`
- `smoke-core,wire`：EXIT 1 / 程序 FAIL；10 项限定 PASS（Core 4、Wire 6）；7 项 Core 检查记 `BLOCKED-SANDBOX-GRANT`，未能执行预期 hook 行为；frontend/packaged 显式 SKIP。ZCode adjudication 与证据边界见 `reports/SMOKE-RESULT-SEGMENT-B-2026-11-12.md`
- `governance`：runner default check EXIT 0（3 warnings），生成 HEAD=`3e0c960a482f5420666faec82d9c0f89e8396159`；最终 Task pinbackfill 后仍需复跑 default + TaskPath、18 pins 与 API 门禁
- `frontend/rust/desktop/npm-audit/packaged`：NOT_RUN-legacy
- 真实 GUI：BLOCKED（headless 测试不替代真实 UI 会话）
