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

        public SourceScanBudget? ProbeBudget(SourceScanTarget target) => Budget;

        public async Task<SourceScanOutcome> ScanAsync(SourceScanTarget target, CancellationToken cancellationToken)
        {
            List<TaskCompletionSource<bool>> signals;
            lock (_gate)
            {
                ScannedSourceIds.Add(target.SourceId);
                IssuedCommands.Add("ScanSourceSync");
                signals = _scanWaiters.Where(waiter => waiter.Count <= ScannedSourceIds.Count)
                    .Select(waiter => waiter.Signal).ToList();
                _scanWaiters.RemoveAll(waiter => waiter.Count <= ScannedSourceIds.Count);
            }

            foreach (var signal in signals) signal.TrySetResult(true);
            if (Block is { } block) await block.Task.ConfigureAwait(false);
            cancellationToken.ThrowIfCancellationRequested();
            return Script?.Invoke(target) ?? SourceScanOutcome.Ok(SourceScanCounts.Zero);
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
        Action<string, string>? error = null)
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
            errorLog);
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
}
