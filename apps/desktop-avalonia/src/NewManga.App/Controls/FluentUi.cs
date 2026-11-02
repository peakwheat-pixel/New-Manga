using Avalonia;
using Avalonia.Automation;
using Avalonia.Controls;
using Avalonia.Controls.Primitives;
using Avalonia.Controls.Shapes;
using Avalonia.Layout;
using Avalonia.Markup.Xaml.MarkupExtensions;
using Avalonia.Media;
using NewManga.App.ViewModels.Fluent;
using NewManga.DesignSystem.Controls;
using NewManga.DesignSystem.Icons;

namespace NewManga.App.Controls;

internal static class FluentUi
{
    public static TextBlock Text(string text, string? classes = null) => new()
    {
        Text = text,
        TextWrapping = Avalonia.Media.TextWrapping.Wrap,
        Classes = { classes ?? "fluent-status-text" },
    };

    public static StackPanel Stack(string? classes = null, Orientation orientation = Orientation.Vertical) => new()
    {
        Orientation = orientation,
        Classes = { classes ?? "fluent-page-layout" },
    };

    public static Button Button(string text, string style, Action? action = null, string? accessibleName = null)
    {
        var button = new Button
        {
            Content = text,
            Classes = { style },
            HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Left,
        };
        AutomationProperties.SetName(button, accessibleName ?? text);
        if (action is not null)
        {
            button.Click += (_, _) => action();
        }

        return button;
    }

    public static Button IconButton(NmIconKind icon, string label, Action action, string? style = null)
    {
        var button = new Button
        {
            Content = new StackPanel
            {
                Orientation = Orientation.Horizontal,
                Classes = { "fluent-page-toolbar" },
                Children =
                {
                    new NmIcon { Kind = icon, Classes = { "sm" } },
                    Text(label, "fluent-status-text"),
                },
            },
            Classes = { style ?? "fluent-icon" },
        };
        AutomationProperties.SetName(button, label);
        button.Click += (_, _) => action();
        return button;
    }

    public static TextBox Input(string name, string? watermark = null, string? initialText = null)
    {
        var input = new TextBox { Watermark = watermark, Text = initialText };
        AutomationProperties.SetName(input, name);
        return input;
    }

    public static SearchField Search(string name, string placeholder)
    {
        var field = new SearchField { Placeholder = placeholder };
        AutomationProperties.SetName(field, name);
        return field;
    }

    public static ComboBox Combo(string name, IReadOnlyList<string> items, string selected)
    {
        var combo = new ComboBox
        {
            ItemsSource = items,
            SelectedItem = selected,
            HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Stretch,
        };
        AutomationProperties.SetName(combo, name);
        return combo;
    }

    public static CheckBox Check(string name, bool isChecked)
    {
        var check = new CheckBox { Content = name, IsChecked = isChecked };
        AutomationProperties.SetName(check, name);
        return check;
    }

    public static Slider Slider(string name, double minimum, double maximum, double value)
    {
        var slider = new Slider { Minimum = minimum, Maximum = maximum, Value = value };
        AutomationProperties.SetName(slider, name);
        return slider;
    }

    public static SettingsField Field(string label, Control input, string? help = null)
    {
        var field = new SettingsField { ColumnDefinitions = new ColumnDefinitions("Auto,*") };
        var labelBlock = Text(label, "fluent-status-text");
        AutomationProperties.SetName(input, label);
        field.Children.Add(labelBlock);
        field.Children.Add(input);
        Grid.SetColumn(input, 1);
        if (!string.IsNullOrWhiteSpace(help))
        {
            AutomationProperties.SetHelpText(input, help);
            ToolTip.SetTip(input, help);
        }

        return field;
    }

    public static SurfaceCard Card(Control content)
    {
        var card = new SurfaceCard { Child = content };
        return card;
    }

    public static EmptyState Empty(string title, string hint, string? action, Action? invoke)
    {
        var empty = new EmptyState { Title = title, Hint = hint, ActionText = action };
        if (invoke is not null)
        {
            empty.ActionInvoked += (_, _) => invoke();
        }

        AutomationProperties.SetName(empty, title);
        return empty;
    }

    public static AlertBanner Banner(StatusKind status, string title, string message, string? action, Action? invoke)
    {
        var banner = new AlertBanner
        {
            Severity = status,
            Title = title,
            Message = message,
            ActionText = action,
            Classes = { "fluent-info-bar" },
        };
        AutomationProperties.SetName(banner, $"{title}：{message}");
        if (invoke is not null)
        {
            banner.ActionInvoked += (_, _) => invoke();
        }

        return banner;
    }

    public static Skeleton LoadingCard() => new() { Variant = SkeletonVariant.BookCard };

    /// <summary>
    /// FEA-06-RESIDUAL-2 IN-1.1 (02-motion §2.3): the shelf background gradient layer. Both gradient
    /// stops bind the existing Bg tokens through DynamicResource so theme and high-contrast swaps follow
    /// without any new colour asset; the loop only mutates <see cref="Avalonia.Media.Brush.Opacity"/>,
    /// never layout. The layer is inserted beneath the page content and never takes hit-tests.
    /// </summary>
    public static Border DecorativeShelfGradient(out LinearGradientBrush brush)
    {
        var start = new GradientStop();
        start[!GradientStop.ColorProperty] = new DynamicResourceExtension("Nm.Color.Bg.Canvas");
        var end = new GradientStop { Offset = 1 };
        end[!GradientStop.ColorProperty] = new DynamicResourceExtension("Nm.Color.Bg.Sunken");
        brush = new LinearGradientBrush
        {
            StartPoint = new RelativePoint(0, 0, RelativeUnit.Relative),
            EndPoint = new RelativePoint(1, 1, RelativeUnit.Relative),
            GradientStops = new GradientStops { start, end },
        };
        return new Border
        {
            Background = brush,
            IsHitTestVisible = false,
            Classes = { "fluent-decorative", "fluent-decorative-shelf" },
        };
    }

    /// <summary>
    /// The fixed per-particle parameters for the IN-1.2 page-turn decor. Deterministic (no RNG) so every
    /// run renders the same 400ms effect for tests and visual evidence.
    /// </summary>
    private sealed record PageTurnParticleSpec(double XRatio, double FromBottom, double Size,
        double DelayMs, double Rise, double DriftX, double MaxOpacity);

    private static readonly PageTurnParticleSpec[] PageTurnParticles =
    [
        new(0.08, 26, 5, 0, 30, -6, 0.85),
        new(0.20, 14, 4, 18, 24, 8, 0.70),
        new(0.33, 34, 6, 36, 36, -10, 0.90),
        new(0.46, 18, 4, 54, 26, 6, 0.65),
        new(0.58, 30, 5, 72, 32, -8, 0.85),
        new(0.71, 12, 4, 90, 22, 10, 0.70),
        new(0.84, 28, 6, 108, 34, -6, 0.90),
        new(0.94, 20, 4, 120, 28, 8, 0.70),
    ];

    /// <summary>
    /// FEA-06-RESIDUAL-2 IN-1.2 (02-motion §2.3): the page-turn particle layer. Created once per turn,
    /// placed beneath the page image, driven via <see cref="UpdatePageTurnParticles"/> and removed when
    /// the run completes. Particle fills bind the existing accent-muted token; positioning is absolute
    /// inside a Canvas so the effect never participates in host layout.
    /// </summary>
    public static Border PageTurnParticleLayer()
    {
        var canvas = new Canvas();
        foreach (var spec in PageTurnParticles)
        {
            var dot = new Ellipse { Width = spec.Size, Height = spec.Size, Opacity = 0, Tag = spec };
            dot[!Ellipse.FillProperty] = new DynamicResourceExtension("Nm.Color.Accent.Muted");
            dot.RenderTransform = new TranslateTransform();
            canvas.Children.Add(dot);
        }

        return new Border
        {
            Child = canvas,
            IsHitTestVisible = false,
            Classes = { "fluent-decorative", "fluent-decorative-particles" },
        };
    }

    /// <summary>
    /// Advances every particle to <paramref name="progress"/> (0..1 over the 400ms run): each dot fades
    /// in and out while rising past the bottom edge — opacity and render transform only, no relayout.
    /// </summary>
    public static void UpdatePageTurnParticles(Border layer, double progress)
    {
        if (layer.Child is not Canvas canvas)
        {
            return;
        }

        foreach (var dot in canvas.Children.OfType<Ellipse>())
        {
            if (dot.Tag is not PageTurnParticleSpec spec)
            {
                continue;
            }

            var total = MotionTimings.DecorativePageTurnMilliseconds;
            var span = total - spec.DelayMs;
            var local = span <= 0 ? 1 : Math.Clamp((progress * total - spec.DelayMs) / span, 0, 1);
            dot.Opacity = Math.Sin(Math.PI * local) * spec.MaxOpacity;
            Canvas.SetLeft(dot, spec.XRatio * canvas.Bounds.Width);
            Canvas.SetTop(dot, Math.Max(0, canvas.Bounds.Height - spec.FromBottom));
            if (dot.RenderTransform is TranslateTransform translate)
            {
                translate.X = spec.DriftX * local;
                translate.Y = -spec.Rise * local;
            }
        }
    }
}
