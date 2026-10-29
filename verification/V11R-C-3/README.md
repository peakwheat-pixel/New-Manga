# V11R-C-3 执行证据（旧主题退役）

- 任务：`V11R-C-3`（执行包：`verification/V11R-C-3-READY/`）
- 分支：`v11r/c3-exec`（基于最新 main df883f2ce；R1 tag `v11r-pre-retire`）
- 状态：R1–R6 全部完成，构建/测试/双 shell 启动/零引用门通过；等待独立复审与 Lead 集成。

## 步骤与 commit

| 步骤 | commit | 内容 | 证据 |
|---|---|---|---|
| R1 | `3a5bdfa` | 创建 tag `v11r-pre-retire`（df883f2ce） | `R1-tag.txt` |
| R2 | `e298aec` + refresh `a4129e8` | 重核依赖图/迁移门/对比度矩阵并更新清单 | `R2-report.md`、`R2-*.log` |
| R3 | `bc3dc1a` | 10 个生产文件迁移，legacy-shell 引用清零 | `R3-report.md`、`R3-zero-ref.log` |
| R4 | `8e89e62` | 5 条硬门替代断言 + 删除 5 个旧测试 | `R4-report.md`、`R4-*.log` |
| R5 | `754dc0d` | 删除 NewManga.Theme 项目/工程引用 | `R5-report.md`、`R5-*.log` |
| R6 | `8d7c367` | 零引用门 + 全量 build/test + 双 shell 启动 | `R6-report.md`、`R6-*.log` |

最新执行 HEAD 以 `git log -1` 为准；C-3 只做退役，未 push。

## 关键结论

- 依赖图终态：legacy-theme-source 0 / legacy-shell 0 / legacy-tests 0；DELETE/MIGRATE/REPLACE fate 均 0；
  仅 EVIDENCE-PIN-PROTECTED 87 + NOT-A-DEPENDENCY 55。
- 全量测试 0 失败（App 271+7skip、ThemeEngine 229、DS 82、Host 49+28skip、CoreClient 116+25skip）；
  迁移门 + 依赖边界 29/29。
- `--shell=v2` 与 `--shell=legacy` 均可启动（真实 sidecar；窗口标题 `New Manga`）。
- 回滚点 tag 未被移动；L1/L2 真实回滚演练仍 NOT_RUN（按计划留待实际回滚）。
- 未改 ThemeEngine / DesignSystem 语义。

