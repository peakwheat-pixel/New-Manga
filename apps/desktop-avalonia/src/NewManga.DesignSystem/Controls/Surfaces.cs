using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.Presenters;
using Avalonia.Input;
using Avalonia.Layout;

namespace NewManga.DesignSystem.Controls;

/// <summary>
/// Drawer (contract §3.2): right-side sliding surface (360px) for Batch details and Console section
/// details. It overlays the main area but does not reset its scroll position — the host keeps the
/// drawer inside a panel so the content underneath stays laid out.
/// </summary>
public sealed class Drawer : Border
{
    /// <summary>Whether the drawer is visible.</summary>
    public static readonly StyledProperty<bool> IsOpenProperty =
        AvaloniaProperty.Register<Drawer, bool>(nameof(IsOpen));

    /// <summary>Drawer header text.</summary>
    public static readonly StyledProperty<string?> HeaderProperty =
        AvaloniaProperty.Register<Drawer, string?>(nameof(Header));

    /// <summary>Drawer body content.</summary>
    public static readonly StyledProperty<object?> ContentProperty =
        AvaloniaProperty.Register<Drawer, object?>(nameof(Content));

    private readonly TextBlock _header = new() { Classes = { "title" } };
    private readonly ContentPresenter _presenter = new();

    public Drawer()
    {
        Classes.Add("drawer");
        var body = new StackPanel
        {
            Classes = { "nm-drawer-body" },
            Orientation = Orientation.Vertical,
            Children = { _header, _presenter },
        };
        Child = body;
        Apply();
    }

    /// <summary>Gets or sets whether the drawer is open.</summary>
    public bool IsOpen
    {
        get => GetValue(IsOpenProperty);
        set => SetValue(IsOpenProperty, value);
    }

    /// <summary>Gets or sets the header text.</summary>
    public string? Header
    {
        get => GetValue(HeaderProperty);
        set => SetValue(HeaderProperty, value);
    }

    /// <summary>Gets or sets the body content.</summary>
    public object? Content
    {
        get => GetValue(ContentProperty);
        set => SetValue(ContentProperty, value);
    }

    protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
    {
        base.OnPropertyChanged(change);
        if (change.Property == IsOpenProperty)
        {
            IsVisible = IsOpen;
        }
        else if (change.Property == HeaderProperty)
        {
            _header.Text = Header;
            _header.IsVisible = !string.IsNullOrWhiteSpace(Header);
        }
        else if (change.Property == ContentProperty)
        {
            _presenter.Content = Content;
        }
    }

    private void Apply()
    {
        IsVisible = IsOpen;
        _header.Text = Header;
        _header.IsVisible = !string.IsNullOrWhiteSpace(Header);
        _presenter.Content = Content;
    }
}

/// <summary>
/// Modal (contract §3.2 base version): confirm/danger/interrupt surfaces over a scrim. The scrim uses
/// the derived <c>Nm.Color.Scrim</c> token; Esc requests close. Default focus and focus trapping are
/// host responsibilities until the shell (V11R-B-1) provides the modal host.
/// </summary>
public sealed class Modal : Border
{
    /// <summary>Whether the modal is visible.</summary>
    public static readonly StyledProperty<bool> IsOpenProperty =
        AvaloniaProperty.Register<Modal, bool>(nameof(IsOpen));

    /// <summary>Modal title.</summary>
    public static readonly StyledProperty<string?> TitleProperty =
        AvaloniaProperty.Register<Modal, string?>(nameof(Title));

    /// <summary>Modal body content.</summary>
    public static readonly StyledProperty<object?> ContentProperty =
        AvaloniaProperty.Register<Modal, object?>(nameof(Content));

    /// <summary>Primary action label.</summary>
    public static readonly StyledProperty<string?> PrimaryActionTextProperty =
        AvaloniaProperty.Register<Modal, string?>(nameof(PrimaryActionText));

    /// <summary>Cancel action label (always present; Esc activates it).</summary>
    public static readonly StyledProperty<string?> CancelActionTextProperty =
        AvaloniaProperty.Register<Modal, string?>(nameof(CancelActionText), "取消");

    private readonly TextBlock _title = new() { Classes = { "title" } };
    private readonly ContentPresenter _presenter = new();
    private readonly Button _primary = new() { Classes = { "primary" } };
    private readonly Button _cancel = new();

    public Modal()
    {
        Classes.Add("modal");
        var actions = new StackPanel
        {
            Classes = { "nm-modal-actions" },
            Orientation = Orientation.Horizontal,
            Children = { _cancel, _primary },
        };
        var panel = new Border
        {
            Classes = { "overlay", "modal-panel" },
            Child = new StackPanel
            {
                Classes = { "nm-modal-body" },
                Orientation = Orientation.Vertical,
                Children = { _title, _presenter, actions },
            },
        };
        Child = panel;
        _primary.Click += (_, _) => PrimaryInvoked?.Invoke(this, EventArgs.Empty);
        _cancel.Click += (_, _) => CloseRequested?.Invoke(this, EventArgs.Empty);
        Apply();
    }

    /// <summary>Raised when the primary action is activated.</summary>
    public event EventHandler? PrimaryInvoked;

    /// <summary>Raised when the modal should be closed (cancel button or Esc).</summary>
    public event EventHandler? CloseRequested;

    /// <summary>Gets or sets whether the modal is open.</summary>
    public bool IsOpen
    {
        get => GetValue(IsOpenProperty);
        set => SetValue(IsOpenProperty, value);
    }

    /// <summary>Gets or sets the title.</summary>
    public string? Title
    {
        get => GetValue(TitleProperty);
        set => SetValue(TitleProperty, value);
    }

    /// <summary>Gets or sets the body content.</summary>
    public object? Content
    {
        get => GetValue(ContentProperty);
        set => SetValue(ContentProperty, value);
    }

    /// <summary>Gets or sets the primary action label.</summary>
    public string? PrimaryActionText
    {
        get => GetValue(PrimaryActionTextProperty);
        set => SetValue(PrimaryActionTextProperty, value);
    }

    /// <summary>Gets or sets the cancel action label.</summary>
    public string? CancelActionText
    {
        get => GetValue(CancelActionTextProperty);
        set => SetValue(CancelActionTextProperty, value);
    }

    protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
    {
        base.OnPropertyChanged(change);
        Apply();
    }

    /// <inheritdoc />
    protected override void OnKeyDown(KeyEventArgs e)
    {
        base.OnKeyDown(e);
        if (e.Key == Key.Escape && IsOpen)
        {
            CloseRequested?.Invoke(this, EventArgs.Empty);
            e.Handled = true;
        }
    }

    private void Apply()
    {
        IsVisible = IsOpen;
        _title.Text = Title;
        _title.IsVisible = !string.IsNullOrWhiteSpace(Title);
        _presenter.Content = Content;
        _primary.Content = PrimaryActionText;
        _primary.IsVisible = !string.IsNullOrWhiteSpace(PrimaryActionText);
        _cancel.Content = CancelActionText;
    }
}

/// <summary>
/// TopBand (contract §3.2 base version): 36px top bar with left / center / right slots for space tabs,
/// breadcrumb, scope selector, attention menu, command palette and theme entry.
/// </summary>
public sealed class TopBand : Border
{
    /// <summary>Left slot content.</summary>
    public static readonly StyledProperty<object?> LeftContentProperty =
        AvaloniaProperty.Register<TopBand, object?>(nameof(LeftContent));

    /// <summary>Center slot content.</summary>
    public static readonly StyledProperty<object?> CenterContentProperty =
        AvaloniaProperty.Register<TopBand, object?>(nameof(CenterContent));

    /// <summary>Right slot content.</summary>
    public static readonly StyledProperty<object?> RightContentProperty =
        AvaloniaProperty.Register<TopBand, object?>(nameof(RightContent));

    private readonly ContentPresenter _left = new();
    private readonly ContentPresenter _center = new();
    private readonly ContentPresenter _right = new();

    public TopBand()
    {
        Classes.Add("top-band");
        var grid = new Grid
        {
            ColumnDefinitions = new ColumnDefinitions("Auto,*,Auto"),
            Classes = { "nm-topband-row" },
        };
        grid.Children.Add(_left);
        grid.Children.Add(_center);
        grid.Children.Add(_right);
        Grid.SetColumn(_center, 1);
        Grid.SetColumn(_right, 2);
        Child = grid;
    }

    /// <summary>Gets or sets the left slot content.</summary>
    public object? LeftContent
    {
        get => GetValue(LeftContentProperty);
        set => SetValue(LeftContentProperty, value);
    }

    /// <summary>Gets or sets the center slot content.</summary>
    public object? CenterContent
    {
        get => GetValue(CenterContentProperty);
        set => SetValue(CenterContentProperty, value);
    }

    /// <summary>Gets or sets the right slot content.</summary>
    public object? RightContent
    {
        get => GetValue(RightContentProperty);
        set => SetValue(RightContentProperty, value);
    }

    protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
    {
        base.OnPropertyChanged(change);
        if (change.Property == LeftContentProperty)
        {
            _left.Content = LeftContent;
        }
        else if (change.Property == CenterContentProperty)
        {
            _center.Content = CenterContent;
        }
        else if (change.Property == RightContentProperty)
        {
            _right.Content = RightContent;
        }
    }
}
