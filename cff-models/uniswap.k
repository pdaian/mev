require "execution.k"

module UNISWAP-SYNTAX
    imports EXECUTION-SYNTAX

    syntax UniswapTX ::= ETHAddress "in" ETHAddress "swaps" Int "input" "for" ETHAddress
                       | ETHAddress "in" ETHAddress "swaps" Int "for" ETHAddress "output"
                       | ETHAddress "adds" Int "tokens and" Int "eth of liquidity to" ETHAddress
                       | ETHAddress "removes" Int "tokens and" Int "eth of liquidity from" ETHAddress
    syntax ETHTransaction ::= UniswapTX
    syntax ETHAddress ::= "Uniswap"
    syntax CurrencyPair ::= ETHAddress "," ETHAddress
    syntax InternalCmd ::= "GetPrice" ETHAddress ETHAddress // Oracle query
    syntax Statement ::= InternalCmd
endmodule

module UNISWAP
    imports UNISWAP-SYNTAX
    imports EXECUTION

    rule <k> exec(Address:ETHAddress in TokenIn:ETHAddress swaps TradeAmount:Int input for TokenOut:ETHAddress fee GasFee:Int)  => 
            Address in TokenIn gets 0 -Int TradeAmount ~>
            Address in TokenOut gets (997 *Int TradeAmount *Int USwapBalanceOut) /Int (1000 *Int USwapBalanceIn +Int 997 *Int TradeAmount) ~>
            Uniswap in TokenIn gets TradeAmount ~>
            Uniswap in TokenOut gets 0 -Int (997 *Int TradeAmount *Int USwapBalanceOut) /Int (1000 *Int USwapBalanceIn +Int 997 *Int TradeAmount) ~>
            Address in 0 gets 0 -Int GasFee
            ...
         </k> 
         <S> ... (Uniswap in TokenOut) |-> USwapBalanceOut (Uniswap in TokenIn) |-> USwapBalanceIn ... </S> 
         <B> ... .List => ListItem(Address in TokenIn swaps TradeAmount input for TokenOut fee GasFee) </B>
            // requires (UserBalance >=Int TradeAmount) 

    rule <k> exec(Address:ETHAddress in TokenIn:ETHAddress swaps TradeAmount:Int for TokenOut:ETHAddress output fee GasFee:Int)  => 
            Address in TokenIn gets 0 -Int ((1000 *Int USwapBalanceIn *Int TradeAmount) /Int (997 *Int (USwapBalanceOut -Int TradeAmount)) +Int 1) ~>
            Address in TokenOut gets TradeAmount ~>
            Uniswap in TokenIn gets ((1000 *Int USwapBalanceIn *Int TradeAmount) /Int (997 *Int (USwapBalanceOut -Int TradeAmount)) +Int 1) ~>
            Uniswap in TokenOut gets 0 -Int TradeAmount ~>
            Address in 0 gets 0 -Int GasFee
            ...
         </k> 
         <S> ... (Uniswap in TokenOut) |-> USwapBalanceOut (Uniswap in TokenIn) |-> USwapBalanceIn ... </S> 
         <B> ... .List => ListItem(Address in TokenIn swaps TradeAmount for TokenOut output fee GasFee) </B>
            // requires (UserBalance >=Int TradeAmount) 

    // todo accurate pricing rules
    // todo fees
    rule <k> exec(LiquidityProvider:ETHAddress adds TokenAmount:Int tokens and ETHAmount:Int eth of liquidity to Token:ETHAddress)  => 
             Uniswap in Token gets TokenAmount ~> Uniswap in 0 gets ETHAmount
             ...
         </k>
         <B> ... .List => ListItem(LiquidityProvider adds TokenAmount tokens and ETHAmount eth of liquidity to Token) </B>

    rule <k> exec(LiquidityProvider:ETHAddress removes TokenAmount:Int tokens and ETHAmount:Int eth of liquidity from Token:ETHAddress)  => Uniswap in Token gets 0 -Int TokenAmount ~> Uniswap in 0 gets 0 -Int ETHAmount 
            ...
         </k>
         <B> ... .List => ListItem(LiquidityProvider removes TokenAmount tokens and ETHAmount eth of liquidity from Token) </B>

//    rule <k> GetPrice Token0 Token1 => .K ... </k>
//         <B> ... .List => ListItem(GetPrice Token0 Token1) </B>
//         <S> ... (Uniswap in Token0) |-> Qty0 (Uniswap in Token1) |-> Qty1 ... </S>
//         <P> Px => Px[(Token0 , Token1) <- (Qty1 /Int Qty0)][(Token1 , Token0) <- (Qty0 /Int Qty1)] </P>

    // insertion rule
    //rule <k> .K </k>
    //     <M> .Set => SetItem(40 adds 1000 tokens and 1000 eth of liquidity to 100) </M>
    //     <N> X => X -Int 1 </N>
    //     requires(X >Int 0)

endmodule
