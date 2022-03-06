import json
from collections import defaultdict
from pprint import pprint
from typing import Dict, List, Tuple
from operator import itemgetter

from web3 import Web3
from web3.types import EventData

from config import CRYPTOPUNKS_ADDRESS, PROJECT_DIR
from utils import gini, project_dir


def main() -> None:

    all_data = [
        "assigns",
        "transfers",
        "punk_transfers",
        "buys",
        "bids_entered",
        "bids_withdrawn",
    ]

    # punk balances latest block
    save_balances(all_data, "balances", False)

    # punk balances after all punks claimed
    save_balances(["assigns"], "balances_after_assigns", False)

    # punk balances over time (20 periods)
    save_balances_intervals(all_data, "balances_punks_20", 20, False)

    # ETH balances over time (20 periods)
    save_balances_intervals(all_data, "balances_eth_20", 20, True)


def save_balances_intervals(
    data_files: List[str], outfile: str, n_intervals: int, eth_balances: bool = True
) -> None:
    to_dump = []

    events = merge_events(data_files)
    start_block, end_block = events[0]["blockNumber"], events[-1]["blockNumber"]
    length = end_block - start_block
    interval_length = length / n_intervals

    for i in range(n_intervals, -1, -1):
        until_block = end_block - round(i * interval_length)
        bal = determine_balances(events, eth_balances, until_block)
        to_dump.append({"block": until_block, "balances": bal})

    with open(f"{PROJECT_DIR}/data/{outfile}.json", "w") as f:
        json.dump(to_dump, f)


def save_balances(
    data_files: List[str], outfile: str, eth_balances: bool = True
) -> None:
    events = merge_events(data_files)
    balances = determine_balances(events, eth_balances)

    to_dump = [{"block": events[-1]["blockNumber"], "balances": balances}]

    with open(f"{PROJECT_DIR}/data/{outfile}.json", "w") as f:
        json.dump(to_dump, f)


def merge_events(event_files: list[str]) -> list[EventData]:
    all_events: list[EventData] = []

    # combine assigns, transfers and buys into single list of events
    for filename in event_files:
        with open(f"{PROJECT_DIR}/data/{filename}.json", "r") as file:
            data = json.load(file)
            all_events += data

    # cleaning
    for i, event in enumerate(all_events):
        # change "fromAddress" to "from" for PunkBought events
        all_events[i]["args"] = {
            "from" if k == "fromAddress" else k: v for k, v in event["args"].items()
        }
        # change "toAddress" to "to" for PunkBought events
        all_events[i]["args"] = {
            "to" if k == "toAddress" else k: v for k, v in event["args"].items()
        }

        # add "from" = CRYPTOPUNKS_ADDRESS for Assign events
        if "from" not in event["args"] and event["event"] == "Assign":
            all_events[i]["args"]["from"] = CRYPTOPUNKS_ADDRESS

    return sorted(all_events, key=itemgetter("blockNumber", "logIndex"))


def determine_balances(
    events: List[EventData], eth_balance: bool = True, until_block: int = None
) -> List[int]:
    owner_to_punks: Dict[str, List[int]] = defaultdict(lambda: [])
    owner_to_punks[CRYPTOPUNKS_ADDRESS] = [i for i in range(10000)]

    bids: Dict[int, List[Tuple[int, str]]] = defaultdict(lambda: [])
    punk_prices = defaultdict(lambda: 0)

    for i, event in enumerate(events):
        receiver = event["args"]["to"] if "to" in event["args"] else "0x123456"
        sender = event["args"]["from"]
        block_number = event["blockNumber"]
        punk_index = event["args"]["punkIndex"] if "punkIndex" in event["args"] else -1
        value = event["args"]["value"] if "value" in event["args"] else -1
        event_type = event["event"]

        if until_block and block_number > until_block:
            break

        # we only need Transfer events to determine to address of PunkBought event
        if event_type == "Transfer":
            continue
        # BidEntered and BidWithdrawn are simply used to keep track of bids
        elif event_type == "PunkBidEntered":
            bids[punk_index].append((value, sender))
            continue
        elif event_type == "PunkBidWithdrawn":
            assert (value, sender) in bids[punk_index]
            bids[punk_index].remove((value, sender))
            continue

        # must determine reciever and value manually
        if (
            receiver == "0x0000000000000000000000000000000000000000"
            and value == 0
            and event_type == "PunkBought"
        ):
            # since events are chronological, previous event will always be the Transfer
            # event corresponding to the PunkBought event
            transfer_event = events[i - 1]
            assert transfer_event["event"] == "Transfer"
            assert block_number == transfer_event["blockNumber"]
            assert sender == transfer_event["args"]["from"]
            receiver = transfer_event["args"]["to"]

            # will take the value to be the higest bid from the person who bought the punk

            bids_from_receiver = filter(
                lambda x: True if x[1] == receiver else False, bids[punk_index]
            )
            # value is highest bid from person who bought punk
            value = sorted(bids_from_receiver, reverse=True)[0][0]

        if event_type == "PunkBought":
            # update latest sale price of punk
            punk_prices[punk_index] = value

        assert punk_index in owner_to_punks[sender]
        owner_to_punks[sender].remove(punk_index)
        owner_to_punks[receiver].append(punk_index)

    # Manual changes
    # Remove price of 9998, as this was not a legitimate purchase (https://twitter.com/larvalabs/status/1453903818308083720)
    punk_prices[9998] = 0
    # Drop all wrapped punks, which belong to this address: 0xb7F7F6C52F2e2fdb1963Eab30438024864c313F6
    try:
        del owner_to_punks["0xb7F7F6C52F2e2fdb1963Eab30438024864c313F6"]
    except KeyError:
        print("Tried to delete wrapped punks address, but address not found")

    if eth_balance:
        balances = {
            k: sum(map(lambda x: punk_prices[x], v)) for k, v in owner_to_punks.items()
        }
    else:
        balances = {k: len(v) for k, v in owner_to_punks.items()}
    balances_list = sorted([v for v in balances.values() if v > 0])

    return balances_list


if __name__ == "__main__":
    main()
