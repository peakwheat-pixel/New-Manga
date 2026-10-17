# P19 AC2 主流程执行计划（可直接执行，2026-10-17）

## 前置（已就绪）
- 产品已重建并校验：前端 dist `index-B2KOm56c.js`、sidecar HEAD=`3b9eff81c`、`bundle==resource` hash `4086E22B193A148E`
- AC4 已实测修复（`ac4-verified-rebuilt-r5.md`，9/9 `IsEnabled=False`）
- 可重放脚本范式：`verification/P19/run-d-acceptance-v2.ps1`（隔离 `NEWMANGA_DATA_ROOT`、逐页 UIA 转储、trace.log）

## 产品约束（**关键**，来自 P19-UI-FIX-1）
空书架时 `import-file-btn`/`import-folder-btn` **disabled**，界面显示「未开放：空书架暂不支持创建作品和章节，当前无法导入文件或文件夹。」
→ **导入前必须使数据具备"可导入目标/章节"**。

## 步骤（按序，每步留 UIA 转储 + trace）

1. **准备数据（二选一，优先 A）**
   - **A. 走真实 UI**：书架 `+ 新建作品` → 填标题 → 建章节 → 确认章节出现在工作台/阅读器可选列表
   - B. 复制一份**含章节**的用户数据副本到隔离根（`catalog/`+`data/`），如 UI 建作品路径不可用则用 B 并**如实声明**
2. **导入**：点 `导入作品` → 若为 A 路径应出现可用目标 → 选择 `p19-fixture/作品A/`（或 `.cbz`）→ 断言：书架出现该作品、`library_list_books` 结果非空
   - 若仍无选择器 → **记录为缺陷**（不得跳过）
3. **Run**：工作台 → 选择作品与章节 → 启动 Run → 断言：Run 状态迁移（如 running→done/blocked），UIA 文本与 trace 留证
4. **导出**：工作台导出面板 → 指定隔离目录 → 断言：导出完成、目标目录产生文件（**导出目标须在隔离区**，不得写用户路径）
5. **阅读器翻页**：书架选作品→章节 → `进入阅读`/`继续` → 断言：页面渲染 + `下一页`/`上一页` 可用且页码/内容变化
6. **更新证据**：把上述转储/轨迹写入 `verification/P19/d-mainflows-*.md` 与 `d-mainflows/`；更新 `doc/handoffs/P19-dsh.md`（Handoff 必须反映**R2 后的真实状态**：AC4 已修、AC2 已跑）

## 之后
- **Codex R3**（可写沙箱；要求其**独立复跑前端套件**，并核 AC3/AC6）
- 依 R3 → closeout P19（`done` 或经用户确认的 `closed_with_limitations`）→ **释放 P20**
- **P20 发布 Gate（必须写入）**：`npm run build` → `build_sidecar.ps1 -Force` → `cargo build` → **校验 bundle==resource hash** → 启动 smoke（应用能起 + 四页可达）

## 已知风险
- 建作品/章节路径若因能力未实现而不可用 → 属**新产品缺陷**，须先修再跑（不得用"数据副本"掩盖）
- 导出写盘须限定隔离目录；`library_import_*` 的失败路径也要留证（负例）