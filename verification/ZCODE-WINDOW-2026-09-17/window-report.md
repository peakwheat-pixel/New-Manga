# ZCode 全权窗口报告（2026-09-17 23:12:28 → 2026-09-18 08:50）

> 作者：ZCode（窗口内唯一主线写入与集成责任人）。授权条款：[STATUS](../../doc/STATUS.md)「ZCode 全权窗口授权（2026-09-17）【生效中】」；作业指令：[ZCODE-WINDOW-2026-09-17.md](../../doc/handoffs/ZCODE-WINDOW-2026-09-17.md)。
> 本报告 v1 固化于 2026-09-18 ~02:30（T1 前）；后续插队项若有交付将追加「v2 追加」节并重新提交。
> **本报告不改变任何 Review 定性**：窗口内全部结论均为 `approved_subagent`（用户授权的同体审查，非协作协议 §1 跨 Agent 独立批准）；**期满后 Codex + DeepSeek Harness 必须对下列全部集成交付补外部 post-hoc 复审，可推翻任何窗口内 `done`**。

## 1. 队列项最终状态

| # | 切片 | 最终状态 | 实现 head | Review | Review 结论 | integration_commit |
|---|---|---|---|---|---|---|
| W1 | [TASK-037](../../doc/tasks/TASK-037.md) 已定性 flaky 修复 + TASK-036 R-01 | **done** | `7b96e72`（docs `b0e243e`） | [doc/reviews/TASK-037-7b96e72.md](../../doc/reviews/TASK-037-7b96e72.md)（`7c35277`） | approved_subagent（2×P3） | `372c3bf` |
| W2 | [TASK-033](../../doc/tasks/TASK-033.md) 完整链收口（旗舰） | **done** | `933819f`（docs `e308f98`） | [doc/reviews/TASK-033-933819f.md](../../doc/reviews/TASK-033-933819f.md)（`401d6d7`） | approved_subagent（R-001 P2 deferred 登记合规；2×P3 备查） | `4d0f932` |
| W3 | [TASK-020](../../doc/tasks/TASK-020.md) Webtoon 分块处理与阅读 | **done** | `7833604` + 修订 `b337f71`（docs `ddcf884`/`e31e7cc`） | [doc/reviews/TASK-020-7833604.md](../../doc/reviews/TASK-020-7833604.md)（首轮 `baffcc4` changes_requested → 复审 `40f20e7`） | 首轮 changes_requested（R-001 P1）→ 修订后 **approved_subagent**（R-001/R-004 closed；R-002/003/005 deferred；R-006 P3 open） | `b738200` |
| W4 | 文档状态同步 + 窗口报告 | **完成** | `157d289`（00_INDEX/12_ROADMAP 状态段）+ 本报告 | —（纯文档） | — | — |
| 插队 | [TASK-023](../../doc/tasks/TASK-023.md) PDF/MOBI 导入 | 见 §2（评估中） | — | — | — | — |
| — | TASK-021/022/025/026/027 | **未触碰**（窗口排除项，保持冻结） | — | — | — | — |

集成均为 `--no-ff` merge（保留 merge 提交，parents＝当时 master + 分支 head），串行执行：`372c3bf` → `4d0f932` → `b738200`。

## 2. 未完成项与冻结原因

- **TASK-023（插队项）**：评估中；若未完成，冻结原因=窗口时间预算下的取舍（W1–W3 优先），恢复条件=后续窗口或常规释放。
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

## 4. 环境变化与基线对照

- **依赖清单：零变更**（`pypdfium2` 未安装——TASK-023 未实施）。无 Schema/migration 变更。未 push、未配置远端。
- **测试基线**（授权基线：master `c3dabc8` 全仓 737 passed / 6 skipped，PowerShell 口径）：
  - 口径差异（非环境变化）：本窗口全部命令在 **Git Bash** 下执行，`shutil.which("openssl")` 可用，`tests/network` 的 6 条 TLS 测试**真实执行**而非 skip → 本窗口全仓口径为 **N passed / 0 skipped**（PowerShell 口径应为 N-6 passed / 6 skipped；两口径收集总数一致）。
  - W1 后：743 passed / 0 skipped（+6 = TASK-037 `test_helpers.py`；即基线 737+6 收集数）。
  - W2 后：754 passed / 0 skipped（+5 = TASK-033 `test_full_chain.py` 4 例 + bootstrap 装配 1 例）。
  - W3 后：**764 passed / 0 skipped**（+10 = TASK-020 `test_webtoon_tiles.py`）。
  - 全仓串跑：TASK-033 ×5、TASK-020 ×5（集成前各 5 次，全部 exit 0）+ 每次集成后复验 1 次，均 0 flaky 命中。
- **环境探针/记录产物**：`verification/TASK-037/`（机制探针×3 + 修前/修后对照日志 + 判别力日志）、`verification/TASK-033/full-suite-runs.log`、`verification/TASK-020/full-suite-runs.log`。

## 5. 遗留风险与建议

1. **post-hoc 复审义务（最高优先）**：T1 后 Codex + DSH 按上表逐一复审；TASK-020 的 R-001 修订历史（首轮 changes_requested → 复审通过）值得重点复核。
2. **planner `_clean_available` 继承缺陷**（TASK-033 R-001 P2）：影响所有 render-only 命令跨 run 使用；建议独立小切片（释放 `src/application/tasks/service.py`）。
3. **超大 webtoon 像素解码**（TASK-020 BLOCKED）：真实产品能力缺口；解锁需依赖变更（用户批准）或 Qt 上游修复；在解锁前产品 webtoon 阅读走整图路径（Qt 可读范围内）或生产装配后走 tile 路径但源文件超限时 fail-closed。
4. **shell 口径双轨**：openssl 有无导致全仓数字双口径（Git Bash / PowerShell）——建议在协作协议或 flaky 节固化两口径换算说明，避免"N passed"对不上（本窗口已在 STATUS 审核行注明）。
5. **窗口内 Review 全部为同体审查**：三切片的 approved_subagent 均不可当独立批准使用；任何一项被 post-hoc 推翻，按协议重开对应 Task。
