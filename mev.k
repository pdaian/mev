module MEV-SYNTAX
    imports DOMAINS-SYNTAX

    syntax UniswapTX ::= TokenAccount "swaps" Int "for" Int
    syntax ETHTransaction ::= UniswapTX

    syntax TokenAccount ::= Int "in" Int // represent balance for account in token

    syntax Statement ::= TokenAccount "gets" Int // set token balance
                    | ETHTransaction
                    | "formtemplate"

    syntax Block ::= Statement
                    > Statement ";" Block

endmodule

module MEV
    imports MEV-SYNTAX
    imports DOMAINS

configuration
    <k color="green"> $PGM:Block </k>
    <availableTXs> .Set </availableTXs>
    <balances> .Map </balances>

// Boring stuff; setup state before miner can execute.  Setup balances and aggregate available txs.
rule <k> (Address:Int in Token:Int gets Amount:Int; Remainder:Block) </k>
     <balances> B => B[(Address in Token) <- 0] </balances> requires notBool((Address in Token) in keys(B))

rule <k> (Address:Int in Token:Int gets Amount:Int; Remainder:Block) => Remainder </k>
     <balances> ... (Address in Token) |-> (OldBalance:Int => (Amount +Int OldBalance)) ... </balances>

rule <k> (TX:ETHTransaction; Remainder:Block) => Remainder </k>
    <availableTXs> ... .Set => SetItem(TX) ...</availableTXs>

rule <k> formtemplate => Address in TokenIn gets (0 -Int TradeAmount); Address in TokenOut gets TradeAmount; 100 in TokenIn gets TradeAmount; 100 in TokenOut gets (0 -Int TradeAmount); formtemplate</k>
     <availableTXs> ... SetItem(Address:Int in TokenIn:Int swaps TradeAmount:Int for TokenOut:Int) => .Set ... </availableTXs>


//rule <k> formtemplate => .K </k>

endmodule
