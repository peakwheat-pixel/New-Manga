import QtQuick
import QtQuick.Controls
import "shell"

// TASK-030: entry window only — it mounts shell/AppShell.qml (TASK-012);
// every page, the navigation rail and all behavior live there. No business
// logic here (D05 §60). Context properties navigationViewModel and
// bookshelfViewModel are injected by bootstrap.app before this file loads.
ApplicationWindow {
    visible: true
    width: 1280
    height: 800
    title: "New Manga"

    AppShell {
        anchors.fill: parent
    }
}
