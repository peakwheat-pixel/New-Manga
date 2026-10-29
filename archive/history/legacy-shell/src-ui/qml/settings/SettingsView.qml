import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"

// D05 §43.1 SettingsView: the settings page is top-level; inside, a fixed
// left category list (no sub-routes) and a content pane on the right.
// T1.2.1: the Provider and 网络/代理 categories are live through
// ``settingsViewModel`` — provider profiles (endpoint/model/credential),
// network profiles (proxy), per-capability bindings and the default
// network profile survive restart and feed the pipeline. Secrets are
// write-only (password fields, no echo-back); the viewmodel exposes only
// a ``credential_set`` flag, never the value (AC-SEC-001~005).
// The remaining categories arrive with later slices.
Rectangle {
    id: settings
    objectName: "settingsView"
    color: Tokens.bgPage

    property var pendingNetworkPayload: null

    // Context properties carry no change notification, and the engine's
    // first binding evaluation can land before the wrapper is reachable
    // (observed as a random "of null" TypeError on startup). Every read
    // below therefore null-guards; once the component completes — when
    // the context is reliably resolvable — we connect the viewmodel's
    // signals imperatively (JS connect bypasses Connections-name
    // matching entirely) and ping refresh() so its change signals re-run
    // every guarded binding with the real data.
    Component.onCompleted: {
        if (settingsViewModel) {
            settingsViewModel.saved.connect(function (message) {
                statusLabel.color = Tokens.stOkT;
                statusLabel.text = message;
            });
            settingsViewModel.failed.connect(function (message) {
                statusLabel.color = Tokens.stFail;
                statusLabel.text = message;
            });
            settingsViewModel.confirmationRequired.connect(function () {
                confirmDialog.open();
            });
            settingsViewModel.refresh();
        }
    }

    function capabilitiesFromChecks() {
        var picked = [];
        for (var i = 0; i < capabilityChecks.count; ++i) {
            var item = capabilityChecks.itemAt(i);
            if (item.checked)
                picked.push(item.capabilityKey);
        }
        return picked;
    }

    function fillProviderForm(profile) {
        providerIdField.text = profile ? profile.provider_profile_id : "";
        providerIdField.enabled = !profile;
        providerNameField.text = profile ? profile.name : "";
        providerTypeField.currentIndex = providerTypeField.find(
            profile ? profile.provider_type : "openai");
        providerBaseUrlField.text = profile ? profile.base_url : "";
        providerModelField.text = profile ? profile.model : "";
        providerApiKeyField.text = "";
        providerClearCredential.checked = false;
        providerNetworkCombo.currentIndex = profile
            ? providerNetworkCombo.indexOfValue(profile.network_profile_id) : -1;
        providerPolicyCombo.currentIndex = providerPolicyCombo.indexOfValue(
            profile ? profile.proxy_policy : "inherit");
        providerEnabledSwitch.checked = profile ? profile.is_enabled : true;
        for (var i = 0; i < capabilityChecks.count; ++i) {
            var item = capabilityChecks.itemAt(i);
            item.checked = profile
                ? profile.capabilities.indexOf(item.capabilityKey) >= 0 : false;
        }
    }

    function fillNetworkForm(profile) {
        networkIdField.text = profile ? profile.network_profile_id : "";
        networkIdField.enabled = !profile;
        networkNameField.text = profile ? profile.name : "";
        networkModeCombo.currentIndex = networkModeCombo.find(
            profile ? profile.mode : "direct");
        networkHttpField.text = profile ? profile.http_proxy : "";
        networkHttpsField.text = profile ? profile.https_proxy : "";
        networkSocksField.text = profile ? profile.socks5_proxy : "";
        networkUserField.text = profile ? profile.username : "";
        networkPasswordField.text = "";
        networkClearCredential.checked = false;
        networkBypassField.text = profile ? profile.bypass_hosts.join(", ") : "";
        networkInheritSwitch.checked = profile ? profile.inherit_system : true;
        networkTlsSwitch.checked = profile ? profile.verify_tls : true;
        networkFallbackSwitch.checked = profile
            ? profile.allow_proxy_failure_direct_fallback : false;
    }

    ListModel {
        id: categoryModel
        ListElement { name: "Provider" }
        ListElement { name: "网络 / 代理" }
        ListElement { name: "OCR" }
        ListElement { name: "翻译" }
        ListElement { name: "图片修复" }
        ListElement { name: "排版样式" }
        ListElement { name: "模型 / GPU" }
        ListElement { name: "任务 / 并发" }
        ListElement { name: "缓存 / Revision" }
        ListElement { name: "回收站" }
        ListElement { name: "备份 / 恢复" }
        ListElement { name: "Plugin / Hooks" }
    }

    Rectangle {
        id: categoryPane
        anchors.top: parent.top
        anchors.bottom: statusLabel.top
        anchors.left: parent.left
        anchors.margins: 8
        width: 180
        color: Tokens.bgPanel
        border.color: Tokens.border
        radius: 6

        ListView {
            id: categoryList
            objectName: "settingsCategoryList"
            anchors.fill: parent
            anchors.margins: 4
            clip: true
            model: categoryModel
            delegate: ItemDelegate {
                width: ListView.view.width
                text: model.name
                highlighted: ListView.isCurrentItem
                onClicked: categoryList.currentIndex = index
            }
        }
    }

    Rectangle {
        id: contentPane
        anchors.top: parent.top
        anchors.bottom: statusLabel.top
        anchors.left: categoryPane.right
        anchors.right: parent.right
        anchors.margins: 8
        anchors.leftMargin: 0
        color: Tokens.bgPanel
        border.color: Tokens.border
        radius: 6
        clip: true

        // ---------------------------------------------------------- //
        // Provider category
        // ---------------------------------------------------------- //
        ColumnLayout {
            id: providerPane
            anchors.fill: parent
            anchors.margins: 12
            spacing: 8
            visible: categoryList.currentIndex === 0

            RowLayout {
                Layout.fillWidth: true
                Label { text: "Provider 配置"; font.bold: true }
                Item { Layout.fillWidth: true }
                ComboBox {
                    id: providerSelect
                    Layout.preferredWidth: 240
                    model: settingsViewModel ? settingsViewModel.profiles : []
                    textRole: "name"
                    valueRole: "provider_profile_id"
                    onCurrentValueChanged: settings.fillProviderForm(
                        settingsViewModel && currentIndex >= 0
                            ? settingsViewModel.profiles[currentIndex] : null)
                }
                Button {
                    text: "新建"
                    onClicked: {
                        providerSelect.currentIndex = -1;
                        settings.fillProviderForm(null);
                    }
                }
            }

            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                ScrollBar.horizontal.policy: ScrollBar.AsNeeded

                GridLayout {
                    width: Math.max(providerPane.width - 40, 520)
                    columns: 2
                    columnSpacing: 12
                    rowSpacing: 8

                    Label { text: "配置 ID" }
                    TextField {
                        id: providerIdField
                        Layout.fillWidth: true
                        placeholderText: "例如 openai-translation"
                    }
                    Label { text: "名称" }
                    TextField { id: providerNameField; Layout.fillWidth: true }
                    Label { text: "Provider 类型" }
                    ComboBox {
                        id: providerTypeField
                        Layout.fillWidth: true
                        editable: true
                        model: ["openai", "local-doctr", "local-mangaocr", "local-ldsr"]
                    }
                    Label { text: "能力" }
                    RowLayout {
                        Repeater {
                            id: capabilityChecks
                            model: settingsViewModel ? settingsViewModel.capabilityList : []
                            CheckBox {
                                required property string modelData
                                readonly property string capabilityKey: modelData
                                text: modelData
                            }
                        }
                    }
                    Label { text: "Endpoint (base_url)" }
                    TextField {
                        id: providerBaseUrlField
                        Layout.fillWidth: true
                        placeholderText: "https://api.example.com/v1（本地 Provider 留空）"
                    }
                    Label { text: "模型" }
                    TextField { id: providerModelField; Layout.fillWidth: true }
                    Label { text: "API Key" }
                    TextField {
                        id: providerApiKeyField
                        Layout.fillWidth: true
                        echoMode: TextInput.Password
                        placeholderText: "已保存时留空表示不修改；仅写入系统凭据库"
                    }
                    Label { text: "已存密钥" }
                    RowLayout {
                        CheckBox {
                            id: providerClearCredential
                            text: "删除已保存的密钥"
                        }
                        Label {
                            property bool hasSecret: settingsViewModel
                                && providerSelect.currentIndex >= 0
                                && settingsViewModel.profiles[providerSelect.currentIndex]
                                ? settingsViewModel.profiles[providerSelect.currentIndex].credential_set
                                : false
                            text: hasSecret ? "已保存（内容不可查看）" : "未保存"
                            color: Tokens.ink3
                        }
                    }
                    Label { text: "代理策略" }
                    ComboBox {
                        id: providerPolicyCombo
                        Layout.fillWidth: true
                        textRole: "text"
                        valueRole: "value"
                        model: [
                            { value: "inherit", text: "跟随默认网络" },
                            { value: "profile", text: "使用指定网络配置" },
                            { value: "direct", text: "始终直连" }
                        ]
                    }
                    Label { text: "网络配置" }
                    ComboBox {
                        id: providerNetworkCombo
                        Layout.fillWidth: true
                        model: settingsViewModel ? settingsViewModel.networks : []
                        textRole: "name"
                        valueRole: "network_profile_id"
                    }
                    Label { text: "启用" }
                    Switch { id: providerEnabledSwitch; checked: true }

                    Item { Layout.fillWidth: true }
                    RowLayout {
                        Layout.alignment: Qt.AlignRight
                        Button {
                            text: "删除"
                            enabled: providerSelect.currentIndex >= 0
                            onClicked: settingsViewModel.deleteProviderProfile(
                                providerSelect.currentValue)
                        }
                        Button {
                            text: "保存"
                            highlighted: true
                            onClicked: settingsViewModel.saveProviderProfile({
                                provider_profile_id: providerIdField.text.trim(),
                                name: providerNameField.text.trim(),
                                provider_type: providerTypeField.editText.trim(),
                                capabilities: settings.capabilitiesFromChecks(),
                                base_url: providerBaseUrlField.text.trim(),
                                model: providerModelField.text.trim(),
                                api_key: providerApiKeyField.text,
                                clear_credential: providerClearCredential.checked,
                                network_profile_id: providerNetworkCombo.currentValue || "",
                                proxy_policy: providerPolicyCombo.currentValue,
                                is_enabled: providerEnabledSwitch.checked
                            })
                        }
                    }
                }
            }

            // Per-capability default bindings (AC-PROVIDER-002).
            Label { text: "能力默认绑定（写入管线默认值，运行时按此解析）"; font.bold: true }
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4
                Repeater {
                    model: settingsViewModel ? settingsViewModel.capabilityList : []
                    RowLayout {
                        required property string modelData
                        readonly property string capabilityKey: modelData
                        Layout.fillWidth: true
                        Label { text: parent.capabilityKey; Layout.preferredWidth: 90 }
                        ComboBox {
                            id: bindingCombo
                            Layout.preferredWidth: 240
                            // R4 B-005: only profiles declaring this
                            // capability are bindable here (R-007) — the
                            // registry descriptor check cannot recover the
                            // user's declaration after projection.
                            model: settingsViewModel
                                ? settingsViewModel.profiles.filter(function (p) {
                                      return p.capabilities.indexOf(parent.capabilityKey) >= 0;
                                  })
                                : []
                            textRole: "name"
                            valueRole: "provider_profile_id"
                            property string boundId: settingsViewModel
                                ? (settingsViewModel.bindings[parent.capabilityKey] || "") : ""
                            currentIndex: boundId === "" ? -1 : indexOfValue(boundId)
                        }
                        Button {
                            text: "绑定"
                            enabled: bindingCombo.currentIndex >= 0
                            onClicked: settingsViewModel.saveBinding(
                                parent.capabilityKey, bindingCombo.currentValue)
                        }
                        Button {
                            text: "清除"
                            onClicked: settingsViewModel.clearBinding(parent.capabilityKey)
                        }
                    }
                }
            }
        }

        // ---------------------------------------------------------- //
        // Network / proxy category
        // ---------------------------------------------------------- //
        ColumnLayout {
            id: networkPane
            anchors.fill: parent
            anchors.margins: 12
            spacing: 8
            visible: categoryList.currentIndex === 1

            RowLayout {
                Layout.fillWidth: true
                Label { text: "网络 / 代理配置"; font.bold: true }
                Item { Layout.fillWidth: true }
                ComboBox {
                    id: networkSelect
                    Layout.preferredWidth: 240
                    model: settingsViewModel ? settingsViewModel.networks : []
                    textRole: "name"
                    valueRole: "network_profile_id"
                    onCurrentValueChanged: settings.fillNetworkForm(
                        settingsViewModel && currentIndex >= 0
                            ? settingsViewModel.networks[currentIndex] : null)
                }
                Button {
                    text: "新建"
                    onClicked: {
                        networkSelect.currentIndex = -1;
                        settings.fillNetworkForm(null);
                    }
                }
            }

            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                ScrollBar.horizontal.policy: ScrollBar.AsNeeded

                GridLayout {
                    width: Math.max(networkPane.width - 40, 520)
                    columns: 2
                    columnSpacing: 12
                    rowSpacing: 8

                    Label { text: "配置 ID" }
                    TextField {
                        id: networkIdField
                        Layout.fillWidth: true
                        placeholderText: "例如 corp-proxy"
                    }
                    Label { text: "名称" }
                    TextField { id: networkNameField; Layout.fillWidth: true }
                    Label { text: "类型" }
                    ComboBox {
                        id: networkModeCombo
                        Layout.fillWidth: true
                        model: settingsViewModel ? settingsViewModel.networkModes : []
                    }
                    Label { text: "HTTP 代理" }
                    TextField {
                        id: networkHttpField
                        Layout.fillWidth: true
                        placeholderText: "http://host:port（不含用户名密码）"
                    }
                    Label { text: "HTTPS 代理" }
                    TextField { id: networkHttpsField; Layout.fillWidth: true }
                    Label { text: "SOCKS5 代理" }
                    TextField { id: networkSocksField; Layout.fillWidth: true }
                    Label { text: "用户名" }
                    TextField { id: networkUserField; Layout.fillWidth: true }
                    Label { text: "代理密码" }
                    TextField {
                        id: networkPasswordField
                        Layout.fillWidth: true
                        echoMode: TextInput.Password
                        placeholderText: "已保存时留空表示不修改；仅写入系统凭据库"
                    }
                    Label { text: "已存密码" }
                    CheckBox { id: networkClearCredential; text: "删除已保存的代理密码" }
                    Label { text: "绕过主机" }
                    TextField {
                        id: networkBypassField
                        Layout.fillWidth: true
                        placeholderText: "逗号分隔，例如 localhost, 127.0.0.1, .internal"
                    }
                    Label { text: "继承系统代理" }
                    Switch { id: networkInheritSwitch; checked: true }
                    Label { text: "验证 TLS 证书" }
                    Switch {
                        id: networkTlsSwitch
                        checked: true
                        // AC-SEC-004: default on; turning it off is gated
                        // by the confirmation dialog on save (AC-SEC-005).
                    }
                    Label { text: "代理失败回退直连" }
                    Switch { id: networkFallbackSwitch; checked: false }

                    Item { Layout.fillWidth: true }
                    RowLayout {
                        Layout.alignment: Qt.AlignRight
                        Button {
                            text: "删除"
                            enabled: networkSelect.currentIndex >= 0
                            onClicked: settingsViewModel.deleteNetworkProfile(
                                networkSelect.currentValue)
                        }
                        Button {
                            text: "保存"
                            highlighted: true
                            onClicked: {
                                var bypass = networkBypassField.text.split(",")
                                    .map(function (s) { return s.trim(); })
                                    .filter(function (s) { return s.length > 0; });
                                settings.pendingNetworkPayload = {
                                    network_profile_id: networkIdField.text.trim(),
                                    name: networkNameField.text.trim(),
                                    mode: networkModeCombo.currentValue,
                                    http_proxy: networkHttpField.text.trim(),
                                    https_proxy: networkHttpsField.text.trim(),
                                    socks5_proxy: networkSocksField.text.trim(),
                                    username: networkUserField.text.trim(),
                                    proxy_password: networkPasswordField.text,
                                    clear_credential: networkClearCredential.checked,
                                    bypass_hosts: bypass,
                                    inherit_system: networkInheritSwitch.checked,
                                    verify_tls: networkTlsSwitch.checked,
                                    allow_proxy_failure_direct_fallback:
                                        networkFallbackSwitch.checked,
                                    confirm_disable_tls: false
                                };
                                settingsViewModel.saveNetworkProfile(
                                    settings.pendingNetworkPayload);
                            }
                        }
                    }

                    Label { text: "默认网络配置" }
                    RowLayout {
                        ComboBox {
                            id: defaultNetworkCombo
                            Layout.preferredWidth: 240
                            model: settingsViewModel ? settingsViewModel.networks : []
                            textRole: "name"
                            valueRole: "network_profile_id"
                            currentIndex: settingsViewModel
                                ? indexOfValue(settingsViewModel.defaultNetworkProfileId) : -1
                        }
                        Button {
                            text: "设为默认"
                            enabled: defaultNetworkCombo.currentIndex >= 0
                            onClicked: settingsViewModel.setDefaultNetworkProfile(
                                "network", defaultNetworkCombo.currentValue)
                        }
                    }
                }
            }
        }

        // Remaining categories keep the placeholder until their slices land.
        Label {
            anchors.centerIn: parent
            visible: categoryList.currentIndex >= 2
            text: "设置项将在后续切片接入"
            color: Tokens.ink3
        }
    }

    Label {
        id: statusLabel
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 8
        elide: Text.ElideRight
        color: Tokens.ink
    }

    // AC-SEC-005: the dangerous-setting confirmation. Accepting re-submits
    // the same payload with the confirm flag set.
    Dialog {
        id: confirmDialog
        modal: true
        anchors.centerIn: parent
        title: "危险设置"
        standardButtons: Dialog.Ok | Dialog.Cancel
        Label { text: "确认禁用 TLS 证书验证？该配置不安全，仅在明确了解风险时继续。" }
        onAccepted: {
            if (settings.pendingNetworkPayload) {
                var payload = settings.pendingNetworkPayload;
                payload.confirm_disable_tls = true;
                settingsViewModel.saveNetworkProfile(payload);
            }
        }
    }
}
