# 五项历史证据精确解释与原子保全设计

## 1. 状态、选择与边界

本文件是设计，binding-specimen.json是拟议运行策略的静态样本，未写入tools/governance，不被现有scanner加载。当前正式12错误必须保持；未来另冻实现Task、固定代码及配置独审后，目标才是只解释R25/R26/R27/R28/R32的5错误、保留其余7完整身份。设计不是清理或原件变更许可，父blocked/r212、五广域根和六旧探针保留。

选择最小共享收口：未来只在clean_workspace.scan_repo_declarations尾部，已完成现有broad保全之后，调用一个拟议_apply_historical_evidence_interpretation(index, scanned)。复用现有ProtectionIndex/Declaration、严格重复JSON键检查、_finish_declaration_scan及copy暂存方式；不抽象新引擎，不改read_text、通用Markdown/JSON/路径拒绝、69例外、独立直读API或三消费者。拟议配置路径仅tools/governance/historical-evidence-interpretation.json；无CLI/环境变量豁免开关。

若前序index已含file=tools/governance/broad-root-preservation.json的fatal，直接返回该index/scanned，不解释5项、不发布新保护，避免前序策略失败时仍部分接受。其它来源错误允许存在，只精准处理以下固定5项。

适用顺序明确冻结：前序broad fatal先原样返回；自己的策略absent+untracked按下节no-op。只有自己的策略已启用时，才要求broad已实际生效：broad策略存在且tracked、无该policy的fatal，前序输出的12条DECL_BROAD_ROOT_PRESERVED warning（其policy标记/来源/locator/角色）对应12条保全Declaration，五广域根保护均在。broad absent+untracked/no-op或证明不足时，本helper只加DEPENDENCY_INACTIVE fatal，不解释5项；不能在原24错误环境悄悄变成19。此证明以及依赖broad策略原字节/tracking在发布末检也复核，不改broad helper或新增状态flag/绕过开关。全局总错误数不硬编码为12：其它错误逐项保留；12→7只指当前canonical验收快照，未来其它债务变化不扩大这5项许可。

## 2. 配置的唯一信任边界

顶层精确六键：schema_version、purpose、approved_design、template_bindings、raw_non_declaration_bindings、reference_guards。schema_version必须type=int且为1（拒绝bool），purpose恒为PRESERVE_EXACT_HISTORICAL_EVIDENCE。任何未知/缺失键、错误类型、重复JSON键/ID、额外记录、数量或固定来源集合不符即fatal；不得兼容猜测或glob。

approved_design精确字段：task_id、design_file、design_raw_sha256、source_facts_file、source_facts_commit、source_facts_raw_sha256；绑定本设计原文件与已审研究事实固定commit8a429a889768c18c6b0add5fc7e5c40b83f62746。实际运行配置必须位于repo_root，Git查询以真实repo_root为cwd，不用worktree TOOL_ROOT猜真值。present且untracked fatal，tracked却missing/不可读/Git查询失败fatal；absent且untracked仅为旧fixture/尚未实施环境no-op，不减少任何错误。

未来实现还须内置一个审核后样本的canonical SHA-256常量：严格JSON解析后用json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')计算，与已批准binding-specimen的同一摘要相等。摘要不含自身字段，具体值放Task/Handoff交付记录；未来实现Task先冻结该值。它覆盖全部绑定与设计SHA，避免只修改tracked策略里的source SHA就扩大许可；任何修改须重新冻结/审查并更新常量。格式/EOL差异不改变canonical摘要，重复键不能参与规范化。不得提供自动接受新hash或生产绕过参数。

嵌套类型也精确冻结：路径/ID/SHA/原文/keep为string，tracking为上述string枚举；strict_utf8恒true、utf8_bom为实际bool（当前均false）。行号/byte_length/C0 offset为非负int且拒绝bool；c0_bytes每项仅offset/byte两int，nul_offsets为升序唯一int数组，byte取0..31且不是9/10/13。parser_snapshot仅declarations/errors/warnings三数组；声明对象精确raw/disposition/source_file/locator/normalized/real_normalized六string，错误和warning对象精确code/message/file/locator四键（locator仅原FILE_UNREADABLE允许null）。空parse快照必须三个空数组，不能改用伪造counts。数组的固定ID集合、数量和顺序按样本冻结，不能在未知键内藏新资源。

设计文件与研究facts必须tracked可读、rawSHA等于绑定；研究facts的固定commit中blob也须等于该rawSHA。所有绑定源只读原路径，expected_tracking严格为tracked或untracked且与git ls-files一致；untracked的P22保持untracked，内嵌Owner不作作者证明，不提交/重建/改名。源字节SHA、文件大小、strict UTF8/BOM形态、精确非空白C0列表、lexical与real身份均验证；文件存在且为普通文件，不接受别名、目录替代、dot/dot-dot、glob或路径扩展。发布前复读策略（含已启用broad依赖）/设计/facts/四源原字节；tracking针对这些配置/事实文件及四源，两个引用目录只核存在性/目录类型/real身份，不把目录当tracked文件。复核6个新增guard根real身份，并复核原line227声明的normalized/real_normalized实目标；漂移则全体回滚。

## 3. 一条模板binding，保留两条精确错误之外的一切

template_bindings恰1项，ID HIE-T01；固定origin_file为旧P09 codex-closeout-p19-view-r12.md。字段严格为id/origin_file/expected_tracking/raw_sha256/byte_length/strict_utf8/utf8_bom/c0_bytes/source_guard/fence/rows/parser_snapshot/errors。source_guard为四键abs/normalized/real/keep，keep恒PRESERVE_REFERENCED。所有绝对路径与origin相对路径在真实repo_root下一致，normalized=real，无别名许可。

fence固定open_global_line117/close_global_line239/open_verbatim/close_verbatim/open_raw_sha256/close_raw_sha256/draft_notice_global_line115/draft_notice_verbatim/draft_notice_raw_sha256。rows恰2项，按物理228/229顺序，分别id R25/R26，字段为id/global_line/parser_locator/verbatim/raw_line_sha256；locator恰section line7/8。每行SHA含原EOL；完整原文件SHA优先，定位/围栏/原文再次验证。不得对整个围栏、整个旧Review或其它同名表建立豁免。

errors恰2个完整code/message/file/locator对象，索引中每个恰出现1次；重复/缺失/消息或定位漂移拒绝。使用当前parse_markdown_declarations在新建隔离index对未改动全文重算，必须完整等于parser_snapshot中的全部声明、错误与warning（模板目前1声明/2错误/2warning），不能通过删除两行后重解析来改写其它语义。

特别保护同围栏物理line227/section line6的已识别worktree：其原raw/disposition/source_file/locator/normalized/real完整声明保持，且原index已有相应保护注册；暂存完成后仍能找到同一声明与保护。不得覆盖它、放弃其它可解析内容，或据模板draft身份反推该真实worktree可退出。发布末检必须重新resolve该声明normalized路径并等于冻结real_normalized、同时保留原lexical与real保护；它是第7个有界实目标复检对象，不是第7条新增Declaration，不改变+6/+4效果。

reference_guards恰2项，ID HIE-REF01/02，各为id/origin_file/origin_global_line/origin_parser_locator/path_rel/abs/normalized/real/keep；都绑定HIE-T01物理229/section8，精确保全tools/governance/tests与verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1两个实际目录，keep恒PRESERVE_REFERENCED。目录存在、身份精确，无自然语言路径推断；这两个根当前已保护，只新增独立可审计保护来源。line228不推断具体Task子目录，五广域根整体保护继续有效。

## 4. 三条含NUL原始证据，空声明只在精确字节上成立

raw_non_declaration_bindings恰3项，ID HIE-O01/O02/O03，分别P14 Owner自请质量证据r1/r2及P22 malformed旧Task快照；固定origin集合不能增删。字段严格为id/origin_file/expected_tracking/raw_sha256/byte_length/strict_utf8/utf8_bom/c0_bytes/nul_offsets/source_guard/parser_snapshot/errors。P14 tracking=tracked且keep=PRESERVE_REFERENCED；P22 tracking=untracked且keep=PRESERVE_UNKNOWN，不把unknown作者改为Codex。

P14的NUL offset各[286]；P22为[12330,20486]，其它0x0b/0x0c/0x08精确offset/byte在c0_bytes冻结。直接strict UTF8解码原始bytes，保留全部NUL/C0，不替换、去除、UTF16/GBK猜测、换行归一化或回写。UTF8可解码不表示通用reader可接纳，也不抹去原证据的含NUL事实。

每项errors恰原1个FILE_UNREADABLE完整identity（包括tracked/untracked原消息及null locator），在输入index中恰出现一次。当前parser在隔离新index上读取原始decode文本，必须为0声明/0错误/0warning且与parser_snapshot精确相等；任一新声明/错误/warning、source bytes/tracking漂移，全部拒绝，不产生泛化非声明规则。仅当四源统一验证及整源保全暂存成功，才从输出errors解释该原1项并加入显式warning。read_text等直读API保持原先NUL拒绝，其它含NUL文件仍FILE_UNREADABLE。

未来默认报告不打印原始NUL/C0正文，warning只输出来源、hash、offset/计数、保护与原错误身份；需要展示时用独立JSON转义视图指向原rawSHA，不改原文件也不让转义视图冒充原件。原件审计意义保持：P14不是协议独立Review，P22不是活跃Task/作者归属证明。

## 5. 四源统一原子发布与精确效果

先全部验证：配置/schema/canonical摘要、设计/facts、四源身份/raw/C0/tracking、模板两行/围栏/完整parse快照、三NUL各空parse快照、完整5错误每项唯一、line227既有保护和两个reference根身份。任何身份解析只在隔离index或使用_resolve_identity(..., warn_alias=False)，不得在原index偷偷追加warning或改变_repo_tops。

暂存必须复制declarations/protected及其每项列表/non_protective/errors/warnings/_repo_tops（以及scanned独立dict），原容器不参与注册。恰移除已核5个完整错误，原其它错误顺序/多重集保持。新增6条Declaration：四个source_guard整文件保护+两个reference_guard目录保护，全部用已核abs/normalized/real和冻结keep；不新增destination或DELETE_SAFE语义，不发明新disposition。每条的source_file使用绑定原来源，locator区分policy-id/raw-file或global229/section8/reference-id，以免冒充旧表原行。

新增4条DECL_HISTORICAL_EVIDENCE_PRESERVED warning（每个origin一条）；结构化file=origin_file，locator明确global行/section行或bytes偏移，message同时含mode/policy/origin/locator/该来源rawSHA/keep/解释的原code集合及guard根。模板warning覆盖2个错误及2个reference根，NUL各覆盖1个。原warnings不删不改，不把warning说成旧源已修复。

重新计算scanned计数，再复读所有输入及real/tracking最终检查，通过后一次返回。未来在当前同数据预期errors12→7、declarations+6、warnings+4；当前6个guard根（四源+两个目录）已存在，新增protected根为0；通用断言应为旧集合子集且所有6根在新集合，不把不同快照的root总数硬编码。三个消费者自动共享收口，不新增各自绕过或真实清理许可；七剩余错误继续阻止清理候选生成。

任一验证/暂存/计数/最终复读异常：丢弃全部暂存，原5错误/其它错误、原声明/保护/warnings保持，仅在传入index新增1项fatal，file为拟议policy路径；使用_finish_declaration_scan复制/同步计数。建议沿用GuardError细分类（POLICY_INVALID/POLICY_DIGEST_MISMATCH/POLICY_UNTRACKED/POLICY_MISSING/DEPENDENCY_INACTIVE/GIT_FAILED/SOURCE_DRIFT/RECORD_DRIFT/ERROR_MISMATCH/REAL_DRIFT），意外异常归POLICY_INVALID；不包含原敏感正文。失败数量为“本次输入错误数+1”，不能固定写13（输入本身可能已因漂移不同）。

## 6. 未来实现验证矩阵——全部planned/NOT_RUN

以下是未来另冻实现Task的验收，不是本设计实测。若用合成Git fixture，必须由未来Task明确拥有workspace/agent-output/TMP并授权自清；本设计不创建fixture。测试可在内存mock模块的批准摘要常量以绑定fixture策略，不增加生产CLI/环境变量绕过。

| ID | planned场景 | 必须验证的结果 |
|---|---|---|
| T01 | 当前四源正向 | 只移5完整错误、其余7不变、+6声明/+4warning、旧保护子集且6guard根存在，source字节不变 |
| T02 | 直接read_text/非列入NUL源/其它模板 | 原拒绝保持，不能借全局围栏/NUL开关通过 |
| T03 | absent+untracked / present+untracked / tracked+missing / Git或读取失败 | 前者无作用，其它fatal；原错误与保护不部分改变 |
| T04 | schema未知键/缺失键/错类型/bool version/重复JSON键/ID/第5源/第3reference | fatal，不接受通用配置扩容 |
| T05 | 配置canonical摘要/设计rawSHA/facts rawSHA或固定blob漂移 | fatal；格式/EOL仅影响canonical配置表示时不扩大语义，原件raw规则不放宽 |
| T06 | 四源任一字节/大小/BOM/strictUTF8/NUL/C0集合漂移 | SOURCE_DRIFT或RECORD_DRIFT，保留输入错误全集，绝不转码/剥离 |
| T07 | 源丢失/目录替代/别名/junction/dot-dot/real目标漂移 | fatal；初检/暂存末检均覆盖，无原index warning副作用 |
| T08 | P22 tracking从untracked变tracked或其它源变untracked | fatal，未知作者和源归属不自动接管 |
| T09 | 模板行/locator/fence边界/draft notice/行rawSHA漂移 | 精确拒绝，不忽略整个围栏或文件 |
| T10 | 模板旧line227声明/保护缺失、隔离parse新增声明/错误/warning | fatal，保护不得被解释策略覆盖 |
| T11 | 两reference缺失/real别名/keep更弱或DELETE_SAFE | fatal，原引用目录不失保 |
| T12 | 三NUL隔离parse出现声明/错误/warning，或伪造空快照 | fatal，即使原文件能UTF8解码也不升级为通用文本许可 |
| T13 | 5错误有任意缺失/重复/message或file/locator变化 | ERROR_MISMATCH，不按code宽泛删除 |
| T14 | 第1/第6次注册、warning、计数阶段注入异常 | 无部分声明/保护/warning/错误减少，仅输入错误+1fatal，scanned一致 |
| T15 | 策略/依赖broad/设计/facts/源/tracking、6guard或原line227 real在验证后变化 | 发布前复检拒绝，原输入容器不变，原line227无需新增Declaration也不得失保 |
| T16 | 清理/remove/consolidate三个合成CLI | 同共享scan，七错误继续拒绝，零真实资源删除；canonical全盘另记NOT_RUN |
| T17 | 旧29+80/本前置18加固回归、双事故回放 | 按实现Task必要性冻结并实测0skip；双回放各15REJECT/0deleted/0violations |
| T18 | 前序broad fatal、absent+untracked/no-op但本策略enabled；其它JSON/EVIDENCE_PIN/直读路径 | 前序fatal原样返回；依赖未实际生效时DEPENDENCY_INACTIVE且保留全部输入错误（如24→25，不是19）；两策略均no-op不加错；其它拒绝/69例外/原pins不变 |

## 7. 本轮实际验证与下一Gate

本轮只执行：原四源raw/五完整身份/12错误和旧保护保全、binding字段与当前真实parse/路径/字节一致、canonical摘要计算与EV/check/diff。未来helper、12→7、6注册/4warning与T01–T18运行矩阵均NOT_RUN，不用设计JSON验证冒充已实现安全测试。实际结果另在validation.json和execution.json，快照计数只对应其时点。

DeepSeek对固定head独审；Codex正常集成并复验后可关闭本设计。下一候选为单独实现Task（Owner Codex/Reviewer DeepSeek，限共享scanner尾部+新运行policy+自身tests/E和权威导航），实施前冻结审核后canonical policy摘要、真实branch/base/范围和自有fixture边界，再独审、main复验。原文件永久原位/原字节保留；不重开旧Task、不修P14旧表、不接管P22、不解除r212或远端push；任何缩小保护或真实处置另需用户对象化裁决。
