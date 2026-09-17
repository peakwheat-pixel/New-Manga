# 08 验收标准与 Release Gate（Target Acceptance Criteria）

> 本文件定义新漫画翻译软件的目标验收标准（To-Be），用于把 `01~07` 的功能、技术、数据、用户流程、UI、Pipeline 与非功能要求转换为可执行、可复现、可留证的验收项目。
>
> 本文件基于：
>
> - `01_FUNCTIONAL_ARCHITECTURE.md`
> - `02_TECHNICAL_ARCHITECTURE_.md`
> - `03_DATA_MODEL.md`
> - `04_USER_FLOW.md`
> - `05_UI_MAPPING.md`
> - `06_TRANSLATION_PIPELINE.md`
> - `07_NON_FUNCTIONAL_REQUIREMENTS.md`
>
> 本文件不重新设计产品。若验收项与前述文档发生冲突，应先修正文档，再修改验收标准，不能用测试代码“替代设计决策”。
> G06～G13 的验收前置语义以 [TASK-002 最小契约](contracts/TASK-002_MINIMUM_DATA_EXECUTION_CONTRACT.md) 为冻结解释。

---

# 1. 验收目标

Release Candidate 必须证明：

```text
功能正确
+
数据不丢
+
人工修改不被静默覆盖
+
长任务可暂停 / 停止 / 继续 / 恢复
+
Webtoon / Paged 均可工作
+
UI 与数据模型一致
+
Windows 环境可运行
+
性能达到目标基线
+
打包后仍可用
```

---

# 2. 验收级别

## 2.1 P0 / Blocker

任一失败：

```text
禁止发布
```

典型：

- 用户源文件被覆盖 / 删除；
- 人工确认译文被后台静默覆盖；
- 数据库损坏；
- Stop 回滚已完成成果；
- Crash 后任务误判 Completed；
- API Key 明文入库 / 入日志；
- 无法在干净 Windows 环境启动；
- 基础导入 / 翻译 / 保存 / 恢复链路不可用。

## 2.2 P1 / Major

原则：

```text
正式 Release 前必须通过
```

典型：

- 任务进度面板统计错误；
- Page 多选批处理错误；
- Translation Memory 污染；
- 双屏窗口恢复错误；
- Webtoon 坐标错误；
- Revision 无法恢复。

## 2.3 P2 / Minor

可以在 Release Notes 中明确后延期，但必须有 Issue / Follow-up。

典型：

- 非关键视觉间距；
- 部分辅助动画；
- 非核心快捷键。

---

# 3. 验收结果状态

每项只能为：

```text
PASS
FAIL
BLOCKED
NOT_RUN
N/A
```

禁止：

```text
大概通过
基本正常
看起来可以
```

---

# 4. 验收证据

每个 P0 / P1 验收项至少保留一种证据：

```text
自动化测试输出
测试日志
截图
录屏
数据库快照
Artifact Hash
Benchmark 结果
Git Commit / CI Run
```

推荐测试记录字段：

| 字段 | 说明 |
|---|---|
| Test ID | 唯一编号 |
| Priority | P0/P1/P2 |
| Environment | OS / App / Commit |
| Preconditions | 前置条件 |
| Steps | 执行步骤 |
| Expected | 预期 |
| Actual | 实际 |
| Result | PASS/FAIL/... |
| Evidence | 日志/截图/测试报告 |
| Notes | 备注 |

---

# 5. Release Gate 总览

```mermaid
flowchart LR

    CODE["Code Complete"]
    UNIT["Unit / Repository"]
    INT["Pipeline Integration"]
    UI["UI / Workflow"]
    DATA["Data Safety"]
    PERF["Performance"]
    PKG["Packaging"]
    CLEAN["Clean Windows Smoke"]
    RC["Release Candidate"]

    CODE --> UNIT --> INT --> UI --> DATA --> PERF --> PKG --> CLEAN --> RC
```

Release 必须满足：

```text
P0 = 100% PASS
P1 = 100% PASS
P2 = 无已知会破坏主流程的问题
```

---

# 6. 环境记录

每次完整验收记录：

```text
App Version
Git Commit
Schema Version
Windows Version
Python Version（开发验收）
PySide6 Version
CPU
RAM
GPU
VRAM
GPU Driver
CUDA / Runtime
Display DPI
Display Count
Primary Monitor Resolution
```

Provider 测试额外记录：

```text
Provider Profile
Model
Local / Remote
Network Profile
```

Secret 不得写入验收报告。

---

# 7. AC-NAV：启动与一级导航

## AC-NAV-001 [P0] 默认进入书架

**Given**

应用正常安装，数据库可用。

**When**

启动应用。

**Then**

```text
一级导航选中：书架
当前页面：BookshelfView
```

且不得：

```text
自动跳到工作台
自动跳到阅读器
```

---

## AC-NAV-002 [P0] 一级页面只有四个

必须只有：

```text
书架
工作台
阅读器
设置
```

作品详情、任务详情、标签管理等不得成为第五个一级 Route。

---

## AC-NAV-003 [P1] 一级页面切换保持上下文

**Given**

用户已打开：

```text
Book A
Chapter 12
Page 23
```

**When**

工作台 → 设置 → 工作台。

**Then**

返回工作台后：

```text
Book A / Chapter 12 上下文仍在
```

运行中的 Pipeline 不因离开页面停止。

---

# 8. AC-WIN：固定面板与悬浮窗

## AC-WIN-001 [P1] 固定位置优先

以下至少为固定区域：

```text
Bookshelf BookDetailPanel
Workbench PageListPanel
Workbench Viewer
Workbench RegionInspector
Workbench TaskProgressPanel
Settings 分类导航
```

不得全部实现成弹窗。

---

## AC-WIN-002 [P1] 编辑窗 Dirty Close

**Given**

编辑类悬浮窗存在未保存修改。

**When**

按 `Esc` 或关闭按钮。

**Then**

必须显示：

```text
保存
放弃
取消
```

---

## AC-WIN-003 [P1] 查看类外部关闭

查看类窗口允许点击窗口外关闭。

编辑类、危险确认类不得因此直接关闭。

---

## AC-WIN-004 [P1] 悬浮窗内容不溢出

验证：

```text
100%
125%
150%
175%
200%
```

Windows 显示缩放。

所有关键按钮、Footer、字段可访问。

---

## AC-WIN-005 [P1] 双屏拖动

悬浮工具窗可：

```text
主窗口内打开
→ 拖到第二屏
→ 调整大小
→ 最大化
```

业务内容不丢失。

---

## AC-WIN-006 [P1] 第二屏消失恢复

窗口上次位于第二显示器。

拔掉 / 禁用第二显示器后再次启动：

```text
窗口必须回到可见屏幕
```

不得恢复到屏幕外。

---

# 9. AC-LIB：书架与作品

## AC-LIB-001 [P0] 新建 Book

可创建：

```text
title
original_title
source_language
target_language
default_chapter_type
default_reading_direction
```

保存后立即出现在书架。

---

## AC-LIB-002 [P1] 自定义标签

支持：

```text
新增
重命名
删除
给 Book 添加
从 Book 移除
```

删除 Tag 不删除 Book。

---

## AC-LIB-003 [P1] 收藏 / 归档与 Tag 分离

收藏、归档必须作为系统状态存在。

不得通过普通 Tag 冒充。

---

## AC-LIB-004 [P1] 最近打开与阅读摘要

BookDetailPanel 能显示：

```text
最近阅读章节
阅读进度
最后阅读时间
累计阅读时长
```

---

# 10. AC-CH：Chapter

## AC-CH-001 [P0] Book → Chapter → Page

数据与 UI 层级必须固定：

```text
Book
→ Chapter
→ Page
```

不得引入必要的 Volume 层破坏主流程。

---

## AC-CH-002 [P0] Paged Chapter

可创建：

```text
chapter_type = paged
reading_direction = rtl 或 ltr
```

---

## AC-CH-003 [P0] Webtoon Chapter

可创建：

```text
chapter_type = webtoon
reading_direction = vertical
```

---

## AC-CH-004 [P1] 同一 Book 混合类型

同一个 Book 中：

```text
Chapter A = paged
Chapter B = webtoon
```

均可正常进入工作台 / 阅读器。

---

# 11. AC-IMPORT：导入

## AC-IMPORT-001 [P0] Managed Copy

**Given**

用户选择原图。

**When**

导入成功。

**Then**

必须：

```text
建立 Managed Copy
记录 source filename
记录 source order
记录 current sort order
记录 hash
记录 width / height
```

---

## AC-IMPORT-002 [P0] 用户源文件不修改

记录源文件 Hash。

完成：

```text
导入
翻译
重修
重渲染
删除项目
永久删除项目
```

后重新计算源文件 Hash。

必须完全一致。

---

## AC-IMPORT-003 [P0] Copy 中断不产生坏 Page

模拟 Copy 中断。

不得留下：

```text
数据库已有 Page
但 Managed Original 不存在
```

---

## AC-IMPORT-004 [P1] Unicode 路径

导入路径覆盖：

```text
中文
日本語
한국어
Emoji
空格
括号
```

全部成功。

---

## AC-IMPORT-005 [P1] 重复检测

相同图片再次导入：

```text
系统能依据 hash 检测重复
```

并按 UI 设定策略处理。

---

# 12. AC-PAGE：页面列表

## AC-PAGE-001 [P0] Page 顺序

同时保留：

```text
source_order
sort_order
```

拖拽重新排序只改变当前排序，不丢原始导入顺序。

---

## AC-PAGE-002 [P1] 多选范围

支持：

```text
单选
Ctrl 多选
Shift 连续多选
```

多选仅限当前 Chapter。

---

## AC-PAGE-003 [P1] Page 状态

Page Tile 至少可区分：

```text
等待
处理中
已完成
失败
跳过
已锁定
```

---

# 13. AC-WEBTOON：Webtoon

## AC-WEBTOON-001 [P0] 一张长图 = 一张 Page

导入一个超长 Webtoon 原图。

数据库与页面列表必须：

```text
只出现一个逻辑 Page
```

---

## AC-WEBTOON-002 [P0] Tile 不是 Page

处理期间生成多个 Tile。

验证：

```text
Page 表无新增 Tile Page
PageList 无 Tile
ReadingProgress 不引用 Tile
```

---

## AC-WEBTOON-003 [P0] 坐标回映

Tile 内检测到 Region 后：

```text
Region 坐标转换为 Original 全局坐标
```

Viewer Overlay 与最终渲染位置一致。

---

## AC-WEBTOON-004 [P1] 按宽缩放

Reader：

```text
按图片宽度适配
高度自然延伸
纵向滚动
```

不得将整张超长图压缩到一屏高度。

---

## AC-WEBTOON-005 [P1] Scroll 恢复

退出后再进入：

```text
last_page_id
scroll_offset_y
```

恢复到合理位置。

---

# 14. AC-REGION：Region 基础

## AC-REGION-001 [P0] Region 统一模型

一个 Region 能关联：

```text
几何
OCR
译文
Mask
Inpaint
TextStyle
Review
Lock
Revision
```

不得拆成无法对应的多套 UI 临时对象。

---

## AC-REGION-002 [P1] 几何编辑

支持：

```text
新建
删除
移动
缩放
Polygon 编辑
合并
拆分
```

保存后重启应用仍存在。

---

## AC-REGION-003 [P1] Reading Order

支持人工调整 `reading_order`。

Translation Context 使用人工最终顺序。

---

## AC-REGION-004 [P1] Region Type

至少支持：

```text
对白
旁白
拟声词
标题
注释
其他
```

---

# 15. AC-OCR：OCR

## AC-OCR-001 [P0] 单 Region OCR

对一个 Region 执行 OCR：

```text
只更新目标 Region
```

同页其他 Region 不变化。

---

## AC-OCR-002 [P0] Re-OCR 不覆盖人工译文

**Given**

Region 有：

```text
edited_translation
final_translation
translation_locked = true
```

**When**

重新 OCR。

**Then**

必须：

```text
ocr_text 可更新
人工译文保留
final_translation 保留
```

并提示：

```text
原文已变化，现有译文可能需要重译
```

---

## AC-OCR-003 [P1] OCR Provider 优先级

验证：

```text
任务临时覆盖
>
章节
>
作品
>
全局
```

实际执行 Provider 与规则一致。

---

## AC-OCR-004 [P1] 韩漫 OCR

Chapter 为韩文 Webtoon，配置 PaddleOCR Korean。

执行 OCR：

```text
实际使用配置的 Korean OCR
```

复杂艺术字 fallback 只在已配置规则下执行。

---

# 16. AC-SFX：拟声词

## AC-SFX-001 [P1] 默认 Skip

`region_type = sfx` 且未覆盖设置。

自动翻译应：

```text
SKIP_POLICY
reason = sfx_skip
```

---

## AC-SFX-002 [P1] Translate

SFX Policy = translate：

```text
进入正常 Translation
```

---

## AC-SFX-003 [P1] Manual

SFX Policy = manual：

```text
自动 Translation 跳过
人工仍可编辑
```

---

# 17. AC-CONSTRAINT：翻译约束

## AC-CONSTRAINT-001 [P0] 优先级

同一术语：

```text
Global = A
Book = B
Chapter = C
```

当前 Chapter Translation 必须使用：

```text
C
```

---

## AC-CONSTRAINT-002 [P0] 人工锁定优先

人工锁定项存在时：

自动术语识别不得覆盖。

---

## AC-CONSTRAINT-003 [P1] Candidate Status

自动术语候选支持：

```text
active
pending
rejected
disabled
```

---

## AC-CONSTRAINT-004 [P1] Rejected 不重复推荐

同一标准化术语被用户 Reject 后：

后续自动识别不得无条件重复创建同一候选。

---

# 18. AC-TM：Translation Memory

## AC-TM-001 [P0] 未确认机器译文不写 TM

自动 Translation 完成但未人工确认：

```text
TM 中不得新增正式记录
```

---

## AC-TM-002 [P0] 人工确认写 TM

人工确认 final_translation 后：

```text
允许写入 TM
```

---

## AC-TM-003 [P1] 查询优先级

验证：

```text
当前作品 Exact
→ 当前作品 Fuzzy
→ 全局 Match
```

---

## AC-TM-004 [P1] TM 不覆盖人工译文

命中 TM：

```text
只能作为翻译参考
```

不得静默覆盖当前人工 final。

---

# 19. AC-TRANS：Translation

## AC-TRANS-001 [P0] 四级文本

Region 可区分：

```text
ocr_text
machine_translation
edited_translation
final_translation
```

---

## AC-TRANS-002 [P0] 人工编辑自动保护

人工修改译文并保存：

```text
manual_edited = true
translation_locked = true
```

---

## AC-TRANS-003 [P0] Context 与 Write Scope

**Given**

单页翻译读取上下 5 页 Context。

**Then**

数据库只允许更新目标 Page / Region。

不得修改上下文 Page。

---

## AC-TRANS-004 [P1] 多页上下文排序

Context 内文本顺序必须遵守：

```text
Page sort_order
+
Region reading_order
```

---

# 20. AC-LOCK：四类 Lock

## AC-LOCK-001 [P0] Page Lock

Page Lock 后执行 Chapter 批量翻译：

```text
该 Page 不被自动处理
```

---

## AC-LOCK-002 [P0] Region Lock

Region Lock 后：

```text
该 Region 自动 OCR / Translation / Inpaint 等跳过
```

---

## AC-LOCK-003 [P0] Translation Lock

Translation Lock 后：

```text
自动重译不得覆盖
```

但：

```text
允许重新渲染
```

---

## AC-LOCK-004 [P0] Inpaint Lock

Inpaint Lock 后：

```text
自动重修不得执行
```

但：

```text
允许使用当前 Clean 重新渲染
```

---

## AC-LOCK-005 [P0] 写入时再次检查 Lock

模拟：

```text
后台 Translation 已发出请求
→ 用户在返回前手工编辑并锁定
→ Provider 返回
```

后台结果不得覆盖用户最新内容。

---

# 21. AC-REV：Revision

## AC-REV-001 [P0] 成功重跑创建新 Revision

重译 / 重修 / 重渲染成功：

```text
新增 Revision
更新 current pointer
旧 Revision 保留
```

---

## AC-REV-002 [P0] 失败不改变 current

新 Inpaint / Render 失败：

```text
旧 current 仍可使用
```

---

## AC-REV-003 [P1] Pin

Pinned Revision：

```text
执行自动清理后仍保留
```

---

## AC-REV-004 [P1] 恢复 Revision

恢复旧 Revision：

```text
先确认
→ 创建可追踪恢复记录
→ current 指向恢复后的版本
```

---

# 22. AC-STYLE：自动字号与排版

## AC-STYLE-001 [P0] 自动字号

Region 默认：

```text
auto_font_size_enabled = true
```

有可靠原图字号时：

```text
优先使用原图字号估算
```

---

## AC-STYLE-002 [P1] Offset 范围

UI 允许：

```text
-5 ... +5
```

不得超出。

---

## AC-STYLE-003 [P0] Shrink-to-fit

译文超过 Region 容量：

```text
自动缩小直到可放入
```

不得直接溢出气泡 / Region。

---

## AC-STYLE-004 [P1] 不自动放大

译文很短时：

```text
不自动放大超过原图估算字号
```

---

## AC-STYLE-005 [P1] Region 关闭自动字号

单 Region：

```text
auto_font_size_enabled = false
```

后手动字号保持。

---

# 23. AC-INPAINT：图片修复

## AC-INPAINT-001 [P0] Mask 持久化

重新打开项目后：

```text
仍能查看当前 Mask Revision
```

---

## AC-INPAINT-002 [P0] 新 Clean 不覆盖旧版本

重新修复：

```text
生成新 ArtifactRevision
```

旧 Clean 保留。

---

## AC-INPAINT-003 [P1] Router provenance

可追踪：

```text
Provider
Model
Options
Router Reason
Fallback Chain
```

---

## AC-INPAINT-004 [P1] Webtoon Color Route

彩色 Webtoon 复杂背景场景：

Router 能按已配置策略选择彩色修复能力。

不要求每次必须使用同一模型，但选择必须可追踪。

---

# 24. AC-RENDER：Rendering

## AC-RENDER-001 [P0] 重新渲染不触发 OCR

执行单页 / 选择页 / 全部重新渲染。

验证：

```text
无 OCR StepRun
无 Translation StepRun
无 Inpaint StepRun
```

---

## AC-RENDER-002 [P0] 缺 Clean 时阻止

没有可用 Clean Artifact 时执行 rerender：

```text
BLOCKED
```

UI 提示先修复。

不得偷偷自动 Inpaint。

---

# 25. AC-RFULL：单 Region 重全翻译

## AC-RFULL-001 [P0] 完整链

必须覆盖：

```text
OCR
→ Color
→ Term Extract
→ Translate
→ Segment
→ Mask Refine
→ Inpaint
→ Render
→ Save
```

---

## AC-RFULL-002 [P0] 只写目标 Region

同 Page 有 Region A/B/C。

对 B 执行重全翻译：

```text
A / C 的 OCR / Translation / Lock / Revision 不变化
```

---

## AC-RFULL-003 [P0] Page / Region Lock 阻止

存在 Page Lock 或 Region Lock：

```text
不能直接执行
```

必须先明确解锁。

---

## AC-RFULL-004 [P0] 专项 Lock 临时覆盖

存在：

```text
Translation Lock
Inpaint Lock
```

用户确认本次覆盖后：

```text
本次可执行
原锁值执行后仍保持 true
```

---

## AC-RFULL-005 [P0] 人工结果保护点

覆盖人工确认 final 前：

```text
必须明确提示
旧 Revision 必须保留
```

---

# 26. AC-CMD：批处理命令

## AC-CMD-001 [P0] 全部翻译复用 OCR

已有有效 OCR。

执行：

```text
全部翻译
```

验证：

```text
OCR = SKIP_VALID
Translation = RUN
```

---

## AC-CMD-002 [P0] 跳过已翻译

执行：

```text
全部翻译（跳过已翻译）
```

已完成 Page：

```text
不得重新翻译
```

未完成 / failed / missing：

```text
进入处理
```

---

## AC-CMD-003 [P1] 选择页目标冻结

选择非连续：

```text
Page 2
Page 7
Page 11
```

开始任务后改变 UI selection。

实际 Run 仍必须只处理：

```text
2 / 7 / 11
```

---

## AC-CMD-004 [P1] 单页命令

单页翻译 / OCR / 重修 / 重渲染：

不得影响其他 Page。

---

# 27. AC-PIPE：Pipeline DAG

## AC-PIPE-001 [P0] StepRun 可追踪

每个执行步骤能关联：

```text
PipelineRun
PipelineTask
StepRun
Target
Provider
Model
Options
Status
Time
```

---

## AC-PIPE-002 [P0] 有效 Step 可 Skip

已有有效输出且输入 / 设置未变化：

```text
SKIP_VALID
```

不得无意义重复推理。

---

## AC-PIPE-003 [P0] Stale 不当作 Valid

上游改变后：

```text
旧结果可保留
但不得作为“当前有效完成”继续错误复用
```

若 03 尚未加入正式 `stale` 枚举，必须通过等价状态实现并在同步文档中修正。

---

## AC-PIPE-004 [P0] Missing prerequisite

例如 translate 目标无 OCR：

```text
允许自动补齐必要 prerequisite
```

但 rerender 缺 Clean：

```text
不得补 Inpaint
```

必须遵守命令语义。

---

# 28. AC-PAUSE：暂停 / 继续

## AC-PAUSE-001 [P0] 暂停请求

Running 时点击暂停：

```text
UI ≤ 200 ms 显示“正在暂停”
```

---

## AC-PAUSE-002 [P0] 安全边界

Provider 不支持中途暂停：

```text
当前 Step 可完成
→ 不启动下一个 Step
→ Run = paused
```

不得留下半 Commit。

---

## AC-PAUSE-003 [P0] 继续

Paused → Continue：

```text
已成功且有效 Step 不重跑
从第一个未完成 / stale Step 继续
```

---

# 29. AC-STOP：停止

## AC-STOP-001 [P0] 停止不回滚

已有 27 页完成。

点击停止：

```text
27 页结果仍存在
```

---

## AC-STOP-002 [P0] Pending Cancel

剩余尚未开始 Task：

```text
转为 cancelled
```

---

## AC-STOP-003 [P0] Stop 不是 Delete

任务停止后：

```text
Run History 仍存在
Artifact / Revision 仍存在
```

---

# 30. AC-CRASH：异常退出恢复

## AC-CRASH-001 [P0] Running → Interrupted

在任务运行中强制结束程序。

重启：

```text
不得显示 Completed
必须识别为 interrupted
```

---

## AC-CRASH-002 [P0] Resume

选择继续：

```text
已完成 Step 不重复
未安全提交 Step 重跑
```

---

## AC-CRASH-003 [P0] Temp Artifact

Crash 后未 Commit 临时文件：

```text
不得成为 current ArtifactRevision
```

可被清理。

---

# 31. AC-RETRY：失败与重试

## AC-RETRY-001 [P0] 失败保留上游结果

OCR 成功，Translation 失败。

重试：

```text
OCR 不重跑
Translate 从失败点继续
```

---

## AC-RETRY-002 [P1] 失败页重试

批量任务：

```text
38 成功
2 失败
```

点击“重试失败页”：

```text
新建新 Run
仅含失败目标
```

原 Run 历史保留。

---

# 32. AC-PROGRESS：任务进度面板

## AC-PROGRESS-001 [P0] 固定底部

工作台必须存在固定 `TaskProgressPanel`。

不得只依赖弹窗。

---

## AC-PROGRESS-002 [P0] 显示内容

运行时至少显示：

```text
任务名
百分比
当前流程 / Step
当前 Page
完成页数
失败页数
阻塞页数与原因
跳过页数
等待页数
暂停
停止
继续
```

---

## AC-PROGRESS-003 [P0] 当前 Page 定位

点击当前 Page：

```text
PageList 自动滚动定位
```

---

## AC-PROGRESS-004 [P1] 失败统计联动

点击：

```text
失败 2
```

PageList 筛选出对应失败 Page。

---

## AC-PROGRESS-005 [P1] 完成统计联动

点击已完成 / 跳过：

PageList 显示对应集合。

---

## AC-PROGRESS-006 [P0] CompletedWithFailures

38 Page 成功、2 Page 失败：

```text
Run = 已完成（有失败）
```

不得把 38 页成功结果视为整体失败。

---

## AC-PROGRESS-007 [P0] PageList 同源

TaskProgressPanel 显示某 Page completed 时：

PageList 不能同时显示 running。

---

# 33. AC-PROVIDER：Provider

## AC-PROVIDER-001 [P1] 同 Provider 多 Profile

允许：

```text
OpenAI-翻译
OpenAI-VisionOCR
OpenAI-备用
```

同时存在。

---

## AC-PROVIDER-002 [P0] Capability 默认绑定

OCR 与 Translation 可以使用不同默认 Profile。

---

## AC-PROVIDER-003 [P0] Run Snapshot

Run 启动后修改全局 Provider：

```text
当前 Run 不静默切换
```

---

## AC-PROVIDER-004 [P0] Provider 消失后的恢复

Interrupted Run 原 Provider 被删除：

```text
不得静默选择其他 Provider
必须要求用户确认重新绑定
```

---

# 34. AC-FALLBACK：Fallback

## AC-FALLBACK-001 [P0] 无配置不跨 Provider

Translation Provider 失败，未设置 fallback：

```text
Step Failed
```

不得随机换另一个模型。

---

## AC-FALLBACK-002 [P1] 显式 fallback

配置：

```text
Primary → Secondary
```

Primary 发生允许 fallback 的错误后：

```text
Secondary 执行
```

Provenance 记录两次尝试。

---

# 35. AC-NET：网络与代理

## AC-NET-001 [P0] 多 Network Profile

可以创建多个：

```text
Direct
System
HTTP
HTTPS
SOCKS5
```

Profile。

---

## AC-NET-002 [P0] Proxy Failure 不静默 Direct

代理配置错误：

```text
任务失败 / 明确提示
```

默认不得直连。

---

## AC-NET-003 [P0] 显式 Direct Fallback

仅当：

```text
allow_proxy_failure_direct_fallback = true
```

才允许。

UI / Audit 可追踪。

---

## AC-NET-004 [P1] Connection Test 分阶段

至少显示：

```text
DNS
TCP
TLS
HTTP
Provider Auth
```

错误不能都显示成“连接失败”。

---

# 36. AC-SEC：Credential 与安全

## AC-SEC-001 [P0] SQLite 无 Secret 明文

扫描数据库：

不得出现完整：

```text
API Key
Proxy Password
```

---

## AC-SEC-002 [P0] 日志无 Secret 明文

运行连接测试、Provider 错误后检查日志。

不得出现 Secret。

---

## AC-SEC-003 [P0] Credential Manager

SQLite 只保存：

```text
credential_ref
```

实际 Secret 存放受保护 Credential Store。

---

## AC-SEC-004 [P0] TLS 默认开启

新 Network Profile：

```text
verify_tls = true
```

---

## AC-SEC-005 [P1] 关闭 TLS 必须确认

关闭时必须出现危险确认。

---

# 37. AC-ART：Artifact 原子性

## AC-ART-001 [P0] 成功 Commit

Artifact：

```text
临时写入
→ 验证
→ 正式路径
→ DB current pointer
```

完成后文件与 DB 一致。

---

## AC-ART-002 [P0] Commit 中断

模拟：

```text
文件生成成功
DB Transaction 前崩溃
```

旧 current 不改变。

---

## AC-ART-003 [P0] Hash

Current Artifact 有可验证 Hash。

---

# 38. AC-DB：SQLite 与 Migration

## AC-DB-001 [P0] Foreign Key

数据库开启：

```text
foreign_keys
```

非法外键写入被拒绝。

---

## AC-DB-002 [P1] WAL

正常生产数据库使用目标 journal 模式。

若最终实现未使用 WAL，必须有明确替代设计和测试证据。

---

## AC-DB-003 [P0] Migration 前备份

任何 Schema Migration：

```text
先生成可恢复 Backup
```

---

## AC-DB-004 [P0] Migration 失败

模拟失败：

```text
不得留下半迁移可写数据库
```

---

## AC-DB-005 [P0] 新 Schema 被旧 App 打开

旧版 App：

```text
拒绝写入
或只读
```

不得盲写。

---

# 39. AC-BACKUP：备份与恢复

## AC-BACKUP-001 [P0] 手动备份

可创建可恢复数据库 / 项目备份。

---

## AC-BACKUP-002 [P1] 自动备份

满足自动策略条件时：

```text
生成自动备份
```

---

## AC-BACKUP-003 [P0] Restore 前再次备份

执行恢复前：

```text
当前状态先备份
```

---

## AC-BACKUP-004 [P0] Restore 不改源文件

恢复项目后：

用户源文件 Hash 不变化。

---

# 40. AC-TRASH：回收站

## AC-TRASH-001 [P0] 软删除

删除 Book：

```text
进入软件回收站
```

不是立即物理清除。

---

## AC-TRASH-002 [P1] Batch Restore

恢复 Book：

只恢复同一删除 batch 中随 Book 一起删除的子项。

---

## AC-TRASH-003 [P0] 永久删除确认

永久删除必须明确确认。

---

## AC-TRASH-004 [P0] 源文件安全

永久删除项目后：

用户原始导入文件仍存在。

---

# 41. AC-EXPORT：导出

## AC-EXPORT-001 [P0] 格式

至少支持：

```text
单图
ZIP
CBZ
PDF
文本
```

---

## AC-EXPORT-002 [P1] ExportHistory

导出后记录：

```text
类型
范围
时间
输出路径
状态
```

---

## AC-EXPORT-003 [P1] Stale 提示

存在 stale / 未最新渲染 Page 时导出：

必须提示。

允许用户：

```text
先重渲染
或明确继续导出现有版本
```

---

# 42. AC-READ：阅读器

## AC-READ-001 [P0] Original / Translated

可切换两种阅读模式。

---

## AC-READ-002 [P1] 独立阅读进度

Original 与 Translated 分别保存进度。

---

## AC-READ-003 [P1] RTL

RTL Chapter 翻页方向正确。

---

## AC-READ-004 [P1] LTR

LTR Chapter 翻页方向正确。

---

## AC-READ-005 [P1] Webtoon Vertical

Vertical Chapter 纵向滚动正确。

---

# 43. AC-PERF：性能

> 性能基线来自 07，均需在固定 Benchmark 环境记录 P50/P95 或至少多次重复结果。

## AC-PERF-001 [P1] 冷启动

普通状态、不加载大型模型：

```text
P95 ≤ 3 秒
```

若未达到：

```text
FAIL 或记录正式豁免
```

不能口头忽略。“正式豁免”如何影响 §5 的 P1 = 100% PASS 仍待用户决定；当前没有生效的豁免，未达到阈值按 FAIL 记录并阻塞 Release。后续如批准例外，必须同步 D07、本条与 Release Gate，不能仅凭一条豁免备注把 FAIL 改为 PASS。TASK-001 保留现有阈值和 P1 优先级。

---

## AC-PERF-002 [P1] 一级页面切换

```text
P95 ≤ 300 ms
```

---

## AC-PERF-003 [P1] 固定面板响应

```text
P95 ≤ 200 ms
```

---

## AC-PERF-004 [P1] Book 搜索

2,000 Book：

```text
P95 ≤ 150 ms
```

---

## AC-PERF-005 [P1] Translation Memory Exact

常规数据集：

```text
P95 ≤ 50 ms
```

---

## AC-PERF-006 [P1] Translation Memory Fuzzy

常规数据集：

```text
P95 ≤ 200 ms
```

---

# 44. AC-CAP：容量 / 压力

## AC-CAP-001 [P1] Library

Fixture：

```text
2,000 Book
20,000 Chapter
100,000 Page metadata
```

书架可启动、搜索、滚动、筛选。

---

## AC-CAP-002 [P1] Chapter 1000 Page

PageList 可滚动、选择、筛选。

不得创建 1000 个全尺寸图片对象。

---

## AC-CAP-003 [P1] 200 Region

单 Page 200 Region：

Viewer 仍可选择 / 编辑 Region。

---

## AC-CAP-004 [P1] 200k Webtoon

约：

```text
1600 x 200000 px
```

Webtoon 可：

```text
打开
滚动
处理 Tile
恢复 Scroll
```

且不会因为一次性全分辨率解码导致应用崩溃。

---

# 45. AC-MEM：内存

## AC-MEM-001 [P1] Core Idle

无重型 AI 模型：

```text
RSS 目标 ≤ 600 MB
```

作为目标基线记录。

---

## AC-MEM-002 [P1] 连续切页

连续浏览：

```text
500 Page
```

内存不能持续线性增长。

---

## AC-MEM-003 [P1] Floating Window

重复打开 / 关闭大型 Floating Window 100 次：

结束后内存回落到稳定平台。

---

# 46. AC-GPU：GPU / Device

## AC-GPU-001 [P0] GPU OOM 不崩主程序

模拟 OOM：

```text
Step Failed
UI 可诊断
App 继续运行
```

---

## AC-GPU-002 [P1] GPU Heavy 默认单并发

默认重型 Inpaint：

```text
并发 = 1
```

除非 Provider 明确允许。

---

## AC-GPU-003 [P1] CPU Fallback 可追踪

支持 CPU fallback 的 Provider：

GPU 不可用时切 CPU。

UI / provenance 显示实际 Device。

---

# 47. AC-CACHE：Cache

## AC-CACHE-001 [P0] 清 Cache 不删业务真值

清理：

```text
Webtoon Tile
Thumbnail Cache
Render Temp
```

后项目数据仍可恢复 / 重建。

---

## AC-CACHE-002 [P0] Pinned 不清理

Artifact 清理不能删除 Pinned Revision。

---

## AC-CACHE-003 [P0] Active Pipeline 输入保护

Pipeline 运行期间清理 Cache：

不得删除正在使用的输入。

---

# 48. AC-DISK：磁盘保护

## AC-DISK-001 [P1] 低磁盘

模拟低于配置红线。

开始：

```text
大导入 / Backup / Export
```

系统必须警告或阻止高风险操作。

---

# 49. AC-LOG：日志与诊断

## AC-LOG-001 [P1] Log Rotation

超过单文件阈值：

```text
日志正常轮转
```

不无限增长。

---

## AC-LOG-002 [P1] Step 错误信息完整

Task Detail 能显示：

```text
Run
Task
Page
Region
Step
Provider
Model
Error Code
Retry
Timestamp
```

适用项不得缺失。

---

## AC-LOG-003 [P1] Diagnostic Bundle

可以导出诊断包。

默认不包含：

```text
用户原图
API Key
Proxy Password
```

---

# 50. AC-NFR-UI：UI 线程

## AC-NFR-UI-001 [P0] AI 不阻塞 UI

OCR / Translation / Inpaint 运行时：

```text
可以切换 Page
滚动
打开 Task Detail
切换设置页
```

UI 不冻结。

---

## AC-NFR-UI-002 [P1] Progress 节流

大量 Step 高频更新时：

TaskProgressPanel 不导致 UI 明显卡顿。

默认目标约：

```text
4 Hz
```

---

# 51. AC-DPI：DPI / 显示

验证：

```text
100
125
150
175
200 %
```

至少测试：

```text
书架
工作台
Reader
Settings
Floating Window
```

无关键内容裁切。

---

# 52. AC-PKG：打包

## AC-PKG-001 [P0] PyInstaller onedir

目标发布包可通过：

```text
PyInstaller onedir
```

或经正式决策批准的等价方案生成。

---

## AC-PKG-002 [P0] 干净 Windows 启动

无开发环境依赖的测试机：

```text
启动成功
```

不得依赖开发机 PATH / venv / 源码目录。

---

## AC-PKG-003 [P0] Qt DLL

干净机不得出现：

```text
PySide6.QtCore DLL missing
Qt plugin missing
```

---

# 53. AC-SMOKE：发布包主流程

干净 Windows 机器完成：

```text
启动
→ 默认书架
→ 创建 Book
→ 创建 Chapter
→ 导入 Page
→ 进入工作台
→ 执行至少一个 Mock / Local Pipeline
→ 保存
→ 阅读
→ 导出
→ 关闭
→ 再启动
→ 数据仍存在
```

全部 PASS 才可发布。

---

# 54. AC-OPTIONAL：可选依赖

## AC-OPTIONAL-001 [P0] 缺重型模型仍可启动

未安装：

```text
PyTorch
大型 Inpaint Model
某 OCR Runtime
```

只要 Core 依赖完整：

```text
应用仍可启动
```

---

## AC-OPTIONAL-002 [P1] Provider 状态

缺依赖 Provider：

```text
显示 Not Ready / Missing Dependency
```

不能让主程序崩溃。

---

# 55. AC-MODEL：模型下载

## AC-MODEL-001 [P1] 下载进度

模型下载：

```text
显示进度
可取消
失败可重试
```

---

## AC-MODEL-002 [P0] 不完整模型不 Ready

下载中断：

```text
Provider / Model 不得显示 Ready
```

---

# 56. AC-OFFLINE：离线

断开网络。

以下仍应工作：

```text
书架
本地阅读
本地编辑
Rendering
已安装的本地 OCR / Inpaint
```

远程 Provider 显示不可用。

---

# 57. AC-PRIVACY：远程数据

远程 Provider 设置页能说明：

```text
OCR 可能上传图片
Translation 可能上传文本
Remote Inpaint 可能上传图片 / Mask
```

不得声称本地处理却实际发送远程数据。

---

# 58. AC-CONFLICT：并发人工修改

## AC-CONFLICT-001 [P0] Optimistic Write Guard

**Given**

后台 Translation 启动时 Region Revision = 10。

**When**

用户编辑并保存后 Region Revision = 12。

随后后台结果返回。

**Then**

后台结果不得覆盖 Revision 12。

应：

```text
保存为候选 / 冲突结果
或
Step needs review
```

---

## AC-CONFLICT-002 [P0] 同能力写冲突

两个 Run 同时尝试写同一个 Region Translation：

系统必须：

```text
排队
序列化
或阻止冲突
```

不得产生不可预测覆盖。

---

# 59. AC-SET：设置继承

验证：

```text
全局
→ Book
→ Chapter
→ 当前任务临时
```

最终值解析正确。

UI 能显示来源。

---

# 60. AC-PROV：Provenance

对于 OCR / Translation / Inpaint / Render 输出：

能够追踪：

```text
Provider / Renderer
Model
Options
Input Revision
Output Revision
Run
Step
Timestamp
```

---

# 61. AC-CLEAN：数据清理

## AC-CLEAN-001 [P0] Current 不清理

执行旧 Revision 清理。

Current Revision 必须保留。

---

## AC-CLEAN-002 [P0] 用户源文件不清理

任何 Cache / Revision / Recycle / Project Cleanup：

不得删除源文件。

---

## AC-CLEAN-003 [P1] Debug Artifact

Debug OCR / Detection Artifact 可清理。

清理后不影响正式 Pipeline current 状态。

---

# 62. AC-ERROR：错误分类

至少能区分：

```text
ProviderAuthenticationError
ProviderRateLimitError
ProviderUnavailableError

ProxyConnectionError
ProxyAuthenticationError
DNSResolutionError
TLSHandshakeError
ConnectTimeout
ReadTimeout

ModelLoadError
OutOfMemoryError
DeviceUnavailableError

FileReadError
FileWriteError
ArtifactCommitError
DatabaseTransactionError

LockBlocked
ManualProtectionConflict
```

---

# 63. AC-ERRUI：错误 UI

影响任务的错误至少在：

```text
Page Badge
TaskProgressPanel
TaskDetailWindow
```

可定位。

Toast 不能是唯一错误载体。

---

# 64. AC-AUTO：Autosave / Dirty

如果实现 Autosave：

```text
不得每输入一个字符产生 Revision
```

切换 Page / Region 前：

```text
pending autosave 必须 flush
```

或明确要求用户保存。

---

# 65. AC-CLOSE：关闭应用

## AC-CLOSE-001 [P0] 运行任务关闭

有 Running Pipeline 时关闭应用：

必须提示并安全处理。

不得直接把任务丢失。

---

## AC-CLOSE-002 [P0] Dirty + Running 分离

同时存在：

```text
未保存编辑
运行任务
```

关闭时必须分别处理。

不能一个“确定退出”同时隐式丢编辑和杀任务。

---

# 66. AC-DOC：设计一致性 Gate

正式开发前必须通过文档一致性检查。

## AC-DOC-001 [P1] 01~08 文件齐全

```text
01
02
03
04
05
06
07
08
```

均存在。

---

## AC-DOC-002 [P1] 核心术语统一

以下名称不能在不同文档中表达不同含义：

```text
Book
Chapter
Page
Region
PipelineRun
PipelineTask
StepRun
ArtifactRevision
RegionRevision
Page Lock
Region Lock
Translation Lock
Inpaint Lock
```

---

## AC-DOC-003 [P1] 四个一级页面统一

01~08 都必须保持：

```text
书架
工作台
阅读器
设置
```

并默认启动书架。

---

# 67. AC-SYNC：06/07 对 03 的同步核验与 Schema 冻结 Gate

在进入正式 Schema 实现前，应以 [TASK-002 最小契约](contracts/TASK-002_MINIMUM_DATA_EXECUTION_CONTRACT.md) 核验：

```text
StageState stale
Region command type
current revision / 多目标 input-output refs / 原子 optimistic guard
source_run_id / retry provenance
Run/Task/Step/Decision/Stage/Review 分层状态
Pin / TM disabled / SFX / invalidation / 每 Step commit
```

TASK-002 冻结的是实现必须遵守的最小字段、枚举、关系与事务语义，不是已运行的 SQL Schema。正式实现只有同时满足该契约 §2～§10 的 FK/唯一性/NULL/枚举、compare-and-write、多 Region 映射与状态聚合，并通过 §11 验证向量，才可通过本 Gate：

```text
允许后续 Schema 设计与实现
不允许把目标文档或字段清单冒充已验证数据库
```

---

# 68. 自动化测试最低覆盖

第一版至少应有自动化测试覆盖：

```text
Domain rules
Repository CRUD
Soft Delete
Lock
Revision
TranslationConstraint priority
TranslationMemory write rule
Pipeline command plan
Step skip / stale
Pause / Continue / Stop
Crash Recovery state
Retry
Artifact atomic commit
Provider resolution
Proxy policy
Context write scope
Webtoon coordinate mapping
Task progress aggregation
```

---

# 69. UI 自动化 / ViewModel 测试最低覆盖

至少：

```text
默认导航书架
4 一级页面
Book → Chapter → Workbench
Book → Chapter → Reader
PageList 多选
Region Inspector 绑定
TaskProgress 状态
暂停 / 停止 / 继续按钮 enable state
失败页筛选
Dirty Close
Settings inheritance display
```

---

# 70. 手工视觉验收

必须手工检查：

```text
100~200% DPI
双屏
长文本
中文 / 日文 / 韩文
超长文件名
空状态
Loading
Error
Disabled
Hovered
Selected
Focused
```

---

# 71. Benchmark Release Gate

每个 Release Candidate 至少生成：

```text
benchmark-report.md
```

记录：

```text
Cold Start
Page Switch
Book Search
Large PageList
Webtoon Memory
TaskProgress Update
DB Query
Peak RAM
Peak VRAM（如有）
```

没有数据时不得写：

```text
性能已优化
性能达标
```

---

# 72. 数据安全 Release Gate

以下测试必须全部 PASS：

```text
用户源文件 Hash 不变
人工译文不被后台覆盖
Current Revision 不被失败任务破坏
Pinned Revision 不被清理
Stop 不回滚
Crash 不误判成功
Migration 可恢复
Secret 不入库 / 不入日志
```

任一失败：

```text
BLOCK RELEASE
```

---

# 73. 最终 Release Checklist

发布前：

```text
[ ] Git working tree / release commit 明确
[ ] 01~08 文档版本一致
[ ] Schema migration verified
[ ] P0 100% PASS
[ ] P1 100% PASS
[ ] Unit tests PASS
[ ] Integration tests PASS
[ ] UI/ViewModel tests PASS
[ ] File safety tests PASS
[ ] Crash recovery tests PASS
[ ] Benchmark completed
[ ] Packaging completed
[ ] Clean Windows smoke PASS
[ ] Secret scan PASS
[ ] Source-file safety PASS
[ ] Backup / Restore PASS
[ ] Release Notes 完成
```

---

# 74. 建议验收结果目录

```text
verification/
├─ 01-functional/
├─ 02-data/
├─ 03-pipeline/
├─ 04-ui/
├─ 05-webtoon/
├─ 06-provider-network/
├─ 07-safety/
├─ 08-performance/
├─ 09-recovery/
├─ 10-packaging/
├─ screenshots/
├─ logs/
├─ benchmark-report.md
└─ verification-summary.md
```

---

# 75. verification-summary.md 推荐格式

```text
Release Candidate:
Commit:
Date:
Environment:

P0:
PASS / TOTAL

P1:
PASS / TOTAL

P2:
PASS / TOTAL

Automated Tests:
xxxx passed

Known Issues:
...

Performance:
...

Packaging:
PASS / FAIL

Clean Windows Smoke:
PASS / FAIL

Final Decision:
READY / NOT READY
```

---

# 76. READY 判定

只有同时满足：

```text
P0 全部 PASS
P1 全部 PASS
无数据安全 Blocker
无人工修改覆盖 Blocker
无源文件破坏 Blocker
无数据库损坏 Blocker
干净 Windows Smoke PASS
```

才允许：

```text
READY
```

否则：

```text
NOT READY
```

---

# 77. 本阶段完成后的项目文档主线

```text
01_FUNCTIONAL_ARCHITECTURE
02_TECHNICAL_ARCHITECTURE
03_DATA_MODEL
04_USER_FLOW
05_UI_MAPPING
06_TRANSLATION_PIPELINE
07_NON_FUNCTIONAL_REQUIREMENTS
08_ACCEPTANCE_CRITERIA
```

这 8 份文档共同构成开发前目标基线：

```text
01：做什么
02：怎么分层
03：数据怎么存
04：用户怎么走
05：界面怎么落
06：后台怎么跑
07：质量要达到什么程度
08：如何证明它真的完成
```

---

# 78. AC-EXT：扩展能力验收

本节将 13 条原始 AC-EXT 草案中的 8 条纳入正式编号 AC，范围沿用已批准的用户决定；它们当前均为 NOT_RUN。其余 5 条继续保留为草案：AGENT-001/002 受 U-4 的未来阶段裁决条件约束；FONT-003 的删除/回退行为和 SAKURA-002/003 的轮询及失败策略细节尚未确定。它们不进入本节 Release Gate，也不得被视为已批准或已验收。

## AC-EXT-IMPORT-003 [P2] 未加密 PDF 按页导入

前提：使用页数和顺序已知的未加密 PDF 测试文件。

步骤：通过 PDF 导入流程导入文件，并检查生成的 Page 顺序、Managed Copy 与 Hash 记录。

预期：每页按 PDF 原始页序生成；Page 文件遵循图片导入相同的 Managed Copy 与 Hash 语义；源 PDF 未被修改。此项只验收 PDF，不代表 MOBI 解析契约已确定。

## AC-EXT-IMPORT-004 [P2] 加密或损坏 PDF 零半成品拒绝

前提：准备加密 PDF 与损坏 PDF。

步骤：分别尝试导入并检查界面错误、数据库和 Managed Storage。

预期：导入被拒绝并说明文件或页级原因；不留下部分 Page、Chapter 或 Managed Artifact；源文件 Hash 保持不变。

## AC-EXT-PLUGIN-001 [P2] 本地插件 Hook 按 Schema 执行

前提：TASK-025 已冻结本地插件 manifest 与版本化 Hook 输入/输出 Schema；测试插件位于用户批准的本地目录并声明 Hook 与所需权限。

步骤：加载合法插件并触发其声明的 Hook。

预期：合法插件在声明的扩展点执行，Hook 输入和输出通过已冻结 Schema 校验；未声明的扩展点不执行。

## AC-EXT-PLUGIN-002 [P2] 插件崩溃或超时被隔离

前提：准备可重复的主链路样本，以及分别崩溃和超时的测试插件。

步骤：对同一样本分别运行不启用插件、启用正常插件、启用故障插件三种情况。

预期：插件崩溃或超时被隔离并留下 Plugin Error 记录；主任务继续按契约完成；与无插件基线相比，插件未获准影响的主链路结果及用户数据保持一致。

## AC-EXT-PLUGIN-003 [P2] 缺少权限声明的插件拒绝加载

前提：准备缺少权限声明或权限声明不完整的本地插件。

步骤：尝试加载并观察 Hook 执行、文件/网络访问和审计记录。

预期：插件在执行 Hook 前被拒绝加载，原因进入审计记录，未声明权限不会被授予。

## AC-EXT-FONT-001 [P2] 获准上传字体可选并用于渲染

前提：字体文件格式受支持、单文件不超过 50 MB，且用户上传字体总数未超过 200。

步骤：发起上传，确认界面显示 U-5 批准的许可提示；上传后在样式选择器选中该字体并渲染测试文本。

预期：提示原文为“上传即声明本人已具备该字体的本地使用许可；用户自行确保许可，应用不分发字体。”；字体进入用户字体列表，可用于渲染且记录 SHA-256；源字体文件未被修改。

## AC-EXT-FONT-002 [P2] 损坏或超限字体拒绝且无半成品

前提：准备损坏字体、超过 50 MB 的字体及已有 200 个用户上传字体的状态。

步骤：分别上传损坏字体、超大字体，并在总数已达 200 时再上传一个有效字体。

预期：三种越界输入均被拒绝并说明原因；字体列表、Managed Storage 与 Hash 记录不留下半成品；200 个和单文件 50 MB 的上限不被突破。

## AC-EXT-SAKURA-001 [P2] Sakura 连接测试报告健康与就绪状态

前提：TASK-019 明确采用的 Sakura 健康/就绪探测端点；准备可就绪及不可用的服务响应。

步骤：对配置好的 Sakura Profile 执行连接测试，分别覆盖就绪响应和连接失败/未就绪响应。

预期：连接测试显示健康/就绪结果及可诊断原因；探测仅读取健康与就绪所需信息，不采集或展示显存、负载等深度指标。

---

# 79. 下一阶段建议

08 完成后，不建议直接让 Codex“全部开始写代码”。

更稳妥的顺序是：

```text
01~08 一致性审计
→ 同步 06/07 对 03 的增量
→ 冻结 Target Baseline
→ 建立实施 Roadmap
→ 拆 Phase / Slice
→ 每个 Slice 绑定对应 AC Test ID
→ 开始实现
```

开发时每个任务都应该回答：

```text
它实现了哪些 AC？
对应自动化测试是什么？
证据在哪里？
```

这样可以避免代码越写越多，但无法判断项目到底是否真正完成。
