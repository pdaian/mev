import sys
from collections import defaultdict
f = open('latest-data/maker-processed/31358499851466632982272067240987752480060719095994161751935692443478204088320.csv', 'r')


block_to_fees = defaultdict(lambda : {})
block_number = 0
cumfees = 10**27

fout = open('latest-data/maker_fees.csv', 'w')

for line in f.readlines():
    line = line.replace(';','').strip()
    if 'block' in line:
        words = line.split()
        block_number = int(words[-1])
    elif 'increment' in line:
        words = line.split()
        increment = int(words[0])
        cumfees += increment
        block_to_fees[block_number] = cumfees

fout.write('Block,Fees\n')        
for block in sorted(block_to_fees):
    fout.write("%d,%d\n" %(block, block_to_fees[block]))
    
