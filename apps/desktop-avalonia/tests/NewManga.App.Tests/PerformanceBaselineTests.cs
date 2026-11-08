using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.Views.Presentation;
using NewManga.Appearance;
using NewManga.DesignSystem.Theming;
using Xunit;
using Xunit.Abstractions;
using Xunit.Sdk;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-07 AC6 / H3 / W-5 + FEA-07-RESIDUAL-2 AC-R4a-3: runtime frontend switch performance baseline.
/// The frozen W-5 gate is unchanged — hot switch p95 ≤ <b>1000 ms</b> — and it is judged as the
/// <b>median of three independent runs</b> (each run: 4 warmups + 20 measured one-way switches); each run
/// records its own p95/max. The default suite ALSO RECORDS <c>uiThreadSchedulingGapMs</c> (largest gap between
/// UI-thread heartbeats) but does not assert it: Review r2 measured 513.55 ms in the parallel full-suite run vs
/// 249.44 ms serial, so the gap ASSERTION lives in the dedicated gated test
/// (<see cref="Gated_HotSwitch_UiThreadSchedulingGapStaysWithinThePerfGateBudget"/>, <c>NEWMANGA_FEA07_PERF=1</c>,
/// run by <c>verification/FEA-07-RESIDUAL-2/tools/verify-fea07-perf.ps1</c>) and is skipped with a reason by
/// default. Real-scale synthetic loads (N ∈ {50, 200, 500} books through
/// <see cref="FakeHostController.ReadySnapshot"/>) are measured separately and recorded (p50/p95) — the cold
/// first switch is recorded but never enters the gate. Metrics are written to a JSON evidence file.
/// </summary>
public sealed class PerformanceBaselineTests : IDisposable
{
    private const int WarmupSwitches = 4;
    // 20 samples are required for the frozen p95 gate to be a real p95: with n samples the used
    // percentile rank is ceil(0.95*n)-1, so n=12 resolves to the maximum sample while n=20 excludes the
    // single worst outlier. The transaction now includes the real frame-render gate (R-001), which makes
    // one-off GC/frame outliers more visible; the gate stays p95 <= 1000 ms (W-5).
    private const int MeasuredSwitches = 20;

    /// <summary>W-5 frozen threshold (must not change: FEA-07 AC6 / ADJ §2 W-05).</summary>
    private const double P95BudgetMilliseconds = 1000.0;

    /// <summary>AC-R4a-3: the gate is the median of this many independent runs.</summary>
    private const int IndependentRuns = 3;

    /// <summary>
    /// AC-R4a-3 (r2 R2-001/R2-003): UI-thread heartbeat budget for the <b>dedicated serial perf gate</b> only.
    /// Calibration basis (2026-11-08, Release, headless):
    /// <list type="bullet">
    /// <item>idle serial worst gap <b>249.44 ms</b> over the committed 3-round calibration
    /// (<c>verification/FEA-07-RESIDUAL-2/evidence/ui-gap-calibration-r4a.json</c>);</item>
    /// <item>loaded serial worst <b>460.88 ms</b> over 3 gated rounds while an external application was using
    /// the machine; parallel full-suite <b>619.00 ms</b> (this rework) and <b>513.55 ms</b> (Review r2) —
    /// see <c>evidence/ui-gap-loaded-condition-r2a.json</c>.</item>
    /// </list>
    /// The value written down here is <b>700 ms</b>: 1.52x the worst loaded serial observation and 2.81x the
    /// idle one, so the gate is not flaky on an ordinary workstation that is doing other work, while a UI
    /// thread frozen for ≥700 ms is still caught. Serial/idle is the only supported condition — the default
    /// suite records <c>uiThreadSchedulingGapMs</c> and never asserts it.
    /// </summary>
    private const double UiThreadSchedulingGapBudgetMs = 700.0;

    private const int ScaleWarmupSwitches = 2;
    private const int ScaleMeasuredSwitches = 10;

    private static readonly (string Label, int Books)[] ScaleLoads =
    {
        ("n50", 50),
        ("n200", 200),
        ("n500", 500),
    };

    private readonly string _root;
    private readonly ITestOutputHelper _output;

    public PerformanceBaselineTests(ITestOutputHelper output)
    {
        _output = output;
        _root = Path.Combine(Path.GetTempPath(), $"nm-fea07-perf-{Guid.NewGuid():N}");
        Directory.CreateDirectory(_root);
    }

    public void Dispose()
    {
        try
        {
            Directory.Delete(_root, recursive: true);
        }
        catch (IOException)
        {
            // best-effort cleanup
        }
    }

    /// <summary>
    /// Default-suite gate: only the frozen W-5 p95 (median of three independent runs) is asserted.
    /// <c>uiThreadSchedulingGapMs</c> is recorded for diagnosis/traceability (r2 R2-001) but never gated here.
    /// </summary>
    [AvaloniaFact]
    public async Task HotSwitch_P95MedianOfThreeIndependentRuns_StaysWithinTheFrozenW5Budget()
    {
        var measurement = await MeasureHotSwitchAsync();
        var runs = measurement.Runs;
        var p95Values = measurement.P95Values;
        var medianP95 = measurement.MedianP95;
        var p95Passed = medianP95 <= P95BudgetMilliseconds;

        var metrics = new
        {
            metric = "FEA-07 hot frontend switch",
            ac = "FEA-07 AC6 / W-5 + FEA-07-RESIDUAL-2 AC-R4a-3",
            suite = "default",
            machine = Environment.MachineName,
            os = Environment.OSVersion.ToString(),
            dotnet = Environment.Version.ToString(),
            config = "headless Avalonia UI thread; real AppShellV2/FluentShellSurface factories",
            warmupSwitches = WarmupSwitches,
            measuredSwitches = MeasuredSwitches,
            independentRuns = IndependentRuns,
            budgetP95Ms = P95BudgetMilliseconds,
            gapGateApplied = false,
            gapRecordedOnlyNote = "uiThreadSchedulingGapMs is recorded in the default suite; its assertion lives in the gated perf test (NEWMANGA_FEA07_PERF=1) because the metric is load-sensitive.",
            uiThreadSchedulingGapPerfGateBudgetMs = UiThreadSchedulingGapBudgetMs,
            runs = runs.Select(run => new
            {
                run = run.Run,
                coldFirstSwitchMs = Round(run.ColdFirstSwitchMs),
                p50Ms = Round(run.P50Ms),
                p95Ms = Round(run.P95Ms),
                maxMs = Round(run.MaxMs),
                uiThreadSchedulingGapMs = Round(run.UiThreadSchedulingGapMs),
                uiThreadHeartbeatTicks = run.UiThreadHeartbeatTicks,
                samplesMs = run.Samples.Select(Round).ToArray(),
                managedMemoryDeltaBytes = run.ManagedMemoryDeltaBytes,
                handleDelta = run.HandleDelta,
            }).ToArray(),
            medianP50Ms = Round(measurement.MedianP50),
            medianP95Ms = Round(medianP95),
            worstRunP95Ms = Round(measurement.WorstRunP95),
            worstUiThreadSchedulingGapMs = Round(measurement.WorstUiGap),
            p95Passed = p95Passed,
            passed = p95Passed,
        };

        var json = JsonSerializer.Serialize(metrics, new JsonSerializerOptions { WriteIndented = true });
        var metricsPath = WriteEvidence("NEWMANGA_FEA07_METRICS_PATH", "nm-fea07-performance-baseline.json", json);
        _output.WriteLine(json);
        _output.WriteLine("metrics-path: " + metricsPath);

        Assert.True(
            p95Passed,
            $"hot switch median p95 {medianP95:0.0} ms exceeds the frozen W-5 budget {P95BudgetMilliseconds:0} ms "
            + $"(runs: {string.Join(", ", p95Values.Select(value => value.ToString("0.0")))}; metrics: {metricsPath})");
        AssertFrozenShape(measurement);
    }

    /// <summary>
    /// Dedicated serial performance gate (r2 R2-001): asserts the calibrated <c>uiThreadSchedulingGapMs</c>
    /// budget in addition to the frozen p95 gate. Skipped with a reason by default — the metric is only stable
    /// in a serial/idle run (<c>verification/FEA-07-RESIDUAL-2/tools/verify-fea07-perf.ps1</c> sets
    /// <c>NEWMANGA_FEA07_PERF=1</c>).
    /// </summary>
    [PerfGateAvaloniaFact]
    public async Task Gated_HotSwitch_UiThreadSchedulingGapStaysWithinThePerfGateBudget()
    {
        var measurement = await MeasureHotSwitchAsync();
        var runs = measurement.Runs;
        var p95Values = measurement.P95Values;
        var medianP95 = measurement.MedianP95;
        var p95Passed = medianP95 <= P95BudgetMilliseconds;
        var gapPassed = measurement.WorstUiGap <= UiThreadSchedulingGapBudgetMs;
        var gapValues = runs.Select(run => run.UiThreadSchedulingGapMs).OrderBy(value => value).ToArray();
        var gapP95 = Percentile(gapValues, 0.95);

        var metrics = new
        {
            metric = "FEA-07 hot frontend switch (dedicated serial perf gate)",
            ac = "FEA-07-RESIDUAL-2 AC-R4a-3 (r2 R2-001)",
            suite = "gated",
            gatedBy = "NEWMANGA_FEA07_PERF=1",
            machine = Environment.MachineName,
            os = Environment.OSVersion.ToString(),
            dotnet = Environment.Version.ToString(),
            config = "headless Avalonia UI thread; real AppShellV2/FluentShellSurface factories; serial run",
            warmupSwitches = WarmupSwitches,
            measuredSwitches = MeasuredSwitches,
            independentRuns = IndependentRuns,
            budgetP95Ms = P95BudgetMilliseconds,
            uiThreadSchedulingGapBudgetMs = UiThreadSchedulingGapBudgetMs,
            runs = runs.Select(run => new
            {
                run = run.Run,
                coldFirstSwitchMs = Round(run.ColdFirstSwitchMs),
                p50Ms = Round(run.P50Ms),
                p95Ms = Round(run.P95Ms),
                maxMs = Round(run.MaxMs),
                uiThreadSchedulingGapMs = Round(run.UiThreadSchedulingGapMs),
                uiThreadHeartbeatTicks = run.UiThreadHeartbeatTicks,
                samplesMs = run.Samples.Select(Round).ToArray(),
                managedMemoryDeltaBytes = run.ManagedMemoryDeltaBytes,
                handleDelta = run.HandleDelta,
            }).ToArray(),
            medianP50Ms = Round(measurement.MedianP50),
            medianP95Ms = Round(medianP95),
            worstRunP95Ms = Round(measurement.WorstRunP95),
            worstUiThreadSchedulingGapMs = Round(measurement.WorstUiGap),
            uiThreadSchedulingGapP95Ms = Round(gapP95),
            p95Passed = p95Passed,
            gapPassed = gapPassed,
            passed = p95Passed && gapPassed,
        };

        var json = JsonSerializer.Serialize(metrics, new JsonSerializerOptions { WriteIndented = true });
        var metricsPath = WriteEvidence("NEWMANGA_FEA07_PERF_GATE_PATH", "nm-fea07-perf-gate.json", json);
        _output.WriteLine(json);
        _output.WriteLine("metrics-path: " + metricsPath);

        Assert.True(
            p95Passed,
            $"hot switch median p95 {medianP95:0.0} ms exceeds the frozen W-5 budget {P95BudgetMilliseconds:0} ms (metrics: {metricsPath})");
        Assert.True(
            gapPassed,
            $"ui thread scheduling gap {measurement.WorstUiGap:0.0} ms exceeds the calibrated {UiThreadSchedulingGapBudgetMs:0} ms perf-gate budget (metrics: {metricsPath})");
        AssertFrozenShape(measurement);
    }

    private void AssertFrozenShape(HotSwitchMeasurement measurement)
    {
        // AC-R4a-3 pins the frozen shape itself: the gate is the median of exactly three independent runs,
        // so a future single-run (or two-run) gate cannot silently pass as "the frozen gate".
        Assert.Equal(3, measurement.Runs.Count);
        Assert.Equal(3, IndependentRuns);
        Assert.Equal(measurement.P95Values[1], measurement.MedianP95);
        Assert.All(measurement.Runs, run => Assert.True(run.Samples.Count == MeasuredSwitches));
    }

    private async Task<HotSwitchMeasurement> MeasureHotSwitchAsync()
    {
        var application = Application.Current!;
        using var themeManager = new DesignSystemThemeManager(application);
        themeManager.Initialize();
        var appearance = new AppearanceCoordinator(new AppearanceStore(Path.Combine(_root, "presentation-settings.json")));
        appearance.Reload();

        var runs = new List<HotSwitchRun>(IndependentRuns);
        for (var run = 1; run <= IndependentRuns; run++)
        {
            runs.Add(await MeasureHotSwitchRunAsync(application, themeManager, appearance, run));
        }

        var p95Values = runs.Select(run => run.P95Ms).OrderBy(value => value).ToArray();
        var p50Values = runs.Select(run => run.P50Ms).OrderBy(value => value).ToArray();
        return new HotSwitchMeasurement(
            runs,
            p50Values[p50Values.Length / 2],
            p95Values[p95Values.Length / 2],
            p95Values[^1],
            runs.Max(run => run.UiThreadSchedulingGapMs),
            p95Values);
    }

    [AvaloniaFact]
    public async Task ScaleLoad_RecordsP50AndP95ForRealSyntheticScale()
    {
        var application = Application.Current!;
        using var themeManager = new DesignSystemThemeManager(application);
        themeManager.Initialize();
        var appearance = new AppearanceCoordinator(new AppearanceStore(Path.Combine(_root, "presentation-settings.json")));
        appearance.Reload();

        var results = new List<ScaleLoadResult>(ScaleLoads.Length);
        foreach (var (label, books) in ScaleLoads)
        {
            results.Add(await MeasureScaleLoadAsync(application, themeManager, appearance, label, books));
        }

        var metrics = new
        {
            metric = "FEA-07 hot frontend switch under real synthetic scale",
            ac = "FEA-07-RESIDUAL-2 AC-R4a-3 (recorded, not part of the W-5 gate)",
            machine = Environment.MachineName,
            os = Environment.OSVersion.ToString(),
            dotnet = Environment.Version.ToString(),
            config = "headless Avalonia UI thread; FakeHostController.ReadySnapshot(N books)",
            warmupSwitches = ScaleWarmupSwitches,
            measuredSwitches = ScaleMeasuredSwitches,
            loads = results.Select(result => new
            {
                label = result.Label,
                books = result.Books,
                booksInSnapshot = result.BooksInSnapshot,
                coldFirstSwitchMs = Round(result.ColdFirstSwitchMs),
                p50Ms = Round(result.P50Ms),
                p95Ms = Round(result.P95Ms),
                maxMs = Round(result.MaxMs),
                samplesMs = result.Samples.Select(Round).ToArray(),
            }).ToArray(),
        };

        var json = JsonSerializer.Serialize(metrics, new JsonSerializerOptions { WriteIndented = true });
        var metricsPath = WriteEvidence("NEWMANGA_FEA07_SCALE_METRICS_PATH", "nm-fea07-performance-scale.json", json);
        _output.WriteLine(json);
        _output.WriteLine("metrics-path: " + metricsPath);

        Assert.Equal(ScaleLoads.Length, results.Count);
        Assert.All(
            results,
            result =>
            {
                Assert.Equal(result.Books, result.BooksInSnapshot);
                Assert.Equal(ScaleMeasuredSwitches, result.Samples.Count);
                Assert.All(result.Samples, sample => Assert.True(sample >= 0));
                Assert.True(result.P95Ms >= result.P50Ms);
            });
    }

    private async Task<HotSwitchRun> MeasureHotSwitchRunAsync(
        Application application,
        DesignSystemThemeManager themeManager,
        AppearanceCoordinator appearance,
        int run)
    {
        var options = AppOptions.Parse(new[] { "--presentation-host=true" });
        var selection = FrontendSelector.Select(FrontendSelector.CurrentV2FrontendId, persistedFrontendId: null);
        var themeHome = ThemeHome(options, run);

        var window = App.CreatePresentationShell(
            options, NullHostController.Instance, selection, appearance, themeHome, themeManager, application);
        var presentation = Assert.IsType<PresentationWindow>(window);
        // R-001: the switch transaction now commits only after the real layout/Loaded/frame-render gates,
        // which require a laid-out window; the measured path is the production path.
        presentation.Show();

        var coldWatch = Stopwatch.StartNew();
        var cold = await presentation.SwitchFrontendAsync(FrontendSelector.FluentFrontendId);
        coldWatch.Stop();
        Assert.True(cold.Succeeded, cold.Failure);

        var samples = new List<double>(MeasuredSwitches);
        using var heartbeat = new UiThreadHeartbeat();
        try
        {
            for (var i = 0; i < WarmupSwitches; i++)
            {
                var target = i % 2 == 0 ? FrontendSelector.CurrentV2FrontendId : FrontendSelector.FluentFrontendId;
                var warmup = await presentation.SwitchFrontendAsync(target);
                Assert.True(warmup.Succeeded, warmup.Failure);
            }

            var process = Process.GetCurrentProcess();
            var handlesBefore = process.HandleCount;
            var memoryBefore = GC.GetTotalMemory(forceFullCollection: true);

            heartbeat.Start();
            for (var i = 0; i < MeasuredSwitches; i++)
            {
                var target = i % 2 == 0 ? FrontendSelector.CurrentV2FrontendId : FrontendSelector.FluentFrontendId;
                var watch = Stopwatch.StartNew();
                var result = await presentation.SwitchFrontendAsync(target);
                watch.Stop();
                Assert.True(result.Succeeded, result.Failure);
                samples.Add(watch.Elapsed.TotalMilliseconds);
            }

            heartbeat.Stop();
            var memoryAfter = GC.GetTotalMemory(forceFullCollection: true);
            process.Refresh();
            var handlesAfter = process.HandleCount;

            var ordered = samples.OrderBy(milliseconds => milliseconds).ToArray();
            return new HotSwitchRun(
                run,
                coldWatch.Elapsed.TotalMilliseconds,
                Percentile(ordered, 0.50),
                Percentile(ordered, 0.95),
                ordered[^1],
                heartbeat.MaxGapMs,
                heartbeat.Ticks,
                samples,
                memoryAfter - memoryBefore,
                handlesAfter - handlesBefore);
        }
        finally
        {
            presentation.Close();
        }
    }

    private async Task<ScaleLoadResult> MeasureScaleLoadAsync(
        Application application,
        DesignSystemThemeManager themeManager,
        AppearanceCoordinator appearance,
        string label,
        int books)
    {
        var titles = Enumerable.Range(0, books)
            .Select(index => $"合成负载书籍 {index:D4}")
            .ToArray();
        var host = new FakeHostController(FakeHostController.ReadySnapshot(titles));
        var options = AppOptions.Parse(new[] { "--presentation-host=true" });
        var selection = FrontendSelector.Select(FrontendSelector.CurrentV2FrontendId, persistedFrontendId: null);
        var themeHome = ThemeHome(options, books);

        var window = App.CreatePresentationShell(
            options, host, selection, appearance, themeHome, themeManager, application);
        var presentation = Assert.IsType<PresentationWindow>(window);
        presentation.Show();

        var coldWatch = Stopwatch.StartNew();
        var cold = await presentation.SwitchFrontendAsync(FrontendSelector.FluentFrontendId);
        coldWatch.Stop();
        Assert.True(cold.Succeeded, cold.Failure);

        var samples = new List<double>(ScaleMeasuredSwitches);
        try
        {
            for (var i = 0; i < ScaleWarmupSwitches; i++)
            {
                var target = i % 2 == 0 ? FrontendSelector.CurrentV2FrontendId : FrontendSelector.FluentFrontendId;
                var warmup = await presentation.SwitchFrontendAsync(target);
                Assert.True(warmup.Succeeded, warmup.Failure);
            }

            for (var i = 0; i < ScaleMeasuredSwitches; i++)
            {
                var target = i % 2 == 0 ? FrontendSelector.CurrentV2FrontendId : FrontendSelector.FluentFrontendId;
                var watch = Stopwatch.StartNew();
                var result = await presentation.SwitchFrontendAsync(target);
                watch.Stop();
                Assert.True(result.Succeeded, result.Failure);
                samples.Add(watch.Elapsed.TotalMilliseconds);
            }

            var ordered = samples.OrderBy(milliseconds => milliseconds).ToArray();
            return new ScaleLoadResult(
                label,
                books,
                host.Snapshot.Books.Count,
                coldWatch.Elapsed.TotalMilliseconds,
                Percentile(ordered, 0.50),
                Percentile(ordered, 0.95),
                ordered[^1],
                samples);
        }
        finally
        {
            presentation.Close();
        }
    }

    private ThemeHomePaths ThemeHome(AppOptions options, int discriminator)
    {
        var directory = Path.Combine(_root, $"theme-home-{discriminator}");
        Directory.CreateDirectory(directory);
        return new ThemeHomePaths(
            Path.Combine(directory, "theme-settings.json"),
            Path.Combine(directory, "themes"),
            Path.Combine(directory, "theme-studio-favorites.json"),
            IsCustom: true);
    }

    /// <summary>
    /// Writes the metrics JSON. When the evidence environment variable is set the file lands in the task
    /// evidence directory (the run that produces the committed evidence); otherwise it stays in the temp
    /// directory so a plain test run never writes into the repository.
    /// </summary>
    private string WriteEvidence(string variable, string fallbackName, string json)
    {
        var configured = Environment.GetEnvironmentVariable(variable);
        var path = string.IsNullOrWhiteSpace(configured)
            ? Path.Combine(Path.GetTempPath(), fallbackName)
            : Path.GetFullPath(configured);
        var directory = Path.GetDirectoryName(path);
        if (!string.IsNullOrEmpty(directory))
        {
            Directory.CreateDirectory(directory);
        }

        File.WriteAllText(path, json + Environment.NewLine);
        return path;
    }

    private static double Round(double value) => Math.Round(value, 2);

    private static double Percentile(IReadOnlyList<double> ordered, double percentile)
    {
        Assert.NotEmpty(ordered);
        var rank = (int)Math.Ceiling(percentile * ordered.Count) - 1;
        return ordered[Math.Clamp(rank, 0, ordered.Count - 1)];
    }

    private sealed record HotSwitchRun(
        int Run,
        double ColdFirstSwitchMs,
        double P50Ms,
        double P95Ms,
        double MaxMs,
        double UiThreadSchedulingGapMs,
        int UiThreadHeartbeatTicks,
        IReadOnlyList<double> Samples,
        long ManagedMemoryDeltaBytes,
        int HandleDelta);

    private sealed record HotSwitchMeasurement(
        IReadOnlyList<HotSwitchRun> Runs,
        double MedianP50,
        double MedianP95,
        double WorstRunP95,
        double WorstUiGap,
        double[] P95Values);

    private sealed record ScaleLoadResult(
        string Label,
        int Books,
        int BooksInSnapshot,
        double ColdFirstSwitchMs,
        double P50Ms,
        double P95Ms,
        double MaxMs,
        IReadOnlyList<double> Samples);

    /// <summary>
    /// AC-R4a-3: UI-thread heartbeat. A dispatcher timer ticks on the UI thread; the largest wall-clock gap
    /// between two consecutive ticks is the time the UI thread could not schedule its own heartbeat
    /// (<c>uiThreadSchedulingGapMs</c>). When the thread never gets a turn the gap is the elapsed segment, so
    /// a frozen UI thread cannot look healthy.
    /// </summary>
    private sealed class UiThreadHeartbeat : IDisposable
    {
        private readonly DispatcherTimer _timer;
        private readonly Stopwatch _watch = new();
        private long _lastTicks;
        private double _maxGapMs;
        private int _ticks;
        private bool _started;

        public UiThreadHeartbeat()
        {
            _timer = new DispatcherTimer(DispatcherPriority.Normal) { Interval = TimeSpan.FromMilliseconds(5) };
            _timer.Tick += OnTick;
        }

        public int Ticks => _ticks;

        public double MaxGapMs => _maxGapMs;

        public void Start()
        {
            _maxGapMs = 0;
            _ticks = 0;
            _watch.Restart();
            _lastTicks = 0;
            _started = true;
            _timer.Start();
        }

        public void Stop()
        {
            if (!_started)
            {
                return;
            }

            _timer.Stop();
            _watch.Stop();
            _started = false;
            RecordGap();
        }

        public void Dispose()
        {
            _timer.Stop();
            _timer.Tick -= OnTick;
        }

        private void OnTick(object? sender, EventArgs args)
        {
            _ticks++;
            RecordGap();
        }

        private void RecordGap()
        {
            var elapsedTicks = _watch.ElapsedTicks;
            var deltaTicks = elapsedTicks - _lastTicks;
            _lastTicks = elapsedTicks;
            var gapMs = deltaTicks * 1000.0 / Stopwatch.Frequency;
            _maxGapMs = Math.Max(_maxGapMs, gapMs);
        }
    }
}

/// <summary>
/// FEA-07-RESIDUAL-2 AC-R4a-3 (r2 R2-001): the dedicated serial performance gate's Avalonia fact. The default
/// suite records <c>uiThreadSchedulingGapMs</c> only, because the metric is load-sensitive (parallel full-suite
/// run: 513.55 ms; serial: 249.44 ms). This attribute keeps the assertion out of the default gate and reports a
/// skip reason instead; <c>verification/FEA-07-RESIDUAL-2/tools/verify-fea07-perf.ps1</c> sets
/// <c>NEWMANGA_FEA07_PERF=1</c> and runs it serially.
/// <para>Not <c>[AvaloniaFact(Skip=...)]</c>: the Avalonia fact attribute is sealed and the discovery-time skip
/// is set through the same discoverer binding the repo already uses for dynamic self-skips (a dynamic
/// <c>SkipException</c> is recorded as a failure in this Avalonia+ xunit chain).</para>
/// </summary>
[AttributeUsage(AttributeTargets.Method, AllowMultiple = false)]
[XunitTestCaseDiscoverer("Avalonia.Headless.XUnit.AvaloniaUIFactDiscoverer", "Avalonia.Headless.XUnit")]
public sealed class PerfGateAvaloniaFactAttribute : FactAttribute
{
    /// <summary>Environment variable that opts into the dedicated (serial) performance gate.</summary>
    public const string GateVariable = "NEWMANGA_FEA07_PERF";

    public PerfGateAvaloniaFactAttribute()
    {
        if (!IsEnabled())
        {
            Skip = "gated perf test: set " + GateVariable + "=1 and run serially "
                + "(verification/FEA-07-RESIDUAL-2/tools/verify-fea07-perf.ps1); the default suite records "
                + "uiThreadSchedulingGapMs only because the metric is load-sensitive.";
        }
    }

    /// <summary>True only when the caller explicitly opted into the serial performance gate.</summary>
    public static bool IsEnabled() =>
        string.Equals(Environment.GetEnvironmentVariable(GateVariable), "1", StringComparison.Ordinal);
}
