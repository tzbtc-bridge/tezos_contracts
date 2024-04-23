# tzBTC ledger

## Description
This contract serves as the source of truth for minting/burning tzBTC. The contract is responsible to keep track of all the incoming UTXOs (minting operations) and outgoing UTXOs (burning operations).

## Compilation
To compile the contract run `make compile-contracts`.

## Deployment
To deploy the contract, firstly you need to update the configuration files. The configuration files
can be found in:
- `deployments/ghostnet/configuration.py` - for ghostnet deployment
- `deployments/mainnet/configuration.py` - for mainnet deployment

After updating the files with the desired values, run the following command:
- `make deploy-ghostnet` - to deploy the contract on ghostnet
- `make deploy-mainnet` - to deploy the contract on mainnet


## Testing
To run the suite of unit tests, run `make test-contracts`.

## Lifecycle of UTXOs
As state before the contract serves as a source of truth for all UTXOs. The life cycle of an UTXO in the contract is the
following.
1. Trusted signers create UTXOs for minting and the UTXO is initialized in the contract (INIT state).
2. If enough trusted signers confirm the same UTXO, it can be used for minting.
3. A mint operation is called and the UTXO's state is changed to USED_FOR_MINT.
4. The UTXO will remaining in the USED_FOR_MINT state as long as the UTXO is not selected for a burn.
5. If the UTXO is selected for a burn, this UTXO is attached to the specific burn and removed from the utxo_map. Note: There can be more than one UTXO attached to a burn. In this case all UTXOs attached to the burn are removed from the utxo_map.
6. The trusted signers then will have to sign all UTXOs attached to the burn.
7. If enough signers have signed the burn UTXOs, the operation is executed on the bitcoin side.
8. Once confirmed on the Bitcoin side, the signers will then have to inform the contract of all the UTXOs that were not completely used for the burn via the confirm_change_utxo entrypoint and a new UTXO will be created in the INIT state.
9. If enough trusted signers confirm the change, then the newly created UTXO will be set to USED_FOR_MINT state (even though in reality it was not used for mint, this allows the backend to still select this UTXO for future burns).

## Restrictions
This section contains restrictions of the contract. These restrictions are not enforced by the contract and can only be stopped by the caller who should never do this operations if specific conditions are not met.

### Service fee update
The service fee should only be updated if there are no active UTXOs that would be used for mint or burn. If the service fee updates during this a period of time this can lead to issues in the contract
where specific operations can never be executed and the UTXOs can never be spent.

### Removing entries from burn map
Removing entries from burn map should be done carefully. Only if the burn has been executed on BITCOIN network should removing of entries happen. The contract does not have the means to check this so it is the responsability of the caller to ensure the restriction is respected.