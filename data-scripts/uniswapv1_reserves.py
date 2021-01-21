import argparse
import csv, os
import pandas as pd
import logging
from uniswapv1 import UniswapV1
from collections import defaultdict
import glob

#fin = open('data-scripts/latest-data/uniswapv1-processed/89d24a6b4ccb1b6faa2625fe562bdd9a23260359.csv', 'r')

filenames = glob.glob('latest-data/uniswapv1-processed/*.csv')
fout = open('latest-data/uniswapv1-reserves.csv', 'w')
fout.write('Block,Address,Token0,Token1,Reserve0,Reserve1\n')
exchange_acc = 'UniswapV1'

for filename in filenames:
    print("processing {} ...".format(filename))
    pair_address = filename.split('/')[-1].split('.')[0]
    fin = open(filename, 'r')

    block_to_reserves = defaultdict(lambda : {})

    uniswapv1 = UniswapV1()

    block_number = 0
    token = int(str(pair_address), 16)
    for line in fin.readlines():
        if 'block' in line:
            words = line.split()
            block_number = int(words[-1])
        else:
            uniswapv1.process(line)
            balances = uniswapv1.config()
            block_to_reserves[block_number][token] = balances[exchange_acc][str(token)]
            block_to_reserves[block_number]['0'] = balances[exchange_acc]['0']
        
    for block_num in block_to_reserves:
        token_reserve = block_to_reserves[block_num][token]
        eth_reserve = block_to_reserves[block_num]['0']
        fout.write("%d,%s,%d,%d,%d,%d\n" % (block_num, pair_address, token, 0, token_reserve, eth_reserve))

        
    
