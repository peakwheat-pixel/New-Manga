using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Layout;

namespace NewManga.DesignSystem.Controls;

/// <summary>
/// SegmentedControl (contract §3.2): 2–4 mutually exclusive segments for view/mode switching
/// (页面/成品/分屏, Page/Batch). Built from themed <see cref="Button"/> segments so keyboard/focus
/// behaviour comes from the design system's Button theme.
/// </summary>
public sealed class SegmentedControl : Border
{
    /// <summary>The segment labels (2–4 recommended, not enforced).</summary>
    public static readonly StyledProperty<IReadOnlyList<string>?> ItemsProperty =
        AvaloniaProperty.Register<SegmentedControl, IReadOnlyList<string>?>(nameof(Items));

    /// <summary>Selected segment index; -1 = none.</summary>
    public static readonly StyledProperty<int> SelectedIndexProperty =
        AvaloniaProperty.Register<SegmentedControl, int>(nameof(SelectedIndex), defaultValue: 0);

    private readonly StackPanel _row = new() { Orientation = Orientation.Horizontal };

    public SegmentedControl()
    {
        Classes.Add("segmented");
        _row.Classes.Add("nm-segmented-row");
        Child = _row;
        Rebuild();
    }

    /// <summary>Raised when the selected segment changes.</summary>
    public event EventHandler<int>? SelectionChanged;

    /// <summary>Gets or sets the segment labels.</summary>
    public IReadOnlyList<string>? Items
    {
        get => GetValue(ItemsProperty);
        set => SetValue(ItemsProperty, value);
    }

    /// <summary>Gets or sets the selected segment index.</summary>
    public int SelectedIndex
    {
        get => GetValue(SelectedIndexProperty);
        set => SetValue(SelectedIndexProperty, value);
    }

    protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
    {
        base.OnPropertyChanged(change);
        if (change.Property == ItemsProperty || change.Property == SelectedIndexProperty)
        {
            Rebuild();
        }
    }

    private void Rebuild()
    {
        _row.Children.Clear();
        var items = Items;
        if (items is null)
        {
            return;
        }

        for (var index = 0; index < items.Count; index++)
        {
            var segmentIndex = index;
            var button = new Button
            {
                Content = items[index],
                Classes = { "segmented-item", "sm" },
            };
            button.Classes.Set("selected", index == SelectedIndex);
            button.Click += (_, _) =>
            {
                if (SelectedIndex == segmentIndex)
                {
                    return;
                }

                SelectedIndex = segmentIndex;
                SelectionChanged?.Invoke(this, segmentIndex);
            };
            _row.Children.Add(button);
        }
    }
}

/// <summary>
/// SearchField (contract §3.2): search-styled text input with IME-safe editing, a watermark and
/// Esc-to-clear. The inner control is a real <see cref="TextBox"/> so the platform text stack is kept.
/// </summary>
public sealed class SearchField : Border
{
    /// <summary>Current text.</summary>
    public static readonly StyledProperty<string?> TextProperty =
        AvaloniaProperty.Register<SearchField, string?>(nameof(Text), defaultBindingMode: Avalonia.Data.BindingMode.TwoWay);

    /// <summary>Placeholder text shown while empty.</summary>
    public static readonly StyledProperty<string?> PlaceholderProperty =
        AvaloniaProperty.Register<SearchField, string?>(nameof(Placeholder), "搜索");

    private readonly TextBox _textBox = new();
    private bool _syncing;

    public SearchField()
    {
        Classes.Add("search-field");
        _textBox.Classes.Add("search");
        _textBox.Watermark = Placeholder;
        _textBox.KeyDown += (_, args) =>
        {
            if (args.Key != Key.Escape)
            {
                return;
            }

            _textBox.Text = string.Empty;
            args.Handled = true;
        };
        _textBox.TextChanged += (_, _) =>
        {
            if (_syncing)
            {
                return;
            }

            _syncing = true;
            SetCurrentValue(TextProperty, _textBox.Text);
            _syncing = false;
        };
        Child = _textBox;
    }

    /// <summary>Gets or sets the current text.</summary>
    public string? Text
    {
        get => GetValue(TextProperty);
        set => SetValue(TextProperty, value);
    }

    /// <summary>Gets or sets the placeholder text.</summary>
    public string? Placeholder
    {
        get => GetValue(PlaceholderProperty);
        set => SetValue(PlaceholderProperty, value);
    }

    protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
    {
        base.OnPropertyChanged(change);
        if (change.Property == TextProperty && !_syncing)
        {
            _syncing = true;
            _textBox.Text = Text;
            _syncing = false;
        }
        else if (change.Property == PlaceholderProperty)
        {
            _textBox.Watermark = Placeholder;
        }
    }
}
