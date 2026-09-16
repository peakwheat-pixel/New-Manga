import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// D05 §31/§32/§33 + D06 §102/§103: the fixed bottom TaskProgressPanel.
// Fixed in the workbench layout (AC-PROGRESS-001) — never a popup. All
// fields come from the shared task projection via workbenchViewModel
// (AC-PROGRESS-007); the panel infers nothing about step success.
Rectangle {
    id: panel
    objectName: "taskProgressPanel"
    color: "#ffffff"

    // Bound by WorkbenchView to the viewmodel's taskProgress map.
    property var progress: ({})
    property bool hasRun: progress.run_id !== undefined && progress.run_id !== ""

    signal pauseClicked()
    signal stopClicked()
    signal continueClicked()
    signal restartClicked()
    signal abandonClicked()
    signal retryFailedClicked()
    signal statisticClicked(string status)
    signal locateCurrentClicked()
    signal viewReasonClicked()

    // D05 §33: collapsed compact strip ↔ expanded layout.
    property bool expanded: true

    implicitHeight: expanded ? 132 : 40

    function statusColor(status) {
        return {
            waiting: "#9ca3af",
            processing: "#2563eb",
            completed: "#16a34a",
            failed: "#dc2626",
            skipped: "#a855f7",
            blocked: "#d97706"
        }[status] || "#9ca3af";
    }

    function statusGlyph(status) {
        return {
            waiting: "○",
            processing: "●",
            completed: "✓",
            failed: "!",
            skipped: "↷",
            blocked: "⏸"
        }[status] || "○";
    }

    // D05 §62 Task 无运行任务: an honest "no running task" line.
    Label {
        anchors.centerIn: parent
        visible: !panel.hasRun
        objectName: "taskProgressEmpty"
        text: "当前无运行任务"
        color: "#6b7280"
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 4
        visible: panel.hasRun

        // Collapsed strip (D05 §33): name · percent · current page ·
        // current step · status · controls stay reachable.
        RowLayout {
            Layout.fillWidth: true
            visible: !panel.expanded
            spacing: 8
            Label { text: panel.progress.run_title || ""; Layout.fillWidth: true; elide: Text.ElideRight }
            Label { objectName: "taskProgressPercentCompact"; text: (panel.progress.progress_percent || 0) + "%" }
            Label { text: panel.progress.current_page_name ? ("当前 " + panel.progress.current_page_name) : "" }
            Label { objectName: "taskProgressStatusCompact"; text: panel.progress.run_status || "" }
        }

        // Expanded header: title + percent + expand/collapse toggle.
        RowLayout {
            Layout.fillWidth: true
            visible: panel.expanded
            spacing: 8
            Label {
                objectName: "taskProgressTitle"
                text: panel.progress.run_title || ""
                font.bold: true
                Layout.fillWidth: true
                elide: Text.ElideRight
            }
            Label {
                objectName: "taskProgressStatus"
                text: panel.statusLabel(panel.progress)
            }
            Label {
                objectName: "taskProgressPercent"
                text: (panel.progress.progress_percent || 0) + "%"
                font.bold: true
            }
            Button {
                objectName: "taskProgressToggle"
                flat: true
                text: panel.expanded ? "折叠" : "展开"
                onClicked: panel.expanded = !panel.expanded
            }
        }

        // Step flow strip (D05 §31.2): 检测 ✓ → OCR ● → 修复 ○ …
        RowLayout {
            Layout.fillWidth: true
            visible: panel.expanded
            spacing: 6
            Repeater {
                model: panel.progress.step_flow || []
                RowLayout {
                    spacing: 2
                    Label { text: modelData.label || modelData.type; color: "#374151" }
                    Label {
                        text: panel.statusGlyph(
                            modelData.state === "running" ? "processing"
                            : modelData.state === "completed" ? "completed"
                            : modelData.state === "failed" ? "failed"
                            : modelData.state === "skipped" ? "skipped" : "waiting")
                        color: panel.statusColor(
                            modelData.state === "running" ? "processing"
                            : modelData.state === "completed" ? "completed"
                            : modelData.state === "failed" ? "failed"
                            : modelData.state === "skipped" ? "skipped" : "waiting")
                    }
                    Label { text: "→"; visible: index < (panel.progress.step_flow || []).length - 1; color: "#d1d5db" }
                }
            }
        }

        // Current page + statistics row (clickable, AC-PROGRESS-003/004/005).
        RowLayout {
            Layout.fillWidth: true
            visible: panel.expanded
            spacing: 12
            Label { text: "当前页：" }
            Button {
                objectName: "taskProgressCurrentPage"
                flat: true
                text: (panel.progress.current_page_name || "—")
                      + (panel.progress.current_step_label
                         ? "　" + panel.progress.current_step_label : "")
                enabled: (panel.progress.current_page_id || "") !== ""
                onClicked: panel.locateCurrentClicked()
            }
            Item { Layout.fillWidth: true }
            Button { objectName: "statCompleted"; flat: true; text: "完成 " + (panel.progress.completed_page_count || 0); onClicked: panel.statisticClicked("completed") }
            Button { objectName: "statFailed"; flat: true; text: "失败 " + (panel.progress.failed_page_count || 0); onClicked: panel.statisticClicked("failed") }
            Button { objectName: "statBlocked"; flat: true; text: "阻塞 " + (panel.progress.blocked_page_count || 0); onClicked: panel.viewReasonClicked() }
            Button { objectName: "statSkipped"; flat: true; text: "跳过 " + (panel.progress.skipped_page_count || 0); onClicked: panel.statisticClicked("skipped") }
            Button { objectName: "statWaiting"; flat: true; text: "等待 " + (panel.progress.waiting_page_count || 0); onClicked: panel.statisticClicked("all") }
        }

        // Control row: D06 §103 enablement comes entirely from the
        // projection; “正在暂停” is the optimistic AC-PAUSE-001 feedback.
        RowLayout {
            Layout.fillWidth: true
            spacing: 8
            Button {
                objectName: "btnPauseRun"
                text: panel.progress.pausing ? "正在暂停…" : "暂停"
                enabled: panel.progress.can_pause === true
                onClicked: panel.pauseClicked()
            }
            Button {
                objectName: "btnStopRun"
                text: "停止"
                enabled: panel.progress.can_stop === true
                onClicked: panel.stopClicked()
            }
            Button {
                objectName: "btnContinueRun"
                text: "继续"
                enabled: panel.progress.can_continue === true
                onClicked: panel.continueClicked()
            }
            Button {
                objectName: "btnRestartRun"
                text: "重新开始"
                visible: panel.progress.can_restart === true
                onClicked: panel.restartClicked()
            }
            Button {
                objectName: "btnAbandonRun"
                text: "放弃"
                visible: panel.progress.can_abandon === true
                onClicked: panel.abandonClicked()
            }
            Button {
                objectName: "btnRetryFailed"
                text: "重试失败页"
                visible: panel.progress.can_retry_failed === true
                onClicked: panel.retryFailedClicked()
            }
            Label {
                objectName: "taskProgressBlockedReason"
                visible: (panel.progress.blocked_reasons || []).length > 0
                text: "阻塞原因：" + (panel.progress.blocked_reasons || []).join("、")
                color: "#d97706"
                elide: Text.ElideRight
                Layout.fillWidth: true
            }
            Item { Layout.fillWidth: !panel.progress.blocked_reasons }
        }
    }

    function statusLabel(progress) {
        switch (progress.run_status) {
        case "pending": return "等待";
        case "running": return progress.pausing ? "正在暂停" : "运行中";
        case "paused": return "已暂停";
        case "blocked": return "已阻塞";
        case "completed": return "已完成";
        case "completed_with_failures": return "已完成（有失败）";
        case "failed": return "失败";
        case "cancelled": return "已停止";
        case "interrupted": return "已中断";
        default: return progress.run_status || "";
        }
    }
}
