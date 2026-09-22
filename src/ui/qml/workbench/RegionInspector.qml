import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"

// D05 §15/§55 right fixed Region Inspector: region list of the current
// page, manual translation editing with dirty tracking (修改文字后自动
// dirty), save/discard, and the single-Region command entries of the
// D05 §56 Screen-Action Map (OCR / 重译 / 重全翻译).
Rectangle {
    id: inspector
    objectName: "regionInspector"
    color: Tokens.bgPanel

    property var regions: []
    property string selectedRegionId: ""
    property string text: ""
    property bool dirty: false

    signal regionClicked(string regionId)
    signal textEdited(string text)
    signal saveClicked()
    signal discardClicked()
    signal commandClicked(string commandType)

    implicitWidth: Tokens.inspW

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 6

        RowLayout {
            Layout.fillWidth: true
            Label { text: "Region Inspector"; font.bold: true
                    color: Tokens.ink; font.pixelSize: Tokens.fsSub }
            Item { Layout.fillWidth: true }
            Label {
                objectName: "inspectorDirtyBadge"
                text: inspector.dirty ? "● 未保存" : ""
                color: Tokens.stWarnT
                font.pixelSize: Tokens.fsSm
            }
        }

        ListView {
            id: regionList
            objectName: "regionListView"
            Layout.fillWidth: true
            Layout.preferredHeight: Math.min(160, contentHeight)
            model: inspector.regions
            clip: true
            spacing: 2
            delegate: Rectangle {
                width: regionList.width
                height: Tokens.rowH
                radius: Tokens.radSm
                objectName: "regionRow-" + modelData.region_id
                color: modelData.region_id === inspector.selectedRegionId
                       ? Tokens.accentSoft : Tokens.bgRaised
                border.color: modelData.region_id === inspector.selectedRegionId
                              ? Tokens.accent : Tokens.border
                TapHandler { onTapped: inspector.regionClicked(modelData.region_id) }
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 4
                    spacing: 4
                    Label {
                        text: "#" + (modelData.reading_order + 1)
                        color: Tokens.ink2
                        font.pixelSize: Tokens.fsSm
                    }
                    Label {
                        Layout.fillWidth: true
                        text: modelData.translation === "" ? "（无译文）" : modelData.translation
                        elide: Text.ElideRight
                        font.pixelSize: Tokens.fsSm
                        // ink-2 rather than ink-3 on both row grounds: the
                        // selected row composites accent-soft over panel and
                        // ink-3 measures 4.29:1 there, under the 4.5:1 bar.
                        color: Tokens.ink2
                    }
                    Label {
                        text: "🔒"
                        visible: modelData.translation_locked
                        color: Tokens.stLock
                        font.pixelSize: Tokens.fsSm
                    }
                }
            }
        }

        Label { text: "译文（人工编辑）"; font.pixelSize: Tokens.fsSm; color: Tokens.ink3 }
        TextArea {
            id: translationInput
            objectName: "inspectorTranslationInput"
            Layout.fillWidth: true
            Layout.fillHeight: true
            text: inspector.text
            color: Tokens.ink
            wrapMode: TextArea.Wrap
            enabled: inspector.selectedRegionId !== ""
            readOnly: inspector.selectedRegionId === ""
            background: Rectangle {
                color: Tokens.bgInset
                border.color: Tokens.border
                radius: Tokens.radSm
            }
            onTextChanged: if (text !== inspector.text) inspector.textEdited(text)
        }
        // User typing breaks the TextArea binding; keep external updates
        // (region switch, save, discard) flowing into the editor.
        Connections {
            target: inspector
            function onTextChanged() {
                if (translationInput.text !== inspector.text)
                    translationInput.text = inspector.text
            }
        }

        RowLayout {
            spacing: 6
            Button {
                objectName: "inspectorSave"
                text: "保存"
                enabled: inspector.dirty
                onClicked: inspector.saveClicked()
            }
            Button {
                objectName: "inspectorDiscard"
                text: "放弃"
                enabled: inspector.dirty
                onClicked: inspector.discardClicked()
            }
            Item { Layout.fillWidth: true }
        }

        // 单 Region 命令入口（D05 §56 工作台动作）。
        RowLayout {
            spacing: 6
            Button {
                objectName: "regionCommandOcr"
                text: "OCR"
                enabled: inspector.selectedRegionId !== ""
                onClicked: inspector.commandClicked("ocr_region")
            }
            Button {
                objectName: "regionCommandRetranslate"
                text: "重译"
                enabled: inspector.selectedRegionId !== ""
                onClicked: inspector.commandClicked("retranslate_region")
            }
            Button {
                objectName: "regionCommandRetranslateFull"
                text: "重全翻译"
                enabled: inspector.selectedRegionId !== ""
                onClicked: inspector.commandClicked("retranslate_region_full")
            }
        }
    }
}
