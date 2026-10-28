# Handoff — SIGNPATH-OSS-SIGNING-1

- Task：[SIGNPATH-OSS-SIGNING-1](../tasks/SIGNPATH-OSS-SIGNING-1.md)（`in_review`，未 push）
- Owner：dsh-lead；Reviewer：region-workbench-owner
- 交付 head：`340867cd807f900e28c831c38f29168c93f5c1b5`（材料 4 件 + facts/REPORT）
- 基线：main `8fcba8a89632502754acfdda61803c3398fcd2f2`

## 交付内容

| 文件 | 说明 |
|---|---|
| `doc/release/SIGNPATH-APPLICATION.md` | 英文申请草案（SignPath 表单字段、项目/架构/许可、构建发布流程、签名对象、完整性校验、动机、成熟度、联系人占位、声明、提交前诚实快照） |
| `doc/release/SIGNPATH-APPLICATION-CHECKLIST.md` | 中文前置清单：P0 硬阻塞（公开仓库许可/README/源码树/CI/内容复核）、P1 申请与 secrets、P2 发布与验证、安全边界、风险 |
| `.github/workflows/build-release.yml` | GitHub Actions 公开构建 + SignPath 签名集成草案（12 steps；签名步骤默认禁用，缺 secrets 不产出假签名） |
| `README.md` | 仓库根 README（简介/架构/前置/构建/测试/发布/校验/许可/未签名说明） |
| `verification/SIGNPATH-OSS-SIGNING-1/facts.json` | GitHub API + 本地 git 只读事实核对 |
| `verification/SIGNPATH-OSS-SIGNING-1/REPORT.md` | 交付报告与静态检查结果 |

## 关键事实（2026-10-28）

- 仓库 public，`license=null`；默认分支 `main` 与 `clean-snapshot-20261026` 根目录均无 LICENSE/README；无 CI。
- 本地 main 有完整许可四件套与 `packaging/release/SHA256SUMS`，但未 push。
- 发布产物 0.1.0：setup.exe 68,611,208 B `ebad8662…3691`（NotSigned）；base/models zip 已在 RELEASE-VERIFY-1 清单中。
- 自签名流水线已验证（RFC3161）；真实签名仍 `WAIVED`（用户接受未签名 v1）。

## 明确未做的事

未 push、未创建 GitHub Release、未运行 CI、未调用 SignPath API、未签名、未代持 token/密钥。

## 用户下一步

按 `SIGNPATH-APPLICATION-CHECKLIST.md`：P0 补齐公开仓库（LICENSE/README/源码树/CI/内容复核）→ P1 注册并提交 SignPath Foundation 申请（替换占位符）→ 审核通过后配置 secrets、启用签名步骤、发布 signed installer 并验证 Authenticode。
