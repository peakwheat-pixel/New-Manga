# 段 B probes 独立分级记录

日期：2026-11-12  
范围：仅隔离 `tmp_path` probes、相应测试和 ZCode 已只读检查的源码路径。没有读取漫画图像或其他真实用户数据，没有运行测试，也没有修改产品文件。ZCode 未独立复现，以下分级是基于 probe 实测结果和源码路径核对的只读裁决。

## 裁决来源

- ZCode session：`sess_8a2f7064-f80d-49a5-b96f-6d5ba20dd1ca`
- 本次确认 turn：`turn_890a0c5b-cb00-4705-82c8-aba099964b7d`
- trace：`f6cbd72f-7b8c-435e-941e-0aaa189905db`
- 只读确认命令、生成时 HEAD、时点和 EXIT：[`probe-triage-confirmation-20261112.log`](../logs/probe-triage-confirmation-20261112.log)
- 原 probe 结果、命令和 EXIT：[`PROBES-RESULT-SEGMENT-B.md`](PROBES-RESULT-SEGMENT-B.md) 及其所列 JSON/log。

ZCode 本轮只复述并确认先前裁决；没有声称独立复现。分级基于隔离 probe 的实际结果、测试构造和指定源码行的静态核对。未运行产品测试或命令。

## Finding 1：目录 junction 下 managed publication 越界写

- Probe：`test_managed_publish_follows_directory_junction`
- 建议分级：**Medium severity / High confidence**
- 观察：隔离 probe 实测 `publish_wrote_outside_managed=true`。此路径调用真实 `ManagedFileStorage.publish`，不是 fixture 替身。
- 静态依据：`src/infrastructure/filesystem/managed_storage.py:115-124` 的 `publish` 执行存在性检查和 `os.replace`，没有 containment/reparse 防护；同文件 `remove_managed`（`:126-204`）具有 lexical、containment、reparse walk 和 handle-chain 检查。`_is_reparse_point`（`:43-48`）存在但未用于 `publish`；`src/infrastructure/sqlite/nmbak.py:153-168` 的 `_resolve_within` 会拒绝 junction 逃逸。
- 影响边界：需要外部行为者在 managed root 内创建 junction（用户权限即可，产品本身不创建 reparse point）；写出内容限于产品生成的 revision bytes，不是任意数据；经 junction 已存在的外部目标受 `final_path.exists()` 保护，当前证据只表明可新建文件。`remove_managed` 的删除/彻底删除路径不受此 probe 影响，不能据此声称 ADJ-001 被破坏。
- 未验证：GC/归档或其他未测路径是否也跟随 junction；真实用户目录/数据中的可达性。若 GC/归档路径另被证实可穿越，风险可能需要重新分级。本结论不外推到这些路径。
- 不升 High 的依据：没有权限提升，写入内容受限，已有外部文件受保护，且需要外部注入 junction 的前提。

## Finding 2：restore 磁盘写失败后缺 typed error 和 rollback 指引

- Probe：`test_nmbak_restore_disk_failure_leaves_changed_database_without_rollback_id`
- 建议分级：**Medium severity / High confidence**
- 观察：隔离 probe 实测 `database_changed=true`、`typed_error=false`、`rollback_id_in_error=false`；pre_restore 包已创建（`pre_restore_packages=1`）。
- 静态依据：`src/infrastructure/sqlite/nmbak.py:1180-1210` 的 `_restore_managed` 逐文件调用 `write_bytes`，未将 `OSError` 包装为 typed error。模块冻结语义要求 every failure is typed（`:28`）；同函数族其他失败路径会返回 `BACKUP_RESTORE_INCOMPLETE` 和 pre_restore id（`:398-405`, `:426-430`）。fixture 使用真实 SQLite 与文件系统；monkeypatch 仅模拟磁盘满，失败注入发生在 pre_restore 创建成功后（`audit/V1-FULL-AUDIT/tests/test_audit_probes.py:34-42`）。
- 影响边界：已有 pre_restore 包，因此数据不是不可恢复；DB 覆盖到备份点状态属于 overwrite-only 设计效果。缺陷在于错误类型契约缺失、错误中无回滚指引；多文件恢复可能留下部分写入的中间状态，是根据逐文件写入作出的**静态推断**，这个单文件 probe 没有实际演示该中间状态。
- 未验证：上层 Core/wire 是否把裸 `OSError` 映射为 typed error；ZCode 未读取该上层路径，不能确认。也未在真实用户数据或真实磁盘故障中复现。维持 Medium，不把未知的上层映射当作事实。

## 已验证的防线：备份路径 `../` 被拒绝

- Probe：`test_nmbak_restore_can_overwrite_outside_managed_root`
- 结论：**defense-verified；不是产品失败，也不是 probe 假阳性。**
- 篡改 manifest 的 `../audit-victim.txt` 在 `_verify_package`（`nmbak.py:996-1152`，经 `_managed_relative_path` `:124-150`）阶段被拒绝为 `BACKUP_CORRUPT`。`restore()` 在解压前先执行 verify（`:372`），拒绝发生在写入之前。
- probe 原本预期复现越界写，但攻击预期落空；probes suite 该项失败不应登记为产品回归。当前防线符合 fail-closed 行为。

## 审计处置与限制

- probes suite 的真实状态仍是 `EXIT=1`、`2 passed / 1 failed`；这是混合 probe 结果，不能汇总为产品全通过或全失败。
- 两项 finding 可在 `AUDIT_ISSUES.md` 登记为 `TRIAGED`，并保留隔离证据、分级和未验证边界。第三项只按 defense-verified 记录。
- `AUDIT-01–14` 继续 `BLOCKED-ORIGINAL-CHECKLIST-MISSING`；probe/suite 结果不映射到任何逐项，也不改变 Release Gate `BLOCKED`。
- 两项修复均触及 `src/**`，超出当前 Task 的 `allowed_paths`；只登记方向，必须另行释放实现 Task。建议方向：`publish` 补与 `remove_managed` 同级的 containment/reparse 防线或抽取共享 helper；`_restore_managed`/restore 顶层将 I/O 错误包装为带 pre_restore `backup_id` 的 `BACKUP_RESTORE_INCOMPLETE`。probe 3 的断言反转属于审计目录，但本轮不改。
