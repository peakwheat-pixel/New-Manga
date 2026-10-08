# Antigravity Owner 续接指令：P03 Review Findings 修订

这是已授权 P03 Task 的续接，不是新产品范围。请继续在 linked worktree `G:/CODEX/New Manga.worktrees/P03-packaged-sfx-entry-antigravity`、branch `agent/antigravity/P03-packaged-sfx-entry` 工作。先核对 common dir=`G:/CODEX/New Manga/.git`、当前 HEAD=`6d84b480d5996d6374192bbbba07807848b8ebde`、状态与未提交文件；保留 `verification/P03-PACKAGED-SFX-ENTRY/antigravity-dispatch.json` 和 `.stderr.log` 原样，不覆盖或删除。

初轮 DSH Review 已对 base=`31abde9bf4b73aea2851931dcd48faa0f750b318`、reviewed_head=`6d84b480d5996d6374192bbbba07807848b8ebde` 正式 `approved`，报告位于 `G:/CODEX/New Manga.worktrees/P03-dsh-review-6d84b48/doc/reviews/P03-PACKAGED-SFX-ENTRY-6d84b480-dsh.md`，session=`session-c52e715d-8f4b-4aa8-98bb-48e71e1f5317`。DSH 复跑 Git/Python/pytest/Gate 为 `NOT_RUN`（`SetNamedSecurityInfoW failed (Win32 5)`）；不要把其静态 Review 写成执行通过。Codex 已决定在集成前修复以下轻量但影响验收可信度的 findings，之后对新固定 head 进行 DSH 复审。

## 只允许写入

- `packaging/m2ac5/run_clean_start_e2e.py`
- `tests/packaging/test_packaged_fifth_sfx_entry.py`
- `verification/P03-PACKAGED-SFX-ENTRY/**`
- `doc/tasks/P03.md`
- 新的 `doc/handoffs/P03-PACKAGED-SFX-ENTRY-<new-code-head8>-r1.md`

不得改 `src/**`、`apps/**`、contracts、Schema、依赖、`core_sidecar.spec`、`build_sidecar.ps1`、requirements、既有测试行为、全局 Plan/Status/索引/路线图或旧 raw。不要改写首轮 `build-logs/**`、`build-manifest.json`、`run-51f6b10c/**`、旧 Handoff 或旧 Review；全部第二轮证据使用 `verification/P03-PACKAGED-SFX-ENTRY/revision-2/**` 新路径。构建若改写任何 `apps/**` 自动生成文件，先与本轮开始时的 Git 状态核对，只恢复能证明是此次构建生成的文件，不能覆盖其他改动。

## 修复目标

1. **R-001（P2，权重来源）**：SFX probe 子进程环境必须屏蔽 `NEWMANGA_SFX_WEIGHTS` 覆盖；正向判据还需明确验证 JSON 的 `weights.resolved_from == "bundle_probe"`，权重路径位于本次安装目录内，且 SHA 匹配 pin。把来源和路径写入 observed。加入一个测试证明外部 env 权重不能替代 bundle 权重。
2. **R-002 / R-010（P2/P4，K07 输入）**：把 K07 文件级 SHA-256 pin `28dab503aca3c903111488c03e857b430d309421a4a54bab335a63bbe7b9cec4` 纳入 SFX 正向 Gate。运行前对真实文件按字节求 hash；缺失或不匹配时记录结构化 FAIL、不执行 probe；匹配时在 observed 记录 `page_file_sha256`。probe JSON 的 `page.sha256` 是 RGB24 像素域 hash，须与文件级 hash 分开命名。为本轮 K07 与 weights pin 预检保存带 PowerShell 版本、完整命令、路径、bytes、实际/预期 SHA、匹配结果和 `EXIT=0` 的 `revision-2/00-input-preflight.log`；在测试/build 开始前实际执行并核验。
3. **R-003（P2，真实清理断言测试）**：让 `SIDECAR_EXES` 成为唯一第五入口清单来源；安装存在断言、survivor 采样名与零存活判定均基于它。提取最小的真实判定函数并让 pytest 直接调用；测试必须在删除 `sfx_detect_probe.exe` 的生产 survivor 判据时失败，不要在测试中重新手抄相同布尔表达式。
4. **R-004（P2，错误工具版本）**：第二轮 manifest 和新 Handoff 只记录本轮构建日志实测值：Node `v24.15.0`、npm `12.0.1`、Rust/Cargo `1.98.1`；Python build `3.12.3`、PyInstaller `6.22.3`，其余以本轮实际版本日志为准。把 npm deprecated / blocked `esbuild` install script 与 6 条 Rust warnings 的数量和性质如实记入 Handoff；不改旧 manifest/Handoff。
5. **R-005 / R-007（P3，解析边界）**：JSON marker 的有效 JSON 若顶层不是 object，应返回结构化判 FAIL，而不是抛 `AttributeError`；`n_candidates` 必须是严格的 JSON integer（布尔值 `true` 与浮点数都拒绝）。成功判据必须确认 `error` key 存在且值为 null。为这些边界加入可区分的负向测试。
6. **R-006（P3，missing-page 前置）**：缺失页场景启动前实际检查该隔离路径不存在；不满足时直接结构化 FAIL、不运行 probe，并在 Gate observed 记录 `path_precondition: absent`。
7. **R-008（P3，复核 artefact）**：保存本轮 `git diff --check` 完整日志（shell/命令/EXIT），并在新 Handoff 记录其 artifact 路径。上述 warnings 也按 R-004 处理。
8. **R-009（P3，opt-in 可见性）**：结构化 Gate 输出要能区分未请求 `--sfx-real-page` 与请求并执行了 CS-S1/CS-S2；不传参数时仍维持兼容的 opt-in 行为，但不得让审核者把普通 clean-start PASS 误读为 SFX 场景已运行。

请以最小改动处理以上问题，尤其复用仓库现有 hash / Gate / 环境清理模式；不要增加依赖或重做既有 clean-start 流程。

## 第二轮验证与交付

1. 将 Task 从 `in_review` 记录为 `changes_requested` 后恢复实现；更新 Task-local `RESUME.md`，记录本轮实际起点、未提交 dispatch evidence、当前 HEAD 和确切下一步。
2. 在**干净的代码提交 HEAD** 上先保存 00-input-preflight，然后运行定向 pytest（`test_packaged_fifth_sfx_entry.py` + `test_runner_output_dir_required.py`）及 `check_snapshots.py`。
3. 在新代码 HEAD 上重新执行 `npm ci --no-audit --no-fund`、`npm run build`、`build_sidecar.ps1 -Force`、`npx --yes @tauri-apps/cli@2 build`。这是更新后的 Gate 源码；不可复用首轮 51f6 installer 来声称 source/installer 同一修订。
4. 在 Gate 前写入第二轮 `build-manifest.json`，记录完整 build source HEAD、fresh NSIS 路径/bytes/SHA-256、工具实测版本、K07 和 weights 输入 pin。随后以该安装器跑完整 clean-start Gate + `--sfx-real-page`，输出到全新 `revision-2/run-<new-code-head8>/`。Gate SHA 必须与 manifest 一致，CS-S1/S2 与所有既有场景通过。完整 stdout/stderr/EXIT 保存在 `revision-2/build-logs/**`。
5. 固定新 code HEAD，再追加新的 Handoff 文档提交；Handoff 明确区分 build source HEAD 与 delivery/review HEAD，逐条 disposition R-001..R-010，并列出仍未运行的真机/GUI等事项。更新 Task AC、状态与 RESUME 为 `in_review`，不得自行 Review、集成或宣称 `done`。
6. 保存 `git diff --name-only 0a31bbc52447b87a3f04145df62a5ad19baa4b44..<new-delivery-head>` 与 `git diff --check 31abde9bf4b73aea2851931dcd48faa0f750b318..<new-delivery-head>` 的完整输出、shell、命令和 EXIT；Owner 差量只准落在以上 allowed paths。提交固定后告知 Codex 新 code HEAD、delivery HEAD、revision-2 installer SHA、Handoff、测试/Gate 日志、未解发现与状态。

不要 push、部署或清理其他 worktree。遇到真实外部输入 hash 漂移时按 BLOCKED 记录并停止相应构建/Gate，不找其他文件替代。
