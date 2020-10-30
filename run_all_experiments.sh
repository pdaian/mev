#!/bin/bash
exchange_name=uniswapv2
pairs_data=data-scripts/data/uniswapv2_pairs.csv
echo exchange,pair,token0,token1,block,numtransactions,mev
for file in `ls -S data-scripts/$exchange_name-processed/0x* | head -n 10`
do
    temp=${file%.csv}
    address=${temp##*/}
    #for block in `sort -rt, -k2 -n data-scripts/active-region/$exchange_name/txcount_$address.csv | grep ,[0-9]$ | head -n 5 | cut -f1 -d,`
    for block in `sort -rt, -k2 -n data-scripts/active-region/$exchange_name/txcount_$address.csv | head -n 10 | cut -f1 -d,`
    do
        cmd="time python3 run_uniswapv2_experiments.py -b $block -a $address -e $exchange_name &"
        #echo $cmd
        #eval $cmd
        mkdir -p /tmp/plot_approx_mev/$exchange_name/
        cp experiments/$block-$address/bound.k /tmp/plot_approx_mev/$exchange_name/convergence-$block-$address.csv
    done
    wait
done
