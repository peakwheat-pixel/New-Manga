# New Manga 源码快照

此目录是固定源码 `349e61faff5f93067af5d4ce2d9e394e0d665b8c` 的独立快照，目标架构为 Windows / React + TypeScript / Tauri / Python Core / SQLite / Managed Copy。SOURCE_MANIFEST.json 记录逐文件来源；源历史、私有漫画/数据、模型、数据库、日志、验证证据及Agent配置未随快照分发。现有Legacy源码仅保留参考，不代表继续演进的目标。未授予新的项目或第三方许可证。

两处文档/测试中的个人目录字面量已替换为USER，清单同时保留源/导出hash。experiments/TASK-016/samples 仅含从自制生成器重建的5个合成测试PNG及manifest，供Rust测试编译，不是漫画素材或模型质量证明。

前端：在 apps/desktop/frontend 中执行 npm ci、npm test、npm run build。Core：在已具备所需Python依赖的环境中，从根目录执行 python -B -m pytest tests/core -q -rs。requirements文件保持源版本，不表示已重新认证全部依赖。

Tauri本地开发检查需设置 M2RC1_DEV_PREVIEW=1 并先构建frontend；生产打包还需要独立准备sidecar、模型与运行环境，详见 packaging/m2ac5/README.md。私有模型/输入不随本快照提供。源码中的历史doc/verification引用属于原项目上下文，此快照不声称包含这些证据。

当前仅供本地检查；没有执行push、发布或签名，构建与审查结果以本次交付记录为准。
