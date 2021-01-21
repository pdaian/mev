import matplotlib
matplotlib.use('Agg')
import pandas as pd
import argparse
from matplotlib import pyplot as plt
import numpy as np
from cycler import cycler
import glob #KB
import sys

exchange_name = sys.argv[1]
if exchange_name == 'uniswapv1':
    exchange = 'Uniswap V1'
elif exchange_name == 'uniswapv2':
    exchange = 'Uniswap V2'
elif exchange_name == 'sushiswap':
    exchange = 'Sushiswap'

filenames = glob.glob(exchange_name + "/*")

dataframes = []

# for filename in filenames:
#     df = pd.read_csv(filename)
#     df['mev'] = df['mev'] / df['mev'].max() * 100
#     df['pathfrac'] = df['pathnum'] / df['pathnum'].max() * 100
#     x = []
#     y = []
#     for index, row in df.iterrows():
#         x = x + [row['pathfrac']]
#         y = y + [row['mev']]
#     dataframes.append((x,y))




# for (x,y) in dataframes:
#     plt.plot(x,y)      
# plt.savefig('convergence_random.pdf')


max_path = 0

for filename in filenames:
    try:
        df = pd.read_csv(filename)
    except pd.errors.EmptyDataError:
        continue
    try:
        if df['mev'].max() <  1:
            continue
        df['mev'] = df['mev'] / df['mev'].max() * 100
    except TypeError:
        print(filename,df)
        continue
    max_path = max(max_path, df['pathnum'].max())
    df['pathfrac'] = df['pathnum'] / df['pathnum'].max() * 100
    df['pathfrac'] = df['pathfrac'].round(6)

    df.set_index('pathfrac', inplace=True)
    df = df.drop(columns='pathnum')
    #df.set_index('pathnum', inplace=True)
    dataframes.append(df)

df = pd.concat(dataframes,axis=1,sort=False).fillna(method='ffill').fillna(0)

'''
x = list(range(max_path))
df['min'] = df.min(axis=1)
df['med'] = df.median(axis=1)
df['first'] = df.quantile(0.25, axis=1)
df['third'] = df.quantile(0.75, axis=1)
df['max'] = df.max(axis=1)

# for num in range(max_path):
#     x += [num]
#     y += df.groupby(df.index)

colors=['#377eb8','#ff7f00','#4daf4a','#f781bf','#a65628','#984ea3','#999999','#e41a1c','#dede00']
all_y = [('first', 'Q1',1) , ('med', 'Median',2), ('third', 'Q3',1), ('max', 'Max',1)]
fig, ax = plt.subplots()
custom_cycler = (cycler(color=['#377eb8','#ff7f00','#4daf4a','#f781bf','#a65628']) +
                 cycler(linestyle=['solid', 'dotted', 'dashed','dashdot', 'solid']))

ax.set_prop_cycle(custom_cycler)
df.plot(y='min', logx=True, label='Min', ax=ax)

for col, lbl,lw in all_y:
    df.plot(y=col, logx=True, label=lbl, ax = ax, lw=lw)

plt.xlabel('Percentage of Paths Explored')
plt.ylabel('MEV Convergence Percentile')
plt.title(exchange + ' MEV Convergence')
# plt.xlim(0, 100)
plt.ylim(-5, 105)
#df.plot(logx=True)
plt.savefig('convergence-'+exchange_name+'.pdf')
'''
