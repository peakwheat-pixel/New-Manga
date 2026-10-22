# P02PRE-R1G follow-up 3 独立 Review

## 结论

- Verdict：`APPROVED_STATIC_CONTENT`
- Reviewed branch：`agent/antigravity/P02PRE-R1G`
- Base：`cddff58469b56e181019a8ddfeade80684bc7eb9`
- Reviewed HEAD：`946938bd0696dfddd01f87d61fe6723c63ecdc86`
- 未解决 findings：P0=0 / P1=0 / P2=0 / P3=0
- Reviewer：Codex 非作者 Reviewer；Owner：Antigravity；Integrator/Adjudicator：Codex `/root`。

在冻结输入范围内没有发现新实质问题。R-009、R-010 的静态修复成立，交由 root Codex adjudicate。本结论只覆盖静态内容，不表示 parser、自检、preflight、capture、AC 或 Gate 通过。

## Review 范围与证据

Reviewer 读取指定 Review prompt 和其中列出的 11 个 exact content inputs。Reviewer 未运行 shell 命令、候选脚本、parser、测试、自检、preflight 或 getter；未计算 hash、搜索、glob、枚举目录、写文件或调用子代理；未访问、stat、hash 或查询 `.tmp.driveupload`。Reviewer 另做了工具元数据查询以确认只读能力。Root 负责输入前后 pins 与裁决。

### R-009：WER 非法路径失败关闭

处置：`FIXED_STATIC`，建议关闭原 P2 finding。

- `p02pre-r1g-capture.ps1` L827–843 将 `REPARSE_POINT` 与 `NOT_DIRECTORY` 纳入失败分类，设置 `werQueriedFields=FAILED` 和 `phases.wer=FAILED`，并记录 stop category、reason、非法目录数量、路径和状态。
- L850 的 `stopReason` guard 阻止进入 `protectedHashes`，也因此阻止其内部的 `aclStability`；两阶段保持 `NOT_REACHED`。
- 既有 directory / registry query error 计数与失败关闭行为仍保留（L828、L832–833）。路径 helper 在遇到 reparse point 或非正常目录时返回，相关记录不进入后续目录 ACL 查询。
- “立即失败”是 WER 阶段既有目录及 registry 采集后的分类判定立即失败；新增 guard 阻止后续 `protectedHashes` / `aclStability`，没有新增查询或扩展 allowlist。

### R-010：最小 evidence fallback 的有限阶段状态

处置：`FIXED_STATIC`，建议关闭原 P2 finding。

- L583–590 的 `Get-BoundedPhaseMap` 固定投影八个阶段键，缺失阶段为 `NOT_REACHED`。
- `New-PartialEvidence` L604、serialization exception fallback L1130、bounded partial 再次超过 64 MiB 的 fallback L1158 均使用固定投影。
- 两个最小 fallback 保留 underlying/original stop 字段及 `PARTIAL_EVIDENCE` 分类，不注入完整 `$Result` 或 inventory。

## 范围与验证限制

- 静态内容未显示新增 executable、profile / registry / ACL 写入、用户源文件写入，或绕过唯一 `CreateNew` 输出；有序 argv 仍经 `ProcessStartInfo.ArgumentList` 逐项传递（L60–115）。
- 三文件范围、branch/base/HEAD、clean status 与 pins 依据 Codex Delivery Adjudication；Reviewer 未独立运行 Git 或计算 hash。
- Reviewer 未运行 parser、纯函数 assertions、child preflight、capture、host getter、Build/Cargo 或 AC1–AC7；上述均仍 `NOT_RUN`。
- OS 路径访问、实际 no-follow、运行期写入闭包与子进程闭包未验证；`WORKTREE_RELATIVE_EXCLUDED_PATH_ACCESS=NOT_VERIFIED` 保持原值。
- Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`。用户接受的残余风险保持 `private_registry_absence=UNPROVABLE`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`，且必须保留 `technical condition unmet; user explicitly accepted residual risk`。

## 推荐下一步

Agent：Codex `/root`。同一 11 项 post-pins 全匹配且 root adjudicate 后，按冻结 manifest 对已审查候选做精确字节 `CreateNew` 集成，再执行 parser/self-check 与 PS7 engine preflight。Self-check 应覆盖 phase map 的完整键、缺失键和额外键投影。Capture 仍须等待独立最终 pre-run 核验与明确 `PRE_RUN_PASS`；本 Review 不释放 Build Gate。
