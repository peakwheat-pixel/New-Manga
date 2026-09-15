---
task_id: TASK-014
reviewer: DeepSeek Harness
author: ZCode
base_commit: 29592c929745410ef0045266da94f21ed97ffdcb
reviewed_head: 72cb2bee0cea56749961392dc899e379383b6fb8
decision: approved
---

# Review：TASK-014 配色与文字排版渲染（72cb2be）

本报告只覆盖 `29592c9..72cb2be`。Handoff 提交 `a49fc76` 在其后追加，不含实现改动，不在被审范围。Review 期间未修改生产代码、测试或共享文件；本报告是 Reviewer 新增的唯一文件。

## 范围与依据

**固定对象**：`base_commit = 29592c929745410ef0045266da94f21ed97ffdcb`、`reviewed_head = 72cb2bee0cea56749961392dc899e379383b6fb8`。被审提交链：`eaa5cd7`（认领）→ `078b5b4`（样式模型）→ `5386aa1`（ports/方向/Qt 排版）→ `786650a`（SourceStyle）→ `b671acd`（Qt 合成器）→ `c2e6aa5`（RenderService）→ **`72cb2be`**（跨套件 helpers 改名）。

**变更**：`git diff --stat 29592c9 72cb2be` = 23 路径、`+2775/−8`；`git diff --check` 退出码 **0**。新增 `src/ports/rendering/**`、`src/application/rendering/**`、`src/application/translation/color/**`、`src/infrastructure/rendering/**`、`tests/rendering/**`，并修改 `doc/tasks/TASK-014.md`。

**依据**：D03 §11（渲染样式与字号）；D06 §8（Source Style）、§23（Rendering Step）、§41（rerender 范围）、§47（单 Region 重渲染）、§85（SFX Policy Gate）；D08 `AC-STYLE-001..005`、`AC-RENDER-001/002`；[TASK-002 契约](../contracts/TASK-002_MINIMUM_DATA_EXECUTION_CONTRACT.md) §8.1/§8.2。

**Reviewer 环境**：Windows `10.0.26200`；`G:/CODEX/New Manga.task-envs/TASK-014-py312`（Python 3.12.3、PySide6 6.11.2、pytest 9.1.1）；`QT_QPA_PLATFORM` 未设置，即**默认 Windows 平台**（按 Handoff 要求，offscreen 无字体库不可用）。

## Spec 轴

| 检查项 | 结论 |
|---|---|
| 字号解析链（D03 §11、AC-STYLE-001..005） | **成立**。`RenderTextStyle` 构造期校验 offset ∈ [-5, 5]；`resolve_font_size` 顺序为「可靠 detected size → 否则 fallback 26（D06 §8）→ +offset → 溢出则 shrink-to-fit（0.5 步进向下，最小 1.0，仍放不下抛 `StyleResolutionError`）」；不自动放大（final ≤ candidate）；`auto` 关闭时走手动字号并显式突破限制、缺手动字号可诊断。测试 `test_style_resolution.py` 18 项覆盖边界值 ±6/±100、置信度阈值含端点、最大可容纳字号、不可容纳诊断、`from_domain` 携带 TASK-008 快照字段、D03 §11.6 默认值 |
| AC-RENDER-001（重渲染不触发 OCR） | **成立且为结构性保证**。`RenderService.__init__` 的依赖只有 `region_repo / locator / artifacts / storage / layout_engine / compositor / source_styles / font_catalog`——**不含任何 AI 端口**，因此"不调用 OCR/Translation/Inpaint"不是靠分支约束而是类型层面不可达；另有 spy 测试 `test_render_never_touches_ai_ports` 佐证 |
| AC-RENDER-002（缺 Clean 阻止） | **成立**。`rerender_page` / `rerender_region` 均在 `_locate_clean` 返回 `None` 时返回 `BLOCKED / MISSING_REQUIRED_INPUT / missing_clean_artifact`，不触发 Inpaint。测试 `test_missing_clean_is_blocked_not_auto_inpainted` |
| D06 §23 Rendering Step 输入 | **一致**。实现读取 current Clean ArtifactRevision、`region.text.final_translation`、Region geometry、TextStyle，与 §23 的四项输入对应 |
| D06 §47 单 Region 重渲染 | **一致（含保守解释）**。`rerender_region` 使用当前 `final_translation` + Clean；`region_locked` 时返回 `BLOCKED / LOCK_CHANGED`（Handoff 说明为对 §47 的保守解释），translation/inpaint lock 不阻止渲染——与 §47「允许在…」的放宽方向一致 |
| D06 §85 SFX Policy Gate | **一致**。批量 `rerender_page` 以 `allow_sfx=False` 跳过 skip/manual 区域；单 Region 路径对 `SKIP` 直接 BLOCKED，对 `MANUAL` 要求显式 `allow_manual_sfx=True`。测试 `test_sfx_skip_regions_follow_policy_gate`、`test_manual_sfx_requires_explicit_flag` |
| TASK-002 §8.1（原子提交、失败保留旧 current） | **成立**。`_commit_translated` 复用 `ArtifactRepositoryPort.commit_revision(PendingArtifactCommit(expected_current_revision_id=…))` 的 compare-and-write seam；`COMMITTED` → 新 `translated` ArtifactRevision；`CONFLICT`/`WRITE_FAILED`/`HASH_MISMATCH`/`TARGET_NOT_FOUND`/`DB_FAILED` 映射为不更新 current 的结果。测试 `test_stale_expectation_conflicts_and_keeps_current`、`test_compositor_failure_keeps_old_current` |
| TASK-002 §8.2（单 Region 合成） | **主体成立，一处错误码偏差与一处原子性偏差**。①启动快照：`snapshot_revision_id = stored.current_revision_id` 与 page translated current 均已记录；②以当前 Page translated 为底、仅替换目标 bbox（`compose_region(base_bytes, clean_bytes, box, op)`）；③提交前复查 region current，变化则不提交；④page 侧由 compare-and-write 兜底。**偏差见 F-02（错误码）与 F-03（非同一事务内"同时比较"）** |

## Architecture 轴

| 检查项 | 结论 |
|---|---|
| `ports` / `application` 无 PySide6/sqlite 依赖 | **PASS**。`git grep -E '^\s*(import\|from)\s+(PySide6\|shiboken6\|sqlite3)' 72cb2be -- src/ports src/application` 无命中；全字检索仅命中 `src/ports/repositories/__init__.py:5` 的 docstring 文字，非导入。DTO（`LayoutRequest`/`RenderOp`/`SourceStyle`/`LayoutResult` 等）全部只用内置类型 |
| `application` 不依赖 `infrastructure` | **PASS**，0 命中 |
| `infrastructure` 依赖方向 | **PASS**。`infrastructure/rendering/**` 只导入 `ports.rendering.ports`、`ports.repositories.artifacts` 与 `application.rendering.style`，未反向被 ports 依赖（除 F-01 所列的 `TextDirection` 例外） |
| 未越白名单 | **PASS**。实际新增路径为 `src/ports/rendering/**`、`src/application/rendering/**`、`src/application/translation/color/**`、`src/infrastructure/rendering/**`、`tests/rendering/**`，与 TASK-014 `allowed_paths` 逐条对应；`verification/TASK-014/**` 与 `doc/handoffs/TASK-014-*.md` 由 Handoff 提交提供 |
| 未改 domain / schema / 共享文件 | **PASS**。`git diff --name-status 29592c9 72cb2be -- src/domain src/infrastructure/sqlite src/ports/repositories src/application/library src/application/editing src/bootstrap src/ui` **为空**；`Ports` 未修改既有 `ArtifactRepositoryPort`（新增只读 `PageArtifactLocator` 而非扩共享文件），未新增迁移，无依赖变化 |
| Qt 依赖的约束方式 | **部分**。Handoff L75 自认"守卫仅覆盖 domain/ui，本切片靠约定 + 测试导入路径维持"——经核对属实（见 F-05） |

## Verification 轴

| 场景 | 命令 | 环境 / commit | 结果 |
|---|---|---|---|
| 必需检查 | `git diff --check 29592c9 72cb2be` | Git 2.52.0 | **PASS，退出码 0** |
| 全量回归（任务指定） | `python -m pytest tests -q` | `TASK-014-py312`（Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1），**默认 Windows Qt 平台** | **PASS，退出码 0，153 passed in 4.40s**（与作者证据一致） |
| 渲染套件 | `python -m pytest tests/rendering -q` | 同上 | **PASS，56 passed in 1.46s** |
| 收集数 | `python -m pytest tests --collect-only -q` | 同上 | 153 tests collected |
| 环境核对 | `python --version`；`import PySide6`；`$env:QT_QPA_PLATFORM` | 同上 | Python 3.12.3；PySide6 6.11.2；变量未设置（默认 Windows 平台，符合 Handoff 复现要求） |
| 视觉质量人工评审（字体美感、shrink 后可读性） | 未执行 | — | **NOT_RUN**（本切片证据为像素/几何断言；Task 禁止虚构视觉达标结论，作者亦未声称） |
| 非 Windows 平台 Qt 行为 | 未执行 | — | **N/A**（产品边界为 Windows） |
| 真实 OCR/翻译质量 | — | — | **N/A**（rerender 不涉及 OCR/Translation，AC-RENDER-001 结构性排除） |
| 并发/多写者竞态实测 | 未执行 | — | **NOT_RUN**（见 F-03；单写者语义已由测试覆盖） |
| 性能 / 大页面批量渲染 | 未执行 | — | **N/A**（本 Task 无性能 AC） |

**未运行项均标记 NOT_RUN/N/A，未以推测替代。**

## Findings

| ID | 级别 | 文件/行 | 触发条件 | 影响 | 复现 | 建议 | disposition |
|---|---|---|---|---|---|---|---|
| F-01 | P2 | `src/ports/rendering/ports.py:13`（`from application.rendering.style import TextDirection`）；同文件 L28/97/130 用作 DTO 字段类型 | 任何对渲染契约的依赖分析或后续切片 | **ports 层反向依赖 application 层**。`TextDirection` 是被 `ports` 与 `infrastructure` 共同消费的共享 DTO，却定义在 `application.rendering.style`，使依赖方向成为 `ports → application`（而 `infrastructure → application`/`infrastructure → ports` 并存）。当前不构成导入环（`application.rendering.style` 不导入 ports），但把"契约层最内层"的分层关系倒置，后续若让 `style.py` 需要 ports 类型即会成环 | `git grep -n 'from application' 72cb2be -- src/ports`（仅此 1 处）；`git grep -n 'from application.rendering.style' -- src/infrastructure/rendering`（3 处） | 把 `TextDirection`（及后续纯枚举 DTO）下沉到 `src/ports/rendering/`（或 domain），令 `application` 与 `infrastructure` 都从 ports 取用；`application.rendering.style` 可 re-export 保持兼容 | open（非阻塞） |
| F-02 | P2 | `src/application/rendering/service.py:287`（`error_code="INPUT_REVISION_CHANGED"`）；L494（透传 `outcome.error_code`） | 合规基座或 Region 在合成期间变化 | TASK-002 §8.2 明文要求"提交时同时比较 Page artifact current 与目标 Region current；**任一变化返回 `COMPOSITION_BASE_CHANGED`**"，而实现两条路径均以 `INPUT_REVISION_CHANGED` 表达（Handoff 措辞为"COMPOSITION_BASE_CHANGED 族"）。契约 §10 把两个码列为**不同行**，调用方若按契约分支将收不到 §8.2 承诺的码 | 阅读 `rerender_region` 的复查分支与 `_commit_translated` 的映射表；对照契约 §8.2 与 §10 错误码表 | 在 Region 复查与 page 侧 compare-and-write 冲突时返回 `COMPOSITION_BASE_CHANGED`（或先在 TASK-002 契约中把两个码的关系写明并经 Codex 确认），使可观察码与 §8.2 一致 | open（非阻塞） |
| F-03 | P2 | `src/application/rendering/service.py:282-290`（复查在 `_commit_translated` **之前**） | 单 Region 合成期间，同一 Region 的 current 在"复查之后、artifact 提交之前"被另一写者更新 | §8.2 要求"提交时**同时**比较"两者，实现是"先复查 region（事务外）→ 再提交 artifact（compare-and-write 只比对 page translated current）"。因此在复查与提交之间的窗口内，Region 的更新不会被任何检查拦截，新 revision 虽基于旧 region 内容仍会提交，current 被推进。可观察语义在**单写者**下成立（复查拦截了测试注入的竞态），窗口竞态需并发写者才可触发 | 阅读两段代码的先后关系；Handoff 风险第 3 条亦自认该窗口 | 中期把 region current 复查并入 artifact 事务（需扩展 TASK-029 的 seam，超出本 Task 白名单），或由 TASK-011 编排层以重试收口；在闭口前应在 Task 中保留该遗留记录 | open（非阻塞，已声明遗留） |
| F-04 | P2 | `doc/tasks/TASK-014.md`（技术决策段末行："测试用 `QT_QPA_PLATFORM=offscreen`"） | 后续 Agent 按 Task 文件复现测试 | 与事实矛盾：Handoff L74 与 Reviewer 实测均表明 **offscreen 平台无字体库，本套件不可用**，必须用默认 Windows 平台。该行是规划期遗留，未随实现更新 | `git show 72cb2be:doc/tasks/TASK-014.md \| Select-String offscreen`；对照 Handoff L74 的复现说明 | 把该行更正为"测试使用默认 Windows 平台（offscreen 无字体库不可用）"，或删除该过时表述 | open（非阻塞） |
| F-05 | P2 | 全切片；对照 `tests/core/test_architecture.py` 的 `DOMAIN_FORBIDDEN`/`UI_FORBIDDEN` | 后续切片在 `ports`/`application` 中误引 Qt/sqlite | TASK-005 架构守卫只覆盖 `src/domain` 与 `src/ui`，本切片新增的 `src/ports/rendering`、`src/application/rendering`、`src/application/translation/color` **不在任何守卫范围内**；当前"无 PySide6/sqlite"完全依赖作者约定与本次人工核验。Handoff L75 亦主动声明这一点 | 阅读 `test_architecture.py` 的禁入集合；本次架构轴为人工 `git grep` 核验，非自动防线 | 把守卫的禁入根扩展到 `src/ports` 与 `src/application`（这两层同样不应出现 Qt/sqlite），使该约束成为回归可测的防线；归属与范围由 Codex 决定 | open（非阻塞） |

P0 = 0，P1 = 0，P2 = 5（F-01～F-05），均不阻塞集成。

## 三轴结论

**Spec**：`AC-STYLE-001..005` 与 `AC-RENDER-001/002` 均有实现与测试对应；`AC-RENDER-001` 是**结构性保证**（构造函数不存在 AI 端口），比分支约束更强；D06 §23/§47/§85 的三处输入与门控语义与实现一致；TASK-002 §8.1 的 compare-and-write 被直接复用而未重写。§8.2 的四处要点中，启动快照、以 Page artifact 为底、仅替换目标 bbox 三点成立，第四点"同时比较并返回 `COMPOSITION_BASE_CHANGED`"存在错误码偏差（F-02）与非同一事务的原子性偏差（F-03）；后者作者已如实登记为需扩 TASK-029 seam 的遗留，超出本 Task 白名单。

**Architecture**：分层守卫的人工核验结果良好——`ports`/`application` 无 Qt 与 sqlite 导入、`application` 不依赖 `infrastructure`、未触碰 `domain`/schema/共享 port 文件、未新增依赖、实际路径与白名单逐条吻合；新端口 `PageArtifactLocator` 以"新增只读协议"而非"扩共享文件"的方式解决 page→artifact 定位，边界处理克制。唯一方向性问题是共享 DTO `TextDirection` 落在 application 层导致 `ports → application`（F-01）；另有"该约束尚无自动守卫"的防线缺口（F-05）。

**Verification**：在指定任务环境、默认 Windows Qt 平台下复跑 `python -m pytest tests -q` 得 **153 passed**（退出码 0），与作者证据一致；渲染套件 56 passed，收集数一致。测试为真实断言（真 Qt 度量、真 SQLite + managed storage、真 PNG 提交），未使用 mock 替代被测行为；助手可见的 spy 仅用于证明"零 AI 调用"。未运行项（视觉质量人工评审、非 Windows 平台、并发实测、性能）均如实标 NOT_RUN/N/A。

## 结论与复审

**`72cb2be` 可交 Codex 集成：decision = approved。**

- 四条 Task AC 中，前三条（字号链与渲染样式、rerender 只用 Clean+final+TextStyle 且不触发 AI、页级/Region 级合成遵守 TASK-002 并输出新 ArtifactRevision、失败保留旧 current）在本切片范围内成立；第四条（Handoff/测试记录/独立 Review/集成）由本次结论与后续 Codex 集成完成。
- 无 P0/P1 未解决；5 项均为 P2，可在集成前后的文本或小改提交中关闭，不需新的 reviewed head。
- 本批准覆盖 `29592c9..72cb2be` 的实现与测试；`base_commit` 不变，未触碰共享文件与 schema，回退方法为整分支 revert。

**集成时须由 Codex 完成**：核对 `72cb2be` 为当前 head、按协议 §6.6 串行集成、记录 `integration_commit`，把本次 decision 与 F-01～F-05 的 disposition 回填 `doc/STATUS.md`、`doc/tasks/TASK-014.md` 与 Handoff，并在集成后执行主线复验；F-05（守卫扩展）建议单独立项，因其修改 `tests/core` 而非本 Task 白名单路径。

**剩余风险**：SourceStyle 的像素估算为启发式（复杂背景会触发 fallback 26，属 D06 §8 设计内行为）；`_SHRINK_STEP=0.5` 为文档未规定的实现选择；Qt 字体度量存在跨平台差异，测试只用比例断言；单 Region 合成的原子性窗口（F-03）由单写者假设覆盖。以上除 F-01～F-05 外无新增风险，且均未超出 TASK-014 授权范围。**本报告不释放任何冻结任务（含 TASK-013/TASK-015），也未修改任何生产代码。** 本报告事实仅适用于 `72cb2be`；分支后续变化（含 `a49fc76`）不延用本批准。
