# GATE4-PAGES-UPGRADE-1 证据（条件 4 收尾）

卡面：`doc/tasks/GATE4-PAGES-UPGRADE-1.md`。基线 `6485c44b8`。

## 1. 四页可达性（安装产物上）

**安装产物**：`%LOCALAPPDATA%\Programs\NewManga\app\NewManga.App.exe`
（`ProductVersion=0.1.1+71cecb95a…`，sha256 `a3ec2133…9230`，来自 `VERSION-MANIFEST-GUARD-1` 校验过的 stage）。

**方法**（`capture-page.ps1`）：`--page=<page>` 启动 → 轮询 `MainWindowHandle` 且**要求窗口标题含 `NewManga`**
→ `PrintWindow(PW_RENDERFULLCONTENT=2)` 直接从窗口渲染（**不用屏幕截图**）→ 亮度方差 ≥ 40 才算非空帧。

| 页 | `--page` | 结果 | 证据 |
|---|---|---|---|
| 书架（资料柜） | `bookshelf` | ✅ **PASS** | `pages/bookshelf.png`，1416×939，variance 2564.3，35,540 B，sha256 `2d62b2d7ca6632…`。**目视确认**：标题栏 `New Manga`、导航 `资料柜 1 / 工位 2 / 控制台 3 / 主题工作室`、内容 `书架还是空的`、底栏 `Host 就绪` |
| 工作台（工位） | `workbench` | ✅ **PASS** | `pages/workbench.png`，1416×939，variance 2499.9，55,232 B，sha256 `27942f4e1703…` |
| 设置 | `settings` | ✅ **PASS** | `pages/settings.png`，1416×939，variance 2646.0，63,857 B，sha256 `09ee3db7cd42…` |
| 阅读器 | `reader` | ❌ **NOT_REACHABLE（空库）** | `pages/reader.png` 与 `bookshelf.png` **哈希完全相同**（`2d62b2d7ca6632…`）⇒ `--page=reader` 在**没有任何书籍**的数据根下回落到了书架 |

**关于阅读器**：`--page=reader` 的导航本身没有报错（`startup.log` 无导航错误），但阅读器需要一本书才能进入；
空数据根下它与书架是同一幅画面。**未**把它算作"已到达" —— 要补齐需先在隔离数据根里导入一本书，
再以 `--page=reader` 启动。**本卡未做**，如实标 `NOT_REACHABLE`。

## 2. ★ 我第一次的截图是假的（必须登记）

**第一版 `capture-page.ps1` 用 `Graphics.CopyFromScreen` 截窗口矩形**，结果四张 PNG 全是**桌面** ——
里面是我的 DSH 对话窗口和 VPN 工具，**没有一张是 NewManga**。
更糟的是：四张图的哈希**各不相同**，variance 也各不相同，**看起来完全像"四页不同"的证据**。

**为什么没发现（我自己差点放过去）**：我只看了 `variance` 数字和"哈希不同"，**没有看图**。
直到我把 `bookshelf.png` 读出来目视检查，才看到那是桌面。

**修正**：改为 `PrintWindow(PW_RENDERFULLCONTENT)`（从窗口自身渲染，不依赖前台与遮挡），
并**强制要求窗口标题含 `NewManga`**，不匹配就 FAIL。修正后 `title='New Manga'`，
`bookshelf.png` 目视确认是真界面。

**教训**：**"数字不同"不等于"内容正确"**。凡是截图类证据，**必须人眼过一遍**，
且必须用**从目标窗口渲染**的方式，而不是"屏幕上刚好是什么"。

## 3. 隔离与数据根保护

- 所有启动都传 `--data-root=<workspace 内隔离目录>`（`...\GATE4-PAGES-UPGRADE-1\data`）。
- 启动前 `%APPDATA%\com.newmanga.desktop` 清单 SHA-256 = `6ae4d6da17a87b5729cb20ab7f4df6662ddd68079c72b28f2bba62ac1c46d9b2`。
- （收尾时复核，见 §5。）

## 4. 截图存放

按卡面 AC7：**截图留在 workspace**（`G:\CODEX\New Manga.workspace\task-envs\GATE4-PAGES-UPGRADE-1\pages\`），
仓库只放本说明与 `capture-page.ps1`（可复现脚本）。

| 文件 | 字节 | sha256（前 16） |
|---|---|---|
| bookshelf.png | 35,540 | `2d62b2d7ca663239` |
| workbench.png | 55,232 | `27942f4e170332bf` |
| settings.png | 63,857 | `09ee3db7cd42e444` |
| reader.png | 35,540 | `2d62b2d7ca663239`（= bookshelf，未到达） |

## 5. 升级/回退矩阵

**NOT_RUN**（本卡未完成）。需要先造一个 0.1.0 的 stage/setup，再做"装 0.1.0 → 覆盖装 0.1.1 → 卸载 → 装 0.1.0"。
造 0.1.0 时的注意点（已在卡面 AC6 写明）：**exe 与 sidecar 的真实 sha256/head 一律不动**，
只改 `VERSION.json.version`，并说明为何这不算造假。

## 6. 边界

- 条件 4 仍**不判 MET**：sidecar 缺 SFX 权重（`yolo11s-seg.onnx`）、安装器 unsigned、
  阅读器页未在空库下到达、升级/回退未做。
- 本卡的截图**只证明"安装产物能到达三个一级页面"**，不证明页面上的功能可用。
