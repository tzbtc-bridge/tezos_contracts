from pytezos import pytezos
import multisig.lambda_builder as settings 

# LAMBDA = '{ DROP; NIL operation; PUSH address "KT1G9hWQUjfd76atZZm2SfwhC6vAzDzzWKSu"; CONTRACT %accept_admin_proposal unit; IF_NONE { PUSH string "InvalidEntrypoint: accept_admin_proposal"; FAILWITH } {}; PUSH mutez 0; UNIT; TRANSFER_TOKENS; CONS }'
LAMBDA = '{ DROP; NIL operation; PUSH address "KT1G9hWQUjfd76atZZm2SfwhC6vAzDzzWKSu"; CONTRACT %set_utxo (pair (pair nat nat) (pair (option address) (pair bytes nat))); IF_NONE { PUSH string "InvalidEntrypoint: set_utxo"; FAILWITH } {}; PUSH mutez 0; PUSH (pair (pair nat nat) (pair (option address) (pair bytes nat))) (Pair (Pair 22 11) (Pair None (Pair 0xbb 1))); TRANSFER_TOKENS; CONS }'

def main():
    """This executes a multisig operation"""
    secret_key = "edsk..."
    shell = "https://ghostnet.smartpy.io/"
    pytezos_admin_client = pytezos.using(key=secret_key, shell=shell)
    multisig_contract = pytezos_admin_client.contract(settings.MULTISIG_GHOSTNET)

    result = multisig_contract.main(
        payload={"counter": settings.COUNTER, "action": {"operation": LAMBDA}},
        sigs=[
            "edsigtjkdxBuvMoRJ8cseaa2fUGk5DQ2tGb1ePxodNTQ7BAsTsLgP7yggSPjFH3c1zaotLtXyNdEVHphkUrKSophH7oWABEPfMY",  
            None,  
        ],
    ).send()
    print(result)


if __name__ == "__main__":
    main()
