module MEVVERIFICATION
    imports MEV
rule <k> // initial balances before block
			0 in 0 gets 5;
0 in 1 gets 10;
1 in 0 gets 10;
2 in 1 gets 20;
// setup uniswap balances; special address 100
100 in 0 gets 100;
100 in 1 gets 50;

0 in 0 swaps 5 for 1;

			// miner game starts
			formtemplate
			 => . 
	 </k>
    <balances>.Map =>(0 in 0) |-> ?OutBalance ?REST:Map</balances>
    <availableTXs> .Set => ?A3 </availableTXs>
    <numTXs> 0 => ?A1 </numTXs>
    <txLog> .List => ?A2</txLog>
    ensures ?OutBalance:Int <=Int 5 andBool ?OutBalance:Int >Int -1
endmodule
