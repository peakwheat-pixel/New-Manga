---
id: HOST-TTL-BOUNDARY-1
title: 修复 import grant 的 TTL 精确边界缺陷（host 取满 Core 验证窗口上限 → 间歇 REF_EXPIRED）
kind: fix
governance_version: 2
status: ready
approval: coordinator_release_20261016_confirmed_cross_boundary_defect
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [HOST-ISSUER-1, HOST-ISSUER-1-C1, HOST-CORE-1, P12-C1]
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
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

- [ ] **AC1 边界语义裁决（先冻结，后改码）**：以 [M2-C1 类型化 IPC 契约](../contracts/M2-C1_TYPED_IPC_CONTRACT.md)
      §5.7 与 HOST-ISSUER-1-C1 revision 为权威，判定是哪一侧越界：
      (a) 契约规定 host 的 TTL 上限即 300 s → 则 Core 的上界守卫或 host 的取值措辞需澄清（例如 host 必须留裕量，或守卫允许微小容差）；
      (b) 契约给的是 `< 300` 或未规定精确上限 → 以契约为准修正实现。
      **必须给出契约条文引用**；**禁止**在两侧各自"试数"直到通过。
- [ ] **AC2 修复**：按 AC1 裁决修正，使 TTL 边界**有明确裕量或明确容差**，
      且**不放松任何安全语义**（来源 scope、只读、`ImportPages`、session 绑定、签名校验一律不变）。
      若同时涉及 Rust 与 Python 两侧，两侧改动必须语义一致并各自有测试。
- [ ] **AC3 确定性回归测试**：新增测试用**注入时钟**（两侧均可注入：Python 侧已支持 `clock=` 参数；
      Rust 侧如无注入点，用可控的 clock 抽象或直接对 `expires_at` 计算做单元断言）覆盖：
      ① `expires_at` 在窗口内 → 注册成功；
      ② Core 读数**等于/略小于** host 构建时刻（模拟粒度截断）→ 仍成功；
      ③ 真正过期（`expires_at <= now`）→ `E_EXPIRED`；
      ④ 超窗（`expires_at > now + 300` 且**确实越界**）→ `E_EXPIRED`。
      四项必须全部断言，**不得**只测"通过"而丢掉拒绝面。
- [ ] **AC4 真实链路证据**：在**已重建的 2.3 frozen bundle** 上跑通
      host 签发 → `RegisterImportSource` → `ImportPages` 的真实往返（原始日志 + 退出码），
      并说明与 ENV-BUNDLE-1-FU1 AC3 的对照关系。若受环境限制无法跑通 → 如实 `BLOCKED` + 原始证据。
- [ ] **AC5 不越界**：不改契约文本、不改 [AD-001](../AD-001_TARGET_DESKTOP_ARCHITECTURE.md)、不新增 wire、
      不改与本缺陷无关的产品行为；不得放宽既有断言或跳过既有测试。
- [ ] **AC6 不回归**：`tests/core/**` 与既有 Rust 测试全绿；给出原始日志与退出码。
- [ ] **AC7 固定交付**：固定 commit、Handoff（[模板](../templates/HANDOFF.md)）、Canonical Evidence（真实 sha256）；
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
| AC1 | 读取 M2-C1 §5.7 与 revision，引用条文 | 只读 | NOT_RUN | 无 |
| AC3 ①–④ | 注入时钟的定向单元测试（成功/粒度截断仍成功/真过期拒绝/真越界拒绝） | 两侧可注入 | NOT_RUN | 无 |
| AC4 | frozen 2.3 bundle 上 host→Core→ImportPages 真实往返 | 重建后的 bundle | NOT_RUN | 无 |
| AC6 | `tests/core/**` + Rust 测试全绿 | 构建产物 | NOT_RUN | 无 |

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
- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无（全部 `NOT_RUN`）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/HOST-TTL-BOUNDARY-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/HOST-TTL-BOUNDARY-1 | verification/HOST-TTL-BOUNDARY-1/resource-manifest.json | 本 Task 独立 worktree；closeout 时按 Worktree Safety Inventory 复核后填写 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：本 Task 全部 AC 尚未执行（`NOT_RUN`）。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` 在释放时同步。
