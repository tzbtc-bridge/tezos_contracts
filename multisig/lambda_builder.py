import smartpy as sp

DUMMY = sp.address("tz1YY1LvD6TFH4z74pvxPQXBjAKHE5tB5Q8f")

TZBTC_LEDGER_MAINNET = sp.address("KT1DuiB3C9dcLKmRewiVWEVVE5nbXngo2Ci5")
TZBTC_LEDGER_GHOSTNET = sp.address("KT1G9hWQUjfd76atZZm2SfwhC6vAzDzzWKSu")

TZBTC_LEDGER = TZBTC_LEDGER_GHOSTNET


CHAINID_MAINNET = "0x7a06a770"
CHAINID_GHOSTNET = "0xaf1864d9"
CHAINID = CHAINID_GHOSTNET

MULTISIG_MAINNET = "KT1JuyPBgJRZCdPm5tcRSaTagYPehwzEZVhu"
# MULTISIG_GHOSTNET = "KT1Q8so1rT58kAy4Epk4unbAiAuxiErBfSxk"
MULTISIG_GHOSTNET = "KT1GdJdfkqXNM8VsNEmJxKE4PM6JGxkqhnSe"

MULTISIG = MULTISIG_GHOSTNET

COUNTER = 1

def accept_admin_proposal(unit):
    sp.set_type(unit, sp.TUnit)

    ledger_ep = sp.contract(
        sp.TUnit, TZBTC_LEDGER, entry_point="accept_admin_proposal"
    ).open_some(message="InvalidEntrypoint: accept_admin_proposal")

    sp.result(sp.list([
        sp.transfer_operation(sp.unit, sp.mutez(0), ledger_ep)
    ]))

def add_gatekeeper(unit, gatekeeper_address):
    sp.set_type(unit, sp.TUnit)

    ledger_ep = sp.contract(
        sp.TAddress, TZBTC_LEDGER, entry_point="add_gatekeeper"
    ).open_some(message="InvalidEntrypoint: add_gatekeeper")

    sp.result(sp.list([
        sp.transfer_operation(gatekeeper_address, sp.mutez(0), ledger_ep)
    ]))

def add_trusted_signer(unit, trusted_signer_address):
    sp.set_type(unit, sp.TUnit)
    
    ledger_ep = sp.contract(
        sp.TAddress, TZBTC_LEDGER, entry_point="add_trusted_signer"
    ).open_some(message="InvalidEntrypoint: add_trusted_signer")

    sp.result(sp.list([
        sp.transfer_operation(trusted_signer_address, sp.mutez(0), ledger_ep)
    ]))

def propose_administrator(unit, proposed_administrator):
    sp.set_type(unit, sp.TUnit)
    
    ledger_ep = sp.contract(
        sp.TAddress, TZBTC_LEDGER, entry_point="propose_administrator"
    ).open_some(message="InvalidEntrypoint: propose_administrator")

    sp.result(sp.list([
        sp.transfer_operation(proposed_administrator, sp.mutez(0), ledger_ep)
    ]))

def remove_administrator(unit, administrator_to_remove):
    sp.set_type(unit, sp.TUnit)
    
    ledger_ep = sp.contract(
        sp.TAddress, TZBTC_LEDGER, entry_point="remove_administrator"
    ).open_some(message="InvalidEntrypoint: remove_administrator")

    sp.result(sp.list([
        sp.transfer_operation(administrator_to_remove, sp.mutez(0), ledger_ep)
    ]))

def remove_trusted_signer(unit, trusted_signer_to_remove):
    sp.set_type(unit, sp.TUnit)
    
    ledger_ep = sp.contract(
        sp.TAddress, TZBTC_LEDGER, entry_point="remove_trusted_signer"
    ).open_some(message="InvalidEntrypoint: remove_trusted_signer")

    sp.result(sp.list([
        sp.transfer_operation(trusted_signer_to_remove, sp.mutez(0), ledger_ep)
    ]))

def remove_gatekeeper(unit, gatekeeper_to_remove):
    sp.set_type(unit, sp.TUnit)
    
    ledger_ep = sp.contract(
        sp.TAddress, TZBTC_LEDGER, entry_point="remove_gatekeeper"
    ).open_some(message="InvalidEntrypoint: remove_gatekeeper")

    sp.result(sp.list([
        sp.transfer_operation(gatekeeper_to_remove, sp.mutez(0), ledger_ep)
    ]))

def remove_utxo(unit, txid, output_no):
    sp.set_type(unit, sp.TUnit)
    
    ledger_ep = sp.contract(
        sp.TPair(sp.TNat, sp.TBytes), TZBTC_LEDGER, entry_point="remove_utxo"
    ).open_some(message="InvalidEntrypoint: remove_utxo")

    sp.result(sp.list([
        sp.transfer_operation(sp.pair(output_no, txid), sp.mutez(0), ledger_ep)
    ]))

def set_max_utxo_per_tx_count(unit, max_utxo_per_tx_count):
    sp.set_type(unit, sp.TUnit)
    
    ledger_ep = sp.contract(
        sp.TNat, TZBTC_LEDGER, entry_point="set_max_utxo_per_tx_count"
    ).open_some(message="InvalidEntrypoint: set_max_utxo_per_tx_count")

    sp.result(sp.list([
        sp.transfer_operation(max_utxo_per_tx_count, sp.mutez(0), ledger_ep)
    ]))

def set_utxo(unit, txid, output_no, receiver, amount, utxo_state):
    sp.set_type(unit, sp.TUnit)
    
    ledger_ep = sp.contract(
        sp.TPair(
            sp.TPair(sp.TNat, sp.TNat),
            sp.TPair(
                sp.TOption(sp.TAddress),
                sp.TPair(sp.TBytes, sp.TNat)
            )
        ),
        TZBTC_LEDGER,
        entry_point="set_utxo"
    ).open_some(message="InvalidEntrypoint: set_utxo")

    sp.result(sp.list([
        sp.transfer_operation(
            sp.pair(
                sp.pair(amount, output_no),
                sp.pair(receiver, sp.pair(txid, utxo_state))
            ),
            sp.mutez(0),
            ledger_ep
        )
    ]))

def update_custody_btc_address(unit, custody_btc_address):
    sp.set_type(unit, sp.TUnit)
    
    ledger_ep = sp.contract(
        sp.TBytes, TZBTC_LEDGER, entry_point="update_custody_btc_address"
    ).open_some(message="InvalidEntrypoint: update_custody_btc_address")

    sp.result(sp.list([
        sp.transfer_operation(custody_btc_address, sp.mutez(0), ledger_ep)
    ]))

def update_gatekeeper_btc_address(gatekeeper_btc_address):
    sp.set_type(unit, sp.TUnit)
    
    ledger_ep = sp.contract(
        sp.TBytes, TZBTC_LEDGER, entry_point="update_gatekeeper_btc_address"
    ).open_some(message="InvalidEntrypoint: update_gatekeeper_btc_address")

    sp.result(sp.list([
        sp.transfer_operation(gatekeeper_btc_address, sp.mutez(0), ledger_ep)
    ]))

def update_max_btc_network_fee(unit, max_btc_network_fee):
    sp.set_type(unit, sp.TUnit)
    
    ledger_ep = sp.contract(
        sp.TNat, TZBTC_LEDGER, entry_point="update_max_btc_network_fee"
    ).open_some(message="InvalidEntrypoint: update_max_btc_network_fee")

    sp.result(sp.list([
        sp.transfer_operation(max_btc_network_fee, sp.mutez(0), ledger_ep)
    ]))

def update_min_burn_amount(unit, min_burn_amount):
    sp.set_type(unit, sp.TUnit)
    
    ledger_ep = sp.contract(
        sp.TNat, TZBTC_LEDGER, entry_point="update_min_burn_amount"
    ).open_some(message="InvalidEntrypoint: update_min_burn_amount")

    sp.result(sp.list([
        sp.transfer_operation(min_burn_amount, sp.mutez(0), ledger_ep)
    ]))

def update_redeem_address(redeem_address):
    sp.set_type(unit, sp.TUnit)

    ledger_ep = sp.contract(
        sp.TAddress, TZBTC_LEDGER, entry_point="update_redeem_address"
    ).open_some(message="InvalidEntrypoint: update_redeem_address")

    sp.result(sp.list([
        sp.transfer_operation(redeem_address, sp.mutez(0), ledger_ep)
    ]))

def update_service_fee(unit, service_fee):
    sp.set_type(unit, sp.TUnit)
    
    ledger_ep = sp.contract(
        sp.TNat, TZBTC_LEDGER, entry_point="update_service_fee"
    ).open_some(message="InvalidEntrypoint: update_service_fee")

    sp.result(sp.list([
        sp.transfer_operation(service_fee, sp.mutez(0), ledger_ep)
    ]))

def update_threshold(unit, threshold):
    sp.set_type(unit, sp.TUnit)
    
    ledger_ep = sp.contract(
        sp.TNat, TZBTC_LEDGER, entry_point="update_threshold"
    ).open_some(message="InvalidEntrypoint: update_threshold")

    sp.result(sp.list([
        sp.transfer_operation(threshold, sp.mutez(0), ledger_ep)
    ]))

def update_treasury_address(unit, treasury_address):
    sp.set_type(unit, sp.TUnit)

    ledger_ep = sp.contract(
        sp.TAddress, TZBTC_LEDGER, entry_point="update_treasury_address"
    ).open_some(message="InvalidEntrypoint: update_treasury_address")

    sp.result(sp.list([
        sp.transfer_operation(treasury_address, sp.mutez(0), ledger_ep)
    ]))

def remove_burn(unit, burn_id):
    sp.set_type(unit, sp.TUnit)

    ledger_ep = sp.contract(
        sp.TNat, TZBTC_LEDGER, entry_point="remove_burn"
    ).open_some(message="InvalidEntrypoint: remove_burn")

    sp.result(sp.list([
        sp.transfer_operation(burn_id, sp.mutez(0), ledger_ep)
    ]))

class MultiSigPayload:
    def make_change_keys(
        chain_id: str,
        multisig_contract_address: str,
        counter: int,
        threshold: int,
        keys: list,
    ):
        execution_payload = sp.pair(
            sp.pair(sp.chain_id_cst(chain_id), sp.address(multisig_contract_address)),
            sp.pair(
                sp.nat(counter),
                sp.variant(
                    "change_keys",
                    sp.pair(
                        sp.nat(threshold),
                        sp.list(l=list(map(lambda x: sp.key(x), keys)), t=sp.TKey),
                    ),
                ),
            ),
        )

        return sp.set_type_expr(execution_payload, MultiSigPayload.get_type())

    def make_lambda(
        chain_id: str, multisig_contract_address: str, counter: int, _lambda
    ):
        execution_payload = sp.pair(
            sp.pair(sp.chain_id_cst(chain_id), sp.address(multisig_contract_address)),
            sp.pair(sp.nat(counter), sp.variant("operation", sp.build_lambda(_lambda))),
        )
        return sp.set_type_expr(execution_payload, MultiSigPayload.get_type())

    def get_type():
        return sp.TPair(
            sp.TPair(sp.TChainId, sp.TAddress),
            sp.TPair(
                sp.TNat,
                sp.TVariant(
                    operation=sp.TLambda(sp.TUnit, sp.TList(sp.TOperation)),
                    change_keys=sp.TPair(sp.TNat, sp.TList(sp.TKey)),
                ).layout(("operation", "change_keys")),
            ),
        )


class LambdaBuilder(sp.Contract):
    def __init__(self, **kargs):
        self.init(**kargs)

    @sp.entry_point
    def aggregation_builder(self, execution_payload):
        sp.set_type(
            execution_payload,
            sp.TLambda(sp.TPair(sp.TString, sp.TPair(sp.TNat, sp.TNat)), sp.TNat),
        )
        sp.local("execution", execution_payload)

    @sp.entry_point
    def builder(self, execution_payload):
        sp.set_type(execution_payload, sp.TLambda(sp.TUnit, sp.TList(sp.TOperation)))
        sp.local("execution", execution_payload)

    @sp.entry_point
    def multisig_builder(self, execution_payload):
        sp.set_type(execution_payload, MultiSigPayload.get_type())

        # operation = sp.local("operation", sp.snd(execution_payload))
        sp.snd(sp.snd(execution_payload))(sp.unit).rev()
        # execution_payload(sp.unit).rev()


if __name__ == "__main__":

    @sp.add_test(name="LambdaBuilder")
    def test():
        scenario = sp.test_scenario()
        lambda_builder = LambdaBuilder()
        scenario += lambda_builder

        lambda_to_send = lambda unit: set_utxo(unit, sp.bytes("0xbb"), 11, sp.none, 22, 1)
        # lambda_to_send = lambda unit: accept_admin_proposal(unit)
        execution_payload = MultiSigPayload.make_lambda(
            chain_id=CHAINID,
            multisig_contract_address=MULTISIG,
            counter=COUNTER,
            _lambda=lambda_to_send,
        )
        packed_payload = sp.pack(execution_payload)
        scenario.show(packed_payload)
        lambda_builder.builder(sp.build_lambda(lambda_to_send))
        lambda_builder.multisig_builder(execution_payload)