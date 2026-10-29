# R-09 冻结令牌对比度修订：修订前后实测表

- 裁决：Lead DSH **R-09**（2026-10-30），记录于 `doc/design/redesign-v1/40-fusion/DECISION_LOG.md` §5
- 规范依据：`doc/design/redesign-v1/40-fusion/DESIGN_SYSTEM.md` §2.3
- 计算方式：WCAG 2.1 相对亮度 + 对比度公式（与 `NewManga.DesignSystem.Accessibility.ContrastMath` 一致）
- 修订文件：`doc/design/redesign-v1/40-fusion/tokens.json`
- 重新生成：`TokenGen` 全量重写，`--check` 逐字节一致

## 修订对照

| 令牌 | 修订前 | 修订前对比度 | 修订后 | 修订后对比度 | 判定 |
|---|---|---|---|---|---|
| `color.dark.status.queued` | `#5C6169` | 2.74:1（bg.panel #1A1C1F） | `#8A9099` | 5.31:1 | ≥4.5 PASS |
| `color.dark.status.skipped` | `#4A4F55` | 2.07:1 | `#82878E` | 4.72:1 | PASS |
| `color.dark.status.failed` | `#C9634F` | 4.38:1 | `#CC6A57` | 4.69:1 | PASS |
| `color.light.status.skipped` | `#8A8F94` | 3.26:1（bg.panel #FFFFFF） | `#73777B` | 4.51:1 | PASS |
| `color.light.accent.base`（白字对比） | `#B4791F` | 3.69:1 | `#96651A` | 5.03:1 | PASS（正文 ≥4.5） |
| `color.light.accent.base`（bg.canvas） | `#B4791F` | 3.32:1 | `#96651A` | 4.53:1 | PASS（焦点环 ≥3） |
| `color.light.accent.hover` | `#9C6717`（亮度 0.1683） | — | `#7F5515`（亮度 0.1106） | — | 明度单调 base>hover PASS |
| `color.light.accent.active` | `#8A5A12`（亮度 0.1276） | — | `#6B470F`（亮度 0.0767） | — | 明度单调 hover>active PASS |
| `color.light.accent.muted` | `rgba(180,121,31,0.12)` | — | `rgba(150,101,26,0.12)` | — | 同色相同步 |
| `color.light.accent.ring` | `rgba(180,121,31,0.40)` | — | `rgba(150,101,26,0.40)` | — | 同色相同步 |

未修订（按 R-09 裁决保持不变）：`color.*.statusMuted.*`（装饰性底色，不承担正文对比度）、
`color.*.bg.*`（五级背景阶梯）、`color.*.line.*`、`color.*.text.*`。

## 修订后标准盘全量状态对比度（对 bg.panel）

| 状态 | dark | light |
|---|---|---|
| queued | 5.31 | 4.79 |
| running | 5.13 | 5.50 |
| done | 6.22 | 6.13 |
| failed | 4.69 | 5.86 |
| blocked | 6.11 | 5.05 |
| stale | 5.40 | 5.92 |
| skipped | 4.72 | 4.51 |

## 残余说明

- light `status.skipped` 对 `bg.canvas`（#F4F3F0）实测 4.07:1，低于 4.5；状态组件按 DESIGN_SYSTEM
  §2.2 落在 `bg.panel`/`bg.raised`/`statusMuted` 表面（对 panel 4.51:1 达标），且同时以符号+文字
  编码；高对比模式在 canvas 上亦达标。此残余已记录于 `DEVIATIONS.md` D-3。
- `accent.ring` 为半透明外发光用途；实现改用实色 `accent.base` 2px 描边作为焦点环（≥3:1）。
