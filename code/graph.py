import json
from typing import List

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

from config import CONTRACT_CREATION_BLOCK
from utils import project_dir, gini


def main() -> None:

    start = CONTRACT_CREATION_BLOCK
    # TODO: don't hard code the end block
    end = 14325807

    to_plot = [
        # Figure 1: Distribution of punks after assign and now
        (
            "Figure 1: Distribution of punks after all claimed, vs now",
            ["balances_after_assigns", "balances"],
            "figure_1",
            "Punks",
        ),
        # Figure 2: Distribution of punks over time
        (
            "Figure 2: Distribution of punks over time",
            ["balances_punks_20"],
            "figure_2",
            "Punks",
        ),
        # Figure 3: Distribution of ETH value of punks over time
        (
            "Figure 3: Distribution of ETH value of punks over time",
            ["balances_eth_20"],
            "figure_3",
            "ETH Value of Punks",
        ),
    ]

    for (title, infiles, outfile, ylabel) in to_plot:
        make_plot(infiles, outfile, start, end, title, ylabel)


def make_plot(
    infiles: List[str], outfile: str, start: int, end: int, title: str, ylab: str
):
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.xlabel("Cumulative Percent of Addresses")
    plt.ylabel(f"Cumulative Percent of {ylab}")
    plt.title(title)
    plt.grid(True)
    plot_equality()
    for file in infiles:
        plot_from_file(file, start, end)
    plt.legend(loc="center right", bbox_to_anchor=(1.6, 0.5))
    plt.savefig(f"../figures/{outfile}", bbox_inches="tight", dpi=200)
    plt.cla()


def plot_from_file(filename: str, start: int, end: int):
    with open(f"{project_dir()}/data/{filename}.json") as f:
        data = json.load(f)
    for entry in data:
        if len(entry["balances"]) <= 2:
            continue
        progress = (entry["block"] - start) / (end - start)
        assert 0 <= progress <= 1
        colour = colour_fade("#42378F", "#F53844", progress)
        label = f"Block {entry['block']:,} (gini = {gini(entry['balances']):.3f})"
        plot_balance(entry["balances"], colour, label)


def plot_balance(balances: List[int], colour: str, label: str) -> None:

    df = pd.DataFrame({"balances": balances})

    total_balance = df["balances"].sum()
    df["%_of_total_balance"] = df["balances"] / total_balance
    df["cumulative_%_of_balance"] = df["%_of_total_balance"].cumsum()

    total_n = df.shape[0]
    df["%_of_total_n"] = 1 / total_n
    df["cumulative_%_of_n"] = df["%_of_total_n"].cumsum()

    # pd.set_option("display.max_columns", None)

    x = df["cumulative_%_of_n"]
    y = df["cumulative_%_of_balance"]

    plt.plot(x, y, color=colour, label=label)


def plot_equality() -> None:
    plot_balance([1 for _ in range(100)], "black", "Equality")


# fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
def colour_fade(c1: str, c2: str, mix: float) -> str:
    assert 0 <= mix <= 1
    colour_1 = np.array(mpl.colors.to_rgb(c1))
    colour_2 = np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1 - mix) * colour_1 + mix * colour_2)


if __name__ == "__main__":
    main()
