# M2-FIX-F02-RESOURCE-CHANNEL-FLAKY Release Evidence — release base `2b81f91c`

- 日期:2026-09-29 03:0x Asia/Shanghai(编排会话,Goal G2 持续推进)
- 释放裁决:Codex(代行,ZCode 会话,用户授权 2026-09-28);依据=LISTBOOKS 集成实测 f02 默认线程两侧首跑均复现(200 vs 400 @main.rs:821)+单线程绿——资源通道「等长重写拒检」安全语义存在真实并发缺口(mtime 短路假设待诊断实证);修复价值=产品安全语义+测试稳定。**代理裁决,用户可撤销。**
- Task:[M2-FIX-F02-RESOURCE-CHANNEL-FLAKY](../../doc/tasks/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY.md);kind=fix(诊断+修复,纯 Rust 侧);base=`2b81f91c`(LISTBOOKS 收口 commit)
- branch=`agent/zcode/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY`;worktree=`G:/CODEX/New Manga.worktrees/M2-FIX-F02-zcode`(从 release commit 检出)
- Owner=ZCode(子 agent 代行实现);非作者 Reviewer=DeepSeek Harness;Integrator=Codex(另一子 agent,保持 Owner≠Integrator)
- 冻结:诊断实证先行(AC1,60 分钟时间盒+降级路径);预期修复=移除 digest 短路每请求全量重验(性能注记录入);f02 语义保持(重写后必须 400);Python 面零改动
- 证据链:`verification/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN/integration-b6cb1af2/integration.md` §2 裁定 1、cargo-test 日志三连记录
