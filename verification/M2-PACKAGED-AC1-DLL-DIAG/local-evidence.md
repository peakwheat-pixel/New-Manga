# Codex独立执行证据（交DSH作者核对/更新报告）
固定执行code head=13804524c12dbf5bb97d9b2c824d947ff43cb276；原probe=d3006691；source_head=cfb5d2ee；installerSHA保持原pin。
raw/static-c9e26f6f45.log、copy-5be2e006d8.log：外层EXIT0；复制副本bridge实际EXIT1/0.8s，QtGui错误复现。
固定installer及五个exe hash实测匹配；安装树关键Qt/ICU文件存在，bundle/installed/build_env QtDLL hash相同。
raw/loader-probe.log：QtCore/QtGui/pyside/pyd WinError127，shiboken/ICU可加载。
raw/loader-system-icu-control.log：独立进程预加载System32 ICU后，同hash QtCore/QtGui可加载；环境对照，不是Gate。
raw/symbol-probe-full-exports.json：QtCore向icuuc要求20个无后缀符号；包内ICU仅导出_78名称，ICU直接缺符号。
raw/binary-version-origin.json：bundle/installed ICU hash匹配39aec884...，QtDLL6.11.2匹配原buildenv，未修改。
raw/icu-control-result.json及两个icu-control日志：复制同一bridge EXE、EOF/自有data根/purgedPATH；
原ICU EXIT1+同QtGui错误；仅自有新副本改名icuuc保留字节，bridge完成初始化EXIT0。
此因果对照不构成安装修复或完整26项Gate PASS。不能全局删ICU78，其他依赖是否需要它仍需后续保持/验证。

证据勘误：第一次wrapper路径错误预检EXIT1，无子进程启动（原记录保留）；初次static子环境缺PATHEXT使step6失败，
补齐子进程识别环境后另行重跑。raw/symbol-probe.json中的QtGui→QtCore64缺符号是pefile默认8192导出项上限伪差，
max_symbol_exports=100000并断言完整名称数后，该64项消失；native GetProcAddress两样本也确认存在。
原PE脚本delay import未独立验证，不将其延迟扫描零项作完整断言。ICU直接普通imports+native+bridge因果链不依赖该扫描。
规范参照 https://learn.microsoft.com/en-us/windows/win32/debug/pe-format （只用于PE符号结构；根因来自本机实测）。

请DSH独立核对Codex支持probe逻辑和原始运行日志，更新REPORT/矩阵与最小拟议修复范围，不自己批准/done。
产品/packaging/deps全部只读；仅诊断Task完成可进入Review。生产修复下一Task仍未释放。
