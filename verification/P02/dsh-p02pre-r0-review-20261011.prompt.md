# P02PRE-R0 独立 Review 请求

## 任务与角色

你是本项目的非作者 Reviewer（DeepSeek Harness）。请独立审查 P02PRE-R0 Owner evidence 的范围、证据绑定、分类和表述；作者/Owner 为 Codex `/root`，Integrator/adjudicator 也为 Codex，作者不审核自己的工作。

仓库路径：`G:/CODEX/New Manga`；branch=`main`；固定基线 HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。

## 限定对象与 pins

只读审查以下固定文件内容。不要检查未列文件，不要刷新 Git 状态或 OS 状态。以下 SHA-256/size 是 Codex 在 Review 前固定的对象 pins：

| 对象 | bytes | SHA-256 |
|---|---:|---|
| `doc/tasks/P02PRE-R0.md` | 6473 | `FE04EBDDA5BDE0312A498F5A191CE07A32751B3096254B0D0B0F8244292694FD` |
| `verification/P02/p02-readonly-preflight-r0-manifest-20261011.md` | 11567 | `8D2977BD0B7310F04E05FDF44D89F5B38981C64AD93E9BE3C2F97366FDDC9ECE` |
| `verification/P02/p02-readonly-preflight-r0-evidence-20261011.md` | 99592 | `AE16A27C5843C71C9EC9414C54C2FF23EBE5A612F75DA0CB5EA3A49B154879F3` |
| `doc/tasks/P02.md` | 205841 | `7CD0CF655A556A9F681629DC44B23AB7F54B7B308789762B13E0AC3DC60989EB` |
| `doc/REBASELINE_PLAN.md` | 226162 | `D9E70DA2A7A16D330483DD3DCCDBDC5D711969C7185030E709001AD152E498AE` |
| `doc/STATUS.md` | 252181 | `97CEB9B0FBC3488152F5DBC199627B20765B944CB50B6CF023CB33E3ADC6A626` |
| `doc/00_INDEX.md` | 42650 | `2FCD361FE6DE96D94AF31510CD1425AF9BC257BF39F30DD92B0F5F5240C298A0` |
| `verification/P02/codex-checkpoint-p02-readonly-preflight-r0-20261011.md` | 13189 | `C584EF6B08AC04D84745081E97C3C5D18FF0CDC651C6299251FEBEC0D1A0910E` |
| `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md` | 44307 | `626E000A94C8C3561DBB13BFA4C5BC66DA315001B9F50B5AC1669339407009DE` |
| `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-review-20261011.md` | 23380 | `A8C0C124C5EEF391CDBB44CA20B1169CFABC99E94C92E0C1AC798450E7DAF9A8` |
| `verification/P02/codex-p02-owner-risk-waiver-manifest-r6-adjudication-20261011.md` | 5560 | `01E556448BA2A5CF1E68F28A0C91D1FDD71EE28EB2CB5ED583983348BFFE9159` |

## Review 问题

1. R0 manifest 是否在宿主查询前冻结，实际最终 capture 是否只调用了明确许可的 getter/query，并绑定到先核验的同一 PowerShell process identity？
2. 逐项核查 42 个冻结 path metadata/ACL、35 项 process environment、HOMEDRIVE+HOMEPATH 组合、两个只读 registry key、三个 WER 目录 direct-child metadata 与 13 项固定 SHA-256 前后对照的记录是否内部一致、是否有越界或缺失。
3. 特别评估 evidence 明示的执行偏差：早期一个路径诊断批次查询了未冻结枚举的父组件且工具输出被截断；该批次未用于结论，最终 capture 只访问 42 个精确对象。判断此偏差是否要求 changes requested、限定证据采纳范围或其它具体修正；不要把未捕获输出推测成成功结果。
4. 核验第一次 WER 批次的路径数组错误已被明确标为无效，并且后续同进程 capture 的三个精确目录结果才作为证据；不得将该有限 snapshot 说成 future T0、真实 dump destination 或 WER policy 证明。
5. 检查 `PASS_WITH_EVIDENCE`、`FAILED`、`UNPROVABLE`、`REQUIRES_ACTIVE_TEST`、`NOT_SAFE_FOR_R0` 分类是否准确区分局部观察、缺失证据和动态行为；核查是否误把 owner waiver 当技术 PASS 或放行 Build Gate。
6. 重点看两个已存在 scratch leaf 的空目录条件、路径祖先/reparse/file-ID/hardlink/ADS、ACL effective access、未来 child token/cache/TEMP、WER policy/view/destination/T0、private registry、完整 protected-invariants hash 与未知子进程闭包是否被如实保留为未解决。
7. 审查工具错误/早期普通 `git status` 缺紧邻 index pre-hash 是否有被隐去或错误描述；确认 report 区分 Codex 治理状态读取与主要 R0 OS query。

## 安全与输出约束

- 只读上表指定文件内容。不得执行命令、测试、Git status、系统/API/registry/ACL/path/environment/WER 查询，不启动任何进程或程序，不写/修改任何文件，不尝试重新计算本地状态。
- 不得调用 AppContainer/profile API、`GetTokenInformation`、P/Invoke、`Add-Type`、Registry/ACL/file write、Windows Sandbox、build/Cargo 或 AC1–AC7。
- Review 不授权 Gate，不替 Codex adjudicate。无技术 PASS 结论可从文本审查推导。
- 输出简体中文、仅返回可存入固定 Review 文件的完整 Markdown。指出每个发现的 severity（P0/P1/P2/P3）、具体证据路径与短引用/section、影响和最小修订建议；没有发现时分别写各级 `0`。

## 固定 Review 交付

最终答复将由 Codex 原样保存到 `verification/P02/p02-readonly-preflight-r0-review-20261011.md`。请以该路径为对象名写标题并给出：Review ID、Reviewer、Owner/Author、被审文件 pins、method/limitations、P0/P1/P2/P3 finding count、findings、结论枚举（`APPROVED_AS_READ_ONLY_EVIDENCE_DELIVERY_ONLY` 或 `CHANGES_REQUESTED`）、明确的 gate non-effect。除 Review 正文外不要输出其它建议性对话。
