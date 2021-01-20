import os, time

for run in range(3):
    for i in [1, 2, 4, 9, 16, 25, 36, 49, 64, 81, 96]:
        print("Running %d %d" % (i, run))
        os.system("rm -rf run-output")
        os.system("mkdir run-output")
        run = "time -o time-%d-%d python3 run_mcd_experiments.py -sb 10245709 -eb 10245722 -cdp 1424800597226405082122559358241526008447780662102 -n %d" % (i, run, i)
        print(run)
        os.system(run)
        time.sleep(5)
