import csv, os
import pandas as pd
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)



from exchanges import get_trade_data_from_log_item, get_uniswap_token, topics_from_text

exchange_name = sys.argv[1]

uniswapv2_logs = 'latest-data/all_logs_uniswapv2.csv'
sushiswap_logs = 'latest-data/all_logs_sushiswap.csv'

exchange_logs = {'uniswapv2' : uniswapv2_logs, 'sushiswap' : sushiswap_logs}
outputdir = 'latest-data/' + exchange_name + '-processed'

uniswapv2_pairs = pd.read_csv('latest-data/uniswapv2_pairs.csv').set_index('pair')

logsdict = csv.DictReader(open(exchange_logs[exchange_name]), delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

# logs sorted by block number and then transaction indices (all logs from same txhash are consecutive)

events_by_address = {}

#Interested in only Mint, Burn and Swap events
interested_topics = ['0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f','0xdccd412f0b1252819cb1fd330b93224ca42612892bb3f4f789976e6d81936496','0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822']

parsed = 0
for log in logsdict:
    topics = topics_from_text(log['topics'])
    if topics[0] not in interested_topics:
        continue
    txhash = log['transaction_hash']
    block_number = log['block_number']
    address = log['address']
    data = log['data']
    gas_price = int(log['gas_price'])
    receipt_gas_used = int(log['receipt_gas_used'])
    data = data[2:] # strip 0x from hex
    token0 = int(str(uniswapv2_pairs.loc[address].token0), 16)
    token1 = int(str(uniswapv2_pairs.loc[address].token1), 16)
    action_requested = None
    if topics[0] == interested_topics[0]:
        # add liquidity
        if len(topics) < 2:
            logger.warning(address, txhash, topics, data)
            continue
        provider = int(str(topics[1]), 16)
        amount0 = int(str(data[:64]), 16)
        amount1 = int(str(data[64:]), 16)
        action_requested = "%d adds %d %d and %d %d of liquidity;" % (provider, amount0, token0, amount1, token1)
    elif topics[0] == interested_topics[1]:
        # remove liquidity
        if len(topics) < 3:
            logger.warning(address, txhash, topics, data)
            continue
        remover = int(str(topics[1]), 16) #msg.sender, because to can be to another contract
        amount0 = int(str(data[:64]), 16)
        amount1 = int(str(data[64:]), 16)
        action_requested = "%d removes %d %d and %d %d of liquidity;" % (remover, amount0, token0, amount1, token1)
    elif topics[0] == interested_topics[2]:
        if len(topics) < 3:
            logger.warning(address, txhash, topics, data)
            continue
        trader = int(str(topics[1]), 16) #msg.sender, because to can be to another contract
        amount0_in = int(str(data[:64]), 16)
        amount1_in = int(str(data[64:128]), 16)
        amount0_out = int(str(data[128:192]), 16)
        amount1_out = int(str(data[192:256]), 16)

        # exactly one input amount zero and exactly one output amount zero is the most common
        # one input amount 0 and both output amounts non zero is common
        # both input amounts non zero and exactly one output amount non zero is rare ~ 100ppm

        if (amount1_out == 0):
            # address swaps for Y by providing x X and y Y with change x X
            action_requested = "%d swaps for %d by providing %d %d and %d %d with change %d fee %d ;" % (
                trader, token0, amount1_in, token1, amount0_in, token0 , amount1_out, gas_price * receipt_gas_used)
        elif (amount0_out == 0):
            action_requested = "%d swaps for %d by providing %d %d and %d %d with change %d fee %d ;" % (
                trader, token1, amount0_in, token0, amount1_in, token1 , amount0_out, gas_price * receipt_gas_used)
        elif (amount1_in == 0):
            action_requested = "%d swaps for %d by providing %d %d and %d %d with change %d fee %d ;" % (
                trader, token1, amount0_in, token0, amount1_in, token1 , amount0_out, gas_price * receipt_gas_used)
        elif (amount0_in == 0):
            action_requested = "%d swaps for %d by providing %d %d and %d %d with change %d fee %d ;" % (
                trader, token0, amount1_in, token1, amount0_in, token0 , amount1_out, gas_price * receipt_gas_used)
        else:
            logger.warning(address, txhash, topics, data)
            continue
        
    if action_requested is not None:
        if not (address) in events_by_address:
            events_by_address[address] = []
        event = "// transaction %s block %s\n%s" % (txhash, block_number, action_requested)
        events_by_address[address].append(event)
        parsed += 1
    if  (parsed % 10000 == 0):
        logger.info("Parsed %d" %(parsed))

for address in events_by_address:
    filepath = '%s/%s.csv' % (outputdir, address)
    open(filepath, 'w').write("\n".join(events_by_address[address]) + '\n')
    logger.info("Written %s" % (filepath))

logger.info("Done...")
