#!/bin/bash
exchange_name=$1
rm -r /tmp/plot_mev/$exchange_name/
mkdir -p /tmp/plot_mev/$exchange_name/
pairs_data=data-scripts/latest-data/data/uniswapv2_pairs.csv
echo exchange,pair,token0,token1,block,numtransactions,mev
#for file in `ls -S data-scripts/latest-data/$exchange_name-processed/0x* | head -n 10`
for file in `find data-scripts/latest-data/$exchange_name-processed/ -type f -exec wc -l {} + | sort -rn | tr -s ' ' | cut -d' ' -f3 | grep 0x | head -n 10`
do
    temp=${file%.csv}
    address=${temp##*/}
    for block in `sort -rt, -k2 -n data-scripts/latest-data/active-region/$exchange_name/txcount_$address.csv | head -n 30 | cut -f1 -d,`
    do
        cmd="python3 run_uniswapv2_experiments.py -b $block -a $address -e $exchange_name -c &"
        eval $cmd
        cp experiments/$block-$address/bound.k /tmp/plot_mev/$exchange_name/convergence-$block-$address.csv
    done
    wait
done
