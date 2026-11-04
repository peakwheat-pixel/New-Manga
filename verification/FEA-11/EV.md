# FEA-11 EV（证据索引）

生成：2026-11-05，HEAD `ed5b29482`（DSH）。状态：待 Review r5 / DSH 集成验证后定稿。

| ID | AC | 证据文件 | 状态 |
|---|---|---|---|
| EV-AC11-1 | AC11-1 | verification/FEA-11/AC-MATRIX.md + logs | r4-rework |
| EV-AC11-2 | AC11-2 | verification/FEA-11/AC-MATRIX.md + logs | r4-rework |
| EV-AC11-3 | AC11-3 | verification/FEA-11/AC-MATRIX.md + logs | r4-rework |
| EV-AC11-4 | AC11-4 | verification/FEA-11/AC-MATRIX.md + logs | r4-rework |
| EV-AC11-5 | AC11-5 | verification/FEA-11/AC-MATRIX.md + logs | r4-rework |
| EV-AC11-6 | AC11-6 | verification/FEA-11/AC-MATRIX.md + logs | r4-rework |
| EV-AC11-7 | AC11-7 | verification/FEA-11/AC-MATRIX.md + logs | r4-rework |
| EV-AC11-8 | AC11-8 | verification/FEA-11/AC-MATRIX.md + logs | r4-rework |
| EV-AC11-9 | AC11-9 | verification/FEA-11/AC-MATRIX.md + logs | pending |
| EV-AC11-10 | AC11-10 | verification/FEA-11/AC-MATRIX.md + logs | pending |

## Canonical evidence 日志

| 文件 | sha256 |
|---|---|
| `verification\FEA-11\logs\dsh-C6-final.log` | `11f1ddca340fd7f5e7623b4bcde46fc1a4f26776e3a7bd8c451c6882e0325ac9` |
| `verification\FEA-11\logs\dsh-C6-gates.log` | `efc283ec3f1acb54c899de33c97647126b9193e421b97de6e424db3bd783f30a` |
| `verification\FEA-11\logs\dsh-C6-r2.log` | `dc67366002fdd80963164ce498739ecdae03bd9d2637580bdca8ea6cf516c405` |
| `verification\FEA-11\logs\dsh-C6-r3.log` | `16e5ee9ef0c34a97c19512ee9eb1cd1bbe9853031a4573d0756d84f3a3a21407` |
| `verification\FEA-11\logs\dsh-C6-r4.log` | `fe9bba66425714c267e0e618b64893034f039f3dad251bb2f774de428ebd6e4d` |
| `verification\FEA-11\logs\dsh-phaseB-main.log` | `9046e7caa61c49724f7b3ddbd67edde787dd27791ecb7d1c27e61d2a572e7256` |
| `verification\FEA-11\logs\dsh-phaseB-providers.log` | `63f3e76f9022247e78f5233d4553b987dacf1fceb5a0da00c19e73851070a4fb` |

## 说明

- AC11-1/3/4/5/6/7/8/9/10 为 PARTIAL（承接：SCAN-1/MATCH-1/AC4-GAPS-1/LINEAGE-1/HOST-AUTH-1 或 limitation），不得在 closeout 前标 MET。
- 全量门禁：`verification/FEA-11/logs/dsh-C6-r4.log`（pytest 3048/0/10、.NET 1359/0/78、IPC 3/3、check、pins）。
