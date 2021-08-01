import requests
import sys
import json

DEBUG = False

def check_response(response):
    if 'result' not in response:
        print(response)
        return -2
    for result in response['result']['results']:
        if 'error' in result:
            print(response['id'], result)
            return -1
    return 0
    

def simulate(block, txs, id):
    data = {}
    data['jsonrpc'] = '2.0'
    data['method'] = 'eth_callBundle'
    data['params'] = [txs, block]
    data['id'] = id
    r = requests.post('http://localhost:8545', json=data)
    response = json.loads(r.content)
    if DEBUG:
        print(data)
        print(response)
    return check_response(response)

def total_mev(blocks, attacks):
    ret = 0.0
    for block in blocks:
        ret += attacks[block]['mev']
    return ret
    
filename = sys.argv[1]

attacks = {}

f = open(filename, 'r')
for line in f.readlines():
    tokens = line.strip().split(',')
    block = hex(int(tokens[0]) - 1)
    transactions = [x for x in tokens if x.startswith('0x')]
    if len(transactions) == 0:
        continue
    if block not in attacks:
        attacks[block] = {}
    attacks[block]['mev'] = float(tokens[1])
    if tokens[2] == '1':
        attacks[block]['upper'] = transactions
    elif tokens[2] == '0':
        attacks[block]['lower'] = transactions
    # if len(attacks) == 6:
    #     break

total = []
tried = []
valid = []
pre_checked = []

for block in attacks:
    total.append(block)
    if len(attacks[block]['upper']) == len(set(attacks[block]['upper'])):
        # no duplicate transactions
        tried.append(block)
        u = simulate(block, attacks[block]['upper'], block)
        l = simulate(block, attacks[block]['lower'], block)
        if u!=-2 and l!=-2:
            pre_checked.append(block)
        if u==0 and l==0:
            valid.append(block)
    print("Total: {}, Tried: {}, Valid: {}, Pre-Checked: {}".format(len(total), len(tried), len(valid), len(pre_checked)))
print(json.dumps([total, tried, valid, pre_checked]))
print("Total: {}, Tried: {}, Valid: {}, Pre-Checked: {}".format(len(total), len(tried), len(valid), len(pre_checked)))
print("Total mev: {}, Tried mev: {}, Valid mev: {}, Pre-Checked mev: {}".format(total_mev(total, attacks), total_mev(tried, attacks), total_mev(valid, attacks), total_mev(pre_checked, attacks)))
    
