#!/bin/bash
exchange_name=$1
rm -r /tmp/plot_mev/$exchange_name/
mkdir -p /tmp/plot_mev/$exchange_name/
cmds_file=tractable_cmds_all
rm -f $cmds_file

waitforjobs() {
    while test $(jobs -p | wc -w) -ge "$1"; do wait -n; done
}


echo exchange,pair,token0,token1,block,numtransactions,mev

for file in `find data-scripts/latest-data/$exchange_name-processed/ -type f -exec wc -l {} + | sort -rn | tr -s ' ' | cut -d' ' -f3 | grep 0x | head -n 10`
do
    temp=${file%.csv}
    address=${temp##*/}
    for block in `sort -rt, -k2 -n data-scripts/latest-data/active-region/$exchange_name/txcount_$address.csv | grep ,[0-9]$ | head -n 30 | cut -f1 -d,`
    do
        cmd="python3 run_uniswapv2_experiments.py -b $block -a $address -e $exchange_name -c &"
        echo $cmd >> $cmds_file
        waitforjobs 20
        eval $cmd
        cp experiments/$block-$address/bound.k /tmp/plot_mev/$exchange_name/convergence-$block-$address.csv

    done
    #wait
done
