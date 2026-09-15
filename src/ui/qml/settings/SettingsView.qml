import QtQuick
import QtQuick.Controls

// D05 §43.1 SettingsView: the settings page is top-level; inside, a fixed
// left category list (no sub-routes) and a content pane on the right.
// Actual settings content arrives with TASK-009/022 wiring.
Rectangle {
    id: settings
    objectName: "settingsView"
    color: "#f5f5f4"

    ListModel {
        id: categoryModel
        ListElement { name: "Provider" }
        ListElement { name: "网络 / 代理" }
        ListElement { name: "OCR" }
        ListElement { name: "翻译" }
        ListElement { name: "图片修复" }
        ListElement { name: "排版样式" }
        ListElement { name: "模型 / GPU" }
        ListElement { name: "任务 / 并发" }
        ListElement { name: "缓存 / Revision" }
        ListElement { name: "回收站" }
        ListElement { name: "备份 / 恢复" }
        ListElement { name: "Plugin / Hooks" }
    }

    Rectangle {
        id: categoryPane
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.margins: 8
        width: 180
        color: "#ffffff"
        border.color: "#d9d9d6"
        radius: 6

        ListView {
            id: categoryList
            objectName: "settingsCategoryList"
            anchors.fill: parent
            anchors.margins: 4
            clip: true
            model: categoryModel
            delegate: ItemDelegate {
                width: ListView.view.width
                text: model.name
                highlighted: ListView.isCurrentItem
                onClicked: categoryList.currentIndex = index
            }
        }
    }

    Rectangle {
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: categoryPane.right
        anchors.right: parent.right
        anchors.margins: 8
        anchors.leftMargin: 0
        color: "#ffffff"
        border.color: "#d9d9d6"
        radius: 6

        Label {
            anchors.centerIn: parent
            text: "设置项将在后续切片接入"
            color: "#6b7280"
        }
    }
}
