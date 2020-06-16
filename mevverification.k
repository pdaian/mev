module MEVVERIFICATION
    imports MEV
rule <k> 
    // transaction 0x95d079a82bbf062f2a58d1fd520b8cc09ec341cb746b453bb33a6ede885a0174
    411498817949579190580624588476262637924693753695 adds 150000000 tokens and 76000000000000000 eth of liquidity to 1000808495181554617867411332362082075473764097814;
			 => .
	 </k>
//    <S>... .Map =>(Uniswap in 0) |-> ?OutBalance:Int ... </S>
  //  ensures ?OutBalance:Int <=Int 5000 andBool ?OutBalance:Int >Int 0 
endmodule
