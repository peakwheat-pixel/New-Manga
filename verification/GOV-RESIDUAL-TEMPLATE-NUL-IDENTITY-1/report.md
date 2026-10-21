# 五项历史模板与NUL身份研究

当前canonical main基线951b7c61f，范围冻结/实际branch base cc72f6a822f0c7823a50996d9e43674147bc7b4a。只读核当前12中的R25/R26/R27/R28/R32，匹配既有32矩阵的完整code/file/locator/message与源rawSHA。五项涉及四源，四个SHA与旧矩阵一致；未修改任何源、旧pin或工具。具体逐字节证据见source-facts.json；audit_identity.py只读/stdout，内含断言，不产生fixture或派生原文。

## 模板两项

R25/R26：旧Review verification/P09-GOVERNANCE-DEBT-20261019/codex-closeout-p19-view-r12.md rawSHA dcc528c1dd803961e55e42d34ba7ed14232089fedc1673f87eadc825b4970baa，tracked且磁盘原字节等于HEAD blob（rawSHA保持不变）。物理line228/229，scanner locator为内嵌section相对line7/8。原文line115明确这是待正式注册、尚未落盘的Task payload；四反引号围栏117..239包围整个草案。不是该旧Review发出的实际资源处置声明。

两行分别含“workspace对应Task子目录/NOT_APPLICABLE或按实核实”和“本Task两个目录”的占位/复合自然语言，不能据此生成具体路径或处置权限。line227的同围栏实际精确worktree已被当前parser登记为PRESERVE_UNKNOWN，必须继续保护；不能泛化忽略围栏或排除整个Review。scanner section_text仅匹配##标题且不感知围栏，故命中内嵌草案，而非前面的###叙述标题。当前对该文件独立内存parse实际1条保护/2错误/2warning，不移除已登记保护。

后续候选仅为精确原文件rawSHA+两行rawSHA+全局/section locator+围栏范围+完整错误identity的历史模板解释设计，原文件全量原位保护、原line227保护与其他表扫描保持。line229提到的tools/governance/tests/和verification/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1/是明确参考目录，可在设计中补充精确保全，不能把整行自然语言当路径；line228不能猜具体Task目录，workspace五广域根继续整体保护即可。本Task不登记运行例外、不改scanner、不消除两错误。

## NUL三项

P14两文件是已有BL-18更正的Owner自请DSH会话/子Agent自批判证据，明确不是协议独立Review。严格UTF-8可解码，各仅byte286（zero-based，物理line3）一个NUL，位于会话简称之间。不是UTF-16误编码；不能简单转码/去NUL，也不能恢复为独立Review。rawSHA分别df4de2411355fe050593b170a4b8602d95c87a716abe3686a416b574a80e0608和122b34494203dbd8557565affc3113182844c0b987251a8757c134515837626a；磁盘字节等于HEAD blob。最后Git改动263e0ec2fea10dce638e43797e99567019668424仅证明提交链，不等于实际Agent作者。

当前doc/tasks/P14.md line133/134明确SOURCE_PIN与上述SHA。但其行与主表被空行/说明隔开且没有新表头，当前scanner未将两个文件注册保护。基线原1865保护集合中四源均无精确根，不能用“文档里写了pin”冒称保护已注册。本研究只在自己的Resource Manifest补四个原位精确保留项（不修改旧Task/pin）；新增保护实际注册后四源均受保护。P14旧表结构完整修复仍未释放，不顺带改变其它历史pin。

P22文件是untracked历史malformed Task快照，rawSHA 7ebd7d40e7334c9422f4bf126a29b3d0f49300e2bdbac86cedfdb1ed74ee98c9，与doc/tasks/P22.md line95的精确保留记录一致；其内嵌Owner/branch/status不是当前授权或实际文件作者证明。两个NUL在byte12330/20486（line91/205）；另有非空白C0控制字节0x0b、0x0c、0x08，详见JSON精确offset。当前Task的原说明确认错误插值/控制字符快照已保留并重建live记录；本研究不推断快照实际写入者或把它当活跃Task。原样PRESERVE_UNKNOWN，不能提交、重建、去控制字符、改名、覆盖或删除。

三份严格UTF-8原文仅在独立ProtectionIndex内存调用现有parse_markdown_declarations，实际各0Declaration/0error/0warning。此为“当前四个标准section/表语法未识别声明”的有界实测，不证明没有任何审计/用户内容，也不将含NUL字节发布到正式reader；当前read_text仍先拒绝NUL，三FILE_UNREADABLE保持。若未来精确解释，应设计原文件raw身份绑定、整源保护和显式可审计视图/opaque策略；识别出新声明、任意字节漂移或未核来源时fail-closed，禁止通用NUL剥离、UTF16猜测或verification全局豁免。

## 验证、边界与推荐

audit_identity.py实测完整5错误多重集/4源rawSHA/严格UTF8/原NUL与C0位置/围栏117..239/全部正式12；有界引用只读P14/P22现有Task相应行及已引用32矩阵/source事实，没有通扫历史。七个历史运行身份仅留在remaining_seven，不重新推断实际路径/价值/处置，不修改其来源。全量进程/文件句柄占用未证明，本研究不做资源退出，标NOT_RUN，不据此认定安全删除。

前后正式12完整identity不变、原保护集合不减；自己的新证据/Task声明只增加保护，四源raw不变，详见preservation-validation.json（快照计数）。check.ps1与diff-check、EV raw/blob/pin和实际登记独立记录。产品构建/旧127测试/CLI真实apply/全101分支139WT完整盘点均NOT_RUN；没有实现变更，不需重跑产品或加固套件。当前101heads/139WT（本研究新增1/1，全部保留），父blocked、r212与五广域根整体保护不变，尚未只剩main。

下一最小范围建议：Codex另冻这五项的“精确历史证据解释设计”，DeepSeek独审；仅设计schema/来源绑定/原子保护/拒绝矩阵，不实现、不修改旧源、不解除清理禁令。两类模板与三类原始证据分开验证，原始文件永久保持原字节；untracked快照writer UNKNOWN不因研究而接管。若设计需要改变源字节、取消原保护或真实清理，必须另列对象/证据/影响请求用户裁决；当前不申请此类授权。
