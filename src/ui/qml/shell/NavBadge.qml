import QtQuick
import QtQuick.Controls
import "../theme"

// D05 §61 nav badge subset: workbench task-state pill. StatusBadge polish
// lands in TASK-022. (Was an inline `component` first, but the 6.11 engine
// rejected that syntax at parse time — a sibling file is equivalent.)
Rectangle {
    id: badge
    property string text: ""
    color: Tokens.stRun
    radius: Tokens.radSm
    width: badgeLabel.implicitWidth + 8
    height: badgeLabel.implicitHeight + 4

    Label {
        id: badgeLabel
        anchors.centerIn: parent
        text: badge.text
        color: Tokens.onAccent
        font.pixelSize: Tokens.fsSm
    }
}
