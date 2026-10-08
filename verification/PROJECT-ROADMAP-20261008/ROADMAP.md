# New Manga 一眼路线图（2026-10-08）

最新工作点：P08/P03=done；唯一释放Task=P01 `ready`，Owner=Codex、Reviewer=DeepSeek Harness，base=`826bea12a132c5af2ac0cd1244d00e9170093c71`。继续指令见[P01 RESUME](../../verification/P01/RESUME.md)。P03验证绑定source `d717c049`与同一installer，集成无产品/runner/test/build差量。

**当前位置：P08/P03=done；P系列done 2/21、ready 1、proposed 18。唯一ready Task=P01；P03 integration=`552464238a69ad2cea63cff18abe98f412dbae87`，DSH R5/R6与Codex Integration Gate PASS。**

人员更新：用户已移除Qoder，图中未来UI/UX责任由ZCode承担；非作者Review与正式Task释放Gate保持。

派生视图；排期事实以 [REBASELINE_PLAN](../../doc/REBASELINE_PLAN.md) 当前覆盖层为准。原审计基线：`main@e4242ecd`；箭头表示启动依赖，不是工期；没有可靠估算，不编造百分比或日期。P03已完成；当前按Plan释放P01，其余候选仍按各自依赖与范围Gate排期。

## 已做到哪里

```mermaid
flowchart TB
  A["已完成：基础架构<br/>Python Core · SQLite · Managed Copy"] --> B["已完成：安全桥接<br/>Tauri IPC · 大图资源通道 · Windows打包"]
  B --> C["已完成：业务竖切<br/>书目/页导航 · 区域改标 · 撤销 · 重渲染"]
  A --> D["已完成：AI生产与实验链<br/>manga检测 · SFX · OCR适配 · JA/KO素材"]
  C --> E["当前产品：部分可操作<br/>Console＋Workbench；任务进度仍占位"]
  D --> E
  E --> F["未完成：完整用户闭环<br/>导入 → 翻译运行/恢复 → 阅读/导出"]
  E --> G["未完成：完整四页界面<br/>书架 / 工作台 / 阅读器 / 设置"]
  F --> H["未完成：整体产品验收<br/>真实质量＋四页行为＋声明的Windows矩阵"]
  G --> H
```

“已完成”仅针对各 Task 冻结范围。AI实验有如实 FAIL 的结论；后端 API 可用、测试模式端到端成功，均不能代替正式界面链路。

## 当前范围内：先收口，再进入整产品主链

```mermaid
flowchart TB
  BASE["当前位置：P08/P03 done<br/>P系列done 2/21、ready 1、proposed 18"] --> P01["P01<br/>ready / 唯一释放Task<br/>台账取证<br/>Owner Codex · Reviewer DSH<br/>base 826bea12"]
  BASE --> P02["P02<br/>proposed / 未释放<br/>真UI验证<br/>点击/300ms刷新/对比度/失效窗口"]
  BASE --> P03["P03<br/>done / Review与Codex集成Gate通过<br/>第五入口Gate<br/>集成55246423；Gate绑定d717"]
  BASE --> P04["P04<br/>proposed / 未释放<br/>生产命令面验证<br/>常量成员与并发响应；先复现再决定修复"]
  BASE --> P05["P05<br/>proposed / 未释放<br/>错误语义澄清<br/>category与retryable注记一致"]
  BASE --> P06["P06<br/>proposed / 未释放<br/>GC迁移补证<br/>旧版本退出/命名空间保护；未知保留"]
  P02 -. "确认实际缺口后" .-> P07["P07<br/>proposed / 未释放<br/>小交互修补<br/>手输image读取/quiet-window busy"]
  style P03 fill:#d1e7dd,stroke:#198754,stroke-width:3px
```

P01已正式释放并冻结allowed_paths、Owner/Reviewer、base、branch和worktree；恢复与自动推进指令见P01 RESUME。P02仍需先冻结真实WebView harness Task；P06仍需实证旧runtime可用性。其余候选按Plan依赖释放。启动每个Task前仍需正式Task、不同Owner/Reviewer和allowed_paths。

## 完整产品：现在就看清后续，而不是每次临时猜下一件

```mermaid
flowchart TB
  P08["P08<br/>done / DSH Review与Codex集成通过<br/>范围＋四页设计冻结<br/>R7 fixed head fe222464；Task与Gate已收口"] --> ARCHDOC["Architecture Documentation Rebaseline Task<br/>未登记 / 未释放<br/>AC-DOC先于P09；stack-specific映射先于P18/P20"]
  ARCHDOC --> P09["P09<br/>proposed / 未释放<br/>真实导入契约与Core适配<br/>图片/PDF/MOBI；真实尺寸；Managed Copy"]
  ARCHDOC -.-> P18
  ARCHDOC -.-> P20
  P08 --> P10["P10<br/>proposed / 未释放<br/>设置与凭据安全通道<br/>Provider配置可验证；secret不进普通DTO"]
  P08 --> P11["P11<br/>proposed / 未释放<br/>长任务契约冻结<br/>启动/快照/暂停取消重试/恢复语义"]
  P09 --> P12["P12<br/>proposed / 未释放<br/>书架与导入产品链<br/>建书/章节/选文件/结果；ZCode接UI"]
  P09 --> P13["P13<br/>proposed / 未释放<br/>Pipeline后台运行与恢复<br/>复用现有调度；持久状态；ZCode实现"]
  P11 --> P13
  P13 --> P14["P14<br/>proposed / 未释放<br/>工作台完整操作链<br/>运行/进度/人工译文/Lock/Pin/区域编辑"]
  P10 --> P15["P15<br/>proposed / 未释放<br/>完整设置页<br/>模型下载/全库备份/P0/P1维护"]
  P13 --> P15
  P13 --> P16["P16<br/>proposed / 未释放<br/>阅读与导出契约＋Core<br/>进度/PNG/ZIP/CBZ/PDF/文本安全输出"]
  P08 -. "D1基础Reader已选入" .-> P16
  P16 --> P17["P17<br/>proposed / 未释放<br/>阅读器与导出UI<br/>读取真实结果/保存进度/安全导出"]
  P10 --> P18["P18<br/>proposed / 未释放<br/>真JA/KO质量资格<br/>检测/OCR/翻译/修复/无字页；DSH验收"]
  P13 --> P18
  P12 --> P19["P19<br/>proposed / 未释放<br/>四页完整E2E与数据安全<br/>正常/失败/人工修改/Lock/重启；非作者验收"]
  P14 --> P19
  P15 --> P19
  P17 --> P19
  P18 --> P19
  P19 --> P20["P20<br/>proposed / 未释放<br/>最终Windows发布Gate<br/>新fixed-head安装包；声明矩阵；独立审查"]
  P03["P03<br/>done / 固定Review与Gate完成<br/>integration 55246423"] --> P20
  P06["P06<br/>proposed / 未释放<br/>GC分发补证"] --> P20
  P20 -. "另行授权，可选" .-> P21["P21<br/>proposed / 未释放<br/>Legacy归档/移除<br/>新架构parity通过后；不修旧架构"]
  style P08 fill:#d1e7dd,stroke:#198754,stroke-width:3px
```

P12/P14/P15/P17另需P08范围确认后分别释放的ZCode页面设计Task通过非作者Review；这些设计切片不额外增加P01–P21产品节点。

完整产品候选任务尚未释放。D1已解冻基础Reader；跨页联动/页缩略图继续延期。缩略图、跨页联动不作为默认任务。P09/P10/P11 内部先契约后实现，正式释放时拆为独立 Task；P14新增编辑能力同样先Codex冻结命令、ZCode/Antigravity实现Core、再ZCode接UI；P16先Core/IPC后P17 UI。Pipeline 最小成功链可先用 deterministic provider，真实质量 Gate 依赖 P10 和可用受控模型/endpoint，不能将 mock PASS 当真质量 PASS。

长会话/磁盘总量、模型扩展与训练不是默认关键路径。BJ13 维持 0.90、手工改标＋skip；Manga109 永久取消。不重新打开已完成 TA3-B2/B3、GC-2、ICU 或 Runner Guard。

## 每一步怎么算完成

```mermaid
flowchart LR
  A["冻结Task<br/>依赖/范围/Owner/基线"] --> B["实现交付<br/>代码＋可复现测试＋Handoff"]
  B --> C["非作者Review<br/>固定提交；条件闭合"]
  C --> D["Codex集成验证<br/>核路径/数据安全/受影响回归"]
  D --> E["done＋更新台账<br/>提前解锁下一规划节点"]
```

额度中断时：读 [RESUME](RESUME.md) → 核 Git/当前 STATUS → 复用报告 → 只重算变化的依赖子图。等待额度恢复无需重做全仓审计；外部 Agent 接管须按协作协议分配，Owner 不得审自己。
