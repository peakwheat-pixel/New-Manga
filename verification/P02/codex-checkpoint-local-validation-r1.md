# P02 本机验证裁决与恢复点

## 记录

- 时间：2026-10-10（Asia/Shanghai）；记录者：Codex。
- 依据：用户明确裁决本项目 Windows Sandbox Feature 验证改为本机 Windows 验证；本机验证按项目验收口径等同于 Windows Sandbox 验证。
- 本裁决覆盖 P02/P04 的项目验证环境：无需查询、安装、启用或启动 Windows Sandbox Feature，也无需 guest 验证。它不表示本机具有虚拟机隔离能力，不豁免源文件、用户数据、凭据和构建输出保护，也不修改全产品干净 Windows 发布 Gate。
- 决策前主线锚点：`main@8a0685c9bf5aec7e7cc51f466f3fec7b176c35de`。P02 Task=`in_progress / ACTIVE`；P04 由本次治理记录释放为 `ready`。

## 当前状态

- P02 产品 AC、Owner allowlist、行为基线和数据保护要求不变；Owner=Antigravity，非作者 Reviewer=DeepSeek Harness，Integrator=Codex。
- P02 既有 Windows Sandbox Feature=`UNKNOWN` 只作为历史环境事实，不再是本机验证 blocker。hook/cache/子进程写入边界和本机 Build Gate 证据仍未闭合，因此 Build Gate=`BLOCKED`、build=`NOT_AUTHORIZED / NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`、Hard Build Barrier=`EFFECTIVE`。未将任何未执行项记为 PASS。
- DSH 对 exact D23=8a0685c9bf5aec7e7cc51f466f3fec7b176c35de 的 follow-up Review 已 APPROVED（P0/P1/P2=0/0/0；R2-1 为唯一非阻断 P3），D23 已于 2026-10-10 09:41 fast-forward 集成到 main。Review 与集成都已完成；D23 review report/prompt/exit/mount 见 dsh-review-p02-post-review-preflight-r2.*。当前只修复并复审 R2-1 文档指针，之后继续 P02 Gate 工作。
- P04 已释放 `ready` 供 Antigravity 编写定向测试；运行 Cargo/Tauri 前仍需 Codex 通过 P02 本机 Build Gate，并提供来源、input pins、Hash 均可复核的 scratch sidecar。
- 本轮只修改项目 Task/状态/恢复文档；未运行 Sandbox、guest、build、Cargo/Tauri、runner、Vitest、GUI 或产品测试。

## 恢复安全与下一步

- 保护主工作区已有 dirty/untracked 文件；只提交本次明确修改的项目文档和新增 checkpoint，不 stage 或清理其他文件。
- 下一步：DSH 对本 P02 docs-only closeout 的固定 tip 做 exact-head Review；通过后集成此文档收口，再闭合 hook/cache/子进程写入范围，并取得解除 Hard Build Barrier 所需的真实隔离证据，最后完成 Codex 本机 Build Gate。任何 Gate 未通过前 build 保持 NOT_AUTHORIZED / NOT_RUN；通过后才为固定 P04 head provision provenance-bound scratch sidecar。
- 已知限制：本机验证是项目接受的 Sandbox 验收替代口径，不是 Windows Sandbox VM 隔离的技术证明；发布级干净 Windows Gate 未被豁免。
