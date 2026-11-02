using Avalonia.Automation;
using Avalonia.Controls;
using Avalonia.Controls.Primitives;
using Avalonia.Layout;
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
}
