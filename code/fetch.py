import json
from dotenv import load_dotenv
load_dotenv()
# from requests_cache import install_cache
# install_cache('cryptopunks_cache')

from web3.auto.infura import w3

from utils import (
    intervals, 
    flatten,
    parseResultList
    )

address = '0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB'
CryptoPunksABI = '../cryptopunks/compiled/CryptoPunksMarket.abi'
contract_creation_block = 3914495

def main():
    with open(CryptoPunksABI) as f:
        abi = json.load(f)
        contract = w3.eth.contract(address=address, abi=abi)

        transfer_event = contract.events.PunkTransfer
        buy_event = contract.events.PunkBought
        assign_event = contract.events.Assign

        # transfer_logs = getPunksLogs(transfer_event, 150)
        # buy_logs = getPunksLogs(buy_event, 150)
        assign_logs = getPunksLogs(assign_event, 2000)

        # savePunksLogs(transfer_logs, '../data/transfers.txt')
        # savePunksLogs(buy_logs, '../data/buys.txt')
        savePunksLogs(assign_logs, '../data/assigns.txt')


def getPunksLogs(filterObject, intervalsCount):
    currentBlock = w3.eth.blockNumber
    queryIntervals = intervals(contract_creation_block, currentBlock, intervalsCount)
    # queryIntervals = [[12370609, 12419122]] #for testing purposes

    payload = []
    for count, [start, end] in enumerate(queryIntervals):
        s = hex(round(start))
        e = hex(round(end))
        print(count, s, e)
        currentFilter = filterObject.createFilter(fromBlock=s, toBlock=e)
        entries = currentFilter.get_all_entries()
        payload.append(entries)

    # payload is a list of lists of dicts
    print(payload)
    return payload

def savePunksLogs(logs, filename):
    flattenedResults = flatten(logs)
    parsedResults = parseResultList(flattenedResults)
    with open(filename, 'w') as f:
        json.dump(parsedResults, f)
        print(parsedResults)
        print(len(parsedResults))



if __name__ == 'main':
    main()


