require "execution.k"

module GOVERNANCE-SYNTAX
    imports EXECUTION-SYNTAX

    syntax VotingTx ::= ETHAddress "votes for" Int "with stake" Int ETHAddress
                       | ETHAddress "votes against" Int "with stake" Int ETHAddress
    syntax ETHAddress ::= "Treasury" | "RandomUser"
    syntax ETHTransaction ::= VotingTx
endmodule

module GOVERNANCE
    imports GOVERNANCE-SYNTAX
    imports EXECUTION

    rule <k> exec(Voter:ETHAddress votes for Proposal:Int with stake Amount:Int Token:ETHAddress fee GasFee:Int)  => 
            Voter in Token gets 0 -Int Amount ~>
            Treasury in Token gets Amount 
            ...
         </k> 
         <T> ... Proposal |-> (Stake => (Stake +Int Amount)) ... </T>
         <B> ... .List => ListItem(Voter votes for Proposal with stake Amount Token fee GasFee) </B>

    rule <k> exec(Voter:ETHAddress votes against Proposal:Int with stake Amount:Int Token:ETHAddress fee GasFee:Int)  => 
            Voter in Token gets 0 -Int Amount ~>
            Treasury in Token gets Amount 
            ...
         </k> 
         <T> ... Proposal |-> (Stake => (Stake -Int Amount)) ... </T>
         <B> ... .List => ListItem(Voter votes against Proposal with stake Amount Token fee GasFee) </B>

endmodule
