using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Wire;

namespace NewManga.Host.Tests;

public sealed class Fea10PrereqProjectionTests
{
    private static readonly string[] C08Codes =
        { "RUN_STALE_PREVIEW", "RUN_PREVIEW_EXPIRED", "RUN_SNAPSHOT_INCOMPLETE" };

    [Theory]
    [InlineData("RUN_STALE_PREVIEW")]
    [InlineData("RUN_PREVIEW_EXPIRED")]
    [InlineData("RUN_SNAPSHOT_INCOMPLETE")]
    public void BeforeRegistration_NewCodesDegradeWithoutChangingCode(string code)
    {
        // Model the M2-C1 rev 2.11 registration, using the SAME production projection.
        var beforeRegistration = HostCommandRegistry.AllowedRunErrorCodes
            .Except(C08Codes).ToHashSet(StringComparer.Ordinal);
        var source = new CoreOperationException(code, "unavailable", true,
            "secret=do-not-leak C:\\private\\source.png", "request-1");
        var projected = HostCommandDispatcher.ProjectRunError(source, beforeRegistration);

        Assert.Equal(code, projected.Code);
        Assert.Equal("unknown", projected.Category);
        Assert.False(projected.Retryable);
        Assert.Equal("Run operation failed", projected.CoreMessage);
        Assert.Equal("request-1", projected.RequestId);
        Assert.DoesNotContain("do-not-leak", projected.Message);
        Assert.DoesNotContain("C:\\private", projected.Message);
        Assert.Equal("unavailable", source.Category); // source/wire remains intact
        Assert.True(source.Retryable);
    }

    [Theory]
    [InlineData("RUN_STALE_PREVIEW", "conflict", false)]
    [InlineData("RUN_PREVIEW_EXPIRED", "conflict", false)]
    [InlineData("RUN_SNAPSHOT_INCOMPLETE", "unavailable", true)]
    public void AfterRegistration_UsesFrozenValuesAndSafeMessage(string code, string category, bool retryable)
    {
        Assert.Contains(code, HostCommandRegistry.AllowedRunErrorCodes);
        var source = new CoreOperationException(code, "internal", !retryable,
            "secret=do-not-leak C:\\private\\source.png", "request-2");
        var projected = HostCommandDispatcher.ProjectRunError(source, HostCommandRegistry.AllowedRunErrorCodes);

        Assert.Equal(code, projected.Code);
        Assert.Equal(category, projected.Category);
        Assert.Equal(retryable, projected.Retryable);
        Assert.Equal("request-2", projected.RequestId);
        Assert.DoesNotContain("do-not-leak", projected.Message);
        Assert.DoesNotContain("C:\\private", projected.Message);
    }

    [Theory]
    [InlineData("RUN_FUTURE_ERROR")]
    [InlineData("run_stale_preview")]
    [InlineData("RUN_STALE_PREVIEW ")]
    public void UnknownCode_CannotEnableSpecificRecoveryOrRetry(string code)
    {
        var projected = HostCommandDispatcher.ProjectRunError(
            new CoreOperationException(code, "conflict", true, "prepare again", null),
            HostCommandRegistry.AllowedRunErrorCodes);
        Assert.Equal(code, projected.Code);
        Assert.Equal("unknown", projected.Category);
        Assert.False(projected.Retryable);
        Assert.Equal("Run operation failed", projected.CoreMessage);
        Assert.Null(projected.RequestId);
        // No actionable registered category or retry bit escapes. The helper is pure:
        // there is no callback, command send, candidate store or recovery operation.
    }

    [Theory]
    [InlineData("INVALID_REQUEST", "validation", false)]
    [InlineData("TARGET_NOT_FOUND", "not_found", false)]
    [InlineData("INVALID_RUN_TRANSITION", "conflict", false)]
    [InlineData("IDEMPOTENCY_KEY_REUSED", "conflict", false)]
    [InlineData("MISSING_REQUIRED_INPUT", "validation", false)]
    [InlineData("SETTINGS_UNAVAILABLE", "unavailable", false)]
    [InlineData("PROVIDER_NOT_CONFIGURED", "internal", false)]
    public void ExistingRegisteredMapping_IsPreserved(string code, string category, bool retryable)
    {
        var source = new CoreOperationException(code, category, retryable, "existing safe message", "old-req");
        Assert.Same(source, HostCommandDispatcher.ProjectRunError(source, HostCommandRegistry.AllowedRunErrorCodes));
    }

    [Theory]
    [InlineData("library_start_run", "StartRun")]
    [InlineData("library_control_run", "ControlRun")]
    [InlineData("library_resume_blocked_run", "ResumeBlockedRun")]
    [InlineData("library_get_run_snapshot", "GetRunSnapshot")]
    [InlineData("library_get_task_projection", "GetTaskProjection")]
    [InlineData("library_retry_failed_targets", "RetryFailedTargets")]
    public void ExistingRunRoutes_KeepMinor3(string name, string coreCommand)
    {
        Assert.True(HostCommandRegistry.IsRunCommand(name));
        var route = HostCommandRegistry.Get(name);
        Assert.Equal(coreCommand, route.CoreCommand);
        Assert.Equal(3, route.CoreMinor);
    }

    [Fact]
    public void Registration_DoesNotIntroduceRunnableCommandsOrAlterOtherFamilies()
    {
        Assert.False(HostCommandRegistry.IsRunCommand("library_start_export"));
        Assert.False(HostCommandRegistry.IsRunCommand("drafts_apply"));
        Assert.DoesNotContain(HostCommandRegistry.All.Values,
            route => route.CoreCommand is "PrepareRun" or "AcceptRun");
        Assert.Equal(3, CoreProtocol.DefaultMinor);
    }
}
