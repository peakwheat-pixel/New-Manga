# 02 架构审查

**产品基线：** 10e4ee013835605800d3830fb960ae8d3aa04167
**审查范围：** AUDIT-01 架构与生命周期；AUDIT-02 静态质量检查。
**阶段结论：** AUDIT-01 FAIL；AUDIT-02 BLOCKED。

## 主要结果

- 当前桌面调用链为 Avalonia App → C# Host → Python Core / Host Bridge sidecars。Python 静态导入图记录 268 个源文件、655 条本地 import edge、9 个动态 import 调用点和 1 个 SCC；.NET 项目图为 10 个项目、13 条引用边，无 project-reference cycle。此结果不覆盖完整运行时依赖或方法级耦合。
- AUDIT-01 的 sidecar 生命周期缺陷 NM-AUD-0001 已由隔离 helper 经实际 SidecarProcess API 复现：启动前取消和直接 DisposeAsync 返回后，忽略 stdin EOF 的 helper 子进程仍存活；probe 后显式清理了 helper。真实 Python sidecar 行为、用户遇到概率和影响尚未测。
- AUDIT-02 的 Python AST 检查和 Avalonia solution build 通过；dotnet format whitespace 报告 1,556 项 WHITESPACE 诊断并 EXIT 2。Python lint/type/security 工具未安装，.NET SDK analyzers 已关闭，语义级代码质量扫描未完成。

## 验证与限制

- Avalonia solution build：EXIT 0，0 warnings / 0 errors。该结果只证明编译成功。
- Avalonia TestHost：8/8 runner EXIT 1、TRX 0 tests，状态为 BLOCKED-TESTHOST-ACCESS；没有将构建结果当作测试通过。
- Wire smoke 6/6 PASS；Core smoke 4 PASS、7 项 BLOCKED-SANDBOX-GRANT；frontend / packaged SKIP。
- 本轮没有改产品源码、原有测试、共享契约、Schema、依赖或构建配置。

## 证据

- 完整阶段矩阵及命令：reports/AUDIT-01-02-ARCHITECTURE-STATIC-2026-11-12.md
- Finding 台账：AUDIT_ISSUES.md 中的 NM-AUD-0001
- 静态图、构建、whitespace、TestHost 与 smoke 的原始日志和结果：AUDIT_EVIDENCE_INDEX.md

该审查不表示全审完成或 Release Gate 通过。
