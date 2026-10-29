# V11R 需求 → 任务 → 证据 追溯矩阵 v1

状态：`ACTIVE`（2026-10-30，DSH）。用于 L3/L4 验收与最终报告；每行最终必须能指向**证据路径**，未取证一律 `NOT_RUN`。
说明：审计 F001–F108 与 66 命令 C001–C066 的逐条状态由 `V11R-A-3` 契约包 + 各任务证据补齐（本文件只维护需求域→任务映射，避免第二份真值）。

---

## 1. 用户指令 §三（V1.1 整改重点）→ 任务

| 用户要求 | 对应任务 | 验收证据 | 当前状态 |
|---|---|---|---|
| 108 项功能真实实现状态 | `V11R-A-3` + 各域任务 | 功能矩阵重核（实现/接入/运行/验证 四维） | **done**（A-3 FROZEN 49/PARTIAL 17/GAP 0；域任务全部合入；见 §9） |
| 66 条命令 DTO/参数/响应/错误码/协议版本 | `V11R-A-3` | 契约 + 派生 parity 测试 | **done**（C077 已真实登记并合入） |
| Core→IPC→Host→UI 完整调用链 | `V11R-A-1`/`A-2`/`INT-1` | 链路测试 + E2E | pending |
| 新建书籍/新建章节/文件导入 | `V11R-A-1` + `V11R-B-1` | E2E-01 | **PARTIAL（L2/L3 PASS；真机交互 E2E NOT_RUN）** |
| 检测/OCR/翻译/修复/渲染任务真实启动与管理 | `V11R-A-2` + `V11R-B-4` | E2E-02/03 | **PARTIAL（Run 控制/投影 L2/L3 PASS；真实模型推理 E2E NOT_RUN）** |
| 暂停/继续/停止/失败重试/阻塞恢复 | `V11R-A-2` + `V11R-B-4` | E2E-03 | **done**（含 R-22 幂等键、Stop 二次确认、gate 模态） |
| Region 编辑/气泡文本编辑/持久化 | `V11R-F0-1` + `V11R-B-3` | E2E-04 | **done**（F0 5 轮审查 + 独立窄验证 CLOSED；C077 投影已合入） |
| 多页上下文/术语表/SFX | `V11R-B-5` + Core 既有能力 | E2E-02 分支 + 术语冲突用例 | pending |
| 阅读器/导出/设置/Provider/网络代理 | `V11R-B-1`/`B-2`/`B-5` | 各屏 L2/L3 | **PARTIAL（导出一项 NOT_WIRED 诚实标注：术语读写/缩略图等 Core 能力缺口）** |
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

---

## 7. 滚动更新（2026-10-30）

| 事项 | 结论/状态 | 证据 |
|---|---|---|
| V11R-A-1 CreateChapter | done（合入 main） | `verification/V11R-A-1/` |
| V11R-A-2 IRunController | done（合入 main） | `verification/V11R-A-2/` |
| V11R-A-3 66 命令契约 | done：FROZEN 49 / PARTIAL 17 / GAP 0；C067–C077 单列 PENDING(minor=3) | `doc/contracts/V11R_COMMAND_CONTRACT_V1.md`、`verification/V11R-A-3/` |
| `library_start_run` minor 兼容 | **结论：升 minor=7 是必要条件非充分；现有命令路径无法透传 `provider_profiles`，UI 不得当已支持** | `verification/V11R-A-3/minor-compat/start-run-minor-probe.json` |
| V11R-A-5 生产写入策略（P0） | done：默认 ReadWrite + 三重护栏（旧壳运行/`--parity=false`/Host 未就绪）+ first-run 备份实证 | `doc/plan/V11R_WRITE_POLICY.md`、`verification/V11R-A-5/` |
| V11R-D-1 M0 + R-09 对比度 + palette seam | 已合入；P1/P2 返修中（独立审查 FAIL，见 `doc/reviews/V11R-D-1-r1-codex.md`） | `verification/V11R-D-1/` |
| V11R-F0-1 Region 写面 | I1 返修中（审查 FAIL：3×P1 原子性/并发/锁继承） | `doc/reviews/V11R-F0-1-r1-codex.md` |
| V11R-F0-2 Region 文本投影（C077） | 已交付待随 F0-1 返修复审后合入 | `verification/V11R-F0-2/` |
| V11R-B-1 / B-2 | B-1 PASS_WITH_ISSUES（返修中）；B-2 待第二轮审查 | `doc/reviews/V11R-B-1-B-3-r1-independent.md` |
| V11R-B-3 / B-4 | B-3 FAIL（P1 画布 Region 命中 + Modal 焦点证据作假，返修中）；B-4 待第二轮审查 | 同上 |
| V11R-C-1 Theme Engine Part A | done（159 测试，合入 main）；Part B 进行中（等 DS `ApplyThemeLayer`） | `verification/V11R-C-1/` |
| V11R-C-2 Theme Studio | 进行中（theme-studio Owner） | — |
| 集成裁定 | R-15 59 键层 / R-16 单一 selection / R-17 TryHandleKey / R-18 断点 / R-19 证据纪律 / R-20 App→ThemeEngine | `doc/V11R_PROGRAM.md §8` |

---

## 9. 收盘状态（main `e27e85524`）

| 需求域 | 结论 | 证据/说明 |
|---|---|---|
| 审计 108 项功能链路 | **PASS_WITH_NOT_RUN** | 所有能落到当前架构并已接入的功能面均实现且有 L2/L3 证据；真实模型推理/真机交互 E2E 标 NOT_RUN |
| 66 命令契约 | **PASS** | FROZEN 49 / PARTIAL 17 / GAP 0；C067–C077 已登记并合入；parity 测试从 registry 派生 |
| 新 UI/UX（A+C 融合） | **PASS** | 三空间 + Studio 双模式 + Theme Studio；新壳默认入口；真实窗口 L4 矩阵 7/7（Host 就绪 7/7） |
| Theme Engine 重建 | **PASS** | 235 测试；独立审查 PASS；零依赖旧 `NewManga.Theme` 断言 |
| Theme Studio 页面 | **PASS_WITH_ISSUES** | 7 分区真实生产服务；P2 已修（I1）；待窄验证签署 |
| 旧主题系统退役 | **PASS** | R1–R6 + I1 + 干净树 R6（`workingTreeDirty=false`、双壳 EXIT 0/0、零引用门） |
| 设计系统 | **PASS** | D-1 r4 PASS_WITH_ISSUES，P2 已闭；对比度矩阵 0/0 |
| 分层验证 L1–L4 | **L1–L3 PASS；L4 部分 NOT_RUN** | 全量 802 通过/0 失败；真实窗口矩阵 7/7；DPI/IME/Trim/AOT/真实交互未验证 |
| 独立审查 | **完成** | 14 份报告（Codex 6 + 独立 Reviewer 8），结论与处置均在 `doc/reviews/` |
| 验收报告 | **交付** | `doc/V11R_ACCEPTANCE_REPORT.md` |