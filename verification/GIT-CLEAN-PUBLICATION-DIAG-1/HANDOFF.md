---
task_id: GIT-CLEAN-PUBLICATION-DIAG-1
author: Codex
recipient: DeepSeek Harness
base_commit: e34a90d001cce1fa966aec7d2b032bb5ad1cf148
delivery_head: fed1a9cf3295e5e05f7ffd363ac1075bd22e90b1
status: ready_for_review
---

# Handoff：GIT-CLEAN-PUBLICATION-DIAG-1

## 交付结果

诊断 head 仅两文件：sandbox.py 保留失败异常的 returncode/stderr，新增两个 mock 测试；生产 registry 未改。默认并发复现、四个单进程对照、三 DB SOURCE_PIN、62文件补包、19个历史 EXIT envelope、12项 packaged 证据另按本 Task SHA 表冻结。AC1/2/4 由 Owner 标 MET；AC3 PARTIAL：旧日志未采集环境不可补造，待独审裁定。所有结果详见 RESULT.md，不是独立批准。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 | cargo test --locked --offline -- --skip packaged_sidecar_tests:: | 隔离副本，e34；unset RUST_TEST_THREADS | 151 passed/2 failed/1 ignored/12 filtered，exit101 | workspace本Task/rust-default-parallel-r2.log/json |
| AC1 对照 | 4个registry测试分别 --exact --nocapture | 每次独立进程，同一Rust源码 | 各1 passed/exit0；非全套通过 | registry-isolated-1至4.log/json |
| AC2 | SQLite immutable只读冻结副本；_grant mock pytest | DB来自r2；mock固定fed | 3库plugin_error；mock2 passed | core-r2-source-pins.json；grant-mock-fixed-head.log/json |
| AC3 | freeze_review.py verify；pytest test_evidence_helpers.py | 补包SHA与负向自检 | 62文件一致；3 passed | review-package-r2/PACKAGE_MANIFEST.json；evidence-helper-tests.log |
| AC4 | 新build_sidecar.ps1 -SkipWeights；先冻结再 cargo test --locked --offline packaged_sidecar_tests:: -- --nocapture | 独立packaged-source/e34；Python3.12.3/PyInstaller6.22.3；unset源码解释器路径 | 最终12 passed/0 failed/154 filtered，exit0；6614文件/1121604514 bytes前后hash不变 | packaged-sidecar-frozen.json；packaged-tests-fixed-head.log/json；packaged-final-postcheck.json |

## 接收方式

诊断仓库为 workspace/task-envs/GIT-CLEAN-PUBLICATION-DIAG-1/source，branch codex/git-clean-publication-diag-1；父候选在父Task的source-export-r4，仍e34。二者无远端。SOURCE_PIN 与完整 argv/env/cwd/exit 在 Canonical Evidence；所有证据本地保留，不随源码发布。唯一源码补丁不可直接当父候选升级或 main 集成。

## 下一任务建议（必填）

本 Task 尚未关闭；下一安全动作是 **执行本 Task 的新独立 Review**，不预释放未知范围的产品修复。

- Task：GIT-CLEAN-PUBLICATION-DIAG-1 Review。
- Agent：DeepSeek Harness；作者Codex，不得自审。
- Recovery/base/head、scope、唯一写路径、交付物、验证与可直接转发指令：本目录 [APPOINTMENT.md](APPOINTMENT.md)，状态APPOINTED_PENDING_EXECUTION。
- Gate：核对精确fed head、SOURCE_PIN与所有失败披露，独立decision后Codex再裁定后续测试隔离/压力验证或Core新环境诊断；不push、不done、不改源main/系统ACL。若新head变化，另行Appointment。

## 风险与遗留

真实产品并发饱和安全未证明，Core旧icacls真实错误码UNKNOWN；mock错误码不是历史事实。旧log环境不完整。首个packaged尝试的head字段取错仓库，原日志保留并附source-head probe；已修正运行器并对同一冻结bundle补跑12项，最终记录绑定e34。无模型、安装包、真实GUI或全产品审计。父r1 blocked保持；资源全部保留，closeout pending。

## 实验附录

只用源仓固定源码、自制夹具与本机现有依赖；不复制169张私有漫画或其338对象，不下载模型、不调用远程API。-SkipWeights明确无模型Gate。三库是pytest临时数据库，不是真实用户库。构建工具版本、解释器SHA、733个输入SHA、6614个输出SHA及每次环境均见机器pins。
