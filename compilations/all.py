import smartpy as sp

import utils.constants as Constants

from contracts.tzbtc_ledger import TzBTCLedger

sp.add_compilation_target(
    "tzBTCLedger",
    TzBTCLedger(
        administrators = sp.big_map({}),
        gatekeepers = sp.big_map({}),
        trusted_signers = sp.big_map({}),
        threshold = sp.nat(3)
    ),
)