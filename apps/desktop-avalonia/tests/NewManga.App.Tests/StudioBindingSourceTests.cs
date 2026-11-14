using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using NewManga.App.Services;
using NewManga.App.ViewModels.V2.Studio;
using NewManga.App.Views.V2.Studio.Controls;
using NewManga.CoreClient;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// E8-STUDIO-BINDING-2: pins the <see cref="StudioHudRingControl"/> binding-source fix from
/// E8-STUDIO-BINDING-1.
///
/// The defect: this control never set a DataContext, so <c>Bind(IsEnabledProperty, new Binding(...))</c>
/// — written without an explicit <c>Source</c> — could never resolve. Production <c>startup.log</c> showed
/// exactly 8 <c>IsEnabled</c> failures, one per HUD slot this control materialises.
///
/// The fix added <c>{ Source = captured }</c>. This test asserts the ACTUAL button state tracks the slot:
/// remove that <c>Source</c> again and <see cref="Buttons_TrackTheirSlotEnabledState"/> goes red, because
/// an unresolved binding leaves <see cref="Button.IsEnabled"/> at its control default instead of following
/// the view model.
/// </summary>
public sealed class StudioBindingSourceTests
{
    [AvaloniaFact]
    public void Buttons_TrackTheirSlotEnabledState()
    {
        var page = CreateStudioPage();
        var control = new StudioHudRingControl(page);

        // One button per HUD slot; production logged exactly 8 IsEnabled failures, matching this count.
        Assert.Equal(8, control.Buttons.Count);

        foreach (var slot in page.HudSlots)
        {
            var button = control.ButtonFor(slot.Action);
            Assert.NotNull(button);

            // Disabled direction is what has teeth: a broken binding falls back to the Button default
            // (enabled), so asserting false here fails if the Source is removed again.
            slot.IsEnabled = false;
            Assert.False(button!.IsEnabled,
                $"slot {slot.Action}: IsEnabled=false but the button is still enabled (binding did not resolve)");

            slot.IsEnabled = true;
            Assert.True(button.IsEnabled,
                $"slot {slot.Action}: IsEnabled=true but the button is still disabled");
        }
    }

    private static StudioPageViewModel CreateStudioPage()
    {
        var snapshot = new HostViewSnapshot(
            HostViewState.Ready,
            "Host ready",
            "read-write (isolated data root)",
            null,
            null,
            Array.Empty<BookSummary>(),
            0,
            true,
            null);
        var host = new FakeHostController(snapshot);
        return new StudioPageViewModel(host);
    }
}
