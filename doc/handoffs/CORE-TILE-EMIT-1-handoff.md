---
task_id: CORE-TILE-EMIT-1
author: avalonia-spike
recipient: DeepSeek Harness
base_commit: 744eccb61
delivery_head: 2c2c1f3ebe4aed18455ce7d1b92d6a9d2230a9ef
status: draft
---

# Handoff：CORE-TILE-EMIT-1

## 结果（AC1–AC5 全 MET）
- **AC1 tile 生成**：新增 \pplication.resource_channel.tiles\，按契约把渲染页切为水平带（默认 2048px 高、整宽），拼接为单一派生流 \page.bin\，清单为 \esource_id/revision/size/tiles[index,offset,length,sha256]\；\alidate_manifest\ 校验连续性/覆盖/64-hex。
- **AC2 摘要一致性**：Host 端独立重算 2/2 tile 摘要 **一致率 100%**，\digest_mismatches=0\；中文/unicode 路径（\中文目录_日本語/日漫_第1页_テスト.png\、输出 \派生_tiles\）不炸，manifest 为纯 ASCII（\\\uXXXX\），原始字节证据已落盘。
- **AC3 契约测试**：Core 输出通过 \TILE-CHANNEL-CONTRACT-V1\ 校验（字段/类型/错误码），Host \TileChannel\ 端到端消费真实 Core 产物（\	est.ps1\ 先生成 artifact，Host 测试读取 manifest → issue → 逐 tile read 校验），**不用 fixture 兜底**。
- **AC4 回归**：pytest **3F/2691P/9S**（基线 3F/2687P/9S，+4 新通过、0 新增失败）；\scripts/test.ps1\ **102/102**；协议 2.3 与 57/66 命令面未改（新增独立模块，向后兼容）。
- **AC5 门禁**：check PASS；证据 E1–E8 64-hex pin；本 Handoff 含 Record Decision。

## 复跑与证据
\erification/CORE-TILE-EMIT-1/**\（MANIFEST \d613227a…\）。复跑：\python -m pytest\；\pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1\（先运行 Core tile emit CLI 生成 E2E artifact）。

## Record Decision
1. **tile 尺寸**：默认 2048px 高（契约默认；CLI \--tile-height\ 可调），整宽切条；派生流为各 PNG band 的字节拼接，Host 按 offset/length 读取并可逐 tile 解码。
2. **契约版本**：严格对齐 TILE-CHANNEL-CONTRACT-V1；未新增协议 2.3 字段、未改命令语义。
3. **unicode 策略**：路径用 pathlib；manifest 以 \nsure_ascii=True\ 写纯 ASCII，非 ASCII 一律 \\\uXXXX\；测试断言 bytes<128 且含转义。
4. **性能影响**：tile emit（1200×2400 两 tile）+ 摘要为毫秒级（证据 \mit.json\ 记录 emit_ms/digest_ms）；不引入常驻开销。
5. **E2E 边界**：artifact 由 test.ps1 的 Python 步骤生成、Host 测试消费；plain dotnet test 无 artifact 时记录 skipped 证据（不伪造通过）。

## 遗留
- 仅覆盖「已渲染页」；Core 渲染管线接线（何时调用 emit）留后续 Core 集成任务。
- Host 侧 UI 已可消费通道；实际阅读器切到真实 Core 产物需 S5-D 安装 smoke 联合验证。
- 旧壳未动、vite/pytest 基线未变；无 push。
