# 剩余32项声明：只读取证结论

范围基线c0a9cb7962669cb4e987af51260f68850f4fe3b0；冻结1681489e8、认领049fe5aa0。Codex取证，DeepSeek独立审查；父收敛blocked与STATUS/r212禁令不变。scope.json冻结32错误，对应17来源。没有重开历史Task、没有修复历史声明/工具代码。

|分类|错误数|处置边界|
|---|---:|---|
|格式/非资源说明进入路径列|6|未来精确文档修订候选；不扩展自然语言路径识别|
|宽泛根source/destination成对|12|6条声明、5唯一根；全部广域保护保留，不按错误数计资源|
|历史身份/枚举/同源标记|7|不能按当前TEMP/APPDATA或目录名还原历史，未知/用户数据保留|
|Review内嵌历史Task模板|2|不是冻结资源身份；不排除整个Review或verification|
|NDJSON日志流|2|R23共6值（1 meta/4 observation/1 closed），R24共64值（1/62/1），完整消费；不重写为单JSON、不运行旧collector|
|含嵌入NUL的Markdown|3|UTF-8可解码但含1/1/2个NUL；原字节/pin不动，不冒称独立Review|

完整逐条矩阵为matrix.json/matrix.md：保留原code/file/locator/message，同时单列实际定位、可证实署名、raw SHA、保护影响、最小建议及授权边界。source-facts.json记录原始指纹及有界摘录，direct-reference-facts.json记录5个直接引用。真实文件作者UNKNOWN时不以嵌入Owner或Git用户名替代证明；两项未跟踪来源原样保留，不提交。

判别事实：

- P02两个流meta.outputRule自述CreateNew NDJSON，内存逐值消费R23共6个NDJSON值（meta=1、observation=4、closed=1）、R24共64个值（meta=1、observation=62、closed=1）；检查resources/resource_type/source_path/destination_path/resource_manifest/resourceManifest键命中0。此项仅是精确路径+raw SHA非声明例外的研究候选，不是已批准例外，也不保证其它未检查语义。
- P14两文件各byte286一个NUL，已有抬头明确不是独立Review；P22未跟踪malformed快照两个NUL偏移见source-facts.json。不是UTF-16整文件误解码，不去NUL/重编码/改源。
- R30/R31原错误locator为disposition，实际环境路径位于resources[2/3].source_path。矩阵同时保留原locator及实际pointer；直接引用只有四个相对文件/hash，无法证明历史绝对用户根。
- R29精确Same标记的旧Task只授权check.ps1，不覆盖clean_workspace.py；源仍是多路径描述，不能只消destination错误。
- 3项跟踪来源磁盘raw与base blob因既有CRLF/LF差异不相等：P09-MANAGED-READ-ROOT-TRUST-1、ENV-BUNDLE-1-FU1清单、P19-UI-FIX-1清单；规范换行后相等且Git状态空。仍分别记录原始字节SHA，绝不以归一化字节替代pin。其余跟踪来源raw相等；2未跟踪来源无base blob。

验证见preservation-validation.json：17来源原字节与逐源Git状态不变，修正报告引用形式后审计exit2、原32项完整错误身份多重集合相等，98 heads/136 worktrees不变。初始审计曾为36项（版本外保留一份失败输出）：本Task将原资源对象结构化引用造成4条重复声明；已将本Task观察字段改为原文字符串并保留失败证据于agent-output。没有忽略源声明或改guard。所有原32项继续fail-closed。

产品/工具回归NOT_RUN（无代码变更）；未全扫历史、未打开用户DB、未做占用释放或恢复演练。没有apply/删除/迁移/归档/GC/prune/push/ACL操作。取证完成不解除保护，不证明错误已消解或父任务done。

推荐下一步：Codex另冻“2个P02 NDJSON非声明身份核验”Task，DeepSeek独审。先验证精确path+raw SHA机制及负例/漂移拒绝，原日志不动、禁止通用坏JSON忽略。此为建议未释放；涉及工具/例外表写入必须另行冻结allowed_paths与语义审查。广域根和历史身份仍待精确裁决，清理禁令不解除。

R1记录修正：R23未跟踪，R24已跟踪，二者不可混写；NDJSON数值为对象总数及分类型计数。R30/31两个record共享同一用户数据source_path；区别在destination是否隔离副本，不代表两个用户源根。初始失败只有一份输出可供独立核验，不宣称两份失败记录。
