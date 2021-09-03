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
import time

start_time = time.time()

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
    '-n', '--num_workers',
    help="Number of threads to use",
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

reserves = pd.read_csv('data-scripts/latest-data/%s-reserves.csv' % (exchange_name))

mcd_fees_data = pd.read_csv('maker-data/mcd/latest-data/maker_fees.csv')

if exchange_name == 'uniswapv2':
    acc = 'UniswapV2'

def get_mcd_rate(given_block):
    pre_fees_data = mcd_fees_data[mcd_fees_data.Block < int(given_block)]
    if len(pre_fees_data) < 1:
        pre_fees = 10**27
    else:
        pre_fees_data = pre_fees_data.iloc[-1]
        pre_fees = pre_fees_data.Fees
    return int(pre_fees)
    
def get_uniswap_reserves(given_block):
    balances = {collateral_token:0, 'DAI':0}

    pre_reserve = reserves[(reserves.Address == args.address) & (reserves.Block <  int(given_block))]
    if len(pre_reserve) < 1:
        return balances
    else:
        tokens = (str(pre_reserve.iloc[0]['Token0']).replace(dai_token, 'DAI'), str(pre_reserve.iloc[0]['Token1']).replace(dai_token, 'DAI'))
        pre_reserve = pre_reserve.iloc[-1]
        return  {tokens[0] : int(pre_reserve.Reserve0), tokens[1]: int(pre_reserve.Reserve1)}

def kint(x):
    if x >= 0:
        return "gets %d" % (x)
    else:
        return "gives %d" % (0-x)


def get_mcd_prologue(mcd_transactions, start_block):
    mcd_transactions = mcd_transactions.split('\n')
    mcd_prologue = ''
    rate = 10**27
    balances = {collateral_token: 0, 'DAI': 0}
    curr_block = 0
    for transaction in mcd_transactions:
        transaction = transaction.strip()
        if 'block' in transaction:
            curr_block = int(transaction.split()[-1])
            if curr_block >= start_block:
                break
        elif 'vault' in transaction:
            curr_balances = get_uniswap_reserves(curr_block)
            curr_rate = get_mcd_rate(curr_block)
            mcd_prologue +=  """{acc} in {token0} {balance0} ;
            {acc} in {token1} {balance1} ;
            {fee_inc} increment in stability fees for {token1} ;
            {tx}
            """.format(acc=acc, token0='DAI', token1=collateral_token, balance0=kint(curr_balances['DAI'] - balances['DAI']), balance1=kint(curr_balances[collateral_token]-balances[collateral_token]),tx=transaction, fee_inc = curr_rate - rate)
            balances = curr_balances
            rate = curr_rate
    curr_balances = get_uniswap_reserves(start_block)
    curr_rate = get_mcd_rate(start_block)
    mcd_prologue +=  """{acc} in {token0} {balance0} ;
    {acc} in {token1} {balance1} ;
    GetPrice {token0} {token1} ;
    {fee_inc} increment in stability fees for {token1} ;
    """.format(acc=acc, token0='DAI', token1=collateral_token, balance0=kint(curr_balances['DAI'] - balances['DAI']), balance1=kint(curr_balances[collateral_token]-balances[collateral_token]), fee_inc = curr_rate - rate)
    balances = curr_balances
    rate = curr_rate
    return mcd_prologue


# TODO : check if exists
transactions_filepath = 'data-scripts/latest-data/' + exchange_name + '-processed/' + args.address + '.csv'
amm_transactions = ''
for block in range(int(args.start_block), int(args.end_block) + 1):
    block_str = str(block)
    pipe = Popen('grep -A 1 "block ' + block_str + '" ' + transactions_filepath, shell=True, stdout=PIPE, stderr=PIPE)
    component_transactions = pipe.stdout.read() + pipe.stderr.read()
    component_transactions = str(component_transactions, "utf-8")
    amm_transactions = amm_transactions + component_transactions
    
#maker_transactions_filepath = 'maker-data/maker_data.txt'
mcd_transactions_filepath = 'maker-data/mcd/latest-data/maker-processed/%s.csv' % (collateral_type)

pipe = Popen('grep -B 1 "vault ' + args.cdp + '" ' + mcd_transactions_filepath, shell=True, stdout=PIPE, stderr=PIPE)
mcd_transactions = pipe.stdout.read() + pipe.stderr.read()
mcd_transactions = str(mcd_transactions, "utf-8")



identifier = args.cdp + '-' + args.start_block + '-' + args.end_block + '-' + args.address
    
spec_file = 'experiments-mcd-'+ exchange_name+'/' + identifier + '/bound.k'
outfile = 'run-output/'+ identifier +'.out'



# replace address w/ semantics keyword
amm_transactions = amm_transactions.replace(dai_token, 'DAI').strip()
mcd_transactions = mcd_transactions.replace(dai_token, 'DAI').replace(collateral_type, collateral_token).strip()


mcd_prologue = get_mcd_prologue(mcd_transactions, int(args.start_block))

mcd_epilogue = ''

transactions = amm_transactions + '\n0 bites vault {} ;'.format(args.cdp)

logger.info(mcd_prologue)

logger.info(transactions)

logger.info(mcd_epilogue)

reordering_time = time.time()
    
reordering_mev(transactions, spec_file, outfile, acc, args.address, mcd_prologue, mcd_epilogue, args.num_workers)

end_time = time.time()

print("{},{},{}".format(args.num_workers, end_time-start_time, end_time-reordering_time))