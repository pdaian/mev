module MEV-SYNTAX
    imports DOMAINS-SYNTAX

    syntax UniswapTX ::= TokenAccount "swaps" Int "for" Int
    syntax ETHTransaction ::= UniswapTX | ETHTransaction Int | ETHTransaction "fee" Int

    syntax TokenAccount ::= Int "in" Int // represent balance for account in token

    syntax Statement ::= TokenAccount "gets" Int // set token balance
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
    <M> .Set </M>     // Available transactions for reordering
    <S> .Map </S>             // System state; mapping of all (Address in Token) to Balance (all type Integer)
    <minerTXsAllowed> 1 </minerTXsAllowed>  // Number of miner own txs allowed (to prevent infinite statespace)
    <numTXs> 0 </numTXs>
    <B> .List </B>

// Boring stuff; setup state before miner can execute.  Setup S and aggregate available txs.
rule <k> (Address:Int in Token:Int gets Amount:Int; Remainder:Block) </k>
     <S> B => B[(Address in Token) <- 0] </S> requires notBool((Address in Token) in keys(B))

rule <k> (Address:Int in Token:Int gets Amount:Int; Remainder:Block) => Remainder </k>
     <S> ... (Address in Token) |-> (OldBalance => (Amount +Int OldBalance)) ... </S> requires (Amount >=Int (0 -Int OldBalance))

rule <k> (TX:ETHTransaction; Remainder:Block) => Remainder </k>
    <M> ... .Set => SetItem(TX N) ...</M>
    <numTXs> N:Int => N +Int 1 </numTXs>

// Once formtemplate happens, the miner can include transactions; choose any valid USwapTX and execute it
rule <k> formtemplate => 
        Address in TokenIn gets (0 -Int TradeAmount); 
        Address in TokenOut gets (997 *Int TradeAmount *Int USwapBalanceOut) /Int (1000 *Int USwapBalanceIn +Int 997 *Int TradeAmount);
        100 in TokenIn gets TradeAmount;
        100 in TokenOut gets 0 -Int (997 *Int TradeAmount *Int USwapBalanceOut) /Int (1000 *Int USwapBalanceIn +Int 997 *Int TradeAmount);
        Address in 0 gets (0 -Int GasFee);
        formtemplate 
     </k> 
     <M> ... SetItem(Address:Int in TokenIn:Int swaps TradeAmount:Int for TokenOut:Int fee GasFee:Int ID:Int) => .Set ... </M> 
     <S> ... (100 in TokenOut) |-> USwapBalanceOut (100 in TokenIn) |-> USwapBalanceIn (Address in TokenIn) |-> UserBalance ... </S> 
     <B> ... .List => ListItem(Address in TokenIn swaps TradeAmount for TokenOut ID) </B>
        requires (UserBalance >=Int TradeAmount) 

//rule <k> formtemplate => 200 in 1 swaps ?X:Int for 0; formtemplate </k>
//     <minerTXsAllowed> I => I -Int 1 </minerTXsAllowed> requires I >Int 0

// The miner can end the game at any time (disable this for debug)
// rule <k> formtemplate => .K </k>

endmodule
