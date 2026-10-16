# P15-C1-FU1 独立 Review（R1，Coordinator 路由的 Reviewer=dsh）

| 项 | 值 |
|---|---|
| Task | P15-C1-FU1（设置面契约修订 FU1：`TestNetworkProfile` 目标语义定案；解 P15-CORE-1C） |
| Owner | Codex（经 DSH 原生 `subagent_codex`… **实际经 `/codex-dispatch` CLI**，因原生通道缺 bundle） |
| Reviewer | **dsh**（本会话，`route-agent.py` 路由；Owner 已机器排除） |
| 交付 | 契约修订 `eeae29831`；HEAD `9b0a24590`（Handoff + 证据） |
| 基线 | `82ce23bd5`（含用户 A1 裁决） |
| 结论 | **approved** |

## 1. 逐项验证

| # | 验证项 | 结果 |
|---|---|---|
| V1 | **范围（契约 only）** | **PASS**：仅 `doc/contracts/P15_SETTINGS_IPC_CONTRACT.md`、`doc/handoffs/P15-C1-FU1-eeae298.md`、`doc/tasks/P15-C1-FU1.md`、`verification/P15-C1-FU1/decision-map.md`；**零产品代码**、未改 Schema/依赖/apps |
| V2 | **A1 落实（唯一方案）** | **PASS**：`TestNetworkProfile { network_profile_id, provider_profile_id }` —— **`?` 已移除**，A1 单方案（A2 未采纳，无残留分支） |
| V3 | **假阳性路径彻底封死（本 FU 的核心目的）** | **PASS**：新增"请求校验与唯一目标"节，规定缺省/null/类型非法/不可解析 **一律 `INVALID_REQUEST`**，并**明文禁止**"转换为阶段 `not_run` 或 `status=passed`"；同时规定 `not_run` **仅**可用于失败阶段之后并须带 `upstream_stage_failed` |
| V4 | **禁止项固化（AC2）** | **PASS**：契约正文明确禁止 ① 自选公网 URL、② loopback/假目标、③ 把 Proxy 主机冒充 TLS/HTTP 目标、④ 伪造阶段结果 |
| V5 | **六阶段语义闭合（AC3）** | **PASS**：新增 **5 模式 × 6 阶段**目标/判定表 + 逐阶段统一判定规则；关键澄清均到位——DNS 目标为 **Provider endpoint 主机名**（非代理主机）、TCP 只报到 endpoint 的**逻辑连接**（代理 socket 检查归 Proxy 阶段）、TLS 只指 HTTPS endpoint（HTTPS 代理自身 TLS 归 Proxy）、HTTP **不跨 authority 跟随重定向**、ProviderAuth **不自动重试/不切 Provider**；新增 4 个 `NotRunReason`（`system_route_is_direct`/`provider_endpoint_is_ip_literal`/`provider_endpoint_uses_http`/`provider_auth_not_required`）语义明确 |
| V6 | **兼容性论证（AC5）** | **PASS**：预算性问题被**如实论证**——minor `6 → 7`，并写明"字段必填是**命令尚未实现、未发布前的窄范围修订**，**不是** M2-C1 §3.2 对已发布 wire 的一般兼容规则"；同时指出旧 rev 2.6 草案请求若省略 `provider_profile_id` 必须被 `INVALID_REQUEST` 拒绝 → **不向后兼容但无已发布客户端受影响**（诚实、不掩盖） |
| V7 | **安全/脱敏保留（AC4）** | **PASS**：§5.2 既有约束保留（结果不得含原始响应/响应体/请求头/认证头/代理凭据/路径或 endpoint 敏感部分）；失败只走 §9 封闭投影 |
| V8 | **未越界改其他语义** | **PASS**：G21/G22/G24 与 P10 边界未动；仅 §5.2 + §2 兼容声明 |
| V9 | **证据记录** | **PASS**：**6 条证据行**，`class` 仅 `CANONICAL`(×2)/`SOURCE_PIN`(×4，含 M2-C1 与裁决)——**符合 BL-19**；**BL-17 包含性 6/6 成立**；**pin 可移植性**：未改动文件（M2-C1）经实测**主仓库同样匹配** ✓ |
| V10 | **测试如实** | **PASS**：测试表全部 `NOT_RUN` 并给出原因（设计类、无 runtime handler），**未把静态撰写计为测试** |

## 2. 结论：approved

FU1 **精确、完整地**落实了 A1：把"缺省即 passed"这条假阳性路径**从契约层面删除**（参数必填 + `INVALID_REQUEST` + 明文禁止映射），并顺势把六阶段的**目标来源与判定条件**补全到可判定程度（含 5 种模式与逐阶段规则），兼容性影响**如实论证而非掩盖**。范围严守"仅契约"。

## 3. closeout 记录项

1. **pin 复算（RV-P15-04 类）**：被修订契约文件的 pin 由 Owner 在其工作树以 **LF** 计算；合并后 main 的磁盘字节为 **CRLF** 形态 → **closeout 必须在主仓库复算**该文件相关 pin（M2-C1 等未改动文件已验证可移植）。
2. **DAG 效果**：FU1 关闭即**解除 P15-CORE-1C 的释放门**（1C 依赖 FU1）→ closeout 同步释放 **P15-CORE-1C**。
3. **过程记录（正向）**：Owner 上一轮（P15-CORE-1）在发现缺口时**失败关闭并引用契约行号上报**，使本次裁决与修订得以**精确、快速**完成——"失败关闭 + 引原文"的纪律经受住检验。
