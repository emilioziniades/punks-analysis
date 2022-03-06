import json
from typing import List

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

from config import CONTRACT_CREATION_BLOCK
from utils import project_dir


def main() -> None:

    start = CONTRACT_CREATION_BLOCK
    # TODO: don't hard code the end block
    end = 14325807

    equality = [50 for _ in range(100)]
    plot_balance(equality, "black")

    # Figure 1: Distribution of punks after assign and now
    # plot_from_file("balances_after_assigns", start, end)
    # plot_from_file("balances", start, end)

    # Figure 2: Distribution of punks over time
    # plot_all_from_file("balances_punks_20", start, end)

    # Figure 3: Distribution of ETH value of punks over time
    plot_all_from_file("balances_eth_20", start, end)

    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.show()


def plot_all_from_file(filename: str, start: int, end: int):
    with open(f"{project_dir()}/data/{filename}.json") as f:
        data = json.load(f)
    for entry in data:
        if len(entry["balances"]) <= 2:
            continue
        progress = (entry["block"] - start) / (end - start)
        assert 0 <= progress <= 1
        colour = colour_fade("blue", "red", progress)
        plot_balance(entry["balances"], colour)


def plot_from_file(filename: str, start: int, end: int):
    with open(f"{project_dir()}/data/{filename}.json") as f:
        data = json.load(f)
    assert data.get("block") and data.get("balances")
    progress = (data["block"] - start) / (end - start)
    colour = colour_fade("blue", "red", progress)
    assert 0 <= progress <= 1
    plot_balance(data["balances"], colour)


def plot_balance(balances: List[int], colour: str) -> None:

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

    plt.plot(x, y, color=colour)


# fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
def colour_fade(c1: str, c2: str, mix: float) -> str:
    assert 0 <= mix <= 1
    colour_1 = np.array(mpl.colors.to_rgb(c1))
    colour_2 = np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1 - mix) * colour_1 + mix * colour_2)


if __name__ == "__main__":
    main()
