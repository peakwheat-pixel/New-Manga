---
task_id: FEA-08
reviewer: "Codex 新独立会话 01a19f92-d2c6-7003-b9f1-387f716f9fe8（未参与 R4 实现；主审 /root；辅助只读审查 /root/semantic_review、/root/standards_gates）"
reviewer_kind: agent
author: "DSH（Lead/Integrator，R4 直接实施）"
base_commit: 2870a9fa52b73fdf344cc723e59957d76d60e395
reviewed_head: 8609c6591634cde4feffa295998f6dbf53c56c3c
implementation_commit: 90e73c224
decision: changes_requested
verdict: changes_requested
p0: 0
p1: 0
p2: 5
provenance:
  head_delta: 0
  branch: main
  git_common_directory: "G:/CODEX/New Manga/.git"
  workspace_evidence: "G:/CODEX/New Manga.workspace/FEA-08/impl-r4-review/"
  isolation: "transaction/cases-v3 fake-repo；semantic 独立脚本/fixtures；standards/checkout 为 HEAD archive + 私有 .git/只读 object alternates"
  source: "用户指定 Codex 新会话 impl-r4 Review；Task 待 DSH Appointment 登记，本报告不改写该字段"
  repository_write_scope: "仅 doc/reviews/FEA-08-impl-r4.md；无提交、无 push"
  uncovered:
    - "真实 USB/SMB/云卷、真实用户取消及 IFileOperation per-item sink；保持原 LIMITED/UNAVAILABLE"
    - "断电、kill、跨进程并发、全部 OS 故障组合；不宣称持久化崩溃原子性"
    - "未实跑 run_all 的完整双生成流水线；真实 H4/H5/H6 分别复跑，晋升 main 在 fake-repo 中注入；其他步骤用 stub 隔离"
    - "无法从登记 SHA 取回 gates_capture.py 的历史仓外版本；只审当前副本及其来源差异"
---

# Review：FEA-08 impl-r4

## 结论

**changes_requested，P0=0 / P1=0 / P2=5。** 当前产品门禁通过，但 R3 的 F08I3-001/002 尚未完整闭合；F08I3-003 的最终日志事务已有实质修复，仍受备份移动失败问题影响。F08I3-004 正例已修复，另发现重复名歧义判定只检查左侧；F08I3-005 的 check 元数据已补，交付的成功声明却不受所 pin 原始日志支持。另有一个仓外脚本 SHA 断链。

本报告是固定 head 的独立 Review，不代替 DSH findings 处置、Appointment、集成或 Task 关闭。P2 均局限于本原型/证据闭包；未发现生产代码变化或用户资料受损，故不升为生产 P1。当前固定 head 不应按“全部 findings 已处置”进入关闭。

## 范围与依据

固定点核实：`git rev-parse HEAD` 为 `8609c6591634cde4feffa295998f6dbf53c56c3c`，与 reviewed_head 相同，head_delta=0；`main`，common directory 为 `G:/CODEX/New Manga/.git`，起始 `git status --porcelain=v1` 空。

读取 AD-002 当前架构及 AD-003 引用边界、STATUS 当前状态、REBASELINE_PLAN 当前 DAG、Task 冻结 AC/70 行 Canonical Evidence、impl-r3 Review、checkpoint §169/§170/§171、r4 Handoff、技术报告与本 Task 引用的原型/证据；协作协议 §4/§5.1 与 REVIEW 模板。没有默认扫描其他历史证据。

差异范围：`git diff 2870a9fa5...8609c6591` 及该区间提交历史；重点检查 R4 `90e73c224` 和登记 `8609c6591`，R3/R2 为保守反例与 pin 回归依据。R4 提交 45 个路径均在 `verification/FEA-08/**`、`doc/research|handoffs|tasks` 内；登记提交 6 个路径为 Task、原 r3 Review、STATUS、Plan、checkpoint、pin-verify 登记。产品禁止路径 diff 为空。

下文简写：`R = G:/CODEX/New Manga.workspace/FEA-08/impl-r4-review/`；`P = G:/CODEX/New Manga.workspace/FEA-08/prototype/`。`transaction/prototype/` 是主审初始逐字节副本；semantic 与 standards 各用独立副本。所有注入/构建/测试/日志均写入 R；原仓库只允许本报告。辅助审查上下文来源分别为 `/root/semantic_review`（Spec/语义）和 `/root/standards_gates`（Standards/pin/门禁），均未参与实现或返修；主审负责最终取舍和事务复现。

## Standards

**executed。** 按 Task allowed_paths、禁止真实资料/清空 API、协作协议 §4.1 的证据来源和 §4.3 的诚实 AC 标记审查。产品源码/契约/schema/依赖无新增变更；边界与许可证未发现新违规。F08I4-004/005 是明确的证据来源/结论不一致。Fowler smell 仅作判断提示，不把重复函数等可维护性现象另造阻断项；事务问题按实际丢文件反例报告。

## Spec

### 逐 AC 与 marker 评估

| AC | 实测与证据 | marker 评估 |
|---|---|---|
| AC-1 H4 | 真实隔离复跑 10 场景，strict 读取完整旧 digest；S4 unavailable；S5a/b 明示 undetected_mixed，评估 unavailable，S5c 阻挡 mmap writer。`semantic/out/h4_results.json`、`os-runs-meta.json` | **可支撑范围内 MET**：strict-only；tolerant mmap 不能写成可用能力。 |
| AC-2 H5 | 真实隔离复跑 9 PASS + 2 LIMITED(mocked)，回收/恢复/中断事实成立，G: bin 0→0、lab leftover=0。`semantic/out/h5_results.json` | **实测/限制登记可支撑冻结原型 AC**；不等于所有卷/取消均 measured。R4 宣称的双门禁完整闭合仍不成立（F08I4-001），不能以 MET 消除该 finding。 |
| AC-3 H6 | 21 场景独立复跑一致；M19/M20 不误 exact；M21/M22 与自制正例 exact；目标侧重复名反例仍不遵循交付候选策略。`h6-comparison.json`、`synthetic-container.json`、`asymmetric-duplicate-name.json` | **不能无条件宣称全项闭合**；建议由 DSH 对重复名策略缺口修复后确认 MET，当前保留 F08I4-003。不是把 AES 等 LIMITED 升级为 MET。 |
| AC-4 交付完整 | 60 格 current/needed/evidence 正确、mock/inferred 无 PASS；70 EV 字节正确。旧集失败恢复、成功门禁记录、仓外脚本 SHA 仍有缺口 | **完整交付的 MET 暂不受全部证据支持**；应修复 F08I4-001/002/004/005 后再核验。Reviewer 不改 Task marker。 |

矩阵是 4 卷×5 输入×3 能力=60 格。逐格结果在 `semantic/matrix-60-cells.json`：60/60 来源/字段检查通过；NTFS 未逐格式实测部分正确为 LIMITED(inferred)，USB/SMB 为 mocked，Cloud 为 inferred；AES 为 LIMITED(pyzipper)。这些是能力限制，不是已达成的 measured 子能力。

### F08I3-001…005 闭合判定

| R3 finding | R4 独立核验 | 结论 |
|---|---|---|
| F08I3-001 H5 语义门禁 | 正常两者通过；R1/R3 fallback/R5b/缺失双计数/计数不等两者拒绝。但 R6b、R9 的还原 digest=false，矩阵仍 PASS、总驱动拒绝；另 R2/R4/R5/R6a 事实同样漏验 | **部分闭合** → F08I4-001 |
| F08I3-002 晋升失败丢旧文件 | 新文件复制和 replace 失败可恢复；旧文件→backup 的 move 失败却删除旧目标；恢复结果未按 hash 核对、部分复制残留新临时文件 | **未闭合** → F08I4-002 |
| F08I3-003 自日志/最终晋升 | 最终 run_all.log/run_all_log.json 的 copyfile、replace 失败均完整回滚；成功只改 fixtures/受管结果日志，gates/pin/gates-raw 全保留。上述两文件备份 move 失败仍缺旧文件，rolled_back=true | **核心顺序已修、端到端仍部分闭合**；统一归 F08I4-002，不重复计数 |
| F08I3-004 唯一映射正例 | 自制唯一内容改名/换位、重复内容同锚+唯一项改名均 exact；锚不一致需确认；两侧同名异内容 candidate；M10/11/12/13/19/20 不回归，M21/M22 两个新断言为 true | **原正例缺陷闭合**；新增单侧重复名反例 → F08I4-003 |
| F08I3-005 check 日志元数据 | 03-check 有 command/EXIT/cwd/shell/Python环境/elapsed；实际 raw 为7份，均有基础字段和elapsed，另6份环境仅在manifest、未记录venv；所 pin check 实为 FAIL | **原 check 字段缺失闭合**；运行结论/记录同步缺陷 → F08I4-004 |

### H5 独立变异（每次只改对应事实）

`semantic/probe.py` 在深拷贝证据上注入，重绑 `run_all.OUT/V_FX` 后调用真实函数；`mutations.json` 保存逐项入/出与错误文本。R6b/R9 等六项还通过真实 `matrix.build` 生成完整矩阵，证据 `matrix-mutant-status.json`、`matrix-mutants/*/matrix.json`，不是只检查布尔辅助函数。

| 注入 | matrix.derive_ntfs | run_all.verify_results |
|---|---|---|
| 正常 | PASS | 通过 |
| R1 restored_digest_matches=false | 降级 | 失败 |
| R3 measured fallback_rmdir_used=true | 降级 | 失败 |
| R3 unrecyclable_branch_disposition.disposition.fallback_rmdir_used=true | 降级 | 失败 |
| R5b refused_to_execute=false | 降级 | 失败 |
| R6b 删除 after_execute/after_recovery 两计数（None/None） | 降级 | 失败（缺整数/重发事实不成立） |
| R6b after_recovery=999≠after_execute | 降级 | 失败 |
| R6b restored_digest_matches=false | **仍 PASS** | 失败 |
| R9 per_file_digest_after_restore_ok=false | **仍 PASS** | 失败 |
| R2 members_digest_match=false | **仍 PASS** | 失败 |
| R4 fs_fact_target_kept_at_origin=false | **仍 PASS** | 失败 |
| R5 refused_to_execute=false | **仍 PASS** | 失败 |
| R6a no_destructive_reissued=false | **仍 PASS** | 失败 |

H4 strict 七个语义 flag、H6 M16/17/18/M19/M20/M21/M22 各语义 flag 的独立置 false 均使对应**矩阵**能力降级；M19/M20/M21/M22 同时使总驱动失败。总驱动对 H4 strict flag 及 M16/17/18 flag 没有同等消费，由矩阵层承接，未将它们冒充为总驱动覆盖。

### 独立 ZIP 与尺寸反例

合成成员为本轮新写的 red/green/blue 字节，未复用内置 ZIP；六组 ZIP + 一组尺寸图在 `semantic/synthetic-zips/`，全部结果在 `synthetic-container.json`。唯一改名→exact；唯一内容改变→needs_confirmation；重复内容同锚+唯一项改名→exact；重复内容无同锚→needs_confirmation；唯一内容同名换位→exact；两边重复名不同内容→candidate；2×6/3×4 同 RGB 字节→candidate、canonical digest 不同。两项正例没有退化为误拒。

额外负控 A=`x:red,y:green`，B=`d:red,d:green`：A→B **exact_match**，B→A **candidate**。两份 ZIP 的内容均唯一，仅 B 有同名不同内容成员；`duplicate_member_names_b=['d']` 已识别，却没参与歧义分支。证据 `asymmetric-duplicate-name.json`、`extra_probe.py`。这是交付自述“重复名不同内容仍 candidate”的方向性缺口。

M21 `assert_exact_unique_mapping=true`、M22 `assert_exact_anchored=true`，各自 `unique_content_mapping=true`；逐个翻转断言后矩阵/总驱动均拒绝。原 M10 ZIP exact、M11 CBZ exact、M12 candidate、M13 ZipCrypto exact、M19 candidate、M20 needs_confirmation 均与 Canonical 一致。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| F08I4-001 | P2 | `P/matrix.py:101–120`；Task:77；research:128 | R6b 还原 digest 或 R9 逐文件还原 digest 置 false，仍输出 NTFS H5 PASS；R2/R4/R5/R6a 事实亦漏验，与“矩阵与总驱动共享必需断言”不符 | `R/semantic/mutations.json`、`matrix-mutant-status.json`、`matrix-mutants/*/matrix.json` | 让矩阵完整消费冻结 H5 事实；复用同一校验或对两门禁逐字段反证，保留正常不误降测试 | open |
| F08I4-002 | P2 | `P/run_all.py:89–123,128–162,410` | move 旧目标到 backup 在移动前抛 OSError，restore 先删旧目标且 backup 不存在；fixtures 可丢42文件，manifest/14个受管文件各可丢旧文件。helper 又先移除 journal，部分失旧或恢复失败仍 rolled_back=true；恢复只查存在，不查hash；初始 copyfile 部分写异常留下 .new 临时文件 | `R/transaction/transactions.json`；`cases-v3/*/result.json`、`transcript.log`，50探针含49真实故障触发 | 按阶段记录旧目标/backup是否实际移动；有效旧备份存在且核验后才移除目标；恢复完成前保留journal；保存旧集合hash并完整核对后才 rolled_back；临时写也纳入try/finally；保留未恢复backup | open |
| F08I4-003 | P2 | `P/h6_run.py:201–207`；research:94/112；Handoff:24/51 | 重复名不同内容只查左容器。A唯一名→B重复名仍exact；反向candidate，违背本轮候选策略，不是唯一内容改名正例失败 | `R/semantic/asymmetric-duplicate-name.json`、`extra_probe.py` 与 asymA/B.zip | 对两侧按重复名分组独立核验；增加左右互换断言；保留M21/M22 exact正例 | open |
| F08I4-004 | P2 | `doc/handoffs/FEA-08-impl-r4.md:32`、Task:174；`logs/gates-raw/03-check.log:2/6/14–17`、`logs/gates.log:23/37–39` | Handoff/Task/checkpoint声称check EXIT0/PASS(3)/3.4s，所pin原始日志却EXIT1/FAIL(3 errors,3 warnings)/1.2s，manifest也pass=false；摘要一面写FAIL、一面“全部通过”，还残留check为SHA-only/R3口径 | `R/standards/audit.json`；Canonical原始log/manifest；本轮 `governance-final.log` 另证当前PASS，不能追溯改变旧运行结果 | 区分登记前失败和登记后成功，保存新的成功原始记录并同步摘要/Task/Handoff/pins；按实际7份日志说明环境元数据覆盖 | open |
| F08I4-005 | P2 | `verification/FEA-08/prototype_hashes.txt:7` 与 `P/gates_capture.py` | 16脚本中1项SHA不符：登记2ee62ae3…，实际7203eca5…；LF归一后仍不符。表本身pin正确不能绑定实际门禁采集器版本 | `R/standards/pins.json`、`prototype/gates_capture.py`、`final-state.json`；主审initial-state亦同 | 确认应交付的仓外版本，登记实际SHA、重出关联来源；不能只用表文件自身pin代替脚本核验 | open |

以上 5 项没有 P0/P1。F08I4-002 将丢旧文件、错误 rolled_back 和临时文件残留合并为同一“旧集合完整恢复”问题，未重复计入原 F08I3-003。

## 验证

### 门禁实测

环境：Windows 11 10.0.26300，Python `C:/Python314/python.exe` 3.14.6，无 venv；PowerShell 7；Python 子进程 argv/shell=False；`PYTHONDONTWRITEBYTECODE=1`。各日志/JSON保存命令、cwd、shell、解释器/环境、EXIT与耗时。测试命令没有 filter，runsettings 未改。

| 场景 | 命令/步骤（cwd 均为 R 下隔离目录，除只读 Git 检查） | 结果 | 证据 |
|---|---|---|---|
| build | `dotnet build apps/desktop-avalonia/NewManga.sln --nologo` | **PASS，EXIT0，0w/0e，7.24s** | `standards/build.log`、`build.json` |
| 无过滤 test | `dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings --nologo` | **PASS，一次1292/0/57，总1349，EXIT0，190.3s，无重试/flake** | `standards/test.log`、`test.json`、`test-summary.json` |
| check | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS(3 warnings)，EXIT0，3.599s**；与交付的FAIL原始快照区分 | `standards/governance-final.log` |
| 冻结 pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS 15/15，EXIT0，0.389s**，行尾字节控制见下 | `standards/freeze-pins-byte-preserving.log`、`frozen-byte-control.json` |
| Canonical pins | 70行逐SHA；69行原始`git cat-file -p commit:path`；worktree/index/archive比较 | **PASS 70/70，69commit+1SHA-only** | `standards/pins.json`，附录A |
| pin_selfcheck | 隔离正常/坏commit/坏SHA各跑 | **PASS：正常EXIT0；两种反例各EXIT1** | `standards/probes.json`、`selfcheck-*-output.log` |
| 原型来源SHA | 16登记脚本逐hash | **15/16通过；1失败** | F08I4-005、`standards/pins.json` |
| 57skip | 与原始02-test逐FQN及源码方法/属性对照 | **57/57集合、源行、方法与属性匹配**；本轮skip集合相同 | `standards/audit.json`、`test-summary.json`；Canonical `test-skip-inventory.md`逐项原因 |
| 旧FEA06四PNG | 原工作树SHA与base Git blob比 | **4/4字节未变** | `standards/audit.json`，附录B |
| 禁止写域 | `git diff --name-only 2870a9fa5..HEAD -- src apps experiments tests packaging scripts tools` | **空，EXIT0** | `standards/forbidden-diff.log` |
| 清空API调用 | `git grep -n -E 'SHEmptyRecycleBin|EmptyRecycleBin|SHERB_' -- src apps experiments tests packaging scripts tools`，再读原型调用链 | **代码路径0匹配（grep EXIT1代表无匹配），原型0调用** | `standards/safety-search.log`；h5/fwin静态检查 |
| H4真实隔离跑 | `python -B semantic/prototype/h4_run.py` | **EXIT0，10场景**，0.134s | `semantic/h4_run.py.log`、`os-runs-meta.json` |
| H5真实隔离跑 | `python -B semantic/prototype/h5_run.py` | **EXIT0，9 PASS/2 LIMITED；bin0→0/leftover0**，2.398s | `semantic/h5_run.py.log`、`out/h5_results.json`、`os-runs-meta.json` |
| H6真实隔离跑 | `probe.py`调用真实`h6_run.run(tmp,out,fixtures)` | **21/21场景结果一致**，0.196s；M8/M9为组合行，故21行并非22行 | `semantic/h6-comparison.json`、`h6_results.json` |
| fixture口径 | 遍历fixtures与两份manifest逐文件SHA | **42=41内容+evidence_manifest；41/41项均一致** | `semantic/manifest-audit.json` |
| 60格与语义 | 逐格核验+H4/H5/H6独立flag/事实变异 | **来源字段60/60；H5漏验FAIL** | `semantic/matrix-60-cells.json`、`mutations.json`、F08I4-001 |
| 晋升事务 | fake-repo真实`main`，仅场景生成/校验stub，shutil/os逐点注入 | **50案例/49故障触发：29完整恢复、20不满足完整恢复** | `transaction/transactions.json`、附录C |
| 不受管日志保留 | 每个事务案例逐hash核对gates.log/pin-verify/gates-raw/skip | **50/50不变**；成功路径仅替换受管集合及fixtures | `transaction/cases-v3/*/result.json` |

无过滤测试逐程序集通过/失败/跳过：Appearance 21/0/0、Presentation 38/0/0、Host 51/0/28、ThemeEngine 253/0/0、DesignSystem 117/0/0、ApplicationCore 31/0/0、CoreClient 128/0/22、App 653/0/7。合计 **1292/0/57**，与要求相同，没有减测或增加skip。57项 skip 原因为已有 fixture/env 门槛，逐项清单与真实原始日志一致。

### 干净复现与行尾控制

完整 HEAD 由 `git archive HEAD` 导出，不建 linked worktree，不写原 index。Windows absolute symlink 物化为 Git link blob 普通文本，清单在 `standards/archive-complete.json`，不跟随外部目标；生产/证据字节保持。隔离私有 `.git` 使用只读 object alternates，所有 ref/index 写入仅在隔离副本。

初次 alternates 被 CRLF 写入导致隔离对象读取失败，早期日志的69 missing属于隔离搭建错误；修为LF后重新读取HEAD/index，最终pin/治理均通过。冻结文档另有既有原始字节pin：archive LF 对比14项CRLF pin失败；15份逐一验证LF规范内容相同，再把原工作树**原始字节**复制到隔离副本后15/15通过。该控制及两次失败日志全部保留，不把初次失败隐去，也不把行尾敏感性误报为本Task回归。70项 FEA-08 EV 则在未改的干净 archive 原始字节中已经全部匹配。

模型 sidecar、BOOK fixture 从已有合成输入复制至 `standards/fixture-inputs/`；模型证据及TEMP/TMP外置，原输入未写。原型脚本均复制后执行，避免 pycache 写回源目录。

### raw日志元数据

当前 `gates-raw` 是 **7份.log**，不是请求沿用R3口径的8份：R4无attempt1，旧attempt1删除计入45个diff路径，历史内容仍可从R3固定commit读取。本轮7份SHA与manifest全部一致；command/EXIT/cwd/shell/elapsed字段7/7；03额外带Python/OS/shell环境；另6份仅由manifest提供环境，未记录venv，故不能声称“每份独立具备所有环境字段”。`gates.log`主体是摘要+指针，但结尾存在F08I4-004所述错误结论/旧口径。

## Architecture

**边界通过，证据可靠性需返修。** 没有 Avalonia UI 直接访问 DB/任意路径/模型的新变化，没有共享契约/schema/依赖修改；只交付隔离 Python 原型与研究证据，符合 AD-002/AD-003 Source 线前置定位。许可证记录沿用预生成fixture与已有依赖，不引入生产依赖；AES/外部卷/per-item sink限制未被本Review升级。

H5 destructive 唯一入口检查合成 lab 路径，实跑目标均由本轮 lab 构造；恢复只枚举 lab 对应条目，未调用清空类API。回收站0→0仅针对本轮采样和lab收尾，不声称可清理真实用户回收站。事务探针仅影响 fake-repo，不触及 Canonical/用户资料。发现的旧文件丢失是可复现的证据集恢复问题，不是已观察到真实用户文件删除。

## Verification 结论

**当前固定head产品门禁通过，R4完整收口验证失败。** pin逐commit、尺寸绑定、M19/M20、60格来源、manifest计数、原H4/H5实跑等回归均通过；完整H5矩阵断言、失败晋升逐文件恢复、双侧重复名策略、check成功证据与脚本来源链仍需处理。机械PASS不能替代这五项语义/来源发现。

未覆盖：真实USB/SMB/云、真实取消、IFileOperation per-item sink、断电/kill/并发故障全组合；保持原LIMITED/UNAVAILABLE。完整真实`run_all`双生成链未重跑，真实H4/H5/H6与矩阵分别跑；事务用真实main+fake步骤生成，verify stub不会用于证明语义门禁。每个故障都有实际触发记录，未触发者不计覆盖。

## 复审与下一步

推荐 **DSH** 先处置 F08I4-001…005、冻结 FEA-08 返修范围；随后由未参与该次返修的 Codex 新会话或独立子上下文复审新head。此时不能直接释放 FEA-09 实施。当前尚未关闭FEA-08，本建议不构成Task释放或push授权。

可直接转发：

> Agent：DSH（Lead/Integrator）。Task：FEA-08 impl-r4 findings处置与返修范围冻结。Recovery：`G:/CODEX/New Manga`，branch=`main`，Task base=`2870a9fa52b73fdf344cc723e59957d76d60e395`，当前head=`8609c6591634cde4feffa295998f6dbf53c56c3c`；报告 `doc/reviews/FEA-08-impl-r4.md`；隔离证据 `G:/CODEX/New Manga.workspace/FEA-08/impl-r4-review/`。先按治理登记处置，再在冻结范围内修复H5矩阵必需断言、备份移动失败及恢复hash/临时文件处理、双侧重复名判定；同步真实check成功原始记录/摘要/pins与gates_capture脚本SHA。允许范围沿用FEA-08原型、verification/FEA-08、research/handoffs/tasks及DSH治理登记；保护旧Canonical/backup和本轮原始证据；禁止生产src/apps/experiments/tests/packaging/scripts/tools变更、共享接口/schema/依赖扩围与push。交付新固定commit、Handoff、逐项finding处置和Canonical pins；逐项重跑本报告负控，要求旧集合逐文件hash恢复、正常不误降、M21/M22保持exact、重复名两方向candidate；门禁build0w/0e、无过滤test至少1292/0/57并如实记录flake/skip、check PASS(3)、pins15/15、旧PNG不变、禁止范围diff空。返修后委任上下文独立Reviewer，不由当前返修会话自审。

## 附录A：70行Canonical逐commit字节核验

下表列“PASS”为原始commit blob / 工作树 / index blob / 干净archive四者SHA均等于Task登记值；commit缺省全部为 `90e73c224`（包含69行），只有pin-verify为SHA-only。完整原始SHA/逐行布尔在 `R/standards/pins.json`；不以checkout后规范化文本代替cat-file原始字节。

| EV | 路径（verification/FEA-08/下） | commit | blob / WT / index / archive |
|---|---|---|---|
| EV-F08-01 | fixtures/anim.gif | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-02 | fixtures/book_dup.zip | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-03 | fixtures/book_dup_copy.zip | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-04 | fixtures/book_dupanchor_left.zip | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-05 | fixtures/book_dupanchor_right.zip | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-06 | fixtures/book_dupcontent_a.zip | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-07 | fixtures/book_dupcontent_b.zip | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-08 | fixtures/book_enc_aes.zip | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-09 | fixtures/book_enc_zipcrypto.zip | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-10 | fixtures/book_enc_zipcrypto_copy.zip | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-11 | fixtures/book_renamed_left.zip | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-12 | fixtures/book_renamed_right.zip | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-13 | fixtures/book_v1.cbz | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-14 | fixtures/book_v1.zip | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-15 | fixtures/book_v1_recompressed.zip | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-16 | fixtures/doc_enc.pdf | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-17 | fixtures/doc_enc_copy.pdf | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-18 | fixtures/doc_v1.pdf | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-19 | fixtures/doc_v1_regen.pdf | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-20 | fixtures/evidence_manifest.json | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-21 | fixtures/firstframe_extract.png | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-22 | fixtures/folder_v1/p1.png | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-23 | fixtures/folder_v1/p2.png | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-24 | fixtures/folder_v1/p3.png | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-25 | fixtures/folder_v2/p1.png | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-26 | fixtures/folder_v2/p2renamed.png | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-27 | fixtures/folder_v2/p4.png | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-28 | fixtures/img_base.png | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-29 | fixtures/img_cmyk.jpg | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-30 | fixtures/img_copy.png | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-31 | fixtures/img_dhash_dist10.png | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-32 | fixtures/img_dhash_dist11.png | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-33 | fixtures/img_dhash_ref.png | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-34 | fixtures/img_dims_a.png | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-35 | fixtures/img_dims_b.png | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-36 | fixtures/img_exif_o6.png | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-37 | fixtures/img_flipped.png | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-38 | fixtures/img_gray.png | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-39 | fixtures/img_gray_as_rgb.png | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-40 | fixtures/img_reenc.jpg | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-41 | fixtures/img_rotated_phys.png | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-42 | fixtures/wrongframe_blue.png | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-43 | logs/gates-raw/01-build.log | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-44 | logs/gates-raw/02-test.log | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-45 | logs/gates-raw/03-check.log | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-46 | logs/gates-raw/04-freeze-pins.log | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-47 | logs/gates-raw/05-fea06-png.log | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-48 | logs/gates-raw/06-forbidden-diff.log | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-49 | logs/gates-raw/07-clearing-api-search.log | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-50 | logs/gates-raw/gates-raw-manifest.json | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-51 | logs/gates-raw/phase1-values.json | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-52 | logs/gates.log | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-53 | logs/h4_run.log | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-54 | logs/h5_run.log | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-55 | logs/h6_run.log | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-56 | logs/make_fixtures.log | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-57 | logs/make_fixtures_regeneration.log | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-58 | logs/matrix.log | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-59 | logs/run_all.log | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-60 | logs/stage_evidence.log | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-61 | logs/test-skip-inventory.md | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-62 | prototype_hashes.txt | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-63 | results/capability_matrix.json | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-64 | results/capability_matrix.md | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-65 | results/fixtures_manifest.json | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-66 | results/h4_results.json | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-67 | results/h5_results.json | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-68 | results/h6_results.json | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-69 | results/run_all_log.json | 90e73c224 | PASS / PASS / PASS / PASS |
| EV-F08-70 | logs/pin-verify.log | - | N/A / PASS / PASS / PASS |

`pin_selfcheck`负控：将登记 `prototype_hashes.txt` 的commit替换为base（该blob在base不存在）→EXIT1；仅改其SHA→EXIT1；正常→EXIT0。不存在“只读index、忽略登记commit”的回归。

脚本异常完整SHA：

- 登记 `gates_capture.py`：`2ee62ae3d8e3aec97369845256e2e2a24090bdc00165a7d8c5937c0e7a782e2c`。
- 本轮初始/最终实际：`7203eca5face7bd997f9e5c064095d540cdbaaa198e6b7512c48f2c15fb3c032`；排除CRLF，其余15脚本匹配。所有16原件前后字节未变。

## 附录B：四PNG

| 文件 | SHA-256（与base blob/当前WT相同） |
|---|---|
| reader.png | 8533c263c79bd53cefa68a21d2aabe6501556fd62218ebf653b528c9cbec78b2 |
| settings.png | fd30b166e30aec7a43e4d82ecd1fefb14dffef3bebe2f5f952e41d45e324a162 |
| shelf.png | 307f8f6748522d1cdb3226135a3f733961744a3b2aa5d410f89aad3fde138b0a |
| workbench.png | d5d878bbba9e47e2b59d9dd03816a370688a7afebec6d6e00016f262a46e2df5 |

## 附录C：50个事务探针

主审 `transaction/review_transactions.py`：每次新建fake-repo并复制70个Canonical旧文件，保存前/后每个文件SHA与完整路径集合；仅 stub make/stage/H4/H5/H6/matrix/verify 以独立测试晋升，实际执行原型 `main/promote_file/promote_dir/rollback/commit_journal`。故障以OSError在指定API实际调用处注入，`triggered`保存src/dst；main的SystemExit由harness捕获记为失败EXIT1，harness成功生成总报告为EXIT0，两者不混淆。

| 注入类别 | 案例数 | 实测 |
|---|---|---|
| 正常main | 1 | 成功，仅fixtures/受管results/log更新；不受管日志逐SHA保留 |
| fixtures旧目录→backup move失败 | 1 | 42个旧fixture文件丢失；rolled_back=false |
| fixtures新目录→Canonical move失败 | 1 | 全部70旧文件完整恢复，rolled_back=true |
| fixtures_manifest旧result→backup move失败 | 1 | 旧result丢失；rolled_back=false |
| 6个实际out result + 8个受管log：新copyfile开始前失败 | 14 | 全部旧集合恢复 |
| 同14文件：旧目标→backup move失败 | 14 | 每次丢对应旧文件，rolled_back仍true |
| 同14文件：os.replace失败 | 14 | 全部旧集合恢复 |
| h4 result / 最终run_all.log copyfile先写部分字节后失败 | 2 | 旧70文件内容在，但新增`.new-PID`残留；rolled_back仍true，集合不等 |
| h4 result replace失败后helper还原move二次失败 | 1 | 旧目标缺失、旧backup仍在，journal已被helper移除，rolled_back仍true |
| h4 result replace失败后还原返回但注入坏字节 | 1 | 目标存在但hash变更，rolled_back仍true；证明只查存在不能代表hash核对 |

共50案例=1正常+49实际故障触发；49中29个完整恢复、20个不满足完整恢复。14受管文件为results的h4/h5/h6/capability_matrix.json/capability_matrix.md/run_all_log.json，logs的make_fixtures/make_fixtures_regeneration/stage_evidence/h4_run/h5_run/h6_run/matrix/run_all。results/fixtures_manifest由stage直接写，单独备份点已测；未把不存在的out manifest复制算作覆盖。

最终 `run_all.log` 和 `run_all_log.json` 的copy/replace失败点，旧70项hash完整恢复，没有新成功Canonical；保留的旧EXIT0日志是被恢复的旧字节。两者backup move失败仍丢旧项，按F08I4-002处理。不受管gates/pin/gates-raw在50案例中全部保留。全部明细：`transaction/cases-v3/<case>/result.json`及`transcript.log`；前/后完整hash、残留backup与tmp均在各result。

复现脚本支持在新目录重跑，避免覆盖本轮证据：

```powershell
$env:FEA08_REVIEW_OUT = 'G:/CODEX/New Manga.workspace/FEA-08/impl-r4-review/transaction-repro-<new-id>'
python -B 'G:/CODEX/New Manga.workspace/FEA-08/impl-r4-review/transaction/review_transactions.py'
```

只在该环境变量指定的新隔离目录注入；勿对原仓库运行原始run_all复现故障。脚本记录复制源SHA和完整场景，不授权删除任何旧workspace资料。

## 定稿核验

`HEAD=8609c6591634cde4feffa295998f6dbf53c56c3c`，head_delta=0；起始工作区clean，定稿`git status --porcelain=v1`仅`?? doc/reviews/FEA-08-impl-r4.md`。70个Canonical文件和原型目录初始/最终逐文件SHA集合完全相同；分支/index未改，无提交、无push。本报告复制到隔离checkout后的治理检查EXIT0/PASS(3 warnings)。证据：`R/final-state.json`、`R/governance-after-report.log`。
