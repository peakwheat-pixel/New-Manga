# Codex adjudication — P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE R1

- Reviewer：DeepSeek Harness（非作者）
- Reviewed head：c3cbb067362b24c79f93d014be5b414b816bfb4c
- Review：verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/dsh-review-r1.md
- Decision：CHANGES_REQUESTED；仅修复证据封装，不改变搜索结果、实现或既有 Gate。

## Finding disposition

| Finding | 裁决 | 处理 |
|---|---|---|
| P2-1：exact-input pins 漏掉 Task 文件 | 接受，阻塞批准 | R1 的 11 个原 pins 已重算匹配，另固定当时 root Task 文件。R2 清单将覆盖 Task、Handoff、请求及全部被审证据，仅排除清单自身的自引用哈希。 |
| P3-1：Task 未固定 reviewed_head | 接受并修正 | 本裁决固定 R1 head；R2 从隔离 worktree 精确 head 派发，Review 后回填最新 reviewed_head。 |
| P3-2：候选排除规则晚于 inventory | 接受为限制 | 不重做清单；后续 TEMP Task 必须在清点前冻结判据。当前只支持 immediate-child 清单的 NO_PRECISE_STORE_PATH。 |
| P3-3：Task/Handoff 命令文本不一致 | 接受并修作文档 | Task 计划命令统一为 Handoff 记载的 -LiteralPath 形式；原始 argv 未单独保存，不声称字节级复现，不重跑清点。 |
| P3-4：五个双点前缀名称无法静态确证 | 接受为信息限制 | 不读新内容或重跑枚举；清单不能独立证明磁盘原始名称。 |
| P3-5：availability / Governance PASS 未固定 | 接受并补证据 | 原 DSH probe 的版本、stdout、stderr、exit 已复制至版本化 verification；最终治理检查输出也将固定。 |

其余 Review 结论接受：87 项仅名称/元数据；无专用候选路径时未运行 exact-marker search 并按边界停止；不外推为整机不存在来源；未改源文件。R1 未重算 SHA，Codex 已复算原 11 项并补入 Task 文件。R1 从主工作区读取文件，dispatch 绑定到 worktree head 的字节同一性不能独立证实；R2 将从隔离 worktree 按新 head 复审。最终批准仍需 R2 完整 pins 与独立 Review。

保持：P2-1 OPEN；H1 Review CHANGES_REQUESTED；X6 BLOCKED；Technical/Build Gate 不变。没有重跑 .codex、23-file/TEMP、H1/H2、executor、Build/Cargo 或 AC1–AC7。
