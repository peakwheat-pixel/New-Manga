# P02两份NDJSON：非声明身份与既有例外适用性

基线50d784300；冻结f08f5c44c、认领2cda9366f。仅只读研究，原日志/guard/正式例外表不变；父Task blocked、STATUS/r212禁令不变。R23未跟踪不提交，R24已跟踪不改写；两原始日志在本Task Manifest显式PRESERVE_REFERENCED。

## 身份核验

|项|原始SHA-256|值数/类型|
|---|---|---|
|R23|bdabb170f9a415dd42855a0978fe557cae4ca1df97466ca143750b1ae288f7a1|6值：meta1 / observation4 / closed1|
|R24|caac6afde8d479cabcd839e2b74fdd86a1ecd8b59e5e8c88100a552382a9458e|64值：meta1 / observation62 / closed1|

每个非空行均解析为单个JSON值，全部内容按行消费；meta.schema=P02-NEW-TIME-BASELINE-collector-1，outputRule说明CreateNew NDJSON。逐值调用当前parse_json_declarations均0声明/0错误，递归核对其两种资源节点签名也0匹配。不是“无path/pin字符串”：path键54/184、disposition各1，但没有source_path+disposition(_original)或resource_type+path+disposition组合。选定pin相关字段有18/28个路径状候选字符串、各保留8例，非完整引用清册。日志及内部引用保留历史证据价值；未读取这些目标、未证明它们全已保护或可删除。详identity-proof.json。

## 机制与实测

load_json_exceptions要求path、64位sha256、reason，并核对原文件存在且raw SHA匹配。scan_repo_declarations在JSON解码之前匹配并绕过整文件；这是对人工核定的非声明内容的信任，不自动验证其语义。不能按文件名/后缀/任意JSON_PARSE或NDJSON批量豁免。

|调用（全部只读）|实际结果|
|---|---|
|正式默认配置before/after|32错误，完整错误身份相同|
|workspace候选保留67条＋仅本两项|30错误，仅R23/R24移除，其余30完整身份不变|
|R23候选路径错配|31错误，R23仍fatal|
|R23候选hash错配|31错误，R23仍fatal|
|R23内存字节加换行漂移|31错误，旧hash不再匹配，R23仍fatal|
|R23内存改为合法资源声明|不适用旧hash，实际注册资源声明，其余30错误不变|
|刻意给合法资源字节登记新hash|该声明被绕过：证明配置的内容审查信任边界，绝不是安全PASS或登记批准|

六候选/负例及默认before/after未调用apply，各例原保护集合不减少（快照1704根；当时本Task的原日志声明尚受表格断行问题影响，修正后另验）。路径错配是候选条目错配，字节变化是内存io.open替换，并非真实改名/编辑源。四输入（两日志/guard/正式表）raw SHA及Git状态不变，受控扫描期间Git状态快照不变；98heads/136worktrees不变。mechanism-proof.json记录完整原32错误、六case结果和探针hash；probe-source.py.txt是实际workspace探针字节快照，只供审查，不要求Reviewer执行（会写自身产物）。probe-run.log为LF转写副本，workspace保留原stdout；双hash见manifest-provenance.json。

初次workspace探针的io.open mock未排除subprocess整数文件描述符而TypeError，未完成全套；仅修探针类型检查后完整复验EXIT0。probe-first-attempt.json记录原因，失败原探针保留workspace。无guard/source实现修改，无同失败盲重试。产品/构建回归NOT_RUN；机制正反例已实际执行，不等同产品测试。

## 历史表不可原地追加

当前DEFAULT引用旧Task的EV-JSON-EXCEPTIONS（doc/tasks/WORKSPACE-DECLARATION-REMEDIATION-1.md:125），Git blob cacd1c021的SHA=c2f185fb489e4b89be28cdfb139eb649c7022a718d0d27877be4ca0d8fa4adc4，67项。工作区磁盘raw SHA=238039dd3a9a70243ff8ffaee8dbf5b080e211cb8dc747de1a5da29211efdef2，因既有CRLF不同；转LF等于blob且Git状态空。首次报告生成的raw==blob断言因此失败，已明确区分两者，未改源或旧pin，不能宣称磁盘raw等于历史pin。manifest-provenance.json保存实际事实。

技术结论：两份固定字节日志可作为既有机制的精确候选，当前未登记，正式错误仍32。后续若释放独立Task，最小方案是新建tools/governance/non-declaration-json-exceptions.json作为版本化当前配置（逐项保留旧67＋两精确条目），仅切换clean_workspace.py的DEFAULT_JSON_EXCEPTION_MANIFEST。旧表/旧Task/pin/原日志均原样保留；不改解析逻辑、Schema或通用匹配。新配置和默认入口写入超出本研究范围，尚未实施。

后续验收须独立Review固定head、新默认实际仅32→30、其他30身份与原保护集合不丢、旧67逐项完整、路径/hash/字节漂移拒绝、真实声明解析成立、四原输入raw状态及旧pin保全、治理check。任何内容/归属漂移拒绝自动刷新hash。候选批准不解除保护，不批准清理/父Task done/只剩main。

R1更正：10 EV行以及两个原日志保留行前有空行，未实际进入guard保护；本Task已仅修表格连续性，实际注册证据见table-registration-proof.json。原10条pin内容与原文件字节不变；旧checkpoint作为历史SOURCE_PIN保留，当前恢复点切换checkpoint-r2.md。新增证据的pin会在复审元数据提交登记，不宣称旧1704快照已包含这些实际保护。本次未扩大到已关闭Task；其证据表是否同类问题需另行有界核验，不能仅凭check.ps1 PASS推断保护注册。
