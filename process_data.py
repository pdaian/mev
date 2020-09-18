import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import sys
from uniswap import Uniswap
from copy import deepcopy

fin = open(sys.argv[1], 'r')
fout = open('data/uniswap_data_cut_'+sys.argv[2] + '_' +sys.argv[3], 'w')

prices = {}
lines = []

start_point = False
block_number = 0

def get_price(cfg):
    return cfg['SAI']/ cfg['0']

def bootstrapped_data(f, cfg, rows):
    f.write("Uniswap in 0 gets {:.0f};\n".format(cfg['0']))
    f.write("Uniswap in SAI gets {:.0f};\n".format(cfg['SAI']))
    f.write("GetPrice SAI 0;\n")
    for row in rows:
        f.write(row)

uniswap = Uniswap()
line_num = 0

for line in fin.readlines():
    line_num += 1
    if 'block' in line:
        words = line.split()
        block_number = int(words[-1])
    if block_number > int(sys.argv[3]):
        break
    
    uniswap.process(line)

    if block_number < int(sys.argv[2]):
        config = deepcopy(uniswap.config()) #arghhhhh!
    elif block_number <= int(sys.argv[3]):
        try:
            prices[block_number] = get_price(uniswap.config())
        except ZeroDivisionError:
            pass
        lines.append(line)

'''
for line in fin.readlines():
    line_num += 1
    if line_num < int(sys.argv[2]):
        uniswap.process(line)
        config = uniswap.config()
    elif line_num <= int(sys.argv[3]):
        fout.write(line)
'''

print("Uniswap in 0", "{:.1f}".format(config['0']))
print("Uniswap in SAI", "{:.1f}".format(config['SAI']))
print(get_price(config))

bootstrapped_data(fout, config, lines)

plt.plot(list(prices.keys()), list(prices.values()))
plt.savefig('img/sai_prices.png')
