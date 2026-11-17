---
id: LICENSE-VARIANT-DECLARATION-1
title: base 变体声明 GPL-3.0-or-later 却内置 632 MB 权重 —— 需用户选向（AGPL 声明 / 移除权重）
kind: fix
governance_version: 3
status: closed_with_limitations
disposition: "ZCode 裁定（doc/reviews/ZCODE-RULING-INSTALLER-LICENSE-2026-11-17.md）：现声明非法；Q2 定为 P0 发布阻塞。合法出口只有 ①保守声明 AGPL-3.0 ②移除权重回归 base。方向取舍属用户产品裁决，DSH 不自裁"
approval: DSH 2026-11-17（由 ZCode 裁定触发；方向待用户决定）
suggested_owner: DSH
owner: DSH
reviewer: reviewer-lvd（DSH 子 agent，独立上下文；2026-11-17 收口复核）
depends_on:
  - INSTALLER-MATRIX-1
  - INSTALLER-METADATA-CONSISTENCY-1
  - VERSION-JSON-GUARD-ALIGN-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: 02c3aaeda
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/LICENSE-VARIANT-DECLARATION-1
allowed_paths:
  - doc/tasks/LICENSE-VARIANT-DECLARATION-1.md
  - doc/reviews/LICENSE-VARIANT-DECLARATION-1-*.md
  - doc/reviews/ZCODE-RULING-INSTALLER-LICENSE-2026-11-17.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/LICENSE-VARIANT-DECLARATION-1/**
---

# LICENSE-VARIANT-DECLARATION-1：许可证声明与随包权重不相容（阻塞：等用户选向）

## 已定的裁决（ZCode，2026-11-17，全文见 `doc/reviews/ZCODE-RULING-INSTALLER-LICENSE-2026-11-17.md`）

- **不得**声明 `GPL-3.0-or-later`：判定规则 R1–R4 顺序执行，本案落在 **R4**（随包权重三项台账均为「待核实」）。
- 合法出口只有两个：
  - **方向 A**：保守声明 **AGPL-3.0**（可立即执行），并同步 `NOTICE.md` 变体表 / `LICENSE_AUDIT.md` / `THIRD_PARTY_LICENSES.md §3` / `installer.nsi` 许可页文案；variant 与 stage 命名对齐；由 `package.ps1` **干净重建**，禁止手工补 `VERSION.json`。
  - **方向 B**：**移除权重**回归真 base，维持 `GPL-3.0-or-later`，`NOTICE` 小改即可。
- 随包 `NOTICE.md` / `LICENSE_AUDIT.md` 与实物矛盾 = **P0 发布阻塞**（对接收方的虚假合规披露）。
- 权重上游许可的**法律属性证据不足**，ZCode 与 DSH 都不认定。

## 为什么 blocked（而不是 ready）

方向 A 与方向 B 是**产品取舍**（是否随包分发 632 MB 权重），ZCode 裁定明确「方向取舍属用户产品裁决」。
DSH 按「需要人工裁决交 Codex/ZCode」的授权只能拿到**规则**，不能替用户选向 ⇒ 本卡等用户一句话。

## 用户只需回答一句

> **保留权重随包（走 A：声明 AGPL-3.0）** 还是 **移除权重（走 B：维持 GPL-3.0-or-later）**？

## Acceptance Criteria（选向后按分支执行）

- [x] **AC1 选向登记**：把用户的选择（A 或 B）与本裁定书链接写进卡面。 <<MET>>
- [x] **AC2 声明一致（A）**：`NOTICE.md` 变体表、`LICENSE_AUDIT.md`、`THIRD_PARTY_LICENSES.md §3`、`installer.nsi` 许可页四处**同时**改为与实物一致；或 <<MET>>
      **AC2'（B）**：从 base stage 移除 `app/core-sidecar/models/` 并用 `package.ps1` 干净重建，`NOTICE` 只做小改。
- [x] **AC3 生成器自证**：改后由 `package.ps1` **干净重建**（禁手工补字段），`verify-package-manifest.ps1` **EXIT=0**。 <<MET>>
- [x] **AC4 判别力**：旧 stage（声明 GPL + 632 MB 权重）在新护栏下仍被拒；新 stage 通过；两者证据并列。 <<MET>>
- [x] **AC5 不越界**：不改护栏检查集合；不宣称条件 4 通过；不覆盖旧 stage 字节。 <<MET>>

## 允许修改范围

- 本卡、`doc/reviews/LICENSE-VARIANT-DECLARATION-1-*.md`、`verification/LICENSE-VARIANT-DECLARATION-1/**`。
- 选 A 时：`NOTICE.md`、`apps/desktop-avalonia/docs/LICENSE_AUDIT.md`、`THIRD_PARTY_LICENSES.md`、`packaging/nsis/installer.nsi`（仅许可页文案）。
- 选 B 时：`packaging/**` 的权重取舍与 `NOTICE.md` 相应行。

## 禁止范围

- 不得放宽 `tools/ci/verify-package-manifest.ps1` 的检查。
- 不得用「加一句免责声明」替代许可声明与实物一致。
- 不得在本卡内认定上游许可的法律属性（证据不足）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 记录用户选向 | 用户决定 | NOT_RUN | 无 |
| AC3 | `package.ps1` 干净重建 + 护栏 | clean worktree、sidecar 需先重建 | NOT_RUN | 无 |
| AC4 | 旧/新 stage 各跑护栏 | 同上 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- 依赖 `INSTALLER-MATRIX-1`（stage 来源）、`INSTALLER-METADATA-CONSISTENCY-1`（护栏）。
- **阻塞**：等用户选向（A/B）。
- **风险 R1**：方向 A 需要四份合规文件同时改，任何一处漏改仍是虚假披露。
- **风险 R2**：`package.ps1` 干净重建需要 sidecar 的 `build-manifest.json`（如缺失需 `build_sidecar.ps1 -Force`，重活）。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无（须独立上下文）。
- 实际测试：尚无。

## 2026-11-17 追加：ZCode 第二次调用的两条可用修正

（第二次调用的正文被截断，只有 236 字符前导段；原文见 `doc/reviews/ZCODE-RULING-INSTALLER-LICENSE-2026-11-17.md` 末节。）

1. **`app_build` 缺口已修**（`VERSION-JSON-GUARD-ALIGN-1`，实测 `package.ps1 exit=0` → 护栏 `OK / EXIT=0`）⇒ 不再是本卡的依赖障碍。
2. **`packaging/nsis/installer.nsi` 有 4 处硬编码 base/GPL 文案**（DSH 已核实行号）：
   - `:60` `VIAddVersionKey "LegalCopyright" "GPL-3.0-or-later (base) / AGPL-3.0 for the models package…"`
   - `:72` `MUI_WELCOMEPAGE_TEXT "本安装包为 base 变体（不含模型权重，按 GPL-3.0-or-later 分发）…"`
   - `:73` `MUI_LICENSEPAGE_TEXT_TOP "base 变体整体按 GPL-3.0-or-later 分发…"`
   - `:103` `FileWrite $InstallLog "variant=base (GPL-3.0-or-later; unsigned)…"`

   ⇒ **方向 A 下必须同时改这 4 处**（把「base/GPL」改成与实际变体一致），否则安装向导与安装日志仍在对接收方作错误声明。
   这使得 AC2 的范围从「四份文档」扩到「四份文档 + `installer.nsi` 四处」。

## 仍缺：方向选择

DSH 已按用户授权把选向交给 ZCode，但第二次调用**正文截断**，未取得 A/B 结论。本卡继续 `blocked`；下次调用改用不带 `--json` 的输出或更短提示词。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) | sha256_basis |
|---|---|---|---|---|---|---|
| EV-LVD-01 | AC1–AC5 证据说明（含 ZCode DECISION=A 原文） | verification/LICENSE-VARIANT-DECLARATION-1/README.md | 02c3aaeda | 5fe45b10d451b7e9ae8659a412cfa36bea7fd489090e57765cd20d5b979e1129 | CANONICAL | BLOB |
| EV-LVD-02 | AC3 models 变体 VERSION.json（AGPL-3.0） | verification/LICENSE-VARIANT-DECLARATION-1/ac3-models-version.json | 02c3aaeda | d6d623ff4e09c3f518804733c57efd9ad3a1ed9ec33a4d283cc353bb7ac51843 | CANONICAL | BLOB |
| EV-LVD-03 | AC3 护栏通过（3 onnx / 632,552,582 B） | verification/LICENSE-VARIANT-DECLARATION-1/ac3-models-guard.log | 02c3aaeda | c7e2291f64435492848a0b1838f98e80289b30ba03e1dff64531205898d75487 | CANONICAL | BLOB |
| EV-LVD-04 | AC3 安装器 build-info（variant=models / license=AGPL-3.0 / sha256） | verification/LICENSE-VARIANT-DECLARATION-1/ac3-installer-build-info.json | 02c3aaeda | 4601675136f40a74e25af114142d0a3ceb80eb5c829c174936bef700078b4457 | CANONICAL | BLOB |
| EV-LVD-05 | AC3 NSIS 收到变体定义（无乱码） | verification/LICENSE-VARIANT-DECLARATION-1/ac3-nsis-variant-defines.log | 02c3aaeda | b829772b0f483f786fff5f34184a1bf9b71f14ae08ac2667ef789e2f39b641dd | CANONICAL | BLOB |
| EV-LVD-06 | AC4 旧 stage 仍被拒（EXIT=1） | verification/LICENSE-VARIANT-DECLARATION-1/ac4-old-stage-still-rejected.log | 02c3aaeda | 88dc4063d0acde324eb662b0ec557f894da21ef5b6fcb87059443dab634b1507 | CANONICAL | BLOB |
| EV-LVD-07 | AC3 package-manifest（models_bytes=632,552,582） | verification/LICENSE-VARIANT-DECLARATION-1/ac3-models-package-manifest.json | 02c3aaeda | 70a224306f8395f5a220a3a722f806d6e71d47ab214e2fa91836609b7fde042e | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/LICENSE-VARIANT-DECLARATION-1/ | NOT_APPLICABLE | — | — | 7 个文件（README + 6 份实测）全部已登记于 Canonical Evidence；无迁移/归档/删除 |

## Closeout Record（2026-11-17，DSH）

- canonical_evidence_status：`complete`；resource_closeout_status：`complete`；删除/迁移/归档：**0**。
- **方向 = A**（ZCode 第二次调用，正文完整）：保留权重随包、整包按 **AGPL-3.0** 声明。
- **AC2**：`NOTICE.md` / `LICENSE_AUDIT.md` / `THIRD_PARTY_LICENSES.md` 三份按实物改写；
  `installer.nsi` 四处改为读取 `${VARIANT_NAME}`/`${VARIANT_LICENSE}`（中文短语在脚本内推导，避免命令行乱码）；
  `build-installer.ps1` 从 stage 取变体并**在「有权重 + 非 AGPL」时直接 throw**（fail-closed）。
- **AC3**：干净 `package.ps1 -WithModels` → `license=AGPL-3.0`、3 onnx / 632,552,582 B，护栏 **EXIT=0**；
  `build-installer.ps1` → `INST_EXIT=0`，`setup.exe` 652,157,341 B / sha256 `a4b11458…`。
- **AC4**：旧 stage（base 名 + 632 MB 权重 + GPL 声明）护栏 **EXIT=1**（8 条 FAIL）⇒ 判别力两侧都有。
- **限制**：
  1. **未做权重上游许可的「核实认定」**：三项仍标「待核实」，整包 AGPL-3.0 是**保守过度声明**，不是核实结论。
  2. 安装向导的**实际渲染**未目验（中文文案在 NSIS 中压缩存储，字符串搜索不可靠）；只验证了 makensis 编译成功与变体定义送达。
  3. `setup.exe` **未签名**（`authenticode=NotSigned`）；Release Gate 条件 4 仍需真证书。
  4. 未改动旧 stage 任何字节；旧 stage 仍被护栏拒绝。
- **边界**：不改变 `Technical Gate=NOT_SATISFIED`；不构成任何发布验收。
