# Reviewer / Owner 可用性实测

**产出**: 2026-10-20 · **依据**: Codex r25 §3.5「释放前确认可用性」

## 一、r25 的建议与理由

> **Antigravity 可用性：当前证据不足以宣告可用或不可用。**
> 当前 `STATUS` 显示 ZCode 遇 429 限流；本 checkout 在
> `antigravity/P09-AC3-DELETE-HARDEN-1`，说明 Antigravity 近期承担过工作，
> 但不能推断其当前负载、会话是否仍运行或能否承接。
>
> **DSH 不宜作为本 Task 的唯一 Reviewer。** 清单由 DSH 制作；虽然扫描并不等同于
> checker 实现，DSH 审查自己的分类、阈值和证据挑选仍存在自我复核风险。
>
> 优先建议：**Antigravity 做 Owner，ZCode 做独立 Reviewer**（各自确认可用性）。

**它拒绝在没有证据的情况下宣布任何人可用。** 本文补上那个证据。

## 二、实测结果

### Antigravity

| 项 | 结果 |
|---|---|
| CLI 路径 | `C:\Users\49745\AppData\Local\agy\bin\agy.exe` |
| 版本 | **`1.4.2`** |
| 探测任务 | 「只回答两个字：可用。不要做别的事。」 |
| 退出码 | **0** |
| API status | **`SUCCESS`** |
| 响应内容 | **`可用`** |

**结论：可用，且响应正常。**

补充：本 Session 中 Antigravity 已完成 **20+ 轮 Review**，其中多次抓出实质错误
（r1 推翻 `P15-HOST-2` AC5 的 `COVERED` 判定、`GOV-P15-MANIFEST-1` r1 实测三个 Junction
指出交付方的推理错误）。**它的可用性不只是「进程能起来」，而是「在本项目上持续有效」。**

### ZCode

| 项 | 结果 |
|---|---|
| PATH | **不在 PATH** |
| `C:\Users\49745\AppData\Roaming\ZCode` | 存在（配置目录） |
| `C:\Users\49745\.zcode` | 存在（配置目录） |
| `C:\Users\49745\AppData\Local\@zcodedesktop-updater` | 存在（更新器） |
| **可执行 CLI** | **未找到** |

**结论：ZCode 只有桌面版配置与更新器，没有可用的 headless CLI。**

这与 `doc/09_COLLABORATION.md` 的描述一致——ZCode 是桌面版 Agent，
通过其内置 CLI 调用，而该 CLI 未在本机 PATH 上暴露。

### 顺带发现

| 项 | 状态 |
|---|---|
| `codex` | `C:\Users\49745\AppData\Local\Programs\OpenAI\Codex\bin\codex.exe`，**可用** |
| `Qoder` | 本机存在多个目录（`Qoder`、`Qoder CN`、`qoder-*`），但 **AGENTS.md 记载 Qoder 已于 2026-10-08 退出本项目**，不分配 Owner/Reviewer |

## 三、因此 r25 的首选方案不可行

r25 建议「**Antigravity Owner + ZCode Reviewer**」。**其中 ZCode 不可用。**

## 四、可行的替代方案

### 方案 A（我推荐）：Owner = dsh，Reviewer = Antigravity

| 角色 | 人 | 理由 |
|---|---|---|
| **Owner** | **dsh** | 已扫出清单、最了解数据；r25 只禁止它做**唯一 Reviewer**，未禁止做 Owner |
| **Reviewer** | **Antigravity** | 实测可用；本 Session 已证明能抓实质错误；**独立于清单制作者** |

**这满足 r25 的核心要求**：

> DSH 审查自己的分类、阈值和证据挑选仍存在自我复核风险。

**由 Antigravity 审查 dsh 的分类与证据挑选——正是要把这个风险移走。**
角色是分离的：**制作者 ≠ 审查者**。

### 方案 B：Owner = Antigravity，Reviewer = dsh

| 角色 | 人 | 风险 |
|---|---|---|
| Owner | Antigravity | 可用，但需它重读 92 项清单与 checker 语义 |
| Reviewer | dsh | **回到 r25 明确反对的形态**：dsh 审查 dsh 扫出的清单 |

**不推荐。**

### 方案 C：Owner = Antigravity，Reviewer = Codex

| 角色 | 人 | 风险 |
|---|---|---|
| Owner | Antigravity | 可用 |
| Reviewer | Codex | Codex 是 Lead / Integrator / 裁定者，**兼做 Reviewer 会混淆裁决与审查** |

**不推荐**——本 Session 的 Codex 裁定质量很高，正因为它不做 Reviewer。

### 方案 D：等 ZCode 恢复

**不推荐作为默认**：ZCode 的可用时间不可知，而本 Task 的前置条件已经全部就绪。

## 五、我的判断

**推荐方案 A。**

理由不是「谁方便」，而是**角色分离的本质**：

- r25 担心的是「清单制作者审查自己的分类」；
- 方案 A 让 **Antigravity 审查 dsh 的分类**，风险被移走；
- 同时保留 **dsh 作为 Owner**——因为**最了解 92 项数据的人做实施，比重新学习一遍的人做实施更可靠**。

**Owner 与 Reviewer 的分离不是「换个人做所有事」，是「做的人不做审的人」。**

## 六、待 Codex 或用户确认

本文只提供**实测事实与建议**，不自行决定角色分配。

**若采用方案 A**，需要：
1. 更新 `GOV-PIN-LINEAGE-1` 的 `owner: dsh` / `reviewer: Antigravity`；
2. Codex 冻结 allowed paths 并释放；
3. 本 Task 当前是 `proposed`，需转 `ready` 才能实施。

**若采用其它方案**，请指明，我再更新 Task 文件。
