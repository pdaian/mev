import json
import csv, os
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

maker_logs = 'latest-data/all_logs_maker.csv'

outputdir = 'latest-data/maker-processed'

logsdict = csv.DictReader(open(maker_logs), delimiter=',',
                          quotechar='"', quoting=csv.QUOTE_MINIMAL)

logs = {}
events_by_collateral = {}
txhashes = []
events= []
tx_to_block = {}
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

for txhash in txhashes:
    for logitem in logs[txhash]:
        address = logitem[0]
        data = logitem[1]
        topics = logitem[2]
        data = data[2:] # strip 0x from hex
        action_requested = None
        collateral_type = ''
        if topics[0][:10] == interested_topics[0]:
            # cdp manipulation
            collateral_type = int(str(data[136:200]), 16)
            cdp_handler = int(str(data[200:264]), 16)
            collateral_amount = hex_to_int(str(data[392:456]))
            debt_amount = hex_to_int(str(data[456:520]))
            if collateral_amount >= 0:
                subaction1 = "%d in %d collateral locked" % (collateral_amount, collateral_type)
            else:
                subaction1 = "%d in %d collateral freed" % (0 - collateral_amount, collateral_type)
            if debt_amount < 0:
                subaction2 = "%d in %d debt wiped" % (0 - debt_amount, debt_type)
            else:
                subaction2 = "%d in %d debt drawn"  % (debt_amount, debt_type)
            action_requested = "%s and %s from vault %d ;" % (subaction1, subaction2, cdp_handler)
        elif topics[0][:10] == interested_topics[1]:
            # Liquidate CDP
            if len(topics) < 3:
                logger.warning(address, txhash, topics, data)
                continue
            collateral_type = int(str(topics[1]), 16)
            cdp_handler = int(str(topics[2]), 16) 
            liquidator = int(str(data[192:256]), 16)
            
            action_requested = "%d bites vault %d ;" % (liquidator, cdp_handler)
            
        elif topics[0][:10] == interested_topics[2]:
            collateral_type = int(str(data[136:200]), 16)
            rate_inc = hex_to_int(str(data[264:328]))
            action_requested = "%d increment in stability fees for %d ;" % (rate_inc, collateral_type)

        elif topics[0][:10] == interested_topics[3]:
            # cdp fungibility
            collateral_type = int(str(data[136:200]), 16)
            src_cdp = int(str(data[200:264]), 16)
            dst_cdp = int(str(data[264:328]), 16)
            collateral_amount = hex_to_int(str(data[328:392]))
            debt_amount = hex_to_int(str(data[392:456]))
            action_requested = "%d in %d and %d in %d transferred from %d to %d ;" %(collateral_amount, collateral_type, debt_amount, debt_type, src_cdp, dst_cdp)
            
        if action_requested is not None:
            if not (collateral_type) in events_by_collateral:
                events_by_collateral[collateral_type] = []
            event = "// transaction %s block %s\n%s" % (txhash, tx_to_block[txhash], action_requested)
            events_by_collateral[collateral_type].append(event)
            events.append(event)
            parsed += 1
        if  (parsed % 10000 == 0):
            logger.info("Parsed %d" %(parsed))

for collateral in events_by_collateral:
    filepath = '%s/%s.csv' % (outputdir, collateral)
    open(filepath, 'w').write("\n".join(events_by_collateral[collateral]) + '\n')
    logger.info("Written %s" % (filepath))

logger.info("Writing All...")
open('%s/all.csv' % (outputdir), 'w').write("\n".join(events) + '\n')
