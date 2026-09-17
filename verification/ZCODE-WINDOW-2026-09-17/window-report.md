# ZCode 全权窗口报告（2026-09-17 23:12:28 → 2026-09-18 08:50）

> 作者：ZCode（窗口内唯一主线写入与集成责任人）。授权条款：[STATUS](../../doc/STATUS.md)「ZCode 全权窗口授权（2026-09-17）【生效中】」；作业指令：[ZCODE-WINDOW-2026-09-17.md](../../doc/handoffs/ZCODE-WINDOW-2026-09-17.md)。
> v1 固化于 2026-09-18 ~02:30；**v2（~03:25）追加插队项 TASK-023 的收口交付**（见「v2 追加」节）。
> **v3（~05:55）追加第二轮（W5/W6/W7）收口交付**——第二轮授权见 [round2 指令包](../../doc/handoffs/ZCODE-WINDOW-2026-09-17-round2.md)（同一 T1=08:50）。
> **本报告不改变任何 Review 定性**：窗口内全部结论均为 `approved_subagent`（用户授权的同体审查，非协作协议 §1 跨 Agent 独立批准）；**期满后 Codex + DeepSeek Harness 必须对下列全部集成交付补外部 post-hoc 复审，可推翻任何窗口内 `done`**。

## 1. 队列项最终状态

| # | 切片 | 最终状态 | 实现 head | Review | Review 结论 | integration_commit |
|---|---|---|---|---|---|---|
| W1 | [TASK-037](../../doc/tasks/TASK-037.md) 已定性 flaky 修复 + TASK-036 R-01 | **done** | `7b96e72`（docs `b0e243e`） | [doc/reviews/TASK-037-7b96e72.md](../../doc/reviews/TASK-037-7b96e72.md)（`7c35277`） | approved_subagent（2×P3） | `372c3bf` |
| W2 | [TASK-033](../../doc/tasks/TASK-033.md) 完整链收口（旗舰） | **done** | `933819f`（docs `e308f98`） | [doc/reviews/TASK-033-933819f.md](../../doc/reviews/TASK-033-933819f.md)（`401d6d7`） | approved_subagent（R-001 P2 deferred 登记合规；2×P3 备查） | `4d0f932` |
| W3 | [TASK-020](../../doc/tasks/TASK-020.md) Webtoon 分块处理与阅读 | **done** | `7833604` + 修订 `b337f71`（docs `ddcf884`/`e31e7cc`） | [doc/reviews/TASK-020-7833604.md](../../doc/reviews/TASK-020-7833604.md)（首轮 `baffcc4` changes_requested → 复审 `40f20e7`） | 首轮 changes_requested（R-001 P1）→ 修订后 **approved_subagent**（R-001/R-004 closed；R-002/003/005 deferred；R-006 P3 open） | `b738200` |
| W4 | 文档状态同步 + 窗口报告 | **完成** | `157d289`（00_INDEX/12_ROADMAP 状态段）+ 本报告 | —（纯文档） | — | — |
| 插队 | [TASK-023](../../doc/tasks/TASK-023.md) PDF/MOBI 导入（v2 追加） | **done** | `7fa9118`（docs `8e713fa`/`52445f4`） | [doc/reviews/TASK-023-7fa9118.md](../../doc/reviews/TASK-023-7fa9118.md)（`c87f21c`） | approved_subagent（4×P3 不阻断） | `ba7d560` |
| — | TASK-021/022/025/026/027 | **未触碰**（窗口排除项，保持冻结） | — | — | — | — |

集成均为 `--no-ff` merge（保留 merge 提交，parents＝当时 master + 分支 head），串行执行：`372c3bf` → `4d0f932` → `b738200` → `ba7d560`。

## 2. 未完成项与冻结原因

- **TASK-023 遗留（v2）**：①MOBI 光栅化 **BLOCKED**（无批准解析依赖；.mobi 导入得到 typed `UNSUPPORTED_FORMAT` 可诊断失败，不伪造）——解锁=用户批准 MOBI 解析依赖；②生产装配点（`ImportDocumentsUseCase` 在 bootstrap/入口 UI 接线）白名单外移交。
- **TASK-020 遗留（白名单外，移交 Codex）**：①生产装配点——`tile_factory` 需在 `bootstrap/app.py` 注入（本切片白名单不含 bootstrap），注入前生产 webtoon 走原整图路径；②1600x200000px fixture **像素解码 BLOCKED**（Qt PNG handler rgb32 ≳300MB 即失败且 `setClipRect` 无效，实测 40000px=256MB ok / 50000px=305MB fail、19GB 空闲内存排除 OOM）——几何层 PASS，解锁条件=批准流式 PNG 解码依赖或 Qt 上游修复。
- **TASK-033 遗留（白名单外，移交 Codex，R-001 P2 deferred）**：`src/application/tasks/service.py` 的 `_clean_available` 检查无人写入的 `clean` stage → render-only `RERENDER_*` 命令**跨 run** 仍规划 `BLOCKED(missing_clean_artifact)`（clean artifact 实际存在也被拦）；同 run `inpaint RUN → render RUN` 分支正常。建议立 planner 修复切片（需释放 `src/application/tasks/**` 范围）。
- **R-002/003/005/006（TASK-020 P3）**：随生产装配切片收口（见 [TASK-020 Handoff](../../doc/handoffs/TASK-020-7833604.md) disposition 表）。
- **W1-W3 期间的继承缺陷/登记**：TASK-034 的 R-03（常量跨层归属）与 R-06（webtoon flaky——已由 TASK-037 修复关闭）按原登记跟踪；flaky 节第 2 条（export 终态发布顺序）机制根因已关、保持登记观测。
- **修前树异常事件（未定性，如实登记）**：TASK-037 修前对照中 1 次全仓在 96% 处进程异常终止（无 pytest summary、EXIT=127；Git Bash 下），复跑 6+ 次未再现；与已知 flaky 签名不同，若再现按 flaky 节口径登记。

## 3. 窗口内全部集成清单（approved_subagent，供 post-hoc 复审排期）

| integration_commit | Task | reviewed_head | Review 报告 |
|---|---|---|---|
| `372c3bf` | TASK-037 | `7b96e72`（docs `b0e243e`） | [TASK-037-7b96e72.md](../../doc/reviews/TASK-037-7b96e72.md) `approved_subagent` |
| `4d0f932` | TASK-033 | `933819f`（docs `e308f98`） | [TASK-033-933819f.md](../../doc/reviews/TASK-033-933819f.md) `approved_subagent` |
| `b738200` | TASK-020 | `b337f71`（docs `e31e7cc`；首轮 `7833604` changes_requested 已修订） | [TASK-020-7833604.md](../../doc/reviews/TASK-020-7833604.md) 复审 `approved_subagent` |
| `ba7d560` | TASK-023 | `7fa9118`（docs `8e713fa`/`52445f4`） | [TASK-023-7fa9118.md](../../doc/reviews/TASK-023-7fa9118.md) `approved_subagent` |

## 4. 环境变化与基线对照

- **依赖清单：零变更**（`pypdfium2` 未安装——TASK-023 未实施）。无 Schema/migration 变更。未 push、未配置远端。
- **测试基线**（授权基线：master `c3dabc8` 全仓 737 passed / 6 skipped，PowerShell 口径）：
  - 口径差异（非环境变化）：本窗口全部命令在 **Git Bash** 下执行，`shutil.which("openssl")` 可用，`tests/network` 的 6 条 TLS 测试**真实执行**而非 skip → 本窗口全仓口径为 **N passed / 0 skipped**（PowerShell 口径应为 N-6 passed / 6 skipped；两口径收集总数一致）。
  - W1 后：743 passed / 0 skipped（+6 = TASK-037 `test_helpers.py`；即基线 737+6 收集数）。
  - W2 后：754 passed / 0 skipped（+5 = TASK-033 `test_full_chain.py` 4 例 + bootstrap 装配 1 例）。
  - W3 后：764 passed / 0 skipped（+10 = TASK-020 `test_webtoon_tiles.py`）。
  - TASK-023（插队）后：**770 passed / 0 skipped**（+6 = `tests/import_formats/`）。**依赖变更留证：pypdfium2==5.13.0 安装前后全仓各 764 passed/0 skipped exit 0**（共享 venv 零扰动）。
  - 全仓串跑：TASK-033 ×5、TASK-020 ×5（集成前各 5 次，全部 exit 0）+ 每次集成后复验 1 次，均 0 flaky 命中。
- **环境探针/记录产物**：`verification/TASK-037/`（机制探针×3 + 修前/修后对照日志 + 判别力日志）、`verification/TASK-033/full-suite-runs.log`、`verification/TASK-020/full-suite-runs.log`。

## 5. 遗留风险与建议

1. **post-hoc 复审义务（最高优先）**：T1 后 Codex + DSH 按上表逐一复审；TASK-020 的 R-001 修订历史（首轮 changes_requested → 复审通过）值得重点复核。
2. **planner `_clean_available` 继承缺陷**（TASK-033 R-001 P2）：影响所有 render-only 命令跨 run 使用；建议独立小切片（释放 `src/application/tasks/service.py`）。
3. **超大 webtoon 像素解码**（TASK-020 BLOCKED）：真实产品能力缺口；解锁需依赖变更（用户批准）或 Qt 上游修复；在解锁前产品 webtoon 阅读走整图路径（Qt 可读范围内）或生产装配后走 tile 路径但源文件超限时 fail-closed。
4. **shell 口径双轨**：openssl 有无导致全仓数字双口径（Git Bash / PowerShell）——建议在协作协议或 flaky 节固化两口径换算说明，避免"N passed"对不上（本窗口已在 STATUS 审核行注明）。
5. **MOBI 能力缺口**（TASK-023 BLOCKED）：需要用户批准 MOBI 解析依赖才能补齐；当前 .mobi 导入为可诊断失败。
6. **`importorskip` 新增的透明说明**：窗口内新测试文件有 2 处 `pytest.importorskip("PySide6", ...)`（TASK-033 `test_full_chain.py`、TASK-020 `test_webtoon_tiles.py`）——与 `tests/library/test_production_adapters.py` 等既有先例同范式，属 Qt 依赖缺失时的**环境声明**而非失败掩蔽：本窗口环境 PySide6 在位，两组测试**实际执行**（全仓 0 skipped）；TASK-033 Review R-002 已逐条审定该范式合规。
7. **窗口内 Review 全部为同体审查**：三切片的 approved_subagent 均不可当独立批准使用；任何一项被 post-hoc 推翻，按协议重开对应 Task。


## v2 追加：TASK-023（插队项）收口

- **插队门核验**：规则 (b) 满足——W1+W2+W3 已于 06:30 前全部集成（实际 ~01:05 完成 W2 集成、02:15 完成 W3 集成），余量 ≥2h；08:20 前完成集成（~03:15）。
- **交付**：integration_commit = `ba7d560`（merge，parents `cca8b09`+`c87f21c`）；实现 head `7fa9118`（7 文件 +603）。
- **依赖变更**：`requirements.txt` 新增 `pypdfium2==5.13.0`（用户批准的唯一一项），安装前后全仓对照各 764 passed/0 skipped/exit 0；readiness 断言零命中、无需更新。
- **Review**：`approved_subagent`（报告 `c87f21c`；四轴 executed；R-001～R-004 全 P3 不阻断）。
- **集成后复验**：全仓 770 passed / 0 skipped、exit 0。
- **MOBI**：BLOCKED（无批准解析依赖），非 PDF 载荷 typed `UNSUPPORTED_FORMAT` 可诊断；未记 PASS。


---

# 第二轮收口（v3 追加，2026-09-18 ~05:55）

> 第二轮窗口 = 同一 T1（08:50）的延续授权；队列 W5（必做）→ W6（必做）→ W7（条件：W5+W6 于 06:30 前集成）；统一证据口径＝`powershell.exe -NoProfile -Command`（Git Bash 会话启动，PATH 继承含 openssl）+ `TASK-012-py312` venv → 全仓 **N passed / 0 skipped**。

## 队列项最终状态（第二轮）

| # | 切片 | 状态 | 实现 head | Review | integration |
|---|---|---|---|---|---|
| W5 | [TASK-038](../../doc/tasks/TASK-038.md) 生产装配收口 | **done** | `317f33e` | [TASK-038-317f33e.md](../../doc/reviews/TASK-038-317f33e.md)（`fcf791f`）approved_subagent（3×P3） | `f835ac9` |
| W6 | [TASK-039](../../doc/tasks/TASK-039.md) planner `_clean_available` 修复 | **done** | `38fbde4` | [TASK-039-38fbde4.md](../../doc/reviews/TASK-039-38fbde4.md)（`18c9834`）approved_subagent（R-001/R-002 文档更正采纳、R-003 deferred、R-004 accepted） | `c8024fe` |
| W7 | [TASK-021](../../doc/tasks/TASK-021.md) 自洽子集（软删除/同 batch 恢复/受控-only 永久删除） | **done（子集）**；其余三个子集 **frozen** | `887e0d6` | [TASK-021-887e0d6.md](../../doc/reviews/TASK-021-887e0d6.md)（`a9b4141`）approved_subagent（R-001 P2 open 登记处置、3×P3） | `5bc17f8` |

## 第二轮关键交付

- **W5**：`assemble_engine` 注册 `readerViewModel`/`exportViewModel`（此前生产阅读器是惰性空态页）；export 双路径注册名对应关系写明并以测试锁定（路径 A=`readerViewModel.exportController`、路径 B=`exportViewModel` 随 workbench 章节重建重发布）；`tile_factory` 注入（TASK-020 分块阅读生产可达）；`ImportDocumentsUseCase` 接线（TASK-023 PDF 可达，MOBI 仍 typed UNSUPPORTED）；`test_qml_contract.py:224` 前提变化等价更新。暴露并处置两个装配面缺陷（Page→ReaderPage 契约适配 `_ManagedReaderCatalog`、无页章节导航防御）。
- **W6**：TASK-033 R-001（P2）关闭——`_clean_available` 判据叠加可选 `clean_probe`（probe=None 与修前逐字节等价；对照矩阵+判别力 7 failed/1 passed 留证）；**生产 probe 注入点（bootstrap）白名单外，移交后续装配切片**。
- **W7**：Page 级软删除/同 batch 恢复/受控-only 永久删除（Schema 预检通过——`deleted_at` 列本就存在，零 Schema 变更）；`remove_managed` 防逃逸；测试含 managed 根外模拟源文件逐字节幸存证明。**R-001 P2 open（跨 batch 重叠 page_id 的 API 层串扰）——处置计划：集成后修复/并入 trash 后续子集。**

## 第二轮 approved_subagent 清单（供 post-hoc 复审排期）

| integration_commit | Task | reviewed_head | Review |
|---|---|---|---|
| `f835ac9` | TASK-038 | `317f33e` | `fcf791f` approved_subagent |
| `c8024fe` | TASK-039 | `38fbde4` | `18c9834` approved_subagent |
| `5bc17f8` | TASK-021 | `887e0d6` | `a9b4141` approved_subagent |

## 第二轮基线与口径

- 基线（round2 指令，纯系统 PATH PowerShell）：764 passed / 6 skipped（`047164e`）。**本窗口全部数字统一为 powershell.exe（继承 PATH，openssl 可用）+ TASK-012-py312 口径**：开工基线 770 passed / 0 skipped → W5 后 772（+2 契约测试）→ W6 后 780（+8）→ W7 后 **786 passed / 0 skipped**（+6）；各切片全仓 ×5 逐次留证（TASK-038/039/021 verification 目录）。
- 依赖清单：**零变更**（本轮无新依赖）。Schema/migration：**零变更**（TASK-021 软删除依赖既有 `deleted_at` 列，预检留证）。

## 第二轮未完成项与冻结原因

- **TASK-021 其余三个子集 frozen**（备份/恢复、缓存/版本/模型清理、日志/诊断包）——窗口时间预算下的取舍（round2 指令：只交付一个完整子集）。
- **生产装配注入遗留清单**（各切片白名单外，移交后续装配切片）：TASK-020 `tile_factory` ✅（W5 已接）、TASK-023 `ImportDocumentsUseCase` ✅（W5 已接）、**TASK-039 `clean_probe` 生产注入（待接——未接前生产 render-only 命令保持既有 BLOCKED 行为）**。
- **MOBI 解析依赖**与**超大 webtoon 像素解码**：维持用户裁决等待状态（第一轮已登记）。
- **TASK-021 R-001 P2**（跨 batch 重叠 page_id 的 API 层串扰）：处置计划=集成后修复/并入 trash 后续子集。
