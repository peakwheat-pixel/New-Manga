# P09-MANAGED-READ-ROOT-TRUST-1 — 8 处逐处映射与判别力

- base_commit：`b8a1e519703f13af73b320dded117004b4bb189a`
- 测试文件：`tests/security/test_p09_managed_read_root_trust.py`
- 判别力证据：`logs/ac3-discrimination.txt`（同一测试文件在 base 源码快照上运行 → 8/8 FAIL；
  在当前 worktree → 8/8 PASS）与 `logs/ac1-before-fix.txt` / `logs/ac1-after-fix.txt`。
- **行号说明**：Task 表引用的是 R5b 审计时（`34fe1069f` 时代）的行号；base 上同一条语句已经漂移。
  第三列给出 **base 实际行号（修改前）**，与 Task 原行号对照。

## 映射表

| # | Task 原行号 | base 实际行号（修改前） | 原缺陷（同一根因的具体形态） | 修法（逐处） | 对应测试 | base | current |
|---|---|---|---|---|---|---|---|
| 1 | `core_service.py` 464–467 | `core_service.py:518-537` `assemble_production_core.read_original_page` | root 与 candidate 双双 `resolve()` 后 containment，再按名字 `read_bytes()` | `CoreServices.managed_root_trust.read_bytes(page.managed_original_ref)`；`E_NOT_FOUND`→`None`，身份/越界族→原 `ValueError` | `test_site1_read_original_page_reader_refuses_repointed_ancestor` | FAIL | PASS |
| 2 | 1923–1926 | `core_service.py:2070-2075` `handle_resolve_page_resource` | 同上，随后 `publish_original(source…)` 按名字复制 | 先按后缀收敛错误面 → trust 读字节 → 私有临时文件交给发布器（关闭路径交接窗口）；越界→原 `RuntimeError`，`E_NOT_FOUND`→原 `RegionLookupError` | `test_site2_resolve_page_resource_refuses_repointed_ancestor` | FAIL | PASS |
| 3 | 2490–2493 | `core_service.py:2636-2643` `_checked_managed_path`（+`_reader_sha256` 2645-2650） | **R5b 原始复现点**：返回 `resolved` 路径，调用方再按名字读/发布 | 返回**句柄规范路径**；`_reader_sha256` 改为句柄流式摘要；导出 hash/providers 改为 `digest_of`/`read_bytes`（每次调用自带完整校验） | `test_site3_checked_managed_path_refuses_repointed_ancestor` | FAIL | PASS |
| 4 | 2533–2542 | `core_service.py:2679-2694` `_is_protected_export_target` | 托管侧 `resolve()` 后与 target 比较；重定向后真实 managed original 不再受保护 | 托管侧改为**纯词法** `trust.canonical_of(ref)`（零文件系统访问）；target 侧保留一次 `resolve()`（用户路径，无冻结身份） | `test_site4_protected_export_target_uses_frozen_managed_baseline` | FAIL | PASS |
| 5 | `core_assembly.py` 227–230 | `core_assembly.py:207-233` `_ManagedPageCatalog.image_state` | 双侧 `resolve()`；junction 后外部文件判 `ok` | `trust.verify_existing(ref)` → `ok`/`invalid` | `test_site5_image_state_refuses_repointed_ancestor` | FAIL | PASS |
| 6 | 236–239 | `core_assembly.py:235-242` `_ManagedPageCatalog._uri_within` | 同上；返回 `file://` URI 给 QML | `trust.verify_existing(ref)` → 句柄规范路径 URI / `""` | `test_site6_uri_within_refuses_repointed_ancestor` | FAIL | PASS |
| 7 | 270–273 | `core_assembly.py:262-288` `_ManagedPageImageSource._page_image` | 同上；`QImage(str(path))` 按名字打开 | `trust.read_bytes(ref)` → `QImage.fromData(bytes)`：解码输入即已验句柄字节 | `test_site7_page_image_source_decodes_verified_handle_bytes` | FAIL | PASS |
| 8 | `handle_resolver.py` 609–617 | `handle_resolver.py:602-620` `resolve_namespace_identity` | walk 后 `resolve()`，再与句柄 final path 比 —— **拿被污染值验证自己**（R5b 与 R6 各自独立复现） | 词法 `expected=os.path.abspath(str(path))` 在任何文件系统访问前冻结 → 单次打开 → 规范路径/身份只来自句柄 → `final==expected` 才接受；既有 reparse 策略保留 | `test_site8_resolve_namespace_identity_refuses_swap_between_walk_and_open` | FAIL | PASS |

## 链接策略与 AC2 对照（显式取舍）

| 场景 | 策略 | 证据 |
|---|---|---|
| 配置根**之上/本身**是 reparse，且对象身份仍等于启动快照 | **允许**（合法部署：数据目录迁移留 junction、data root 是链接） | 测试全程以 `live -> real` junction 作为数据根的祖先；换 root 前的合法读取断言（site 1–7 各自的第一段断言）+ `test_ancestor_junction_is_allowed_for_legal_reads`（base/current 均 PASS） |
| 配置根**之下**任何 reparse 段（含指向根内兄弟目录的链接） | **拒绝** | `test_internal_link_below_the_root_is_refused`（base FAIL → current PASS） |
| 「任一祖先 reparse 即拒绝」 | **未采用**（会破坏上表第一行两类合法部署；对象身份快照已提供更强判据） | 设计文档第四节；`DESIGN-expected-identity.md` |
| `resolve_namespace_identity` 既有「盘符根起拒绝 reparse」 | **保留**（derived/GC 域契约） | `tests/m2_resource_channel/test_handle_resolver.py` 106 passed（含 `test_reparse_derived_root_is_refused`、`test_race_equivalent_slipped_walk_still_refused`） |

## 共享基建

`src/infrastructure/resource_channel/handle_resolver.py`：

- `ManagedRootTrust.capture(root)`：装配时一次句柄快照（对象身份 + 句柄规范路径 + 词法绝对根）。
- `read_bytes` / `digest_of` / `verify_existing`：每次调用 = 词法冻结 → 打开并验根身份 →
  打开目标并验句柄规范路径 → 通过同一句柄读取。
- `canonical_of`：纯词法比较（site 4）。
- 装配处：`bootstrap/core_assembly.assemble_core_services`（`storage.ensure_layout()` 之后）
  创建快照，写入 `CoreServices.managed_root_trust`，并传给两个私有读取类。

## 未覆盖/非目标（与设计文档一致）

- 叶子**内容**身份仍由既有 `sha256` pin 负责；本 Task 不新增叶子身份快照。
- 硬链接与「同名目录替换」的残余风险见 `DESIGN-expected-identity.md` 第六节；
  前者属于托管树写权限/ACL 边界，后者需要 `NtCreateFile` 相对句柄链（删除域同类基建）。
- 第 5/6 处（QML `file://` 交接）与第 3 处 Reader 预览发布分支（发布器按名字复制）存在
  **交接窗口**残余风险，已显式记录；第 2 处的同类窗口已用「已验字节 → 私有临时文件」关闭。
