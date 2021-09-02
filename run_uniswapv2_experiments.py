from subprocess import Popen, PIPE
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import sys, os
from copy import deepcopy
import pandas as pd
import argparse
import logging
#from find_mev_krun_uniswapv2 import reordering_mev
from find_mev_uniswapv2 import reordering_mev
from collections import defaultdict

# price in eth
def get_price(token, reserves, block):
    weth = '1097077688018008265106216665536940668749033598146'
    if token == weth:
        return 1.0
    pre_reserve = reserves[(reserves.Token0 == token) & (reserves.Token1 == weth) & (reserves.Block <  int(block))]
    # pre_reserve = pre_reserve.iloc[-1]
    if len(pre_reserve) > 0:
        return (int(pre_reserve.iloc[-1].Reserve1) + 0.0) / (int(pre_reserve.iloc[-1].Reserve0))
    pre_reserve = reserves[(reserves.Token0 == weth) & (reserves.Token1 == token) & (reserves.Block <  int(block))]
    # pre_reserve = pre_reserve.iloc[-1]
    if len(pre_reserve) > 0:
        return (int(pre_reserve.iloc[-1].Reserve0) + 0.0) / (int(pre_reserve.iloc[-1].Reserve1))
    return None

def get_address_from_tx(transaction, tokens):
    # print(transaction)
    for address in tokens:
        token0 = tokens[address][0]
        token1 = tokens[address][1]
        if token0 in transaction and token1 in transaction:
            # print(address)
            return address 
    return None

def associate_address(data, tokens):
    ret = {}
    transactions = data.split('\n')
    for idx in range(1, len(transactions), 2):
        address = get_address_from_tx(transactions[idx], tokens)
        if address is None:
            continue
        if address not in ret:
            ret[address] = ''
        ret[address] = ret[address] + transactions[idx-1] + '\n' + transactions[idx] + '\n'
    return ret
    



parser = argparse.ArgumentParser(description='Run UniswapV2 experiments')

parser.add_argument(
    '-v', '--verbose',
    help="Be verbose",
    action="store_const", dest="loglevel", const=logging.INFO,
    default=logging.WARNING
)

parser.add_argument(
    '-e', '--exchange',
    help="sushiswap/uniswapv2",
    default='uniswapv2'
)


parser.add_argument(
    '-b', '--block',
    help="Block number to find MEV in",
    required=True
)

parser.add_argument(
    '-d', '--date',
    help="Date",
    required=""
)

parser.add_argument(
    '-a', '--address',
    nargs='+',
    help="pair address",
    required=True

)

parser.add_argument(
    '-c', '--convergence',
    help="collect convervgence data",
    action="store_true"
)

parser.add_argument(
    '-p', '--paths',
    help="collect paths data to validate",
    default=""
)



args = parser.parse_args()    
logging.basicConfig(level=args.loglevel, format='%(message)s')

logger = logging.getLogger(__name__)

logger.info('Block : %s', args.block)

exchange_name = args.exchange

addresses = set(args.address)

date = args.date
month = date[:7]

reserves = pd.read_csv('data-scripts/latest-data/{}-reserves-segmented/{}'.format(exchange_name, month))
#uniswapv2_pairs = pd.read_csv('data-scripts/latest-data/data/uniswapv2_pairs.csv').set_index('pair')

balances = {}
tokens = {}
prices = {}

for address in addresses:
    balances[address] = (0,0)
    address_reserves = reserves[(reserves.Address == address)]
    pre_reserve = address_reserves[(address_reserves.Block <  int(args.block))]
    if len(pre_reserve) > 0:
        pre_reserve = pre_reserve.iloc[-1]
        balances[address] = (int(pre_reserve.Reserve0), int(pre_reserve.Reserve1))
    token0 = address_reserves.iloc[0].Token0
    token1 = address_reserves.iloc[0].Token1
    tokens[address] = (token0, token1)
    prices[token0] = get_price(token0, reserves, args.block)
    prices[token1] = get_price(token1, reserves, args.block)
    if prices[token0] is None or prices[token1] is None:
        logger.warning("unknown prices for %s", address)
        sys.exit(1)

logger.info(tokens)
logger.info(balances)

if exchange_name == 'uniswapv2':
    acc = 'UniswapV2'
elif exchange_name == 'sushiswap':
    acc = 'Sushiswap'

identifier = args.block + '-' + '-'.join([address[:8] for address in addresses])
    
spec_file = 'experiments/' + identifier + '/bound.k'
outfile = 'output/'+ identifier +'.out'

# TODO : check if exists
transactions = {}

if date != "":
    transactions_filepath = 'data-scripts/latest-data/' + exchange_name + '-indexed/' + date + '.csv' 
    pipe = Popen('grep -A 1 "block ' + args.block + '" ' + transactions_filepath, shell=True, stdout=PIPE, stderr=PIPE)
    transactions = associate_address(str(pipe.stdout.read() + pipe.stderr.read(), "utf-8"), tokens)
else:
    for address in addresses:
        transactions_filepath = 'data-scripts/latest-data/' + exchange_name + '-processed/' + address + '.csv'
        pipe = Popen('grep -A 1 "block ' + args.block + '" ' + transactions_filepath, shell=True, stdout=PIPE, stderr=PIPE)
        transactions[address] = str(pipe.stdout.read() + pipe.stderr.read(), "utf-8")

logger.info(transactions)

total_mev = 0
tx_ordering_u = []
tx_ordering_l = []

for address in addresses:
    mev, u, l = reordering_mev(transactions[address], spec_file, outfile, acc, tokens[address], balances[address], address, prices, args.block, args.convergence)
    total_mev += mev
    tx_ordering_u.append(u)
    tx_ordering_l.append(l)

path_filename = args.paths

if path_filename != '':
    path_f = open(path_filename, 'a')    
    path_f.write('{},{},{},{},{}\n'.format(args.block, total_mev, '1', acc, ','.join(tx_ordering_u)))
    path_f.write('{},{},{},{},{}\n'.format(args.block, total_mev, '0', acc, ','.join(tx_ordering_l)))
    path_f.close()

# print(acc, pair_address, token0, token1, block, len(all_transactions), mev, sep=',')
    
