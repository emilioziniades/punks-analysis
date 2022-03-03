import json, pdb
from collections import defaultdict
from pprint import pprint

from config import CRYPTOPUNKS_ADDRESS, CRYPTOPUNKS_ABI, CONTRACT_CREATION_BLOCK


def main():
    data_files = [
        "../data/assigns.json",
        "../data/transfers.json",  # neg numbers
        "../data/buys.json",
    ]

    newfiles = parse_logs(data_files)
    final_balance = reconcile_logs(newfiles)
    balances = sorted([v for k, v in final_balance.items()])
    breakpoint()


def reconcile_logs(balance_data_files):

    most_recent_balances = {}
    most_recent_balances[CRYPTOPUNKS_ADDRESS] = 10000

    for balance_data in balance_data_files:
        with open(balance_data, "r") as f:
            balances = json.load(f)
            for (account, balance) in balances.items():

                if most_recent_balances.get(account):
                    most_recent_balances[account] += balance
                else:
                    most_recent_balances.update({account: balance})

    return most_recent_balances


def parse_logs(data_files):
    filenames = []
    for data in data_files:
        with open(data, "r") as f:
            logs = json.load(f)
            clean_logs = _count_punks_by_owner(logs)
            current_filename = data[:-4] + "_balances.json"
            filenames.append(current_filename)
            with open(current_filename, "w") as g:
                json.dump(clean_logs, g)
                # print(clean_logs)

    return filenames


def _count_punks_by_owner(logs):

    balances = defaultdict(lambda: 0)
    # balances[CRYPTOPUNKS_ADDRESS] = 10000
    print(len(logs))
    pprint(logs[544:546])
    for log in logs:

        block_number = log["blockNumber"]
        punk_receiver = log.get("args").get("to") or log.get("args").get("toAddress")
        punk_sender = (
            log.get("args").get("from")
            or log.get("args").get("fromAddress")
            or CRYPTOPUNKS_ADDRESS
        )
        punk_index = log["args"]["punkIndex"]
        value = log.get("args").get("value") or "Not given"
        event_type = log["event"]

        balances[punk_sender] -= 1
        balances[punk_receiver] += 1

    return balances


if __name__ == "__main__":
    main()
