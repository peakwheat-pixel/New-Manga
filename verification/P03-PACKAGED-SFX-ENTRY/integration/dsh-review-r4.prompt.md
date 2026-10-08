# P03 正式非作者 Review 请求（R4）

请作为 P03 的非作者正式 Reviewer，对下列固定 Git 范围独立审查。只读，不修改、格式化或生成仓库文件，不把未提交文件计入 reviewed diff。

## 固定身份与审查范围

- Repository: `G:/CODEX/New Manga`
- Review worktree: `G:/CODEX/New Manga.worktrees/P03-review-prep-85482c5b`
- 当前目录应为上述 worktree；Task=`doc/tasks/P03.md`；Task status=`in_review`
- Author/Owner=Antigravity；Reviewer=DeepSeek Harness（必须非作者）；Integrator=Codex
- Fixed `base_commit=31abde9bf4b73aea2851931dcd48faa0f750b318`
- Fixed `reviewed_head=d717c049a41544a6d592943a0b0fe1b76a41a050`
- 只审查已提交 diff `base..reviewed_head`；不要替换为当前refs/主工作区dirty文件或旧Review。未提交的 `build-logs/21–22` 和 R4 prompt 只作为Codex保存的验证输入，不是reviewed diff。准确标注你自己运行的命令和未运行项。

先核对 HEAD、branch、worktree、common-dir、精确changed-path集合与 `git diff --check base..head`。如shell因 Win32 5/沙箱故障不能执行，明确记录 `NOT_RUN`，不要从Codex日志推称自己已运行。Codex在此固定head保存的trace为：

- `verification/P03-PACKAGED-SFX-ENTRY/integration/build-logs/21-finalfixedhead-scope-diff-check.log`：132 paths、out-of-scope=0、`git diff --check` EXIT=0。
- `verification/P03-PACKAGED-SFX-ENTRY/integration/build-logs/22-finalfixedhead-normalization.log`：两份read-only normalizer各6/6 PASS、EXIT=0。

以上都是Codex侧的执行证据，需与DSH自行执行结论区分。精确范围应仅包含P03获准工具/测试/Task/验证文档及由Codex维护的导航元数据；`src/**`、`apps/**`、contracts、Schema、依赖、build spec/script、release-gate runner不得有差量。

## 必须读取与核实

阅读 `AGENTS.md`、`doc/09_COLLABORATION.md` §6、`doc/templates/REVIEW.md`、`doc/tasks/P03.md`、两份P03 RESUME、相关Handoffs、`integration/build-manifest.json`、P03实现/测试文件、R3正式报告及其原始JSONL、固定head下的测试/Gate/scope/normalization证据。必要时核对ZIP内原始文件哈希。

独立复核以下内容，不要预设finding已关闭：

1. **R3-01（P2）**：R3指出40项C-002测试日志不绑定提交、28/28 packaged Gate只引用先前runner commit。现登记的修订是在集成source commit `423ea5f196e6276f007bd3f96e381fa893985eb9` 上重新运行40项定向测试和同一installer上的完整Gate，并在当前reviewed head中归档日志19/20与原始Gate ZIP。确认日志内source HEAD、python/EXIT、28/28结构化结果、installer SHA一致；同一Gate JSON的S1真实K07正向与S2缺页失败场景是否真实且正确；零触碰断言是否匹配。
2. **R3-02（P3）**：确认对`423ea5f1…`的scope/diff与两份normalization traces（17/18）已提交；Task/manifest/STATUS/README/Plan/roadmap与恢复点是否指向集成head并避免声称DSH跑过未运行命令。
3. **R3-03（P3、明确范围外）**：`packaging/release-gate/run_release_gate.py`仍列四个sidecar，历史`main.rs`注释也写四个；这两处不在P03 allowed scope。检查P03将它如实登记为非阻断P20未来release-gate范围候选，且没有暗中修改范围外文件。不要要求本Task越界修复；可以对将来P20是否需要重新冻结范围给出建议。
4. **既有R-001–R-006、C-001–C-003**：逐项核对Task的disposition；特别检查R-003 fail-closed、C-002 sensitivity repair（每个负例先验证有效baseline）、installer/source/hash关联、R-004未独立重算ONNX的deferred风险是否仍表述准确。
5. 对Task AC1–AC5逐项给证据结论。AC5仍未勾选；不得由DSH代Codex声明Task `done` 或替Codex做integration Gate。
6. 检查数据保护、安装/AppData隔离、真实用户数据不触碰、任何新P0–P3 finding、Review/Plan/Status不一致。

## Review 输出格式

用简体中文返回可归档的正式Review，开头注明：`task_id=P03`、`reviewer=DeepSeek Harness`、`author=Antigravity`、精确base/head、`decision=approved`或`changes_requested`。分别报告Architecture与Verification判定；按ID/等级/文件行/触发与影响/最小建议/状态列出findings；逐项说明AC1–AC5；明确P0/P1 unresolved数、实际执行命令、NOT_RUN命令、环境限制与残余风险。只有你独立确认无未解决P0/P1且Task与集成边界准确时才可approved。不要修改仓库文件；不要把R3批准延伸到任何新commit。
