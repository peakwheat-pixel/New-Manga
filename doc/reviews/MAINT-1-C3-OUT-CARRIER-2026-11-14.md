# C3 设计选择/范围外 · 正式 OUT 载体（MAINT-1，2026-11-14）

用途：满足 DoD §3「设计选择类转为 OUT + waiver」。
性质：**append-only 裁决记录**；不改任何 Task 卡/Review/`verification/**` 历史字节；不把可行性问题伪装成设计选择（见 §3 排除项）。

裁决人：DSH（用户 2026-11-14 全权授权）；**用户可事后推翻**，推翻后按对应项重开卡。

## 1. 逐项 OUT

| # | 节点 | 项 | OUT 理由 | 用户可见后果 | 重开条件 |
|---|---|---|---|---|---|
| C3-1 | FEA-14-AI-1 | DDL「version 不可变」的含义 | **已裁**：version 由 Core 单调 +1，调用方不可指定（该卡 limitation ⑤ 原文即此裁决） | 无（语义已定） | 若需调用方指定 version |
| C3-2 | FEA-14-EDIT-1 | `position` 形状 `{x,y}`（0–1 相对坐标） | PREQ §8 未定义，属该卡实现裁决；本线不提升为跨卡契约 | 无（仅编辑层内部表示） | 若提升为跨卡契约 → 先出 PREQ errata/ADR |
| C3-3 | FEA-14-EDIT-1 | 批量 resolve/delete、列表分页/跨书过滤、`kind` UI 预置集合 | 属 EDIT-2/EDIT-3 范围，本线未释放 | 无（单条编辑可用） | 立项 EDIT-2/EDIT-3 |
| C3-4 | FEA-14-EDIT-1 | `issue_markers` 无外键、删书不清理孤儿行 | 与 `reading_bookmarks` 既有先例一致；`book_exists` 守卫使已删书标记不复现 | 无 | 立项清理卡 |
| C3-5 | FEA-14-FONT-1 | FONT-2 范围：字体渲染消费、设置页字体 UI、家族/字重元数据解析（需 fontTools）、内置字体授权 | 属 FONT-2 范围；内置字体涉及许可证边界（不随包） | 字体可管理与引用，但渲染侧未消费 | 立项 FONT-2 + 许可核查 |
| C3-6 | FEA-15-A3-1 | 日志根在只给 `--data-root`、不给 `--log-dir` 时回落真实 `%APPDATA%` | 源码 `MainWindow.axaml.cs:1041-1047` 明示为**有意保留的发行默认**；改成"数据根隐含日志根"属**行为变更**（原 Q5） | 隔离运行若只给 `--data-root`，仍会在真实 `%APPDATA%` 留 1 个日志文件（实测 166 B 级追加） | 用户要求改默认行为 → 开实现卡（小改动） |

## 2. 与其他类别的边界

- **C2（5 项）不在本载体**：AI-1 name 唯一/规范化、AI-1 `UPDATE OR REPLACE` label 覆盖、EDIT-1 position 若升为契约、LIB-1 R-11 三项 deferral、READ-1 P12/P15 偏差——均需 errata / additive / UNFREEZE 或 ADJ，属契约对齐，不得以"设计选择"掩盖。
- **C1（约 13 项）不在本载体**：需实现并 MET，不得转 OUT（否则等于把未做工作合法化）。

## 3. 排除项（明确不属 C3，防止误分类）

| 项 | 真实类别 | 依据 |
|---|---|---|
| `FEA-11` folder source relink 判别测试 | **C1** | C-17 `:278` 允许"能证明同一"，可构造 |
| `FEA-06-RESIDUAL-2` Tab 遍历 / a11y 属性 | **C1** | 可 headless 断言 |
| `FEA-07` AC1 A03/ACK/Run、AC2 单写 owner | **C1** | `RESIDUAL-CLOSEOUT-PLAN §11.1` 已纠正 |
| `FEA-15-A3-1` 日志根**硬编码** | **不成立** | 实为有意的默认行为（见 C3-6），非缺陷 |
| 术语表冲突 NOT_WIRED | **无关项** | 术语冲突 ≠ 区域冲突（第二意见指出的范畴错误） |

## 4. 与 DoD 的对应

- 本载体关闭 **C3 共 6 项**（其中 C3-1 为既有裁决的正式归位）。
- **未关闭**：C1 约 13、C2 5、Q6（pytest 16F）。
- 故 DoD §3 仍未达成；本载体是达成路径的第二块前置件（第一块为 C4 载体）。

## 5. 可推翻性

任一项若被判为"应当实现"，立即作废该 OUT 并以 append-only 记录推翻原因；已实现部分不受影响。
