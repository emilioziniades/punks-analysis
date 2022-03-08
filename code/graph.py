import json, os
from typing import List, Tuple

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

from config import CONTRACT_CREATION_BLOCK, PROJECT_DIR, RESEARCH_END_BLOCK


def main() -> None:
    if not os.path.exists(f"{PROJECT_DIR}/figures"):
        os.mkdir(f"{PROJECT_DIR}/figures")

    save_examples()

    start = CONTRACT_CREATION_BLOCK
    end = RESEARCH_END_BLOCK

    to_plot = [
        # Example 1: Equality
        (
            "Example 1: Equality",
            ["example_equality"],
            "example_1",
            "Punks",
            [True, False, False, "Equality"],
        ),
        # Example 2 :  inequality with five people
        (
            "Example 2: Inequality",
            ["example_inequality"],
            "example_2",
            "Punks",
            [True, True, False, "Inequality"],
        ),
        # Figure 1: Distribution of punks after assign and now
        (
            "Figure 1: Distribution of punks after all claimed, vs now",
            ["balances_after_assigns", "balances"],
            "figure_1",
            "Punks",
            [False, True, True, ""],
        ),
        # Figure 2: Distribution of punks over time
        (
            "Figure 2: Distribution of punks over time",
            ["balances_punks_20"],
            "figure_2",
            "Punks",
            [False, True, True, ""],
        ),
        # Figure 3: Distribution of ETH value of punks over time
        (
            "Figure 3: Distribution of ETH value of punks over time",
            ["balances_eth_20"],
            "figure_3",
            "ETH Value of Punks",
            [False, True, True, ""],
        ),
    ]

    for (title, infiles, outfile, ylabel, options) in to_plot:
        dots, equality, progress_colour, custom_label = options
        make_plot(
            infiles,
            outfile,
            start,
            end,
            title,
            ylabel,
            dots,
            equality,
            progress_colour,
            custom_label,
        )


def make_plot(
    infiles: List[str],
    outfile: str,
    start: int,
    end: int,
    title: str,
    ylab: str,
    dots: bool = False,
    equality: bool = True,
    progress_colour: bool = True,
    custom_label: str = "",
):
    print(f"Graphing {title}")
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.xlabel("Cumulative Percent of Addresses")
    plt.ylabel(f"Cumulative Percent of {ylab}")
    plt.title(title)
    plt.grid(True)
    if equality:
        plot_equality()

    for file in infiles:
        with open(f"{PROJECT_DIR}/data/{file}.json") as f:
            data_entries = json.load(f)
        for entry in data_entries:
            if len(entry["balances"]) <= 2:
                continue

            if progress_colour:
                progress = (entry["block"] - start) / (end - start)
                assert 0 <= progress <= 1
                colour = colour_fade("#42378F", "#F53844", progress)
            else:
                colour = "black"

            if custom_label == "":
                label = f"{entry['date']} (n = {len(entry['balances']) -1}, gini = {entry['gini']:.3f})"
            else:
                label = custom_label

            x, y = calculate_cumulatives(entry["balances"])
            plt.plot(x, y, color=colour, label=label)
            if dots:
                plt.scatter(x, y, color=colour)

    plt.legend(loc="center right", bbox_to_anchor=(1.7, 0.5))
    plt.savefig(f"{PROJECT_DIR}/figures/{outfile}", bbox_inches="tight", dpi=200)
    plt.cla()


def calculate_cumulatives(balances: List[int]) -> Tuple[List, List]:

    df = pd.DataFrame({"balances": balances})

    total_balance = df["balances"].sum()
    df["%_of_total_balance"] = df["balances"] / total_balance
    df["cumulative_%_of_balance"] = df["%_of_total_balance"].cumsum()

    total_n = df.shape[0]
    df["%_of_total_n"] = 1 / total_n
    df["cumulative_%_of_n"] = df["%_of_total_n"].cumsum()

    # pd.set_option("display.max_columns", None)

    x = list(df["cumulative_%_of_n"])
    y = list(df["cumulative_%_of_balance"])
    x.insert(0, 0)
    y.insert(0, 0)
    return x, y


def plot_equality() -> None:
    x, y = calculate_cumulatives([1 for _ in range(100)])
    plt.plot(x, y, color="black", linestyle="dashed", label="Equality")


# fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
def colour_fade(c1: str, c2: str, mix: float) -> str:
    assert 0 <= mix <= 1
    colour_1 = np.array(mpl.colors.to_rgb(c1))
    colour_2 = np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1 - mix) * colour_1 + mix * colour_2)


def save_examples() -> None:
    examples = [
        ([1, 1, 1, 1, 1], "example_equality"),
        ([1, 1, 1, 1, 6], "example_inequality"),
    ]

    for balance, filename in examples:
        with open(f"{PROJECT_DIR}/data/{filename}.json", "w") as f:
            eg_data = [{"block": 0, "balances": balance}]
            json.dump(eg_data, f)


if __name__ == "__main__":
    main()
