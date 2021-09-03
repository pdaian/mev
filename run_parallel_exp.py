import os, time

for run in range(3):
    for i in [96, 81, 64, 49, 36, 25, 16, 11, 7, 5, 4, 3]:
        print("Running %d %d" % (i, run))
        os.system("rm -rf run-output")
        os.system("mkdir run-output")
        cmd = "python3 run_mcd_experiments.py -sb 10245709 -eb 10245722 -cdp 1424800597226405082122559358241526008447780662102 -n %d >> results " % (i)
        print(cmd)
        os.system(cmd)
        time.sleep(5)
