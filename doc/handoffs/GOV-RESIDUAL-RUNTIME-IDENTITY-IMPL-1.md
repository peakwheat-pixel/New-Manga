# GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1 交付与下一 Gate

Owner dsh（Coordinator epoch 10，lease `37230d7822a141fcae8f46acd7841890`）；Reviewer antigravity（独立，未参与本 Task 实现）。
canonical 仓库 `G:/CODEX/New Manga`；branch `main`；base `8e31aaa1dff113e5f95ca7db5ece0de00126059a`。
依赖：`GOV-RESIDUAL-RUNTIME-IDENTITY-1`（r2 approved `8e31aaa1d`）。

## 1. 交付摘要

新增一个独立、字节绑定的历史运行身份解释层，把 `GOV-RESIDUAL-RUNTIME-IDENTITY-1` 取证的 7 项残余声明错误映射为显式身份，并使真实用户数据目录获得保护：

| 文件 | 变更 |
|---|---|
| `tools/governance/residual-runtime-identity.json` | 新 policy：7 个 binding（RRI-01..07）、approved_research 指向取证矩阵、canonical SHA-256 = `5a47481d9bee7752fab5270b1bf7b348a855bdd3e8445fcf05e78cf36fd51b88` |
| `tools/governance/clean_workspace.py` | 新增 `_apply_residual_runtime_identity`（挂在 HIE 阶段之后）与摘要常量；既有解析语义零改动 |
| `tools/governance/tests/test_residual_runtime_identity.py` | 12 个测试：生产 7→0、保护补齐、无通配泄漏、6 类负例 fail-closed |

身份落地：E1–E3 → `ALREADY_ABSENT`（非保护，且断言目标不存在）；E4 → `NON_IDENTITY_RECORD`（通配 + 环境变量不展开）；E5 → `NON_IDENTITY_PROSE`；E6/E7 → 为 `C:/Users/49745/AppData/Roaming/com.newmanga.m2rc1.desktop` 的 `catalog`/`data`/`derived` 注册保护根（`PRESERVE_REFERENCED` / `PRESERVE_USER_DATA`）。

## 2. 实测结果

```
baseline : 2639 declarations / 1936 protected roots / 7 errors / 285 warnings  (exit 2)
after    : 2648 declarations / 1939 protected roots / 0 errors   / 292 warnings (exit 0)
保护集合 : 旧 1936 根 ⊂ 新 1939 根，dropped 0；APPDATA catalog/data/derived 全部命中；无通配展开
测试     : 12/12 OK；既有 test_path_header_compat 5/5 OK、test_ac_gate 12/12 OK
治理检查 : PASS (2 warnings)；git diff --check 与 --cached --check 均 exit 0
```

完整命令、EXIT 与未运行项见 `verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/verification-log.txt`。

## 3. 边界与不变量

- 未修改任何历史原件字节：`doc/tasks/P19.md`、`verification/ENV-BUNDLE-1-FU1/resource-manifest.json`、`verification/P19-UI-FIX-1/resource-manifest.json`。
- 未修改已批准的 `historical-evidence-interpretation.json`、`broad-root-preservation.json`、`non-declaration-json-exceptions.json`、`resource-manifest.schema.json` 及其摘要/数量断言。
- 不全局忽略错误码；不按变量名整体豁免；不展开任何通配或环境变量。
- 真实资源操作 0/0/0；无 GC/prune/push/reset/stash；r212 禁令与全部既有保护不变。
- linked worktree `G:/CODEX/New Manga.workspace/worktrees/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1`（分支 `codex/gov-residual-runtime-identity-impl-1`）保留为开发记录，按禁令不合并、不删除。

## 4. 下一 Gate

Antigravity 对固定 head 做独立审查（Architecture + Verification 双面），重点：
1. 解释层是否真的不展开环境变量/通配；
2. 负例是否真的有判别力（篡改 policy、origin 漂移、目标复活、未绑定错误）；
3. 保护集合只增不减与 APPDATA 三根的注册是否成立；
4. 是否改动任何禁止路径或既有解析语义。
approved 后由 dsh 在 main 同点复验并 done；不批准不得 done，不得因此解除 r212 或获得清理授权。

## 5. 可转发指令（下一节点）

“从 `G:/CODEX/New Manga` 当前 `main` 先读 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、本 Handoff 与 `verification/GOV-RESIDUAL-RUNTIME-IDENTITY-1/matrix.md`，核对 HEAD 与 epoch 10 租约。`GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1` 完成后，声明审计的 7 项历史错误应已降为 0 且 APPDATA 用户数据受保护。下一步是推进 `GIT-MAINLINE-CONVERGENCE-1` 的收敛盘点：以 `verification/GIT-MAINLINE-CONVERGENCE-1/branch-analysis.json` 与 `worktree-analysis.json` 为基线复用既有证据，只补查新增 6 分支/6 工作树的变化；对 103 heads 逐项给出 A/B/C/D 分类与最小授权清单。**不得**在 r212 禁令下执行任何删除、归档、引用移除或 prune；真实处置必须另提具体对象、证据、影响与最小授权并等待用户裁决。”
