# 用户裁决（2026-11-18）：Gate 条件 2 按 A —— 保持现状

## 原文（逐字）

> 条件 2 按 A，保持现状

- 裁决者：**用户**（产品 Owner）
- 时间：2026-11-18（用户回合）
- 记录者：DSH（Lead / Architect / Integrator）

## 背景

Gate 条件 2 原文（`13_RELEASE_GATE.md:26`）：

> 完成 `AUDIT-11-INC-001` 的只读远端可见性调查**或**由产品 Owner 明确接受该未知风险；
> 任何删除、history rewrite 或发布动作另需授权与审查。

- **调查（前半）**：`SEC-01-REMOTE-VISIBILITY-1`（`done`）已确认 —— 仓库 `https://github.com/peakwheat-pixel/New-Manga` **公开可匿名访问**，
  `cc88d1ee`、`b1c1f5a5` 提交可见，`.tmp.driveupload` 历史树可枚举。
- **处置方案（`SEC-02-REMOTE-DISPOSITION-1`，`done`）**：列出 A–E 五个选项，**推荐 A（保持现状 + 监测）**。
- **未做的动作**：B 删历史分支、C force-push 改写历史、D 联系 GitHub 清缓存、E 转私有/删库 —— **一律不做**。

## 本裁决的内容

**选择 A：保持现状并继续监测**。即 Owner 按 Gate 原文的**第二种满足方式**「明确接受该未知风险」，
不执行任何远端删除、history rewrite、平台清理或可见性变更。

⇒ **Gate 条件 2 由此关闭**（调查已完成 + Owner 已明确接受风险，两条都成立）。

## 执行约束（DSH 据此执行）

1. **不删除任何远端 ref**。本轮只做过只读查询（`git ls-remote --heads origin`、`gh auth status`、`git rev-list`），
   远端状态与裁决前**完全一致**：`clean-snapshot-20261026`、`clean-snapshot-20261029`、`clean-snapshot-20261102`、
   `codex/clean-source-snapshot`、`main`、`public-release` 六个分支**全部保留**。
2. **不联系 GitHub**、不提交敏感数据移除请求。
3. **不联系任何人、不改仓库可见性**（仍为 public）。
4. **继续监测**：可见性/新增暴露的变化按需记录；若将来决定处置，须另立 Task 并重新授权与审查（Gate 原文要求）。
5. **不宣称风险已消除**：本裁决是**接受风险**，不是**消除风险**。真相是：历史里的 `.tmp.driveupload` 与素材对象**仍然可被匿名枚举**。
6. 与条件 4/5 无关，不改变 `Technical Gate = NOT_SATISFIED`，也不解除 `Release Gate = BLOCKED`（仍差条件 5 之外的部分，见 STATUS）。

## 被否决的替代方案（留档，便于将来重开）

| 选项 | 本轮状态 | 若将来重启需满足 |
|---|---|---|
| A 保持现状 | **采纳** | — |
| B 删除含素材的历史分支 | 未执行 | 只读确认每个分支无独有可用提交（实测：`clean-snapshot-20261026` 独有 2 / `-20261029` 独有 1 / `codex/clean-source-snapshot` 独有 1 / `public-release` 独有 **15**），且需保存 ref 清单 |
| C force-push 改写 main | 未执行 | 不可逆：需完整备份 + 独立 Review + 通知所有 fork |
| D 联系 GitHub 清缓存 | 未执行 | 需素材权利证明与影响说明；结果不确定 |
| E 转私有 / 删库 | 未执行 | 转私有可能影响 fork 与外部引用；删库不可逆 |
