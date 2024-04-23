import smartpy as sp

import utils.errors as Errors
from utils.administrable_mixin import SingleAdministrableMixin


class BurnState:
    PROPOSED = 0
    CONFIRMED = 1


class Burn:
    def get_type():
        return sp.TRecord(
            proposer=sp.TAddress,
            receiver=sp.TString,
            amount=sp.TNat,
            state=sp.TNat,
            fee=sp.TNat,
            utxos=sp.TMap(UTXO.get_key_type(), UTXO.get_burn_type()),
        ).layout(("proposer", ("receiver", ("amount", ("state", ("fee", "utxos"))))))

    def make(proposer, receiver, amount, state, fee, utxos):
        return sp.set_type_expr(
            sp.record(
                proposer=proposer,
                receiver=receiver,
                amount=amount,
                fee=fee,
                utxos=utxos,
                state=state,
            ),
            Burn.get_type(),
        )


class UTXO_STATE:
    INIT = 0
    USED_FOR_MINT = 1


class UTXO:
    def get_key_type():
        return sp.TRecord(
            txid=sp.TBytes,
            output_no=sp.TNat,
        ).layout(("txid", "output_no"))

    def get_candidate_key_type():
        return sp.TRecord(
            receiver=sp.TOption(sp.TAddress),
            amount=sp.TNat,
        ).layout(("receiver", "amount"))

    def get_utxo_candidate_value_type():
        return sp.TRecord(
            approvers=sp.TSet(sp.TAddress),
            candidates=sp.TMap(UTXO.get_candidate_key_type(), sp.TSet(sp.TAddress)),
        ).layout(("approvers", "candidates"))

    def get_value_type():
        return sp.TRecord(
            state=sp.TNat,
            receiver=sp.TOption(sp.TAddress),
            amount=sp.TNat,
        ).layout(("state", ("receiver", "amount")))

    def get_burn_type():
        return sp.TRecord(
            amount=sp.TNat,
            signatures=sp.TMap(
                sp.TAddress, sp.TBytes
            ),  # map from signer address to signature.
        ).layout(("amount", "signatures"))

    def make_key(txid, output_no):
        return sp.set_type_expr(
            sp.record(
                txid=txid,
                output_no=output_no,
            ),
            UTXO.get_key_type(),
        )

    def make_value(state, receiver, amount):
        return sp.set_type_expr(
            sp.record(state=state, receiver=receiver, amount=amount),
            UTXO.get_value_type(),
        )

    def make_candidate_key_type(receiver, amount):
        return sp.set_type_expr(
            sp.record(
                receiver=receiver,
                amount=amount,
            ),
            UTXO.get_candidate_key_type(),
        )

    def make_utxo_candidate_value_type(approvers, candidates):
        return sp.set_type_expr(
            sp.record(approvers=approvers, candidates=candidates),
            UTXO.get_utxo_candidate_value_type(),
        )

    def make_burn_type(amount, signatures):
        return sp.set_type_expr(
            sp.record(amount=amount, signatures=signatures), UTXO.get_burn_type()
        )


def execute_fa1_token_transfer(token_address, sender, receiver, amount):
    """
    Creates and execute a FA1 token transfer.

    Parameters
    ----------
    token_address: sp.TAddress
        The FA1 token contract.
    sender: sp.TAddress
        The owner of the tokens in whose name the transfer is made.
    receiver: sp.TAddress
        The receiver of the tokens.
    amount: sp.TNat
        The amount of tokens transfered.

    Raises
    ------
    InvalidEntrypoint: transfer
        If the token contract does not have an FA1 compliant transfer entrypoint.
    """
    transfer_entrypoint = sp.contract(
        sp.TPair(sp.TAddress, sp.TPair(sp.TAddress, sp.TNat)),
        token_address,
        entry_point="transfer",
    ).open_some("InvalidEntrypoint: transfer")

    payload = sp.pair(sender, sp.pair(receiver, amount))
    sp.transfer(payload, sp.mutez(0), transfer_entrypoint)


"""
"""


class TzBTCLedger(sp.Contract, SingleAdministrableMixin):
    def __init__(
        self,
        administrators=sp.big_map(l={}, tkey=sp.TAddress, tvalue=sp.TNat),
        administrators_num=sp.nat(0),
        gatekeepers=sp.big_map(l={}, tkey=sp.TAddress, tvalue=sp.TUnit),
        trusted_signers=sp.big_map(l={}, tkey=sp.TAddress, tvalue=sp.TUnit),
        threshold=sp.nat(3),
        token_address=sp.address("KT1PWx2mnDueood7fEmfbBDKx1D9BAnnXitn"),
        treasury_address=sp.address("KT1PWx2mnDueood7fEmfbBDKx1D9BAnnXitn"),
        btc_gatekeeper_address=sp.bytes("0xff"),
        custody_btc_address=sp.bytes("0xff"),
        service_fee=sp.nat(100),
        min_burn_amount=sp.nat(100),
        redeem_address=sp.address("KT1PWx2mnDueood7fEmfbBDKx1D9BAnnXitn"),
        max_btc_network_fee=sp.nat(1000000),
        max_utxo_per_tx_count = sp.nat(20)
    ):
        metadata = sp.big_map(
            l={
                "": sp.bytes(
                    "0x74657a6f732d73746f726167653a64617461"
                ),  # "tezos-storage:data"
                "data": sp.utils.bytes_of_string(
                    '{ "name": "tzBTC Ledger Contract", "authors": ["Papers <contact@papers.ch>"], "homepage":  "https://www.papers.ch" }'
                ),
            },
            tkey=sp.TString,
            tvalue=sp.TBytes,
        )

        self.init_type(
            sp.TRecord(
                administrators=sp.TBigMap(sp.TAddress, sp.TNat),
                administrators_num=sp.TNat,
                gatekeepers=sp.TBigMap(sp.TAddress, sp.TUnit),
                trusted_signers=sp.TBigMap(sp.TAddress, sp.TUnit),
                whitelisted_addresses=sp.TBigMap(sp.TAddress, sp.TUnit),
                threshold=sp.TNat,
                min_burn_amount=sp.TNat,
                service_fee=sp.TNat,
                max_btc_network_fee=sp.TNat,
                burn_id_counter=sp.TNat,
                burns_map=sp.TBigMap(sp.TNat, Burn.get_type()),
                utxo_map=sp.TBigMap(UTXO.get_key_type(), UTXO.get_value_type()),
                candidate_utxo_map=sp.TBigMap(
                    UTXO.get_key_type(), UTXO.get_utxo_candidate_value_type()
                ),
                metadata=sp.TBigMap(sp.TString, sp.TBytes),
                token_address=sp.TAddress,
                treasury_address=sp.TAddress,
                redeem_address=sp.TAddress,
                btc_gatekeeper_address=sp.TBytes,
                custody_btc_address=sp.TBytes,
                max_utxo_per_tx_count=sp.TNat
            )
        )

        self.init(
            administrators=administrators,
            administrators_num=administrators_num,
            gatekeepers=gatekeepers,
            trusted_signers=trusted_signers,
            whitelisted_addresses=sp.big_map(l={}, tkey=sp.TAddress, tvalue=sp.TUnit),
            threshold=threshold,
            min_burn_amount=min_burn_amount,
            burns_map=sp.big_map(l={}, tkey=sp.TNat, tvalue=Burn.get_type()),
            utxo_map=sp.big_map(
                l={}, tkey=UTXO.get_key_type(), tvalue=UTXO.get_value_type()
            ),
            candidate_utxo_map=sp.big_map(
                l={},
                tkey=UTXO.get_key_type(),
                tvalue=UTXO.get_utxo_candidate_value_type(),
            ),
            burn_id_counter=sp.nat(0),
            service_fee=service_fee,
            max_btc_network_fee=max_btc_network_fee,
            token_address=token_address,
            treasury_address=treasury_address,
            redeem_address=redeem_address,
            btc_gatekeeper_address=btc_gatekeeper_address,
            custody_btc_address=custody_btc_address,
            max_utxo_per_tx_count=max_utxo_per_tx_count,
            metadata=metadata,
        )

    @sp.private_lambda(with_storage="read-only", with_operations=False, wrap_call=True)
    def verify_is_gatekeeper(self, unit):
        """
        Verifies if the sender of the operation is a gatekeeper.

        Parameters
        ----------
        unit: sp.TUnit
            Unit parameter

        Raises
        ------
        NotGatekeeper
            If the sender of the operation is not a gatekeeper
        """
        sp.verify(
            self.data.gatekeepers.contains(sp.sender), message=Errors.NOT_GATEKEEPER
        )

    @sp.private_lambda(with_storage="read-only", with_operations=False, wrap_call=True)
    def verify_is_trusted_signer(self, unit):
        """
        Verifies if the sender of the operation is a trusted signer.

        Parameters
        ----------
        unit: sp.TUnit
            Unit parameter

        Raises
        ------
        NotTrustedSigner
            If the sender of the operation is not a trusted signer
        """
        sp.verify(
            self.data.trusted_signers.contains(sp.sender),
            message=Errors.NOT_TRUSTED_SIGNER,
        )

    @sp.private_lambda(with_storage="read-only", with_operations=False, wrap_call=True)
    def verify_is_verified_user(self, unit):
        """
        Verifies if the sender of the operation is a verified user.

        Parameters
        ----------
        unit: sp.TUnit
            Unit parameter

        Raises
        ------
        NotVerifiedUser
            If the sender of the operation is not a verified user
        """
        sp.verify(
            self.data.whitelisted_addresses.contains(sp.sender),
            message=Errors.NOT_VERIFIED_USER,
        )

    @sp.entry_point(check_no_incoming_transfer=True)
    def confirm_utxo(self, param):
        """
        Confirms an UTXO which will be used for mint if enough signers confirm it.
        This entrypoint can only be called by a trusted signer and it adds an UTXO
        candidate to the storage or increase the number of confirmations for the given
        candidate UTXO.
        If one candidate has enough confirmations, it creates a new entry in the UTXO
        map to be used for a mint.

        Parameters
        ----------
        amount: sp.TNat
            The amount spent by the UTXO.
        output_no: sp.TNat
            The output number associated with the UTXO
        receiver: sp.TAddress
            The receiving tezos address of tzBTC once enough confirmations are sent.
        txid: sp.TBytes
            The transaction id of the UTXO.

        Raises
        ------
        NotTrustedSigner
            If the caller is not a trusted signer of the contract.
        AmountTooLow
            If the amount in the UTXO is lower than the service fee.
        UTXOAlreadyConfirmed
            If the UTXO has enough confirmations.
        MultipleConfirmationsFromSameSignerNotAllowed
            If the same sender tries to confirm the same UTXO more than once (even if
            the parameters are different)
        """
        param_type = sp.TRecord(
            amount=sp.TNat, output_no=sp.TNat, receiver=sp.TAddress, txid=sp.TBytes
        ).layout(("amount", ("output_no", ("receiver", "txid"))))
        sp.set_type(param, param_type)

        self.verify_is_trusted_signer(sp.unit)
        sp.verify(param.amount >= self.data.service_fee, message=Errors.AMOUNT_TOO_LOW)
        utxo_key = sp.local("utxo_key", UTXO.make_key(param.txid, param.output_no))
        sp.verify(
            ~self.data.utxo_map.contains(utxo_key.value),
            message=Errors.UTXO_ALREADY_CONFIRMED,
        )

        candidate_utxo = sp.local(
            "candidate_utxo",
            self.data.candidate_utxo_map.get(
                utxo_key.value,
                default_value=UTXO.make_utxo_candidate_value_type(
                    sp.set([]), sp.map({})
                ),
            ),
        )
        sp.verify(
            ~candidate_utxo.value.approvers.contains(sp.sender),
            message=Errors.SIGNER_ALREADY_CONFIRMED,
        )
        candidate_utxo.value.approvers.add(sp.sender)

        candidate_key = sp.local(
            "candidate_key",
            UTXO.make_candidate_key_type(sp.some(param.receiver), param.amount),
        )
        candidate_approvers = sp.local(
            "candidate_approvers",
            candidate_utxo.value.candidates.get(
                candidate_key.value, default_value=sp.set([])
            ),
        )
        candidate_approvers.value.add(sp.sender)
        candidate_utxo.value.candidates[candidate_key.value] = candidate_approvers.value
        self.data.candidate_utxo_map[utxo_key.value] = candidate_utxo.value

        with sp.if_(
            sp.len(candidate_utxo.value.candidates[candidate_key.value])
            >= self.data.threshold
        ):
            self.data.utxo_map[utxo_key.value] = UTXO.make_value(
                state=UTXO_STATE.INIT,
                receiver=candidate_key.value.receiver,
                amount=candidate_key.value.amount,
            )
            del self.data.candidate_utxo_map[utxo_key.value]

    @sp.entry_point(check_no_incoming_transfer=True)
    def confirm_change_utxo(self, created_utxos):
        """
        Confirms a change in a list UTXOs. All UTXOs that are used for a burn, will either
        be completely spent or split. If an UTXO is split after a burn, the signer should
        call this entrypoint to add the newly created UTXO to the candidates map.

        The old UTXO would have been completely removed from the storage in the
        confirm_burn entrypoint.

        For each candidate of a new UTXO we increase the number of approvers. If there
        are enough approvers for a candidate, that candidate becomes the new UTXO, it is
        added to the utxo_map and the UTXO can be later spent by a burn (the state of
        UTXO becomes USED_FOR_MINT).

        Parameters
        ----------
        created_utxos: sp.TList(single_param_type)
            A list of all new created UTXOs after a burn.
        A single entry in the list contains:
        amount: sp.TNat
            The amount spent by the UTXO.
        output_no: sp.TNat
            The output number associated with the UTXO
        txid: sp.TBytes
            The transaction id of the UTXO.

        Raises
        ------
        NotTrustedSigner
            If the caller is not a trusted signer of the contract.
        MultipleConfirmationsFromSameSignerNotAllowed
            If the same sender tries to confirm the same UTXO more than once (even if
            the parameters are different)
        """
        single_param_type = sp.TRecord(
            txid=sp.TBytes, output_no=sp.TNat, amount=sp.TNat
        ).layout(("txid", ("output_no", "amount")))
        sp.set_type(created_utxos, sp.TList(single_param_type))

        self.verify_is_trusted_signer(sp.unit)

        with sp.for_("utxo", created_utxos) as utxo:
            utxo_key = sp.local("utxo_key", UTXO.make_key(utxo.txid, utxo.output_no))

            with sp.if_(~self.data.utxo_map.contains(utxo_key.value)):
                candidate_utxo = sp.local(
                    "candidate_utxo",
                    self.data.candidate_utxo_map.get(
                        utxo_key.value,
                        default_value=sp.record(
                            approvers=sp.set([]), candidates=sp.map({})
                        ),
                    ),
                )
                sp.verify(
                    ~candidate_utxo.value.approvers.contains(sp.sender),
                    message=Errors.SIGNER_ALREADY_CONFIRMED,
                )
                candidate_utxo.value.approvers.add(sp.sender)

                candidate_key = sp.local(
                    "candidate_key", UTXO.make_candidate_key_type(sp.none, utxo.amount)
                )
                candidate_approvers = sp.local(
                    "candidate_approvers",
                    candidate_utxo.value.candidates.get(
                        candidate_key.value, default_value=sp.set([])
                    ),
                )
                candidate_approvers.value.add(sp.sender)
                candidate_utxo.value.candidates[candidate_key.value] = (
                    candidate_approvers.value
                )
                self.data.candidate_utxo_map[utxo_key.value] = candidate_utxo.value

                with sp.if_(
                    sp.len(candidate_utxo.value.candidates[candidate_key.value])
                    >= self.data.threshold
                ):
                    self.data.utxo_map[utxo_key.value] = UTXO.make_value(
                        state=UTXO_STATE.USED_FOR_MINT,
                        receiver=candidate_key.value.receiver,
                        amount=candidate_key.value.amount,
                    )
                    del self.data.candidate_utxo_map[utxo_key.value]

    @sp.entry_point(check_no_incoming_transfer=True)
    def mint(self, txid, output_no):
        """
        Calls mints on the tzBTC contract if enough confirmations were sent for the
        associated UTXO and mints the amount in the UTXO for the receiver. The service
        fee is taken away from the receiver and minted for the treasury instead.

        Parameters
        ----------
        txid: sp.TBytes
            The txid of the associated UTXO.
        output_no: sp.TNat
            The output number of the associated UTXO.

        Raises
        ------
        NotGatekeeper
            If the caller of the entrypoints is not a gatekeeper of the contract.
        InvalidUTXOKey
            If the UTXO key is not part of the UTXO map.
        InvalidUTXOState
            If the UTXO is not in the INIT state.
        ReceiverNotSet
            If the receiver for the tzBTC has not been set in the UTXO.
        """
        sp.set_type(txid, sp.TBytes)
        sp.set_type(output_no, sp.TNat)
        self.verify_is_gatekeeper(sp.unit)

        utxo_key = sp.local("utxo_key", UTXO.make_key(txid, output_no))
        sp.verify(
            self.data.utxo_map.contains(utxo_key.value), message=Errors.INVALID_UTXO_KEY
        )

        utxo_value = sp.local("utxo_value", self.data.utxo_map[utxo_key.value])
        sp.verify(
            utxo_value.value.state == UTXO_STATE.INIT, message=Errors.INVALID_UTXO_STATE
        )

        utxo_value.value.state = UTXO_STATE.USED_FOR_MINT
        self.data.utxo_map[utxo_key.value] = utxo_value.value

        mint_contract_ep = sp.contract(
            sp.TPair(sp.TAddress, sp.TNat), self.data.token_address, entry_point="mint"
        ).open_some("Invalid Entrypoint: mint")

        entitled_amount = sp.local(
            "entitled_amount",
            sp.as_nat(utxo_value.value.amount - self.data.service_fee),
        )

        sp.verify(utxo_value.value.receiver.is_some(), message=Errors.RECEIVER_NOT_SET)
        sp.transfer(
            sp.pair(utxo_value.value.receiver.open_some(), entitled_amount.value),
            sp.mutez(0),
            mint_contract_ep,
        )
        sp.transfer(
            sp.pair(self.data.treasury_address, self.data.service_fee),
            sp.mutez(0),
            mint_contract_ep,
        )

    @sp.entry_point(check_no_incoming_transfer=True)
    def set_utxo(self, txid, output_no, receiver, amount, utxo_state):
        """
        Creates or Updates an UTXO. This entrypoint can only be called by an admin and it
        is a failsafe mechanism if something goes wrong with the UTXOs.

        Parameters
        ----------
        txid: sp.TBytes
            The transaction id of the UTXO.
        output_no: sp.TNat
            The output number of the UTXO.
        receiver: sp.TOption(sp.TAddress)
            The tezos address that should receive the tzBTC (if any)
        amount: sp.TNat
            The amount associated with the UTXO.
        utxo_state: sp.TNat
            A value of 0, 1 or 2 corresponding to the UTXO state.

        Raises
        ------
        NotAdmin
            If the caller of the entrypoint is not an admin of the contract.
        InvalidUTXOState
            If the UTXO state is not 0 or 1.
        """
        sp.set_type(txid, sp.TBytes)
        sp.set_type(output_no, sp.TNat)
        sp.set_type(receiver, sp.TOption(sp.TAddress))
        sp.set_type(amount, sp.TNat)
        sp.set_type(utxo_state, sp.TNat)

        self.verify_is_admin(sp.unit)
        sp.verify(utxo_state < 2, message=Errors.INVALID_UTXO_STATE)

        utxo_key = sp.local("utxo_key", UTXO.make_key(txid, output_no))
        self.data.utxo_map[utxo_key.value] = UTXO.make_value(
            state=utxo_state, receiver=receiver, amount=amount
        )

    @sp.entry_point(check_no_incoming_transfer=True)
    def remove_utxo(self, txid, output_no):
        """
        Removes an UTXO entirely from the map. This entrypoint can only be called by an
        admin and it is a failsafe mechanism if something goes wrong with the UTXOs.

        Parameters
        ----------
        txid: sp.TBytes
            The transaction id of the UTXO.
        output_no: sp.TNat
            The output number of the UTXO.

        Raises
        ------
        NotAdmin
            If the caller of the entrypoint is not an admin of the contract.
        """
        sp.set_type(txid, sp.TBytes)
        sp.set_type(output_no, sp.TNat)

        self.verify_is_admin(sp.unit)

        utxo_key = sp.local("utxo_key", UTXO.make_key(txid, output_no))
        del self.data.utxo_map[utxo_key.value]

    @sp.entry_point(check_no_incoming_transfer=True)
    def set_max_utxo_per_tx_count(self, max_utxo_per_tx_count):
        """
        sets the maximum count per transaction allowed of UTXOs

        Parameters
        ----------
        max_utxo_per_tx_count: sp.TNat
            The maximum number of UTXOs per transaction.

        Raises
        ------
        NotAdmin
            If the caller of the entrypoint is not an admin of the contract.
        """
        sp.set_type(max_utxo_per_tx_count, sp.TNat)
        self.verify_is_admin(sp.unit)

        self.data.max_utxo_per_tx_count = max_utxo_per_tx_count

    @sp.entry_point(check_no_incoming_transfer=True)
    def verify_address(self, address, verified):
        """
        Adds/Removes an address from the big_map of verified addresses.

        Parameters
        ----------
        address: sp.TAddress
            The address to be added to the verified big map.
        verified: sp.TBool
            If true the address is added, if false the address is remove from the map.

        Raises
        ------
        NotGatekeeper
            If the sender of the operation is not a gatekeeper for the contract.
        """
        sp.set_type(address, sp.TAddress)
        sp.set_type(verified, sp.TBool)

        self.verify_is_gatekeeper(sp.unit)
        with sp.if_(verified):
            self.data.whitelisted_addresses[address] = sp.unit
        with sp.else_():
            del self.data.whitelisted_addresses[address]

    @sp.entry_point(check_no_incoming_transfer=True)
    def propose_burn(self, amount, receiver, optional_callback):
        """
        Creates a new entry for a future burn for the given amount. The new burn entry
        will hold the information about the amount and the receiver of BTC. The fee and
        UTXOs attached to this burn will be later added in the confirm_burn entrypoint.
        It transfers the given amount of BTC from the caller to this contract. The
        contract will hold the funds until the burn is confirmed or canceled.

        The optional callback is used to return the id of the newly created burn entry.

        Parameters
        ----------
        amount: sp.TNat
            The amount of tzBTC to be burnt.
        receiver: sp.TString
            The receiving BTC address after the tzBTC are burnt.
        optional_callback: sp.TOption(sp.TContract(sp.TNat))
            A optional callback contract to return the newly created burn entry.

        Raises
        ------
        NotVerifiedUser
            If the caller is not part of the verified users.
        AmountTooLow
            If the amount proposed to be burnt is lower than the minimum amount allowed to
            be burnt.
        """
        sp.set_type(amount, sp.TNat)
        sp.set_type(receiver, sp.TString)
        sp.set_type(optional_callback, sp.TOption(sp.TContract(sp.TNat)))

        self.verify_is_verified_user(sp.unit)
        sp.verify(amount >= self.data.min_burn_amount, message=Errors.AMOUNT_TOO_LOW)

        self.data.burns_map[self.data.burn_id_counter] = Burn.make(
            proposer=sp.sender,
            receiver=receiver,
            amount=amount,
            state=BurnState.PROPOSED,
            fee=0,
            utxos=sp.map({}),
        )

        self.data.burn_id_counter += 1
        execute_fa1_token_transfer(
            self.data.token_address, sp.sender, sp.self_address, amount
        )

        with sp.if_(optional_callback.is_some()):
            callback = sp.local("callback", optional_callback.open_some())
            sp.transfer(self.data.burn_id_counter, sp.mutez(0), callback.value)

    @sp.entry_point(check_no_incoming_transfer=True)
    def cancel_burn(self, burn_id):
        """
        Cancels a proposed burn, removes the entry from the burns map and transfers back
        the proposed burn amount to the proposer.

        Parameters
        ----------
        burn_id: sp.TNat
            The id of the burn to be cancelled.

        Raises
        ------
        InvalidBurnId
            If burn id is not present in the burns map.
        NotAllowed
            If the caller is not the proposer of the burn or a gatekeeper of the contract.
        BurnAlreadyConfirmed
            If the burn has already been confirmed.
        """
        sp.set_type(burn_id, sp.TNat)
        sp.verify(self.data.burns_map.contains(burn_id), message=Errors.INVALID_BURN_ID)
        sp.verify(
            (self.data.burns_map[burn_id].proposer == sp.sender)
            | (self.data.gatekeepers.contains(sp.sender)),
            message=Errors.NOT_ALLOWED,
        )
        sp.verify(
            self.data.burns_map[burn_id].state == BurnState.PROPOSED,
            message=Errors.BURN_ALREADY_CONFIRMED,
        )

        execute_fa1_token_transfer(
            token_address=self.data.token_address,
            sender=sp.self_address,
            receiver=self.data.burns_map[burn_id].proposer,
            amount=self.data.burns_map[burn_id].amount,
        )

        del self.data.burns_map[burn_id]

    @sp.entry_point(check_no_incoming_transfer=True)
    def confirm_burn(self, utxos, fee, burn_id):
        """
        Confirms the burn with the given burn id to the signers by attaching a list of
        UTXOs to the given burn and checks if the given UTXOs cover the amount specified
        by the burn + fees.
        This entrypoint also calls burns on the tzBTC contract after checking that the
        UTXOs covers the burn.

        Parameters
        ----------
        utxos: sp.TMap(UTXO.key_type(), UTXO.burn_type())
            The list of UTXOs to cover the burn amount.
        fee: sp.TNat
            The fee associated with each UTXO.
        burn_id: sp.TNat
            The id of the burn for which the UTXOs are checked.

        Raises
        ------
        NotGatekeeper
            If the caller of the entrypoint is not a gatekeeper.
        InvalidBurnId
            If the burns map does not contain the given burn id.
        InvalidState
            If the burn is not in the proposed state
        InvalidUTXOKey
            If any of the given UTXO are not present in the UTXO map.
        InvalidUTXOState
            If any of the given UTXOs are not in the USED_FOR_MINT state.
        AmountTooLow
            If the given UTXOs does not cover the proposed burnt amount + fees.
        """
        sp.set_type(utxos, sp.TMap(UTXO.get_key_type(), UTXO.get_burn_type()))
        sp.set_type(fee, sp.TNat)
        sp.set_type(burn_id, sp.TNat)

        self.verify_is_gatekeeper(sp.unit)
        sp.verify(self.data.burns_map.contains(burn_id), message=Errors.INVALID_BURN_ID)

        amount_covered_by_utxos = sp.local("amount_covered_by_utxos", sp.nat(0))
        fee_paid_for_all_utxos = sp.local("fee_paid_for_all_utxos", sp.nat(0))

        burn_op = sp.local("burn_op", self.data.burns_map[burn_id])
        sp.verify(
            burn_op.value.state == BurnState.PROPOSED, message=Errors.INVALID_BURN_STATE
        )

        sp.verify(sp.len(utxos) < self.data.max_utxo_per_tx_count, message=Errors.TOO_MANY_UTXOS)

        with sp.for_("burn_utxo", utxos.items()) as burn_utxo:
            utxo_key = burn_utxo.key
            utxo_value = burn_utxo.value

            sp.verify(
                self.data.utxo_map.contains(utxo_key), message=Errors.INVALID_UTXO_KEY
            )
            utxo = sp.local("utxo", self.data.utxo_map[utxo_key])

            sp.verify(
                utxo.value.state == UTXO_STATE.USED_FOR_MINT,
                message=Errors.INVALID_UTXO_STATE,
            )

            sp.verify(sp.len(burn_utxo.value.signatures) == 0,
                message=Errors.SIGNATURE_CANNOT_BE_SET,
            )

            amount_covered_by_utxos.value += utxo_value.amount
            fee_paid_for_all_utxos.value += fee

            # Remove the UTXO from the utxo map (the output UTXO will be later added in
            # the confirmChangeUTXO)
            del self.data.utxo_map[utxo_key]

        sp.verify(
            amount_covered_by_utxos.value
            >= burn_op.value.amount,
            message=Errors.AMOUNT_TOO_LOW,
        )
        sp.verify(
            fee_paid_for_all_utxos.value <= self.data.max_btc_network_fee,
            message=Errors.FEE_TOO_HIGH,
        )

        burn_op.value.utxos = utxos
        burn_op.value.fee = fee_paid_for_all_utxos.value
        burn_op.value.state = BurnState.CONFIRMED
        self.data.burns_map[burn_id] = burn_op.value

        # call burn on the tzBTC contract (first we need to transfer the amount to the
        # redeem address)
        amount_to_burn = sp.local(
            "amount_to_burn", sp.as_nat(burn_op.value.amount - self.data.service_fee)
        )
        execute_fa1_token_transfer(
            self.data.token_address,
            sp.self_address,
            self.data.redeem_address,
            amount_to_burn.value,
        )
        execute_fa1_token_transfer(
            self.data.token_address,
            sp.self_address,
            self.data.treasury_address,
            self.data.service_fee,
        )

        burn_contract_ep = sp.contract(
            sp.TNat, self.data.token_address, entry_point="burn"
        ).open_some("Invalid Entrypoint: burn")
        sp.transfer(amount_to_burn.value, sp.mutez(0), burn_contract_ep)

    @sp.entry_point(check_no_incoming_transfer=True)
    def sign_burn(self, burn_id, utxos_with_signature):
        """
        Sets the signatures for all UTXOs contained by a burn. It can only be called by
        a trusted signer and contains a list of signatures for each UTXO to craft the BTC
        transaction associated with the UTXO.
        The signature is added to the associated UTXO to be later used in crafting the BTC
        transaction. The signatures will be stored with the associated signer that calls
        this entrypoint.

        NOTE: Not all UTXOs attached to the burn are required by this entrypoint. The
        signer can send their signatures for the UTXOs by calling sign_burn multiple
        times.

        Parameters
        ----------
        burn_id:
            The id of the burn with the associated UTXOs
        utxos_with_signature
            A list of UTXOs and their associated signature for the BTC transaction
            crafting.

        Raises
        ------
        NotTrustedSigner
            If the caller is not part of the trusted signers map.
        InvalidBurnId
            If the given burn id is not in the burns map
        UTXONotPartOfBurn
            If any of the given UTXOs is not attached to the burn.

        """
        sp.set_type(burn_id, sp.TNat)
        sp.set_type(
            utxos_with_signature,
            sp.TList(
                sp.TRecord(
                    txid=sp.TBytes, output_no=sp.TNat, signature=sp.TBytes
                ).right_comb()
            ),
        )

        self.verify_is_trusted_signer(sp.unit)
        sp.verify(self.data.burns_map.contains(burn_id), message=Errors.INVALID_BURN_ID)

        burn = sp.local("burn", self.data.burns_map[burn_id])
        utxos = sp.local("utxos", burn.value.utxos)

        with sp.for_("entry", utxos_with_signature) as entry:
            utxo_key = sp.local("utxo_key", UTXO.make_key(entry.txid, entry.output_no))
            sp.verify(
                utxos.value.contains(utxo_key.value),
                message=Errors.UTXO_NOT_PART_OF_BURN,
            )
            utxo = sp.local("utxo", utxos.value[utxo_key.value])
            utxo.value.signatures[sp.sender] = entry.signature

            utxos.value[utxo_key.value] = utxo.value

        burn.value.utxos = utxos.value
        self.data.burns_map[burn_id] = burn.value

    @sp.entry_point(check_no_incoming_transfer=True)
    def remove_burn(self, burn_id):
        """
        Removes an entry from the burns_map. Can only be called by the admin and it is
        used to clear up the burns_map. It is the responsability of the caller to make
        sure that the burn was executed successfully and the signatures are no longer
        required.

        Parameters
        ----------
        burn_id:
            The id of the burn with the associated UTXOs

        Raises
        ------
        NotAdmin
            If the caller is not an admin of the contract.
        InvalidBurnId
            If the given burn id is not in the burns map
        """
        sp.set_type(burn_id, sp.TNat)

        self.verify_is_admin(sp.unit)
        sp.verify(self.data.burns_map.contains(burn_id), message=Errors.INVALID_BURN_ID)
        del self.data.burns_map[burn_id]

    @sp.onchain_view()
    def get_latest_burn_id(self):
        """
        Returns the id of the latest created burn entry in the burns map.
        """
        with sp.if_(self.data.burn_id_counter > 0):
            sp.result(self.data.burn_id_counter)
        with sp.else_():
            sp.result(sp.as_nat(self.data.burn_id_counter - 1))
