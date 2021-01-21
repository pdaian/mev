#!/bin/bash
exchange_name=$1
cmds_file=intractable_cmds_all
rm -f $cmds_file

waitforjobs() {
    while test $(jobs -p | wc -w) -ge "$1"; do wait -n; done
}

echo exchange,pair,token0,token1,block,numtransactions,mev

for file in `find data-scripts/latest-data/$exchange_name-processed/ -type f -exec wc -l {} + | sort -rn | tr -s ' ' | cut -d' ' -f3 | grep 0x | head -n 10`
do
    temp=${file%.csv}
    address=${temp##*/}
    for block in `sort -rt, -k2 -n data-scripts/latest-data/active-region/$exchange_name/txcount_$address.csv | head -n 30 | cut -f1 -d,`
    do
        cmd="python3 run_uniswapv2_experiments.py -b $block -a $address -e $exchange_name &"
        echo $cmd >> $cmds_file
        waitforjobs 15
        eval $cmd
    done
    #wait
done
