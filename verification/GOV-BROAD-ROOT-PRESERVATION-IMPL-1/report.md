# 精确广域根保全：实现与验证

来源设计R3 232e3a589/source e33a51b4d；实现 528940a007ffc53ae7278a3ea007fa80d4a65f6d。只改共享clean_workspace.py与新增broad-root-preservation.json，自己的新测试；三个消费者代码、两历史源、69项例外及旧证据/pin保持不变。main已镜像本Task新增policy并track以便候选以canonical数据验证；旧guard尚未合并，main正式仍24错误，不能把候选12写成已集成。

运行schema严格六记录/五根/两源、裁决原字节、整源SHA/原行SHA和global/relative locator、source/destination、保全枚举、lexical+real及完整错误对；未知键/重复键/ID/record/未跟踪/缺失/Git或读取失败/漂移拒绝。只在共享scan尾部用隔离index/scanned登记12保护来源、12warnings后一次发布；中断丢弃暂存，原容器+fatal，不改通用拒绝/EVIDENCE_PIN/prose/JSON/直连/事故回放。额外拒绝absolute dot-dot并在发布前复核5根realpath。

同canonical main当前数据，旧24→候选12，恰移六record的12广域错误；其它12完整code/file/locator/message相同。旧保护集合是子集，新增5根/12Declaration/12warning；计数与scanned一致。runtime-proof.json记录快照commit和原输入指纹，数值不是永久实时计数；新增自有EV后保护根会增加。13覆盖检查包含五根/五future-child/祖先/两相邻根，邻接仅无新增根命中，不能要求repo原保护为空。

最终18新T01-T18方法（含多组负例、7个原子失败注入、源/policy读中漂移和最终realpath漂移）＋29声明＋80安全回归全部通过，0skip；共127。初轮新测试T16有两处fixture调用假设错误（consolidate默认主线及remove报告文件名），只修新测试，失败原日志留workspace。最后两处生产边界增强后已重跑127，不以旧代码日志替代。

新T16真实调用三个CLI的合成Git fixture，保护候选文件/worktree不删除；canonical候选audit/clean/remove拒绝探针均exit2/12errors/空候选。remove的探针输入是本Task自有空合成inventory，仅验证有错误时先拒绝，不冒称当前真实资源清单；未重新运行canonical consolidate整100/138资源盘点，三个入口共用行为由代码调用链及合成CLI核验。三入口都未运行真实apply。

最终source code的双事故回放各15REJECT/0deleted/0violations。产品/构建NOT_RUN；未来独审未完成。完整命令/退出码/日志见test-execution.json和cli-execution.json。100heads/138worktrees全保留，未执行真实删除/迁移/归档/GC/prune/push/ACL/Legacy；父blocked和r212仍有效。整体workspace保护即使其它12问题未来解决也拒绝其所有后代自动退出，不是资源清理许可。

下一Gate：DeepSeek对固定head独审并实际核新增测试/负例，Codex在main正常merge后复验正式24→12、原保护和源指纹/EV/check，然后才可done。未提交原作者文件不动；旧bundle不覆盖本轮新提交/dirty/ignored/会话。

## R2 后收尾

当前 source6e3bac7867c67a2e76e45e2facbbf859d5dba526；18+29+80重新通过，0skip，双15REJECT/0deleted/0violations重新通过。test-execution.json明确区分原CRLF日志与版本化LF日志哈希。身份复核改无副作用解析，warning正文补源和locator。六处审查探针原位空目录全登记保护；R1的5是历史不完整计数。R2独立批准旧head，14内存负例实测；完整18 fixture复跑NOT_RUN，当前修改需R3。main仍旧代码正式24，候选12不等于已集成；r212禁令不变。
