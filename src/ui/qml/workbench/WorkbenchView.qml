import QtQuick
import QtQuick.Controls
import "../common"

// D05 §15/§16 WorkbenchView is a TASK-013 slice; this stage delivers the
// skeleton with the D05 §62 workbench empty state only. The action stays
// disabled because the selection floating window does not exist yet.
Rectangle {
    id: workbench
    objectName: "workbenchView"
    color: "#f5f5f4"

    EmptyState {
        anchors.centerIn: parent
        title: "尚未选择作品 / 章节"
        description: "翻译、OCR、Region 编辑与任务进度将在工作台提供"
        Button {
            objectName: "workbenchPickContext"
            text: "选择作品和章节"
            enabled: false  // 选择悬浮窗属 TASK-013
        }
    }
}
