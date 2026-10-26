# 许可证一致性审计（RELEASE-PACKAGE-1）

- 包内 `LICENSE` / `NOTICE.md` / `THIRD_PARTY_LICENSES.md` 与仓库根逐字节复制（SHA-256 相等，见 `package-summary.json`）。
- 字体：**仅系统字体栈**（Segoe UI / Microsoft YaHei UI / PingFang SC / Noto Sans CJK SC / sans-serif），不随包任何字体。
- AGPL 结论：仓库当前依赖清单未包含 AGPL 运行时组件；若未来集成 AGPL 组件（如 Ultralytics），整体分发许可改为 AGPL-3.0 并在 NOTICE 更新。本卡未引入新依赖。
- 模型权重不随包；第三方许可文本随包原样分发。
