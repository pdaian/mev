#!/bin/bash
exchange_name=uniswapv1
echo exchange,pair,token0,token1,block,numtransactions,mev
for file in `ls -S data-scripts/latest-data/$exchange_name-processed/* | head -n 10`
do
    temp=${file%.csv}
    address=${temp##*/}
    for block in `sort -rt, -k2 -n data-scripts/latest-data/active-region/$exchange_name/txcount_$address.csv | grep ,[0-9]$ | head -n 30 | cut -f1 -d,`
    #for block in `sort -rt, -k2 -n data-scripts/latest-data/active-region/$exchange_name/txcount_$address.csv | head -n 30 | cut -f1 -d,`
    do
        cmd="python3 run_uniswapv1_experiments.py -b $block -a $address -e $exchange_name &"
        #echo $cmd
        eval $cmd
        mkdir -p /tmp/plot_mev/$exchange_name/
        cp experiments-uniswapv1/$block-$address/bound.k /tmp/plot_mev/$exchange_name/convergence-$block-$address.csv
    done
    wait
done

