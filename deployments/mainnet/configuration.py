from deployments.utils import AdministratorStatus

NODE_URL = 'https://rpc.tzbeta.net'
SECRET_KEY = 'edsk...'

# IMPORTANT: ADMINISTRATOR_NUM must be equal to the number of entries in the
# ADMINISTRATORS map
ADMINISTRATORS_NUM = 2  # TBD
ADMINISTRATORS = {
    'tz1YY1LvD6TFH4z74pvxPQXBjAKHE5tB5Q8f' : AdministratorStatus.SET,
    'KT1JuyPBgJRZCdPm5tcRSaTagYPehwzEZVhu' : AdministratorStatus.SET,
}
GATEKEEPERS = {}
TRUSTED_SIGNERS = {}
THRESHOLD = 4  # TBD
MIN_BURN_AMOUNT = 150_000
SERVICE_FEE = 0
TOKEN_ADDRESS = 'KT1PWx2mnDueood7fEmfbBDKx1D9BAnnXitn'
MAX_BTC_NETWORK_FEE = 1_000_000  # TBD
BTC_GATEKEEPER_ADDRESS = bytes.fromhex("2200204f98cc840180932e1a41a75531f626ada7db8889a24ca1bf6453c1178778c05c")
CUSTODY_BTC_ADDRESS =bytes.fromhex("220020cec33d6ebe8301f1d5689a32d37b7e515c78edb837b694e834a3381e1ea49b27")
REDEEM_ADDRESS = 'KT1PWx2mnDueood7fEmfbBDKx1D9BAnnXitn' # The redeem address set on the tzbtc token contract.
TREASURY_ADDRESS = 'tz1dLTL7zmFEVaLH1mevxA7o6kW65Eq42rQ9' # TBD
MAX_UTXO_PER_TX_COUNT = 10
METADATA = {
    "": bytes.fromhex('74657a6f732d73746f726167653a64617461'), # "tezos-storage:data"
    # Data field is the hex string of:
    # { "name": "tzBTC Ledger", "contact": ["LEXR <tzbtc@lexr.com>"], "homepage":  " https://www.lexr.com" }
    "data": bytes.fromhex('7b20226e616d65223a2022747a425443204c6564676572222c2022636f6e74616374223a205b224c455852203c747a627463406c6578722e636f6d3e225d2c2022686f6d6570616765223a2020222068747470733a2f2f7777772e6c6578722e636f6d22207d')
}