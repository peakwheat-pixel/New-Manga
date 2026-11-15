---
id: SIDECAR-SCHEMA-STALE-1
title: 测试夹具 sidecar 落后 8 个 schema 版本（v6 vs v14）—— prepare-sidecar 默认取已退役 Tauri 产物且副本不刷新（原诊断误指产品包，已勘误）
kind: defect
governance_version: 3
status: closed_with_limitations
suggested_owner: DSH
owner: DSH
reviewer: 未派（本卡为缺陷核实与登记卡；修复与复核由后续卡承接）
depends_on: []
approval: 用户 2026-11-15「全部授权」；目标 B「Release Gate 可独立完成部分」
base_commit: 69fed50bc
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/SIDECAR-SCHEMA-STALE-1
canonical_evidence_status: complete
resource_closeout_status: complete
allowed_paths:
  - doc/tasks/SIDECAR-SCHEMA-STALE-1.md
  - apps/desktop-avalonia/build/sidecar/**
  - packaging/**
  - doc/TASK_LEDGER.md
  - verification/SIDECAR-SCHEMA-STALE-1/**
---

# SIDECAR-SCHEMA-STALE-1：测试夹具 sidecar 的 schema 版本严重落后

> ## ⚠️ 勘误（2026-11-16，依据独立复核 r1 的 P0-1）
>
> **本卡初版的诊断方向是错的，必须更正。**
>
> 初版断言：「`package.ps1` 产出的安装包内含过时 sidecar，用户安装后程序启动即 fail-closed，产品不可用。」
>
> **这个断言不成立。** 独立复核（`doc/reviews/SIDECAR-SCHEMA-STALE-1-r1.md`，CHANGES_REQUESTED）查明：
>
> - 变更前 release `NewManga-e2c9fd058` 内 sidecar 的 `schema.pyc` 与新构建 bundle **字节完全相同**
>   （`sha256 f1058b07…`，`co_names` 含 V1..V14，`default_migrations` 14 条）⇒ **产品包一直是 v14**；
> - 尺寸也对得上：835.25 − 43.56 = 791.69 MiB（旧 release 1,024 文件 / 791.69 MiB）；
> - 卡面点名的 `NewManga-0.2.0-dev-win-x64-models` 实测内嵌 **v14** sidecar（直接反证）；
> - 我自己引用的 B1 失败日志 L72 就写着失败的 sidecar 是
>   **`HOST-CORECLIENT-1\sidecar-copy`**，不是 bundle。
>
> **v6 的真实实体是「测试夹具副本」**：`test.ps1` 的 `SidecarDirectory` 默认指向
> `workspace/task-envs/HOST-CORECLIENT-1/sidecar-copy`，
> 而 `prepare-sidecar.ps1:16` 的默认 `-Source` 指向**已退役的 Tauri 路径**
> `apps/desktop/src-tauri/target/release/resources/core-sidecar`（2026-10-23 的产物）。
> V6 加于 10/23 15:01、V7 加于 11/03 ⇒ 那个 legacy 产物**必然只到 v6**。
>
> **真缺陷因此重新定义为**：
> 1. `prepare-sidecar.ps1` 默认从**已退役的 Tauri 产物**取 sidecar；
> 2. `test.ps1` 的夹具副本「**存在即不刷新**」，导致过期副本被长期使用。
>
> 这两条已于 2026-11-16 修复（见 §修复）。**产品包从未损坏这一结论不因本卡而改变。**



## 怎么发现的

`RELEASE-PACKAGE-1` AC6 要求「`scripts/test.ps1` 全绿」。补跑后 **3 failed**，
全部停在 `core.ping` **握手阶段**，stderr：

```
RuntimeError: database schema v14 is newer than this application knows (v6); refusing to run
```

## 核实（不是猜测）

### 源码侧的 schema 版本

`src/infrastructure/sqlite/schema.py`：

```
SCHEMA_VERSION_V1 = 1
...
SCHEMA_VERSION_V14 = 14
```

且 `default_migrations()` 返回 **V1 … V14 共 14 条迁移**。

`core_assembly.py:1179`：

```python
latest_known = max(migration.schema_version for migration in migrations)
```

⇒ **源码认识的最新 schema = v14**。

### sidecar bundle 侧

`apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar/core_service.exe`
（构建时间 **2026-11-15 03:16**，400 KB 的 launcher）—— 运行时只认识到 **v6**。

### 结论

**sidecar bundle 落后源码 8 个 schema 迁移版本（v6 → v14）。**

## 影响（这才是重点）

这不是"测试环境脏了"，是**打包产物不可用**：

`apps/desktop-avalonia/scripts/package.ps1` 产出的安装包
（如 `NewManga-0.2.0-dev-win-x64-models`）**内含这个 v6 的 sidecar**。
用户安装后，若数据根是 v14 schema（当前源码迁移后的状态），

⇒ **sidecar 启动即 fail-closed 拒绝运行，产品无法启动。**

| Gate | 影响 |
|---|---|
| A（四件套） | **不受影响**（不跑 sidecar，30 skipped） |
| **B 条件 4（安装矩阵）** | **直接影响** —— 包不可用 |
| B 条件 5（翻译质量） | 间接（`translate` 命令需 sidecar） |
| C/D | 不涉及 |

## 为什么之前没被发现

四件套口径（`NewManga.CoreClient.Tests` 单独跑）**跳过全部 30 个 sidecar 测试**，
所以一直 203/0/30 全绿。只有 `scripts/test.ps1`（配夹具、0 skipped）才暴露出来。

⇒ **这是一个"门禁盲区"**：日常门禁跑不到真实 sidecar，导致 bundle 过期不被发现。

## 修复方向

| 方案 | 做法 | 代价 |
|---|---|---|
| **A（推荐）** | 用 `packaging/m2ac5/build_sidecar.ps1` + `core_sidecar.spec` 重建 sidecar bundle | 构建耗时（约 800 MB / 1000+ 文件）；产物 git-ignored |
| B | 若短期无法重建，至少在 `package.ps1` 里加**schema 版本一致性校验**，打包时对比 sidecar 认识的版本与源码最新版本，不一致则失败 | 小；但不能让包可用 |

**建议 A + B 都做**：先 B（防止再发出坏包），再 A（真正修复）。

## Acceptance Criteria

- [x] **AC1 版本对照已核实（勘误后口径）**：源码 schema.py 确实 SCHEMA_VERSION_V1..V14、default_migrations() 14 条；**但原「bundle 认 v6」的判断错误** —— v6 的实体是测试夹具副本，产品 bundle 变更前已是 v14（r1 复核以 .pyc sha256 f1058b07… 证明） <<MET>>
- [x] **AC2 影响面判定（勘误后口径）**：**产品包不受影响**（从未损坏）；受影响的是 scripts/test.ps1 的全部 sidecar 测试（夹具用 legacy v6 副本，握手必败） <<MET>>
- [x] **AC3 门禁盲区记录**：说明"四件套跳过 sidecar 测试"导致未被发现。 <<MET>>
- [x] **AC4 打包加一致性校验**：`package.ps1` 在打包前比对 sidecar schema 版本与源码最新版本，不一致则失败并给出明确指示。 <!-- 实施于 package.ps1：读 bundle 的 build-manifest.json，缺失则拒绝打包；存在则比对 manifest.schema_version 与源码 schema.py 的 SCHEMA_VERSION_V<n> 最大值，不等则拒绝。两个场景实测：① 无 manifest → EXIT=1「cannot prove which schema it understands」；② manifest 声明 v6 而源码 v14 → EXIT=1「built against schema v6 but the source tree is at v14 ... Rebuild the bundle」。build_sidecar.ps1 已改为构建时写入该 manifest。 --> <<MET>>
- [x] **AC5 重建或登记**：重建 sidecar bundle（或明确登记为需专门构建轮次，附操作步骤）。 <!-- 2026-11-16 DSH：已用 build venv（Python 3.14.6 + PyInstaller 6.22.3）执行 packaging/m2ac5/build_sidecar.ps1 -Force 重建成功，bundle 835.3MB，build-manifest.json 写入 schema_version=14；package.ps1 安全阀由拒绝转为放行（sidecar schema check: v14 == source v14）；test.ps1 重跑后 schema v14/v6 错误归零。详见 workspace/tasks/SIDECAR-SCHEMA-STALE-1/rebuild-report-v2.md。**重要限制**：test.ps1 仍有 **5 failed / 251 passed**（schema 错误已归零，但新 bundle 暴露了 5 个全新类别失败：INVALID_REQUEST / pending 超时等），与 schema 无关，需独立诊断，本卡不宣称 test 全绿。 --> <<MET>>
- [ ] **AC6 独立复核**：固定 head 交独立上下文 Review。 <<BLOCKED: 待 AC4/AC5 实施后一并送审>>

## 禁止范围

- 不得为让测试变绿而修改 `schema.py` 的版本常量；
- 不得让 sidecar 绕过 schema 版本校验（那是正确的防御）；
- 不得把 v14 数据库降级到 v6（会丢数据）。

## 说明

本卡发现的缺陷**比 B1 的任何一条都严重**：其他都是文档/证据缺口，这条是
**交付物实际不可用**。优先级应高于继续清 B1。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-SSS-01 | AC1/AC2/AC3 版本对照与影响面证据 | verification/SIDECAR-SCHEMA-STALE-1/version-check.log | 4f786190c | cee05df9c31944d9165c898a33da24ca31f1b7ebb212574584a2fe0750d5f219 | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/SIDECAR-SCHEMA-STALE-1/ | NOT_APPLICABLE | — | — | 新增证据，无迁移/归档 |

## Closeout Record

- Closeout：2026-11-16，DSH（核实与登记；修复未做）。
- **缺陷**：sidecar bundle 落后源码 **8 个 schema 迁移版本**（bundle 认 v6，源码已 v14）。
- **影响**：package.ps1 产出的安装包内含该 v6 sidecar ⇒ 面对 v14 数据根时
  **启动即 fail-closed，产品不可用**。Gate 条件 4（安装矩阵）直接受影响。
- **为什么之前没发现**：四件套口径跳过全部 30 个 sidecar 测试（0 skipped 只在
  scripts/test.ps1 里出现），形成**门禁盲区**。
- **本卡只做核实与登记**，AC4（打包加一致性校验）与 AC5（重建 bundle）标 BLOCKED，
  属独立实施轮次。**状态 closed_with_limitations 即"已定位但未修复"**。

## 修复（2026-11-16，回应 r1 复核 P0-2）

r1 复核指出：本卡前三轮提交只改 package.ps1 / uild_sidecar.ps1 / 卡面，
**没有修真正的缺陷**（测试夹具的选取与刷新逻辑），实质修复只是对 workspace 副本的手工替换，不可复现。

已按复核建议补齐两处：

| 文件 | 改动 |
|---|---|
| pps/desktop-avalonia/scripts/prepare-sidecar.ps1:16 | 默认 -Source 从**已退役的 Tauri 路径** pps/desktop/src-tauri/target/release/resources/core-sidecar 改为 Avalonia 构建产物 uild/sidecar/core-sidecar/core-sidecar；新增 NEWMANGA_SIDECAR_SOURCE 覆盖 |
| pps/desktop-avalonia/scripts/test.ps1:39-73 | 夹具副本不再「存在即用」：读 uild-manifest.json 比对 schema_version 与 git_head，缺失/不等则**先删除再重建**（删除是必要的 —— 
obocopy /E 叠加会让 _internal 混杂，导致 Failed to import encodings module） |

### 实测（把夹具 manifest 伪造成 v6/旧 head）

`
sidecar fixture: refreshing ...sidecar-copy (fixture schema v6 != build bundle v14)
刷新后 git_head: f7d273d9a  schema: 14
`

自动刷新生效，无需手工干预。

## 仍未达成（不掩盖）

scripts/test.ps1 **仍未全绿**：schema/管道/encodings 三类错误已归零，但仍有
**5 failed / 251 passed**（INVALID_REQUEST、pending 超时等），
判断为新 bundle 与 v14 源码对齐后暴露的**测试期望过时**问题，需独立诊断。
本卡**不宣称 test 全绿**。
