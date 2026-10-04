---
id: M2-SFX-SYNTH-BG-AUTO
title: "SFX 合成底图自动 provider：ChatGPT 网页版全自动生成（Playwright 持久登录态）+ 底图库缺口自动触发（零 src；数据外部树）"
kind: feature
status: ready
approval: user_ruling_2026-10-04_合成底图线路入项目_全自动内嵌（本会话原话「同意批量跑一组 20 张不同风格的底图」实测 20/20 后「我要把这个线路加入到项目中，在项目中所需要素这种素材的时候自动调用」+自动化形态裁决「全自动内嵌」）
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
depends_on: [M2-SFX-DATA-INFRA]
base_commit: 6f1117d6
branch: agent/zcode/M2-SFX-SYNTH-BG-AUTO
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-SYNTH-BG-AUTO-zcode
integration_commit: null
---

# M2-SFX-SYNTH-BG-AUTO：SFX 合成底图自动 provider

## 来源与目标

2026-10-04 实测验证的合成数据线路（ChatGPT 网页版生底图 + 程序叠字精确 GT，见外部树
`task-envs/sfx-synth-exp/` PoC 与 T1a 交付）中，「ChatGPT 网页底图生成」一段目前靠
ZCode 会话人工驱动。本 Task 把它工具化：**项目需要合成底图素材时自动调用**——
底图库余量低于阈值时自动批量生成入库，用户裁决自动化形态=**全自动内嵌**
（Playwright 持久登录态驱动本机 Chrome；fail-closed 停等人，不静默降级）。

## Acceptance Criteria

- [ ] AC1 `backgrounds` 子命令：Playwright persistent context 复用本机 Chrome profile
  （`login` 子命令人工登录一次后持久）→ prompt 风格变体库 → 逐张发送→等待→提取→落盘
  底图库（外部树 `training_data/sfx-v1/backgrounds/`）→ manifest 登记
  provenance（source=chatgpt-web + prompt 原文 + 时间）。实测四坑固化：发送点按钮不用
  Enter；完成判据=最新图 blob src 变化且无停止/微调/思考中；98% 微调阶段排除；思考卡死
  超时 reload 重发。
- [ ] AC2 **缺口自动触发**：底图库余量 < `--min-backgrounds` 时（render/数据构建入口）
  自动调用 backgrounds 补量；`--dry-run` 只报告缺口不联网。
- [ ] AC3 **fail-closed**：未登录/Cloudflare 验证/风控限流/连续 N 张失败 → 结构化状态
  输出（含人工处置指引）停等人，禁止静默降级与半写状态；每张落盘即证据。
- [ ] AC4 prompt 变体库 ≥20 风格（黑白漫画、无文字人物气泡，中央/边部留白适配叠字），
  常量冻结可复现；manifest 兼容 T1a schema 摘要口径。
- [ ] AC5 测试：浏览器交互层以 Protocol/mock 隔离单测（发送/判据/落盘/缺口触发/
  fail-closed），真实 ChatGPT 冒烟标 `slow`/manual 由集成方代跑留证。
- [ ] AC6 零 src；`--help`/`selfcheck` EXIT=0；数据本体落 gitignored 外部树；Git 只进
  代码/manifest 摘要与哈希。

## 允许修改范围

`experiments/M2-SFX-SYNTH-BG-AUTO/**`、`verification/M2-SFX-SYNTH-BG-AUTO/**`、
`requirements.txt`（+playwright 一行，带本 Task ID 注释）、Task/Handoff。外部数据树
（`training_data/sfx-v1/backgrounds/`）新建于 gitignored 区。

## 禁止范围

`src/**`、`tests/**`（仓库级）、`doc/contracts/**`、`packaging/**`、`apps/**`、
`doc/STATUS.md`、T1a 已集成代码的行为变更（只允许新增文件与新增子命令入口）。

## 测试要求

| 场景/AC | 计划步骤 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 发送/判据/落盘 | mock 浏览器单测 | venv | NOT_RUN | |
| AC2 缺口触发 | mock 余量检查单测 | venv | NOT_RUN | |
| AC3 fail-closed | mock 异常路径单测 | venv | NOT_RUN | |
| AC5 真实冒烟 | ChatGPT 真生成 2 张 | 人工登录态 | NOT_RUN（manual） | |

## 依赖、风险与阻塞

依赖 M2-SFX-DATA-INFRA done @`6f1117d6`（底图库目录约定与 manifest 口径）。
风险：①ChatGPT 风控/改版→自动化脆弱（缓解：fail-closed 停等人+手动兜底流程文档+
底图库接口稳定可退回半自动）；②Playwright 自动化特征检测比 ZCode 内置浏览器敏感
（缓解：真实 Chrome channel+持久 profile；首跑验证）；③首次登录需人工（交付说明）。
用户账号：peakwheat（Plus）——额度消耗已由用户裁决接受。

## 交付与运行记录

- Handoff：尚无。Review：尚无。
