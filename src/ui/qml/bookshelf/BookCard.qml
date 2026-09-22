import QtQuick
import QtQuick.Controls
import "../theme"

// D05 §7.1 Book Card: cover placeholder, titles, tags summary, progress,
// favorite/archive states. No business logic — display only.
//
// T2.1.1: every value comes from Tokens (F · Graphite Atelier). Text items set
// an explicit color and font.pixelSize because the accepted default theme is
// dark: an unstyled Label inherits the platform's black text and disappears.
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

    color: cardMouse.containsPress ? Tokens.bgPress
           : cardMouse.containsMouse ? Tokens.bgHover : Tokens.bgRaised
    border.color: Tokens.border
    radius: Tokens.radSm

    MouseArea {
        id: cardMouse
        anchors.fill: parent
        hoverEnabled: true
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
            radius: Tokens.radSm
            color: Tokens.bgInset
            Label {
                anchors.centerIn: parent
                text: "封面"
                color: Tokens.inkDis
                font.pixelSize: Tokens.fsSm
            }
        }
        Label {
            width: parent.width
            text: card.title
            color: Tokens.ink
            font.pixelSize: Tokens.fsLg
            font.weight: Font.DemiBold
            elide: Text.ElideRight
        }
        Label {
            width: parent.width
            visible: card.originalTitle !== ""
            text: card.originalTitle
            color: Tokens.ink2
            font.pixelSize: Tokens.fsSm
            elide: Text.ElideRight
        }
        Item { width: 1; height: 1 }
        Row {
            spacing: 6
            // Triple-encoded badge: glyph + tokenized color + text (§7.2).
            Rectangle {
                visible: card.isArchived
                color: Tokens.skipSoft
                radius: Tokens.radSm
                width: archivedLabel.implicitWidth + 8
                height: archivedLabel.implicitHeight + 4
                Label {
                    id: archivedLabel
                    anchors.centerIn: parent
                    text: "▣ 归档"
                    color: Tokens.stSkip
                    font.pixelSize: Tokens.fsSm
                }
            }
            Label {
                text: "进度 " + card.progress
                color: Tokens.ink3
                font.pixelSize: Tokens.fsSm
            }
        }
    }

    AbstractButton {
        id: favoriteButton
        objectName: "favorite-" + card.bookId
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 6
        width: Tokens.ctlH
        height: Tokens.ctlH
        text: card.isFavorite ? "★" : "☆"
        font.pixelSize: Tokens.fsSub
        ToolTip.visible: hovered
        ToolTip.text: card.isFavorite ? "取消收藏" : "收藏"
        onClicked: card.favoriteToggled(card.bookId, !card.isFavorite)
        contentItem: Label {
            text: favoriteButton.text
            color: card.isFavorite ? Tokens.accentText : Tokens.ink3
            font.pixelSize: Tokens.fsSub
        }
        background: Item {}
    }
}
