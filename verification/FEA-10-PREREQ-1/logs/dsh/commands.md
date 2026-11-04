COMMAND: dotnet build apps/desktop-avalonia/NewManga.sln -c Release --nologo
CWD: G:\CODEX\New Manga
DATE: 2026-11-04T15:10:00+08:00
EXIT=0 (成功；0 warnings / 0 errors)

COMMAND: dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build --nologo
EXIT=0 (1344 passed / 0 failed / 74 skipped; 8 assemblies)

COMMAND: dotnet test CoreClient.Tests --filter "FullyQualifiedName~CoreProtocolTests|FullyQualifiedName~AsciiWireTests"
EXIT=0 (13 passed)

COMMAND: dotnet test Host.Tests --filter FullyQualifiedName~Fea10PrereqProjectionTests
EXIT=0 (23 passed)
