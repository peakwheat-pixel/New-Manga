# P19 AC2 主流程实测记录（2026-10-17，执行者 dsh）

- 产品：**重建并校验**的构建（`bundle==resource` hash `0041944060C42844`；dist 含 FEAT-CREATE-4 前端；exe 含 FEAT-CREATE-3 host）
- 数据：**隔离根** `%TEMP%\p19-ac2-r3`（由 `%APPDATA%\com.newmanga.m2rc1.desktop` 的 `catalog`+`data` **只读复制** + 空 `derived`）→ **用户真实数据未被修改**
- 素材：`%TEMP%\p19fx\A`（2 张 PNG，由 `p19-fixture/作品A` 复制到纯 ASCII 路径）

## ① 建作品 —— PASS
```
点击「+ 新建作品」：create_btn=True  IsEnabled=True      ← 用户裁决 A 的核心要求
表单控件：Edit「作品标题」 + Button「创建作品」（另有 取消/关闭）
填入 "E2E 作品 A" → 点「创建作品」
结果：空态消失（"书架当前为空" 不再出现）；出现作品行
      ☆ | 页数 | 章节数 | 章节列表 | + 新建章节
```
→ 经 `library_create_book` → Core `CreateBook`（2.8）**真实持久化到隔离根**。

## ② 建章节 —— PASS
```
表单控件：Edit「章节标题」 + Button「创建章节」
填入 "E2E 章节 1" → 点「创建章节」
结果：elements 61；出现「导入页面」入口（此前为"暂无章节，请点击…"）
```

## ③ 导入页面 —— **链路已证实现；完成动作未达成（工具限制）**
**代码级核验（三处齐备）**：
- host：`PRODUCTION_COMMANDS` 含 `library_import_file`/`library_import_folder`（`main.rs:119-120`）、handler（`L860/L889` → `import_from_path`）、`generate_handler!`（`L1526-1527`）
- Core：`handle_import_pages`（`core_service.py:1811`）+ 分发 `ImportPages`（`L2709/2715`）
- 前端：`client.ts:49-50` 定义两条命令并调用

**实测**：
```
章节级「导入」按钮（en=True）→ 面板出现「📄 选择图片/PDF 文件」「📁 选择图片文件夹」（均 en=True）
点「📁 选择图片文件夹」→ 原生对话框弹出：#32770 name='选择文件夹'  ✓
键盘驱动：AppActivate 成功 + Ctrl+L + 路径 + Enter + Alt+S 全部送达
应用内出现「⏳ 正在导入中...」→ 但轮询 70s 未完成；0 页入库；db 字节未变
```
**结论**：产品侧**选择器可弹出、链路完整**；**未完成的是"确认选择"这一步**（该 Explorer 选择器 UIA 不暴露确认按钮，`Alt+S` 未生效）→ **验收工具限制**，非产品缺陷。
**如实登记**：`pages_in_store=0`，③ **未达成**。

## ④ Run / ⑤ 导出 / ⑥ 阅读器翻页 —— **未执行**（依赖 ③ 的页面数据）

## 执行者自己的失误（务必留痕）
1. 先用**无章节上下文的** `导入页面` 面板，其「选择图片文件夹」为 `en=False`（正确行为），我一度误报为"缺陷" → 后更正为"入口选错"。
2. 一次在导入**进行中**用 `Stop-Process` 清理，**杀掉了正在导入的应用**，导致该次结果为空 → 属我操作失误。
3. 对 Explorer 选择器直接 `SetValue`/`FindFirst` 触发 `Operation timed out` → UIA 不适用于该控件，应改用键盘。

## 已确定的操作地图（供后续脚本/R3 复用）
| 用途 | 控件/操作 |
|---|---|
| 建作品 | Edit `作品标题` → Button `创建作品` |
| 建章节 | Edit `章节标题` → Button `创建章节` |
| 页面导入 | Button `导入` → Button `📁 选择图片文件夹` → Ctrl+L + 路径 + Enter + **确认（待定方式）** |
| 阅读 | Button `阅读` |