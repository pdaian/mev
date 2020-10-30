import pandas as pd
from exchanges import get_node_label_for

#df = pd.read_csv('../sushiswap_mev.csv')
df = pd.read_csv('../uniswapv1_mev.csv')
name_file = 'data/token_names.csv'
name_dict = pd.read_csv(name_file).to_dict('list')

print(name_dict)

#for token in set(df.token0).union(set(df.token1)):
for token in set(df.token0).union(set(df.token1)):   
    token_address = str(hex(int(token)))[2:]
    token_address = '0'*(40-len(token_address)) + token_address
    symbol = get_node_label_for(token_address)[0]
    name_dict['name'].append(symbol)
    name_dict['address'].append(token)
name_df = pd.DataFrame(name_dict).drop_duplicates()
name_df.to_csv(name_file, index=False)
