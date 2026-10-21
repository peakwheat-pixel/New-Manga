# 五个广域根整体保护：精确保全解释设计

本文件是设计，不是运行策略。用户裁决见ruling.md；6条精确绑定及两源指纹见binding-specimen.json（DESIGN_SPECIMEN_NOT_RUNTIME_POLICY）。正式guard仍24项错误、不能清理。本设计不解除r212禁令或修复其余12项，也不证明只剩main。

## 最小实现选择

保留通用路径/身份/Markdown/JSON解析与拒绝规则，在共享scan_repo_declarations的正常扫描完成后增加一次“受裁决记录转为整体保护”的收口阶段。全部6绑定先验证；成功后在隔离的新index容器中登记12个保护Declaration，追加12条warnings，并只替换对应12个DECL_GENERALIZED/DECL_DESTINATION_GENERALIZED错误。不是删掉错误后不保护，也不是跳过源文件/表格。其它24→12中的剩12错误必须完整保留。

不修改_resolve_identity/_declared_identity/_prose_probe的通用拒绝，不引入allow_broad=True、全局ignore/generalized开关、任意CLI覆盖或新的自然语言路径解析。EVIDENCE_PIN、JSON声明和prose探测没有这种许可。直接构造ProtectionIndex、事故回放也保持原行为。只允许scan_repo_declarations通过已验证的当前策略执行保全收口；三个消费者现有调用签名不变，json_exceptions现有参数不承担此功能。

拟新增运行配置tools/governance/broad-root-preservation.json；仅此新配置保存当前用户裁决，历史两个Task和旧pin保持原位原字节。不得修改现有69项NDJSON/JSON非声明例外表。绑定样本是研究证据，不能直接复制改名为运行策略；实施Task须生成严格运行schema并在固定commit独审。

## 运行schema和精确身份

运行JSON顶层只允许schema_version=1、policy_kind=BROAD_ROOT_PRESERVATION、scope_id=workspace-preserve-20261021-5roots、decision_ref、decision_sha256、bindings。decision_ref必须是本设计ruling.md的仓库相对路径（不能ENV/glob/遍历/URL），SHA精确绑定原裁决字节；Git commit pin由实施Task Canonical Evidence负责，无自引用hash。禁止未知键、重复ID、重复完整记录身份、缺失/空/不合类型值。

bindings恰6条，源文件集合仅doc/tasks/SEC-FIX-PATH-ECHO-1.md（1条）与doc/tasks/WORKSPACE-CONSOLIDATION-1.md（5条）；根集合恰workspace本身、task-envs、worktrees、review-scratch、temp五个，workspace有来自两个源的两条记录。不能从目录枚举推导授权，不能换成父G:/CODEX或其它管理根。六source与destination均同一个精确根，不扩大根集合。

每条记录字段：id、origin_file、origin_raw_sha256、global_line、row_raw_sha256、row_verbatim、parser_locator、root_abs、root_normalized、root_real_expected、source_keep、error_pair。bindings样本里的error_original_ids/source_fingerprints/current_error_count等是研究元数据，不属于运行schema，不能被宽松接受。origin_file要求精确仓库相对路径，origin_raw_sha256为整源磁盘原始字节，不归一化换行；row_raw_sha256包括原始行尾。global_line是实际物理行，parser_locator是Resource Manifest表内相对定位，二者不能混用。完整原始行须仍属于标准Resource Manifest，复用既有section_text/iter_table_blocks/parse_table_block等解析辅助，不另写第二套Markdown解释器。

source_keep仅允许样本里已有的PRESERVE_REFERENCED（4条）或PRESERVE_UNKNOWN（2条），逐record与原行一致；不能接受DELETE_SAFE/MIGRATE/ARCHIVE/NOT_APPLICABLE/未知值。destination必须与source同根。realpath不能只校验lexical：先用现有resolve_declared_path和resolve_real_target进行glob/ENV/遍历/绝对身份校验，再与冻结lexical/real精确相等；本六根目前lexical=real。若junction/symlink目标变化，拒绝本策略，不把别的真实根静默纳入许可。根当前为空/不存在不等于可删，也不要求创建目录。

error_pair每条恰两项完整code/file/locator/message，且在正常扫描结果中各恰出现一次：source DECL_GENERALIZED与destination DECL_DESTINATION_GENERALIZED。不能只匹配根字符串或错误码；不得吞其它同源错误、未知disposition、schema错误、重复列、EVIDENCE_PIN错误。诊断格式/locator漂移也必须重新审查，不能自动重签。

## 收口阶段与失败关闭

1. 正常读取所有tracked与非ignored untracked doc/tasks/verification文件，照现有规则解析；不跳过两个历史源。加载运行策略并严格验证schema/ruling原始SHA/全部6记录/两源raw SHA与完整原行/表上下文/role/disposition/lexical+real及12个完整错误。
2. 所有检查通过前，不删除任何index.errors、不登记部分许可。先构造12个pending Declaration：每record source保留原source_keep，destination使用既有DESTINATION_PIN；source_file/locator保留真实来源，可附带角色便于审计。
3. 全部通过后调用既有_register_protective登记lexical及real保护，再按多重集合精确替换12项错误；保留其余错误的顺序和身份。新增12条warnings：每record的source/destination各调用add_warning一次，code=DECL_BROAD_ROOT_PRESERVED，message包含role、policy/源文件/locator/root/原source_keep；不进errors、不新增diagnostics schema，也不是JSON_NON_DECLARATION。正常成功warnings恰+12；错误24→12、Declaration+12、根+5。不得把保护登记绕到non_protective或只保留裸分支名。
4. 在读取策略前，用现有git_checked执行git ls-files -z -- tools/governance/broad-root-preservation.json，并以完整相对路径精确判断tracked状态；Git命令失败fatal，不当“未安装”。策略存在但untracked必须POLICY_UNTRACKED fatal，不加载/激活；tracked但磁盘丢失必须BROAD_PRESERVATION_POLICY_MISSING fatal；tracked且可读才进入schema/指纹验证。不新增CLI开关或硬编码本机repo路径。这里“未安装fixture保持旧行为”仅指有效Git RepoFixture中策略既未tracked也不存在，保留原广域拒绝。非Git目录的scan_repo_declarations本来就要求Git成功，继续fatal，不给无Git例外；直接ProtectionIndex/parse/model不加载策略、不调用Git。tracked检查只是必要运行条件，不能代替实施Task固定commit独审和发布Gate；未审查工作副本不能冒称已发布。
5. 策略存在但JSON/schema/裁决SHA/来源raw SHA/原行/完整error pair/realpath等任一不符：保留原12错误、添加明确POLICY_INVALID/SOURCE_DRIFT/RECORD_DRIFT/ERROR_MISMATCH/REAL_DRIFT等失败诊断，不做部分接受。即使源漂移后原12错误不再出现，也必须因该策略绑定漂移拒绝，不能因此把根意外收窄。策略删除或权限/读取失败不能降级为忽略。
6. 原子发布采用隔离容器/两阶段提交：保持原index的declarations/protected/non_protective/errors/warnings不变；先构造全部pending及新的ProtectionIndex状态。新容器列表和protected的dict-of-lists全部独立拷贝，Declaration只读复用，不能浅拷贝可变列表后写穿原index。只在新容器登记12条并add_warning12条、替换12错误；所有暂存计数/报告字段也成功后，scanner在最终返回处一次发布(new_index, new_scanned)快照；在此之前保留原index及原scanned引用。任意阶段异常丢弃新容器，返回原index并只增加一项fatal失败诊断，不能暴露部分登记/部分移除/部分warning。T01/T12要求注入第1/6/12次登记和warning/最终计数阶段异常，确认原保护/声明/12错误均未减少。

7. 收口必须在scan_repo_declarations末尾计算scanned["errors"]和scanned["warnings"]之前执行；所有已有scanned计数与返回index同一发布快照；scanned也独立暂存并纳入同一失败处理边界，index.counts的declarations/protected_roots也来自新容器。不为此新增独立计数schema；正常成功scanned文件/解析类别统计保持原值，已有声明/根计数若存在则刷新为新index；errors减12、warnings加12。失败快照为原index+fatal，不能让scanned仍反映旧容器。

8. 读取策略及两源时使用原始字节计算SHA；组装后复核采样未漂移，报告绑定本次policy/source指纹。现有apply路径必须继续重新构建报告并验证release-window/inventory哈希；设计不添加新的执行窗口或变更这些授权门槛。本阶段失败时仍通过既有index.errors使clean/remove拒绝，consolidate报告不可信；没有任何真实资源操作。

## 保护语义与调用链

根保护是整体保护：包括现有/未来所有后代，也拒绝删除其祖先；不是只保护当前列出的文件或被某Task提及的子目录。workspace自身已覆盖其它4根，仍保留全部6条来源与5个根身份以便追踪，不因覆盖冗余删原记录。相邻G:/CODEX/New Manga主仓库与New Manga.workspace-other不因字符串前缀被误包含；“本规则不命中”绝不等于其它规则或权限允许删除。

| 消费点 | 已有行为/必须保留 | 后续验证 |
|---|---|---|
| clean_workspace.py scan_repo_declarations/run_clean_workspace | 共用index；有errors时exit2/空候选；候选用evaluate做父子保护；apply仍有独立window/inventory门槛 | 精确12被转为保护后仍有剩12，主仓CLI仍exit2；纯合成无其它错误时workspace子项也REJECT |
| remove_worktrees.py build_worktree_report/evaluate_candidate | 共用scan；有errors拒绝；名称映射之外仍调用index.evaluate(path) | workspace/worktrees根保护必须经path覆盖拒绝，不能只依靠protected_worktree_names（它只映射直接子根）；不改变库存保护或worktree safety要求 |
| consolidate.py build_inventory/main | 共用scan和evaluate生成保护；declaration_errors存在时报告不可信并非删除工具 | 显示整体保护来源，仍报告其它12错误；不以clean/unmerged统计直接授权资源处置 |
| ProtectionIndex直连/_prose_probe/EVIDENCE_PIN/JSON/incident replay | 无新通用许可，仍拒绝未裁决广域根 | 原29+80回归及双15事故回放必须保留 |

只改共享scanner/default运行配置；三个入口不新增平行规则或表。若实现过程中发现消费者必须改动或既有独立缺陷，先记录并另冻范围，不夹带修复。remove_worktrees名称分支的容器类型问题尚未独立复现，本设计不宣称所有分支无bug、不顺手改它；本规则必须由已有path evaluate覆盖。

## 模型证据与未实现内容

model-proof.json只把已验证6记录投影到既有ProtectionIndex的内存拷贝：新增12保护声明、5根，原保护集合为子集；移除恰12广域错误后模拟剩12。15个覆盖assert包含6root/6future-child/祖先/两个相邻前缀路径；相邻断言仅检查新增五根没有命中，不要求evaluate(repo)==[]，因为repo本身可能已有其它保护。模型同时按设计向warnings增加12条，明确模拟诊断承载；没有证明运行策略激活/异常回滚。它证明目标保护语义能复用现有evaluate，不证明运行loader/绑定/漂移拒绝/原子收口或三个CLI已实现。真实工具仍24错误，不能把SIMULATION写成PASS实现。

binding-specimen.json/model-proof.json均不构造当前resource声明节点；原始record在row_verbatim字符串中保存。两历史源字节/status及tool源码/运行配置前后必须不变。计数都是所记录commit/time快照，自有EV会增加声明/根数，不当作永久值。

## 后续实现Task的最小冻结范围

建议拟议GOV-BROAD-ROOT-PRESERVATION-IMPL-1（未创建、未释放）；Owner Codex（共享seam），Reviewer DeepSeek。依赖本设计独审done。只允许tools/governance/clean_workspace.py、新tools/governance/broad-root-preservation.json、自己的新tests/verification/Task/Handoff及STATUS/Plan/ledger/checkpoint；不改两个历史源、旧测试源码、69项例外配置、其它消费者、产品代码、旧证据/pin。独立worktree若必须创建，按禁令保留；不要仅为测试新增环境/分支。新测试复用RepoFixture/现有runner结构，不另造框架或依赖。

实施需固定source commit及reviewed head；完整证明真实24→12恰上述12条、其余12完整身份不变、旧保护集合不减少并新增五个根/12role保护来源；三入口共同使用。生产真实仍有剩12必须exit2，不得标clean或请求清理。只有实现、独审及main复验通过才可done；这仍不解除任何保护/禁令。

## 后续实际测试矩阵（全部PLANNED / NOT_RUN）

| ID | 场景 | 实施后的要求 |
|---|---|---|
| T01 | 六记录+两源原SHA、role/路径/原行正确 | 仅12错误转为12保护来源+12条warnings；5根；其余错误完整保留；scanned与index.counts同一发布快照；注入中途失败不部分发布 |
| T02 | 改file/path或只同名/另目录 | 无宽根许可；策略fatal |
| T03 | 任何源多一字节/换行漂移 | SOURCE_DRIFT，原保护不弱化，不自动重签 |
| T04 | row/global_line/parser_locator/role漂移 | RECORD_DRIFT/ERROR_MISMATCH，不吞其他错误 |
| T05 | 错/缺SHA、hash大小写规范、坏JSON、未知key/type/version | 合法SHA按大小写无关比较；其它invalid fatal |
| T06 | 缺少/多余绑定、重复ID/完整身份、根集合变更 | fatal，不部分接受 |
| T07 | 源disposition改DELETE_SAFE/MIGRATE/ARCHIVE/N/A/未知 | fatal，不保护许可兼容非保全语义 |
| T08 | destination换根/只有source一侧/缺配对错误 | fatal，不允许只处理一半 |
| T09 | 未裁决广域根/父G:/CODEX、ENV/glob/遍历 | 原通用拒绝，不用ruling泛化 |
| T10 | lexical同根但realpath/junction目标变化 | REAL_DRIFT，两个身份均不能绕过 |
| T11 | exact root/未来任意深后代/祖先/相邻词头 | 前三受保护，相邻只断言新增根差集无命中，不要求全evaluate空；不是删除许可 |
| T12 | 同源还存在schema/enum/其它错误 | 其它错误完整保留；缺expected pair时全部保全收口失败；注入登记/warning/计数异常确认原容器不变（仅添fatal） |
| T13 | EVIDENCE_PIN/prose/JSON/直接ProtectionIndex | 不继承宽根许可，仍原拒绝 |
| T14 | 有效Git fixture未安装、存在但untracked、tracked但丢失、无法读取/Git失败、非Git scanner | 仅有效Git RepoFixture的未tracked且不存在保持原行为；untracked存在=POLICY_UNTRACKED；tracked丢失=MISSING；非Git/Git失败/读取失败均fatal，无旁路 |
| T15 | 两源/策略读取中漂移/替换 | SOURCE_DRIFT或policy drift；apply报告绑定重新校验 |
| T16 | clean/remove/consolidate三个入口及名称映射遗漏 | 真实其它12errors继续拒绝；合成整体保护依path生效，scanned与index一致；相邻仅验证无新增根命中，不要求repo原保护为空；无实际删除 |
| T17 | ruling_ref/SHA错误或引用遍历/URL/换其它裁决 | fatal，不能靠配置文字自称授权 |
| T18 | 新配置untracked或没有已独审固定commit | untracked运行时fatal；tracked也仅满足必要条件，缺固定commit独审仍不通过实施Task发布Gate，不把派生specimen当运行策略 |

实施Task还须跑原29声明+80工具回归，TMP/TEMP隔离自己的workspace目录，0skip；双事故回放clean_workspace/remove_worktrees各15 REJECT/0deleted/0violations；本设计不重跑、不把它们列为本Task已通过。主仓真实audit与policy/source原字节、真实pin注册、pwsh -NoProfile -File tools/governance/check.ps1、git diff --check、固定head独审和Codex集成复验均为Gate。产品/构建NOT_RUN（治理工具范围）。

## 风险与下一步

整体保护意味着workspace所有子树继续禁止自动删除；消解广域错误不会使Git资源可以退出，最后只剩main仍受其余12项/原保护/r212/用户数据/支线裁决约束。整源raw SHA绑定使任何合法历史元数据变更也会导致策略失效，这是保守设计；未来需要更新必须新Task/独审，不能自动签新SHA。

本设计固定head经DeepSeek独审、Codex核销后，推荐另冻上述实现Task。当前只交付设计，不实施新guard/default policy，不动原文件，也不申请任何删除窗口。

## R1修订说明

R1固定3879cb936 changes_requested：P1诊断承载与policy untracked激活已明确修订；P2相邻断言、发布/计数时点和Git fixture边界均在上述规范与T01/T11/T12/T14/T16/T18冻结。绑定六条/原字节/用户范围不变，模型仅补12条warnings以匹配设计。修订仍为设计，不冒称loader或回滚真实测试已执行。
