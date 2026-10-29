# 阶段 4 实施计划（融合方案 A+C）

> 依据：`FUSION_SPEC.md`（结构）、`DESIGN_SYSTEM.md` + `tokens.json`（视觉与组件）。
> 原则：**先补能力、再搭骨架、后填模块**；每个阶段都有可验证的完成判据，不做"一次性大爆炸"重写。

---

## 0. 基线与隔离

| 项 | 内容 |
|---|---|
| 基线 commit | `main@65d9efa19`（设计产物在 `agent/dsh/UIUX-REDESIGN-1@06c2c9dec`） |
| 实施分支 | `agent/dsh/UIUX-FUSION-IMPL-1`（从设计分支拉出，独立 worktree） |
| 回退基线 | 实施前打 tag `baseline-pre-fusion-impl`；旧前端代码全部保留在 Git 历史，不做 `git rm` 之外的破坏性操作 |
| 用户数据 | 不改 DB schema、不迁移用户数据；新前端只经现有 IPC（及 F0 新增命令）访问 |
| 生产代码边界 | 只新增/替换 `apps/desktop/frontend/**`；`src-tauri/**` 与 `src/**` 仅在 F0 契约任务内改动 |

---

## 1. 阶段划分

```
F0 能力补齐 ──► F1 令牌与基座 ──► F2 应用骨架 ──► F3 模块实施 ──► F4 联调运行 ──► F5 质量门
   (Core/IPC)      (设计系统落地)     (三空间+双模式)    (六个工作面)      (真实 Tauri)     (QA/无障碍/复核)
```

### F0 · 能力补齐（阻塞项，必须先做）

**为什么必须前置**：`00-facts/05_GAP_LIST.md` 的 B 类缺口里，Region 写面（B-02）全缺 —— 设计中的 Region 编辑主路径在现有 IPC 上**跑不通**。若先做 UI，等于把界面建在不存在的通道上。

| 任务 | 内容 | 验收 |
|---|---|---|
| F0-1 | Core 新增区域写面命令：`create_region` / `delete_region` / `save_region_geometry` / `merge_regions` / `split_region` / `reorder_regions` / `save_manual_translation` / `confirm_region_final` / `set_region_lock` / `pin_revision`（按 `application/editing/service.py` 已有实现接线，复用现有 commit seam） | 每条命令有 typed error；乐观锁（`expected_revision`）语义与 `INPUT_REVISION_CHANGED` 一致；pytest 覆盖 |
| F0-2 | Tauri 侧注册上述命令 + capability 白名单（production-only，沿用 option-B 先例） | `main.rs` 命令常量分组；capability JSON 更新；Rust 测试 |
| F0-3 | 导出 stale 策略（`abort` / `continue_existing`）确认与接线 | Core/Tauri/契约一致 |
| F0-4 | 术语表 / 不译表能力确认（A-01）：若确无实现，冻结为「二期能力」，UI 明确标注"待接入" | 事实结论写入 Task |

> F0 由 Core/Tauri 侧实施，与前端可并行启动 F1；但 **F3 的 Region 编辑模块必须等 F0-1/2 完成**。

### F1 · 令牌与组件基座

| 任务 | 内容 | 验收 |
|---|---|---|
| F1-1 | `tokens.json` → `src/styles/tokens.css`（双主题 CSS 变量），并写生成脚本（token → CSS），保证单一来源 | 脚本可复现；CSS 中无裸值 |
| F1-2 | 基础样式层：reset、字体栈、focus-visible、scrollbar、reduced-motion | 无全局副作用；暗/浅主题切换无闪烁 |
| F1-3 | 基础组件 10 个（Button/IconButton/Segmented/Chip/Input/Search/Select/Checkbox/Toggle/Progress/Badge/Kbd） | 每个有 6 态（default/hover/active/focus/disabled/loading）与单测 |
| F1-4 | 图标库：内联 SVG sprite（≥40 个），1.25px stroke | 视觉重量一致；无 emoji |

### F2 · 应用骨架

| 任务 | 内容 | 验收 |
|---|---|---|
| F2-1 | 应用外壳：`TopBand` + 三空间路由（Library/Studio/Console）+ 上下文保留 | 空间切换后 selection/滚动/筛选保持 |
| F2-2 | Studio 双模式：`Page` ↔ `Batch`（`Tab`），共享 selection store | 两模式互相切换 selection 一致；下钻/上浮双向可达 |
| F2-3 | 状态管理与数据层：IPC client 适配、投影订阅（`TaskProjection`）、事件失效处理、错误模型 | 单一数据源；无双重真值；事件只作失效提示 |
| F2-4 | 全局能力：命令面板（Ctrl+K，含空间/模式/作用域标注）、跳转（Ctrl+P）、键位注册表、焦点管理 | 命令覆盖全部业务动作；快捷键无冲突 |
| F2-5 | 通用状态组件：`EmptyState`/`AlertBanner`/`Modal`/`Drawer`/`Toast`/骨架屏 | 12 状态真相各自的呈现可被路由级演示 |

### F3 · 模块实施（六个工作面）

| 模块 | 内容 | 依赖 |
|---|---|---|
| F3-1 Library | 作品条目 / 章节账本 / 页网格 / 导入 dock（含部分失败）/ 回收站 / 阅读浮层（Paged RTL+LTR、Webtoon 纵向、双模态进度） | F0（B-01 书籍写面若缺则只读+标注） |
| F3-2 Studio · Page | 胶片条、画布三态（页面/成品/分屏）、Region 覆盖与几何编辑、HUD 环、检查器五页签（文本/样式/修复/锁定/历史） | F0-1/2（Region 写面） |
| F3-3 Studio · Batch | 阶段轨道（门禁）、状态矩阵（框选/下钻）、概览胶囊、批量动作条、Run 带、任务面板 | 现有 Run IPC |
| F3-4 Console | 任务队列、Provider/凭据、网络、模型/设备、缓存与版本、备份、插件 | 现有 settings IPC（19 条） |
| F3-5 导出 | 预检（未确认/过期/失败）+ 范围+格式+stale 策略 + 历史 | F0-3 |
| F3-6 术语与约束 | 术语表/不译表维护 + 冲突提示 + 应用到重译 | F0-4 |

### F4 · 真实运行与联调

| 任务 | 内容 | 验收 |
|---|---|---|
| F4-1 | `tauri dev` 真实启动（Python Core sidecar + 资源通道） | 冷启动到可用；无 IPC 报错 |
| F4-2 | 端到端走查：导入 → 处理 → 精修 → Batch 异常处置 → 导出 | 六条关键旅程（J1/J2/J4/J5/J6/J7）脚本化通过 |
| F4-3 | 性能：大图渲染（256 MiB 上限）、1000 行矩阵、分块加载 | 交互 ≥ 30fps；无内存泄漏 |
| F4-4 | 高 DPI：100/150/200% 实机截图 | 1px 线不消失、文字不裁切 |

### F5 · 质量门（Gate）

| Gate | 内容 | 证据 |
|---|---|---|
| G-QA1 交互测试 | Playwright/E2E 覆盖六条旅程 + 键盘可达 + 焦点陷阱 | 测试日志 + 录屏 |
| G-QA2 视觉 QA | 每个工作面 1600×1000 / 1280×800 / 暗浅双主题截图；与设计稿逐项比对 | 截图清单 + 差异记录 |
| G-QA3 无障碍 | 对比度（axe 扫描）、键盘全功能、状态非颜色单编码、`prefers-reduced-motion` | axe 报告 + 手工清单 |
| G-QA4 独立复核 | `uiux-verify` 角色只读复核，不得由实现者自审 | `VERIFY_REPORT.md`（`ISOLATED_SESSION` 起） |
| G-QA5 Gate 链 | `uiux-engine` G0–G6 正式链（需冻结 request 契约） | `finalize` 派生 TaskResult |

---

## 2. 首批任务（本轮可立即执行）

| ID | 任务 | 建议 Owner | 依赖 | 判据 |
|---|---|---|---|---|
| IMPL-1 | F1-1/F1-2 令牌编译与基础样式层 | DSH | 无 | CSS 变量可从 tokens.json 重建；双主题切换无裸值 |
| IMPL-2 | F0-1/F0-2 Region 写面 IPC 契约任务 | Core 侧 Agent（非 DSH 自审） | 无 | 命令可调用、typed error、测试通过 |
| IMPL-3 | F2-1/F2-2 应用骨架 + 双模式 | DSH | IMPL-1 | 三空间可切、双模式共享 selection |
| IMPL-4 | F3-3 Batch 矩阵（先用现有 Run IPC 投影） | DSH | IMPL-3 | 矩阵可框选/下钻/批量（真数据） |

---

## 3. 风险与对策

| 风险 | 影响 | 对策 |
|---|---|---|
| Region 写面 IPC 补齐耗时超预期 | F3-2 阻塞 | F3-2 先做只读呈现 + 标注"待接入"；F0 并行推进；不做假交互 |
| 旧前端能力覆盖缺口（B-01 书籍写面等） | Library 功能不全 | UI 明确标注能力状态，不假装；按 GAP 清单排序补齐 |
| 双模式共享 selection 的复杂度 | 状态管理混乱 | 单一 store + 明确的选择模型（选择是 UI 状态不是领域状态）；写单测 |
| 视觉实现走样（塑料感回归） | 交付质量不达标 | 令牌强制 + 视觉 QA 截图比对 + 独立复核 |
| 一次性重写范围过大 | 无法收敛 | 按工作面分批合入；每批可独立运行；旧分支可回退 |

---

## 4. 完成定义（DoD）

阶段 4 完成需同时满足：

1. 六个工作面全部可用，且仅通过现有 + F0 新增 IPC 访问后端。
2. 六条关键旅程在真实 Tauri 环境通过。
3. 12 个状态真相在真实数据下可复现（非 mock）。
4. 视觉 QA、无障碍、独立复核三份证据齐全且无 P0。
5. `uiux-engine finalize` 派生 TaskResult；Gate 结论由证据派生，不由自填。
6. 用户数据零破坏：源文件只读、Managed Copy 完整、既有 DB 可读。
