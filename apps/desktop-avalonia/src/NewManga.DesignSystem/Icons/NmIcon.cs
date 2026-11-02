using Avalonia;
using ShapePath = Avalonia.Controls.Shapes.Path;
using Avalonia.Media;

namespace NewManga.DesignSystem.Icons;

/// <summary>The linear icon vocabulary shipped by the design system (DESIGN_SYSTEM §5: 1.25px stroke,
/// 20x20 viewBox, line-only, accent only for the active state, never emoji).</summary>
public enum NmIconKind
{
    Add,
    Close,
    Search,
    Settings,
    Check,
    Warning,
    Error,
    Info,
    ChevronLeft,
    ChevronRight,
    ChevronDown,
    ChevronUp,
    Folder,
    Page,
    Play,
    Pause,
    Stop,
    Lock,
    Refresh,
    Export,
    Import,
    More,
    Grid,
    List,
    Filter,
    Theme,
    Command,
    Retry,
    History,
    Delete,
    Edit,
    Eye,
    Split,
    ZoomIn,
    ZoomOut,
    FitWindow,
    Chapter,
    Library,
    Studio,
    Reader,
    File,}

/// <summary>
/// A single-path linear icon. The geometry comes from the design-system icon table; the stroke colour,
/// stroke width and size come from tokens through styles (<c>NmIcon</c>, <c>NmIcon.active</c>,
/// <c>NmIcon.sm</c>), so icons follow theme/contrast changes like every other token consumer.
/// </summary>
public sealed class NmIcon : ShapePath
{
    /// <summary>Which icon geometry to render.</summary>
    public static readonly StyledProperty<NmIconKind> KindProperty =
        AvaloniaProperty.Register<NmIcon, NmIconKind>(nameof(Kind));

    private static readonly IReadOnlyDictionary<NmIconKind, string> Geometries = new Dictionary<NmIconKind, string>
    {
        [NmIconKind.Add] = "M10 3 L10 17 M3 10 L17 10",
        [NmIconKind.Close] = "M5 5 L15 15 M15 5 L5 15",
        [NmIconKind.Search] = "M8.5 3 A5.5 5.5 0 1 0 8.5 14 A5.5 5.5 0 1 0 8.5 3 M12.5 12.5 L17 17",
        [NmIconKind.Settings] = "M10 7 A3 3 0 1 0 10 13 A3 3 0 1 0 10 7 M10 2 L10 4 M10 16 L10 18 M2 10 L4 10 M16 10 L18 10 M4.3 4.3 L5.7 5.7 M14.3 14.3 L15.7 15.7 M15.7 4.3 L14.3 5.7 M5.7 14.3 L4.3 15.7",
        [NmIconKind.Check] = "M4 10 L8 14 L16 5",
        [NmIconKind.Warning] = "M10 3 L18 17 L2 17 Z M10 8 L10 12 M10 14.5 L10 15",
        [NmIconKind.Error] = "M10 3 A7 7 0 1 0 10 17 A7 7 0 1 0 10 3 M7 7 L13 13 M13 7 L7 13",
        [NmIconKind.Info] = "M10 3 A7 7 0 1 0 10 17 A7 7 0 1 0 10 3 M10 9 L10 14 M10 6.5 L10 7",
        [NmIconKind.ChevronLeft] = "M12 4 L6 10 L12 16",
        [NmIconKind.ChevronRight] = "M8 4 L14 10 L8 16",
        [NmIconKind.ChevronDown] = "M4 8 L10 14 L16 8",
        [NmIconKind.ChevronUp] = "M4 12 L10 6 L16 12",
        [NmIconKind.Folder] = "M3 6 L8 6 L10 8 L17 8 L17 16 L3 16 Z",
        [NmIconKind.Page] = "M5 3 L12 3 L16 7 L16 17 L5 17 Z M12 3 L12 7 L16 7",
        [NmIconKind.Play] = "M7 4 L16 10 L7 16 Z",
        [NmIconKind.Pause] = "M7 4 L7 16 M13 4 L13 16",
        [NmIconKind.Stop] = "M5 5 L15 5 L15 15 L5 15 Z",
        [NmIconKind.Lock] = "M6 9 L6 7 A4 4 0 0 1 14 7 L14 9 M4 9 L16 9 L16 17 L4 17 Z",
        [NmIconKind.Refresh] = "M16 10 A6 6 0 1 1 12 4.5 M12 1.5 L12.4 4.5 L15 4",
        [NmIconKind.Export] = "M10 12 L10 3 M6 6 L10 3 L14 6 M4 12 L4 17 L16 17 L16 12",
        [NmIconKind.Import] = "M10 3 L10 12 M6 9 L10 12 L14 9 M4 12 L4 17 L16 17 L16 12",
        [NmIconKind.More] = "M4 10 A1 1 0 1 0 6 10 A1 1 0 1 0 4 10 M9 10 A1 1 0 1 0 11 10 A1 1 0 1 0 9 10 M14 10 A1 1 0 1 0 16 10 A1 1 0 1 0 14 10",
        [NmIconKind.Grid] = "M3 3 L9 3 L9 9 L3 9 Z M11 3 L17 3 L17 9 L11 9 Z M3 11 L9 11 L9 17 L3 17 Z M11 11 L17 11 L17 17 L11 17 Z",
        [NmIconKind.List] = "M4 5 L16 5 M4 10 L16 10 M4 15 L16 15",
        [NmIconKind.Filter] = "M3 5 L17 5 L11 11 L11 17 L9 15 L9 11 Z",
        [NmIconKind.Theme] = "M10 3 A7 7 0 1 0 10 17 A7 7 0 1 0 10 3 M10 3 L10 17",
        [NmIconKind.Command] = "M6 4 L8 8 L6 12 M14 4 L12 8 L14 12",
        [NmIconKind.Retry] = "M16 10 A6 6 0 1 1 12 4.5 M12 1.5 L12.4 4.5 L15 4",
        [NmIconKind.History] = "M10 3 A7 7 0 1 1 3 10 M2.5 6 L3 10 L6.5 9 M10 6 L10 10 L13 12",
        [NmIconKind.Delete] = "M4 6 L16 6 M7 6 L7 4 L13 4 L13 6 M6 6 L7 17 L13 17 L14 6 M9 9 L9 14 M11 9 L11 14",
        [NmIconKind.Edit] = "M4 16 L4 13 L13 4 L16 7 L7 16 Z M12 5 L15 8",
        [NmIconKind.Eye] = "M2 10 C5 5.5 8 4 10 4 C12 4 15 5.5 18 10 C15 14.5 12 16 10 16 C8 16 5 14.5 2 10 Z M10 7.5 A2.5 2.5 0 1 0 10 12.5 A2.5 2.5 0 1 0 10 7.5",
        [NmIconKind.Split] = "M3 4 L17 4 L17 16 L3 16 Z M10 4 L10 16 M10 10 L3 10 M10 10 L17 10",
        [NmIconKind.ZoomIn] = "M8.5 3 A5.5 5.5 0 1 0 8.5 14 A5.5 5.5 0 1 0 8.5 3 M8.5 5.5 L8.5 11.5 M5.5 8.5 L11.5 8.5 M12.5 12.5 L17 17",
        [NmIconKind.ZoomOut] = "M8.5 3 A5.5 5.5 0 1 0 8.5 14 A5.5 5.5 0 1 0 8.5 3 M5.5 8.5 L11.5 8.5 M12.5 12.5 L17 17",
        [NmIconKind.FitWindow] = "M3 7 L3 3 L7 3 M13 3 L17 3 L17 7 M17 13 L17 17 L13 17 M7 17 L3 17 L3 13 M7 7 L13 7 L13 13 L7 13 Z",
        [NmIconKind.Chapter] = "M4 4 L4 16 L9 16 L9 4 Z M11 4 L11 16 L16 16 L16 4 Z M4 4 L9 4 M11 4 L16 4",
        [NmIconKind.Library] = "M3 4 L3 17 L7 17 L7 4 Z M8.5 4 L8.5 17 L12.5 17 L12.5 4 Z M14 5 L17 16 L14.5 17 L12 6 Z",
        [NmIconKind.Studio] = "M3 4 L17 4 L17 13 L3 13 Z M10 13 L10 16 M7 17 L13 17",
        [NmIconKind.Reader] = "M10 5 C7.5 3.5 5 3.5 3 4.5 L3 15 C5 14 7.5 14 10 15.5 C12.5 14 15 14 17 15 L17 4.5 C15 3.5 12.5 3.5 10 5 Z M10 5 L10 15.5",
        [NmIconKind.File] = "M5 3 L12 3 L16 7 L16 17 L5 17 Z M12 3 L12 7 L16 7 M8 10 L13 10 M8 13 L13 13",    };

    public NmIcon()
    {
        Stretch = Stretch.Uniform;
        Apply();
    }

    /// <summary>Gets or sets which icon geometry to render.</summary>
    public NmIconKind Kind
    {
        get => GetValue(KindProperty);
        set => SetValue(KindProperty, value);
    }

    protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
    {
        base.OnPropertyChanged(change);
        if (change.Property == KindProperty)
        {
            Apply();
        }
    }

    private void Apply()
    {
        Data = Geometry.Parse(Geometries[Kind]);
        InvalidateMeasure();
    }
}

