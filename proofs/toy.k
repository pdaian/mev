require "uniswapv2.k"

module INSTABILITY

imports UNISWAPV2

claim <k>

     On UniswapV2 User adds 2000 BBT and 100 ETH of liquidity;
     On Sushiswap User adds 2000 BBT and 100 ETH of liquidity;
     
     On UniswapV2 Miner swaps for ETH by providing Alpha:Int BBT and 0 ETH with change 0 fee 0 ;
     On Sushiswap Miner swaps for Alpha BBT by providing ETH fee 0 ;

     => .K
     </k>
     <S> .Map => ?S:Map </S>
     <B> .List => ?_ </B>
     requires (Alpha >Int 0) andBool (Alpha <Int 100)
     ensures ({?S[Miner in BBT]}:>Int <=Int 0  ) andBool ({?S[Miner in ETH]}:>Int <=Int 0  )

endmodule

