# HOST-TTL-BOUNDARY-1 独立 Review（R1）

| 项 | 值 |
|---|---|
| Task | HOST-TTL-BOUNDARY-1（import grant TTL 精确边界缺陷） |
| Owner | codex |
| Reviewer | dsh（epoch 6；独立于 Owner） |
| 交付 commit | 实现+测试 `6284f6f32`；记录 `a4bc60dca` |
| 基线 | `45b3c3a4ba497955daa41b90dc4fe5bb38eb9308` |
| 结论 | **changes_requested（I1，1 项）** —— import 侧修复正确且有强证据；但**同类缺陷的第二处实例（导出 grant）未被覆盖** |

## 1. 已独立验证且成立的部分

| # | 验证项 | 方法 | 结果 |
|---|---|---|---|
| V1 | AC1 边界裁决 | 读 `verification/HOST-TTL-BOUNDARY-1/ac1-contract-ruling.md` 与契约原文 | **成立**。以 M2-C1 §5.7（L456/L476）把有效期交由 §10.3/§10.4；§10.4 L826 只规定导入引用**默认 TTL 300 s 且活动期滑动续期**，**未要求 host 恰好签 300**。故裁决 (b)：host 改签 **299 s**，Core 守卫不变。这是"先按契约裁决、不两侧试数"的正确做法 |
| V2 | AC2 修复最小性 | `git diff 45b3c3a4b..a4bc60dca -- host_issuer.rs` | **PASS**。仅 `build_import_grant`: `+300.0 → +299.0`；来源 scope / 只读 / `ImportPages` / session 绑定 / 签名校验**均未放松** |
| V3 | AC3 边界用例 | 读 `ac3-python-ttl-boundary-6284f6f.log`、`ac3-rust-ttl-boundary-6284f6f.log` | **5/5 + 1/1 PASS**，覆盖：窗口内成功、Core 时钟**等于** host 时刻成功、**略早**（负偏差）成功、真过期拒绝、真超窗拒绝 —— 四项拒绝面均保留 |
| V4 | AC4 真实链路 | 读 `ac4-ac6-packaged-rust-6284f6f.log` + 新增 packaged 测试 | **最强证据**：在 **frozen 2.3 Core**（SHA `896bd562…`）上 `OpenHostSession → 签发 → RegisterImportSource → ImportPages`，**注册被接受**，随后按预期返回 `TARGET_NOT_FOUND`（测试 chapter 不存在）。这与 ENV-BUNDLE-1-FU1 AC3 停在 `REF_EXPIRED` 形成**直接对照**，证明缺陷已被消除 |
| V5 | 签名精度未破坏 | 代码 + 上述 frozen 往返 | `format!("{expires_at:.6}")` 与 Core `f"{expires_at:.6f}"` 未变；frozen Core **接受**新 expiry → 签名校验通过 |
| V6 | 未弱化既有断言 | `git diff` 两份测试文件 | `packaged_sidecar_tests.rs` **仅新增** 1 个测试（packaged 6→7）；`tests/core/test_p09_fu2_import_pages.py` **无删除行**（纯新增参数化用例） |
| V7 | 证据 pin | 逐行复算表内 sha256 | **10/10 与钉住值一致**（第 11 行是表头） |
| V8 | 范围 | `git diff --name-only` | 仅 `host_issuer.rs`、两个测试文件、Task/Handoff/verification；契约、Schema、依赖、`STATUS`/`Plan` 未改 |

## 2. I1（必须返修，bounded）

**finding**：本 Task 只修了 **import** grant；**导出** grant 存在**同类零裕量缺陷**，仍未修复：

| 侧 | 位置 | 现状 |
|---|---|---|
| host | `apps/desktop/src-tauri/src/host_issuer.rs:301`（`build_export_grant`，函数声明于 L263） | **仍为 `unix_seconds() + 300.0`**（Reviewer 已复读确认） |
| Core | `src/infrastructure/export/target_refs.py:127` | `if expires_at <= now or expires_at > now + 300: raise ExportTargetRefError("REF_EXPIRED")` —— 与 import 侧**逐字相同** |
| 签名 | host `host_issuer.rs:303-305` ↔ Core `target_refs.py:188` | 同样以 `{:.6}` / `{:.6f}` 耦合 |

**Reviewer 的经验证明（与 import 侧同等强度）**：差分探针注入时钟、`expires_at = t_host + 300.0`：

```
A now_core = t_host + 0.005 -> REF_SIGNATURE_INVALID (越过过期边界)
B now_core = t_host         -> REF_SIGNATURE_INVALID (越过过期边界)
C now_core = t_host - 0.001 -> REF_EXPIRED          (被过期边界拒绝)
D now_core = t_host - 0.020 -> REF_EXPIRED          (被过期边界拒绝)
```

→ **导出 grant 裕量同样为零**：1 ms 的负向时钟偏差即让 `RegisterExportTarget` 必然失败。
探针与原始输出：`G:/CODEX/New Manga.workspace/tmp/guarded/export-ttl-boundary-probe.{py,log}`。

**影响**：`library_start_export`（`main.rs:460-493`）——**P17 导出 UI 将要调用的既有命令**——走这条路径，因此 P17 暴露在**同一根因**下（与 P12 导入侧同源）。

**返修要求（bounded，与本 Task 已验证的 import 做法对称）**：

1. 把**同一 AC1 裁决的同一裕量原则**应用到导出侧：`build_export_grant` 改为留有明确裕量的 TTL
   （与 import 一致的 1 s 裕量即可，除非 AC1 契约对导出另有规定——若有，须引用条文并说明差异）。
   `target_refs.py` 的守卫**保持不变**（与 import 侧同构）。
2. 补**对称的边界测试**（导出侧 4 项以上）：窗口内成功、Core 时钟**等于** host 时刻成功、
   **负偏差（略早）**成功、真过期拒绝、真超窗拒绝 —— **不得**只测通过面。
3. 若可能，补一条**导出侧的真实链路证据**（frozen 2.3 Core 上 `RegisterExportTarget` 被接受），
   或在 Handoff 说明为何不可行（如实 `NOT_RUN`/`BLOCKED`）。
4. 保持签名精度格式不变（`{:.6}` ↔ `{:.6f}`）；若改动精度，必须两侧同步并在提交中说明。
5. 更新 Task/Handoff/Canonical Evidence（含新证据 sha256），固定 commit。

**不做**：不得放松任何安全语义；不得改动与本缺陷无关的行为；不得改契约、`STATUS`/`Plan`。

## 3. 已接受的信息性记录（非返修项）

- **N1**：AC4 的 `ImportPages` 返回 `TARGET_NOT_FOUND` 是**预期**结果（测试 chapter 不存在），不代表功能缺失；Owner 已如实标注。
- **N2**：1 项既有 Rust perf 测试保持 `ignored`（非本 Task 引入）；Owner 如实记录。
- **N3**：Cargo 生成的行尾噪音已按既有先例处理，未入库。

## 4. 收敛计划

`I1 返修（Owner=codex，bounded：导出侧同裕量 + 对称测试） → Reviewer 复核其边界测试与真实链路证据 → 必要时 I2（上限 1 次） → 集成 → closeout`。
