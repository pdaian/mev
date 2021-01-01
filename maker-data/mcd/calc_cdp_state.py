import json
import csv, os
import pandas as pd
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

maker_logs = 'latest-data/all_logs_maker.csv'

logsdict = csv.DictReader(open(maker_logs), delimiter=',',
                          quotechar='"', quoting=csv.QUOTE_MINIMAL)

logs = {}
events_by_collateral = {}
txhashes = []
events= []
tx_to_block = {}
cdp_to_state = defaultdict(lambda : [0,0])
debt_type = 611382286831621467233887798921843936019654057231

#Interested in only frob, Bite, fold, fork
interested_topics = ['0x76088703', '0xa716da86', '0xb65337df', '0x870c616d']

def hex_to_int(raw_hex, bits=256):
    val = int(raw_hex, 16)
    # check MSB
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits) 
    return val
    

for log in logsdict:
    topics = json.loads(log['topics'].replace('\'', '\"'))
    if topics[0][:10] not in interested_topics:
        continue
    hash = log['transaction_hash']
    if not hash in logs:
        logs[hash] = []
        txhashes.append(hash)
    logs[hash].append((log['address'], log['data'], topics, log['gas_price'], log['receipt_gas_used'], log['block_number']))
    tx_to_block[hash] = log['block_number']

parsed = 0
rate = 10**27
liquidated_cdps = set()

fout = open('latest-data/cdp_states.csv', 'w')
fout.write('Block,CDP,Collateral_type,Collateral,Debt\n')
for txhash in txhashes:
    modified_cdps = set()
    block = tx_to_block[txhash]
    for logitem in logs[txhash]:
        address = logitem[0]
        data = logitem[1]
        topics = logitem[2]
        data = data[2:] # strip 0x from hex
        collateral_type = ''
        action_requested = None
        if topics[0][:10] == interested_topics[0]:
            # cdp manipulation
            collateral_type = int(str(data[136:200]), 16)
            cdp_handler = int(str(data[200:264]), 16)
            collateral_amount = hex_to_int(str(data[392:456]))
            debt_amount = hex_to_int(str(data[456:520]))
            cdp_to_state[cdp_handler][0] = cdp_to_state[cdp_handler][0] + collateral_amount
            cdp_to_state[cdp_handler][1] = cdp_to_state[cdp_handler][1] + debt_amount
            modified_cdps.add((cdp_handler, collateral_type))

        elif topics[0][:10] == interested_topics[1]:
            # Liquidate CDP
            if len(topics) < 3:
                logger.warning(address, txhash, topics, data)
                continue
            cdp_handler = int(str(topics[2]), 16) 
            liquidated_cdps.add(cdp_handler)


        elif topics[0][:10] == interested_topics[3]:
            # cdp fungibility
            collateral_type = int(str(data[136:200]), 16)
            src_cdp = int(str(data[200:264]), 16)
            dst_cdp = int(str(data[264:328]), 16)
            collateral_amount = hex_to_int(str(data[328:392]))
            debt_amount = hex_to_int(str(data[392:456]))
            cdp_to_state[src_cdp][0] = cdp_to_state[src_cdp][0] - collateral_amount
            cdp_to_state[src_cdp][1] = cdp_to_state[src_cdp][1] - debt_amount
            cdp_to_state[dst_cdp][0] = cdp_to_state[dst_cdp][0] + collateral_amount
            cdp_to_state[dst_cdp][1] = cdp_to_state[dst_cdp][1] + debt_amount
            modified_cdps.add((src_cdp, collateral_type))
            modified_cdps.add((dst_cdp, collateral_type))
            
        if  (parsed % 10000 == 0):
            logger.info("Parsed %d" %(parsed))

        parsed+= 1

                # dont bother about liquidated ones because mcd semantics doesnt handle bites well
    for (cdp_handler, collateral_type) in modified_cdps:
        if cdp_handler not in liquidated_cdps:
            action_requested = "{block},{cdp},{collateral_type},{collateral},{debt}\n".format(block=block,cdp=cdp_handler,collateral_type=collateral_type,collateral=cdp_to_state[cdp_handler][0],debt=cdp_to_state[cdp_handler][1])
            fout.write(action_requested)

fout.close()
