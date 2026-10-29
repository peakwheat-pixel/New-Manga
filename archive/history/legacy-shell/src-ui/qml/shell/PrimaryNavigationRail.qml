import QtQuick
import QtQuick.Controls
import "../theme"

// D05 §3.1 primary navigation rail: exactly four sibling entries, the
// bookshelf selected at startup. Switching pages never destroys views —
// AppShell keeps every page alive (AC-NAV-003).
Rectangle {
    id: rail
    objectName: "navRail"
    color: Tokens.bgRail

    Column {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 6
        spacing: 4

        Repeater {
            model: navigationViewModel.pages

            // pages is a QVariantList: delegates see `modelData`, not named roles.
            delegate: Button {
                id: navButton
                objectName: "nav-" + modelData.id
                width: parent.width
                text: modelData.label
                checkable: true
                checked: navigationViewModel.currentPage === modelData.id
                focus: modelData.id === "bookshelf"
                onClicked: navigationViewModel.navigate(modelData.id)

                // D05 §3.1: workbench badge shows task state (placeholder
                // until TASK-011 pipelines exist; never cleared by switching).
                NavBadge {
                    visible: modelData.id === "workbench" && navigationViewModel.workbenchRunning
                    text: navigationViewModel.workbenchBadge
                    anchors.top: parent.top
                    anchors.right: parent.right
                    anchors.margins: 2
                }
            }
        }
    }
}
