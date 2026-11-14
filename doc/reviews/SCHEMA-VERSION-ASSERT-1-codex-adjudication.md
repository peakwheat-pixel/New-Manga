---
task: SCHEMA-VERSION-ASSERT-1
adjudicator: codex (external, delegated by DSH 2026-11-15)
scope: 把测试里硬编码的 schema_version=9 改为读产品版本常量，是否算"放宽既有断言"
date: 2026-11-15
adjudication_base: main@688cd2bf90b7255e38b57aa5195e4fc2f09b7d06
---

# Codex 裁决：schema 断言的预期更新是否属于"放宽断言"

## 问题

项目纪律写明"不得放宽既有断言"。三处测试硬编码 `Assert.Equal(9, schema_version)`，而产品 schema
已到 14（`src/**/schema.py:965 MIGRATION_V14_NAME`，`default_migrations()` 注册 v1..v14）。
这 3 处断言在新 sidecar 下必然失败，但长期被 opt-in 环境变量 SKIP 而未暴露。

## 裁决

### 1. 方案 C 不属于"放宽既有断言"

**属于修正随产品迁移演进而过时的测试预期。** 判断标准是**是否削弱应验证的产品约束**，
不能仅因测试由红变绿而认定违规。

C 仍要求版本**精确相等**，拒绝低于或高于当前预期的版本；但不能称它比 `==9`"更强"，
两者是**预期基线不同**。本案夹具运行当前完整迁移链，并未固定测试 v9；因此将预期同步至
已存在的 v14 有代码依据。**此结论不授权修改冻结的历史证据。**

### 2. C 可用，优先采用测试内常量

放在 `NewManga.Host.Tests` 项目的 `Support/CoreSchema.cs`，定义
`internal static class CoreSchema`、`Current = 14`。

当前需求只有测试使用，**无须**把数据库实现版本新增为 Host 或 CoreClient 的产品契约；
Python Core 继续保持持久化权威。

### 3. 无需走"C 算放宽"的替代路径

A（改成 `== 14`）也是合法的预期更新，但仍有重复维护成本；B（`>= 9`）扩大接受范围，
**属于放宽**；D（标 BLOCKED 等回退 sidecar）缺乏回退 v9 的产品依据，不能据此要求回退。

## 事实核实清单（Codex 实际执行）

- 三处 `Assert.Equal(9, …)` 及所述行号均属实；都读取 `tests/fea11/support/ipc_seed.py` 生成的回执，
  相关 Fact 默认由 `NEWMANGA_FEA11_IPC=1` 启用。
- `ipc_seed.py:71` 调用 `MigrationRunner(conn, default_migrations()).apply_pending()`；
  `:87–96` 从数据库读取 `MAX(schema_version)` 写入回执，**未限制迁移至 v9**。
- `schema.py:56/58/938/965` 分别确认版本 14、v1/v13/v14 迁移名；`:990–1005` 实际注册 v1–v14。
- 以 `python -B` 在 SQLite **内存库**执行生产迁移链，成功应用连续 14 项，迁移表确有 v1–v14 共 14 条记录。
- `core_assembly.py:1221–1224` 确认启动日志生成逻辑；原 sidecar 日志及原新建库**未直接复核**
  （不将文档记录冒充本次实测）。
- `GATE3-SIDECAR-COVERAGE-1` AC6 明文要求"不得放宽任何断言"；该卡范围同时禁止修改测试，
  故本裁决**不自动扩大其实施范围**。

## 建议实施步骤（由 DSH 冻结范围后实施）

1. 新增测试常量 `Support/CoreSchema.cs`，仅替换三处预期值，保留其余业务断言。
2. 增加**默认执行、无需 IPC opt-in** 的跨语言守护：调用 Python `default_migrations()`，
   校验版本序列连续且最大值精确等于 `CoreSchema.Current`；**环境缺失应失败，不得静默跳过**。
3. **直接检查实际注册迁移**，避免仅用正则读取 `MIGRATION_V14_NAME`；
   **预期值不得取自被测回执**，否则会失去判别力。
4. 启用相关 opt-in 并补齐恢复环境后复跑，保留原失败记录，固定交付 commit，交上下文独立 Review。

**三处修复不等于 Release Gate 通过。**

## DSH 实施结果（2026-11-15，commit `07811dcad`）

按上述 1–3 实施，4 部分完成（复跑 11 passed / 2 failed，剩余 2 个非 schema、已记录为待归因）。
判别力实测：`CoreSchema.Current` 临时改 13 → 守护测试 FAIL（`Expected: 13, Actual: 14`），已还原。
