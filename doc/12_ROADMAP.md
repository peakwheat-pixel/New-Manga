# Roadmap

This file is a short navigation view. The authoritative roadmap, dependency
graph, acceptance boundaries and historical Task audit live in
[REBASELINE_PLAN.md](REBASELINE_PLAN.md). Live execution state lives in
[STATUS.md](STATUS.md).

## Future architecture milestone

[M2 — Desktop Architecture Migration](REBASELINE_PLAN.md#architecture-decision-and-future-migration-registration) 已进入 `FIRST_WAVE_RELEASED / BOUNDED_IMPLEMENTATION`；[M2-I1](tasks/M2-I1.md)、[M2-I2](tasks/M2-I2.md)、[M2-R1](tasks/M2-R1.md) 均已独立 Review、集成并标 `done`（I1 R3 DeepSeek Harness Review approved，integration=`cff1e0a`）；[M2-UI1](tasks/M2-UI1.md) 已经 Antigravity 独立 Review approved 并集成标 `done`（integration=`5242f64`）。M2-D1=`done`，integration=`100abfb`；M2-C1/M2-S1 未释放。T3.2.1 Legacy Production Gate 保持独立 OPEN。

## Current order

1. **T1.1.2, T1.1.1, T1.2.1, T2.1.1, T2.2.1, T3.1.1**: verified complete; fixed commits and evidence are in the authoritative Plan.
2. **[T3.2.1 — Windows Packaging & Release Gate](tasks/T3.2.1.md)**：Legacy Production Gate `OPEN`，父 AC3=`BLOCKED`；REPAIR-13=`done`（`6fe7455`）、REPAIR-14=`done`（`296131b`）。M2 启动不改变父 Gate，具体阻塞与验证状态见 [STATUS](STATUS.md)。

Historical phases and task ledgers remain in place for traceability; they do
not override the rebaseline.
