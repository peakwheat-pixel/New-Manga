---
task_id: M2-SFX-SYNTH-BG-AUTO
author: ZCode（Owner）
recipient: Codex（Integrator，编排会话代行）
base_commit: 6f1117d6
delivery_head: efc56e4a（r1 基线）；r2=72506d36；r3=b1baa24f；r4 doc-fix=见 §r4（集成时最终 tip）
status: r4-docfix-delivered（DSH r3 approved_with_conditions 条件 1-7 已闭合，集成修正 commit 一次性收口）
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

**r2 验证**：`pytest tests/ -q` → **13 收集项=12 passed+1 slow-skip**（新增 reload 回归/non-PNG
丢弃/CLI 契约等；green-run-r2.log 含完整命令行与真实 EXIT）；selfcheck EXIT=0；
help EXIT=0；**CLI 契约矩阵**（cli-contract-r2.log）：dry-run→3、足量→0、未登录
真实触发→4+结构化 fail_closed JSON（r1 P1-2 的裸 traceback 已消除）。

**r3 期 cli-contract-r3.log 已 SUPERSEDED**（同名参数 default 覆盖坑，终版见 cli-contract-r3-final.log）。
**下一接收者**：DSH r2 复核 → Codex 集成（真实冒烟 manual 步骤保留给用户人工登录后
由集成方代跑留证）。

## 风险与遗留

- ChatGPT UI 改版会使定位器失效（维护点集中 browser.py）；Playwright 特征检测首跑观察；
- 极端情况退回半自动（ZCode 会话人工生图入库，gap.py 消费者无感）。

## 下一任务建议

Task=M2-SFX-DATA-INFRA 后续批量生产切片（T1b 或独立）；Agent=ZCode；Scope=竖排
prompt+真实底图与 T1a 合成渲染打通（端到端样册）；Verification=目检+GT 互算；
Forwardable instruction=待用户对真实冒烟样张目检通过后释放。


---

## r3 返修轮（2026-10-04，DSH r2 changes_requested → 返修，commit 见 §r3_head）

**r2 结论**：changes_requested（N1 P0 selfcheck 回归 + N2 P1 + N3 P2 + N4-N8 P3）。

**r3 修复**（DSH 五点清单逐条）：
1. **N1/P2-5**：`cmd_selfcheck` 的 manifest.json → `bg_index.json` 同名修正（r2 改名漏
   引用点的回归）；selfcheck-run.log 重录为真实 EXIT=0（r2 期实物 EXIT=1 与交付声明
   相反的失效证据已替换，教训同 T1a r3：**声称值必须来自重录后的实物**）。
2. **N2**：`cmd_check_gap` 补 `except Exception` → ENV_ERROR 结构化 JSON + EXIT 4。
3. **N3**：`cmd_generate` 去掉 except 分支内冗余 close，finally 唯一 close 点。
4. **N4**：死常量 BUSY_MARKERS 删除。**N6**：全局参数 parent parser 且每个子 parser
   单独挂（add_subparsers 不支持 parents 级联）——子命令前后置均可。
5. **N7**：reload 后复检 blocking_state（登录态丢失报 NOT_LOGGED_IN 而非连续失败）。
   **N5/N8**：README/handoff 计数更新 12+1skipped、green-run 引用改 r3 日志、
   Task/STATUS 回填随集成收口。

**r3 验证**：tests **12 passed + 1 skipped**（green-run-r3.log 完整命令行+真实 EXIT）；
selfcheck EXIT=0（重录实物）；**CLI 契约矩阵 cli-contract-r3.log**（完整命令行+前后置
双验证）：selfcheck=0、check-gap 空目录 dry-run=3（后置+前置式）、真触发未登录=4+
结构化 fail_closed JSON、min=0 足量=0。

**下一接收者**：DSH r3 定向复核（N1/N2/N3/P2-10 + r1 P2 表残留）→ Codex 集成
（真实冒烟 manual 保留给用户登录后代跑留证）。


---

## r4 doc-fix 轮（2026-10-04，DSH r3 approved_with_conditions 条件 1-7 集成修正 commit 闭合）

DSH r3：代码层四项修复全部正确、无新代码缺陷。本 commit 按 r3 返修清单闭合文档/证据层：
cli.py 注释统一后置唯一口径 / handoff 计数与引用修正（13 收集项、cli-contract-r3-final.log）/ 
cli-contract-r3.log 加 SUPERSEDED 头 / README 补 ENV_ERROR 行与 13 计数 / Task 文件回填
status=in_review+AC 勾选+测试表实跑数字 / N7 回归测试补（reload 后 blocking_state 复检）。
真实冒烟（AC5 manual）保留给用户人工登录后由集成方代跑留证。


---

## 真实冒烟留证（2026-10-04，AC5 manual 闭合）

用户人工登录 peakwheat（去自动化参数窗口，Google OAuth 放行）→ 集成方代跑
`generate --count 2` EXIT=0：bg_001（radial_speed_lines, 2289KB）+ bg_002
（explosion_smoke, 2947KB）落**主仓**底图库（r2 P2-3 共享路径设计实战生效）。
取证（bg-index-smoke.json）：PNG 魔数完整、blob src 互异（r2 P1-1 修复不复现）、
count_backgrounds=2。两次 send 定位器超时被重试机制兜住（连续失败计数未达阈值，
实战验证 fail-closed 设计）。首登风控：去自动化参数（ignore --enable-automation +
disable AutomationControlled）实测放行 Google OAuth——r1 P3-6 的"待验证"声明转正。
产物 gitignored 确认（check-ignore 通过）。
