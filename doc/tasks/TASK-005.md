---
id: TASK-005
title: 建立最小工程入口与架构守卫
kind: implementation
status: proposed
approval: approved
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [TASK-002, TASK-003, TASK-004]
base_commit: d761fc1e28c1f922595a0b09fc8a2ab3fe7172ba
branch: null
worktree: null
integration_commit: null
---

# TASK-005：建立最小工程入口与架构守卫

本 Task 已获用户授权并批准方案 A；当前只完成书面规格，尚未建立实现分支/worktree，也未实施。用户确认本规格后，Codex 才登记实际分支/worktree 并进入 `ready`。本 Task 不释放 TASK-006～TASK-027。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D02 §1/14/16；D07 §83；D08 AC-OPTIONAL；G01/G18。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-OPTIONAL-001。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 采用 TASK-004 获批版本提供可重复安装/运行/测试入口；只使用精确版本 requirements 文件锁定依赖，不引入第二套依赖/锁定工具。
- [ ] Core 无 torch/transformers 等重型可选依赖仍可启动；按需建模块，不批量生成空实现。
- [ ] 建立 Domain 禁止导入 Qt/SQLite/ML、UI 禁止直连具体存储/Provider 的可运行守卫。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 已批准设计：方案 A

### 依赖与入口

- Python 主版本固定为 3.12；Core 固定 `PySide6_Essentials==6.11.2` 与 `shiboken6==6.11.2`。
- `requirements.txt` 保存 Core 的完整精确版本；`requirements-dev.txt` 通过 `-r requirements.txt` 复用 Core，并精确固定 pytest `9.1.1`、PyInstaller `6.22.3`、hooks-contrib `2026.7` 及其实际传递依赖。二者是同一种 requirements 锁定方式。
- 不创建 `pyproject.toml`、`uv.lock`、Poetry 配置或第二套依赖声明；TASK-004 未验证的新工具不进入本任务。
- 运行入口为设置 `PYTHONPATH=src` 后执行 `python -m bootstrap.app`；验证入口增加 `--smoke-test`，加载真实 QML 后自动退出并返回可判断的退出码。

### 最小生产结构

- `src/bootstrap/app.py`：唯一装配/启动入口；创建 Qt Application、加载 QML，并在加载失败时向 stderr 输出包含 QML 路径的诊断信息后返回非零退出码。
- `src/ui/qml/Main.qml`：只提供可启动的 `ApplicationWindow` 与项目标题，不实现书架、工作台、阅读器、设置或其他业务行为。
- `src/bootstrap/__init__.py`、`src/ui/__init__.py`、`src/domain/__init__.py`：只声明当前实际需要的包边界；Application、Ports、Infrastructure 等目录留给后续获授权任务，不生成空实现。

### 架构守卫

- 守卫位于 `tests/core/test_architecture.py`，仅使用 Python 标准库 `ast` 扫描仓库内 Python import，不增加 import-linter 等依赖。
- Domain 禁止导入 `PySide6`、`sqlite3`、`torch`、`transformers`、`onnxruntime`。
- UI 禁止直接导入 `infrastructure` 下的具体存储或 Provider；UI 可依赖 Application/Ports 的后续接口。
- 违规输出必须包含文件、行号与被禁止模块。测试使用临时合成违规文件证明守卫会检测失败，同时扫描真实 `src/domain` 与 `src/ui`。

### 测试与错误边界

- TDD 首个 RED：启动测试因 `bootstrap.app` 尚不存在而失败；架构测试因所需包边界尚不存在而失败。
- GREEN：Core-only 环境不安装 torch/transformers/onnxruntime，真实加载最小 QML 并退出 0；缺失 QML 路径返回非零并提供诊断。
- `python -m pytest tests/core` 是唯一测试入口；验证记录必须包含固定 commit、Python/Qt/pytest 版本、完整命令、退出码与仓库内证据。
- 不在本 Task 创建数据库、Repository、Provider、业务实体、四页导航、打包发布配置或 CI。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- requirements.txt
- requirements-dev.txt
- .gitignore
- src/bootstrap/**
- src/domain/__init__.py
- src/ui/__init__.py
- src/ui/qml/**
- tests/core/**
- doc/tasks/TASK-005.md
- doc/handoffs/TASK-005-*.md
- doc/reviews/TASK-005-*.md
- verification/TASK-005/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 计划：在仓库外创建干净 Python 3.12 venv，分别执行 `python -m pip install -r requirements.txt`、`python -m bootstrap.app --smoke-test` 与开发环境中的 `python -m pytest tests/core`。
- 至少一个 Domain 和一个 UI 合成边界违规会被守卫检测；实际源码扫描无违规；QML 缺失时产生含路径的可诊断错误和非零退出码。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-002](TASK-002.md)、[TASK-003](TASK-003.md)、[TASK-004](TASK-004.md)。依赖必须已经集成 done 才可开始。

主线/依赖/启动装配由 Codex维护；应用骨架从本任务才开始。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-14 用户授权 TASK-005 并批准方案 A；Owner=Codex，Reviewer=DeepSeek Harness，固定 `base_commit=d761fc1`。书面规格等待用户确认；实现分支/worktree 尚未创建，状态保持 proposed。
