using System.IO;
using System.Text.Json;
using NewManga.Presentation.Avalonia.Windows;

namespace NewManga.Presentation.Avalonia.Tests;

/// <summary>FEA-07 AC5: per-window placement persistence (atomic, corrupt-tolerant).</summary>
public sealed class WindowStateMementoTests : IDisposable
{
    private readonly string _root = Path.Combine(Path.GetTempPath(), $"nm-fea07-memento-{Guid.NewGuid():N}");

    public WindowStateMementoTests() => Directory.CreateDirectory(_root);

    public void Dispose()
    {
        try
        {
            Directory.Delete(_root, recursive: true);
        }
        catch (IOException)
        {
            // best-effort test cleanup
        }
    }

    private string StatePath => Path.Combine(_root, "window-state.json");

    [Fact]
    public void SaveAndLoad_RoundTripsEveryField()
    {
        var store = new WindowStateMementoStore(StatePath);
        var memento = new WindowStateMemento(120, 80, 1440, 900, "DISPLAY2", 1.5, IsMaximized: false);

        store.Save(memento);
        var loaded = store.TryLoad(out var error);

        Assert.Null(error);
        Assert.Equal(memento, loaded);
        Assert.False(File.Exists(StatePath + ".tmp"));
    }

    [Fact]
    public void MissingFile_ReturnsNullWithoutError()
    {
        var store = new WindowStateMementoStore(Path.Combine(_root, "missing.json"));
        Assert.Null(store.TryLoad(out var error));
        Assert.Null(error);
    }

    [Fact]
    public void CorruptFile_IsToleratedAndReported()
    {
        File.WriteAllText(StatePath, "{ not json");
        var store = new WindowStateMementoStore(StatePath);

        Assert.Null(store.TryLoad(out var error));
        Assert.NotNull(error);
    }
}

/// <summary>
/// FEA-07 AC5/A08: display-topology planning — clamp off-screen mementos, keep mixed-DPI scales and
/// return a removed display's second-window content to the main window (fail-closed unsaved edits).
/// </summary>
public sealed class DisplayTopologyPlannerTests
{
    private static readonly DisplayInfo[] TwoDisplays =
    [
        new("PRIMARY", 0, 0, 1920, 1080, 1.0, IsPrimary: true),
        new("SECONDARY", 1920, 0, 2560, 1440, 1.5, IsPrimary: false),
    ];

    [Fact]
    public void OnScreenMemento_IsKeptInsideItsDisplay()
    {
        var memento = new WindowStateMemento(2000, 100, 1200, 800, "SECONDARY", 1.5, false);

        var clamped = DisplayTopologyPlanner.Clamp(memento, TwoDisplays);

        Assert.Equal(memento, clamped);
    }

    [Fact]
    public void OffScreenMemento_IsBroughtBackInsideTheDisplay()
    {
        var memento = new WindowStateMemento(9000, 9000, 1200, 800, "PRIMARY", 1.0, false);

        var clamped = DisplayTopologyPlanner.Clamp(memento, TwoDisplays);

        Assert.InRange(clamped.X, 0, 1920 - clamped.Width);
        Assert.InRange(clamped.Y, 0, 1080 - clamped.Height);
        Assert.Equal(1200, clamped.Width);
        Assert.Equal(800, clamped.Height);
    }

    [Fact]
    public void OversizedMemento_IsClampedToMinimumAndDisplayBounds()
    {
        var memento = new WindowStateMemento(-500, -500, 100, 100, "PRIMARY", 1.0, false);

        var clamped = DisplayTopologyPlanner.Clamp(memento, TwoDisplays);

        Assert.Equal(DisplayTopologyPlanner.DefaultMinWidth, clamped.Width);
        Assert.Equal(DisplayTopologyPlanner.DefaultMinHeight, clamped.Height);
        Assert.True(clamped.X >= 0);
        Assert.True(clamped.Y >= 0);
    }

    [Fact]
    public void MissingDisplay_ResolvesToPrimaryAndRecordsIt()
    {
        var memento = new WindowStateMemento(5000, 100, 1200, 800, "GONE", 1.5, false);

        var clamped = DisplayTopologyPlanner.Clamp(memento, TwoDisplays);

        Assert.Equal("PRIMARY", clamped.DisplayId);
        Assert.Equal(1.5, clamped.Scale); // mixed-DPI: the window keeps its own scale
    }

    [Fact]
    public void SecondaryOnExistingDisplay_IsKept()
    {
        var plan = DisplayTopologyPlanner.Plan(
            TwoDisplays,
            new WindowStateMemento(100, 100, 1400, 900, "PRIMARY", 1.0, false),
            [("inspector", new WindowStateMemento(2000, 100, 900, 700, "SECONDARY", 1.5, false), false)]);

        var secondary = Assert.Single(plan.Secondary);
        Assert.Equal(SecondWindowDisposition.KeepOnDisplay, secondary.Disposition);
        Assert.False(plan.RetainUnsavedEditsInMainBuffer);
    }

    [Fact]
    public void UnpluggedDisplay_ReturnsContentToMainWindow()
    {
        var plan = DisplayTopologyPlanner.Plan(
            [TwoDisplays[0]],
            new WindowStateMemento(100, 100, 1400, 900, "PRIMARY", 1.0, false),
            [("inspector", new WindowStateMemento(2000, 100, 900, 700, "SECONDARY", 1.5, false), true)]);

        var secondary = Assert.Single(plan.Secondary);
        Assert.Equal(SecondWindowDisposition.ReturnContentToMainWindow, secondary.Disposition);
        Assert.True(plan.RetainUnsavedEditsInMainBuffer);
        Assert.Equal("PRIMARY", secondary.Memento.DisplayId);
    }

    [Fact]
    public void MainOffScreen_IsClampedButKeepsScale()
    {
        var plan = DisplayTopologyPlanner.Plan(
            [TwoDisplays[0]],
            new WindowStateMemento(5000, 5000, 1600, 1000, "SECONDARY", 1.5, true),
            Array.Empty<(string, WindowStateMemento, bool)>());

        Assert.Equal("PRIMARY", plan.MainMemento.DisplayId);
        Assert.Equal(1.5, plan.MainMemento.Scale);
        Assert.True(plan.MainMemento.X >= 0 && plan.MainMemento.Y >= 0);
    }
}
