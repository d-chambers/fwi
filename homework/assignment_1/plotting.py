"""
Utilties for plotting.
"""



def plot_simulations(results, axes, fig, cols_to_plot, max_y=40):
    """
    Plot the simulations.

    Parameters
    ----------
    results
        The results dataframe
    axes
        The axes to plot
    """
    for ax, col in zip(axes, cols_to_plot):
        ser = results[col]
        ax.plot(ser.index, ser)
        ax.ticklabel_format(axis='Y', scilimits=(0, 1))
        ax.set_ylim(0, max([max_y, ser.max()]))

    fig.supylabel('Temperature (k)')
    fig.supxlabel('Distance (m)')
    return fig, axes