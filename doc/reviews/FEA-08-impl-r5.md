---
task_id: FEA-08
reviewer: "Codex 新独立会话（主审 /root；辅助只读上下文 /root/standards、/root/spec；均未参与 R5 实现或返修）"
reviewer_kind: agent
author: "DSH（R5 实施者 / Lead / Integrator）"
base_commit: 2870a9fa52b73fdf344cc723e59957d76d60e395
reviewed_head: b44d4a74884652d879e61060a5648270e680f5cf
implementation_commit: f015108ad
decision: changes_requested
verdict: changes_requested
p0: 0
p1: 0
p2: 4
provenance:
  head_delta: 0
  branch: main
  git_common_directory: "G:/CODEX/New Manga/.git"
  workspace_evidence: "G:/CODEX/New Manga.workspace/FEA-08/review-r5-20261103/"
  isolation: "私有 clone/object alternates；独立脚本副本；fake-repo；真实 OS 全流水线仅绑定隔离 evidence；模型 sidecar/合成 BOOK 输入复制后运行"
  source: "用户指定 impl-r5 Codex 新独立会话；Task reviewer 仍待 DSH Appointment 登记，本报告不改 Task"
  repository_write_scope: "仅 doc/reviews/FEA-08-impl-r5.md；无提交、无 push"
  uncovered:
    - "真实 USB/SMB/云卷、真实用户取消、IFileOperation per-item sink；沿用 LIMITED/UNAVAILABLE"
    - "断电、强杀、跨进程并发及所有 OS 故障组合；OSError 注入不等于持久化崩溃原子性验证"
    - "原型仓外历史版本不能仅凭登记 hash 还原；本报告审查当前 16/16 hash 匹配的脚本"
    - "默认 checkout 的既有冻结契约混合行尾 pin 不直接通过；原仓库及保留冻结字节口径的隔离副本通过，详见 Verification"
---

# Review：FEA-08 impl-r5

## 结论

**changes_requested，P0=0 / P1=0 / P2=4。** R5 修复了多数上一轮反例：H5 矩阵补齐大部分事实、普通晋升失败可完整恢复且 hash 不符时不再虚报 rolled_back、重复名双侧判定正确、交付 check 原始日志确为成功输出、16 个脚本实际 SHA 全部匹配。F08I4-001 仍漏 R6b 恢复列表；F08I4-002 仍会漏报待恢复 backup，下一次启动会删除唯一旧备份。另发现数值事实可被 JSON boolean 绕过，以及门禁采集器失败时仍写“全部通过”。

上述缺陷限定于隔离原型与证据闭包；未发现生产路径变更或用户资料受损，延续 P2 口径。当前固定 head 不满足“全部 findings 已处置”的收口声明，不建议直接关闭 FEA-08。本报告不替代 DSH Appointment、findings 处置、集成验证或 Task 生命周期裁决。

## 范围与依据

`git rev-parse HEAD` 实测为 `b44d4a74884652d879e61060a5648270e680f5cf`；与指定 head 相同，head_delta=0。分支 main，common directory 解析为 `G:/CODEX/New Manga/.git`，审查前 `git status --porcelain=v1` 空。比较 `git diff 2870a9fa5...HEAD` 与 `git log 2870a9fa5..HEAD --oneline`；重点为 R5 delivery `f015108ad`、登记 `b44d4a748`，对照 R4 `90e73c224`/`8609c6591`。

依据：AD-002 当前架构、AD-003 引用源边界、ADJ-001 删除语义；STATUS 当前状态与 REBASELINE_PLAN 当前 DAG；Task 冻结 AC、72 项 EV；impl-r4 Review 的 F08I4-001…005；checkpoint §172/§173；R5 Handoff、技术报告；协作协议 §2/§4/§5.1、REVIEW 模板。没有默认扫描历史 Task 或其他 verification 目录。

简写：`P = G:/CODEX/New Manga.workspace/FEA-08/prototype/`；`R = G:/CODEX/New Manga.workspace/FEA-08/review-r5-20261103/`。`/root/standards` 独立审查事务/Standards，`/root/spec` 独立审查 H5/H6；主审核对结果、直接复现门禁失败负控，并负责 pin、完整真实 OS 流水线、产品门禁及最终判断。各辅助上下文未参与被审实现或返修，仓库写权均为空。

## Standards

**executed。** 以 Task allowed_paths、合成文件/禁止清空边界、协作协议 §4.1 证据来源、§4.3 诚实 marker 为依据。禁止产品路径 diff 为空；没有新增共享接口/schema/生产依赖或许可证变化。F08I5-002/004 属恢复材料保护和证据结论的明确行为缺陷，不是风格判断。Fowler smell baseline 仅作提示；矩阵与总驱动重复维护断言的风险已由实际反例证明，归入 F08I5-001，不另设纯风格 finding。

## Spec

### 逐 AC 评估

| 冻结 AC | 独立验证 | 本轮判断 |
|---|---|---|
| AC-1 H4：同句柄 identity/size/mtime、读中变化、mmap 盲区 | 完整隔离 `run_all` 实跑 10 场景：7 complete_old_digest、1 unavailable、2 undetected_mixed；strict-only 约束保留，盲区不冒充稳定能力 | 可支撑已登记限制内的原型 MET |
| AC-2 H5：保留或回收并还原 digest、拒绝永久 fallback、receipt 恢复不重发 | 真实 9 PASS + 2 LIMITED(mocked)，5 条还原记录；bin 0→0、lab leftover=0；137 个独立坏证据负控检验两门禁 | OS 场景事实成立；“矩阵与总驱动逐字段一致/计数为整数”的收口不成立，F08I5-001/003 待修 |
| AC-3 H6：内容/规范像素/尺寸/成员身份唯一映射、重复 occurrence | 22 场景实跑；独立完整 H6 结果行与 Canonical 全相同；自制 22 双向组合及 18 双向回归全部符合预期 | M19/M20/M21/M22/M23 及重复名策略均通过；AES 限制保留 |
| AC-4：60 格来源、真实交付、失败保护、依赖/许可、无生产改动 | 60/60 字段完整；mocked/inferred 无 PASS；72 EV、双 manifest、16 脚本 SHA 通过；事务失败后备份生命周期及门禁失败总结有反例 | 不能按完整收口 MET 关闭；F08I5-002/004 待修。Reviewer 不修改 Task marker |

### F08I4-001…005 逐项复核

| 上轮 finding | R5 修复事实与负控 | 判定 |
|---|---|---|
| F08I4-001 H5 全量语义 | R1/R2/R3/R4/R5/R5b/R6a/R9 与计数缺失/不等、poll 缺失/超时多数已拒绝；R6b `restored` 缺失/空/坏条目 8 项仍仅矩阵放过 | **部分闭合** → F08I5-001；类型边界新增 F08I5-003 |
| F08I4-002 晋升旧集完整恢复 | 备份移动前 OSError、部分 copy、replace、自日志、两个 staging manifest 等普通故障均恢复；hash 损坏正确报告 false；恢复 move 失败仍漏备份、二次启动删除旧备份 | **部分闭合** → F08I5-002 |
| F08I4-003 重复名双侧 | 唯一/重复、反向、双方重复、同/异内容均保守 candidate；M21/M22 仍 exact；M23 两方向断言为 true | **闭合** |
| F08I4-004 当前交付日志口径 | 所 pin `03-check.log` 为 EXIT=0、PASS(3)、elapsed=1.2s 的新采集记录；7 份 raw 与 manifest SHA/元数据相符；摘要无旧 FAIL/R3/R4 矛盾 | **当前交付记录缺陷闭合**；采集器失败路径另报 F08I5-004，不把本次成功记录写成失败 |
| F08I4-005 脚本 SHA | 逐项实际文件 SHA 16/16 匹配；gates_capture 为 `e542b9aa4e5c2c2bf4c1a891fc9339a4cb6d2e2e9506ccac53fc81d3136f4f14`；hash 表自身 EV-F08-64 @f015108ad 正确 | **闭合** |

### H5 逐字段负控与正常对照

`R/spec/probe.py` 深拷贝 Canonical JSON 后逐个修改字段；真实调用 `matrix.derive_ntfs` 和 `run_all.verify_results`，仅把 OUT、fixtures_root 重绑隔离路径。共 **137 个负控，48 个独立字段路径 + 1 个组合计数变异**。正常证据两门禁均接受。以下 M=矩阵、D=总驱动；完整逐项输入、输出和错误在 `spec/h5-negative-controls.json`。

| 事实/变异 | M / D 结果 |
|---|---|
| R1/R6b restored_digest_matches=false/缺失/null/1 | 均拒绝 |
| R1 restored 列表缺失/空/坏条目 | 均拒绝 |
| **R6b restored 列表缺失/空/条目 false/条目缺字段/条目 null/1 等 8 项** | **M 接受；D 拒绝** |
| R2 members_digest_match=false/缺失；restored_count 缺失/0/字符串 | 均拒绝 |
| R3 measured_branch、LIMITED(mocked)、两处 fallback=false 破坏 | 均拒绝 |
| R4 保留/digest 破坏或 recycle_entry_found 为真；R5/R5b 拒绝/零 destructive/identity/type 事实破坏 | 均拒绝 |
| R6a no_destructive_reissued 或 fs_fact_target_kept 破坏 | 均拒绝 |
| R6b 三计数分别缺失/null/字符串/float，恢复后计数不等 | 均拒绝 |
| **R6b 三计数全部 JSON true；或仅 before_execute=true** | **均接受** |
| R9 per_file_digest_after_restore_ok 破坏；R1/R2/R9 entries_poll 缺失/空/超时/iterations 缺失或字符串 | 均拒绝 |
| **R2 restored_count=true/1.0；poll iterations=false** | **均接受** |
| 各场景 verdict 改错 | 均拒绝 |

静态对应也不一致：总驱动 `run_all.py:310–314` 对 R1/R6b 同时要求非空 restored 列表及每项 true；矩阵 `matrix.py:109–111` 仅 R1 有此项，`:128–131` 的 R6b 没有。8 项动态分歧均来自此差异；不能把“大部分字段一致”写成“逐字段一致”。

### 事务注入与旧集合恢复

`R/standards/probe_transactions.py` 每案新建 fake-repo，以独立逐文件 SHA/路径集合保存旧树；真实执行 main、promote、stage_evidence、rollback。仅 fixture 生成、H4/H5/H6/matrix 场景和 verify 以 stub 隔离，不能用该 stub 证明 OS 能力；OS 能力另由主审完整实跑。

**114 案例 = 1 成功 + 113 实际注入；145 次 OSError + 16 次还原内容变异，另 16 次第二启动提前 RuntimeError。** 权威结果为 `standards/cases-v3/`、`transactions.json`、`summary.json`；cases/cases-v2 是探针调试历史，不计最终覆盖。

| 注入点 | 案例 | 完整恢复/观察 |
|---|---:|---|
| staging 的 fixtures_manifest/evidence_manifest replace | 2 | 2 完整恢复 |
| fixtures、fixtures_manifest、各 result/log、自日志：旧件移动到 backup 前失败 | 16 | 16 完整恢复 |
| 新文件部分 copy；各 file replace；fixtures 新目录部分 move | 15 + 15 + 1 | 31 完整恢复，`.new-*` 无残留 |
| backup move 已产生可见结果再抛错 | 16 | 不虚报 rolled_back；实际 backup 漏列。核心 finding 不依赖此边界模型 |
| 晋升失败后恢复 move 持续失败 / 仅首次失败 | 16 + 16 | 恢复条目先被移除，不重试本项，32 案备份漏列 |
| 晋升失败后还原文件/目录内容被变异 | 16 | 全部发现 hash/tree mismatch，rolled_back=false |
| 成功路径 | 1 | fixtures + 15 受管文件替换正确；未受管结果、gates/pin/raw/skip/额外文件均保留 |

113 个失败案例中 49 个完整恢复且 rolled_back=true，64 个为 false；**没有 false true**。114/114 保留未受管文件，`.new-*` 残留 0。48 案实际备份与 failure JSON 清单不一致；16 案第二次 main 尚未进入晋升，就把尚可恢复的唯一旧备份删除。故修复了“误报回滚成功”，仍没有完整实现“未恢复 backup 保留并列出”。

### H6 独立组合与矩阵来源

自制 ZIP 成员使用本轮新写的 alpha/beta 字节，不只重跑内置 fixture：唯一名↔重复名、双方重复、同内容/异内容、成员顺序交换均双向检查。任一侧重复名均 candidate；唯一内容改名换位、重复内容同 name/ordinal 锚仍 exact；无同锚重复内容 needs_confirmation。22 个独立组合通过；M10/M11/M12/M13/M19/M20/M21/M22/M23 共 18 个双向回归通过。M19 同 RGB 字节但尺寸不同，canonical digest 不同且非 exact；M23 两方向 candidate 及两个断言均成立。证据 `spec/h6-controls.json`、`h6-full-compare.json`（differences={}）。

60 格 = 4 卷 × 5 输入 × 3 能力；来源 measured=8、mocked=30、inferred=22。每格有 status/evidence/current/needed，非 measured 无 PASS。NTFS 未逐格式实跑部分保留 volume-level inferred，AES 仍 LIMITED(pyzipper)。证据 `R/matrix-60.json`；技术报告各状态总数与此 60 格一致。

## Findings

路径 P/R 含义见范围节，行号指本轮 hash 匹配的实际脚本。

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| F08I5-001 | P2 | `P/matrix.py:128–131`；对照 `P/run_all.py:310–314` | R6b restored 缺失/空/未还原项时，矩阵仍 H5 PASS，总驱动拒绝；R5 逐字段一致声明不成立 | `R/spec/h5-negative-controls.json` 的 8 个 disagreement | 让两门禁消费同一完整事实集合；补 R6b 列表与条目负控并保留正常对照 | open；延续 F08I4-001 |
| F08I5-002 | P2 | `P/run_all.py:192–194,214–216,407–410,487–494` | helper 先移除 journal 再恢复并忽略恢复错误；失败旧备份漏列；下一次 main 删除整个 OUT，连同唯一旧备份一并删除 | `R/standards/cases-v3/run_all_log-restore_fail/result.json`；16 项二次启动控制 | 恢复/核验成功后才移除条目；failure 清单覆盖实际 backup；有未处理备份时先恢复/隔离保留，禁止启动时无条件清理 | open；延续 F08I4-002 |
| F08I5-003 | P2 | `P/matrix.py:130`；`P/run_all.py:339–341`（同型 `matrix.py:112,133` / `run_all.py:315,348`） | Python bool 是 int 子类；三计数全 true 仍通过，缺失真实次数不能证明没有重发。R2 true/1.0、poll false 也被接受 | `R/spec/h5-negative-controls.json`：R6b.all_counts_boolean 等 7 项双接受 | 按 JSON 整数语义校验，明确排除 boolean；对 count/poll 使用一致类型规则和必要取值约束 | open |
| F08I5-004 | P2 | `P/gates_capture.py:269,293,315,328` | 注入 check EXIT=1/FAIL 后，摘要 [3] 写 FAIL、manifest pass=false，末句仍“本次采集的门禁运行全部通过”；CLI 未消费 phase2 返回结果 | `R/gate-negative.py`、`gate-negative/result.json`、隔离 `evidence/logs/gates.log` | 由所有实测 exit/pass 派生总结果与 CLI 退出码；保存失败原始日志，不无条件输出通过 | open；本次所 pin 成功日志本身通过 |

F08I5-002 最小证据：对最后晋升的 `logs/run_all.log`，先令 os.replace 抛 OSError，再令 backup→dst 的首次 move 抛 OSError。failure 写 rolled_back=false、目标 missing，却 `backups_left_for_manual_recovery=[]`；磁盘仍有 `_promote_backup/15_run_all.log`，SHA=`ae43e41326527ac1089ab94b4210a96db06ad051239589faf093ab3a79846d20`。清除故障并第二次 main，在首个生成步骤主动停止，backup 已空、目标仍缺失。一次暂态恢复失败足以触发，不要求持续权限故障。

F08I5-004 主审负控直接复制 hash 匹配的采集器，重绑 REPO/V/LOGS/RAW 到新目录，只替换 subprocess.run 返回 `CompletedProcess(returncode=1, stdout='Governance check: FAIL ...')`。真实 phase2 输出 check_pass=false；最终文件同时含 EXIT=1/FAIL 与“全部通过”。这不否认本次 Canonical 03-check 成功，只证明下次失败仍可产生矛盾交付摘要。

## 验证

环境 Windows 11、Python 3.14.6、venv=None；门禁使用 .NET SDK 10.0.401、net9.0 测试目标。主仓库只运行只读 Git/check/pins；构建、测试、真实回收实验及负控在 R 下副本执行。日志记录 EXIT、cwd、shell/解释器、环境与耗时。

| 场景 | 实际命令/步骤 | 结果 | 证据（R 下） |
|---|---|---|---|
| build | `dotnet build apps/desktop-avalonia/NewManga.sln --nologo`，cwd=checkout | PASS：EXIT0，0 warning / 0 error，8.29s | `gates/build.log` |
| 无过滤 test（首次干净副本） | `dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings --nologo` | EXIT0，**1289/0/60**，180.75s；额外 3 skip 缺模型 sidecar/BOOK 输入，不能冒充 1292/0/57 | `gates/test.log`、`test-summary.json` |
| 无过滤 test（隔离补齐输入） | 同命令，模型 sidecar/BOOK 均复制后以环境变量指定，TEMP/TMP/evidence 独立 | **PASS：EXIT0，1292/0/57，总1349，182.19s，无 flake** | `gates/test-with-inputs.log`、`test-with-inputs.json`、`test-final-summary.json` |
| 当前治理 | `pwsh -NoProfile -File tools/governance/check.ps1`，分别在 checkout/主仓库只读运行 | PASS(3 warnings)，EXIT0 | `gates/check.log`、`check-main.log`；定稿后 `check-after-report.log` |
| 冻结 pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 主仓库 **15/15 PASS**；保留冻结行尾的隔离副本 **15/15 PASS**，初次失败见下文 | `gates/pins-main.log`、`pins-clean-preserved-eol.log`、`eol-control.json` |
| Canonical pin | 逐行 `git cat-file -p <commit>:<path>` + WT/index/clean checkout 原始字节 SHA | **72/72**；71 commit pin，只有 pin-verify SHA-only | `audit.json`；附录 A |
| 原型实际 SHA | prototype_hashes 逐项对当前 P 文件重算 | **16/16 PASS**，表自身 pin 正确 | `audit.json`、`standards/audit.json` |
| 双 manifest/fixtures | 递归实际文件 + 按两个清单重算全部内容 hash | **44 = 43 内容 + evidence_manifest；43/43 + 43/43 全匹配** | `audit.json` |
| 完整真实流水线 | `python R/osrun/prototype/run_all.py`；仅硬编码根路径替换到隔离 fake-repo | **EXIT0，5.71s**；双生成、真实 stage/H4/H5/H6/matrix/verify/晋升均完成 | `osrun.py`、`osrun/run-all.log`、`meta.json`、`osrun-summary.json` |
| H4/H5/H6 | 上述流水线 + H6 额外直接复跑 | H4=10；H5=9 PASS/2 LIMITED；H6=22；bin0→0、还原5条/leftover0、tmp=[] | `osrun/out/*_results.json`；`spec/h6-full-compare.json` |
| H5 语义变异 | `python R/spec/probe.py` | 正常双接受；137 负控；8 分歧、7 双放过，见 findings | `spec/h5-negative-controls.json` |
| H6 自制双向组合 | 同探针自建 ZIP/尺寸与直接函数比较 | 22 自制 + 18 回归全部通过 | `spec/h6-controls.json` |
| 事务晋升注入 | 真实 main/promote/rollback；stub 场景生成；见事务表 | 114 案例；无 false rolled_back=true；backup 保留/登记失败 | `standards/cases-v3/`、`summary.json` |
| 门禁失败负控 | `python R/gate-negative.py` | FAIL：真实 phase2 总结矛盾，F08I5-004 | `gate-negative/result.json` |
| 60 格来源 | 枚举 volume/input/capability 与 current/needed/evidence/status | 60/60；mocked30/inferred22 均无 PASS | `matrix-60.json` |
| 旧 FEA-06 四 PNG | 逐个对 base blob/工作树/已登记 SHA | 4/4 未变 | `audit.json` |
| 禁止范围 diff/安全 | `git diff --name-only 2870a9fa5..HEAD -- src apps experiments tests packaging scripts tools`；代码/原型调用检查 | diff 空；清空 API 无调用；原型仅搜索字符串/注释提及 | `audit.json`；本报告 Architecture |
| 审查写域/head | 前后 status、head、Canonical/脚本 hash 对比 | HEAD 未变；72 EV/16 脚本原字节未变；主仓库仅新增本报告；无提交、无 push | `status-before.txt`、`final-state.json` |

测试总数始终 1349。首次 1289/0/60 与最终 1292/0/57 的差值为 CoreClient 的 3 项 ModelsBuild 测试；补齐复制的合成 BOOK 和模型 sidecar 后由 skip 转为 pass，其他程序集不变。最终逐程序集通过/失败/跳过：Appearance 21/0/0、Presentation 38/0/0、Host 51/0/28、ThemeEngine 253/0/0、DesignSystem 117/0/0、ApplicationCore 31/0/0、CoreClient 128/0/22、App 653/0/7。最终 57 项 skip 完整标识集合与 Canonical raw 日志/清单完全相同，没有增加跳过；原因沿用已有 sidecar/env 门槛及仓库已登记跳过项。本轮两次测试均 EXIT0，不把缺输入后的环境补齐称为 flake 重试。输入复制清单为 `fixture-input-manifest.json`（sidecar 1964 文件、BOOK 28 文件，复制前后 SHA 全一致）；证据、TEMP/TMP 均指定 R 下独立路径。

干净 checkout 的行尾控制：默认 core.autocrlf=true 使 14 份契约由 LF 变 CRLF，pins 初次为 FAIL(14)；全 LF 新 clone 则只有 C07 不匹配（其冻结 pin 使用 CRLF）。这些契约自 base 到 HEAD 零 diff，属于既有冻结字节口径，未将其报为 R5 回归。`lf-checkout` 用私有 `.git/info/attributes` 将 C07 设 eol=crlf、其余 LF，刷新私有 index 的行尾元数据后，index/tree 与 HEAD 一致、status 空，15/15 通过。初次/中间失败日志均保留（pins.log、pins-lf.log、pins-clean-lf.log）；没有改主仓库属性或冻结文件，也没有重写 pin 值。72 项 FEA-08 EV 在原始干净 checkout 中已全部匹配，无需此适配。

本次独立复跑与交付采集为不同运行：交付 raw 的 check 记录为 1.2s、STATUS=3146 bytes、PLAN=5162 bytes；当前 head 复跑为 STATUS=3165、PLAN=5154，仍 PASS(3)。R5 登记改变了治理文档，不能把两个采集时间的字节数或耗时强行视为相同。交付 build/test/check/pins 数值与 Handoff/报告对应记录一致。Task 叙述中残留“69 文件”/“19 场景”等旧说明，本轮按 EV72（71+1）/实际 H6=22 核实；不把旧说明作为测试依据，建议 DSH 同步清理文字。

## Architecture

**边界通过；证据发布/恢复可靠性需返修。** FEA-08 仍是 AD-003 Source 线前置隔离原型；没有把实验算法接入 Avalonia UI、Host grant、Python Core schema 或真实资料。无生产源码、共享契约、依赖闭包变化；SQLite/DB 不在本卡范围。SHFileOperationW 只处理本轮 synthetic lab 路径，未调用清空类 API；实验条目恢复后移除且回收站总数回到基线。IFileOperation per-item sink、外部卷、真实取消及 AES(pyzipper) 限制保留，不升级为已测能力。既有依赖/预生成 fixture 许可登记未扩大生产依赖。

F08I5-002 涉及原型证据集合，不等同于实现了产品备份/恢复契约；也不能用原型本轮正常成功推出生产事务安全。H4 tolerant mmap 盲区继续明确 unavailable，strict-only 为后续 Source 实现硬约束。

## Verification 结论

**产品门禁与常规复现通过；独立负控发现 4 项 P2，故整体 changes_requested。** build0w/0e、最终无过滤1292/0/57、check PASS(3)、主仓库及保留冻结行尾的隔离 pins15/15、72/72 EV、16/16 脚本 SHA、四 PNG/禁止 diff 均通过。真实完整流水线成功不抵消坏证据/恢复失败/门禁失败路径的确定反例。结论覆盖本报告列明的场景与限制，不将 USB/SMB/云/取消/AES 或崩溃组合写成 PASS。

## 复审与下一步

推荐 **DSH** 先处置 F08I5-001…004，冻结 FEA-08 下一轮返修范围；保留本轮失败副本、待恢复备份与 Review 原字节。返修后交未参与该轮实现/返修的 Codex 新会话或独立子上下文复审新 head。当前不推荐直接关闭 FEA-08 或启动 FEA-09 实施。本建议不构成任务释放、集成或 push 授权。

可直接转发：

> Agent：DSH（Lead/Integrator）。Task：FEA-08 impl-r5 findings 处置与返修范围冻结。Recovery：`G:/CODEX/New Manga`，branch=main，Task base=`2870a9fa52b73fdf344cc723e59957d76d60e395`，head=`b44d4a74884652d879e61060a5648270e680f5cf`，delivery=`f015108ad`；报告 `doc/reviews/FEA-08-impl-r5.md`；隔离证据 `G:/CODEX/New Manga.workspace/FEA-08/review-r5-20261103/`。先登记 F08I5-001…004 处置，再在冻结范围内修复 H5 双门禁 R6b 恢复列表及 JSON 整数类型、恢复失败 backup 的 journal/人工清单/二次启动保留、门禁采集总结果与失败退出码；同步实际脚本 SHA、Canonical pins、Task/研究报告/Handoff。允许范围沿用 FEA-08 workspace 原型、verification/FEA-08、research/handoffs/tasks 与 DSH 治理登记；禁止生产 src/apps/experiments/tests/packaging/scripts/tools 改动、共享接口/schema/依赖扩围、真实资料/清空操作及 push。保留旧 Canonical、失败 backup 和历史 Review；交付新固定 commit、Handoff、逐 finding 处置及证据 pins。逐项重跑本报告正常/坏 H5、114 事务案例及二次启动控制、H6 双向正负例与门禁失败负控；门禁要求 build0w/0e、无过滤至少1292/0/57、check PASS(3)、pins15/15、旧四 PNG 不变、禁止 diff 空，完整记录 flake/skip/行尾控制。随后 Appointment 上下文独立 Reviewer，DSH 另做集成验证与资源 closeout；本指令不自动释放 FEA-09。

## 附录 A：72 项逐行 pin 核验

每行实际执行登记 commit 的 `git cat-file -p` 并以原始字节求 SHA；同时核对主工作树、主 index blob、干净 checkout。前 71 行均 @f015108ad；pin-verify 是唯一 SHA-only，自引用例外。完整预期 SHA 与每项布尔见 `R/audit.json`。表中“通过”为全部适用比较通过，不以 HEAD blob 替代登记 commit blob。

| EV | 路径（verification/FEA-08/下） | commit | blob / WT / index / checkout |
|---|---|---|---|
| EV-F08-01 | fixtures/anim.gif | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-02 | fixtures/book_asym_left.zip | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-03 | fixtures/book_asym_right.zip | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-04 | fixtures/book_dup.zip | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-05 | fixtures/book_dup_copy.zip | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-06 | fixtures/book_dupanchor_left.zip | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-07 | fixtures/book_dupanchor_right.zip | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-08 | fixtures/book_dupcontent_a.zip | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-09 | fixtures/book_dupcontent_b.zip | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-10 | fixtures/book_enc_aes.zip | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-11 | fixtures/book_enc_zipcrypto.zip | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-12 | fixtures/book_enc_zipcrypto_copy.zip | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-13 | fixtures/book_renamed_left.zip | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-14 | fixtures/book_renamed_right.zip | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-15 | fixtures/book_v1.cbz | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-16 | fixtures/book_v1.zip | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-17 | fixtures/book_v1_recompressed.zip | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-18 | fixtures/doc_enc.pdf | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-19 | fixtures/doc_enc_copy.pdf | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-20 | fixtures/doc_v1.pdf | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-21 | fixtures/doc_v1_regen.pdf | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-22 | fixtures/evidence_manifest.json | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-23 | fixtures/firstframe_extract.png | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-24 | fixtures/folder_v1/p1.png | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-25 | fixtures/folder_v1/p2.png | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-26 | fixtures/folder_v1/p3.png | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-27 | fixtures/folder_v2/p1.png | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-28 | fixtures/folder_v2/p2renamed.png | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-29 | fixtures/folder_v2/p4.png | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-30 | fixtures/img_base.png | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-31 | fixtures/img_cmyk.jpg | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-32 | fixtures/img_copy.png | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-33 | fixtures/img_dhash_dist10.png | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-34 | fixtures/img_dhash_dist11.png | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-35 | fixtures/img_dhash_ref.png | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-36 | fixtures/img_dims_a.png | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-37 | fixtures/img_dims_b.png | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-38 | fixtures/img_exif_o6.png | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-39 | fixtures/img_flipped.png | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-40 | fixtures/img_gray.png | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-41 | fixtures/img_gray_as_rgb.png | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-42 | fixtures/img_reenc.jpg | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-43 | fixtures/img_rotated_phys.png | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-44 | fixtures/wrongframe_blue.png | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-45 | logs/gates-raw/01-build.log | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-46 | logs/gates-raw/02-test.log | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-47 | logs/gates-raw/03-check.log | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-48 | logs/gates-raw/04-freeze-pins.log | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-49 | logs/gates-raw/05-fea06-png.log | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-50 | logs/gates-raw/06-forbidden-diff.log | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-51 | logs/gates-raw/07-clearing-api-search.log | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-52 | logs/gates-raw/gates-raw-manifest.json | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-53 | logs/gates-raw/phase1-values.json | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-54 | logs/gates.log | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-55 | logs/h4_run.log | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-56 | logs/h5_run.log | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-57 | logs/h6_run.log | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-58 | logs/make_fixtures.log | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-59 | logs/make_fixtures_regeneration.log | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-60 | logs/matrix.log | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-61 | logs/run_all.log | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-62 | logs/stage_evidence.log | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-63 | logs/test-skip-inventory.md | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-64 | prototype_hashes.txt | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-65 | results/capability_matrix.json | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-66 | results/capability_matrix.md | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-67 | results/fixtures_manifest.json | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-68 | results/h4_results.json | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-69 | results/h5_results.json | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-70 | results/h6_results.json | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-71 | results/run_all_log.json | f015108ad | PASS / PASS / PASS / PASS |
| EV-F08-72 | logs/pin-verify.log | - | N/A / PASS / PASS / PASS |
