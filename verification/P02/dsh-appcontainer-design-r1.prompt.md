你是 New Manga 项目的独立 Reviewer：DeepSeek Harness。请只读审查 Windows AppContainer isolation design candidate，不实现、不改任何文件、不修改 P02 Task/allowlist/Gate，也不要查询/探测 Windows host、创建 profile、运行 smoke/build/Cargo/Sandbox。

固定对象：`verification/P02/appcontainer-isolation-candidate-r1.md`，文件 SHA-256=`2febe1e204702b137e4894d7cd830ae494a1a01579295c708bb56753a951a60c`。这是未提交的 docs-only candidate，因此请将结论绑定到该文件 hash，而非声称它绑定到某个 Git HEAD。若文件内容 hash 不符，停止并报告 `BLOCKED / hash mismatch`。

审查范围：
1. AppContainer/LPAC 作为本机 OS 写入隔离候选是否技术上合适；不得称等价于 Windows Sandbox/VM。
2. `CreateAppContainerProfile`、private registry、profile ACL 和重定向 `LOCALAPPDATA`/`TEMP`/`TMP` 是否如实作为 scratch-only scope delta 暴露；是否仍有其他 profile外写入遗漏。
3. PyInstaller 主进程、isolated hook worker、Torch/Hugging Face cache 与后代进程的 token/capability/ACL 证据设计是否充分；哪些必须在实现前明确。
4. protected-path deny、scratch write、网络能力关闭、process tree token、前后 manifest/hash、精确 profile lifecycle/cleanup 是否足以构成后续 smoke 证据；指出具体缺口与最小修正。
5. 只评价设计候选。`P02 Hard Build Barrier` 必须保持 `EFFECTIVE`；Build Gate、build、AC1–AC7 均仍 BLOCKED/NOT_RUN。不要批准 profile 创建、host smoke 或 build。

请用简体中文输出 decision=`APPROVED | CHANGES_REQUESTED | NOT_VERIFIED | BLOCKED`，列有证据的 findings（路径/小节、严重度、影响、最小修复）、scope delta、尚未验证内容、能否进入用户 scope review，以及下一条动作。不得修改文件；完整 Review 作为 stdout 最终回答。