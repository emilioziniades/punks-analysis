import math
from inspect import getsourcefile
from os.path import abspath, split
from typing import List, Callable

from web3.datastructures import AttributeDict


def non_equal_intervals(
    start: int, end: int, parts: int, transform_formula: Callable[[float], float]
) -> List[List[int]]:
    duration = end - start
    transformed_array = list(map(transform_formula, range(parts + 1)))
    squash_factor = duration / transformed_array[-1]
    squash = lambda x: x * squash_factor
    squashed_array = list(map(squash, transformed_array))

    intervals = []
    for i, _ in enumerate(squashed_array):
        try:
            s = squashed_array[i] + start
            e = squashed_array[i + 1] + start
            if i == 0:
                intervals.append([round(s), round(e)])
            else:
                intervals.append([round(s) + 1, round(e)])

        except IndexError:
            continue

    print("\n")
    print(intervals)
    print("\n")
    print([end - start for (start, end) in intervals])
    print("\n")
    return intervals


def intervals(start: int, end: int, parts: int):
    # Breaks up an number into equal sized intervals
    return non_equal_intervals(start, end, parts, lambda x: x)


def to_dict(dict_to_parse: AttributeDict) -> dict:
    # convert any 'AttributeDict' type found to 'dict'
    parsed_dict = dict(dict_to_parse)
    for key, val in parsed_dict.items():
        # check for nested dict structures to iterate through
        if "dict" in str(type(val)).lower():
            parsed_dict[key] = to_dict(val)
            # convert 'HexBytes' type to 'str'
        elif "HexBytes" in str(type(val)):
            parsed_dict[key] = val.hex()
    return parsed_dict


def project_dir() -> str:
    file_location = abspath(getsourcefile(lambda: 0))
    code_dir, _ = split(file_location)
    project_dir, _ = split(code_dir)
    return project_dir


def gini(balances: List[int]) -> float:
    n = len(balances)
    mean = sum(balances) / n
    differences = sum([abs(i - j) for i in balances for j in balances])
    mean_differences = differences / n**2
    relative_mean_difference = mean_differences / mean

    return relative_mean_difference / 2


def exponential(x: float) -> float:
    return (math.e ** (x / 50)) - 1


def linear(x: float) -> float:
    return x
