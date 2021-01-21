#!/bin/bash
block=$1
tx=$2
uniswapv2_address=$3
sushiswap_address=$4

#sushiswap_tx=`sed "/$tx/q" ~/github-mev/data-scripts/latest-data/sushiswap-processed/"$sushiswap_address".csv | grep -v "^//" | sed -e 's/^/On Sushiswap /'`

sushiswap_tx=`grep -A1 "block $block" ~/github-mev/data-scripts/latest-data/sushiswap-processed/"$sushiswap_address".csv | sed "/$tx/q" | grep -v "^//" | sed -e 's/^/On Sushiswap /'`

uniswapv2_tx=`grep -A1 "block $block" ~/github-mev/data-scripts/latest-data/uniswapv2-processed/"$uniswapv2_address".csv | sed "/$tx/q" | grep -v "^//" | sed -e 's/^/On UniswapV2 /'`

sushiswap_state=`sed "/$block/q" ~/github-mev/data-scripts/latest-data/sushiswap-reserves.csv | grep $sushiswap_address | tail -n 1`

uniswapv2_state=`sed "/$block/q" ~/github-mev/data-scripts/latest-data/uniswapv2-reserves.csv | grep $uniswapv2_address | tail -n 1`


sushiswap_token0=`echo $sushiswap_state | cut -d, -f3 `
sushiswap_token1=`echo $sushiswap_state | cut -d, -f4 `
sushiswap_amount0=`echo $sushiswap_state | cut -d, -f5 `
sushiswap_amount1=`echo $sushiswap_state | cut -d, -f6 `

uniswapv2_token0=`echo $uniswapv2_state | cut -d, -f3 `
uniswapv2_token1=`echo $uniswapv2_state | cut -d, -f4 `
uniswapv2_amount0=`echo $uniswapv2_state | cut -d, -f5 `
uniswapv2_amount1=`echo $uniswapv2_state | cut -d, -f6 `

echo 'require "proof.k"

module INSTABILITY

imports UNISWAPV2

claim <k>' > instability.k

echo $sushiswap_tx >> instability.k
echo $uniswapv2_tx >> instability.k

echo "     On UniswapV2 Miner swaps for 1097077688018008265106216665536940668749033598146 by providing Alpha:Int 1096451400262405796991039590211805051831004063880 and 0 1097077688018008265106216665536940668749033598146 with change 0 fee 0 ;
     On Sushiswap Miner swaps for Alpha 1096451400262405796991039590211805051831004063880 by providing 1097077688018008265106216665536940668749033598146 fee 0 ;

     => .K
     </k>
     <S> (Sushiswap in $sushiswap_token0) |-> $sushiswap_amount0 (Sushiswap in $sushiswap_token1) |-> $sushiswap_amount1 (UniswapV2 in $uniswapv2_token0) |-> $uniswapv2_amount0 (UniswapV2 in $uniswapv2_token1) |-> $uniswapv2_amount1 => ?S:Map </S>
     <B> .List => ?_ </B>
     requires (Alpha >Int 0) andBool (Alpha <Int 100000000000000000000000) //10**23
     ensures ({?S[Miner in 1096451400262405796991039590211805051831004063880]}:>Int <=Int 0  ) andBool ({?S[Miner in 1097077688018008265106216665536940668749033598146]}:>Int <=Int 0  )

endmodule" >> instability.k



