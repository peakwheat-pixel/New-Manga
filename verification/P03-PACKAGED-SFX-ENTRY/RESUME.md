# P03 恢复点

时间：2026-10-09（Asia/Shanghai）；Task=`P03`；TaskStatus=`in_review`；ExecutionState=`CHECKPOINTED`。
build source HEAD=`51f6b10c9621c07d5ad7087918d1b904106f0218`；
NSIS installer SHA-256=`af25a4b7230cf0f9d64c2509f541fe7124112cf188a00d473d7ef4455c551ada`；
Packaged Gate=`PASS`（全量既有场景 + CS-S1 real-page + CS-S2 missing-page 全部通过）。

## 固定状态

- 仓库：`G:/CODEX/New Manga`；Task代码base=`31abde9bf4b73aea2851931dcd48faa0f750b318`；release metadata commit=`ece8765461ce19f7493ce636ff7d69ae6a3e1c4b`；branch=`agent/antigravity/P03-packaged-sfx-entry`；worktree=`G:/CODEX/New Manga.worktrees/P03-packaged-sfx-entry-antigravity`；common-dir=`G:/CODEX/New Manga/.git`。
- Owner=`Antigravity`；非作者 Reviewer=`DeepSeek Harness`；Integrator=`Codex`。
- 依赖项：`M2-PROD-SFX-PROBE-1`、`M2-RUNNER-SNAPSHOT-DEBT`、`M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD` 均已完成。
- K07 anchor page SHA-256=`28dab503aca3c903111488c03e857b430d309421a4a54bab335a63bbe7b9cec4`（实测匹配，1,020,887 bytes）；pinned v2b SFX weights SHA-256=`944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d`（实测匹配，40,824,255 bytes）。
- P03 fresh source HEAD=`51f6b10c9621c07d5ad7087918d1b904106f0218`；fresh NSIS installer path=`apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe`；installer SHA-256=`af25a4b7230cf0f9d64c2509f541fe7124112cf188a00d473d7ef4455c551ada`，大小 579,539,399 bytes。Gate JSON 内记录的 installer SHA 与此完全一致。

## 已确认事实与保护集合

- `packaging/m2ac5/run_clean_start_e2e.py` 的 `SIDECAR_EXES` 与终态进程存活清零断言已纳入第五入口 `sfx_detect_probe.exe`。
- opt-in `--sfx-real-page` 在同一份新安装包下成功执行了正向（K07 真实页面）和负向（隔离缺失路径）对照，且结构化结果并入 Gate：
  - 正向 CS-S1：exit 0，恰有一条 `SFX_PROBE_JSON: `，`python.frozen=true`，`error=null`，`n_candidates=1`，weights SHA 与 pin 吻合，DirectML 执行（`device=dml`, `sfx_ep=dml`, `sfx_ep_fallback=null`）。
  - 负向 CS-S2：exit 1，恰有一条 `SFX_PROBE_JSON: `，`python.frozen=true`，结构化 `error`（FileNotFoundError）。
- 定向测试 `tests/packaging/test_packaged_fifth_sfx_entry.py`（28 passed）与 `tests/packaging/test_runner_output_dir_required.py` 覆盖清单存在、清理断言、判别逻辑及参数解析。
- 主 checkout 既有未提交内容原样保留；`src/**`、`apps/**`、contracts、Schema、依赖、spec/script 零修改；历史 raw 零修改。

## 当前步骤与下一条直接指令

1. 提交所有验证证据、测试日志、Handoff 及任务状态文档，固定 delivery/review HEAD。
2. 将任务交接给非作者 Reviewer `DeepSeek Harness`，按协作协议 §6 进行独立 Review。
3. Reviewer 批准且无未解决 P0/P1 后，由 Codex 执行集成验证。

## 已运行 / 未运行 / 阻塞

- 已运行：
  - 开工核验与外部输入 SHA-256 校验：PASS
  - 定向单元测试 `test_packaged_fifth_sfx_entry.py` + `test_runner_output_dir_required.py`（28 passed in 0.50s）：PASS
  - 快照护栏 `check_snapshots.py`（16 cases）：PASS
  - 前端构建 `npm ci` + `npm run build`：PASS
  - Sidecar 构建 `build_sidecar.ps1 -Force`：PASS
  - Tauri NSIS 打包：PASS
  - Packaged Clean-Start E2E Gate（完整场景 + CS-S1 + CS-S2，GATE: PASS，EXIT 0）：PASS
- 未运行：
  - 全新纯净 Windows 物理机安装验证（属于 M2 最终发布 Gate 范围，非本机 host simulation 范围）：NOT_RUN
  - 非作者独立 Review：待 DSH 执行
  - 主线集成：待 Codex 执行
- 当前已知产品决策阻塞：无。
