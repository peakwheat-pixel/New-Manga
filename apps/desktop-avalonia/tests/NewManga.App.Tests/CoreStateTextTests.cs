using NewManga.App.Shell.V2;
using NewManga.DesignSystem;

namespace NewManga.App.Tests;

/// <summary>
/// REALUSE-DATA-SAFETY-3 AC4 (audit MA-10): Core's run terminals and step error codes reached the UI
/// as raw enum values (<c>completed_with_failures</c>, <c>MISSING_REQUIRED_INPUT</c>). They must be
/// explained in Chinese while keeping the identifier available for diagnosis.
/// </summary>
public sealed class CoreStateTextTests
{
    [Theory]
    [InlineData("completed", "已完成")]
    [InlineData("completed_with_failures", "已完成（有失败页）")]
    [InlineData("interrupted", "已中断")]
    [InlineData("cancelled", "已取消")]
    [InlineData("paused", "已暂停")]
    [InlineData("blocked", "阻塞")]
    [InlineData("running", "进行中")]
    [InlineData("failed", "失败")]
    public void RunStateText_ExplainsEveryCoreTerminal(string state, string expected)
    {
        Assert.Equal(expected, RunStatusMonitor.RunStateText(state));
    }

    [Fact]
    public void RunStateText_KeepsUnknownValuesDiagnosable()
    {
        Assert.Equal("some_future_state", RunStatusMonitor.RunStateText("some_future_state"));
        Assert.Equal("未知", RunStatusMonitor.RunStateText(string.Empty));
    }

    [Theory]
    [InlineData("completed", NmStatus.Done)]
    [InlineData("completed_with_failures", NmStatus.Done)]
    [InlineData("interrupted", NmStatus.Failed)]
    [InlineData("paused", NmStatus.Queued)]
    public void RunStateStatus_MapsTheFrozenSevenStateLanguage(string state, NmStatus expected)
    {
        Assert.Equal(expected, RunStatusMonitor.RunStateStatus(state));
    }

    [Theory]
    [InlineData("PROVIDER_NOT_CONFIGURED", "未配置模型 Provider")]
    [InlineData("MISSING_REQUIRED_INPUT", "缺少必要输入")]
    [InlineData("ARTIFACT_HASH_MISMATCH", "产物校验不一致")]
    [InlineData("EXPORT_WRITE_FAILED", "导出写入失败")]
    [InlineData("COMPOSITION_BASE_CHANGED", "合成底图已变化")]
    public void StepErrorText_ExplainsKnownCodes_AndKeepsThem(string code, string explanation)
    {
        var text = RunStatusMonitor.StepErrorText(code);

        Assert.Contains(explanation, text, StringComparison.Ordinal);
        // The identifier stays visible so a report can still be matched to the Core.
        Assert.Contains(code, text, StringComparison.Ordinal);
    }

    [Fact]
    public void StepErrorText_KeepsUnknownCodesVerbatim_AndNamesTheEmptyCase()
    {
        Assert.Equal("SOME_NEW_CODE", RunStatusMonitor.StepErrorText("SOME_NEW_CODE"));
        Assert.Equal("无错误码", RunStatusMonitor.StepErrorText(null));
        Assert.Equal("无错误码", RunStatusMonitor.StepErrorText("  "));
    }
}
