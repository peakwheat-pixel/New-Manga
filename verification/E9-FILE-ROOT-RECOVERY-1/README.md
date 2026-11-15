# E9-FILE-ROOT-RECOVERY-1：实施方案 E，**E-9 已解锁**

基线 `17e8efa56`。依据 `doc/reviews/E9-UNLOCK-ADJUDICATION-zcode-2026-11-15.md`。

## 1. 改动（一处判别分支）

`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceOperationCoordinator.cs` 的
`MintRecoveryGrantsAsync`：

```csharp
// 改前：任何非 folder 源一律 typed 拒绝
if (!string.Equals(sourceKind, "folder", StringComparison.Ordinal))
{
    throw new SourceAccessException("SOURCE_PLAN_UNAVAILABLE");
}

// 改后：非 folder 源只要 roots[0] 确实是文件就放行
if (!string.Equals(sourceKind, "folder", StringComparison.Ordinal)
    && !File.Exists(roots[0]))
{
    throw new SourceAccessException("SOURCE_PLAN_UNAVAILABLE");
}
```

同时**更正了那段注释**：旧注释断言"registry ROOT 是授权边界（目录），不是容器"，并称
"没有任何权威路径可用" —— **那是基于错误前提**。新注释写明：
`SourceImportModels.IssueGrantsAsync` 把**同一个 `path`** 同时传给 `FindOrRegisterRootAsync`（注册为 root）
与 `IssueAsync`（作为 sourcePath），且 `RegisterRoot` 写 `roots = [path]`
⇒ **对容器源，`roots[0]` 就是容器文件本身**。

**fail-closed 保留**：若有人给容器 kind 注册了**目录** root，`File.Exists` 为假 ⇒ 仍然 typed 拒绝。

**契约零改动**：`verify_pins` 仍 **18/18**。

## 2. 验收证据（三条独立证据）

### 2.1 解锁的直接证据（预期红转绿）

改代码后、翻回断言前，先跑那 2 个当时断言"必须拒绝"的测试：

```
Assert.Throws() Failure: No exception was thrown
失败! - 失败: 1
```

⇒ **`AcknowledgeAsync` 不再拒绝** —— 判别分支生效。

### 2.2 断言翻回后全量 Host.Tests

```
2 failed / 347 passed / 50 skipped / 399   (opt-in: NEWMANGA_FEA11_IPC=1)
```

- **剩余 2 个失败**：`CrashPoint_Park` / `CrashPoint_Recover`
  —— 缺 `NEWMANGA_FEA11_CRASH_STATE` 的**前置 assert**（环境类，与本改动无关；
  驱动脚本会自己设那个变量）。
- **E-9 原先挡住的 `Ack_SendsAFreshAuthorization...` 与 `Recovery_UsesAFreshAuthorization...` 已通过**。
- 断言**翻回为原始正向断言**（`acknowledged` / `recovered`），**未放宽**。

### 2.3 ★ 真实崩溃点驱动：`NOT_SATISFIED` → **PASS**

`verification/FEA-11-HOST-AUTH-3/tools/crash-ack.ps1`（park → kill 整棵进程树 → recover）：

```
CHECK commit_digest_match=1
CHECK distinct_host_pid=1
CHECK distinct_core_session=1
CHECK source_sha256_unchanged=1
CHECK rows_unchanged=1
CHECK gates_open=1
CHECK second_call_idempotent=1
CHECK fresh_grant=1
CHECK page_bindings_fields_unchanged=1
CHECK journal_present=1
CRASH_POINT=PASS acknowledge_once=1 gates_open=True rows_unchanged=True second_call_idempotent=True
  commit_digest_match=True distinct_host_pid=True distinct_core_session=True fresh_grant=True
  source_sha256_unchanged=True sidecar_proven_dead=1
EXIT=0
```

**改前**（`1984eaf6e`）：`CRASH_POINT=NOT_SATISFIED`，`SOURCE_PLAN_UNAVAILABLE`，`EXIT=12`。
**改后**：**PASS，EXIT=0**。

证据归档：`verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-0a1d9d2eb425495fad533910d0ef414a/`。

## 3. 证据卫生

跑 opt-in 与驱动前快照 `verification/` 下 **14517** 个受控文件，跑完复查 **`polluted=0`**。

## 4. 仍未做（诚实）

- **负例测试未加**：裁决要求"目录 root + 容器 kind 仍须 typed 拒绝"要有测试固定住。
  当前**只有代码逻辑**（`File.Exists`），**没有测试**。⇒ 若有人把条件改成无条件放行，现有测试**不会红**。
- `E9-KNOWN-LIMITATION-REGISTER.md` **尚未按裁决回退**（仍写着限制成立）。
## 5. 负例测试已补（`E9-NEGATIVE-TEST-1`，2026-11-15）

上一节 §4 登记"负例测试未加"。**本节补上。**

### 5.1 做法：把判别条件提取为 internal 纯函数

原实现把判别写在 `MintRecoveryGrantsAsync` 内部，方法私有、依赖多，**无法在不改可见性的前提下单测**。
改为提取：

```csharp
internal static bool IsRecoverableRoot(string sourceKind, string root) =>
    string.Equals(sourceKind, "folder", StringComparison.Ordinal) || File.Exists(root);
```

调用点变为 `if (!IsRecoverableRoot(sourceKind, roots[0])) throw ...`。
**行为完全不变**（同样的两个分支），只是把判别变成可测的纯函数。

配套：`src/NewManga.Host/AssemblyInfo.cs` 新增 `[assembly: InternalsVisibleTo("NewManga.Host.Tests")]`
（沿用 `NewManga.App` 已有的同一模式）。

### 5.2 测试（`RecoveryRootPredicateTests.cs`，6 个）

| 测试 | 断言 |
|---|---|
| `FolderRoot_IsAlwaysUsable_BecauseTheRootIsTheContainer` | folder + 目录 root → **true**（folder 的 root 就是容器） |
| `ContainerRoot_MustBeAnExistingFile` | zip + 不存在的路径 → **false**；创建该文件后 → **true** |
| `DirectoryRoot_ForAContainerKind_StaysRejected`（Theory：zip/cbz/pdf/image） | 目录 root → **false**；同目录下的真实文件 → **true** |

**每个 Theory 用例都同时断言"目录被拒"和"文件被接受"** —— 这样测试**不会因为一律拒绝而通过**。

### 5.3 判别力（实测）

把 `IsRecoverableRoot` 临时改成无条件 `true;`：

```
zip: a DIRECTORY root must not be treated as a container
image: a DIRECTORY root must not be treated as a container
pdf: a DIRECTORY root must not be treated as a container
cbz: a DIRECTORY root must not be treated as a container
```

**4 个用例全部变红，消息准确**。已还原（`PROBE` 计数 0）。

### 5.4 回归

全量 Host.Tests（`NEWMANGA_FEA11_IPC=1` + `NEWMANGA_BUILD_PYTHON`）：

```
2 failed / 353 passed / 50 skipped / 405
```

- 对上一轮（`2 failed / 347 passed / 50 skipped / 399`）：**passed +6、total +6**（正是新增的 6 个用例）；
- **failed 仍为 2**（`CrashPoint_Park` / `CrashPoint_Recover`，缺 `NEWMANGA_FEA11_CRASH_STATE` 的**前置 assert**，环境类）；
- **skip 未增加**（仍 50）。

### 5.5 剩余局限（诚实）

**上述负例测的是"判别函数"本身，不是"整条 ACK/Recovery 调用链在目录 root 下的行为"。**
端到端负例需要构造"journal 指向一个目录 root 的 registry"，而 journal 是 apply 时由生产链路写入、
测试无法篡改 —— 要做就得改产品代码或写一个全新的 fixture 链，成本远超收益。

**⇒ 这条端到端负例仍未做**，但它覆盖的是"产品的 journal 是否可能指向目录 root"这一命题，
而生产唯一写 journal 的路径（`IssueGrantsAsync`）**只传用户选中的那个 path**，
所以该场景需要**人为构造非法注册**才会出现。**判别函数层的测试已经守住"即使出现也不会误放行"。**
