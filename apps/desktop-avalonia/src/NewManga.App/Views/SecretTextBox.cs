using Avalonia;
using Avalonia.Automation;
using Avalonia.Automation.Peers;
using Avalonia.Controls;

namespace NewManga.App.Views;

/// <summary>
/// CREDENTIAL-UI-1 AC1/AC3: the only input control allowed to hold a credential secret.
///
/// Defence in depth:
///  - visual masking through <see cref="TextBox.PasswordChar"/> (never a plain TextBox);
///  - no context flyout / context menu, so "copy" is not offered by the control;
///  - the settings section additionally swallows Ctrl+C / Ctrl+X / Ctrl+Insert while this control has
///    focus (see <c>CredentialSection</c>);
///  - a custom automation peer that exposes no value: the secret never enters the UI automation tree,
///    unlike the stock TextBox peer (which can surface Text through the value pattern);
///  - no undo history (undo would retain earlier secrets).
/// </summary>
public sealed class SecretTextBox : TextBox
{
    public SecretTextBox()
    {
        Name = "CredentialSecret";
        PasswordChar = '●';
        Watermark = "粘贴或输入 API Key / 代理密码（掩码输入）";
        MaxLength = 4096;
        IsUndoEnabled = false;
        AcceptsReturn = false;
        ContextFlyout = null;
        ContextMenu = null;
        AutomationProperties.SetName(this, "凭据密码（掩码输入，不暴露明文）");
        AutomationProperties.SetHelpText(this, "输入内容以掩码显示；复制快捷键被禁用；提交后立即清空。");
    }

    protected override AutomationPeer OnCreateAutomationPeer() => new MaskedSecretAutomationPeer(this);

    // Avalonia resolves the control theme by style key; a derived control must keep the TextBox theme,
    // otherwise it measures to 0x0 and is invisible (found in the real-app screenshot pass).
    protected override Type StyleKeyOverride => typeof(TextBox);

    /// <summary>Tests/evidence: the peer this control would publish (it must not carry the secret).</summary>
    public AutomationPeer CreatePeerForVerification() => OnCreateAutomationPeer();

    private sealed class MaskedSecretAutomationPeer : ControlAutomationPeer
    {
        public MaskedSecretAutomationPeer(Control owner)
            : base(owner)
        {
        }

        protected override string GetClassNameCore() => "SecretTextBox";

        protected override AutomationControlType GetAutomationControlTypeCore() => AutomationControlType.Edit;

        protected override string GetNameCore() => "凭据密码（掩码输入，不暴露明文）";
    }
}
