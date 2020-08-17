import re
from collections import defaultdict 


class Uniswap:
    def __init__(self):
        self.token_balances = defaultdict(lambda : 0)

    def process(self, tx):
        tx = tx.replace(';', '')
        
        if 'adds' in tx:
            self.add_liquidity(tx)
        elif 'removes' in tx:
            self.remove_liquidity(tx)
        elif 'input' in tx:
            self.input_swap(tx)
        elif 'output' in tx:
            self.output_swap(tx)
        elif tx.startswith('//'):
            pass
        else:
            print("ILLEGAL ", tx)

    def add_liquidity(self, tx):
        vals = re.match(r'(.*) adds (.*) tokens and (.*) eth of liquidity to (.*)', tx)
        self.token_balances['0'] += int(vals.group(3))
        self.token_balances[vals.group(4)] += int(vals.group(2))

        
    def remove_liquidity(self, tx):
        vals = re.match(r'(.*) removes (.*) tokens and (.*) eth of liquidity from (.*)', tx)
        self.token_balances['0'] -= int(vals.group(3))
        self.token_balances[vals.group(4)] -= int(vals.group(2))

    def input_swap(self, tx):
        vals = re.match(r'(.*) in (.*) swaps (.*) input for (.*) fee (.*)', tx)
        self.token_balances[vals.group(4)] -= ((997 * int(vals.group(3)) * self.token_balances[vals.group(4)]) / (1000 * self.token_balances[vals.group(2)] + 997 * int(vals.group(3)) ))
        self.token_balances[vals.group(2)] += int(vals.group(3))

    def output_swap(self, tx):
        vals = re.match(r'(.*) in (.*) swaps (.*) for (.*) output fee (.*)', tx)
        self.token_balances[vals.group(2)] += ((1000 * int(vals.group(3)) * self.token_balances[vals.group(2)]) / (997 * self.token_balances[vals.group(4)] - int(vals.group(3)) ) + 1)
        self.token_balances[vals.group(4)] -= int(vals.group(3))

    def config(self):
        return self.token_balances
