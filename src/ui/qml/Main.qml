import QtQuick
import QtQuick.Controls
import "shell"
import "theme"

// TASK-030: entry window only — it mounts shell/AppShell.qml (TASK-012);
// every page, the navigation rail and all behavior live there. No business
// logic here (D05 §60). Context properties navigationViewModel and
// bookshelfViewModel are injected by bootstrap.app before this file loads.
ApplicationWindow {
    visible: true
    width: 1280
    height: 800
    title: "New Manga"
    color: Tokens.bgPage
    // F ships dark by default, so the Controls that still draw with the
    // platform style have to read the same palette: Button, TextField and
    // Dialog take these roles, and every Label inherits windowText.
    palette.window: Tokens.bgPage
    palette.windowText: Tokens.ink
    palette.base: Tokens.bgInset
    palette.button: Tokens.bgRaised
    palette.buttonText: Tokens.ink
    palette.highlight: Tokens.accent
    palette.highlightedText: Tokens.onAccent
    palette.text: Tokens.ink
    palette.placeholderText: Tokens.ink3
    palette.toolTipBase: Tokens.bgPanel
    palette.toolTipText: Tokens.ink


    AppShell {
        anchors.fill: parent
    }
}
