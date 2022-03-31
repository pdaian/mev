from sympy import *
from sympy.parsing.sympy_parser import parse_expr
from sympy.unify.usympy import *


def can_unify(eq1, eq2, substitutions):
    # process equations into symbolic python library sympy
    # expand into standard polynomial form
    try:
        for substitution in substitutions:
            eq1 = eq1.replace(substitution[0], substitution[1])
            eq2 = eq2.replace(substitution[0], substitution[1])
        print("Attempting to unify", eq1, "\n", eq2)
        eq1 = expand(parse_expr(eq1))
        eq2 = expand(parse_expr(eq2))
        print("Attempting to unify", eq1, eq2)
        print("SUBSTITUTION SUCCESSFUL", next(unify(eq1, eq2, variables=eq1.free_symbols)))
        return True
    except:
        return False


# decomposition of formal paths, sourced from https://github.com/runtimeverification/verified-smart-contracts/blob/master/uniswap/results/ethToTokenSwapInput.txt line 374
# (to find, grep for only line with Status: SUCCESS)
formalverification_path_ethToTokenSwapInput = "msgvalue * 997 * token_reserve / ((selfbalance - msgvalue) * 1000 + msgvalue * 997)"
# CFF model return value, sourced from our file uniswap.k
cff_ethToTokenSwapInput = "(997 * TradeAmount * USwapBalanceOut) / (1000 * USwapBalanceIn + 997 * TradeAmount)"

# we may have to make manual variable substitutions to account for differences in execution (by inspection)
# in the Uniswap EVM code, the EVM adds the ETH value of the transaction to the Uniswap balance before executing logic
# USwapBalanceIn in our spec represents the balance *before* this call, so we must perform the substraction for equivalence
# (this is the kind of manual reasoning required to prove specs equivalent)
substitutions = [("(selfbalance - msgvalue)", "USwapBalanceIn")]


# this will fail, due to execution path differences in CFF/the bytecode we manually validate and specify next
print(can_unify(cff_ethToTokenSwapInput, formalverification_path_ethToTokenSwapInput, []))
# this will now succeed
print(can_unify(cff_ethToTokenSwapInput, formalverification_path_ethToTokenSwapInput, substitutions))


# decomposition of formal paths, sourced from https://github.com/runtimeverification/verified-smart-contracts/blob/master/uniswap/results/ethToTokenSwapOutput.txt
# (to find, grep for only line with Status: SUCCESS)
formalverification_path_ethToTokenSwapOutput = "((selfbalance - msgvalue) * token_bought * 1000) / ((token_reserve - token_bought) * 997) + 1"
# CFF model return value, sourced from our file uniswap.k
cff_ethToTokenSwapOutput = "((1000 * USwapBalanceIn * TradeAmount) / (997 * (USwapBalanceOut - TradeAmount)) + 1)"

# now, we do the same check for ethToTokenSwapOutput
print(can_unify(cff_ethToTokenSwapOutput, formalverification_path_ethToTokenSwapOutput, []))
print(can_unify(cff_ethToTokenSwapOutput, formalverification_path_ethToTokenSwapOutput, substitutions))
