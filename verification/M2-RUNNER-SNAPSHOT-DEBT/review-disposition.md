# DSH r1 处置（任务仍BLOCKED）
2026-10-08；真实CLI EXIT0；session-dbe4f574-2377-4302-885a-1f4cba2ae9f9。
精确工作区会话挂载EXIT0；desktop下次启动后可发现，本轮未重启，web_visibility=unverified。
报告原文按final.text UTF8入Git；完整blob原字节SHA见review-binding.log。
r1 reviewed_head=7556cb2d；代码approve_with_conditions，0P0/P1/P2；
整个Task blocked / AC4 FAIL / AC6未集成，Code approval不能代替完整Gate。

C1/F04：git diff --name-only cfb5d2ee 7556cb2d、实际rev-parse已落盘，只有文档/证据，
raw构建HEAD=cfb一致；后继RC2只改docstring，AST等价已断言。
C2/F01：改为从释放Task/M2-C1 rev1.8 §5手动固定的独立15条oracle，分别比对Rust与runner，
不能从被测实现/回包动态生成期望；F02 capability/error/status四个负向新增，
最小实际谓词检查现在16项，父侧EXIT0。
F03：probe混入用例只是等值多项拒绝；另有真实probe公告反向校验，声明不夸大。
C3/F05：旧run_app没有单次起止/timeout分支日志，精确退出时间线无法事后重造，改UNKNOWN；
DLL/详细时间线交候选只读诊断，本轮没有伪造超时分支PASS。
F06：明确PS7省略Force，仅走skip-existing路径的模型hash/copy；未重跑PyInstaller。
F07：补RC2 usage/output-dir及fresh lab文档串。
C4：DSH误写scratch违背只读指令，报告主动erratum；确认自有raw路径/唯一marker，
按其作者明确清理说明移除单一scratch，无用户或其他Agent文件删除。
r1报告内部F17编号及21/21完整Gate建议原文保留；实际应为26个完整场景，
当前21个报告=20PASS/1FAIL，另5NOT_RUN，不放宽到21项。
后续r2只复核有界修正，不重复或豁免AC4；Task不合并实现，不done。

## r2：有界纠正未能批准新head

reviewed_head=41d77f98；原报告doc/reviews/M2-RUNNER-SNAPSHOT-DEBT-41d77f98-dsh-r2.md，
C2/C3/C4 fixed，C1 partial/unverified；N1 P2需补准确新head完整name-only和AST命令日志，
N2 P3标签精度、N3 P3顺序来源、N4 P3最新16项指针已修，N5 P4原报告编号问题原文保留。
R1_REPORT_UTF8_GIT_BLOB_SHA256指Git blob内容字节的SHA256，不是Git对象ID（SHA1）；
既有标签未改写原绑定日志，新日志将字段明确为REPORT_CONTENT_BYTES_SHA256。
Oracle是人工固定release base main.rs的有序面，M2-C1冻结membership而非wire行顺序；
它不从当前被测runner/公告实时提取，可以检出runner与runtime同时漂移。
固定本轮代码head后另加只读绑定证据commit，审查head与evidence_commit分列。

## DSH r3 最终有界复核（2026-10-08）

固定 reviewed_code_head=2af6b71aa06979b822e543b221aaf3a2d5f01abe；evidence_commit=653a00628e484ecb8ae023f2594b80233bce4e9a。
真实CLI EXIT0；session=session-f303c70c-9bcf-4db2-b356-1f4794458d0b；原始报告
doc/reviews/M2-RUNNER-SNAPSHOT-DEBT-2af6b71a-dsh-r3.md。DSH只读静态复核，零重跑；
有界代码批准，0P0/P1，列4个非阻断P2收尾；不等于Task批准，AC4 FAIL、AC6未集成，Task仍BLOCKED。
P2-1/2/3父侧实际补raw/review-binding-r3-supplement.log（EXIT0）：6af→653父子和全路径、
原始bytes SHA256（旧verified日志hash由text归一化计算，原文保留）、release968 Rust源码hash
及968→cfb Rust零差量。P2-4 Handoff AC3改指r3的16项日志。补充未重跑产品Gate。
下一步仍为单独释放DSH只读DLL诊断；不继续范围外实现、不合并runner。
