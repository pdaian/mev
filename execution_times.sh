#!/bin/bash
TIMEFORMAT=%R,%U,%S
WORK_DIR=$(HOME)/github-mev
RESULTS_FILE=$WORK_DIR/results/uniswapv2_execution_time.csv
echo TxCount,RealTime,UserTime,SysTime,Filename > $RESULTS_FILE
for file in `ls -rS $WORK_DIR/data-scripts/latest-data/uniswapv2-processed/0x*.csv`
do
    lines=`wc -l $file | awk '{print $1}'`
    num_tx=$(( $lines / 2 ))
    num_sampled=`grep "^$num_tx," $RESULTS_FILE | wc -l`
    if [ $num_sampled -lt 2 ]
    then
        runtime=$({ time krun $file ; } 2>&1 >/dev/null)
        echo $num_tx,$runtime,$file >> $RESULTS_FILE
    fi
done
