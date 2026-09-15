import QtQuick
import QtQuick.Controls

// D05 §7.1 Book Card: cover placeholder, titles, tags summary, progress,
// favorite/archive states. No business logic — display only.
Rectangle {
    id: card
    property string bookId: ""
    property string title: ""
    property string originalTitle: ""
    property bool isFavorite: false
    property bool isArchived: false
    property string lastOpenedAt: ""
    property string progress: "—"

    signal cardActivated(string bookId)
    signal favoriteToggled(string bookId, bool favorite)

    color: cardMouse.containsPress ? "#e8e8e4" : "#ffffff"
    border.color: "#d9d9d6"
    radius: 6

    MouseArea {
        id: cardMouse
        anchors.fill: parent
        onClicked: card.cardActivated(card.bookId)
    }

    Column {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 4

        Rectangle {
            // cover placeholder until covers exist (TASK-007 stores none)
            width: parent.width
            height: parent.height * 0.45
            radius: 4
            color: "#dfe3ee"
            Label {
                anchors.centerIn: parent
                text: "封面"
                color: "#9aa1b0"
            }
        }
        Label {
            width: parent.width
            text: card.title
            font.weight: Font.DemiBold
            elide: Text.ElideRight
        }
        Label {
            width: parent.width
            visible: card.originalTitle !== ""
            text: card.originalTitle
            color: "#6b7280"
            font.pixelSize: 11
            elide: Text.ElideRight
        }
        Item { width: 1; height: 1 }
        Row {
            spacing: 6
            Rectangle {
                visible: card.isArchived
                color: "#f0b429"
                radius: 3
                width: archivedLabel.implicitWidth + 8
                height: archivedLabel.implicitHeight + 4
                Label { id: archivedLabel; anchors.centerIn: parent; text: "归档"; font.pixelSize: 10 }
            }
            Label { text: "进度 " + card.progress; color: "#6b7280"; font.pixelSize: 11 }
        }
    }

    AbstractButton {
        id: favoriteButton
        objectName: "favorite-" + card.bookId
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 6
        width: 24
        height: 24
        text: card.isFavorite ? "★" : "☆"
        font.pixelSize: 16
        ToolTip.visible: hovered
        ToolTip.text: card.isFavorite ? "取消收藏" : "收藏"
        onClicked: card.favoriteToggled(card.bookId, !card.isFavorite)
        contentItem: Label { text: favoriteButton.text; font.pixelSize: 16; color: "#e2a400" }
        background: Item {}
    }
}
