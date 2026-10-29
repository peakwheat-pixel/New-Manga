using Avalonia;
using Avalonia.Markup.Xaml;
using Avalonia.Styling;
using Avalonia.Themes.Fluent;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// Minimal headless application for the design-system test suite. It deliberately does not host the
/// product shell: tests only need Avalonia + the same style stack the real app composes
/// (FluentTheme first, design-system styles last), exactly like <c>App.axaml</c>.
/// </summary>
public sealed class DesignSystemTestApp : Application
{
    public override void Initialize()
    {
        Styles.Add(new FluentTheme());
        var designSystemStyles = (Styles)AvaloniaXamlLoader.Load(
            new Uri("avares://NewManga.DesignSystem/Styles/NewMangaStyles.axaml"));
        Styles.Add(designSystemStyles);
    }
}
