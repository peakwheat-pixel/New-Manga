---
id: TASK-004
title: 验证 Windows 运行环境与打包路线
kind: experiment
status: done
approval: approved
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [TASK-002]
base_commit: 8addf1b7d87c07f51d3acf8275030375be08adda
branch: agent/zcode/TASK-004-windows-packaging
worktree: G:/CODEX/New Manga.worktrees/TASK-004-zcode
integration_commit: a501372dd09086e93f86d41937c43cb41e41e563
---

# TASK-004：验证 Windows 运行环境与打包路线

本 Task 已完成独立 Review 与 Codex 集成验证，状态为 `done`。本 Task 只包含隔离实验，未创建生产应用骨架，也未自动释放 TASK-005 或其他后续 Task。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D02 §1/13；D07 §2/81～85/107；G18。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：本任务为设计/实验/基础工作，验收以下专属条件；关联产品 AC 不因本任务完成就自动 PASS。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [x] 在隔离实验目录验证 Python/PySide6/QML/pytest/PyInstaller 的具体兼容版本，记录 OS/架构与准确命令。（PASS；Python 3.12.3 / 3.14.0 × PySide6 6.11.2 × pytest 9.1.1 × PyInstaller 6.22.3，见 [research §3～§4](../research/TASK-004.md)）
- [x] 无重型 AI 依赖能打开最小 QML 验证窗口；打包 onedir 在可取得的干净 Windows 环境验证，否则明确 BLOCKED。（QML 真实窗口 ×2 个 Python 版本、onedir 构建与无开发 PATH 启动均 PASS；干净 Windows 机器不可得，已明确 [BLOCKED](../research/TASK-004.md) 并附解除条件）
- [x] 给出 Core/可选 ML 依赖分离、字体/Qt资源/路径方案和锁定版本建议；由 Codex审核后供工程使用。（[research §5](../research/TASK-004.md) Proposal，含 Essentials-only 实测证据）
- [x] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。（最终 Handoff：[TASK-004-181a356](../handoffs/TASK-004-181a356.md)）

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- experiments/TASK-004/**
- doc/research/TASK-004.md
- doc/tasks/TASK-004.md
- doc/handoffs/TASK-004-*.md
- doc/reviews/TASK-004-*.md
- verification/TASK-004/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 实验启动/关闭与 Qt DLL 加载检查。
- 无开发机 PATH/venv 的打包复现；不可用环境不得用本机代替。
- 以上已执行（2026-09-14，owner ZCode）：QML 启动/关闭、Qt DLL/plugin 加载检查、pytest 冒烟、onedir 构建与「无开发机 PATH」启动全部 PASS；干净 Windows 环境复现 BLOCKED。逐项命令、退出码与证据见 [research §3 结果总表](../research/TASK-004.md) 与 [verification/TASK-004](../../verification/TASK-004/)。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-002](TASK-002.md)。依赖必须已经集成 done 才可开始。

不把当前机器 Python 版本直接视为项目选型；实验不得向生产 src 写代码。

TASK-003 与 TASK-004 分别由 DeepSeek Harness 与 ZCode 执行，必须使用不同 worktree、虚拟环境、缓存和输出目录；不得切换或清理另一 Task 的 checkout。干净 Windows 环境不可取得时必须记录 `BLOCKED`，不能用当前开发机结果替代。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：[TASK-004-181a356](../handoffs/TASK-004-181a356.md)（delivery_head=`181a356cdb91725aa63961d123605ac179074286`）。
- Review：DeepSeek Harness 最终复审 [approved](../reviews/TASK-004-181a356.md)（commit `5f4db0f`）；R-001 fixed，R-002 deferred。干净 Windows 仍是发布 Gate 的 `BLOCKED`，不伪装为已验证。
- 实际执行/实验/测试：[research/TASK-004.md](../research/TASK-004.md)（结果总表 E1～E18）+ [verification/TASK-004](../../verification/TASK-004/)（env_report.txt 与 logs/）。
- 集成：Codex 以 merge commit `a501372dd09086e93f86d41937c43cb41e41e563` 串行集成。Python 3.12 QML、pytest（3 passed）、Qt 资源、Python 3.14 QML、Essentials-only QML、PyInstaller onedir 正常启动及仅系统 PATH 启动均 PASS。
- 集成诊断：首次 Codex 打包被桌面运行时注入 PATH 中的 ICU/UCRT DLL 污染并导致 QtCore 加载失败；移除该运行时 PATH 后重建 PASS，且污染 DLL 未进入最终实验产物。该结果不改变干净 Windows 机器验证的 `BLOCKED` 状态。
- 最近状态（历史）：2026-09-14 ZCode 完成全部计划内隔离实验：Python 3.12.3 / 3.14.0 + PySide6 6.11.2 + pytest 9.1.1（3.12 另加 PyInstaller 6.22.3）下，QML 真实窗口启停、Qt DLL/plugin 完整性、pytest、onedir 构建与启动（含清除开发 PATH 模拟）全部 PASS；`PySide6_Essentials` 单独支撑 QML PASS；干净 Windows 环境验证 BLOCKED（环境不可得，未用开发机结果替代）。reviewed_head=`18a9dff`。状态 in_progress → in_review，等待独立 Review。
