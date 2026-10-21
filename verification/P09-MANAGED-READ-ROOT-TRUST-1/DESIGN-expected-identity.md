# P09-MANAGED-READ-ROOT-TRUST-1：设计答案——「期望身份」从哪来

- 状态：设计冻结（实施前的第一交付物；先于任何产品代码修改）
- 作者：DeepSeek Harness（Owner: `p09-root-trust`）
- base_commit：`b8a1e519703f13af73b320dded117004b4bb189a`
- branch / worktree：`dsh/P09-MANAGED-READ-ROOT-TRUST-1` / `G:/CODEX/New Manga.workspace/worktrees/P09-MANAGED-READ-ROOT-TRUST-1`
- 来源：`P09-AC3-DELETE-HARDEN-1` R5b P2（`verification/P20-CLOSE-BOUND-HARDEN-2/r5b-p2-read-path-draft.md`）、R5b/R6 原始复现（`workspace/agent-output/coordinator/codex-r5b-result.md`、`codex-r6-result.md`）
- 本文件只回答设计问题并冻结修法方向；**不是** Handoff，不声明 AC 通过。

---

## 一、问题：被污染的期望值

8 处的共同缺陷不是「没做 resolve」，而是**「期望值本身来自一次可被竞态改变的名字解析」**：

```text
root   = <configured root>.resolve()      # 期望值的一半
cand   = <candidate>.resolve()            # 期望值的另一半
cand.relative_to(root)                    # 用两个「受污染的值」互相验证
```

若在两次解析之间把 **configured root 的祖先**替换为指向外部目录的 junction，两侧一起漂移，
containment 恒真，随后按名字读/发布，外部字节被读出（R5b 已实测；本 worktree 用
`verification/P09-MANAGED-READ-ROOT-TRUST-1/ac1-r5b-repro.py` 在 base 代码上复现，见该探针输出）。

`handle_resolver.resolve_namespace_identity`（第 8 处）是同一根因的显式版本：它把
**句柄的 final path 与已经重定向后的 `resolved` 名字**比对 —— **拿被污染的值验证自己**。

**结论：再加一次更仔细的 `resolve()` 不解决问题。** 只要「期望身份」是运行时解析出来的，
它就与被验证对象共享同一条可被替换的名字路径。

---

## 二、设计答案（冻结）

> **期望身份 = 启动装配时，对配置根实际打开的那一个句柄所携带的对象身份
> `(dwVolumeSerialNumber, nFileIndexHigh<<32|nFileIndexLow)`，加上该句柄报告的规范路径
> （`GetFinalPathNameByHandleW`，去掉 `\\?\` 前缀）；配置根的**词法绝对路径**
> （`os.path.abspath`，不跟随链接）作为名字侧基准，单独保存。**

三个分量缺一不可：

| 分量 | 取值时机 | 为什么必须是它 |
|---|---|---|
| **对象身份** `(volume, file_index)` | 装配时（任何业务读取之前）打开配置根目录句柄，`GetFileInformationByHandle` | 身份是**对象**的属性，不是名字的属性。之后无论何时把祖先换成 junction/符号链接/新目录，**同一个名字到达的是另一个对象**，身份必然不同 → 可判定。 |
| **规范路径**（句柄报告） | 同一句柄，`GetFinalPathNameByHandleW` | 它是「启动时这个对象在哪里」的权威答案；后续每次读取都要重新打开配置根并**再次用句柄报告路径**，与它比对（根自身被搬走/替换 → 拒绝）。 |
| **词法绝对路径** | `os.path.abspath(str(configured_root))`，**纯字符串、零文件系统访问** | 用来把数据库里的相对引用 / `storage.absolute_path()` 拼出的绝对引用**在字符串层面**折算成「配置根下的相对段」。这一折算必须在任何名字解析之前完成，且不随后续解析变化。 |

**写入位置**：装配时生成 `ManagedRootTrust`（`src/infrastructure/resource_channel/handle_resolver.py`），
作为 `CoreServices.managed_root_trust` 随 Core 生命周期固定；`core_assembly` 的三处读取类
（`_ManagedPageCatalog`、`_ManagedPageImageSource`）在装配时接收同一个实例。**不是**每次请求现取。

### 每次读取的守卫序列（全部 8 处共用同一原语）

1. **词法折算**：引用 → 相对段序列（拒绝 `..`、`.`、空段、盘符相对形式、绝对路径越界）。
   此步零文件系统访问；期望值在此刻冻结。
2. **打开配置根并验证身份**：按词法绝对路径打开配置根目录句柄；
   `identity(handle) != 快照身份` → **typed 拒绝**（`FILE_IDENTITY_CHANGED`）；
   句柄 final path ≠ 快照规范路径 → 拒绝。
3. **打开目标并验证对象类型与规范路径**：从已验配置根的名字打开目标；
   - 已打开句柄的 `FILE_ATTRIBUTE_DIRECTORY` 必须为 0（**R-001**：同名**目录**替换会让规范路径
     恰好等于期望值，只有打开后的对象类型能识别；旧调用方的 `is_file()` 不再作为依赖）；
   - 句柄 final path 必须等于 **「快照规范路径 + 词法相对段」**（大小写不敏感比较）；不等 → 拒绝
     （覆盖：根下任何内部 junction/符号链接、祖先在步骤 2 之后被替换、叶子被指向他处）。
4. **读通过句柄**：`ReadFile`/`GetFileInformationByHandle` 全部作用在步骤 3 打开的同一个句柄上；
   **校验与使用是同一个对象**，不存在「检查后再按名字打开」的第二次解析（删除路径已用同一原则：
   `win_unlink.unlink_by_handle` 的句柄链）。

**为什么它满足「竞态发生前固定、不随后续解析变化」**：

- 快照取自**装配时刻的真实句柄**，之后没有任何代码再问「根应该是什么」；
- 竞态只能改变「名字现在指向哪个对象」，改变不了快照里的对象身份；
- 步骤 2 在**每次读取时**重新打开并比对身份，因此「装配后被替换的祖先」在第一次读取就被拒绝；
- 步骤 3/4 在**同一个已验对象之下**完成，替换发生在打开之后也不能改变已打开句柄指向的对象。

### 叶子身份说明（明确非目标）

本设计**不**为每个叶子文件引入「期望身份」。读取的 containment 判据是
**「叶子句柄报告的规范路径 == 快照根 + 词法引用」**，它是名字无关的；叶子**内容**身份仍由既有
上层 pin 负责（Reader/Export 的 `sha256` 校验、`_reader_sha256`），本 Task 不放宽也不新增。
硬链接替换属于既有 ACL/不可变层边界，见「六、残余风险」。

---

## 三、第 8 处：`resolve_namespace_identity` 的期望身份

该函数的调用方（derived root / catalog DB）**不经过 managed root 装配**，且 R5b/R6 的复现是
「首次 `_lstat_reparse_walk(path)` 之后、`path.resolve()` 时注入祖先 junction」。
因此它的期望身份来源是同上原则的**函数内局部版本**：

```text
expected = os.path.abspath(str(path))        # 1) 词法基准：在任何文件系统访问之前固定
_lstat_reparse_walk(path)                    # 2) 既有策略不变：盘符根到 path 任一 reparse 即拒绝
handle = open(expected)                      # 3) 只打开一次
final  = GetFinalPathNameByHandle(handle)    # 4) 规范路径只来自句柄
identity = GetFileInformationByHandle(handle)# 5) 身份只来自同一句柄
require normalized(final) == normalized(expected)   # 6) 拿「打开后的对象」对「打开前的词法名字」
```

- 注入发生在 3) 之前：打开落到外部对象，`final` ≠ `expected` → 拒绝（旧实现会把 `final`
  与已经重定向的 `resolved` 比，恒等 → 接受）。
- 注入发生在 3) 之后：句柄仍指向原对象，返回值来自句柄；调用方用 `NamespaceBinding`
  里冻结的 `(derived_root, identity)` 四元组再次校验，行为不变。
- 既有更严格策略（「盘符根起任一 reparse 即拒绝」）**保留**，不因本 Task 放宽；这是
  derived/GC 删除域的既有契约，不属于「合法业务读取」的 managed root 链接策略。

---

## 四、链接策略（显式取舍，AC2 要求）

**采用的策略不是「任一祖先 reparse 即拒绝」。** 具体：

| 位置 | 策略 | 理由 |
|---|---|---|
| **配置根之上（祖先）或配置根本身是 reparse** | **允许 —— 当且仅当对象身份仍等于启动快照** | 用户把 managed 数据迁移到别的盘、原位置留 junction，或 data root 本身是链接，是合法部署；快照钉住的是**对象**，名字拼写变化不影响读取。替换/重定向到别的对象 → 身份不匹配 → 拒绝。 |
| **配置根之下（managed 布局内部）的任何 reparse 段** | **拒绝** | Managed Copy 的不可变布局内部引用必须指向真实的受控目录；内部链接可把「受保护的 original」经兄弟章节的链接读出，且与删除路径 `remove_managed` 的既有语义一致（删除路径同样拒绝内部链接）。判据是第 3 步的规范路径比对（链接会把 final 路径变成目标路径），不是「看到 reparse 就拒绝」。 |
| **`resolve_namespace_identity` 的既有「盘符根起拒绝 reparse」** | **保留** | 该函数服务 derived/GC 删除域，其「别名根不可判定为同一命名空间」的契约已在 `verification/P09-AC3-DELETE-HARDEN-1` 中冻结；本 Task 不改删除域语义。 |

作为对照：**「任一祖先 reparse 即拒绝」未被采用**，因为它会直接破坏上表第一行两种合法部署；
且本设计已有更强的对象级判据（身份快照），不需要用一刀切牺牲合法用法。

---

## 五、8 处逐处映射（base `b8a1e51` 实际行号）

> Task 表引用的是 R5b 审计时的行号（`34fe1069f` 时代）；base 上同一条语句已漂移，
> 下表给出 **base 实际行号**（修改前）。

| # | 位置（base 行号） | 原实现的问题 | 修法（逐处） |
|---|---|---|---|
| 1 | `src/bootstrap/core_service.py:518-537` `assemble_production_core.read_original_page` | `storage.root.resolve()` + `candidate.resolve()` 双侧解析后 containment，再 `read_bytes()` | `core.managed_root_trust.read_bytes(page.managed_original_ref)`，读通过句柄；`E_NOT_FOUND` → 维持 `None`，其余拒绝 → 维持 `ValueError("managed original escaped the Managed Copy root")` |
| 2 | `src/bootstrap/core_service.py:2070-2075` `handle_resolve_page_resource` | 同上，随后 `publish_original(source...)` 按名字复制 | 同上，`read_bytes` 拒绝 → 维持 `RuntimeError`；`E_NOT_FOUND` → 维持 `RegionLookupError` |
| 3 | `src/bootstrap/core_service.py:2636-2643` `_checked_managed_path`（+ 2645-2650 `_reader_sha256`） | 该函数是 R5b 的原始复现点：接受被祖先 junction 重定向的路径 | 返回**句柄规范路径**；`_reader_sha256` 改为通过句柄摘要；导出 provider 改为每次调用时 `read_bytes`/`digest_of`（惰性 provider 也自带完整校验）；预览发布分支的句柄→路径交接见残余风险 |
| 4 | `src/bootstrap/core_service.py:2679-2694` `_is_protected_export_target` | 托管侧 `resolve()` 后与 target 比较；祖先被重定向后「真正受保护的 managed original」不再被识别 → 导出可覆盖它 | 托管侧改为**纯词法** `canonical_of(ref)`（零文件系统访问，来自快照规范根）；target 侧保持 `target.parent.resolve()/name` 一次解析；比较用 `normcase` |
| 5 | `src/bootstrap/core_assembly.py:207-233` `_ManagedPageCatalog.image_state` | 双侧 `resolve()`；junction 后把外部文件判为 `ok` | `trust.verify_existing(ref)`（打开+身份+规范路径+存在性），拒绝/缺失 → `invalid` |
| 6 | `src/bootstrap/core_assembly.py:235-242` `_ManagedPageCatalog._uri_within` | 同上；返回 `file://` URI 给 QML | `trust.verify_existing(ref)`，拒绝 → `""`；合法 → 句柄规范路径的 URI |
| 7 | `src/bootstrap/core_assembly.py:262-288` `_ManagedPageImageSource._page_image` | 同上；随后 `QImage(str(path))` 按名字打开 | `trust.read_bytes(ref)` → `QImage.fromData(bytes)`：解码输入就是已验句柄读出的字节 |
| 8 | `src/infrastructure/resource_channel/handle_resolver.py:602-620` `resolve_namespace_identity` | walk 后 `resolve()`，与句柄 final path 比 → 拿被污染值验证自己 | 见第三节：词法 `expected` 先冻结，单次打开，`final` 来自句柄 |

**第 1–7 处的共享基建**（本 Task 唯一新产品代码载体）：

- `handle_resolver.ManagedRootTrust`：
  `capture(root)` / `identity` / `canonical_path` / `read_bytes(ref)` / `digest_of(ref)` /
  `verify_existing(ref)` / `canonical_of(ref)`（纯词法）。
  `ref` 同时接受**数据库相对引用**与 `ManagedFileStorage.absolute_path()` 产出的**绝对路径**
  （后者用词法前缀折算，不解析）。
- 装配处 `core_assembly.assemble_core_services`：`storage.ensure_layout()` 之后
  `ManagedRootTrust.capture(managed_root)`，写入 `CoreServices.managed_root_trust` 并传给
  第 5–7 处的两个私有类。
- **不新增依赖**（`ctypes`/`os`/`pathlib` 均已在 `handle_resolver` 使用）；
  **不改 IPC 契约、Schema、ACL、前端**；**不改删除路径**（`win_unlink.py`、`managed_storage.remove_managed`、
  `render_preview`、`tile_cache_sweep`、`backup` 不动）。

错误面沿用既有类型，不新增 wire code：
- 读取原语抛既有 `TypedResourceChannelError`（`E_IDENTITY_CHANGED` / `E_OUT_OF_SCOPE` /
  `E_REPARSE` / `E_NOT_FOUND` / `E_OPEN_FAILED`），各处按原有异常类型/文案映射（见上表），
  因此 IPC 观测面不变。

---

## 六、残余风险（显式记录，不隐藏）

1. **交给其它消费者的路径/URI 存在交接窗口**：
   - 第 5/6 处（QML `file://`）：Python 侧在签发时完成「身份 + 规范路径」验证，但 QML 在
     Python 返回之后才按 URI 打开；若恰在交接窗口内重定向配置根祖先，QML 会打开外部路径。
     窗口由「Python 调用结束 → QML 打开」的最小调度间隙构成，且需要写权限修改配置根祖先。
   - 第 3 处的 **Reader 翻译预览发布分支**（`RenderPreviewPublisher.publish` 按名字复制）：
     发布器内部按名字重新打开源文件，交接窗口为 `_checked_managed_path` 返回后到 `publish`
     的 `open()` 之间。**发布器在删除域已加固范围内（`P09-AC3-DELETE-HARDEN-1`），本 Task 不改它。**
   - 第 4 处的 target 侧 `resolve()` 是**用户选择的目标**路径，不是托管数据；保留一次解析是
     正确语义（目标侧无「期望身份」可冻结）。
2. **叶子对象身份不在快照内，且「同名替换」不是 junction 重定向**：
   - 本设计的叶子判据是「叶子句柄报告的规范路径 == 快照规范根 + 词法相对段」。任何
     **junction/符号链接**重定向（无论是在根之上还是根之下）都会让句柄规范路径改变，
     因此被拒绝；这是 R5b/R6 复现的完整攻击面。
   - **硬链接**：托管树内出现指向根外同卷文件的硬链接时，句柄规范路径可能仍等于请求
     路径（名字相同、对象是外部数据），本设计不引入叶子内容身份。这需要**托管树写权限**，
     属于既有 ACL/不可变层边界，**不是本 Task 引入的暴露**，也不在本 Task 范围内收紧。
   - **同名对象替换**：
     - **文件 → 目录替换已关闭（R-001）**：守卫序列第 3 步在**已打开目标句柄**上拒绝
       `FILE_ATTRIBUTE_DIRECTORY`，因此同名目录不会再被当成可读文件（`image_state -> invalid`、
       URI 为空、读取 typed 拒绝）。
     - **整体 rename + 原名重建普通文件**：攻击者若在「根身份校验」与「叶子打开」之间把配置根
       整体改名、并在原路径重建同名**普通文件**，叶子规范路径仍可能等于期望值。这需要
       **配置根父目录的写权限**（与植入 junction 所需权限相同），且读到的是攻击者写入
       **同名路径**的数据；它不产生「读取根外路径字节」的 primitive。要彻底消除需要
       `NtCreateFile(RootDirectory=已验证根句柄)` 的相对句柄链（与删除域
       `win_unlink.unlink_by_handle` 同类基建），本 Task 的 8 处修复不依赖它，作为已知
       残余风险记录。
3. **托管树内部链接一律拒绝**是策略选择（第四节），会把「内部链接当合法用法」的用户
   判为 `invalid`/拒绝；这与删除路径既有行为一致，属于有意的 fail-closed。
4. **装配后 root 被整体搬走/替换**：所有读取拒绝（fail-closed）。这是设计目标，不是缺陷；
   运维影响是「数据目录被移动后需重启 Core」。

---

## 七、验证策略（判别力）

1. **before/after 差分**：`verification/P09-MANAGED-READ-ROOT-TRUST-1/ac1-r5b-repro.py` 用
   `git archive b8a1e51 src` 取出 **base 源码快照**，在同一探针里先跑 base（应 VULNERABLE：
   读到 `OUTSIDE` 字节）、再跑当前 worktree（应 SAFE：拒绝）。只在临时目录运行，不 checkout、
   不改仓库。
2. **逐处测试**：8 处各一条以上 pytest（`tests/security/test_p09_managed_read_root_trust.py`），
   每处都先用**合法读取不回归**断言（AC2），再用「装配后把配置根祖先 junction 重定向到外部镜像」
   断言拒绝（AC1/AC3）；第 8 处用「在 walk 与打开之间替换祖先」复现 R6 的注入时序。
3. **AC5**：`P09-AC3-DELETE-HARDEN-1` 的 9 个探针以仅改路径常量的副本在本 worktree 重跑，
   逐项记录 `injection_fired` / `outside_survived`，对照该 Task 记录的基线结果。
4. **AC4**：`git diff --stat` 证明无依赖清单/契约/Schema/ACL 变更；读取原语仅用既有标准库与既有模块。

## 八、边界

本设计不授权：改删除路径、改 IPC 契约/Schema/ACL/依赖、放宽 `resolve_namespace_identity` 既有
reparse 策略、引入叶子身份快照、或修改 `P09-AC3-DELETE-HARDEN-1` 的证据/探针。实施提交只落在
`dsh/P09-MANAGED-READ-ROOT-TRUST-1`。
