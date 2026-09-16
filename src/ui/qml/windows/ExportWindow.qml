import QtQuick
import QtQuick.Controls

Window {
    id: exportWindow
    objectName: "exportWindow"
    title: "导出成果"
    width: 520
    height: 360
    modality: Qt.ApplicationModal

    Column {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 12
        Label { text: "范围、顺序、输出路径和覆盖策略由导出请求确定"; wrapMode: Text.WordWrap }
        ComboBox { id: format; objectName: "exportFormat"; model: ["png", "zip", "cbz", "pdf", "txt"] }
        CheckBox { id: overwrite; objectName: "exportOverwrite"; text: "覆盖已有目标文件" }
        Label { text: exportViewModel.statusMessage; color: "#9a3412"; visible: text !== "" }
        Button { text: "导出"; onClicked: exportViewModel.export(format.currentText, "") }
    }
}
