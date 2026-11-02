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
using NewManga.App.Services;
using NewManga.App.Views.Presentation;
using NewManga.Appearance;
using NewManga.DesignSystem.Theming;
using Xunit;
using Xunit.Abstractions;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-07 AC6 / H3 / W-5: runtime frontend switch performance baseline. The gate is the frozen
/// W-5 threshold (hot switch p95 ≤ 1000 ms); cold first switch is recorded separately. Metrics are
/// written to the temp directory for the evidence log and also asserted here.
/// </summary>
public sealed class PerformanceBaselineTests : IDisposable
{
    private const int WarmupSwitches = 2;
    private const int MeasuredSwitches = 12;
    private const double P95BudgetMilliseconds = 1000.0;

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

    [AvaloniaFact]
    public async Task HotSwitch_P95_StaysWithinTheFrozenW5Budget()
    {
        var application = Application.Current!;
        using var themeManager = new DesignSystemThemeManager(application);
        themeManager.Initialize();
        var appearance = new AppearanceCoordinator(new AppearanceStore(Path.Combine(_root, "presentation-settings.json")));
        appearance.Reload();
        var options = AppOptions.Parse(new[] { "--presentation-host=true" });
        var selection = FrontendSelector.Select(FrontendSelector.CurrentV2FrontendId, persistedFrontendId: null);
        var themeHome = new ThemeHomePaths(
            Path.Combine(_root, "theme-settings.json"),
            Path.Combine(_root, "themes"),
            Path.Combine(_root, "theme-studio-favorites.json"),
            IsCustom: true);

        var window = App.CreatePresentationShell(
            options, NullHostController.Instance, selection, appearance, themeHome, themeManager, application);
        var presentation = Assert.IsType<PresentationWindow>(window);
        var firstSwitch = Stopwatch.StartNew();
        var cold = await presentation.SwitchFrontendAsync(FrontendSelector.FluentFrontendId);
        firstSwitch.Stop();
        Assert.True(cold.Succeeded, cold.Failure);

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
            var samples = new List<double>(MeasuredSwitches);
            for (var i = 0; i < MeasuredSwitches; i++)
            {
                var target = i % 2 == 0 ? FrontendSelector.CurrentV2FrontendId : FrontendSelector.FluentFrontendId;
                var watch = Stopwatch.StartNew();
                var result = await presentation.SwitchFrontendAsync(target);
                watch.Stop();
                Assert.True(result.Succeeded, result.Failure);
                samples.Add(watch.Elapsed.TotalMilliseconds);
            }

            var memoryAfter = GC.GetTotalMemory(forceFullCollection: true);
            process.Refresh();
            var handlesAfter = process.HandleCount;

            var ordered = samples.OrderBy(milliseconds => milliseconds).ToArray();
            var p50 = Percentile(ordered, 0.50);
            var p95 = Percentile(ordered, 0.95);
            var metrics = new
            {
                metric = "FEA-07 hot frontend switch",
                machine = Environment.MachineName,
                os = Environment.OSVersion.ToString(),
                dotnet = Environment.Version.ToString(),
                config = "headless Avalonia UI thread; real AppShellV2/FluentShellSurface factories",
                warmupSwitches = WarmupSwitches,
                measuredSwitches = MeasuredSwitches,
                coldFirstSwitchMs = Math.Round(firstSwitch.Elapsed.TotalMilliseconds, 2),
                p50Ms = Math.Round(p50, 2),
                p95Ms = Math.Round(p95, 2),
                maxMs = Math.Round(ordered[^1], 2),
                samplesMs = samples.Select(milliseconds => Math.Round(milliseconds, 2)).ToArray(),
                managedMemoryDeltaBytes = memoryAfter - memoryBefore,
                handleDelta = handlesAfter - handlesBefore,
                budgetP95Ms = P95BudgetMilliseconds,
                passed = p95 <= P95BudgetMilliseconds,
            };

            var json = JsonSerializer.Serialize(metrics, new JsonSerializerOptions { WriteIndented = true });
            var metricsPath = Path.Combine(Path.GetTempPath(), "nm-fea07-performance-baseline.json");
            File.WriteAllText(metricsPath, json + Environment.NewLine);
            _output.WriteLine(json);
            _output.WriteLine("metrics-path: " + metricsPath);

            Assert.True(
                p95 <= P95BudgetMilliseconds,
                $"hot switch p95 {p95:0.0} ms exceeds the frozen W-5 budget {P95BudgetMilliseconds:0} ms (metrics: {metricsPath})");
        }
        finally
        {
            presentation.Close();
        }
    }

    private static double Percentile(IReadOnlyList<double> ordered, double percentile)
    {
        Assert.NotEmpty(ordered);
        var rank = (int)Math.Ceiling(percentile * ordered.Count) - 1;
        return ordered[Math.Clamp(rank, 0, ordered.Count - 1)];
    }
}
