# M2-RC2 sidecar 隔离证据（RC2-AC2，F-05）

## 结论

resource-channel sidecar（`python -m infrastructure.resource_channel.host_bridge`）经 F-05 修复后，导入面只含 resource channel 所需模块；`infrastructure.filesystem`、`infrastructure.sqlite`、`infrastructure.sqlite.reading_export`、`domain.books.*` 不再被传递加载。产品侧既有消费方 `from infrastructure import sqlite` 经 PEP 562 惰性导入保持可用。

## 修前证据（fail-before-pass 对照）

- 文件：[raw/sidecar-import-before-fix.log](raw/sidecar-import-before-fix.log)
- 抓取时机：**任何代码修改之前**（claim head `b4a78f0c`，2026-09-27T07:34:49Z）。
- 内容：headless 子进程 `import infrastructure.resource_channel.host_bridge` 后，项目模块集合包含：
  - `infrastructure.filesystem`
  - `infrastructure.sqlite`
  - `infrastructure.sqlite.reading_export`
  - `domain.books` / `domain.books.entities`
- 结论：F-05 描述的脆弱边界真实存在——上述 `__init__` 任何一天引入重依赖（如 PySide6），sidecar 即被拖垮。这构成修改 `src/infrastructure/__init__.py`（Task 条件允许路径）的必要性证据。

## 修复

`src/infrastructure/__init__.py` 改为 PEP 562 `__getattr__` 惰性导入（唯一触碰的禁改候选路径；理由与证据在 Task/Handoff 记录）。`infrastructure/resource_channel/__init__.py` 与 `application/**` 本来就轻，无需改动。

## 修后门禁（多层）

| 层 | 实现 | 证据 |
|---|---|---|
| pytest 子进程隔离门禁 | `tests/m2_resource_channel/test_sidecar_isolation.py`：干净子进程导入 sidecar/loader 入口，项目模块集合按白名单门禁；另验证 `from infrastructure import sqlite` 惰性路径仍可用 | `python -m pytest tests/m2_resource_channel/test_sidecar_isolation.py -q`（4 passed） |
| E2E headless 隔离检查 | `run_e2e.py` 第 3 阶段，同样子进程门禁 | [raw/e2e-sidecar-import-isolation.log](raw/e2e-sidecar-import-isolation.log) |
| **真实启动**模块 dump | sidecar `main()` 在 `M2RC2_MODULE_DUMP` 指定时写实际加载的 `sys.modules`；E2E 的 PROBE 与 INTERACTIVE 两个阶段各 dump 一份并按白名单门禁 | `raw/e2e-*.log` 汇总 + `%TEMP%/m2rc2-lab/sidecar-modules-*.json` |

## 边界说明

- 白名单口径：项目内允许 `application.resource_channel.*`、`infrastructure.resource_channel.*` 与包 `__init__` 本身；任何 `infrastructure.filesystem/sqlite`、`domain.*` 都是违规。
- 标准库与第三方模块不在本门禁范围（sidecar 依赖 ctypes/json/sqlite3 等标准库）。
- 隔离证明的是**导入边界**；sidecar 的行为边界（catalog authority、typed 拒绝）见 [allow-deny-matrix.md](allow-deny-matrix.md)。
