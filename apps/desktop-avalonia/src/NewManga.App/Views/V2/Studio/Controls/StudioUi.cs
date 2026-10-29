using Avalonia;
using Avalonia.Controls;
using Avalonia.Data;
using Avalonia.Layout;
using Avalonia.Media;
using NewManga.App.ViewModels.V2.Studio;

namespace NewManga.App.Views.V2.Studio.Controls;

/// <summary>
/// V11R-B-3: small composition helpers for the Studio views. Views are composed in C# (the same way
/// MainWindow/Pages are built in this app) so a headless test can assert on the real control tree;
/// every visual value still comes from a <c>Nm.*</c> token through the Studio stylesheet classes.
/// </summary>
public static class StudioUi
{
    public static TextBlock Text(string text, params string[] classes)
    {
        var block = new TextBlock { Text = text };
        foreach (var name in classes)
        {
            block.Classes.Add(name);
        }

        return block;
    }

    /// <summary>Text bound to a view-model path (DataContext is inherited from the composed root).</summary>
    public static TextBlock BoundText(string path, params string[] classes)
    {
        var block = Text(string.Empty, classes);
        block.Bind(TextBlock.TextProperty, new Binding(path));
        return block;
    }

    public static Border Box(params string[] classes)
    {
        var border = new Border();
        foreach (var name in classes)
        {
            border.Classes.Add(name);
        }

        return border;
    }

    public static Border Box(Control child, params string[] classes)
    {
        var border = Box(classes);
        border.Child = child;
        return border;
    }

    public static StackPanel Row(double spacing = 8)
    {
        return new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = spacing,
            VerticalAlignment = VerticalAlignment.Center,
        };
    }

    public static StackPanel Column(double spacing = 8)
    {
        return new StackPanel
        {
            Orientation = Orientation.Vertical,
            Spacing = spacing,
        };
    }

    public static Button Button(string content, string classes, Action? onClick = null, string? tooltip = null)
    {
        var button = new Button
        {
            Content = content,
            VerticalAlignment = VerticalAlignment.Center,
        };
        foreach (var name in classes.Split(' ', StringSplitOptions.RemoveEmptyEntries))
        {
            button.Classes.Add(name);
        }

        if (onClick is not null)
        {
            button.Click += (_, _) => onClick();
        }

        if (!string.IsNullOrEmpty(tooltip))
        {
            ToolTip.SetTip(button, tooltip);
            ToolTip.SetShowDelay(button, 300);
        }

        return button;
    }

    /// <summary>Bound button label (e.g. "保存译文 · 能力待接入").</summary>
    public static Button BoundLabelButton(string path, string classes, Action? onClick = null)
    {
        var button = Button(string.Empty, classes, onClick);
        button.Bind(ContentControl.ContentProperty, new Binding(path));
        return button;
    }

    /// <summary>State glyph with the shared colour class; the symbol itself comes from the contract.</summary>
    public static TextBlock Glyph(StudioStateKind? state, params string[] extraClasses)
    {
        var block = Text(state is { } value ? StudioStates.Glyph(value) : "–");
        block.Classes.Add(state is { } token ? StudioStates.StyleClass(token) : "studio-state-nodata");
        block.Classes.Add("data");
        foreach (var name in extraClasses)
        {
            block.Classes.Add(name);
        }

        return block;
    }

    public static Border Dot(StudioStateKind? state, params string[] extraClasses)
    {
        var border = Box("studio-dot");
        border.Classes.Add(state is { } token ? FillClass(token) : "studio-fill-nodata");
        foreach (var name in extraClasses)
        {
            border.Classes.Add(name);
        }

        return border;
    }

    /// <summary>Maps a state to the muted fill class used by dots/matrix cells.</summary>
    public static string FillClass(StudioStateKind state) => state switch
    {
        StudioStateKind.Queued => "studio-fill-queued",
        StudioStateKind.Running => "studio-fill-running",
        StudioStateKind.Done => "studio-fill-done",
        StudioStateKind.Failed => "studio-fill-failed",
        StudioStateKind.Blocked => "studio-fill-blocked",
        StudioStateKind.Stale => "studio-fill-stale",
        StudioStateKind.Skipped => "studio-fill-skipped",
        StudioStateKind.NotStarted => "studio-fill-notstarted",
        _ => "studio-fill-nodata",
    };

    /// <summary>Binds a boolean path to visibility.</summary>
    public static T VisibleWhen<T>(this T control, string path, bool invert = false)
        where T : Control
    {
        control.Bind(Visual.IsVisibleProperty, new Binding(invert ? "!" + path : path));
        return control;
    }

    /// <summary>Binds a string path to a TextBlock.</summary>
    public static T BindText<T>(this T control, string path)
        where T : TextBlock
    {
        control.Bind(TextBlock.TextProperty, new Binding(path));
        return control;
    }

    /// <summary>Keeps one style class in sync with a predicate (class toggling is not bindable in code).</summary>
    public static void TrackClass(
        Control control,
        string className,
        StudioObservable? source,
        Func<bool> predicate)
    {
        void Apply() => control.Classes.Set(className, predicate());
        Apply();
        if (source is null)
        {
            return;
        }

        source.PropertyChanged += (_, _) => Apply();
    }

    public static void TrackVisible(Control control, StudioObservable? source, Func<bool> predicate, bool invert = false)
    {
        void Apply() => control.IsVisible = invert ? !predicate() : predicate();
        Apply();
        if (source is null)
        {
            return;
        }

        source.PropertyChanged += (_, _) => Apply();
    }

    /// <summary>Reads a token value (double) from the merged resource dictionary; fallback for headless.</summary>
    public static double TokenDouble(string key, double fallback)
    {
        var app = Application.Current;
        return app is not null && app.TryGetResource(key, null, out var value) && value is double number
            ? number
            : fallback;
    }

    public static void SetTooltip(Control control, string? text)
    {
        if (string.IsNullOrEmpty(text))
        {
            ToolTip.SetTip(control, null);
            return;
        }

        ToolTip.SetTip(control, text);
        ToolTip.SetShowDelay(control, 300);
    }

    /// <summary>Creates a vertical grid row helper for the composite controls.</summary>
    public static Grid Rows(params (double Height, bool Star)[] rows)
    {
        var grid = new Grid();
        foreach (var (height, star) in rows)
        {
            grid.RowDefinitions.Add(star
                ? new RowDefinition(GridLength.Star)
                : new RowDefinition(GridLength.Auto));
        }

        return grid;
    }

    public static Separator Hairline()
    {
        var border = Box("studio-divider");
        border.Height = 1;
        return new Separator { Height = 1, Opacity = 0.0, IsHitTestVisible = false, Background = border.Background };
    }
}
