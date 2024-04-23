import smartpy as sp
import utils.errors as Errors
import utils.constants as Constants


class AdministratorStatus:
    PROPOSED = 0
    SET = 1


class SingleAdministrableMixin:
    """
    Mixin used to compose andministrable functionality of a contract.
    Still requires the inerhiting contract to define the apropiate storage.
    """

    @sp.private_lambda(with_storage="read-only", with_operations=False, wrap_call=True)
    def verify_is_admin(self, unit):
        """
        Verifies if the sender of the operation is a set admin of the contract.

        Parameters
        ----------
        unit: sp.TUnit
            Unit parameter

        Raises
        ------
        NotAdmin
            If the sender of the operation is not a set admin of the contract.
        """
        sp.verify(
            self.data.administrators[sp.sender] == AdministratorStatus.SET,
            message=Errors.NOT_ADMIN,
        )

    @sp.entry_point(check_no_incoming_transfer=True)
    def propose_administrator(self, proposed_admin):
        """
        Propose an address to be added to the admins map of the contract.

        Parameters
        ----------
        proposed_admin: sp.TAddress
            The address which is proposed to become administrator.

        Raises
        ------
        NotAdmin
            If the sender of the operation is not a set admin of the contract.
        """
        sp.set_type(proposed_admin, sp.TAddress)
        self.verify_is_admin(sp.unit)
        sp.verify(
            ~self.data.administrators.contains(proposed_admin),
            message=Errors.ALREADY_ADMIN,
        )

        self.data.administrators[proposed_admin] = AdministratorStatus.PROPOSED

    @sp.entry_point(check_no_incoming_transfer=True)
    def add_gatekeeper(self, gatekeeper):
        """
        Add an address to the gatekeepers map of the contract.

        Parameters
        ----------
        gatekeeper: sp.TAddress
            The address to add as a gatekeeper.

        Raises
        ------
        NotAdmin
            If the sender of the operation is not a set admin of the contract.
        """
        sp.set_type(gatekeeper, sp.TAddress)
        self.verify_is_admin(sp.unit)
        self.data.gatekeepers[gatekeeper] = sp.unit

    @sp.entry_point(check_no_incoming_transfer=True)
    def add_trusted_signer(self, signer):
        """
        Add an address to the set of trusted signers.

        Parameters
        ----------
        trusted_signer: sp.TAddress
            The address to add to the trusted signer set

        Raises
        ------
        NotAdmin
            If the sender of the operation is not a set admin of the contract.
        """
        sp.set_type(signer, sp.TAddress)
        self.verify_is_admin(sp.unit)
        self.data.trusted_signers[signer] = sp.unit

    @sp.entry_point(check_no_incoming_transfer=True)
    def update_threshold(self, threshold):
        """
        Updates the threshold.

        Parameters
        ----------
        threshold: sp.TNat
            The new threshold.

        Raises
        ------
        NotAdmin
            If the sender of the operation is not a set admin of the contract.
        """
        sp.set_type(threshold, sp.TNat)
        self.verify_is_admin(sp.unit)
        self.data.threshold = threshold

    @sp.entry_point(check_no_incoming_transfer=True)
    def update_min_burn_amount(self, min_burn_amount):
        """
        Updates the minimum amount allowed to burn.

        Parameters
        ----------
        min_burn_amount : sp.TNat
            The new minimum amount allowed to burn.

        Raises
        ------
        NotAdmin
            If the sender of the operation is not a set admin of the contract.
        """
        sp.set_type(min_burn_amount, sp.TNat)
        self.verify_is_admin(sp.unit)
        self.data.min_burn_amount = min_burn_amount

    @sp.entry_point(check_no_incoming_transfer=True)
    def update_gatekeeper_btc_address(self, gatekeeper_btc_address):
        """
        Updates the gatekeeper withdrawl BTC address.

        Parameters
        ----------
        gatekeeper_btc_address: sp.TBytes
            The new gatekeeper withdrawl BTC address.

        Raises
        ------
        NotAdmin
            If the sender of the operation is not a set admin of the contract.
        """
        sp.set_type(gatekeeper_btc_address, sp.TBytes)
        self.verify_is_admin(sp.unit)
        self.data.btc_gatekeeper_address = gatekeeper_btc_address

    @sp.entry_point(check_no_incoming_transfer=True)
    def update_custody_btc_address(self, custody_btc_address):
        """
        Updates the custody BTC address.

        Parameters
        ----------
        custody_btc_address: sp.TBytes
            The new custody BTC address.

        Raises
        ------
        NotAdmin
            If the sender of the operation is not a set admin of the contract.
        """
        sp.set_type(custody_btc_address, sp.TBytes)
        self.verify_is_admin(sp.unit)
        self.data.custody_btc_address = custody_btc_address

    @sp.entry_point(check_no_incoming_transfer=True)
    def update_service_fee(self, fee):
        """
        Updates the service fee

        Parameters
        ----------
        fee : sp.TNat
            The new service fee.

        Raises
        ------
        NotAdmin
            If the sender of the operation is not a set admin of the contract.
        """
        sp.set_type(fee, sp.TNat)
        self.verify_is_admin(sp.unit)
        self.data.service_fee = fee

    @sp.entry_point(check_no_incoming_transfer=True)
    def update_max_btc_network_fee(self, max_btc_network_fee):
        """
        Updates the maximum allowed BTC network fee for a transaction.

        Parameters
        ----------
        max_btc_network_fee : sp.TNat
            The new maximum allowed BTC network fee.

        Raises
        ------
        NotAdmin
            If the sender of the operation is not a set admin of the contract.
        """
        sp.set_type(max_btc_network_fee, sp.TNat)
        self.verify_is_admin(sp.unit)
        self.data.max_btc_network_fee = max_btc_network_fee

    @sp.entry_point(check_no_incoming_transfer=True)
    def update_treasury_address(self, treasury_address):
        """
        Updates the treasury address (this address will receive the fees from mints/burns)

        Parameters
        ----------
        treasury_address: sp.TAddress
            The new treasury address.

        Raises
        ------
        NotAdmin
            If the sender of the operation is not a set admin of the contract.
        """
        sp.set_type(treasury_address, sp.TAddress)
        self.verify_is_admin(sp.unit)
        self.data.treasury_address = treasury_address

    @sp.entry_point(check_no_incoming_transfer=True)
    def update_redeem_address(self, redeem_address):
        """
        Updates the redeem address (this address is used to sent the funds before a burn)

        Parameters
        ----------
        redeem_address: sp.TAddress
            The new redeeem address.

        Raises
        ------
        NotAdmin
            If the sender of the operation is not a set admin of the contract.
        """
        sp.set_type(redeem_address, sp.TAddress)
        self.verify_is_admin(sp.unit)
        self.data.redeem_address = redeem_address

    @sp.entry_point(check_no_incoming_transfer=True)
    def accept_admin_proposal(self, unit):
        """
        Entrypoint called by a proposed address to accept the administrator role.

        Parameters
        ----------
        unit: sp.TUnit
            The unit parameter.

        Raises
        ------
        NotProposedAdmin
            If the caller of the entrypoint is not a proposed admin of the contract.
        """
        sp.set_type(unit, sp.TUnit)
        sp.verify(
            self.data.administrators[sp.sender] == AdministratorStatus.PROPOSED,
            message=Errors.NOT_PROPOSED_ADMIN,
        )
        self.data.administrators[sp.sender] = AdministratorStatus.SET
        self.data.administrators_num += 1

    @sp.entry_point(check_no_incoming_transfer=True)
    def remove_administrator(self, administrator_to_remove):
        """
        Entrypoint called by a set admin to remove an administrator account (not
        necessarily the same address as the caller).

        Parameters
        ----------
        administrator_to_remove: sp.TAddress
            The address to be remove as administrator.

        Raises
        ------
        NotAdmin
            If the caller of the entrypoint is not a set admin of the contract.
        """
        sp.set_type(administrator_to_remove, sp.TAddress)
        self.verify_is_admin(sp.unit)
        sp.verify(
            self.data.administrators_num > 1, message=Errors.CANNOT_REMOVE_LAST_ADMIN
        )

        del self.data.administrators[administrator_to_remove]
        self.data.administrators_num = sp.as_nat(self.data.administrators_num - 1)

    @sp.entry_point(check_no_incoming_transfer=True)
    def remove_gatekeeper(self, gatekeeper_to_remove):
        """
        Entrypoint called by a set admin to remove a gatekeeper account.

        Parameters
        ----------
        gatekeeper_to_remove: sp.TAddress
            The address to be remove as gatekeeper.

        Raises
        ------
        NotAdmin
            If the caller of the entrypoint is not a set admin of the contract.
        """
        sp.set_type(gatekeeper_to_remove, sp.TAddress)
        self.verify_is_admin(sp.unit)
        del self.data.gatekeepers[gatekeeper_to_remove]

    @sp.entry_point(check_no_incoming_transfer=True)
    def remove_trusted_signer(self, signer):
        """
        Entrypoint called by a set admin to remove a trusted signer.

        Parameters
        ----------
        signer: sp.TAddress
            The address to be remove as signer.

        Raises
        ------
        NotAdmin
            If the caller of the entrypoint is not a set admin of the contract.
        """
        sp.set_type(signer, sp.TAddress)
        self.verify_is_admin(sp.unit)
        del self.data.trusted_signers[signer]
