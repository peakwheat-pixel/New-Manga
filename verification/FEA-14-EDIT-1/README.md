# FEA-14-EDIT-1 证据索引（问题标记）

- Task：`FEA-14-EDIT-1`（FEA-14 S5 EDIT 切片；复用 PREQ 预冻结 wire P16–P20）
- 实现提交：`9a968c3e4`（base `68a9e2e74`，即 LIB-1 收口 + EDIT-1 冻结提交）
- 日期：2026-11-10
- 日志生成口径：4 个 Canonical 日志均于本轮门禁在 **`9a968c3e4`** 生成，头行记录生成时 HEAD 与 `git status --short`（同批顺序生成，后生成的日志会看到前序日志未提交；产品字节均为 `9a968c3e4`）。README 与证据表在日志之后写入，属证据簿记，不含产品字节。

## 结论状态

| AC | 判别 | 结果 |
|---|---|---|
| AC1 数据面/v13 | `issue_markers` additive 建表 + 两索引 + 位置成对/0–1 的 DB CHECK；v1–v12 字节不变；旧库升级无损 | **MET**：schema **v13** 仅新增 `issue_markers`（`marker_id` PK、`book_id/chapter_id/page_id`、`position_x/position_y`（可空成对、0–1 CHECK）、`kind`（非空）、`note`、`state`（open/resolved）、`created_at`、`resolved_at`）+ `idx_issue_markers_book_state` / `idx_issue_markers_page`；`test_v13_adds_issue_markers_and_keeps_legacy_rows` 先升 v12、插入真实书/章/页行、再升 v13 并断言行保留 |
| AC2 P16 列表 | `book_id` + 可选 `state`；默认 open；排序稳定；PREQ 字段 | **MET**：service 默认 `open`、`state=resolved` 返回已解决、其他值 → `INVALID_REQUEST`；排序 `created_at, marker_id`；wire 响应键集实测与 PREQ 一致（`position` 仅位置标记、`resolved_at` 仅已解决） |
| AC3 P17 新建 | 归属校验（书→章→页）；position 成对 0–1；返回 `marker_id` 且 `state=open` | **MET**：缺书/章不属于书/页不属于章/页不存在 → `TARGET_NOT_FOUND`；position 半对/越界/bool/字符串 → `INVALID_REQUEST`；`kind` 空/超 64 → `INVALID_REQUEST`；成功返回 `marker_id`、`created_at` 有值、`state=open` |
| AC4 P18–P20 状态/删除 | resolve/reopen 状态迁移 + `resolved_at`；delete 物理删且不影响其他数据 | **MET**：resolve 幂等（重复调用时间戳不变）、reopen 清空 `resolved_at`；delete 后列表不可见；测试断言书/章/页行数不变 |
| AC5 契约/门禁 | C-07 UNFREEZE v1.7（74/81）成员表逐行 = stdout；pin 重算；`--check`/pins | **MET**：inventory **74/81**，正式成员表 74 方法 + 4 非方法 = stdout（`ALL_MATCH: True`）；v1.7 pin `bb775912…`（v1.6 原值保留）；`--check` EXIT 0、`verify_pins` 18/18 |
| AC6 证据 | 定向/回归/App.Tests、日志 EXIT、NOT_RUN | **MET**：见下表与 NOT_RUN |

## 门禁与证据（本目录）

| 文件 | 内容 | EXIT |
|---|---|---|
| `logs/pytest-edit.log` | `test_issue_markers.py` + `test_issue_marker_wire.py` **5 passed** | 0 |
| `logs/regression-v13.log` | v13 回归：storage+core+fea09+fea11 **1258 passed** | 0 |
| `logs/dotnet-app-tests.log` | App.Tests 全量 **882 passed / 0 failed / 11 skipped**（5m23s） | 0 |
| `logs/pins-api.log` | `verify_pins` 18/18（C07=`bb7759126620`）、`generate_api_inventory.py --check` EXIT 0（74/81） | 0 |

**提交同步更新**：`doc/plan/FEA-C07_API_INVENTORY.md`（成员表 = 脚本 stdout，74 方法 + 4 非方法成员；S5 计划节仅剩 P21–P25）、`doc/plan/FEA-CONTRACT-FROZEN-C07.md`（§1 v1.6/v1.7 pin 链、§1B、§2 条件 3 `1/74/6=81`、§3、§5）、`doc/reviews/CONTRACT-UNFREEZE-2026-11-10-EDIT1.md`。

## 设计说明与 limitation

- **`position` 形状**（PREQ §8 未给出）：裁决为相对页面坐标 `{"x":number,"y":number}`（0–1，成对；整页标记省略）。preq 键集不变，属形状细化；DB 层同时用 CHECK 兜底成对与范围。
- **typed 错误**：所有 service 失败都是 `IssueMarkerError(code)` → wire `TARGET_NOT_FOUND/not_found` 或 `INVALID_REQUEST/validation`，不落 `UNKNOWN/internal`；无半写路径（创建前完成全部校验）。
- **删除语义**：标记是用户工作产物、非受保护内容，P20 物理删行；不触碰漫画/页/进度/人工修改（ADJ-001 不适用，已在卡面登记）。
- **状态机**：resolve/reopen 幂等（状态不变时不改 `resolved_at`）。
- 批量解决/批量删除、列表分页/跨书过滤、`kind` 的 UI 预置集合 = 后续 EDIT-2/EDIT-3 或 UI 卡（PREQ 明确批量由 UI 循环）。
- C-07 契约只按流程改统计/成员表（UNFREEZE v1.7），无其他契约字节。

## NOT_RUN（不得记 PASS）

- EDIT 可见 UI（标记列表、新建标记、页面定位渲染、kind 选择器）= NOT_RUN（EDIT-2/EDIT-3/UI 卡）。
- 批量 resolve/delete 命令 = NOT_RUN（PREQ 未纳入，UI 循环或后续批量命令）。
- 真实 Host↔Core 进程级联调：5 个新 `CoreServiceClient` 方法未对活 Core 调用；C# 4 个端口测试覆盖 NullHost 降级 + Fake 命令记录/状态机，但**不覆盖真实 IPC 读写映射**。
- 标记与翻译/渲染管线联动（EDIT-3 受控样式重渲染）= NOT_RUN（另卡）。
- 万级标记/跨书查询性能、真实大库迁移 = NOT_RUN。
- FEA-15 正式验收声明未审。

## 复现

```powershell
python -m pytest tests/storage/test_issue_markers.py tests/core/test_issue_marker_wire.py -q
python -m pytest tests/storage tests/core tests/fea09/test_v7_migration.py tests/fea11/test_source_gate_unify.py -q
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --nologo
python tools/generate_api_inventory.py --check
pwsh -NoProfile -File tools/governance/verify_pins.ps1
```
