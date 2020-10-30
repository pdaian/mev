import glob
import argparse
from collections import defaultdict
import logging


parser = argparse.ArgumentParser(description='Find MEV from krun logs')

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
    default='11006503'
)

parser.add_argument(
    '-a', '--address',
    help="pair address",
    default='0xa2107fa5b38d9bbd2c461d6edf11b11a50f6b974'

)

args = parser.parse_args()    
logging.basicConfig(level=args.loglevel, format='%(message)s')

logger = logging.getLogger(__name__)


if args.exchange == 'uniswapv2':
    exchange_acc = 'UniswapV2'
elif args.exchange == 'sushiswap':
    exchange_acc = 'Sushiswap'


log_filenames = glob.glob('output/%s-%s.out*' % (args.block, args.address) )
token0 = '1097077688018008265106216665536940668749033598146'
token1 = '464057641162257223597913127019930606481545201354'

lower_bounds = defaultdict(lambda : {token0 : 99999999999999999999999999999999})
upper_bounds = defaultdict(lambda : {token0 : -99999999999999999999999999999999})

for log_filename in log_filenames:
    balances = {}
    f = open(log_filename, 'r')
    for line in f.readlines():
        if '|->' in line:
            chunks = line.strip().split()
            acc = chunks[0]
            token = chunks[2]
            balance = chunks[4]
            if acc not in balances:
                balances[acc] = {}
            balances[acc][token] = int(balance)
    for acc in balances:
        if acc == exchange_acc:
            continue
        balance0 =  balances[acc][token0]
        balance1 =  balances[acc][token1]
        total_balance = balance0 + (balances[exchange_acc][token0] * balance1) / balances[exchange_acc][token1]
        lower_bounds[acc][token0] = min(lower_bounds[acc][token0], total_balance)
        upper_bounds[acc][token0] = max(upper_bounds[acc][token0], total_balance)


for acc in lower_bounds:
    print(acc)
    print(upper_bounds[acc][token0] - lower_bounds[acc][token0])
