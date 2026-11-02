using Avalonia;
using Avalonia.Controls;

namespace NewManga.DesignSystem.Controls;

/// <summary>Token-styled Fluent surface card used by the FEA-06 frontend.</summary>
public sealed class SurfaceCard : Border
{
    public SurfaceCard() => Classes.Add("fluent-surface-card");
}

/// <summary>Token-styled Fluent modal surface. The owner supplies the overlay and open state.</summary>
public sealed class FluentDialog : Border
{
    public static readonly StyledProperty<bool> IsOpenProperty =
        AvaloniaProperty.Register<FluentDialog, bool>(nameof(IsOpen));

    public FluentDialog()
    {
        Classes.Add("fluent-dialog");
        IsVisible = false;
    }

    public bool IsOpen
    {
        get => GetValue(IsOpenProperty);
        set => SetValue(IsOpenProperty, value);
    }

    protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
    {
        base.OnPropertyChanged(change);
        if (change.Property == IsOpenProperty)
        {
            IsVisible = IsOpen;
        }
    }
}

/// <summary>Book cover card visual for the Shelf grid.</summary>
public sealed class BookCard : Button
{
    public BookCard() => Classes.Add("fluent-book-card");
}

/// <summary>Book row visual for the Shelf list.</summary>
public sealed class BookRow : Button
{
    public BookRow() => Classes.Add("fluent-book-row");
}

/// <summary>Token-styled chapter list region.</summary>
public sealed class ChapterList : StackPanel
{
    public ChapterList() => Classes.Add("fluent-chapter-list");
}

/// <summary>Horizontal page-thumbnail strip.</summary>
public sealed class PageThumbStrip : ItemsControl
{
    public PageThumbStrip() => Classes.Add("fluent-page-thumb-strip");
}

/// <summary>Workbench overlay for one Core-projected region.</summary>
public sealed class RegionBox : Border
{
    public RegionBox() => Classes.Add("fluent-region-box");
}

/// <summary>Lazy film-strip thumbnail surface.</summary>
public sealed class StreamingThumb : Border
{
    public StreamingThumb() => Classes.Add("fluent-streaming-thumb");
}

/// <summary>Horizontally scrollable workbench status matrix.</summary>
public sealed class BatchMatrix : ScrollViewer
{
    public BatchMatrix() => Classes.Add("fluent-batch-matrix");
}

/// <summary>Run status projection bar; its values must come from a Host projection.</summary>
public sealed class RunProjectionBar : Border
{
    public RunProjectionBar() => Classes.Add("fluent-run-projection-bar");
}

/// <summary>Full-bleed reader page surface.</summary>
public sealed class ReaderPage : Border
{
    public ReaderPage() => Classes.Add("fluent-reader-page");
}

/// <summary>Token-styled progress track for the reader.</summary>
public sealed class ReaderProgressBar : ProgressBar
{
    public ReaderProgressBar() => Classes.Add("fluent-reader-progress");
}

/// <summary>Settings group card.</summary>
public sealed class SettingsGroup : Border
{
    public SettingsGroup() => Classes.Add("fluent-settings-group");
}

/// <summary>One label/control/help row in Settings.</summary>
public sealed class SettingsField : Grid
{
    public SettingsField() => Classes.Add("fluent-settings-field");
}

/// <summary>Horizontal tab strip with tokenized selection visuals.</summary>
public sealed class TabStrip : StackPanel
{
    public TabStrip()
    {
        Classes.Add("fluent-tab-strip");
        Orientation = Avalonia.Layout.Orientation.Horizontal;
    }
}
