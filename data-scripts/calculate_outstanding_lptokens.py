import argparse
import csv, os
import pandas as pd
import logging
from exchanges import topics_from_text
from collections import defaultdict

parser = argparse.ArgumentParser(description='Get UniswapV2 Reserves')
parser.add_argument(
    '-v', '--verbose',
    help="Be verbose",
    action="store_const", dest="loglevel", const=logging.INFO,
    default=logging.WARNING
)

parser.add_argument(
    '-e', '--exchange',
    help="sushiswap/uniswapv2",
    default='sushiswap'
)


args = parser.parse_args()    
logging.basicConfig(level=args.loglevel, format='%(message)s')

logger = logging.getLogger(__name__)

exchange_name = args.exchange

uniswapv2_logs = 'latest-data/all_logs_uniswapv2.csv'
# sushiswap_logs = 'latest-data/all_logs_sushiswap.csv'
sushiswap_logs = 'latest-data/sushiswap_eth_usdc_logs.csv'

exchange_logs = {'uniswapv2' : uniswapv2_logs, 'sushiswap' : sushiswap_logs}

logsdict = csv.DictReader(open(exchange_logs[exchange_name]), delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

block_to_supply = defaultdict(lambda : defaultdict(lambda: 0))
address_to_supply = defaultdict(lambda: 0)
#Interested in only Transfer events
interested_topics = ['0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef']


parsed = 0
for log in logsdict:
    topics = topics_from_text(log['topics'])
    if topics[0] not in interested_topics:
        continue
    txhash = log['transaction_hash']
    block_number = log['block_number']
    address = log['address']
    data = log['data']
    data = data[2:] # strip 0x from hex
    action_requested = None

    if topics[0] == interested_topics[0]:
        # transfer
        from_address = topics[1]
        to_address = topics[2]
        if int(from_address, 16) == 0:
            #minting lp tokens
            block_num = int(block_number)
            value = int(data, 16)
            address_to_supply[address] += value
            block_to_supply[block_num][address] = address_to_supply[address]
            parsed += 1
        elif int(to_address, 16) == 0:
            # burning lp tokens
            block_num = int(block_number)
            value = int(data, 16)
            address_to_supply[address] -= value
            block_to_supply[block_num][address] = address_to_supply[address]
            parsed += 1
    if  (parsed % 10000 == 0):
        logger.info("Parsed %d" %(parsed))


filepath = 'latest-data/%s-lptokens.csv' % (exchange_name)

logger.info("Writing to %s" % (filepath))

fout = open(filepath, 'w')
fout.write('Block,Address,Supply\n')
for block_num in block_to_supply:
    for address in block_to_supply[block_num]:
        supply = block_to_supply[block_num][address]
        fout.write("%d,%s,%d\n" % (block_num, address, supply))
        
