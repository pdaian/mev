import argparse
import csv, os
import pandas as pd
import logging
from exchanges import topics_from_text

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
sushiswap_logs = 'latest-data/all_logs_sushiswap.csv'

exchange_logs = {'uniswapv2' : uniswapv2_logs, 'sushiswap' : sushiswap_logs}

uniswapv2_pairs = pd.read_csv('latest-data/uniswapv2_pairs.csv').set_index('pair')

logsdict = csv.DictReader(open(exchange_logs[exchange_name]), delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

logs = {}
block_to_reserves = {}
txhashes = []
events= []
tx_to_block = {}

#Interested in only Sync events
interested_topics = ['0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1']

for log in logsdict:
    topics = topics_from_text(log['topics'])
    if topics[0] not in interested_topics:
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
        if topics[0] == interested_topics[0]:
            # sync reserves
            reserve0= int(str(data[:64]), 16)
            reserve1= int(str(data[64:128]), 16)
            block_num = int(tx_to_block[txhash])
            if block_num not in block_to_reserves:
                block_to_reserves[block_num] = {}
            block_to_reserves[block_num][address] = (reserve0, reserve1)
            parsed += 1
        if  (parsed % 10000 == 0):
            logger.info("Parsed %d" %(parsed))


filepath = 'latest-data/%s-reserves.csv' % (exchange_name)

logger.info("Writing to %s" % (filepath))

fout = open(filepath, 'w')
fout.write('Block,Address,Token0,Token1,Reserve0,Reserve1\n')
for block_num in block_to_reserves:
    for address in block_to_reserves[block_num]:
        token0 = int(str(uniswapv2_pairs.loc[address].token0), 16)
        token1 = int(str(uniswapv2_pairs.loc[address].token1), 16)
        reserve0 = block_to_reserves[block_num][address][0]
        reserve1 = block_to_reserves[block_num][address][1]
        fout.write("%d,%s,%d,%d,%d,%d\n" % (block_num, address, token0, token1, reserve0, reserve1))
        
