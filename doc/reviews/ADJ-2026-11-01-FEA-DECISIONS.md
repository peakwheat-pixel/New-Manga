# 用户裁决记录 · FEA 契约冻结前置（2026-11-01）

状态：**已裁决 / 生效**
裁决人：用户（项目 Owner）
记录人：DSH（Lead / Architect / Integrator）
裁决时间：2026-11-01（用户原话：「按推荐裁决」）
依据：[NIGHT-SHIFT-2026-11-01 晨报](../handoffs/NIGHT-SHIFT-2026-11-01.md)「待你拍板」区 + Codex 独立意见（4 项技术建议，1 项与我方推荐不同，已处置）+ [冻结矩阵](../plan/FEA-CONTRACT_FREEZE_MATRIX.md)

---

## 裁决内容（5 项，全部按推荐）

| # | 代号 | 问题 | 裁决 | 影响契约 | 备注 |
|---|---|---|---|---|---|
| 1 | **`R`** | AD-002 责任表 / 哨兵口径 | **C1=D 零字节**、**C3=是**（哨兵保持 `Managed Copy`）、C2/C4 无需回答 | C-01b 冻结前置③ | 不改 AD-002 任何字节；解释由 AD-003 §2 表首行 + AD-002 `:9-10` 横幅承担，并在 C-01b 编成 SC-07/SC-01 |
| 2 | **U-04** | Fluent 视觉是否豁免 V11R 圆角/阴影/模糊禁令 | **批准** C-02 V-05 的 2 行 per-scheme 例外（材质层次 + 圆角），**令牌强制** | C-02 §2.4 | 仅 `builtin.fluent` 生效；Current 禁令不变；禁止提高全局 `ThemeCorners.MaxRadius`（判据④） |
| 3 | **U-05a** | 外观持久化是否纳动效三态/三类 | **纳入** `motion.mode = auto/full/reduce` + 三类 `navigation/feedback/decorative` | C-03 §2.2/§2.3 | 迁移：旧 `true → reduce` + 三类全禁；旧 `false → full`；`auto` 为新选项（v5 修正） |
| 4 | **U-05b** | 旧 `theme-settings.json` 迁移后是否删除 | **保留**（兼容期后可写，结束后转只读） | C-03 §2.1 | 转只读必须在保存路径完全接管之后（顺序铁律） |
| 5 | **U-05c** | 系统 reduced-motion 与用户显式 `full` 的优先级 | **用户显式优先**（`auto` 跟随 / `full` 覆盖 / `reduce` 强制） | C-03 §2.3 | 与方案 r4 `:866`「系统覆盖所有类别」的分歧已显式声明；若改系统优先需同步改 `full` 语义与判据② |

## Codex 独立意见的处置

Codex 于 2026-11-01 出具 4 项技术意见（只读、未改文件）。DSH 逐条核验：

| 项 | Codex 意见 | 核验结果 | 处置 |
|---|---|---|---|
| ① `R` | 同意 D 零字节 | 证据链一致（`AD-002:9`、`AD-003:32`、`C-01b:34/45`） | 采纳；补记「D 非零风险：后续 Task 可能只截取 `:28` 漏掉横幅」 |
| ② U-04 | 同意 per-scheme 例外；指出不得提高全局 `ThemeCorners.MaxRadius` | 成立（`ThemeModels.cs:206`、`ThemeValidator.cs:223` 共享上限） | 写成 C-02 V-05 **判据④** |
| ③ U-05a | **部分不同**：支持三态三类，但旧 `false` 应映射 `full` 而非 `auto`；且系统优先级与方案 r4 `:866` 冲突 | **成立，我方 v4 写错**（代码事实：`SetReducedMotion(false)` 移除覆盖层 = 完整动效；`Motion.Reduced.axaml` 全时长置 0 = 全禁） | C-03 **v5** 修正 + 新增 **U-05c** 分歧声明；判据②同步 |
| ④ U-05b | 同意保留；指出只读时序风险（`TrySave` 异常被吞） | 成立（`ThemeService.cs:647/654`） | 写成 C-03 **顺序铁律** |

**结论**：Codex 找出了 C-03 的一处实质缺陷（`false → auto`），DSH 已修并送独立窄面复核（`FEA-GOV-12`）。该项修复不改变 U-05a 的"纳入"结论，只修正迁移映射。

## 冻结授权

本裁决**仅解除用户侧前置条件**。以下仍为冻结的必要条件，DSH 按 [冻结矩阵 §2](../plan/FEA-CONTRACT_FREEZE_MATRIX.md) 逐步执行：

- `G-DELETE-CONTRACT` 关闭（ADJ-001 PD 语义；D04–D07 裁决）
- `G-CONTRACT` 关闭（AD-003 存储契约）
- DSH 批准协议 minor 2.11
- M2-C1 §5.11.3/§5.11.5 扩展（独立 Task）
- C-08 协议注册（独立 Task）

**不构成**：契约整体冻结、实现 Task 释放、远端 push 授权。

## 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：5 项裁决 + Codex 意见处置表 + 冻结授权边界 | DSH |
