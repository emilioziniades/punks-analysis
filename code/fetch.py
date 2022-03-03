import json, math

import requests_cache
from dotenv import load_dotenv

load_dotenv()
from web3.auto.infura import w3

from utils import non_equal_intervals, flatten, parse_result_list
from config import CRYPTOPUNKS_ADDRESS, CRYPTOPUNKS_ABI, CONTRACT_CREATION_BLOCK


def main():
    requests_cache.install_cache("punks")
    with open(CRYPTOPUNKS_ABI) as f:
        abi = json.load(f)
        contract = w3.eth.contract(address=CRYPTOPUNKS_ADDRESS, abi=abi)

        exponent_function = lambda x: (math.e ** (x / 100)) - 1

        # Events contain the following relevant information:
        # 	Transfers: to, from, punkIndex, blockheight
        # 	Assigns: to, punkIndex, blockheight
        # 	Buys: to, from, punkIndex, value,blockheight

        transfer_logs = get_punks_logs(contract.events.PunkTransfer, 160)
        buy_logs = get_punks_logs(contract.events.PunkBought, 160)

        # exponent_function ensures that intervals are narrower at start of contract life,
        # when there were many more assigns ocurring
        assign_logs = get_punks_logs(contract.events.Assign, 700, exponent_function)

        save_punks_logs(transfer_logs, "../data/transfers.json")
        save_punks_logs(buy_logs, "../data/buys.json")
        save_punks_logs(assign_logs, "../data/assigns.json")


def get_punks_logs(filter_object, num_intervals, transform_function=lambda x: x):
    current_block = w3.eth.blockNumber
    query_intervals = non_equal_intervals(
        CONTRACT_CREATION_BLOCK, current_block, num_intervals, transform_function
    )
    # query_intervals = [[12370609, 12419122]]  # for testing purposes
    payload = []
    for count, [start, end] in enumerate(query_intervals):
        s = hex(round(start))
        e = hex(round(end))
        print(count, start, end)
        current_filter = filter_object.createFilter(fromBlock=s, toBlock=e)
        entries = current_filter.get_all_entries()
        payload.append(entries)

    # pprint(payload)
    # breakpoint()
    return payload


def save_punks_logs(logs, filename):
    flattened_results = flatten(logs)
    parsed_results = parse_result_list(flattened_results)
    with open(filename, "w") as f:
        json.dump(parsed_results, f)
        print(parsed_results)
        print(len(parsed_results))


if __name__ == "__main__":
    main()
