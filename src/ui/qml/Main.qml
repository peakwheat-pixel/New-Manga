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
    // REPAIR-13 R13-AC3: the native Windows Quick Controls style ignores
    // palette.button and QML background customization (Build 3 Sandbox
    // screenshots: light system surfaces), while palette.buttonText *is*
    // honored — it previously painted the light `ink` text onto those
    // light surfaces, leaving button labels unreadable on all four pages.
    // `ink-inv` is the F token for text on inverted (light) surfaces, so
    // native-styled buttons render dark-on-light and stay readable while
    // the Graphite Atelier dark surfaces around them are unchanged.
    // (QStyleHints.colorScheme was probed as a fix and does not affect the
    // native style — verification/T3.2.1/repair-13/probe-ui-states.*.log.)
    palette.buttonText: Tokens.inkInv
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
