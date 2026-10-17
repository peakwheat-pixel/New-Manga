# P19 AC4 修复验证（重建后的真实产品，2026-10-17）

- 执行者：dsh；**用重建并校验过的产品**（前端 dist 重编 `index-B2KOm56c.js`、sidecar 重建 HEAD=`3b9eff81c`、`cargo build` 重编；**bundle 与 resources 的 core_service.exe hash 一致 `4086E22B193A148E`**）
- 环境：隔离 `NEWMANGA_DATA_ROOT`（真实布局副本：`catalog`+`data` 从 `%APPDATA%` 只读复制，+ 空 `derived`）；**未修改用户真实数据**
- 操作：UIA Invoke `⚙️ 设置` → 枚举所有名称含「未开放」的 Button 并读取 `IsEnabled`

## 结果（9/9 真禁用）

```
OCR，未开放：等待 section schema 冻结          => IsEnabled=False
图片修复，未开放：等待 section schema 冻结      => IsEnabled=False
排版样式，未开放：等待 section schema 冻结      => IsEnabled=False
模型/GPU，未开放：等待 section schema 冻结     => IsEnabled=False
任务/并发，未开放：等待 section schema 冻结     => IsEnabled=False
缓存/Revision，未开放：等待 section schema 冻结 => IsEnabled=False
回收站，未开放：等待 section schema 冻结        => IsEnabled=False
备份/恢复，未开放：等待 section schema 冻结     => IsEnabled=False
Plugin/Hooks，未开放：等待 section schema 冻结  => IsEnabled=False
count=9  disabled=9
```

## 判定

- **Codex R2 判 FAIL 的 AC4 缺陷已实际修复**：修复前后对比——
  - 修复前：`Button … en=True`，逐个 Invoke 成功且页面变化（`d-run-v2/uia/04-settings.uia.txt`、`trace.log`）
  - 修复后：**`IsEnabled=False`（9/9）**，且**可见性保留**（仍在列表中）、**原因文案更明确**（"等待 section schema 冻结"）
- 本验证针对的是**集成后并重建的产品**，非工作树源码，故可作为 R3 的 AC4 依据。

## 仍未覆盖（交 P19 AC2 / R3）

- **AC2 主流程**：导入→Run→导出、阅读器翻页（需先具备可用章节数据；产品约束：空书架时导入显示"未开放"提示）
- 前端测试套件需 R3 独立复跑一次（本轮未跑）