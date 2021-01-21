#!/bin/bash

./run_tractable_experiments.sh sushiswap > sushiswap_mev.csv 2> sushiswap_mev.err &
./run_intractable_experiments.sh sushiswap > sushiswap_approx_mev.csv 2> sushiswap_approx_mev.err &
wait
./run_intractable_experiments.sh uniswapv2 > uniswapv2_approx_mev.csv 2> uniswapv2_approx_mev.err &
./run_tractable_experiments.sh uniswapv2 > uniswapv2_mev.csv 2> uniswapv2_mev.err &
