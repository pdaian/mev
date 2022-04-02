require "execution.k"
require "betting.k"

module FLASHLOAN-SYNTAX
    imports BETTING-SYNTAX
    syntax FlashloanTx ::= ETHAddress "borrows" Int ETHAddress "calls into" ETHTransaction "returns" Int ETHAddress
    syntax ETHTransaction ::= FlashloanTx
    syntax ETHAddress ::= "Pool"
endmodule

module FLASHLOAN
    imports FLASHLOAN-SYNTAX
    imports BETTING

    rule <k> exec(Player:ETHAddress borrows Amount:Int Token:ETHAddress calls into Call:ETHTransaction returns Change:Int Token:ETHAddress fee GasFee:Int)  => 
            Player in Token gets Amount ~>
            Pool in Token gets 0 -Int Amount ~>
            Call ~>
            Player in Token gets 0 -Int Change ~>
            Pool in Token gets Change
            ...
         </k>
        //  <S> Pool |-> Reserves </S>
         <B> ... .List => ListItem(Player borrows Amount Token calls into Call returns Change Token fee GasFee) </B>
        requires (Change >=Int Amount)// check here or in kprove claim? 

endmodule
