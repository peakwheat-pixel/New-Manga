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

数据落位：底图 `training_data/sfx-v1/backgrounds/bg_NNN.png`（gitignored 外部树），
manifest 同目录 `manifest.json`（source=chatgpt-web-auto + prompt 原文，与 T1a 摘要口径兼容）。

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
- Playwright 自动化特征比人工浏览敏感——channel=chrome + 持久 profile 已降低检测面，
  首次真实跑建议有头模式观察；
- 极端情况可退回"半自动"：底图由 ZCode 会话人工生成入库（`gap.py` 消费者无感）。
