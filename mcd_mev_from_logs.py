import glob
from collections import defaultdict
import matplotlib.pyplot as plt

run_ids = set()
for filename in glob.glob('run-output/*'):
    id = filename[:filename.find('.out')]
    run_ids.add(id)
mev = defaultdict(lambda : 0)
block_to_mev = defaultdict(lambda : 0)
block_to_count = defaultdict(lambda : 0)
for id in run_ids:
    print(id)
    temp = id[:id.find('0x') - 1][-12 :]
    block = int(temp[temp.find('-') + 1 : ])
    for run_instance in glob.glob(id+'*'):
        lines = open(run_instance, 'r').readlines()
        for line in lines:
            if '|->' in line and ' 0 in DAI'in line:
                liquidated_debt = int(line.split()[-1])
                # mev is half the liquidation debt
                mev[id] = max(mev[id], liquidated_debt / 2)
    if id in mev:
        block_to_mev[block] += mev[id]
        block_to_count[block] += 1

print(run_ids - set(mev.keys()))
print(mev)
print(block_to_mev)
print(block_to_count)
