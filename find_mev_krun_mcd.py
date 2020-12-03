import os
import sys
from subprocess import Popen, PIPE
import re
from pathlib import Path
import itertools
import random

def all_orderings(all_transactions):
    num_transactions = len(all_transactions)
    if num_transactions < 10:
        ret = list(itertools.permutations(all_transactions))
        random.shuffle(ret)
    else:
        ret = []
        for i in range(400000):
            ret.append(random.sample(all_transactions, num_transactions))

    print("Num all reorderings ", len(ret))
    return ret


def valid_ordering(transaction_ordering):
    '''
    for transaction in transaction_ordering:
        if 'locks' in transaction:
            return True
        elif 'draws' in transaction:
            return False
    '''
    return True

def reordering_mev(program, program_file, outfile, acc, pair_address, maker_prologue, maker_epilogue):

    program = program.strip()

    
#    addresses = set()
    transactions = program.split('\n')
    all_transactions = [transaction for transaction in transactions if not transaction.strip().startswith('//')]
    '''
    print(all_transactions)
    for i in range(0, len(all_transactions)):
        chunks = all_transactions[i].split()
        #print(chunks)
        addresses.add(chunks[0])

    #print(addresses)

    lower_balance_bounds = {}
    upper_balance_bounds = {}

    MAX = 99999999999999999999999999999999
    MIN = -99999999999999999999999999999999
    
    for address in addresses:
        lower_balance_bounds[address] = {tokens[0] : MAX, tokens[1] : MAX}
        upper_balance_bounds[address] = {tokens[0] : MIN, tokens[1] : MIN}
    '''

    PROLOGUE = maker_prologue + '\n'
    
    path_num = 0
    for transaction_ordering in all_orderings(all_transactions):
        output = ""
        Path(os.path.dirname(program_file)).mkdir(parents=True, exist_ok=True)
        #print("Writing program to", program_file)
        open(program_file, "w").write(PROLOGUE + '\n'.join(transaction_ordering) + maker_epilogue)
        sys.stdout.flush()
        pipe = Popen("krun " + program_file, shell=True, stdout=PIPE, stderr=PIPE)
        output = pipe.stdout.read() + pipe.stderr.read()
        output = str(output, "utf-8")
        outfilename = outfile+str(path_num)
        print("Writing output to", outfilename, "...")
        open(outfilename, "w").write(output)
        path_num += 1

