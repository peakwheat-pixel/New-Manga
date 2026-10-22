# Codex adjudication: H2 source R2

2026-10-13；Reviewer DeepSeek Harness（非作者），session `session-bb74c298-dcd7-4db7-bd22-4198854737f3`，external exit 0，结论 `CHANGES_REQUESTED`。Review 固定 code head `72145184b7664f8dcc660db5329fa217320b2be4`、doc head `4a90d820a5d58a54cbc190665fbd87d563bc19af`。Codex 对 R2 Review 记录的 8 项输入逐字节复算，size/SHA 全匹配；证据见 `dsh-source-review-r2.md` 与 `source-review-r2-input-verification.json`。原始 DSH JSONL 保存在 `G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-COLLECTOR/r2/dsh-review-r2.stdout.jsonl`。

## 裁决

- H2-01、H2-02、H2-03、H2-04、H2-05、H2-07 与 CX-01、CX-02：按 DSH R2 证据接受为已修复。此前的原始 findings 与 R1 记录保留。
- H2-06 / CX-03：仍部分完成。固定 refs 比较、source/index 双时点、卷检查已有实现，但路径链和全域排除访问证据仍不完整。
- R2-01 P1 ACCEPTED / OPEN：stream 在 `Open-ExclusiveCreateNew` 后已存在，而后续 getter 仍要求 `targetAbsent`，所以 `output-path-chain-volume` 必然 FAIL 并使任何 live run exit 4。Codex 独立按代码顺序与受控 fixture 复核成立。修复须保留 CreateNew 前捕获的 absent/chain/volume/exclusion 原始事实；成功创建后记录目标现为存在及实际独占 stream 状态，不得把 post-create 状态冒充 preflight。CreateNew 冲突仍必须 fail-closed。
- R2-02 P2 ACCEPTED / OPEN：`Test-PathAncestorsOrdinary` 只检查父路径；受控 junction fixture 证明 leaf reparse 被误报 ordinary。修复必须分类现存 file/directory leaf，确认 protected selfcheck、source/index、固定仓库路径和七个 executor targets 的叶子属性；target absence 不能把 dangling link 当成不存在。复用既有 `FileInfo` / `DirectoryInfo` 属性采集，不引入 ACL 写入或 live collector。
- R2-03 P2 ACCEPTED / OPEN：排除守卫没有覆盖全部实际访问路径，也没有保存被检查的路径清单；TEMP/TMP 运行值及派生路径可能进入实际 getter。所有路径在任何相应 filesystem probe 前必须先做纯字符串排除检查；完整 `{path, underExclusion}` 清单必须进入 getter 输入和 raw observation。Codex 另确认 output preflight 当前先调用 `Directory.Exists(OutputDir)`、之后才检查排除段，需将纯字符串排除检查前移到首次该路径 filesystem 访问之前。`RootIndexPath`、H1 Task snapshot、TEMP/TMP plan 与派生 parent/target 路径须纳入可审计清单。
- R2-04 P3 ACCEPTED / OPEN：root index after 采样位于最后几项 `git check-ignore` 与 executor 静态文件读取之前，和 “after whole collection” 声明不符。把 after 复读移至所有采集/只读子进程之后、final close 之前，并保留前后 hash 的实际比较。
- R2 P4 精度项接受为同轮低风险修正：`nonDirectoryComponents` 需真实区分“文件挡住目录链”与“路径不存在”；path-probe-plan uniqueness check 的 pointer 应指向保存了完整 plan 的 raw observation。它们不单独阻塞本次状态，但应随同一个 allowlist 修正，避免 evidence pointer 只支撑摘要。

R2 的 126 PASS / 6 SKIP 和 Parser 0 errors 仅证明其所覆盖范围，未覆盖上述运行时序与路径反例，因此不满足代码批准门槛。R2 固定 head 不可集成，也不释放 live collector。Owner ZCode 在原 worktree/allowlist 继续 R3 修复并提交新 head；Codex 复跑 Parser/pure/受控 fixture，DeepSeek Harness 对新 exact head 独立复审。修复通过前 H2 保持 `in_progress`，H2-RUN 保持 proposed。

## 保持不变的状态

历史 H1 v2 仍为 `PRE_RUN_PASS`（23 PASS / 1 NOT_VERIFIED），P2-1 OPEN；新时点证据不能改写旧 finding 或作为 X6 S0。Technical Gate `NOT_SATISFIED`、`private_registry_absence=UNPROVABLE`、Owner Risk Acceptance `APPROVED`、Gate Disposition `WAIVED_BY_OWNER`、Build Gate `BLOCKED`、Hard Build Barrier `EFFECTIVE`、Build/Cargo 与 AC1–AC7 `NOT_RUN`，均保持原值。未运行 live collector、Registry/ACL/Profile/Sandbox、executor、Build、Cargo 或 AC。
