# P06 发布阻断检查清单（供 P20 引用）

> 依据：`doc/contracts/M2_DERIVED_PREVIEW_GC_DESIGN.md` §2.3 上线 Gate、`verification/M2-DERIVED-GC-2/g7-enablement-boundary.md` §2「分发迁移阻断 Gate」以及 `doc/tasks/P06.md` AC4。

---

## 1. 核心阻断准则（Release Blocking Policy）

在**包含早于 preview namespace 租约协议（`M2-DERIVED-GC-2` 之前版本）的存量装机升级/发布**场景下：
**分发迁移验收证据未完全归档前，发布物绝对不得以启用 sweep 的配置出货。**
若出货前无法满足本检查清单中的全部强制前置条件，发布构建必须：
- **处置方案**：通过配置或编译开关禁用 live-preview sweep 与 orphan/dead-row sweep（即 Core 启动时不执行扫描删除，保持只读/服务），或者阻断 Windows 安装包/升级包的分发（Fail-Closed）。

---

## 2. 逐项判定清单（P20 接入前必检）

| 编号 | 判定项 | 依据条款 | 所需证据形态 | 满足标准 | 不满足时的处置 |
|---|---|---|---|---|---|
| **CHK-01** | 旧进程受控全退出机制 | GC-2 G7 §2 (a) / AC2 | 双进程实测日志 + PID + 时间戳 + exit code (`verification/P06/ac2-quiet-window-evidence.json`) | 证明任何持共享租约的旧/同伴进程存活时，新版 Core 独占扫描被**非阻塞跳过**；所有旧进程退出后，新版 Core 独占窗口**首次扫描成功**。 | **阻断发布**。若多版本共存场景未证明旧进程全退出，sweep 必须保持全局禁用。 |
| **CHK-02** | 旧 catalog Fail-Closed 策略 | GC-2 G7 §2 (b) / AC3 | 真实进程启动日志 + 数据库指纹不变性证明 (`verification/P06/ac3-legacy-catalogs-evidence.json`) | 证明存量旧 catalog（含已有资源行未绑定、及旧 schema 缺 lifecycle 表两类）在新版本启动时**拒绝启动/拒绝服务**，数据库文件 SHA-256 **零改变**（零静默迁移、零复用）。 | **阻断发布**。若新版本对旧数据静默覆盖或未绑定认领，发布立即撤回。 |
| **CHK-03** | 显式迁移工具就绪与受控流程 | GC-2 G7 §2 (b) | 独立迁移工具 Task/文档及验收报告（若释放） | 存量旧 catalog 只能通过显式受控流程迁移（新 catalog + 校验工具）；不得依赖运行时自动迁移。 | 若无显式迁移工具且存在存量库，安装器必须提示用户全新安装或拒绝就地升级。 |
| **CHK-04** | 机制验证 vs 真实装机区分明确 | P06 AC6 / 边界纪律 | 证据报告中的边界声明文本 (`verification/P06/REPORT.md` §5) | 明确说明本仓库测试为受控构造下的「内核租约互斥机制验证」，**不等于**真实海量存量终端装机实测。 | P20 必须如实将本项标记为「机制已闭环，存量装机由分发升级脚本保证旧进程 kill」。 |
| **CHK-05** | 交付物指纹与 SHA-256 锁定 | P06 Canonical Evidence | 64 位十六进制 SHA-256 哈希值与工作区文件精确匹配 | 所有证据 JSON、日志与脚本的 SHA256 均通过 `Get-FileHash -Algorithm SHA256` 校验。 | 哈希不匹配视为证据篡改，P20 拒绝引用。 |

---

## 3. P20 引用指导

P20（Windows 发布 Gate）执行人在评估安装包与升级策略时：
1. 若本次发布为**全新安装（首版部署）**，且用户环境中无旧版本残留：
   - 引用 P06 的 AC1–AC3 机制证据，核验租约防护完备，允许开启 sweep。
2. 若本次发布为**包含旧版本升级的覆盖分发**：
   - 必须在 NSIS / MSI 安装升级脚本中加入**强制终止/关闭旧版全部残留进程（kill existing processes）**步骤；
   - 升级安装后新版本首次启动，将落在干净的独占静默窗口内，安全完成首次扫描；
   - 若旧 catalog 无法解析，安装器必须提示用户备份并执行受控迁移，严禁静默覆盖。
