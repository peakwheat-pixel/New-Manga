# Rolling Checkpoint — UI-SHELL-THEME-1（S3）

Date: 2026-10-27 · HEAD: `649e54ba1` · 集成：`657d36817` · 交付：`28cd1324c`

## 完成

- AC1–AC6 MET；DSH 复核 PASS：单命令 `scripts/test.ps1` → **74/74**（裸跑 58/16 skip 有原因）。
- 主窗：沉浸标题栏（Mica/Win10 回退）、四页导航、单实例、首帧不阻塞、WinExe 无控制台。
- 主题中心：ThemePack 六件套 + `ThemeDictionaries{Light,Dark}`；内置 **6 套**（Saber Purple 默认）；3 套×10 次热切 **p95 2.215ms**（门禁 ≤100ms）；reduced-motion 归零、无色残留。
- 书架：紫渐变顶栏、1400 居中、搜索+标签、3:4 网格（VM 计算列数 1400→7）、hover 详情、空态/无结果态。
- 设置骨架：主题中心 + 命令台账；13 条命令接线；S2 的 50 NS 中登记 8 条 PLANNED（S3-A/B/C）。
- 状态：done；canonical_evidence=complete（E1–E11 + 70 SOURCE_PIN）；resource_closeout=complete。

## 未完成 / 风险

- 8 条 NS 仍 PLANNED（随 S4/S5 批次接线）。
- 真机 Mica/无控制台未重新 publish 验证（打包参数同 S1/S2，S5 安装包 Gate 统一复验）。
- 截图证据以资源色差分替代 Skia 截图（可接受）。
- IME/Narrator/真 200% 屏仍未验证。

## 下一步

1. S4 `UI-WORKBENCH-READER-1` 已释放并派发（task-12）。
2. 并行：Core 瘦身立项、`INFER-BASELINE-EP-1` 释放、pytest triage。
3. S4 done → S5 `LEGACY-SHELL-REMOVAL-1`。
