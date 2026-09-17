# TASK-034 集成验证：`b6051e5`（AC ②③④⑤ 部分；AC ① 仍 BLOCKED）

## 固定对象

| 项目 | 值 |
|---|---|
| base commit | `b34b27e2bc7c1dbd4c3b15a91f08e158d966f365`（切片 diff base；分支起点 `c94c183` = 释放纯文档提交） |
| reviewed head（delivery） | `f83a33e` |
| 元数据 / 分支 head | `8ca99d4` |
| Review 报告 commit | `abda60f` → [`doc/reviews/TASK-034-f83a33e.md`](../../doc/reviews/TASK-034-f83a33e.md)（Reviewer=Codex，**非作者**；decision=`approved`，范围＝AC ②③④⑤） |
| AC ① 裁决 commit | 同 `abda60f` → [`doc/reviews/TASK-034-ac1-route-policy-ruling.md`](../../doc/reviews/TASK-034-ac1-route-policy-ruling.md)（R-1～R-7 + `src/` 三文件范围批准） |
| implementation merge / integration commit | `b6051e5`（merge，parents `abda60f` + `8ca99d4`） |
| 环境 | Windows `10.0.26200`；`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1）；`PYTHONDONTWRITEBYTECODE=1`；全部 `-p no:cacheprovider` |

## 复验结果（master `b6051e5`）

| # | 命令 | 退出码 | passed | skipped | 结果 | skip 原因 |
|---:|---|---:|---:|---:|---|---|
| 1 | `…python.exe -m pytest tests/providers tests/core tests/reading_export -q -p no:cacheprovider -rs` | 0 | **193** | **0** | `193 passed` | 无 |
| 2 | `…python.exe -m pytest tests/providers tests/editing -q -p no:cacheprovider` | 0 | **136** | **0** | `136 passed`（AC ④ 顺序 A） | 无 |
| 3 | `…python.exe -m pytest tests/editing tests/providers -q -p no:cacheprovider` | 0 | **136** | **0** | `136 passed`（AC ④ 顺序 B） | 无 |
| 4 | `…python.exe -m pytest -q -p no:cacheprovider -rs`（全仓） | 0 | **682** | **6** | `682 passed, 6 skipped` | 6 项均为既有 `tests/network` 的 `openssl unavailable`（`test_connection_tester.py:106`、`test_transport_tls.py:39/47/62/69/83`） |
| 5 | AC ② 判别力（Reviewer 独立探针） | 0 | — | — | 合成 `importlib.import_module`/`__import__` 文件 → **2 命中**；现树 `src/application` → **0 命中** | — |
| 6 | `git diff --name-only b34b27e b6051e5 -- src/` | 0 | — | — | **空**：整条切片 `src/` 零改动（AC ① 第 2 步未开始） | — |

## 集成结论

- [x] 非作者独立 Review 绑定固定 base/head，四轴（Standards / Spec / Architecture / Verification）均 `executed`、逐轴小结、**未跨轴排名**；**并行偏差已在报告显式声明**（未能取得两条独立 sub-agent 线程 → 按 §6 第 6 条兜底做两遍相互隔离检查）。
- [x] AC ②③④⑤ 已集成为生产测试基线；作者三项核心数字（193/0、136/136、682/6）由 Reviewer 独立复现，并在 master 上再次复验。
- [x] 6 条 skip 全为既有 `openssl unavailable`；**未新增 skip、未放宽/删除任何断言语义**。
- [x] 边界：22 个路径全在允许范围（`tests/**`、`doc/tasks/TASK-034.md`、`doc/handoffs/TASK-034-*.md`、`verification/TASK-034/**`），越界 0；未改 Schema/migration、依赖清单、pipeline seam 本体、`AGENTS.md`、`src/**`、其他 Task；未 push。
- [ ] **AC ① 未关闭**：第 1 步（裁决请求）已交付，**第 2 步未开始**，`src/` 保持零改动 → AC ① 记为 **`BLOCKED`**，Task 不得 `done`。

## Findings 处置

| ID | 级别 | 内容 | 处置 |
|---|---|---|---|
| R-01 | **P2** | `tests/reading_export/test_qml_contract.py:12`、`test_viewmodels.py:13` 的裸 `conftest` 导入与 AC ④ 同根因：`pytest tests/reading_export <伙伴目录>` 六种顺序全部 **2 collection errors / exit 2**（`ImportError: cannot import name 'requires_pyside6' from 'conftest'`）；`b34b27e` 纯净树同样复现 = **既有**缺陷 | **deferred，且绑定为强制项**：AC ① 第 2 步切片**必须**一并消除，并给出两种参数顺序 + 一个伙伴目录顺序的对照证据。**已在 master 上复现**（`pytest tests/reading_export tests/editing` → 2 collection errors），故这是**已知未关闭项**，不是遗漏 |
| R-02 | P3 | AC ⑤ 字面"passed 不减少" vs `tests/providers` 111→110（守卫迁出至 `tests/core`，该目录 +3） | **accepted**：口径按"总量不减少（679→682）+ 无断言语义丢失"解释；**不得**在 `tests/providers` 留转发薄用例（与 AC ②"不得留下两套"冲突） |
| R-03 | P3 | webtoon 用例首处由"一次 `processEvents()` 后断言"改为"5 s 有界等待后断言" = 观察窗口改变 | **accepted**（作者已主动披露）；集成记录与 Handoff **保留该披露**，不得记为"完全无变化"；导出用例方向经核对为**收紧** |
| R-04 | P3 | 半发布窗口的判别测试用合成假对象，真实 VM 结论依赖行号引用（引文经 Reviewer 逐行核对准确） | **open（非阻塞，如实登记）** |
| R-05 | P3 | 生产侧发布顺序（`src/ui/viewmodels/export/viewmodel.py:380/389`、`:392/398`）为 flaky 机制根因 | **deferred**：`src/ui/**` 不在本 Task 允许范围；登记为后续切片候选 |
| R-06 | P3 | webtoon 保存 flaky 12 次串跑未复现，根因未定 | **deferred**（登记，等待复现；诊断已就位） |
| R-07 | P3 | `allowed_routes` 为字符串时逐字符展开；`requirements` 非 bool 值被 `bool()` 强制转换（D-9/D-10） | **本次冻结 + 登记为后续项**（建议由"设置输入校验"切片统一处理），不在本 Task 扩张 |

## AC ① 裁决要点（详见 [裁决文档](../../doc/reviews/TASK-034-ac1-route-policy-ruling.md)）

- **R-1** 认可（显式 `default` 参数）；**R-2** 认可（两处一致抛 `ProviderInputError`，**须记录"装配路径由静默回落变为启动期报错"**）；**R-3** 认可；**R-4** 冻结；**R-5** 冻结（不收紧非 bool）；**R-6 采纳 Option B**（默认不指定彩色路线），并要求 `DEFAULT_ROUTE_POLICY` 对齐 `RoutePolicy` 默认与 TASK-018 已记录的 `default_eligible`（`allowed=("simple-fill","edge-bleed")`、`color_route=None`、`requirements={}`）；**R-7** 冻结 + 登记。
- **`src/` 范围变更：批准** 3 文件（`application/translation/inpaint/router.py` 新增唯一入口；`infrastructure/providers/runtime.py` 与 `handlers.py` 删除私有副本并复用），**限定**不改路由判定算法（`decide_route`/`acceptable_routes`/`preferred_route_order`/`route_gate`/`RouterFeatures`）与 Schema/依赖/seam。
- Option B 下的可观测变化必须在第 2 步 Handoff 记录，并提供"四种特征组合裁决前后**均 BLOCKED**、只是理由/allowed 集合变化"的证据。
