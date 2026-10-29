using System.Collections.ObjectModel;
using System.Windows.Input;
using Avalonia.Media;
using NewManga.App.Shell.V2;
using NewManga.ThemeEngine;

namespace NewManga.App.ViewModels.V2.ThemeStudio;

/// <summary>
/// ① 主题库 (THEME_STUDIO_SPEC §3.1): search + category chips + appearance filters + card grid whose
/// breakpoints are 4/3/2 columns at ≥1600 / ≥1280 / &lt;1280 (frozen spec). Every card renders the theme's
/// own palette through a <c>PaletteScope</c>, so the mini tri-view is a real control tree, not a snapshot.
/// </summary>
public sealed class ThemeStudioLibraryViewModel : ThemeStudioSectionViewModel
{
    /// <summary>Minimum card width accepted by the grid, derived from the DS tokens (≈249).</summary>
    public static double MinCardWidth => ThemeStudioMetrics.CardMinWidth;

    /// <summary>Gap between cards (DS spacing token <c>Nm.Space.4</c>).</summary>
    public static double CardGap => ThemeStudioMetrics.CardGap;

    private readonly List<ThemeStudioFilterChip> _categoryChips = new();
    private readonly List<ThemeStudioFilterChip> _appearanceChips = new();
    private string _searchText = string.Empty;
    private string _categoryKey = "all";
    private string _appearanceKey = "any";
    private int _columnCount = 4;
    private double _cardWidth = ThemeStudioMetrics.CardWidthDefault;
    private ThemeStudioCardViewModel? _selectedCard;
    private bool _isRefreshing;

    internal ThemeStudioLibraryViewModel(ThemeStudioViewModel owner)
        : base(owner, ThemeStudioSection.Library)
    {
        AddCategory("all", "全部");
        AddCategory("builtin", "内置");
        AddCategory("user", "我的");
        AddCategory("favorite", "收藏");

        AddAppearance("any", "任意明暗");
        AddAppearance("light", "支持浅色");
        AddAppearance("dark", "支持深色");
        AddAppearance("both", "明暗均支持");
        AddAppearance("highcontrast", "高对比友好");

        ClearFiltersCommand = new RelayCommand(ClearFilters);
        FocusSearchCommand = new RelayCommand(() => Owner.FocusSearch());

        // Populated after the Add* calls: an ObservableCollection copy taken before them would stay empty.
        CategoryChips = new ObservableCollection<ThemeStudioFilterChip>(_categoryChips);
        AppearanceChips = new ObservableCollection<ThemeStudioFilterChip>(_appearanceChips);
    }

    /// <summary>Card list after search + chips.</summary>
    public ObservableCollection<ThemeStudioCardViewModel> Cards { get; } = new();

    /// <summary>Category chips (全部/内置/我的/收藏).</summary>
    public ObservableCollection<ThemeStudioFilterChip> CategoryChips { get; }

    /// <summary>Appearance filters (明/暗/均支持/高对比友好).</summary>
    public ObservableCollection<ThemeStudioFilterChip> AppearanceChips { get; }

    public ICommand ClearFiltersCommand { get; }

    public ICommand FocusSearchCommand { get; }

    public string SearchText
    {
        get => _searchText;
        set
        {
            if (Set(ref _searchText, value ?? string.Empty))
            {
                Refresh();
            }
        }
    }

    /// <summary>Selected category key (single choice).</summary>
    public string CategoryKey
    {
        get => _categoryKey;
        private set => Set(ref _categoryKey, value);
    }

    /// <summary>Selected appearance filter key (single choice).</summary>
    public string AppearanceKey
    {
        get => _appearanceKey;
        private set => Set(ref _appearanceKey, value);
    }

    /// <summary>Columns of the card grid (4/3/2 per the frozen breakpoints).</summary>
    public int ColumnCount
    {
        get => _columnCount;
        private set => Set(ref _columnCount, value);
    }

    /// <summary>Computed card width for the current column count (bound by the view).</summary>
    public double CardWidth
    {
        get => _cardWidth;
        private set => Set(ref _cardWidth, value);
    }

    public ThemeStudioCardViewModel? SelectedCard
    {
        get => _selectedCard;
        set
        {
            if (ReferenceEquals(_selectedCard, value))
            {
                return;
            }

            if (_selectedCard is not null)
            {
                _selectedCard.IsSelected = false;
            }

            _selectedCard = value;
            if (_selectedCard is not null)
            {
                _selectedCard.IsSelected = true;
            }

            OnPropertyChanged(nameof(SelectedCard), nameof(HasSelection), nameof(SelectionSummary));
        }
    }

    public bool HasSelection => SelectedCard is not null;

    /// <summary>Right-rail line for the selected card.</summary>
    public string SelectionSummary => SelectedCard is null
        ? "选中一个主题以查看摘要"
        : $"{SelectedCard.Name} · {SelectedCard.Author} · {SelectedCard.SupportLabel}";

    public bool HasCards => Cards.Count > 0;

    public bool IsEmpty => Cards.Count == 0;

    /// <summary>Empty-state copy (search miss vs empty catalog).</summary>
    public string EmptyTitle => HasActiveFilters ? "没有匹配的主题" : "还没有可用的主题";

    public string EmptyHint => HasActiveFilters
        ? "清空搜索与筛选后重试。"
        : "导入一个 .nmtheme 主题包，或从内置主题“另存为”。";

    public bool HasActiveFilters =>
        !string.IsNullOrWhiteSpace(SearchText) ||
        !string.Equals(CategoryKey, "all", StringComparison.Ordinal) ||
        !string.Equals(AppearanceKey, "any", StringComparison.Ordinal);

    /// <summary>
    /// Frozen breakpoint rule (spec §3.1): ≥ full → 4, ≥ compact → 3, otherwise 2. The breakpoint values
    /// are DS tokens resolved by <see cref="ThemeStudioMetrics"/>, not literals.
    /// </summary>
    public static int ColumnsForWidth(double width) => ThemeStudioMetrics.ColumnsForWidth(width);

    /// <summary>
    /// Updates the grid metrics. The column breakpoints are defined on the <b>window</b> width
    /// (THEME_STUDIO_SPEC §3.1: ≥1600 → 4, ≥1280 → 3, otherwise 2); the card width is derived from the
    /// content width available to the grid, so the rails never squeeze the cards below MinCardWidth.
    /// </summary>
    public void SetViewportMetrics(double windowWidth, double contentWidth)
    {
        var columns = ColumnsForWidth(windowWidth);
        if (columns != ColumnCount)
        {
            ColumnCount = columns;
        }

        var available = contentWidth - (CardGap * (columns - 1));
        var cardWidth = Math.Max(MinCardWidth, available / columns);
        if (Math.Abs(cardWidth - CardWidth) > 0.5)
        {
            CardWidth = cardWidth;
            foreach (var card in Cards)
            {
                card.Width = cardWidth;
            }
        }
    }

    /// <summary>Convenience overload when content width equals the window width (tests / narrow hosts).</summary>
    public void SetViewportWidth(double width) => SetViewportMetrics(width, width);

    /// <summary>Selects the next/previous card (arrow-key navigation, THEME_STUDIO_SPEC §5).</summary>
    public void MoveSelection(int delta)
    {
        if (Cards.Count == 0)
        {
            return;
        }

        var index = SelectedCard is null ? -1 : Cards.IndexOf(SelectedCard);
        var next = index < 0
            ? (delta >= 0 ? 0 : Cards.Count - 1)
            : Math.Clamp(index + delta, 0, Cards.Count - 1);
        SelectedCard = Cards[next];
    }

    /// <summary>Previews the selected card in the session (Enter / double click).</summary>
    public void PreviewSelected()
    {
        if (SelectedCard is not null)
        {
            Owner.PreviewThemeById(SelectedCard.Id);
        }
    }

    /// <summary>Applies the selected card directly (card "应用" button).</summary>
    public void ApplySelected()
    {
        if (SelectedCard is not null)
        {
            Run(() => Owner.ApplyThemeAsync(SelectedCard.Id, commitPreview: true));
        }
    }

    public void ToggleFavorite(ThemeStudioCardViewModel card)
    {
        ArgumentNullException.ThrowIfNull(card);
        Run(() => Owner.ToggleFavoriteAsync(card));
    }

    /// <summary>Rebuilds the card list from the catalog (keeps selection by id).</summary>
    public void Refresh()
    {
        if (_isRefreshing)
        {
            return;
        }

        _isRefreshing = true;
        try
        {
            var selectedId = SelectedCard?.Id;
            Cards.Clear();
            var paletteRequest = Owner.CardPaletteRequest;
            foreach (var package in Service.Themes)
            {
                if (!PassesCategory(package) || !PassesAppearance(package) || !PassesSearch(package))
                {
                    continue;
                }

                var palette = Service.ComposePalette(package, paletteRequest);
                var card = new ThemeStudioCardViewModel(
                    package,
                    palette,
                    Service.IsFavorite(package.Descriptor.Id),
                    new RelayCommand(() => Owner.PreviewThemeById(IdOf(package))),
                    new RelayCommand(() => Run(() => Owner.ApplyThemeAsync(IdOf(package), commitPreview: true))),
                    new RelayCommand(() => ToggleFavoriteById(IdOf(package))))
                {
                    Width = CardWidth,
                };

                card.OwnerPalette = palette;
                Cards.Add(card);
            }

            SelectedCard = selectedId is null
                ? null
                : Cards.FirstOrDefault(card => string.Equals(card.Id, selectedId, StringComparison.Ordinal));

            OnPropertyChanged(
                nameof(HasCards),
                nameof(IsEmpty),
                nameof(EmptyTitle),
                nameof(EmptyHint),
                nameof(HasActiveFilters),
                nameof(SelectionSummary));
        }
        finally
        {
            _isRefreshing = false;
        }
    }

    /// <inheritdoc />
    public override void OnActivated() => Refresh();

    /// <summary>Projects a theme into the grid (shared with 我的主题 so both use the same card visuals).</summary>
    internal ThemeStudioCardViewModel BuildCard(ThemePackage package)
    {
        var palette = Service.ComposePalette(package, Owner.CardPaletteRequest);
        var card = new ThemeStudioCardViewModel(
            package,
            palette,
            Service.IsFavorite(package.Descriptor.Id),
            new RelayCommand(() => Owner.PreviewThemeById(IdOf(package))),
            new RelayCommand(() => Run(() => Owner.ApplyThemeAsync(IdOf(package), commitPreview: true))),
            new RelayCommand(() => ToggleFavoriteById(IdOf(package))))
        {
            Width = CardWidth,
        };
        card.OwnerPalette = palette;
        return card;
    }

    private void ToggleFavoriteById(string themeId)
    {
        Run(async () =>
        {
            await Owner.ToggleFavoriteByIdAsync(themeId).ConfigureAwait(true);
            Refresh();
        });
    }

    private static string IdOf(ThemePackage package) => package.Descriptor.Id;

    private bool PassesCategory(ThemePackage package) => CategoryKey switch
    {
        "builtin" => package.Descriptor.Kind == ThemeKind.BuiltIn,
        "user" => package.Descriptor.Kind == ThemeKind.User,
        "favorite" => Service.IsFavorite(package.Descriptor.Id),
        _ => true,
    };

    private bool PassesAppearance(ThemePackage package) => AppearanceKey switch
    {
        "light" => package.Descriptor.SupportsLight,
        "dark" => package.Descriptor.SupportsDark,
        "both" => package.Descriptor.SupportsLight && package.Descriptor.SupportsDark,
        "highcontrast" => ThemeStudioContrastAuditor.IsHighContrastFriendly(package),
        _ => true,
    };

    private bool PassesSearch(ThemePackage package)
    {
        var query = SearchText.Trim();
        if (query.Length == 0)
        {
            return true;
        }

        return package.Descriptor.Name.Contains(query, StringComparison.OrdinalIgnoreCase) ||
               (package.Descriptor.Author ?? string.Empty).Contains(query, StringComparison.OrdinalIgnoreCase) ||
               (package.Descriptor.Description ?? string.Empty).Contains(query, StringComparison.OrdinalIgnoreCase) ||
               package.Descriptor.Tags.Any(tag => tag.Contains(query, StringComparison.OrdinalIgnoreCase));
    }

    private void AddCategory(string key, string label)
    {
        var chip = new ThemeStudioFilterChip(key, label, new RelayCommand(() => SelectCategory(key)));
        _categoryChips.Add(chip);
        UpdateCategoryChips();
    }

    private void AddAppearance(string key, string label)
    {
        var chip = new ThemeStudioFilterChip(key, label, new RelayCommand(() => SelectAppearance(key)));
        _appearanceChips.Add(chip);
        UpdateAppearanceChips();
    }

    /// <summary>Selects a category chip (public so keyboard/commands/tests share one path).</summary>
    public void SelectCategory(string key)
    {
        CategoryKey = key;
        UpdateCategoryChips();
        Refresh();
    }

    /// <summary>Selects an appearance filter chip.</summary>
    public void SelectAppearance(string key)
    {
        AppearanceKey = key;
        UpdateAppearanceChips();
        Refresh();
    }

    private void UpdateCategoryChips()
    {
        foreach (var chip in _categoryChips)
        {
            chip.IsOn = string.Equals(chip.Key, CategoryKey, StringComparison.Ordinal);
        }
    }

    private void UpdateAppearanceChips()
    {
        foreach (var chip in _appearanceChips)
        {
            chip.IsOn = string.Equals(chip.Key, AppearanceKey, StringComparison.Ordinal);
        }
    }

    private void ClearFilters()
    {
        SearchText = string.Empty;
        CategoryKey = "all";
        AppearanceKey = "any";
        UpdateCategoryChips();
        UpdateAppearanceChips();
        Refresh();
    }
}

/// <summary>② 我的主题 tab (THEME_STUDIO_SPEC §3.3): 已安装 / 收藏 / 自定义.</summary>
public enum ThemeStudioMyThemesTab
{
    Installed,
    Favorites,
    Custom,
}

/// <summary>③ 我的主题: the three tabs and the per-theme actions (apply/favorite/copy/export/delete).</summary>
public sealed class ThemeStudioMyThemesViewModel : ThemeStudioSectionViewModel
{
    private readonly List<ThemeStudioOption> _tabOptions = new();
    private ThemeStudioMyThemesTab _tab = ThemeStudioMyThemesTab.Installed;
    private ThemeStudioCardViewModel? _selectedItem;

    internal ThemeStudioMyThemesViewModel(ThemeStudioViewModel owner)
        : base(owner, ThemeStudioSection.MyThemes)
    {
        AddTab(ThemeStudioMyThemesTab.Installed, "已安装", "所有可用主题");
        AddTab(ThemeStudioMyThemesTab.Favorites, "收藏", "星标过的主题");
        AddTab(ThemeStudioMyThemesTab.Custom, "自定义", "从主题另存为产生的用户主题");

        ExportCommand = new RelayCommand(() => Run(ExportSelectedAsync));
        DuplicateCommand = new RelayCommand(() => Run(DuplicateSelectedAsync));
        DeleteCommand = new RelayCommand(DeleteSelected);
        ApplyCommand = new RelayCommand(() => Run(ApplySelectedAsync));
        ToggleFavoriteCommand = new RelayCommand(() => Run(ToggleFavoriteAsync));

        // Populated after the AddTab calls (same copy-order rule as the chips above).
        TabOptions = new ObservableCollection<ThemeStudioOption>(_tabOptions);
    }

    public ObservableCollection<ThemeStudioOption> TabOptions { get; }

    public ObservableCollection<ThemeStudioCardViewModel> Items { get; } = new();

    public ICommand ExportCommand { get; }

    public ICommand DuplicateCommand { get; }

    public ICommand DeleteCommand { get; }

    public ICommand ApplyCommand { get; }

    public ICommand ToggleFavoriteCommand { get; }

    public ThemeStudioMyThemesTab Tab
    {
        get => _tab;
        private set => Set(ref _tab, value);
    }

    public ThemeStudioCardViewModel? SelectedItem
    {
        get => _selectedItem;
        set
        {
            if (ReferenceEquals(_selectedItem, value))
            {
                return;
            }

            if (_selectedItem is not null)
            {
                _selectedItem.IsSelected = false;
            }

            _selectedItem = value;
            if (_selectedItem is not null)
            {
                _selectedItem.IsSelected = true;
            }

            OnPropertyChanged(nameof(SelectedItem), nameof(HasSelection), nameof(SelectionLabel), nameof(CanDelete));
        }
    }

    public bool HasSelection => SelectedItem is not null;

    public string SelectionLabel => SelectedItem is null ? "未选中主题" : $"{SelectedItem.Name}（{SelectedItem.Id}）";

    /// <summary>Built-in themes can be copied/saved but never deleted (spec §3.3).</summary>
    public bool CanDelete => SelectedItem is { IsBuiltIn: false };

    public bool HasItems => Items.Count > 0;

    public bool IsEmpty => Items.Count == 0;

    public string EmptyTitle => Tab switch
    {
        ThemeStudioMyThemesTab.Favorites => "还没有收藏的主题",
        ThemeStudioMyThemesTab.Custom => "还没有自定义主题",
        _ => "还没有用户主题",
    };

    public string EmptyHint => Tab switch
    {
        ThemeStudioMyThemesTab.Favorites => "在主题库或此处点击“收藏”即可加入。",
        _ => "在主题编辑器中点击“从当前主题另存为”，或导入一个 .nmtheme。",
    };

    public void SelectTab(ThemeStudioMyThemesTab tab)
    {
        Tab = tab;
        foreach (var option in _tabOptions)
        {
            option.IsSelected = string.Equals(option.Key, tab.ToString(), StringComparison.Ordinal);
        }

        Refresh();
    }

    /// <summary>Escalates the destructive delete through the owner's confirm dialog (二次确认).</summary>
    public void DeleteSelected()
    {
        if (SelectedItem is null)
        {
            return;
        }

        if (SelectedItem.IsBuiltIn)
        {
            Owner.ReportStatus("内置主题不可删除：可复制或另存为自定义主题。");
            return;
        }

        Owner.ShowDeleteThemeDialog(SelectedItem, async () =>
        {
            await Service.DeleteAsync(SelectedItem.Id).ConfigureAwait(true);
            SelectedItem = null;
            Refresh();
        });
    }

    public void Refresh()
    {
        var selectedId = SelectedItem?.Id;
        Items.Clear();
        foreach (var package in Service.Themes)
        {
            if (!PassesTab(package))
            {
                continue;
            }

            Items.Add(Owner.Library.BuildCard(package));
        }

        SelectedItem = selectedId is null
            ? Items.FirstOrDefault()
            : Items.FirstOrDefault(item => string.Equals(item.Id, selectedId, StringComparison.Ordinal)) ?? Items.FirstOrDefault();

        OnPropertyChanged(nameof(HasItems), nameof(IsEmpty), nameof(EmptyTitle), nameof(EmptyHint), nameof(CanDelete));
    }

    /// <inheritdoc />
    public override void OnActivated() => Refresh();

    private bool PassesTab(ThemePackage package) => Tab switch
    {
        ThemeStudioMyThemesTab.Favorites => Service.IsFavorite(package.Descriptor.Id),
        ThemeStudioMyThemesTab.Custom => package.Descriptor.Kind == ThemeKind.User,
        _ => true,
    };

    private async Task ApplySelectedAsync()
    {
        if (SelectedItem is null)
        {
            return;
        }

        await Owner.ApplyThemeAsync(SelectedItem.Id, commitPreview: true).ConfigureAwait(true);
        Refresh();
    }

    private async Task ToggleFavoriteAsync()
    {
        if (SelectedItem is null)
        {
            return;
        }

        await Owner.ToggleFavoriteByIdAsync(SelectedItem.Id).ConfigureAwait(true);
        Refresh();
    }

    private async Task ExportSelectedAsync()
    {
        if (SelectedItem is null)
        {
            return;
        }

        await Owner.ExportThemeAsync(SelectedItem.Id).ConfigureAwait(true);
    }

    private async Task DuplicateSelectedAsync()
    {
        if (SelectedItem is null)
        {
            return;
        }

        var source = SelectedItem;
        Owner.ShowDuplicateThemeDialog(source, async newName =>
        {
            var result = await Service.DuplicateAsync(source.Id, newName).ConfigureAwait(true);
            Owner.ReportStatus(result.Message);
            Refresh();
            Owner.Refresh();
        });
    }

    private void AddTab(ThemeStudioMyThemesTab tab, string label, string description)
    {
        var option = new ThemeStudioOption(
            tab.ToString(),
            label,
            description,
            new RelayCommand(() => SelectTab(tab)));
        option.IsSelected = tab == _tab;
        _tabOptions.Add(option);
    }
}
