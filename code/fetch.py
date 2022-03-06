import json

from typing import Any, Callable

from dotenv import load_dotenv

load_dotenv()
from web3.auto.infura import w3

from utils import non_equal_intervals, to_dict, project_dir, exponential, linear
from config import CRYPTOPUNKS_ADDRESS, CRYPTOPUNKS_ABI, CONTRACT_CREATION_BLOCK


def main():
    with open(CRYPTOPUNKS_ABI) as f:
        abi = json.load(f)
        contract = w3.eth.contract(address=CRYPTOPUNKS_ADDRESS, abi=abi)

        to_fetch = [
            (contract.events.Transfer, "transfers", 250, linear),
            (contract.events.PunkTransfer, "punk_transfers", 250, linear),
            (contract.events.PunkBidEntered, "bids_entered", 600, linear),
            (contract.events.PunkBidWithdrawn, "bids_withdrawn", 600, linear),
            (contract.events.PunkBought, "buys", 250, linear),
            # exponential transform ensures that intervals are narrower at start of contract life, when all assigns occur
            (contract.events.Assign, "assigns", 500, exponential),
        ]

        for (event, name, n_intervals, transformation) in to_fetch:
            get_and_save_punks_logs(event, name, n_intervals, transformation)


def get_and_save_punks_logs(
    event: Any,
    name: str,
    n_intervals: int,
    transformation: Callable[[float], float] = linear,
) -> None:
    print(name)

    # RPC call: eth_blockNumber
    current_block = w3.eth.blockNumber

    # generate intervals of (possibly non-equal) size
    query_intervals = non_equal_intervals(
        CONTRACT_CREATION_BLOCK, current_block, n_intervals, transformation
    )

    # Fetch event data from smart contract via filters
    # RPC calls: eth_newFilter and eth_getFilterLogs
    payload = []
    for count, [start, end] in enumerate(query_intervals):
        s = hex(round(start))
        e = hex(round(end))
        print(count, start, end)
        entries = event.createFilter(fromBlock=s, toBlock=e).get_all_entries()
        payload += entries

    # convert AttributeDict into normal dict and save events to json
    dict_payload = [to_dict(i) for i in payload]
    with open(f"{project_dir()}/data/{name}.json", "w") as f:
        json.dump(dict_payload, f)
        print(len(dict_payload))


if __name__ == "__main__":
    main()
