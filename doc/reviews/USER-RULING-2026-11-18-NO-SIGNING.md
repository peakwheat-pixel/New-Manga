# 用户裁决（2026-11-18）：本项目不需要代码签名证书

## 原文（逐字）

> 本项目不需要证书

- 裁决者：**用户**（项目所有者）
- 时间：2026-11-18 02:25 (+08:00)
- 记录者：DSH（Lead / Architect / Integrator）

## 影响（DSH 据此执行，不再询问）

1. **`RELEASE-GATE4-SIGNED-MATRIX-1` 的 AC2（Authenticode 签名可验证）作废**，改为「**未签名状态如实披露**」：
   记录 `Get-AuthenticodeSignature` 为 `NotSigned`，并在安装说明里写清 SmartScreen 会提示（`packaging/nsis/installer.nsi` 已内置该提示）。
2. **AC1 去掉「签名证书身份/时间戳服务器」**，保留「真实 Windows 环境 + 安装包 hash + 快照/机器标识」。
3. **AC3–AC6（clean install / 四页可达 / 跨版本升级回退 / 卸载与用户数据保护）不变**，且因为不再依赖证书，
   **现在即可由 Agent 执行**（此前是外部资源阻塞）。
4. 与既有裁定的关系：
   - Codex 2026-11-17 Q3 曾裁定「条件 4 需要真实 Authenticode 签名（不许自签名、不许 dry-run）」。
     该条**被本次用户裁决覆盖**（用户是产品取舍的最终决定者）。
   - `INSTALLER-MATRIX-1` 的 `L-IM-3`（无 Authenticode 签名）**从限制降为已裁决现状**，不再作为缺陷登记。
5. **不改变**：`Technical Gate = NOT_SATISFIED`、条件 5 的 `LIMITATION_ACCEPTED`、以及「不得把未跑完的矩阵说成通过」。
6. **仍然要求诚实**：包是**未签名**的，任何说明、发布页、证据都必须写明这一点；不得暗示已验证签名。

## 后续

条件 4 的剩余工作全部是 Agent 可执行的矩阵（`RELEASE-GATE4-SIGNED-MATRIX-1` AC3–AC6），
执行清单见 `doc/reviews/RELEASE-GATE4-EXECUTION-CHECKLIST-2026-11-17.md`（其中 S1 签名步骤按本裁决跳过）。
