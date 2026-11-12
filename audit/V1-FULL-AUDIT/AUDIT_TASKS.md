# 专项状态

## 段 A（历史基线 `349e61faff5f93067af5d4ce2d9e394e0d665b8c`）

- AUDIT-00: PASS（仅段 A 基线与清单；语义覆盖后续核对）
- AUDIT-01–14: NOT_TESTED（未完成；不迁移为段 B 结论）

## 段 B（当前产品基线 `10e4ee013835605800d3830fb960ae8d3aa04167`）

- AUDIT-00: PASS（静态项目盘点完成；结构图、模块索引、有效源码覆盖、启动/接口、schema/存储、模型 pin、测试/构建/发布与历史架构差异见 `reports/01_PROJECT_INVENTORY.md`；命令与基线核对见 `logs/audit-00-inventory-20261112.log`。外部模型文件字节和运行时行为未在本项验证）
- AUDIT-01: FAIL（阶段报告与正式 runner 复现见 `reports/AUDIT-01-02-ARCHITECTURE-STATIC-2026-11-12.md`、`logs/sidecar-lifecycle-probe-20261112T143133097703Z.log`、对应 JSON；`NM-AUD-0001` 证明取消/直接 dispose 后忽略 EOF 的 helper 子进程仍运行并已由 probe 清理。ZCode 对阶段交付 `ACCEPT`、维持 P2；真实 sidecar、UI、完整异常/状态/耦合链仍未验）
- AUDIT-02: BLOCKED（Python AST 语法扫描、.NET solution build PASS；`dotnet format whitespace` EXIT 2，1,556 项诊断；Python lint/type/security 工具未安装，.NET analyzers disabled，语义扫描未完成。详见阶段报告与对应 logs）
- AUDIT-03: NOT_TESTED（专项尚未完成；已有 `SEG-B-PROBES-001` 的目录 junction publication 证据与风险映射，完整导入路径审阅和合成素材隔离验证待做）
- AUDIT-04: NOT_TESTED（待模型链路静态核对/合成 GT；真实素材准确率具名受限）
- AUDIT-05: NOT_TESTED（待 SFX 契约、状态机与错误路由逐项核对）
- AUDIT-06: NOT_TESTED（待翻译配置/重试/超时/并发审阅；真实付费 API 不在本轮授权）
- AUDIT-07: NOT_TESTED（待修复/排版/导出链路和许可核对）
- AUDIT-08: FAIL（有限合成 DB 专项 284 passed / 0 skipped / EXIT 0；迁移 v1–v13→v14、关系保留、约束、并发、异常 rollback、意外退出恢复与关闭后路径移动有隔离证据。`SEG-B-PROBES-002` 重跑确认裸 I/O 错误且无 rollback ID。ZCode 首轮独立 Review `ACCEPT`，0 P0/P1/P2、2 P3：异常中断映射已补列；post-pinbackfill 门禁日志待本轮 pinbackfill。真实库、运行时任务状态、应用路径迁移、真实损坏恢复、断电及多文件部分写仍未验证。详见 `reports/AUDIT-08-SQLITE-PERSISTENCE-2026-11-13.md` 和 `reports/ZCODE-AUDIT-08-REVIEW-2026-11-13.md`）
- AUDIT-09: NOT_TESTED（待 Avalonia 静态页面覆盖审阅；真实 GUI 运行具名 BLOCKED）
- AUDIT-10: NOT_TESTED（待可重复 Core 合成样本微基准；GUI 性能具名 BLOCKED）
- AUDIT-11: FAIL（安全静态阶段报告 `reports/AUDIT-11-SECURITY-STATIC-2026-11-12.md`；`SEG-B-PROBES-001` 路径写越界与 `SEG-B-PROBES-002` restore I/O 恢复缺陷均为 Medium / High confidence，`NM-AUD-0001` 经 ZCode 复核为 P2。独立 Review `ACCEPT`，0 个 P0/P1/P2 阻断项；1 个 P3 扫描器源 SHA 差异已确认为移除尾随空格并披露，未重跑 scanner。Key/日志/命令/SQL/依赖等其余面为 PARTIAL 或具名 NOT_TESTED；真实 UI/vault、恶意文件 fuzz、Python 依赖漏洞数据库、竞态和远端可见性未验证）
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
