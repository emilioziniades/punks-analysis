import json, pdb
from collections import defaultdict
from pprint import pprint

def main():
    data_files = [
        '../data/assigns.txt',
        '../data/transfers.txt', #neg numbers
        '../data/buys.txt'
        ]

    newfiles = parse_logs(data_files)
    final_balance = reconcile_logs(newfiles)
    balances = sorted([v for k,v in final_balance.items()])
    pdb.set_trace()


def reconcile_logs(balance_data_files):

    punksMarketAddress = '0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB'
    most_recent_balances = {}
    most_recent_balances[punksMarketAddress] = 10000

    for balance_data in balance_data_files:
        with open(balance_data, 'r') as f:
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
        with open(data, 'r') as f:
            logs = json.load(f)
            clean_logs = _countPunksByOwner(logs)
            current_filename = data[:-4] + '_balances.txt'
            filenames.append(current_filename)
            with open(current_filename, 'w') as g:
                json.dump(clean_logs, g)
                # print(clean_logs)

    return filenames


def _countPunksByOwner(logs):

    balances = defaultdict(lambda: 0)
    punksMarketAddress = '0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB'
    # balances[punksMarketAddress] = 10000
    print(len(logs))
    pprint(logs[544:546])
    for log in logs:

        blockNumber = log['blockNumber']
        punkReceiver = log.get('args').get('to') or log.get('args').get('toAddress')
        punkSender = log.get('args').get('from') or log.get('args').get('fromAddress') or punksMarketAddress
        punkIndex = log['args']['punkIndex']
        value = log.get('args').get('value') or 'Not given'
        eventType = log['event']

        balances[punkSender] -= 1
        balances[punkReceiver] += 1

    return balances


if __name__ == '__main__':
    main()