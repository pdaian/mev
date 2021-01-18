#!/bin/bash
num_cores=40
function limited_parallel {
   while [ `jobs | wc -l` -ge $num_cores ]
   do
      sleep 5
   done
}
for vault in `grep bite maker-data/mcd/latest-data/maker-processed/31358499851466632982272067240987752480060719095994161751935692443478204088320.csv | cut -d' ' -f 4`
do
    limited_parallel
    block=`grep -B 1 "bites vault $vault" maker-data/mcd/latest-data/maker-processed/31358499851466632982272067240987752480060719095994161751935692443478204088320.csv | head -n 1 | cut -d' ' -f 5`
    cmd="python3 run_mcd_experiments.py -sb $block -eb $block -cdp $vault &"
    echo $cmd
    eval $cmd
done
