# FEA-09-PREREQ-1 Handoff — Source 存储/读取契约冻结（2026-11-03）

- Task：`FEA-09-PREREQ-1`（`done`）；owner/reviewer：DSH / r7 Codex 独立会话 `01a1a0c1-a96a-7331-90e3-db9b3be296c0`。
- base：`6e274dd94c5b64d8fbc3f9d578363d3c502a2b68`；delivery/integration：`24c10567926fb302d9bac6ba63ae92d673cf9e83`（冻结 commit）。
- 复核链：r1 changes_requested（P1×11）→ r2（P1×6）→ r3（P1×3）→ r4（P1×2）→ r5（P2×2）→ r6（P2×1）→ **r7 approved（P0/P1/P2=0）**；报告原字节归档 `doc/reviews/FEA-09-PREREQ-1-r1…r7.md`。
- 冻结对象（17 对象门禁，`verify_pins.ps1` PASS 17/17）：
  - **C-05 v1.1**（UNFREEZE）：referenced 页可见性模式分派 + 三谓词拆分；pin 见 `FEA-CONTRACT-FROZEN-C05.md`。
  - **C-06 v1.1**（UNFREEZE）：Host 铸造型 source-read grant、四维 scope、双侧 Verify、撤销 ACK/失联 fail-closed；pin 见 `FROZEN-C06`。
  - **C-15 v1.0**（草案 v5）：v7 DDL（sources/source_locations/source_versions/source_entries/page_bindings/rendition_cache + pages 两列）、迁移 pre-commit 校验、完整性/可见性/可读性拆分、五读路径、Host Registry 规范、跨存储次序。
  - **C-16 v1.0**（草案 v7）：source-access-wire 1.1（Registry 命令/RegisterSourceReadGrant/密码 DPAPI 短期引用/异步 Plan-Start-Cancel-Receipt/WireLog 前置脱敏/错误码）。
- UNFREEZE 载体：`doc/reviews/CONTRACT-UNFREEZE-2026-11-03.md`（C-05/C-06 v1.0 pin 历史保留）。
- 门禁证据（`verification/FEA-09-PREREQ-1/logs/`）：check PASS(3)、pins 17/17、pin 负测（缺记录/错 pin 均 EXIT 1）、DDL 内存验证 PASS、范围 diff 空、旧 FEA-06 四 PNG 前缀匹配。
- 未覆盖（实现阶段验证）：生产迁移 callback、真实 Host Registry/DPAPI/ACL/跨进程锁、source-read 运行时、ZipCrypto/PDFium 密码路径、真实 PDF 解码、全量产品回归。
- **下一步**：FEA-09 scope-r2（独立上下文；不得由本 Task reviewer 兼任实现）；approved 后 DSH Appointment 实现（建议 owner=Codex）；FEA-09-UI-1 协同 UI 接线。**不 push；不重开 FEA-08。**