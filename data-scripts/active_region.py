import sys
import os

input_dir = sys.argv[1]
output_dir = sys.argv[2]

for filename in os.listdir(input_dir):
    fin = open(os.path.join(input_dir,filename), 'r')
    outfile = os.path.join(output_dir, 'txcount_' + filename)

    block_to_numTx = {}
    
    lines = fin.readlines()

    fout = open(outfile, 'w')
    fout.write("Block,TxCount\n")
    for i in range(0,len(lines), 2):
        block_num = lines[i].strip().split(" ")[-1]
        if block_num not in block_to_numTx:
            block_to_numTx[block_num] = 0
        block_to_numTx[block_num] += 1
    

    for block in block_to_numTx:
        fout.write(str(block) + "," + str(block_to_numTx[block]) + "\n")

    fout.close()
