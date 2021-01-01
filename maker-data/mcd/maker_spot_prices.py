import json
import csv, os
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

maker_logs = 'latest-data/all_logs_maker.csv'

outfile = 'latest-data/spot_prices.csv'

logsdict = csv.DictReader(open(maker_logs), delimiter=',',
                          quotechar='"', quoting=csv.QUOTE_MINIMAL)

logs = {}
events_by_collateral = {}
txhashes = []
events= []
tx_to_block = {}

#Interested in only file
interested_topics = ['0x1a0b287e']
what = '0x73706f74'

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
        if topics[0][:10] == interested_topics[0] and topics[2][:10] == what:
            # oracle update
            collateral_type = int(str(data[136:200]), 16)
            spot_price = int(str(data[264:328]), 16)
            action_requested = "%d,%s,%d" % (collateral_type, tx_to_block[txhash], spot_price)
            events.append(action_requested)
        parsed += 1
        if  (parsed % 10000 == 0):
            logger.info("Parsed %d" %(parsed))

logger.info("Writing All...")
fout = open(outfile, 'w')
fout.write("CollateralType,Block,SpotPrice\n")
fout.write("\n".join(events) + '\n')

