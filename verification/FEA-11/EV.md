# FEA-11 EV（证据索引）

生成：2026-11-05，代码/文档 head `3e675de59`（DSH）。状态：r7 复审前；`canonical_evidence_status: pending`（待 r7 approved + 集成提交后回填）。

| ID | AC | 证据文件 | 状态 |
|---|---|---|---|
| EV-AC11-1 | AC11-1 | verification/FEA-11/AC-MATRIX.md + logs | PARTIAL（定时/watcher → SCAN-1；本卡两条路径已测） |
| EV-AC11-2 | AC11-2 | AC-MATRIX + tests/fea11 | MET（仅 Core seam） |
| EV-AC11-3 | AC11-3 | AC-MATRIX + tests/fea11 | PARTIAL（pixel profile → MATCH-1） |
| EV-AC11-4 | AC11-4 | AC-MATRIX + tests/fea11 | PARTIAL（并发/DB/第三区域 → AC4-GAPS-1） |
| EV-AC11-5 | AC11-5 | AC-MATRIX + tests/fea11 | PARTIAL（lineage 读隔离 → LINEAGE-1） |
| EV-AC11-6 | AC11-6 | AC-MATRIX + tests/fea11 | PARTIAL（folder relink 一律 typed 拒绝；跨卷/重排证据缺） |
| EV-AC11-7 | AC11-7 | AC-MATRIX + tests/fea11 | PARTIAL（诊断接线后续） |
| EV-AC11-8 | AC11-8 | AC-MATRIX + tests/fea11 + Host.Tests | PARTIAL（Host 自签授权 → HOST-AUTH-1；崩溃点杀进程 NOT_RUN） |
| EV-AC11-9 | AC11-9 | AC-MATRIX + Fea11SourceIpcTests | PARTIAL（Core 直连证据；Host E2E/旧键不可变未覆盖） |
| EV-AC11-10 | AC11-10 | 本目录交付件 + logs | PARTIAL（r7 复审 + 集成后定稿） |

## Canonical evidence 日志

| 文件 | sha256 |
|---|---|
| `verification\FEA-11\logs\dsh-C6-final.log` | `11f1ddca340fd7f5e7623b4bcde46fc1a4f26776e3a7bd8c451c6882e0325ac9` |
| `verification\FEA-11\logs\dsh-C6-gates.log` | `efc283ec3f1acb54c899de33c97647126b9193e421b97de6e424db3bd783f30a` |
| `verification\FEA-11\logs\dsh-C6-r2.log` | `dc67366002fdd80963164ce498739ecdae03bd9d2637580bdca8ea6cf516c405` |
| `verification\FEA-11\logs\dsh-C6-r3.log` | `16e5ee9ef0c34a97c19512ee9eb1cd1bbe9853031a4573d0756d84f3a3a21407` |
| `verification\FEA-11\logs\dsh-C6-r4.log` | `fe9bba66425714c267e0e618b64893034f039f3dad251bb2f774de428ebd6e4d` |
| `verification\FEA-11\logs\dsh-C6-r5.log` | `e1f6ecba079208a0da3a1c99a58d0e22bff47b91be2bf77761e848f66816051f` |
| `verification\FEA-11\logs\dsh-C6-r6.log` | `87268285cee1017fbc6babcc52b94c74b43766e039bd458bcdd90bf04807891f` |
| `verification\FEA-11\logs\dsh-phaseB-main.log` | `9046e7caa61c49724f7b3ddbd67edde787dd27791ecb7d1c27e61d2a572e7256` |
| `verification\FEA-11\logs\dsh-phaseB-providers.log` | `63f3e76f9022247e78f5233d4553b987dacf1fceb5a0da00c19e73851070a4fb` |
