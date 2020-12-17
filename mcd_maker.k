require "uniswapv2.k" 

module MAKER-SYNTAX
       imports UNISWAPV2-SYNTAX

       syntax MakerSubTx ::= Int "in" ETHAddress "collateral locked"
       | Int "in" ETHAddress "collateral freed"
       | Int "in" ETHAddress "debt wiped"
       | Int "in" ETHAddress "debt drawn"
              

       syntax MakerTX ::= "open vault" ETHAddress "for collateral" ETHAddress
       | MakerSubTx "and" MakerSubTx "from vault" ETHAddress
       | ETHAddress "bites vault" ETHAddress
       | Int "increment in stability fees for" ETHAddress
       | Int "in" ETHAddress "and" Int "in" ETHAddress "transferred from" ETHAddress "to" ETHAddress

       syntax ETHTransaction ::= MakerTX
       syntax ETHAddress ::= "DAI"

endmodule

module MAKER
       imports MAKER-SYNTAX
       imports UNISWAPV2


rule
     <k> exec(_:Int in CAddress:ETHAddress collateral locked and _:MakerSubTx from vault Vault:ETHAddress)
     ...
     </k>
     <V> V => V[Vault <- CAddress] </V>
     <S> S => S[(Vault in CAddress) <- 0:Int][(Vault in DAI) <- 0:Int] </S>
     <B> ... .List => ListItem(open vault Vault for collateral CAddress) </B>
     requires notBool(Vault in keys(V))   


rule
     <k> exec(_:Int in CAddress:ETHAddress collateral freed and _:MakerSubTx from vault Vault:ETHAddress)
     ...
     </k>
     <V> V => V[Vault <- CAddress] </V>
     <S> S => S[(Vault in CAddress) <- 0:Int][(Vault in DAI) <- 0:Int] </S>
     <B> ... .List => ListItem(open vault Vault for collateral CAddress) </B>
     requires notBool(Vault in keys(V))   


rule
     <k> exec(CAmount:Int in CAddress:ETHAddress collateral locked and DAmount:Int in DAI debt wiped from vault Vault:ETHAddress) =>
     Vault in CAddress gets CAmount ~>
     Vault in DAI gets (0 -Int DAmount)
     ...
     </k>
     <V> ... Vault |-> CAddress ... </V>
     <S> ... (Vault in DAI) |-> TotalDebt  ... </S>    
     <B> ... .List => ListItem(CAmount in CAddress collateral locked and DAmount in DAI debt wiped from vault Vault) </B>
     requires (TotalDebt >=Int DAmount)


rule
     <k> exec(CAmount:Int in CAddress:ETHAddress collateral locked and DAmount:Int in DAI debt drawn from vault Vault:ETHAddress) =>
     Vault in CAddress gets CAmount ~>
     Vault in DAI gets DAmount
     ...
     </k>
     <R> ... CAddress |-> Rate ... </R>
     <V> ... Vault |-> CAddress ... </V>
     <P> ... (CAddress , DAI) |-> Px ... </P>
     <S> ... (Vault in CAddress) |-> TotalCollateral (Vault in DAI) |-> TotalDebt  ... </S>
     <B> ... .List => ListItem(CAmount in CAddress collateral locked and DAmount in DAI debt drawn from vault Vault) </B>
     requires (TotalCollateral +Int CAmount) *Int Px *Int 100 *Int 1000000000000000000000000000  >=Int 150 *Int Rate *Int (TotalDebt +Int DAmount)


rule
     <k> exec(CAmount:Int in CAddress:ETHAddress collateral locked and DAmount:Int in DAI debt drawn from vault Vault:ETHAddress) =>
     Vault in CAddress gets CAmount ~>
     Vault in DAI gets DAmount
     ...
     </k>
     <V> ... Vault |-> CAddress ... </V>
     <P> P:Map </P>
     <B> ... .List => ListItem(CAmount in CAddress collateral locked and DAmount in DAI debt drawn from vault Vault) </B>
     requires notBool((CAddress , DAI) in keys(P))


rule
     <k> exec(CAmount:Int in CAddress:ETHAddress collateral freed and DAmount:Int in DAI debt wiped from vault Vault:ETHAddress) =>
     Vault in CAddress gets (0 -Int CAmount) ~>
     Vault in DAI gets (0 -Int DAmount)
     ...
     </k>
     <R> ... CAddress |-> Rate ... </R>
     <V> ... Vault |-> CAddress ... </V>
     <P> ... (CAddress , DAI) |-> Px ... </P>
     <S> ... (Vault in CAddress) |-> TotalCollateral (Vault in DAI) |-> TotalDebt  ... </S>
     <B> ... .List => ListItem(CAmount in CAddress collateral freed and DAmount in DAI debt wiped from vault Vault) </B>
     requires ((TotalCollateral -Int CAmount) *Int Px *Int 100 *Int 1000000000000000000000000000 >=Int 150 *Int Rate *Int (TotalDebt -Int DAmount)) andBool (TotalDebt >=Int DAmount)

rule
     <k> exec(CAmount:Int in CAddress:ETHAddress collateral freed and DAmount:Int in DAI debt wiped from vault Vault:ETHAddress) =>
     Vault in CAddress gets (0 -Int CAmount) ~>
     Vault in DAI gets (0 -Int DAmount)
     ...
     </k>
     <V> ... Vault |-> CAddress ... </V>
     <P> P:Map </P>
     <B> ... .List => ListItem(CAmount in CAddress collateral freed and DAmount in DAI debt wiped from vault Vault) </B>
     requires notBool((CAddress , DAI) in keys(P))



rule
     <k> exec(CAmount:Int in CAddress:ETHAddress collateral freed and DAmount:Int in DAI debt drawn from vault Vault:ETHAddress) =>
     Vault in CAddress gets (0 -Int CAmount) ~>
     Vault in DAI gets DAmount
     ...
     </k>
     <R> ... CAddress |-> Rate ... </R>
     <V> ... Vault |-> CAddress ... </V>
     <P> ... (CAddress , DAI) |-> Px ... </P>
     <S> ... (Vault in CAddress) |-> TotalCollateral (Vault in DAI) |-> TotalDebt  ... </S>
     <B> ... .List => ListItem(CAmount in CAddress collateral freed and DAmount in DAI debt drawn from vault Vault) </B>
     requires (TotalCollateral -Int CAmount) *Int Px *Int 100 *Int 1000000000000000000000000000 >=Int 150 *Int Rate *Int (TotalDebt +Int DAmount)


rule
     <k> exec(CAmount:Int in CAddress:ETHAddress collateral freed and DAmount:Int in DAI debt drawn from vault Vault:ETHAddress) =>
     Vault in CAddress gets (0 -Int CAmount) ~>
     Vault in DAI gets DAmount
     ...
     </k>
     <V> ... Vault |-> CAddress ... </V>
     <P> P:Map </P>
     <B> ... .List => ListItem(CAmount in CAddress collateral freed and DAmount in DAI debt drawn from vault Vault) </B>
     requires notBool((CAddress , DAI) in keys(P))


// TODO : use specific amount, sometimes fat finger limits the amount
rule
     <k> exec(Address:ETHAddress bites vault Vault:ETHAddress) =>
     Vault in DAI gets (0 -Int TotalDebt) ~>
     Vault in CAddress gets 0 -Int TotalCollateral ~>
     Address in DAI gets (0 -Int TotalDebt *Int Rate /Int 1000000000000000000000000000) ~>
     Address in CAddress gets TotalCollateral // win the reverse auction
//     Address in CAddress gets (0 -Int ((90 *Int TotalDebt *Int Rate) /Int (Px *Int 100 *Int 1000000000000000000000000000)) ) //10% discount, abstraction for auction
     ...
     </k>
     <R> ... CAddress |-> Rate ... </R>
     <V> ... Vault |-> CAddress ... </V>
     <P> ... (CAddress, DAI) |-> Px ... </P>
     <S> ... (Vault in CAddress) |-> TotalCollateral (Vault in DAI) |-> TotalDebt  ... </S>
     <B> ... .List => ListItem(Address bites vault Vault) </B>
     requires (TotalCollateral *Int Px *Int 100 *Int 1000000000000000000000000000 <Int 150 *Int Rate *Int TotalDebt) andBool (Px >Int 0)



rule
     <k> exec(CAmount:Int in CAddress:ETHAddress and DAmount:Int in DAI transferred from SrcVault:ETHAddress to DstVault:ETHAddress) =>
     SrcVault in CAddress gets (0 -Int CAmount) ~>
     SrcVault in DAI gets (0 -Int DAmount) ~>
     DstVault in CAddress gets CAmount ~>
     DstVault in DAI gets DAmount
     ...
     </k>
     <V> ... SrcVault |-> CAddress DstVault |-> CAddress  ... </V>
     <B> ... .List => ListItem(CAmount in CAddress and DAmount in DAI transferred from SrcVault to DstVault) </B>


rule
     <k> exec(_:Int increment in stability fees for CAddress:ETHAddress) ... </k>
     <R> R => R[CAddress <- 1000000000000000000000000000:Int]  </R> //10**27
     requires notBool(CAddress in keys(R))   

rule
     <k> exec(Delta:Int increment in stability fees for CAddress:ETHAddress) => .K ... </k>
     <R> ... CAddress |-> (OldRate => (OldRate +Int Delta)) ...  </R>
     <B> ... .List => ListItem(Delta increment in stability fees for CAddress) </B>



endmodule

       
