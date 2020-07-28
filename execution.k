module EXECUTION-SYNTAX
    imports DOMAINS-SYNTAX

    syntax Executable ::= "exec(" ETHTransaction ")"
    syntax ETHTransaction ::= ETHTransaction "fee" Int
    syntax ETHAddress ::= Int | "ETH"
    syntax BalanceEntry ::= ETHAddress "in" ETHAddress

    syntax Statement ::= ETHAddress "in" ETHAddress "gets" Int // set token balance
                    | ETHTransaction

    syntax Block ::= Statement ";"
                    | Block Statement ";"
endmodule

module EXECUTION
    imports EXECUTION-SYNTAX
    imports DOMAINS

configuration
//    <exec>
    <k color="green"> $PGM:Block </k>       // Instructions left to execute
    <M> .Set </M>     // Available transactions for reordering
    <S> .Map </S>             // System state; mapping of all (Address in Token) to Balance (all type Integer)
    <B> .List </B>
	<P> .Map </P>
	<V> .Map </V> // Mapping of Maker Vault to Owner
//    </exec>
	// Boring stuff; setup state before miner can execute.  Setup S and aggregate available txs.
    rule <k> Address:ETHAddress in Token:ETHAddress gets _:Int ... </k>
         <S> B => B[(Address in Token) <- 0:Int] </S> requires notBool((Address in Token) in keys(B))

    rule <k> Address:ETHAddress in Token:ETHAddress gets Amount:Int => .K ... </k>
         <S> ... (Address in Token) |-> (OldBalance => (Amount +Int OldBalance)) ... </S> 
         //requires (Amount >=Int (0 -Int OldBalance))

    rule <k> TX:ETHTransaction => .K ... </k>
         <M> ... .Set => SetItem(TX) </M>

	// Tx censoring
    //rule <k> TX:ETHTransaction => .K ... </k>

    rule <k> .K => exec(TX) </k>
         <M> ... SetItem(TX:ETHTransaction) => .Set ... </M>

    rule <k> B:Block S:Statement; => B ~> S ... </k>
    rule <k> S:Statement; => S ... </k>

endmodule
