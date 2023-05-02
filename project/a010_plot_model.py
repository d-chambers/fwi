"""
Run the true model.
"""
import local
import matplotlib.pyplot as plt
import specster as sp

if __name__ == "__main__":
    import specster as sp

    control = sp.Control2d().copy("outputs/base")  # loads the base example
    control.plot_geometry(kernel=["vs", "vp"])  # plots VP and VS

    plt.savefig(local.basic_plot_path, bbox_inches="tight", pad_inches=0)
