import QtQuick
import QtQuick.Controls

// D05 §9 Chapter List: chapter number/title/type/direction/page count +
// row actions. Row actions call the viewmodel directly; 编辑/页面管理/
// 翻译设置 are honest placeholders until TASK-013/022 deliver them.
Rectangle {
    id: chapterList
    objectName: "chapterList"
    color: "#ffffff"
    border.color: "#d9d9d6"
    radius: 6

    property var shelf: bookshelfViewModel
    property string currentChapterId: ""

    signal chapterSelected(string chapterId)

    ListView {
        id: listView
        objectName: "chapterListView"
        anchors.fill: parent
        anchors.margins: 4
        clip: true
        spacing: 2
        model: shelf.chapterListModel

        delegate: Rectangle {
            width: ListView.view.width
            height: 44
            radius: 4
            color: listView.currentIndex === index ? "#e8edff" : "#fafafa"

            Row {
                anchors.fill: parent
                anchors.margins: 6
                spacing: 8

                Label {
                    anchors.verticalCenter: parent.verticalCenter
                    text: model.chapterNumber !== "" ? model.chapterNumber : "·"
                    font.weight: Font.DemiBold
                    color: "#4f6bed"
                }
                Column {
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 0
                    Label { text: model.title; font.weight: Font.DemiBold }
                    Label {
                        text: (model.chapterType === "webtoon" ? "Webtoon" : "分页")
                              + " · "
                              + (model.readingDirection === "rtl" ? "从右到左"
                                 : model.readingDirection === "ltr" ? "从左到右"
                                 : "竖排")
                              + " · " + model.pageCount + " 页"
                        color: "#6b7280"
                        font.pixelSize: 11
                    }
                }
                Item { width: 1; height: 1 }  // spacer before actions

                Button { text: "进入翻译"; flat: true
                         onClicked: shelf.enterTranslation(model.chapterId) }
                Button { text: "进入阅读"; flat: true
                         onClicked: shelf.enterReading(model.chapterId) }
                Button { text: "编辑"; flat: true; enabled: false }
                Button { text: "页面管理"; flat: true; enabled: false }
                Button { text: "翻译设置"; flat: true; enabled: false }
                Button { objectName: "deleteChapter-" + model.chapterId
                         text: "删除"; flat: true
                         onClicked: shelf.deleteChapter(model.chapterId) }
            }
            MouseArea {
                anchors.fill: parent
                // Row selection: the chapter id comes straight from the
                // delegate roles — QML cannot call plain (non-slot) python
                // model methods like roleForName/data.
                onClicked: {
                    listView.currentIndex = index
                    chapterList.currentChapterId = model.chapterId
                    chapterList.chapterSelected(model.chapterId)
                }
                z: -1
            }
        }

        Label {
            anchors.centerIn: parent
            visible: listView.count === 0
            text: "暂无章节"
            color: "#6b7280"
        }
    }
}
