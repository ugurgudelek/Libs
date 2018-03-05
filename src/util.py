import math
import matplotlib.pyplot as plt





def subplot(dictionary, xname, yname, ncols=None, nrows=None):
    """

    Args:
        self:
        dictionary:
        xname:
        yname:
        ncols:

    Returns:

    """

    if nrows is None:
        if ncols is None:
            raise Exception('Please enter nrows or ncols only, not both')
        nrows = int(math.ceil(len(dictionary) / ncols))
    if ncols is None:
        if nrows is None:
            raise Exception('Please enter nrows or ncols only, not both')
        ncols = int(math.ceil(len(dictionary) / nrows))

    fig, axs = plt.subplots(nrows, ncols, sharex=True, sharey=True)
    axs = axs.reshape(nrows, ncols)
    for i, (name, reading) in enumerate(dictionary.items()):

        x = reading[xname]
        y = reading[yname]
        axs[i // ncols, i % ncols].plot(x, y)
        axs[i // ncols, i % ncols].set_title(name)
        axs[i // ncols, i % ncols].grid( which='both', color='r', linestyle='--', linewidth=0.5)


    plt.show()