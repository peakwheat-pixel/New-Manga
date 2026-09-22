import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import "../theme"

// Export window (TASK-015; D05 §51): 范围 / 格式 / 输出位置 / 渲染设置
// (content mode + stale policy) / 文件命名 / 覆盖策略, 导出 + 取消, and
// after-export 打开所在文件夹 / 再次导出.
//
// Reached from the reader, which passes its ready controller in via the
// `controller` property; when opened standalone the `exportViewModel`
// context property is used if published. Either way the window renders
// disabled instead of crashing without a controller.
Window {
    id: exportWindow
    objectName: "exportWindow"
    title: "导出成果"
    width: 560
    height: 480
    modality: Qt.ApplicationModal
    color: Tokens.bgPage
    // F ships dark by default, so the Controls that still draw with the
    // platform style have to read the same palette: Button, TextField and
    // Dialog take these roles, and every Label inherits windowText.
    palette.window: Tokens.bgPage
    palette.windowText: Tokens.ink
    palette.base: Tokens.bgInset
    palette.button: Tokens.bgRaised
    palette.buttonText: Tokens.ink
    palette.highlight: Tokens.accent
    palette.highlightedText: Tokens.onAccent
    palette.text: Tokens.ink
    palette.placeholderText: Tokens.ink3
    palette.toolTipBase: Tokens.bgPanel
    palette.toolTipText: Tokens.ink

    property var controller: (typeof exportViewModel !== "undefined" ? exportViewModel : null)
    readonly property bool ready: controller !== null && controller.pageCount > 0

    function syncFromController() {
        if (controller === null)
            return
        staleBanner.text = controller.staleWarningText
        staleBanner.visible = controller.staleWarningVisible
        statusLabel.text = controller.statusMessage
    }

    onControllerChanged: syncFromController()
    Component.onCompleted: {
        if (controller !== null)
            controller.refreshStaleWarning()
        syncFromController()
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 8

        GridLayout {
            columns: 2
            columnSpacing: 12
            rowSpacing: 8
            Layout.fillWidth: true

            Label { text: "范围" }
            Label {
                objectName: "exportScope"
                text: ready ? controller.scopeSummary : "没有可导出的页面"
                Layout.fillWidth: true
            }

            Label { text: "内容" }
            RowLayout {
                ComboBox {
                    objectName: "exportMode"
                    enabled: ready
                    textRole: "label"
                    valueRole: "value"
                    model: [
                        { value: "translated", label: "Translated（译图）" },
                        { value: "original", label: "Original（原图）" }
                    ]
                    currentIndex: 0
                    onActivated: if (controller !== null) controller.setMode(currentValue)
                    Component.onCompleted: currentIndex = indexOfValue(controller ? controller.mode : "translated")
                }
            }

            Label { text: "格式" }
            ComboBox {
                objectName: "exportFormat"
                enabled: ready
                textRole: "label"
                valueRole: "value"
                model: ready ? controller.formats : []
                Component.onCompleted: currentIndex = indexOfValue(controller ? controller.format : "zip")
                onActivated: {
                    if (controller !== null)
                        controller.setFormat(currentValue)
                    exportWindow.syncFromController()
                }
            }

            Label { text: "输出位置" }
            RowLayout {
                Layout.fillWidth: true
                TextField {
                    objectName: "exportOutputPath"
                    Layout.fillWidth: true
                    enabled: ready
                    text: ready ? controller.outputPath : ""
                    onEditingFinished: if (controller !== null) controller.setOutputPath(text)
                }
                Button {
                    text: "浏览…"
                    enabled: ready
                    onClicked: fileDialog.open()
                }
            }
            FileDialog {
                id: fileDialog
                fileMode: FileDialog.SaveFile
                nameFilters: ["导出文件 (*)"]
                onAccepted: {
                    if (controller !== null)
                        controller.setOutputPath(selectedFile.toString())
                    exportWindow.syncFromController()
                }
            }

            Label { text: "覆盖策略" }
            ComboBox {
                objectName: "exportOverwritePolicy"
                enabled: ready
                textRole: "label"
                valueRole: "value"
                model: [
                    { value: "overwrite", label: "覆盖已有目标文件" },
                    { value: "skip", label: "跳过（保留现有文件）" },
                    { value: "auto_rename", label: "自动改名（名称 (1)）" }
                ]
                Component.onCompleted: currentIndex = indexOfValue(controller ? controller.overwritePolicy : "overwrite")
                onActivated: if (controller !== null) controller.setOverwritePolicy(currentValue)
            }

            Label { text: "Stale 处理" }
            ComboBox {
                objectName: "exportStalePolicy"
                enabled: ready
                textRole: "label"
                valueRole: "value"
                model: [
                    { value: "abort", label: "提示并等待（先重新渲染）" },
                    { value: "continue", label: "继续导出现有版本" }
                ]
                Component.onCompleted: currentIndex = indexOfValue(controller ? controller.stalePolicy : "abort")
                onActivated: {
                    if (controller !== null)
                        controller.setStalePolicy(currentValue)
                    exportWindow.syncFromController()
                }
            }
        }

        // D06 §97 stale prompt — never silently pretend output is current.
        Label {
            id: staleBanner
            objectName: "exportStaleBanner"
            Layout.fillWidth: true
            color: Tokens.stWarnT
            font.pixelSize: Tokens.fsSm
            wrapMode: Text.WordWrap
            visible: false
        }

        Label {
            id: statusLabel
            objectName: "exportStatus"
            Layout.fillWidth: true
            color: Tokens.ink
            font.pixelSize: Tokens.fsSm
            wrapMode: Text.WordWrap
            visible: text !== ""
        }

        Item { Layout.fillHeight: true }

        RowLayout {
            Layout.alignment: Qt.AlignRight
            spacing: 8
            Button {
                objectName: "exportRunButton"
                text: controller !== null && controller.running ? "导出中…" : "导出"
                enabled: ready && controller !== null && !controller.running
                onClicked: {
                    if (controller !== null)
                        controller.setOutputPath(exportOutputPath.text)
                    if (controller !== null)
                        controller.startExport()
                    exportWindow.syncFromController()
                }
            }
            Button {
                objectName: "exportCancelButton"
                text: "取消导出"
                enabled: controller !== null && controller.running
                onClicked: if (controller !== null) controller.cancelExport()
            }
            Button {
                objectName: "exportOpenFolderButton"
                text: "打开所在文件夹"
                enabled: controller !== null && controller.history.length > 0
                onClicked: if (controller !== null) controller.openOutputFolder()
            }
            Button {
                objectName: "exportRepeatButton"
                text: "再次导出（相同设置）"
                enabled: controller !== null && controller.history.length > 0 && !controller.running
                onClicked: {
                    if (controller !== null && controller.history.length > 0)
                        controller.repeatExport(controller.history[0].export_id)
                    exportWindow.syncFromController()
                }
            }
            Button {
                objectName: "exportCloseButton"
                text: "关闭"
                onClicked: exportWindow.close()
            }
        }
    }

    Connections {
        target: controller
        function onChanged() { exportWindow.syncFromController() }
        function onExportFinished(summary) { exportWindow.syncFromController() }
        function onExportFailed(message) { exportWindow.syncFromController() }
    }
}
