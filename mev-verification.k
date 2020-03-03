module MEV-VERIFICATION
    imports MEV
rule <k> formtemplate => . </k>
     <balances> ... (100 in TokenOut) |-> USwapBalanceOut => USwapBalanceOut_After
                    (100 in TokenIn)  |-> USwapBalanceIn  => USwapBalanceIn_After
     ... </balances>
requires USwapBalanceOut +Int USwapBalanceIn <=Int 2000
ensures  USwapBalanceOut_After +Int USwapBalanceIn_After <=Int 2000

rule <k> $PGM => . </k>
     <balances> .Map => 
                  (100 in TokenOut) |-> USwapBalanceOut_After
                  (100 in TokenIn)  |-> USwapBalanceIn_After
                  REST:Map
     </balances>
ensures USwapBalanceOut_After +Int USwapBalanceIn_After <=Int 2000
endmodule
