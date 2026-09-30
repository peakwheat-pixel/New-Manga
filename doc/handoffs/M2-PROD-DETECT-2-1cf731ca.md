---
task_id: M2-PROD-DETECT-2
author: ZCode
recipient: Codex（integrator）；reviewer=DeepSeek Harness（非作者）
base_commit: f79203eb
delivery_head: 1cf731ca
status: delivered_for_review
---

# Handoff：M2-PROD-DETECT-2（发布形态检测器运行时/权重分发）

## 交付结果

发布形态（NSIS 安装包）的 detect 链路真正可用：ML 运行时进 PyInstaller sidecar 闭包、manga 权重随包分发、装配段支持包内权重回退查找。与 AC 逐项对照（详见 `verification/M2-PROD-DETECT-2/release-notes.md`）：

- **AC1 构建链**：`packaging/m2ac5/requirements-build.txt` 翻转为「packager + runtime closure」（ML 五行与主 requirements 逐字一致，头注释登记裁决 2）；`core_sidecar.spec` EXCLUDED 撤 torch/torchvision/doctr（pandas/build-tooling 保持，`console=True` FROZEN 未触碰）；**hiddenimports 零新增**——PyInstaller 经函数内 lazy import 跟踪 + PYZ 归档已覆盖 transformers/doctr（最大风险点未发生）；构建 exit=0，warn 13 个 missing 全为平台条件性/可选噪音、0 ML 相关。
- **AC2 权重随包**：`build_sidecar.ps1` 新增 `Copy-MangaWeights`（逐文件 SHA-256 校验后复制、失败即 throw、`-SkipWeights` 调试开关、幂等短路路径也校验）；onedir 与 NSIS 安装后三文件哈希均与 `detection_manga.py` pin 一致；tauri.conf.json 零改动；权重零入库。
- **AC3 包内回退解析**：`src/bootstrap/core_assembly.py` 新增模块级 `_resolve_detector_weights_path(..., *, bundled_in_release)`，manga/doctr 两分支共用；查找顺序=env override（原样）> data root 探测 > frozen 包内探测 > 默认 data root 路径；**frozen+manga 全缺=装配时 fail-closed 列全部候选**（安装损坏语义），**frozen+doctr 全缺=设计内状态不 raise**（保持 detect 时 NOT_CONFIGURED，裁决 3），**非 frozen 逐字节零变化**（既有测试锁死行为未动）。新增 11 测。
- **AC4 GATE**：25/25 PASS（新 onedir + 新 NSIS）；体积 onedir 99,308,142B/161 文件 → **1,116,380,855B/5,550 文件**、NSIS 27,924,371B → **460,184,382B（438.9 MiB）**、构建时长 onedir 278s + tauri ≈6min；M2-AC5 raw 6 文件按先例 `git checkout --` 还原。
- **AC5 发布形态探针**：5/5 PASS——frozen 启动 ping EXIT=0；包内权重反证（移走→启动 exit=1 含 probed candidates→还原恢复）；**真实 manga 推理 EXIT=0、text 候选=2、稳态 299ms/页**（冷启动 6,542ms 含加载；ML 版本逐字一致）；docTR frozen 正常启动（fail-closed 留在 detect 时）。**边界：frozen 命令面（M2-IPC1）无 detect RPC，推理在 frozen 闭包外以同源 ML 栈 + 安装后包内权重执行**；frozen 闭包完整性由 L1 启动 + warn 零 ML missing + PYZ 归档清单三重背书。
- **AC6 回归**：pytest providers 286+1（既有环境性失败保持）/m2_acceptance 35/core 77（387+1 口径 +11 新增）；cargo 44+1 ignored；vitest 31；`git diff --check` 双 EXIT=0；禁改面专项 diff 为空。
- **AC7**：本 Handoff + Task 测试表/AC 勾选回填。

提交列表（branch `agent/zcode/M2-PROD-DETECT-2`，未 push）：
- `44e70f66` claim（status ready→in_progress）
- `1cf731ca` implement（全部实现 + 测试 + verification 证据 + Task 回填）
- handoff commit（本文件 + Task frontmatter `delivery_head`）

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 构建 | `pip install -r packaging/m2ac5/requirements-build.txt`（代理）→ `build_sidecar.ps1 -Force` | build venv m2ac5-build @1cf731ca | PASS（exit=0，onedir 278s） | verification/M2-PROD-DETECT-2/raw/build-sidecar-console.log |
| AC1 warn 面 | 读 `pyinstaller-work/core_sidecar/warn*.txt` | 同上 | PASS（13 missing 全平台噪音、0 ML） | 同上（分析结论在 release-notes.md） |
| AC1 PYZ 归档 | `pyi-archive_viewer -r -l core_service.exe` | 同上 | PASS（doctr 全树 + transformers 2320 条目在 PYZ） | release-notes.md §AC1 |
| AC2 权重 | sha256sum onedir 与安装后目录三文件 | @1cf731ca | PASS（与 pin 一致） | release-notes.md §AC2 |
| AC3 单测 | `pytest tests/providers/test_detector_weights_lookup.py`（主 venv，PYTHONPATH=src） | @1cf731ca | PASS 11/11 | 本表 |
| AC3 既有面 | `pytest test_detector_assembly.py test_detection_manga.py test_provider_fail_closed.py` | 同上 | PASS 37 | 本表 |
| AC4 GATE | `run_clean_start_e2e.py`（主 venv） | NSIS sha256 6c765ed3… @1cf731ca | **PASS 25/25** | verification/M2-PROD-DETECT-2/raw/cleanstart-runner-stdout.log |
| AC4 M2-AC5 raw 还原 | `git checkout -- verification/M2-AC5/raw/` | @1cf731ca | PASS（专项 diff 为空） | git status |
| AC5 探针 | `packaged-detect-probe.py --install-dir %TEMP%/m2ac5-cleanstart/install` | 同上 | **PASS 5/5** | packaged-detect-probe-results.json + raw/l1/l2/l3/l4*.log |
| AC6 pytest | providers / m2_acceptance / core（主 venv） | @1cf731ca | 286+1 / 35 / 77 | 本表 |
| AC6 cargo | `cargo test`（apps/desktop/src-tauri） | @1cf731ca | 44 passed + 1 ignored | 本表 |
| AC6 vitest | `npm test`（frontend） | @1cf731ca | 31 passed | 本表 |
| AC6 纪律 | `git diff --check`（f79203eb..HEAD 与工作区）+ 禁改面专项 diff + `git ls-files` 权重核查 | @1cf731ca | 双 EXIT=0；禁改面空；权重零 tracked | 本表 |

未运行项与原因：真干净 Windows 机器覆盖属 M2 Release Gate（口径冻结 NOT_RUN，同 M2-AC5）；frozen 进程内推理不可运行——M2-IPC1 命令面无 detect RPC（见 AC5 边界），不伪造。

## 四条代理裁决的落地与撤销方式

| 裁决 | 落地 | 撤销方式 |
|---|---|---|
| 1 安装包体积（438.9 MiB 可接受） | onedir/NSIS 体积如实记录 | revert `core_sidecar.spec` + `requirements-build.txt` 两文件改动（build venv 同步删 ML 行）即回 26.63 MiB 轻量包，detect 回 DEPENDENCY_MISSING（同 M2-PROD-DETECT-1 交付态） |
| 2 build venv 定位翻转 | requirements-build.txt 头注释登记 + ML 五行逐字一致 | 同上（同一 revert） |
| 3 只带 manga 权重 | ps1 只复制 manga 三文件；doctr frozen 全缺不 raise（NOT_CONFIGURED 留在 detect 时） | 把 doctr 三处装配/查找语义改回「frozen 也 fail-fast」并扩展 ps1 复制 doctr 快照即可（代码层一个 `bundled_in_release=True` 参数） |
| 4 权重查找顺序 | `_resolve_detector_weights_path` 单一函数实现 | revert `core_assembly.py` 装配段即回 env>默认路径（非 frozen 语义本就零变化） |

## 接收方式

- 分支 `agent/zcode/M2-PROD-DETECT-2`（worktree `G:/CODEX/New Manga.worktrees/M2-PROD-DETECT-2-zcode`，base=f79203eb），未 push、未 merge。
- 复现构建：`powershell -NoProfile -ExecutionPolicy Bypass -File packaging/m2ac5/build_sidecar.ps1 -Force` → `cd apps/desktop/src-tauri && npx --yes @tauri-apps/cli@2 build` → `python packaging/m2ac5/run_clean_start_e2e.py` → `python verification/M2-PROD-DETECT-2/packaged-detect-probe.py --install-dir %TEMP%/m2ac5-cleanstart/install`。
- 前置条件：build venv 已含 ML 栈（本 Task 已装好，fresh 重建则 `pip install -r packaging/m2ac5/requirements-build.txt`，代理 `http://127.0.0.1:7890`）；权重快照在 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/...`（repo 外）。
- Reviewer 检查建议：①warn 文件 13 个 missing 逐一确认平台噪音属性；②`_resolve_detector_weights_path` 的 `bundled_in_release` 分叉语义 vs 裁决 3/4 自洽性；③L3 探针「frozen 闭包外推理」边界的可接受性（AC5 字面 vs M2-IPC1 冻结的冲突处理）；④tauri build 重写的 gen/schemas 与 permissions/autogenerated 已 `git checkout --` 还原。

## 下一任务建议（必填）

- Task ID / 标题：无需新立 Task——本 Task 进入 DSH review（r1）；review 通过后由 Codex 集成（integration + master merge）。
- 推荐 Agent / Reviewer：DeepSeek Harness（非作者 review）；集成=编排会话代行 Codex。
- 推荐原因与前置依赖：契约 `reviewer: DeepSeek Harness（非作者）`；M2-PROD-DETECT-1 已 done @056617e4，本 Task 只依赖其集成态。
- Recovery point：仓库 `G:/CODEX/New Manga`，branch/worktree `agent/zcode/M2-PROD-DETECT-2`（`G:/CODEX/New Manga.worktrees/M2-PROD-DETECT-2-zcode`），base `f79203eb`，delivery_head `1cf731ca`（worktree 已存在）。
- 允许修改路径（review-fix 范围）：`packaging/m2ac5/{core_sidecar.spec,requirements-build.txt,build_sidecar.ps1,README.md}`、`src/bootstrap/core_assembly.py`（仅权重解析段）、`tests/providers/test_detector_weights_lookup.py`、`doc/tasks/M2-PROD-DETECT-2.md`、`doc/handoffs/M2-PROD-DETECT-2-*.md`、`verification/M2-PROD-DETECT-2/**`。
- 禁止范围与新增授权条件：`apps/**`、`tauri.conf.json`、`run_clean_start_e2e.py`、`ports/**`、两个 detection provider、`requirements.txt`、`experiments/**`；spec `console=True` FROZEN；权重/模型文件永不入库；如需扩 core_service 命令面（detect RPC）须 Codex 先立契约范围。
- 交付物：review 报告入 `verification/M2-PROD-DETECT-2/`（照 M2-PROD-DETECT-1 r1/r2 先例）。
- 验证命令、环境与完成 Gate：上表「接收方式」四条命令全绿（GATE 25/25 + 探针 5/5 + 三套件口径 + diff --check EXIT=0）。
- 可直接转发给 Agent 的指令：`「你是 DSH reviewer（非作者）。在 worktree G:/CODEX/New Manga.worktrees/M2-PROD-DETECT-2-zcode（branch agent/zcode/M2-PROD-DETECT-2，base f79203eb，head 1cf731ca）审 M2-PROD-DETECT-2：先读 doc/tasks/M2-PROD-DETECT-2.md 契约与 verification/M2-PROD-DETECT-2/release-notes.md，重点核查①warn 面判定②bundled_in_release 语义分叉③AC5 探针边界（frozen 闭包外推理）④体积/回归证据真实性；复跑四条验证命令；报告写入 verification/M2-PROD-DETECT-2/review-r1-dsh.md。禁改面见 Task。」`

## 风险与遗留

- **已知限制**：①docTR 权重不进包（裁决 3；发布形态切回=fail-closed NOT_CONFIGURED+指引，data root 放权重或 env 可启用）；②权重随包冻结（换权重=重装或 data root 覆盖，无 UI）；③无 UI 权重管理；④build venv 传递依赖（opencv/scipy/shapely/h5py/onnx/pypdfium2 由 pip 解析带入闭包，pypdfium2 与主 requirements 同为 5.13.0；mobi 仍不进）；⑤frozen 进程内无 detect RPC（AC5 边界）。
- **用户选择点**：安装包 26.63 MiB → 438.9 MiB（裁决 1，可撤销）；四条裁决均可逆（见撤销表）。
- **破坏性操作**：无（无迁移、无宿主 %APPDATA% 写入——GATE CS-Z4 字节不变 PASS）。
- **关联**：M2-PROD-DETECT-1（done @056617e4，provider 与 backend 选择）；M2-DOCTR-QUAL-C4（权重快照来源）；M2-RG1（console=True 冻结源）。
- 回退方法：见裁决撤销表；整 Task 回退 = `git revert` 三个 commit 或 branch 删除。
