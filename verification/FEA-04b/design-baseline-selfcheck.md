# FEA-04b 设计基线自查清单（DSH 起草侧）

**日期**：2026-11-02
**交付**：`doc/design/fluent-v1/`（README + 01–10，共 11 个文件）
**版本**：`fluent-v1.0.0`

## 1. AC 对应

| AC | 要求 | 落点 | 自查 |
|---|---|---|---|
| AC1 | 四页规格齐全，含所有状态（空/载入/错/满）与响应式断点 | 05–08 四页、09 状态矩阵、04 断点 | 四页各含状态表；断点 Narrow/Medium/Compact/Full 见 04 §2 |
| AC2 | `Nm.Corner.Fluent.*` / `Nm.Material.*` / `Nm.Elevation.*` 取值 + C-02 V-05 判据①对表 | 01 §2/§3/§4 | 取值表 + 对表 + 裸值禁令 + G-1b/G-1c 缺口登记 |
| AC3 | 三类动效 × auto/full/reduce 参数，满足 C-03 §3 判据 ①–⑤ | 02 §2/§3 | 三张参数表 + 判据逐条对应 + categories 关闭语义 |
| AC4 | 焦点顺序、快捷键、高对比、屏幕阅读器标签；与 C-02 V-08b KeyMap 无冲突 | 03 | 键位表（17 条，与 `ShellCommands.cs` 一致）+ 四页 Tab 序 + 高对比 + AutomationProperties |
| AC5 | 用户确认 + 独立 Review + DSH 冻结 | 待办 | 独立 Review r1–r4 已走；用户确认未进行（自主推进模式，待裁决） |

## 2. 上游一致性

| 上游 | 检查 | 结果 |
|---|---|---|
| C-02 §6.1 空间/模式/surface | 未新增 `SpaceId`/`StudioMode`/`ShellSurface` | 一致 |
| C-02 V-03/V-05 令牌 | 只引用冻结名；缺键（`Nm.Focus.Ring.*`、`Nm.Corner.Fluent.*`、`Nm.Material.*`、`Nm.Elevation.*`）登记为 G-1/G-1c，不用其他键替代 | 一致 |
| C-02 V-08b KeyMap | 全局键位来自 `ShellCommands.cs`（17 条）；Fluent 不私建注册表；无无修饰 Tab 冲突（页签用 ←/→） | 一致 |
| C-03 §2.3 三态三类 | `auto/full/reduce` + `navigation/feedback/decorative`；浮层归 `navigation`；判据 ①–⑤（含 feedback 颜色过渡 0ms） | 一致 |
| C-03 §2.2 外观字段 | 设置页字段与 `presentation-settings.json` 对齐（appearance/contrast/corners/material/motion.*/layout.*/followSystemAccent/schemaVersion） | 一致 |
| C-05 页可见性 | 四页不新增页；阅读器为 overlay | 一致 |

## 3. 缺口登记

| # | 缺口 | 处置 |
|---|---|---|
| G-1 | `Nm.Corner.Fluent.*` / `Nm.Material.*` / `Nm.Elevation.*` 未生成 | FEA-05 生成；本基线冻结取值 |
| G-1b | 尺寸/断点复用既有 `Nm.Size.*`（TopBand 36 / TreeWidth 200 / FilmStrip 56·200 / Inspector 40·320 / Row 24·26 / StatusBand 28·24 / ControlHeight）；断点三档 1024/1280/1600；批量矩阵列宽最小 96 为设计常量 | 不新增令牌；额外尺寸须 FEA-05 登记 + DSH 裁决 |
| G-1c | `Nm.Focus.Ring.Width/Offset/Color` 缺失 | FEA-05 生成或 DSH 裁决替代 |
| G-2 | 用户确认（AC5）未进行 | 自主推进模式下待用户确认 |
| G-3 | 设计资产（图标/字体）未产出 | 沿用 `NmIcon` 既有集合；新资产 FEA-05 按许可评估 |
| G-4 | 双屏/拔屏细节只给原则 | FEA-07 实现时按 04 §4 扩展 |

## 4. 复核处置记录

- **r1（P1×7）**：令牌名改既有冻结名；G-1b 尺寸/断点；命令 Id；Tab 序；判据⑤；09 矩阵 4 格；08 字段。
- **r2（P1×4）**：焦点环改 G-1c；05–08 断点/令牌同步；删 `Ctrl+Tab`；判据⑤「所有时长 0ms」。
- **r3（P1×1）**：06 `Compact`→`Narrow`；图中 72/240→`Nm.Size.TreeWidth`；07 高 40/36→`Nm.Size.ControlHeight`。
- **r4（P1×1）**：06 矩阵列宽恢复 96 并在 01 G-1b 登记为设计常量（`RowNormal` 是行高，不作列宽）。
- 证据表 12 项 sha256 与最终文件一致（commit 列以交付 head 为准）。

## 5. 评审要点（给独立 Reviewer）

- 四页状态是否覆盖全部（对照 09 逐格核对）。
- 令牌名是否全部可追到冻结名/已登记缺口；有无裸值。
- 动效表是否逐条满足 C-03 §3 判据 ①–⑤。
- 键位表是否与 `ShellCommands.cs` 一一对应。
- 09 与四页正文是否一致。
- 与 FEA-04 Current 基线不退化。
