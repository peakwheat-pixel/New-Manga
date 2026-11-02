; NSIS-INSTALLER-1: per-user, unsigned installer for the New Manga base variant.
;
; Build with apps/desktop-avalonia/scripts/build-installer.ps1 (it passes every define below).
;   makensis /DVERSION=0.1.0 /DVERSION4=0.1.0.0 /DSTAGE_DIR=<base stage> /DOUT_FILE=<setup.exe> \
;            /DINSTALL_SIZE_KB=... /DLICENSE_FILE=<stage>\NOTICE.md [/DICON_FILE=<icon.ico>] installer.nsi
;
; Design constraints frozen by the task card:
;   * per-user install under %LOCALAPPDATA%\Programs\NewManga, RequestExecutionLevel user (no UAC);
;   * HKCU uninstall entry + Start Menu shortcuts only - never HKLM / Program Files;
;   * the user data root %APPDATA%\com.newmanga.desktop is NEVER touched by install or uninstall;
;   * /S silent install and silent uninstall both supported; reinstall is an in-place upgrade;
;   * the package is unsigned (SmartScreen warning is the documented known limitation).

Unicode true
!include "MUI2.nsh"

!ifndef VERSION
  !error "VERSION define is required (-DVERSION=<x.y.z>)"
!endif
!ifndef VERSION4
  !error "VERSION4 define is required (-DVERSION4=<x.y.z.0>, NSIS VIProductVersion needs 4 numbers)"
!endif
!ifndef STAGE_DIR
  !error "STAGE_DIR define is required (-DSTAGE_DIR=<packaged base stage directory>)"
!endif
!ifndef OUT_FILE
  !error "OUT_FILE define is required (-DOUT_FILE=<setup.exe path>)"
!endif
!ifndef INSTALL_SIZE_KB
  !define INSTALL_SIZE_KB 220000
!endif
!ifndef LICENSE_FILE
  !define LICENSE_FILE "${STAGE_DIR}\NOTICE.md"
!endif

!define APP_NAME "New Manga"
!define APP_ID "NewManga"
!define APP_EXE "NewManga.App.exe"
!define APP_PUBLISHER "New Manga"
!define APP_URL "https://github.com/new-manga/new-manga"
!define UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_ID}"
!define APP_REG_KEY "Software\${APP_ID}"
!define INSTALL_LOG "$TEMP\NewManga-install-${VERSION}.log"
!define UNINSTALL_LOG "$TEMP\NewManga-uninstall-${VERSION}.log"

Name "${APP_NAME} ${VERSION}"
OutFile "${OUT_FILE}"
InstallDir "$LOCALAPPDATA\Programs\NewManga"
InstallDirRegKey HKCU "${APP_REG_KEY}" "InstallLocation"
RequestExecutionLevel user
SetCompressor /SOLID lzma
SetCompressorDictSize 32

VIProductVersion "${VERSION4}"
VIAddVersionKey "ProductName" "${APP_NAME}"
VIAddVersionKey "ProductVersion" "${VERSION}"
VIAddVersionKey "FileVersion" "${VERSION}"
VIAddVersionKey "CompanyName" "${APP_PUBLISHER}"
VIAddVersionKey "FileDescription" "${APP_NAME} setup (per-user, unsigned)"
VIAddVersionKey "LegalCopyright" "GPL-3.0-or-later (base) / AGPL-3.0 for the models package; see LICENSE and LICENSE-AGPL-3.0.txt"

!ifdef ICON_FILE
  Icon "${ICON_FILE}"
  UninstallIcon "${ICON_FILE}"
  !define MUI_ICON "${ICON_FILE}"
  !define MUI_UNICON "${ICON_FILE}"
!endif

; ---- UI ---------------------------------------------------------------------
!define MUI_ABORTWARNING
!define MUI_WELCOMEPAGE_TITLE "${APP_NAME} ${VERSION} 安装"
!define MUI_WELCOMEPAGE_TEXT "本安装包为 base 变体（不含模型权重，按 GPL-3.0-or-later 分发）。安装到当前用户目录，无需管理员权限；用户数据根 %APPDATA%\com.newmanga.desktop 不会被改动。"
!define MUI_LICENSEPAGE_TEXT_TOP "base 变体整体按 GPL-3.0-or-later 分发。若安装 models 变体（含 Ultralytics YOLO11s-seg 权重），该包整体按 AGPL-3.0 分发。完整文本随包提供：LICENSE、LICENSE-AGPL-3.0.txt、NOTICE.md、THIRD_PARTY_LICENSES.md。"
!define MUI_LICENSEPAGE_TEXT_BOTTOM "点击「我接受」继续安装。"
!define MUI_FINISHPAGE_RUN "$INSTDIR\app\${APP_EXE}"
!define MUI_FINISHPAGE_RUN_TEXT "运行 ${APP_NAME}"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\MANUAL_VERIFY.md"
!define MUI_FINISHPAGE_SHOWREADME_TEXT "查看安装后验证说明"
!define MUI_DIRECTORYPAGE_TEXT_TOP "安装到当前用户目录（per-user），不需要管理员权限。数据目录独立保留。"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "${LICENSE_FILE}"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "SimpChinese"
!insertmacro MUI_LANGUAGE "English"

Var InstallLog
Var UninstallLog

; ---- install ----------------------------------------------------------------
Section "Install" SecInstall
  SetShellVarContext current
  AddSize ${INSTALL_SIZE_KB}

  FileOpen $InstallLog "${INSTALL_LOG}" w
  FileWrite $InstallLog "NewManga installer ${VERSION}$\r$\n"
  FileWrite $InstallLog "variant=base (GPL-3.0-or-later; unsigned)$\r$\n"
  FileWrite $InstallLog "install_dir=$INSTDIR$\r$\n"
  FileWrite $InstallLog "data_root_not_touched=%APPDATA%\com.newmanga.desktop$\r$\n"

  SetOutPath "$INSTDIR"
  ; In-place upgrade: drop the previous payload we own (the data root lives elsewhere and is never
  ; referenced here). This also keeps reinstall idempotent when a file disappeared upstream.
  RMDir /r "$INSTDIR\app"
  Delete "$INSTDIR\*.md"
  Delete "$INSTDIR\*.txt"
  Delete "$INSTDIR\*.ps1"
  Delete "$INSTDIR\*.json"
  Delete "$INSTDIR\LICENSE"
  Delete "$INSTDIR\Uninstall.exe"

  ; The whole base stage: app\ (Avalonia single-file exe + bundled Core sidecar), the four license
  ; files + LICENSE_AUDIT.md, install/uninstall/migrate scripts, UPGRADE.md/MANUAL_VERIFY.md,
  ; VERSION.json and package-manifest.json.
  File /r "${STAGE_DIR}\*.*"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  FileWrite $InstallLog "payload_copied_from=${STAGE_DIR}$\r$\n"
  FileWrite $InstallLog "payload_copied_to=$INSTDIR$\r$\n"

  ; Start Menu shortcuts (per-user context; no desktop shortcut by default).
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\app\${APP_EXE}" "" "$INSTDIR\app\${APP_EXE}" 0
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\卸载 ${APP_NAME}.lnk" "$INSTDIR\Uninstall.exe"
  FileWrite $InstallLog "shortcut=$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk$\r$\n"

  ; HKCU uninstall entry (per-user; no HKLM writes anywhere in this script).
  WriteRegStr HKCU "${UNINST_KEY}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKCU "${UNINST_KEY}" "DisplayVersion" "${VERSION}"
  WriteRegStr HKCU "${UNINST_KEY}" "Publisher" "${APP_PUBLISHER}"
  WriteRegStr HKCU "${UNINST_KEY}" "URLInfoAbout" "${APP_URL}"
  WriteRegStr HKCU "${UNINST_KEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKCU "${UNINST_KEY}" "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegStr HKCU "${UNINST_KEY}" "QuietUninstallString" '"$INSTDIR\Uninstall.exe" /S'
  WriteRegStr HKCU "${UNINST_KEY}" "DisplayIcon" "$INSTDIR\app\${APP_EXE}"
  WriteRegDWORD HKCU "${UNINST_KEY}" "NoModify" 1
  WriteRegDWORD HKCU "${UNINST_KEY}" "NoRepair" 1
  WriteRegDWORD HKCU "${UNINST_KEY}" "EstimatedSize" ${INSTALL_SIZE_KB}
  WriteRegStr HKCU "${APP_REG_KEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKCU "${APP_REG_KEY}" "Version" "${VERSION}"
  FileWrite $InstallLog "registry=HKCU\${UNINST_KEY}$\r$\n"
  FileWrite $InstallLog "install_complete=1$\r$\n"
  FileClose $InstallLog
SectionEnd

; ---- uninstall ---------------------------------------------------------------
Section "Uninstall"
  SetShellVarContext current

  FileOpen $UninstallLog "${UNINSTALL_LOG}" w
  FileWrite $UninstallLog "NewManga uninstaller ${VERSION}$\r$\n"
  FileWrite $UninstallLog "install_dir=$INSTDIR$\r$\n"
  FileWrite $UninstallLog "data_root_preserved=%APPDATA%\com.newmanga.desktop$\r$\n"

  ; Remove exactly what the installer owns: shortcuts, HKCU entries, install directory.
  ; %APPDATA%\com.newmanga.desktop is deliberately absent from this section.
  Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}\卸载 ${APP_NAME}.lnk"
  RMDir "$SMPROGRAMS\${APP_NAME}"
  FileWrite $UninstallLog "shortcuts_removed=1$\r$\n"

  DeleteRegKey HKCU "${UNINST_KEY}"
  DeleteRegKey HKCU "${APP_REG_KEY}"
  FileWrite $UninstallLog "registry_removed=HKCU\${UNINST_KEY}$\r$\n"

  RMDir /r "$INSTDIR\app"
  Delete "$INSTDIR\*.md"
  Delete "$INSTDIR\*.txt"
  Delete "$INSTDIR\*.ps1"
  Delete "$INSTDIR\*.json"
  Delete "$INSTDIR\LICENSE"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir /r "$INSTDIR"
  FileWrite $UninstallLog "install_dir_removed=1$\r$\n"
  FileWrite $UninstallLog "uninstall_complete=1$\r$\n"
  FileClose $UninstallLog
SectionEnd

Function .onInit
  SetShellVarContext current
FunctionEnd

Function un.onInit
  SetShellVarContext current
FunctionEnd
