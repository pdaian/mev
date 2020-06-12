module MEV-SYNTAX
    imports DOMAINS-SYNTAX


    syntax UniswapTX ::= ETHAddress "in" ETHAddress "swaps" Int "input" "for" ETHAddress 
                       | ETHAddress "in" ETHAddress "swaps" Int "for" ETHAddress "output"
                       | ETHAddress "adds" Int "tokens and" Int "eth of liquidity to" ETHAddress
                       | ETHAddress "removes" Int "tokens and" Int "eth of liquidity from" ETHAddress
    syntax ETHTransaction ::= UniswapTX | ETHTransaction "fee" Int
    syntax ETHAddress ::= Int | "Uniswap" | "ETH"
    syntax BalanceEntry ::= ETHAddress "in" ETHAddress

    syntax Statement ::= ETHAddress "in" ETHAddress "gets" Int // set token balance
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
    <M> .List </M>     // Available transactions for reordering
    <S> .Map </S>             // System state; mapping of all (Address in Token) to Balance (all type Integer)
    <minerTXsAllowed> 1 </minerTXsAllowed>  // Number of miner own txs allowed (to prevent infinite statespace)
    <numTXs> 0 </numTXs>
    <B> .List </B>

// Boring stuff; setup state before miner can execute.  Setup S and aggregate available txs.
rule <k> (Address:ETHAddress in Token:ETHAddress gets Amount:Int; Remainder:Block) </k>
     <S> B => B[(Address in Token) <- 0] </S> requires notBool((Address in Token) in keys(B))

rule <k> (Address:ETHAddress in Token:ETHAddress gets Amount:Int; Remainder:Block) => Remainder </k>
     <S> ... (Address in Token) |-> (OldBalance => (Amount +Int OldBalance)) ... </S> 
     // requires (Amount >=Int (0 -Int OldBalance))

rule <k> (TX:ETHTransaction; Remainder:Block) => Remainder </k>
    <M> ... .List => ListItem(TX) </M>

// Once formtemplate happens, the miner can include transactions; choose any valid USwapTX and execute it
rule <k> formtemplate => 
        Address in TokenIn gets 0 -Int TradeAmount; 
        Address in TokenOut gets (997 *Int TradeAmount *Int USwapBalanceOut) /Int (1000 *Int USwapBalanceIn +Int 997 *Int TradeAmount);
        Uniswap in TokenIn gets TradeAmount;
        Uniswap in TokenOut gets 0 -Int (997 *Int TradeAmount *Int USwapBalanceOut) /Int (1000 *Int USwapBalanceIn +Int 997 *Int TradeAmount);
        Address in 0 gets 0 -Int GasFee;
        formtemplate 
     </k> 
     <M> ListItem(Address:ETHAddress in TokenIn:ETHAddress swaps TradeAmount:Int input for TokenOut:ETHAddress fee GasFee:Int) => .List ... </M> 
     <S> ... (Uniswap in TokenOut) |-> USwapBalanceOut (Uniswap in TokenIn) |-> USwapBalanceIn ... </S> 
     <B> ... .List => ListItem(Address in TokenIn swaps TradeAmount input for TokenOut fee GasFee) </B>
        // requires (UserBalance >=Int TradeAmount) 

rule <k> formtemplate => 
        Address in TokenIn gets 0 -Int ((1000 *Int USwapBalanceIn *Int TradeAmount) /Int (997 *Int (USwapBalanceOut -Int TradeAmount)) +Int 1); 
        Address in TokenOut gets TradeAmount;
        Uniswap in TokenIn gets ((1000 *Int USwapBalanceIn *Int TradeAmount) /Int (997 *Int (USwapBalanceOut -Int TradeAmount)) +Int 1);
        Uniswap in TokenOut gets 0 -Int TradeAmount;
        Address in 0 gets 0 -Int GasFee;
        formtemplate 
     </k> 
     <M> ListItem(Address:ETHAddress in TokenIn:ETHAddress swaps TradeAmount:Int for TokenOut:ETHAddress output fee GasFee:Int) => .List ... </M> 
     <S> ... (Uniswap in TokenOut) |-> USwapBalanceOut (Uniswap in TokenIn) |-> USwapBalanceIn ... </S> 
     <B> ... .List => ListItem(Address in TokenIn swaps TradeAmount for TokenOut output fee GasFee) </B>
        // requires (UserBalance >=Int TradeAmount) 

// todo accurate pricing rules
// todo fees
rule <k> formtemplate => Uniswap in Token gets TokenAmount; Uniswap in 0 gets ETHAmount; formtemplate </k>
     <M> ListItem(LiquidityProvider:ETHAddress adds TokenAmount:Int tokens and ETHAmount:Int eth of liquidity to Token:ETHAddress) => .List ... </M> 
     <B> ... .List => ListItem(LiquidityProvider adds TokenAmount tokens and ETHAmount eth of liquidity to Token) </B>

rule <k> formtemplate => Uniswap in Token gets 0 -Int TokenAmount; Uniswap in 0 gets 0 -Int ETHAmount; formtemplate </k>
     <M> ListItem(LiquidityProvider:ETHAddress removes TokenAmount:Int tokens and ETHAmount:Int eth of liquidity from Token:ETHAddress) => .List ... </M> 
     <B> ... .List => ListItem(LiquidityProvider removes TokenAmount tokens and ETHAmount eth of liquidity from Token) </B>
    


//rule <k> formtemplate => 200 in 1 swaps ?X:Int for 0; formtemplate </k>
//     <minerTXsAllowed> I => I -Int 1 </minerTXsAllowed> requires I >Int 0

// The miner can end the game at any time (disable this for debug)
// rule <k> formtemplate => .K </k>

endmodule
