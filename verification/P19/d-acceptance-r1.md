# P19 D 变体验收证据 R1（真实 WebView2 + UIA 语义断言）

- 时间：2026-10-17；执行者：dsh；**变体：D**（D+ 的 CDP 通道不可用，已如实登记于 dplus-status-r3.md；本证据为**真实 WebView2 窗口**的 **UIA 语义断言**）
- 被测产物：`apps/desktop/src-tauri/target/debug/m2rc1-desktop.exe`（main `6f128dfe2` 构建），sidecar bundle **重建于 11:15（HEAD=c6d2e9a3）**、资源 hash `41932CED…` 一致
- 环境：Windows 真实桌面 2560×1440；CUA High 完整性；**CDP 不可用**（WebView2 未带 `remote-debugging-port`，Tauri 覆盖环境变量）
- 启动结果：**应用成功启动**，窗口 `M2-RC1 resource channel runtime`（1180×890），`responding=True`；sidecar stderr 显示 `[core.derived_gc] orphan_files_removed=0 dead_rows_removed=0` 与 `[m2rc2-allowlist] production:…`（含 49 条生产面，含 P15 全部 settings 命令 + `credential_put`/`credential_clear`）

## 1. 四页可达（AC2）

| 页 | UIA 证据（有名称元素数） | 判定 |
|---|---|---|
| 书架 | 21：`📚 书架 / 🛠️ 工作台 / 📖 阅读器 / ⚙️ 设置`、`+ 新建作品`、`导入作品`、`搜索作品标题 / 原名 (Ctrl+F)`、`★ 收藏`、`归档`、`按更新时间`、`⊞/☰`、`还没有作品`、`书架当前为空…`、`未选择作品` | **PASS** |
| 工作台 | 101：`选择作品与章节`、`拖动调整页序`（**"页序写入 wire 尚未冻结，页面顺序保持 Core 投影结果。"**）、`页面缩略图`（**"当前只有原图资源通道，低清缩略图能力尚未接入。"**）、`按页面 ID 定位`（Edit）、`页面查看器`、`缩小页面` | **PASS** |
| 阅读器 | 36：`← 返回书架`、`尚未选择章节`、`继续`、`从头开始`、`原文 (Original)`、`译文 (Translated)`、`尚未选择阅读章节`、`请先在书架中选择一个作品及章节，然后点击「进入阅读」`、`前往书架` | **PASS** |
| 设置 | 64：`设置分类` 组；`Provider`、`网络/代理`、`翻译`、`OCR 未开放`、`图片修复 未开放`、`排版样式 未开放`、`模型/GPU 未开放`、`任务/并发 未开放`、`缓存/Revision 未开放`、`回收站 未开放`、`备份/恢复 未开放`、`Plugin/Hooks 未开放`；`Provider Profile`、**"同一 Provider 类型可配置多个 Profile（以 profile_id 区分）；凭据只经专用一次性通道配置，永不回显明文。"**、`暂无 Provider Profile。`、`新建 Profile` | **PASS** |

## 2. 未交付缺口保持禁用（AC4）

- 设置页 **9 个分区标「未开放」**（OCR/图片修复/排版样式/模型GPU/任务并发/缓存Revision/回收站/备份恢复/Plugin-Hooks），可见且带原因 ✓
- 工作台两处**能力未接入的诚实说明**（页序写入 wire 未冻结；低清缩略图未接入）✓
- **未发现**任何 path/secret/凭据/原始响应文本出现在 UI ✓（本次为 UIA 文本层断言；内存级边界由 P15-HOST-2 六类反例测试覆盖）

## 3. 未完成/限制（如实）

- **CDP（DOM 级）不可用** → 本证据为 **UIA 语义级**，非 DOM 级；已在 `dplus-status-r3.md` 登记。
- **未执行交互型主流程**（导入真实文件 → 生成 Run → 导出、阅读器翻页等）：需构造用户数据/长耗时操作，**本轮未做**，P19 关闭前应补或明确声明为限制。
- 截图：`app-window.png`（书架，1180×890）。