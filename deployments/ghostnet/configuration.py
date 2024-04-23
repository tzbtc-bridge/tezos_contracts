from deployments.utils import AdministratorStatus

NODE_URL = 'https://ghostnet.smartpy.io'
SECRET_KEY = 'edsk...'

# IMPORTANT: ADMINISTRATOR_NUM must be equal to the number of entries in the
# ADMINISTRATORS map
ADMINISTRATORS_NUM = 2 
ADMINISTRATORS = {
    'tz1YZkgk9jfxcBTKWvaFTuh5fPxYEueQGDT8' : AdministratorStatus.SET,
    'tz1YY1LvD6TFH4z74pvxPQXBjAKHE5tB5Q8f' : AdministratorStatus.PROPOSED
}
GATEKEEPERS = {
    'tz1YZkgk9jfxcBTKWvaFTuh5fPxYEueQGDT8' : None,
}
TRUSTED_SIGNERS = {
    'tz3ekishqwvwD3TcWqKr69VH6hPPSGSgGZzW' : None,
    'tz3NAPQZPKQZzkrr2yxkhwKokJLSKLD2uHJ8' : None,
    'tz3QuXHbySZvCaXzHnoZCjgvHouHVoHPPLtF' : None,
    'tz3UPtEiofqe8BG4jpFqKNZWHPh6P7izs2NP' : None,
    'tz3YNgb5bURsGBmtJT5vSPi9YwDnL59fNyz9' : None,
    'tz3cCyqMgEDw4EmKfwHwiSZNzXjXB6hmaPAr' : None,
    'tz3dPSmjvaaBGaEqiSxbrApyqr9eGuA6DknU' : None,
    'tz3dmrzPZo5XWDT4u4mPCWUaUntpmR2YHoqN' : None,
    'tz3h3qaqy43T9q45RiZ6bnnt9To2xEwmfF9v' : None,
}
THRESHOLD = 1
MIN_BURN_AMOUNT = 250
SERVICE_FEE = 100
TOKEN_ADDRESS = 'KT18jqS6maEXL8AWvc2x2bppHNRQNqPq8axP'
MAX_BTC_NETWORK_FEE = 1_000_000
BTC_GATEKEEPER_ADDRESS = bytes.fromhex("220020098092d4bb569269aff17f802a1adeca4bc76bb6262b635de46e1bf6e7762e94")
CUSTODY_BTC_ADDRESS =bytes.fromhex("220020f0360a5c58b91fbdcd5bb43458fcc7a2f6ef4f950c96091edbb9b852468e3099") 
REDEEM_ADDRESS = 'tz1YZkgk9jfxcBTKWvaFTuh5fPxYEueQGDT8'
TREASURY_ADDRESS = 'tz1YZkgk9jfxcBTKWvaFTuh5fPxYEueQGDT8'
MAX_UTXO_PER_TX_COUNT = 10
METADATA = {
    "": bytes.fromhex('74657a6f732d73746f726167653a64617461'), # "tezos-storage:data"
    # Data field is the hex string of:
    # { "name": "tzBTC Ledger", "authors": ["Papers <contact@papers.ch>"], "homepage":  "https://www.papers.ch" }
    "data": bytes.fromhex('7b20226e616d65223a2022747a425443204c6564676572222c2022617574686f7273223a205b22506170657273203c636f6e74616374407061706572732e63683e225d2c2022686f6d6570616765223a20202268747470733a2f2f7777772e7061706572732e636822207d')
}