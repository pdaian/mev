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
    '-a', '--address',
    help="pair address",
    required=True

)


args = parser.parse_args()    
logging.basicConfig(level=args.loglevel, format='%(message)s')

logger = logging.getLogger(__name__)

logger.info('Block : %s', args.block)

exchange_name = args.exchange

reserves = pd.read_csv('data-scripts/%s-reserves.csv' % (exchange_name))
#uniswapv2_pairs = pd.read_csv('data-scripts/data/uniswapv2_pairs.csv').set_index('pair')

# TODO : check if exists
transactions_filepath = 'data-scripts/' + exchange_name + '-processed/' + args.address + '.csv'

pipe = Popen('grep -A 1 "block ' + args.block + '" ' + transactions_filepath, shell=True, stdout=PIPE, stderr=PIPE)
transactions = pipe.stdout.read() + pipe.stderr.read()
transactions = str(transactions, "utf-8")

logger.info(transactions)

post_reserve = reserves[(reserves.Address == args.address) & (reserves.Block ==  int(args.block))]
post_price = (int(post_reserve.Reserve1) // int(post_reserve.Reserve0) , int(post_reserve.Reserve0) // int(post_reserve.Reserve1) )

logger.info(post_reserve)

balances = (0,0)
tokens = (post_reserve.iloc[0]['Token0'], post_reserve.iloc[0]['Token1'])

pre_reserve = reserves[(reserves.Address == args.address) & (reserves.Block <  int(args.block))]
if len(pre_reserve) < 1:
    post_price = (0,0) # TODO : subtle issue wrt MEV here, ERROR should be pre
else:
    pre_reserve = pre_reserve.iloc[-1]
    pre_price = (int(pre_reserve.Reserve1) // int(pre_reserve.Reserve0) , int(pre_reserve.Reserve0) // int(pre_reserve.Reserve1) )
    balances = (int(pre_reserve.Reserve0), int(pre_reserve.Reserve1))

logger.info(pre_reserve)

if exchange_name == 'uniswapv2':
    acc = 'UniswapV2'
elif exchange_name == 'sushiswap':
    acc = 'Sushiswap'

identifier = args.block + '-' + args.address
    
spec_file = 'experiments/' + identifier + '/bound.k'
outfile = 'output/'+ identifier +'.out'

    
reordering_mev(transactions, spec_file, outfile, acc, tokens, balances, pre_price, post_price, args.address, args.block)
