---
task_id: M2-SFX-SYNTH-BG-AUTO
author: ZCode（Owner）
recipient: Codex（Integrator，编排会话代行）
base_commit: 6f1117d6
delivery_head: 97ccf78d（本文件经 amend 随实现提交）
status: r2-delivered（r1 changes_requested 已返修，待 DSH r2 复核；r1 报告 doc/reviews/ 入库随集成）
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

---

## r2 返修轮（2026-10-04，DSH r1 changes_requested → 返修）

**r1 结论**：changes_requested（P0-1 证据无效 + 3×P1 + 10×P2 + 9×P3）。

**P0-1 闭合**：`tests/conftest.py` 补齐（仓库根直跑可用）；green-run 重录
`green-run-r2.log`（完整命令行+12 passed+1 slow-skip+真实 EXIT=0——r1 的 EXIT 经
管道拿到的是 tail 的退出码恒 0，r2 改为直接捕获 pytest 退出码）。
**P1-1**：reload 后重取 prev_src 基准（回归测试 test_reload_then_success：stale 旧
URL 陷阱下落盘的必须是真新图）。**P1-2**：异常路径 try/finally 保证 close；
check-gap 捕获 BGGenerationError 输出结构化 JSON+EXIT 4；非 BGGenerationError
（ENV_ERROR）同结构化。**P1-3**：新增 `tests/test_smoke_real_chatgpt.py`
（pytest.mark.slow + CHATGPT_BG_SMOKE=1 闸门；断言 2 张落盘/bg_index 2 条/src 互异）。
**P2 全处置**：P2-1 busy 判据 stop-button 定位器优先+文本兜底限定最后 assistant 消息；
P2-2 blocking 状态码不折叠（CLOUDFLARE_CHALLENGE/NOT_LOGGED_IN/RATE_LIMITED 独立）
+英文 Cloudflare 标题+限额 marker 扩充；P2-3 路径 env 三通道（CHATGPT_BG_*）+
git common dir 主仓根推断；P2-4 PNG tmp/replace 原子写+count 魔数校验+manifest
失败回滚 PNG；P2-5 改名 bg_index.json 并声明旁路索引；P2-6 backgrounds 别名；
P2-7 残留登记（调用方接线属 T1b）；P2-8 EXIT 4 契约；P2-9 CLI 契约测试+
非 PNG 丢弃+reload 后成功续跑断言；P2-10 delivery_head=efc56e4a 修正（r1 所见
97ccf78d 为 amend 前悬空）。
**P3**：死参数清理/__main__ 保护/CHALLENGE 单源（引 splits）复核+README 风险声明
降级为待验证/命名纪律登记。

**r2 验证**：`pytest tests/ -q` → **12 passed, 1 skipped**（新增 reload 回归/non-PNG
丢弃/CLI 契约等；green-run-r2.log 含完整命令行与真实 EXIT）；selfcheck EXIT=0；
help EXIT=0；**CLI 契约矩阵**（cli-contract-r2.log）：dry-run→3、足量→0、未登录
真实触发→4+结构化 fail_closed JSON（r1 P1-2 的裸 traceback 已消除）。

**下一接收者**：DSH r2 复核 → Codex 集成（真实冒烟 manual 步骤保留给用户人工登录后
由集成方代跑留证）。

## 风险与遗留

- ChatGPT UI 改版会使定位器失效（维护点集中 browser.py）；Playwright 特征检测首跑观察；
- 极端情况退回半自动（ZCode 会话人工生图入库，gap.py 消费者无感）。

## 下一任务建议

Task=M2-SFX-DATA-INFRA 后续批量生产切片（T1b 或独立）；Agent=ZCode；Scope=竖排
prompt+真实底图与 T1a 合成渲染打通（端到端样册）；Verification=目检+GT 互算；
Forwardable instruction=待用户对真实冒烟样张目检通过后释放。
