# P03 非作者正式 Review 指令

你是 P03 的正式非作者 Reviewer：DeepSeek Harness。作者为 Antigravity，Integrator 为 Codex。请只读审查，不改任何生产实现、测试、Task、Handoff、Plan、Status、RESUME 或其他文件；唯一允许新增/修改的文件是你自己的 Review 报告：

`doc/reviews/P03-PACKAGED-SFX-ENTRY-6d84b480-dsh.md`

## 固定范围

- Task base / Review base：`31abde9bf4b73aea2851931dcd48faa0f750b318`
- 固定 reviewed HEAD：`6d84b480d5996d6374192bbbba07807848b8ebde`
- Owner 开工 HEAD：`0a31bbc52447b87a3f04145df62a5ad19baa4b44`
- Build source HEAD：`51f6b10c9621c07d5ad7087918d1b904106f0218`
- Fresh NSIS installer SHA-256：`af25a4b7230cf0f9d64c2509f541fe7124112cf188a00d473d7ef4455c551ada`
- Owner branch：`agent/antigravity/P03-packaged-sfx-entry`
- 当前 Reviewer 工作区为从固定 reviewed HEAD 派生的独立 linked worktree；Git common dir 必须是 `G:/CODEX/New Manga/.git`。

Codex 在正式释放期间先提交了 Task / Plan / Status / 索引 / 路线图元数据（release commit `ece8765461ce19f7493ce636ff7d69ae6a3e1c4b`，同步检查点 `0a31bbc52447b87a3f04145df62a5ad19baa4b44`）。这些是 Owner 开工前的控制面状态，不属于 Antigravity 的实现差量。请同时检查固定 Review 全范围 `31abde9..6d84b48`，并以 `0a31bbc..6d84b48` 隔离归属 Owner 的交付差量；不要把 Codex 预先释放的状态文档误判为 Owner 越界修改。

## 必读事实来源

- `AGENTS.md`
- `doc/09_COLLABORATION.md`
- `doc/REBASELINE_PLAN.md`、`doc/STATUS.md`
- `doc/tasks/P03.md`、`doc/handoffs/P03-PACKAGED-SFX-ENTRY-51f6b10c.md`
- `doc/templates/REVIEW.md`
- `packaging/m2ac5/run_clean_start_e2e.py`
- `tests/packaging/test_packaged_fifth_sfx_entry.py`
- `tests/packaging/test_runner_output_dir_required.py`
- `src/bootstrap/sfx_detect_probe.py` 及相关打包清单 / runner 调用点
- `verification/P03-PACKAGED-SFX-ENTRY/build-manifest.json`、`build-logs/**`、`run-51f6b10c/**`

## 审查重点

1. `sfx_detect_probe.exe` 是否进入 NSIS 安装存在清单和最终 sidecar survivor 零存活断言；判断是否有调用方、路径或清理分支遗漏。
2. `--sfx-real-page` opt-in 的输入校验、安装程序定位、隔离输出目录、进程启动、stdout/stderr/exit 捕获和单条 JSON marker 解析是否在错误输入、命令失败、多 marker、畸形 JSON、缺失权重、零候选、fallback 等情况下安全且 fail-closed。
3. 正向场景是否验证 frozen runtime、候选数大于零、pinned weights SHA；fallback/device/provider 信息是否完整且原样记录。负向缺页是否保证隔离路径确实不存在并检查 frozen runtime 和非空结构化错误。
4. 新定向测试是否覆盖风险逻辑，并保留原 `--output-dir` 必填及防历史 raw 覆盖行为。
5. Build source HEAD、installer SHA、运行 Gate 的 installer SHA 是否严格一致；K07 / weights 外部哈希和每项命令证据是否可复核，EXIT / shell / Python 版本是否完整，失败或警告是否被如实记录。
6. Owner 差量 `0a31bbc..6d84b48` 是否只触及 P03 授权路径；`src/**`、`apps/**`、contracts、Schema、依赖、spec/script 和历史 raw 应零修改。`git diff --check 31abde9..6d84b48` 应通过。
7. Architecture 与 Verification 两面都给出结论。逐项核对 P03 AC；发现项按严重级别列出文件/行、触发条件、影响、复现和最小修复。明确未覆盖的风险与 NOT_RUN/BLOCKED 项。

可尝试运行相关检查，但不要声称未亲自执行的测试通过；若 DSH 的 Windows ACL 或环境禁止运行，逐项标成 `NOT_RUN` 并说明错误。请按 Review 模板写入上述唯一报告文件，固定 `base_commit` 与 `reviewed_head`，给出 `approved` / `changes_requested` / `blocked` 决定、P0/P1 未解决数和明确审查范围。禁止改实现、测试或其他文件。
