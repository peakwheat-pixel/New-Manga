---
task_id: M2-PROD-SFX-PROBE-1
author: ZCode
recipient: Codex（集成轮）；Reviewer=DeepSeek Harness（非作者）
base_commit: d298ecd0
delivery_head: 33e824e4（r0 Owner 交付）→ r1 返修链 441f4ab5 / f6a25d69 / 4d95a2e7 → r2 顺笔闭合 441f4ab5..b4a9ad4d（runner+证据）+ 本 docs 同步——分支 tip 为准（DSH r2 R-1 同步登记）
status: in_review
---

# Handoff：M2-PROD-SFX-PROBE-1 — packaged sfx-detect 探针（frozen 进程内 SFX 真实推理 DML 运行证据）

## 交付结果

给 frozen sidecar 闭包新增**第五个独立探针入口** `sfx_detect_probe.exe`：启动即对样例页跑一次生产 `SfxDetectionProvider.detect`（与 `core.detect` handler 同一 provider 类、同装配语义）并打印 JSON（候选数/耗时/三键 `device`/`sfx_ep`/`sfx_ep_fallback`/权重 sha/页 sha），随后退出。**不动 IPC 命令面、不经 Tauri、零契约修订**（catalog_loader 独立入口先例形，AC1②；AC1③ 契约修订草案=不适用）。对 NSIS 安装后环境完成 frozen 进程内真实推理实测：K07_R123 真实页候选=1、conf=0.9047（与 v2b 锚点同源同页：页文件哈希逐位一致、conf 差 1.79e-7 在 GPU↔CPU 漂移窗口 ≤2e-06 内——DSH r1 P1-1 措辞更正）、device=dml 无 fallback、696ms——M2-PROD-DETECT-2 裁决⑥ NOT_RUN 的 sfx slice 由此闭合（deploy-record §5 声明，按 DSH r1 §4.1 精确边界=闭包面闭合，非 core_service 进程内可达、非 manga slice）。

Commit 链（worktree `G:/CODEX/New Manga.worktrees/M2-PROD-SFX-PROBE-1-zcode`，branch `agent/zcode/M2-PROD-SFX-PROBE-1`，base=d298ecd0）：

1. `a35bc041` claim(M2-PROD-SFX-PROBE-1)：Owner claim，status ready→in_progress
2. `b3caad0e` design：AC1① 冻结粒度核实（M2-C1/M2-IPC1/catalog_loader 先例/GATE CS-I1 at-least 语义）+ AC1② 探针路径提案 + AC2 实测面预登记
3. `2b4e4946` impl：`src/bootstrap/sfx_detect_probe.py` + `packaging/m2ac5/entries/entry_sfx_detect_probe.py` + `core_sidecar.spec`（五入口+探针专用 onnxruntime 闭包断言）+ `build_sidecar.ps1`（sanity gate+1）+ `tests/core/test_sfx_detect_probe.py`（12 测试）+ `verification/M2-PROD-SFX-PROBE-1/packaged-sfx-detect-probe.py`（runner）
4. `33e824e4` verify：探针 PASS / GATE 25/25 / 回归数字 / 包体积 / 构建链证据落盘
5. docs：Task 回填 in_review + deploy-record + 本 Handoff（b1dd1ad4）
6. r1 返修（集成方顺笔，DSH r1 C1-C4）：`441f4ab5` runner 判据加固+可追溯字段 → `f6a25d69` r1fix 重跑 4/4 PASS+range diff --check 真实落盘 → `4d95a2e7` docs+spec+README（C1/C2/C4）
7. r2 顺笔闭合（DSH r2 R-1..R-10）：`b4a9ad4d` R-2 SP-L2 三键判据落代码+R-7 注释+R-8 证据卫生+R-10 清理 → 本 docs 同步（R-1 Handoff 全同步/R-4 计数拆分/R-5 归因更正/R-6 spec 头注/R-9 frontmatter 清爽化/R-3 报告归档措辞）

变更路径（全部在 Task 允许面内）：`src/bootstrap/sfx_detect_probe.py`（新增，逐文件声明）、`packaging/m2ac5/{core_sidecar.spec,build_sidecar.ps1,entries/entry_sfx_detect_probe.py}`、`tests/core/test_sfx_detect_probe.py`、`verification/M2-PROD-SFX-PROBE-1/**`、`doc/tasks/M2-PROD-SFX-PROBE-1.md`、`doc/handoffs/`。**零触碰**：`contracts/**`、`apps/desktop/src-tauri/**`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、GATE runner 场景集（专项 diff 空）。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 冻结粒度核实+additive 选型 | 读 `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` rev 1.4 + `src/bootstrap/core_service.py` + `packaging/m2ac5/README.md` §3 + `run_clean_start_e2e.py` CS-I1 断言 | base d298ecd0 | PASS（结论落 Task 设计登记段） | `doc/tasks/M2-PROD-SFX-PROBE-1.md` |
| AC1 零触碰 | `git diff HEAD --stat -- contracts/ apps/desktop/src-tauri/ doc/STATUS.md doc/REBASELINE_PLAN.md packaging/m2ac5/run_clean_start_e2e.py` | 33e824e4 | PASS（空 diff） | verify commit |
| AC2 SP-L2 真实页 frozen 实测 | `packaged-sfx-detect-probe.py --install-dir <GATE 安装态>`（purged PATH+全 NEWMANGA_* 清除） | 构建 HEAD=2b4e4946，NSIS sha256 `3ffa03f5…` | **PASS：EXIT=0，候选=1，conf=0.9046692252159119（锚点 0.9046694040298462，差 1.79e-7 在漂移窗口 ≤2e-06 内；r1fix 实测页文件 sha256 与锚点 frame_sha256 逐位一致），elapsed=696ms，device=dml/sfx_ep=dml/sfx_ep_fallback=null** | `verification/M2-PROD-SFX-PROBE-1/packaged-sfx-detect-probe-results.json` + `raw/sp-l2-real-page.log` |
| AC2 SP-L1 合成页 frozen 冒烟 | 同上（内置合成页） | 同上 | PASS：EXIT=0，候选=4（conf_max=0.798），1846ms（含 DML 冷启动），同三键 dml/dml/null | `raw/sp-l1-synthetic.log` |
| AC2 SP-P0/SP-L3 | 第五入口+权重在位断言；installed core_service.exe stdio ping/shutdown | 同上 | PASS（ready/stopped，EXIT=0） | `raw/probe-runner.log` + `raw/sp-l3-core-service-ping.log` |
| AC3 GATE 25/25 | `TASK-012-py312/Scripts/python.exe packaging/m2ac5/run_clean_start_e2e.py` | installer sha256 `3ffa03f5…`（本 Task 包） | **PASS 25/25 EXIT=0**；M2-AC5/raw 落点按 GPU-EP-1 先例快照+`git checkout --` 还原（历史证据原样） | `raw/gate-clean-start-e2e.log` + `raw/m2ac5-gate-artifacts-thisrun/cleanstart-gate.json` |
| AC3 包体积 | Get-Item/Get-ChildItem 实测 | 33e824e4 构建 | NSIS 580,540,551 B / 553.65 MiB（+64.72 MiB vs GPU-EP-1 基线；主体=第五入口内嵌 PYZ 67.9 MB，与既有 ML/Qt 入口同形态） | `raw/bundle-sizes.log` |
| AC4 全量回归 | `T1.1.1-impl-py312/Scripts/python.exe -m pytest tests -q`（worktree 根） | 33e824e4 | **1835 passed + 1 skipped + 1 failed（test_catalog 既有 BASELINE_FAILURE）** = 基线 1823+新增 12 逐项吻合 | `raw/pytest-full-regression.log` |
| AC4 纪律 | `git diff --check`（range 口径）+禁改面专项 diff | 33e824e4 | range check：raw 证据 log 报 55 行 git 输出（27 trailing whitespace+1 blank-at-EOF，CRLF/EOF 忠实形态沿 GPU-EP-1 先例豁免）；排除 raw/** 后 EXIT=0；专项 diff 空 | `raw/r1fix/range-diff-check-*.log`（r1fix 补落盘） |
| r1fix 终态判据重跑 | 终态 runner（SP-L2 含三键在场判据）`python -B packaged-sfx-detect-probe.py --install-dir <GATE 安装态> --raw-subdir r1fix` | b4a9ad4d，安装态同 r0 | **PASS 4/4：frozen_in_process=true、weights_sha256_matches_pin=true、三键在场（含 sfx_ep_fallback 键判据）、conf=0.9046692252159119 与 r0 逐位一致、page_file_sha256=锚点 frame_sha256** | `packaged-sfx-detect-probe-results-r1fix.json` + `raw/r1fix/`（含 probe-runner.log） |
| 构建链闭包断言 | `build_sidecar.ps1 -Force`（HEAD=2b4e4946 绑定） | m2ac5-build venv，pyinstaller 6.22.3 | EXIT=0；断言 PASS ×2（core_service 8584 modules ML 全量面；**sfx_detect_probe 8455 modules——断言口径=onnxruntime 引擎在场，PYZ 实际含第二份 torch/transformers/doctr 闭包（DSH r1 P2-1 归属更正，机理=detection_doctr 函数体静态 import），见 deploy-record §3 取舍登记**） | `raw/build-sidecar.log` |
| 新增单测 | `pytest tests/core/test_sfx_detect_probe.py -q` | 33e824e4 | 12 passed | impl commit + 回归 log |

未运行/边界（如实登记）：本机无 wrapper CPU 回退形态可观测（GPU-EP-1 §1.3 回退矩阵不因此扩展；`sfx_ep_fallback` 在探针 JSON 为可观测字段，runner 如实登记不判失败）；真干净 Windows 覆盖仍属 M2 Release Gate（NOT_RUN，先例口径）；探针候选数为运行事实，不构成检测质量判定。

## 接收方式

- 分支 `agent/zcode/M2-PROD-SFX-PROBE-1`（worktree `G:/CODEX/New Manga.worktrees/M2-PROD-SFX-PROBE-1-zcode`），base=d298ecd0；r0 delivery_head=33e824e4，r1/r2 返修链见 Commit 链第 6/7 条（**分支 tip 为准**）。
- 复现探针：GATE（或 NSIS `/S /D=`）安装 `apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe`（sha256 `3ffa03f5…`）→ `"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" verification/M2-PROD-SFX-PROBE-1/packaged-sfx-detect-probe.py --install-dir <安装目录>`。
- 复现单测：`"G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" -m pytest tests/core/test_sfx_detect_probe.py -q`（worktree 根）。
- 前置：安装包/target 产物为 gitignored 构建物；fresh checkout 复现构建链按 `packaging/m2ac5/README.md`（frontend build → build_sidecar.ps1 → tauri build）。
- Reviewer（DSH）检查建议：①AC1 判定链（设计登记段的冻结粒度核实是否成立、第五入口是否确属 catalog_loader 先例形）；②探针 JSON 三键与 v2b 锚点 conf 对账；③GATE 落点快照/还原纪律；④spec 探针闭包断言是否可被静默放松。

## 下一任务建议（必填）

- Task ID / 标题：无需新建 Task——本 Task 进入 Review→集成轮收口；manga 检测器的对应 frozen 进程内证据缺口（PROD-DETECT-2 裁决⑥剩余 slice）仍待释放，未获授权不自行扩范围。
- 推荐 Agent / Reviewer：DeepSeek Harness（本 Task 非作者 Review）→ Codex 集成。
- 推荐原因与前置依赖：本 Task status=in_review，等 DSH 独立 Review 与 Codex 集成验证（GATE 证据已在包）。
- Recovery point：仓库 `G:/CODEX/New Manga`，worktree `G:/CODEX/New Manga.worktrees/M2-PROD-SFX-PROBE-1-zcode`，branch `agent/zcode/M2-PROD-SFX-PROBE-1`，base=d298ecd0 / head=分支 tip（r0=33e824e4，返修链见 Commit 链）。
- 允许修改路径（Review 返修时）：同本 Task 允许面（`packaging/m2ac5/**`、`src/bootstrap/sfx_detect_probe.py`、`tests/core/test_sfx_detect_probe.py`、`verification/M2-PROD-SFX-PROBE-1/**`、本 Task 文档/Handoff）。
- 禁止范围与新增授权条件：`contracts/**` 既有语义、`apps/desktop/src-tauri/**`、`doc/STATUS.md`/`doc/REBASELINE_PLAN.md`、GATE runner 场景集——维持零 diff；任何契约修订须按 AC1③ 由 Codex 立草案。
- 交付物：见「验证证据」表路径。
- 验证命令、环境与完成 Gate：同「接收方式」；完成 Gate=DSH Review 通过 + Codex 集成验证 + STATUS 收口。
- 可直接转发给 Agent 的指令（DSH Review）：
  > Review M2-PROD-SFX-PROBE-1（非作者）：worktree `G:/CODEX/New Manga.worktrees/M2-PROD-SFX-PROBE-1-zcode`，branch `agent/zcode/M2-PROD-SFX-PROBE-1`，head=33e824e4。按 Task 合同 AC1-AC5 审 `doc/tasks/M2-PROD-SFX-PROBE-1.md`（设计登记+交付回填）、`verification/M2-PROD-SFX-PROBE-1/deploy-record.md` 与 `packaged-sfx-detect-probe-results.json`；重点核 AC1 additive 判定链（第五 frozen 入口 vs M2-C1/M2-IPC1 冻结粒度）、AC2 三键实测（device=dml/sfx_ep=dml/fallback=null，conf 0.9047 与 `experiments/M2-SFX-T4-SWITCH/v2b-k07-r123-anchor.json` 对账）、GATE 25/25 与 M2-AC5/raw 快照还原纪律、回归 1835+1sk+1failed 与基线核算。产出 Review 文档按模板落 `doc/reviews/`。

## 风险与遗留

- 包体积 +64.72 MiB（**DSH r1 P2-1 归属更正**：主体=第五入口内嵌 PYZ 复用生产 provider import 闭包的代价，且该闭包含第二份 torch/transformers/doctr 链——`detection_doctr` 函数体静态 import 被 modulegraph 跟进，非 onnxruntime 面；**取舍登记（DSH r1 P2-2 三选一，集成裁决选 (a)）**：(a) 接受（零产品风险、回退=revert spec 第五行+sanity gate 行）；(b) core_service.exe 一次性 CLI 模式（0 B）被拒——分叉产品主入口启动行为；(c) 瘦身探针 import 面/共享 PYZ 属产品 src 重构，留后续 slice）。
- `apps/desktop/src-tauri/src/main.rs:378-379` 注释列举 sidecar exe 名单仍为四个（纯注释、无功能引用；本 Task 保持 src-tauri 零 diff，留集成轮裁量是否顺带更新）。
- 探针权重解析在非 frozen dev 形态拒绝猜测数据根（诚实配置错误）；`--weights`/`NEWMANGA_SFX_WEIGHTS` 通道可用。
- K07_R123 锚点页与 v2b 权重在 gitignored task-envs 树（`M2-DOCTR-QUAL-work/regions/`、`M2-SFX-DETECT/weights-v2b/`）；其他机器复现 SP-L2 需本地放置并在 runner 用 `--real-page` 指向（缺失=SKIP/NOT_RUN，不判失败）。
