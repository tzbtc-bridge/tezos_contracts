import smartpy as sp

from utils.administrable_mixin import SingleAdministrableMixin, AdministratorStatus


class AdministrableContract(sp.Contract, SingleAdministrableMixin):
    def __init__(
        self,
        administrators=sp.big_map(l={}, tkey=sp.TAddress, tvalue=sp.TNat),
        administrators_num=sp.nat(0),
        gatekeepers=sp.big_map(l={}, tkey=sp.TAddress, tvalue=sp.TUnit),
        trusted_signers=sp.big_map(l={}, tkey=sp.TAddress, tvalue=sp.TUnit),
        threshold=sp.nat(3),
        min_burn_amount=sp.nat(100),
        btc_gatekeeper_address=sp.bytes("0xff"),
        custody_btc_address=sp.bytes("0xff"),
        service_fee=sp.nat(100),
        max_btc_network_fee=sp.nat(1000000),
        treasury_address=sp.address("KT1PWx2mnDueood7fEmfbBDKx1D9BAnnXitn"),
        redeem_address=sp.address("KT1PWx2mnDueood7fEmfbBDKx1D9BAnnXitn"),
    ):
        self.init_type(
            sp.TRecord(
                administrators=sp.TBigMap(sp.TAddress, sp.TNat),
                administrators_num=sp.TNat,
                gatekeepers=sp.TBigMap(sp.TAddress, sp.TUnit),
                trusted_signers=sp.TBigMap(sp.TAddress, sp.TUnit),
                threshold=sp.TNat,
                min_burn_amount=sp.TNat,
                service_fee=sp.TNat,
                max_btc_network_fee=sp.TNat,
                treasury_address=sp.TAddress,
                redeem_address=sp.TAddress,
                btc_gatekeeper_address=sp.TBytes,
                custody_btc_address=sp.TBytes,
            )
        )

        self.init(
            administrators=administrators,
            administrators_num=administrators_num,
            gatekeepers=gatekeepers,
            trusted_signers=trusted_signers,
            threshold=threshold,
            min_burn_amount=min_burn_amount,
            service_fee=service_fee,
            max_btc_network_fee=max_btc_network_fee,
            treasury_address=treasury_address,
            redeem_address=redeem_address,
            btc_gatekeeper_address=btc_gatekeeper_address,
            custody_btc_address=custody_btc_address,
        )


@sp.add_test(name="Administrable Mixin")
def test():
    scenario = sp.test_scenario()

    scenario.h1("Administrable Mixin Unit Tests")
    scenario.table_of_contents()

    scenario.h2("Set up/Bootstrapping")
    admin1 = sp.test_account("Admin1")
    admin2 = sp.test_account("Admin2")
    admin3 = sp.test_account("Admin3")
    gatekeeper = sp.test_account("Gatekeeper")
    trusted_signer = sp.test_account("TrustedSigner")
    alice = sp.test_account("Alice")
    bob = sp.test_account("Bob")
    default = sp.test_account("Default")

    scenario.h2("Accounts")
    scenario.show([admin1, admin2, admin3, gatekeeper, trusted_signer, alice, bob])

    administable_contract = AdministrableContract(
        administrators=sp.big_map({admin1.address: AdministratorStatus.PROPOSED}),
        administrators_num=sp.nat(0),
        gatekeepers=sp.big_map({}),
        trusted_signers=sp.big_map({}),
        threshold=sp.nat(3),
        min_burn_amount=sp.nat(100),
        btc_gatekeeper_address=sp.bytes("0xff"),
        custody_btc_address=sp.bytes("0xff"),
        service_fee=sp.nat(100),
        max_btc_network_fee=sp.nat(1000000),
        treasury_address=default.address,
        redeem_address=default.address,
    )
    scenario += administable_contract

    scenario.h2("Only proposed admins can accept proposal")
    scenario += administable_contract.accept_admin_proposal().run(
        sender=admin2, valid=False
    )
    scenario += administable_contract.accept_admin_proposal().run(sender=admin1)
    scenario.verify_equal(
        administable_contract.data.administrators[admin1.address],
        AdministratorStatus.SET,
    )
    scenario.verify(administable_contract.data.administrators_num == 1)

    scenario.h2("Only a set admin can propose new admins")
    scenario += administable_contract.propose_administrator(admin2.address).run(
        sender=admin1
    )
    scenario.verify_equal(
        administable_contract.data.administrators[admin2.address],
        AdministratorStatus.PROPOSED,
    )
    scenario.verify(administable_contract.data.administrators_num == 1)
    scenario += administable_contract.propose_administrator(alice.address).run(
        sender=alice, valid=False
    )
    scenario += administable_contract.propose_administrator(alice.address).run(
        sender=admin2, valid=False
    )

    scenario.h2("Only a set admin can add a gatekeeper")
    scenario += administable_contract.add_gatekeeper(gatekeeper.address).run(
        sender=alice, valid=False
    )
    scenario += administable_contract.add_gatekeeper(gatekeeper.address).run(
        sender=admin2, valid=False
    )
    scenario += administable_contract.add_gatekeeper(gatekeeper.address).run(
        sender=admin1
    )
    scenario.verify(administable_contract.data.gatekeepers.contains(gatekeeper.address))

    scenario.h2("Only a set admin can add a trusted signer")
    scenario += administable_contract.add_trusted_signer(trusted_signer.address).run(
        sender=alice, valid=False
    )
    scenario += administable_contract.add_trusted_signer(trusted_signer.address).run(
        sender=admin2, valid=False
    )
    scenario += administable_contract.add_trusted_signer(trusted_signer.address).run(
        sender=admin1
    )
    scenario.verify(
        administable_contract.data.trusted_signers.contains(trusted_signer.address)
    )

    scenario.h2("Only a set admin can update threshold")
    scenario += administable_contract.update_threshold(sp.nat(2)).run(
        sender=alice, valid=False
    )
    scenario += administable_contract.update_threshold(sp.nat(2)).run(
        sender=admin2, valid=False
    )
    scenario += administable_contract.update_threshold(sp.nat(2)).run(sender=admin1)
    scenario.verify(administable_contract.data.threshold == 2)

    scenario.h2("Only a set admin can update min burn amount")
    scenario += administable_contract.update_min_burn_amount(sp.nat(200)).run(
        sender=alice, valid=False
    )
    scenario += administable_contract.update_min_burn_amount(sp.nat(200)).run(
        sender=admin2, valid=False
    )
    scenario += administable_contract.update_min_burn_amount(sp.nat(200)).run(
        sender=admin1
    )
    scenario.verify(administable_contract.data.min_burn_amount == 200)

    scenario.h2("Only a set admin can update the bitcoin gatekeeper address")
    scenario += administable_contract.update_gatekeeper_btc_address(
        sp.bytes("0xfe")
    ).run(sender=alice, valid=False)
    scenario += administable_contract.update_gatekeeper_btc_address(
        sp.bytes("0xfe")
    ).run(sender=admin2, valid=False)
    scenario += administable_contract.update_gatekeeper_btc_address(
        sp.bytes("0xfe")
    ).run(sender=admin1)
    scenario.verify(
        administable_contract.data.btc_gatekeeper_address == sp.bytes("0xfe")
    )

    scenario.h2("Only a set admin can update the bitcoin custody address")
    scenario += administable_contract.update_custody_btc_address(sp.bytes("0xfe")).run(
        sender=alice, valid=False
    )
    scenario += administable_contract.update_custody_btc_address(sp.bytes("0xfe")).run(
        sender=admin2, valid=False
    )
    scenario += administable_contract.update_custody_btc_address(sp.bytes("0xfe")).run(
        sender=admin1
    )
    scenario.verify(administable_contract.data.custody_btc_address == sp.bytes("0xfe"))

    scenario.h2("Only a set admin can update the service fee")
    scenario += administable_contract.update_service_fee(sp.nat(200)).run(
        sender=alice, valid=False
    )
    scenario += administable_contract.update_service_fee(sp.nat(200)).run(
        sender=admin2, valid=False
    )
    scenario += administable_contract.update_service_fee(sp.nat(200)).run(sender=admin1)
    scenario.verify(administable_contract.data.service_fee == sp.nat(200))

    scenario.h2("Only a set admin can update the maximum bitcoin network fee")
    scenario += administable_contract.update_max_btc_network_fee(sp.nat(2_000_000)).run(
        sender=alice, valid=False
    )
    scenario += administable_contract.update_max_btc_network_fee(sp.nat(2_000_000)).run(
        sender=admin2, valid=False
    )
    scenario += administable_contract.update_max_btc_network_fee(sp.nat(2_000_000)).run(
        sender=admin1
    )
    scenario.verify(administable_contract.data.max_btc_network_fee == sp.nat(2_000_000))

    scenario.h2("Only a set admin can update the treasury address")
    scenario += administable_contract.update_treasury_address(alice.address).run(
        sender=alice, valid=False
    )
    scenario += administable_contract.update_treasury_address(alice.address).run(
        sender=admin2, valid=False
    )
    scenario += administable_contract.update_treasury_address(alice.address).run(
        sender=admin1
    )
    scenario.verify(administable_contract.data.treasury_address == alice.address)

    scenario.h2("Only a set admin can update the redeem address")
    scenario += administable_contract.update_redeem_address(alice.address).run(
        sender=alice, valid=False
    )
    scenario += administable_contract.update_redeem_address(alice.address).run(
        sender=admin2, valid=False
    )
    scenario += administable_contract.update_redeem_address(alice.address).run(
        sender=admin1
    )
    scenario.verify(administable_contract.data.redeem_address == alice.address)

    scenario.h2("Only a set admin can remove an admin")
    # Small setup to have 2 set admins and one proposed one.
    scenario += administable_contract.accept_admin_proposal().run(sender=admin2)
    scenario.verify_equal(
        administable_contract.data.administrators[admin2.address],
        AdministratorStatus.SET,
    )
    scenario.verify(administable_contract.data.administrators_num == 2)
    scenario += administable_contract.propose_administrator(admin3.address).run(
        sender=admin2
    )
    scenario.verify_equal(
        administable_contract.data.administrators[admin3.address],
        AdministratorStatus.PROPOSED,
    )
    scenario.verify(
        administable_contract.data.administrators_num == 2
    )  # num of admin does not change until acceptance

    scenario += administable_contract.remove_administrator(admin2.address).run(
        sender=alice, valid=False
    )
    scenario += administable_contract.remove_administrator(admin2.address).run(
        sender=admin3, valid=False
    )
    scenario += administable_contract.remove_administrator(admin2.address).run(
        sender=admin1
    )
    scenario.verify(~administable_contract.data.administrators.contains(admin2.address))
    scenario.verify(administable_contract.data.administrators_num == 1)

    scenario.h2("Cannot remove the last administrator")
    scenario += administable_contract.remove_administrator(admin1.address).run(
        sender=admin1, valid=False
    )

    scenario.h2("Only a set admin can remove a gatekeeper")
    scenario += administable_contract.remove_gatekeeper(gatekeeper.address).run(
        sender=alice, valid=False
    )
    scenario += administable_contract.remove_gatekeeper(gatekeeper.address).run(
        sender=admin3, valid=False
    )
    scenario += administable_contract.remove_gatekeeper(gatekeeper.address).run(
        sender=admin1
    )
    scenario.verify(
        ~administable_contract.data.gatekeepers.contains(gatekeeper.address)
    )

    scenario.h2("Only a set admin can remove a trusted signer")
    scenario += administable_contract.remove_trusted_signer(trusted_signer.address).run(
        sender=alice, valid=False
    )
    scenario += administable_contract.remove_trusted_signer(trusted_signer.address).run(
        sender=admin3, valid=False
    )
    scenario += administable_contract.remove_trusted_signer(trusted_signer.address).run(
        sender=admin1
    )
    scenario.verify(
        ~administable_contract.data.trusted_signers.contains(trusted_signer.address)
    )
