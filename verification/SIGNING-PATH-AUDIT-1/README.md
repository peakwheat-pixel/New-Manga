# SIGNING-PATH-AUDIT-1：签名路径**不需要买证书** —— 有 SignPath 免费 OSS 通道，只差两步 GitHub 操作

基线 `b1742a052`。承接 `GATE4-MODEL-RECOVERED-1`（同一次"别假设做不了"的审计）。

## 1. 我此前的说法

`GATE4-REMAINING-1` / `BLOCKED-ITEM-AUDIT-1` 里我写：

> installer unsigned = **BLOCKED（需用户提供签名证书）**

**这个说法不准确。** 它把一个**已在推进的免费路径**说成了"要买证书"。

## 2. 仓库里的真实状态

### 2.1 "unsigned" 是**当前设计**，不是疏漏

`apps/desktop-avalonia/scripts/build-installer.ps1`：

```
:3    Build the per-user, unsigned NSIS installer (NSIS-INSTALLER-1) ...
:239  authenticode: {0} (unsigned release by design)
```

⇒ 脚本**明确标注** "unsigned release by design"，并把
`authenticode_status` 写进 `build-info.json` 供证据 pin 使用。

### 2.2 **文件系统搜索确认没有现成证书**

`Get-ChildItem -Recurse -Include *.pfx,*.p12,*.cer,*.crt,*.snk,*.p7b` —— **零结果**（这次是**真搜了文件系统**，
不是只搜索引）。⇒ **本机确实没有证书**。

### 2.3 ★ 但有 **SignPath 免费 OSS 签名**通道，且已推进到 P0-4

- `doc/release/SIGNPATH-APPLICATION.md`（185 行，**英文申请草案**）
- `doc/release/SIGNPATH-APPLICATION-CHECKLIST.md`（73 行，**中文操作指引**）

**清单原文的关键结论**：

> 免费签名可以申请，但**当前公开仓库还不满足审核前提**……
> **执行状态（2026-10-28，Task `PUBLIC-RELEASE-P0-1`）**：公开分支 `public-release` 已推送
> （`3207e9c18…`，1040 文件/16.73 MiB，含许可四件套 + README + 产品源码树 + CI 草案；远端 `main` 未动）。
> - **P0-1 / P0-2 / P0-3 / P0-5：已在 `public-release` 分支完成**（raw 全部 200）
> - **P0-4：部分完成** —— workflow 已公开且 YAML 可解析，但**首次 Run 与默认分支切换需用户两步**：
>   ① GitHub Settings → Branches → 默认分支改为 `public-release`；
>   ② Actions → `build-release` → Run（`version=0.1.0`、`sign=false`）。
>   本机 `gh` 未认证、无 `GH_TOKEN`，Agent 未代持 token、未伪造 Run。

## 3. 结论：阻塞性质被我说错了

| 我此前的说法 | 真实情况 |
|---|---|
| "需用户提供**签名证书**" | **不需要买证书**。有 SignPath Foundation 免费 OSS 签名通道 |
| （隐含：这是个大成本） | **P0-1/2/3/5 已完成**；**只差 P0-4 的两步 GitHub 操作** |

**⇒ 条件 4 的签名项应改为**：
**「需仓库所有者在 GitHub 做两步（切默认分支 + 手动 Run 一次 workflow），然后提交 SignPath 申请」**
—— 而不是"需提供证书"。

**且**：即使不签名，`build-installer.ps1` 也已经**按设计**产出 unsigned 安装包并把
`authenticode_status` 记进 `build-info.json` —— **unsigned 是一个被明确记录的状态，不是隐瞒**。

## 4. 这是**第 4 次**"把可推进的事说成需人/需买"

| # | 项 | 我的错误 | 实际 |
|---|---|---|---|
| 1 | `L-F1-3` | "需真人定义压测口径" | 夹具我自己能造 |
| 2 | `E-9` | "需新增持久化" | 路径就在 `roots[0]` |
| 3 | `yolo11s-seg.onnx` | "全盘搜索过，不存在" | 在 `target/` 里（gitignore） |
| 4 | **签名** | "**需用户提供签名证书**" | **已有 SignPath 免费通道，只差两步 GitHub 操作** |

**共同点：我把"我没查清"说成了"需要用户/需要花钱"。**
**前三次都是外部裁决（ZCode）替我抓住的；这次是我自己按上一轮的承诺主动去查的。**

## 5. 未做（诚实）

- **未核实 GitHub 当前默认分支到底是哪个**（`gh` 未认证；本卡只读仓库内文档，未访问远端）。
  清单说"远端 `main` 未动"，但那是 **2026-10-28** 的记录，**可能已变化**。
- **未提交 SignPath 申请**（需真实身份与邮箱，属用户动作）。
- 未验证 `public-release` 分支是否仍在（需远端访问）。

## 6. 核实"两步 GitHub"是否真的需人（2026-11-15）

我在别处把 P0-4 的两步标为"需人"。**按纪律要核实，不能凭印象。**

实测：

```
(Get-Command gh).Source  -> C:\Program Files\GitHub CLI\gh.exe   （gh 已安装）
gh auth status           -> You are not logged into any GitHub hosts. To log in, run: gh auth login
$env:GH_TOKEN            -> unset
$env:GITHUB_TOKEN        -> unset
git remote -v            -> origin  https://github.com/peakwheat-pixel/New-Manga.git
```

**⇒ 结论：确认需人。**

- `gh` **已安装**，但**未认证**；
- **没有任何 token 环境变量**；
- 我不能、也不应该代持 GitHub 凭据（项目纪律：Agent 不代持账号/token/密钥）。

**⇒ 这两步（切默认分支 + 手动 Run 一次 workflow）必须由仓库所有者完成。这不是我的推测，是实测。**

**我能做、且已做的部分**：
- 定位到 SignPath 免费通道（`SIGNPATH-APPLICATION.md`）；
- 确认 P0-1/2/3/5 **已在 `public-release` 分支完成**；
- 确认只差 P0-4 的两步；
- **提供确切的操作路径**（Settings → Branches → 默认分支改 `public-release`；
  Actions → `build-release` → Run，`version=0.1.0`、`sign=false`）。
