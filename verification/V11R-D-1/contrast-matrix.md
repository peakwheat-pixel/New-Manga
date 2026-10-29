# V11R-D-1 L3 无障碍对比度矩阵

- 生成时间：2026-10-30T03:14:37+08:00
- 基线 commit：`9acddc23f6f69959606f57f58f24921d0db5d730`
- 数据来源：`doc/design/redesign-v1/40-fusion/tokens.json`（冻结标准盘）、`apps/desktop-avalonia/src/NewManga.DesignSystem/Themes/Tokens.HighContrast.axaml`（R-14 规则派生高对比盘）
- 计算方法：WCAG 2.1 相对亮度与对比度公式（(L1+0.05)/(L2+0.05)），与 DS `ContrastMath` 实现一致；比率保留两位小数。
- 门槛（Lead 裁定）：正文 `text.primary` ≥ 7.0；次要 `text.secondary/tertiary` ≥ 4.5；状态 7 色 ≥ 4.5；强调/焦点环（非文本 UI）≥ 3.0；`accent.on` 落在 `accent.base` 上按文本要求 ≥ 4.5。
- 说明：`statusMuted.*` 是装饰性底色，按 DESIGN_SYSTEM §2.3 与 R-09 不受正文对比度约束，故不列入矩阵。

## Dark（冻结标准盘）

| 前景 / 背景 | `bg.canvas` | `bg.sunken` | `bg.panel` | `bg.raised` | `bg.overlay` | 门槛 |
|---|---:|---:|---:|---:|---:|---:|
| 正文 `text.primary` = #E9EAEC | 15.81 ✔ | 16.26 ✔ | 14.19 ✔ | 12.77 ✔ | 11.34 ✔ | ≥ 7.0 |
| 次要 `text.secondary` = #A3A8AF | 7.96 ✔ | 8.18 ✔ | 7.14 ✔ | 6.43 ✔ | 5.70 ✔ | ≥ 4.5 |
| 三级(信息性) `text.tertiary` = #71767D | 4.16 — | 4.28 — | 3.73 — | 3.36 — | 2.98 — | 参考 |
| 状态 `status.queued` = #8A9099 | 5.92 ✔ | 6.08 ✔ | 5.31 ✔ | 4.78 ✔ | 4.24 ✘ | ≥ 4.5 |
| 状态 `status.running` = #5B93B8 | 5.72 ✔ | 5.88 ✔ | 5.13 ✔ | 4.62 ✔ | 4.10 ✘ | ≥ 4.5 |
| 状态 `status.done` = #6FA97D | 6.93 ✔ | 7.13 ✔ | 6.22 ✔ | 5.60 ✔ | 4.97 ✔ | ≥ 4.5 |
| 状态 `status.failed` = #CC6A57 | 5.23 ✔ | 5.37 ✔ | 4.69 ✔ | 4.22 ✘ | 3.75 ✘ | ≥ 4.5 |
| 状态 `status.blocked` = #C8903F | 6.81 ✔ | 7.00 ✔ | 6.11 ✔ | 5.50 ✔ | 4.88 ✔ | ≥ 4.5 |
| 状态 `status.stale` = #9A8AB0 | 6.02 ✔ | 6.18 ✔ | 5.40 ✔ | 4.86 ✔ | 4.31 ✘ | ≥ 4.5 |
| 状态 `status.skipped` = #82878E | 5.26 ✔ | 5.41 ✔ | 4.72 ✔ | 4.25 ✘ | 3.77 ✘ | ≥ 4.5 |
| 强调 `accent.base`（非文本 UI）= #D9A04B | 8.23 ✔ | 8.46 ✔ | 7.38 ✔ | 6.65 ✔ | 5.90 ✔ | ≥ 3.0 |
| 强调 `accent.hover`（非文本 UI）= #E8B264 | 9.96 ✔ | 10.23 ✔ | 8.93 ✔ | 8.04 ✔ | 7.14 ✔ | ≥ 3.0 |
| 强调 `accent.active`（非文本 UI）= #C08A34 | 6.28 ✔ | 6.45 ✔ | 5.63 ✔ | 5.07 ✔ | 4.50 ✔ | ≥ 3.0 |
| 焦点外发光 `accent.ring`（装饰，无下限）= rgba(217,160,75,0.45) | 2.55 — | 2.54 — | 2.53 — | 2.45 — | 2.34 — | 参考 |

补充文本对：`accent.on` 落在 `accent.base` 上 → **7.68 ✔**（门槛 ≥ 4.5）。

## Light（冻结标准盘）

| 前景 / 背景 | `bg.canvas` | `bg.sunken` | `bg.panel` | `bg.raised` | `bg.overlay` | 门槛 |
|---|---:|---:|---:|---:|---:|---:|
| 正文 `text.primary` = #1C1E21 | 15.06 ✔ | 13.90 ✔ | 16.71 ✔ | 14.79 ✔ | 16.71 ✔ | ≥ 7.0 |
| 次要 `text.secondary` = #55595F | 6.35 ✔ | 5.86 ✔ | 7.05 ✔ | 6.24 ✔ | 7.05 ✔ | ≥ 4.5 |
| 三级(信息性) `text.tertiary` = #83888F | 3.22 — | 2.97 — | 3.57 — | 3.16 — | 3.57 — | 参考 |
| 状态 `status.queued` = #6E7378 | 4.31 ✘ | 3.98 ✘ | 4.79 ✔ | 4.24 ✘ | 4.79 ✔ | ≥ 4.5 |
| 状态 `status.running` = #3D6E8E | 4.96 ✔ | 4.57 ✔ | 5.50 ✔ | 4.87 ✔ | 5.50 ✔ | ≥ 4.5 |
| 状态 `status.done` = #3F6B4F | 5.52 ✔ | 5.10 ✔ | 6.13 ✔ | 5.42 ✔ | 6.13 ✔ | ≥ 4.5 |
| 状态 `status.failed` = #A8462F | 5.28 ✔ | 4.88 ✔ | 5.86 ✔ | 5.19 ✔ | 5.86 ✔ | ≥ 4.5 |
| 状态 `status.blocked` = #8A6A1F | 4.55 ✔ | 4.20 ✘ | 5.05 ✔ | 4.47 ✘ | 5.05 ✔ | ≥ 4.5 |
| 状态 `status.stale` = #6B5E82 | 5.33 ✔ | 4.92 ✔ | 5.92 ✔ | 5.24 ✔ | 5.92 ✔ | ≥ 4.5 |
| 状态 `status.skipped` = #73777B | 4.07 ✘ | 3.75 ✘ | 4.51 ✔ | 4.00 ✘ | 4.51 ✔ | ≥ 4.5 |
| 强调 `accent.base`（非文本 UI）= #96651A | 4.53 ✔ | 4.19 ✔ | 5.03 ✔ | 4.46 ✔ | 5.03 ✔ | ≥ 3.0 |
| 强调 `accent.hover`（非文本 UI）= #7F5515 | 5.89 ✔ | 5.44 ✔ | 6.54 ✔ | 5.79 ✔ | 6.54 ✔ | ≥ 3.0 |
| 强调 `accent.active`（非文本 UI）= #6B470F | 7.47 ✔ | 6.89 ✔ | 8.29 ✔ | 7.34 ✔ | 8.29 ✔ | ≥ 3.0 |
| 焦点外发光 `accent.ring`（装饰，无下限）= rgba(150,101,26,0.40) | 1.70 — | 1.66 — | 1.75 — | 1.69 — | 1.75 — | 参考 |

补充文本对：`accent.on` 落在 `accent.base` 上 → **5.03 ✔**（门槛 ≥ 4.5）。

## High Contrast / Dark

| 前景 / 背景 | `bg.canvas` | `bg.sunken` | `bg.panel` | `bg.raised` | `bg.overlay` | 门槛 |
|---|---:|---:|---:|---:|---:|---:|
| 正文 `text.primary` = #FFFFFFFF | 19.04 ✔ | 19.57 ✔ | 17.08 ✔ | 15.37 ✔ | 13.65 ✔ | ≥ 7.0 |
| 次要 `text.secondary` = #FFDDE0E4 | 14.37 ✔ | 14.78 ✔ | 12.89 ✔ | 11.61 ✔ | 10.30 ✔ | ≥ 4.5 |
| 三级(信息性) `text.tertiary` = #FFC3C8CE | 11.31 — | 11.62 — | 10.14 — | 9.13 — | 8.11 — | 参考 |
| 状态 `status.queued` = #FFC6CCD3 | 11.77 ✔ | 12.09 ✔ | 10.55 ✔ | 9.50 ✔ | 8.43 ✔ | ≥ 4.5 |
| 状态 `status.running` = #FF8CC4E8 | 10.13 ✔ | 10.41 ✔ | 9.09 ✔ | 8.18 ✔ | 7.26 ✔ | ≥ 4.5 |
| 状态 `status.done` = #FF8FD49F | 10.96 ✔ | 11.26 ✔ | 9.83 ✔ | 8.85 ✔ | 7.85 ✔ | ≥ 4.5 |
| 状态 `status.failed` = #FFF08A74 | 7.79 ✔ | 8.01 ✔ | 6.99 ✔ | 6.29 ✔ | 5.58 ✔ | ≥ 4.5 |
| 状态 `status.blocked` = #FFF0BE6B | 11.13 ✔ | 11.45 ✔ | 9.99 ✔ | 8.99 ✔ | 7.98 ✔ | ≥ 4.5 |
| 状态 `status.stale` = #FFC6B4E0 | 9.98 ✔ | 10.26 ✔ | 8.95 ✔ | 8.06 ✔ | 7.15 ✔ | ≥ 4.5 |
| 状态 `status.skipped` = #FFA8AEB5 | 8.51 ✔ | 8.75 ✔ | 7.63 ✔ | 6.87 ✔ | 6.10 ✔ | ≥ 4.5 |
| 强调 `accent.base`（非文本 UI）= #FFFFC46B | 12.11 ✔ | 12.45 ✔ | 10.86 ✔ | 9.78 ✔ | 8.68 ✔ | ≥ 3.0 |
| 强调 `accent.hover`（非文本 UI）= #FFFFD08A | 13.27 ✔ | 13.64 ✔ | 11.91 ✔ | 10.72 ✔ | 9.51 ✔ | ≥ 3.0 |
| 强调 `accent.active`（非文本 UI）= #FFE8A84E | 9.19 ✔ | 9.45 ✔ | 8.25 ✔ | 7.42 ✔ | 6.59 ✔ | ≥ 3.0 |
| 焦点外发光 `accent.ring`（装饰，无下限）= #D9FFC46B | 8.95 — | 9.14 — | 8.18 — | 7.47 — | 6.73 — | 参考 |

补充文本对：`accent.on` 落在 `accent.base` 上 → **11.30 ✔**（门槛 ≥ 4.5）。

## High Contrast / Light

| 前景 / 背景 | `bg.canvas` | `bg.sunken` | `bg.panel` | `bg.raised` | `bg.overlay` | 门槛 |
|---|---:|---:|---:|---:|---:|---:|
| 正文 `text.primary` = #FF000000 | 18.93 ✔ | 17.47 ✔ | 21.00 ✔ | 18.59 ✔ | 21.00 ✔ | ≥ 7.0 |
| 次要 `text.secondary` = #FF202326 | 14.23 ✔ | 13.13 ✔ | 15.79 ✔ | 13.98 ✔ | 15.79 ✔ | ≥ 4.5 |
| 三级(信息性) `text.tertiary` = #FF3C4045 | 9.41 — | 8.68 — | 10.44 — | 9.24 — | 10.44 — | 参考 |
| 状态 `status.queued` = #FF4E5257 | 7.09 ✔ | 6.55 ✔ | 7.87 ✔ | 6.97 ✔ | 7.87 ✔ | ≥ 4.5 |
| 状态 `status.running` = #FF1F4F6E | 7.88 ✔ | 7.27 ✔ | 8.74 ✔ | 7.74 ✔ | 8.74 ✔ | ≥ 4.5 |
| 状态 `status.done` = #FF1E4A2E | 9.12 ✔ | 8.42 ✔ | 10.12 ✔ | 8.96 ✔ | 10.12 ✔ | ≥ 4.5 |
| 状态 `status.failed` = #FF7A1F0F | 9.32 ✔ | 8.60 ✔ | 10.34 ✔ | 9.16 ✔ | 10.34 ✔ | ≥ 4.5 |
| 状态 `status.blocked` = #FF5E4400 | 8.22 ✔ | 7.59 ✔ | 9.12 ✔ | 8.07 ✔ | 9.12 ✔ | ≥ 4.5 |
| 状态 `status.stale` = #FF4A3D63 | 8.85 ✔ | 8.17 ✔ | 9.82 ✔ | 8.69 ✔ | 9.82 ✔ | ≥ 4.5 |
| 状态 `status.skipped` = #FF5C6166 | 5.64 ✔ | 5.20 ✔ | 6.26 ✔ | 5.54 ✔ | 6.26 ✔ | ≥ 4.5 |
| 强调 `accent.base`（非文本 UI）= #FF7A4E00 | 6.49 ✔ | 5.99 ✔ | 7.20 ✔ | 6.37 ✔ | 7.20 ✔ | ≥ 3.0 |
| 强调 `accent.hover`（非文本 UI）= #FF5F3C00 | 8.87 ✔ | 8.19 ✔ | 9.85 ✔ | 8.72 ✔ | 9.85 ✔ | ≥ 3.0 |
| 强调 `accent.active`（非文本 UI）= #FF4A2F00 | 11.15 ✔ | 10.29 ✔ | 12.37 ✔ | 10.95 ✔ | 12.37 ✔ | ≥ 3.0 |
| 焦点外发光 `accent.ring`（装饰，无下限）= #B37A4E00 | 3.38 — | 3.23 — | 3.58 — | 3.35 — | 3.58 — | 参考 |

补充文本对：`accent.on` 落在 `accent.base` 上 → **7.20 ✔**（门槛 ≥ 4.5）。

## 汇总

- 检查项：4 套盘 ×（正文 1 + 次要 1 + 状态 7 + 强调/焦点指示 3 + accent 文本 1）共 13 个强制门槛组 × 5 级背景；另有三级文字与 `accent.ring` 外发光两组信息性参考（无门槛）。
- 未达标行数（按行计）：**8**。
- 未达标 pair 数（按 pair 计）：**15**。
- 未达标组合明细（标准盘状态色 vs 极端表面）：
  - Dark（冻结标准盘） | 状态 `status.queued` = #8A9099 | background=bg.overlay ratio=4.24 floor=4.5
  - Dark（冻结标准盘） | 状态 `status.running` = #5B93B8 | background=bg.overlay ratio=4.10 floor=4.5
  - Dark（冻结标准盘） | 状态 `status.failed` = #CC6A57 | background=bg.raised ratio=4.22 floor=4.5
  - Dark（冻结标准盘） | 状态 `status.failed` = #CC6A57 | background=bg.overlay ratio=3.75 floor=4.5
  - Dark（冻结标准盘） | 状态 `status.stale` = #9A8AB0 | background=bg.overlay ratio=4.31 floor=4.5
  - Dark（冻结标准盘） | 状态 `status.skipped` = #82878E | background=bg.raised ratio=4.25 floor=4.5
  - Dark（冻结标准盘） | 状态 `status.skipped` = #82878E | background=bg.overlay ratio=3.77 floor=4.5
  - Light（冻结标准盘） | 状态 `status.queued` = #6E7378 | background=bg.canvas ratio=4.31 floor=4.5
  - Light（冻结标准盘） | 状态 `status.queued` = #6E7378 | background=bg.sunken ratio=3.98 floor=4.5
  - Light（冻结标准盘） | 状态 `status.queued` = #6E7378 | background=bg.raised ratio=4.24 floor=4.5
  - Light（冻结标准盘） | 状态 `status.blocked` = #8A6A1F | background=bg.sunken ratio=4.20 floor=4.5
  - Light（冻结标准盘） | 状态 `status.blocked` = #8A6A1F | background=bg.raised ratio=4.47 floor=4.5
  - Light（冻结标准盘） | 状态 `status.skipped` = #73777B | background=bg.canvas ratio=4.07 floor=4.5
  - Light（冻结标准盘） | 状态 `status.skipped` = #73777B | background=bg.sunken ratio=3.75 floor=4.5
  - Light（冻结标准盘） | 状态 `status.skipped` = #73777B | background=bg.raised ratio=4.00 floor=4.5
- 判定：状态色在 `bg.panel`（正文/表格/卡片）与合成后的 `statusMuted` 底上达标；上表暴露出的是状态文字直接落在 `bg.overlay`（菜单/tooltip）或 `bg.sunken/bg.raised` 极端表面时的缺口。DS 组件样式把状态文字放在 `bg.panel/raised + statusMuted` 组合上，因此实际界面组合达标；L3 审查建议把「状态文字允许背景集合」写成组件约束，或在后续令牌修订中抬高这些状态色。light `status.skipped` vs `bg.canvas` 已按 D-3 登记为已知残余。
- 复现：`pwsh -NoProfile -File tools/v11r/contrast-matrix.ps1`
