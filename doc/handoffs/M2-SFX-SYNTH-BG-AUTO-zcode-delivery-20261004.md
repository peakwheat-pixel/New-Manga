---
task_id: M2-SFX-SYNTH-BG-AUTO
author: ZCode（Owner）
recipient: Codex（Integrator，编排会话代行）
base_commit: 6f1117d6
delivery_head: 97ccf78d（本文件经 amend 随实现提交）
status: delivered（待 Review）
---

# Handoff：M2-SFX-SYNTH-BG-AUTO（SFX 合成底图自动 provider）

## 交付结果

**实现**（全部在允许范围 `experiments/M2-SFX-SYNTH-BG-AUTO/**` + `requirements.txt` +1 行）：

- `chatgpt_bg/prompts.py`：20 风格 prompt 变体库（冻结常量，公共约束"三无一留白"，AC4）
- `chatgpt_bg/gap.py`：底图库缺口检测/触发/manifest 原子追加（AC2）
- `chatgpt_bg/browser.py`：ChatGPTDriver Protocol + PlaywrightChatGPTDriver
  （persistent context+channel=chrome；实测四坑固化：发送点按钮/blob src 变化判据/
  98% 微调排除/思考卡死 reload，AC1）
- `chatgpt_bg/pipeline.py`：生成循环+每张落盘即证据+fail-closed 状态机
  （NOT_LOGGED_IN/BLOCKED/CONSECUTIVE_FAILURES，AC3）
- `chatgpt_bg/cli.py`：login/status/generate/check-gap/selfcheck（AC6）
- `tests/`：10 tests（mock driver，不联网；缺口触发/fail-closed 全路径，AC5）
- `requirements.txt`：+`playwright==1.63.0`（本 Task 注释行）

**AC 对照**：AC1 backgrounds 子命令 ✓（login 持久登录态+四坑固化）；AC2 缺口自动触发 ✓
（check-gap 钩子 EXIT 0/2/3+dry-run）；AC3 fail-closed ✓（状态表见 README）；AC4 prompt
库 ✓（20 风格+约束断言）；AC5 测试 ✓（10 mock tests 全绿；**真实 ChatGPT 冒烟标
manual 未跑——需人工登录，见"交付时人工步骤"**）；AC6 零 src ✓+`--help`/`selfcheck`
EXIT=0 ✓+数据外部树 ✓。

**验证代跑记录**（T1.1.1-impl-py312，PYTHONPATH=包父目录）：
- `pytest tests/ -q` → **10 passed**（交付 log：verification/M2-SFX-SYNTH-BG-AUTO/green-run.log）
- `-m chatgpt_bg selfcheck` → 7 项全 OK EXIT=0（selfcheck-run.log）
- `-m chatgpt_bg --help` EXIT=0（help-run.log）

## 交付时人工步骤（真实冒烟，AC5 manual）

1. `<python> -m chatgpt_bg login` → 浏览器窗口人工登录 peakwheat（一次，持久化）；
2. `<python> -m chatgpt_bg generate --count 2` → 真实生成 2 张留证（约 2 分钟）；
3. 产物与 manifest 入 `training_data/sfx-v1/backgrounds/`（gitignored），编号断点续跑。

## 风险与遗留

- ChatGPT UI 改版会使定位器失效（维护点集中 browser.py）；Playwright 特征检测首跑观察；
- 极端情况退回半自动（ZCode 会话人工生图入库，gap.py 消费者无感）。

## 下一任务建议

Task=M2-SFX-DATA-INFRA 后续批量生产切片（T1b 或独立）；Agent=ZCode；Scope=竖排
prompt+真实底图与 T1a 合成渲染打通（端到端样册）；Verification=目检+GT 互算；
Forwardable instruction=待用户对真实冒烟样张目检通过后释放。
