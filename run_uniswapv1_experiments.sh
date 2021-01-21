#!/bin/bash
exchange_name=uniswapv1
type=$1

waitforjobs() {
    while test $(jobs -p | wc -w) -ge "$1"; do wait -n; done
}

echo exchange,pair,token0,token1,block,numtransactions,mev
if [ "$type" = intractable ]; then
    for file in `ls -S data-scripts/latest-data/$exchange_name-processed/* | head -n 10`

    do
        temp=${file%.csv}
        address=${temp##*/}
        for block in `sort -rt, -k2 -n data-scripts/latest-data/active-region/$exchange_name/txcount_$address.csv | head -n 30 | cut -f1 -d,`
        do
            cmd="python3 run_uniswapv1_experiments.py -b $block -a $address -e $exchange_name &"
            waitforjobs 20
            eval $cmd
        done
    done
    
else
    rm -r /tmp/plot_mev/$exchange_name/
    mkdir -p /tmp/plot_mev/$exchange_name/
    for file in `ls -S data-scripts/latest-data/$exchange_name-processed/* | head -n 10`
    do
        temp=${file%.csv}
        address=${temp##*/}
        for block in `sort -rt, -k2 -n data-scripts/latest-data/active-region/$exchange_name/txcount_$address.csv | grep ,[0-9]$ | head -n 30 | cut -f1 -d,`
        do
            cmd="python3 run_uniswapv1_experiments.py -b $block -a $address -e $exchange_name -c &"
            waitforjobs 20
            eval $cmd
            cp experiments-uniswapv1/$block-$address/bound.k /tmp/plot_mev/$exchange_name/convergence-$block-$address.csv
        done
    done  
fi

