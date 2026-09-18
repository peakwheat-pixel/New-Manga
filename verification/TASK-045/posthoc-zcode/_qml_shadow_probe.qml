
import QtQuick
Rectangle {
    id: root
    width: 100; height: 100
    // stands in for the context property the ViewModel would be
    property var model: [{url: "a"}, {url: "b"}]
    property bool hostVisible: true

    Column {
        Repeater {
            objectName: "legacy"
            // the TASK-020 .. 602cca8 spelling, verbatim
            model: visible ? model.tiles : []
            delegate: Rectangle { width: 10; height: 10; color: "red" }
        }
    }
    Column {
        Repeater {
            objectName: "partial"
            // 1171bc5: model qualified, visible still shadowed
            model: visible && root.model ? root.model : []
            delegate: Rectangle { width: 10; height: 10; color: "green" }
        }
    }
    Column {
        id: tilesHost
        Repeater {
            objectName: "fixed"
            // a165aa3: both names qualified
            model: tilesHost.visible && root.model ? root.model : []
            delegate: Rectangle { width: 10; height: 10; color: "blue" }
        }
    }
}
