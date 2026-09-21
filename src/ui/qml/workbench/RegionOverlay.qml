import QtQuick
import QtQuick.Controls

// T1.1.2: draw text regions on the Original page and see the existing ones.
//
// Two hard rules, both load-bearing:
//  - the page extent comes from the viewmodel, never from Image.sourceSize,
//    so the constants used to draw a box are the constants used to store it.
//    Two copies of the letterbox arithmetic would eventually disagree, and
//    the failure is a box drawn at A that is clicked at B.
//  - only normalized (0..1) values cross to the viewmodel. Page-pixel rounding
//    and every geometry rejection belong to the Python converter, so QML
//    cannot invent a second set of rules (D05 §60).
Rectangle {
    id: overlay
    objectName: "regionOverlay"
    color: "transparent"

    property var vm: null
    property string drawingMode: "rect"          // "rect" | "polygon"
    property real pageW: vm ? vm.viewerPageWidth : 0
    property real pageH: vm ? vm.viewerPageHeight : 0

    // The same PreserveAspectFit fit the Image underneath computes, derived
    // from the same extent constants the converter is called with.
    readonly property real scale: (pageW > 0 && pageH > 0)
                                  ? Math.min(width / pageW, height / pageH) : 0
    readonly property real contentW: pageW * scale
    readonly property real contentH: pageH * scale
    readonly property real offsetX: (width - contentW) / 2
    readonly property real offsetY: (height - contentH) / 2

    // In-progress geometry is view state only: it is dropped, never persisted.
    property var draftPoints: []                 // normalized [nx, ny] pairs
    property point dragFrom: Qt.point(0, 0)
    property point dragTo: Qt.point(0, 0)
    property bool dragging: false

    // Position and extent must not share one helper: an extent scales, it is
    // not shifted by the letterbox offset.
    function toItemX(pageX) { return pageX * scale + offsetX; }
    function toItemY(pageY) { return pageY * scale + offsetY; }

    function toNormalized(mx, my) {
        if (scale <= 0) return null;
        var nx = (mx - offsetX) / contentW;
        var ny = (my - offsetY) / contentH;
        // A stroke that starts in the grey band is not a page location;
        // refuse it instead of clamping to a box hugging the page edge.
        if (nx < 0 || nx > 1 || ny < 0 || ny > 1) return null;
        return [nx, ny];
    }

    function cancelDraft() {
        draftPoints = [];
        dragging = false;
        canvas.requestPaint();
    }

    function commitPolygon() {
        if (overlay.vm && draftPoints.length >= 3)
            overlay.vm.createPolygon(JSON.stringify(draftPoints));
        cancelDraft();
    }

    Canvas {
        id: canvas
        anchors.fill: parent
        onPaint: {
            var ctx = getContext("2d");
            // Only the Canvas 2D surface this repo can actually verify: the
            // paint path is not driven headlessly, so no optional API is used.
            ctx.clearRect(0, 0, width, height);
            if (!overlay.vm || overlay.scale <= 0) return;

            // Regions already on this page, page px -> item px.
            var regions = overlay.vm.inspectorRegions || [];
            for (var i = 0; i < regions.length; ++i) {
                var geometry = regions[i].geometry;
                if (!geometry || !geometry.bbox) continue;
                var box = geometry.bbox;
                var selected = regions[i].region_id === overlay.vm.inspectorRegionId;
                ctx.strokeStyle = selected ? "#ea580c" : "#0ea5e9";
                ctx.lineWidth = selected ? 2 : 1;
                ctx.beginPath();
                ctx.rect(overlay.toItemX(box[0]), overlay.toItemY(box[1]),
                         box[2] * overlay.scale, box[3] * overlay.scale);
                ctx.stroke();
            }

            // The draft, in item px straight from the pointer.
            ctx.strokeStyle = "#16a34a";
            ctx.fillStyle = "#16a34a";
            ctx.lineWidth = 1;
            ctx.beginPath();
            if (overlay.drawingMode === "rect" && overlay.dragging) {
                ctx.rect(Math.min(overlay.dragFrom.x, overlay.dragTo.x),
                         Math.min(overlay.dragFrom.y, overlay.dragTo.y),
                         Math.abs(overlay.dragTo.x - overlay.dragFrom.x),
                         Math.abs(overlay.dragTo.y - overlay.dragFrom.y));
                ctx.stroke();
            } else if (overlay.drawingMode === "polygon"
                       && overlay.draftPoints.length) {
                var first = overlay.draftPoints[0];
                ctx.moveTo(overlay.toItemX(first[0] * overlay.pageW),
                           overlay.toItemY(first[1] * overlay.pageH));
                for (var p = 1; p < overlay.draftPoints.length; ++p) {
                    ctx.lineTo(overlay.toItemX(overlay.draftPoints[p][0] * overlay.pageW),
                               overlay.toItemY(overlay.draftPoints[p][1] * overlay.pageH));
                }
                ctx.stroke();
                for (var d = 0; d < overlay.draftPoints.length; ++d) {
                    var dp = overlay.draftPoints[d];
                    ctx.beginPath();
                    ctx.rect(overlay.toItemX(dp[0] * overlay.pageW) - 2,
                             overlay.toItemY(dp[1] * overlay.pageH) - 2, 4, 4);
                    ctx.fill();
                }
            }
        }
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()
    }

    MouseArea {
        id: input
        objectName: "regionOverlayInput"
        anchors.fill: parent
        enabled: overlay.visible && overlay.scale > 0 && overlay.vm !== null
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        cursorShape: Qt.CrossCursor

        onPressed: (mouse) => {
            overlay.forceActiveFocus();
            if (overlay.drawingMode !== "rect" || mouse.button !== Qt.LeftButton)
                return;
            var start = overlay.toNormalized(mouse.x, mouse.y);
            if (!start) return;                    // started in the grey band
            overlay.dragFrom = Qt.point(mouse.x, mouse.y);
            overlay.dragTo = overlay.dragFrom;
            overlay.dragging = true;
        }
        onPositionChanged: (mouse) => {
            if (!overlay.dragging) return;
            overlay.dragTo = Qt.point(mouse.x, mouse.y);
            canvas.requestPaint();
        }
        onReleased: (mouse) => {
            if (!overlay.dragging) return;
            overlay.dragging = false;
            var cornerA = overlay.toNormalized(
                Math.min(overlay.dragFrom.x, mouse.x),
                Math.min(overlay.dragFrom.y, mouse.y));
            var cornerB = overlay.toNormalized(
                Math.max(overlay.dragFrom.x, mouse.x),
                Math.max(overlay.dragFrom.y, mouse.y));
            if (cornerA && cornerB && overlay.vm)
                overlay.vm.createRectangle(cornerA[0], cornerA[1],
                                           cornerB[0], cornerB[1]);
            canvas.requestPaint();
        }
        onClicked: (mouse) => {
            if (overlay.drawingMode !== "polygon") return;
            if (mouse.button === Qt.RightButton) {  // close the ring and save
                overlay.commitPolygon();
                return;
            }
            var point = overlay.toNormalized(mouse.x, mouse.y);
            if (!point) return;
            overlay.draftPoints = overlay.draftPoints.concat([point]);
            canvas.requestPaint();
        }
    }

    // Reachable controls: declared after the MouseArea so they take their own
    // clicks instead of being treated as the start of a shape.
    Row {
        objectName: "regionToolbar"
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 8
        spacing: 4
        visible: overlay.visible

        Button {
            id: rectTool
            objectName: "regionToolRect"
            text: "矩形"
            visible: overlay.visible
            enabled: input.enabled
            palette.buttonText: overlay.drawingMode === "rect" ? "#ffffff" : "#44403c"
            onClicked: overlay.drawingMode = "rect"
        }
        Button {
            id: polygonTool
            objectName: "regionToolPolygon"
            text: "多边形"
            visible: overlay.visible
            enabled: input.enabled
            palette.buttonText: overlay.drawingMode === "polygon" ? "#ffffff" : "#44403c"
            onClicked: overlay.drawingMode = "polygon"
        }
    }

    Label {
        objectName: "regionToolHint"
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.margins: 8
        visible: input.enabled
        text: overlay.drawingMode === "polygon"
              ? "左键添加节点 · 右键闭合并保存 · Esc 取消 · Delete 删除选中"
              : "拖拽框选 · Esc 取消 · Delete 删除选中"
        color: "#57534e"
    }

    Connections {
        target: overlay.vm
        enabled: overlay.vm !== null
        function onInspectorChanged() { canvas.requestPaint(); }
        function onViewerChanged() { canvas.requestPaint(); }
    }

    // Keys go to the canvas only after the pointer has been used there, so the
    // Inspector keeps the keyboard while the user is typing a translation.
    Keys.onEscapePressed: (event) => { overlay.cancelDraft(); event.accepted = true; }
    Keys.onDeletePressed: (event) => {
        if (overlay.vm && overlay.vm.inspectorRegionId) {
            overlay.vm.deleteRegion(overlay.vm.inspectorRegionId);
            event.accepted = true;
        }
    }

    onDraftPointsChanged: canvas.requestPaint()
    onDragToChanged: canvas.requestPaint()
    onScaleChanged: canvas.requestPaint()
    onDrawingModeChanged: cancelDraft()
}
