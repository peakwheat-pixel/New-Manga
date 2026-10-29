import QtQuick
import QtQuick.Controls
import "../theme"

// D05 §62 empty state: title + optional description + action buttons
// provided by the user of this component (default property).
Column {
    id: root
    property string title: ""
    property string description: ""
    default property alias actions: actionsRow.data

    spacing: Tokens.gap

    Label {
        anchors.horizontalCenter: parent.horizontalCenter
        text: root.title
        font.pixelSize: Tokens.fsSub
        font.weight: Font.DemiBold
        color: Tokens.ink
    }
    Label {
        anchors.horizontalCenter: parent.horizontalCenter
        visible: root.description !== ""
        text: root.description
        color: Tokens.ink3
        font.pixelSize: Tokens.fsSm
    }
    Row {
        id: actionsRow
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: Tokens.gap
    }
}
