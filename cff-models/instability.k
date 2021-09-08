
require "uniswap.k"
require "uniswapv2.k"

module INSTABILITY

imports UNISWAP
imports UNISWAPV2

rule <k>

     User adds 2000 BBT and 100 0 of liquidity;     // UniswapV2

     User adds 1000 tokens and 100 eth of liquidity to BBT;     // UniswapV1
     
     Miner swaps for BBT by providing Alpha:Int 0 and 0 BBT with change 0 fee 0 ; // UniswapV2

     Miner in BBT swaps Alpha:Int for 0 output fee 0 ; // UniswapV1

     => .K
     </k>
     <S> .Map => ?S:Map </S>
     <B> .List => ?_ </B>
     requires (Alpha >Int 0) andBool (Alpha <Int 100) 
     ensures ({?S[Miner in BBT]}:>Int <=Int 0  ) andBool ({?S[Miner in 0]}:>Int <=Int 0  )
     //ensures ( (?X ==K FAIL) orBool (({?S[Miner in BBT]}:>Int <=Int 0  )  andBool (?X ==K DONE) ) )
     //ensures (?X ==K FAIL)

endmodule

