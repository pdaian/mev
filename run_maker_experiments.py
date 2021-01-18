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
#from find_mev_uniswapv1 import reordering_mev
from find_mev_krun_maker import reordering_mev

parser = argparse.ArgumentParser(description='Run UniswapV1 experiments')

parser.add_argument(
    '-v', '--verbose',
    help="Be verbose",
    action="store_const", dest="loglevel", const=logging.INFO,
    default=logging.WARNING
)

parser.add_argument(
    '-e', '--exchange',
    help="uniswapv1",
    default='uniswapv1'
)


parser.add_argument(
    '-sb', '--start_block',
    help="Block number to find MEV in",
    required=True
)

parser.add_argument(
    '-eb', '--end_block',
    help="Block number to find MEV in",
    required=True
)

parser.add_argument(
    '-a', '--address',
    help="pair address",
    default='89d24a6b4ccb1b6faa2625fe562bdd9a23260359'

)

parser.add_argument(
    '-cdp', '--cdp',
    help="CDP id",
    required=True
)

sai_token_address = '89d24a6b4ccb1b6faa2625fe562bdd9a23260359'
sai_token = '786821374916005576892310737142965798721793950553'


args = parser.parse_args()    
logging.basicConfig(level=args.loglevel, format='%(message)s')

logger = logging.getLogger(__name__)

logger.info('Block : %s', args.start_block)
logger.info('Block : %s', args.end_block)

exchange_name = args.exchange

reserves = pd.read_csv('data-scripts/latest-data/%s-reserves.csv' % (exchange_name))
#uniswapv2_pairs = pd.read_csv('data-scripts/latest-data/data/uniswapv2_pairs.csv').set_index('pair')

# TODO : check if exists
transactions_filepath = 'data-scripts/latest-data/' + exchange_name + '-processed/' + args.address + '.csv'
transactions = ''
for block in range(int(args.start_block), int(args.end_block) + 1):
    block_str = str(block)
    pipe = Popen('grep -A 1 "block ' + block_str + '" ' + transactions_filepath, shell=True, stdout=PIPE, stderr=PIPE)
    component_transactions = pipe.stdout.read() + pipe.stderr.read()
    component_transactions = str(component_transactions, "utf-8")
    transactions = transactions + component_transactions
    
maker_transactions_filepath = 'maker-data/maker_data.txt'
pipe = Popen('grep "vault ' + args.cdp + ';" ' + maker_transactions_filepath, shell=True, stdout=PIPE, stderr=PIPE)
maker_transactions = pipe.stdout.read() + pipe.stderr.read()
maker_transactions = str(maker_transactions, "utf-8")
transactions = transactions + maker_transactions


#post_reserve = reserves[(reserves.Address == args.address) & (reserves.Block ==  int(args.end_block))]
#post_price = (int(post_reserve.Reserve1) // int(post_reserve.Reserve0) , int(post_reserve.Reserve0) // int(post_reserve.Reserve1) )
post_price = (0, 0) #TODO : handle properly

balances = (0,0)

pre_reserve = reserves[(reserves.Address == args.address) & (reserves.Block <  int(args.start_block))]
tokens = (str(pre_reserve.iloc[0]['Token0']).replace(sai_token, 'SAI'), str(pre_reserve.iloc[0]['Token1']).replace(sai_token, 'SAI'))
if len(pre_reserve) < 1:
    pre_price = (0,0) # TODO : subtle issue wrt MEV here
else:
    pre_reserve = pre_reserve.iloc[-1]
    pre_price = (int(pre_reserve.Reserve1) // int(pre_reserve.Reserve0) , int(pre_reserve.Reserve0) // int(pre_reserve.Reserve1) )
    balances = (int(pre_reserve.Reserve0), int(pre_reserve.Reserve1))

logger.info(pre_reserve)

if exchange_name == 'uniswapv1':
    acc = 'Uniswap'

identifier = args.cdp + '-' + args.start_block + '-' + args.end_block + '-' + args.address
    
spec_file = 'experiments-maker-'+ exchange_name+'/' + identifier + '/bound.k'
outfile = 'output/'+ identifier +'.out'




transactions = transactions.split('\n')

maker_prologue = '\n'.join(filter(lambda x: 'opens' in x, transactions))

transactions = '\n'.join([transaction for transaction in transactions if 'opens' not in transaction])

maker_epilogue = '\n0 bites vault {} ;'.format(args.cdp)

# replace address w/ semantics keyword
transactions = transactions.replace(sai_token, 'SAI')

logger.info(maker_prologue)

logger.info(transactions)

logger.info(maker_epilogue)
    
reordering_mev(transactions, spec_file, outfile, acc, tokens, balances, pre_price, post_price, args.address, maker_prologue, maker_epilogue)
