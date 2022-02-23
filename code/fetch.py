import json, math, pdb
from dotenv import load_dotenv
load_dotenv()
from web3.auto.infura import w3

from utils import (
    non_equal_intervals,
    flatten,
    parseResultList
    )

address = '0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB'
CryptoPunksABI = '../cryptopunks/compiled/CryptoPunksMarket.abi'
contract_creation_block = 3914495

def main():
    with open(CryptoPunksABI) as f:
        abi = json.load(f)
        contract = w3.eth.contract(address=CRYPTOPUNKS_SMART_CONTRACT_ADDRESS, abi=abi)

        transfer_event = contract.events.PunkTransfer
        buy_event = contract.events.PunkBought
        assign_event = contract.events.Assign

        exponent_function = lambda x: (math.e ** (x/100)) -1

        transfer_logs = getPunksLogs(transfer_event, 150)
        buy_logs = getPunksLogs(buy_event, 150)
        assign_logs = getPunksLogs(assign_event, 700, exponent_function)

        savePunksLogs(transfer_logs, '../data/transfers.txt')
        savePunksLogs(buy_logs, '../data/buys.txt')
        savePunksLogs(assign_logs, '../data/assigns.txt')


def getPunksLogs(filterObject, intervalsCount, transformFunction= lambda x: x):
    currentBlock = w3.eth.blockNumber
    queryIntervals = non_equal_intervals(
                        contract_creation_block, 
                        currentBlock, 
                        intervalsCount,
                        transformFunction
                        )
    # queryIntervals = [[12370609, 12419122]] #for testing purposes
    pdb.set_trace()
    payload = []
    for count, [start, end] in enumerate(queryIntervals):
        s = hex(round(start))
        e = hex(round(end))
        print(count, s, e)
        currentFilter = filterObject.createFilter(fromBlock=s, toBlock=e)
        entries = currentFilter.get_all_entries()
        payload.append(entries)

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


