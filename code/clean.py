import json
from collections import defaultdict
from pprint import pprint
from typing import Dict, List, Tuple
from operator import itemgetter

from web3.types import EventData

from config import CRYPTOPUNKS_ADDRESS
from utils import gini


def main():
    data_files = [
        "../data/assigns.json",
        "../data/transfers.json",
        "../data/punk_transfers.json",
        "../data/buys.json",
        # "../data/bids.json",
    ]

    events = unify_events(data_files)
    balances = determine_balances(events)
    balances_list = sorted([v for v in balances.values()])
    pprint(balances)
    print(balances_list)
    print(sum([i for i in balances_list if i < 0]))
    print(gini([i for i in balances_list if i != 0]))


def unify_events(event_files: list[str]) -> list[EventData]:
    all_events: list[EventData] = []

    # combine assigns, transfers and buys into single list of events
    for filename in event_files:
        with open(filename, "r") as file:
            data = json.load(file)
            # pprint(data[0])
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
        if "from" not in event["args"]:
            all_events[i]["args"]["from"] = CRYPTOPUNKS_ADDRESS

    return sorted(all_events, key=itemgetter("blockNumber", "logIndex"))


def determine_balances(events: list[EventData]) -> Dict[str, int]:
    balances: Dict[str, int] = defaultdict(lambda: 0)
    # bids: Dict[int, List[Tuple[int, str]]] = {}

    balances[CRYPTOPUNKS_ADDRESS] = 10000
    for i, event in enumerate(events):
        receiver = event["args"]["to"]
        sender = event["args"]["from"]
        block_number = event["blockNumber"]
        punk_index = event["args"]["punkIndex"] if "punkIndex" in event["args"] else -1
        value = event["args"]["value"] if "value" in event["args"] else -1
        event_type = event["event"]

        # if event_type != "Assign":
        #     break

        # if event_type == "PunkBidEntered":
        #     bids[punk_index].append((value, sender))

        # we only need Transfer events to determine to address of PunkBought event
        if event_type == "Transfer":
            continue

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

        assert balances[sender] > 0
        balances[sender] -= 1
        balances[receiver] += 1

    return balances


if __name__ == "__main__":
    main()
