# V11R 需求 → 任务 → 证据 追溯矩阵 v1

状态：`ACTIVE`（2026-10-30，DSH）。用于 L3/L4 验收与最终报告；每行最终必须能指向**证据路径**，未取证一律 `NOT_RUN`。
说明：审计 F001–F108 与 66 命令 C001–C066 的逐条状态由 `V11R-A-3` 契约包 + 各任务证据补齐（本文件只维护需求域→任务映射，避免第二份真值）。

---

## 1. 用户指令 §三（V1.1 整改重点）→ 任务

| 用户要求 | 对应任务 | 验收证据 | 当前状态 |
|---|---|---|---|
| 108 项功能真实实现状态 | `V11R-A-3` + 各域任务 | 功能矩阵重核（实现/接入/运行/验证 四维） | in_progress |
| 66 条命令 DTO/参数/响应/错误码/协议版本 | `V11R-A-3` | `doc/contracts/V11R_COMMAND_CONTRACT_V1.md` + parity 测试 | in_progress |
| Core→IPC→Host→UI 完整调用链 | `V11R-A-1`/`A-2`/`INT-1` | 链路测试 + E2E | pending |
| 新建书籍/新建章节/文件导入 | `V11R-A-1` + `V11R-B-1` | E2E-01 | in_progress |
| 检测/OCR/翻译/修复/渲染任务真实启动与管理 | `V11R-A-2` + `V11R-B-4` | E2E-02/03 | in_progress |
| 暂停/继续/停止/失败重试/阻塞恢复 | `V11R-A-2` + `V11R-B-4` | E2E-03 | in_progress |
| Region 编辑/气泡文本编辑/持久化 | `V11R-F0-1` + `V11R-B-3` | E2E-04 | in_progress |
| 多页上下文/术语表/SFX | `V11R-B-5` + Core 既有能力 | E2E-02 分支 + 术语冲突用例 | pending |
| 阅读器/导出/设置/Provider/网络代理 | `V11R-B-1`/`B-2`/`B-5` | 各屏 L2/L3 | in_progress |
| ONNX/DirectML/CPU fallback/权重/打包 | `V11R-L4-1`（实机验证）+ Console 设备区 | EP 记录 + 权重 SHA 清单 | pending |
| CI/构建路径/版本溯源/实机验证 | `V11R-A-4` + `V11R-L4-1` | 同 SHA CI + `VERSION.json` 溯源链 | pending |

## 2. 用户指令 §四（全新 UI/UX 覆盖域）→ 屏幕

| 用户要求 | 落点 | 规格 | 任务 |
|---|---|---|---|
| 书架 | Library 空间 | SCREEN_SPECS §2 | `V11R-B-1` |
| 漫画翻译工作台 | Studio Page + Batch 双模式 | SCREEN_SPECS §3/§4 | `V11R-B-3`/`B-4` |
| 阅读器 | Library 内阅读浮层（不设独立页） | SCREEN_SPECS §2 | `V11R-B-1` |
| 设置中心 | Console 空间 9 分区 | SCREEN_SPECS §5 | `V11R-B-2` |
| 项目与章节管理 | Library 详情面板 + 章节账本 | SCREEN_SPECS §2 | `V11R-B-1` |
| 任务进度与错误恢复 | RunStrip/StatusBand/AlertBanner/AttentionMenu | SCREEN_SPECS §1/§4 | `V11R-B-1`/`B-4` |
| 编辑器与各类弹窗 | Inspector 5 页签 + Modal/Drawer | SCREEN_SPECS §3 | `V11R-B-3` |
| 信息架构/组件系统/交互/快捷键/状态/响应式 | 冻结 FUSION_SPEC + DESIGN_SYSTEM + 契约 §2/§3/§6 | — | `V11R-D-1`/`B-1` |
| 新 UI 必须真正连接 Core | `V11R-INT-1` | 无 Mock 冒充；未接入标"待接入" | pending |

## 3. 用户指令 §五（Theme Studio）→ 任务

| 用户要求 | 任务 | 证据 |
|---|---|---|
| C1 五个上游项目研究（架构/视觉/许可证/维护） | `V11R-C-RESEARCH-1` ✅ | `doc/design/theming/RESEARCH_V1.md` |
| C2 全新 Theme Engine 10 子系统 | `V11R-C-1` | `NewManga.ThemeEngine` + 单测 |
| C2 实时切换/深浅/系统/高对比/持久化/安全恢复 | `V11R-C-1` | 切换测试 + 回退测试 |
| C2 颜色风格与导航/书架布局/密度解耦 | 契约 §4 `ThemePackage` vs `LayoutProfile` | 单测：主题包不可含布局 |
| C2 禁止主题切换改变漫画像素/译文/未保存编辑 | `V11R-C-1` + `V11R-C-2` + `V11R-B-3` | 像素哈希 + 状态断言 |
| C3 主题中心 7 分区 | `V11R-C-2` | `THEME_STUDIO_SPEC.md` §6 清单 |
| C3 现代桌面视觉质量（不得退化成色卡列表） | `V11R-C-2` | 截图 + L3 审查 |
| C4 依赖图/替换清单/安全迁移/逐项删除 | `V11R-C-3` | `V11R_THEME_RETIREMENT_PLAN.md` |
| 旧配置主题 ID 安全迁移不崩溃 | `V11R-C-3` | 9+2 迁移用例 |
| 生产路径不再依赖旧主题 | `V11R-C-3` | 零引用断言 |

## 4. 用户指令 §六（统一 Design System）→ 任务

| 要求 | 任务 | 证据 |
|---|---|---|
| 色彩/字体/间距/圆角/边框/阴影令牌 | `V11R-D-1` | 生成器 + 键清单 |
| Button/Input/Card/Dialog/Menu/Tab 等组件 | `V11R-D-1` | 组件测试 + 画廊截图 |
| Hover/Pressed/Focus/Disabled/Loading/Error 状态 | `V11R-D-1` | 状态矩阵断言 |
| 动效/缩放/无障碍规范 | `V11R-D-1` | reduced-motion + 对比度测试 |
| 主题资源与组件绑定规则 | 契约 §2 + `V11R-D-1` | 无裸值断言 |
| 独立审查后冻结 V1 契约 | `V11R-VERIFY-1` | 审查报告 |
| B/C 共用一套设计系统 | 全部 UI 任务 | 零第二套定义断言 |

## 5. 用户指令 §九（分层验证）→ 门

| 等级 | 适用范围 | 当前安排 |
|---|---|---|
| L1 | DS 组件、服务层、单屏实现 | Owner 自检 + 单测（每任务） |
| L2 | 功能组（建书建章导入、Run 控制、Region 编辑、主题切换） | 功能测试 + 必要时独审 |
| L3 | M1 基座 / M2 新壳可用 / M3 全工作面 / M4 退役集成 | 独立 Reviewer（Codex/ZCode） |
| L4 | 发布验收 | 全量回归 + E2E 十旅程 + 实机 + 独立 Release Audit |
| 高风险 | `V11R-F0-1`（数据/Revision）、`V11R-C-3`（删除/迁移）、IPC 契约冻结 | 强制独立审查，不等 L4 |

## 6. 审计 E2E-01…E2E-10 → 归属

| E2E | 内容 | 归属 | 状态 |
|---|---|---|---|
| E2E-01 | 空库→建书→建章→导入→重启 | A-1 + B-1 + INT-1 | pending |
| E2E-02 | 真实 Run（检测/OCR/翻译/渲染） | A-2 + B-4 + L4 | pending |
| E2E-03 | 暂停/继续/停止/重启/重试 | A-2 + B-4 | pending |
| E2E-04 | 编辑区域/文字→保存→撤销 | F0-1 + B-3 | pending |
| E2E-05 | 长图阅读/章节切换/进度 | B-1 + L4 | pending |
| E2E-06 | 导出 ZIP/PDF/取消/历史 | B-5 + 既有导出命令 | pending |
| E2E-07 | Provider/网络代理/凭据真实 Run | B-2 + A-2 + L4 | pending |
| E2E-08 | Windows 11 实机 DPI/长图/IME/Esc | L4（需实机） | NOT_RUN |
| E2E-09 | 旧数据备份→升级→卸载→重装 | L4（沿用既有升级证据 + 新包） | pending |
| E2E-10 | 干净 Windows clone 构建 | A-4 + L4 | pending |
