module EXECUTION-SYNTAX
    imports DOMAINS-SYNTAX

    syntax Executable ::= "exec(" ETHTransaction ")"
    syntax ETHTransaction ::= ETHTransaction "fee" Int
                              | ETHTransaction "block" Int
    
    syntax ETHAddress ::= Int | "ETH" | "BBT" | "Miner" | "User"
    syntax BalanceEntry ::= ETHAddress "in" ETHAddress

    syntax Statement ::= ETHAddress "in" ETHAddress "gets" Int // set token balance
                         | ETHAddress "in" ETHAddress "gives" Int // set token balance 
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
    <R> .Map </R> // Stability fees for Maker
    <T> 0 |-> 0 </T> //Proposals for voting
    <C> .Map </C> // CLaimed NFTs
    <N> 1 </N> // Number of transactions a miner can insert

    // Boring stuff; setup state before miner can execute.  Setup S and aggregate available txs.
    rule <k> Address:ETHAddress in Token:ETHAddress gets _:Int ... </k>
         <S> B => B[(Address in Token) <- 0:Int] </S> requires notBool((Address in Token) in keys(B))

    rule <k> Address:ETHAddress in Token:ETHAddress gets Amount:Int => .K ... </k>
         <S> ... (Address in Token) |-> (OldBalance => (Amount +Int OldBalance)) ... </S> 
         //requires (Amount >=Int (0 -Int OldBalance))

    rule <k> Address:ETHAddress in Token:ETHAddress gives Amount:Int => Address in Token gets (0 -Int Amount) ... </k>


//    rule <k> TX:ETHTransaction => .K ... </k>
//         <M> ... .Set => SetItem(TX) </M>

//    rule <k> .K => exec(TX) </k>
//         <M> ... SetItem(TX:ETHTransaction) => .Set ... </M>

    rule <k> TX:ETHTransaction => exec(TX) ... </k>

    // TX Censoring
    // rule <k> _:ETHTransaction => .K ... </k>

    rule <k> B:Block S:Statement; => B ~> S ... </k>
    rule <k> S:Statement; => S ... </k>

    // execution ends when nothing left to execute or txs to re-order
    rule
     <k> .K => DONE </k>
     <M> .Set </M>

endmodule
