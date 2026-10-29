namespace NewManga.App.Shell.V2;

/// <summary>
/// Request for the shell confirmation modal (DESIGN_SYSTEM §6.2 Modal: default focus on 取消,
/// Esc closes, dangerous actions spell out the consequence and the affected scope).
/// </summary>
public sealed record ConfirmRequest(
    string Title,
    string Body,
    string ConfirmText,
    bool IsDanger,
    Action OnConfirm,
    bool CanConfirm = true,
    string? BlockedReason = null);
