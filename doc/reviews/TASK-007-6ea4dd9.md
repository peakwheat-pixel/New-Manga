---
task_id: TASK-007
reviewer: DeepSeek Harness
author: ZCode
base_commit: 6b123fe55f2e6373335b044fc5e5f169b5d108e0
reviewed_head: 6ea4dd9241c0a24f60964b570cb768bb48dfa0f3
decision: approved
---

# Review：TASK-007 书架领域与本地图片导入（6ea4dd9）

本报告只覆盖 `6b123fe..6ea4dd9`。Review 期间未修改被审实现、测试或验证脚本，未触碰 ZCode worktree；本报告是 Reviewer 新增的唯一文件。

## 范围与依据

**固定对象**：`base_commit = 6b123fe55f2e6373335b044fc5e5f169b5d108e0`、`reviewed_head = 6ea4dd9241c0a24f60964b570cb768bb48dfa0f3`；作者分支 `agent/zcode/TASK-007-library-import`，后置元数据提交不在被审范围。

**变更**：`git diff --stat 6b123fe 6ea4dd9` = 20 路径、`+1489/−8`，全部位于 TASK-007 `allowed_paths`（`src/domain/books/**`、`src/domain/pages/**`、`src/application/library/**`、`src/application/importing/images/**`、`tests/library/**`、`doc/tasks/TASK-007.md`）。`src/infrastructure`、`src/ports`、`src/bootstrap`、`src/ui`、`tests/core`、`tests/storage`、依赖清单、AGENTS、其他 Task **零触碰**（独立过滤确认空集）；无 QML、无 Volume、无新依赖。

**依据**：TASK-007 四条 AC 与 13 个主责任编号 AC；D03 §3/§4.1~4.4/§5/§30；D04 §4~10；D07 §37~39；D08 `AC-LIB-001~003`、`AC-CH-001~004`、`AC-IMPORT-001~005`、`AC-PAGE-001`。

**Reviewer 环境**：Windows `10.0.26200`；系统 Python `3.14.6`；项目固定环境（Reviewer venv Python `3.12.3`，含 PySide6 6.11.2）；1 组独立探针（临时目录，未写入被审仓库）。

## 重点核验项结论

| 核验项 | 结论 |
|---|---|
| ① `application/importing/images/service.py` 失败顺序与 AC-IMPORT-003 | **满足**。`import_files` 逐文件顺序为 `read → sha256 → 去重(可选跳过) → decode 校验 → Managed Copy → add_page`；`add_page` 严格在 `store_original` 返回之后（源码 L111 注释即此约束）。AC-IMPORT-003 的禁止形态是"数据库已有 Page 但 Managed Original 不存在"：copy 抛 `OSError` → `COPY_FAILED` 且不建 Page；decode 抛 `ImageDecodeError` → `INVALID_IMAGE` 且既不复制也不建 Page（测试断言 `store.stored == {} and sink.pages == []`）。取消在下一个文件开始前生效，已提交页保留、未处理文件进 `pending_after_cancel`。`Page.__post_init__` 还强制 `managed_original_ref` 非空，形成第二道防线 |
| ② 领域方向不变量与 D03 §4.4 等价性 | **等价（实际路径正确）**。D03 §4.4 要求：webtoon 默认 vertical、paged 默认方向由作品设置继承且可为 rtl/ltr、同 Book 可混类型。`Chapter._enforce_direction_invariant` 把前两条升格为硬不变量（webtoon 非 vertical、paged 为 vertical 均抛 `ValueError`），`LibraryService.create_chapter` 的解析顺序为「显式 direction → webtoon 则 vertical → book 默认非 vertical 则继承 → 否则回落 rtl」。**独立探针**验证：book 默认 ltr + paged → `ltr`（继承正确）；webtoon 书默认 → `webtoon/vertical`；webtoon 书下显式 paged → `paged/rtl`（回落而非非法继承）；显式 webtoon → `vertical`；`paged + vertical` 被拒。**但同名的 `Chapter.with_inherited_defaults` 是错误死代码**（见 F-01） |
| ③ `application/library/ports.py` 的消费侧契约定义 | **形态可接受，位置需统一**。以 `typing.Protocol` 定义 `LibraryRepository`（16 个方法，覆盖 book/chapter/tag 与 book-tag 关联），遵守消费侧定义端口的分层惯例，也未把持久化细节泄漏进用例。Handoff 已声明原因（本 Task `allowed_paths` 不含 `src/ports`/`src/infrastructure`）并明确 SQLite 落地待后续授权。**但** TASK-006 已在 `src/ports/repositories/**` 建立端口位置约定，两套位置并存构成架构分叉（F-04） |
| ④ favorite/archive 与 Tag 隔离测试充分性 | **充分**。`test_favorite_and_archive_are_system_states` 断言三件事：设置系统标志后 `list_tags() == []` 与 `tags_of_book() == []`（不产生 Tag 行）；创建同名用户标签"收藏夹"并绑定后，`is_favorite=False` 不影响该标签存在；两者互不干扰。**独立探针**复现同一结论。`Book.is_favorite`/`is_archived` 是实体字段，`Tag` 实体不含这两个语义，`set_favorite`/`set_archived` 只调用 `update_book`，代码路径上不存在创建 Tag 的可能 |
| ⑤ 完整阅读 diff/调用链/需求/测试 | 已逐文件阅读 20 个变更路径与 `tests/library` 全部 5 个文件（25 项）。依赖方向正确：`domain` 不依赖 `application`；`application` 只依赖 `domain` 与自身 `ports`；`src/domain` 与 `src/application` **无 sqlite3/PySide6 实际导入**（TASK-005 架构守卫通过）。未发现契约外错误码、未发现业务越界 |

## Findings

| ID | 级别 | 文件/行 | 触发条件 | 影响 | 复现 | 建议 | disposition |
|---|---|---|---|---|---|---|---|
| F-01 | P2 | `src/domain/books/entities.py:165-185`（`Chapter.with_inherited_defaults`） | 任何调用方按 docstring 期望"未设置方向时从 book 继承"而调用它 | 该方法**无法实现其声明**：`Chapter.reading_direction` 是带默认值 `RTL` 的非 Optional 字段，且 `__post_init__` 会拒绝 `None`，因此 `reading_direction is None` 分支不可达。**独立探针**：`Chapter(...)` 默认 direction=`rtl`；`with_inherited_defaults(PAGED, LTR)` 仍返回 `rtl`（未继承）；传 `reading_direction=None` 构造直接抛 `ValueError: None is not a valid ReadingDirection`。全仓检索确认该方法**无任何调用点**，属死代码；真正的继承逻辑在 `LibraryService.create_chapter` 内重复实现 | 探针输出；`git grep -n 'with_inherited_defaults' 6ea4dd9` 仅命中定义行 | 删除该方法（继承已由 service 承担），或改为接受 `ReadingDirection \| None` 并把继承语义真正实现后由 service 复用；无论哪种都应补一条直接测试，避免"看似存在第二套继承实现" | open（非阻塞） |
| F-02 | P2 | `tests/library/test_book_crud.py:92-104`；`tests/library/test_chapters.py:51-64` | 读者依据测试名与 Handoff/Task 表述判断覆盖强度 | ① `test_simulated_restart_keeps_persisted_state` 中 `repo = type(library._repo)()` 只创建**一个** repository 实例，`first` 与 `second` 两个 `LibraryService` 共用它；`InMemoryLibraryRepository` 用实例属性存储，因此该测试证明的是"service 无状态、状态全在 repository"，**并非**"重启后从持久化重载"。Handoff 与 Task 的"含模拟重启重载"表述强于测试实际强度。② `test_type_defaults_inherit_from_book` 只覆盖"webtoon 书 → webtoon 章节"与"webtoon 书下 paged 回落 rtl"，未覆盖 `create_chapter` 的 **"book 默认 ltr → paged 章节继承 ltr"** 分支（该分支经 Reviewer 探针确认实现正确，但无测试守护） | 阅读两处测试代码；探针确认 ltr 继承行为；`InMemoryLibraryRepository.__init__` 的实例属性存储 | ① 把测试名或注释改为"service 无状态/同一 repository 复used"的准确表述，或在 fake 上增加显式快照/重建语义；② 为 ltr 继承分支补一条断言 | open（非阻塞） |
| F-03 | P2 | `tests/library/helpers.py:15-16`（经 `tests/library/conftest.py:7` 传递） | 在未安装 PySide6 的解释器上运行任一条任务命令（含纯领域测试） | `helpers.py` 在**模块级**导入 `PySide6.QtCore/QtGui`，而 `conftest.py` 导入 `helpers`，因此 `tests/library` 整个目录在**收集期**即失败——即使只想跑不涉及解码的领域测试也无法运行。**实测**：`python -m pytest tests/library` 与 `PYTHONPATH=src python -m pytest tests` 在系统 Python `3.14.6`（无 PySide6）分别以退出码 4 / 2 终止于 `ModuleNotFoundError: No module named 'PySide6'`；在项目固定环境 Python `3.12.3` 下分别为 25 passed / 62 passed | 两条字面命令在两个解释器下的对比运行（见验证表） | 把 Qt 相关导入移到使用处（函数内 import）或对依赖 Qt 的测试用 `pytest.importorskip("PySide6")` 标记，使领域测试可在无 Qt 环境单独收集；项目固定环境为 3.12，故不阻塞本切片 | open（非阻塞） |
| F-04 | P2 | `src/application/library/ports.py`；`src/application/importing/images/ports.py`（对照 `src/ports/repositories/**`） | 后续切片实现 SQLite 适配器时 | TASK-006 已在 `src/ports/repositories/**` 建立端口位置约定（`ArtifactRepositoryPort`、`DatabasePort`、`ManagedFileStoragePort`），本 Task 因 `allowed_paths` 限制改在 `src/application/*/ports.py` 定义消费侧 Protocol。两者都合法，但**同一仓库的两套端口位置**会让后续适配器不知道该实现哪一侧，长期形成架构分叉。Handoff 已如实声明该边界并指出 SQLite 落地待协调 | 两个目录的实际文件与 Handoff「边界与设计决策」第 1 条 | 由 Codex 在后续授权切片明确取舍：或把 `LibraryRepository` 迁入 `src/ports/`，或确立"消费侧协议留在 application、`src/ports/` 只放共享端口"的规则并同步 TASK-006 的两个端口；在规则确定前不要求本 Task 改动 | open（非阻塞） |

P0 = 0，P1 = 0，P2 = 4（F-01～F-04），均不阻塞集成。

## 验证

| 场景 | 命令或步骤 | 环境 / commit | 结果 | 证据 |
|---|---|---|---|---|
| 必需检查 1 | `git diff --check 6b123fe 6ea4dd9 --` | Git 2.52.0 | PASS，退出码 0 | 无输出 |
| 必需检查 2 | `git diff --stat 6b123fe 6ea4dd9` | 同上 | PASS | 20 files changed, 1489 insertions(+), 8 deletions(−) |
| 必需检查 3（任务命令字面） | `python -m pytest tests/library` | 系统 Python `3.14.6` | **FAIL（环境）** 退出码 4，`ModuleNotFoundError: PySide6`（收集期，见 F-03） | `tests/library/conftest.py` → `helpers.py` |
| 必需检查 4（任务命令字面） | `PYTHONPATH=src python -m pytest tests` | 系统 Python `3.14.6` | **FAIL（环境）** 退出码 2，同一原因 | 同上 |
| 同两条命令（项目固定环境） | `python -m pytest tests/library`；`PYTHONPATH=src python -m pytest tests` | Python `3.12.3`（Reviewer venv） | **PASS，退出码 0**：library **25 passed**、全量 **62 passed**（core 6 + storage 31 + library 25） | 与作者证据一致 |
| 独立探针：方向继承与不变量 | 构造 book/chapter 组合并断言 direction/type | Python `3.12.3` | **PASS**（实现正确） | book 默认 ltr + paged → `ltr`；webtoon 书下 paged → `rtl`；`paged+vertical` 被拒 |
| 独立探针：`with_inherited_defaults` | 调用并观察返回 | 同上 | **FAIL（发现 F-01）** | 传 book 默认 LTR 仍返回 `rtl`；传 `None` 抛 `ValueError` |
| 独立探针：favorite/archive 隔离 | set 标志后检查 Tag 集合 | 同上 | **PASS** | `list_tags() == []`、`tags_of_book() == []`；同名用户标签独立存活 |
| 架构边界 | `git grep -n -E '^\s*(import\|from)\s+(sqlite3\|PySide6)' -- src/domain src/application` | `6ea4dd9` | PASS | 0 命中（无实际导入） |
| 越界与冻结范围 | `git diff --name-only` 过滤 `src/infrastructure\|src/ports\|src/bootstrap\|src/ui\|tests/core\|tests/storage\|requirements*` | `6b123fe..6ea4dd9` | PASS | 空集 |
| 测试真实性 | 阅读 `tests/library` 全部 5 文件 | 同上 | PASS（含 F-02 的强度保留） | 失败注入为真实异常（`FakeManagedCopyStore` 抛 `OSError`）；decode 用真实 `QImage.fromData` 解码截断 PNG；无 mock/monkeypatch 绕过断言 |
| SQLite 持久化 / 真实事务与迁移 | 未执行 | — | **NOT_RUN（范围外）** | `allowed_paths` 不含 infrastructure/ports；Handoff 与 author-verification 已声明 |
| 生产 ImageDecoder / ManagedCopyStore 装配 | 未执行 | — | **NOT_RUN（范围外）** | 端口已定义，Qt 适配器仅在测试中 |
| 书架 UI / 搜索 / 回收站 / QML | 未执行 | — | **N/A** | 本 Task 禁止 QML；属 TASK-012+ |
| ReadingProgress 与 AC-LIB-004 | 未执行 | — | **N/A** | 非本 Task 主责 AC；`last_opened_at` 字段已就位 |
| PDF/MOBI/网页导入 | 未执行 | — | **N/A** | TASK-023 |
| 容量 / 性能 / 大书架 | 未执行 | — | **N/A** | 无本 Task AC |

## 三轴结论

**Spec**：13 个主责任编号 AC 均可由实现与测试对应，且关键路径经 Reviewer 独立探针复核。`AC-IMPORT-003` 的失败顺序（decode 校验在 Managed Copy 之前、Page 提交在 Copy 之后）正确，损坏图既不入库也不复制；`AC-IMPORT-002` 的源文件只读由真实文件 Hash 前后一致证明；`AC-LIB-003` 的"收藏/归档不得用普通 Tag 冒充"由三重断言与探针共同确认；`AC-CH-002/003` 的类型-方向不变量在领域层硬约束、在 service 层正确解析继承。未新增契约外错误码，未扩大产品范围（无 Volume、无 PDF/MOBI/网页导入、无 QML）。

**Architecture**：分层与依赖方向正确（`domain` ← `application`，`application` 只依赖 `domain` 与自身端口），`src/domain`/`src/application` 无 sqlite3/PySide6 实际导入，TASK-005 架构守卫未被破坏；`Page`/`Book`/`Chapter`/`Tag` 的不变量放在实体构造期，导入用例的三条端口（`ImageDecoder`/`ManagedCopyStore`/`ImportPageSink`）把成像栈与持久化挡在应用层之外，方向正确。需要 Codex 裁决的是端口位置分叉（F-04）与死代码方法（F-01）——两者都不影响本切片的运行行为，但会影响后续适配器与维护者的判断。

**Verification**：两条任务命令在**项目固定环境（Python 3.12.3）** 下通过（library 25 passed、全量 62 passed），与作者证据一致；在**系统 Python 3.14.6** 下因 `helpers.py` 的收集期 PySide6 依赖而失败（F-03）——该项目固定环境为 3.12（TASK-004/005 决定），故记为环境问题而非实现缺陷，并如实标注为 FAIL 而非 PASS。失败注入真实有效（真实 `OSError`、真实 Qt 解码截断 PNG），持久化落库与真实事务仍为 NOT_RUN（已声明）。测试强度有两处保留（F-02），已逐条列明而不影响结论。NOT_RUN/N/A 项按实记录。

## 结论与复审

**`6ea4dd9` 可交 Codex 集成：decision = approved。**

- 13 个主责任 AC 与四条 Task AC（AC1~AC3 由实现与测试支撑，AC4 待集成）在本切片范围内成立；重点核验的五项均给出明确结论。
- 无 P0/P1 未解决；本轮 4 项均为 P2，可在集成前后的文本/小改提交中关闭，不需新的 reviewed head。
- 本切片不触碰 `src/infrastructure`/`src/ports`，SQLite 落地与本 Review 提出的端口位置统一（F-04）应由 Codex 在后续授权切片一并处理。

**集成时须由 Codex 完成**：核对 `6ea4dd9` 为当前 head、按协议 §6.6 串行集成、记录 `integration_commit`，把本次 decision 与 F-01～F-04 disposition 回填 `doc/STATUS.md`、`doc/tasks/TASK-007.md` 与 Handoff，并勾选 AC1～AC4（AC4 需集成验证完成后）；集成后执行该切片的集成检查。

**剩余风险**：真实持久化（SQLite BookRepository、schema 扩展）完全未验证，`InMemoryLibraryRepository` 不能证明事务、约束与迁移行为——这是本切片最大的已知边界，Handoff 已如实声明；导入去重目前限同 Chapter 范围（`existing_sources_hashes(chapter_id)`），跨书架去重属产品决策未授权；`Page.page_locked`/`review_state`/`overall_status` 已建模但无消费方。四个一级页面、Provider、Pipeline、打包与发布均未实现，也未获本 Task 授权。本报告事实仅适用于 `6ea4dd9`；分支后续变化不延用本批准。
