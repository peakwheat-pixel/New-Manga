using NewManga.App.Services;
using NewManga.CoreClient;
using NewManga.Host;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-A-2 (audit P-02, contract §5.2): the Run control service seam. Wire facts checked against
/// <c>src/bootstrap/core_service.py::_dispatch_run_command</c> + <c>src/application/tasks/service.py</c>:
/// StartRun needs command/scope/idempotency_key (scope must be a frozen PipelineScope variant);
/// ControlRun maps Pause→pause, Resume→continue, Stop→stop, Restart→restart (key only for restart);
/// ResumeBlockedRun takes run_id only; GetRunSnapshot/GetTaskProjection take run_id;
/// RetryFailedTargets needs run_id + idempotency_key. All six are registered at protocol minor 3.
/// </summary>
public sealed class RunControllerNullFakeTests
{
    private static readonly NullHostController Controller = NullHostController.Instance;

    private static RunStartRequest Request(string command = "translate_all", string key = "n/a")
    {
        return new RunStartRequest(
            command,
            new Dictionary<string, object?> { ["kind"] = "chapter", ["chapter_id"] = "chapter-1" },
            null,
            key);
    }

    [Fact]
    public async Task NullController_StartRun_IsDeterministicAndReusesIdempotencyKey()
    {
        var key = "null-key-" + Guid.NewGuid().ToString("N");
        var first = await Controller.StartRunAsync(Request(key: key));
        Assert.NotNull(first);
        Assert.StartsWith("null-run-", first!.RunId, StringComparison.Ordinal);
        Assert.Equal("pending", first.Status);

        // Same key + same fingerprint reuses the accepted run (the Core returns created=false).
        var reuse = await Controller.StartRunAsync(Request(key: key));
        Assert.NotNull(reuse);
        Assert.Equal(first.RunId, reuse!.RunId);

        // Same key, different request → the Core's IDEMPOTENCY_KEY_REUSED case.
        Assert.Null(await Controller.StartRunAsync(Request(command: "rerender_all", key: key)));
    }

    [Fact]
    public async Task NullController_StartRun_RefusesMissingScopeOrKey()
    {
        Assert.Null(await Controller.StartRunAsync(new RunStartRequest("translate_all", new Dictionary<string, object?>(), null, " ")));
        Assert.Null(await Controller.StartRunAsync(new RunStartRequest(" ", new Dictionary<string, object?> { ["kind"] = "book", ["book_id"] = "b" }, null, "k")));
        Assert.Null(await Controller.StartRunAsync(Request(key: "cancel-key"), new CancellationToken(canceled: true)));
    }

    [Fact]
    public async Task NullController_ControlRun_FollowsTheFrozenTransitionTable()
    {
        var started = await Controller.StartRunAsync(Request(key: "null-control-" + Guid.NewGuid().ToString("N")));
        Assert.NotNull(started);

        // Core: pause requires running → a freshly accepted (pending) run is an invalid transition.
        Assert.Null(await Controller.ControlRunAsync(started!.RunId, RunControlAction.Pause));
        // Core: stop is valid for pending → cancelled.
        var stopped = await Controller.ControlRunAsync(started.RunId, RunControlAction.Stop);
        Assert.NotNull(stopped);
        Assert.Equal("cancelled", stopped!.Status);
        // Stopping a cancelled run is not a valid transition.
        Assert.Null(await Controller.ControlRunAsync(started.RunId, RunControlAction.Stop));

        // Restart always needs the caller's key (R-08) — refused before any lookup.
        Assert.Null(await Controller.ControlRunAsync(started.RunId, RunControlAction.Restart));
        Assert.Null(await Controller.ControlRunAsync("missing-run", RunControlAction.Stop));
    }

    [Fact]
    public async Task NullController_SnapshotAndProjection_EchoStateWithoutFabricatingProgress()
    {
        var started = await Controller.StartRunAsync(Request(key: "null-read-" + Guid.NewGuid().ToString("N")));
        Assert.NotNull(started);

        var snapshot = await Controller.GetRunSnapshotAsync(started!.RunId);
        Assert.NotNull(snapshot);
        Assert.Equal(started.RunId, snapshot!.RunId);
        Assert.Equal("translate_all", snapshot.Command);
        Assert.Equal("chapter", snapshot.Scope.Kind);
        Assert.Equal("chapter-1", snapshot.Scope.ChapterId);
        Assert.Empty(snapshot.Targets); // the fake has no pages; no target rows are invented
        Assert.Equal("pending", snapshot.Status);

        var projection = await Controller.GetTaskProjectionAsync(started.RunId);
        Assert.NotNull(projection);
        Assert.Equal(started.RunId, projection!.RunId);
        Assert.Empty(projection.Rows);
        Assert.Empty(projection.Tasks);
        Assert.Null(projection.Counts.Total); // unknown stays unknown
        Assert.Null(projection.OverallProgress);

        Assert.Null(await Controller.GetRunSnapshotAsync("missing-run"));
        Assert.Null(await Controller.GetTaskProjectionAsync("missing-run"));
    }

    [Fact]
    public async Task NullController_ResumeAndRetry_RefuseWithoutTheCoreState()
    {
        var started = await Controller.StartRunAsync(Request(key: "null-retry-" + Guid.NewGuid().ToString("N")));
        Assert.NotNull(started);

        // resume_blocked_run only works for a blocked run.
        Assert.Null(await Controller.ResumeBlockedRunAsync(started!.RunId));
        // retry_failed_targets only works after completed_with_failures and needs the key.
        Assert.Null(await Controller.RetryFailedTargetsAsync(started.RunId, " "));
        Assert.Null(await Controller.RetryFailedTargetsAsync(started.RunId, "retry-key"));
        Assert.Null(await Controller.RetryFailedTargetsAsync("missing-run", "retry-key"));
    }
}

/// <summary>V11R-A-2 AC6: the UI test double exposes the same recording + typed-failure channels.</summary>
public sealed class RunControllerUiSeamTests
{
    private static FakeHostController Ready() => new(FakeHostController.ReadySnapshot("书一"));

    private static RunStartRequest Request() => new(
        "translate_all",
        new Dictionary<string, object?> { ["kind"] = "chapter", ["chapter_id"] = "chapter-0" },
        null,
        "ui-key");

    [Fact]
    public async Task FakeController_RecordsRequestsAndScriptsTypedOutcomes()
    {
        var controller = Ready();
        var started = await controller.StartRunAsync(Request());
        Assert.NotNull(started);
        var recorded = controller.StartRunRequests.Single();
        Assert.Equal("translate_all", recorded.Command);
        Assert.Equal("ui-key", recorded.IdempotencyKey);
        Assert.Equal("chapter-0", (string?)recorded.Scope["chapter_id"]);

        controller.ScriptedTaskProjections.Enqueue(null);
        Assert.Null(await controller.GetTaskProjectionAsync(started!.RunId));
        Assert.Equal("SCRIPTED_FAILURE", controller.Snapshot.LastError);
        Assert.Contains(started.RunId, controller.TaskProjectionRequests);

        Assert.Null(await controller.ControlRunAsync(started.RunId, RunControlAction.Restart));
        Assert.Equal("INVALID_REQUEST", controller.Snapshot.LastError);
        Assert.Null(await controller.RetryFailedTargetsAsync(started.RunId, " "));
        Assert.Equal("INVALID_REQUEST", controller.Snapshot.LastError);
    }

    [Fact]
    public async Task FakeController_DrivesRealControlTransitions()
    {
        var controller = Ready();
        var started = await controller.StartRunAsync(Request());
        Assert.NotNull(started);

        // Stop from pending → cancelled, exactly like the frozen Core transition table.
        var stopped = await controller.ControlRunAsync(started!.RunId, RunControlAction.Stop);
        Assert.NotNull(stopped);
        Assert.Equal("cancelled", stopped!.Status);
        Assert.Equal((started.RunId, RunControlAction.Stop, (string?)null), controller.ControlRunRequests.Single());
    }
}

/// <summary>
/// V11R-A-2: local (no sidecar) refusal paths of the production controller. Required arguments and the
/// R-08 key rules must be refused before any wire frame with a typed <see cref="HostViewSnapshot.LastError"/>.
/// </summary>
public sealed class RunControllerHostLocalFailureTests
{
    private static HostOptions Options() => new()
    {
        DataRoot = Path.Combine(Path.GetTempPath(), "newmanga-a2-local-" + Guid.NewGuid().ToString("N")[..10]),
        LogDirectory = Path.Combine(Path.GetTempPath(), "newmanga-a2-local-logs"),
        SidecarDirectoryOverride = Path.Combine(Path.GetTempPath(), "no-sidecars-in-this-test"),
        MutexName = @"Local\NewManga.App.Tests.A2.Local." + Guid.NewGuid().ToString("N")[..10],
        DetectLegacyShell = false,
        ParityReached = true,
    };

    private static RunStartRequest Request(string? key = "k-1") => new(
        "translate_all",
        new Dictionary<string, object?> { ["kind"] = "book", ["book_id"] = "book-1" },
        null,
        key!);

    [Fact]
    public async Task RunWrites_BeforeStart_PublishHostNotReady()
    {
        await using var controller = new HostController(Options());

        Assert.Null(await controller.StartRunAsync(Request()));
        Assert.Equal("HOST_NOT_READY", controller.Snapshot.LastError);

        Assert.Null(await controller.ControlRunAsync("run-1", RunControlAction.Stop));
        Assert.Equal("HOST_NOT_READY", controller.Snapshot.LastError);

        Assert.Null(await controller.ResumeBlockedRunAsync("run-1"));
        Assert.Equal("HOST_NOT_READY", controller.Snapshot.LastError);

        Assert.Null(await controller.RetryFailedTargetsAsync("run-1", "retry-key"));
        Assert.Equal("HOST_NOT_READY", controller.Snapshot.LastError);

        Assert.Null(await controller.GetRunSnapshotAsync("run-1"));
        Assert.Equal("HOST_NOT_READY", controller.Snapshot.LastError);
    }

    [Fact]
    public async Task RunWrites_MissingMandatoryIdempotencyKey_AreRefusedLocally()
    {
        await using var controller = new HostController(Options());

        Assert.Null(await controller.StartRunAsync(Request(key: " ")));
        Assert.Equal("INVALID_REQUEST", controller.Snapshot.LastError);

        Assert.Null(await controller.ControlRunAsync("run-1", RunControlAction.Restart));
        Assert.Equal("INVALID_REQUEST", controller.Snapshot.LastError);

        Assert.Null(await controller.RetryFailedTargetsAsync("run-1", "  "));
        Assert.Equal("INVALID_REQUEST", controller.Snapshot.LastError);

        Assert.Null(await controller.StartRunAsync(null!));
        Assert.Equal("INVALID_REQUEST", controller.Snapshot.LastError);
    }

    [Fact]
    public async Task RunRequests_CancelledToken_PublishCancelled()
    {
        await using var controller = new HostController(Options());
        using var cancelled = new CancellationTokenSource();
        cancelled.Cancel();

        Assert.Null(await controller.StartRunAsync(Request(), cancelled.Token));
        Assert.Equal("CANCELLED", controller.Snapshot.LastError);

        Assert.Null(await controller.GetTaskProjectionAsync("run-1", cancelled.Token));
        Assert.Equal("CANCELLED", controller.Snapshot.LastError);
    }
}

/// <summary>
/// V11R-A-2 AC6 integration: the real <see cref="HostController"/> against the frozen sidecars.
/// Success / typed Core errors / idempotent reuse / invalid transition / read-only are all driven
/// through the registered C056-C061 commands. Real per-page progress needs a seeded data root.
/// </summary>
public sealed class RunControllerHostIntegrationTests
{
    [RunSidecarFact]
    public async Task RunCommands_MapCoreErrors_AndReuseIdempotencyKeys()
    {
        var options = RunFixture.CreateOptions("v11r-a2-errors", parity: true, out var dataRoot);
        var controller = new HostController(options);
        try
        {
            await controller.StartAsync();
            Assert.True(
                controller.Snapshot.State == HostViewState.Ready,
                $"host not ready: {controller.Snapshot.ErrorCode} {controller.Snapshot.ErrorMessage}");

            var book = await CreateEmptyChapterAsync(controller, "V11R-A-2 错误映射");
            var chapterId = book.ChapterId;
            var chapterScope = new Dictionary<string, object?>
            {
                ["kind"] = "chapter",
                ["chapter_id"] = chapterId,
            };

            // A chapter without pages expands to no targets: Core EMPTY_TARGET_SELECTION → INVALID_REQUEST.
            Assert.Null(await controller.StartRunAsync(
                new RunStartRequest("translate_all", chapterScope, null, "empty-scope-key")));
            Assert.Equal("INVALID_REQUEST", controller.Snapshot.LastError);

            // Unknown run ids keep the Core's TARGET_NOT_FOUND on every read/control face.
            Assert.Null(await controller.GetRunSnapshotAsync("missing-run"));
            Assert.Equal("TARGET_NOT_FOUND", controller.Snapshot.LastError);

            Assert.Null(await controller.GetTaskProjectionAsync("missing-run"));
            Assert.Equal("TARGET_NOT_FOUND", controller.Snapshot.LastError);

            Assert.Null(await controller.ControlRunAsync("missing-run", RunControlAction.Stop, "restart-key"));
            Assert.Equal("TARGET_NOT_FOUND", controller.Snapshot.LastError);

            Assert.Null(await controller.ResumeBlockedRunAsync("missing-run"));
            Assert.Equal("TARGET_NOT_FOUND", controller.Snapshot.LastError);

            Assert.Null(await controller.RetryFailedTargetsAsync("missing-run", "retry-key"));
            Assert.Equal("TARGET_NOT_FOUND", controller.Snapshot.LastError);

            // Cancellation is local: no wire frame, typed CANCELLED status.
            Assert.Null(await controller.StartRunAsync(
                new RunStartRequest("translate_all", chapterScope, null, "cancelled-key"),
                new CancellationToken(canceled: true)));
            Assert.Equal("CANCELLED", controller.Snapshot.LastError);
        }
        finally
        {
            await controller.DisposeAsync();
            RunFixture.TryDeleteDirectory(dataRoot);
        }
    }

    [RunBookFixtureFact]
    public async Task RunCommands_StartSuccessfulRun_ProjectRealPerPageState_AndReuseKey()
    {
        var options = RunFixture.CreateOptionsWithBookFixture("v11r-a2-run", parity: true, out var dataRoot);
        var controller = new HostController(options);
        try
        {
            await controller.StartAsync();
            Assert.True(
                controller.Snapshot.State == HostViewState.Ready,
                $"host not ready: {controller.Snapshot.ErrorCode} {controller.Snapshot.ErrorMessage}");

            var book = controller.Snapshot.Books.Single();
            var chapter = (await controller.ListChaptersAsync(book.BookId)).Single();
            var pages = await controller.ListChapterPagesAsync(chapter.ChapterId);
            Assert.NotEmpty(pages);

            var request = new RunStartRequest(
                "translate_all",
                new Dictionary<string, object?>
                {
                    ["kind"] = "chapter",
                    ["chapter_id"] = chapter.ChapterId,
                },
                null,
                "run-key-" + Guid.NewGuid().ToString("N"));

            // AC2/AC6 success: C056 → Core StartRun creates the run.
            var started = await controller.StartRunAsync(request);
            Assert.NotNull(started);
            Assert.False(string.IsNullOrWhiteSpace(started!.RunId));
            Assert.Equal("pending", started.Status);
            Assert.Null(controller.Snapshot.LastError);

            // AC6 idempotent reuse: the same key + fingerprint returns the accepted run.
            var reused = await controller.StartRunAsync(request);
            Assert.NotNull(reused);
            Assert.Equal(started.RunId, reused!.RunId);

            // AC5 IDEMPOTENCY_KEY_REUSED: same key, different request.
            Assert.Null(await controller.StartRunAsync(new RunStartRequest(
                "rerender_all",
                request.Scope,
                null,
                request.IdempotencyKey)));
            Assert.Equal("IDEMPOTENCY_KEY_REUSED", controller.Snapshot.LastError);

            // AC2: C059 snapshot is the real Core projection (targets == chapter pages).
            var snapshot = await controller.GetRunSnapshotAsync(started.RunId);
            Assert.NotNull(snapshot);
            Assert.Equal(started.RunId, snapshot!.RunId);
            Assert.Equal("translate_all", snapshot.Command);
            Assert.Equal(chapter.ChapterId, snapshot.Scope.ChapterId);
            Assert.Equal(pages.Count, snapshot.Targets.Count);
            Assert.All(snapshot.Targets, target => Assert.Equal("page", target.TargetType));

            // AC4: C060 projection carries the real per-page rows / stage flow / counters. A freshly
            // accepted run is still pending until the Core scheduler plans it (<= 250 ms poll), so the
            // test waits for the planned projection instead of asserting a made-up immediate state.
            TaskProjectionInfo? projection = null;
            for (var attempt = 0; attempt < 40; attempt++)
            {
                projection = await controller.GetTaskProjectionAsync(started.RunId);
                Assert.NotNull(projection);
                if (projection!.Rows.Count > 0)
                {
                    break;
                }

                await Task.Delay(250);
            }

            Assert.NotNull(projection);
            Assert.Equal(started.RunId, projection!.RunId);
            Assert.False(string.IsNullOrWhiteSpace(projection.RunStatus));
            Assert.Equal(pages.Count, projection.Rows.Count);
            Assert.Equal(pages.Count, projection.Counts.Total);
            Assert.NotEmpty(projection.StepFlow);
            Assert.All(projection.Rows, row => Assert.False(string.IsNullOrWhiteSpace(row.Status)));

            // AC6 invalid transition: "continue" only accepts a paused/interrupted run (this one is
            // pending/running/finished, never paused) → INVALID_RUN_TRANSITION.
            Assert.Null(await controller.ControlRunAsync(started.RunId, RunControlAction.Resume));
            Assert.Equal("INVALID_RUN_TRANSITION", controller.Snapshot.LastError);
        }
        finally
        {
            await controller.DisposeAsync();
            RunFixture.TryDeleteDirectory(dataRoot);
        }
    }

    [RunSidecarFact]
    public async Task RunCommands_WhenReadOnly_PublishHostReadOnly()
    {
        var options = RunFixture.CreateOptions("v11r-a2-readonly", parity: false, out var dataRoot);
        var controller = new HostController(options);
        try
        {
            await controller.StartAsync();
            Assert.True(
                controller.Snapshot.State == HostViewState.Ready,
                $"host not ready: {controller.Snapshot.ErrorCode} {controller.Snapshot.ErrorMessage}");
            Assert.False(controller.Snapshot.WritesAllowed);

            var request = new RunStartRequest(
                "translate_all",
                new Dictionary<string, object?> { ["kind"] = "book", ["book_id"] = "any-book" },
                null,
                "readonly-key");

            Assert.Null(await controller.StartRunAsync(request));
            Assert.Equal("HOST_READ_ONLY", controller.Snapshot.LastError);

            Assert.Null(await controller.ControlRunAsync("run-1", RunControlAction.Stop));
            Assert.Equal("HOST_READ_ONLY", controller.Snapshot.LastError);

            Assert.Null(await controller.RetryFailedTargetsAsync("run-1", "retry-key"));
            Assert.Equal("HOST_READ_ONLY", controller.Snapshot.LastError);

            // Reads stay allowed in read-only mode; the Core's typed error is still surfaced.
            Assert.Null(await controller.GetRunSnapshotAsync("missing-run"));
            Assert.Equal("TARGET_NOT_FOUND", controller.Snapshot.LastError);
        }
        finally
        {
            await controller.DisposeAsync();
            RunFixture.TryDeleteDirectory(dataRoot);
        }
    }

    private static async Task<(string BookId, string ChapterId)> CreateEmptyChapterAsync(
        HostController controller,
        string label)
    {
        var title = label + " " + Guid.NewGuid().ToString("N")[..8];
        Assert.True(await controller.TryCreateBookAsync(title));
        var book = controller.Snapshot.Books.Single(candidate => candidate.Title == title);
        var chapter = await controller.CreateChapterAsync(book.BookId, "第 1 章");
        Assert.NotNull(chapter);
        return (book.BookId, chapter!.ChapterId);
    }
}

/// <summary>V11R-A-2: Run integration fact — needs the AC11 sidecar copy only.</summary>
public sealed class RunSidecarFactAttribute : FactAttribute
{
    public RunSidecarFactAttribute()
    {
        if (!RunFixture.TryGetSidecarDirectory(out _, out var reason))
        {
            Skip = reason;
        }
    }
}

/// <summary>V11R-A-2: Run integration fact — needs the sidecar copy AND the BOOK-FIXTURE data root.</summary>
public sealed class RunBookFixtureFactAttribute : FactAttribute
{
    public RunBookFixtureFactAttribute()
    {
        if (!RunFixture.TryGetSidecarDirectory(out _, out var sidecarReason))
        {
            Skip = sidecarReason;
        }
        else if (!RunFixture.TryGetBookFixtureRoot(out _, out var fixtureReason))
        {
            Skip = fixtureReason;
        }
    }
}

/// <summary>
/// V11R-A-2: test environment for the Run integration facts. Mirrors the existing Host fixture
/// conventions: AC11 sidecar copy via <c>NEWMANGA_CORECLIENT_SIDECAR_DIR</c>, isolated writable data
/// root, optional BOOK-FIXTURE copy via <c>NEWMANGA_BOOK_FIXTURE_ROOT</c>.
/// </summary>
internal static class RunFixture
{
    private const string SidecarVariable = "NEWMANGA_CORECLIENT_SIDECAR_DIR";
    private const string EvidenceVariable = "NEWMANGA_EVIDENCE_DIR";
    private const string BookFixtureVariable = "NEWMANGA_BOOK_FIXTURE_ROOT";
    private static string DefaultBookFixtureRoot => TestWorkspacePaths.Path("task-envs/BOOK-FIXTURE-1/isolated-data");

    public static bool TryGetSidecarDirectory(out string directory, out string reason)
    {
        directory = Environment.GetEnvironmentVariable(SidecarVariable) ?? string.Empty;
        if (string.IsNullOrWhiteSpace(directory))
        {
            reason = $"reason: needs sidecar fixture - set {SidecarVariable} or run " +
                     "apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy)";
            return false;
        }

        foreach (var exe in new[] { "core_service.exe", "host_bridge.exe" })
        {
            if (!File.Exists(Path.Combine(directory, exe)))
            {
                reason = $"reason: needs sidecar fixture - {exe} missing under {SidecarVariable}";
                return false;
            }
        }

        reason = string.Empty;
        return true;
    }

    public static bool TryGetBookFixtureRoot(out string dataRoot, out string reason)
    {
        dataRoot = Environment.GetEnvironmentVariable(BookFixtureVariable) ?? string.Empty;
        if (string.IsNullOrWhiteSpace(dataRoot) || !Directory.Exists(dataRoot))
        {
            dataRoot = DefaultBookFixtureRoot;
        }

        if (!Directory.Exists(dataRoot) || !File.Exists(Path.Combine(dataRoot, "library.db")))
        {
            reason = $"reason: needs BOOK-FIXTURE data root - set {BookFixtureVariable} " +
                     "(an isolated root with library.db and managed/)";
            return false;
        }

        reason = string.Empty;
        return true;
    }

    public static HostOptions CreateOptions(string label, bool parity, out string dataRoot)
    {
        dataRoot = NewDataRoot(label);
        return Options(label, dataRoot, parity);
    }

    /// <summary>
    /// Copies the durable BOOK-FIXTURE state (library.db + WAL sidecars + managed/) into a disposable
    /// root. Derived caches are intentionally not copied: they are bound to the source root identity.
    /// </summary>
    public static HostOptions CreateOptionsWithBookFixture(string label, bool parity, out string dataRoot)
    {
        if (!TryGetBookFixtureRoot(out var source, out var reason))
        {
            throw new InvalidOperationException(reason);
        }

        dataRoot = NewDataRoot(label);
        foreach (var file in Directory.EnumerateFiles(source, "*", SearchOption.AllDirectories))
        {
            var relative = Path.GetRelativePath(source, file);
            var firstSegment = relative.Split(Path.DirectorySeparatorChar, StringSplitOptions.RemoveEmptyEntries)
                .FirstOrDefault() ?? string.Empty;
            if (firstSegment.Equals("logs", StringComparison.OrdinalIgnoreCase) ||
                firstSegment.Equals("backups", StringComparison.OrdinalIgnoreCase) ||
                firstSegment.Equals("derived", StringComparison.OrdinalIgnoreCase) ||
                firstSegment.Equals("catalog", StringComparison.OrdinalIgnoreCase) ||
                relative.EndsWith(".lock", StringComparison.OrdinalIgnoreCase))
            {
                continue;
            }

            var target = Path.Combine(dataRoot, relative);
            Directory.CreateDirectory(Path.GetDirectoryName(target)!);
            File.Copy(file, target, overwrite: true);
        }

        return Options(label, dataRoot, parity);
    }

    private static HostOptions Options(string label, string dataRoot, bool parity)
    {
        if (!TryGetSidecarDirectory(out var sidecarDirectory, out var reason))
        {
            throw new InvalidOperationException(reason);
        }

        var evidence = Environment.GetEnvironmentVariable(EvidenceVariable);
        var logDirectory = string.IsNullOrWhiteSpace(evidence)
            ? Path.Combine(Path.GetTempPath(), "newmanga-app-tests-logs", label)
            : Path.Combine(evidence, "host-logs", label);
        Directory.CreateDirectory(logDirectory);

        return new HostOptions
        {
            DataRoot = dataRoot,
            LogDirectory = logDirectory,
            SidecarDirectoryOverride = sidecarDirectory,
            MutexName = @"Local\NewManga.App.Tests.A2." + Guid.NewGuid().ToString("N")[..12],
            DetectLegacyShell = false,
            ParityReached = parity,
            EnableWireEvidence = true,
            StartupTimeout = TimeSpan.FromSeconds(90),
            RequestTimeout = TimeSpan.FromSeconds(60),
        };
    }

    private static string NewDataRoot(string label)
    {
        var root = Path.Combine(
            Path.GetTempPath(),
            "newmanga-app-tests",
            label + "-" + Guid.NewGuid().ToString("N")[..10]);
        foreach (var child in new[] { "derived", "catalog", "managed" })
        {
            Directory.CreateDirectory(Path.Combine(root, child));
        }

        return root;
    }

    public static void TryDeleteDirectory(string path)
    {
        try
        {
            if (Directory.Exists(path))
            {
                Directory.Delete(path, recursive: true);
            }
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
        {
            // best effort; temp roots are disposable
        }
    }
}
