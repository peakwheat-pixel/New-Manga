using Avalonia;
using Avalonia.Automation;
using Avalonia.Controls;
using Avalonia.Interactivity;
using Avalonia.LogicalTree;
using NewManga.App.Views.V2.Shell.Controls;
using DsKbd = NewManga.DesignSystem.Controls.Kbd;

namespace NewManga.App.Shell.V2;

/// <summary>
/// V11R-A11Y-1: mechanical accessible-name fallback for the V2 shell.
///
/// Real-machine UIA exposed buttons whose Content is a control tree as their CLR type name
/// (<c>Avalonia.Controls.StackPanel</c>). Explicit <see cref="AutomationProperties.Name"/> is always
/// preferred; this fallback derives a readable name from the content text (or the nested Kbd gesture)
/// for buttons that were not named explicitly. Icon-only actions still need an explicit name, which the
/// accessibility regression test enforces.
/// </summary>
public static class V2AccessibleNames
{
    private static int _registered;

    /// <summary>Registers the content-name fallback once per process (App.Initialize).</summary>
    public static void Register()
    {
        if (Interlocked.Exchange(ref _registered, 1) == 1)
        {
            return;
        }

        Button.ContentProperty.Changed.AddClassHandler<Button>((button, _) => Apply(button));
    }

    /// <summary>Applies the fallback to one button (also reusable from tests).</summary>
    public static void Apply(Button button)
    {
        if (button.IsSet(AutomationProperties.NameProperty))
        {
            return;
        }

        var name = DeriveName(button.Content);
        if (!string.IsNullOrWhiteSpace(name))
        {
            AutomationProperties.SetName(button, name);
            button.Loaded -= OnButtonLoaded;
            return;
        }

        // DataTemplate content can be populated after Content is assigned; retry once on Loaded.
        button.Loaded -= OnButtonLoaded;
        button.Loaded += OnButtonLoaded;
    }

    private static void OnButtonLoaded(object? sender, RoutedEventArgs e)
    {
        if (sender is Button button)
        {
            button.Loaded -= OnButtonLoaded;
            Apply(button);
        }
    }

    private static string? DeriveName(object? content)
    {
        switch (content)
        {
            case string text:
                return Normalize(text);
            case Kbd kbd:
                return string.IsNullOrWhiteSpace(kbd.Text) ? null : $"快捷键 {kbd.Text}";
            case DsKbd kbd:
                return string.IsNullOrWhiteSpace(kbd.Gesture) ? null : $"快捷键 {kbd.Gesture}";
            case Control control:
                var texts = control.GetLogicalDescendants()
                    .OfType<TextBlock>()
                    .Select(block => Normalize(block.Text))
                    .Where(text => text is { Length: > 0 })
                    .Distinct(StringComparer.Ordinal)
                    .Take(3)
                    .ToArray();
                return texts.Length == 0 ? null : string.Join(" ", texts);
            default:
                return null;
        }
    }

    private static string? Normalize(string? text)
    {
        if (string.IsNullOrWhiteSpace(text))
        {
            return null;
        }

        var normalized = string.Join(' ', text.Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries));
        return normalized.Length == 0 ? null : normalized;
    }
}
