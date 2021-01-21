import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from cycler import cycler
import sys

#exchange_name = 'uniswapv2'
#exchange_name = 'uniswapv1'
#exchange_name = 'sushiswap'

exchange_name = sys.argv[1]

if exchange_name == 'uniswapv2':
    token_file = 'token_names.csv'
    exchange_acc = 'UniswapV2'
elif exchange_name == 'sushiswap':
    token_file = 'token_names.csv'
    exchange_acc = 'Sushiswap'
elif exchange_name == 'uniswapv1':
    exchange_acc = 'UniswapV1'
    token_file = 'v1_token_names.csv'


# Full MEV
df = pd.read_csv(exchange_name + '_mev.csv')
token_names = pd.read_csv(token_file).set_index('address').T.to_dict('records')[0]
print(token_names)
df['name0'] = df['token0'].map(token_names)
df['name1'] = df['token1'].map(token_names)

if exchange_name == 'uniswapv1':
    df['name0'] = 'ETH'

df['pair_name'] = df['name0'] + '/' + df['name1']

max_mev = df.sort_values('mev', ascending=False).drop_duplicates(['pair'])

max_mev['mev'] = max_mev['mev'] / 10**18 #KB

print(max_mev[['pair', 'block', 'mev', 'pair_name']])

# APPROX MEV
df2 = pd.read_csv(exchange_name + '_approx_mev.csv')
df2['name0'] = df2['token0'].map(token_names)
df2['name1'] = df2['token1'].map(token_names)

if exchange_name == 'uniswapv1':
    df2['name0'] = 'ETH'


df2['pair_name'] = df2['name0'] + '/' + df2['name1']

approx_max_mev = df2.sort_values('mev', ascending=False).drop_duplicates(['pair'])

approx_max_mev['mev'] = approx_max_mev['mev'] / 10**18 #KB

print(approx_max_mev[['pair', 'block', 'mev', 'pair_name']])


# plot
ax = approx_max_mev.plot('pair_name', 'mev', kind='bar', color='#ff7f00', label='Intractable Blocks', position=0, width=0.4, hatch='\\', edgecolor='gray')
ax.set_ylabel('MEV (in ETH)')
ax.set_xlabel('Pair')
max_mev.plot('pair_name', 'mev', kind='bar', ax=ax, color='#377eb8', label='Tractable Blocks', position=1, width=0.4)

plt.xticks(rotation=20)
plt.title(exchange_acc + ' MEV ')
plt.savefig(exchange_name + '-mev.pdf')
