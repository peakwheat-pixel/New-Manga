---
task_id: M2-S1
reviewer: Codex
author: DeepSeek Harness
base_commit: 85a2aa7fd07a2dca843bf5cea3ec34070b63bdbc
reviewed_head: 4eaad684769a02035748b95186d478bbed926042
handoff_commit: 7766a2bb2b1a21f398c73019135bb705bb03aa25
decision: changes_requested
---

# M2-S1 Review — initial fixed head

## 范围与依据

在共享仓库从 DSH standalone clone 的 Git bundle 导入原始 `4eaad684`、`7766a2bb`，核对父提交链为 `85a2aa7 → 4eaad684 → 7766a2bb`。按 [M2-S1 Task](../tasks/M2-S1.md) AC1–AC6、[AD-001](../AD-001_TARGET_DESKTOP_ARCHITECTURE.md) §Migration constraints 4/6、[M2-C1 Contract](../contracts/M2-C1_TYPED_IPC_CONTRACT.md) §10/§11 及[协作协议](../09_COLLABORATION.md)审查报告、Handoff、探针和原始日志。Review 不批准产品通道或 runtime。

## Architecture

候选矩阵覆盖受限引用、流式/分块、命名与匿名 Windows section，并把 JSON/Base64 作为禁止路线的对照。Python↔Python、热页缓存与未测 Tauri/WebView 边界已明确。以下两处安全属性描述超出了探针证明范围。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| R-001 | P1 | `doc/research/M2-S1_RESOURCE_CHANNEL_SPIKE.md:294,343`；`verification/M2-S1/probes/m2s1_lab.py:368-388,397-403` | 报告写“引用越界读已缓解”“重解析逃逸全部为稳定拒绝”。原型先 `Path.resolve()`/逐段 `lstat()`，随后返回路径由宿主再次 `open()`；文件大小也先 `getsize()` 再打开。并发替换 junction、文件或大小的窗口未测，不能据静态拒绝样例断言攻击被缓解。此处正影响推荐路线 A 的安全边界。 | 固定 head 的上述代码与 A-13/A-15 静态负向场景；没有并发替换或句柄绑定场景。 | 把缓解结论限定为**静态路径输入下实测 PASS**；在威胁模型、推荐和 blocker 清单中显式标记检查到打开之间的竞态 `UNVERIFIED`，列出产品实现需用句柄绑定/打开后校验及负向探针的解除条件。无需在本研究 Task 实现产品防护。 | open |
| R-002 | P2 | `doc/research/M2-S1_RESOURCE_CHANNEL_SPIKE.md:107`；`verification/M2-S1/probes/m2s1_lab.py:269-279` | “不透明引用”与原型不符。token 的正文只是 Base64URL 编码的 JSON，包含 `rel`、`rid`、`scope`、`exp`、`mode`；签名保证完整性，不保密。这个差别会影响路径信息暴露判断。 | Reviewer 用固定脚本调用 `mint_token(...)`，无密钥即可解出 `{"rel":"private/asset.png",...}`；命令及结果见下表。 | 将原型称为“签名的可解码引用”，说明相对路径可见；若产品需要不透明性，将服务端映射 ID 或加密方案列为后续设计/验证条件。 | open |

## Verification

| 检查 | 环境/固定点 | 结果 | 证据 |
|---|---|---|---|
| Git ancestry / 原 SHA | 共享仓库；base `85a2aa7`，delivery `4eaad684`，Handoff `7766a2bb` | PASS | `git rev-parse 7766a2b^`=`4eaad684`；`git rev-parse 4eaad684^`=`85a2aa7` |
| 授权路径与空白 | `git diff --name-status 85a2aa7..7766a2bb`；`git diff --check 85a2aa7 7766a2bb` | PASS：39 路径仅 Task、研究报告、新 Handoff、`verification/M2-S1/**`；diff-check exit 0 | 本 Review 独立执行，Owner `raw/20-delivery-scope.log` 可交叉比对 |
| Evidence hash | C: standalone clone；逐条 `Get-FileHash -Algorithm SHA256` 并核字节数 | PASS：36 条，0 mismatch | `raw/06-evidence-hashes.log` |
| 场景与结果 | 读取 `raw/probeA..E-result.json` 和 `raw/00-run-all.log` | PASS：A 15、B 12、C 14、D 8、E 11；总计 60/60，五探针 exit 0；原始日志记录 Python 3.14.6 / PowerShell 7.6.6 | Handoff 与原始 JSON 一致；未把负向场景的 PASS 解释成安全属性全面通过 |
| token 不透明性 | `python -c 'import sys,base64; sys.path.insert(0,"verification/M2-S1/probes"); from m2s1_lab import mint_token; t=mint_token(b"x"*32,resource_id="r",rel_path="private/asset.png",scope="derived-read-only",expires_at=1); print(base64.urlsafe_b64decode(t.split(".")[1]+"==").decode())'` | FAIL：输出含 `"rel":"private/asset.png"`；签名不提供保密性 | reviewer 本机执行，exit 0 |
| 完整产品 runtime/GUI | Task 禁止范围 | NOT_RUN | Owner 亦明确标注；不据此批准产品实现 |

## 结论与复审

**Architecture=`CHANGES_REQUESTED`，Verification=部分 PASS；Decision=`changes_requested`。** AC1/AC2/AC3/AC6 的研究证据可保留。AC4/AC5 的安全描述须按 R-001/R-002 改正后才能批准该固定交付。Owner 可在原 standalone clone 的授权路径内修订报告、Task、Handoff/证据，并提交**新** reviewed head；Codex 对新 head 重新审查。旧提交与本 Review 保留为审计记录。
