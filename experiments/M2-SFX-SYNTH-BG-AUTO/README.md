# chatgpt_bg：SFX 合成底图自动 provider（M2-SFX-SYNTH-BG-AUTO）

ChatGPT 网页版全自动生成漫画底图（黑白/无文字/留白区），供 T1a 合成渲染管线叠字用。
**自动化形态=全自动内嵌**（用户裁决 2026-10-04）：Playwright 持久登录态驱动本机
Chrome（channel=chrome 真实指纹），底图库缺量自动补齐；**fail-closed 停等人，不静默降级**。

```bash
cd experiments/M2-SFX-SYNTH-BG-AUTO
<python> -m chatgpt_bg --help        # EXIT=0
<python> -m chatgpt_bg selfcheck     # 离线自检 EXIT=0
<python> -m pytest tests/ -q         # 10 tests（mock，不联网）

# 首次使用（一次性人工登录，登录态持久化在外部树 profile）：
<python> -m chatgpt_bg login

# 日常：
<python> -m chatgpt_bg status                       # 底图库余量/缺口
<python> -m chatgpt_bg generate --count 5           # 指定张数
<python> -m chatgpt_bg generate                     # 自动补齐缺口（默认阈值 20）
<python> -m chatgpt_bg check-gap --dry-run          # 只报告缺口（EXIT 3=有缺口）
```

数据落位：底图 `training_data/sfx-v1/backgrounds/bg_NNN.png`（gitignored 外部树，PNG
魔数校验+tmp/replace 原子写），索引同目录 `bg_index.json`（r2 P2-5：**旁路索引**，
非 T1a manifest container 口径；T1a 对接属 T1b）。**命名纪律**：人工入库也必须叫
`bg_NNN.png`（否则缺口计数数不到）。路径可用 env `CHATGPT_BG_DATA_ROOT` /
`CHATGPT_BG_PROFILE` / `CHATGPT_BG_REPO_ROOT` 覆盖（worktree/主仓共享底图库与登录态）。

**check-gap 退出码契约**（数据构建钩子用）：`0`=充足 / `2`=已触发补齐 / `3`=dry-run
缺口 / `4`=fail-closed（stdout 仍输出结构化 JSON：`{"fail_closed": {state, detail}}`）。

## fail-closed 状态（AC3）

| 状态 | 含义 | 人工处置 |
|---|---|---|
| NOT_LOGGED_IN | 登录态丢失 | 跑 `login` |
| CLOUDFLARE_CHALLENGE | 人机验证页 | 浏览器窗口人工通过后重跑 |
| RATE_LIMITED | ChatGPT 限额/风控 | 等待窗口重置或降频 |
| CONSECUTIVE_FAILURES | 连续 3 张失败 | 检查页面状态后重跑（编号断点续跑） |

## 实测四坑（已固化进实现）

1. 发送必须点发送按钮（Enter 在对话页不可靠）——`send_prompt` data-testid 优先+aria 兜底；
2. 完成判据=最新图 blob src 变化且无停止/微调/思考中（消息计数会被虚拟滚动骗）；
3. "最后再微调一下…98%"阶段无停止按钮但图未出——busy 标记排除；
4. "思考中"卡死不自愈——超时 reload 重发一次，再失败计入连续失败。

## 风险与边界

- ChatGPT UI 改版会使定位器失效（维护点集中在 `browser.py` 一个文件）；
- Playwright 连接下 `navigator.webdriver` 仍为 true——channel=chrome+持久 profile+
  默认有头是**降低检测面的待验证手段**而非已证结论；**全新 profile 首次登录
  ChatGPT 可能触发风控**（这正是 AC5 真实冒烟要回答的问题，首跑建议人工盯着）；
- 极端情况可退回"半自动"：底图由 ZCode 会话人工生成入库（命名仍须 `bg_NNN.png`，
  `gap.py` 消费者无感）。
- AC2 残留登记：`check-gap` 钩子已就绪，但"render/数据构建入口自动调用"的调用方
  尚不存在（受"T1a 已集成代码零触碰"限制）——接线属 T1b/后续 Task，需 Codex 释放。
