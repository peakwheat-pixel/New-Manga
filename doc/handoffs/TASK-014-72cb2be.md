---
task_id: TASK-014
author: ZCode
recipient: DeepSeek Harness (Review) → Codex (integration)
base_commit: 29592c929745410ef0045266da94f21ed97ffdcb
delivery_head: 72cb2be
status: delivered
---

# Handoff：TASK-014 实现配色与文字排版渲染

## 交付结果

在 base=`29592c9` 上以 TDD 完成渲染切片，实现 head 为 `72cb2be`（本 Handoff 为其后的文档提交，不改变实现内容）。

提交列表（自 base 起）：

| commit | 内容 |
|---|---|
| `eaa5cd7` | start(TASK-014)：ZCode 认领，Task 元数据对齐主线 release 并置 in_progress |
| `078b5b4` | 渲染样式模型 `RenderTextStyle` 与字号解析链（D03 §11.1/§11.2，AC-STYLE-001..005） |
| `5386aa1` | 渲染 ports（layout/compositor/source-style/font/locator）、auto 方向解析、Qt 排版引擎与 Windows 字体目录 |
| `786650a` | SourceStyle 提取（D06 §8）：像素投影分析器 + fallback 判定服务 |
| `b671acd` | Qt 图像合成器：页级多 Region 渲染与单 Region 局部合成（TASK-002 §8.2） |
| `c2e6aa5` | RenderService：`rerender_page`/`rerender_region` 用例 + sqlite PageArtifactLocator |
| `72cb2be` | 修复跨套件 helpers 模块名冲突（改名 rendering_helpers） |

新增路径（全部在 Task 白名单内；未触碰白名单外任何文件）：

- `src/application/rendering/`：`style.py`（D03 §11.5 完整渲染样式 + 字号解析）、`layout.py`（方向解析）、`service.py`（rerender 用例）
- `src/application/translation/color/`：`service.py`（D06 §8 Color/Source Style Step 用例）
- `src/ports/rendering/`：`ports.py`（TextLayoutEngine / ImageCompositor / SourceStyleAnalyzer / FontCatalog / PageArtifactLocator 协议与 DTO）
- `src/infrastructure/rendering/`：`qt_layout.py`、`qt_compositor.py`、`pixel_source_style.py`、`font_catalog.py`、`locator.py`
- `tests/rendering/`：`rendering_helpers.py`、`conftest.py`、5 个测试模块
- `verification/TASK-014/author-verification.md`

### AC 对照

| AC | 实现 | 状态 |
|---|---|---|
| SourceStyle 提取/字号 fallback、最终文本、字体/描边/方向/行距和 -5..+5 偏移；shrink-to-fit 符合规则 | `PixelSourceStyleAnalyzer`（ink 行投影估字号+置信度+主色+方向提示）；`RenderTextStyle` 构造期校验 offset∈[-5,5]；`resolve_font_size`：可靠 detected → base，否则 fallback 26（D06 §8）→ +offset → 溢出 shrink-to-fit（0.5 步进向下搜索，最小 1.0，仍放不下则 `StyleResolutionError` 可诊断）；auto 关闭用手动字号且显式突破限制；不自动放大（final ≤ candidate）；横/竖排、行距、描边、字体由 Qt 引擎与合成器实现 | 满足（测试见下） |
| rerender 仅使用有效 Clean+final+TextStyle，缺 Clean 可诊断阻止，不触发 OCR/Translation/Inpaint | `rerender_page`/`rerender_region` 无 Clean → `BLOCKED / MISSING_REQUIRED_INPUT / missing_clean_artifact`；服务构造函数不含任何 AI 端口（结构性保证 AC-RENDER-001），spy 测试证明全路径零 AI 调用 | 满足 |
| 页级与 Region 级合成遵守 TASK-002 协议，输出新 ArtifactRevision，失败保留旧 current | 页级：Clean 为底全 Region 合成 → `translated` ArtifactRevision 经 `SqliteArtifactRepository.commit_revision` compare-and-write；Region 级：启动时快照 page translated current 与 region current（§8.2），合成 = base 上用 Clean 恢复目标 bbox 后重绘，提交前复查 region current，任一变化 → `INPUT_REVISION_CHANGED`（COMPOSITION_BASE_CHANGED 族），current 不动；合成器故障 → `WRITE_FAILED` 旧 current 保持 | 满足 |
| 交付 Handoff、实际测试记录，经独立 Review 与集成后 done | 本文件 + `verification/TASK-014/author-verification.md`；等待 DSH Review | 部分（流程项） |

### 明确不做 / 留给后续 Task 的部分

- **样式编辑 UI 与 RegionTextStyle 持久化扩展**：domain `TextStyle`（TASK-008 最小集）不改；完整样式经 `RenderTextStyle.from_domain()` 合并 + 渲染期参数传递，字号解析结果记入 ArtifactRevision `provenance_json`。样式编辑入 TASK-022。
- **SourceStyle 颜色自动应用**：提取了 text/background 颜色但渲染默认仍用 D03 §11.6 默认样式（黑字白描边），不擅自替用户改配色——应用策略属 UI/用户决策。
- **渲染区域 lock 完整语义**：`region_locked` 时单 Region 渲染被拒绝（保守解释 §47）；translation/inpaint lock 不阻止渲染（§47 明文允许）。
- **StepRun/PipelineRun 集成**：TASK-011 编排未实现，本切片提供用例层 `RenderService`，`source_run_id` 等溯源字段留待编排接入。

## 验证证据

完整命令输出（逐条 verbose）见 [author-verification.md](../../verification/TASK-014/author-verification.md)。

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 证据 |
|---|---|---|---|---|
| 字号解析链（AC-STYLE-001..005，18 项） | `python -m pytest tests/rendering/test_style_resolution.py -v` | Win10.0.26200 / Py3.12.3 / PySide6 6.11.2 / `72cb2be` | PASS 18/18 | author-verification.md |
| 方向解析 + Qt 排版（横/竖排、拉丁整词、行距、缺字体，14 项） | `python -m pytest tests/rendering/test_layout.py -v` | 同上 | PASS 14/14 | 同上 |
| SourceStyle 提取（合成已知字号图像、置信度、fallback、越界 clamp，9 项） | `python -m pytest tests/rendering/test_source_style.py -v` | 同上 | PASS 9/9 | 同上 |
| 图像合成（ink 落位、邻区像素保持、描边颜色、竖排直立，6 项） | `python -m pytest tests/rendering/test_compositor.py -v` | 同上 | PASS 6/6 | 同上 |
| rerender 用例（提交新 Revision、缺 Clean BLOCKED、SFX gate、空 final skip、竞态冲突保留旧 current、合成失败保留旧 current、AI spy、单 Region 邻区保持、Region 变化冲突、manual SFX 门，11 项） | `python -m pytest tests/rendering/test_rerender.py -v` | 同上（真 SQLite+managed storage） | PASS 11/11 | 同上 |
| 渲染套件合计 | `python -m pytest tests/rendering -v` | 同上 | PASS 56/56，退出码 0 | 同上 |
| 全仓库回归（core/editing/library/storage/rendering，含架构守卫） | `python -m pytest tests` | 同上 | PASS 153/153，退出码 0 | 同上 |

未运行项与原因：

- 无 NOT_RUN 项。视觉质量（字体美感、shrink 后可读性）未做人工评审——本切片证据为像素级断言与几何断言，不虚构视觉达标结论（Task 禁止项）。真实 OCR/翻译质量不适用（rerender 不涉及）。

## 接收方式

- Worktree：`G:/CODEX/New Manga.worktrees/TASK-014-rendering-style`，分支 `agent/zcode/TASK-014-rendering-style`，实现 head `72cb2be`（Handoff 提交在其后追加，文档不改变实现）。
- 复现：`G:/CODEX/New Manga.task-envs/TASK-014-py312/Scripts/python.exe -m pytest tests -q`（依赖按 requirements-dev.txt 精确锁定安装；Qt 用默认 Windows 平台——offscreen 平台无字体库，不可用于本套件）。
- Reviewer 请按协议 §6 固定 `base_commit=29592c9`、`reviewed_head=72cb2be` 建独立 worktree；架构轴重点：ports/application 无 PySide6/sqlite import（守卫仅覆盖 domain/ui，本切片靠约定 + 测试导入路径维持）。
- 依赖变化：无（PySide6_Essentials 6.11.2 既有锁定；未新增任何第三方依赖）。

## 风险与遗留

1. **像素 SourceStyle 估算是启发式**：行投影中位带高，confidence 为带高一致性；复杂背景（渐变、网点）会低估置信度并触发 fallback 26——这是设计内行为（D06 §8），非缺陷。
2. **`_SHRINK_STEP=0.5` 网格**：最终字号非连续；文档未规定步进粒度，0.5px 为实现选择。
3. **单 Region 合成的 region current 复查在 artifact 事务之外**：region 表与 artifact 事务未跨表合并（需要扩 TASK-029 seam，超出本 Task 白名单）；现有顺序复查 + artifact compare-and-write 已满足"任一变化不更新 current"的可观察语义，窗口内的理论竞态留给 TASK-011 编排层收口。
4. **Qt 字体度量跨平台差异**：布局断言只用比例关系（≤ box、行数、列序），不用绝对像素，Windows CI 重复性可保持；非 Windows 平台不在产品边界。
5. **测试操纵实现私有属性**（`service._compositor` 等）注入竞态 spy：仅为测试注入 seam，非生产行为。
6. 回退方法：整分支 revert 到 `29592c9` 即可；未动共享文件与 schema，无迁移影响。

下一接收者：DeepSeek Harness（独立 Review）→ Codex（集成与主线复验）。
