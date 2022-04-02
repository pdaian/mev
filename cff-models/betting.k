require "governance.k"
module BETTING-SYNTAX
    imports GOVERNANCE-SYNTAX
    
    syntax BettingTx ::= ETHAddress "claims reward for" Int
    syntax ETHTransaction ::= BettingTx
endmodule

module BETTING
    imports BETTING-SYNTAX
    imports GOVERNANCE

    rule <k> exec(Player:ETHAddress claims reward for Proposal:Int fee GasFee:Int)  => 
            Player in ETH gets 10
            ...
         </k> 
         <T> ... Proposal |-> Stake  ... </T>
         <B> ... .List => ListItem(Player claims reward for Proposal fee GasFee) </B>
        requires(Stake >=Int 0) // Proposal passed
endmodule
