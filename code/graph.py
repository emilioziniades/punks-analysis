import json, os
from typing import List, Tuple

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from config import PROJECT_DIR


def main() -> None:
    if not os.path.exists(f"{PROJECT_DIR}/figures"):
        os.mkdir(f"{PROJECT_DIR}/figures")

    save_examples()

    to_plot = [
        # Example 1: Equality
        (
            "Example 1: Equality",
            ["example_equality"],
            "example_1",
            "Punks",
            [True, False, "Equality", ["black"]],
        ),
        # # Example 2 :  inequality with five people
        (
            "Example 2: Inequality",
            ["example_inequality"],
            "example_2",
            "Punks",
            [True, True, "Inequality", ["black"]],
        ),
        # # Figure 1: Distribution of punks after assign and now
        (
            "Figure 1: Distribution of Punks after all claimed, vs now",
            ["balances_after_assigns", "balances"],
            "figure_1",
            "Punks",
            [False, True, "", ["#D47162", "#7C376D"]],
        ),
        # Figure 2: Distribution of punks over time
        (
            "Figure 2: Distribution of Punks over time",
            ["balances_punks_20"],
            "figure_2",
            "Punks",
            [False, True, "", None],
        ),
        # # Figure 3: Distribution of ETH value of punks over time
        (
            "Figure 3: Distribution of ETH value of Punks over time",
            ["balances_eth_20"],
            "figure_3",
            "ETH Value of Punks",
            [False, True, "", None],
        ),
    ]

    for (
        title,
        infiles,
        outfile,
        ylabel,
        options,
    ) in to_plot:
        dots, equality, custom_label, colours = options
        make_plot(
            infiles,
            outfile,
            title,
            ylabel,
            dots,
            equality,
            colours,
            custom_label,
        )


def make_plot(
    infiles: List[str],
    outfile: str,
    title: str,
    ylab: str,
    dots: bool = False,
    equality: bool = True,
    custom_colours: List[Tuple[float, float, float]] = None,
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

    # gather all plots to graph
    plots = []
    for file in infiles:
        with open(f"{PROJECT_DIR}/data/{file}.json") as f:
            data_entries = json.load(f)
        for entry in data_entries:
            plots.append(entry)

    # determine colours to use
    if custom_colours:
        assert len(custom_colours) == len(plots)
        colours = custom_colours
    else:
        colours = sns.color_palette("flare_r", n_colors=len(plots))

    # plot each entry
    for i, plot in enumerate(plots):
        if len(plot["balances"]) <= 2:
            continue

        if custom_label == "":
            label = f"{plot['date']} (n = {len(plot['balances']) -1}, gini = {plot['gini']:.3f})"
            label_box_x_width = 1.7
        else:
            label = custom_label
            label_box_x_width = 1.3

        x, y = calculate_cumulatives(plot["balances"])

        plt.plot(x, y, c=colours[i], label=label, alpha=0.8)
        if dots:
            plt.scatter(x, y, c=colours[i])

    plt.legend(loc="center right", bbox_to_anchor=(label_box_x_width, 0.5))
    plt.savefig(f"{PROJECT_DIR}/figures/{outfile}", bbox_inches="tight", dpi=200)
    plt.clf()


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
    plt.plot(x, y, color="black", linestyle="--", label="Equality")


def save_examples() -> None:
    examples = [
        ([1, 1, 1, 1, 1], "example_equality"),
        ([1, 1, 1, 1, 6], "example_inequality"),
    ]

    for balance, filename in examples:
        eg_data = [{"block": 0, "balances": balance}]
        with open(f"{PROJECT_DIR}/data/{filename}.json", "w") as f:
            json.dump(eg_data, f)


if __name__ == "__main__":
    main()
