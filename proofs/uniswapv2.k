require "execution.k"

module UNISWAPV2-SYNTAX
    imports EXECUTION-SYNTAX
    syntax UniswapV2TX ::= "On" Exchange ETHAddress "swaps for" ETHAddress "by providing" Int ETHAddress "and" Int ETHAddress "with change" Int
                       | "On" Exchange ETHAddress "swaps for" Int ETHAddress "by providing" ETHAddress
                       | "On" Exchange ETHAddress "adds" Int ETHAddress "and" Int ETHAddress "of liquidity"
                       | "On" Exchange ETHAddress "removes" Int ETHAddress "and" Int ETHAddress "of liquidity"  
    syntax ETHTransaction ::= UniswapV2TX
    syntax Exchange ::= "UniswapV2" | "Sushiswap"
    syntax ETHAddress ::= Exchange
    syntax CurrencyPair ::= ETHAddress "," ETHAddress
    syntax InternalCmd ::= "GetPrice" ETHAddress ETHAddress // Oracle query
    syntax Statement ::= InternalCmd
endmodule

module UNISWAPV2
    imports UNISWAPV2-SYNTAX
    imports EXECUTION

    rule <k> exec(On Amm:Exchange Address:ETHAddress swaps for TokenOut:ETHAddress by providing AmountInTokenIn:Int TokenIn:ETHAddress and AmountInTokenOut:Int TokenOut:ETHAddress with change AmountOutTokenIn:Int fee GasFee:Int)  => 
            Address in TokenIn gets 0 -Int AmountInTokenIn ~>
            Amm in TokenIn gets AmountInTokenIn ~>
            Address in TokenOut gets 0 -Int AmountInTokenOut ~>
            Amm in TokenOut gets AmountInTokenOut ~>
            Address in TokenIn gets AmountOutTokenIn ~>
            Amm in TokenIn gets 0 -Int AmountOutTokenIn ~>
            Address in TokenOut gets (((997 *Int AmountInTokenIn -Int 1000 *Int AmountOutTokenIn) *Int USwapV2BalanceOut) /Int (1000 *Int (USwapV2BalanceIn -Int AmountOutTokenIn) +Int 997 *Int AmountInTokenIn)) +Int ((AmountInTokenOut *Int 997) /Int (1000)) ~>
            Amm in TokenOut gets 0 -Int ( (((997 *Int AmountInTokenIn -Int 1000 *Int AmountOutTokenIn) *Int USwapV2BalanceOut) /Int (1000 *Int (USwapV2BalanceIn -Int AmountOutTokenIn) +Int 997 *Int AmountInTokenIn)) +Int ((AmountInTokenOut *Int 997) /Int (1000)) ) ~>
            Address in 0 gets 0 -Int GasFee
            //GetPrice TokenIn TokenOut
            ...
         </k> 
         <S> ... (Amm in TokenOut) |-> USwapV2BalanceOut (Amm in TokenIn) |-> USwapV2BalanceIn ... </S> 
         <B> ... .List => ListItem(On Amm Address swaps for TokenOut by providing AmountInTokenIn TokenIn and AmountInTokenOut TokenOut with change AmountOutTokenIn fee GasFee) </B>
            // requires (UserBalance >=Int TradeAmount) 



    rule <k> exec(On Amm:Exchange Address:ETHAddress swaps for AmountOutTokenOut:Int TokenOut:ETHAddress by providing TokenIn:ETHAddress fee GasFee:Int)  => 
            Address in TokenOut gets AmountOutTokenOut ~>
            Amm in TokenOut gets 0 -Int AmountOutTokenOut ~>
            Address in TokenIn gets 0 -Int ((1000 *Int USwapV2BalanceIn *Int AmountOutTokenOut) /Int (997 *Int (USwapV2BalanceOut -Int AmountOutTokenOut )) +Int 1) ~>
            Amm in TokenIn gets ((1000 *Int USwapV2BalanceIn *Int AmountOutTokenOut) /Int (997 *Int (USwapV2BalanceOut -Int AmountOutTokenOut )) +Int 1) ~>
            Address in 0 gets 0 -Int GasFee 
            //GetPrice TokenIn TokenOut
            ...
         </k>
         <S> ... (Amm in TokenOut) |-> USwapV2BalanceOut (Amm in TokenIn) |-> USwapV2BalanceIn ... </S> 
         <B> ... .List => ListItem(On Amm Address swaps for AmountOutTokenOut TokenOut by providing TokenIn fee GasFee) </B>
            // requires (UserBalance >=Int TradeAmount) 




    rule <k> exec(On Amm:Exchange Address:ETHAddress swaps for TokenOut:ETHAddress by providing AmountInTokenIn:Int TokenIn:ETHAddress and AmountInTokenOut:Int TokenOut:ETHAddress with change AmountOutTokenIn:Int fee GasFee:Int)  => FAIL ... </k>
         <S> S </S>
         <M> _:Set => .Set </M>
         <B> ... .List => ListItem(On Amm Address swaps for TokenOut by providing AmountInTokenIn TokenIn and AmountInTokenOut TokenOut with change AmountOutTokenIn fee GasFee) </B>
         requires notBool (((Amm in TokenOut) in keys(S)) andBool ((Amm in TokenIn) in keys(S)) )



    // todo accurate pricing rules
    // todo fees
    rule <k> exec(On Amm:Exchange LiquidityProvider:ETHAddress adds Amount0:Int Token0:ETHAddress and Amount1:Int Token1:ETHAddress of liquidity)  => 
             Amm in Token0 gets Amount0 ~> Amm in Token1 gets Amount1
             //GetPrice Token0 Token1
             ...
         </k>
         <B> ... .List => ListItem(On Amm LiquidityProvider adds Amount0 Token0 and Amount1 Token1 of liquidity) </B>

    rule <k> exec(On Amm:Exchange LiquidityProvider:ETHAddress removes Amount0:Int Token0:ETHAddress and Amount1:Int Token1:ETHAddress of liquidity)  => 
             Amm in Token0 gets 0 -Int Amount0 ~> Amm in Token1 gets 0 -Int Amount1 
             //GetPrice Token0 Token1
             ...
         </k>
         <B> ... .List => ListItem(On Amm LiquidityProvider removes Amount0 Token0 and Amount1 Token1 of liquidity) </B>

    rule <k> GetPrice Token0 Token1 => .K ... </k>
         <B> ... .List => ListItem(GetPrice Token0 Token1) </B>
         <S> ... (Amm in Token0) |-> Qty0 (Amm in Token1) |-> Qty1 ... </S>
         <P> Px => Px[(Token0 , Token1) <- (Qty1 /Int Qty0)][(Token1 , Token0) <- (Qty0 /Int Qty1)] </P>


endmodule
