import smartpy as sp

from utils.administrable_mixin import SingleAdministrableMixin, AdministratorStatus
from contracts.tzbtc_ledger import TzBTCLedger, UTXO, UTXO_STATE, Burn, BurnState


class DummyTzBtcToken(sp.Contract):
    def __init__(
        self,
        administrator,
        redeem_address,
    ):
        self.init_type(
            sp.TRecord(
                ledger=sp.TBigMap(
                    sp.TAddress,
                    sp.TRecord(
                        approvals=sp.TMap(sp.TAddress, sp.TNat), balance=sp.TNat
                    ),
                ),
                total_supply=sp.TNat,
                administrator=sp.TAddress,
                redeem_address=sp.TAddress,
                operators=sp.TBigMap(sp.TAddress, sp.TUnit),
            )
        )

        self.init(
            ledger=sp.big_map(
                l={},
                tkey=sp.TAddress,
                tvalue=sp.TRecord(
                    approvals=sp.TMap(sp.TAddress, sp.TNat), balance=sp.TNat
                ),
            ),
            total_supply=sp.nat(0),
            administrator=administrator,
            redeem_address=redeem_address,
            operators=sp.big_map(l={}, tkey=sp.TAddress, tvalue=sp.TUnit),
        )

    @sp.entry_point
    def transfer(self, params):
        sp.set_type(params, sp.TPair(sp.TAddress, sp.TPair(sp.TAddress, sp.TNat)))
        from_ = sp.fst(params)
        to_ = sp.fst(sp.snd(params))
        value = sp.snd(sp.snd(params))

        sp.verify(
            (
                (from_ == sp.sender)
                | (self.data.ledger[from_].approvals[sp.sender] >= value)
            ),
            message="NotAllowed",
        )
        self.maybe_add_address(from_)
        self.maybe_add_address(to_)
        sp.verify(
            self.data.ledger[from_].balance >= value, message="InsufficientBalance"
        )

        self.data.ledger[from_].balance = sp.as_nat(
            self.data.ledger[from_].balance - value
        )
        self.data.ledger[to_].balance += value
        with sp.if_(from_ != sp.sender):
            self.data.ledger[from_].approvals[sp.sender] = sp.as_nat(
                self.data.ledger[from_].approvals[sp.sender] - value
            )

    @sp.entrypoint
    def approve(self, params):
        sp.set_type(
            params,
            sp.TRecord(spender=sp.TAddress, value=sp.TNat).layout(("spender", "value")),
        )
        self.maybe_add_address(sp.sender)
        already_approved = self.data.ledger[sp.sender].approvals.get(params.spender, 0)
        sp.verify(
            (already_approved == 0) | (params.value == 0),
            message="UnsafeAllowanceChange",
        )
        self.data.ledger[sp.sender].approvals[params.spender] = params.value

    def maybe_add_address(self, address):
        with sp.if_(~self.data.ledger.contains(address)):
            self.data.ledger[address] = sp.record(balance=0, approvals={})

    def is_operator(self, sender):
        return self.data.operators.contains(sender)

    @sp.entry_point
    def mint(self, params):
        sp.set_type(params, sp.TPair(sp.TAddress, sp.TNat))
        sp.verify(self.is_operator(sp.sender), message="NotOperator")

        self.maybe_add_address(sp.fst(params))
        self.data.ledger[sp.fst(params)].balance += sp.snd(params)
        self.data.total_supply += sp.snd(params)

    @sp.entry_point
    def burn(self, param):
        sp.set_type(param, sp.TNat)
        sp.verify(self.is_operator(sp.sender), message="NotOperator")

        sp.verify(
            self.data.ledger[self.data.redeem_address].balance >= param,
            message="InsufficientBalance",
        )
        self.data.ledger[self.data.redeem_address].balance = sp.as_nat(
            self.data.ledger[self.data.redeem_address].balance - param
        )
        self.data.total_supply = sp.as_nat(self.data.total_supply - param)

    @sp.entry_point
    def add_operator(self, params):
        sp.set_type(params, sp.TAddress)
        sp.verify(self.data.administrator == sp.sender, message="NotAdmin")
        self.data.operators[params] = sp.unit


@sp.add_test(name="TzBTC Ledger")
def test():
    scenario = sp.test_scenario()

    scenario.h1("TzBTC Ledger Unit Tests")
    scenario.table_of_contents()

    scenario.h2("Set up/Bootstrapping")
    token_admin = sp.test_account("TokenAdmin")
    redeem_address = sp.test_account("RedeemAddress")
    token_contract = DummyTzBtcToken(token_admin.address, redeem_address.address)
    scenario += token_contract

    ledger_admin = sp.test_account("LedgerAdmin")
    gatekeeper = sp.test_account("Gatekeeper")
    signer1 = sp.test_account("Signer1")
    signer2 = sp.test_account("Signer2")
    signer3 = sp.test_account("Signer3")
    treasury = sp.test_account("Treasury")
    alice = sp.test_account("Alice")
    bob = sp.test_account("Bob")
    charlie = sp.test_account("Charlie")
    dan = sp.test_account("Dan")

    # Constants of the contract
    THRESHOLD = sp.nat(2)
    BTC_GATEKEEPER_ADDRESS = sp.bytes("0xff")
    BTC_CUSTODY_ADDRESS = sp.bytes("0xfe")
    SERVICE_FEE = 100
    MIN_BURN_AMOUNT = 100
    MAX_BTC_NETWORK_FEE = 1_000

    tzbtc_ledger = TzBTCLedger(
        administrators=sp.big_map({ledger_admin.address: AdministratorStatus.SET}),
        administrators_num=sp.nat(1),
        gatekeepers=sp.big_map({gatekeeper.address: sp.unit}),
        trusted_signers=sp.big_map(
            {
                signer1.address: sp.unit,
                signer2.address: sp.unit,
                signer3.address: sp.unit,
            }
        ),
        threshold=THRESHOLD,
        token_address=token_contract.address,
        treasury_address=treasury.address,
        btc_gatekeeper_address=BTC_GATEKEEPER_ADDRESS,
        custody_btc_address=BTC_CUSTODY_ADDRESS,
        service_fee=SERVICE_FEE,
        min_burn_amount=MIN_BURN_AMOUNT,
        redeem_address=redeem_address.address,
        max_btc_network_fee=MAX_BTC_NETWORK_FEE,
    )
    scenario += tzbtc_ledger

    scenario.h2("Token Contract Accounts")
    scenario.show([token_admin, redeem_address])
    scenario.h2("TzBTC ledger Accounts")
    scenario.show(
        [ledger_admin, gatekeeper, signer1, signer2, signer3, treasury, alice, bob]
    )

    # Set the tzbtc ledger as an operator for the token contract
    scenario += token_contract.add_operator(tzbtc_ledger.address).run(
        sender=token_admin
    )

    #####################################################################################
    #                                confirm_utxo checks                                #
    #####################################################################################
    scenario.h2("confirm_utxo")

    scenario.p("NonSigners cannot call confirm_utxo")
    scenario += tzbtc_ledger.confirm_utxo(
        sp.record(
            amount=sp.nat(1000),
            output_no=sp.nat(0),
            receiver=alice.address,
            txid=sp.bytes("0xffffff"),
        )
    ).run(sender=alice, valid=False)

    scenario.p("confirm_utxo fails if amount is too low")
    scenario += tzbtc_ledger.confirm_utxo(
        sp.record(
            amount=sp.nat(SERVICE_FEE - 1),
            output_no=sp.nat(0),
            receiver=alice.address,
            txid=sp.bytes("0xffffff"),
        )
    ).run(sender=signer1, valid=False)

    scenario.p("new confirm_utxo passed if it is sent by signer")
    UTXO_KEY = UTXO.make_key(sp.bytes("0xeeeeee"), sp.nat(0))
    scenario += tzbtc_ledger.confirm_utxo(
        sp.record(
            amount=sp.nat(1000),
            output_no=sp.nat(0),
            receiver=bob.address,
            txid=sp.bytes("0xeeeeee"),
        )
    ).run(sender=signer1)
    candidate_bob_key = UTXO.make_candidate_key_type(sp.some(bob.address), sp.nat(1000))
    scenario.verify_equal(
        tzbtc_ledger.data.candidate_utxo_map[UTXO_KEY],
        UTXO.make_utxo_candidate_value_type(
            approvers=sp.set([signer1.address]),
            candidates=sp.map({candidate_bob_key: sp.set([signer1.address])}),
        ),
    )

    scenario.p(
        "confirm_utxo from the same signer with different amount/receiver is not allowed"
    )
    UTXO_KEY = UTXO.make_key(sp.bytes("0xeeeeee"), sp.nat(0))
    scenario += tzbtc_ledger.confirm_utxo(
        sp.record(
            amount=sp.nat(1000),
            output_no=sp.nat(0),
            receiver=alice.address,  # changed the receiver to alice
            txid=sp.bytes("0xeeeeee"),
        )
    ).run(
        sender=signer1, valid=False
    )  # signer 1 already sent the confirmation.

    scenario.p("confirm_utxo passed if it is sent by signer")
    UTXO_KEY = UTXO.make_key(sp.bytes("0xffffff"), sp.nat(0))
    scenario += tzbtc_ledger.confirm_utxo(
        sp.record(
            amount=sp.nat(1000),
            output_no=sp.nat(0),
            receiver=alice.address,
            txid=sp.bytes("0xffffff"),
        )
    ).run(sender=signer1)
    candidate_alice_key = UTXO.make_candidate_key_type(
        sp.some(alice.address), sp.nat(1000)
    )

    scenario.verify_equal(
        tzbtc_ledger.data.candidate_utxo_map[UTXO_KEY],
        UTXO.make_utxo_candidate_value_type(
            approvers=sp.set([signer1.address]),
            candidates=sp.map({candidate_alice_key: sp.set([signer1.address])}),
        ),
    )

    scenario.p(
        "confirm_utxo new candidate is created if same utxo contains different receiver"
    )
    scenario += tzbtc_ledger.confirm_utxo(
        sp.record(
            amount=sp.nat(1000),
            output_no=sp.nat(0),
            receiver=bob.address,  # receiver was changed to bob.
            txid=sp.bytes("0xffffff"),
        )
    ).run(sender=signer2)
    candidate_bob_key = UTXO.make_candidate_key_type(sp.some(bob.address), sp.nat(1000))
    scenario.verify_equal(
        tzbtc_ledger.data.candidate_utxo_map[UTXO_KEY],
        UTXO.make_utxo_candidate_value_type(
            approvers=sp.set([signer1.address, signer2.address]),
            candidates=sp.map(
                {
                    candidate_alice_key: sp.set([signer1.address]),
                    candidate_bob_key: sp.set([signer2.address]),
                }
            ),
        ),
    )

    scenario.p("confirm_utxo creates an utxo with enough signers confirming it")
    scenario += tzbtc_ledger.confirm_utxo(
        sp.record(
            amount=sp.nat(1000),
            output_no=sp.nat(0),
            receiver=alice.address,
            txid=sp.bytes("0xffffff"),
        )
    ).run(sender=signer3)
    # candidate is removed once the quorum has been reached and a new UTXO is created
    scenario.verify(tzbtc_ledger.data.candidate_utxo_map.contains(UTXO_KEY) == False)
    scenario.verify_equal(
        tzbtc_ledger.data.utxo_map[UTXO_KEY],
        UTXO.make_value(
            state=UTXO_STATE.INIT, receiver=sp.some(alice.address), amount=sp.nat(1000)
        ),
    )

    #####################################################################################
    #                                 mint checks                                       #
    #####################################################################################
    scenario.h2("Minting")
    scenario.p("Minting fails if the caller is not the gatekeeper")
    scenario += tzbtc_ledger.mint(txid=sp.bytes("0xffffff"), output_no=sp.nat(0)).run(
        sender=alice, valid=False
    )

    scenario.p("Minting fails if the UTXO does not exist")
    scenario += tzbtc_ledger.mint(txid=sp.bytes("0xffffff"), output_no=sp.nat(1)).run(
        sender=gatekeeper, valid=False
    )

    scenario.p("Minting fails if the UTXO is not in the init state")
    # setup
    scenario += tzbtc_ledger.set_utxo(
        txid=sp.bytes("0xeeeeee"),
        output_no=sp.nat(0),
        receiver=sp.some(alice.address),
        amount=sp.nat(1000),
        utxo_state=UTXO_STATE.USED_FOR_MINT,
    ).run(sender=ledger_admin)
    scenario += tzbtc_ledger.mint(txid=sp.bytes("0xeeeeee"), output_no=sp.nat(0)).run(
        sender=gatekeeper, valid=False
    )

    scenario.p("Minting fails if there is no receiver set in the UTXO")
    # setup
    scenario += tzbtc_ledger.set_utxo(
        txid=sp.bytes("0xeeeeee"),
        output_no=sp.nat(0),
        receiver=sp.none,
        amount=sp.nat(1000),
        utxo_state=UTXO_STATE.INIT,
    ).run(sender=ledger_admin)
    scenario += tzbtc_ledger.mint(txid=sp.bytes("0xeeeeee"), output_no=sp.nat(0)).run(
        sender=gatekeeper, valid=False
    )
    # clean up
    scenario += tzbtc_ledger.remove_utxo(
        txid=sp.bytes("0xeeeeee"),
        output_no=sp.nat(0),
    ).run(sender=ledger_admin)

    scenario.p("Minting goes through")
    scenario += tzbtc_ledger.mint(txid=sp.bytes("0xffffff"), output_no=sp.nat(0)).run(
        sender=gatekeeper
    )
    scenario.verify_equal(
        token_contract.data.ledger[alice.address].balance, sp.nat(1000 - SERVICE_FEE)
    )
    scenario.verify_equal(
        token_contract.data.ledger[treasury.address].balance, sp.nat(SERVICE_FEE)
    )
    scenario.verify_equal(
        tzbtc_ledger.data.utxo_map[UTXO_KEY].state, UTXO_STATE.USED_FOR_MINT
    )

    #####################################################################################
    #                           confirm_change_utxo checks                              #
    #####################################################################################
    scenario.h2("Confirm Change UTXO")
    scenario.p("confirm_change_utxo fails if the sender is not trusted signer")
    scenario += tzbtc_ledger.confirm_change_utxo(
        sp.list(
            [
                sp.record(
                    txid=sp.bytes("0xdddddd"),
                    output_no=sp.nat(0),
                    amount=sp.nat(1000),
                )
            ]
        )
    ).run(sender=alice, valid=False)

    scenario.p("confirm_change_utxo creates candidate if the sender is a signer")
    UTXO_KEY = UTXO.make_key(sp.bytes("0xdddddd"), sp.nat(0))
    scenario += tzbtc_ledger.confirm_change_utxo(
        sp.list(
            [
                sp.record(
                    txid=sp.bytes("0xdddddd"),
                    output_no=sp.nat(0),
                    amount=sp.nat(1000),
                )
            ]
        )
    ).run(sender=signer1)
    candidate_1000_key = UTXO.make_candidate_key_type(sp.none, sp.nat(1000))
    scenario.verify_equal(
        tzbtc_ledger.data.candidate_utxo_map[UTXO_KEY],
        UTXO.make_utxo_candidate_value_type(
            approvers=sp.set([signer1.address]),
            candidates=sp.map({candidate_1000_key: sp.set([signer1.address])}),
        ),
    )

    scenario.p("confirm_change_utxo fails if the same signer tries to confirm again")
    scenario += tzbtc_ledger.confirm_change_utxo(
        sp.list(
            [
                sp.record(
                    txid=sp.bytes("0xdddddd"),
                    output_no=sp.nat(0),
                    amount=sp.nat(1000),
                )
            ]
        )
    ).run(sender=signer1, valid=False)

    scenario.p(
        "confirm_change_utxo creates a new candidate from a signer with different amount"
    )
    scenario += tzbtc_ledger.confirm_change_utxo(
        sp.list(
            [
                sp.record(
                    txid=sp.bytes("0xdddddd"),
                    output_no=sp.nat(0),
                    amount=sp.nat(999),
                )
            ]
        )
    ).run(sender=signer2)
    candidate_999_key = UTXO.make_candidate_key_type(sp.none, sp.nat(999))
    scenario.verify_equal(
        tzbtc_ledger.data.candidate_utxo_map[UTXO_KEY],
        UTXO.make_utxo_candidate_value_type(
            approvers=sp.set([signer1.address, signer2.address]),
            candidates=sp.map(
                {
                    candidate_1000_key: sp.set([signer1.address]),
                    candidate_999_key: sp.set([signer2.address]),
                }
            ),
        ),
    )

    scenario.p(
        "confirm_change_utxo creates a candidate if enough confirmations are sent"
    )
    scenario += tzbtc_ledger.confirm_change_utxo(
        sp.list(
            [
                sp.record(
                    txid=sp.bytes("0xdddddd"),
                    output_no=sp.nat(0),
                    amount=sp.nat(1000),
                )
            ]
        )
    ).run(sender=signer3)
    scenario.verify(tzbtc_ledger.data.candidate_utxo_map.contains(UTXO_KEY) == False)
    scenario.verify_equal(
        tzbtc_ledger.data.utxo_map[UTXO_KEY],
        UTXO.make_value(
            state=UTXO_STATE.USED_FOR_MINT, receiver=sp.none, amount=sp.nat(1000)
        ),
    )

    ######################################################################################
    #                                set_utxo checks                                     #
    ######################################################################################
    scenario.h2("Set UTXO")
    scenario.p("set_utxo fails if sender is not admin")
    scenario += tzbtc_ledger.set_utxo(
        txid=sp.bytes("0xeeeeee"),
        output_no=sp.nat(0),
        receiver=sp.none,
        amount=sp.nat(1000),
        utxo_state=UTXO_STATE.INIT,
    ).run(sender=alice, valid=False)

    scenario.p("set_utxo fails the set state is not valid")
    scenario += tzbtc_ledger.set_utxo(
        txid=sp.bytes("0xeeeeee"),
        output_no=sp.nat(0),
        receiver=sp.none,
        amount=sp.nat(1000),
        utxo_state=2,  # No such state exists
    ).run(sender=ledger_admin, valid=False)

    scenario.p("set_utxo goes through")
    scenario += tzbtc_ledger.set_utxo(
        txid=sp.bytes("0xeeeeee"),
        output_no=sp.nat(0),
        receiver=sp.none,
        amount=sp.nat(1000),
        utxo_state=UTXO_STATE.USED_FOR_MINT,
    ).run(sender=ledger_admin)

    ######################################################################################
    #                              remove_utxo checks                                    #
    ######################################################################################
    scenario.h2("Remove UTXO")
    scenario.p("remove_utxo fails if sender is not admin")
    scenario += tzbtc_ledger.remove_utxo(
        txid=sp.bytes("0xeeeeee"),
        output_no=sp.nat(0),
    ).run(sender=alice, valid=False)

    scenario.p("remove_utxo goes through")
    scenario += tzbtc_ledger.remove_utxo(
        txid=sp.bytes("0xeeeeee"),
        output_no=sp.nat(0),
    ).run(sender=ledger_admin)

    ######################################################################################
    #                             verify_address checks                                  #
    ######################################################################################
    scenario.h2("Verify address")
    scenario.p("verify_address fails on adding if sender is not gatekeeper")
    scenario += tzbtc_ledger.verify_address(address=alice.address, verified=True).run(
        sender=alice, valid=False
    )

    scenario.p("verify_address adds a whitelisted address")
    scenario += tzbtc_ledger.verify_address(address=alice.address, verified=True).run(
        sender=gatekeeper
    )
    scenario.verify(tzbtc_ledger.data.whitelisted_addresses.contains(alice.address))

    scenario.p("verify_address fails on removing if sender is not gatekeeper")
    scenario += tzbtc_ledger.verify_address(address=alice.address, verified=False).run(
        sender=alice, valid=False
    )

    scenario.p("verify_address removes the whitelisted address")
    scenario += tzbtc_ledger.verify_address(address=alice.address, verified=False).run(
        sender=gatekeeper
    )
    scenario.verify(~tzbtc_ledger.data.whitelisted_addresses.contains(alice.address))

    ######################################################################################
    #                             propose_burn checks                                    #
    ######################################################################################
    scenario.h2("Propose burn")
    # Set up
    alice_bitcoin_addr = sp.bytes("0xf0f0f0")
    scenario += tzbtc_ledger.verify_address(address=alice.address, verified=True).run(
        sender=gatekeeper
    )

    scenario.p("propose burn fails if the sender is not verified user")
    scenario += tzbtc_ledger.propose_burn(
        amount=sp.nat(1000), receiver=alice_bitcoin_addr, optional_callback=sp.none
    ).run(sender=bob, valid=False)

    scenario.p("propose burn fails if the amount is too low")
    scenario += tzbtc_ledger.propose_burn(
        amount=sp.nat(MIN_BURN_AMOUNT - 1),
        receiver=alice_bitcoin_addr,
        optional_callback=sp.none,
    ).run(sender=alice, valid=False)

    scenario.p("propose burn goes through")
    # Setup
    scenario += token_contract.approve(
        sp.record(spender=tzbtc_ledger.address, value=sp.nat(900))
    ).run(sender=alice)

    scenario += tzbtc_ledger.propose_burn(
        amount=sp.nat(900), receiver=alice_bitcoin_addr, optional_callback=sp.none
    ).run(sender=alice)
    scenario.verify(tzbtc_ledger.data.burn_id_counter == sp.nat(1))
    scenario.verify(
        token_contract.data.ledger[tzbtc_ledger.address].balance == sp.nat(900)
    )
    scenario.verify_equal(
        tzbtc_ledger.data.burns_map[0],
        Burn.make(
            proposer=alice.address,
            receiver=alice_bitcoin_addr,
            amount=sp.nat(900),
            state=BurnState.PROPOSED,
            fee=0,
            utxos=sp.map({}),
        ),
    )

    ######################################################################################
    #                                cancel_burn checks                                  #
    ######################################################################################
    scenario.h2("Cancel burn")
    scenario.p("cancel burn fails if the sender is not the proposer")
    scenario += tzbtc_ledger.cancel_burn(sp.nat(0)).run(sender=bob, valid=False)

    scenario.p("cancel burn fails if the burn id is not valid")
    scenario += tzbtc_ledger.cancel_burn(sp.nat(1)).run(sender=alice, valid=False)

    scenario.p("cancel burn goes through if the sender is a gatekeeper")
    scenario += tzbtc_ledger.cancel_burn(sp.nat(0)).run(sender=gatekeeper)
    scenario.verify(token_contract.data.ledger[alice.address].balance == sp.nat(900))
    scenario.verify(tzbtc_ledger.data.burns_map.contains(sp.nat(0)) == False)

    scenario.p("cancel burn goes through if the sender is the proposer")
    # Setup (alice proposes a burn)
    scenario += token_contract.approve(
        sp.record(spender=tzbtc_ledger.address, value=sp.nat(900))
    ).run(sender=alice)
    scenario += tzbtc_ledger.propose_burn(
        amount=sp.nat(900), receiver=alice_bitcoin_addr, optional_callback=sp.none
    ).run(sender=alice)

    scenario += tzbtc_ledger.cancel_burn(sp.nat(1)).run(sender=alice)
    scenario.verify(token_contract.data.ledger[alice.address].balance == sp.nat(900))
    scenario.verify(tzbtc_ledger.data.burns_map.contains(sp.nat(1)) == False)

    # Note: the check for a burn being already confirmed will be done below in the
    # confirm burn checks as the setup will be created there.

    ######################################################################################
    #                              confirm_burn checks                                   #
    ######################################################################################
    scenario.h2("Confirm burn")
    # set up
    scenario += token_contract.approve(
        sp.record(spender=tzbtc_ledger.address, value=sp.nat(900))
    ).run(sender=alice)
    scenario += tzbtc_ledger.propose_burn(
        amount=sp.nat(900), receiver=alice_bitcoin_addr, optional_callback=sp.none
    ).run(sender=alice)
    BURN_UTXOS = sp.map(
        {
            UTXO.make_key(sp.bytes("0xdddddd"), sp.nat(0)): UTXO.make_burn_type(
                sp.nat(1000), sp.map({})
            ),
            UTXO.make_key(sp.bytes("0xffffff"), sp.nat(0)): UTXO.make_burn_type(
                sp.nat(1000), sp.map({})
            ),
        }
    )

    scenario.p("confirm_burn fails if the sender is not a gatekeeper")
    scenario += tzbtc_ledger.confirm_burn(
        utxos=BURN_UTXOS, fee=sp.nat(0), burn_id=sp.nat(2)
    ).run(sender=alice, valid=False)

    scenario.p("confirm_burn fails if the burn id is invalid")
    scenario += tzbtc_ledger.confirm_burn(
        utxos=BURN_UTXOS, fee=sp.nat(0), burn_id=sp.nat(3)
    ).run(sender=gatekeeper, valid=False)

    scenario.p("confirm_burn fails if any of the utxos are not in the utxos map")
    scenario += tzbtc_ledger.confirm_burn(
        utxos=sp.map(
            {
                UTXO.make_key(sp.bytes("0xdddddd"), sp.nat(0)): UTXO.make_burn_type(
                    sp.nat(1000), sp.map({})
                ),
                UTXO.make_key(sp.bytes("0xeeeeee"), sp.nat(0)): UTXO.make_burn_type(
                    sp.nat(1000), sp.map({})
                ),
                UTXO.make_key(sp.bytes("0xffffff"), sp.nat(0)): UTXO.make_burn_type(
                    sp.nat(1000), sp.map({})
                ),
            }
        ),
        fee=sp.nat(0),
        burn_id=sp.nat(2),
    ).run(sender=gatekeeper, valid=False)

    scenario.p(
        "confirm_burn fails if any of the utxos are not in the USED_FOR_MINT state"
    )
    # set up
    scenario += tzbtc_ledger.set_utxo(
        txid=sp.bytes("0xeeeeee"),
        output_no=sp.nat(0),
        receiver=sp.some(alice.address),
        amount=sp.nat(1000),
        utxo_state=UTXO_STATE.INIT,
    ).run(sender=ledger_admin)
    scenario += tzbtc_ledger.confirm_burn(
        utxos=sp.map(
            {
                UTXO.make_key(sp.bytes("0xdddddd"), sp.nat(0)): UTXO.make_burn_type(
                    sp.nat(1000), sp.map({})
                ),
                UTXO.make_key(sp.bytes("0xeeeeee"), sp.nat(0)): UTXO.make_burn_type(
                    sp.nat(1000), sp.map({})
                ),
                UTXO.make_key(sp.bytes("0xffffff"), sp.nat(0)): UTXO.make_burn_type(
                    sp.nat(1000), sp.map({})
                ),
            }
        ),
        fee=sp.nat(0),
        burn_id=sp.nat(2),
    ).run(sender=gatekeeper, valid=False)
    # clean up
    scenario += tzbtc_ledger.remove_utxo(
        txid=sp.bytes("0xeeeeee"),
        output_no=sp.nat(0),
    ).run(sender=ledger_admin)

    scenario.p("confirm_burn fails if the utxos does not cover the burnt amount + fees")
    scenario += tzbtc_ledger.confirm_burn(
        utxos=sp.map(
            {
                UTXO.make_key(sp.bytes("0xdddddd"), sp.nat(0)): UTXO.make_burn_type(
                    sp.nat(1000), sp.map({})
                ),
            }
        ),
        fee=sp.nat(101),
        burn_id=sp.nat(2),
    ).run(sender=gatekeeper, valid=False)

    scenario.p("confirm_burn goes through")
    scenario += tzbtc_ledger.confirm_burn(
        utxos=BURN_UTXOS, fee=sp.nat(101), burn_id=sp.nat(2)
    ).run(sender=gatekeeper)
    scenario.verify_equal(
        tzbtc_ledger.data.burns_map[sp.nat(2)],
        Burn.make(
            proposer=alice.address,
            receiver=alice_bitcoin_addr,
            amount=sp.nat(900),
            state=BurnState.CONFIRMED,
            fee=2 * 101,
            utxos=BURN_UTXOS,
        ),
    )
    scenario.verify_equal(
        token_contract.data.ledger[tzbtc_ledger.address].balance, sp.nat(0)
    )
    scenario.verify_equal(
        token_contract.data.ledger[treasury.address].balance,
        sp.nat(200),  # 100 from mint + 100 from the burn
    )

    scenario.p(
        "confirm_burn fails if the burn is already confirmed (no longer proposed)"
    )
    scenario += tzbtc_ledger.confirm_burn(
        utxos=BURN_UTXOS, fee=sp.nat(101), burn_id=sp.nat(2)
    ).run(sender=gatekeeper, valid=False)

    # Check for the cancel burn (cancel burn should no longer work once the burn has been
    # confirmed)
    scenario += tzbtc_ledger.cancel_burn(sp.nat(2)).run(sender=gatekeeper, valid=False)
    scenario += tzbtc_ledger.cancel_burn(sp.nat(2)).run(sender=alice, valid=False)

    ######################################################################################
    #                                sign_burn checks                                    #
    ######################################################################################
    scenario.h2("Sign Burn")
    scenario.p("sign_burn fails if the sender is not a trusted signer")
    scenario += tzbtc_ledger.sign_burn(
        burn_id=sp.nat(2),
        utxos_with_signature=sp.list(
            [
                sp.record(
                    txid=sp.bytes("0xdddddd"),
                    output_no=sp.nat(0),
                    signature=sp.bytes("0x000000"),
                ),
                sp.record(
                    txid=sp.bytes("0xffffff"),
                    output_no=sp.nat(0),
                    signature=sp.bytes("0x111000"),
                ),
            ]
        ),
    ).run(sender=alice, valid=False)

    scenario.p("sign_burn fails if burn_id is not in the burns_map")
    scenario += tzbtc_ledger.sign_burn(
        burn_id=sp.nat(3),
        utxos_with_signature=sp.list(
            [
                sp.record(
                    txid=sp.bytes("0xdddddd"),
                    output_no=sp.nat(0),
                    signature=sp.bytes("0x000000"),
                ),
                sp.record(
                    txid=sp.bytes("0xffffff"),
                    output_no=sp.nat(0),
                    signature=sp.bytes("0x111000"),
                ),
            ]
        ),
    ).run(sender=signer1, valid=False)

    scenario.p("sign_burn fails if one of the UTXOs is not part of the burn")
    scenario += tzbtc_ledger.sign_burn(
        burn_id=sp.nat(2),
        utxos_with_signature=sp.list(
            [
                sp.record(
                    txid=sp.bytes("0xdddddd"),
                    output_no=sp.nat(0),
                    signature=sp.bytes("0x000000"),
                ),
                sp.record(
                    txid=sp.bytes("0xeeeeee"),  # not part of the burns utxos
                    output_no=sp.nat(0),
                    signature=sp.bytes("0x111000"),
                ),
            ]
        ),
    ).run(sender=signer1, valid=False)

    scenario.p("sign_burn goes through")
    scenario += tzbtc_ledger.sign_burn(
        burn_id=sp.nat(2),
        utxos_with_signature=sp.list(
            [
                sp.record(
                    txid=sp.bytes("0xdddddd"),
                    output_no=sp.nat(0),
                    signature=sp.bytes("0x000000"),
                ),
                sp.record(
                    txid=sp.bytes("0xffffff"),
                    output_no=sp.nat(0),
                    signature=sp.bytes("0x111000"),
                ),
            ]
        ),
    ).run(sender=signer1)
    scenario.verify_equal(
        tzbtc_ledger.data.burns_map[sp.nat(2)],
        Burn.make(
            proposer=alice.address,
            receiver=alice_bitcoin_addr,
            amount=sp.nat(900),
            state=BurnState.CONFIRMED,
            fee=2 * 101,
            utxos=sp.map(
                {
                    UTXO.make_key(sp.bytes("0xdddddd"), sp.nat(0)): UTXO.make_burn_type(
                        sp.nat(1000), sp.map({signer1.address: sp.bytes("0x000000")})
                    ),
                    UTXO.make_key(sp.bytes("0xffffff"), sp.nat(0)): UTXO.make_burn_type(
                        sp.nat(1000), sp.map({signer1.address: sp.bytes("0x111000")})
                    ),
                }
            ),
        ),
    )

    ######################################################################################
    #                              remove_burn checks                                    #
    ######################################################################################
    scenario.h2("Remove Burn")
    scenario.p("remove_burn fails if the sender is not an admin of the contract")
    scenario += tzbtc_ledger.remove_burn(sp.nat(2)).run(sender=alice, valid=False)

    scenario.p("remove_burn fails if the burn id does not exist")
    scenario += tzbtc_ledger.remove_burn(sp.nat(3)).run(
        sender=ledger_admin, valid=False
    )

    scenario.p("remove_burn goes through")
    scenario += tzbtc_ledger.remove_burn(sp.nat(2)).run(sender=ledger_admin)
    scenario.verify(tzbtc_ledger.data.burns_map.contains(sp.nat(2)) == False)
