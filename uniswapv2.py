import re
from collections import defaultdict 


class UniswapV2:
    def __init__(self, balances={}, exchange_name='UniswapV2'):
        self.exchange_name = exchange_name
        self.token_balances = defaultdict(lambda : defaultdict(lambda : 0))
        self.token_balances[self.exchange_name] = balances

    def process(self, tx):
        tx = tx.replace(';', '').strip()
        
        if 'adds' in tx:
            self.add_liquidity(tx)
        elif 'removes' in tx:
            self.remove_liquidity(tx)
        elif 'swaps' in tx:
            self.swap(tx)
        elif tx.startswith('//'):
            pass
        else:
            print("ILLEGAL ", tx)

    def add_liquidity(self, tx):
        vals = re.match(r'(.*) adds (.*) (.*) and (.*) (.*) of liquidity', tx)
        token0 = vals.group(3)
        token1 = vals.group(5)
        amount0 = int(vals.group(2))
        amount1 = int(vals.group(4))
        address = vals.group(1)
        self.token_balances[self.exchange_name][token0] += amount0
        self.token_balances[self.exchange_name][token1] += amount1
        self.token_balances[address][token0] -= amount0
        self.token_balances[address][token1] -= amount1

        
    def remove_liquidity(self, tx):
        vals = re.match(r'(.*) removes (.*) (.*) and (.*) (.*) of liquidity', tx)
        token0 = vals.group(3)
        token1 = vals.group(5)
        amount0 = int(vals.group(2))
        amount1 = int(vals.group(4))
        address = vals.group(1)
        self.token_balances[self.exchange_name][token0] -= amount0
        self.token_balances[self.exchange_name][token1] -= amount1
        self.token_balances[address][token0] += amount0
        self.token_balances[address][token1] += amount1

        
    def swap(self, tx):
        vals = re.match(r'(.*) swaps for (.*) by providing (.*) (.*) and (.*) (.*) with change (.*) fee (.*)', tx)
        address = vals.group(1)
        token_in = vals.group(4)
        token_out = vals.group(6)
        amount_in_token_in = int(vals.group(3))
        amount_in_token_out = int(vals.group(5))
        amount_out_token_in = int(vals.group(7))

        amount_out_token_out = (((997 * amount_in_token_in - 1000 * amount_out_token_in) * self.token_balances[self.exchange_name][token_out]) // (1000 * (self.token_balances[self.exchange_name][token_in] - amount_out_token_in) + 997 * amount_in_token_in)) + ((amount_in_token_out * 997) // (1000))
        
        self.token_balances[self.exchange_name][token_in] += amount_in_token_in - amount_out_token_in
        self.token_balances[self.exchange_name][token_out] += amount_in_token_out - amount_out_token_out
        self.token_balances[address][token_in] += amount_out_token_in - amount_in_token_in
        self.token_balances[address][token_out] += amount_out_token_out - amount_in_token_out

    
    def config(self):
        return self.token_balances
