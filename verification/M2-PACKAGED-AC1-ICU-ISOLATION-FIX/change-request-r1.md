# M2-PACKAGED-AC1-ICU-ISOLATION-FIX：DSH r1 修订指令

Task 状态为 changes_requested。Owner=Antigravity；非作者 Reviewer=DeepSeek Harness；Integrator=Codex。

## 恢复点与固定边界

- 唯一仓库：G:/CODEX/New Manga
- Owner branch：agent/antigravity/M2-PACKAGED-AC1-ICU-ISOLATION-FIX
- Owner worktree：G:/CODEX/New Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity
- 修订起点：46f50a097d25a1893dd1f43b0a38479952242161（已实测 clean，共享 common-dir=G:/CODEX/New Manga/.git）
- 原 Task base 保持：5a72db9e3c5778ce4700b7d404250853e474c5de
- 原实现 head：aa099f2a013408bf53c3466ab8361bc028289743
- 完整 DSH r1：review-dsh-r1.md；decision=changes_requested
- 生产允许路径仍仅 packaging/m2ac5/**；Task、verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/**、该 Task 的 Handoff 仅作交付证据与治理。
- 禁止写 src/**、apps/**、tests/**、Schema、共享 IPC、依赖或用户数据；不部署、不合并、不改用户既有安装；不 reset/clean/stash 他人工作区。
- 不降低既有 runner 阈值/场景、不合并 M2-RUNNER-SNAPSHOT-DEBT。遇到支持的 Windows 基线或消费者行为需要产品取舍时暂停并交 Codex/用户。

## 必须关闭的 Review findings

1. R-001 P1 / R-002 P1：先提交全部生产代码修订并固定新 code head；只在该 commit 上 fresh 构建五入口 Sidecar 与 NSIS，再跑 Dev 和 Packaged Gate。所有命令日志必须记录同一个 source HEAD、命令、解释器、EXIT、耗时。build-fingerprint 的 source_head 必须等于实际构建 HEAD。Packaged runner JSON 内的 installer SHA256 必须与 fingerprint 中被交付 installer SHA256 逐字节相同；把完整26项 Gate 输出、EXIT日志、正确 JSON 一同入库。不得在 NSIS 仍运行时启动 packaged runner，不得用只有命令首行的日志声称通过。
2. R-003 P2：在本 Task verification 下提供412 PE扫描的脚本或可复现命令及原始输出/逐文件结果和输入文件清单/hash；列明静态导入之外的动态加载覆盖边界。矩阵每项以证据或 UNKNOWN 表示，不把 UNKNOWN 提升为 PROVEN。修正 REPORT/Handoff 对 closure-matrix.json 与 scan_closure.py 的断链引用。复用已安装依赖，不新增依赖。
3. R-004 P2：修正 core_sidecar.spec 的按名称、深度无关、来源无关的全包 ICU 删除。原 Task 明确禁止全局删除 ICU、未知引用必须保留；只允许针对已证实的污染源做最小处置，并保留其它/未知来源条目，或对无法安全分类的候选 fail closed 并记录证据。不能用 PATH 子串净化替代消费者审计；净化仅针对已证实来源，finally 必须恢复。输出分类/命中数及最终闭包证据。
4. R-005 P3：移除不可达的 post-filter 断言或改成真正独立、覆盖大小写/分隔符且有判别力的检查；让 PowerShell 检查与真实打包布局相符。报告中的防线名称/行为必须与代码一致。
5. R-006 P3：所有耗时、PID、PyInstaller 版本、哈希与报告从本轮固定原始日志/JSON生成；CS-E2 只记录文件存在和实测 hash，除非新增有固定 expected SHA 的明确判据，否则不能写“SHA256匹配”。逐项修正 Task、REPORT、Handoff。
6. R-007 P3：查明并引用当前项目已声明的 Windows 支持基线；在不改变产品支持范围的前提下记录 System32 ICU 运行依赖和可执行的基线验证。若当前支持基线不具备该 DLL或需要改变支持范围，停止并请求 Codex/用户裁决，不自行改产品承诺。

## 执行与交付 Gate

- 先阅读正式 Task、AGENTS.md、Plan/STATUS、协作协议、DLL-DIAG 原始报告与 DSH Review。
- 修改仅落在冻结 allowed_paths；生产文件 diff 不得越出 packaging/m2ac5/**。
- 先提交生产代码修订并记为 code head；再以该固定 HEAD 运行 fresh Sidecar、NSIS、Dev 10/10 + 13/13、Packaged 26/26。日志中 Git HEAD 必须与 build-fingerprint.source_head 一致；gate JSON installer hash 必须与最终 fingerprint 一致。
- AC-1 扫描 artefact、AC-2 对照日志、build-fingerprint.json、所有核心 Gate JSON/日志、两份固定 runner 副本来源记录、REPORT、Task 状态更新、Handoff 均在本 Task 目录/允许路径内；报告每一项 PASS/FAIL/BLOCKED/NOT_RUN 和 Skip 原因，旧FAIL不回填。
- 交付新固定实现 commit、证据文档 commit、clean 状态与 common-dir/branch/HEAD/diff 范围结果。不要合并主线；Codex 再派真实 DSH 对新固定 head 复审。
- 如果新修订无法在现有 Task 范围内满足安全判据，停止实现，记录 blocker/证据并交 Codex，不扩大范围。
