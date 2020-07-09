module MAKER-SYNTAX
    imports DOMAINS-SYNTAX


    syntax UniswapTX ::= ETHAddress "intoken" ETHAddress "swaps" Int "input" "for" ETHAddress 
                       | ETHAddress "intoken" ETHAddress "swaps" Int "for" ETHAddress "output"
                       | ETHAddress "adds" Int "tokens and" Int "eth of liquidity to" ETHAddress
                       | ETHAddress "removes" Int "tokens and" Int "eth of liquidity from" ETHAddress

    syntax MakerTX ::= ETHAddress "opens vault" ETHAddress
    	   	    | ETHAddress "locks" Int "collateral to vault" ETHAddress
		    | ETHAddress "draws" Int "debt from vault" ETHAddress
		    | ETHAddress "wipes" Int "debt from vault" ETHAddress
		    | ETHAddress "frees" Int "collateral from vault" ETHAddress
		    | ETHAddress "bites vault" ETHAddress

    syntax ETHTransaction ::= UniswapTX | MakerTX | ETHTransaction "fee" Int
    syntax ETHAddress ::= Int | "Uniswap"
    syntax BalanceEntry ::= ETHAddress "intoken" ETHAddress
    syntax CurrencyPair ::= ETHAddress "," ETHAddress
    syntax InternalCmd ::= "GetPrice" ETHAddress ETHAddress // Oracle query 

    syntax Statement ::= ETHAddress "intoken" ETHAddress "gets" Int // set token balance
                    | ETHTransaction
		    | InternalCmd

    syntax Block ::= Statement ";"
                    | Block Statement ";"
    syntax KItem ::= Statement
endmodule

module MAKER
    imports MAKER-SYNTAX
    imports DOMAINS
    imports FLOAT
  syntax KResult ::= Int | Bool | String

configuration
    <k color="green"> $PGM:Block </k>       // Instructions left to execute
    <M> .Set </M>     // Available transactions for reordering
    <S> .Map </S>             // System state; mapping of all (Address intoken Token) to Balance (all type Integer)
    <B> .List </B>
    <P> .Map </P>
    <V> .Map </V> // Mapping of Maker Vault to Owner

// Boring stuff; setup state before miner can execute.  Setup S and aggregate available txs.
rule <k> Address:ETHAddress intoken Token:ETHAddress gets _Amount:Int ... </k>
 <S> B => B[(Address intoken Token) <- 0:Int] </S> requires notBool((Address intoken Token) in keys(B))

rule <k> Address:ETHAddress intoken Token:ETHAddress gets Amount:Int => .K ... </k>
     <S> ... (Address intoken Token) |-> (FoldBalance => (Amount +Int FoldBalance)) ... </S> 
     //requires (Amount >=Int (0 -Int OldBalance))

rule <k> TX:ETHTransaction => .K ... </k>
     <M> ... .Set => SetItem(TX) </M>

rule <k> B:Block S:Statement; => B ~> S ... </k>
rule <k> S:Statement; => S ... </k>

// Once formtemplate happens, the miner can include transactions; choose any valid USwapTX and execute it
rule <k> . => 
        Address intoken TokenIn gets 0 -Int TradeAmount ~>
        Address intoken TokenOut gets (997 *Int TradeAmount *Int USwapBalanceOut) /Int (1000 *Int USwapBalanceIn +Int 997 *Int TradeAmount) ~>
        Uniswap intoken TokenIn gets TradeAmount ~>
        Uniswap intoken TokenOut gets 0 -Int (997 *Int TradeAmount *Int USwapBalanceOut) /Int (1000 *Int USwapBalanceIn +Int 997 *Int TradeAmount) ~>
        Address intoken 0 gets 0 -Int GasFee ~>
	GetPrice TokenIn TokenOut
     </k> 
     <M> ... SetItem(Address:ETHAddress intoken TokenIn:ETHAddress swaps TradeAmount:Int input for TokenOut:ETHAddress fee GasFee:Int) => .Set ... </M> 
     <S> ... (Uniswap intoken TokenOut) |-> USwapBalanceOut (Uniswap intoken TokenIn) |-> USwapBalanceIn ... </S> 
     <B> ... .List => ListItem(Address intoken TokenIn swaps TradeAmount input for TokenOut fee GasFee) </B>
        // requires (UserBalance >=Int TradeAmount) 

rule <k> .K => 
        Address intoken TokenIn gets 0 -Int ((1000 *Int USwapBalanceIn *Int TradeAmount) /Int (997 *Int (USwapBalanceOut -Int TradeAmount)) +Int 1) ~>
        Address intoken TokenOut gets TradeAmount ~>
        Uniswap intoken TokenIn gets ((1000 *Int USwapBalanceIn *Int TradeAmount) /Int (997 *Int (USwapBalanceOut -Int TradeAmount)) +Int 1) ~>
        Uniswap intoken TokenOut gets 0 -Int TradeAmount ~>
        Address intoken 0 gets 0 -Int GasFee ~>
	GetPrice TokenIn TokenOut
     </k> 
     <M> ... SetItem(Address:ETHAddress intoken TokenIn:ETHAddress swaps TradeAmount:Int for TokenOut:ETHAddress output fee GasFee:Int) => .Set ... </M> 
     <S> ... (Uniswap intoken TokenOut) |-> USwapBalanceOut (Uniswap intoken TokenIn) |-> USwapBalanceIn ... </S> 
     <B> ... .List => ListItem(Address intoken TokenIn swaps TradeAmount for TokenOut output fee GasFee) </B>
        // requires (UserBalance >=Int TradeAmount) 

// todo accurate pricing rules
// todo fees
rule <k> .K => Uniswap intoken Token gets TokenAmount ~> Uniswap intoken 0 gets ETHAmount </k>
     <M> ... SetItem(LiquidityProvider:ETHAddress adds TokenAmount:Int tokens and ETHAmount:Int eth of liquidity to Token:ETHAddress) => .Set ... </M> 
     <B> ... .List => ListItem(LiquidityProvider adds TokenAmount tokens and ETHAmount eth of liquidity to Token) </B>

rule <k> .K => Uniswap intoken Token gets 0 -Int TokenAmount ~> Uniswap intoken 0 gets 0 -Int ETHAmount </k>
     <M> ... SetItem(LiquidityProvider:ETHAddress removes TokenAmount:Int tokens and ETHAmount:Int eth of liquidity from Token:ETHAddress) => .Set ... </M> 
     <B> ... .List => ListItem(LiquidityProvider removes TokenAmount tokens and ETHAmount eth of liquidity from Token) </B>


rule <k> GetPrice Token0 Token1 => .K ... </k>
     <B> ... .List => ListItem(GetPrice Token0 Token1) </B>
     <S> ... (Uniswap intoken Token0) |-> Qty0 (Uniswap intoken Token1) |-> Qty1 ... </S>
     <P> Px => Px[(Token0 , Token1) <- (Qty1 /Int Qty0)][(Token1 , Token0) <- (Qty0 /Int Qty1)] </P>


rule
     <k> .K </k>
     <M> ... SetItem(Address:ETHAddress opens vault Vault:ETHAddress) => .Set ... </M> 
     <V> V => V[(Vault) <- Address:ETHAddress] </V>
     <S> B => B[(Vault intoken 0) <- 0:Int][(Vault intoken 1) <- 0:Int] </S> // replace 1 with DAI
     <B> ... .List => ListItem(Address opens vault Vault) </B>
     requires notBool((Vault intoken 0) in keys(B)) andBool notBool((Vault intoken 1) in keys(B)) andBool notBool((Vault) in keys(V))

rule
     <k> .K =>
     	 Address intoken 0 gets (0 -Int Amount) ~>
	 Vault intoken 0 gets Amount
     </k>  
     <M> ... SetItem(Address:ETHAddress locks Amount:Int collateral to vault Vault:ETHAddress) => .Set ... </M> 
     <V> ... Vault |-> Address ... </V>
     <S> ... (Address intoken 0) |-> UserBalance ... </S>
     <B> ... .List => ListItem(Address locks Amount collateral to vault Vault) </B>
     requires (UserBalance >=Int Amount)

rule
     <k> .K =>
         Address intoken 1 gets Amount ~>
	 Vault intoken 1 gets Amount
     </k>  
     <M> ... SetItem(Address:ETHAddress draws Amount:Int debt from vault Vault:ETHAddress) => .Set ... </M> 
     <V> ... Vault |-> Address ... </V>
     <P> ... (0 , 1) |-> Px ... </P>
     <S> ... (Vault intoken 0) |-> TotalCollateral (Vault intoken 1) |-> TotalDebt  ... </S>
     <B> ... .List => ListItem(Address draws Amount debt from vault Vault) </B>
     requires TotalCollateral *Int Px >=Int 150 *Int (TotalDebt +Int Amount) 

rule
     <k> .K =>
         Address intoken 0 gets Amount ~>
	 Vault intoken 0 gets (0 -Int Amount)
     </k>  
     <M> ... SetItem(Address:ETHAddress frees Amount:Int collateral from vault Vault:ETHAddress) => .Set ... </M> 
     <V> ... Vault |-> Address ... </V>
     <P> ... (0 , 1) |-> Px ... </P>
     <S> ... (Vault intoken 0) |-> TotalCollateral (Vault intoken 1) |-> TotalDebt  ... </S>
     <B> ... .List => ListItem(Address frees Amount collateral from vault Vault) </B>
     requires (TotalCollateral -Int Amount) *Int Px >=Int 150 *Int TotalDebt

rule
     <k> .K =>
         Address intoken 1 gets (0 -Int Amount) ~>
	 Vault intoken 1 gets (0 -Int Amount)
     </k>  
     <M> ... SetItem(Address:ETHAddress wipes Amount:Int debt from vault Vault:ETHAddress) => .Set ... </M> 
     <V> ... Vault |-> Address ... </V>
     <S> ... (Address intoken 1) |-> UserBalance (Vault intoken 1) |-> TotalDebt  ... </S>
     <B> ... .List => ListItem(Address wipes Amount debt from vault Vault) </B>
     requires (UserBalance >=Int Amount) andBool (TotalDebt >=Int Amount)

// TODO : fix division by zero
rule
     <k> .K =>
         Vault intoken 1 gets (0 -Int TotalDebt) ~>
	 Vault intoken 0 gets (((90 *Int TotalDebt) /Int Px) /Int 100) ~> // 10% penalty
	 Address intoken 1 gets TotalDebt ~>
	 Address intoken 0 gets (0 -Int (((90 *Int TotalDebt) /Int Px) /Int 100) ) //10% discount
     </k>  
     <M> ... SetItem(Address:ETHAddress bites vault Vault:ETHAddress) => .Set ... </M>
     <P> ... (0 , 1) |-> Px ... </P>
     <S> ... (Vault intoken 0) |-> TotalCollateral (Vault intoken 1) |-> TotalDebt  ... </S>
     <B> ... .List => ListItem(Address bites vault Vault) </B>
     requires TotalCollateral *Int Px <Int 150 *Int TotalDebt


endmodule
