runs=3
start=10245709
end=10245722
cdp=1424800597226405082122559358241526008447780662102
python3 run_mcd_experiments.py -sb $start -eb $end -cdp $cdp -n 96
waitforjobs() {
    while test $(jobs -p | wc -w) -ge "$1"; do wait -n; done
}
for run in $(seq $runs)
do
	for i in {96,81,64,49,36,25,16,11,7,5,4,3}
	do
		starttime=`date +%s`
		for file in experiments-mcd-uniswapv2/$cdp-$start-$end-0xa478c2975ab1ea89e8196811f51a7b7ade33eb11/bound.k*
		do
			krun $file > /dev/null &
			waitforjobs $i
		done
		endtime=`date +%s`
		delta=$(( $endtime - $starttime ))
		echo $run,$i,$delta	
	done
done

