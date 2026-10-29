using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace NewManga.App.ViewModels.V2.Studio;

/// <summary>
/// V11R-B-3: minimal observable base for the Studio view models. The repo has no shared MVVM base
/// (the legacy VMs re-implement INPC each time); the Studio area keeps one local copy instead of
/// introducing a cross-area dependency while the V2 shell is still being built by another owner.
/// </summary>
public abstract class StudioObservable : INotifyPropertyChanged
{
    public event PropertyChangedEventHandler? PropertyChanged;

    protected bool Set<T>(ref T field, T value, [CallerMemberName] string? name = null)
    {
        if (EqualityComparer<T>.Default.Equals(field, value))
        {
            return false;
        }

        field = value;
        Raise(name);
        return true;
    }

    protected void Raise([CallerMemberName] string? name = null) =>
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
}
