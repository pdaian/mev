import os
import sys
from subprocess import Popen, PIPE
import re
from pathlib import Path
import itertools
import random
import concurrent.futures

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

def reordering_mev(program, program_file, outfile, acc, pair_address, maker_prologue, maker_epilogue, num_workers):

    num_workers = int(num_workers)
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


    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        for transaction_ordering in all_orderings(all_transactions):
            executor.submit(process_tx_order, transaction_ordering, program_file, PROLOGUE, maker_epilogue, outfile, path_num)
            path_num += 1



def process_tx_order(transaction_ordering, program_file, prologue, maker_epilogue, outfile, path_num):
    output = ""
    Path(os.path.dirname(program_file)).mkdir(parents=True, exist_ok=True)
    #print("Writing program to", program_file)
    f = open(program_file + str(path_num), "w")
    f.write(prologue + '\n'.join(transaction_ordering) + maker_epilogue)
    f.flush()
    os.fsync(f.fileno())
    f.close()
    # sys.stdout.flush()
    # pipe = Popen("krun " + program_file, shell=True, stdout=PIPE, stderr=PIPE)
    # output = pipe.stdout.read() + pipe.stderr.read()
    # output = str(output, "utf-8")
    # outfilename = outfile+str(path_num)
    # print("Writing output to", outfilename, "...")
    # f = open(outfilename, "w")
    # f.write(output)
    # f.close()
