using NewManga.Host.Sources;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// MINT-FAILURE-DIAG-1: <c>SourceReadCoordinator.MapMintFailure</c> used to funnel every exception it did
/// not enumerate into <c>SOURCE_ENTRY_MISSING</c> **and discard the original exception**. That made
/// "file missing", "unauthorized" and "anything else" indistinguishable on the error code, which is
/// exactly what blocked triage of a genuinely failing test (<c>Fea11Residual4AIpcTests</c>):
/// all we could see was <c>SOURCE_ENTRY_MISSING</c> with no way to learn why.
///
/// The fix keeps the public error codes EXACTLY as they were (so no caller or assertion changes) and only
/// attaches the original exception for diagnostics. These facts pin both halves:
///   * the code is unchanged, and
///   * the original exception type is observable.
///
/// If someone removes the inner exception again, the second assertion goes red.
/// </summary>
public sealed class MapMintFailureDiagnosticsTests
{
    [Fact]
    public void UnlistedException_KeepsSourceEntryMissingCode()
    {
        // InvalidOperationException is NOT an IOException/ArgumentException subclass, so it really does take
        // the catch-all. (PathTooLongException would NOT: it derives from IOException and maps to
        // FILE_IDENTITY_CHANGED -- a mistake this test originally made and now documents.)
        var mapped = SourceReadCoordinator.MapMintFailure(new InvalidOperationException("probe"));

        Assert.Equal("SOURCE_ENTRY_MISSING", mapped.Code);

        // The message must stay exactly the code: existing assertions and the frozen vocabulary depend on it.
        Assert.Equal("SOURCE_ENTRY_MISSING", mapped.Message);
    }

    [Fact]
    public void UnlistedException_OriginalTypeIsObservable()
    {
        var mapped = SourceReadCoordinator.MapMintFailure(new InvalidOperationException("probe"));

        Assert.NotNull(mapped.InnerException);
        Assert.Equal(nameof(InvalidOperationException), mapped.OriginalExceptionType);
    }

    [Fact]
    public void EnumeratedExceptions_KeepTheirOwnCodes_AndCarryTheOrigin()
    {
        var missing = SourceReadCoordinator.MapMintFailure(new FileNotFoundException("gone"));
        Assert.Equal("SOURCE_ENTRY_MISSING", missing.Code);
        Assert.Equal(nameof(FileNotFoundException), missing.OriginalExceptionType);

        var denied = SourceReadCoordinator.MapMintFailure(new UnauthorizedAccessException("nope"));
        Assert.Equal("SOURCE_ENTRY_MISSING", denied.Code);
        Assert.Equal(nameof(UnauthorizedAccessException), denied.OriginalExceptionType);

        var changed = SourceReadCoordinator.MapMintFailure(new IOException("busy"));
        Assert.Equal("FILE_IDENTITY_CHANGED", changed.Code);
        Assert.Equal(nameof(IOException), changed.OriginalExceptionType);

        var invalid = SourceReadCoordinator.MapMintFailure(new ArgumentException("bad"));
        Assert.Equal("SOURCE_ACCESS_DENIED", invalid.Code);
        Assert.Equal(nameof(ArgumentException), invalid.OriginalExceptionType);
    }
}
