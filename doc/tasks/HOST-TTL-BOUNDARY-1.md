---
id: HOST-TTL-BOUNDARY-1
title: 修复 import/export grant 的 TTL 精确边界缺陷（host 取满 Core 300 秒验证窗口 → REF_EXPIRED）
kind: fix
governance_version: 2
status: done
approval: coordinator_release_20261016_confirmed_cross_boundary_defect
suggested_owner: Codex
owner: Codex
reviewer: dsh
depends_on: [HOST-ISSUER-1, HOST-ISSUER-1-C1, HOST-CORE-1, P12-C1]
base_commit: 45b3c3a4ba497955daa41b90dc4fe5bb38eb9308
branch: codex/HOST-TTL-BOUNDARY-1-grant-ttl
worktree: G:/CODEX/New Manga.workspace/worktrees/HOST-TTL-BOUNDARY-1
integration_commit: 23587397e1f22516e3736a6e0928b2d5b55987b2
delivery_head: fdf974645f4d3fdcabacbda5a8bf1b1678572398
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/HOST-TTL-BOUNDARY-1
---

# HOST-TTL-BOUNDARY-1：import/export grant TTL 精确边界缺陷

## 来源与缺陷事实（Coordinator 只读复核确认）

- **来源**：ENV-BUNDLE-1-FU1 的 AC3 packaged 探测在 `RegisterImportSource` 上返回 `REF_EXPIRED`
  （见 `verification/ENV-BUNDLE-1-FU1/ac3-host-control-blocked.md`）。Owner 提出"亚秒边界错配"假设但如实声明**未精确测定**。
  Coordinator 复核源码后确认这是一个**精确边界设计缺陷**，而非随机网络/负载问题。

**Import 原始缺陷代码事实（Task base）**：

| 侧 | 位置 | 行为 |
|---|---|---|
| host（Rust） | `apps/desktop/src-tauri/src/host_issuer.rs:152`（Task base） | 原为 `let expires_at = unix_seconds() + 300.0;` —— **恰取 Core 允许的最大 TTL**；L171 以原始 f64 下发 payload |
| Core（Python） | `src/infrastructure/resource_channel/import_source_refs.py:152-154` | `now = self._clock()`；`if expires_at <= now or expires_at > now + 300: raise TypedResourceChannelError(E_EXPIRED)` |
| Core 时钟 | `import_source_refs.py:105-106`、`src/bootstrap/core_assembly.py:1260` | `clock=time.time`（默认，无覆盖）—— 两侧同为 epoch 墙钟，**不是时钟域错配** |

**Export 同类缺陷（DSH R1 I1）**：

| 侧 | 位置 | 行为 |
|---|---|---|
| host（Rust） | `apps/desktop/src-tauri/src/host_issuer.rs:263-305` | `build_export_grant` 原为 `unix_seconds() + 300.0`，恰取 Core 最大窗口 |
| Core（Python） | `src/infrastructure/export/target_refs.py:127` | `expires_at <= now or expires_at > now + 300`，保持原样 |
| 签名 | Rust `host_issuer.rs:303-305` ↔ Python `target_refs.py:188` | `{:.6}` / `{:.6f}`，保持原样 |

Export 侧的差分探针在 1 ms 负时钟偏差时得到 `REF_EXPIRED`；细节见用户提供的 DSH R1 §2。`library_start_export`
（`apps/desktop/src-tauri/src/main.rs:464-493`，P17 导出 UI 使用的既有命令）经 `export_with_session` 签发 grant 并调用
`RegisterExportTarget`，因此与 P12 导入路径同源。

**推论（纯代数，不依赖测量）**：`expires_at = t_host + 300`，Core 拒绝条件中的上界分支为
`expires_at > now + 300` ⟺ `t_host > t_core`。即**只有当 Core 的时钟读数严格 ≥ host 构建 grant 的时刻，注册才会成功**。
host 把 TTL 取满 300，使"允许区间"退化为**单点边界、零裕量**：任何负向偏差
（Python `time.time()` 的时钟粒度/取整低于 Rust 的高精度读数、进程间读数次序、序列化精度）都会让它**必然失败**。
这与观察到的**间歇性** `REF_EXPIRED` 一致（AC3 一次探测失败；owner 未测出稳定通过）。

**为什么不只是"测试不稳定"**：`library_import_file` / `library_import_folder`
（`apps/desktop/src-tauri/src/main.rs:409-458`，即 **P12 导入 UI 将要调用的既有命令**）内部经
`import_from_path` → `host_issuer.rs` 签发 grant → `RegisterImportSource`。
因此该缺陷会让**用户可见的导入功能间歇性失败**，属关键路径上的产品缺陷。
Export 由 `library_start_export` → `start_export_to_path` → `build_export_grant` → `RegisterExportTarget` 经过同一 Core 上界；因此 P17 也暴露在该零裕量边界上。

## Acceptance Criteria

- [x] **AC1 PASS（Import/Export 同一边界裁决）**：以 [M2-C1 类型化 IPC 契约](../contracts/M2-C1_TYPED_IPC_CONTRACT.md)
      §5.7 与 §10.3/§10.4 为权威。§5.7（L456、L476）将 grant 有效期上限与拒绝语义交回 §10.3/§10.4；§10.4（L826）规定导入引用默认 TTL 为 300 秒并活动消费时滑动续期，§10.3（L814）规定导出引用默认有效期 300 秒、不滑动续期且单次消费。两节均没有要求 host 必须恰好签发 300 秒或把默认值定义为精确 host 上限。故两侧均采用 AC1(b)：host 签发值为构建时刻后 299 秒，留 1 秒裕量；Core 的精确过期与 `> now + 300` 超窗守卫保持不变。Export 的不续期、单目标和单次消费语义不变。HOST-ISSUER-1-C1 rev 2.3 不改变既有 P12/P16 wire、ref 与 `REF_*` 语义。逐条文见 `verification/HOST-TTL-BOUNDARY-1/ac1-contract-ruling.md`。Core 和 host 守卫未通过试数放宽。
- [x] **AC2 PASS**：import/export host expiry 均为 +299 秒；两侧 Core 上下界守卫均未改。来源 scope、只读与 `ImportPages`、导出单目标写 scope、session 绑定、一次性消费、替换授权及签名校验保持不变，没有放宽安全语义。
- [x] **AC3 PASS**：Import 与 Export 各有五个确定性边界断言：窗口内成功、Core 时钟等于 host 时刻成功、Core 时钟略早成功、真正过期拒绝、真正超窗拒绝。Export Python 测试注入 `ExportTargetGrantRegistry(clock=...)`；Rust issuer 测试断言签发 TTL 为 299 秒，留 1 秒裕量。测试均保留通过面与拒绝面。
- [x] **AC4 PASS（Import/Export frozen 链路）**：在协议 2.3 frozen Core（SHA-256 `896bd56286b25bc8539028d52f3ef991cfbcbda24f93ae6c6d75758a7dbfd842`）上跑通 host 签发、HostControl 注册及下游命令。Import 注册成功后 `ImportPages` 返回 `TARGET_NOT_FOUND`；Export `RegisterExportTarget` 被接受，随后 `StartExport` 对不存在的 Book 返回 `TARGET_NOT_FOUND`，目标文件未写入。该结果证明请求越过注册点，不声称写入页面或完成导出。
- [x] **AC5 PASS**：不改契约文本、不改 [AD-001](../AD-001_TARGET_DESKTOP_ARCHITECTURE.md)、不新增 wire、
      不改与本缺陷无关的产品行为；不得放宽既有断言或跳过既有测试。
- [x] **AC6 PASS**：`tests/core/**` 405 passed（1 条既有 Pillow deprecation warning）；Rust 非-packaged 76 passed/1 ignored；frozen packaged 8 passed。Rust 两组分环境执行，合计 84 passed/1 ignored；原始日志与退出码已记录。
- [x] **AC7 PASS（交付物固定；Review 未完成）**：固定 commit、Handoff（[模板](../templates/HANDOFF.md)）、Canonical Evidence（真实 sha256）；
      未跑项如实 `NOT_RUN`/`BLOCKED`；不 `push`、不 `merge`。

## 允许修改范围

- `apps/desktop/src-tauri/src/host_issuer.rs`（TTL/边界；如 AC1 判定为 host 越界）
- `src/infrastructure/resource_channel/import_source_refs.py`、`src/infrastructure/export/target_refs.py`（守卫/容差只读；如 AC1 判定 Core 越界才可申请改动。本次保持不变）
- `apps/desktop/src-tauri/src/packaged_sidecar_tests.rs`、`tests/core/test_p09_fu2_import_pages.py`、`tests/core/test_p16_reader_export.py`（对应定向回归测试）
- 本 Task、`doc/handoffs/HOST-TTL-BOUNDARY-1-*.md`、`verification/HOST-TTL-BOUNDARY-1/**`
- 契约**只读引用**（若判定契约本身需要修订，**先 BLOCK 交 Coordinator**，不得自行改契约）

## 禁止范围

- **不得**改契约、Schema、依赖清单、`doc/STATUS.md` / `doc/REBASELINE_PLAN.md`。
- **不得触碰**用户 19 项 dirty/untracked。
- **不得**用"把守卫放宽到无穷"之类方式掩盖缺陷——必须保留可拒绝的真实越界用例（AC3 ④）。
- 不得改与本缺陷无关的产品行为；不 `push`/`merge`/`reset`/`stash`。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 读取 M2-C1 §5.7、§10.3、§10.4 与 HOST-ISSUER-1-C1 rev 2.3，冻结 Import/Export 同一边界裁决 | 只读；export 改码前 | PASS；两侧均按默认 300 秒契约留 1 秒 host 裕量 | `verification/HOST-TTL-BOUNDARY-1/ac1-contract-ruling.md` |
| AC2 | 核对两侧 grant expiry、Core 守卫、scope/session/signature 检查 | Rust host + Core | PASS；两侧 +299 秒；Core 守卫和安全语义未改 | delivery diff；AC3/AC4 logs |
| AC3 Import | `python -m pytest tests/core/test_p09_fu2_import_pages.py -k ttl_boundary -vv`；Rust import issuer 定向测试 | 注入时钟 / issuer expiry 断言 | PASS；Python 5/5，Rust 1/1 | `ac3-python-ttl-boundary-6284f6f.log`; `ac3-rust-ttl-boundary-6284f6f.log` |
| AC3 Export | `python -m pytest tests/core/test_p16_reader_export.py -k ttl_boundary -vv`；Rust export issuer 定向测试 | Python 注入 `clock=`；Rust build-time expiry 断言 | PASS；Python 5/5，Rust 1/1 | `ac3-export-python-ttl-boundary-4662239.log`; `ac3-rust-export-ttl-boundary-4662239.log` |
| AC4 Export | frozen 2.3 bundle 上 Rust host → `RegisterExportTarget` → `StartExport` | `M2RC1_PACKAGED=1`; source/Python overrides unset; frozen exe SHA `896bd56286b25bc8539028d52f3ef991cfbcbda24f93ae6c6d75758a7dbfd842` | PASS；登记接受；下游 `StartExport` 返回预期 `TARGET_NOT_FOUND`；目标未写入 | `ac4-export-frozen-rust-7fbce30.log`; `EXIT_CODE=0` |
| AC4 / AC6 packaged | frozen 2.3 packaged suite | 同上；串行启动，startup timeout 120 s | PASS；8/8；包含 ImportPages 与 StartExport 的真实 grant 注册链 | `ac6-export-rust-packaged-7fbce30.log`; `EXIT_CODE=0` |
| AC5 | `git diff --name-only 45b3c3a4b..7fbce3018` 范围核对 | 固定 implementation/test commit | PASS；未改契约、Core 守卫、Schema、依赖、AD-001、STATUS/Plan 或 wire | implementation/test commit diff |
| AC6 Core | `python -m pytest tests/core -q` | Python 3.14.6 / pytest 9.1.1；code/test commit `7fbce3018` | PASS；405 passed、1 条既有 Pillow deprecation warning，EXIT 0 | `ac6-export-tests-core-7fbce30.log` |
| AC6 Rust non-packaged | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop -- --skip packaged_sidecar_tests --test-threads=1` | `M2RC1_PYTHON=C:\Python314\python.exe`；packaged env unset | PASS；76 passed/1 ignored，EXIT 0 | `ac6-export-rust-nonpackaged-7fbce30.log` |
| AC6 Rust packaged | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop packaged_sidecar_tests -- --test-threads=1 --nocapture` | `M2RC1_PACKAGED=1`；Python/source overrides unset | PASS；8 passed，EXIT 0 | `ac6-export-rust-packaged-7fbce30.log` |
| AC7 | 固定 source/test commit、Task/Handoff、Canonical Evidence | 本任务分支 | PASS；implementation/test commit `7fbce3018` 固定；Task 仍 `in_review`，等待 DSH exact-head re-review | 本 Task 与新 Handoff |

## 依赖、风险与阻塞

- `depends_on` 均已 `done`（wire 与两侧实现存在）。**ENV-BUNDLE-1-FU1 提供缺陷现场**，本 Task 修复它。
- 风险一：Rust import/export 共享 Core TTL 窗口；两处 host issuer 均留 1 秒，Core 两个守卫保持原样并各有成功/拒绝边界测试。
- 风险二：改动触碰签名覆盖字段（`expires_at` 在签名串内，见 `host_issuer.rs:153/157`）→ 若改变序列化精度，
  必须同步 Core 侧 `"{expires_at:.6f}"` 的重算格式，否则签名校验会退化。**这是本 Task 最容易踩的坑**。
- 阻塞条件：若 AC1 判定需要修订契约 → `BLOCKED` 并交 Coordinator，不得自行改契约。

## 交付与运行记录

- 2026-10-16 Coordinator 释放（dsh, epoch 6）：依据 ENV-BUNDLE-1-FU1 AC3 的实测 `REF_EXPIRED` +
  Coordinator 对 `host_issuer.rs:152` 与 `import_source_refs.py:152-154` 的只读复核。
  与在飞的 [ENV-BUNDLE-1-FU1](ENV-BUNDLE-1-FU1.md)（I1 返修）与 [P12](P12.md)（书架导入 UI）并行，
  写入路径不重叠；但**注意**：P12 的实现依赖 `library_import_file`，本缺陷若不在 P12 验收前修复，
  P12 的导入 E2E 可能间歇失败——Coordinator 必须在 P12 REVIEW 时把本 Task 状态纳入考虑。
- 2026-10-16 Codex，AC1 在任何生产代码编辑前冻结为 (b)：契约只定义导入默认 TTL 300 秒和滑动续期，未规定精确 host 签发上限；rev 2.3 不改既有 P12 import semantics。实施选择：host 设为 299 秒，Core 的 `> now + 300` 与 `<= now` 拒绝逻辑不变。依据与行号见 `verification/HOST-TTL-BOUNDARY-1/ac1-contract-ruling.md`。
- 2026-10-16 Codex，delivery commit `6284f6f322fa4e990037d56a7cd480d219c0febb`；修改仅限 host issuer、对应 Rust/Python 测试和 AC1 证据。
- 2026-10-16 frozen bundle 复测：`OpenHostSession` 成功；Rust issuer 签发的 import grant 在 Core 注册成功；Core 对随后 `ImportPages` 请求返回 `TARGET_NOT_FOUND`，证明已越过此前的注册拒绝点。与 ENV-BUNDLE-1-FU1 AC3 的 `REF_EXPIRED` 对照：后者在注册阶段失败，当前结果来自下游导入命令。目标 Chapter 故意不存在，本 probe 不声称写入 Page。
- 签名精度保持不变：Rust 仍以 `format!("{expires_at:.6}")` 覆盖签名，Core 仍以 `f"{expires_at:.6f}"` 重算；只改变 expiry 数值。Frozen Core 注册成功并验证签名，证明两端规范化仍一致。
- 2026-10-16 复测环境：AC3 Python 5/5；Core 全量 400/400；Rust 76 passed/1 ignored 与 packaged 7/7，均绑定 delivery commit 内容。P02 Rust 测试要求 `M2RC1_PYTHON=C:\Python314\python.exe`；packaged 测试要求该变量 unset，故分两条命令全覆盖。
- 测试接线重试记录：首次 AC4 probe 漏掉显式 `OpenHostSession`，在 host 侧返回 `HOST_SESSION_INVALID`，没有到 Core；修正后复跑通过（初始日志：`ac4-frozen-host-importpages.log`）。首次综合 Rust 运行因未设置必需的 `M2RC1_PYTHON` 有 1 项 setup failure，拆分后 83 项通过、1 项既有 ignored（初始日志：`ac6-rust-tests.log`）。首次 Rust 编译日志 `ac3-rust-ttl-boundary-build-attempt-1.log` 保留；临时 Tauri `frontend/dist` 占位用于编译，最终已删除。
- 证据副作用：Cargo 将 27 个生成 Schema/permission 文件显示为状态变化；逐项用 `git diff` 确认没有内容差异后恢复。并发 Rust 测试生成的 P04 diagnostic 已逐字节复制到本 Task evidence 后移除原位置。
- 2026-10-16 DSH R1 changes_requested：唯一 I1 指出 `build_export_grant` 仍为 `+300.0`，与 `target_refs.py:127` 的精确 `now + 300` 上界产生相同零裕量。修复遵循本 Task AC1 同一裁决，Core 守卫、导出 scope 与一次性语义均未改。
- 2026-10-16 Codex bounded repair：implementation/test commit `4662239b4` 将 export issuer 改为 `+299.0` 并新增 Rust issuer 断言与 5 项 Python 注入时钟边界；`7fbce3018` 修正 packaged 测试请求 fixture 字段。Rust `{:.6}` 与 Core `{:.6f}` 未变。
- Export AC4：冻结协议 2.3 `core_service.exe`（68,717,156 bytes，SHA-256 `896bd56286b25bc8539028d52f3ef991cfbcbda24f93ae6c6d75758a7dbfd842`）接受 `RegisterExportTarget`；`StartExport` 对不存在的 Book 返回预期 `TARGET_NOT_FOUND`，目标文件未写入。全 packaged suite 8/8。
- 新增验证：export 边界 Python 5/5；Python Core 405 passed；Rust non-packaged 76 passed/1 ignored；frozen packaged 8 passed。各命令实际退出码和 SHA 见下表。
- Packaged probe 接线重试：首次请求误用 `chapter_id` / `page_ids`，由 host schema 校验返回 `INVALID_REQUEST`，未作为通过证据；按既有 `book_id` / `chapter_ids` / `ordered_page_ids` 形状修正后通过。原始失败日志保留为 `ac4-export-frozen-rust-attempt1-4662239.log`。
- Cargo 生成的 27 个 schema/permission 改动经 `git diff --ignore-space-at-eol` 确认为纯行尾噪音后逐文件恢复；P04 diagnostic 已逐字节复制到本 Task evidence 并清除测试生成的 P04 临时文件。临时 `frontend/dist/index.html` 仅用于 Rust 编译，已删除。
- 新 Handoff：`doc/handoffs/HOST-TTL-BOUNDARY-1-export-ttl-r1.md`。原 `6284f6f` Handoff 保留为 import 阶段历史记录。
- Review：DSH R1 已提出 I1；I1 实现已固定于 `7fbce3018`，等待 DSH 对最终 branch tip exact-head re-review。Task 保持 `in_review`，未声明 accepted 或 done。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| EVD-HOSTTTL-AC1 | AC1 | `verification/HOST-TTL-BOUNDARY-1/ac1-contract-ruling.md` | `7fbce3018` | `6f37cd21c3c119ed75be37b7d8312d08088f214c05a9025da29413092d2c8d80` | CANONICAL |
| EVD-HOSTTTL-AC3-PY | AC3 | `verification/HOST-TTL-BOUNDARY-1/ac3-python-ttl-boundary-6284f6f.log` | a4bc60dca0f31c61605ba45281dc4b511caf184e | `e2af0d4509d780a0fd4db569a5d4120856f67ba76b93039bb6c456b9b7ca3677` | CANONICAL |
| EVD-HOSTTTL-AC3-RUST | AC2/AC3 | `verification/HOST-TTL-BOUNDARY-1/ac3-rust-ttl-boundary-6284f6f.log` | a4bc60dca0f31c61605ba45281dc4b511caf184e | `55c8216aa283871a677a773d6c785583f0fd354e6eae9c90a18adc1bdf436102` | CANONICAL |
| EVD-HOSTTTL-AC4-PACKAGED | AC4/AC6 | `verification/HOST-TTL-BOUNDARY-1/ac4-ac6-packaged-rust-6284f6f.log` | a4bc60dca0f31c61605ba45281dc4b511caf184e | `52c93b31491c139bf04795e8c7746b5ab109cffb3656eabcee0ea6fecb97788a` | CANONICAL |
| EVD-HOSTTTL-AC6-CORE | AC6 | `verification/HOST-TTL-BOUNDARY-1/ac6-tests-core-6284f6f.log` | a4bc60dca0f31c61605ba45281dc4b511caf184e | `431466fbbff67dd410ed246812ae9483d6f2634bbc62600bb3c7ab0d3fd0d852` | CANONICAL |
| EVD-HOSTTTL-AC6-RUST | AC6 | `verification/HOST-TTL-BOUNDARY-1/ac6-rust-source-6284f6f.log` | a4bc60dca0f31c61605ba45281dc4b511caf184e | `1b06a84c35bad0e4a8410d85d47caae8ec83af72771fa2e53aa6cf7c99686a9e` | CANONICAL |
| EVD-HOSTTTL-AC6-RUST-DIAG | AC6 | `verification/HOST-TTL-BOUNDARY-1/ac6-rust-concurrency-diagnostic-6284f6f.jsonl` | a4bc60dca0f31c61605ba45281dc4b511caf184e | `67d01f0661a12a114a97154b8df776ec7c0465d50d6859307e4e444c25859739` | CANONICAL |
| EVD-HOSTTTL-AC3-EXPORT-PY | AC3 | `verification/HOST-TTL-BOUNDARY-1/ac3-export-python-ttl-boundary-4662239.log` | fdf974645f4d3fdcabacbda5a8bf1b1678572398 | `8a8089c31cca5afaa00777ff42abde9cf9ce967c29eeede209e31cddb478cfd6` | CANONICAL |
| EVD-HOSTTTL-AC3-EXPORT-RUST | AC2/AC3 | `verification/HOST-TTL-BOUNDARY-1/ac3-rust-export-ttl-boundary-4662239.log` | fdf974645f4d3fdcabacbda5a8bf1b1678572398 | `aacc0ebf0c5e3a6b3f125a966f28fa2725c1f8d553ae1202ec3f60105ba7f637` | CANONICAL |
| EVD-HOSTTTL-AC4-EXPORT | AC4 | `verification/HOST-TTL-BOUNDARY-1/ac4-export-frozen-rust-7fbce30.log` | fdf974645f4d3fdcabacbda5a8bf1b1678572398 | `187e5dfe7cf37db72ebe919c1740e3cfbcf67f4ca2f5d6f0345f6889752e818f` | CANONICAL |
| EVD-HOSTTTL-AC6-CORE-EXPORT | AC6 | `verification/HOST-TTL-BOUNDARY-1/ac6-export-tests-core-7fbce30.log` | fdf974645f4d3fdcabacbda5a8bf1b1678572398 | `96e840bc68900ef454c89d6f218896c06bf53f307c78814dbe26c41fb75b4063` | CANONICAL |
| EVD-HOSTTTL-AC6-RUST-NONPACKAGED-EXPORT | AC6 | `verification/HOST-TTL-BOUNDARY-1/ac6-export-rust-nonpackaged-7fbce30.log` | fdf974645f4d3fdcabacbda5a8bf1b1678572398 | `b5bfa6ee647919fd0a4ce778a89c7707026d26e93b79752ae076e695bbec79c8` | CANONICAL |
| EVD-HOSTTTL-AC6-RUST-PACKAGED-EXPORT | AC4/AC6 | `verification/HOST-TTL-BOUNDARY-1/ac6-export-rust-packaged-7fbce30.log` | fdf974645f4d3fdcabacbda5a8bf1b1678572398 | `62eb8810b2bb7e8f6b6d6a0c7e164333704c4f7aae7f6572f9544c9372594722` | CANONICAL |
| EVD-HOSTTTL-AC6-RUST-DIAG-EXPORT | AC6 | `verification/HOST-TTL-BOUNDARY-1/ac6-export-rust-concurrency-diagnostic-7fbce30.jsonl` | fdf974645f4d3fdcabacbda5a8bf1b1678572398 | `1fc9e10c1affa2ede34e75e21267188bb620796c23a21ea94ebd7689aa17e424` | CANONICAL |
| EVD-HOSTTTL-FU1-AC3 | AC4 source comparison | `verification/ENV-BUNDLE-1-FU1/ac3-host-control-blocked.md` | `998200d48e10899e2916a73143578c69bceb30cf` | `851a00ea6aef2dcef14131c9c4fb3263713529444e239483543c2a568be9b10f` | SOURCE_PIN |
| EVD-HOSTTTL-C1-COVERAGE | AC1 source pin | `verification/HOST-ISSUER-1-C1/coverage-matrix.md` | `af6fa705de54489ce32811cdc8dd3be51a1fd999` | `f2a522000c50d43247d9ba55a8a456394bcf2e549e80bb26c2b1ccab13e7d22d` | SOURCE_PIN |
| EVD-HOSTTTL-M2C1-CONTRACT | AC1 source pin | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | `af6fa705de54489ce32811cdc8dd3be51a1fd999` | `6a2f38e0b17062d9d4f1d6ee109b4353b745504a5a6b889148781eee84fa2062` | SOURCE_PIN |

| HOST-TTL-BOUNDARY-1-REVIEW-R1 | AC1-AC7 (independent review; I1 converged) | `verification/HOST-TTL-BOUNDARY-1/dsh-review-r1.md` | `775bf0ea9a82032631d29450eac0a8e67d3b59f7` | - | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/HOST-TTL-BOUNDARY-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/HOST-TTL-BOUNDARY-1 | verification/HOST-TTL-BOUNDARY-1/resource-manifest.json | 本 Task 独立 worktree；closeout 时按 Worktree Safety Inventory 复核后填写 |

## Closeout Record

- Closeout date / Coordinator：2026-10-16（dsh, epoch 6）。Reviewer=dsh（独立于 Owner=codex）。
- canonical_evidence_status：`complete`（Owner 证据 + 独立 Review 行；Reviewer 复算证据 pin 与逐项复核）。
- resource_closeout_status：`complete`（worktree `PRESERVE_REFERENCED`）。
- 删除、迁移、归档数量/字节数：0。
- 未关闭项及保留原因：**无未关闭 AC**。如实保留的主导限定：AC4 证明的是"注册被接受 + 下游命令可达并返回 Core 权威 typed 响应"；
  因**无真实 fixture 章节/导出目标**，`ImportPages`/`StartExport` 返回预期 `TARGET_NOT_FOUND`，**未实际写入页面或导出产物**。
- 交付状态：`done`。集成 `23587397e`；delivery_head（分支 head）见 front matter；实现 `4662239b4`（export TTL）+`7fbce3018`（测试对齐）+`fdf974645`（记录）。
  Review R1 **approved**（I1 收敛）：import 侧 `6284f6f32` 与 export 侧 `4662239b4` 均改为 `+299.0`，Core 守卫未动（对称修复在 issuer 侧）。
- 根因归档（供未来同类问题复用）：host 把 TTL 取在 Core 验证窗口的**精确上限** → 零裕量；任何负向时钟偏差即必然 `REF_EXPIRED`。
  Reviewer 差分探针（workspace `tmp/guarded/{ttl,export-ttl}-boundary-probe.{py,log}`）证明 **1 ms 负偏差**即触发。
  **同类风险提示**：新增任何 grant 类型时，issuer 侧必须留裕量，不得取满验证窗口上限。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` 已同步（HOST-TTL-BOUNDARY-1 移出 READY）。
