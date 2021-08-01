#!/bin/bash

# AMM

# get data

python3 get_uniswapv2_pairs.py
python3 get_uniswapv2_relayers.py
python3 get_uswapv2_logs.py

python3 get_bq_relayers.py
python3 get_uswap_logs.py

#process data

mkdir -p latest-data/uniswapv1-processed
mkdir -p latest-data/uniswapv2-processed
mkdir -p latest-data/sushiswap-processed


python3 uniswap_trades.py &> uniswap_trades.nohup

python3 get_top_uniswapv2_pairs.py
python3 uniswapv2_trades.py sushiswap &> sushiswap_trades.nohup
python3 uniswapv2_trades.py uniswapv2 &> uniswapv2_trades.nohup
python3 uniswapv2_reserves.py -e sushiswap &> sushiswap_reserves.nohup
python3 uniswapv2_reserves.py -e uniswapv2 &> uniswapv2_reserves.nohup

mkdir -p latest-data/active-region/sushiswap
mkdir -p latest-data/active-region/uniswapv2
mkdir -p latest-data/active-region/uniswapv1

python3 active_region.py latest-data/uniswapv1-processed/ latest-data/active-region/uniswapv1/
python3 active_region.py latest-data/sushiswap-processed/ latest-data/active-region/sushiswap/
python3 active_region.py latest-data/uniswapv2-processed/ latest-data/active-region/uniswapv2/

