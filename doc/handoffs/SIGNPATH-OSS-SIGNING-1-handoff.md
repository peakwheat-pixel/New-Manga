# Handoff — SIGNPATH-OSS-SIGNING-1

## 交付结果

- Task：[SIGNPATH-OSS-SIGNING-1](../tasks/SIGNPATH-OSS-SIGNING-1.md)（`in_review`，未 push）
- Owner：dsh-lead；Reviewer：region-workbench-owner（独立审阅，见任务卡 Review）
- 交付 head：见任务卡 `delivery_head`（材料 + facts/REPORT 提交）；基线 main `8fcba8a89`
- 产出：
  - `doc/release/SIGNPATH-APPLICATION.md` — 英文申请草案（SignPath 表单字段、项目/架构/隐私/许可、构建发布流程、签名对象、完整性校验、动机、成熟度、联系人占位、声明、发布策略、提交前诚实快照）
  - `doc/release/SIGNPATH-APPLICATION-CHECKLIST.md` — 中文前置清单（P0 硬阻塞 / P1 申请与 secrets / P2 发布验证 / 安全边界 / 风险）
  - `.github/workflows/build-release.yml` — GitHub Actions 公开构建 + SignPath 签名集成草案（`sign` 输入默认 false，签名步骤禁用；不伪造签名）
  - `README.md` — 仓库根 README（英文 + 中文要点）
  - `verification/SIGNPATH-OSS-SIGNING-1/{facts.json,REPORT.md,check-governance.json,logs/*}` — 事实核对、报告、门禁证据

## 验证证据

- `verification/SIGNPATH-OSS-SIGNING-1/facts.json`：GitHub API + `git ls-remote` + 本地 git/哈希（仓库 public、`license=null`、默认分支/快照分支均无 LICENSE/README、无 CI；产物 sha256；测试基线；隐私事实）。
- `verification/SIGNPATH-OSS-SIGNING-1/REPORT.md`：事实表、交付物、静态检查（YAML 可解析、占位符、相对链接 0 missing）、明确未做事项、门禁。
- `verification/SIGNPATH-OSS-SIGNING-1/check-governance.json`：`check.ps1 -TaskPath` 复跑结果（PASS）。
- `verification/SIGNPATH-OSS-SIGNING-1/logs/extract-command-surface.log`：命令面 66/66 PASS。
- 独立审阅：region-workbench-owner 给出 CHANGES_REQUESTED（3 P0 / 8 P1 / 9 P2）；本 Handoff 对应 Rev2 修复后版本，修复记录见 REPORT §7 与任务卡 Review。

## 接收方式

- 读任务卡与 `doc/release/` 两份文档；按 CHECKLIST 的 P0 → P1 → P2 顺序由用户本人执行（需要 GitHub 账号与 SignPath 审核）。
- 不要 push 本 worktree 分支；集成由 DSH 完成（`git merge --no-ff task/SIGNPATH-OSS-SIGNING-1` 后更新 STATUS/PLAN/LEDGER）。
- 本 Task 不含任何签名动作；签名要等 SignPath 审核通过并在 GitHub Actions secrets 配置后进行。

## 下一任务建议（必填）

- **用户动作优先**：按 CHECKLIST 完成 P0（公开默认分支补 LICENSE/README/源码树 + 手动跑一次 `build-release`，`sign=false`）→ P1（注册并提交 SignPath Foundation 申请，替换申请材料占位符）。
- **审核通过后**：由 DSH 释放签名实施 Task（配置 secrets、`sign=true` 触发签名、验证 Authenticode、发布 signed installer），并收口 `V1-RELEASE-SIGNING-1`。
- 若审核未通过：保持 RELEASE-VERIFY-1 的 SHA-256 + SmartScreen 指引发布流程；可选先在 README/发行说明中补英文摘要再申请。
- 无其他安全可立即释放的 READY 节点（READY 为空），不阻塞主线。

## 风险与遗留

- 申请是否通过由 SignPath 决定（star/fork=0、无公开 release，存在被拒风险）；本 Task 不承诺通过。
- 公开仓库当前缺 LICENSE/README/CI/产品源码树，是申请的**硬前置**（CHECKLIST P0）；不补齐则申请无意义。
- 用户个人信息（姓名/邮箱/时区/发布分支）需本人填写；Agent 不代填、不代持 token。
- 模型权重（725MB）与第三方素材不得进公开仓库；`-models` 权重走独立分发。
- 隐私表述已按代码事实修正（默认本地；用户显式配置远程 Provider 时会发送页面图片/文本/遮罩），不得再使用“完全不上传任何数据”的绝对表述。
