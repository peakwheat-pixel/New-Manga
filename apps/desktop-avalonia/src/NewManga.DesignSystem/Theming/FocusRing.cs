using System.Runtime.CompilerServices;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.Primitives;
using Avalonia.Input;
using Avalonia.Layout;
using Avalonia.VisualTree;

namespace NewManga.DesignSystem.Theming;

/// <summary>
/// Shared outside focus outline for every focusable design-system control (DESIGN_SYSTEM §8): on
/// keyboard focus a 2px accent <see cref="Border"/> is hosted in the window's overlay layer just
/// outside the control bounds; on blur it is removed. The control's own template geometry is never
/// touched and no shadow is used.
///
/// <para>
/// Avalonia's plain <c>Control.FocusAdorner</c> property is not rendered by the window/headless adorner
/// layer, so the ring is hosted explicitly and positioned from the adorned control's bounds. Every
/// layout update recomputes the position, so scrolling or resizing keeps the ring attached.
/// </para>
/// </summary>
public sealed class FocusRing : AvaloniaObject
{
    /// <summary>Fallback stroke only used if the token dictionary is not loaded yet.</summary>
    private const double FallbackStroke = 2d;

    /// <summary>Attached property that opts a control into the shared focus outline.</summary>
    public static readonly AttachedProperty<bool> IsEnabledProperty =
        AvaloniaProperty.RegisterAttached<FocusRing, Control, bool>("IsEnabled");

    private static readonly ConditionalWeakTable<Control, RingState> States = new();

    static FocusRing()
    {
        IsEnabledProperty.Changed.AddClassHandler<Control>(OnIsEnabledChanged);
    }

    public static bool GetIsEnabled(Control control) => control.GetValue(IsEnabledProperty);

    public static void SetIsEnabled(Control control, bool value) => control.SetValue(IsEnabledProperty, value);

    private static void OnIsEnabledChanged(Control control, AvaloniaPropertyChangedEventArgs args)
    {
        var state = States.GetValue(control, static _ => new RingState());
        if (args.GetNewValue<bool>())
        {
            if (state.Subscribed)
            {
                return;
            }

            control.GotFocus += OnGotFocus;
            control.LostFocus += OnLostFocus;
            control.DetachedFromVisualTree += OnDetached;
            state.Subscribed = true;
            if (control.IsFocused)
            {
                Show(control, state);
            }
        }
        else
        {
            Unsubscribe(control, state);
            Hide(control, state);
        }
    }

    private static void OnGotFocus(object? sender, GotFocusEventArgs args)
    {
        if (sender is Control control && States.TryGetValue(control, out var state))
        {
            Show(control, state);
        }
    }

    private static void OnLostFocus(object? sender, Avalonia.Interactivity.RoutedEventArgs args)
    {
        if (sender is Control control && States.TryGetValue(control, out var state))
        {
            Hide(control, state);
        }
    }

    private static void OnDetached(object? sender, VisualTreeAttachmentEventArgs args)
    {
        if (sender is Control control && States.TryGetValue(control, out var state))
        {
            Hide(control, state);
        }
    }

    private static void OnLayoutUpdated(object? sender, EventArgs args)
    {
        if (sender is Control control && States.TryGetValue(control, out var state))
        {
            Position(control, state);
        }
    }

    private static void Show(Control control, RingState state)
    {
        if (state.Ring is not null)
        {
            return;
        }

        var host = FindOverlayHost(control);
        if (host is null)
        {
            return;
        }

        state.Host = host;
        state.Ring = new Border
        {
            Classes = { "nm-focus-ring" },
            IsVisible = true,
            IsHitTestVisible = false,
            HorizontalAlignment = HorizontalAlignment.Left,
            VerticalAlignment = VerticalAlignment.Top,
        };

        host.Children.Add(state.Ring);
        control.LayoutUpdated += OnLayoutUpdated;
        state.LayoutSubscribed = true;
        Position(control, state);
    }

    private static void Position(Control control, RingState state)
    {
        if (state.Ring is null || state.Host is null)
        {
            return;
        }

        var topLeft = control.TranslatePoint(new Point(0, 0), state.Host);
        if (topLeft is null)
        {
            return;
        }

        var stroke = ResolveStroke(control);
        var bounds = control.Bounds;
        state.Ring.Width = bounds.Width + (stroke.Left * 2);
        state.Ring.Height = bounds.Height + (stroke.Top * 2);
        state.Ring.BorderThickness = stroke;
        if (state.Host is Canvas canvas)
        {
            Canvas.SetLeft(state.Ring, topLeft.Value.X - stroke.Left);
            Canvas.SetTop(state.Ring, topLeft.Value.Y - stroke.Top);
        }
        else
        {
            state.Ring.Margin = new Thickness(topLeft.Value.X - stroke.Left, topLeft.Value.Y - stroke.Top, 0, 0);
        }
    }

    /// <summary>Reads the 2px outline stroke from the frozen token dictionary (no naked pin in code).</summary>
    private static Thickness ResolveStroke(Control control)
    {
        return control.TryFindResource(NmKeys.Border.Focus, out var value) && value is Thickness thickness
            ? thickness
            : new Thickness(FallbackStroke);
    }

    private static void Hide(Control control, RingState state)
    {
        if (state.LayoutSubscribed)
        {
            control.LayoutUpdated -= OnLayoutUpdated;
            state.LayoutSubscribed = false;
        }

        if (state.Ring is not null)
        {
            state.Host?.Children.Remove(state.Ring);
            state.Ring = null;
            state.Host = null;
        }
    }

    private static void Unsubscribe(Control control, RingState state)
    {
        if (!state.Subscribed)
        {
            return;
        }

        control.GotFocus -= OnGotFocus;
        control.LostFocus -= OnLostFocus;
        control.DetachedFromVisualTree -= OnDetached;
        state.Subscribed = false;
    }

    /// <summary>Finds the top-level overlay layer that paints above the normal visual tree.</summary>
    private static Panel? FindOverlayHost(Control control)
    {
        var window = TopLevel.GetTopLevel(control);
        if (window is null)
        {
            return null;
        }

        var overlay = window.GetVisualDescendants().OfType<OverlayLayer>().FirstOrDefault();
        if (overlay is not null)
        {
            return overlay;
        }

        return window.GetVisualDescendants().OfType<AdornerLayer>().FirstOrDefault() as Panel;
    }

    private sealed class RingState
    {
        public bool Subscribed { get; set; }

        public bool LayoutSubscribed { get; set; }

        public Panel? Host { get; set; }

        public Border? Ring { get; set; }
    }
}

