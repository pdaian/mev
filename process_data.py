import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import sys
from uniswap import Uniswap

fin = open(sys.argv[1], 'r')
fout = open('actions_data_cut_'+sys.argv[2] + '_' +sys.argv[3]+'.txt', 'w')

prices = []

start_point = False
block_number = 0

uniswap = Uniswap()
line_num = 0
'''
for line in fin.readlines():
    line_num += 1
    if 'block' in line:
        words = line.split()
        block_number = int(words[-1])
    
    if block_number < int(sys.argv[2]):
        uniswap.process(line)
        config = uniswap.config()
    elif block_number <= int(sys.argv[3]):
        fout.write(line)
'''
for line in fin.readlines():
    line_num += 1
    if line_num < int(sys.argv[2]):
        uniswap.process(line)
        config = uniswap.config()
    elif line_num <= int(sys.argv[3]):
        fout.write(line)

price = config['SAI']/ config['0']
print(config)
print(price)
