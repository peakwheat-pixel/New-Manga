import QtQuick
import QtQuick.Controls
import "../bookshelf"
import "../workbench"
import "../reader"
import "../settings"

// D05 §3.1 App Shell: fixed primary navigation rail on the left, current
// top-level page on the right. All four pages stay instantiated — only
// visibility changes — so Book/Chapter/Page context survives switches
// (AC-NAV-003) and a running pipeline would keep running (D05 §3.1).
//
// Consumes context properties `navigationViewModel` and
// `bookshelfViewModel`, registered by the Python assembly (bootstrap).
// Main.qml wiring itself is a registered scope change (TASK-012 task
// file) — this file is fully loadable standalone, which tests exercise.
Item {
    id: root
    objectName: "appShell"

    PrimaryNavigationRail {
        id: rail
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        width: 64
    }

    Item {
        id: pageHost
        objectName: "pageHost"
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: rail.right
        anchors.right: parent.right

        BookshelfView {
            objectName: "page-bookshelf"
            anchors.fill: parent
            visible: navigationViewModel.currentPage === "bookshelf"
        }
        WorkbenchView {
            objectName: "page-workbench"
            anchors.fill: parent
            visible: navigationViewModel.currentPage === "workbench"
        }
        ReaderView {
            objectName: "page-reader"
            anchors.fill: parent
            visible: navigationViewModel.currentPage === "reader"
        }
        SettingsView {
            objectName: "page-settings"
            anchors.fill: parent
            visible: navigationViewModel.currentPage === "settings"
        }
    }
}
