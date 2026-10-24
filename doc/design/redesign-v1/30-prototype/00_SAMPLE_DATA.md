# 原型共享假数据集（三套方向必须使用同一份）

> 目的：三套方向必须**用同一份数据**演示，用户才能公平比较设计差异而不是内容差异。
> 数据完全虚构，不含任何真实作品内容或版权素材。

---

## 1. 作品库

| 作品 | 类型 | 语言 | 章节 | 页数 | 进度 |
|---|---|---|---|---|---|
| 夜光列车 | 日漫 / Paged / RTL | 日→中 | 全 14 话（已完成 11 话） | 第12话 23 页 | 处理中 |
| 雨の停車場 | 日漫 / Paged / RTL | 日→中 | 单话（第 3 话） | 18 页 | 待处理 |
| 汉江之夜 | 韩漫 / Webtoon / Vertical | 韩→中 | 全 60 话（已完成 12 话） | 第13话 1 张长图 | 待处理 |
| 旧校舍的夏天 | 日漫 / Paged / LTR | 日→中 | 全 8 话 | 第 2 话 20 页 | 已完成 |

主演示作品：**夜光列车 · 第12话「雨の停車場」· 23 页**

## 2. 章节状态分布（第12话）

| 页 | 状态 | 说明 |
|---|---|---|
| 001–016 | 已完成 · 已确认 | 全部 16 页 `review_state = confirmed` |
| 017 | 已完成 · 待确认 | 3 条 `needs_review` |
| 018 | 部分完成 · 失败 | `translate` 失败：`ProviderRateLimitError`（2 次重试后放弃） |
| 019 | 部分完成 · 失败 | `inpaint` 失败：`ModelLoadError`（`anime_lama_v2` 权重缺失） |
| 020 | 过期 `stale` | 用户在第 019 页改了 Region 几何 → 该页 `render` 过期 |
| 021 | 处理中 | `translate` 进行中，62% |
| 022–023 | 未处理 | `not_started` |

本章汇总：23 页 · 完成 18 · 失败 2 · 过期 1 · 待确认 3 · 处理中 1 · 未处理 2

## 3. 当前页面 007.jpg 的 Region（核心演示数据）

| # | 类型 | 几何（相对页面 1200×1800） | 原文 ocr_text | 机器译文 machine_translation | 人工译文 edited_translation | review_state | Lock |
|---|---|---|---|---|---|---|---|
| 1 | speech 对白 | (148, 210, 322, 268) | おはよう、また会えたね | 早上好，又见面了呢 | — | confirmed | — |
| 2 | speech 对白 | (612, 186, 300, 244) | この雨、三日は止まないらしい | 这场雨，好像三天都不会停 | 这场雨，恐怕要下三天 | confirmed | translation |
| 3 | narration 旁白 | (140, 560, 640, 96) | 三日後の朝 | 三天后的早晨 | — | needs_review | — |
| 4 | sfx 拟声词 | (700, 640, 260, 180) | ザァァァ | —（SFX 策略 skip） | — | unreviewed | region |
| 5 | speech 对白 | (430, 980, 296, 232) | 切符をなくした | 我把车票弄丢了 | — | confirmed | — |
| 6 | note 注释 | (120, 1560, 420, 120) | ※時刻表は変更されています | ※时刻表已更改 | — | needs_review | — |

四轨状态（第 007 页）：detect ✓ / ocr ✓ / color ✓ / term ✓ / translate ✓ / segment ✓ / mask_refine ✓ / inpaint ✓ / render ✓ / review 进行中

## 4. 韩漫 Webtoon 演示（汉江之夜 · 第13话）

- 1 张 1200×14800 长条图 = 1 个逻辑 Page
- 切片缓存 12 片（tile），不是逻辑页
- Region 共 47 个，其中 9 个为竖排韩文旁白
- 修复路线：`BrushNet`（彩色渐变背景）
- 独占演示：长内容导航、单页内 Region 过多时的聚合、切片对用户不可见

## 5. 任务/队列演示

```
Run #R-8831   translate_untranslated   第12话   23 页
  status: running   progress: 62%
  current: 021.jpg · translate · step 5/9
  counts: total 23 / completed 18 / failed 2 / skipped 1 / waiting 2
  can_pause: true  can_continue: false  can_stop: true
  elapsed: 12:07   ETA: 4m12s

Run #R-8830   reinpaint_selected   第11话 · 选中 5 页   completed   （3 分钟前）
Run #R-8829   rerender_all        第10话               completed_with_failures（1 页失败：OutputMappingError）
Run #R-8828   translate_all       第9话                blocked（Provider 认证失效）
Run #R-8827   translate_all       第8话                interrupted（异常退出）
```

## 6. 错误样例（必须使用真实错误码语义）

| 错误码 | 中文摘要 | 处置建议 |
|---|---|---|
| `ProviderRateLimitError` | Provider 限流，重试 2 次后失败 | 降低并发 / 换 Provider / 稍后重试 |
| `ModelLoadError` | 修复模型权重缺失：`anime_lama_v2` | 安装模型 / 换修复路线 |
| `MissingOCRText` | 该 Region 无有效 OCR 文本 | 先重 OCR 再翻译 |
| `LockBlocked` | 目标被 Region Lock 阻止 | 解锁或改用显式覆盖 |
| `INPUT_REVISION_CHANGED` | 输入版本已变更（乐观锁冲突） | 刷新后重试 |
| `ProxyConnectionError` | 代理连接失败（`socks5://127.0.0.1:1080`） | 检查代理 / 切直连 |

## 7. 约束表（术语/不译）

| 原文 | 译文 | 类型 | 作用域 | 来源 |
|---|---|---|---|---|
| 夜光列車 | 夜光列车 | 术语（专有名词） | 作品 | 人工 |
| 車掌 | 列车长 | 术语（职业） | 作品 | 人工 |
| 停留所 | 站点 | 术语（场所） | 作品 | 自动识别 |
| ザァァァ | （不译） | 不译（拟声词） | 章节 | 人工 |

**冲突演示**：第 008 页某 Region 的机器译文把「車掌」译成「乘务员」，与术语表冲突 → 需在审阅界面提示。

## 8. 版本历史演示（第 007 页 · Region 2）

| 版本 | 时间 | 来源 | 变化 | 状态 |
|---|---|---|---|---|
| r5 | 14:22 | 人工 | 译文改为「这场雨，恐怕要下三天」 | current · confirmed |
| r4 | 14:05 | pipeline | translate 覆盖（machine） | needs_review |
| r3 | 13:58 | 人工 | 字号 +1，溢出策略 → shrink | — |
| r2 | 13:40 | pipeline | inpaint 完成（BrushNet） | — |
| r1 | 13:31 | pipeline | OCR 初识别 | — |

## 9. 设置项演示（Console / 工具抽屉用）

- Provider：`deepseek-v3`（翻译，默认）、`manga_ocr`（识别）、`anime_lama_v2`（修复）
- 网络：`HTTP 代理 socks5://127.0.0.1:1080`（默认直连，Provider 级覆盖）
- 并发：翻译 4、修复 1、网络 8
- 缓存与历史：`ArtifactRevision` 保留 30 天 / 上限 8 GiB / 当前 2.1 GiB
- 备份：`.nmbak` 最近 3 份，最近一次 2026-10-24 22:10
- 插件：2 个启用（`glossary-sync`、`batch-rename`），1 个停用

## 10. 使用要求

- 三套原型中出现的数字、页数、状态、错误码、术语必须与本文件一致。
- 允许为了布局需要增加次要条目，但不得改变主演示数据。
- 页面图像必须用 CSS/SVG 自绘的抽象漫画页（分格线 + 文本块 + 网点纹理），**不得**使用任何真实漫画截图。
