import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

exchange_name = 'uniswapv2'
if exchange_name == 'uniswapv2':
    exchange_acc = 'UniswapV2'
elif exchange_name == 'sushiswap':
    exchange_acc = 'Sushiswap'


df = pd.read_csv(exchange_name + '_mev.csv')
token_names = pd.read_csv('data-scripts/data/token_names.csv').set_index('address').T.to_dict('records')[0]
df['name0'] = df['token0'].map(token_names)
df['name1'] = df['token1'].map(token_names)

#df['pair'] = df['pair'].str.slice(2,8) + '..'
#print(df)

df['pair_name'] = df['name0'] + '/' + df['name1']

max_mev = df.sort_values('mev', ascending=False).drop_duplicates(['pair'])

print(max_mev[['pair', 'block', 'mev', 'pair_name']])

#df = df.groupby('pair')['mev'].apply(lambda x: pd.Series(x.values)).unstack()

#ax = df.plot(kind='bar', stacked=True, legend=None)
ax = max_mev.plot('pair_name', 'mev', kind='bar', legend=None)
ax.set_ylabel('MEV (in ETH) * 1e18')
ax.set_xlabel('Pair')
plt.xticks(rotation=20)
plt.title(exchange_acc + ' MEV ')
#plt.legend(title='UniswapV2 MEV', bbox_to_anchor=(1.0, 1), loc='upper left')
plt.savefig(exchange_name + '-mev.png')
plt.show()
