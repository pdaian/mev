module BOUND
    imports MEV
    rule <k>
            0 in 0 gets 0;
            0 in SAI gets 0;
            1 opens vault 101;
			1 locks 5 collateral to vault 101;
			2 is given vault 101;
			2 draws 500 debt from vault 101;
            0 bites vault 101 ;
			1 adds 20000 tokens and 1 eth of liquidity to SAI;
			=> .K
     </k>
    <S> .Map =>?S:Map </S>
    <M> .Set => .Set </M>
    <B> .List => ?A2 </B>
	<P> .Map => ?A3 </P>
	<V> .Map => ?A4 </V>
	ensures ({?S[0 in SAI]}:>Int >Int 0)

// ( ({?S[0 in SAI]}:>Int <=Int 0) andBool ?X ==K DONE) orBool (?X ==K FAIL)
	
	// notBool((?Y ==K .K) andBool (?M ==K .Set)) orBool ({?S[0 in SAI]}:>Int <=Int 0 )
	// orBool (notBool ((0 , SAI) in keys(?P)))
	// (notBool(?X ==K .K) andBool notBool(?Y ==K .K)) orBool (?X ==K .K andBool ?Y ==K .K andBool ({?S[0 in SAI]}:>Int <=Int 0 )) 
	// (	notBool(?X ==K DONE)) orBool
endmodule