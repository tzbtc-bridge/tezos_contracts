from pytezos.operation.result import OperationResult
from pytezos import pytezos, ContractInterface
import time
import sys
from deployments.utils import get_address, wait_applied
import deployments.mainnet.configuration as mainnet_config
import deployments.ghostnet.configuration as ghostnet_config


def deploy(config):
    pytezos_admin_client = pytezos.using(key=config.SECRET_KEY, shell=config.NODE_URL)

    tzbtc_ledger_code = ContractInterface.from_file(
        "__SNAPSHOTS__/compilation/all/tzBTCLedger/step_000_cont_0_contract.tz"
    )
    storage = tzbtc_ledger_code.storage.dummy()
    storage['administrators'] = config.ADMINISTRATORS
    storage['administrators_num'] = config.ADMINISTRATORS_NUM
    storage['gatekeepers'] = config.GATEKEEPERS
    storage['trusted_signers'] = config.TRUSTED_SIGNERS
    storage['whitelisted_addresses'] = {}
    storage['threshold'] = config.THRESHOLD
    storage['min_burn_amount'] = config.MIN_BURN_AMOUNT
    storage['service_fee'] = config.SERVICE_FEE
    storage['max_btc_network_fee'] = config.MAX_BTC_NETWORK_FEE
    storage['burn_id_counter'] = 0 
    storage['burns_map'] = {}
    storage['utxo_map'] = {}
    storage['candidate_utxo_map'] = {}
    storage['token_address'] = config.TOKEN_ADDRESS
    storage['treasury_address'] = config.TREASURY_ADDRESS
    storage['redeem_address'] = config.REDEEM_ADDRESS
    storage['btc_gatekeeper_address'] = config.BTC_GATEKEEPER_ADDRESS
    storage['custody_btc_address'] = config.CUSTODY_BTC_ADDRESS
    storage['metadata'] = config.METADATA
    storage['max_utxo_per_tx_count'] = config.MAX_UTXO_PER_TX_COUNT

    operation_group = pytezos_admin_client.origination(
        script=tzbtc_ledger_code.script(initial_storage=storage)
    ).send()
    address = get_address(pytezos_admin_client, operation_group.hash())
    print("TZBTC ledger address: " + address)

    # This will faill for mainnet deployment, but we can do this manually.
    tzbtc_contract = pytezos_admin_client.contract(config.TOKEN_ADDRESS)
    operation_group = tzbtc_contract.addOperator(address).send()
    wait_applied(pytezos_admin_client, operation_group.hash())

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Invalid number of arguments")
    
    network = sys.argv[1]
    if network == "ghostnet":
        deploy(ghostnet_config)
    elif network == "mainnet":
        deploy(mainnet_config)
    else:
        print("Invalid network name") 