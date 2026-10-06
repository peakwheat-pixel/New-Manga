# DeepSeek 预检处置（Codex，2026-10-07）

审查固定基线 bb7f3dcb；原报告与 JSONL 保持原文。CLI EXIT=0，session=session-f5860d59-a729-48b1-8684-a05322ef47c9，已挂载 RC4-review-preflight 工作区；desktop 下次启动可见，未主动重启。Reviewer 沙箱无法运行 pwsh，所以这是静态契约预检，不能当实现或测试批准。

| Finding | 冻结处置 / 最终验收 |
|---|---|
| P1-1 | 374cf50a 已冻结优先 ORIGINAL / Managed Copy fallback；无重叠 skip/manual bbox 成品像素必须等于原图，缺必要原图 fail-closed。 |
| P2-2 | 保持既有显式完整快照恢复，包括锁回退；历史确认明确提示文字、类型、策略及锁状态。Undo 前后锁不变，后续锁写入由 expected current 守卫拒绝。验证真实 SQLite 新 restored、历史/pin 保留及冲突零写。 |
| P2-3 | 页级 render 消费 locked final，不修改 region 数据或锁；保留既有页级语义，不移植单区域门、不遗漏 locked 译文。 |
| P2-4 | 页级 conflict→INPUT_REVISION_CHANGED；其他写失败→ARTIFACT_WRITE_FAILED，不透传内部 DB/hash code。 |
| P2-5 | 每次随机 catalog key；host 仍 issue opaque grant。相同 catalog/derived 配置传给两进程；页产物切换立即 revoke 旧 key grants，同页请求串行防乱序。撤销失败已提交产物保留，新 preview fail-closed 并保留旧 key 重试。host restart 旧 grant 失效，key 可重新 issue，沿既有 TTL。 |
| P2-6 | C1 §5 明列三命令 / minor 4；pin 写仍 Proposal。同步 rerender_page 承载设计稿意图，不声称通用 PipelineRun 已实现。 |
| P3-7 | core_service handler 校验页存在，无需 RenderService 新 port。 |
| P3-8 | MISSING_REQUIRED_INPUT 覆盖 clean/必要原图及字体布局不可用。 |
| P3-9 | reports status rendered/skipped；skip_reason null/skip_policy/empty_final，禁止内部自由文本。 |
| P3-10 | preview_error 仅 PREVIEW_UNAVAILABLE，细节 stderr，不下发路径。 |

以上属于已授权契约技术澄清，未改变阈值、BJ13 或 A/B/C 裁决。只有固定实现提交的独立 Review、实际 Gate 与 post-merge 回归后才能 closed；本表不是实现批准。
