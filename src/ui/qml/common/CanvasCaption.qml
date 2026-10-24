import QtQuick
import QtQuick.Controls
import "../theme"

// Anything that must be legible over the viewer/reader canvas sits on a panel
// pill: ui-reference .vfloat floats viewer chrome as background:var(--bg-panel),
// and no ink-* token reaches 4.5:1 on bg-canvas in both modes (bg-canvas is a
// dark surface in light mode too). Text keeps an audited ground.
Rectangle {
    id: caption

    property alias text: label.text

    color: Tokens.bgPanel
    border.color: Tokens.border
    radius: Tokens.radSm
    width: label.implicitWidth + Tokens.gap
    height: label.implicitHeight + Tokens.gap / 2

    Label {
        id: label
        anchors.centerIn: parent
        color: Tokens.ink2
        font.pixelSize: Tokens.fsSm
    }
}
