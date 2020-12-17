
sushiswap_factory = "0xc0aee478e3658e2610c5f7a4a2e1777ce9e4f2ac"
uniswapv2_fctory = "0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f"

import pandas as pd
from exchanges import parse_address
token_counts = {}
sushiswap_pairs = set()
uniswapv2_pairs = set()


df = pd.read_csv('latest-data/all_logs_uniswapv2_factory.csv')
for _, row in df.iterrows():
    topics = row['topics'][1:-1]
    data = row['data'][2:]
    topics = topics.replace("'","").replace(" ", "").split(',')
    if len(topics) != 3:
        print(topics)
    else:
        token0_addr = parse_address(topics[1])
        token1_addr = parse_address(topics[2])
        if token0_addr not in token_counts:
            token_counts[token0_addr] = 0
        if token1_addr not in token_counts:
            token_counts[token1_addr] = 0
        token_counts[token0_addr] += 1
        token_counts[token1_addr] += 1
        if row['address'] == sushiswap_factory :
            pair_address = data[24:64]
            sushiswap_pairs.add(pair_address)
            print(pair_address)
        elif row['address'] == uniswapv2_fctory:
            pair_address = data[24:64]
            uniswapv2_pairs.add(pair_address)
            print(pair_address)
                        

sushiswap_file = 'latest-data/sushiswap_relayers'
f_sushiswap = open(sushiswap_file, 'w')
for pair_address in sushiswap_pairs:
    f_sushiswap.write('0x'+ pair_address + '\n')

uniswapv2_file = 'latest-data/uniswapv2_relayers'
f_uniswapv2 = open(uniswapv2_file, 'w')
for pair_address in uniswapv2_pairs:
    f_uniswapv2.write('0x' + pair_address + '\n')
