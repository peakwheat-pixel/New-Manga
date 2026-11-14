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
}
