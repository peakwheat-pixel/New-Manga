---
id: TASK-014
title: 实现配色与文字排版渲染
kind: implementation
status: done
approval: approved
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [TASK-008]
base_commit: 29592c929745410ef0045266da94f21ed97ffdcb
branch: agent/zcode/TASK-014-rendering-style
worktree: G:/CODEX/New Manga.worktrees/TASK-014-rendering-style
reviewed_head: 72cb2bee0cea56749961392dc899e379383b6fb8
implementation_merge: a61216afce9d78819e62cc2907a371fa01e46dfb
integration_commit: a9432971ebf6450d7cc3afa23a245af917ffad2e
---

# TASK-014：实现配色与文字排版渲染

本 Task 已获用户批准并由 ZCode 交付；2026-09-15 已完成串行集成并置 `done`。Reviewer=DeepSeek Harness，固定 `base_commit=29592c9`、`reviewed_head=72cb2be`。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D03 §11；D06 §8/23/41/47/86；D08 AC-STYLE/RENDER。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-STYLE-001、AC-STYLE-002、AC-STYLE-003、AC-STYLE-004、AC-STYLE-005、AC-RENDER-001、AC-RENDER-002。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [x] 实现SourceStyle提取/字号fallback、最终文本、字体/描边/方向/行距和-5..+5偏移；shrink-to-fit符合已确认规则。
- [x] rerender仅使用有效Clean+final+TextStyle，缺Clean可诊断阻止，不触发OCR/Translation/Inpaint。
- [x] 页级与Region级合成遵守TASK-002协议，输出新ArtifactRevision，失败保留旧current。
- [x] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。（Review approved；集成验证 153 passed）

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- src/application/translation/color/**
- src/application/rendering/**
- src/ports/rendering/**
- src/infrastructure/rendering/**
- tests/rendering/**
- doc/tasks/TASK-014.md
- doc/handoffs/TASK-014-*.md
- verification/TASK-014/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- executed：`python -m pytest tests/rendering -v` → 56 passed（style 解析 18 / 方向+Qt 排版 14 / SourceStyle 9 / 合成器 6 / rerender 11）；横/竖排、多语言（CJK+Latin）、长文本折行、offset 边界与越界、缺字体诊断均覆盖。
- executed：AI spy 验证 rerender 全路径零 OCR/Translation/Inpaint 调用 + 服务依赖闭包无 provider 引用；单 Region 合成邻区像素逐像素保持；渲染产物经 managed storage 落盘并在测试中读回断言（保存重开可读）。
- executed：`python -m pytest tests`（全仓库回归，含架构守卫）→ 153 passed，退出码 0。
- executed（Codex 集成复验）：`G:/CODEX/New Manga.task-envs/TASK-014-py312/Scripts/python.exe -m pytest tests -q` → 153 passed，退出码 0；默认 Windows Qt 平台，未设置 `QT_QPA_PLATFORM`。
- executed（固定对象检查）：`git diff --check 29592c9 72cb2be --` → 退出码 0。
- 环境：Windows 10.0.26200、Python 3.12.3、PySide6 6.11.2、pytest 9.1.1；作者逐条输出见 [author-verification](../../verification/TASK-014/author-verification.md)，主线复验见 [integration verification](../../verification/TASK-014/integration-a943297.md)。

## 依赖、风险与阻塞

硬依赖：[TASK-008](TASK-008.md)。依赖必须已经集成 done 才可开始。

字体上传UI由TASK-022，字体来源/许可随素材规范记录；不得编造视觉达标结论。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## Review findings disposition

- **F-01 fixed**：纯 `TextDirection` 下沉至 `src/ports/rendering/direction.py`；application 保留导入兼容，ports 与 infrastructure 不再反向依赖 application。
- **F-02 fixed**：单 Region 的 Region current 复查及 Page artifact compare-and-write 冲突统一返回 `COMPOSITION_BASE_CHANGED`；页级 rerender 的一般 §8.1 输入冲突仍保留 `INPUT_REVISION_CHANGED`。
- **F-03 deferred**：Region current 复查与 Artifact 提交尚未进入同一事务；需要扩展 TASK-029 seam 或未来获批编排 Task，本次不启动其他 Task。
- **F-04 fixed**：已将测试平台更正为默认 Windows Qt，并明确 `offscreen` 无字体库不可用。
- **F-05 deferred**：ports/application 的 Qt/sqlite 自动架构守卫需另行由 Codex 协调；扩展会触及 `tests/core`，本次不越过 TASK-014 白名单。

## 交付与运行记录

- Handoff：[TASK-014-72cb2be](../handoffs/TASK-014-72cb2be.md)，实现 head `72cb2be`（7 个实现/修复提交自 base 起），验证证据 [author-verification](../../verification/TASK-014/author-verification.md)。
- Review：[TASK-014-72cb2be](../reviews/TASK-014-72cb2be.md)，`report_commit=5276a18`，decision=`approved`。
- 实际执行/实验/测试：rendering 56 passed；作者全仓库 153 passed；Codex 集成复验 153 passed；未运行项按 Review 保持 NOT_RUN/N/A。
- 集成：实现 merge=`a61216a`；Review 报告 merge=`a943297`（`integration_commit`）；F-01/F-02/F-04 收口=`524d03f`。
- 最近状态：2026-09-15 DSH Review approved；Codex 串行集成并完成主线复验，状态 `approved` → `done`。
- 最近状态：2026-09-13 接管规划创建；proposed，pending_user_review。
- 最近状态：2026-09-15 用户批准释放（主线 `c77b40b`）；ZCode 接管，`ready` → `in_progress`，开始需求阅读与 TDD 实施。

## 实施与集成记录

边界结论（对照 base=`29592c9` 实际结构核对）：

- `src/domain/regions/entities.py` 的 `TextStyle` 是最小子集且不在本 Task 白名单内；本切片在 `src/application/rendering/style.py` 定义完整渲染样式 `RenderTextStyle`（D03 §11.5 字段），经 `from_domain()` 兼容 TASK-008 已持久化的最小样式。不修改 domain/SQLite schema。
- 渲染产物通过现有 `SqliteArtifactRepository.commit_revision`（TASK-002 §8.1 compare-and-write）提交为新 `translated` ArtifactRevision；失败/conflict 保留旧 current（复用已集成 seam，不重写）。
- page→artifact 定位：现有 `ArtifactRepositoryPort` 无按 page 查询方法；新增只读 `PageArtifactLocator` port（`src/ports/rendering/`）+ SQLite 读适配（`src/infrastructure/rendering/locator.py`），不改共享 port 文件。
- 图像栈：PySide6 QtGui（QImage/QPainter/QTextLayout），已在 requirements 锁定，不新增依赖；测试使用默认 Windows 平台（`offscreen` 无字体库不可用）。

模块与 TDD 顺序：

1. `src/application/rendering/style.py`：字号解析链（D03 §11.1、AC-STYLE-001..005）——detected→fallback 26→offset(-5..+5 校验)→溢出→shrink-to-fit→final；auto 关闭用手动字号。
2. `src/ports/rendering/ports.py`：TextLayoutEngine / ImageCompositor / SourceStyleAnalyzer / FontCatalog / PageArtifactLocator 协议 + DTO。
3. `src/infrastructure/rendering/qt_layout.py`：横/竖排折行与度量；`font_catalog.py`：字体可用性与 fallback 诊断。
4. `src/application/translation/color/`：SourceStyle 提取用例（D06 §8：detected_source_font_size、confidence、颜色、方向提示、fallback 决策）；`src/infrastructure/rendering/pixel_source_style.py`：灰度行投影像素分析。
5. `src/infrastructure/rendering/qt_compositor.py`：页级多 Region 合成与单 Region 局部合成（描边/竖排绘制），输出 PNG。
6. `src/application/rendering/service.py`：`RenderService.rerender_page` / `rerender_region`——缺 Clean → BLOCKED（D06 §41）；SFX skip/manual 批量跳过（§85）；单 Region 合成 base 变化 → 冲突不更新（§8.2）；依赖闭包无任何 AI provider（AC-RENDER-001）。
7. `tests/rendering/`：style 解析、方向/折行、SourceStyle、合成像素断言、rerender 行为、SFX、冲突保留旧 current、AI spy。
