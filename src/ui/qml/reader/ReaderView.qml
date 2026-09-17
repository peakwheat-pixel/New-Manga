import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../common"
import "../windows"

// Reader page (TASK-015; D05 §37~42).
// Layout: primary nav rail lives in AppShell; this page is
// Reader Toolbar (§38) + Reader Nav (§41 progress) + Viewer (§39/§40).
//
// The ViewModel arrives as the `readerViewModel` context property. Like
// every page this file must stay loadable standalone (no context property
// in the assembly yet), so all controls no-op via `rv.hasChapter` until
// bootstrap publishes the real ViewModel (integration wiring is recorded
// in the TASK-015 handoff).
//
// RTL/LTR paging (D05 §39): on an RTL chapter the Left key and the left
// edge action advance (right→left reading); on LTR the Right key does.
// Webtoon (§40): vertical Flickable, width-fit image, throttled
// scroll_offset_y saves — full按宽滚动 acceptance is TASK-020's.
Rectangle {
    id: rv
    objectName: "readerView"
    color: "#f5f5f4"
    focus: true  // keyboard paging (D05 §39) needs active focus on this page

    property var model: (typeof readerViewModel !== "undefined" ? readerViewModel : null)
    readonly property bool active: model !== null && model.hasChapter
    readonly property bool vertical: active && model.chapterType === "webtoon"

    function progressText() {
        if (!active)
            return "";
        return model.pageNumber + " / " + model.pageCount + " 页 · " + Math.round(model.progressPercent) + "%"
    }

    Keys.onLeftPressed: (event) => {
        if (!active || vertical)
            return;
        if (model.direction === "rtl")
            model.nextPage();
        else
            model.previousPage();
        event.accepted = true;
    }
    Keys.onRightPressed: (event) => {
        if (!active || vertical)
            return;
        if (model.direction === "rtl")
            model.previousPage();
        else
            model.nextPage();
        event.accepted = true;
    }

    Component {
        id: exportWindowComponent
        ExportWindow {
            controller: rv.model ? rv.model.exportController : null
            Component.onCompleted: open()
            onVisibleChanged: if (!visible) destroy()
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 4

        // ---- Reader Toolbar (D05 §38) ----
        // RTL chapters (D05 §39 右→左): the toolbar mirrors, so "下一页"
        // sits on the physical left where RTL reading advances. Button
        // labels always name their own action (R-001).
        RowLayout {
            objectName: "readerToolbar"
            Layout.fillWidth: true
            Layout.margins: 8
            spacing: 8
            layoutDirection: active && model.direction === "rtl" ? Qt.RightToLeft : Qt.LeftToRight

            Label {
                objectName: "readerChapterTitle"
                text: active ? model.chapterTitle : "尚未选择阅读章节"
                font.bold: true
                Layout.preferredWidth: 220
                elide: Text.ElideRight
            }
            Button {
                objectName: "readerPickChapter"
                // D04 §33: chapters are entered from the shelf/workbench with
                // context; an in-reader chapter picker needs the chapter list
                // source, which the assembly wires (see TASK-015 handoff).
                // Disabled keeps the TASK-012 honest-skeleton contract.
                text: "章节…"
                enabled: false
            }
            Button {
                objectName: "readerModeOriginal"
                text: "Original"
                enabled: active
                highlighted: active && model.mode === "original"
                onClicked: model.setMode("original")
            }
            Button {
                objectName: "readerModeTranslated"
                text: "Translated"
                enabled: active
                highlighted: active && model.mode === "translated"
                onClicked: model.setMode("translated")
            }
            Button {
                objectName: "readerPreviousPage"
                text: "◀ 上一页"
                enabled: active && model.canGoPrevious
                onClicked: model.previousPage()
            }
            Button {
                objectName: "readerNextPage"
                text: model && model.direction === "rtl" ? "▶ 下一页" : "下一页 ▶"
                enabled: active && model.canGoNext
                onClicked: model.nextPage()
            }
            Button {
                objectName: "readerContinueLast"
                text: "继续上次位置"
                enabled: active
                onClicked: model.continueReading()
            }
            Button {
                objectName: "readerRestart"
                text: "从开头开始"
                enabled: active
                onClicked: model.restartFromBeginning()
            }
            Item { Layout.fillWidth: true }
            Label {
                objectName: "readerProgress"
                text: progressText()
                visible: active
            }
            Button {
                objectName: "readerExportButton"
                text: "导出…"
                enabled: active
                onClicked: {
                    if (model.openExporter() !== null)
                        exportWindowComponent.createObject(rv)
                }
            }
        }

        // ---- missing translated / stale banner ----
        Label {
            objectName: "readerStatusBanner"
            Layout.fillWidth: true
            Layout.leftMargin: 8
            text: active ? model.statusMessage : ""
            color: "#9a3412"
            visible: text !== ""
            wrapMode: Text.WordWrap
        }

        // ---- progress detail (D05 §41) ----
        Label {
            objectName: "readerSummary"
            Layout.fillWidth: true
            Layout.leftMargin: 8
            visible: active && model.bookSummary.has_progress
            text: active && model.bookSummary.has_progress
                  ? "最后阅读 " + model.bookSummary.last_read_at + " · 累计 " + Math.round(model.totalReadSeconds) + " 秒"
                  : ""
            color: "#57534e"
        }

        // ---- Viewer (D05 §39 paged / §40 webtoon) ----
        Loader {
            objectName: "readerViewerHost"
            Layout.fillWidth: true
            Layout.fillHeight: true
            sourceComponent: rv.vertical ? webtoonViewer : pagedViewer
        }

        Component {
            id: pagedViewer
            Rectangle {
                color: "#1c1917"
                Image {
                    objectName: "readerPage"
                    anchors.centerIn: parent
                    source: active ? model.sourcePath : ""
                    fillMode: Image.PreserveAspectFit
                    asynchronous: true
                    width: parent.width
                    height: parent.height
                }
            }
        }

        Component {
            id: webtoonViewer
            // 按宽适配、高度自然延伸、纵向滚动（D05 §40；禁止按固定高度压缩）。
            // TASK-020: when the assembly injects a tile factory the page is
            // served as rebuildable tile bands (按需解码 + 预取限制); without
            // one the whole-page image path below is unchanged.
            Flickable {
                id: webtoonScroll
                objectName: "readerWebtoonScroll"
                clip: true
                contentWidth: width
                contentHeight: tilesHost.visible
                    ? tilesHost.childrenRect.height
                    : webtoonImage.paintedHeight
                boundsBehavior: Flickable.StopAtBounds

                // Tile geometry is known immediately (no decode round-trip),
                // so the saved offset restores as soon as the tiled host is
                // live; the whole-image path keeps its R-003 decode wait.
                onVisibleChanged: if (visible) Qt.callLater(restoreSavedOffset)
                onWidthChanged: if (visible) Qt.callLater(restoreSavedOffset)
                Component.onCompleted: Qt.callLater(restoreSavedOffset)

                function restoreSavedOffset() {
                    if (tilesHost.visible && active && model.scrollOffsetY > 0)
                        webtoonScroll.contentY = model.scrollOffsetY
                }

                Timer {
                    id: scrollSaveTimer
                    interval: 500
                    onTriggered: if (active) model.saveScrollOffset(webtoonScroll.contentY)
                }
                onContentYChanged: {
                    scrollSaveTimer.restart()
                    if (tilesHost.visible)
                        model.requestTiles(webtoonScroll.contentY,
                                           webtoonScroll.contentY + webtoonScroll.height)
                }

                Column {
                    id: tilesHost
                    visible: active && model.tilesActive
                    width: parent.width

                    Repeater {
                        model: visible ? model.tiles : []
                        delegate: Image {
                            required property var modelData
                            source: modelData.url
                            width: tilesHost.width
                            height: modelData.pageWidth > 0
                                ? modelData.height * tilesHost.width / modelData.pageWidth
                                : 0
                            fillMode: Image.PreserveAspectFit
                            asynchronous: true
                        }
                    }
                }

                Image {
                    id: webtoonImage
                    objectName: "readerPage"
                    visible: !tilesHost.visible
                    width: parent.width
                    fillMode: Image.PreserveAspectFit
                    horizontalAlignment: Image.AlignHCenter
                    source: active && !tilesHost.visible ? model.sourcePath : ""
                    asynchronous: true
                    // R-003: restore the saved offset only after the async
                    // image has real content height, or the Flickable clamps
                    // it back to 0.
                    onStatusChanged: {
                        if (status === Image.Ready && active && model.scrollOffsetY > 0)
                            webtoonScroll.contentY = model.scrollOffsetY
                    }
                }
            }
        }
    }

    // Standalone-load empty state (no ViewModel injected yet).
    EmptyState {
        objectName: "readerEmptyState"
        anchors.centerIn: parent
        visible: !active
        title: "尚未选择阅读章节"
        description: "在书架中选择作品后进入阅读"
    }
}
