import QtQuick
import QtQuick.Controls

// D05 §62 empty state: title + optional description + action buttons
// provided by the user of this component (default property).
Column {
    id: root
    property string title: ""
    property string description: ""
    default property alias actions: actionsRow.data

    spacing: 12

    Label {
        anchors.horizontalCenter: parent.horizontalCenter
        text: root.title
        font.pixelSize: 18
        font.weight: Font.DemiBold
        color: "#1f2328"
    }
    Label {
        anchors.horizontalCenter: parent.horizontalCenter
        visible: root.description !== ""
        text: root.description
        color: "#6b7280"
    }
    Row {
        id: actionsRow
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 8
    }
}
