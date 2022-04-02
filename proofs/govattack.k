require "flashloan.k"

module GOVATTACK

imports FLASHLOAN

rule <k>
    RandomUser votes for 0 with stake Y ETH fee 0;
    RandomUser votes against 0 with stake Z ETH fee 0;
    User borrows X ETH calls into User votes for 0 with stake X ETH fee 0 returns X ETH fee 0;
    User claims reward for 0 fee 0;

     => .K
     </k>
     <S> (Pool in ETH) |-> X:Int => ?S:Map </S>
     <T> 0 |-> 0 => ?T:Map </T>
     <B> .List => ?_ </B>
    //  requires (Alpha >Int 0) andBool (Alpha <Int 10000000000000000000000) 
    ensures ({?S[User in ETH]}:>Int <=Int 0  ) andBool ({?S[Pool in ETH]}:>Int >=Int 0  )

endmodule

