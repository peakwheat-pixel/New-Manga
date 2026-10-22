# Codex adjudication：H2 source r1

2026-10-13；Reviewer DeepSeek Harness（非作者），session session-bb74c298-dcd7-4db7-bd22-4198854737f3，exit0 / CHANGES_REQUESTED。固定实现831e368b2d564a27859a188e5efa575c8ff7fb7e、文档af151e79043e93d8e71f83886ac8732685310f42。11项输入pre/post SHA全匹配，独立Parser0 errors、pure selftest90PASS/6SKIP；这些不代表源代码符合全部AC。

## 裁决与最小返修

- H2-01 P1 ACCEPTED/OPEN：真实A6精确v2 status getter为3条 `? `、220 bytes，源码冻结 `?? `必然错误。原v2历史223B记录只支持v1式记录语义，仍不能从冻结历史证明完整旧helper argv；保留旧P2-1与先前P3-5限制，不篡改旧记录。
- H2-02 P2 ACCEPTED/OPEN：TEMP==TMP重复id；seq指针虽唯一，Task要求call id也唯一，须路径去重或按语义来源/序号命名，加入判别力纯测试。
- H2-03 ACCEPTED：已知OS exit不得被PostProcess异常改成null，补纯负例，异常仍非零disposition。
- H2-04 ACCEPTED：runtime check必须真实解析到现有raw observation，不能只做prefix；复用既有resolver，dangling须阻塞。
- H2-05 PARTIAL/非阻塞：H1 Task是可变运行文档，不应硬pin其完整live内容导致协调更新即漂移。可在review/source manifest记录其读取时snapshot/hash；v2四文件的固定expected来源可引用已存在的immutable H1 input-verification manifest。禁止把mutable Task伪装immutable执行输入；无需扩大产品范围。
- H2-06 ACCEPTED/须修：contract7明确要求protected/index/source before/after；不是格式豁免。保留frozen source/index前后值，关闭前复读比对；refs身份也必须实际比较top/common-dir与frozen真实仓库，而非只观察不验证。
- H2-07：删除dead rootRecords与仅测试使用的RunId函数可做小清理；StreamWriter构造失败时非零退出+保留空文件+wrapper stderr是诚实失败证据，不要求额外fallback写通道。

## Codex额外已证/必需修复

- CX-01 P2：Get-PathProbeObservation在不存在路径返回无attributes字段，Main摘要在StrictMode抛错。隔离pure fixture已复现；原始证据workspace absent-path-repro.json。WER key缺失分支同样须保持完整字段shape，合法absence不能因摘要取缺失字段崩溃。不得live查询registry/ACL进行测试。
- CX-02 P2：raw base64超过4MiB可省略且相关check仍PASS，与完整raw要求冲突。去掉不必要上限/选项并完整保存，或超限明确fail-closed且不得PASS；不增加配置/旁路。
- CX-03：output/target/protected/source/CWD等固定路径按既有executor AssertChain模式检查ancestor/reparse和排除路径；卷证据须实际ready/NTFS等冻结条件，不能仅靠同一drive-letter推断普通同卷。至少全ancestor reparse检查必须在首次CreateNew前。元数据getter只查task列明路径，不扩张filesystem扫描。

Owner=ZCode，在同一allowlist、同一worktree/session续修，新commit、Parser/pure regression日志/Handoff，再由DSH独立复审。不得live collector。源代码修复不由Codex替作者完成。普通技术授权已存在，无需再次询问用户。

当前结论CHANGES_REQUESTED，live-run proposed、X6/Build/AC仍BLOCKED/NOT_RUN，Technical NOT_SATISFIED/private_registry_absence UNPROVABLE与Owner waiver原值保留。
