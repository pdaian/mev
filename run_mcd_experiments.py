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
from find_mev_krun_mcd import reordering_mev

parser = argparse.ArgumentParser(description='Run MCD experiments')

parser.add_argument(
    '-v', '--verbose',
    help="Be verbose",
    action="store_const", dest="loglevel", const=logging.INFO,
    default=logging.WARNING
)

parser.add_argument(
    '-e', '--exchange',
    help="uniswapv2",
    default='uniswapv2'
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
    default='0xa478c2975ab1ea89e8196811f51a7b7ade33eb11'

)

parser.add_argument(
    '-cdp', '--cdp',
    help="CDP id",
    required=True
)

#sai_token_address = '89d24a6b4ccb1b6faa2625fe562bdd9a23260359'
dai_token_address = 'a478c2975ab1ea89e8196811f51a7b7ade33eb11'
#sai_token = '786821374916005576892310737142965798721793950553'
dai_token = '611382286831621467233887798921843936019654057231'

collateral_type = '31358499851466632982272067240987752480060719095994161751935692443478204088320'
collateral_token = '1097077688018008265106216665536940668749033598146'

args = parser.parse_args()    
logging.basicConfig(level=args.loglevel, format='%(message)s')

logger = logging.getLogger(__name__)

logger.info('Block : %s', args.start_block)
logger.info('Block : %s', args.end_block)

exchange_name = args.exchange

reserves = pd.read_csv('data-scripts/%s-reserves.csv' % (exchange_name))

mcd_fees_data = pd.read_csv('maker-data/mcd/maker_fees.csv')


# TODO : check if exists
transactions_filepath = 'data-scripts/' + exchange_name + '-processed/' + args.address + '.csv'
amm_transactions = ''
for block in range(int(args.start_block), int(args.end_block) + 1):
    block_str = str(block)
    pipe = Popen('grep -A 1 "block ' + block_str + '" ' + transactions_filepath, shell=True, stdout=PIPE, stderr=PIPE)
    component_transactions = pipe.stdout.read() + pipe.stderr.read()
    component_transactions = str(component_transactions, "utf-8")
    amm_transactions = amm_transactions + component_transactions
    
#maker_transactions_filepath = 'maker-data/maker_data.txt'
mcd_transactions_filepath = 'maker-data/mcd/maker-processed/%s.csv' % (collateral_type)

pipe = Popen('grep "vault ' + args.cdp + '" ' + mcd_transactions_filepath, shell=True, stdout=PIPE, stderr=PIPE)
mcd_transactions = pipe.stdout.read() + pipe.stderr.read()
mcd_transactions = str(mcd_transactions, "utf-8")


#post_reserve = reserves[(reserves.Address == args.address) & (reserves.Block ==  int(args.end_block))]
#post_price = (int(post_reserve.Reserve1) // int(post_reserve.Reserve0) , int(post_reserve.Reserve0) // int(post_reserve.Reserve1) )
post_price = (0, 0) #TODO : handle properly

balances = (0,0)

pre_reserve = reserves[(reserves.Address == args.address) & (reserves.Block <  int(args.start_block))]
tokens = (str(pre_reserve.iloc[0]['Token0']).replace(dai_token, 'DAI'), str(pre_reserve.iloc[0]['Token1']).replace(dai_token, 'DAI'))
if len(pre_reserve) < 1:
    pre_price = (0,0) # TODO : subtle issue wrt MEV here
else:
    pre_reserve = pre_reserve.iloc[-1]
    pre_price = (int(pre_reserve.Reserve1) // int(pre_reserve.Reserve0) , int(pre_reserve.Reserve0) // int(pre_reserve.Reserve1) )
    balances = (int(pre_reserve.Reserve0), int(pre_reserve.Reserve1))

logger.info(pre_reserve)

pre_fees_data = mcd_fees_data[mcd_fees_data.Block < int(args.start_block)]
if len(pre_fees_data) < 1:
    pre_fees = 0
else:
    pre_fees_data = pre_fees_data.iloc[-1]
    pre_fees = pre_fees_data.FeesInc
    

if exchange_name == 'uniswapv2':
    acc = 'UniswapV2'

identifier = args.cdp + '-' + args.start_block + '-' + args.end_block + '-' + args.address
    
spec_file = 'experiments-mcd-'+ exchange_name+'/' + identifier + '/bound.k'
outfile = 'run-output/'+ identifier +'.out'



# replace address w/ semantics keyword
amm_transactions = amm_transactions.replace(dai_token, 'DAI')
mcd_transactions = mcd_transactions.replace(dai_token, 'DAI').replace(collateral_type, collateral_token)


mcd_transactions = mcd_transactions.split('\n')

# censor on-chain liquidation tx

mcd_transactions = filter(lambda x: 'bites' not in x, mcd_transactions)

#maker_prologue = '\n'.join(filter(lambda x: 'opens' in x, transactions))
mcd_prologue = '\n'.join(mcd_transactions)
mcd_prologue = '%s increment in stability fees for %s ;\n' %(pre_fees, collateral_token) + mcd_prologue

mcd_epilogue = ''

transactions = amm_transactions + '\n0 bites vault {} ;'.format(args.cdp)

logger.info(mcd_prologue)

logger.info(transactions)

logger.info(mcd_epilogue)
    
reordering_mev(transactions, spec_file, outfile, acc, tokens, balances, pre_price, post_price, args.address, mcd_prologue, mcd_epilogue)
