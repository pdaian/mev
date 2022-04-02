require "execution.k"

module AIRDROP-SYNTAX
    imports EXECUTION-SYNTAX
    syntax NFTList ::= Int 
                    | Int "," NFTList
    syntax AirdropTx ::= ETHAddress "claims for" NFTList
    syntax ETHTransaction ::= AirdropTx
    syntax ETHAddress ::= "ApeCoin"
endmodule

module AIRDROP
    imports AIRDROP-SYNTAX
    imports EXECUTION

    rule <k> exec(Player:ETHAddress claims for NFT:Int fee GasFee:Int)  => 
            Player in ApeCoin gets 60564000000000000000000 // 60564 ApeCoins airdropped
            ...
         </k> 
         <C> C => C[NFT <- 1:Int] </C>
         <B> ... .List => ListItem(Player claims for NFT fee GasFee) </B>
        requires notBool (NFT in keys(C)) //otherwise already claimed

    rule <k> exec(Player:ETHAddress claims for NFT:Int , NFTs:NFTList fee GasFee:Int)  => 
            Player in ApeCoin gets 60564000000000000000000  ~>
            Player claims for NFTs fee GasFee
            ...
         </k> 
         <C> C => C[NFT <- 1:Int] </C>
         <B> ... .List => ListItem(Player claims for NFT fee GasFee) </B>
        requires notBool (NFT in keys(C)) //otherwise already claimed
endmodule
