# 固定基线与保护证据

2026-10-08 Codex；base=968c8f34601b72667831f1fd15bb20cd2c8f3cb7。
真实git show解析：旧PRODUCTION_EXPECTED=9，旧CS-L1 response期望minor=3。
当前冻结main.rs生产面=15，Core PROTOCOL_MINOR=6，静态实际谓词12项检查EXIT0。
请求minor=3保持作为向后兼容探针；只将返回声明严格期望改为minor=6。

真实旧失败载体：verification/M2-DERIVED-GC-2/g1-g7-matrix.md §G6、
raw/dev-runner-m2rc2.log、raw/packaged-ac5-run/tenth-round-build-and-run.log。
不重写任何旧PASS/FAIL；新验收须使用本Task独立output目录。
本轮初次npm-ci调用使用了错误的相对harness路径，Python报告文件不存在，EXIT1；
没有启动npm或写任何文件。随后改为绝对harness路径，npm-ci EXIT0。
两次functions JS模板解析失败均在执行前报错，没有文件写入；随后修正命令。

提交raw后整体cached diff --check首次报Windows子进程CR/CRCR及空行；
代码/文档范围检查EXIT0。未修改raw原始字节；只在本Task目录.gitattributes对raw/**
使用 -text -whitespace（既有verification/M2-SFX-FINETUNE-PREFLIGHT原文保护先例）。
不豁免代码、判别脚本、Task、Handoff，不放宽产品Gate。后续整体检查实测重新执行。
主仓库实施期间出现他人.qoder-credits未提交内容，保留且不纳入本Task提交。
