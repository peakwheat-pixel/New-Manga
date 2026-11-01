# FEA-04b 设计基线自查清单（DSH 起草侧）

**日期**：2026-11-02
**交付**：`doc/design/fluent-v1/`（README + 01–10，共 11 个文件）
**版本**：`fluent-v1.0.0`

## 1. AC 对应

| AC | 要求 | 落点 | 自查 |
|---|---|---|---|
| AC1 | 四页规格齐全，含所有状态（空/载入/错/满）与响应式断点 | `05-page-shelf.md`、`06-page-workbench.md`、`07-page-reader.md`、`08-page-settings.md`、`09-state-matrix.md`、`04-layout-responsive.md` | 四页各含状态表；断点 Compact/Medium/Expanded/Wide 在 04 §2 与各页 §5 |
| AC2 | `Nm.Corner.Fluent.*`/`Nm.Material.*`/`Nm.Elevation.*` 取值 + C-02 V-05 判据①对表 | `01-design-tokens.md` §2/§3 | 取值表 + 对表 + 裸值禁令 |
| AC3 | 三类动效 × `auto`/`full`/`reduce` 参数，满足 C-03 §3 判据 ①–⑤ | `02-motion.md` §2/§3 | 三张参数表 + 判据逐条对应 |
| AC4 | 焦点顺序、快捷键、高对比、屏幕阅读器标签；与 C-02 V-08b KeyMap 无冲突 | `03-accessibility.md` | 键位表来自 `ShellCommands.cs`；四页 Tab 序；高对比降级；AutomationProperties |
| AC5 | 用户确认 + 独立 Review + DSH 冻结 | 待办 | 用户确认未进行（自主推进模式，已登记待裁决）；独立 Review 待派发 |

## 2. 上游一致性

| 上游 | 检查 | 结果 |
|---|---|---|
| C-02 §6.1 空间/模式/surface | `SpaceId.Library/Studio/Console`、`StudioMode.Page/Batch`、`ShellSurface.Spaces/ThemeStudio/ReaderOverlay` 未新增 | ✓（README §1、05–07 页 ID） |
| C-02 V-05 令牌 | 只引用 C-02 已定义的 Fluent 令牌名（`Corner.Fluent.*`/`Material.*`/`Elevation.*`）；未新增令牌名 | ✓（01 §1） |
| C-02 V-08b KeyMap | 全局键位来自 `ShellCommands.cs`；Fluent 不私建注册表；上下文键三元 | ✓（03 §1） |
| C-03 动效三态/三类 | `auto/full/reduce` + `navigation/feedback/decorative`；浮层归 `navigation`；判据 ①–⑤ | ✓（02 §1–§3） |
| C-03 外观字段 | 设置页字段与 `presentation-settings.json` 迁移后字段一致；`AppearanceCoordinator` 唯一写者 | ✓（08 §3） |
| C-05 页可见性 | 四页不新增页；阅读器为 overlay | ✓（07 页 ID） |

## 3. 已知缺口 / 待裁决

| # | 缺口 | 影响 | 处置建议 |
|---|---|---|---|
| G-1 | `Nm.Corner.Fluent.*`、`Nm.Material.*`、`Nm.Elevation.*` 目前在 `NmKeys.g.cs` **不存在**（Material/Elevation 为保留空键） | FEA-05 实现前需生成令牌；否则设计数值无落点 | 由 FEA-05 在 C-02 已冻结名义下生成；本基线只冻结取值（01 §1 已注明） |
| G-2 | 用户确认（AC5）未进行 | AC5 无法 MET | 自主推进模式下由用户后续确认；已登记 GOAL-PROGRESS 待裁决 |
| G-3 | 设计资产（图标/字体）未产出 | FEA-05/06 需图标时无基线 | 本基线不引入新资产；沿用 `NmIcon.cs` 既有集合；新资产在 FEA-05 按许可边界评估 |
| G-4 | 双屏/拔屏细节只给出原则，未给具体窗口尺寸 | FEA-07 多窗口实现需补充 | 由 FEA-07 在实现时按 04 §4 扩展（不阻断本基线） |

## 4. 评审要点（给独立 Reviewer）

- 四页规格是否覆盖**全部**状态（对照 `09-state-matrix.md`，逐格核对）。
- 令牌取值是否全部可追到 C-02 冻结名；有无自造令牌名/裸值。
- 动效表是否逐条满足 C-03 §3 判据 ①–⑤（每条可给验证断言）。
- 键位表是否与 `ShellCommands.cs` 一一对应；有无新增全局键位。
- 状态矩阵与四页正文是否一致（无矛盾/遗漏）。
- 是否有与 FEA-04 Current 基线冲突的行为（不退化要求）。
