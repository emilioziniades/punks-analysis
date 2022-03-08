import json, os
from typing import Any, Callable

from dotenv import load_dotenv

load_dotenv()

from web3.auto.infura import w3

from utils import non_equal_intervals, to_dict, exponential, linear, print_progress
from config import (
    CRYPTOPUNKS_ADDRESS,
    CRYPTOPUNKS_ABI,
    CONTRACT_CREATION_BLOCK,
    RESEARCH_END_BLOCK,
    PROJECT_DIR,
    NUMBER_OF_INTERVALS,
)


def main():

    if not os.path.exists(f"{PROJECT_DIR}/data"):
        os.mkdir(f"{PROJECT_DIR}/data")
    with open(CRYPTOPUNKS_ABI) as f:
        abi = json.load(f)
        contract = w3.eth.contract(address=CRYPTOPUNKS_ADDRESS, abi=abi)

        to_fetch = [
            (contract.events.Transfer, "transfers", NUMBER_OF_INTERVALS, linear),
            (
                contract.events.PunkTransfer,
                "punk_transfers",
                NUMBER_OF_INTERVALS,
                linear,
            ),
            (
                contract.events.PunkBidEntered,
                "bids_entered",
                NUMBER_OF_INTERVALS,
                linear,
            ),
            (
                contract.events.PunkBidWithdrawn,
                "bids_withdrawn",
                NUMBER_OF_INTERVALS,
                linear,
            ),
            (contract.events.PunkBought, "buys", NUMBER_OF_INTERVALS, linear),
            # exponential transform ensures that intervals are narrower at start of contract life, when all assigns occur
            (contract.events.Assign, "assigns", NUMBER_OF_INTERVALS, exponential),
        ]

        for (event, name, n_intervals, transformation) in to_fetch:
            get_and_save_punks_logs(event, name, n_intervals, transformation)


def get_and_save_punks_logs(
    event: Any,
    name: str,
    n_intervals: int,
    transformation: Callable[[float], float] = linear,
) -> None:
    print(f"fetching {name} in {n_intervals} intervals...")

    # generate intervals of (possibly non-equal) size
    query_intervals = non_equal_intervals(
        CONTRACT_CREATION_BLOCK, RESEARCH_END_BLOCK, n_intervals, transformation
    )

    # Fetch event data from smart contract via filters
    # RPC calls: eth_newFilter and eth_getFilterLogs
    payload = []
    for count, [start, end] in enumerate(query_intervals):
        s = hex(round(start))
        e = hex(round(end))
        print_progress(count + 1, n_intervals)
        entries = event.createFilter(fromBlock=s, toBlock=e).get_all_entries()
        payload += entries

    # convert AttributeDict into normal dict and save events to json
    dict_payload = [to_dict(i) for i in payload]
    with open(f"{PROJECT_DIR}/data/event_{name}.json", "w") as f:
        json.dump(dict_payload, f)
        print(len(dict_payload))


if __name__ == "__main__":
    main()
