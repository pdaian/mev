
require "uniswap.k"
require "uniswapv2.k"

module SIMPLE

imports UNISWAP
imports UNISWAPV2

claim <k>

     User adds 2000 BBT and 100 0 of liquidity;     // UniswapV2

     => .K
     </k>
     <S> .Map => ?S:Map </S>
     <B> .List => ?_ </B>
     ensures ({?S[UniswapV2 in BBT]}:>Int >=Int 0  ) andBool ({?S[UniswapV2 in 0]}:>Int >=Int 0  )

endmodule

