# FEA-11-RESIDUAL-4A Review r2（独立上下文 fresh subagent）

| 项 | 值 |
|---|---|
| 被审 head | **`fbe337f95`**（r1 返修；父 `5c2ac5eeb`） |
| 结论 | **`approved`** —— P0=0 / P1=0 / P2=0 / **P3=4** |

## 实跑
全量 .NET **1733/0/102**；Host.Tests **302/0/71**；pytest **3395/10**、fea11 **217**；gated `Fea11Residual4AIpcTests` **4/4**；pins **18/18**；check PASS；API EXIT 0；diff 33 文件；禁止面 0；FEA-09 已恢复；`git diff --check` 0。

## 复核
- **D-1c 已闭合**：`RecordSourceOperationFailure` 严格一处改为三键平铺（`operation_id/request_digest/code`），与 Core `runtime.py:263-273` 精确一致；gated 失败路径证「失败不打开 gates」；非 gated 哨兵可判别。独立变异：还原嵌套 → 哨兵 + gated **双 RED** → 复原 sha256 `A468708C…` MATCH → `--no-incremental` 重建 → 双 GREEN；与提交 `logs/mutation-d1c.log` 一致。
- **P2-2 已闭合**：before 归因纠正（D-1b ping `INVALID_JSON` / D-1a 客户端异常）；`after-full-chain.txt` 与真实 fixture **字节一致**（`scan_via/apply_via=dispatcher`、无 defect key）；`after-failure-record.txt` 同；`DEFECTS.md` 数字与实测一致。
- **回归/范围**：D-1a/D-1b 未回退；diff ⊆ 授权面；FEA-11 status/AC 行未动；无「完全实现/全部关闭」。

## P3（非阻塞）
P3-1 `HostRuntime.cs` 三次 DSH 扩域未入卡 front-matter allowed_paths（建议 ADJ/closeout 留痕）；P3-2 哨兵 `RepositoryRoot()` 不兼容 linked worktree/导出树；P3-3 文本哨兵判别面窄（仅 gated 覆盖真实形状）；P3-4 gated 失败路径未回读 Core operation 状态。

## DSH 处置
P3 登记；AC-R3-6（EV/Manifest/integration_commit）由 DSH closeout 完成。
