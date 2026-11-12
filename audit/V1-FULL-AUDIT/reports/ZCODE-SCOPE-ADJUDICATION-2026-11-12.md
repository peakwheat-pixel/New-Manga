# NEW-MANGA-V1-FULL-AUDIT 范围裁决记录

日期：2026-11-12
受托裁决者：ZCode，独立 CLI session `sess_535b3a33-11ba-410a-a10b-0b914435f171`（final turn `turn_3e3d7ad0-d3f2-4ae4-945c-5658e3b59e44`）
绑定产品基线：`main` HEAD `10e4ee013835605800d3830fb960ae8d3aa04167`
记录者：Codex；本文件是裁决摘要和本地核验记录，不是 ZCode 回复的逐字副本。

## 裁决

1. “私有素材不传播”阻止素材及含素材的历史继续上传、推送或导出；它不阻止在原仓库内进行受限本地审计。AUDIT-01–14 可继续，但素材仅限不暴露内容的元数据核对。不得复制或展示图片内容，不得输出真实路径值。
2. 原基线 `349e61faff5f93067af5d4ce2d9e394e0d665b8c` 的既有结果封存为段 A 历史证据；未完成的 AUDIT-01–14 在当前架构基线 `10e4ee013835605800d3830fb960ae8d3aa04167` 作为段 B 重新冻结。段 B 的 AUDIT-00 也须重跑，段 A 的 PASS 不迁移。
3. Task 可由 `blocked` 恢复到 `in_progress`。Owner 仍为 Codex；交付后的 Review 指派给未参与实施的 ZCode 新上下文。当前裁决 session 不实施审计，也不作为实施者自审。
4. 解封仅覆盖 Task 原 `allowed_paths`。不授权 push、force push、远端分支处置、历史改写、删除、GC/prune、安装依赖、付费 API、业务源码/测试/契约/Schema/依赖修改或证据 pin 政策变更；不预置任何 AUDIT 项为 PASS，也不授权直接关闭 Task。

## 阶段 0 本地核验

完整命令、生成时间、HEAD、工作树和逐项 EXIT 记录见 [stage0-resume-verification-20261112.log](../logs/stage0-resume-verification-20261112.log)，SHA-256：`B561337B697AD62506049EF310EF04A52B8C69487CE31F6C9046E2B9B470EB6D`。

| 核验 | 结果 |
|---|---|
| branch / HEAD / 工作树 | `main` / `10e4ee013835605800d3830fb960ae8d3aa04167` / clean |
| `349e61…` → 当前 HEAD | `git merge-base --is-ancestor` EXIT 0 |
| `87f61d8…` → `349e61…` → 当前 HEAD | 两段祖先关系 EXIT 0 |
| `349e61…` → `b1c1f5a5…` → 当前 HEAD | 两段祖先关系 EXIT 0 |
| `349e61…` → 本地 `refs/remotes/origin/main` | EXIT 0；本地跟踪 ref=`9b06838220e9caa496c6428a7986cfd5e9391234` |
| `349e61…..HEAD` | 2,366 commits |
| `.tmp.driveupload` at `349e61…` | tree 存在，2,148 个条目；未读取条目内容 |

## 私有素材传播风险披露

### 已核实的仓库事实

- `refs/remotes/origin/main` 的本地 reflog 记录 2026-10-30 09:46–09:50（+0800）三次 `update by push`，目标依次为 `cc88d1ee9fdd27825869b4cdc0a1b68965b3d1fc`、`e97d6a242ed886f82db0e03e2dbd9d2aea7153a2`、`b1c1f5a56840988e149c18375f6e414bf5c7fbda`。其后 2026-11-06、2026-11-09 也有 main push reflog 记录。
- 仓库发布文档分别记载 `main @ cc88d1ee` 已推送和 `origin/main` 已推送到 `e97d6a24`；`doc/tasks/GIT-CLEAN-PUBLICATION-1.md` 记录用户 2026-10-26 选择“只推干净源码快照”。
- 材料清查报告记载 `.tmp.driveupload` 含压缩 Git 对象及嵌入图像；本地树核验显示该目录在 `349e61…` 中有 2,148 个条目。`87f61d8…` 是 `349e61…` 的祖先，`349e61…` 是推送目标 `b1c1f5a5…` 的祖先，且 `b1c1f5a5…` 是当前 HEAD 与本地 `origin/main` 的祖先。
- 仓库版本化记录称仓库于 2026-10-28 已设为 public（`doc/handoffs/SIGNPATH-OSS-SIGNING-1-handoff.md`；`doc/tasks/PUBLIC-RELEASE-P0-1.md`）。

### 结论与未知项

ZCode 将以上证据归纳为：私有素材对象很可能随 2026-10-30 的 main push 进入当时的公开远端历史。这是高置信度传播风险结论，且与“只推干净源码快照”和 2026-10-24 “不传播”记录冲突。它不是对当前 GitHub 可见性的实时验证；本轮没有运行 `git ls-remote`、GitHub API 或网页查询。当前是否仍为 public、材料是否可由外部 fetch、当时执行者所依据的完整授权语境均未实测/未知。

`audit/V1-FULL-AUDIT/reports/MATERIAL_CLEARANCE.md` 的原始材料结论和指纹保持不变。本 Task 不执行远端删分支、改私有、历史重写、清缓存、push 或其他补救。远端暴露面处置是独立事项；本次授权只释放本地审计，不能把“全面授权”解释为传播素材。

## 段 B 执行边界与停止条件

- 基线：固定 `10e4ee013835605800d3830fb960ae8d3aa04167`；审计期间 main 前进不自动变更被审基线，证据需绑定实际审计 head。
- 允许路径：沿用 Task frontmatter 中原 `allowed_paths`。运行临时数据仅放在 `G:/CODEX/New Manga.workspace/task-env/NEW-MANGA-V1-FULL-AUDIT/`；判别力报告和日志进入 `audit/V1-FULL-AUDIT/`。
- 状态：段 B 开始时 AUDIT-00–14 均为 `NOT_TESTED`，仅当次真实证据允许更新；NOT_RUN/BLOCKED 不能改写为 PASS。
- 任一条件即停止并记录：①需要修改产品源码、测试或共享契约；②需要读取、复制、展示素材内容或输出真实本地路径；③阶段 0 的 HEAD/clean/祖先关系改变；④治理检查失败且修复超出允许路径；⑤发现新的真实用户数据暴露面；⑥用户对远端暴露面作出新裁决。
- 完成后进入 `in_review`，由新上下文 Review；独立 Review、证据 pin、门禁和集成验证未完成前不得置 `done`。
