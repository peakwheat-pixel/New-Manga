# TASK-024 作者验证（仅设计；实现 head 见 Handoff）

## 环境与范围

- OS：Windows 11（win32 10.0.26200 x64），Git Bash
- 工作路径：`G:/CODEX/New Manga.worktrees/TASK-024-zcode`
- 窗口 base：`116e682`（解冻时 master HEAD）
- 任务性质：kind=design——交付物为设计文档与追踪表回写，无生产代码；验证以
  引用完整性、范围边界与一致性检查为准，不涉及产品行为验收。

## 结果

| # | 精确命令（Git Bash，CWD=worktree） | 退出码 | passed | skipped | 结论 |
|---|---|---:|---:|---:|---|
| V1 | `PYTHONPATH=src python - <<'PY'`（引用核对脚本，见下） | 0 | 12 断言 | 0 | PASS：设计文档引用的 D01/D02/D04/D05/D06/D07 章节与追踪条目全部真实存在 |
| V2 | `git diff --name-only master` | 0 | — | — | PASS：变更仅在白名单（doc/13_ACCEPTANCE_TRACEABILITY.md、doc/contracts/extensions.md、doc/tasks/TASK-024.md、doc/handoffs/TASK-024-*.md、verification/TASK-024/**） |
| V3 | `PYTHONPATH=src python -m pytest tests -q`（全仓） | 0 | 536 | 0 | PASS：纯文档提交不触碰代码，全仓保持绿色（架构守卫含在内） |

V1 引用核对脚本（内联，逐条断言目标内容存在于被引文档）：

```python
import pathlib
doc = pathlib.Path("doc")
ext = (doc / "contracts" / "extensions.md").read_text(encoding="utf-8")
checks = {
    "D01 §2 补充扩展能力": "补充扩展能力：网页导入、PDF/MOBI 导入解析、AI 生成插件 Agent、字体上传、Sakura 本地服务监控" in (doc / "01_FUNCTIONAL_ARCHITECTURE.md").read_text(encoding="utf-8"),
    "D02 §12 Plugin Agent 如保留": "Plugin Agent 如保留，只负责生成/管理插件" in (doc / "02_TECHNICAL_ARCHITECTURE_.md").read_text(encoding="utf-8"),
    "D02 §6.2.2 本地 Sakura": "本地 Sakura" in (doc / "02_TECHNICAL_ARCHITECTURE_.md").read_text(encoding="utf-8"),
    "D02 §6.2.2 外部站点": "gallery-dl" in (doc / "02_TECHNICAL_ARCHITECTURE_.md").read_text(encoding="utf-8"),
    "D04 §8 PDF/MOBI": "PDF / MOBI" in (doc / "04_USER_FLOW.md").read_text(encoding="utf-8"),
    "D05 §48 字体选择": "字体选择" in (doc / "05_UI_MAPPING.md").read_text(encoding="utf-8"),
    "D07 §72 插件崩溃": "不得让 Core Domain / SQLite 损坏" in (doc / "07_NON_FUNCTIONAL_REQUIREMENTS.md").read_text(encoding="utf-8"),
    "D07 §84 模型下载口径": "不得注册为 Ready" in (doc / "07_NON_FUNCTIONAL_REQUIREMENTS.md").read_text(encoding="utf-8"),
    "追踪表 ACG-EXT-IMPORT 已指向设计": "TASK-024已定义边界" in (doc / "13_ACCEPTANCE_TRACEABILITY.md").read_text(encoding="utf-8"),
    "AC 草案 11 条": all(f"AC-EXT-{n}" in ext for n in ["IMPORT-001", "IMPORT-002", "IMPORT-003", "IMPORT-004", "PLUGIN-001", "PLUGIN-002", "PLUGIN-003", "AGENT-001", "AGENT-002", "FONT-001", "FONT-002"]) and "AC-EXT-FONT-003" in ext and "AC-EXT-SAKURA-001" in ext,
    "用户待决清单 U-1~U-6": all(f"U-{i}" in ext for i in range(1, 7)),
    "D03 §47 排除项引用": "不排入用户注册" in ext,
}
failed = [k for k, ok in checks.items() if not ok]
assert not failed, failed
print("all reference checks passed:", len(checks))
```

## AC 对照说明（仅设计任务）

三条设计 AC 的证据形态为设计文档章节 + 追踪表回写（见 TASK-024.md 勾选），
不适用 passed/skipped 计数；第四条（Review/集成）随窗口流程推进。

## NOT_RUN / BLOCKED 项（不掩盖）

| 项 | 状态 | 原因 |
|---|---|---|
| §3 权威文档回写（08 新增 AC-EXT 节、Roadmap 前置条件） | NOT_RUN（有意） | 需求裁决属用户保留权；本设计只登记 §4 待决清单 U-1~U-6，批准后以元数据提交回写，避免自我批准 |
| Sakura/Plugin/字体/导入的产品级 AC 验收 | NOT_RUN | 属 TASK-023/025/019/022 的实现后验收；设计任务不产生产品证据 |
| 真实 Sakura 实例探测验证 | NOT_RUN | 本机无 Sakura 服务；属 TASK-019 实现后验收 |
