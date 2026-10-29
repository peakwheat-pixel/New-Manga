# V11R-C-3 偏差登记

## D-C3-1：LegacyChrome 的兼容度量与中性 fallback（契约 §2.4 例外）

- 位置：``apps/desktop-avalonia/src/NewManga.App/Views/Legacy/LegacyChrome.cs``
- 内容：
  1. 旧壳 token 解析失败时的 fallback 画笔（panel/canvas/text/muted/accent/accentOn）是**显式中性常量**，
     仅在 DesignSystem 资源缺失（独立 legacy 测试或极早构造）时使用；DS 资源存在时 ``Resource()`` 永远优先。
  2. 旧壳卡片的圆角 12/8/6 是历史 pack 度量，DS 的 ``radius.sm/md`` 为 2px/3px，无法等价映射；登记为
     固定兼容度量（``CornerCardNeutral`` 等常量），**不进入** DS 令牌体系。
- 理由：``--shell=legacy`` 仅保留一个版本周期用于降级启动，不重新引入第二套主题真源；避免为退役路径
  新增令牌或契约分支。
- 退役：删旧壳时与 ``Views/Legacy/`` 一并删除，无需迁移。
