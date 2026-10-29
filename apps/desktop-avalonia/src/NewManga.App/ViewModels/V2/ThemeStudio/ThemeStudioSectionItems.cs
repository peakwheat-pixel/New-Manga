using System.Collections.ObjectModel;
using System.Windows.Input;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Media;
using NewManga.App.Shell.V2;
using NewManga.ThemeEngine;

namespace NewManga.App.ViewModels.V2.ThemeStudio;

/// <summary>One entry of the left navigation rail (icon + title + subtitle + dirty marker).</summary>
public sealed class ThemeStudioSectionItem : ObservableObject
{
    private bool _isSelected;
    private bool _isDirty;

    internal ThemeStudioSectionItem(ThemeStudioSection section, ICommand selectCommand)
    {
        Section = section;
        Title = ThemeStudioLabels.Section(section);
        Subtitle = ThemeStudioLabels.SectionSubtitle(section);
        Icon = ThemeStudioIcons.For(section);
        SelectCommand = selectCommand;
    }

    public ThemeStudioSection Section { get; }

    public string Title { get; }

    public string Subtitle { get; }

    public Geometry Icon { get; }

    public ICommand SelectCommand { get; }

    public bool IsSelected
    {
        get => _isSelected;
        internal set => Set(ref _isSelected, value);
    }

    public bool IsDirty
    {
        get => _isDirty;
        internal set => Set(ref _isDirty, value);
    }

    /// <summary>Accessible description: the dirty state is also spoken (never colour-only, AC11).</summary>
    public string AccessibleLabel => IsDirty ? $"{Title}（有未提交改动）" : Title;
}

/// <summary>
/// 20×20 stroked line icons (DESIGN_SYSTEM §5: 1.25px stroke, no emoji, no filled icons). Geometries are
/// authored inline here so the rail never depends on image assets.
/// </summary>
public static class ThemeStudioIcons
{
    /// <summary>Stroke width applied by the rail (kept in the view through the design-system token).</summary>
    public static Geometry For(ThemeStudioSection section) => Geometry.Parse(section switch
    {
        ThemeStudioSection.Library =>
            "M3,3 H9 V9 H3 Z M11,3 H17 V9 H11 Z M3,11 H9 V17 H3 Z M11,11 H17 V17 H11 Z",
        ThemeStudioSection.Preview =>
            "M2,10 C5,4.5 15,4.5 18,10 C15,15.5 5,15.5 2,10 Z M10,7.5 A2.5,2.5 0 1 0 10.01,7.5",
        ThemeStudioSection.MyThemes =>
            "M5,3 H15 V17 L10,13.5 L5,17 Z",
        ThemeStudioSection.Editor =>
            "M3,6 H17 M3,14 H17 M7,3 V9 M13,11 V17",
        ThemeStudioSection.Appearance =>
            "M10,2.5 V4.5 M10,15.5 V17.5 M2.5,10 H4.5 M15.5,10 H17.5 M5.2,5.2 L6.6,6.6 M13.4,13.4 L14.8,14.8 M14.8,5.2 L13.4,6.6 M6.6,13.4 L5.2,14.8 M10,6.3 A3.7,3.7 0 1 0 10.01,6.3",
        ThemeStudioSection.ImportExport =>
            "M7,3 V13 M4,10 L7,13 L10,10 M13,17 V7 M10,10 L13,7 L16,10",
        _ => "M4,7 A7,7 0 1 1 3.2,11.5 M4,3 V7 H8",
    });
}

/// <summary>
/// Shared plumbing for the seven section view models: owner back-pointer (single source of truth),
/// status/busy routing and async command hygiene.
/// </summary>
public abstract class ThemeStudioSectionViewModel : ObservableObject
{
    private bool _isBusy;

    protected ThemeStudioSectionViewModel(ThemeStudioViewModel owner, ThemeStudioSection section)
    {
        Owner = owner ?? throw new ArgumentNullException(nameof(owner));
        Section = section;
    }

    /// <summary>The surface view model that owns state (never a second copy of the draft).</summary>
    protected ThemeStudioViewModel Owner { get; }

    /// <summary>Section this view model renders.</summary>
    public ThemeStudioSection Section { get; }

    /// <summary>True while an async command of this section runs (skeleton instead of full-page spinner).</summary>
    public bool IsBusy
    {
        get => _isBusy;
        protected set => Set(ref _isBusy, value);
    }

    /// <summary>The service facade (sections never touch the engine directly).</summary>
    protected IThemeStudioService Service => Owner.Service;

    /// <summary>Called when the section becomes visible (recompose palettes / refresh lists).</summary>
    public virtual void OnActivated()
    {
    }

    /// <summary>Called when the section is left (persist lightweight UI state only).</summary>
    public virtual void OnDeactivated()
    {
    }

    /// <summary>Runs an async command with consistent busy + error reporting (never throws at the UI).</summary>
    protected async void Run(Func<Task> action, string? busyMessage = null)
    {
        if (IsBusy)
        {
            return;
        }

        IsBusy = true;
        Owner.ReportStatus(busyMessage);
        try
        {
            await action().ConfigureAwait(true);
        }
        catch (Exception exception) when (exception is not OperationCanceledException)
        {
            Owner.ReportError(exception.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }
}

/// <summary>One theme card of the library grid (mini tri-view + identity + actions).</summary>
public sealed class ThemeStudioCardViewModel : ObservableObject
{
    private bool _isFavorite;
    private bool _isSelected;
    private ThemeStudioPalette? _palette;
    private double _width = ThemeStudioMetrics.CardWidthDefault;

    internal ThemeStudioCardViewModel(
        ThemePackage package,
        ThemeStudioPalette palette,
        bool isFavorite,
        ICommand previewCommand,
        ICommand applyCommand,
        ICommand favoriteCommand)
    {
        Package = package ?? throw new ArgumentNullException(nameof(package));
        Palette = palette;
        _isFavorite = isFavorite;
        PreviewCommand = previewCommand;
        ApplyCommand = applyCommand;
        FavoriteCommand = favoriteCommand;
    }

    public ThemePackage Package { get; }

    public string Id => Package.Descriptor.Id;

    public string Name => Package.Descriptor.Name;

    public string Author => string.IsNullOrWhiteSpace(Package.Descriptor.Author) ? "未知作者" : Package.Descriptor.Author;

    public string Version => $"v{Package.Descriptor.Version}";

    public string TagsLabel => Package.Descriptor.Tags.Count == 0 ? "无标签" : string.Join(" · ", Package.Descriptor.Tags);

    public string SupportLabel => ThemeStudioLabels.AppearanceSupport(
        Package.Descriptor.SupportsLight,
        Package.Descriptor.SupportsDark);

    public string KindLabel => ThemeStudioLabels.ThemeKindLabel(Package.Descriptor.Kind);

    public bool IsBuiltIn => Package.Descriptor.Kind == ThemeKind.BuiltIn;

    /// <summary>Mini tri-view palette: the card's own personality with the current appearance knobs.</summary>
    public ThemeStudioPalette Palette
    {
        get => _palette ??= OwnerPalette!;
        private set => _palette = value;
    }

    internal ThemeStudioPalette? OwnerPalette { get; set; }

    public ICommand PreviewCommand { get; }

    public ICommand ApplyCommand { get; }

    public ICommand FavoriteCommand { get; }

    public bool IsFavorite
    {
        get => _isFavorite;
        internal set
        {
            if (Set(ref _isFavorite, value))
            {
                OnPropertyChanged(nameof(FavoriteLabel), nameof(AccessibleLabel));
            }
        }
    }

    public string FavoriteLabel => IsFavorite ? "★ 已收藏" : "☆ 收藏";

    public bool IsSelected
    {
        get => _isSelected;
        internal set => Set(ref _isSelected, value);
    }

    /// <summary>Column width of the grid cell (the view model computes 4/3/2 columns from the viewport).</summary>
    public double Width
    {
        get => _width;
        internal set => Set(ref _width, value);
    }

    /// <summary>Accessible name: identity + support + favorite state, no colour-only encoding.</summary>
    public string AccessibleLabel =>
        $"{Name}，{Author}，{KindLabel}，{SupportLabel}{(IsFavorite ? "，已收藏" : string.Empty)}";
}

/// <summary>A filter chip of the library header (category or appearance filter).</summary>
public sealed class ThemeStudioFilterChip : ObservableObject
{
    private bool _isOn;

    internal ThemeStudioFilterChip(string key, string label, ICommand toggleCommand)
    {
        Key = key;
        Label = label;
        ToggleCommand = toggleCommand;
    }

    public string Key { get; }

    public string Label { get; }

    public ICommand ToggleCommand { get; }

    public bool IsOn
    {
        get => _isOn;
        internal set => Set(ref _isOn, value);
    }
}

/// <summary>One selectable option rendered as a card/segmented button (appearance, density, preview mode…).</summary>
public sealed class ThemeStudioOption : ObservableObject
{
    private bool _isSelected;

    internal ThemeStudioOption(string key, string label, string? description, ICommand selectCommand)
    {
        Key = key;
        Label = label;
        Description = description;
        SelectCommand = selectCommand;
    }

    public string Key { get; }

    public string Label { get; }

    public string? Description { get; }

    public bool HasDescription => !string.IsNullOrEmpty(Description);

    public ICommand SelectCommand { get; }

    public bool IsSelected
    {
        get => _isSelected;
        internal set => Set(ref _isSelected, value);
    }

    /// <summary>Accessible description keeps the selection state in text (AC11).</summary>
    public string AccessibleLabel => IsSelected ? $"{Label}（已选）" : Label;
}

/// <summary>Simple row used by read-only summaries (layout/limits/migration notices).</summary>
public sealed record ThemeStudioInfoRow(string Label, string Value, string? Hint = null)
{
    public bool HasHint => !string.IsNullOrEmpty(Hint);

    public string ValueLabel => string.IsNullOrEmpty(Value) ? "—" : Value;
}
