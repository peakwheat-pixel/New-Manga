using System.Text.Json;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Wire;
using NewManga.Host.Sources;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// FEA-11-SCAN-1 (AC-S1/S2/S3/S5): the Host-side read-only periodic scan scheduler, driven by a fake
/// executor ("fake core") and a manual <see cref="TimeProvider"/>. Ticks are always invoked through
/// <see cref="SourceScanScheduler.TickAsync"/> or a manually advanced clock — the tests never sleep.
/// </summary>
public sealed class SourceScanSchedulerTests
{
    // ---------------------------------------------------------------------------------------
    // Shared infrastructure: manual clock + fake core + log capture.
    // ---------------------------------------------------------------------------------------

    private sealed class ManualTimeProvider : TimeProvider
    {
        private readonly object _gate = new();
        private readonly List<ManualTimer> _timers = new();
        private DateTimeOffset _now;
        private TaskCompletionSource<bool> _timerScheduled = new(TaskCreationOptions.RunContinuationsAsynchronously);

        public ManualTimeProvider(DateTimeOffset start) => _now = start;

        public override DateTimeOffset GetUtcNow()
        {
            lock (_gate) return _now;
        }

        public override ITimer CreateTimer(TimerCallback callback, object? state, TimeSpan dueTime, TimeSpan period)
        {
            var timer = new ManualTimer(this, callback, state);
            timer.Change(dueTime, period);
            TaskCompletionSource<bool> scheduled;
            lock (_gate)
            {
                _timers.Add(timer);
                scheduled = _timerScheduled;
                _timerScheduled = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
            }

            scheduled.TrySetResult(true);
            return timer;
        }

        /// <summary>Signals once at least one timer exists (used to await the loop's first delay deterministically).</summary>
        public Task WaitForPendingTimerAsync()
        {
            lock (_gate)
            {
                if (_timers.Count > 0) return Task.CompletedTask;
                return _timerScheduled.Task;
            }
        }

        public void Advance(TimeSpan delta)
        {
            List<ManualTimer> due;
            lock (_gate)
            {
                _now += delta;
                due = _timers.Where(timer => timer.IsDue(_now)).ToList();
            }

            foreach (var timer in due)
            {
                timer.Fire(_now);
            }
        }

        private void Remove(ManualTimer timer)
        {
            lock (_gate) _timers.Remove(timer);
        }

        private sealed class ManualTimer(ManualTimeProvider owner, TimerCallback callback, object? state) : ITimer
        {
            private readonly object _gate = new();
            private DateTimeOffset? _dueAt;
            private bool _disposed;

            public bool Change(TimeSpan dueTime, TimeSpan period)
            {
                lock (_gate)
                {
                    if (_disposed) return false;
                    _dueAt = dueTime == Timeout.InfiniteTimeSpan ? null : owner.GetUtcNow() + dueTime;
                }

                return true;
            }

            internal bool IsDue(DateTimeOffset now)
            {
                lock (_gate) return !_disposed && _dueAt is { } due && due <= now;
            }

            internal void Fire(DateTimeOffset now)
            {
                TimerCallback? fire;
                object? fireState;
                lock (_gate)
                {
                    if (_disposed || _dueAt is not { } due || due > now) return;
                    _dueAt = null;
                    fire = callback;
                    fireState = state;
                }

                fire(fireState);
            }

            public void Dispose()
            {
                lock (_gate) _disposed = true;
                owner.Remove(this);
            }

            public ValueTask DisposeAsync()
            {
                Dispose();
                return ValueTask.CompletedTask;
            }
        }
    }

    private sealed class FakeScanExecutor : ISourceScanExecutor
    {
        private readonly object _gate = new();
        private readonly List<(int Count, TaskCompletionSource<bool> Signal)> _scanWaiters = new();

        public List<string> ScannedSourceIds { get; } = new();

        public List<string> IssuedCommands { get; } = new();

        public Func<SourceScanTarget, SourceScanOutcome>? Script { get; set; }

        public SourceScanBudget? Budget { get; set; }

        public TaskCompletionSource<bool>? Block { get; set; }

        public int ScanCalls => ScannedSourceIds.Count;

        public int ActiveScans;
        public int MaxConcurrentScans;

        public SourceScanBudget? ProbeBudget(SourceScanTarget target) => Budget;

        public async Task<SourceScanOutcome> ScanAsync(SourceScanTarget target, CancellationToken cancellationToken)
        {
            List<TaskCompletionSource<bool>> signals;
            lock (_gate)
            {
                ScannedSourceIds.Add(target.SourceId);
                IssuedCommands.Add("ScanSourceSync");
                ActiveScans++;
                if (ActiveScans > MaxConcurrentScans) MaxConcurrentScans = ActiveScans;
                signals = _scanWaiters.Where(waiter => waiter.Count <= ScannedSourceIds.Count)
                    .Select(waiter => waiter.Signal).ToList();
                _scanWaiters.RemoveAll(waiter => waiter.Count <= ScannedSourceIds.Count);
            }

            foreach (var signal in signals) signal.TrySetResult(true);
            if (Block is { } block) await block.Task.ConfigureAwait(false);
            cancellationToken.ThrowIfCancellationRequested();
            var outcome = Script?.Invoke(target) ?? SourceScanOutcome.Ok(SourceScanCounts.Zero);
            lock (_gate) ActiveScans--;
            return outcome;
        }

        public Task WaitForScanCountAsync(int count)
        {
            lock (_gate)
            {
                if (ScannedSourceIds.Count >= count) return Task.CompletedTask;
                var signal = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
                _scanWaiters.Add((count, signal));
                return signal.Task;
            }
        }
    }

    private sealed class FakeTargetEnumerator : ISourceScanTargetEnumerator
    {
        private readonly object _gate = new();
        private readonly List<(int Count, TaskCompletionSource<bool> Signal)> _callWaiters = new();
        private readonly TaskCompletionSource<bool> _started =
            new(TaskCreationOptions.RunContinuationsAsynchronously);
        private int _calls;

        public int Calls
        {
            get
            {
                lock (_gate)
                {
                    return _calls;
                }
            }
        }

        public Func<int, SourceScanEnumerationResult>? Script { get; set; }

        public TaskCompletionSource<bool>? Block { get; set; }

        /// <summary>FEA-11-SCAN-RH-1: optional per-call gate awaited before the scripted result.</summary>
        public Func<int, Task>? WaitFor { get; set; }

        /// <summary>FEA-11-SCAN-RH-1 (AC-RH-2): blocks until the enumeration token is cancelled.</summary>
        public bool BlockUntilCancelled { get; set; }

        /// <summary>FEA-11-SCAN-RH-1 (AC-RH-2): true when the enumeration observed cancellation.</summary>
        public bool CancellationObserved { get; private set; }

        /// <summary>FEA-11-SCAN-RH-1: completes when the first enumeration call starts.</summary>
        public Task Started => _started.Task;

        public async Task<SourceScanEnumerationResult> EnumerateAsync(CancellationToken cancellationToken)
        {
            int call;
            List<TaskCompletionSource<bool>> signals;
            lock (_gate)
            {
                call = ++_calls;
                signals = _callWaiters.Where(waiter => waiter.Count <= call)
                    .Select(waiter => waiter.Signal).ToList();
                _callWaiters.RemoveAll(waiter => waiter.Count <= call);
            }

            _started.TrySetResult(true);
            foreach (var signal in signals) signal.TrySetResult(true);

            if (WaitFor is { } waitFor)
            {
                await waitFor(call).ConfigureAwait(false);
            }

            if (BlockUntilCancelled)
            {
                try
                {
                    await Task.Delay(Timeout.InfiniteTimeSpan, cancellationToken).ConfigureAwait(false);
                }
                catch (OperationCanceledException)
                {
                    CancellationObserved = true;
                    throw;
                }
            }

            if (Block is { } block)
            {
                await block.Task.ConfigureAwait(false);
            }

            cancellationToken.ThrowIfCancellationRequested();
            return Script?.Invoke(call) ?? SourceScanEnumerationResult.Completed(
                Array.Empty<SourceScanTarget>(), 0);
        }

        public Task WaitForCallsAsync(int count)
        {
            lock (_gate)
            {
                if (_calls >= count) return Task.CompletedTask;
                var signal = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
                _callWaiters.Add((count, signal));
                return signal.Task;
            }
        }
    }

    private static SourceScanTarget EnumeratedTarget(
        string sourceId,
        string? path = null,
        string registryId = "reg-1",
        int generation = 1,
        string? identityDigest = null,
        IReadOnlyList<string>? projectIds = null) =>
        new(
            sourceId,
            path ?? ("C:\\fixtures\\" + sourceId + ".zip"),
            projectIds ?? new[] { "b1" },
            "1",
            registryId,
            generation,
            "zip",
            identityDigest ?? new string('a', 64));

    private sealed class CapturedLog
    {
        public List<string> Info { get; } = new();

        public List<string> Warn { get; } = new();

        public List<string> Error { get; } = new();
    }

    private static readonly DateTimeOffset Start = new(2026, 11, 6, 1, 0, 0, TimeSpan.Zero);

    private static SourceScanTarget Target(string sourceId, string? path = null) =>
        new(sourceId, path ?? ("C:\\fixtures\\" + sourceId + ".zip"), new[] { "b1" }, "1");

    private static SourceScanScheduler NewScheduler(
        FakeScanExecutor executor,
        ManualTimeProvider clock,
        CapturedLog? log = null,
        SourceScanOptions? options = null,
        Action<string>? info = null,
        Action<string>? warn = null,
        Action<string, string>? error = null,
        ISourceScanTargetEnumerator? enumerator = null)
    {
        Action<string>? infoLog = info;
        Action<string>? warnLog = warn;
        Action<string, string>? errorLog = error;
        if (log is not null)
        {
            infoLog ??= line => log.Info.Add(line);
            warnLog ??= line => log.Warn.Add(line);
            errorLog ??= (code, message) => log.Error.Add(code + " " + message);
        }

        return new SourceScanScheduler(
            options ?? new SourceScanOptions { IntervalSeconds = 900 },
            executor,
            clock,
            infoLog,
            warnLog,
            errorLog,
            enumerator);
    }

    // ---------------------------------------------------------------------------------------
    // AC-S1: lifecycle, configuration, injected clock.
    // ---------------------------------------------------------------------------------------

    [Fact]
    public async Task Start_IsIdempotent_AndRunsASingleLoop()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor();
        var scheduler = NewScheduler(executor, clock);
        scheduler.RegisterTarget(Target("s1"));

        scheduler.Start();
        await clock.WaitForPendingTimerAsync().WaitAsync(TimeSpan.FromSeconds(10));
        scheduler.Start(); // must NOT create a second loop
        Assert.True(scheduler.IsRunning);

        clock.Advance(TimeSpan.FromSeconds(900));
        await executor.WaitForScanCountAsync(1).WaitAsync(TimeSpan.FromSeconds(10));
        // A second loop would have produced a second scan for the same single advance.
        Assert.Equal(1, executor.ScanCalls);

        await scheduler.DisposeAsync();
        Assert.False(scheduler.IsRunning);

        clock.Advance(TimeSpan.FromSeconds(900));
        Assert.Equal(1, executor.ScanCalls); // stopped: no further tick
    }

    [Fact]
    public async Task ManualTicks_UseTheInjectedClockForLastAndNextTick()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor();
        var scheduler = NewScheduler(executor, clock);
        scheduler.RegisterTarget(Target("s1"));

        await scheduler.TickAsync();
        var first = scheduler.Snapshot();
        Assert.Equal(Start, first.LastTickAt);
        Assert.Equal(Start.AddSeconds(900), first.NextTickAt);
        Assert.Equal(1, executor.ScanCalls);

        clock.Advance(TimeSpan.FromMinutes(5));
        await scheduler.TickAsync();
        var second = scheduler.Snapshot();
        Assert.Equal(Start.AddMinutes(5), second.LastTickAt);
        Assert.Equal(Start.AddMinutes(5).AddSeconds(900), second.NextTickAt);
        Assert.Equal(2, executor.ScanCalls);

        await scheduler.DisposeAsync();
    }

    [Fact]
    public async Task Pause_BlocksCoreCalls_AndResumeContinues()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor();
        var log = new CapturedLog();
        var scheduler = NewScheduler(executor, clock, log);
        scheduler.RegisterTarget(Target("s1"));

        await scheduler.TickAsync();
        Assert.Equal(1, executor.ScanCalls);

        scheduler.Pause("test");
        Assert.True(scheduler.Paused);
        clock.Advance(TimeSpan.FromSeconds(900));
        await scheduler.TickAsync();
        Assert.Equal(1, executor.ScanCalls);
        Assert.True(scheduler.Snapshot().Paused);

        scheduler.Resume();
        await scheduler.TickAsync();
        Assert.Equal(2, executor.ScanCalls);
        Assert.False(scheduler.Snapshot().Paused);

        await scheduler.DisposeAsync();
    }

    [Fact]
    public async Task DisabledOption_NeverCallsTheExecutor()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor();
        var scheduler = NewScheduler(executor, clock, options: new SourceScanOptions { Enabled = false });
        scheduler.RegisterTarget(Target("s1"));

        Assert.False(await scheduler.TickAsync());
        Assert.Equal(0, executor.ScanCalls);
        Assert.False(scheduler.Snapshot().Enabled);

        await scheduler.DisposeAsync();
    }

    [Theory]
    [InlineData(900, null, 900, false)]
    [InlineData(60, null, 60, false)]
    [InlineData(86400, null, 86400, false)]
    [InlineData(900, "120", 120, false)]
    [InlineData(900, "  1800  ", 1800, false)]
    [InlineData(900, "0", 900, true)]
    [InlineData(900, "-1", 900, true)]
    [InlineData(900, "59", 900, true)]
    [InlineData(900, "86401", 900, true)]
    [InlineData(900, "not-a-number", 900, true)]
    [InlineData(30, null, 900, true)]
    [InlineData(900000, null, 900, true)]
    public void IntervalResolution_AppliesEnvironmentOverride_AndFallsBackOnIllegalValues(
        int configured, string? environment, int expected, bool expectedFallback)
    {
        var interval = SourceScanScheduler.ResolveIntervalSeconds(configured, environment, out var fallback);
        Assert.Equal(expected, interval);
        Assert.Equal(expectedFallback, fallback);
    }

    [Fact]
    public async Task SessionInvalid_PausesScheduler_WithoutRetryOrSessionReopen()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor
        {
            Script = _ => throw new CoreOperationException(
                "HOST_SESSION_INVALID", "authorization", false, "session gone", null),
        };
        var log = new CapturedLog();
        var scheduler = NewScheduler(executor, clock, log);
        scheduler.RegisterTarget(Target("s1"));

        await scheduler.TickAsync();
        Assert.Equal(1, executor.ScanCalls);
        Assert.True(scheduler.Paused);
        Assert.Contains(log.Warn, line => line.Contains("paused", StringComparison.Ordinal)
            && line.Contains("HOST_SESSION_INVALID", StringComparison.Ordinal));

        await scheduler.TickAsync();
        Assert.Equal(1, executor.ScanCalls); // fail-closed: no retry while paused

        await scheduler.DisposeAsync();
    }

    [Fact]
    public async Task CapabilityMissing_PausesScheduler()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor
        {
            Script = _ => throw new CoreOperationException(
                "CORE_CAPABILITY_MISSING", "protocol", false, "missing", null),
        };
        var scheduler = NewScheduler(executor, clock);
        scheduler.RegisterTarget(Target("s1"));

        await scheduler.TickAsync();
        Assert.True(scheduler.Paused);
        await scheduler.TickAsync();
        Assert.Equal(1, executor.ScanCalls);

        await scheduler.DisposeAsync();
    }

    [Fact]
    public async Task SidecarExit_PausesScheduler()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor
        {
            Script = _ => throw new SidecarException(SidecarErrorCode.ProcessExited, "core_service", "exited"),
        };
        var scheduler = NewScheduler(executor, clock);
        scheduler.RegisterTarget(Target("s1"));

        await scheduler.TickAsync();
        Assert.True(scheduler.Paused);
        Assert.Equal(1, executor.ScanCalls);

        await scheduler.DisposeAsync();
    }

    // ---------------------------------------------------------------------------------------
    // AC-S2: registration, single-flight, scan-only.
    // ---------------------------------------------------------------------------------------

    [Fact]
    public async Task SingleFlight_MergesOverlappingTick_AndKeepsOneScan()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor { Block = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously) };
        var scheduler = NewScheduler(executor, clock);
        scheduler.RegisterTarget(Target("s1"));

        var first = scheduler.TickAsync();
        Assert.Equal(1, executor.ScanCalls);

        // Overlapping tick is merged (never queued) while the scan is in flight.
        Assert.False(await scheduler.TickAsync());
        Assert.Equal(1, executor.ScanCalls);

        // The snapshot and registration stay available while the scan is blocked.
        Assert.Single(scheduler.Snapshot().Targets);
        Assert.True(scheduler.RegisterTarget(Target("s2")));

        executor.Block.TrySetResult(true);
        Assert.True(await first);

        await scheduler.DisposeAsync();
    }

    [Fact]
    public async Task TwoSources_OneTick_TwoSequentialScanCommands()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor();
        var scheduler = NewScheduler(executor, clock);
        scheduler.RegisterTarget(Target("s2"));
        scheduler.RegisterTarget(Target("s1"));

        await scheduler.TickAsync();
        Assert.Equal(new[] { "s1", "s2" }, executor.ScannedSourceIds); // deterministic ordinal order
        Assert.Equal(2, executor.IssuedCommands.Count);
        var snapshot = scheduler.Snapshot();
        Assert.Equal(new[] { "s1", "s2" }, snapshot.Targets.Select(target => target.SourceId));
        Assert.All(snapshot.Targets, target => Assert.Equal(SourceScanResults.Ok, target.LastResult));

        await scheduler.DisposeAsync();
    }

    [Fact]
    public async Task ReRegisterSameSource_OverwritesInsteadOfGrowing()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor();
        var scheduler = NewScheduler(executor, clock);
        scheduler.RegisterTarget(new SourceScanTarget("s1", "C:\\fixtures\\v1.zip", new[] { "b1" }, "1"));
        scheduler.RegisterTarget(new SourceScanTarget("s1", "C:\\fixtures\\v2.zip", new[] { "b2" }, "2"));

        Assert.Single(scheduler.Snapshot().Targets);
        await scheduler.TickAsync();
        Assert.Equal(1, executor.ScanCalls);

        await scheduler.DisposeAsync();
    }

    [Fact]
    public async Task TickCommands_AreExactlyScanSourceSync_NoWriteCommands()
    {
        var forbidden = new[]
        {
            "PlanSourceSync", "PreviewSourceSyncPlan", "ConfirmSourceSyncPlan", "ApplySourceSyncPlan",
            "RelinkSource", "RepointSource", "ResyncSource", "AcknowledgeSourceOperation",
            "CompleteSourceOperationRecovery", "RecordSourceOperationFailure",
        };
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor();
        var scheduler = NewScheduler(executor, clock);
        scheduler.RegisterTarget(Target("s1"));
        scheduler.RegisterTarget(Target("s2"));

        await scheduler.TickAsync();
        Assert.NotEmpty(executor.IssuedCommands);
        Assert.All(executor.IssuedCommands, command => Assert.Equal("ScanSourceSync", command));
        Assert.All(forbidden, command => Assert.DoesNotContain(command, executor.IssuedCommands));

        await scheduler.DisposeAsync();
    }

    // ---------------------------------------------------------------------------------------
    // AC-S3: budget, deferral, backoff, isolation.
    // ---------------------------------------------------------------------------------------

    [Fact]
    public async Task Budget_RotatesTenTargetsIntoFourFourTwo()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor();
        var scheduler = NewScheduler(executor, clock, options: new SourceScanOptions
        {
            IntervalSeconds = 900,
            MaxTargetsPerTick = 4,
        });
        for (var index = 0; index < 10; index++)
        {
            scheduler.RegisterTarget(Target("s" + index));
        }

        await scheduler.TickAsync();
        Assert.Equal(new[] { "s0", "s1", "s2", "s3" }, executor.ScannedSourceIds);
        await scheduler.TickAsync();
        Assert.Equal(new[] { "s4", "s5", "s6", "s7" }, executor.ScannedSourceIds.Skip(4));
        await scheduler.TickAsync();
        Assert.Equal(new[] { "s8", "s9" }, executor.ScannedSourceIds.Skip(8));
        Assert.Equal(10, executor.ScanCalls);

        await scheduler.DisposeAsync();
    }

    [Fact]
    public async Task Backoff_FollowsTheFrozenSequence_AndSuccessResetsIt()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor { Script = _ => SourceScanOutcome.Error("SOURCE_SYNC_STORAGE_FAILED") };
        var log = new CapturedLog();
        var scheduler = NewScheduler(executor, clock, log);
        scheduler.RegisterTarget(Target("s1"));

        await scheduler.TickAsync(); // failure 1 → backoff 60
        Assert.Equal(1, executor.ScanCalls);
        clock.Advance(TimeSpan.FromSeconds(59));
        await scheduler.TickAsync();
        Assert.Equal(1, executor.ScanCalls); // still backed off
        clock.Advance(TimeSpan.FromSeconds(1));
        await scheduler.TickAsync(); // failure 2 → backoff 120
        Assert.Equal(2, executor.ScanCalls);

        clock.Advance(TimeSpan.FromSeconds(119));
        await scheduler.TickAsync();
        Assert.Equal(2, executor.ScanCalls);
        clock.Advance(TimeSpan.FromSeconds(1));
        await scheduler.TickAsync(); // failure 3 → backoff 240
        Assert.Equal(3, executor.ScanCalls);

        clock.Advance(TimeSpan.FromSeconds(239));
        await scheduler.TickAsync();
        Assert.Equal(3, executor.ScanCalls);
        clock.Advance(TimeSpan.FromSeconds(1));
        await scheduler.TickAsync(); // failure 4 → backoff 480
        Assert.Equal(4, executor.ScanCalls);

        // Success clears the counter: the next failure starts again at 60s.
        executor.Script = _ => SourceScanOutcome.Ok(SourceScanCounts.Zero);
        clock.Advance(TimeSpan.FromSeconds(480));
        await scheduler.TickAsync();
        Assert.Equal(5, executor.ScanCalls);
        executor.Script = _ => SourceScanOutcome.Error("SOURCE_SYNC_STORAGE_FAILED");
        await scheduler.TickAsync();
        Assert.Equal(6, executor.ScanCalls);
        clock.Advance(TimeSpan.FromSeconds(59));
        await scheduler.TickAsync();
        Assert.Equal(6, executor.ScanCalls);
        clock.Advance(TimeSpan.FromSeconds(1));
        await scheduler.TickAsync();
        Assert.Equal(7, executor.ScanCalls);

        await scheduler.DisposeAsync();
    }

    [Fact]
    public async Task BudgetProbeExceeded_DefersWithoutScanning()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor { Budget = new SourceScanBudget(1024, 10) };
        var log = new CapturedLog();
        var scheduler = NewScheduler(executor, clock, log);
        scheduler.RegisterTarget(Target("s1"));

        await scheduler.TickAsync();
        Assert.Equal(0, executor.ScanCalls);
        var target = Assert.Single(scheduler.Snapshot().Targets);
        Assert.True(target.Deferred);
        Assert.Null(target.LastResult); // deferred is NOT a result
        Assert.Contains(log.Info, line => line.Contains("deferred=budget", StringComparison.Ordinal));

        await scheduler.DisposeAsync();
    }

    [Fact]
    public async Task BlockedScan_DoesNotBlockSnapshotOrRegistration()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor { Block = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously) };
        var scheduler = NewScheduler(executor, clock);
        scheduler.RegisterTarget(Target("s1"));

        var pending = scheduler.TickAsync();
        var blockedSnapshot = scheduler.Snapshot();
        Assert.Single(blockedSnapshot.Targets);
        Assert.True(scheduler.RegisterTarget(Target("s2")));
        Assert.False(await scheduler.TickAsync()); // merged, returns immediately

        executor.Block.TrySetResult(true);
        await pending;
        Assert.Equal(2, scheduler.Snapshot().Targets.Count);

        await scheduler.DisposeAsync();
    }

    // ---------------------------------------------------------------------------------------
    // AC-S5: status projection and redaction.
    // ---------------------------------------------------------------------------------------

    [Fact]
    public async Task Status_ProjectsResultsDeferredAndCapsRecentAtFifty()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor
        {
            Script = _ => SourceScanOutcome.Changed(new SourceScanCounts(0, 1, 0, 0, 0)),
        };
        var scheduler = NewScheduler(executor, clock);
        scheduler.RegisterTarget(Target("s1"));

        for (var index = 0; index < 60; index++)
        {
            clock.Advance(TimeSpan.FromSeconds(1));
            await scheduler.TickAsync();
        }

        var target = Assert.Single(scheduler.Snapshot().Targets);
        Assert.Equal(SourceScanResults.Changed, target.LastResult);
        Assert.Equal(1, target.Counts!.Added);
        Assert.Equal(Start.AddSeconds(60), target.LastScanAt);

        var snapshot = scheduler.Snapshot();
        Assert.Equal(SourceScanResults.MaxRecentEntries, snapshot.Recent.Count);
        Assert.All(snapshot.Recent, entry => Assert.Equal(SourceScanResults.Changed, entry.Result));
        Assert.True(snapshot.Recent[^1].At >= snapshot.Recent[0].At);

        await scheduler.DisposeAsync();
    }

    [Fact]
    public async Task UnchangedScan_DoesNotAppendRecentButUpdatesTarget()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor();
        var scheduler = NewScheduler(executor, clock);
        scheduler.RegisterTarget(Target("s1"));

        await scheduler.TickAsync();
        var snapshot = scheduler.Snapshot();
        Assert.Empty(snapshot.Recent);
        Assert.Equal(SourceScanResults.Ok, Assert.Single(snapshot.Targets).LastResult);

        await scheduler.DisposeAsync();
    }

    [Fact]
    public async Task StatusAndLogs_AreRedacted_NoPathGrantSessionOrExceptionText()
    {
        var secretRoot = Path.Combine(Path.GetTempPath(), "fea11-scan-1-redaction-root");
        var targetPath = Path.Combine(secretRoot, "private-source.zip");
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor
        {
            Script = _ => throw new IOException("raw failure text at " + targetPath),
        };
        var log = new CapturedLog();
        var scheduler = NewScheduler(executor, clock, log);
        scheduler.RegisterTarget(new SourceScanTarget("s1", targetPath, new[] { "b1" }, "1"));

        await scheduler.TickAsync();
        var statusJson = JsonSerializer.Serialize(scheduler.Snapshot());
        var allLogs = string.Join("\n", log.Info.Concat(log.Warn).Concat(log.Error));

        foreach (var sensitive in new[] { secretRoot, targetPath, "private-source", "raw failure text", "source-", "host_session" })
        {
            Assert.DoesNotContain(sensitive, statusJson, StringComparison.Ordinal);
            Assert.DoesNotContain(sensitive, allLogs, StringComparison.Ordinal);
        }

        Assert.Contains(log.Warn, line => line.Contains("SOURCE_SYNC_STORAGE_FAILED", StringComparison.Ordinal));
        Assert.Contains(log.Warn, line => line.Contains("source=s1", StringComparison.Ordinal));

        await scheduler.DisposeAsync();
    }

    // ---------------------------------------------------------------------------------------
    // r2 fixes: denied backoff (P2-1), locked snapshot (P2-2), registry exact match (P2-5),
    // ProbeBudget (P3-2), Disabled semantics (P3-4).
    // ---------------------------------------------------------------------------------------

    [Fact]
    public async Task DeniedResult_IsBackedOff_AndKeepsDeniedResult()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor
        {
            Script = _ => SourceScanOutcome.Denied("SOURCE_ACCESS_DENIED"),
        };
        var log = new CapturedLog();
        var scheduler = NewScheduler(executor, clock, log);
        scheduler.RegisterTarget(Target("s1"));

        await scheduler.TickAsync();
        Assert.Equal(1, executor.ScanCalls);
        Assert.Equal(SourceScanResults.Denied, scheduler.Snapshot().Targets.Single().LastResult);
        Assert.False(scheduler.Paused); // denied is a per-target failure, not a scheduler pause
        Assert.Contains(log.Warn, line => line.Contains("SOURCE_ACCESS_DENIED", StringComparison.Ordinal)
            && line.Contains("backoff=60", StringComparison.Ordinal));

        clock.Advance(TimeSpan.FromSeconds(59));
        await scheduler.TickAsync();
        Assert.Equal(1, executor.ScanCalls); // denied now backs off like any typed failure
        clock.Advance(TimeSpan.FromSeconds(1));
        await scheduler.TickAsync();
        Assert.Equal(2, executor.ScanCalls);
        Assert.Contains(log.Warn, line => line.Contains("backoff=120", StringComparison.Ordinal));

        await scheduler.DisposeAsync();
    }

    [Fact]
    public async Task ConcurrentSnapshotDuringTicks_DoesNotRaceOrThrow()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor
        {
            Script = _ => SourceScanOutcome.Changed(new SourceScanCounts(0, 1, 0, 0, 0)),
        };
        var scheduler = NewScheduler(executor, clock);
        for (var index = 0; index < 6; index++)
        {
            scheduler.RegisterTarget(Target("s" + index));
        }

        var failures = new List<Exception>();
        var stop = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        var readers = Enumerable.Range(0, 4).Select(_ => Task.Run(async () =>
        {
            try
            {
                while (!stop.Task.IsCompleted)
                {
                    var snapshot = scheduler.Snapshot();
                    if (snapshot.Targets.Count != 6) throw new InvalidOperationException("target count torn");
                    if (snapshot.Recent.Count > SourceScanResults.MaxRecentEntries)
                        throw new InvalidOperationException("recent overflow");
                    await Task.Yield();
                }
            }
            catch (Exception error)
            {
                lock (failures) failures.Add(error);
            }
        })).ToArray();

        for (var index = 0; index < 40; index++)
        {
            clock.Advance(TimeSpan.FromSeconds(1));
            await scheduler.TickAsync();
        }

        stop.TrySetResult(true);
        await Task.WhenAll(readers).WaitAsync(TimeSpan.FromSeconds(10));
        Assert.Empty(failures);
        Assert.Equal(240, executor.ScanCalls); // 40 ticks × 6 targets

        await scheduler.DisposeAsync();
    }

    [Fact]
    public void DisabledStatus_IsNotPaused()
    {
        var status = SourceScanStatus.Disabled(900);
        Assert.False(status.Enabled);
        Assert.False(status.Paused); // r1 P3-4: disabled != paused
        Assert.Equal(900, status.IntervalSeconds);
        Assert.Empty(status.Targets);
        Assert.Empty(status.Recent);
    }

    [Fact]
    public void ProbeBudget_UsesRealFileSizeAndFolderMemberLimits()
    {
        var root = Path.Combine(Path.GetTempPath(), "fea11-scan-budget-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        try
        {
            var file = Path.Combine(root, "book.zip");
            File.WriteAllBytes(file, new byte[64]);
            var folder = Path.Combine(root, "folder");
            Directory.CreateDirectory(folder);
            for (var index = 0; index < 3; index++)
            {
                File.WriteAllBytes(Path.Combine(folder, "p" + index + ".png"), new byte[4]);
            }

            var executor = new HostSourceScanExecutor(null!, null!, new SourceScanOptions
            {
                MaxBytesPerSource = 64,
                MaxEntriesPerSource = 3,
            });

            var fileBudget = executor.ProbeBudget(new SourceScanTarget("s1", file, new[] { "b1" }, "1"));
            Assert.NotNull(fileBudget);
            Assert.False(fileBudget!.Exceeded);
            Assert.Equal(64, fileBudget.Metric);
            Assert.Equal(64, fileBudget.Limit);

            var folderBudget = executor.ProbeBudget(new SourceScanTarget("s2", folder, new[] { "b1" }, "1"));
            Assert.NotNull(folderBudget);
            Assert.Equal(3, folderBudget!.Metric);
            Assert.False(folderBudget.Exceeded);

            var missing = executor.ProbeBudget(
                new SourceScanTarget("s3", Path.Combine(root, "gone.zip"), new[] { "b1" }, "1"));
            Assert.Null(missing); // stat fails -> no budget verdict (missing path decides)
        }
        finally
        {
            try { Directory.Delete(root, recursive: true); }
            catch (Exception error) when (error is IOException or UnauthorizedAccessException) { }
        }
    }

    [Fact]
    public void RegistryResolution_PrefersExactMatch_AndFailsClosedOnRevokedExactEntry()
    {
        const string fixtureRoot = @"C:\fixtures";
        const string exactFile = @"C:\fixtures\book.zip";
        static SourceRoot Root(string path) => new(path, 1, 1, "2026-11-06T00:00:00Z", true);
        static SourceAuthorization Entry(string id, string locator, params string[] roots) =>
            new(id, locator, 1, "2026-11-06T00:00:00Z", "2026-11-06T00:00:00Z", null,
                roots.Select(Root).ToArray());

        var parent = Entry("reg-parent", fixtureRoot, fixtureRoot);
        var exact = Entry("reg-exact", exactFile, exactFile);

        // Exact root/locator match wins over the containing parent entry.
        var resolved = HostSourceScanExecutor.ResolveRegistryEntry(new[] { parent, exact }, exactFile);
        Assert.NotNull(resolved);
        Assert.Equal("reg-exact", resolved!.RegistryId);

        // No exact entry -> controlled containment fallback to the parent (real-IPC fixture shape).
        var fallback = HostSourceScanExecutor.ResolveRegistryEntry(new[] { parent }, exactFile);
        Assert.NotNull(fallback);
        Assert.Equal("reg-parent", fallback!.RegistryId);

        // A revoked entry that matches exactly is a typed failure, never a fall-through to parent.
        var revoked = exact with { RevokedAt = "2026-11-06T00:00:01Z" };
        Assert.Null(HostSourceScanExecutor.ResolveRegistryEntry(new[] { parent, revoked }, exactFile));

        // Nothing matches at all -> null (typed failure downstream).
        Assert.Null(HostSourceScanExecutor.ResolveRegistryEntry(new[] { parent }, @"D:\other\book.zip"));
    }

    // ---------------------------------------------------------------------------------------
    // FEA-11-SCAN-2 (B1): cold-start enumeration, registry re-verification, typed skips.
    // ---------------------------------------------------------------------------------------

    private static readonly string ValidDigest = new string('a', 64);

    [Fact]
    public async Task Refresh_MergesAndDeduplicatesTargets_AndIsIdempotent()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor();
        var enumerator = new FakeTargetEnumerator
        {
            Script = _ => SourceScanEnumerationResult.Completed(
                new[] { EnumeratedTarget("s1"), EnumeratedTarget("s2") }, 2),
        };
        var log = new CapturedLog();
        var scheduler = NewScheduler(executor, clock, log, enumerator: enumerator);

        Assert.True(await scheduler.RefreshTargetsAsync());
        Assert.True(await scheduler.RefreshTargetsAsync());
        var snapshot = scheduler.Snapshot();
        Assert.Equal(2, snapshot.Targets.Count);
        Assert.NotNull(snapshot.Enumeration);
        Assert.True(snapshot.Enumeration!.Available);
        Assert.Equal(2, snapshot.Enumeration.SkippedTargets);
        Assert.Equal(2, enumerator.Calls);
        Assert.Contains(log.Info, line => line.Contains("source scan refresh targets=2", StringComparison.Ordinal));

        // A SCAN-1 style registration with the same source_id is merged, not duplicated.
        scheduler.RegisterTarget(Target("s1"));
        var after = scheduler.Snapshot();
        Assert.Equal(2, after.Targets.Count);
        Assert.Single(after.Targets, target => target.SourceId == "s1");

        await scheduler.DisposeAsync();
    }

    [Fact]
    public async Task Refresh_Unavailable_IsTypedFailClosed_DoesNotBlockTicks_AndDoesNotRetryStorm()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor();
        var enumerator = new FakeTargetEnumerator
        {
            Script = _ => SourceScanEnumerationResult.Unavailable("CORE_CAPABILITY_MISSING"),
        };
        var log = new CapturedLog();
        var scheduler = NewScheduler(executor, clock, log, enumerator: enumerator);
        scheduler.RegisterTarget(Target("s1"));

        Assert.False(await scheduler.RefreshTargetsAsync());
        var snapshot = scheduler.Snapshot();
        Assert.NotNull(snapshot.Enumeration);
        Assert.False(snapshot.Enumeration!.Available);
        Assert.Equal("CORE_CAPABILITY_MISSING", snapshot.Enumeration.LastErrorCode);
        Assert.Contains(log.Warn, line => line.Contains("code=CORE_CAPABILITY_MISSING", StringComparison.Ordinal));

        // The scheduler still ticks; enumeration is NOT retried automatically (no retry storm).
        await scheduler.TickAsync();
        await scheduler.TickAsync();
        Assert.Equal(2, executor.ScanCalls);
        Assert.Equal(1, enumerator.Calls);

        await scheduler.DisposeAsync();
    }

    [Fact]
    public async Task Refresh_IsSingleFlightWithTicks()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor();
        var enumerator = new FakeTargetEnumerator { Block = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously) };
        var scheduler = NewScheduler(executor, clock, enumerator: enumerator);
        scheduler.RegisterTarget(Target("s1"));

        var refresh = scheduler.RefreshTargetsAsync();
        await Task.Yield();
        // A tick started while the refresh holds the single-flight gate is merged, not queued.
        Assert.False(await scheduler.TickAsync());
        Assert.Equal(0, executor.ScanCalls);
        enumerator.Block!.TrySetResult(true);
        Assert.True(await refresh.WaitAsync(TimeSpan.FromSeconds(10)));
        Assert.Equal(1, enumerator.Calls);

        await scheduler.DisposeAsync();
    }

    [Fact]
    public async Task SkippedOutcome_IsRecorded_AndDoesNotPauseScheduler()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor
        {
            Script = _ => SourceScanOutcome.Skipped("SOURCE_GRANT_REVOKED"),
        };
        var log = new CapturedLog();
        var scheduler = NewScheduler(executor, clock, log);
        scheduler.RegisterTarget(Target("s1"));

        await scheduler.TickAsync();
        var snapshot = scheduler.Snapshot();
        Assert.Equal(SourceScanResults.Skipped, snapshot.Targets.Single().LastResult);
        Assert.False(snapshot.Paused);
        Assert.Contains(snapshot.Recent, entry => entry.Result == SourceScanResults.Skipped
            && entry.ErrorCode == "SOURCE_GRANT_REVOKED");

        await scheduler.DisposeAsync();
    }

    [Fact]
    public async Task EnumerationStatus_IsRedacted_NoPathOrSecret()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor();
        var enumerator = new FakeTargetEnumerator
        {
            Script = _ => SourceScanEnumerationResult.Completed(
                new[] { EnumeratedTarget("s1", @"C:\secret-root\private-source.zip") }, 1),
        };
        var log = new CapturedLog();
        var scheduler = NewScheduler(executor, clock, log, enumerator: enumerator);

        await scheduler.RefreshTargetsAsync();
        var statusJson = JsonSerializer.Serialize(scheduler.Snapshot());
        var allLogs = string.Join("\n", log.Info.Concat(log.Warn).Concat(log.Error));
        foreach (var sensitive in new[] { "secret-root", "private-source", "C:\\", "source-", "host_session" })
        {
            Assert.DoesNotContain(sensitive, statusJson, StringComparison.Ordinal);
            Assert.DoesNotContain(sensitive, allLogs, StringComparison.Ordinal);
        }

        await scheduler.DisposeAsync();
    }

    private static JsonElement EnumeratedJson(
        string sourceId = "src-1",
        string registryId = "reg-1",
        int generation = 1,
        string sourceKind = "zip",
        string? identityDigest = null,
        string[]? projectIds = null) =>
        JsonDocument.Parse(
            "{\"source_id\":\"" + sourceId + "\",\"registry_id\":\"" + registryId
            + "\",\"generation\":" + generation + ",\"source_kind\":\"" + sourceKind
            + "\",\"identity_digest\":\"" + (identityDigest ?? ValidDigest) + "\",\"project_ids\":["
            + string.Join(",", (projectIds ?? new[] { "b1" }).Select(id => "\"" + id + "\""))
            + "]}").RootElement.Clone();

    private static SourceAuthorization RegistryEntry(
        string registryId = "reg-1",
        int generation = 1,
        string root = @"C:\fixtures\src-1.zip",
        string? revokedAt = null) =>
        new(registryId, root, generation, "2026-11-06T00:00:00Z", "2026-11-06T00:00:00Z", revokedAt,
            new[] { new SourceRoot(root, 1, 1, "2026-11-06T00:00:00Z", true) });

    [Fact]
    public void EnumeratorMapping_MapsValidTargetFromRegistryRoot()
    {
        var entries = new Dictionary<string, SourceAuthorization>(StringComparer.Ordinal)
        {
            ["reg-1"] = RegistryEntry(),
        };

        Assert.True(HostSourceScanTargetEnumerator.TryMap(EnumeratedJson(), entries, out var target));
        Assert.Equal("src-1", target.SourceId);
        Assert.Equal("reg-1", target.RegistryId);
        Assert.Equal(1, target.Generation);
        Assert.Equal("zip", target.SourceKind);
        Assert.Equal(ValidDigest, target.IdentityDigest);
        Assert.Equal(@"C:\fixtures\src-1.zip", target.Path);
        Assert.True(target.IsEnumerated);
        Assert.Equal(new[] { "b1" }, target.ProjectIds);
    }

    [Fact]
    public void EnumeratorMapping_SkipsUnknownKindMalformedDigestAndTooManyProjectIds()
    {
        var entries = new Dictionary<string, SourceAuthorization>(StringComparer.Ordinal)
        {
            ["reg-1"] = RegistryEntry(),
        };
        var tooMany = Enumerable.Range(0, 21).Select(index => "b" + index).ToArray();

        Assert.False(HostSourceScanTargetEnumerator.TryMap(
            EnumeratedJson(sourceKind: "video"), entries, out _));
        Assert.False(HostSourceScanTargetEnumerator.TryMap(
            EnumeratedJson(identityDigest: "not-a-digest"), entries, out _));
        Assert.False(HostSourceScanTargetEnumerator.TryMap(
            EnumeratedJson(projectIds: tooMany), entries, out _));
        Assert.False(HostSourceScanTargetEnumerator.TryMap(
            EnumeratedJson(generation: 0), entries, out _));
        Assert.False(HostSourceScanTargetEnumerator.TryMap(
            EnumeratedJson(projectIds: Array.Empty<string>()), entries, out _));
    }

    [Fact]
    public void EnumeratorMapping_SkipsMissingRevokedAndGenerationDriftedRegistry()
    {
        var revoked = RegistryEntry(revokedAt: "2026-11-06T00:00:01Z");
        var drifted = RegistryEntry(generation: 2);
        var entries = new Dictionary<string, SourceAuthorization>(StringComparer.Ordinal)
        {
            ["reg-1"] = revoked,
            ["reg-2"] = drifted,
        };

        Assert.False(HostSourceScanTargetEnumerator.TryMap(EnumeratedJson(), entries, out _));
        Assert.False(HostSourceScanTargetEnumerator.TryMap(EnumeratedJson(registryId: "reg-2"), entries, out _));
        Assert.False(HostSourceScanTargetEnumerator.TryMap(EnumeratedJson(registryId: "reg-missing"), entries, out _));
    }

    private static (HostSourceScanExecutor Executor, SourceAccessRegistry Registry, string Root)
        ExecutorWithFileRegistry()
    {
        var root = Path.Combine(Path.GetTempPath(), "fea11-scan-2-exec-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        var registry = new SourceAccessRegistry(root);
        var sources = new SourceReadCoordinator(null!, registry, () => true);
        var executor = new HostSourceScanExecutor(null!, sources, new SourceScanOptions());
        return (executor, registry, root);
    }

    [Fact]
    public async Task Executor_EnumeratedTarget_RevokedRegistry_IsSkipped_NoScan()
    {
        var (executor, registry, root) = ExecutorWithFileRegistry();
        try
        {
            var file = Path.Combine(root, "book.zip");
            await File.WriteAllBytesAsync(file, new byte[4]);
            var entry = registry.Register("fixture", new[] { file });
            registry.Revoke(entry.RegistryId);
            var target = EnumeratedTarget("src-1", file, entry.RegistryId, entry.Generation, ValidDigest);

            var outcome = await executor.ScanAsync(target, CancellationToken.None);
            Assert.Equal(SourceScanOutcomeKind.Skipped, outcome.Kind);
            Assert.Equal("SOURCE_GRANT_REVOKED", outcome.ErrorCode);
        }
        finally
        {
            TryDeleteDirectory(root);
        }
    }

    [Fact]
    public async Task Executor_EnumeratedTarget_GenerationDrift_IsSkipped()
    {
        var (executor, registry, root) = ExecutorWithFileRegistry();
        try
        {
            var file = Path.Combine(root, "book.zip");
            await File.WriteAllBytesAsync(file, new byte[4]);
            var entry = registry.Register("fixture", new[] { file });
            var target = EnumeratedTarget("src-1", file, entry.RegistryId, entry.Generation + 7, ValidDigest);

            var outcome = await executor.ScanAsync(target, CancellationToken.None);
            Assert.Equal(SourceScanOutcomeKind.Skipped, outcome.Kind);
            Assert.Equal("SOURCE_REGISTRY_BUSY", outcome.ErrorCode);
        }
        finally
        {
            TryDeleteDirectory(root);
        }
    }

    [Fact]
    public async Task Executor_EnumeratedTarget_ColdStartMissingRoot_IsRegistryUnavailable()
    {
        var (executor, registry, root) = ExecutorWithFileRegistry();
        try
        {
            var file = Path.Combine(root, "book.zip");
            await File.WriteAllBytesAsync(file, new byte[4]);
            var entry = registry.Register("fixture", new[] { file });
            File.Delete(file); // cold start: the production file-root vanished before any verification
            var target = EnumeratedTarget("src-1", file, entry.RegistryId, entry.Generation, ValidDigest);

            var outcome = await executor.ScanAsync(target, CancellationToken.None);
            Assert.Equal(SourceScanOutcomeKind.Error, outcome.Kind);
            Assert.Equal("SOURCE_REGISTRY_UNAVAILABLE", outcome.ErrorCode);
        }
        finally
        {
            TryDeleteDirectory(root);
        }
    }

    [Fact]
    public async Task Executor_EnumeratedTarget_ReplacedRoot_IsRegistryUnavailable()
    {
        var (executor, registry, root) = ExecutorWithFileRegistry();
        try
        {
            var file = Path.Combine(root, "book.zip");
            await File.WriteAllBytesAsync(file, new byte[4]);
            var entry = registry.Register("fixture", new[] { file });
            File.Delete(file);
            await File.WriteAllBytesAsync(file, new byte[4]); // same path, new physical file
            var target = EnumeratedTarget("src-1", file, entry.RegistryId, entry.Generation, ValidDigest);

            var outcome = await executor.ScanAsync(target, CancellationToken.None);
            Assert.Equal(SourceScanOutcomeKind.Error, outcome.Kind);
            Assert.Equal("SOURCE_REGISTRY_UNAVAILABLE", outcome.ErrorCode);
        }
        finally
        {
            TryDeleteDirectory(root);
        }
    }

    private static void TryDeleteDirectory(string root)
    {
        try
        {
            if (Directory.Exists(root)) Directory.Delete(root, recursive: true);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            // isolated temp fixture expires with the OS temp directory
        }
    }

    // ---------------------------------------------------------------------------------------
    // FEA-11-SCAN-2 r2 (P1-1): scope selection + exact ScanSourceSync payload.
    // ---------------------------------------------------------------------------------------

    private static JsonElement ParsePayload(string payload) => JsonDocument.Parse(payload).RootElement.Clone();

    private static string[] ProjectIdsOf(JsonElement payload) =>
        payload.GetProperty("project_ids").EnumerateArray().Select(value => value.GetString()!).ToArray();

    [Fact]
    public void ScanPayload_SingleProject_UsesCurrentScope()
    {
        var target = EnumeratedTarget("src-1", projectIds: new[] { "book-1" });

        var payload = ParsePayload(HostSourceScanExecutor.BuildScanSourceSyncPayload(target, "grant-1"));

        Assert.Equal("current", payload.GetProperty("scope").GetString());
        Assert.Equal(new[] { "book-1" }, ProjectIdsOf(payload));
        Assert.Equal("resync", payload.GetProperty("kind").GetString());
        Assert.Equal("grant-1", payload.GetProperty("grant_ids").EnumerateArray().Single().GetString());
        Assert.Empty(payload.GetProperty("missing").EnumerateArray());
    }

    [Fact]
    public void ScanPayload_SharedSource_UsesAllScope_AndAllProjectIds()
    {
        var target = EnumeratedTarget("src-1", projectIds: new[] { "book-1", "book-2" });

        var payload = ParsePayload(HostSourceScanExecutor.BuildScanSourceSyncPayload(target, "grant-1"));

        // P1-1 discriminator: scope=current with 2 projects is rejected by the Core
        // (scanner.py "scope=current needs exactly one project"); a shared source must use "all".
        Assert.Equal("all", payload.GetProperty("scope").GetString());
        Assert.Equal(new[] { "book-1", "book-2" }, ProjectIdsOf(payload));
        Assert.Equal("grant-1", payload.GetProperty("grant_ids").EnumerateArray().Single().GetString());
    }

    [Fact]
    public void MissingPayload_UsesSameScopeSelection_AndCarriesObservation()
    {
        var single = EnumeratedTarget("src-1", projectIds: new[] { "book-1" });
        var shared = EnumeratedTarget("src-2", projectIds: new[] { "book-1", "book-2" });

        var singlePayload = ParsePayload(HostSourceScanExecutor.BuildScanMissingPayload(
            single, "reg-1", 1, "2026-11-06T00:00:00.000Z", new string('a', 64)));
        var sharedPayload = ParsePayload(HostSourceScanExecutor.BuildScanMissingPayload(
            shared, "reg-2", 3, "2026-11-06T00:00:00.000Z", new string('b', 64)));

        Assert.Equal("current", singlePayload.GetProperty("scope").GetString());
        Assert.Equal("all", sharedPayload.GetProperty("scope").GetString());
        Assert.Empty(singlePayload.GetProperty("grant_ids").EnumerateArray());
        var missing = singlePayload.GetProperty("missing").EnumerateArray().Single();
        Assert.Equal("reg-1", missing.GetProperty("registry_id").GetString());
        Assert.Equal(1, missing.GetProperty("generation").GetInt32());
        Assert.Equal(new string('a', 64), missing.GetProperty("expected_identity_digest").GetString());
        Assert.Equal("2026-11-06T00:00:00.000Z", missing.GetProperty("observed_at").GetString());
    }

    [Fact]
    public async Task RefreshRequestedDuringTick_IsReplayedAfterTickCompletes()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor { Block = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously) };
        var enumerator = new FakeTargetEnumerator
        {
            Script = _ => SourceScanEnumerationResult.Completed(new[] { EnumeratedTarget("s2") }, 0),
        };
        var log = new CapturedLog();
        var scheduler = NewScheduler(executor, clock, log, enumerator: enumerator);
        scheduler.RegisterTarget(Target("s1"));

        var tick = scheduler.TickAsync();
        await executor.WaitForScanCountAsync(1).WaitAsync(TimeSpan.FromSeconds(10)); // tick holds the gate

        // P2-1: a Refresh during the tick is coalesced, not silently dropped.
        Assert.False(await scheduler.RefreshTargetsAsync());
        Assert.Contains(log.Info, line => line.Contains("refresh queued", StringComparison.Ordinal));

        executor.Block!.TrySetResult(true);
        Assert.True(await tick.WaitAsync(TimeSpan.FromSeconds(10)));

        // The tick wrapper replayed the pending refresh before returning: the new target exists.
        Assert.Equal(1, enumerator.Calls);
        Assert.Contains(scheduler.Snapshot().Targets, target => target.SourceId == "s2");

        // And it is scanned on the next tick (not lost for the session).
        executor.Block = null;
        Assert.True(await scheduler.TickAsync());
        Assert.Contains("s2", executor.ScannedSourceIds);

        await scheduler.DisposeAsync();
    }

    // ---------------------------------------------------------------------------------------
    // FEA-11-WATCH-1 (AC-W2/W4): watcher hints reuse the existing single-flight/budget/backoff
    // machinery; a hint is only a due bit, never a changed/deleted verdict.
    // ---------------------------------------------------------------------------------------

    [Fact]
    public async Task HintedTarget_IsScannedFirst_WithinTheSameBudget()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor();
        var scheduler = NewScheduler(executor, clock);
        for (var index = 0; index < 10; index++)
        {
            scheduler.RegisterTarget(Target("s" + index));
        }

        Assert.True(scheduler.HintSource("s9"));
        await scheduler.HintIdleAsync().WaitAsync(TimeSpan.FromSeconds(10));

        Assert.Equal("s9", executor.ScannedSourceIds[0]);
        Assert.True(executor.ScanCalls <= 8); // the default budget still applies
        await scheduler.DisposeAsync();
    }

    [Fact]
    public async Task HintDuringInFlightTick_IsMerged_AndReplayedAtMostOnce()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor
        {
            Block = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously),
        };
        var scheduler = NewScheduler(executor, clock);
        scheduler.RegisterTarget(Target("s1"));
        scheduler.RegisterTarget(Target("s2"));

        var inFlight = scheduler.TickAsync();
        await executor.WaitForScanCountAsync(1).WaitAsync(TimeSpan.FromSeconds(10));

        Assert.True(scheduler.HintSource("s2"));
        await scheduler.HintIdleAsync().WaitAsync(TimeSpan.FromSeconds(10));
        Assert.False(await scheduler.TickAsync()); // single-flight: merged, never queued/unbounded

        executor.Block!.TrySetResult(true);
        Assert.True(await inFlight.WaitAsync(TimeSpan.FromSeconds(10)));
        await scheduler.HintIdleAsync().WaitAsync(TimeSpan.FromSeconds(10));

        // The in-flight pass scanned s1+s2; the single replay pass re-scanned them hinted-first.
        // AC-W4: each source is scanned at most twice (in-flight + one replay) and never concurrently.
        Assert.Equal(1, executor.MaxConcurrentScans);
        Assert.All(
            executor.ScannedSourceIds.GroupBy(id => id, StringComparer.Ordinal),
            group => Assert.InRange(group.Count(), 1, 2));
        Assert.Contains("s2", executor.ScannedSourceIds); // the hinted source is covered by the replay
        await scheduler.DisposeAsync();
    }

    [Fact]
    public async Task HintedBackoffTarget_IsNotScannedEarly_ThenScannedAfterBackoff()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor { Script = _ => SourceScanOutcome.Error("SOURCE_SYNC_FAILED") };
        var scheduler = NewScheduler(executor, clock);
        scheduler.RegisterTarget(Target("s1"));
        Assert.True(await scheduler.TickAsync());
        Assert.Equal(1, executor.ScanCalls); // error -> backoff

        Assert.True(scheduler.HintSource("s1"));
        await scheduler.HintIdleAsync().WaitAsync(TimeSpan.FromSeconds(10));
        Assert.Equal(1, executor.ScanCalls); // backoff is not bypassed by a hint

        clock.Advance(TimeSpan.FromSeconds(61));
        Assert.True(scheduler.HintSource("s1"));
        await scheduler.HintIdleAsync().WaitAsync(TimeSpan.FromSeconds(10));
        Assert.Equal(2, executor.ScanCalls); // due bit preserved until the backoff expires
        await scheduler.DisposeAsync();
    }

    [Fact]
    public async Task HintedPausedScheduler_ScansNothing_AndResumeScans()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor();
        var scheduler = NewScheduler(executor, clock);
        scheduler.RegisterTarget(Target("s1"));
        scheduler.Pause("TEST");

        Assert.True(scheduler.HintSource("s1"));
        await scheduler.HintIdleAsync().WaitAsync(TimeSpan.FromSeconds(10));
        Assert.Equal(0, executor.ScanCalls);

        scheduler.Resume();
        Assert.True(scheduler.HintSource("s1"));
        await scheduler.HintIdleAsync().WaitAsync(TimeSpan.FromSeconds(10));
        Assert.Equal(1, executor.ScanCalls);
        await scheduler.DisposeAsync();
    }

    [Fact]
    public async Task HintTriggeredPass_UsesOnlyScanSourceSync_AndNeverMarksChanged()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor();
        var log = new CapturedLog();
        var scheduler = NewScheduler(executor, clock, log);
        scheduler.RegisterTarget(Target("s1"));

        Assert.True(scheduler.HintSource("s1"));
        await scheduler.HintIdleAsync().WaitAsync(TimeSpan.FromSeconds(10));

        Assert.NotEmpty(executor.IssuedCommands);
        Assert.All(executor.IssuedCommands, command => Assert.Equal("ScanSourceSync", command));
        var target = Assert.Single(scheduler.Snapshot().Targets);
        Assert.Equal(SourceScanResults.Ok, target.LastResult);
        Assert.NotEqual(SourceScanResults.Changed, target.LastResult);
        await scheduler.DisposeAsync();
    }

    [Fact]
    public async Task HintForUnknownSource_IsIgnored_AndNothingIsScanned()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor();
        var scheduler = NewScheduler(executor, clock);
        scheduler.RegisterTarget(Target("s1"));

        Assert.False(scheduler.HintSource("not-registered"));
        Assert.True(await scheduler.TickAsync());
        Assert.Equal(1, executor.ScanCalls); // only the periodic pass for s1, never a hint-driven one
        await scheduler.DisposeAsync();
    }

    // ---------------------------------------------------------------------------------------
    // r2 (P1/P3): hint-after-prior-rotation must not be skipped by a non-zero budget cursor.
    // ---------------------------------------------------------------------------------------

    [Fact]
    public async Task HintAfterPriorRotation_IsScannedInTheSamePass_AndPendingClears()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor();
        var scheduler = NewScheduler(
            executor,
            clock,
            options: new SourceScanOptions { IntervalSeconds = 900, MaxTargetsPerTick = 4 });
        for (var index = 0; index < 10; index++)
        {
            scheduler.RegisterTarget(Target("s" + index));
        }

        // First pass is a normal rotation tick: scans s0..s3 and leaves the cursor at 4 (the r1 P1 probe).
        Assert.True(await scheduler.TickAsync());
        Assert.Equal(new[] { "s0", "s1", "s2", "s3" }, executor.ScannedSourceIds);
        var beforeHint = executor.ScanCalls;

        Assert.True(scheduler.HintSource("s9"));
        await scheduler.HintIdleAsync().WaitAsync(TimeSpan.FromSeconds(10));

        // r2 P1: the hint pass starts at index 0, so the hinted source is scanned in THIS pass even
        // though the rotation cursor is non-zero; budget is still respected and the due bit is consumed.
        Assert.Contains("s9", executor.ScannedSourceIds.Skip(beforeHint));
        Assert.True(executor.ScanCalls - beforeHint <= 4);
        Assert.False(scheduler.HintPending);
        await scheduler.DisposeAsync();
    }

    [Fact]
    public async Task DisposeAsync_WithInFlightHintPass_CompletesWithoutThrowing()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor
        {
            Block = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously),
        };
        var scheduler = NewScheduler(executor, clock);
        scheduler.RegisterTarget(Target("s1"));

        Assert.True(scheduler.HintSource("s1"));
        await executor.WaitForScanCountAsync(1).WaitAsync(TimeSpan.FromSeconds(10));

        var dispose = scheduler.DisposeAsync().AsTask();
        executor.Block!.TrySetResult(true);
        await dispose.WaitAsync(TimeSpan.FromSeconds(10)); // r2 P3-6: joins the in-flight hint pass
    }

    // ---------------------------------------------------------------------------------------
    // FEA-11-SCAN-RH-1 (AC-RH-1): a Refresh that arrives while another Refresh is enumerating is
    // coalesced into _refreshPending and replayed as soon as the first pass releases the
    // single-flight gate — without waiting for a tick (the pre-fix behavior delayed it up to 900 s).
    // ---------------------------------------------------------------------------------------

    [Fact]
    public async Task RefreshDuringInFlightRefresh_IsReplayedAfterTheFirstPass_WithoutATick()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor();
        var firstGate = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        var replayGate = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        var enumerator = new FakeTargetEnumerator
        {
            Script = call => call == 1
                ? SourceScanEnumerationResult.Completed(new[] { EnumeratedTarget("s1") }, 0)
                : SourceScanEnumerationResult.Completed(
                    new[] { EnumeratedTarget("s1"), EnumeratedTarget("s2") }, 0),
            WaitFor = call => call switch
            {
                1 => firstGate.Task,
                2 => replayGate.Task,
                _ => Task.CompletedTask,
            },
        };
        var log = new CapturedLog();
        var scheduler = NewScheduler(executor, clock, log, enumerator: enumerator);

        var first = scheduler.RefreshTargetsAsync();
        await enumerator.WaitForCallsAsync(1).WaitAsync(TimeSpan.FromSeconds(10));
        Assert.Empty(scheduler.Snapshot().Targets); // pass 1 is still enumerating: nothing merged yet

        // The second request finds the gate held: it is coalesced (returns false), never dropped.
        Assert.False(await scheduler.RefreshTargetsAsync());
        Assert.Equal(1, enumerator.Calls);
        Assert.Contains(log.Info, line => line.Contains("refresh queued", StringComparison.Ordinal));

        // Releasing the first pass must start the replayed enumeration immediately...
        firstGate.TrySetResult(true);
        await enumerator.WaitForCallsAsync(2).WaitAsync(TimeSpan.FromSeconds(10));
        Assert.Single(scheduler.Snapshot().Targets); // only the first pass has merged so far
        replayGate.TrySetResult(true);

        // ...and the first Refresh call returns only after the replay merged the new target.
        Assert.True(await first.WaitAsync(TimeSpan.FromSeconds(10)));
        Assert.Equal(2, enumerator.Calls);
        Assert.Equal(0, executor.ScanCalls); // no TickAsync was needed to apply the replay
        var snapshot = scheduler.Snapshot();
        Assert.Contains(snapshot.Targets, target => target.SourceId == "s1");
        Assert.Contains(snapshot.Targets, target => target.SourceId == "s2");

        await scheduler.DisposeAsync();
    }

    [Fact]
    public async Task RefreshReplay_IsBoundedToOncePerCompletedPass()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor();
        var firstGate = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        var replayGate = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        var enumerator = new FakeTargetEnumerator
        {
            Script = call => SourceScanEnumerationResult.Completed(
                new[] { EnumeratedTarget("s" + Math.Min(call, 2)) }, 0),
            WaitFor = call => call switch
            {
                1 => firstGate.Task,
                2 => replayGate.Task,
                _ => Task.CompletedTask,
            },
        };
        var scheduler = NewScheduler(executor, clock, enumerator: enumerator);

        var first = scheduler.RefreshTargetsAsync();
        await enumerator.WaitForCallsAsync(1).WaitAsync(TimeSpan.FromSeconds(10));
        Assert.False(await scheduler.RefreshTargetsAsync()); // coalesced while pass 1 enumerates
        firstGate.TrySetResult(true);
        await enumerator.WaitForCallsAsync(2).WaitAsync(TimeSpan.FromSeconds(10)); // the single replay

        // A request that arrives during the replay is coalesced but must NOT trigger a recursive
        // third pass from inside the replay (bounded: one replay per completed pass).
        Assert.False(await scheduler.RefreshTargetsAsync());
        replayGate.TrySetResult(true);
        Assert.True(await first.WaitAsync(TimeSpan.FromSeconds(10)));
        Assert.Equal(2, enumerator.Calls);

        // It is not lost either: the next completed pass replays it exactly once.
        Assert.True(await scheduler.TickAsync());
        Assert.Equal(3, enumerator.Calls);
        Assert.Contains(scheduler.Snapshot().Targets, target => target.SourceId == "s2");

        await scheduler.DisposeAsync();
    }

    // ---------------------------------------------------------------------------------------
    // FEA-11-SCAN-RH-1 (AC-RH-2): the scheduler lifetime token is linked into the refresh
    // enumeration; DisposeAsync cancels it first, then joins the in-flight refresh (bounded) before
    // the single-flight gate is torn down — so no ObjectDisposedException can escape to the log.
    // ---------------------------------------------------------------------------------------

    [Fact]
    public async Task DisposeAsync_WithInFlightRefresh_CancelsAndJoinsBeforeTeardown()
    {
        var clock = new ManualTimeProvider(Start);
        var executor = new FakeScanExecutor();
        var enumerator = new FakeTargetEnumerator { BlockUntilCancelled = true };
        var log = new CapturedLog();
        var scheduler = NewScheduler(executor, clock, log, enumerator: enumerator);

        var refresh = scheduler.RefreshTargetsAsync();
        await enumerator.Started.WaitAsync(TimeSpan.FromSeconds(10));

        var stopwatch = System.Diagnostics.Stopwatch.StartNew();
        var dispose = scheduler.DisposeAsync().AsTask();
        await dispose.WaitAsync(TimeSpan.FromSeconds(10));
        stopwatch.Stop();

        // AC-RH-2: the in-flight enumeration observed the scheduler lifetime cancellation and the
        // disposal joined it before returning (bounded, not abandoned).
        Assert.True(enumerator.CancellationObserved);
        await Assert.ThrowsAnyAsync<OperationCanceledException>(() => refresh);
        Assert.True(stopwatch.Elapsed < TimeSpan.FromSeconds(5),
            "DisposeAsync must be bounded, elapsed=" + stopwatch.Elapsed);

        // AC-RH-2: the gate is torn down only after the refresh pass stopped using it; a disposal
        // detail escaping into the Host log (the pre-fix warning) means the fix did not work.
        var allLogs = string.Join("\n", log.Info.Concat(log.Warn).Concat(log.Error));
        Assert.DoesNotContain("ObjectDisposedException", allLogs, StringComparison.Ordinal);
    }
}