require "airdrop.k"

module VAULT-SYNTAX
    imports AIRDROP-SYNTAX
    syntax VaultTx ::= ETHAddress "deposits" NFTList
                    | ETHAddress "withdraws" NFTList
    syntax ETHTransaction ::= VaultTx
    syntax ETHAddress ::= "BAYCToken" | "Vault"
endmodule

module VAULT
    imports VAULT-SYNTAX
    imports AIRDROP

    rule <k> exec(Player:ETHAddress deposits NFT:Int fee GasFee:Int)  => 
            Player in BAYCToken gets -1 // fungible token
            ...
         </k> 
         <S> S => S[(Vault in NFT) <- 1:Int][(Player in NFT) <- 0:Int] </S>
         <B> ... .List => ListItem(Player deposits NFT fee GasFee) </B>
    
    rule <k> exec(Player:ETHAddress deposits NFT:Int , NFTs:NFTList fee GasFee:Int)  => 
            Player in BAYCToken gets -1 ~> // fungible token
            Player deposits NFTs fee GasFee    
            ...
         </k> 
         <S> S => S[(Vault in NFT) <- 1:Int][(Player in NFT) <- 0:Int] </S>
         <B> ... .List => ListItem(Player deposits NFT fee GasFee) </B>
    
    rule <k> exec(Player:ETHAddress withdraws NFT:Int fee GasFee:Int)  => 
            Player in BAYCToken gets 1 // fungible token
            ...
         </k> 
         <S> S => S[(Vault in NFT) <- 0:Int][(Player in NFT) <- 1:Int] </S>
         <B> ... .List => ListItem(Player withdraws NFT fee GasFee) </B>
    
    rule <k> exec(Player:ETHAddress withdraws NFT:Int , NFTs:NFTList fee GasFee:Int)  => 
            Player in BAYCToken gets 1 ~> // fungible token
            Player withdraws NFTs fee GasFee    
            ...
         </k> 
         <S> S => S[(Vault in NFT) <- 0:Int][(Player in NFT) <- 1:Int] </S>
         <B> ... .List => ListItem(Player withdraws NFT fee GasFee) </B>
    



endmodule
