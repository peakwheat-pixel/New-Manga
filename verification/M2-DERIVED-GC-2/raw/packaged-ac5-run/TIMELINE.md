# m2ac5 packaged runner 两轮时间线（Codex r1 F-08 说明）

- 第一轮（FAIR，修正前 runner）：产品代码同 HEAD，但 runner 尚无 AC1 fixture
  prebind 与 CS-Z2 协议锁白名单 → CS-A1..A5 FAIL（fixture catalog 未绑定）+
  CS-Z2 FAIL（.preview-lifecycle.lock 出现在 derived 根）。该轮完整输出已随
  packaged-runners.log 首段归档。
- 第二轮（PASS 场景面，本目录 second-round-full-stdout.log）：runner 补两处
  fixture 语义修正后重跑，18 项打印场景全 PASS；gate JSON=cleanstart-gate.json。
  唯一 FAIL=CS-L1（runner 协议 minor 3 陈旧快照，既有漂移，交 debt Task）。
- 修复与重跑之间产品代码零改动（同一安装包）。
