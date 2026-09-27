# M2-S3 Review 派发记录（DSH headless，reviewed head 233d0901）

- 派发时间：2026-09-26（Owner 交付当日，用户指令"固定 head 后交 DeepSeek Harness 独立 Review"）
- 派发者：ZCode 会话（协议 §6.1 CLI 派发路径）
- 被审工作区：`G:\CODEX\New Manga.worktrees\M2-S3-zcode`
- 派发命令：`dsh --profile headless --json "$(cat %TEMP%\m2s3-review-prompt.txt)"`
- **exit code：0**
- **session ID**：`session-8c7a4ddc-69cc-447e-a816-6a3c978ca24b`（254 事件）
- 原始 JSONL：`%TEMP%\m2s3-dsh-review-run.jsonl`

## Review 结果（引自 DSH final 消息）

- 报告：`doc/reviews/M2-S3-233d0901.md`（218 行，**未提交**，由集成方处理）
- **决定：`approved`**；`findings_disposition: no_blocking_findings`（0×P0 / 0×P1；5×P2 非阻断；5×P3 advisory）
- Architecture：PASS（隔离严格、与 T5 分层信任一致、resolve 防线顺序与报告一致、traversal 结构性不可达）
- Verification：PASS（带 1×BLOCKED）——DSH 沙箱 `SHELL_UNAVAILABLE`（pwsh 初始化失败 `SetNamedSecurityInfoW Win32 5`，与 M2-C2 Review 同因），git/cargo/python/探针 exe 无法独立执行；范围与重跑两项改用 reflog + 全树交叉核验（沿用 M2-C2 Review 同一做法）
- Reviewer 加 17 组模式重扫两份结果 JSON：0 命中

## Findings 与 Owner 处置（DSH 指引：纯文本更正可由 Owner 在任一文本提交关闭，不需新 reviewed head，TASK-029 先例）

| ID | 级别 | 要点 | 处置 |
|---|---|---|---|
| F-01 | P2 | P-04 的 PASS 是字面量且引用不存在的 `observed.url` | **已修复**：`probe()` 返回补 `url` 字段；P-04 改为程序化可见性审计（扫描页面可达 URL 材料的路径泄漏模式）；重跑 16/16 PASS（`raw/probe-results-post-findings.json`） |
| F-02 | P2 | 报告 N-05"issue 层拒绝"表述不精确（实为 `sign_all` 硬编码守卫，未 canonicalize） | **已更正**报告 §3.2 N-05 行：明确守卫机制与 `issue()` 不做 containment 的分工 |
| F-03 | P2 | N-06 的 `../` 被 URL 解析器归一化后才发送，报告描述与实际请求形态不符 | **已更正**报告 §3.2 N-06 行：注明归一化、实际请求形态；N-07 编码形态才是穿透原始 `..` 的场景 |
| F-04 | P2 | L-03 在 fetch 抛错时判定变量变 falsy → 假 PASS | **已修复**：三分类 verdict（`BYPASSED`/`RE_RESOLVED_*`/`FETCH_ERROR`——仅两者皆 `RE_RESOLVED` 才 PASS，fetch 错误记 FAIL）；重跑 verdict=`RE_RESOLVED_REF_REVOKED` ×2 |
| F-05 | P2 | Task 文件"在途不中断…全部实测"与报告 §5.2 自陈限制冲突 | **已更正** Task 运行记录措辞（一次性 body 形态完整、真流式窗口 NOT_RUN） |
| P3×5 | P3 | §10.2 子集声明、NOT_RUN 缺项、Tauri 精确版本、泄漏 verdict 过宽、§3.4 出处 | **部分已关闭**：Tauri 精确版本（tauri 2.11.6 / tauri-build 2.6.3 / wry 0.55.1 / tao 0.35.3）补入报告与 environment.md；泄漏扫描词表扩充（+`nested.png`/`win.ini`）且 verdict 改为逐命中分类（2 命中=探针自编攻击 URL，非泄漏）；其余（子集声明、revision 变化/滑动续期场景、§3.4 出处）留集成/后续微调，不阻断 |

修复后探针重跑：**16/16 PASS，exit 0**（`raw/probe-results-post-findings.json`）；泄漏扫描三份结果：host 侧零泄漏（2 个分类命中为场景输入 URL）。

## 状态

- M2-S3 保持 `in_review`（DSH `approved` @233d0901；findings 文本提交在本记录所属 commit，按 DSH 指引不需要新 reviewed head）。
- 下一步：Codex 集成（复核 `git diff --name-status/--check 90c3e459..233d0901` → Review 报告入库 → Task 以 master 为基合并回填 → integration_commit + STATUS）。
