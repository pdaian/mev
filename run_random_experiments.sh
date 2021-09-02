#!/bin/bash
exchange_name=$1
month=$2
cmds_file=random_cmds_all_${exchange_name}_${month}
rm -f $cmds_file
results_file=validate_random_${exchange_name}_${month}
rm -f $results_file

waitforjobs() {
    while test $(jobs -p | wc -w) -ge "$1"; do wait -n; done
}


echo exchange,pair,token0,token1,block,numtransactions,mev



for sample in `python3 get_random_blocks.py -m $month -e $exchange_name -n 1000`
do
    date=`echo $sample | cut -d, -f1 `
    block=`echo $sample | cut -d, -f2 `
    relayers=`echo $sample | awk -F "," '{$1=$2=$3=""; print $0}'`
    cmd="python3 run_uniswapv2_experiments.py -b $block -e $exchange_name -d $date -a " 
    for relayer in `echo $relayers`
    do
        cmd="${cmd} ${relayer}"
    done
    cmd="${cmd} -p ${results_file} &"
    echo $cmd
    echo $cmd >> $cmds_file
    waitforjobs 25
    eval $cmd
done
