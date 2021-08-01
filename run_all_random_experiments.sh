exchange=$1
for line in `cat boundary_blocks`
do
    start_block=`echo $line | cut -d, -f1`
    end_block=`echo $line | cut -d, -f2`
    month=`echo $line | cut -d, -f3`
    cmd="./run_random_experiments.sh $exchange $month $start_block $end_block"
    echo $cmd
    eval $cmd
done