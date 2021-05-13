import json, pdb
from collections import defaultdict
from pprint import pprint

def main():
        with open('result.txt', 'r') as f:
            logs = json.load(f)
            result = _countPunksByOwner(logs)
            pprint(result)
            with open('balances.txt', 'w') as g:
                json.dump(result, g)


def _countPunksByOwner(logs):

    balances = defaultdict(lambda: 0)

    for log in logs:
        [punkSender, punkReceiver, _] = log['args'].values()
        balances[punkSender] -= 1
        balances[punkReceiver] += 1

    return balances


if __name__ == '__main__':
    main()