require "execution.k"

module UNISWAPV2-SYNTAX
    imports EXECUTION-SYNTAX
    syntax UniswapV2TX ::= ETHAddress "swaps for" ETHAddress "by providing" Int ETHAddress "and" Int ETHAddress "with change" Int
                       | ETHAddress "adds" Int ETHAddress "and" Int ETHAddress "of liquidity"
                       | ETHAddress "removes" Int ETHAddress "and" Int ETHAddress "of liquidity"  
    syntax ETHTransaction ::= UniswapV2TX
    syntax ETHAddress ::= "UniswapV2"
    syntax CurrencyPair ::= ETHAddress "," ETHAddress
    syntax InternalCmd ::= "GetPrice" ETHAddress ETHAddress // Oracle query
    syntax Statement ::= InternalCmd
endmodule

module UNISWAPV2
    imports UNISWAPV2-SYNTAX
    imports EXECUTION

    rule <k> exec(Address:ETHAddress swaps for TokenOut:ETHAddress by providing AmountInTokenIn:Int TokenIn:ETHAddress and AmountInTokenOut:Int TokenOut:ETHAddress with change AmountOutTokenIn:Int fee GasFee:Int)  => 
            Address in TokenIn gets 0 -Int AmountInTokenIn ~>
            UniswapV2 in TokenIn gets AmountInTokenIn ~>
            Address in TokenOut gets 0 -Int AmountInTokenOut ~>
            UniswapV2 in TokenOut gets AmountInTokenOut ~>
            Address in TokenIn gets AmountOutTokenIn ~>
            UniswapV2 in TokenIn gets 0 -Int AmountOutTokenIn ~>
            Address in TokenOut gets (((997 *Int AmountInTokenIn -Int 1000 *Int AmountOutTokenIn) *Int USwapV2BalanceOut) /Int (1000 *Int (USwapV2BalanceIn -Int AmountOutTokenIn) +Int 997 *Int AmountInTokenIn)) +Int ((AmountInTokenOut *Int 997) /Int (1000)) ~>
            UniswapV2 in TokenOut gets 0 -Int ( (((997 *Int AmountInTokenIn -Int 1000 *Int AmountOutTokenIn) *Int USwapV2BalanceOut) /Int (1000 *Int (USwapV2BalanceIn -Int AmountOutTokenIn) +Int 997 *Int AmountInTokenIn)) +Int ((AmountInTokenOut *Int 997) /Int (1000)) ) ~>
            Address in 0 gets 0 -Int GasFee ~>
            GetPrice TokenIn TokenOut
            ...
         </k> 
         <S> ... (UniswapV2 in TokenOut) |-> USwapV2BalanceOut (UniswapV2 in TokenIn) |-> USwapV2BalanceIn ... </S> 
         <B> ... .List => ListItem(Address swaps for TokenOut by providing AmountInTokenIn TokenIn and AmountInTokenOut TokenOut with change AmountOutTokenIn fee GasFee) </B>
            // requires (UserBalance >=Int TradeAmount) 

    // todo accurate pricing rules
    // todo fees
    rule <k> exec(LiquidityProvider:ETHAddress adds Amount0:Int Token0:ETHAddress and Amount1:Int Token1:ETHAddress of liquidity)  => 
             UniswapV2 in Token0 gets Amount0 ~> UniswapV2 in Token1 gets Amount1 ~> 
             GetPrice Token0 Token1
             ...
         </k>
         <B> ... .List => ListItem(LiquidityProvider adds Amount0 Token0 and Amount1 Token1 of liquidity) </B>

    rule <k> exec(LiquidityProvider:ETHAddress removes Amount0:Int Token0:ETHAddress and Amount1:Int Token1:ETHAddress of liquidity)  => 
             UniswapV2 in Token0 gets 0 -Int Amount0 ~> UniswapV2 in Token1 gets 0 -Int Amount1 ~>
             GetPrice Token0 Token1
             ...
         </k>
         <B> ... .List => ListItem(LiquidityProvider removes Amount0 Token0 and Amount1 Token1 of liquidity) </B>

    rule <k> GetPrice Token0 Token1 => .K ... </k>
         <B> ... .List => ListItem(GetPrice Token0 Token1) </B>
         <S> ... (UniswapV2 in Token0) |-> Qty0 (UniswapV2 in Token1) |-> Qty1 ... </S>
         <P> Px => Px[(Token0 , Token1) <- (Qty1 /Int Qty0)][(Token1 , Token0) <- (Qty0 /Int Qty1)] </P>


endmodule
