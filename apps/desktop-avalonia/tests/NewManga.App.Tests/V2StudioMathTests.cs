using NewManga.App.ViewModels.V2.Studio;
using NewManga.CoreClient;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-B-3 pure-logic tests: percentage↔pixel region geometry, zoom/pan math, the frozen seven-state
/// vocabulary, the HUD ring cycle, the capability gate and the shared selection model. No Avalonia
/// session needed — these are the numbers the headless UI tests then assert against.
/// </summary>
public sealed class V2StudioMathTests
{
    private static readonly RegionPageSize Page = new(1200, 1660);

    [Fact]
    public void Coordinates_NormalizedToPixels_MatchesRealPagePixels()
    {
        var geometry = new RegionGeometrySummary(0.10, 0.10, 0.40, 0.20, Array.Empty<RegionGeometryPoint>());
        var rect = StudioCoordinates.NormalizedToPixels(geometry, Page);

        Assert.Equal(120, rect.X, 3);
        Assert.Equal(166, rect.Y, 3);
        Assert.Equal(480, rect.Width, 3);
        Assert.Equal(332, rect.Height, 3);

        // 86% default zoom → rendered overlay rectangle (what RegionBox Left/Top/Width/Height use).
        var rendered = StudioCoordinates.ToRendered(rect, StudioCoordinates.DefaultZoom);
        Assert.Equal(120 * 0.86, rendered.X, 3);
        Assert.Equal(166 * 0.86, rendered.Y, 3);
        Assert.Equal(480 * 0.86, rendered.Width, 3);
        Assert.Equal(332 * 0.86, rendered.Height, 3);
    }

    [Fact]
    public void Coordinates_PixelNormalizedRoundTrip_IsStable()
    {
        var original = new StudioRect(120, 166, 480, 332);
        var normalized = StudioCoordinates.PixelsToNormalized(original, Page);
        var back = StudioCoordinates.NormalizedToPixels(
            new RegionGeometrySummary(normalized.X, normalized.Y, normalized.Width, normalized.Height,
                Array.Empty<RegionGeometryPoint>()), Page);

        Assert.Equal(original.X, back.X, 3);
        Assert.Equal(original.Y, back.Y, 3);
        Assert.Equal(original.Width, back.Width, 3);
        Assert.Equal(original.Height, back.Height, 3);
        Assert.Equal(0.1, normalized.X, 6);
        Assert.Equal(0.4, normalized.Width, 6);
    }

    [Fact]
    public void Coordinates_ClampOutOfRangeGeometry_AndUnknownPageExtent()
    {
        var overflow = new RegionGeometrySummary(0.9, 0.9, 0.5, 0.5, Array.Empty<RegionGeometryPoint>());
        var rect = StudioCoordinates.NormalizedToPixels(overflow, Page);
        Assert.Equal(1080, rect.X, 3);
        Assert.Equal(120, rect.Width, 3); // clamped to page edge, never paints outside the page
        Assert.Equal(166, rect.Height, 3);

        Assert.True(StudioCoordinates.NormalizedToPixels(overflow, null).IsEmpty);
        Assert.True(StudioCoordinates.NormalizedToPixels(null, Page).IsEmpty);
        Assert.Equal((0d, 0d), StudioCoordinates.ContentSize(null, 1.0));
    }

    [Fact]
    public void Coordinates_WheelZoom_KeepsPointerContentPointFixed()
    {
        const double oldZoom = 0.86;
        const double newZoom = 0.86 * StudioCoordinates.WheelZoomFactor;
        var (offsetX, offsetY) = StudioCoordinates.ZoomAroundPoint(120, 80, 300, 200, oldZoom, newZoom);

        // The content point under the pointer before and after must be identical.
        var beforeX = (300 - 120) / oldZoom;
        var afterX = (300 - offsetX) / newZoom;
        var beforeY = (200 - 80) / oldZoom;
        var afterY = (200 - offsetY) / newZoom;
        Assert.Equal(beforeX, afterX, 6);
        Assert.Equal(beforeY, afterY, 6);

        // Zoom is clamped; keyboard steps are exactly one 10% step from the current zoom.
        Assert.Equal(StudioCoordinates.MaxZoom, StudioCoordinates.ApplyWheelZoom(10, 100), 6);
        Assert.Equal(0.76, StudioCoordinates.ZoomOut(0.86), 6);
        Assert.Equal(0.96, StudioCoordinates.ZoomIn(0.86), 6);
        Assert.Equal("86%", StudioCoordinates.ZoomLabel(StudioCoordinates.DefaultZoom));
    }

    [Fact]
    public void Coordinates_FitAndCenter_AndOffsetClamp()
    {
        var zoom = StudioCoordinates.FitZoom(1504, 844, 1200, 1660);
        Assert.True(zoom > 0 && zoom < 1);

        var (fitted, offsetX, offsetY) = StudioCoordinates.FitAndCenter(1504, 844, Page);
        Assert.Equal(fitted, zoom, 6);
        Assert.True(offsetX >= 0);
        Assert.True(offsetY >= 0);

        // Smaller-than-viewport content is centred on that axis, larger is clamped to the edges.
        var (centerX, _) = StudioCoordinates.ClampOffset(0, 0, 800, 2000, 1000, 900);
        Assert.Equal(100, centerX, 3);
        var (clampedX, clampedY) = StudioCoordinates.ClampOffset(500, 500, 2000, 2000, 1000, 900);
        Assert.Equal(0, clampedX, 3);
        Assert.Equal(0, clampedY, 3);
        var (lowX, lowY) = StudioCoordinates.ClampOffset(-5000, -5000, 2000, 2000, 1000, 900);
        Assert.Equal(-1000, lowX, 3);
        Assert.Equal(-1100, lowY, 3);
    }

    [Fact]
    public void States_GlyphsMatchTheFrozenContractVocabulary()
    {
        // Contract §2.3 / DESIGN_SYSTEM §2.2: symbol is part of the contract, not a UI choice.
        Assert.Equal("·", StudioStates.Glyph(StudioStateKind.Queued));
        Assert.Equal("◐", StudioStates.Glyph(StudioStateKind.Running));
        Assert.Equal("●", StudioStates.Glyph(StudioStateKind.Done));
        Assert.Equal("✗", StudioStates.Glyph(StudioStateKind.Failed));
        Assert.Equal("▲", StudioStates.Glyph(StudioStateKind.Blocked));
        Assert.Equal("▨", StudioStates.Glyph(StudioStateKind.Stale));
        Assert.Equal("–", StudioStates.Glyph(StudioStateKind.Skipped));
        Assert.Equal("○", StudioStates.Glyph(StudioStateKind.NotStarted));
        Assert.Equal("▮", StudioRegionLockGlyph.Value);

        foreach (var state in Enum.GetValues<StudioStateKind>())
        {
            Assert.False(string.IsNullOrWhiteSpace(StudioStates.Label(state)));
            Assert.StartsWith("studio-state-", StudioStates.StyleClass(state));
            Assert.StartsWith("Nm.Color.", StudioStates.ColorTokenKey(state));
            Assert.Contains(StudioStates.Glyph(state), StudioStates.LegendText(state));
        }

        Assert.Equal(8, StudioStates.LegendOrder.Count);
        Assert.Equal(StudioStateKind.Queued, StudioStates.FromReviewState("needs_review"));
        Assert.Equal(StudioStateKind.Done, StudioStates.FromReviewState("confirmed"));
        Assert.Equal(StudioStateKind.NotStarted, StudioStates.FromReviewState("unreviewed"));
        Assert.Null(StudioStates.FromReviewState("bogus"));
        Assert.Equal(StudioStateKind.Running, StudioStates.FromProjectionStatus("processing"));
        Assert.Equal(StudioStateKind.Done, StudioStates.FromProjectionStatus("completed"));
        Assert.Null(StudioStates.FromProjectionStatus("unknown_projection_state"));
    }

    [Fact]
    public void Stages_TenCanonicalColumns_MapCoreStepTypes()
    {
        Assert.Equal(10, StudioStages.Count);
        Assert.Equal("save", StudioStages.Canonical[^1].Key);
        Assert.Null(StudioStages.Canonical[^1].CoreStepType);

        Assert.Equal("translate", StudioStages.FindByCoreStep("translate")!.Key);
        Assert.Equal("term", StudioStages.FindByCoreStep("term_extract")!.Key);
        Assert.Equal("mask", StudioStages.FindByCoreStep("mask_refine")!.Key);
        Assert.Null(StudioStages.FindByCoreStep("save"));
        Assert.Null(StudioStages.FindByCoreStep(null));

        // The band maps a NOT_WIRED projection to "no data" for every stage — never a fake state.
        var band = StudioRunStageMapper.MapBandStages(null);
        Assert.Equal(10, band.Count);
        Assert.All(band, entry => Assert.Null(entry.State));
    }

    [Fact]
    public void HudRing_HasEightSlots_InRingOrder_AndCyclesEnabledOnly()
    {
        Assert.Equal(8, StudioHudRing.Count);
        Assert.Equal(new[] { "N", "NE", "E", "SE", "S", "SW", "W", "NW" }, StudioHudRing.Positions);

        bool Enabled(StudioHudSlot slot) => slot.Command is null || StudioCapabilityGate.IsWired(slot.Command.Value);

        // Clockwise from "no focus" lands on the first slot; full loop returns to it.
        var first = StudioHudRing.Cycle(-1, 1, Enabled);
        Assert.Equal(0, first);
        var enabledCount = StudioHudRing.Slots.Count(Enabled);
        Assert.True(enabledCount >= 5);
        var index = first;
        for (var step = 0; step < enabledCount; step++)
        {
            index = StudioHudRing.Cycle(index, 1, Enabled);
        }

        Assert.Equal(first, index);

        // Counter-clockwise from 0 lands on a real slot too.
        Assert.True(StudioHudRing.Cycle(0, -1, Enabled) >= 0);

        // Everything disabled → -1 (the cycle must not trap focus on an unrunnable action).
        Assert.Equal(-1, StudioHudRing.Cycle(-1, 1, _ => false));
    }

    [Fact]
    public void CapabilityGate_WiresOnlyTheThreeExistingCommands()
    {
        var wired = Enum.GetValues<StudioCommand>().Where(StudioCapabilityGate.IsWired).OrderBy(command => command).ToList();
        Assert.Equal(
            new[] { StudioCommand.RerenderPage, StudioCommand.RestoreRevision, StudioCommand.SetRegionType }
                .OrderBy(command => command),
            wired);

        var gate = new StudioCapabilityGate();
        Assert.True(gate.CanExecute(StudioCommand.SetRegionType));
        Assert.False(gate.CanExecute(StudioCommand.SaveEditedTranslation));
        Assert.Equal(StudioCapabilityGate.NotWiredTooltip, gate.Tooltip(StudioCommand.SaveEditedTranslation));
        Assert.True(gate.IsNotWired(StudioCommand.LockRegion));

        var readOnly = new StudioCapabilityGate(true, false);
        Assert.False(readOnly.CanExecute(StudioCommand.SetRegionType));
        Assert.Equal(StudioCapabilityGate.ReadOnlyTooltip, readOnly.Tooltip(StudioCommand.SetRegionType));

        var notReady = new StudioCapabilityGate(false, false);
        Assert.Equal(StudioCapabilityGate.HostNotReadyTooltip, notReady.Tooltip(StudioCommand.RerenderPage));
    }

    [Fact]
    public void Selection_KeepsOneSharedScope_WithoutADuplicateModel()
    {
        var selection = new StudioSelection();
        Assert.Equal("本章", selection.SelectionSummary);

        selection.CurrentPageId = "p1";
        Assert.Equal("当前页", selection.SelectionSummary);

        selection.CurrentRegionId = "r1";
        Assert.Equal("当前 Region", selection.SelectionSummary);

        selection.SetSelectedPages(new[] { "p2", "p3", "p2" });
        Assert.Equal(2, selection.SelectedPageIds.Count);
        Assert.Equal("选中 2 页", selection.SelectionSummary); // R-16

        selection.SetSelectedPages(Array.Empty<string>());
        Assert.Equal("当前 Region", selection.SelectionSummary);

        var changes = 0;
        selection.Changed += (_, _) => changes++;
        selection.TogglePage("p4");
        Assert.True(changes >= 1); // ShellState routes every change
        selection.TogglePage("p5");
        Assert.Equal(2, selection.SelectedPageIds.Count);
        Assert.True(changes >= 2);

        selection.Zoom = 12.0;
        Assert.Equal(StudioCoordinates.MaxZoom, selection.Zoom, 6);
    }
}

/// <summary>The locked glyph is part of the frozen vocabulary but is an overlay flag, not a state.</summary>
public static class StudioRegionLockGlyph
{
    public const string Value = "▮";
}