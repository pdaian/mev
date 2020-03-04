module MEV-SYNTAX
    imports DOMAINS-SYNTAX

    syntax UniswapTX ::= TokenAccount "swaps" Int "for" Int
    syntax ETHTransaction ::= UniswapTX | ETHTransaction Int

    syntax TokenAccount ::= Int "in" Int // represent balance for account in token

    syntax Statement ::= TokenAccount "gets" Int // set token balance
                    | TokenAccount "updates" Int
                    | ETHTransaction
                    | "formtemplate"

    syntax Block ::= Statement
                    > Statement ";" Block

endmodule

module MEV
    imports MEV-SYNTAX
    imports DOMAINS

configuration
    <k color="green"> $PGM:Block </k>       // Instructions left to execute
    <availableTXs> .Set </availableTXs>     // Available transactions for reordering
    <balances> .Map </balances>             // System state; mapping of all (Address in Token) to Balance (all type Integer)
    //<minerTXsAllowed> 5 </minerTXsAllowed>  // Number of miner own txs allowed (to prevent infinite statespace)
    <numTXs> 0 </numTXs>
    <txLog> .List </txLog>

// Boring stuff; setup state before miner can execute.  Setup balances and aggregate available txs.
rule <k> (Address:Int in Token:Int gets Amount:Int; Remainder:Block) </k>
     <balances> B => B[(Address in Token) <- 0:Int] </balances> requires notBool((Address in Token) in keys(B))

rule <k> (Address:Int in Token:Int gets Amount:Int; Remainder:Block) => (Address in Token updates Amount; Remainder) </k>
     <balances> B </balances> requires ((Address in Token) in keys(B))

rule <k> (Address:Int in Token:Int updates Amount:Int; Remainder:Block) => Remainder </k>
     <balances> (Address in Token) |-> (OldBalance => (Amount +Int OldBalance)) ... </balances>

rule <k> (TX:ETHTransaction; Remainder:Block) => Remainder </k>
    <availableTXs> ... .Set => SetItem(TX N) ...</availableTXs>
    <numTXs> N:Int => N +Int 1 </numTXs>

// Once formtemplate happens, the miner can include transactions; choose any valid USwapTX and execute it
rule <k> formtemplate => 
        Address in TokenIn gets (0 -Int TradeAmount); 
        Address in TokenOut gets (USwapBalanceOut -Int ((USwapBalanceIn *Int USwapBalanceOut) /Int (USwapBalanceIn +Int TradeAmount)));
        100 in TokenIn gets TradeAmount;
        100 in TokenOut gets (USwapBalanceOut -Int ((USwapBalanceIn *Int USwapBalanceOut) /Int (USwapBalanceIn +Int TradeAmount)));
        formtemplate 
     </k> 
     <availableTXs> ... SetItem(Address:Int in TokenIn:Int swaps TradeAmount:Int for TokenOut:Int ID:Int) => .Set ... </availableTXs> 
     <balances> ... (100 in TokenOut) |-> USwapBalanceOut (100 in TokenIn) |-> USwapBalanceIn (Address in TokenIn) |-> UserBalance ... </balances> 
     <txLog> ... .List => ListItem(ID) </txLog>
        requires (UserBalance >=Int TradeAmount) 

//rule <k> formtemplate => 200 in 1 swaps ?X:Int for 0 I; formtemplate </k>
//     <minerTXsAllowed> I => I -Int 1 </minerTXsAllowed> requires I >Int 0
     //<balances> ... (200 in TokenIn) |-> B (100 in TokenOut:Int) |-> X ... </balances>

// The miner can end the game at any time (disable this for debug)
rule <k> formtemplate => .K </k>

endmodule
