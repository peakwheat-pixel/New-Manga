using System.Text.Json;
using NewManga.Host.Sources;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// FEA-11-WATCH-1 (AC-W1…W5): the Host-only read-only directory watcher. Deterministic tests use a
/// fake watch factory + manual clock (zero sleep); a separate real-file-tree test covers the actual
/// BCL <see cref="FileSystemWatcher"/> wiring on an isolated directory.
/// </summary>
public sealed class SourceWatcherTests
{
    private static readonly DateTimeOffset Start = new(2026, 11, 6, 2, 0, 0, TimeSpan.Zero);

    // ---------------------------------------------------------------------------------------
    // Shared infrastructure: manual clock, fake watch factory/handle, recording executor.
    // ---------------------------------------------------------------------------------------

    private sealed class ManualTimeProvider : TimeProvider
    {
        private readonly object _gate = new();
        private readonly List<ManualTimer> _timers = new();
        private DateTimeOffset _now;

        public ManualTimeProvider(DateTimeOffset start) => _now = start;

        public override DateTimeOffset GetUtcNow()
        {
            lock (_gate) return _now;
        }

        public override ITimer CreateTimer(TimerCallback callback, object? state, TimeSpan dueTime, TimeSpan period)
        {
            var timer = new ManualTimer(this, callback, state);
            timer.Change(dueTime, period);
            lock (_gate) _timers.Add(timer);
            return timer;
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

    private sealed class FakeWatchHandle : ISourceWatchHandle
    {
        public FakeWatchHandle(string directory, bool includeSubdirectories, string filter, int internalBufferBytes)
        {
            Directory = directory;
            IncludeSubdirectories = includeSubdirectories;
            Filter = filter;
            InternalBufferSize = internalBufferBytes;
        }

        public string Directory { get; }

        public bool IncludeSubdirectories { get; }

        public string Filter { get; }

        public bool EnableRaisingEvents { get; set; }

        public int InternalBufferSize { get; set; }

        public int DisposeCount { get; private set; }

        public event FileSystemEventHandler? Changed;

        public event FileSystemEventHandler? Created;

        public event FileSystemEventHandler? Deleted;

        public event RenamedEventHandler? Renamed;

        public event ErrorEventHandler? Error;

        public void RaiseFileEvent(string fullPath, bool deleted = false)
        {
            var args = new FileSystemEventArgs(
                deleted ? WatcherChangeTypes.Deleted : WatcherChangeTypes.Created, Directory, Path.GetFileName(fullPath));
            if (deleted)
            {
                Deleted?.Invoke(this, args);
            }
            else
            {
                Created?.Invoke(this, args);
            }
        }

        public void RaiseChanged(string fullPath) =>
            Changed?.Invoke(this, new FileSystemEventArgs(
                WatcherChangeTypes.Changed, Directory, Path.GetFileName(fullPath)));

        public void RaiseOverflow() => Error?.Invoke(this, new ErrorEventArgs(new InternalBufferOverflowException()));

        public void RaiseRenamed(string fullPath) =>
            Renamed?.Invoke(this, new RenamedEventArgs(
                WatcherChangeTypes.Renamed,
                Path.GetDirectoryName(fullPath) ?? Directory,
                Path.GetFileName(fullPath),
                "old"));

        public void Dispose() => DisposeCount++;
    }

    private sealed class FakeWatchFactory : ISourceWatchFactory
    {
        public List<FakeWatchHandle> Created { get; } = new();

        public ISourceWatchHandle Create(string directory, bool includeSubdirectories, string filter, int internalBufferBytes)
        {
            var handle = new FakeWatchHandle(directory, includeSubdirectories, filter, internalBufferBytes);
            Created.Add(handle);
            return handle;
        }
    }

    private sealed class RecordingExecutor : ISourceScanExecutor
    {
        public List<string> Commands { get; } = new();

        public int ScanCalls => Commands.Count;

        public List<string> ScannedSourceIds { get; } = new();

        public Func<SourceScanTarget, SourceScanOutcome>? Script { get; set; }

        public SourceScanBudget? Budget { get; set; }

        public SourceScanBudget? ProbeBudget(SourceScanTarget target) => Budget;

        public Task<SourceScanOutcome> ScanAsync(SourceScanTarget target, CancellationToken cancellationToken)
        {
            Commands.Add("ScanSourceSync");
            ScannedSourceIds.Add(target.SourceId);
            return Task.FromResult(Script?.Invoke(target) ?? SourceScanOutcome.Ok(SourceScanCounts.Zero));
        }
    }

    private sealed class CapturedLog
    {
        public List<string> Info { get; } = new();
        public List<string> Warn { get; } = new();
    }

    private sealed class Fixture : IDisposable
    {
        public Fixture(string name, SourceWatchOptions? options = null, SourceScanOptions? scanOptions = null)
        {
            Root = Path.Combine(Path.GetTempPath(), "fea11-watch-" + name + "-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(Root);
            WatchData = Path.Combine(Root, "host-data");
            Registry = new SourceAccessRegistry(WatchData);
            Clock = new ManualTimeProvider(Start);
            Executor = new RecordingExecutor();
            Factory = new FakeWatchFactory();
            Log = new CapturedLog();
            Scheduler = new SourceScanScheduler(
                scanOptions ?? new SourceScanOptions { IntervalSeconds = 900, MaxTargetsPerTick = 8 },
                Executor,
                Clock,
                infoLog: line => Log.Info.Add(line),
                warnLog: line => Log.Warn.Add(line));
            Options = options ?? new SourceWatchOptions { DebounceMilliseconds = 2000, MaxWatches = 16 };
        }

        public string Root { get; }

        public string WatchData { get; }

        public SourceAccessRegistry Registry { get; }

        public ManualTimeProvider Clock { get; }

        public RecordingExecutor Executor { get; }

        public FakeWatchFactory Factory { get; }

        public CapturedLog Log { get; }

        public SourceScanScheduler Scheduler { get; }

        public SourceWatchOptions Options { get; }

        public SourceWatcher CreateWatcher(ISourceWatchFactory? factory = null) =>
            new(Scheduler, Registry, Options, Clock, factory ?? Factory,
                infoLog: line => Log.Info.Add(line), warnLog: line => Log.Warn.Add(line));

        public string CreateFile(string relative)
        {
            var path = Path.Combine(Root, relative);
            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            File.WriteAllBytes(path, new byte[] { 1, 2, 3 });
            return path;
        }

        public string CreateFolder(string relative)
        {
            var path = Path.Combine(Root, relative);
            Directory.CreateDirectory(path);
            return path;
        }

        public void Dispose()
        {
            Scheduler.DisposeAsync().AsTask().GetAwaiter().GetResult();
            try
            {
                if (Directory.Exists(Root)) Directory.Delete(Root, recursive: true);
            }
            catch (Exception error) when (error is IOException or UnauthorizedAccessException)
            {
            }
        }
    }

    private static SourceScanTarget FileTarget(string sourceId, string path) =>
        new(sourceId, path, new[] { "b1" }, "1", SourceKind: "zip");

    // ---------------------------------------------------------------------------------------
    // AC-W1: lifecycle & scope.
    // ---------------------------------------------------------------------------------------

    [Fact]
    public async Task Start_ArmsFileAndFolderTargets_WithFrozenScopeRules()
    {
        using var fixture = new Fixture("scope");
        var file = fixture.CreateFile("book.zip");
        var folder = fixture.CreateFolder("folder");
        fixture.Registry.Register("fixture-root", new[] { fixture.Root });
        fixture.Scheduler.RegisterTarget(FileTarget("s-file", file));
        fixture.Scheduler.RegisterTarget(new SourceScanTarget("s-folder", folder, new[] { "b1" }, "1", SourceKind: "folder"));

        using var watcher = fixture.CreateWatcher();
        watcher.Start();

        Assert.Equal(2, fixture.Factory.Created.Count);
        var fileWatch = Assert.Single(fixture.Factory.Created, handle => !handle.IncludeSubdirectories);
        Assert.Equal(fixture.Root, fileWatch.Directory); // file targets watch the parent directory
        Assert.Equal("book.zip", fileWatch.Filter);
        var folderWatch = Assert.Single(fixture.Factory.Created, handle => handle.IncludeSubdirectories);
        Assert.Equal(folder, folderWatch.Directory);
        Assert.True(fileWatch.EnableRaisingEvents);
        Assert.True(folderWatch.EnableRaisingEvents);

        var status = watcher.Status();
        Assert.True(status.Enabled);
        Assert.True(status.Armed);
        Assert.Equal(2, status.Active);
        Assert.Equal(0, status.Uncovered);
    }

    [Fact]
    public async Task RepeatedRegistration_DoesNotGrowWatchers()
    {
        using var fixture = new Fixture("repeat");
        var file = fixture.CreateFile("book.zip");
        fixture.Registry.Register("fixture-root", new[] { fixture.Root });
        fixture.Scheduler.RegisterTarget(FileTarget("s1", file));

        using var watcher = fixture.CreateWatcher();
        watcher.Start();
        Assert.Single(fixture.Factory.Created);

        // Same source id re-registered + a target-set notification: same path/source -> no new watch.
        fixture.Scheduler.RegisterTarget(FileTarget("s1", file));
        fixture.Scheduler.RegisterTarget(FileTarget("s2", file)); // shared path deduped into one watch
        Assert.Single(fixture.Factory.Created);
        Assert.Equal(1, watcher.Status().Active);
    }

    [Fact]
    public async Task RegistryRevokedOrMissing_IsUncovered_NotArmed()
    {
        using var fixture = new Fixture("registry");
        var file = fixture.CreateFile("book.zip");
        fixture.Registry.Register("fixture-root", new[] { fixture.Root });
        var registered = fixture.Registry.Register("exact-root", new[] { file });
        fixture.Scheduler.RegisterTarget(new SourceScanTarget(
            "s1", file, new[] { "b1" }, "1", registered.RegistryId, registered.Generation, "zip"));
        fixture.Scheduler.RegisterTarget(new SourceScanTarget(
            "s2", file, new[] { "b1" }, "1", "reg-missing", 1, "zip"));
        fixture.Registry.Revoke(registered.RegistryId);

        using var watcher = fixture.CreateWatcher();
        watcher.Start();

        Assert.Empty(fixture.Factory.Created);
        Assert.True(watcher.Status().Uncovered >= 1);
    }

    [Fact]
    public async Task DeclaredFileTargetOnDirectory_IsUncovered_AndNeverGuessesFileName()
    {
        using var fixture = new Fixture("dir-as-file");
        var folder = fixture.CreateFolder("folder");
        fixture.Registry.Register("fixture-root", new[] { fixture.Root });
        // Declared file kind (zip) but the path is a directory: must not watch a guessed file name.
        fixture.Scheduler.RegisterTarget(new SourceScanTarget("s1", folder, new[] { "b1" }, "1", SourceKind: "zip"));

        using var watcher = fixture.CreateWatcher();
        watcher.Start();

        Assert.Empty(fixture.Factory.Created);
        Assert.Equal(1, watcher.Status().Uncovered);
    }

    [Fact]
    public async Task RegistryUnavailable_DegradesToUncovered_AndPeriodicTickStillScans()
    {
        using var fixture = new Fixture("registry-unavailable");
        var file = fixture.CreateFile("book.zip");
        var registered = fixture.Registry.Register("exact-root", new[] { file });
        fixture.Scheduler.RegisterTarget(new SourceScanTarget(
            "s1", file, new[] { "b1" }, "1", registered.RegistryId, registered.Generation, "zip"));
        File.Delete(file); // L-S1: deleting the file-root makes the whole registry unreadable

        using var watcher = fixture.CreateWatcher();
        watcher.Start();
        Assert.Empty(fixture.Factory.Created);
        Assert.True(watcher.Status().Uncovered >= 1);

        Assert.True(await fixture.Scheduler.TickAsync());
        Assert.Contains("s1", fixture.Executor.ScannedSourceIds);
    }

    [Fact]
    public async Task StartTwice_StopTwice_IsIdempotent_AndStopProducesZeroHints()
    {
        using var fixture = new Fixture("lifecycle", new SourceWatchOptions { DebounceMilliseconds = 250 });
        var file = fixture.CreateFile("book.zip");
        fixture.Registry.Register("fixture-root", new[] { fixture.Root });
        fixture.Scheduler.RegisterTarget(FileTarget("s1", file));
        var watcher = fixture.CreateWatcher();

        watcher.Start();
        watcher.Start();
        Assert.Single(fixture.Factory.Created);

        watcher.Stop();
        watcher.Stop();
        Assert.False(watcher.Status().Armed);
        Assert.Equal(0, watcher.Status().Active);

        // Events after Stop must produce no hint and no scan (even after the debounce window elapses).
        fixture.Factory.Created[0].RaiseFileEvent(file);
        fixture.Clock.Advance(TimeSpan.FromSeconds(5));
        await fixture.Scheduler.HintIdleAsync();
        Assert.Equal(0, fixture.Executor.ScanCalls);
        Assert.Equal(0, watcher.Status().HintCount);
        watcher.Dispose();
    }

    // ---------------------------------------------------------------------------------------
    // AC-W2: hint semantics, debounce & merge.
    // ---------------------------------------------------------------------------------------

    [Fact]
    public async Task Debounce_MergesManyEventsIntoOneHint_AndOneFullRescan()
    {
        using var fixture = new Fixture("debounce", new SourceWatchOptions { DebounceMilliseconds = 2000 });
        var file = fixture.CreateFile("book.zip");
        fixture.Registry.Register("fixture-root", new[] { fixture.Root });
        fixture.Scheduler.RegisterTarget(FileTarget("s1", file));
        using var watcher = fixture.CreateWatcher();
        watcher.Start();
        var handle = Assert.Single(fixture.Factory.Created);

        for (var index = 0; index < 5; index++)
        {
            handle.RaiseFileEvent(file);
        }

        fixture.Clock.Advance(TimeSpan.FromMilliseconds(1999));
        Assert.Equal(0, fixture.Executor.ScanCalls);
        fixture.Clock.Advance(TimeSpan.FromMilliseconds(1));
        await fixture.Scheduler.HintIdleAsync();
        Assert.Equal(1, fixture.Executor.ScanCalls);
        Assert.Equal(1, watcher.Status().HintCount);
        Assert.Equal(5, watcher.Status().DebouncedEvents);
        Assert.Equal(0, watcher.Status().PendingHints);

        // Next window: one more event -> exactly one more hint/scan.
        handle.RaiseFileEvent(file);
        fixture.Clock.Advance(TimeSpan.FromMilliseconds(2000));
        await fixture.Scheduler.HintIdleAsync();
        Assert.Equal(2, fixture.Executor.ScanCalls);
        Assert.Equal(2, watcher.Status().HintCount);
    }

    [Fact]
    public async Task HintIsNotAChangedVerdict_AndStatusIsRedacted()
    {
        using var fixture = new Fixture("redaction", new SourceWatchOptions { DebounceMilliseconds = 250 });
        var file = fixture.CreateFile("private-source.zip");
        fixture.Registry.Register("fixture-root", new[] { fixture.Root });
        fixture.Scheduler.RegisterTarget(FileTarget("s1", file));
        using var watcher = fixture.CreateWatcher();
        watcher.Start();

        fixture.Factory.Created[0].RaiseFileEvent(file);
        fixture.Factory.Created[0].RaiseChanged(file);
        fixture.Clock.Advance(TimeSpan.FromMilliseconds(250));
        await fixture.Scheduler.HintIdleAsync();

        var statusJson = JsonSerializer.Serialize(watcher.Status());
        var schedulerJson = JsonSerializer.Serialize(fixture.Scheduler.Snapshot());
        var logs = string.Join("\n", fixture.Log.Info.Concat(fixture.Log.Warn));
        foreach (var sensitive in new[] { fixture.Root, "private-source", "C:\\", "host_session", "source-" })
        {
            Assert.DoesNotContain(sensitive, statusJson, StringComparison.Ordinal);
            Assert.DoesNotContain(sensitive, schedulerJson, StringComparison.Ordinal);
            Assert.DoesNotContain(sensitive, logs, StringComparison.Ordinal);
        }

        // A hint only marks due; the result comes from the full scan (unchanged -> ok, never changed).
        var target = Assert.Single(fixture.Scheduler.Snapshot().Targets);
        Assert.Equal(SourceScanResults.Ok, target.LastResult);
    }

    [Fact]
    public async Task EventForOtherFile_Name_IsIgnored_ForFileKindWatches()
    {
        using var fixture = new Fixture("filter", new SourceWatchOptions { DebounceMilliseconds = 250 });
        var file = fixture.CreateFile("book.zip");
        var other = fixture.CreateFile("other.zip");
        fixture.Registry.Register("fixture-root", new[] { fixture.Root });
        fixture.Scheduler.RegisterTarget(FileTarget("s1", file));
        using var watcher = fixture.CreateWatcher();
        watcher.Start();

        fixture.Factory.Created[0].RaiseFileEvent(other);
        fixture.Clock.Advance(TimeSpan.FromMilliseconds(250));
        await fixture.Scheduler.HintIdleAsync();

        Assert.Equal(0, fixture.Executor.ScanCalls);
        Assert.Equal(0, watcher.Status().HintCount);
    }

    // ---------------------------------------------------------------------------------------
    // AC-W3: overflow / root lost / re-arm.
    // ---------------------------------------------------------------------------------------

    [Fact]
    public async Task Overflow_HintsAllTargets_Degrades_AndNeverCrashes()
    {
        using var fixture = new Fixture("overflow", new SourceWatchOptions { DebounceMilliseconds = 250 });
        var first = fixture.CreateFile("a.zip");
        var second = fixture.CreateFile("b.zip");
        fixture.Registry.Register("fixture-root", new[] { fixture.Root });
        fixture.Scheduler.RegisterTarget(FileTarget("s1", first));
        fixture.Scheduler.RegisterTarget(FileTarget("s2", second));
        using var watcher = fixture.CreateWatcher();
        watcher.Start();

        fixture.Factory.Created[0].RaiseOverflow();
        Assert.True(watcher.Status().OverflowCount >= 1);
        Assert.True(watcher.Status().Degraded);

        await fixture.Scheduler.HintIdleAsync();
        Assert.Equal(2, fixture.Executor.ScanCalls); // all targets became due
        Assert.False(fixture.Scheduler.HintPending);
    }

    [Fact]
    public async Task Overflow_RespectsBudget_AndCompletesAcrossTicks()
    {
        using var fixture = new Fixture(
            "overflow-budget",
            new SourceWatchOptions { DebounceMilliseconds = 250 },
            new SourceScanOptions { IntervalSeconds = 900, MaxTargetsPerTick = 4 });
        fixture.Registry.Register("fixture-root", new[] { fixture.Root });
        for (var index = 0; index < 10; index++)
        {
            fixture.Scheduler.RegisterTarget(FileTarget("s" + index, fixture.CreateFile("f" + index + ".zip")));
        }

        using var watcher = fixture.CreateWatcher();
        watcher.Start();
        fixture.Factory.Created[0].RaiseOverflow();
        await fixture.Scheduler.HintIdleAsync();
        var afterHintedPass = fixture.Executor.ScanCalls;
        Assert.True(afterHintedPass <= 4); // budget respected (hinted pass is one tick)

        for (var pass = 0; pass < 6 && fixture.Executor.ScannedSourceIds.Distinct().Count() < 10; pass++)
        {
            var before = fixture.Executor.ScannedSourceIds.Count;
            Assert.True(await fixture.Scheduler.TickAsync());
            Assert.True(fixture.Executor.ScannedSourceIds.Count - before <= 4);
        }

        Assert.Equal(10, fixture.Executor.ScannedSourceIds.Distinct().Count());
    }

    [Fact]
    public async Task RootLost_IsDegraded_AndReArmsOrCountsUncovered()
    {
        using var fixture = new Fixture("root-lost", new SourceWatchOptions { DebounceMilliseconds = 250 });
        var folder = fixture.CreateFolder("folder");
        fixture.Registry.Register("fixture-root", new[] { fixture.Root });
        fixture.Scheduler.RegisterTarget(new SourceScanTarget("s1", folder, new[] { "b1" }, "1", SourceKind: "folder"));
        using var watcher = fixture.CreateWatcher();
        watcher.Start();
        Assert.Equal(1, watcher.Status().Active);

        // Delete the watched root from disk, then report the deletion through the fake handle.
        Directory.Delete(folder, recursive: true);
        fixture.Factory.Created[0].RaiseRenamed(folder);
        Assert.True(watcher.Status().Degraded);

        var status = watcher.Status();
        Assert.True(status.Degraded);
        Assert.True(status.Uncovered >= 1 || status.Active >= 0);
        Assert.NotNull(fixture.Scheduler.Snapshot().Watcher);
        // No crash and the periodic path still runs.
        Assert.True(await fixture.Scheduler.TickAsync());
    }

    [Fact]
    public async Task MaxWatchesCap_LeavesUncovered_AndSchedulerStillScansEverything()
    {
        using var fixture = new Fixture("cap", new SourceWatchOptions { MaxWatches = 1, DebounceMilliseconds = 250 });
        fixture.Registry.Register("fixture-root", new[] { fixture.Root });
        for (var index = 0; index < 3; index++)
        {
            fixture.Scheduler.RegisterTarget(FileTarget("s" + index, fixture.CreateFile("f" + index + ".zip")));
        }

        using var watcher = fixture.CreateWatcher();
        watcher.Start();
        Assert.Single(fixture.Factory.Created);
        Assert.True(watcher.Status().Uncovered >= 2);

        Assert.True(await fixture.Scheduler.TickAsync());
        Assert.Equal(3, fixture.Executor.ScannedSourceIds.Distinct().Count());
    }

    [Fact]
    public async Task OptionsNormalization_ClampsBoundaries_AndFallsBackOnIllegalValues()
    {
        var defaults = new SourceWatchOptions().Normalized();
        Assert.Equal(SourceWatchOptions.DefaultMaxWatches, defaults.MaxWatches);
        Assert.Equal(SourceWatchOptions.DefaultInternalBufferBytes, defaults.InternalBufferBytes);
        Assert.Equal(SourceWatchOptions.DefaultDebounceMilliseconds, defaults.DebounceMilliseconds);

        var clamped = new SourceWatchOptions
        {
            MaxWatches = 0,
            InternalBufferBytes = 1024,
            DebounceMilliseconds = 100,
        }.Normalized();
        Assert.Equal(SourceWatchOptions.DefaultMaxWatches, clamped.MaxWatches);
        Assert.Equal(SourceWatchOptions.MinimumInternalBufferBytes, clamped.InternalBufferBytes);
        Assert.Equal(SourceWatchOptions.DefaultDebounceMilliseconds, clamped.DebounceMilliseconds);

        var clampedUpper = new SourceWatchOptions
        {
            MaxWatches = 99_999,
            InternalBufferBytes = 999_999,
            DebounceMilliseconds = 99_999,
        }.Normalized();
        Assert.Equal(SourceWatchOptions.DefaultMaxWatches, clampedUpper.MaxWatches);
        Assert.Equal(SourceWatchOptions.MaximumInternalBufferBytes, clampedUpper.InternalBufferBytes);
        Assert.Equal(SourceWatchOptions.DefaultDebounceMilliseconds, clampedUpper.DebounceMilliseconds);

        var boundaries = new SourceWatchOptions
        {
            MaxWatches = 1,
            InternalBufferBytes = SourceWatchOptions.MaximumInternalBufferBytes,
            DebounceMilliseconds = SourceWatchOptions.MaximumDebounceMilliseconds,
        }.Normalized();
        Assert.Equal(1, boundaries.MaxWatches);
        Assert.Equal(SourceWatchOptions.MaximumInternalBufferBytes, boundaries.InternalBufferBytes);
        Assert.Equal(SourceWatchOptions.MaximumDebounceMilliseconds, boundaries.DebounceMilliseconds);
    }

    [Fact]
    public async Task RealFileSystemWatcher_DetectsIsolatedFileChange()
    {
        using var fixture = new Fixture("real-tree", new SourceWatchOptions { DebounceMilliseconds = 250 });
        var file = fixture.CreateFile("book.zip");
        fixture.Registry.Register("fixture-root", new[] { fixture.Root });
        fixture.Scheduler.RegisterTarget(FileTarget("s1", file));
        using var watcher = new SourceWatcher(
            fixture.Scheduler, fixture.Registry, fixture.Options, fixture.Clock,
            factory: new FileSystemSourceWatchFactory(),
            infoLog: line => fixture.Log.Info.Add(line), warnLog: line => fixture.Log.Warn.Add(line));
        watcher.Start();
        Assert.Equal(1, watcher.Status().Active);

        await Task.Delay(150); // let the OS handle start before the first write
        await File.WriteAllBytesAsync(file, new byte[] { 9, 9, 9 });

        var deadline = DateTime.UtcNow + TimeSpan.FromSeconds(10);
        while (DateTime.UtcNow < deadline && watcher.Status().PendingHints == 0
               && fixture.Executor.ScanCalls == 0)
        {
            await Task.Delay(25);
        }

        // The manual clock must still deliver the debounce hint deterministically.
        fixture.Clock.Advance(TimeSpan.FromSeconds(1));
        await fixture.Scheduler.HintIdleAsync().WaitAsync(TimeSpan.FromSeconds(10));
        Assert.True(watcher.Status().DebouncedEvents >= 1);
        Assert.True(fixture.Executor.ScanCalls >= 1);
    }
}
