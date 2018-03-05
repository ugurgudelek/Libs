import math
import matplotlib.pyplot as plt


def subplot(dictionary, xname, yname, ncols=3):
    """

    Args:
        self:
        dictionary:
        xname:
        yname:
        ncols:

    Returns:

    """
    nrows = int(math.ceil(len(dictionary) / ncols))

    fig, axs = plt.subplots(nrows, ncols, sharex=True, sharey=True)
    axs = axs.reshape(nrows, ncols)
    for i, (name, reading) in enumerate(dictionary.items()):

        x = reading[xname]
        y = reading[yname]
        axs[i // 3, i % 3].plot(x, y)
        axs[i // 3, i % 3].set_title(name)
    plt.show()