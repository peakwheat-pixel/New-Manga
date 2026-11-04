using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Interactivity;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.Shell.V2;
using NewManga.App.ViewModels.V2.Library;
using NewManga.App.Views.V2.Library;
using NewManga.CoreClient;
using Xunit;
using static NewManga.App.Tests.FakeHostController;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-09-UI-1: headless VM coverage of the referenced-import face in the V2 ImportDock —
/// plan preview render, password gate, confirm parameters, running cancel, retry (fresh plan,
/// never a duplicate submission), plan-stale refusal and password non-leakage into any UI text.
///
/// These are VIEW-MODEL state-machine tests over the real <see cref="ImportDockViewModel"/> and
/// the real <see cref="ImportDockView"/>; the controller seam is scripted (the REAL
/// Host↔Core↔production-adapter evidence lives in NewManga.Host.Tests.Fea09UiImportIpcTests
/// under NEWMANGA_FEA09_IPC=1 and is what backs AC-4, not this file).
/// </summary>
public sealed class ReferencedImportUiTests
{
    private const string SecretProbe = "never-leak-this-password";

    private static void Pump() => Dispatcher.UIThread.RunJobs();

    private static void Click(Button button) => button.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));

    private static (ImportDockViewModel ViewModel, List<(string Text, NmStatus Status)> Notices) Create(
        FakeHostController host,
        string? chapterId = "ch-1")
    {
        var notices = new List<(string, NmStatus)>();
        var viewModel = new ImportDockViewModel(
            host,
            picker: null,
            notify: (text, status) => notices.Add((text, status)),
            chapterId: () => chapterId,
            chapterTitle: () => "第 1 章",
            afterImport: () => Task.CompletedTask,
            requestCreateChapter: () => { },
            referencePollDelay: () => Task.CompletedTask);
        return (viewModel, notices);
    }

    private static SourcePlanPreview Plan(bool encrypted = false) => new(
        "ch-1",
        "skip",
        "plan-1",
        "digest-1",
        new[] { "grant-1" },
        new[]
        {
            new SourcePlanItemView(
                0,
                encrypted ? "locked.cbz" : "page.png",
                encrypted ? "cbz" : "image",
                encrypted ? "encrypted" : "ok",
                encrypted ? null : 1,
                null,
                false),
        },
        new SourcePlanTotals(encrypted ? 0 : 1, 0, 0, 0));

    private static SourceImportReceipt Receipt(
        string operationId,
        SourceImportOperationState state,
        int imported,
        int pending) => new(
        operationId,
        "ch-1",
        state,
        false,
        imported,
        new[]
        {
            new SourceImportReceiptItem(0, "page.png", "image", state == SourceImportOperationState.Failed ? "failed" : "imported",
                state == SourceImportOperationState.Failed ? "SOURCE_PASSWORD_INVALID" : null, imported, pending,
                new SourceImportCounts(ImportedPages: imported, PendingPages: pending)),
        },
        new SourceImportCounts(ImportedPages: imported, PendingPages: pending));

    private static IEnumerable<string> AllVisibleText(ImportDockViewModel viewModel) => new[]
    {
        viewModel.Summary,
        viewModel.ReferencePlanSummary,
        viewModel.ReferenceProgressText,
        viewModel.ReferenceErrorText,
        viewModel.Title,
    }.Concat(viewModel.ReferencePlanItems.Select(row => row.StatusText + row.WillImportText + row.DisplayName))
     .Concat(viewModel.ReferenceReceiptItems.Select(row => row.SourceName + row.OutcomeText + row.CountsText));

    // ------------------------------------------------------------------ plan preview (AC-1)

    [AvaloniaFact]
    public async Task PlanPreviewRendersCorePlanAndTotals()
    {
        var host = new FakeHostController(ReadySnapshot());
        host.ScriptedReferencePlans.Enqueue(Plan());
        var (viewModel, _) = Create(host);

        await viewModel.PlanReferenceImportAsync(new[] { new ReferenceImportSource(@"C:\manga\page.png", IsFolder: false) });

        Assert.True(viewModel.HasReferencePlan);
        Assert.False(viewModel.NeedsPassword);
        var row = Assert.Single(viewModel.ReferencePlanItems);
        Assert.Equal("page.png", row.DisplayName);
        Assert.Contains("可导入", row.StatusText);
        Assert.Contains("将导入 1 页", row.WillImportText);
        Assert.Contains("导入 1", viewModel.ReferencePlanSummary);
        Assert.Equal("ch-1", host.ReferencePlanCalls.Single().ChapterId);
        Assert.Equal("skip", host.ReferencePlanCalls.Single().Policy);
        Assert.Equal(string.Empty, viewModel.ReferenceErrorText);
    }

    [AvaloniaFact]
    public async Task PlanRefusalRendersTypedCodeOnly()
    {
        var host = new FakeHostController(ReadySnapshot());
        host.ScriptedReferencePlans.Enqueue(null);
        host.Snapshot = host.Snapshot with { LastError = "SOURCE_ACCESS_DENIED" };
        var (viewModel, notices) = Create(host);

        await viewModel.PlanReferenceImportAsync(new[] { new ReferenceImportSource(@"C:\manga\page.png", IsFolder: false) });

        Assert.False(viewModel.HasReferencePlan);
        Assert.Contains("SOURCE_ACCESS_DENIED", viewModel.ReferenceErrorText);
        Assert.NotEmpty(notices);
    }

    [AvaloniaFact]
    public async Task PlanWithoutChapterIsRefusedBeforeAnyHostCall()
    {
        var host = new FakeHostController(ReadySnapshot());
        var (viewModel, notices) = Create(host, chapterId: null);

        await viewModel.PlanReferenceImportAsync(new[] { new ReferenceImportSource(@"C:\manga\page.png", IsFolder: false) });

        Assert.Empty(host.ReferencePlanCalls);
        Assert.Contains(notices, notice => notice.Text.Contains("尚未选择章节"));
    }

    // ------------------------------------------------------------------ password gate (AC-2)

    [AvaloniaFact]
    public async Task EncryptedPlanRequiresPasswordBeforeConfirm()
    {
        var host = new FakeHostController(ReadySnapshot());
        host.ScriptedReferencePlans.Enqueue(Plan(encrypted: true));
        var (viewModel, _) = Create(host);

        await viewModel.PlanReferenceImportAsync(new[] { new ReferenceImportSource(@"C:\manga\locked.cbz", IsFolder: false) });

        Assert.True(viewModel.NeedsPassword);
        Assert.False(viewModel.CanConfirmReference);
        // entering the password unlocks exactly one start
        viewModel.ReferencePassword = SecretProbe;
        Assert.True(viewModel.CanConfirmReference);
        host.ScriptedReferenceStarts.Enqueue(SourceImportStartResult.Accepted("op-1"));
        host.ScriptedReferenceReceipts.Enqueue(Receipt("op-1", SourceImportOperationState.Completed, 2, 0));

        await viewModel.ConfirmReferenceImportAsync();

        Assert.Equal(SecretProbe, host.LastStartPassword);
    }

    [AvaloniaFact]
    public async Task PasswordIsClearedAfterStartAndNeverAppearsInUiText()
    {
        var host = new FakeHostController(ReadySnapshot());
        host.ScriptedReferencePlans.Enqueue(Plan(encrypted: true));
        var (viewModel, notices) = Create(host);

        await viewModel.PlanReferenceImportAsync(new[] { new ReferenceImportSource(@"C:\manga\locked.cbz", IsFolder: false) });
        viewModel.ReferencePassword = SecretProbe;
        host.ScriptedReferenceStarts.Enqueue(SourceImportStartResult.Accepted("op-1"));
        host.ScriptedReferenceReceipts.Enqueue(Receipt("op-1", SourceImportOperationState.Running, 1, 1));
        host.ScriptedReferenceReceipts.Enqueue(Receipt("op-1", SourceImportOperationState.Completed, 2, 0));

        await viewModel.ConfirmReferenceImportAsync();

        Assert.Equal(string.Empty, viewModel.ReferencePassword);
        Assert.DoesNotContain(SecretProbe, AllVisibleText(viewModel));
        Assert.DoesNotContain(SecretProbe, string.Concat(notices.Select(notice => notice.Text)));
    }

    [AvaloniaFact]
    public async Task FailedReceiptRendersTypedReasonWithoutSecrets()
    {
        var host = new FakeHostController(ReadySnapshot());
        host.ScriptedReferencePlans.Enqueue(Plan(encrypted: true));
        var (viewModel, _) = Create(host);

        await viewModel.PlanReferenceImportAsync(new[] { new ReferenceImportSource(@"C:\manga\locked.cbz", IsFolder: false) });
        viewModel.ReferencePassword = SecretProbe;
        host.ScriptedReferenceStarts.Enqueue(SourceImportStartResult.Accepted("op-9"));
        host.ScriptedReferenceReceipts.Enqueue(Receipt("op-9", SourceImportOperationState.Failed, 0, 2));

        await viewModel.ConfirmReferenceImportAsync();

        Assert.Contains("密码错误", viewModel.ReferenceReceiptItems.Single().OutcomeText);
        Assert.DoesNotContain(SecretProbe, AllVisibleText(viewModel));
        Assert.DoesNotContain(@"C:\manga", AllVisibleText(viewModel));
    }

    // ------------------------------------------------------------------ confirm / retry (AC-3)

    [AvaloniaFact]
    public async Task ConfirmWhileRunningIsIgnored_SoARunningImportIsNeverResubmitted()
    {
        var host = new FakeHostController(ReadySnapshot());
        var pollGate = new SemaphoreSlim(0, 100);
        var viewModel = new ImportDockViewModel(
            host,
            picker: null,
            notify: (_, _) => { },
            chapterId: () => "ch-1",
            chapterTitle: () => "第 1 章",
            afterImport: () => Task.CompletedTask,
            requestCreateChapter: () => { },
            referencePollDelay: () => pollGate.WaitAsync());

        host.ScriptedReferencePlans.Enqueue(Plan());
        await viewModel.PlanReferenceImportAsync(new[] { new ReferenceImportSource(@"C:\manga\page.png", IsFolder: false) });
        host.ScriptedReferenceStarts.Enqueue(SourceImportStartResult.Accepted("op-2"));

        var confirming = viewModel.ConfirmReferenceImportAsync();
        Pump();
        Assert.True(viewModel.IsReferenceRunning);

        // a second click while running must be a no-op — the running import is never re-submitted
        await viewModel.ConfirmReferenceImportAsync();
        Assert.Equal(1, host.ReferenceStartCalls);

        host.ScriptedReferenceReceipts.Enqueue(Receipt("op-2", SourceImportOperationState.Completed, 1, 0));
        pollGate.Release();
        await confirming;

        Assert.False(viewModel.IsReferenceRunning);
        // the plan was consumed by the accepted start — a plain re-confirm can never re-submit it
        Assert.False(viewModel.HasReferencePlan);
        Assert.False(viewModel.CanConfirmReference);
    }

    [AvaloniaFact]
    public async Task ConsumedPlanCannotBeReconfirmed_RetryGoesThroughAFreshPlan()
    {
        var host = new FakeHostController(ReadySnapshot());
        host.ScriptedReferencePlans.Enqueue(Plan());
        var (viewModel, _) = Create(host);

        await viewModel.PlanReferenceImportAsync(new[] { new ReferenceImportSource(@"C:\manga\page.png", IsFolder: false) });
        host.ScriptedReferenceStarts.Enqueue(SourceImportStartResult.Accepted("op-1"));
        host.ScriptedReferenceReceipts.Enqueue(Receipt("op-1", SourceImportOperationState.Completed, 1, 0));
        await viewModel.ConfirmReferenceImportAsync();
        Assert.False(viewModel.CanConfirmReference);

        // retry = fresh plan (new plan id) → new operation id; natural keys in the Core keep the
        // committed pages from being duplicated
        host.ScriptedReferencePlans.Enqueue(Plan() with { PlanId = "plan-2" });
        await viewModel.ReplanReferenceImportAsync();
        Assert.True(viewModel.HasReferencePlan);
        Assert.Equal(2, host.ReferencePlanCalls.Count);
    }

    [AvaloniaFact]
    public async Task PlanStaleStartRefusalDropsThePlanAndAsksForAFreshPreview()
    {
        var host = new FakeHostController(ReadySnapshot());
        host.ScriptedReferencePlans.Enqueue(Plan());
        var (viewModel, _) = Create(host);

        await viewModel.PlanReferenceImportAsync(new[] { new ReferenceImportSource(@"C:\manga\page.png", IsFolder: false) });
        host.ScriptedReferenceStarts.Enqueue(SourceImportStartResult.Failed("SOURCE_PLAN_STALE", SourceImportText.CodeText("SOURCE_PLAN_STALE")));

        await viewModel.ConfirmReferenceImportAsync();

        Assert.False(viewModel.HasReferencePlan);
        Assert.False(viewModel.CanConfirmReference);
        Assert.Contains("重新预览", viewModel.ReferenceErrorText);
        Assert.DoesNotContain(@"C:\manga", viewModel.ReferenceErrorText);
    }

    // ------------------------------------------------------------------ cancel (AC-3)

    [AvaloniaFact]
    public async Task RunningCancelInvokesTheHostCancelFace()
    {
        var host = new FakeHostController(ReadySnapshot());
        var pollGate = new SemaphoreSlim(0, 100);
        var viewModel = new ImportDockViewModel(
            host,
            picker: null,
            notify: (_, _) => { },
            chapterId: () => "ch-1",
            chapterTitle: () => "第 1 章",
            afterImport: () => Task.CompletedTask,
            requestCreateChapter: () => { },
            referencePollDelay: () => pollGate.WaitAsync());

        host.ScriptedReferencePlans.Enqueue(Plan());
        await viewModel.PlanReferenceImportAsync(new[] { new ReferenceImportSource(@"C:\manga\page.png", IsFolder: false) });
        host.ScriptedReferenceStarts.Enqueue(SourceImportStartResult.Accepted("op-d"));
        var confirming = viewModel.ConfirmReferenceImportAsync();
        Pump();
        Assert.True(viewModel.CanCancelReference);

        await viewModel.CancelReferenceImportAsync();

        var cancelled = Assert.Single(host.ReferenceCancelCalls);
        Assert.Equal("op-d", cancelled);
        Assert.Contains("已请求取消", viewModel.ReferenceProgressText);

        host.ScriptedReferenceReceipts.Enqueue(Receipt("op-d", SourceImportOperationState.Cancelled, 0, 1));
        pollGate.Release();
        await confirming;
        Assert.Contains("已取消", viewModel.ReferenceProgressText);
        Assert.Contains("待处理 1", viewModel.ReferenceProgressText);
    }

    [AvaloniaFact]
    public async Task CancelWithoutRunningOperationIsIgnored()
    {
        var host = new FakeHostController(ReadySnapshot());
        var (viewModel, _) = Create(host);

        await viewModel.CancelReferenceImportAsync();

        Assert.Empty(host.ReferenceCancelCalls);
    }

    // ------------------------------------------------------------------ close guard

    [AvaloniaFact]
    public async Task CloseIsRefusedWhileReferenceImportRuns()
    {
        var host = new FakeHostController(ReadySnapshot());
        var pollGate = new SemaphoreSlim(0, 100);
        var notices = new List<(string Text, NmStatus Status)>();
        var viewModel = new ImportDockViewModel(
            host,
            picker: null,
            notify: (text, status) => notices.Add((text, status)),
            chapterId: () => "ch-1",
            chapterTitle: () => "第 1 章",
            afterImport: () => Task.CompletedTask,
            requestCreateChapter: () => { },
            referencePollDelay: () => pollGate.WaitAsync());

        host.ScriptedReferencePlans.Enqueue(Plan());
        await viewModel.PlanReferenceImportAsync(new[] { new ReferenceImportSource(@"C:\manga\page.png", IsFolder: false) });
        Assert.True(viewModel.IsOpen);
        host.ScriptedReferenceStarts.Enqueue(SourceImportStartResult.Accepted("op-x"));
        var confirming = viewModel.ConfirmReferenceImportAsync();
        Pump();

        viewModel.Close();

        Assert.True(viewModel.IsOpen);
        Assert.Contains(notices, notice => notice.Text.Contains("导入进行中"));

        host.ScriptedReferenceReceipts.Enqueue(Receipt("op-x", SourceImportOperationState.Completed, 1, 0));
        pollGate.Release();
        await confirming;
        viewModel.Close();
        Assert.False(viewModel.IsOpen);
    }

    // ------------------------------------------------------------------ view rendering

    [AvaloniaFact]
    public async Task ViewRendersPlanRowsPasswordBoxAndButtonsFromRealControls()
    {
        var host = new FakeHostController(ReadySnapshot());
        host.ScriptedReferencePlans.Enqueue(Plan(encrypted: true));
        var (viewModel, _) = Create(host);
        var view = new ImportDockView { DataContext = viewModel };
        var window = new Window { Content = view };
        window.Show();
        await viewModel.PlanReferenceImportAsync(new[] { new ReferenceImportSource(@"C:\manga\locked.cbz", IsFolder: false) });
        Pump();

        var password = view.GetControl<TextBox>("ReferencePasswordBox");
        Assert.NotNull(password);
        Assert.True(password.IsVisible);
        Assert.Equal('•', password.PasswordChar);

        var confirm = view.GetControl<Button>("ConfirmReferenceButton");
        Assert.False(confirm.IsEnabled);
        password.Text = SecretProbe;
        Pump();
        Assert.True(confirm.IsEnabled);

        // the plan row shows the Core's status text, never the picked path
        var progress = view.GetControl<TextBlock>("ReferenceProgressText");
        Assert.NotNull(progress);
        Assert.DoesNotContain(@"C:\manga", viewModel.ReferencePlanSummary + viewModel.ReferencePlanItems.Single().DisplayName);
    }
}
