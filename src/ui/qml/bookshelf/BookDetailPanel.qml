import QtQuick
import QtQuick.Controls
import "../common"
import "../theme"

// D05 §7.1 BookDetailPanel: fixed on the right — cover, book fields, tags,
// favorite/archive, chapter list, 进入翻译/进入阅读. 编辑 and 更多 stay
// disabled placeholders (TASK-022 windows).
Rectangle {
    id: detail
    objectName: "bookDetailPanel"
    color: Tokens.bgPanel
    border.color: Tokens.border
    radius: Tokens.radSm

    property var shelf: bookshelfViewModel
    property var info: shelf.selectedBook

    // REPAIR-13 R13-AC1: the toolbar's import entry lives in BookshelfView
    // but needs the selected chapter id. `chapters` is an inner id — QML ids
    // are not visible across components, so the previous cross-component
    // `detailArea.chapters.currentChapterId` access raised "TypeError:
    // Cannot read property 'currentChapterId' of undefined" (Build 3
    // stderr, 31 occurrences). Expose the id as a proper property instead.
    readonly property alias currentChapterId: chapters.currentChapterId

    Column {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 8

        EmptyState {
            objectName: "detailEmptyState"
            visible: info.book_id === undefined || info.book_id === ""
            title: "未选择作品"
            description: "点击左侧作品查看详情"
        }

        Column {
            visible: !(info.book_id === undefined || info.book_id === "")
            spacing: 6

            Label {
                text: info.title !== undefined ? info.title : ""
                font.pixelSize: Tokens.fsTitle
                font.weight: Font.DemiBold
                color: Tokens.ink
            }
            Label {
                visible: info.originalTitle !== undefined && info.originalTitle !== ""
                text: info.originalTitle !== undefined ? info.originalTitle : ""
                color: Tokens.ink2
                font.pixelSize: Tokens.fsBase
            }
            Label {
                text: info.author !== undefined && info.author !== ""
                      ? "作者：" + info.author : ""
                color: Tokens.ink3
                font.pixelSize: Tokens.fsSm
            }
            Label {
                text: "标签：" + (info.tags !== undefined && info.tags.length > 0
                      ? info.tags.join("、") : "无")
                color: Tokens.ink3
                font.pixelSize: Tokens.fsSm
            }
            Label {
                text: "进度：—"  // 阅读进度字段尚未落地（TASK-007），诚实显示
                color: Tokens.ink3
                font.pixelSize: Tokens.fsSm
            }

            Row {
                spacing: 8
                CheckBox {
                    objectName: "detailFavorite"
                    text: "收藏"
                    checked: info.is_favorite === true
                    onClicked: shelf.setFavorite(info.book_id, checked)
                }
                CheckBox {
                    objectName: "detailArchived"
                    text: "归档"
                    checked: info.is_archived === true
                    onClicked: shelf.setArchived(info.book_id, checked)
                }
            }

            Row {
                spacing: 6
                TextField {
                    id: chapterTitleInput
                    objectName: "chapterTitleInput"
                    placeholderText: "章节标题"
                    width: 120
                }
                TextField {
                    id: chapterNumberInput
                    objectName: "chapterNumberInput"
                    placeholderText: "编号"
                    width: 60
                }
                Button {
                    objectName: "btnCreateChapter"
                    text: "新建章节"
                    enabled: info.book_id !== undefined && info.book_id !== ""
                             && chapterTitleInput.text !== ""
                    onClicked: {
                        shelf.createChapter(
                            info.book_id, chapterTitleInput.text,
                            chapterNumberInput.text)
                        chapterTitleInput.text = ""
                        chapterNumberInput.text = ""
                    }
                }
            }

            ChapterList {
                id: chapters
                width: parent.width
                height: 220
            }

            Row {
                spacing: 8
                Button {
                    objectName: "btnEnterTranslation"
                    text: "进入翻译"
                    enabled: chapters.currentChapterId !== ""
                    onClicked: shelf.enterTranslation(chapters.currentChapterId)
                }
                Button {
                    objectName: "btnEnterReading"
                    text: "进入阅读"
                    enabled: chapters.currentChapterId !== ""
                    onClicked: shelf.enterReading(chapters.currentChapterId)
                }
                Button { text: "编辑"; enabled: false }
                Button { text: "更多…"; enabled: false }
            }
        }
    }
}
