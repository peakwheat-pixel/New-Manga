# ARCH-DOC-REBASELINE AC5 非功能需求（NFR）新栈映射与证据 Gate 报告

**任务项**：AC5（P20 的 Tauri/WebView2/Python sidecar/Windows/UI/可选模型 对旧 stack-specific 条目的逐项保留与新证据 Gate）  
**执行角色**：Owner（Antigravity）  
**审查角色**：Reviewer（DeepSeek Harness）  
**基准 Commit**：`4ef92f3daa527adac752b8fc52d492176697a292`  
**当前状态**：NOT_RUN（旧 NFR 条目已逐项映射并保留且不降阈值，新二进制实测基准待 P20 执行）  
**消费 Gate**：P20（AC5）

---

## 1. 核心原则：产品级性能与质量阈值严格不降

> [!IMPORTANT]
> 架构从 PySide6 迁移至 Tauri + React + Python Core，目的是获得现代化的 UI 开发体验、强大的 WebGL 渲染生态和更高的工程健壮性，**绝不是为了放宽或妥协产品质量**。
> `07 非功能需求` 中定义的产品级性能指标、安全要求与稳定性阈值**全部保留，并且阈值绝对不作任何调宽或降低**。

---

## 2. 旧技术栈专属条目与新架构映射矩阵

| NFR 领域 | 旧架构实现形态与关注点 (PySide6 / QML / PyInstaller) | 新架构映射形态与关注点 (Tauri / WebView2 / Python Sidecar) | 产品级保留阈值与强制要求 | 新架构技术专项风险与防范措施 |
|---|---|---|---|---|
| **冷启动性能 (Cold Start)** | PyInstaller onedir 解包加载 Python 运行时、初始化 Qt Quick 引擎与 QML 界面渲染 | - Tauri 原生 Rust 进程秒级唤醒，迅速创建 WebView2 窗口<br/>- 异步启动 Python Core Sidecar 子进程并通过本地 IPC 完成握手 | - **主窗口首次呈现时间**：<= 2.0 秒<br/>- **Python Core 就绪并可处理请求**：<= 3.5 秒 | **风险**：Python 子进程启动延迟可能阻塞 UI。<br/>**防范**：前端先展示书架骨架屏并异步轮询握手，不锁死主界面。 |
| **内存占用 (Memory Footprint)** | 单进程模型：Python + PySide6 C++ 绑定 + QML 渲染树内存总和 | **多进程树模型 (Process Tree)**：<br/>1. Tauri Rust 主进程<br/>2. WebView2 渲染器进程群<br/>3. Python Core Sidecar 独立进程 | - **基础空闲驻留内存**（不加载大模型）：**<= 350 MB**（三者物理工作集 Working Set 严格总和）<br/>- 单图批处理峰值内存：<= 1.5 GB | **风险**：WebView2 与 Python 多进程导致内存膨胀。<br/>**防范**：限制 WebView2 缓存大小；Python Core 惰性加载大型科学计算库。 |
| **交互响应与帧率 (UI Latency & FPS)** | QML Scene Graph 渲染；Qt 信号槽跨线程通知可能导致 UI 掉帧卡顿 | React 虚拟 DOM + WebGL 画布渲染；Tauri 异步事件流驱动状态更新 | - **按键/点击交互延迟**：<= 50 ms<br/>- **单页/Webtoon 长图滚动帧率**：稳定 **60 FPS**<br/>- 缩放平移无明显撕裂 | **风险**：长图高分辨率渲染导致 GPU 显存过载。<br/>**防范**：采用虚拟列表（Virtual List）与切片可视区域渲染。 |
| **打包与分发 (Packaging & Distribution)** | PyInstaller 生成 Windows onedir，依赖打包 Qt DLL 与 Python C 扩展 | **Tauri Bundler** 打包 MSI / NSIS 安装包，内置 Python 独立运行时环境（Embedded Python）与预编译 Sidecar | - **干净 Windows 10/11 x64 环境一键安装**<br/>- 完整卸载无垃圾注册表与残留文件<br/>- 基础安装包体积控制在合理桌面软件范围 | **风险**：目标机器缺失 WebView2 Runtime 或 VC++ 运行库。<br/>**防范**：安装包配置自动检测并静默安装 WebView2 Bootstrapper。 |
| **模型解耦与无 GPU 兼容 (Optional Models)** | 本地模型直接 import PyTorch，缺 CUDA 时可能直接 Crash 退出 | **模型模块化与优雅降级 (Graceful Fallback)**：<br/>模型运行时按需动态加载；严格区分本地模型与远程 API Provider | - **无独立显卡/无 CUDA 环境时**：系统能够正常启动，基础功能与在线 API 正常运行，本地模型自动降级为 CPU 模式<br/>- 严禁因缺少 GPU 驱动导致启动失败 | **风险**：CPU 模式下模型计算极慢。<br/>**防范**：提供明确超时保护，并在设置页明确标记 CPU 性能警告与建议配置。 |
| **故障隔离与自愈 (Process Isolation)** | 单进程崩溃导致整个软件直接闪退，未保存数据面临严重丢失 | **进程故障隔离 (Fault Tolerance)**：<br/>Tauri 作为守护者监控 Python Sidecar 退出状态与异常输出 | - Python 异常崩溃时，Tauri 主窗口**严禁直接白屏退出**<br/>- 立即拦截并提示用户“后端服务异常，正在尝试热重启”<br/>- 本地未提交草稿与操作状态受前端保护不丢失 | **风险**：子进程死锁或僵尸进程。<br/>**防范**：Tauri 定期执行 IPC 心跳探测（Heartbeat），超时强制回收重启。 |

---

## 3. 新证据 Gate 验证规范

针对 P20 的验收，建立如下端到端测试与测量协议：

1. **测试基准环境**：
   - 操作系统：Windows 11 x64 / Windows 10 22H2 纯净虚拟机或物理机。
   - 硬件基线：Intel i5 / 8GB RAM / 无独立 GPU（纯集成显卡基线）与 具备 NVIDIA GPU 档位分别测量。
2. **监控测量工具**：
   - 采用标准 PowerShell 性能监控脚本与 Windows Performance Recorder (WPR)；
   - 监控指标必须采集整棵进程树（`Tauri.exe` + 多个 `msedgewebview2.exe` + `python.exe`）的 Working Set 与 Private Bytes。
3. **证据产物归档**：
   - 性能测试必须产出 CSV 格式的采样时序数据、内存曲线图与系统日志。

---

## 4. 核验结论与 Gate 裁决

- **本项结论**：**NOT_RUN**
  - **已达成**：旧技术栈条目已逐项完成新架构映射，产品级 NFR 阈值（冷启动、进程树内存总和、60 FPS 滚动、打包分发、故障隔离）得到完整保留且无任何降级；新证据 Gate 规范已正式冻结。
  - **未达成（NOT_RUN 原因）**：当前工作空间属于文档重基线阶段，新架构 Tauri + Python 完整集成包尚未产出，真实环境下的基准测量数据待后续实施。
- **未决项与责任 Gate**：
  - 转移至下游消费任务 **P20（AC5）**：由 P20 在完成 Tauri 桌面打包与集成构建后，在干净 Windows 测试环境下执行 NFR 基准测试，出具正式的 NFR 验收证据报告。
