sushiswap_factory = "0xc0aee478e3658e2610c5f7a4a2e1777ce9e4f2ac"
uniswapv2_fctory = "0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f"

import pandas as pd
import csv
from exchanges import parse_address
token_counts = {}
pairs_to_tokens = {}


df = pd.read_csv('latest-data/all_logs_uniswapv2_factory.csv')
for _, row in df.iterrows():
    topics = row['topics'][1:-1]
    data = row['data'][2:]
    topics = topics.replace("'","").replace(" ", "").split(',')
    if len(topics) != 3:
        print(topics)
    else:
        address = parse_address(row['address'])
        token0_addr = parse_address(topics[1])
        token1_addr = parse_address(topics[2])
        if (address, token0_addr) not in token_counts:
            token_counts[(address, token0_addr)] = 0
        if (address, token1_addr) not in token_counts:
            token_counts[(address, token1_addr)] = 0
        token_counts[(address, token0_addr)] += 1
        token_counts[(address, token1_addr)] += 1
        pair_address = data[24:64]
        pairs_to_tokens[(address, pair_address)] = (token0_addr, token1_addr)
                        

uniswapv2_top_tokens = 'latest-data/uniswapv2_top_tokens.csv'
uniswapv2_pairs = 'latest-data/uniswapv2_pairs.csv'

with open(uniswapv2_top_tokens, 'w') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

    spamwriter.writerow("exchange,token,num_pairs".split(","))
    for address in token_counts:
        spamwriter.writerow(['0x'+address[0], '0x'+address[1], token_counts[(address)]])

with open(uniswapv2_pairs, 'w') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

    spamwriter.writerow("exchange,pair,token0,token1".split(","))
    for address in pairs_to_tokens:
        spamwriter.writerow(['0x'+address[0], '0x'+address[1], '0x'+pairs_to_tokens[address][0] , '0x'+pairs_to_tokens[address][1]])
