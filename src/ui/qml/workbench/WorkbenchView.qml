import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../common"

// D05 §15/§16 workbench: fixed Toolbar / PageList / Viewer / Inspector /
// bottom TaskProgressPanel, all simultaneously live (TASK-013 AC 1).
//
// The viewmodel arrives as the ``workbenchViewModel`` context property.
// Without it (shell-level tests, unbootstrapped embedding) this page stays
// the honest D05 §62 empty state with the pick action disabled — the same
// surface TASK-012 shipped. QML holds no business logic (D05 §60): every
// state read/write below delegates to the viewmodel; the ``w*`` aliases
// keep the no-viewmodel case a defined value instead of a null deref.
Rectangle {
    id: workbench
    objectName: "workbenchView"
    color: "#f5f5f4"

    property var vm: (typeof workbenchViewModel !== "undefined"
                      && workbenchViewModel !== null) ? workbenchViewModel : null
    property bool hasContext: vm !== null && vm.hasContext

    // guarded aliases (no-viewmodel → neutral values)
    property var wCtx: vm !== null ? vm.contextInfo
                                   : { book_title: "", chapter_title: "" }
    property string wViewerPageId: vm !== null ? vm.viewerPageId : ""
    property string wViewerMode: vm !== null ? vm.viewerMode : "original"
    property string wViewerImage: vm !== null ? vm.viewerImageUrl : ""
    property string wViewerTranslated: vm !== null ? vm.viewerImageUrlFor("translated") : ""
    property string wViewerPageName: vm !== null ? vm.viewerPageName : ""
    property int wSelectedCount: vm !== null ? vm.selectedPageCount : 0
    property string wRunStatus: vm !== null ? vm.runStatus : "idle"
    property var wRegions: vm !== null ? vm.inspectorRegions : []
    property string wInspectorRegionId: vm !== null ? vm.inspectorRegionId : ""
    property string wInspectorText: vm !== null ? vm.inspectorText : ""
    property bool wDirty: vm !== null ? vm.hasDirtyEditor : false
    property var wProgress: vm !== null ? vm.taskProgress : {}
    property var wPageModel: vm !== null ? vm.pageListModel : null
    property string wCommandError: vm !== null ? vm.commandErrorText : ""

    // “选择作品和章节” uses a floating window per D05 §62; the picker is
    // part of the shelf→workbench assembly slice, so the entry stays
    // disabled here until a context is set programmatically.
    EmptyState {
        anchors.centerIn: parent
        visible: !workbench.hasContext
        title: "尚未选择作品 / 章节"
        description: "翻译、OCR、Region 编辑与任务进度将在工作台提供"
        Button {
            objectName: "workbenchPickContext"
            text: "选择作品和章节"
            enabled: workbench.hasContext  // disabled without context
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        visible: workbench.hasContext

        WorkbenchToolbar {
            objectName: "workbenchToolbarHost"
            Layout.fillWidth: true
            bookTitle: workbench.wCtx.book_title
            chapterTitle: workbench.wCtx.chapter_title
            viewerMode: workbench.wViewerMode
            hasSelection: workbench.wSelectedCount > 0
            runActive: workbench.wRunStatus === "running"
                       || workbench.wRunStatus === "pending"

            onPreviousPageClicked: workbench.stepPage(-1)
            onNextPageClicked: workbench.stepPage(1)
            onViewerModeClicked: function(mode) { workbench.vm.setViewerMode(mode) }
            onTranslateAllClicked: workbench.vm.startTranslateAll()
            onTranslateUntranslatedClicked: workbench.vm.startTranslateUntranslated()
            onTranslateSelectedClicked: workbench.vm.startTranslateSelected()
        }

        // TASK-052 (PROVISIONAL): minimal non-blocking failure surface.
        // Smallest visible element that makes commandError reachable by the
        // user (text + copy + dismiss); the TASK-047 design gate owns the
        // final visual language and information hierarchy.
        Rectangle {
            objectName: "commandErrorBar"
            visible: workbench.wCommandError !== ""
            Layout.fillWidth: true
            Layout.preferredHeight: visible ? 32 : 0
            color: "#fef2f2"
            border.color: "#dc2626"

            TextEdit {
                id: commandErrorCopyHelper
                visible: false
                width: 0
                height: 0
            }
            Label {
                objectName: "commandErrorText"
                anchors.left: parent.left
                anchors.leftMargin: 8
                anchors.right: commandErrorCopyButton.left
                anchors.rightMargin: 8
                anchors.verticalCenter: parent.verticalCenter
                text: workbench.wCommandError
                elide: Text.ElideRight
                color: "#991b1b"
            }
            Button {
                id: commandErrorCopyButton
                objectName: "commandErrorCopyButton"
                anchors.right: commandErrorCloseButton.left
                anchors.rightMargin: 4
                anchors.verticalCenter: parent.verticalCenter
                text: "复制"
                onClicked: {
                    commandErrorCopyHelper.text = workbench.wCommandError
                    commandErrorCopyHelper.selectAll()
                    commandErrorCopyHelper.copy()
                }
            }
            Button {
                id: commandErrorCloseButton
                objectName: "commandErrorCloseButton"
                anchors.right: parent.right
                anchors.rightMargin: 4
                anchors.verticalCenter: parent.verticalCenter
                text: "×"
                onClicked: {
                    if (workbench.vm !== null) workbench.vm.clearCommandError()
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            PageListPanel {
                id: pageListPanel
                objectName: "pageListPanelHost"
                Layout.fillHeight: true
                pageModel: workbench.wPageModel
                viewerPageId: workbench.wViewerPageId

                onPageClicked: function(pageId) { workbench.vm.selectPage(pageId) }
                onPageCtrlClicked: function(pageId) { workbench.vm.togglePageSelected(pageId) }
                onPageShiftClicked: function(pageId) { workbench.vm.selectRangeTo(pageId) }

                Connections {
                    target: workbench.vm
                    function onPageLocateRequested(pageId) {
                        pageListPanel.locatePage(pageId)
                    }
                }
            }

            Rectangle { Layout.preferredWidth: 1; Layout.fillHeight: true; color: "#e7e5e4" }

            ViewerPanel {
                objectName: "viewerPanelHost"
                Layout.fillWidth: true
                Layout.fillHeight: true
                imageUrl: workbench.wViewerImage
                translatedUrl: workbench.wViewerTranslated
                pageName: workbench.wViewerPageName
                mode: workbench.wViewerMode
            }

            Rectangle { Layout.preferredWidth: 1; Layout.fillHeight: true; color: "#e7e5e4" }

            RegionInspector {
                objectName: "regionInspectorHost"
                Layout.fillHeight: true
                regions: workbench.wRegions
                selectedRegionId: workbench.wInspectorRegionId
                text: workbench.wInspectorText
                dirty: workbench.wDirty

                onRegionClicked: function(regionId) { workbench.vm.selectRegion(regionId) }
                onTextEdited: function(text) { workbench.vm.setInspectorText(text) }
                onSaveClicked: workbench.vm.saveInspector()
                onDiscardClicked: workbench.vm.discardInspector()
                onCommandClicked: function(commandType) {
                    workbench.vm.startRegionCommand(commandType)
                }
            }
        }

        Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 1; color: "#e7e5e4" }

        TaskProgressPanel {
            objectName: "taskProgressPanelHost"
            Layout.fillWidth: true
            progress: workbench.wProgress

            onPauseClicked: workbench.vm.pauseRun()
            onStopClicked: workbench.vm.stopRun()
            onContinueClicked: workbench.vm.continueRun()
            onRestartClicked: workbench.vm.restartRun()
            onAbandonClicked: workbench.vm.abandonRun()
            onRetryFailedClicked: workbench.vm.retryFailedPages()
            onStatisticClicked: function(status) { workbench.vm.filterByStatus(status) }
            onLocateCurrentClicked: workbench.vm.locatePipelinePage()
            onViewReasonClicked: workbench.vm.setPageFilter("all")
        }
    }

    DirtyConfirmDialog {
        id: dirtyDialog
        objectName: "dirtyConfirmDialogHost"
        anchors.centerIn: Overlay.overlay
        visible: false
        onDecision: function(action) {
            dirtyDialog.close()
            workbench.vm.resolveDirtyConfirm(action)
        }
    }

    Connections {
        target: workbench.vm
        ignoreUnknownSignals: true
        function onInspectorDirtyConfirmRequested(target) {
            dirtyDialog.open()
        }
    }

    // QML only forwards the toolbar action; page math stays in the ViewModel.
    function stepPage(delta) {
        if (workbench.vm !== null) workbench.vm.stepPage(delta);
    }
}
