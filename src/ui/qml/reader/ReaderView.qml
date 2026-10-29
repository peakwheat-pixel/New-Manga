import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../common"
import "../theme"
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
    color: Tokens.bgPage
    focus: true  // keyboard paging (D05 §39) needs active focus on this page

    property var model: (typeof readerViewModel !== "undefined" ? readerViewModel : null)
    property var shelf: (typeof bookshelfViewModel !== "undefined" ? bookshelfViewModel : null)
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
            // F-13-2: ExportWindow's root is a Window, not a Popup — `open()`
            // does not exist on it and threw `ReferenceError` on every export
            // click, so the window was created but never shown.
            Component.onCompleted: show()
            onVisibleChanged: if (!visible) destroy()
        }
    }

    ChapterPicker {
        id: readerChapterPicker
        shelf: rv.shelf
        action: "reader"
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
                text: "章节…"
                enabled: rv.shelf !== null && rv.shelf.bookCount > 0
                Accessible.name: "选择阅读章节"
                onClicked: readerChapterPicker.open()
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
                // F-5 (TASK-045): the toolbar is gated on the vertical viewer
                // exactly like the keyboard above — a webtoon chapter scrolls,
                // it does not page (the tile band is rebuilt on every page
                // turn, so an ungated button would swap pixels under the user).
                enabled: active && !vertical && model.canGoPrevious
                onClicked: model.previousPage()
            }
            Button {
                objectName: "readerNextPage"
                text: model && model.direction === "rtl" ? "▶ 下一页" : "下一页 ▶"
                enabled: active && !vertical && model.canGoNext
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
            color: Tokens.stWarnT
            font.pixelSize: Tokens.fsSm
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
            color: Tokens.ink3
            font.pixelSize: Tokens.fsSm
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
                color: Tokens.bgCanvas
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
            Rectangle {
                objectName: "readerWebtoonCanvas"
                color: Tokens.bgCanvas

                Flickable {
                    id: webtoonScroll
                    objectName: "readerWebtoonScroll"
                    anchors.fill: parent
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

                // F-11 (TASK-045): contentY/height are **display** pixels while
                // the tile grid speaks **page** pixels, so the host passes the
                // ratio (display per page pixel). The tiles are drawn at
                // tilesHost.width, so the scale is host width / page width.
                    function tileScale() {
                        if (!active || !model.pagePixelWidth || tilesHost.width <= 0)
                            return 1.0;
                        return tilesHost.width / model.pagePixelWidth;
                    }

                    onContentYChanged: {
                        scrollSaveTimer.restart()
                        if (tilesHost.visible)
                            model.requestTiles(webtoonScroll.contentY,
                                               webtoonScroll.contentY + webtoonScroll.height,
                                               tileScale())
                    }

                    Column {
                        id: tilesHost
                        objectName: "readerTilesHost"
                        visible: active && model.tilesActive
                        width: parent.width

                        Repeater {
                        // F-5/R-003 (TASK-045): qualify both names. An
                        // unqualified `model` inside a Repeater resolves to the
                        // Repeater's own model property (`model.tiles` was
                        // undefined → no delegate was ever created) and an
                        // unqualified `visible` resolves to the Repeater's own
                        // visible (always true), so the intent is expressed on
                        // the host explicitly.
                            model: tilesHost.visible && rv.model ? rv.model.tiles : []
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
