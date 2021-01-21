import os
import sys
from subprocess import Popen, PIPE
import re
from pathlib import Path
import itertools
import random

def all_orderings(all_transactions):
    ret = list(itertools.permutations(all_transactions))
    random.shuffle(ret)
    return ret

def reordering_mev(program, program_file, outfile, acc, tokens, balances, pre_price, post_price, pair_address, blocknum, convergence):

    program = program.strip()

    addresses = set()
    transactions = program.split('\n')
    all_transactions = [transaction for transaction in transactions if not transaction.strip().startswith('//')]
    print(all_transactions)
    for i in range(0, len(all_transactions)):
        chunks = all_transactions[i].split()
        print(chunks)
        addresses.add(chunks[0])

    print(addresses)

    lower_balance_bounds = {}
    upper_balance_bounds = {}

    MAX = 99999999999999999999999999999999
    MIN = -99999999999999999999999999999999
    
    for address in addresses:
        lower_balance_bounds[address] = {tokens[0] : MAX, tokens[1] : MAX}
        upper_balance_bounds[address] = {tokens[0] : MIN, tokens[1] : MIN}

    PROLOGUE = """{acc} in {token0} gets {balance0} ;
    {acc} in {token1} gets {balance1} ;
    """.format(acc=acc, token0=tokens[0], token1=tokens[1], balance0=balances[0], balance1=balances[1])
    path_num = 0
    for transaction_ordering in all_orderings(all_transactions):
        output = ""
        Path(os.path.dirname(program_file)).mkdir(parents=True, exist_ok=True)
        #print("Writing program to", program_file)
        open(program_file, "w").write(PROLOGUE + '\n'.join(transaction_ordering))
        sys.stdout.flush()
        pipe = Popen("krun " + program_file, shell=True, stdout=PIPE, stderr=PIPE)
        output = pipe.stdout.read() + pipe.stderr.read()
        output = str(output, "utf-8")
        outfilename = outfile+str(path_num)
        print("Writing output to", outfilename, "...")
        open(outfilename, "w").write(output)
        path_num += 1

def main():
    PROGRAM = open('data/' + sys.argv[1]).read()
    program_file = sys.argv[1]+'/bound.k'
    outfile = 'output/'+sys.argv[1]+'.out'
    find_mev_cdp(PROGRAM, program_file, outfile, 155042, 155042)

if __name__ == '__main__':
    main()
