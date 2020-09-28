module EXECUTION-SYNTAX
    imports DOMAINS-SYNTAX

    syntax TaggedTransaction ::= ETHTransaction "serial" Int
    syntax Executable ::= "exec(" ETHTransaction ")"
    syntax ETHTransaction ::= ETHTransaction "fee" Int
                              | ETHTransaction "block" Int
    syntax ETHAddress ::= Int | "ETH"
    syntax BalanceEntry ::= ETHAddress "in" ETHAddress

    syntax Statement ::= ETHAddress "in" ETHAddress "gets" Int // set token balance
                    | ETHTransaction
                    | "DONE" | "FAIL"
                    | Executable

    syntax Block ::= Statement ";"
                    | Block Statement ";"
endmodule

module EXECUTION
    imports EXECUTION-SYNTAX
    imports DOMAINS

configuration
    <k color="green"> $PGM:Block </k>       // Instructions left to execute
    <M> .Set </M>     // Available transactions for reordering
    <S> .Map </S>             // System state; mapping of all (Address in Token) to Balance (all type Integer)
    <B> .List </B>
    <P> .Map </P>
    <V> .Map </V> // Mapping of Maker Vault to Owner
    <N> 0 </N> // Number of transactions tagged
    <C> 0 </C> // Number of transactions untagged

    // Boring stuff; setup state before miner can execute.  Setup S and aggregate available txs.
    rule <k> Address:ETHAddress in Token:ETHAddress gets _:Int ... </k>
         <S> B => B[(Address in Token) <- 0:Int] </S> requires notBool((Address in Token) in keys(B))

    rule <k> Address:ETHAddress in Token:ETHAddress gets Amount:Int => .K ... </k>
         <S> ... (Address in Token) |-> (OldBalance => (Amount +Int OldBalance)) ... </S> 
         //requires (Amount >=Int (0 -Int OldBalance))


    // TX Censoring
    // rule <k> _:ETHTransaction => .K ... </k>

    rule <k> .K => exec(TX) </k>
         <M> ... SetItem(TX:ETHTransaction serial N:Int) => .Set ... </M>
         <C> Curr => Curr +Int 1 </C>
         requires (N >=Int 0) andBool ( (N /Int 2) *Int 2 <=Int Curr )

    rule <k> .K => exec(TX) </k>
         <M> ... SetItem(TX:ETHTransaction serial -1) => .Set ... </M>

    rule <k> B:Block S:Statement; => B ~> S ... </k>
    rule <k> S:Statement; => S ... </k>

    // execution ends when nothing left to execute or txs to re-order
    rule
     <k> .K => DONE </k>
     <M> .Set </M>

endmodule
