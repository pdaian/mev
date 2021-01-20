import pandas as pd
from functools import reduce


exchange_name = 'uniswapv2'
collateral_type = '31358499851466632982272067240987752480060719095994161751935692443478204088320'
pair_address = '0xa478c2975ab1ea89e8196811f51a7b7ade33eb11'

reserves = pd.read_csv('data-scripts/latest-data/%s-reserves.csv' % (exchange_name))
reserves.Block = reserves.Block.astype(int)
reserves = reserves[reserves.Address == pair_address]

start_block = reserves.Block.min()
end_block = reserves.Block.max()


cdp_states = pd.read_csv('maker-data/mcd/latest-data/cdp_states.csv')
cdp_states = cdp_states[cdp_states.Collateral_type == collateral_type]
cdp_states.Block = cdp_states.Block.astype(int)
cdp_states['tx_count'] = cdp_states.groupby('CDP').cumcount()

rates = pd.read_csv('maker-data/mcd/latest-data/maker_fees.csv')
rates.Fees = rates.Fees.astype(float)
rates.Block = rates.Block.astype(int)

oracle_prices = pd.read_csv('maker-data/mcd/latest-data/spot_prices.csv')
oracle_prices = oracle_prices[oracle_prices.CollateralType == collateral_type]
oracle_prices.Block = oracle_prices.Block.astype(int)
oracle_prices.SpotPrice = oracle_prices.SpotPrice.astype(float)


#filter before merging
rates = rates[(rates.Block <= end_block) & (rates.Block >= start_block)]
cdp_states = cdp_states[(cdp_states.Block <= end_block) & (cdp_states.Block >= start_block)]
oracle_prices = oracle_prices[(oracle_prices.Block <= end_block) & (oracle_prices.Block >= start_block)]


rates.set_index('Block', inplace=True)
cdp_states.set_index('Block', inplace=True)
reserves.set_index('Block', inplace=True)
oracle_prices.set_index('Block', inplace=True)


dfs = [cdp_states, reserves, rates, oracle_prices]

df_merged = reduce(lambda  left,right: pd.merge(left,right,on=['Block'], how='outer'), dfs)
df_merged = df_merged.reset_index().sort_values('Block', kind='mergesort') #mergesort for stable sort
df_merged = df_merged.fillna(method='ffill').dropna()

df_merged.Collateral = (df_merged.Collateral.astype(float) / 10**18)

df_merged.Debt = (df_merged.Debt.astype(float) / 10**18)
df_merged['Tab'] = df_merged.Debt * df_merged.Fees / 10**27
df_merged.Reserve0 = df_merged.Reserve0.astype(float)
df_merged.Reserve1 = df_merged.Reserve1.astype(float)

df_merged['Uniswap_price'] = df_merged['Reserve0'] / df_merged['Reserve1']

df = df_merged[['Block', 'Tab', 'Collateral', 'Uniswap_price',  'Reserve0', 'Reserve1', 'SpotPrice', 'Debt', 'CDP', 'tx_count']]

#filter out CDPs without debt
df = df[df.Tab > 0]

df['Uniswap_ratio'] = ( (df.Collateral * df.Uniswap_price) / (df.Tab) )
df['Oracle_ratio'] = ( (df.Collateral * df.SpotPrice) / (df.Tab * 10**27) ) * 1.5

df = df.sort_values('Uniswap_ratio')
fd = df[df.Debt > 0]
filtered = fd[(fd.Tab > 300) & (fd.Oracle_ratio > 1.5) & (fd.Uniswap_ratio > 1.5)].drop_duplicates('CDP')
filtered2 = fd[(fd.Tab > 300) & (fd.Oracle_ratio > 1.5)].drop_duplicates('CDP')

filtered.to_csv('insertion_targets.csv', index=False)

filtered2.to_csv('easy_targets.csv', index=False)
