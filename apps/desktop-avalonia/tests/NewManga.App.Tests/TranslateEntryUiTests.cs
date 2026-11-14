using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.CoreClient;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// TRANS-ENTRY-UI (L1-T-C) AC1/AC2/AC3/AC4/AC8: the user-facing sentences are asserted here as
/// STRINGS (not internal enums), and the two preflights are pinned behaviourally:
/// no provider → no StartRun frame; empty chapter → readable sentence; probe failure never blocks.
/// </summary>
public sealed class TranslateEntryUiTests
{
    private static async Task<(FakeHostController Host, WorkbenchViewModel Vm)> SubjectAsync()
    {
        var host = new FakeHostController(new HostViewSnapshot(
            HostViewState.Ready, "ready", "—", null, null, Array.Empty<BookSummary>(), 0, false, null));
        var vm = new WorkbenchViewModel(host, "session-1");
        host.ChapterPagesByChapter["chapter-1"] = new[]
        {
            new ChapterPageSummary("page-1", "page-1.jpg", 0),
        };
        host.ScriptedBindingResolveResults.Enqueue(new ProviderBindingResult(false, "profile-1", "Translation", "global"));
        await vm.LoadAsync("chapter-1");
        return (host, vm);
    }

    [Fact]
    public void FourFailureClasses_HaveDistinctUserVisibleSentences()
    {
        var notConfigured = TranslateErrorText.ForCode("PROVIDER_NOT_CONFIGURED");
        var authFailed = TranslateErrorText.ForCode("PROVIDER_AUTH_FAILED");
        var rejected = TranslateErrorText.ForCode("INVALID_REQUEST");
        var rateLimited = TranslateErrorText.ForCode("PROVIDER_RATE_LIMITED");

        Assert.Contains("设置 → Provider 与凭据", notConfigured, StringComparison.Ordinal);
        Assert.Contains("401/403", authFailed, StringComparison.Ordinal);
        Assert.Contains("重试不会改善", authFailed, StringComparison.Ordinal);
        Assert.Contains("模型名写错", rejected, StringComparison.Ordinal);
        Assert.Contains("额度", rejected, StringComparison.Ordinal);
        Assert.Contains("429", rateLimited, StringComparison.Ordinal);
        Assert.Contains("复用同一个意图键", rateLimited, StringComparison.Ordinal);

        // AC2: four classes, four different sentences — never one shared blob.
        var sentences = new[] { notConfigured, authFailed, rejected, rateLimited };
        Assert.Equal(4, sentences.Distinct(StringComparer.Ordinal).Count());
    }

    [Fact]
    public void RestartHint_IsPartOfTheActionableProviderSentence()
    {
        Assert.Equal("修改模型配置后需重启应用生效。", TranslateErrorText.RestartHint);
        Assert.Contains(TranslateErrorText.RestartHint, TranslateErrorText.ProviderNotConfigured, StringComparison.Ordinal);
    }

    [Fact]
    public async Task MissingBinding_BlocksBeforeAnyStartRun()
    {
        var (host, vm) = await SubjectAsync();
        host.ScriptedBindingResolveResults.Clear();
        host.ScriptedBindingResolveResults.Enqueue(new ProviderBindingResult(true, null, "Translation", null));

        var started = await vm.StartRunAsync();

        Assert.False(started);
        Assert.Equal(TranslateErrorText.ProviderNotConfigured, vm.Error);
        Assert.Empty(host.StartRunRequests);
    }

    [Fact]
    public async Task EmptyChapter_ProbeRuns_AndItsSentenceIsReadable()
    {
        var (host, vm) = await SubjectAsync();
        host.ChapterPagesByChapter["chapter-1"] = Array.Empty<ChapterPageSummary>();

        await vm.StartRunAsync();

        // Card constraint 4: the probe is advisory — it runs, the attempt still goes out, and the
        // readable sentence (never INVALID_REQUEST) is what the user would see.
        Assert.Contains("chapter-1", host.ChapterPageCalls);
        Assert.NotEmpty(host.StartRunRequests);
        Assert.Contains("本章没有可处理的页面", TranslateErrorText.EmptyChapter, StringComparison.Ordinal);
        Assert.DoesNotContain("INVALID_REQUEST", TranslateErrorText.EmptyChapter, StringComparison.Ordinal);
    }
    [Fact]
    public async Task ReadyHostWithNoPages_ShowsTheEmptyChapterSentence()
    {
        var (host, vm) = await SubjectAsync();
        host.ChapterPagesByChapter["chapter-1"] = Array.Empty<ChapterPageSummary>();
        host.ScriptedStartRuns.Enqueue(null);
        host.ScriptedStartRunErrorCode = "INVALID_REQUEST";

        var started = await vm.StartRunAsync();

        Assert.False(started);
        Assert.Contains("chapter-1", host.ChapterPageCalls);
        // P1-1: READY host + genuinely 0 pages -> the readable empty-chapter sentence.
        Assert.Equal(TranslateErrorText.EmptyChapter, vm.Error);
        Assert.DoesNotContain("INVALID_REQUEST", vm.Error, StringComparison.Ordinal);
    }

    [Fact]
    public async Task UnreadyHost_DoesNotPretendTheChapterIsEmpty()
    {
        // P1-1: ListChapterPagesAsync returns an empty list when the Host is not ready
        // (HostController.cs:967-970); that must never become "本章没有页面".
        var host = new FakeHostController(new HostViewSnapshot(
            HostViewState.Failed, "HOST_NOT_READY", "Host 未就绪", null, null,
            Array.Empty<BookSummary>(), 0, false, null));
        var vm = new WorkbenchViewModel(host, "session-1");
        host.ChapterPagesByChapter["chapter-1"] = Array.Empty<ChapterPageSummary>();
        host.ScriptedBindingResolveResults.Enqueue(new ProviderBindingResult(false, "profile-1", "Translation", "global"));
        host.ScriptedStartRuns.Enqueue(null);
        host.ScriptedStartRunErrorCode = "INVALID_REQUEST";
        await vm.LoadAsync("chapter-1");

        var started = await vm.StartRunAsync();

        Assert.False(started);
        Assert.NotEqual(TranslateErrorText.EmptyChapter, vm.Error);
        Assert.Equal(TranslateErrorText.ForCode("INVALID_REQUEST"), vm.Error);
    }
    // P1-2 (r2): the execution-time surface — FluentRunRow.ErrorCell — had zero test coverage.
    [Fact]
    public void ErrorCell_MapsExecutionTimeCodeToReadableSentence()
    {
        var row = new FluentRunRow("p1", 0, "a.png", NewManga.DesignSystem.Controls.StatusKind.Failed, "失败", "failed", "PROVIDER_AUTH_FAILED", "row");

        Assert.Equal(TranslateErrorText.ForCode("PROVIDER_AUTH_FAILED"), row.ErrorCell);
        Assert.DoesNotContain("PROVIDER_AUTH_FAILED", row.ErrorCell, StringComparison.Ordinal);
    }

    [Fact]
    public void ErrorCell_KeepsUnknownCodeForDiagnosis()
    {
        var row = new FluentRunRow("p1", 0, "a.png", NewManga.DesignSystem.Controls.StatusKind.Failed, "失败", "failed", "SOMETHING_NEW", "row");

        Assert.Contains("SOMETHING_NEW", row.ErrorCell, StringComparison.Ordinal);
    }
}