import QtQuick
import QtQuick.Controls

// D05 §55 dirty navigation guard dialog: 保存 / 放弃 / 取消 — the QML face
// of WorkbenchViewModel.inspectorDirtyConfirmRequested; the decision is
// routed back through resolveDirtyConfirm(action).
Dialog {
    id: dialog
    objectName: "dirtyConfirmDialog"
    modal: true
    title: "有未保存的修改"
    standardButtons: Dialog.NoButton
    closePolicy: Popup.NoAutoClose

    signal decision(string action)

    Label {
        width: parent.width
        text: "Inspector 的修改尚未保存。切换前要保存吗？"
        wrapMode: Text.Wrap
    }

    footer: DialogButtonBox {
        Button {
            objectName: "dirtySave"
            text: "保存"
            onClicked: dialog.decision("save")
        }
        Button {
            objectName: "dirtyDiscard"
            text: "放弃"
            onClicked: dialog.decision("discard")
        }
        Button {
            objectName: "dirtyCancel"
            text: "取消"
            onClicked: dialog.decision("cancel")
        }
    }
}
