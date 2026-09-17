# TASK-037：webtoon 滚动保存 flaky 的机制探针（修正 TASK-036 定性）

日期：2026-09-17（ZCode 全权窗口 W1）。环境：`G:/CODEX/New Manga.task-envs/TASK-012-py312`，PySide6 + 真 QML harness，树 = TASK-037 分支（修前几何状态与 master `c3dabc8` 相同，探针不依赖本切片改动）。

探针脚本（入库于 [`probes/`](probes/)，均在临时目录构造页面，不触碰仓库数据）：

- [`probe_webtoon_geometry.py`](probes/probe_webtoon_geometry.py)（探针 1）：打开 webtoon 章节后逐 100 ms 打印 Flickable/Image 几何，最后在**稳定状态**下 `setProperty("contentY", 240)`。
- [`probe_webtoon_early_set.py`](probes/probe_webtoon_early_set.py)（探针 2）：**复现 flaky 时序**——在 `contentHeight == 0`（图片尚未布局）的瞬间写入 `contentY=240`，随后逐 100 ms 追踪。
- [`probe_webtoon_tall_page.py`](probes/probe_webtoon_tall_page.py)（探针 3）：把页面换为 40x1000，验证 `contentY=240` 落在合法 extent 内后**稳定保持**并被保存。

## 实测事实

探针 1（几何时间线，节选）：

```text
sc_w=1280.0  sc_h=738.0   # Flickable 尺寸
sc_ch=60.0                 # contentHeight 稳定值 = 图片原始高度（40x60 PNG）
img_ph=0.0  img_pw=0.0     # paintedWidth/Height 恒 0（读取对象存疑，见"未决"）
ch_minus_h=-678.0          # contentHeight - height 恒为负
--- set contentY=240 ---   # 在时间线 4s 后（contentHeight=60 已稳定）
contentY after set: 240.0
contentY settle: 240.0
saved: 240.0               # 保存成功
```

**事实 A**：本 harness 的 webtoon 内容是单页 40x60 PNG，`contentHeight` 稳定值恒为 **60**（图片原始高度），`contentHeight - height ≥ 240` 在此场景**永远不会成立**——"先等待容纳 240 再写入"（TASK-036 建议的候选 ①、AC ① 示例之一）在本测试场景不可实现。

**事实 B**：`contentHeight=60` 稳定后写入 240 **不被夹回**、保存成功——写入本身不触发 clamp。

探针 2（早期写入 = flaky 时序，节选）：

```text
contentHeight at find: 0.0
contentY immediately after early set: 240.0    # 写入表面成功（读回 240！）
t=   0ms contentY=240.0 contentHeight=0.0 saved=0.0
t= 100ms contentY=-0.0  contentHeight=60.0 saved=0.0   # ← 事件循环批次消化 0→60 时被回写
t= 200ms contentY=-0.0  contentHeight=60.0 saved=0.0   # 恒定 -0.0，saved 保持 0
```

**事实 C（flaky 真实机制，100% 复现）**：在 `contentHeight == 0` 时写入 240，Qt **立即接受**（读回 240.0）；随后承载 `contentHeight 0→60` 的同一事件循环批次里，Flickable 的 StopAtBounds extent 修复把 `contentY` 回写为 **`-0.0`**（与 STATUS flaky 条目的历史签名逐字吻合）；`onContentYChanged` 因此**有**触发（240→-0.0），节流 timer 启动并把 **0** 持久化 → `saved_scroll_offset_y = 0.0` → 等待 `== 240.0` 的 2 s 断言超时失败。

## 对 TASK-036 定性的修正

TASK-036 `registered-flaky-signature.md` 推断为"`setProperty` 被 Flickable 夹回 0 → 值未变 → `onContentYChanged` 不触发 → 节流保存不启动"。探针证明该链条两处不准：

1. 写入当时**不被**夹回（读回 240.0）；回写发生在**之后的 extent 批次**（竞争窗口 = 测试的 `contentHeight > 0` 轮询条件通过到 Flickable 消化该变化之间，窗口极窄 → 低频）。
2. `onContentYChanged` **有**触发、timer **有**启动，只是持久化的值是回写后的 **0** 而非 240。

**测试触发路径**：旧测试在 `contentHeight > 0` 通过的瞬间写入——正好落在窗口边缘；多数情况下该批次已随同一轮 `processEvents` 处理完毕（通过），偶发跨批次时被回写（flaky，历史频率 ≈15% 全仓 / 1/7 mandated）。

## 修复取舍（AC ①）

- 候选 ①"等待 `contentHeight - height ≥ 240` 再写"：被**事实 A** 排除（该条件在本场景恒假，等待只会 100% 超时——修复 v1 即此方案，单用例立即失败于该等待，见下）。
- 候选 ②"设值后断言 `contentY == 240` 再等保存"：**采用**。最终形态 = "夹具提供真正可滚动的内容（40x1000 页）+ 写入后 `landed == 240` 落点断言 + 原 2 s 保存断言不变"。最终断言未放宽、预算未变。

### 修复迭代记录（如实登记，两版中间态被对照否决）

| 版本 | 方案 | 结果 |
|---|---|---|
| v1 | 等待 `contentHeight - height ≥ 240` 再写 | 单用例 100% 失败于新等待（事实 A：该条件恒假）→ 否决 |
| v2 | 保留 `contentHeight > 0` 等待 + 写入后一轮 processEvents 校验落点、被吞则**单次重写** + landed 断言 | 单目录 30/30 通过；**全仓 2/2 命中同一失败**（`landed` 通过后 `contentY` 仍被后续 extent 重算改回 `-0.0`，timer 保存 0）→ 证明 240 写入 **contentHeight=60** 的内容本就是不稳定状态，重写只是补丁且改变时序反而放大命中率 → 否决 |
| v3（最终） | **夹具改高页**（`real_png_pages(page_height=1000)`，仅 webtoon 用例使用）使 `contentHeight=1000`、240 落在 extent 内（探针 3 验证稳定保持并保存）+ 保留 `contentHeight > 0` 等待（`safe_number` 化）+ `landed == 240` 断言 + 原 2 s 保存断言不变 | 见 Task AC ③ 对照记录 |

v3 的夹具依据：被测契约是"webtoon 滚动 → 节流保存/恢复偏移"，要求内容可容纳目标偏移是契约自身的**成立前置条件**；40x60 页面（内容不可滚动）依赖 Qt 对 property 写入的不完全 clamp 才能通过，属于测试场景缺陷而非放宽——恢复断言（R-003 的 `scroll2.contentY == 240`）同样因此真正有效。重写补丁被移除：内容容纳后写入稳定，保留重写反而会掩盖"合法写入被回写"的真实回归。

## 未决（不阻塞本切片）

- `paintedHeight/paintedWidth` 经 `safe_number` 读回 0：探针经 `find_by_name("readerPage")` 取 Image，树上可能存在同名残留（pagedViewer 亦有 `readerPage`），或 PySide6 对该属性存在与 `QQuickImageBase::Status` 同类的转换限制；不影响上述任何结论（`contentHeight`/`contentY` 均从 Flickable 直读）。
