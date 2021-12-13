import requests
import sys
import json

DEBUG = True
id = 0
def storage(address, index, block):
    global id
    data = {}
    data['jsonrpc'] = '2.0'
    data['method'] = 'eth_getStorageAt'
    data['params'] = [address, index, block]
    data['id'] = id
    id += 1
    r = requests.post('http://localhost:8545', json=data)
    response = json.loads(r.content)
    if DEBUG:
        # print(data)
        print(response['result'])
        if int(response['result'], 16) == int('0x6e71edae12b1b97f4d1f60370fef10105fa2faae0126114a169c64845d6126c9',16):
            print('voila!!!')
    
def call(address, block):
    global id
    data = {}
    data['jsonrpc'] = '2.0'
    data['method'] = 'eth_call'
    data['params'] = [{"to":address, "data":"0x0"}, block]
    data['id'] = id
    id += 1
    r = requests.post('http://localhost:8545', json=data)
    response = json.loads(r.content)
    if DEBUG:
        # print(data)
        print(response)

address = '0x397ff1542f962076d0bfe58ea045ffa2d347aca0'
block_number = 13770000
block = hex(block_number+1)

for index in range(0,100):
    storage(address, hex(index), block)

# call(address, block)