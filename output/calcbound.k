module CALCBOUND
    imports MEV
    rule <k>
                        0 in 0 gets 0;
            0 in SAI gets 0;
1 in 0 gets 100000000;
Uniswap in 0 gets 5;
Uniswap in SAI gets 500;
GetPrice 0 SAI;
1 opens vault 2;
1 locks 6 collateral to vault 2;
1 draws 6 debt from vault 2;
1 in 0 swaps 40 input for SAI fee 5;
0 bites vault 2;

         => ?X
     </k>
    <S> ( (Uniswap in 0) |-> 0 (Uniswap in SAI) |-> 0 ) =>?Y0:Map </S>
    <M> .Set => ?Y1:Set </M>
    <B> .List => ?Y2:List </B>
    <P> .Map => ?Y3:Map </P>
    <V> .Map => ?Y4:Map </V>
    ensures ( ({?Y0[0 in SAI]}:>Int <=Int 0) andBool ?X ==K DONE) orBool (?X ==K FAIL)
endmodule
