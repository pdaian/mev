module MEV-SYNTAX
    imports DOMAINS-SYNTAX


    syntax UniswapTX ::= ETHAddress "intoken" ETHAddress "swaps" Int "input" "for" ETHAddress 
                       | ETHAddress "intoken" ETHAddress "swaps" Int "for" ETHAddress "output"
                       | ETHAddress "adds" Int "tokens and" Int "eth of liquidity to" ETHAddress
                       | ETHAddress "removes" Int "tokens and" Int "eth of liquidity from" ETHAddress
    syntax ETHTransaction ::= UniswapTX | ETHTransaction "fee" Int
    syntax ETHAddress ::= Int | "Uniswap" | "ETH"
    syntax BalanceEntry ::= ETHAddress "intoken" ETHAddress

    syntax Statement ::= ETHAddress "intoken" ETHAddress "gets" Int // set token balance
                    | ETHTransaction

    syntax Block ::= Statement ";"
                    | Block Statement ";"
    syntax KItem ::= Statement
endmodule

module MEV
    imports MEV-SYNTAX
    imports DOMAINS
  syntax KResult ::= Int | Bool | String

configuration
    <k color="green"> $PGM:Block </k>       // Instructions left to execute
    <M> .Set </M>     // Available transactions for reordering
    <S> .Map </S>             // System state; mapping of all (Address intoken Token) to Balance (all type Integer)
    <B> .List </B>

// Boring stuff; setup state before miner can execute.  Setup S and aggregate available txs.
rule <k> Address:ETHAddress intoken Token:ETHAddress gets Amount:Int ... </k>
 <S> B => B[(Address intoken Token) <- 0:Int] </S> requires notBool((Address intoken Token) in keys(B))

rule <k> Address:ETHAddress intoken Token:ETHAddress gets Amount:Int => .K ... </k>
     <S> ... (Address intoken Token) |-> (FoldBalance => (Amount +Int FoldBalance)) ... </S> 
     //requires (Amount >=Int (0 -Int OldBalance))

rule <k> TX:ETHTransaction => .K ... </k>
     <M> ... .Set => SetItem(TX) </M>

rule <k> B:Block S:Statement; => B ~> S ... </k>
rule <k> S:Statement; => S ... </k>

// Once formtemplate happens, the miner can include transactions; choose any valid USwapTX and execute it
rule <k> . => 
        Address intoken TokenIn gets 0 -Int TradeAmount ~>
        Address intoken TokenOut gets (997 *Int TradeAmount *Int USwapBalanceOut) /Int (1000 *Int USwapBalanceIn +Int 997 *Int TradeAmount) ~>
        Uniswap intoken TokenIn gets TradeAmount ~>
        Uniswap intoken TokenOut gets 0 -Int (997 *Int TradeAmount *Int USwapBalanceOut) /Int (1000 *Int USwapBalanceIn +Int 997 *Int TradeAmount) ~>
        Address intoken 0 gets 0 -Int GasFee
     </k> 
     <M> ... SetItem(Address:ETHAddress intoken TokenIn:ETHAddress swaps TradeAmount:Int input for TokenOut:ETHAddress fee GasFee:Int) => .Set ... </M> 
     <S> ... (Uniswap intoken TokenOut) |-> USwapBalanceOut (Uniswap intoken TokenIn) |-> USwapBalanceIn ... </S> 
     <B> ... .List => ListItem(Address intoken TokenIn swaps TradeAmount input for TokenOut fee GasFee) </B>
        // requires (UserBalance >=Int TradeAmount) 

rule <k> .K => 
        Address intoken TokenIn gets 0 -Int ((1000 *Int USwapBalanceIn *Int TradeAmount) /Int (997 *Int (USwapBalanceOut -Int TradeAmount)) +Int 1) ~>
        Address intoken TokenOut gets TradeAmount ~>
        Uniswap intoken TokenIn gets ((1000 *Int USwapBalanceIn *Int TradeAmount) /Int (997 *Int (USwapBalanceOut -Int TradeAmount)) +Int 1) ~>
        Uniswap intoken TokenOut gets 0 -Int TradeAmount ~>
        Address intoken 0 gets 0 -Int GasFee
     </k> 
     <M> ... SetItem(Address:ETHAddress intoken TokenIn:ETHAddress swaps TradeAmount:Int for TokenOut:ETHAddress output fee GasFee:Int) => .Set ... </M> 
     <S> ... (Uniswap intoken TokenOut) |-> USwapBalanceOut (Uniswap intoken TokenIn) |-> USwapBalanceIn ... </S> 
     <B> ... .List => ListItem(Address intoken TokenIn swaps TradeAmount for TokenOut output fee GasFee) </B>
        // requires (UserBalance >=Int TradeAmount) 

// todo accurate pricing rules
// todo fees
rule <k> .K => Uniswap intoken Token gets TokenAmount ~> Uniswap intoken 0 gets ETHAmount </k>
     <M> ... SetItem(LiquidityProvider:ETHAddress adds TokenAmount:Int tokens and ETHAmount:Int eth of liquidity to Token:ETHAddress) => .Set ... </M> 
     <B> ... .List => ListItem(LiquidityProvider adds TokenAmount tokens and ETHAmount eth of liquidity to Token) </B>

rule <k> .K => Uniswap intoken Token gets 0 -Int TokenAmount ~> Uniswap intoken 0 gets 0 -Int ETHAmount </k>
     <M> ... SetItem(LiquidityProvider:ETHAddress removes TokenAmount:Int tokens and ETHAmount:Int eth of liquidity from Token:ETHAddress) => .Set ... </M> 
     <B> ... .List => ListItem(LiquidityProvider removes TokenAmount tokens and ETHAmount eth of liquidity from Token) </B>
    


//rule <k> formtemplate => 200 in 1 swaps ?X:Int for 0; formtemplate </k>
//     <minerTXsAllowed> I => I -Int 1 </minerTXsAllowed> requires I >Int 0

// The miner can end the game at any time (disable this for debug)
// rule <k> formtemplate => .K </k>

endmodule
