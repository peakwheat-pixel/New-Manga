---
id: HOST-TTL-BOUNDARY-1
title: 修复 import grant 的 TTL 精确边界缺陷（host 取满 Core 验证窗口上限 → 间歇 REF_EXPIRED）
kind: fix
governance_version: 2
status: in_review
approval: coordinator_release_20261016_confirmed_cross_boundary_defect
suggested_owner: Codex
owner: Codex
reviewer: null
depends_on: [HOST-ISSUER-1, HOST-ISSUER-1-C1, HOST-CORE-1, P12-C1]
base_commit: 45b3c3a4ba497955daa41b90dc4fe5bb38eb9308
branch: codex/HOST-TTL-BOUNDARY-1-grant-ttl
worktree: G:/CODEX/New Manga.workspace/worktrees/HOST-TTL-BOUNDARY-1
integration_commit: null
delivery_head: 6284f6f322fa4e990037d56a7cd480d219c0febb
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/HOST-TTL-BOUNDARY-1
---

# HOST-TTL-BOUNDARY-1：import grant TTL 精确边界缺陷

## 来源与缺陷事实（Coordinator 只读复核确认）

- **来源**：ENV-BUNDLE-1-FU1 的 AC3 packaged 探测在 `RegisterImportSource` 上返回 `REF_EXPIRED`
  （见 `verification/ENV-BUNDLE-1-FU1/ac3-host-control-blocked.md`）。Owner 提出"亚秒边界错配"假设但如实声明**未精确测定**。
  Coordinator 复核源码后确认这是一个**精确边界设计缺陷**，而非随机网络/负载问题。

**代码事实（当前 main）**：

| 侧 | 位置 | 行为 |
|---|---|---|
| host（Rust） | `apps/desktop/src-tauri/src/host_issuer.rs:152` | `let expires_at = unix_seconds() + 300.0;` —— **恰取 Core 允许的最大 TTL**；L171 以原始 f64 下发 payload |
| Core（Python） | `src/infrastructure/resource_channel/import_source_refs.py:152-154` | `now = self._clock()`；`if expires_at <= now or expires_at > now + 300: raise TypedResourceChannelError(E_EXPIRED)` |
| Core 时钟 | `import_source_refs.py:105-106`、`src/bootstrap/core_assembly.py:1260` | `clock=time.time`（默认，无覆盖）—— 两侧同为 epoch 墙钟，**不是时钟域错配** |

**推论（纯代数，不依赖测量）**：`expires_at = t_host + 300`，Core 拒绝条件中的上界分支为
`expires_at > now + 300` ⟺ `t_host > t_core`。即**只有当 Core 的时钟读数严格 ≥ host 构建 grant 的时刻，注册才会成功**。
host 把 TTL 取满 300，使"允许区间"退化为**单点边界、零裕量**：任何负向偏差
（Python `time.time()` 的时钟粒度/取整低于 Rust 的高精度读数、进程间读数次序、序列化精度）都会让它**必然失败**。
这与观察到的**间歇性** `REF_EXPIRED` 一致（AC3 一次探测失败；owner 未测出稳定通过）。

**为什么不只是"测试不稳定"**：`library_import_file` / `library_import_folder`
（`apps/desktop/src-tauri/src/main.rs:409-458`，即 **P12 导入 UI 将要调用的既有命令**）内部经
`import_from_path` → `host_issuer.rs` 签发 grant → `RegisterImportSource`。
因此该缺陷会让**用户可见的导入功能间歇性失败**，属关键路径上的产品缺陷。

## Acceptance Criteria

- [x] **AC1 PASS（边界语义裁决，先冻结后改码）**：以 [M2-C1 类型化 IPC 契约](../contracts/M2-C1_TYPED_IPC_CONTRACT.md)
      §5.7 与 HOST-ISSUER-1-C1 revision 为权威，判定是哪一侧越界：
      (a) 契约规定 host 的 TTL 上限即 300 s → 则 Core 的上界守卫或 host 的取值措辞需澄清（例如 host 必须留裕量，或守卫允许微小容差）；
      (b) 契约给的是 `< 300` 或未规定精确上限 → 以契约为准修正实现。
      **裁决为 (b)**：§5.7（契约 L456、L476）将有效期上限与拒绝语义交回 §10.3/§10.4；§10.4（L826）规定导入引用默认 TTL 为 300 秒并在活动消费期间滑动续期，但没有规定 host 必须签发恰好 300 秒或将 300 秒规定为精确上限。HOST-ISSUER-1-C1 rev 2.3（契约 L3、L17、L23；`verification/HOST-ISSUER-1-C1/coverage-matrix.md` L14、L22–23）冻结新增 HostControl 通道并保持既有 P12 import wire、ref 与 `REF_*` 语义不变，没有为导入 grant 新增精确 TTL 上限。修 host 签发时间为构建时刻后 299 秒，留出明确 1 秒裕量；Core 守卫保持原样。条文逐字核对见 `verification/HOST-TTL-BOUNDARY-1/ac1-contract-ruling.md`。禁止在两侧试数直到通过。
- [x] **AC2 PASS**：按 AC1 裁决修正，使 TTL 边界**有明确裕量或明确容差**，
      且**不放松任何安全语义**（来源 scope、只读、`ImportPages`、session 绑定、签名校验一律不变）。
      host import expiry 为 +299 秒；Core 守卫未改。来源、只读、`ImportPages`、session 绑定和签名规则保持不变。
- [x] **AC3 PASS**：新增测试用**注入时钟**（两侧均可注入：Python 侧已支持 `clock=` 参数；
      Rust 侧如无注入点，用可控的 clock 抽象或直接对 `expires_at` 计算做单元断言）覆盖：
      ① `expires_at` 在窗口内 → 注册成功；
      ② Core 读数**等于/略小于** host 构建时刻（模拟粒度截断）→ 仍成功；
      ③ 真正过期（`expires_at <= now`）→ `E_EXPIRED`；
      ④ 超窗（`expires_at > now + 300` 且**确实越界**）→ `E_EXPIRED`。
      五个确定性断言全部通过（窗口内、Core 时钟等于 host 时刻、略早、真过期、真超窗），Rust 另断言 host 签发值留有 1 秒裕量。
- [x] **AC4 PASS（真实控制链路到达 ImportPages）**：在**已重建的 2.3 frozen bundle** 上跑通
      host 签发 → `RegisterImportSource` → `ImportPages` 的真实往返（原始日志 + 退出码），
      并说明与 ENV-BUNDLE-1-FU1 AC3 的对照关系。冻结 Core 接受注册，`ImportPages` 返回预期 `TARGET_NOT_FOUND`（测试使用不存在的 Chapter）；这证明真实 host-control 请求走到 Core 导入命令，未声称完成页面导入。
- [x] **AC5 PASS**：不改契约文本、不改 [AD-001](../AD-001_TARGET_DESKTOP_ARCHITECTURE.md)、不新增 wire、
      不改与本缺陷无关的产品行为；不得放宽既有断言或跳过既有测试。
- [x] **AC6 PASS**：`tests/core/**` 与既有 Rust 测试全绿；给出原始日志与退出码。
      Python Core 400 passed、Rust 非-packaged 76 passed/1 ignored、frozen packaged 7 passed；合计 83 passed/1 ignored。
- [x] **AC7 PASS（交付物固定；Review 未完成）**：固定 commit、Handoff（[模板](../templates/HANDOFF.md)）、Canonical Evidence（真实 sha256）；
      未跑项如实 `NOT_RUN`/`BLOCKED`；不 `push`、不 `merge`。

## 允许修改范围

- `apps/desktop/src-tauri/src/host_issuer.rs`（TTL/边界；如 AC1 判定为 host 越界）
- `src/infrastructure/resource_channel/import_source_refs.py`（守卫/容差；如 AC1 判定为 Core 越界）
- 两侧对应测试文件（新增定向回归测试）
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
| AC1 | 读取 M2-C1 §5.7、§10.4 与 HOST-ISSUER-1-C1 rev 2.3，冻结边界裁决 | 只读，改码前 | PASS（裁决 b；host 留 1 秒裕量） | `verification/HOST-TTL-BOUNDARY-1/ac1-contract-ruling.md` |
| AC2 | 核对 grant expiry 值、Core 守卫和 scope/session/signature 检查 | Rust host + frozen Core | PASS；+299 秒，Core 守卫及安全检查未改 | delivery diff；AC3/AC4 logs |
| AC3 ①–④ | `python -m pytest tests/core/test_p09_fu2_import_pages.py -k ttl_boundary -vv`；Rust `host_issuer` 定向测试 | Python 注入时钟；Rust build-time expiry 断言 | PASS；5/5 Python 边界断言，Rust 1/1 | `ac3-python-ttl-boundary-6284f6f.log`; `ac3-rust-ttl-boundary-6284f6f.log` |
| AC4 | frozen 2.3 bundle 上 Rust host → `RegisterImportSource` → `ImportPages` | `M2RC1_PACKAGED=1`; source/Python overrides unset; frozen exe SHA `896bd56286b25bc8539028d52f3ef991cfbcbda24f93ae6c6d75758a7dbfd842` | PASS；注册成功，`ImportPages` 返回 `TARGET_NOT_FOUND`（预期 fixture） | `ac4-ac6-packaged-rust-6284f6f.log`; `EXIT_CODE=0` |
| AC5 | `git diff --name-only 45b3c3a4b..6284f6f` 范围核对 | 固定 delivery commit | PASS；未改契约、Schema、依赖、AD-001、STATUS/Plan 或 wire | delivery commit diff |
| AC6 Core | `python -m pytest tests/core -q` | Python 3.14.6 / pytest 9.1.1 | PASS；400 passed、1 既有 Pillow deprecation warning，EXIT 0 | `ac6-tests-core-6284f6f.log` |
| AC6 Rust | `cargo test ... --skip packaged_sidecar_tests -- --test-threads=1` + packaged suite | P02 Python 明确设置的非-packaged 测试与 frozen packaged 环境分开 | PASS；76 passed/1 ignored + 7 passed，EXIT 0/0 | `ac6-rust-source-6284f6f.log`; `ac4-ac6-packaged-rust-6284f6f.log` |
| AC7 | 固定实现提交、Handoff、Canonical Evidence | 本任务分支 | PASS；delivery head 固定，Task 状态为 `in_review`，独立 Review 待执行 | 本 Task 与 Handoff |

## 依赖、风险与阻塞

- `depends_on` 均已 `done`（wire 与两侧实现存在）。**ENV-BUNDLE-1-FU1 提供缺陷现场**，本 Task 修复它。
- 风险一：**两侧同时改动**（Rust + Python）→ 必须一次提交内语义同步，并各自有测试（对齐既有"四处同步"纪律）。
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
- Handoff：`doc/handoffs/HOST-TTL-BOUNDARY-1-6284f6f.md`；delivery head 为 `6284f6f322fa4e990037d56a7cd480d219c0febb`。
- Review：未执行；Reviewer 尚未由 Coordinator 指定。Task 保持 `in_review`，不声称已接受。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| EVD-HOSTTTL-AC1 | AC1 | `verification/HOST-TTL-BOUNDARY-1/ac1-contract-ruling.md` | `6284f6f322fa4e990037d56a7cd480d219c0febb` | `90be3f7a3d955b9869343d7b28dbda37e7903b3420142d3c3dfd80012063ebb6` | CANONICAL |
| EVD-HOSTTTL-AC3-PY | AC3 | `verification/HOST-TTL-BOUNDARY-1/ac3-python-ttl-boundary-6284f6f.log` | `6284f6f322fa4e990037d56a7cd480d219c0febb` | `e2af0d4509d780a0fd4db569a5d4120856f67ba76b93039bb6c456b9b7ca3677` | CANONICAL |
| EVD-HOSTTTL-AC3-RUST | AC2/AC3 | `verification/HOST-TTL-BOUNDARY-1/ac3-rust-ttl-boundary-6284f6f.log` | `6284f6f322fa4e990037d56a7cd480d219c0febb` | `55c8216aa283871a677a773d6c785583f0fd354e6eae9c90a18adc1bdf436102` | CANONICAL |
| EVD-HOSTTTL-AC4-PACKAGED | AC4/AC6 | `verification/HOST-TTL-BOUNDARY-1/ac4-ac6-packaged-rust-6284f6f.log` | `6284f6f322fa4e990037d56a7cd480d219c0febb` | `52c93b31491c139bf04795e8c7746b5ab109cffb3656eabcee0ea6fecb97788a` | CANONICAL |
| EVD-HOSTTTL-AC6-CORE | AC6 | `verification/HOST-TTL-BOUNDARY-1/ac6-tests-core-6284f6f.log` | `6284f6f322fa4e990037d56a7cd480d219c0febb` | `431466fbbff67dd410ed246812ae9483d6f2634bbc62600bb3c7ab0d3fd0d852` | CANONICAL |
| EVD-HOSTTTL-AC6-RUST | AC6 | `verification/HOST-TTL-BOUNDARY-1/ac6-rust-source-6284f6f.log` | `6284f6f322fa4e990037d56a7cd480d219c0febb` | `1b06a84c35bad0e4a8410d85d47caae8ec83af72771fa2e53aa6cf7c99686a9e` | CANONICAL |
| EVD-HOSTTTL-AC6-RUST-DIAG | AC6 | `verification/HOST-TTL-BOUNDARY-1/ac6-rust-concurrency-diagnostic-6284f6f.jsonl` | `6284f6f322fa4e990037d56a7cd480d219c0febb` | `67d01f0661a12a114a97154b8df776ec7c0465d50d6859307e4e444c25859739` | CANONICAL |
| EVD-HOSTTTL-FU1-AC3 | AC4 source comparison | `verification/ENV-BUNDLE-1-FU1/ac3-host-control-blocked.md` | `998200d48e10899e2916a73143578c69bceb30cf` | `851a00ea6aef2dcef14131c9c4fb3263713529444e239483543c2a568be9b10f` | SOURCE_PIN |
| EVD-HOSTTTL-C1-COVERAGE | AC1 source pin | `verification/HOST-ISSUER-1-C1/coverage-matrix.md` | `af6fa705de54489ce32811cdc8dd3be51a1fd999` | `f2a522000c50d43247d9ba55a8a456394bcf2e549e80bb26c2b1ccab13e7d22d` | SOURCE_PIN |
| EVD-HOSTTTL-M2C1-CONTRACT | AC1 source pin | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | `af6fa705de54489ce32811cdc8dd3be51a1fd999` | `6a2f38e0b17062d9d4f1d6ee109b4353b745504a5a6b889148781eee84fa2062` | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/HOST-TTL-BOUNDARY-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/HOST-TTL-BOUNDARY-1 | verification/HOST-TTL-BOUNDARY-1/resource-manifest.json | 本 Task 独立 worktree；closeout 时按 Worktree Safety Inventory 复核后填写 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`complete`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：独立 Review / Coordinator adjudication / integration 尚未执行；Reviewer 未指定，因此 Task 保持 `in_review`，未声明 accepted/done。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` 在释放时同步。
